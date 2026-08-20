# Chapter 8 — Secrets Management

**What this chapter covers.** Every backend system is a lattice of secrets — database passwords, API keys, TLS private keys (Ch 4), signing keys (Ch 3), OAuth client secrets (Ch 6), encryption DEKs/KEKs (Ch 3), and the tokens that carry identity (Ch 5). A secret is any value whose disclosure breaks a security property, and managing secrets is managing their entire lifecycle: generation, distribution, storage, rotation, revocation, and audit — across dozens of services, multiple environments, CI/CD pipelines, and ephemeral compute that may live for seconds. Hard-coded credentials and long-lived static secrets remain the most common breach vector not because engineers do not know better, but because the easy path leaks. This chapter builds a disciplined secrets plane: envelope encryption, Vault (HashiCorp Vault 1.15+ / OpenBao) as the central secrets manager, dynamic and short-lived credentials, distribution via agent/sidecar/CSI, rotation without downtime, detection and remediation of leaked secrets, and the distributed-systems reality of secret replication, blast radius, and availability when the secrets store itself is a dependency of every service.

Learning goals — after this chapter you should be able to:

- Classify secrets by kind, lifetime, and blast radius — and explain why static, long-lived secrets are the wrong default for any credential that can be made dynamic or short-lived.
- Operate Vault/OpenBao 1.15+ for KV v2, Transit, PKI, and database dynamic credentials — policies, auth methods (AppRole, Kubernetes, JWT/OIDC, AWS IAM), response wrapping, and audit devices.
- Distinguish encryption at rest (envelope encryption with KMS/HSM), encryption in transit (TLS per Ch 4), and secret distribution — and implement each correctly.
- Distribute secrets to workloads via Vault Agent, Agent Injector, Secrets Store CSI Driver, and External Secrets Operator — and compare their lifecycle and failure modes.
- Implement rotation — automated, staggered, dual-credential, and lease-based — for database passwords, API keys, and certificates without downtime, and plan emergency revocation.
- Detect leaked secrets in git, logs, and artifacts (gitleaks, TruffleHog, GitHub secret scanning) and remediate by rotation, not redaction.
- Design the secrets plane for scale — HA Vault clusters (Raft integrated storage), replication, seal/unseal with auto-unseal (KMS/Shamir), and the availability trade-off when Vault is a hard dependency.

> **Boundary notes.** *Cryptographic primitives* (AEAD, KDFs, hashing) are **Ch 1–3** — this chapter consumes them via envelope encryption and compares secret storage to key management (Ch 3's KEK/DEK hierarchy reappears as Vault's barrier key / recovery key). *PKI and TLS private keys* are **Ch 4** (certificate lifecycle, rotation, mTLS); this chapter covers how those private keys are stored and distributed, not how X.509 chains validate. *Authentication tokens* (sessions, JWTs, OAuth) are **Ch 5–6**; this chapter stores the secrets that *mint* those tokens (signing keys, client secrets) and the dynamic credentials that replace static passwords. *Build/CI secrets* (pipeline poisoning, OIDC workload identity for CI) are covered in Companion Book 4; this chapter focuses on runtime secrets, including CI as one consumer. *Workload identity* (SPIFFE/SPIRE, mTLS) is **Ch 10** — the preferred replacement for many long-lived secrets. *Threat modeling* secrets as assets is **Ch 11**.

## Why secrets management is a lifecycle, not a vault

Putting secrets in a vault is necessary but not sufficient. A secret has six phases, and a failure at any one is a breach:

```
Generate → Store → Distribute → Use → Rotate → Revoke/Audit
```

- **Generate** with a CSPRNG (Ch 1) or via the secrets manager itself (Vault `gen/creds`). Never derive from weak entropy, timestamps, or `math/rand`.
- **Store** encrypted at rest with envelope encryption, with access control (Vault policies, not broad IAM), and with audit logging on every read.
- **Distribute** over TLS (Ch 4) to the workload that needs it, with minimal scope (one service gets one database role, not `root`), minimal lifetime (minutes–hours, not months), and no persistence in env vars that leak to `/proc` or crash dumps.
- **Use** in memory only, never logged, never echoed in error messages, never returned in API responses. Mask in observability.
- **Rotate** automatically, with dual-credential overlap so rotation does not require coordinated downtime.
- **Revoke/audit** instantly on suspicion, with a bounded propagation window and a log of who read what, when, from where.

The naive path — `.env` file, Kubernetes `Secret` (base64), environment variable, checked into git — fails at every phase: generation is ad-hoc, storage is plaintext (etcd at rest is not encrypted by default), distribution is a copy, use leaks to logs, rotation is manual (so it never happens), and revocation is "change the password and redeploy everything at 2 a.m."

This chapter replaces each phase with a concrete mechanism.

## What counts as a secret

| Class | Examples | Lifetime that is safe | Replacement |
|---|---|---|---|
| **Database credentials** | Postgres/MySQL passwords, connection strings | Minutes–hours (dynamic) | Vault database engine — per-service, per-pod ephemeral creds |
| **API keys / tokens** | Stripe, AWS, GitHub PATs, internal service tokens | Hours–days, scoped | Vault KV + rotation, or OIDC workload identity (Ch 10) |
| **TLS private keys** | Server leaf keys, mTLS client keys (Ch 4) | Hours (SPIRE) to 90 days (ACME) | Vault PKI / SPIRE SVID — short-lived, auto-renewed |
| **Signing keys** | JWT signing keys (Ch 5), image signing keys (Companion Book 5) | Days–months, versioned (`kid`) | Vault Transit / KMS — sign via API, key never leaves HSM |
| **Encryption keys** | DEKs, KEKs (Ch 3) | DEK per object, KEK per scope | Envelope encryption — KEK in KMS/HSM, DEK wrapped |
| **CI/CD secrets** | Registry passwords, deploy keys, cloud credentials | Minutes (OIDC-federated) | OIDC workload identity — no static secret at all |
| **Human credentials** | Break-glass passwords, recovery codes | One-time, sealed | Vault Cubbyhole / Shamir split, break-glass audit |

Rule of thumb: if the secret *can* be made dynamic and short-lived, it *should* be. Static secrets are technical debt that accrues breach risk with age.

## Envelope encryption: how secrets rest safely

A secrets manager does not just "encrypt the database" — it uses **envelope encryption**, the same KEK/DEK hierarchy from Ch 3, now applied to the storage layer.

```mermaid
flowchart TB
    subgraph KMS["KMS / HSM (Root of Trust)"]
        KEK["KEK (never leaves KMS)<br/>e.g., AWS KMS CMK, GCP KMS, HSM"]
    end
    subgraph Vault["Vault Barrier"]
        DEK["DEK (data encryption key)<br/>AES-256-GCM, rotated periodically"]
        Barrier["Barrier-encrypted storage<br/>Raft / etcd / Consul"]
    end
    subgraph Payload["Secret Payload"]
        S["Secret value<br/>db_password=..."]
        Enc["AEAD ciphertext<br/>nonce + ciphertext + tag"]
    end

    KEK -- "wraps (Encrypt API)" --> DEK
    DEK -- "AEAD encrypts" --> Enc
    Enc --> Barrier
    S --> Enc

    KMS -.->|"auto-unseal<br >on restart"| Vault

    style KEK fill:#ffcccc
    style DEK fill:#fff3cd
    style Enc fill:#d4edda
```

- The **KEK** lives in a KMS/HSM and never leaves it. Vault calls `Encrypt`/`Decrypt` via the KMS API. Compromise of the Vault host does not expose the KEK.
- The **DEK** (Vault calls it the *barrier key*) encrypts the Raft storage. Rotating the DEK re-wraps storage without re-encrypting every secret — only the DEK wrapper changes.
- **Auto-unseal** (Vault 1.15+ `seal "awskms"` / `seal "gcpckms"` / `seal "transit"`) removes the manual Shamir unseal ceremony. The Vault process fetches the barrier key from KMS on start. For break-glass without KMS, Shamir seals (`threshold=3, shares=5`) remain an option — store shards with separate custodians.

For application-layer secrets (e.g., encrypting a column before it reaches Vault), use the same pattern explicitly — Vault Transit is the service that does it:

```bash
# Vault Transit 1.15+ — envelope encryption as a service
vault secrets enable transit
vault write -f transit/keys/app-dek exportable=false type=aes256-gcm96

# App encrypts via Transit — DEK never leaves Vault
vault write transit/encrypt/app-dek plaintext=$(base64 <<< "sensitive payload")
# → ciphertext: vault:v1:...

vault write transit/decrypt/app-dek ciphertext="vault:v1:..."
```

This keeps DEKs out of application memory and makes rotation a Vault API call, not a re-encryption migration.

## Vault as the control plane

HashiCorp Vault (1.15+; OpenBao is the open-source fork under the same API — either is fine) is the de facto control plane. Its architecture maps directly to the lifecycle above.

```mermaid
flowchart TB
    subgraph Clients["Clients"]
        App["App Workload<br/>(K8s Pod, VM, Lambda)"]
        CI["CI Runner"]
        Human["Operator<br/>(break-glass)"]
    end
    subgraph Vault["Vault Cluster (HA, Raft)"]
        Auth["Auth Methods<br/>k8s / jwt / approle / aws / userpass"]
        Policy["Policies (HCL)<br/>path-based ACL"]
        Audit["Audit Devices<br/>file / syslog / socket"]
        Engines["Secrets Engines<br/>kv-v2 / transit / pki / database / aws"]
        Lease["Lease Manager<br/>TTL, renewal, revocation"]
    end
    subgraph Storage["Storage"]
        Raft["Raft Integrated Storage<br/>(replicated, bolt)"]
        KMS2["KMS Auto-Unseal"]
    end

    App --> Auth --> Policy --> Engines --> Lease --> Audit
    CI --> Auth
    Human --> Auth
    Engines --> Raft
    Vault -.-> KMS2

    style Auth fill:#dff0ff
    style Policy fill:#fff3cd
    style Audit fill:#d4edda
```

### Policies (version-pinned: HCL, Vault 1.15+)

Policies are path-based ACLs. Every token's capabilities derive from exactly the policies attached to it — no policy, no access.

```hcl
# vault/policy/app-payments.hcl — scoped to one service, one env
path "kv/data/payments/prod/*" {
  capabilities = ["read"]
}
path "kv/data/payments/prod/api-keys/*" {
  capabilities = ["read"]
}
# Transit encrypt/decrypt — key never leaves Vault
path "transit/encrypt/app-dek" { capabilities = ["update"] }
path "transit/decrypt/app-dek" { capabilities = ["update"] }
# Dynamic DB creds — read-only role
path "database/creds/payments-ro" {
  capabilities = ["read"]
}
# Renew own lease only
path "sys/leases/renew" { capabilities = ["update"] }
path "sys/leases/revoke" { capabilities = ["update"] }

# Explicit deny trumps allow — block prod secrets from staging identity
path "kv/data/payments/prod/*" {
  capabilities = ["deny"]
  # Applied via a staging policy that is never attached to prod roles
}

# Write:
# vault policy write app-payments vault/policy/app-payments.hcl
```

Attach policies to roles, not to tokens directly. Roles bind an auth method to a policy set:

```bash
# Kubernetes auth — Vault 1.15+ (vault auth enable kubernetes)
vault auth enable kubernetes
vault write auth/kubernetes/config kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443"

vault write auth/kubernetes/role/payments-prod \
    bound_service_account_names=payments \
    bound_service_account_namespaces=prod \
    policies=app-payments \
    ttl=15m max_ttl=1h period=15m \
    token_type=batch  # batch tokens: lightweight, non-renewable, ~30% lower overhead

# AppRole for VMs / non-K8s
vault auth enable approle
vault write auth/approle/role/payments-prod \
    token_policies=app-payments token_ttl=15m token_max_ttl=1h \
    secret_id_ttl=10m token_type=batch

# JWT/OIDC for CI (GitHub Actions, GitLab) — no static secret at all
vault auth enable jwt
vault write auth/jwt/config oidc_discovery_url="https://token.actions.githubusercontent.com"
vault write auth/jwt/role/github-deploy \
    bound_audiences="https://github.com/example-org" \
    bound_claims='{"repository":"example-org/payments"}' \
    policies=ci-deploy ttl=5m max_ttl=5m
```

The `ttl`/`max_ttl` on the role *is* the blast-radius control — a leaked token is useful for at most `max_ttl`.

### Auth methods: choosing correctly

| Method | Use when | Token type | Rotation |
|---|---|---|---|
| **Kubernetes** (`k8s`) | Workload is a Pod with a ServiceAccount JWT | `batch` (short) | Automatic via SA token projection (hourly) |
| **JWT/OIDC** | CI runner, serverless, any OIDC issuer | `batch` | Per-run, no persistence |
| **AppRole** | VM, bare metal, non-K8s host | `batch` or `service` | `secret_id` rotation via automation |
| **AWS IAM** | EC2/ECS/Lambda with instance role | `batch` | IAM role session (hours) |
| **Userpass / LDAP** | Break-glass human | `service` (renewable) | Manual + MFA (TOTP per Ch 5) |

Prefer `batch` tokens for workloads — they are not persisted in Vault storage, cannot be renewed, and have lower overhead. Use `service` tokens only for long-lived human or controller identities that need renewal.

### Secrets engines

**KV v2** (`kv/data/...`) — the generic encrypted store. Versioned, with `max_versions`, `delete_version_after`, and `cas` (check-and-set) for safe concurrent writes:

```bash
vault secrets enable -path=kv kv-v2
vault kv put kv/payments/prod/db host=db.prod.example.com password="$(openssl rand -base64 32)"
vault kv get kv/payments/prod/db
vault kv metadata put -max-versions=10 -delete-version-after=720h kv/payments/prod/db
```

**Transit** — encryption as a service (above). Use for app-layer envelope encryption and for signing (`transit/sign`, `transit/hmac`).

**PKI** — internal CA for short-lived certs (Ch 4). Issue SPIFFE-compatible SVIDs or private TLS leaves with `ttl=1h`:

```bash
vault secrets enable pki
vault write pki/root/generate internal common_name="prod.example.com" ttl=87600h
vault write pki/roles/app-server allow_any_name=true max_ttl=24h server_flag=true client_flag=false
vault write pki/issue/app-server common_name="payments.prod.example.com" ttl=1h
```

**Database** — dynamic, ephemeral credentials. Vault creates a temporary user, grants a role, and revokes on lease expiry:

```bash
vault secrets enable database
vault write database/config/pg-prod \
    plugin_name=postgresql-database-plugin \
    connection_url="postgresql://{{username}}:{{password}}@pg.prod.example.com:5432/payments?sslmode=require" \
    username="vault_admin" password="$VAULT_ADMIN_PW" \
    allowed_roles="payments-ro,payments-rw"

vault write database/roles/payments-ro \
    db_name=pg-prod \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    revocation_statements="DROP ROLE IF EXISTS \"{{name}}\";" \
    default_ttl=15m max_ttl=1h
```

Every `vault read database/creds/payments-ro` mints a unique `(username, password)` valid for `15 m`, auto-dropped on lease expiry. No static password to leak.

## Distributing secrets to workloads

Storing secrets in Vault is half the job; getting them to the workload without reintroducing the leaks you just fixed is the other half. Four patterns dominate in 2024–2026:

| Pattern | How it works | Secret appears as | Rotation | Failure mode |
|---|---|---|---|---|
| **Vault Agent (sidecar)** | Sidecar authenticates, renders templates to `tmpfs` | File on `emptyDir: medium: Memory` | Agent re-renders on lease renewal | Agent crash → stale file; monitor `vault_agent_cache_hit` |
| **Agent Injector (mutating webhook)** | Webhook injects Agent sidecar + annotations | File (same) | Same as Agent | Webhook down → pods start without secrets (fail-closed is correct) |
| **Secrets Store CSI Driver** | CSI volume mounts secrets as files | File (tmpfs) | CSI rotation (`rotationPollInterval: 2m`) | Driver DaemonSet down → mount fails |
| **External Secrets Operator (ESO)** | Controller syncs Vault → K8s `Secret` | Native `Secret` (etcd, base64) | `refreshInterval: 1h` | ESO down → stale `Secret`; etcd at rest must be encrypted |

All four are production-grade; the choice is blast-radius and ergonomics:

- For **new K8s workloads**, prefer **CSI Driver** or **Agent Injector** — secrets never become Kubernetes `Secret` objects, never land in etcd, and are `tmpfs`-only.
- For **existing workloads that already consume `Secret` env vars**, **ESO** is the migration path — it replaces manual `kubectl create secret` with automated sync and gives you a single control plane while you migrate to file mounts.

```yaml
# Vault Agent Injector — annotation-driven (Vault 1.15+, vault-k8s 1.4+)
apiVersion: apps/v1
kind: Deployment
metadata: { name: payments, namespace: prod }
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/agent-inject-secret-db: "kv/data/payments/prod/db"
        vault.hashicorp.com/agent-inject-template-db: |
          {{`{{- with secret "kv/data/payments/prod/db" -}}`}}
          host={{`{{ .Data.data.host }}`}}
          password={{`{{ .Data.data.password }}`}}
          {{`{{- end }}`}}
        vault.hashicorp.com/role: "payments-prod"
        vault.hashicorp.com/agent-cache-enable: "true"
        # Template rendered to /vault/secrets/db (tmpfs), re-rendered on renewal
    spec:
      serviceAccountName: payments
      containers:
      - name: app
        image: registry.example.com/payments:1.42.0
        # App reads /vault/secrets/db — never an env var
        volumeMounts: [{ name: vault-secrets, mountPath: /vault/secrets }]
---
# Secrets Store CSI Driver — Vault provider (secrets-store.csi.k8s.io v1.4+)
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata: { name: vault-db, namespace: prod }
spec:
  provider: vault
  parameters:
    vaultAddress: "https://vault.prod.example.com:8200"
    roleName: "payments-prod"
    objects: |
      - objectName: "db-password"
        secretPath: "kv/data/payments/prod/db"
        secretKey: "password"
  # Optional: sync to K8s Secret for legacy consumers — avoid if possible
  # secretObjects:
  # - secretName: payments-db
  #   type: Opaque
  #   data:
  #   - objectName: db-password
  #     key: password
---
# ESO — Vault → K8s Secret sync (external-secrets.io v0.9+)
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: payments-db, namespace: prod }
spec:
  refreshInterval: 5m
  secretStoreRef: { name: vault-backend, kind: ClusterSecretStore }
  target:
    name: payments-db          # K8s Secret that is created/updated
    creationPolicy: Owner
    deletionPolicy: Retain
  data:
  - secretKey: password
    remoteRef: { key: kv/payments/prod/db, property: password }
```

Application consumption — read from file, never from env:

```go
// Go 1.22 — read secret from Vault Agent / CSI tmpfs file
// File is rendered as KEY=VALUE or JSON; never logged, never returned in errors.

func loadDBPassword(path string) (string, error) {
    b, err := os.ReadFile(path) // /vault/secrets/db or /mnt/secrets-store/db-password
    if err != nil {
        return "", fmt.Errorf("read secret: %w", err) // do not include file content
    }
    // If template rendered as KEY=VALUE, parse; if raw value, trim space.
    // Keep in memory only as long as needed; zero after use if held in []byte.
    pw := strings.TrimSpace(string(b))
    // Explicitly clear the byte slice that held the raw read
    for i := range b {
        b[i] = 0
    }
    if pw == "" {
        return "", errors.New("empty secret")
    }
    return pw, nil
}
```

Hardening checklist for distribution:

- **No env vars for secrets.** Env vars leak to `/proc/<pid>/environ`, crash dumps, and child processes. Files on `tmpfs` with `0400` are the correct target.
- **`tmpfs` only.** `emptyDir: { medium: Memory }` or CSI `tmpfs` — never a persistent volume. Secrets must not survive pod rescheduling on disk.
- **No logging.** Scrub `password`, `token`, `secret` keys from structured logs. Test with a canary secret and grep logs for its value in CI.
- **Response wrapping for bootstrapping.** When a human or CI must hand a secret to a workload, use Vault response wrapping (`vault read -wrap-ttl=5m ...`) — the wrapping token is single-use and short-lived, not the secret itself.

## Rotation: the only remediation that matters

Redacting a leaked secret from git history does not revoke it. **Rotation is remediation** — every other action is hygiene.

### Principles

1. **Dual-credential overlap.** At any moment, `N` and `N+1` are both valid for a window (minutes–hours). Writers use `N+1` immediately; readers accept both; after the window, `N` is revoked. No coordinated restart.
2. **Automated, not manual.** If rotation requires a human, it will not happen before the incident. Automate via Vault leases, ESO `refreshInterval`, or a rotation controller; alert on `vault_lease_expiry` and `secret_age_days`.
3. **Staggered.** Rotate one shard/region/service at a time. A fleet-wide rotation that breaks one service should not break all of them simultaneously.
4. **Lease-based where possible.** Dynamic credentials (Vault database engine) rotate by construction — the lease *is* the rotation. Prefer leases over cron.

```mermaid
sequenceDiagram
    participant Rotator as Rotation Controller
    participant Vault
    participant DB as Postgres
    participant App as App Pods (rolling)

    Rotator->>Vault: Generate new password (N+1)<br/>kv put / kv patch
    Vault-->>Rotator: version N+1, Zookie/revision
    Rotator->>DB: ALTER USER app WITH PASSWORD 'N+1'<br/>(both N and N+1 accepted during window)
    Note over DB: Dual-password window (e.g., 10m)<br/>some extensions support this natively,<br/>otherwise keep two roles active
    Rotator->>App: Rolling update — new pods read N+1<br/>old pods still on N, both valid
    App-->>Rotator: All pods on N+1 (readiness probes)
    Rotator->>Vault: Revoke / delete version N<br/>DB: drop old password
    Note over Rotator,App: Staggered per shard/region
```

### Concrete rotation patterns

**Database — dynamic credentials (preferred, no rotation needed beyond lease):**

```go
// Go — Vault database dynamic creds with lease renewal
import vault "github.com/hashicorp/vault/api"

func dbWithDynamicCreds(vaultAddr, role string) (*sql.DB, error) {
    vc, _ := vault.NewClient(&vault.Config{Address: vaultAddr})
    // Auth via K8s / JWT / AppRole — Vault Agent handles this; app reads VAULT_TOKEN file
    secret, err := vc.Logical().Read("database/creds/" + role) // "payments-ro"
    if err != nil || secret == nil {
        return nil, fmt.Errorf("mint creds: %w", err)
    }
    username := secret.Data["username"].(string)
    password := secret.Data["password"].(string)
    leaseID := secret.LeaseID
    leaseDuration := time.Duration(secret.LeaseDuration) * time.Second

    dsn := fmt.Sprintf("postgres://%s:%s@pg.prod.example.com:5432/payments?sslmode=require",
        url.QueryEscape(username), url.QueryEscape(password))
    db, err := sql.Open("pgx", dsn)
    if err != nil {
        return nil, err
    }

    // Renew lease in background; on failure, re-mint (Vault revokes old user on lease expiry)
    go func() {
        ticker := time.NewTicker(leaseDuration / 2)
        defer ticker.Stop()
        for range ticker.C {
            s, err := vc.Sys().Renew(leaseID, 0)
            if err != nil || s == nil {
                slog.Error("lease renewal failed, re-minting", "err", err)
                // Re-mint path: Read new creds, open new *sql.DB, drain old pool
                return
            }
            // Update ticker to half of new duration
            ticker.Reset(time.Duration(s.LeaseDuration/2) * time.Second)
        }
    }()
    return db, nil
}
```

**Static API key — automated rotation via Vault + controller:**

```yaml
# Kubernetes CronJob that rotates a Stripe-like API key every 30d (staggered)
apiVersion: batch/v1
kind: CronJob
metadata: { name: rotate-stripe-key, namespace: prod }
spec:
  schedule: "0 3 1 * *"   # monthly — plus on-demand via `kubectl create job`
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: rotator
          restartPolicy: OnFailure
          containers:
          - name: rotator
            image: registry.example.com/rotator:1.2.0
            env:
            - name: VAULT_ADDR
              value: "https://vault.prod.example.com:8200"
            command:
            - /bin/sh
            - -c
            - |
              set -euo pipefail
              # 1. Mint new key at provider (Stripe example)
              NEW_KEY=$(stripe_generate_key --scope payments)
              # 2. Write to Vault as new version (KV v2 keeps history)
              vault kv put kv/payments/prod/stripe api_key="$NEW_KEY" rotated_at="$(date -u +%FT%TZ)"
              # 3. Dual-key window: keep old key valid at provider for 1h
              #    (provider-specific — Stripe: keep both keys active briefly)
              # 4. Trigger rolling update so pods pick up new version
              kubectl rollout restart deployment/payments -n prod
              kubectl rollout status deployment/payments -n prod --timeout=300s
              # 5. Revoke old key at provider after rollout succeeds
              stripe_revoke_key "$OLD_KEY_ID"
```

**JWKS / signing keys** — see Ch 5. Rotate by adding `kid=N+1` alongside `kid=N`, deploy verifiers (RS) first, then start signing with `N+1`, then retire `N` after `max_token_lifetime`.

### Emergency revocation

When a secret is known-compromised, rotation speed is containment:

1. **Revoke the lease / delete the version** — `vault lease revoke -prefix database/creds/` or `vault kv delete kv/payments/prod/db` + `vault kv destroy` (permanent). For dynamic DB creds, lease revocation drops the database user immediately.
2. **Push a config-plane blocklist** — for tokens/JWTs, add the `jti`/`kid` to a blocklist distributed via config (Ch 4 pattern). Assume Vault revocation alone is not instant for already-issued tokens.
3. **Force workload restart** — `kubectl rollout restart` fleet-wide. Do not wait for `refreshInterval` — the compromised value is in memory.
4. **Rotate the KEK if scope warrants it** — if the Vault barrier or transit KEK is suspected, re-wrap via KMS. This is rare but must be rehearsed.

## Detecting leaked secrets

Prevention fails without detection. Three layers:

**Pre-commit / pre-push:**

```yaml
# .pre-commit-config.yaml — gitleaks 8.18+ (github.com/gitleaks/gitleaks)
repos:
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.18.4
  hooks:
  - id: gitleaks
# TruffleHog 3.70+ as CI fallback
# trufflehog git --since-commit HEAD~1 --fail --only-verified
```

**CI / repo scanning:**

```bash
# gitleaks in CI — scans the diff, not just HEAD
gitleaks detect --source . --verbose --redact --max-target-megabytes 100

# TruffleHog verified-only (reduces false positives — only reports creds that actually authenticate)
trufflehog git file://. --only-verified --fail

# GitHub secret scanning (push protection) — enable at org level:
# Settings → Code security → Secret scanning → Push protection (blocks push that contains a secret)
```

**Runtime / artifact scanning:**

```bash
# Scan container images and logs for accidental secret inclusion
trufflehog docker --image registry.example.com/payments:1.42.0 --only-verified
gitleaks detect --source /var/log/app --no-git
```

When a leak is found, the runbook is the same every time: **rotate, do not redact.** Rewriting git history (`filter-repo`) without rotating leaves the secret valid in every clone, fork, and CI cache that already fetched it. Rotate first, then clean history to reduce future exposure.

## Vault at scale: HA, replication, and the availability trade-off

Vault is a hard dependency — if Vault is down, no pod can mint a new database password, no sidecar can render a new secret, and no rotation can complete. Design for its availability explicitly.

```mermaid
flowchart TB
    subgraph Primary["Primary Cluster (prod-us)"]
        V1["Vault Active<br/>(Raft leader)"]
        V2["Vault Standby"]
        V3["Vault Standby"]
        Raft1["Raft Storage<br/>(replicated)"]
        KMS1["KMS Auto-Unseal<br/>(us KMS)"]
        V1 --> Raft1
        V2 --> Raft1
        V3 --> Raft1
        V1 -.-> KMS1
    end
    subgraph DR["DR / Secondary (prod-eu)"]
        VS["Vault Secondary<br/>(replication follower)"]
        Raft2["Raft Storage (replicated)"]
        KMS2["KMS Auto-Unseal<br/>(eu KMS)"]
        VS --> Raft2
        VS -.-> KMS2
    end
    Primary -.->|"Vault Replication<br > performance + DR "| DR
    V1 --> App1["App Fleet"]
    VS --> App2["EU Fleet<br/>(local reads)"]

    style V1 fill:#d4edda
    style VS fill:#fff3cd
```

- **Raft integrated storage** (Vault 1.15+ default) — no external Consul/etcd. Three or five voters, `retry_join` for auto-clustering, `autopilot` for dead-server cleanup. Back up Raft snapshots to S3/GCS (`vault operator raft snapshot save`).
- **Performance replication** — secondary clusters serve reads locally (KV, Transit) without forwarding to primary. Required for multi-region latency — a `5 ms` local read vs `80 ms` cross-region.
- **DR replication** — async WAL shipping for failover. Promote secondary if primary region is lost. Test promotion — a DR cluster you have never promoted is a hope, not a plan.
- **Seal HA.** KMS auto-unseal must itself be multi-region or the KMS region outage seals Vault. Use KMS multi-region keys or Shamir as fallback.
- **Caching and graceful degradation.** Vault Agent cache (`cache { use_auto_auth_token = true }`) and `proxy_cache` let workloads survive a brief Vault outage with cached leases. Size cache TTLs to cover your p99 Vault recovery time, and alert on `vault_core_unsealed` and `vault_raft_autopilot_healthy`.

Operational metrics to export and alert on:

```yaml
# Prometheus alerts for the secrets plane
groups:
- name: vault
  rules:
  - alert: VaultSealed
    expr: vault_core_unsealed == 0
    for: 1m
    labels: { severity: critical }
  - alert: VaultLeaseExpiryStalled
    expr: increase(vault_expire_num_leases{success="false"}[5m]) > 0
    labels: { severity: warning }
  - alert: SecretAgeTooHigh
    expr: (time() - vault_kv_version_created_time) / 86400 > 30
    for: 1h
    labels: { severity: warning }
    annotations: { summary: "Secret {{ $labels.path }} not rotated in 30d" }
  - alert: VaultRaftLag
    expr: vault_raft_autopilot_healthy == 0
    for: 5m
    labels: { severity: critical }
```

## Kubernetes and cloud-native hardening

- **etcd encryption at rest.** Kubernetes `Secret` is base64, not encrypted, unless you enable `EncryptionConfiguration` with a KMS provider:

```yaml
# EncryptionConfiguration — KMS provider (Kubernetes 1.29+)
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources: [secrets]
  providers:
  - kms:
      apiVersion: v2
      name: aws-kms
      endpoint: unix:///var/run/kms-plugin/socket.sock  # aws-encryption-provider
      cachesize: 1000
      timeout: 3s
  - aesgcm:  # fallback — key in local file, weaker than KMS
    - name: fallback
      keys: [{ name: key1, secret: <base64-32-bytes> }]
```

Without this, anyone with etcd read or snapshot access reads every `Secret` in plaintext.

- **RBAC on Secrets.** No `get/list` on `Secrets` for broad roles. Audit `ClusterRole` bindings that include `secrets`:

```bash
kubectl auth can-i --list --as=system:serviceaccount:default:default | grep secrets
# Any unexpected "yes" is a finding.
```

- **Cloud workload identity over static cloud keys.** No `AWS_ACCESS_KEY_ID` in Vault if you can use IRSA (EKS), Workload Identity (GKE), or Managed Identity (AKS) — Vault's `aws` secrets engine can vend STS credentials instead, or eliminate the secret entirely via OIDC federation (Ch 10).

## Distributed-systems lens

- **Secrets are a consistency and blast-radius problem.** A database password change must propagate to every replica's connection pool within a bounded window. Dynamic credentials with short leases make the window explicit (lease TTL); static secrets with long TTLs make it unbounded. Prefer the explicit window.
- **Cold start vs steady state.** At pod start, the secret must be available before the app becomes ready (readiness probe should fail if the secret file is absent). Warm, the secret refreshes on lease renewal. Design both paths — a pod that starts without a secret must not become `Ready` and serve unauthenticated fallback behavior.
- **Thundering herd on rotation.** A fleet-wide rotation that expires `N` secrets at the same second causes `N` simultaneous Vault reads. Jitter renewal (`lease_duration/2 ± 10%`) and stagger rotation (one shard at a time) to smooth the load.
- **Region affinity for latency.** A service in `eu-west-1` that fetches secrets from `us-east-1` Vault pays cross-region latency on every cold start and renewal. Performance replication or a regional Vault cluster is not optional for multi-region fleets.
- **Audit as a forensic requirement.** Every read, write, and lease revocation must be auditable (Vault audit device → SIEM). In a breach, "which workloads read this secret, when, from which IP, with which token?" is the first question. If you cannot answer it, the blast radius is "everything that could have."



#### Secrets Retrieval with Sidecar

```mermaid
sequenceDiagram
    participant App as App
    participant Side as Vault Agent sidecar
    participant Vault as Vault
    participant DB as DB
    App->>Side: read /secrets/db
    Side->>Vault: auth via k8s SA JWT
    Vault-->>Side: short-lived lease + secret
    Side->>Side: render to tmpfs file
    App->>DB: connect with secret
```

#### Secret Rotation Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Active: version 1 issued
    Active --> Rotating: schedule rotation
    Rotating --> Dual: v1 + v2 valid
    Dual --> Retired: app migrated to v2
    Retired --> Revoked: revoke v1 lease
    Revoked --> Active: v2 now active
    Revoked --> [*]
```

#### Transit Encryption

```mermaid
flowchart LR
    App["App"] --> Transit["Vault transit encrypt<br/>plaintext → ciphertext"]
    Transit --> Store["Store ciphertext only"]
    Store --> Decrypt["Vault transit decrypt<br/>on read"]
    Decrypt --> App
    Note["Key never leaves Vault"] --> Transit
```

## Key takeaways

- A secret's lifecycle is generate → store → distribute → use → rotate → revoke/audit. Optimizing only "store" (putting it in a vault) while leaving distribution as env vars and rotation as manual is the common failure mode.
- Envelope encryption (KEK in KMS/HSM wrapping a DEK that AEAD-encrypts storage) is the correct at-rest model — for Vault's barrier, for Transit, and for app-layer encryption. Auto-unseal via KMS removes the manual Shamir ceremony; keep Shamir as break-glass.
- Vault 1.15+ (or OpenBao) organizes the control plane as auth methods → policies (HCL, per-path) → secrets engines (KV v2, Transit, PKI, database) → leases. Bind policies to roles (k8s, JWT/OIDC, AppRole), use `batch` tokens for workloads (15 m TTL), and enforce `ttl`/`max_ttl` as the blast-radius bound.
- Prefer dynamic, short-lived credentials (database engine, PKI) over static secrets — the lease *is* the rotation. Where static secrets remain, automate rotation with dual-credential overlap, staggered rollout, and forced restarts; never rely on manual rotation.
- Distribute via file on `tmpfs` (Vault Agent sidecar/Injector, CSI Driver) rather than Kubernetes `Secret` / env vars. ESO is the migration path for legacy `Secret` consumers. In all cases, the app reads a file with `0400`, never logs the value, and fails readiness if the file is absent.
- Detect leaks with gitleaks 8.18+ and TruffleHog 3.70+ in pre-commit and CI, plus GitHub push protection. Remediation is always rotation first, history cleanup second — redaction without rotation leaves the secret valid in every clone and cache.
- Vault at scale is an HA Raft cluster (3/5 voters) with performance replication for multi-region reads, DR replication for failover, KMS auto-unseal, Agent caching for brief outages, and alerts on seal status, lease failures, secret age, and Raft health. Enable etcd/KMS encryption at rest for Kubernetes Secrets and lock down RBAC on `get/list` secrets.

## Further reading

- **Vault:** HashiCorp Vault 1.15+ docs — https://developer.hashicorp.com/vault/docs — auth methods, policies, audit, replication, Raft storage, seal. OpenBao docs — https://openbao.org/docs/ — open-source Vault lineage. Vault Agent / Injector / CSI provider docs — https://developer.hashicorp.com/vault/docs/platform/k8s.
- **Kubernetes secrets plane:** *Kubernetes Secrets* (https://kubernetes.io/docs/concepts/configuration/secret/) and *Encrypting Secret Data at Rest* (https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/). Secrets Store CSI Driver (https://secrets-store-csi-driver.sigs.k8s.io/) and Vault CSI Provider. External Secrets Operator (https://external-secrets.io/latest/) — `ExternalSecret` / `ClusterSecretStore`.
- **Cloud workload identity:** AWS IRSA (https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html), GCP Workload Identity (https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity), Azure Workload Identity — the path to eliminating static cloud keys entirely (see Ch 10 for SPIFFE generalization).
- **Detection:** gitleaks 8.18+ (https://github.com/gitleaks/gitleaks), TruffleHog 3.70+ (https://github.com/trufflesecurity/trufflehog), GitHub Secret Scanning & Push Protection (https://docs.github.com/en/code-security/secret-scanning).
- **Standards & papers:** NIST SP 800-57 Part 1 Rev. 5 — *Recommendation for Key Management* — key lifecycle and cryptoperiods. NIST SP 800-53 — controls for media protection and key management.Envelope encryption pattern — see Google Cloud KMS / AWS KMS docs for KEK/DEK reference architectures.
