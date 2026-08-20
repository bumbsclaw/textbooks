# Chapter 10 — Zero Trust and Service-to-Service Authentication: mTLS and SPIFFE/SPIRE

**What this chapter covers.** Perimeter security assumes a hard outside and a soft inside — once traffic crosses the firewall, services trust each other implicitly because they are "inside" the network. Zero trust rejects that assumption: every service-to-service call is authenticated and authorized as if it traversed the public internet, regardless of where the caller sits in the VPC, the cluster, or the mesh. The network is not a trust boundary; identity is. This chapter builds that model from first principles to fleet reality. We start with why network-bound trust (VPC firewalls, perimeter TLS, shared secrets) fails at scale, define zero trust as workload identity plus mutual authentication plus least-privilege authorization, and then implement the two load-bearing pieces: mutual TLS (mTLS) — how TLS client authentication gives each workload a cryptographic identity — and SPIFFE/SPIRE — how a fleet issues, rotates, and federates short-lived X.509 SVIDs and JWT-SVIDs at scale without long-lived secrets. We show Envoy/Istio mTLS in depth (peer authentication, authorization policy, certificate rotation), raw Go/Java mTLS with `crypto/tls` and `javax.net.ssl`, SPIRE server/agent deployment with Kubernetes and `Workload API`, and federation across trust domains. Every pattern is anchored in runnable, version-pinned config and code and viewed through the distributed-systems lens where rotation without restarts, revocation without CRLs, and blast-radius isolation determine whether zero trust is a posture or just a diagram.

Learning goals — after this chapter you should be able to:

- Define zero trust for backend systems — workload identity as the trust anchor, mutual authentication on every hop, and authorization by identity (not by network) — and explain why perimeter/VPC trust breaks under lateral movement and single-service compromise.
- Establish mTLS correctly — TLS 1.2+ mutual authentication (`CertificateRequest` + `CertificateVerify`), peer-certificate validation (`verify_peer`, `SAN`/`SPIFFE ID` matching), cipher/TLS-version pinning, and why server-only TLS is not zero trust.
- Operate SPIFFE/SPIRE — `SPIFFE ID` (`spiffe://trust-domain/workload/...`) as the universal workload identity, `X509-SVID` and `JWT-SVID` issuance via the `Workload API`, attestation (Kubernetes `k8s_psat`, `k8s_sat`, `join_token`, `x509pop`), node vs workload attestation, registration entries, and automatic rotation.
- Deploy SPIRE on Kubernetes (SPIRE server with `k8s_psat` node attestation, agents as DaemonSets, `spire-agent` Workload API socket) and issue identities to pods without injecting long-lived secrets or restarting workloads on rotation.
- Configure service-mesh and raw mTLS enforcement: Istio `PeerAuthentication`/`AuthorizationPolicy` (or Cilium/Linkerd equivalents), Envoy `transport_socket` + `validation_context` with `SPIFFE` bundle, and Go/Java `tls.Config` with `GetCertificate`/`GetClientCertificate` + `VerifyPeerCertificate` pinning to a SPIFFE bundle.
- Federate trust domains (`spiffe://prod.example.com` ↔ `spiffe://partner.example.net`) via bundle exchange and JWKS/SPIFFE federation, handle CA rotation and bundle updates without downtime, and reason about revocation via short TTLs rather than CRLs/OCSP.
- Reason through the distributed-systems lens — certificate rotation without restarts, hot-reload of trust bundles, the blast radius of a compromised workload, audit and observability of identity (logging SPIFFE IDs, not IPs), and the interaction with secrets (Ch 8), authorization (Ch 7), and AppSec egress (Ch 9).

> **Boundary notes.** *TLS/PKI mechanics* (handshake, cert chains, CA hierarchies) are **Ch 4 (Certificates, PKI, and TLS Operations)** — this chapter assumes them. *OAuth/OIDC and human/CI identity* are **Ch 6**; *authorization by workload identity* builds on **Ch 7 (RBAC/ABAC/ReBAC)** with SPIFFE ID as the principal. *Secrets that zero-trust replaces or reduces* are **Ch 8**. *AppSec egress that rides on mTLS* is **Ch 9 (SSRF)**, and *supply-chain workload identity* (keyless signing, Fulcio) is the **Companion Series, Book 5** — SPIFFE complements, not replaces, that layer.

---

## Zero trust — the model and why perimeters fail

### The perimeter assumption

The classic network assumes:

```
Internet —[ firewall ]— DMZ —[ firewall ]— private VPC — trusted services
```

Inside the VPC, services call each other over plaintext or server-only TLS, authenticate with a shared secret or a bearer token that any insider can copy, and authorize by "if you reached me, you must be allowed." Identity, where it exists, is the *network location* — source IP, security group, namespace, or the fact that the caller is inside the mesh.

This fails in three routine ways:

1. **Lateral movement.** One compromised pod (SSRF, deserialization, leaked secret — Ch 9) can call any other service because nothing authenticates the caller. The blast radius is the entire VPC.
2. **Insider and supply-chain.** A malicious or compromised dependency that runs inside the network is already "trusted" — the perimeter cannot distinguish it from a legitimate caller.
3. **Cloud and multi-cluster.** Workloads span VPCs, regions, clusters, and providers. There is no single perimeter to draw — and even if there were, east-west traffic already dominates north-south.

Zero trust collapses the perimeter to *each connection*: the network is assumed hostile, every caller proves its identity cryptographically, and every callee authorizes the caller by that identity — not by where the bytes arrived from.

### The three tenets for backend systems

| Tenet | Means in practice | Replaces |
|-------|-------------------|----------|
| **Workload identity** | Every workload (pod, VM, job, function) has a stable, non-secret, cryptographically verifiable identity — the SPIFFE ID | IP, hostname, API key, shared secret |
| **Mutual authentication** | Every hop authenticates *both* sides with short-lived credentials bound to that identity (mTLS) | Server-only TLS + bearer token |
| **Identity-based authorization** | Every callee authorizes by the caller's identity (SPIFFE ID / JWT-SVID claim), not by network or token possession alone | Security-group / subnet / "inside the cluster" |

```mermaid
flowchart TB
    subgraph PerimeterModel["Perimeter model — trust by location"]
        C1["Caller (pod A)"] -->|"HTTP (plaintext<br/>or server-only TLS)<br/>no client cert"| S1["Callee (pod B)"]
        N1["Network: VPC / mesh<br/>is the trust boundary"] -. trust .- S1
        X1["Compromised pod C<br/>same VPC → calls B<br/>implicitly trusted"] -.-> S1
        style N1 fill:#f96,stroke:#333,color:#fff
        style X1 fill:#c55,stroke:#333,color:#fff
    end

    subgraph ZeroTrust["Zero-trust model — trust by identity"]
        C2["Caller — SPIFFE ID<br/>spiffe://prod/ns/api/svc/frontend"] -->|"mTLS — client SVID + server SVID<br/>both sides verify SPIFFE ID"| S2["Callee — SPIFFE ID<br/>spiffe://prod/ns/api/svc/payments"]
        P2["AuthorizationPolicy<br/>allow: frontend → payments /charge<br/>deny: all else"] -. enforce .- S2
        X2["Compromised pod C<br/>spiffe://prod/ns/batch/svc/untrusted<br/>mTLS succeeds but<br/>authZ denies /charge"] -.->|"mTLS ok, authZ DENY"| S2
        style P2 fill:#6a6,stroke:#333,color:#fff
        style X2 fill:#fa6,stroke:#333,color:#fff
    end
```

Two consequences matter for backend design:

- **Identity is not a secret.** A SPIFFE ID (`spiffe://trust-domain/...`) is public — like a username, not a password. Possession of the *SVID* (the X.509 cert bound to the private key) proves the identity; knowledge of the ID alone does not. This is why SPIFFE replaces API keys — the private key never leaves the workload's `Workload API` socket.
- **Trust is explicit and enumerable.** An `AuthorizationPolicy` that says "only `spiffe://prod/ns/api/svc/frontend` may call `POST /v1/charge`" is auditable — unlike a security-group rule that says "any pod in subnet `10.4.2.0/24` may call payments."

---

## Mutual TLS — the authentication hop

### What mTLS adds to TLS (and what Ch 4 already covered)

Vol 3, Ch 6 and Ch 4 of this volume cover the TLS 1.3 handshake, cipher suites, and PKI. mTLS changes one thing: the server requests and verifies a *client* certificate. The handshake becomes:

```
Client                          Server
  |  ClientHello (+ key_share)      |
  |-------------------------------->|
  |  ServerHello (+ key_share)      |
  |  Certificate (server SVID)      |  same as server-only TLS
  |  CertificateVerify (server)     |
  |  CertificateRequest             |  ← mTLS addition
  |<--------------------------------|
  |  Certificate (client SVID)      |  ← mTLS addition
  |  CertificateVerify (client)     |  ← proves possession of client private key
  |  Finished                       |
  |<-------------------------------->|
  |  Finished                       |
  |<===============================>|  application data (both directions authenticated)
```

The two `CertificateVerify` messages each sign the transcript with the sender's private key — proving possession without ever transmitting the key. A middlebox that sees the wire learns the SPIFFE IDs (they are in the certs) but cannot impersonate either side.

> **Why server-only TLS is not zero trust.** With server-only TLS, only the client verifies the server. A compromised client can still call the server — the server has no cryptographic reason to refuse. mTLS gives the *server* the same proof the client has.

### What to validate — the checklist

| Check | What it means | Failure mode if skipped |
|-------|---------------|------------------------|
| **Peer cert chain validates to a trusted bundle** | `verify_peer` against the SPIFFE trust bundle (or mesh CA bundle) | Any self-signed cert accepted |
| **Leaf SAN is the expected SPIFFE ID** (or URI SAN prefix) | `URI:spiffe://prod/ns/api/svc/frontend` exact match or `spiffe://prod/ns/api/*` pattern | Any workload in the trust domain can impersonate any other |
| **Cert is not expired and not yet valid** | `NotBefore` ≤ now ≤ `NotAfter`; short TTL (1h–24h) expected | Clock skew hides stale creds; long TTL widens compromise window |
| **TLS version and cipher pinned** | `TLS 1.2+`, `AEAD` ciphers only (`TLS_AES_128_GCM_SHA256`, `TLS_CHACHA20_POLY1305_SHA256`, `TLS_ECDHE_*_WITH_AES_*_GCM`) | Downgrade to weak ciphers |
| **SNI / ALPN consistent** (gRPC/HTTP2) | `h2`/`grpc` ALPN; SNI matches expected service if used | Protocol confusion |
| **Rotation without restart** | Hot-reload cert and bundle on `Workload API` update | Rotation requires pod restart → rollout or outage |

### Go — raw mTLS with SPIFFE bundle (no mesh)

```go
// Go 1.22+ — mTLS client and server using a SPIFFE bundle as the trust anchor.
// In production, certs come from the Workload API (see SPIRE section below);
// this shows the tls.Config shape with hot-reload.

package mtls

import (
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"net/http"
)

// newServerTLS returns a tls.Config that *requires* a client cert signed by the SPIFFE bundle
// and verifies the client's SPIFFE ID is in the allowed set.
func newServerTLS(cert tls.Certificate, bundle *x509.CertPool, allowedIDs map[string]bool) *tls.Config {
	return &tls.Config{
		Certificates: []tls.Certificate{cert},
		ClientAuth:   tls.RequireAndVerifyClientCert,
		ClientCAs:    bundle, // SPIFFE bundle (trust domain root) — not the system pool
		MinVersion:   tls.VersionTLS12,
		VerifyPeerCertificate: func(rawCerts [][]byte, _ [][]*x509.Certificate) error {
			if len(rawCerts) == 0 {
				return fmt.Errorf("no client certificate presented")
			}
			leaf, err := x509.ParseCertificate(rawCerts[0])
			if err != nil {
				return err
			}
			// SPIFFE ID is a URI SAN; Envoy/Go expose it as leaf.URIs
			if len(leaf.URIs) == 0 || leaf.URIs[0].Scheme != "spiffe" {
				return fmt.Errorf("client cert has no SPIFFE URI SAN")
			}
			id := leaf.URIs[0].String()
			if !allowedIDs[id] {
				return fmt.Errorf("SPIFFE ID %q not authorized", id)
			}
			return nil
		},
		GetCertificate: func(*tls.ClientHelloInfo) (*tls.Certificate, error) {
			// In SPIRE deployments, fetch from Workload API here for rotation without restart
			return &cert, nil
		},
	}
}

// newClientTLS returns a tls.Config that presents a client cert and verifies the server's SPIFFE ID.
func newClientTLS(cert tls.Certificate, bundle *x509.CertPool, expectedServerID string) *tls.Config {
	return &tls.Config{
		Certificates: []tls.Certificate{cert},
		RootCAs:      bundle,
		MinVersion:   tls.VersionTLS12,
		ServerName:   "payments.prod.example.com", // SNI — or leave empty and verify in VerifyPeerCertificate
		VerifyPeerCertificate: func(rawCerts [][]byte, _ [][]*x509.Certificate) error {
			if len(rawCerts) == 0 {
				return fmt.Errorf("no server certificate")
			}
			leaf, err := x509.ParseCertificate(rawCerts[0])
			if err != nil {
				return err
			}
			if len(leaf.URIs) == 0 || leaf.URIs[0].String() != expectedServerID {
				return fmt.Errorf("server SPIFFE ID mismatch: got %v want %q", leaf.URIs, expectedServerID)
			}
			// Also verify chain to bundle — Go does this automatically when RootCAs is set
			// and VerifyPeerCertificate is nil; with a custom verifier, do it explicitly:
			opts := x509.VerifyOptions{Roots: bundle, KeyUsages: []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth}}
			if _, err := leaf.Verify(opts); err != nil {
				return fmt.Errorf("server cert chain invalid: %w", err)
			}
			return nil
		},
	}
}

// Wiring — servers hot-reload certs by re-reading from the Workload API or a file watcher.
// Clients reuse the same tls.Config with http.Transport or grpc.WithTransportCredentials.
func Example() {
	// cert, bundle loaded from Workload API (see SPIRE section) or files:
	// certPEM, keyPEM, bundlePEM := workloadAPI.GetX509SVID(ctx)
	// cert, _ := tls.X509KeyPair(certPEM, keyPEM)
	// bundle := x509.NewCertPool(); bundle.AppendCertsFromPEM(bundlePEM)
	_ = &http.Server{
		Addr:      ":8443",
		TLSConfig: newServerTLS(tls.Certificate{}, x509.NewCertPool(), map[string]bool{"spiffe://prod/ns/api/svc/frontend": true}),
	}
}
```

> **Production note.** Above, `GetCertificate`/`GetClientCertificate` and a bundle watcher replace cert and `ClientCAs`/`RootCAs` without restarting the process. Libraries like `go-spiffe/v2` and `java-spiffe` do this by implementing `tls.Config.GetCertificate` against the `Workload API` stream — see the SPIRE Workload API section below. Never read `cert.pem` once at startup.

---

## SPIFFE and SPIRE — workload identity at fleet scale

Shared secrets and long-lived certs do not scale — they leak, they require rotation ceremonies that need restarts, and they give every workload the same credential shape whether it is a deployment, a job, or a third-party integration. SPIFFE (Secure Production Identity Framework for Everyone, CNCF graduated) defines a *universal* workload identity and SPIRE (SPIFFE Runtime Environment) is its fleet-scale issuer.

### The primitives

| Primitive | What it is | Example |
|-----------|------------|---------|
| **SPIFFE ID** | URI `spiffe://trust-domain/path` — the identity, not the credential | `spiffe://prod.example.com/ns/payments/sa/payments-api` |
| **Trust domain** | The authority namespace — one per organization/environment that owns a root CA | `prod.example.com`, `staging.example.com` |
| **X509-SVID** | Short-lived X.509 cert (TTL 1h–24h) with SPIFFE ID in URI SAN + private key | What mTLS actually uses |
| **JWT-SVID** | Short-lived JWT (`aud`, `sub=SPIFFE ID`, `exp` in minutes) via `Workload API` | For non-mTLS hops (HTTP `Authorization: Bearer <JWT-SVID>`) |
| **Bundle** | Trust domain's root CA(s) + JWT signing keys — what verifiers pin | `spiffe://prod.example.com` bundle |
| **Workload API** | Unix-domain-socket gRPC API (`/run/spire/sockets/agent.sock`) that workloads call to fetch/rotate SVIDs | `FetchX509SVID`, `FetchJWTSVID`, `FetchBundle` |
| **Attestation** | How SPIRE proves a workload *is* the SPIFFE ID it claims — node + workload attestors | `k8s_psat`, `k8s_sat`, `join_token`, `x509pop`, `aws_iid` |

```mermaid
flowchart TB
    subgraph SPIREControl["SPIRE control plane"]
        Server["SPIRE Server<br/>CA + Bundle + Registration API"]
        DS["Datastore<br/>(SQLite / Postgres)"]
        Server --- DS
    end
    subgraph Node["Kubernetes node"]
        Agent["SPIRE Agent (DaemonSet)<br/>Node attestation → Server<br/>Workload attestation → Pod"]
        Sock["Workload API socket<br/>/run/spire/sockets/agent.sock"]
        Agent --- Sock
        W1["Pod: frontend<br/>spiffe://prod/ns/api/svc/frontend<br/>fetches X509-SVID via UDS"]
        W2["Pod: payments<br/>spiffe://prod/ns/api/svc/payments<br/>fetches X509-SVID via UDS"]
        W1 --- Sock
        W2 --- Sock
    end
    Agent <-- "mTLS (agent SVID)<br/>Fetch + rotation stream" --> Server

    W1 -- "mTLS with X509-SVIDs<br/>both sides verify SPIFFE ID<br/>against bundle" --> W2

    style Server fill:#69c,stroke:#333,color:#fff
    style Agent fill:#6a6,stroke:#333,color:#fff
    style Sock fill:#fa6,stroke:#333,color:#fff
```

### Node attestation vs workload attestation

SPIRE verifies identity in two stages:

1. **Node attestation** — the Agent proves the *node* to the Server. On Kubernetes, `k8s_psat` (Projected ServiceAccount Token) is the modern default — the Agent presents a projected SAT bound to the node's service account; the Server validates it against the Kubernetes API. Older `k8s_sat` and cloud attestors (`aws_iid`, `gcp_iit`, `azure_msi`) work the same way — the node proves it is what it claims.

2. **Workload attestation** — the Agent proves a *pod/process* to itself before handing over an SVID. Selectors like `k8s:ns:payments`, `k8s:sa:payments-api`, `k8s:pod-label:app=payments`, `unix:uid:1000` are matched against registration entries. Only if the pod's attested selectors match an entry does the Agent issue that entry's SPIFFE ID.

A pod cannot claim an arbitrary SPIFFE ID — it only receives the IDs whose selectors it satisfies.

### SPIRE on Kubernetes — production config (SPIRE 1.9+)

```yaml
# spire-server — StatefulSet (excerpt, SPIRE 1.9.x, Kubernetes 1.29+)
# Full chart: spire-helm / spiffe/spire; this is the minimal Server config.
apiVersion: v1
kind: ConfigMap
metadata:
  name: spire-server
  namespace: spire
data:
  server.conf: |
    server {
      bind_address = "0.0.0.0"
      bind_port = "8081"
      trust_domain = "prod.example.com"
      data_dir = "/run/spire/data"
      log_level = "INFO"
      ca_key_type = "ec-p256"
      ca_ttl = "24h"
      default_x509_svid_ttl = "1h"
      default_jwt_svid_ttl = "5m"
    }
    plugins {
      DataStore "sql" {
        plugin_data {
          database_type = "postgres"
          connection_string = "postgres://spire:__VAULT_SECRET__@postgres.spire.svc.cluster.local/spire?sslmode=require"
        }
      }
      NodeAttestor "k8s_psat" {
        plugin_data {
          clusters = {
            prod = {
              service_account_allow_list = ["spire:spire-agent"]
              audience = ["spire-server"]   # must match the agent's projected SAT audience
            }
          }
        }
      }
      KeyManager "disk" {
        plugin_data { keys_path = "/run/spire/data/keys.json" }
      }
      Notifier "k8sbundle" {
        plugin_data { namespace = "spire" }  # publishes bundle as ConfigMap spire-bundle
      }
    }
    health_checker {
      registration_uds_path = "/run/spire/sockets/server.sock"
    }
---
# spire-agent — DaemonSet (one per node)
apiVersion: v1
kind: ConfigMap
metadata:
  name: spire-agent
  namespace: spire
data:
  agent.conf: |
    agent {
      data_dir = "/run/spire/data"
      log_level = "INFO"
      server_address = "spire-server.spire.svc.cluster.local"
      server_port = "8081"
      trust_domain = "prod.example.com"
      trust_bundle_path = "/run/spire/bundle/bundle.crt"  # from spire-bundle ConfigMap
    }
    plugins {
      NodeAttestor "k8s_psat" {
        plugin_data {
          cluster = "prod"
          audience = ["spire-server"]
        }
      }
      WorkloadAttestor "k8s" {
        plugin_data {
          # uses kubelet /pods API; no extra config
        }
      }
      KeyManager "disk" {
        plugin_data { directory = "/run/spire/data" }
      }
    }
---
# Registration entries — who gets which SPIFFE ID (SPIRE CRD / server API)
# Prefer the Kubernetes CRD (spire-controller-manager) over CLI for GitOps.
apiVersion: spire.spiffe.io/v1alpha1
kind: ClusterSPIFFEID
metadata:
  name: payments-api
spec:
  spiffeIDTemplate: "spiffe://prod.example.com/ns/{{ .PodMeta.Namespace }}/sa/{{ .PodSpec.ServiceAccountName }}"
  podSelector:
    matchLabels:
      app: payments
  workloadSelectorTemplates:
    - "k8s:ns:payments"
    - "k8s:sa:payments-api"
    - "k8s:pod-label:app=payments"
---
# Alternative — server CLI (for non-CRD installs):
# spire-server entry create \
#   -spiffeID spiffe://prod.example.com/ns/payments/sa/payments-api \
#   -parentID spiffe://prod.example.com/spire/agent/k8s_psat/prod/$(uuid) \
#   -selector k8s:ns:payments -selector k8s:sa:payments-api -selector k8s:pod-label:app=payments \
#   -x509SVIDTTL 3600
```

```yaml
# Workload pod — no secret injection; just mount the Workload API socket
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payments
  namespace: payments
spec:
  template:
    metadata:
      labels: { app: payments }
    spec:
      serviceAccountName: payments-api
      containers:
        - name: payments
          image: ghcr.io/acme/payments:1.4.2
          volumeMounts:
            - name: spire-agent-socket
              mountPath: /run/spire/sockets
              readOnly: true
          env:
            - name: SPIFFE_ENDPOINT_SOCKET
              value: unix:///run/spire/sockets/agent.sock
      volumes:
        - name: spire-agent-socket
          csi:
            driver: csi.spiffe.io   # SPIFFE CSI driver — mounts the agent socket
            readOnly: true
```

### Workload API — fetching and rotating SVIDs

Workloads never write `cert.pem` to disk — they stream SVIDs over the Workload API Unix socket. Two idiomatic paths:

```go
// Go — fetch X509-SVID via Workload API (github.com/spiffe/go-spiffe/v2 2.3+, SPIRE 1.9+)
package main

import (
	"context"
	"crypto/tls"
	"log"
	"net/http"

	"github.com/spiffe/go-spiffe/v2/workloadapi"
	"github.com/spiffe/go-spiffe/v2/spiffetls/tlsconfig"
	"github.com/zeebo/errs"
)

func main() {
	ctx := context.Background()

	// X509Source watches the Workload API and hot-reloads certs + bundle.
	// No restart on rotation — the source pushes updates.
	source, err := workloadapi.NewX509Source(ctx, workloadapi.WithClientOptions(
		workloadapi.WithAddr("unix:///run/spire/sockets/agent.sock"),
	))
	if err != nil {
		log.Fatalf("x509 source: %v", err)
	}
	defer source.Close()

	// Server: require any client in the trust domain (authZ refines this — see mesh/AuthZ below)
	tlsConfig := tlsconfig.MTLSServerConfig(source, source,
		tlsconfig.AuthorizeAny())  // or AuthorizeMemberOf("prod.example.com")

	// Client: present our SVID and verify the server's SPIFFE ID
	clientTLS := tlsconfig.MTLSClientConfig(source, source,
		tlsconfig.AuthorizeMemberOf("prod.example.com"))

	_ = &http.Server{
		Addr:      ":8443",
		TLSConfig: tlsConfig,
	}
	_ = &http.Client{Transport: &http.Transport{TLSClientConfig: clientTLS}}

	// JWT-SVID for non-mTLS hops (aud is the intended audience):
	// jwtSource, _ := workloadapi.NewJWTSource(ctx, ...)
	// jwt, _ := jwtSource.FetchJWTSVID(ctx, jwtsvid.Params{Audience: "payments"})
	// req.Header.Set("Authorization", "Bearer "+jwt.Marshal())
	_ = errs.Wrap
}
```

```java
// Java — same shape (java-spiffe 0.8+, SPIRE 1.9+)
import io.spiffe.workloadapi.X509Source;
import io.spiffe.workloadapi.X509SourceConfig;
import io.spiffe.provider.SpiffeSslContext;
import javax.net.ssl.SSLContext;

X509Source source = X509Source.newSource(
    X509SourceConfig.newBuilder()
        .setWorkloadApiSocket("unix:///run/spire/sockets/agent.sock")
        .build());

SSLContext serverCtx = SpiffeSslContext.newBuilder()
    .withX509Source(source)
    .buildServerSSLContext();   // hot-reloads; no restart

SSLContext clientCtx = SpiffeSslContext.newBuilder()
    .withX509Source(source)
    .buildClientSSLContext("spiffe://prod.example.com/ns/payments/sa/payments-api");
// For JWT-SVID: JwtSource + JwtSvid.getToken()
```

```mermaid
sequenceDiagram
    participant Pod as payments pod
    participant Agent as SPIRE Agent (UDS)
    participant Server as SPIRE Server

    Pod->>Agent: WorkloadAPI FetchX509SVID (CSR with SPIFFE ID)
    Agent->>Agent: Workload attestation —<br/>k8s selectors match entry?<br/>k8s:ns:payments, k8s:sa:payments-api

    alt selectors match
        Agent->>Server: Sign CSR (agent SVID mTLS)
        Server->>Server: Issue X509-SVID (TTL 1h)<br/>sign with trust-domain CA
        Server-->>Agent: X509-SVID + bundle
        Agent-->>Pod: X509-SVID + bundle (stream)
        Note over Pod,Agent: Pod hot-reloads tls.Config<br/>no restart; Agent re-issues before expiry
    else selectors do not match
        Agent-->>Pod: PermissionDenied — no entry
    end

    Pod->>Pod: Watch stream —<br/>new SVID arrives before old expires<br/>tls.Config updated atomically
```

---

## Enforcing — mesh policy and raw authZ

Identity is only useful if the callee enforces it. Two layers: mesh-level policy (Istio/Envoy/Cilium/Linkerd) for fleet-wide enforcement without code changes, and application-level SPIFFE ID checks for defense in depth.

### Istio — `PeerAuthentication` + `AuthorizationPolicy` (Istio 1.22+, SPIRE as CA)

Istio's control plane (`istiod`) can consume SPIRE-issued SVIDs when SPIRE is the mesh CA (plug-in CA) or when `istiod` federates with SPIRE via `istio-spire` / `MCP`. The policy is the same shape:

```yaml
# Enforce mTLS STRICT on payments — no plaintext allowed
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: payments-strict-mtls
  namespace: payments
spec:
  selector:
    matchLabels: { app: payments }
  mtls:
    mode: STRICT   # PERMISSIVE during migration; STRICT after all callers have SVIDs
---
# Allow only frontend → payments on POST /v1/charge
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payments-allow-frontend-charge
  namespace: payments
spec:
  selector:
    matchLabels: { app: payments }
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/api/sa/frontend"]  # Istio SPIFFE form; with SPIRE: spiffe://prod.example.com/ns/api/sa/frontend
      to:
        - operation:
            methods: ["POST"]
            paths: ["/v1/charge"]
    # Optional: also allow SRE break-glass identity with audit
    - from:
        - source:
            principals: ["spiffe://prod.example.com/ns/sre/sa/break-glass"]
      to:
        - operation:
            methods: ["GET"]
            paths: ["/v1/orders/*"]
---
# During migration — log but don't yet deny non-mTLS
# AuthorizationPolicy with action: AUDIT / CUSTOM (Envoy ext_authz) for canary
```

With SPIRE as the root, `principals` are full SPIFFE IDs (`spiffe://prod.example.com/...`). The Envoy sidecar validates the peer cert against the SPIFFE bundle and extracts the SPIFFE ID for `source.principal` matching — no IP rules.

### Envoy — raw mTLS with SPIFFE bundle (no full mesh)

When you do not run a mesh control plane, Envoy as a sidecar or gateway can still enforce mTLS with a SPIFFE bundle:

```yaml
# Envoy listener — require client cert, verify SPIFFE URI SAN, route by SPIFFE ID
# Envoy 1.31+, SPIRE bundle at /run/spire/bundle/bundle.crt (rotated by SPIRE agent)
static_resources:
  listeners:
    - name: payments_listener
      address: { socket_address: { address: 0.0.0.0, port_value: 8443 } }
      filter_chains:
        - transport_socket:
            name: envoy.transport_sockets.tls
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
              require_client_certificate: true
              common_tls_context:
                tls_certificate_sds_secret_configs:
                  - name: "spiffe://prod.example.com/ns/payments/sa/payments-api"
                    sds_config:
                      path_config_source: { path: "/run/spire/sockets/agent.sock" }  # SDS via Workload API
                validation_context_sds_secret_config:
                  name: "spiffe://prod.example.com"
                  sds_config:
                    path_config_source: { path: "/run/spire/sockets/agent.sock" }
                # Enforce TLS 1.2+, AEAD ciphers
                tls_params:
                  tls_minimum_protocol_version: TLSv1_2
                  cipher_suites: ["ECDHE-ECDSA-AES128-GCM-SHA256", "ECDHE-RSA-AES128-GCM-SHA256"]
          filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                stat_prefix: payments
                route_config:
                  name: payments_routes
                  virtual_hosts:
                    - name: payments
                      domains: ["*"]
                      routes:
                        # RBAC by SPIFFE ID — only frontend may POST /v1/charge
                        - match: { prefix: "/v1/charge", headers: [{ name: ":method", exact_match: "POST" }] }
                          route: { cluster: payments_local }
                          typed_per_filter_config:
                            envoy.filters.http.rbac:
                              "@type": type.googleapis.com/envoy.config.rbac.v3.RBACPerRoute
                              rules:
                                action: ALLOW
                                policies:
                                  frontend:
                                    principals:
                                      - authenticated: { principal_name: { exact: "spiffe://prod.example.com/ns/api/svc/frontend" } }
                                    permissions:
                                      - any: true
                http_filters:
                  - name: envoy.filters.http.rbac
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.rbac.v3.RBAC
                      rules: {}  # per-route RBAC above
                  - name: envoy.filters.http.router
```

### Application-level — defense in depth behind the mesh

Mesh policy covers the fleet; application code still checks the SPIFFE ID it sees — so a misconfigured mesh does not silently grant access:

```go
// Go — authorize by SPIFFE ID inside the handler (defense in depth)
func (h *Handler) Charge(w http.ResponseWriter, r *http.Request) {
    // tls.ConnectionState.PeerCertificates[0].URIs[0] is the caller SPIFFE ID
    // With go-spiffe, use spiffetls handshaker; with raw tls, parse leaf.URIs
    peerID := spiffeIDFromContext(r.Context()) // from tls.ConnectionState or gRPC peer.AuthInfo
    if peerID != "spiffe://prod.example.com/ns/api/svc/frontend" {
        http.Error(w, "forbidden: caller not authorized for /v1/charge", http.StatusForbidden)
        return
    }
    // ... handle charge
}

// gRPC interceptor — same check for gRPC
func spiffeAuthInterceptor(allowed map[string]bool) grpc.UnaryServerInterceptor {
    return func(ctx context.Context, req any, _ *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (any, error) {
        p, ok := peer.FromContext(ctx)
        if !ok {
            return nil, status.Error(codes.Unauthenticated, "no peer")
        }
        tlsInfo, ok := p.AuthInfo.(credentials.TLSInfo)
        if !ok || len(tlsInfo.State.PeerCertificates) == 0 {
            return nil, status.Error(codes.Unauthenticated, "no client certificate")
        }
        leaf := tlsInfo.State.PeerCertificates[0]
        if len(leaf.URIs) == 0 {
            return nil, status.Error(codes.Unauthenticated, "no SPIFFE URI SAN")
        }
        id := leaf.URIs[0].String()
        if !allowed[id] {
            return nil, status.Errorf(codes.PermissionDenied, "SPIFFE ID %q not authorized", id)
        }
        return handler(ctx, req)
    }
}
```

---

## Federation — trust across domains

A single trust domain (`prod.example.com`) is a single root CA — if it is compromised, everything is. Federation lets two domains authenticate each other without sharing a CA: each domain publishes its bundle, the other imports it, and workloads in domain A can verify SVIDs from domain B.

```
Domain A: spiffe://prod.example.com/ns/api/svc/frontend
Domain B: spiffe://partner.example.net/ns/fulfillment/svc/shipper

Federation: A imports B's bundle; B imports A's bundle
Frontend (A) → Shipper (B): mTLS — shipper verifies frontend's SVID against A's bundle
Shipper → Frontend: reverse — frontend verifies shipper's SVID against B's bundle
```

```mermaid
flowchart TB
    subgraph DomainA["Trust domain A — prod.example.com"]
        CA_A["Root CA_A<br/>bundle_A<br/>(JWKS + X.509)"]
        Agent_A["SPIRE Agent A"]
        W_A["Workload A<br/>spiffe://prod.example.com/..."]
    end
    subgraph DomainB["Trust domain B — partner.example.net"]
        CA_B["Root CA_B<br/>bundle_B"]
        Agent_B["SPIRE Agent B"]
        W_B["Workload B<br/>spiffe://partner.example.net/..."]
    end
    subgraph Federation["Federation — bundle exchange"]
        BE["BundleEndpoint<br/>https://spire.prod.example.com/bundle<br/>+ JWKS at /.well-known/spiffe/bundle.json"]
        BA["BundleEndpoint<br/>https://spire.partner.example.net/bundle"]
    end

    CA_A --- BE
    CA_B --- BA
    BE -. "poll + pin (mTLS or JWT)" .-> Agent_B
    BA -. "poll + pin" .-> Agent_A

    W_A -- "mTLS — present SVID_A<br/>verify with bundle_A" --> W_B
    W_B -- "verify caller with bundle_A<br/>(federated bundle)" --> W_A

    style BE fill:#fa6,stroke:#333,color:#fff
    style BA fill:#fa6,stroke:#333,color:#fff
```

```yaml
# SPIRE server — federation config (SPIRE 1.9+)
server {
  trust_domain = "prod.example.com"
  federation {
    bundle_endpoint {
      address = "0.0.0.0"
      port = "8443"
      acme { domain_name = "spire.prod.example.com" }  # TLS for bundle endpoint
    }
    federates_with "partner.example.net" {
      bundle_endpoint_url = "https://spire.partner.example.net:8443"
      bundle_endpoint_profile "https_spiffe" {
        endpoint_spiffe_id = "spiffe://partner.example.net/spire/server"
      }
    }
  }
}

# Agent — fetches federated bundles for its trust domain
agent {
  trust_domain = "prod.example.com"
  # federated bundles appear alongside the local bundle via Workload API FetchBundle
}
```

Verification explicitly pins the federated bundle to a SPIFFE ID (`endpoint_spiffe_id`) or a CA — never `InsecureSkipVerify`. Rotation of a federated bundle is the same hot-reload path as the local bundle: the Agent watches `BundleEndpoint` and pushes updates to workloads via the Workload API stream.

> **JWT-SVID federation.** JWT-SVIDs use the same bundle exchange but carry the federated `iss` (`https://spire.prod.example.com`) and a `kid` that maps to the federated bundle's JWKS. Verifiers must check `iss` against the expected trust domain before accepting `sub`.

---

## Rotation, revocation, and the distributed-systems lens

### Rotation without restarts

Workload certs rotate *before* they expire — typically at ⅓ to ½ of the TTL. With SPIRE, the Agent pushes a new SVID over the existing Workload API stream; the workload's `X509Source` swaps `tls.Config.Certificates` atomically; established connections continue with the old cert until they close, new handshakes use the new one. No pod restart, no rolling deploy for rotation.

The CA rotation is longer-lived (24h–7d for the signing CA, months for the root) and uses **bundle updates**: the new root is added to the bundle alongside the old, both are distributed, workloads trust either during the overlap window, then the old is removed. The same overlap handles a compromised CA — publish a new root, distribute, then stop signing with the old.

### Revocation via short TTLs, not CRLs

Zero trust at fleet scale does not use CRLs or OCSP for workload certs — distribution latency and size make them impractical for 10k-workload fleets with 1h certs. Instead, SPIRE issues the shortest TTL the fleet can tolerate (1h, 5m for JWT-SVIDs) and revokes by *not re-issuing*: delete the registration entry or fail workload attestation, and the cert expires within one TTL. For immediate isolation, combine with mesh-level `AuthorizationPolicy` deny or a data-plane close (drain connections, deny at the sidecar) — the cert may remain technically valid for minutes, but the workload is already denied at the next hop.

### Blast radius and audit

- **Per-workload identity limits blast radius.** A compromised `payments` pod holds only `spiffe://prod/ns/payments/sa/payments-api` — it cannot forge `frontend`'s SVID, and mesh + application authZ denies it `frontend`→`payments` is not its grant. With shared secrets, one leaked key impersonates any service.
- **Log SPIFFE IDs, not IPs.** `source_ip: 10.4.2.88` is ephemeral and NAT'd; `caller_spiffe_id: spiffe://prod/ns/api/svc/frontend` is stable, auditable, and joins with deployment metadata. Emit it in access logs, traces (`peer.service` in OpenTelemetry), and error reviews (Ch 7) — it is the `request_id` for identity.
- **Break-glass.** Keep an audited break-glass identity (`spiffe://prod/ns/sre/sa/break-glass`) with a deliberately short TTL (5m) and an approval workflow (PAM/OIDC — Ch 6) that mints a one-time SVID via the SPIRE API. Every use is logged and alerted — unlike a shared SSH key or a subnet allowlist that has no per-use audit.

```mermaid
flowchart TB
    subgraph Rotation["Rotation — no restarts, no CRLs"]
        Cert1["X509-SVID issued<br/>TTL 1h, NotAfter T+1h"]
        Agent1["Agent stream<br/>push new SVID at T+40m"]
        Source1["X509Source<br/>atomic swap<br/>tls.Config updated"]
        Conn1["Existing mTLS conns<br/>stay open with old cert"]
        Conn2["New handshakes<br/>use new cert"]
        Cert1 --> Agent1 --> Source1
        Source1 --> Conn1
        Source1 --> Conn2
    end

    subgraph Revocation["Revocation — entry deletion + short TTL"]
        Del["Delete entry or<br/>fail attestation"]
        NoReissue["Agent stops re-issuing<br/>cert expires in ≤ TTL"]
        Deny["Mesh AuthorizationPolicy<br/>DENY or drain<br/>immediate isolation"]
        Del --> NoReissue
        Del --> Deny
    end

    subgraph CARotation["CA rotation — bundle overlap"]
        NewRoot["New root CA<br/>added to bundle<br/>both roots trusted"]
        Distr["Distribute bundle<br/>to all agents + workloads"]
        SignNew["New SVIDs signed<br/>with new CA"]
        RemoveOld["Old root removed<br/>after overlap window"]
        NewRoot --> Distr --> SignNew --> RemoveOld
    end
```

```mermaid
sequenceDiagram
    participant Pod as Workload pod
    participant Agent as SPIRE Agent
    participant Server as SPIRE Server
    participant Peer as Peer service (callee)

    Note over Pod,Peer: Steady state — mTLS with SPIFFE IDs
    Pod->>Peer: mTLS — present SVID (spiffe://prod/ns/api/svc/frontend)
    Peer->>Peer: Verify against bundle — SPIFFE ID allowed?

    Note over Pod,Server: Rotation — before expiry
    Agent-->>Pod: Stream: new X509-SVID + updated bundle
    Pod->>Pod: Atomic tls.Config swap
    Pod->>Peer: Next handshake uses new SVID
    Peer->>Peer: Bundle already has new root — verification passes

    Note over Pod,Peer: Revocation — compromise of Pod's node
    Server->>Agent: Registration entry deleted
    Agent-->>Pod: No re-issue — last SVID expires in ≤ 1h
    Peer->>Peer: AuthorizationPolicy DENY spiffe://prod/ns/compromised/*<br/>immediate isolation even within TTL

    Note over Pod,Peer: CA rotation — new root distributed
    Server-->>Agent: Bundle update: root_A_old + root_A_new
    Agent-->>Pod: Bundle: both roots trusted (overlap)
    Note over Pod,Peer: After overlap — old root removed
    Agent-->>Pod: Bundle: root_A_new only
```

---

## Putting it together — zero trust in a Kubernetes fleet

A minimal end-to-end checklist for a cluster that means it:

1. **Identity.** Deploy SPIRE server + agents (`k8s_psat` node attestation), `ClusterSPIFFEID` per workload. No workload holds a long-lived secret; every workload fetches via `Workload API`.
2. **Authentication.** Every service-to-service hop uses mTLS with `X509-SVID` — mesh (`PeerAuthentication STRICT`) or raw Envoy/go-spiffe. `PERMISSIVE` only during migration with a deadline and a burn-down metric.
3. **Authorization.** `AuthorizationPolicy` per callee by SPIFFE ID + path/method — not by IP/namespace. Application-level SPIFFE ID check as defense in depth.
4. **Rotation.** `default_x509_svid_ttl = 1h`, `default_jwt_svid_ttl = 5m`; workload `X509Source` hot-reloads; CA rotation via bundle overlap. No restart for rotation — alert if a pod's SVID is within 10m of expiry and not re-issued.
5. **Federation.** Publish `BundleEndpoint`, pin by SPIFFE ID/CA, import partner bundles — verify `iss` on JWT-SVIDs.
6. **Observability.** Access logs and traces carry `caller_spiffe_id` and `callee_spiffe_id`; metric `istio_requests_total{source_principal, destination_principal, response_code}` (Istio) or `envoy_cluster_ssl_connection_error` + RBAC `shadow_denied` for policy impact before enforcement.
7. **Break-glass.** Short-lived SVID mint via SPIRE API gated by OIDC + approval; every use audited; TTL 5m.

---



#### mTLS with SPIFFE

```mermaid
sequenceDiagram
    participant W as Workload
    participant Agent as SPIRE Agent
    participant Server as SPIRE Server
    participant Peer as Peer workload
    W->>Agent: request SVID
    Agent->>Server: attest + sign CSR
    Server-->>Agent: X509 SVID spiffe://trust/svc
    Agent-->>W: SVID + bundle
    W->>Peer: mTLS handshake with SVID
    Peer->>Peer: verify SVID + bundle + policy
```

#### Zero Trust Policy Evaluation

```mermaid
flowchart TB
    Req["Request with<br/>mTLS SVID"] --> AuthN["AuthN: verify cert<br/>+ SPIFFE ID"]
    AuthN --> Device["Device / workload posture"]
    Device --> Policy["Policy engine<br/>OPA / Cedar"]
    Policy -->|allow| Allow["Allow + audit"]
    Policy -->|deny| Deny["Deny + alert"]
```

## Key takeaways

- Zero trust replaces network trust with workload identity + mutual authentication + identity-based authorization on every hop. The network is never a trust boundary — identity (SPIFFE ID) is.
- mTLS is the authentication hop: both sides present and verify an X.509 SVID, prove possession with `CertificateVerify`, and pin the peer's URI SAN (SPIFFE ID) against a trusted bundle. Server-only TLS is not zero trust — the server must also authenticate the caller.
- SPIFFE gives the universal identity (`spiffe://trust-domain/path`); SPIRE is the fleet issuer — node attestation (`k8s_psat`) proves the node, workload attestation (k8s selectors) proves the pod, the `Workload API` Unix socket delivers and rotates `X509-SVID`s and `JWT-SVID`s, and the bundle is the trust anchor. Short TTLs (1h X.509, 5m JWT) replace CRLs.
- On Kubernetes, run SPIRE server (StatefulSet, `k8s_psat`, Postgres/SQLite, `disk` KeyManager) and agents (DaemonSet, `k8s` workload attestation), `ClusterSPIFFEID` per workload, and mount the `Workload API` socket via the SPIFFE CSI driver — workloads fetch with `go-spiffe`/`java-spiffe` `X509Source` and hot-reload on rotation without restarts.
- Enforce with mesh policy (`PeerAuthentication STRICT` + `AuthorizationPolicy` by `principals` SPIFFE IDs) and raw Envoy `transport_socket` + `RBAC` where no mesh control plane exists; keep an application-level SPIFFE ID check for defense in depth so a misconfigured mesh does not silently authorize.
- Federate trust domains by exchanging bundles via `BundleEndpoint` (pin by SPIFFE ID/CA), import federated bundles on agents, and verify JWT-SVID `iss` against the expected trust domain — no shared CA. Rotate CAs via bundle overlap (both roots trusted during the window).
- Operate the distributed-systems properties: rotation without restarts (Workload API stream + `X509Source` atomic swap), revocation by entry deletion + short TTL plus immediate mesh `DENY`/drain, logging and tracing by SPIFFE ID (not IP), per-principal metrics, canary `AUDIT`/`shadow` policy before `STRICT`, and a short-lived break-glass SVID gated by OIDC with full audit.

## Further reading

- SPIFFE — Concepts, SPIFFE ID, SVID, Workload API, Federation. https://spiffe.io/docs/latest/spiffe-about/overview/ / https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE.md
- SPIRE — Architecture, deployment, attestation, registration, federation. https://spiffe.io/docs/latest/spire-about/overview/ / https://github.com/spiffe/spire
- SPIRE on Kubernetes — `k8s_psat`, `ClusterSPIFFEID`, CSI driver. https://spiffe.io/docs/latest/deploying/spire-for-k8s/
- `go-spiffe/v2` / `java-spiffe` — `X509Source`, `JWTSource`, `tlsconfig`. https://github.com/spiffe/go-spiffe / https://github.com/spiffe/java-spiffe
- Envoy — TLS/mTLS, SDS, RBAC (`transport_socket`, `validation_context`, `SdsSecretConfig`). https://www.envoyproxy.io/docs/envoy/latest/api-v3/extensions/transport_sockets/tls/v3/tls.proto / https://www.envoyproxy.io/docs/envoy/latest/configuration/security/rbac
- Istio — `PeerAuthentication`, `AuthorizationPolicy`, SPIRE CA integration. https://istio.io/latest/docs/reference/config/security/peer_authentication/ / https://istio.io/latest/docs/reference/config/security/authorization-policy/ / https://istio.io/latest/docs/concepts/security/
- NIST SP 800-207 — Zero Trust Architecture. https://doi.org/10.6028/NIST.SP.800-207
- BeyondCorp / Google Zero Trust — BeyondProd, context-aware access. https://cloud.google.com/beyondcorp / https://research.google/pubs/beyondcorp-a-new-approach-to-enterprise-security/
- Cilium / Linkerd — eBPF and mTLS/identity alternatives. https://docs.cilium.io/en/stable/security/network/encryption/ / https://linkerd.io/2/features/automatic-mtls/
- Smallstep — `step-ca`, SPIFFE-aware CA, mTLS tooling. https://smallstep.com/docs/step-ca/
- RFC 8446 — TLS 1.3 (mTLS handshake). https://www.rfc-editor.org/rfc/rfc8446.html
- RFC 5280 — X.509 Certificates and CRLs. https://www.rfc-editor.org/rfc/rfc5280.html
- Vol 3, Ch 6 — TLS 1.3 and the Web PKI (handshake mechanics). Vol 9, Ch 4 — PKI/TLS operations. Vol 9, Ch 7 — Authorization by workload identity. Vol 9, Ch 8 — Secrets management.

