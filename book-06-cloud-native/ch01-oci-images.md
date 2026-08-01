# Chapter 1 — Container Images: OCI Format, Layers, and Attack Surface

*What this chapter covers.* You run containers every day. You `docker build`, you `docker push`,
you `kubectl apply`, and something that started life as a `Dockerfile` ends up as processes on a
node in a cluster. This chapter is about what that *something* actually is on the wire and on
disk — the **OCI image** — because you cannot secure an artifact whose structure you treat as
opaque. An image is not a binary blob and not a filesystem snapshot; it is a small, precisely
specified graph of **content-addressed JSON and tar blobs**, and nearly every attack and defense
in the rest of Book 6 is a statement about that graph. Signing (Book 5) signs a node in it.
Scanning (Chapter 4) enumerates what a node contains. Admission control (Chapter 6) checks a
node's identity before it runs. Registries (Chapter 2) store the graph and hand out its edges.
This chapter builds the format from the bottom up — manifest, config, layers, index — is precise
about **digests versus tags** and **compressed-blob digests versus uncompressed diff IDs**, walks
the layer/overlay model and the secret-leak it enables, maps the image attack surface that frames
the rest of the book, and ends at the **OCI referrers model**, the mechanism by which the entire
signing/SBOM/provenance ecosystem hangs off an image by its digest.

Learning goals — after this chapter you should be able to:

- Name the **OCI specifications** (Image Format, Distribution, Runtime) and explain the
  Docker-to-OCI standardization and why interoperability matters.
- Describe an image precisely as a **manifest + config + layers**, all **content-addressed by
  SHA-256**, and state what each part contains and what the manifest digest *is* (the image's
  identity — the thing you sign and deploy by).
- Distinguish the **manifest digest** (of the compressed layer blob) from the config's **diff_id**
  (of the uncompressed tar), and explain why both exist.
- Explain the **image index / manifest list** and how one tag resolves to a per-platform manifest.
- Explain the **overlay filesystem** layer model, why **nothing is ever deleted across layers**,
  and how secrets leak into images that a later `RUN rm` cannot remove.
- Use **multi-stage builds** to leave build-time secrets and junk behind.
- Map the **image attack surface**: base OS packages, app dependencies, added tooling, embedded
  secrets — and the tampering vectors that content-addressing does and does not defeat.
- Explain the **mutable-tag / immutable-digest** distinction as a TOCTOU problem and why fleets
  deploy by digest.
- Explain the **OCI 1.1 Referrers API** and the `subject` field, and the older cosign `.sig` tag
  convention, as the way signatures, SBOMs, and provenance attach to an image.

## The OCI specifications

Before 2015 there was no *standard* container image; there was **Docker's** image format and its
registry protocol, which everyone reverse-engineered because Docker was the only game in town.
That is a fragile way to run an industry. In 2015 Docker, CoreOS, and others formed the **Open
Container Initiative (OCI)** under the Linux Foundation, and Docker **donated** its image format
and runtime as the seed. OCI turned a de-facto format into three published, versioned
specifications:

- **Image Format Specification** — what an image *is*: the manifest, config, layer, and index
  media types and their JSON schemas, and the content-addressing rules. This is the spec this
  chapter is mostly about.
- **Distribution Specification** — how images move: the HTTP registry API (the `/v2/` API) for
  pushing and pulling manifests and blobs by tag or digest, including (as of v1.1) the Referrers
  API. Chapter 2 is built on this.
- **Runtime Specification** — how an *unpacked* image is run as a container: the on-disk bundle
  (a root filesystem plus a `config.json`) and the lifecycle a runtime like `runc` or `crun`
  executes. Largely out of scope for supply chain; we touch only the image-config fields that
  become runtime posture.

The relationship to Docker is worth stating plainly because it still confuses people: **the
Docker image format and the OCI image format are two dialects of the same thing**, differing
almost entirely in media-type strings. `docker build` today produces OCI-compatible artifacts;
containerd, CRI-O, Podman, Buildah, Kaniko, BuildKit, `crane`, `skopeo`, and every cloud registry
speak OCI. When we say "the image" we mean the OCI artifact, and where Docker's legacy media types
differ we note it.

Why standardization is not a footnote: **interoperability is a security property, not only a
convenience.** Because the format is a published spec rather than one vendor's implementation, a
signature produced by cosign, an SBOM produced by Syft, a scan produced by Trivy, and an admission
check enforced by Kyverno all operate on the *same* bytes with the *same* digest and mean the same
thing across GitHub, GitLab, ECR, GCR, Harbor, and a bare `registry:2`. A closed format would force
each tool to re-derive identity, and identity is the one thing a supply chain cannot afford to have
two opinions about.

## What an image actually is

Strip away the tooling and an OCI image is **four kinds of object**, all identified by the SHA-256
of their own bytes (Book 5, Chapter 1 — Cryptographic Foundations, on content addressing):

| Object | Media type (OCI) | Content | Role |
|---|---|---|---|
| **Manifest** | `application/vnd.oci.image.manifest.v1+json` | JSON: one config descriptor + ordered list of layer descriptors | The image *identity*. Its own digest is `sha256:...` — the thing you sign, pin, and deploy. |
| **Config** | `application/vnd.oci.image.config.v1+json` | JSON: env, entrypoint/cmd, user, workdir, `rootfs.diff_ids`, `history` | Runtime configuration + the ordered list of layer *identities* + build history. |
| **Layer** | `application/vnd.oci.image.layer.v1.tar+gzip` | gzipped tar of filesystem changes (a "diff") | The actual bytes: files added, changed, or whited-out relative to the layer below. |
| **Index** | `application/vnd.oci.image.index.v1+json` | JSON: list of manifest descriptors with `platform` | Multi-platform: one name → per-arch/OS manifests. Optional. |

Everything is glued together by **descriptors**. A descriptor is the OCI spec's universal pointer:
a small JSON object with a `mediaType`, a `digest`, and a `size`. It is a content-addressed edge in
the graph — it says "there is an object of *this* type, with *this* SHA-256, of *this* many bytes,"
and nothing more. The single top-level digest transitively commits to every byte of the image,
because the manifest names the config and layers by digest, and the config names each layer's
uncompressed identity by digest. Change one byte anywhere and the top digest changes. That is the
whole integrity argument, and we will lean on it repeatedly.

```mermaid
flowchart TD
  IDX["Image Index<br/>vnd.oci.image.index.v1+json<br/>sha256:INDEX"]
  M_AMD["Manifest amd64<br/>sha256:MANIFEST_A"]
  M_ARM["Manifest arm64<br/>sha256:MANIFEST_B"]
  CFG["Config JSON<br/>sha256:CONFIG<br/>env, entrypoint, user,<br/>rootfs.diff_ids, history"]
  L0["Layer 0 blob<br/>tar+gzip<br/>sha256:LAYER0"]
  L1["Layer 1 blob<br/>tar+gzip<br/>sha256:LAYER1"]
  L2["Layer 2 blob<br/>tar+gzip<br/>sha256:LAYER2"]

  IDX -->|"platform amd64"| M_AMD
  IDX -->|"platform arm64"| M_ARM
  M_AMD -->|"config descriptor"| CFG
  M_AMD -->|"layers[0]"| L0
  M_AMD -->|"layers[1]"| L1
  M_AMD -->|"layers[2]"| L2
```

### The manifest

The manifest is the root of a *single-platform* image. Here is a real one, fetched with `crane`
(the go-containerregistry CLI), trimmed:

```bash
$ crane manifest cgr.dev/chainguard/nginx:latest | jq .
```
```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "config": {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "digest": "sha256:7f3c1b9e0a...c21",
    "size": 2841
  },
  "layers": [
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "digest": "sha256:b5d2f8e4a1...9ac",
      "size": 3125478
    },
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "digest": "sha256:0e91ab77c3...f10",
      "size": 41522
    }
  ]
}
```

Three things to internalize. First, the manifest is *small* — a few kilobytes of pointers — and it
contains **no image bytes**, only descriptors. Second, the layer order is **significant**: layers
apply bottom-to-top and later layers override earlier ones. Third, and most important, the
**manifest's own digest is the image's identity**:

```bash
$ crane digest cgr.dev/chainguard/nginx:latest
sha256:4b2c9e6f1a3d8c0b5e7a2f9d4c1b8e6a3f0d7c2b9e5a1f8d4c0b7e3a6f2d9c1b
```

That `sha256:4b2c...` is what you sign in Book 5, Chapter 3, what you pin in a Deployment, and what
an admission controller checks in Chapter 6. It is not the digest of a layer or of the config; it is
the digest of the manifest JSON, and by transitivity of the whole image.

Docker's legacy dialect uses `application/vnd.docker.distribution.manifest.v2+json` for the manifest,
`application/vnd.docker.container.image.v1+json` for the config, and
`application/vnd.docker.image.rootfs.diff.tar.gzip` for layers. Structurally identical; only the
strings differ. A registry and runtime dispatch on these `mediaType` values to decide how to parse
each object, which is why getting them right matters for interoperability.

### The config

The config blob is the image's *behavior and provenance-of-assembly*. Fetch it by the digest the
manifest gave:

```bash
$ crane config cgr.dev/chainguard/nginx:latest | jq .
```
```json
{
  "created": "2026-05-14T09:12:44Z",
  "architecture": "amd64",
  "os": "linux",
  "config": {
    "User": "65532",
    "Env": ["PATH=/usr/sbin:/usr/bin:/sbin:/bin"],
    "Entrypoint": ["/usr/sbin/nginx"],
    "Cmd": ["-g", "daemon off;"],
    "WorkingDir": "/",
    "ExposedPorts": { "8080/tcp": {} }
  },
  "rootfs": {
    "type": "layers",
    "diff_ids": [
      "sha256:1f0d7c2b9e...5a1",
      "sha256:6a3f0d7c2b...9e5"
    ]
  },
  "history": [
    { "created": "2026-05-14T09:12:40Z", "created_by": "ADD file:... in /", "comment": "buildkit" },
    { "created": "2026-05-14T09:12:44Z", "created_by": "RUN apk add nginx", "comment": "buildkit" }
  ]
}
```

The `config` object holds the runtime knobs: `Entrypoint`/`Cmd`, `Env`, `WorkingDir`, `ExposedPorts`,
and `User`. These become the container's default behavior — we return to their security implications
below.

`rootfs.diff_ids` is the subtle part and a common source of confusion. It is the ordered list of
**layer identities** — but these are **not** the same digests the manifest lists. **The manifest's
layer digest is the SHA-256 of the *compressed* (gzipped) blob; the config's `diff_id` is the
SHA-256 of the *uncompressed* tar.** Two digests for the same layer, for two different jobs:

- The **manifest digest** identifies the blob *as stored and transferred* — the registry
  deduplicates and serves it under that digest, and gzip determinism is not guaranteed, so this is
  the "on-the-wire" identity.
- The **diff_id** identifies the layer's *content* independent of how it was compressed — the runtime
  computes the rootfs from `diff_id`s, and it is stable even if you recompress. The **chain ID**
  (a running hash of diff_ids) is what overlay snapshotters use to name a stack of applied layers.

You will trip over this exactly once — when a layer digest in `docker history` or a scan report does
not match the manifest — and then never again. Keep the rule: *manifest lists compressed digests,
config lists uncompressed diff_ids.*

`history` is the config's record of **how each layer was made**: roughly one entry per Dockerfile
instruction, with `created_by` holding the command. Entries with `empty_layer: true` correspond to
instructions like `ENV`, `WORKDIR`, `USER`, `ENTRYPOINT` that change configuration without adding a
layer, so `history` is usually longer than `diff_ids`. This is the record `docker history` renders —
and, as we will see, a place secrets go to be discovered.

### The layers

A layer is a **tar archive of filesystem changes** relative to the layers beneath it — a *diff*, not
a full filesystem. If a build step adds `/usr/bin/app` and modifies `/etc/nginx/nginx.conf`, the
layer's tar contains exactly those two paths. Deletions are encoded with **whiteout** entries: to
delete `/etc/secret` a layer contains a zero-length file `/etc/.wh.secret`, and to mask an entire
directory it contains an *opaque whiteout* `/dir/.wh..wh..opq`. The whiteout is an instruction to the
union filesystem — "hide this path from the layers below" — and it is central to the secret-leak
problem later.

Layers are **content-addressed, deduplicated, and shared**. Two images built `FROM` the same base
reference the *same* base-layer blobs by the *same* digest; the registry stores each blob once and a
node caches each blob once. A 10 MB app on a 120 MB base costs 10 MB to push and pull if the base is
already present. This sharing is the economic engine of containers at fleet scale — and, as the
distributed-systems lens will show, also a **blast-radius multiplier**.

## Multi-platform images: the index

A single manifest is one architecture and OS. Real registries serve `nginx:latest` to amd64 laptops
and arm64 nodes from **one tag**, using an **image index** (Docker calls it a *manifest list*):

```bash
$ crane manifest --platform all nginx:1.27 | jq '{mediaType, manifests: [.manifests[] | {digest, platform}]}'
```
```json
{
  "mediaType": "application/vnd.oci.image.index.v1+json",
  "manifests": [
    { "digest": "sha256:aa11...", "platform": { "architecture": "amd64", "os": "linux" } },
    { "digest": "sha256:bb22...", "platform": { "architecture": "arm64", "os": "linux" } },
    { "digest": "sha256:cc33...", "platform": { "architecture": "s390x", "os": "linux" } }
  ]
}
```

The index is itself a content-addressed object with its own digest, and each entry is a descriptor
pointing to a **per-platform manifest** carrying a `platform` field. When a runtime pulls a tag that
resolves to an index, it selects the manifest matching its own `architecture`/`os` and pulls *that*.
An index also serves as the container for referrers responses and, increasingly, for bundling an
image with its attestations — the same structure, reused. When you pin `nginx@sha256:INDEX_DIGEST`
you are pinning the *index*, which transitively commits to every per-platform image under it.

## How images are built: the layer model

`docker build` (or BuildKit, Buildah, Kaniko) walks a `Dockerfile` and turns instructions into
layers. Roughly: each filesystem-mutating instruction — `RUN`, `COPY`, `ADD` — produces a new layer
whose tar is the diff that instruction caused; metadata-only instructions — `ENV`, `WORKDIR`,
`USER`, `ENTRYPOINT`, `CMD`, `LABEL` — produce empty-layer history entries and mutate the config
instead.

```dockerfile
FROM alpine:3.20                 # base layers (shared)
RUN apk add --no-cache nginx     # layer: nginx package tree
COPY nginx.conf /etc/nginx/      # layer: one config file
COPY app /usr/bin/app            # layer: the binary
USER 65532                       # config change, empty layer
ENTRYPOINT ["/usr/bin/app"]      # config change, empty layer
```

The build **cache** keys each step on the instruction *and* the state of everything it consumed; a
step is reused only if it and every step before it are unchanged. This is why **layer order
determines cache efficiency**: put the stable, slow layers (dependency install) *before* the volatile
ones (your source), so a code change re-runs only the cheap tail. Order also matters for
**reproducibility** (Book 4, Chapter 2 — Hermetic and Reproducible Builds): non-deterministic steps
early in the file poison the cache and the digest for everything after them.

### The overlay filesystem at runtime

At runtime the layers are not re-tarred; they are **stacked by a union filesystem** — on Linux
almost always **overlayfs**. Each layer is unpacked once into its own directory (named by chain ID)
and marked read-only. overlayfs presents a single **merged** view where upper layers shadow lower
ones, and gives the container a thin **writable upper layer** (`upperdir`) for changes it makes while
running; the image layers are the read-only `lowerdir`s.

```mermaid
flowchart TB
  subgraph merged["Merged view — the container rootfs"]
    direction TB
    RW["Writable container layer (upperdir)<br/>runtime changes, ephemeral"]
  end
  L3["Layer 2 (ro): /usr/bin/app"]
  L2["Layer 1 (ro): /etc/nginx/nginx.conf"]
  L1["Layer 0 (ro): base OS filesystem"]
  RW --> L3 --> L2 --> L1
  classDef ro fill:#eef,stroke:#557
  class L1,L2,L3 ro
```

Two consequences follow directly and are the crux of image security:

1. **Layers are read-only and immutable once built.** A container writing to `/etc/secret` writes to
   its *own* upperdir; the image's layers are untouched. Nothing a running container does changes the
   image.
2. **Deletion is a masking operation, not an erasure.** When a build step deletes a file, the tooling
   writes a *whiteout* in the new layer that hides the path in the merged view. **The bytes remain in
   the earlier layer's blob.** The merged filesystem doesn't show them; the image still ships them.

### Nothing is ever deleted: the secret-leak

This is the single most important image-hygiene fact, and it burns teams constantly. Consider:

```dockerfile
FROM node:20
COPY id_rsa /root/.ssh/id_rsa       # layer N: private key added
RUN git clone git@github.com:acme/private.git \
 && rm /root/.ssh/id_rsa            # layer N+1: "removes" the key
```

The author believes the key is gone: it is not in the running container's filesystem, and
`ls /root/.ssh` shows nothing. But the image is a *stack of layers*, and **layer N still contains
`id_rsa` in full**. Anyone who pulls the image can list the layers and extract the blob:

```bash
$ crane export acme/app:latest - | tar -tf - | grep -c id_rsa   # merged view: 0, masked by whiteout
0
$ crane blob acme/app@sha256:LAYER_N | tar -xzf - root/.ssh/id_rsa   # the raw layer: still there
$ cat root/.ssh/id_rsa
-----BEGIN OPENSSH PRIVATE KEY-----
...the secret, fully intact...
```

`docker history` makes the leak trivial to *locate* even without extraction, because the config's
history records the commands verbatim:

```bash
$ docker history --no-trunc acme/app:latest
IMAGE          CREATED BY                                          SIZE
sha256:...      RUN git clone ... && rm /root/.ssh/id_rsa           412MB
sha256:...      COPY id_rsa /root/.ssh/id_rsa                       3.4kB   <-- the key layer
sha256:...      FROM node:20                                        1.1GB
```

```mermaid
flowchart LR
  subgraph img["Image blobs (what ships and is pullable)"]
    LN["Layer N<br/>ADDS /root/.ssh/id_rsa<br/>SECRET PRESENT"]
    LN1["Layer N+1<br/>whiteout /root/.ssh/.wh.id_rsa<br/>hides it in merged view"]
  end
  MV["Merged rootfs<br/>id_rsa: NOT visible"]
  ATT["Attacker: crane blob layer N<br/>-> extracts id_rsa intact"]
  LN --> MV
  LN1 --> MV
  LN --> ATT
  style LN fill:#fdd,stroke:#a33
  style ATT fill:#fdd,stroke:#a33
```

The rule: **`RUN rm` (or `docker rmi`, or deleting in a later `COPY`) never removes anything from the
image.** It only adds a whiteout. Anything a secret ever touched a layer — a `.npmrc` with a token, a
cloud credential file, a `.env`, a build SSH key, a `pip` config with an index password — is
recoverable by anyone who can pull the image, forever, regardless of what later layers do. The
correct responses are: never let the secret land in a layer (mount it as a **build secret** —
`RUN --mount=type=secret` in BuildKit — so it exists only during that step and is never committed),
and use multi-stage builds to leave build-time material behind entirely.

### Multi-stage builds

A multi-stage build (Book 4, Chapter 2) uses several `FROM` stages in one `Dockerfile` and ships only
the *last* stage's layers. Earlier stages — with compilers, source, package caches, SSH keys, and the
entire toolchain — are built, used, and **discarded**; only files explicitly `COPY --from`'d into the
final stage survive into the image:

```dockerfile
# Stage 0: build — has the toolchain, source, and secrets. NOT shipped.
FROM golang:1.23 AS build
WORKDIR /src
COPY . .
RUN --mount=type=secret,id=gh_token \
    GOFLAGS=-mod=mod go build -o /out/app ./cmd/app

# Stage 1: final — inherits none of stage 0's layers.
FROM gcr.io/distroless/static:nonroot
COPY --from=build /out/app /app
USER 65532
ENTRYPOINT ["/app"]
```

The final image contains the `distroless/static` base and one file, `/app`. It has **no shell, no
package manager, no compiler, no source, and no build key** — none of stage 0's layers are in its
manifest, so none of stage 0's bytes ship. This is simultaneously the answer to the secret-leak
(build secrets live and die in a discarded stage) and the on-ramp to minimal base images
(Chapter 3 — Base Image Strategy), which shrink the attack surface we turn to now.

## The image attack surface

Everything in the image is your attack surface and your vulnerability surface: whatever bytes are in
those layers can be exploited if reachable, and every package is a component that scanners (Chapter 4)
and SBOMs (Book 3) must account for. Map it in four buckets, roughly by size:

- **The base image.** The OS userland — libc, coreutils, OpenSSL, package manager, shell — is
  usually the *bulk of the components and the bulk of the vulnerabilities* in an image, often by an
  order of magnitude over your own code. A `debian:12`-based image inherits every Debian CVE in its
  installed set; that is why base image choice (Chapter 3) is the single highest-leverage security
  decision for an image, and why SBOMs for services (Book 3) are dominated by base-image packages.
- **Your app and its dependencies.** Your compiled binary or interpreted code plus the language
  dependency tree (Book 2 — the dependency supply chain). A vulnerable transitive npm/pip/Go module
  is in the image exactly as much as if you had written it.
- **Added tools and binaries.** `curl`, `bash`, `netcat`, `python`, a package manager left in for
  "debugging," a static `busybox` — each is a capability handed to whoever gets code execution in the
  container.
- **Embedded secrets and config.** Tokens, keys, `.env` files, world-readable credential files —
  including the ones "deleted" in a later layer (above), which are still present.

### Tampering vectors and what content-addressing defends

An image can be attacked at several seams between build and run:

- A **modified layer** — a backdoor injected into a layer blob.
- A **swapped manifest** — pointing a tag at different config/layers.
- A **poisoned base image** — the upstream `FROM` was compromised, so everything built on it inherits
  the malware (Chapter 3; and the concentration argument below).
- A **malicious layer injected in the registry** — a compromised or malicious registry serving
  different bytes (Chapter 2 — Registries).

**Content-addressing is the structural defense against undetected tampering.** Because every object
is named by the SHA-256 of its own bytes and the manifest commits to config and layers by digest,
*any* change to *any* byte changes the top-level digest. You cannot alter a layer, swap a config, or
substitute a manifest without producing a different `sha256:...`. So a verifier that **knows the
digest it expects** and recomputes it on pull detects all four tampering vectors — a modified layer
won't match its descriptor, a swapped manifest won't match the pinned digest, a poisoned or malicious
registry cannot serve different bytes than the digest names (Book 5, Chapter 1). This is precisely why
you **deploy and verify by digest, not by tag** — and why the referrers model (below) lets signatures
and provenance *reference* an image by that digest.

What content-addressing does **not** defend: it guarantees *integrity* (these are the bytes you
named), not *goodness* (these bytes are safe). A digest for a backdoored base image is a perfectly
valid, verifiable digest. Integrity plus a *trusted source* and *signed provenance* is the full story
(Book 5); the digest is the anchor all of it attaches to.

### The mutable-tag problem

A **tag** — `:latest`, `:v1.4`, `:prod` — is a **mutable pointer**, a name in the registry that maps
to a manifest digest and **can be repointed at any time**. A **digest** — `@sha256:...` — is
**immutable**: it *is* the content, so it cannot point at anything else. This distinction is a supply
chain hole, not a nicety:

```mermaid
sequenceDiagram
  participant CI as CI (verify)
  participant Reg as Registry
  participant K8s as Kubernetes (run)
  Note over CI,K8s: Deploying by TAG — TOCTOU window
  CI->>Reg: pull acme/app:v1.4
  Reg-->>CI: manifest sha256:GOOD
  CI->>CI: scan + verify sha256:GOOD  (passes)
  Note over Reg: attacker (or a rebuild) repoints<br/>tag v1.4 -> sha256:EVIL
  K8s->>Reg: pull acme/app:v1.4
  Reg-->>K8s: manifest sha256:EVIL
  Note over K8s: runs EVIL — not what CI verified
```

This is a **time-of-check-to-time-of-use (TOCTOU)** gap: you verified `:v1.4` and it was
`sha256:GOOD`; between verification and run, the tag was repointed — by an attacker with registry
write access, by a well-meaning `docker push` that overwrote it, or by an upstream `:latest` moving —
and the pod runs `sha256:EVIL`. **The artifact you verified is not guaranteed to be the one that
runs.** The fix is to collapse the check and use onto the *same* immutable name: resolve the tag to a
digest once, then verify, deploy, and admit **by digest** (Book 5, Chapter 8 — Provenance
Verification; Chapter 5 — Image Signing in Kubernetes). Kubernetes runs `image: acme/app@sha256:GOOD`
happily; admission controllers can *require* digest pins and reject bare tags. Tags are fine as
human-facing labels; they must not be the thing you trust.

### Bloat is attack surface

Every unnecessary thing in an image is a tool for whoever compromises the container. A shell lets an
attacker pivot interactively; `curl`/`wget` let them pull a second-stage payload; a package manager
lets them install one; `setuid` binaries are privilege-escalation primitives; leftover dev tooling is
a ready-made toolkit. Minimizing the image is therefore a security control, not only an image-size
optimization: fewer packages mean fewer CVEs, fewer exploitation primitives, and a smaller SBOM to
reason about. This is the motivation for **minimal and distroless base images** (Chapter 3), where a
production image may contain a single static binary and its CA certificates — nothing for an attacker
to live off of.

## Image configuration and runtime posture

A handful of config fields set the container's default security posture. Deep runtime security is
beyond supply chain, but **image-config hygiene is squarely in scope** because it is baked into the
artifact you ship:

- **`User`.** If unset, the container's default user is **root (UID 0)**. A process running as root
  in-container is root against any kernel path it can reach and against mounted host resources; a
  container breakout from root is far worse than from an unprivileged UID. Set a non-root `USER`
  (a numeric UID, e.g. `USER 65532`, so it works without an `/etc/passwd` entry) in the image. This
  is a property of the *image*, independently enforceable by admission (`runAsNonRoot`), but it should
  be correct at build time.
- **`Entrypoint`/`Cmd`.** The default process. A shell-form entrypoint (`ENTRYPOINT nginx`) runs via
  `/bin/sh -c`, which requires a shell in the image (attack surface) and complicates signal handling;
  prefer exec form (`ENTRYPOINT ["nginx"]`).
- **`Env`.** Environment variables are stored **in the config in plaintext** and are visible to
  anyone who can `crane config` the image or read it in the registry. **Never bake secrets into
  `ENV`.** Inject them at runtime (Kubernetes Secrets, a secrets manager), not into the image.
- **`ExposedPorts`, `Volume`, `WorkingDir`.** Documentation and defaults rather than enforcement, but
  they shape how the image is run and are worth getting right.

None of these is enforced by the image alone — the runtime and admission layer enforce them — but a
well-configured image makes the secure default the *easy* default across the fleet.

## Signatures, SBOMs, and provenance: the OCI referrers model

We have said repeatedly that signatures, SBOMs, and provenance **attach to an image by its digest**.
Here is the mechanism — and it is the bridge from this chapter to the rest of Book 6 and to Book 5.

The problem: an image is content-addressed and immutable, so you *cannot* add metadata to it — any
change would change its digest and thus its identity. You need to associate *external* artifacts
(a signature, an SBOM, an SLSA provenance attestation) with an existing image **without altering it**,
and store them **in the same registry** so they travel with the image. OCI solves this with the
**Referrers API**, standardized in the **Distribution Spec v1.1** and supported by the **Image Spec
v1.1** `subject` field.

The idea: an attestation is itself a normal OCI manifest — with its own config and layers (the
signature bytes, the SBOM document, the provenance JSON) — that carries a **`subject`** field. The
`subject` is a *descriptor* pointing at the digest of the image it refers to, and an `artifactType`
naming what kind of thing it is:

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "artifactType": "application/vnd.dev.cosign.artifact.sig.v1+json",
  "config": { "mediaType": "application/vnd.oci.empty.v1+json", "digest": "sha256:44136f...", "size": 2 },
  "layers": [
    { "mediaType": "application/vnd.dev.cosign.simplesigning.v1+json", "digest": "sha256:sig...", "size": 250 }
  ],
  "subject": {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "digest": "sha256:4b2c9e6f1a3d...",   // <-- the image being signed
    "size": 2841
  }
}
```

A verifier asks the registry: *what refers to this image?*

```bash
$ crane referrers acme/app@sha256:4b2c9e6f1a3d...
```

which the registry answers (`GET /v2/acme/app/referrers/sha256:4b2c...`) with an **image index** whose
entries are exactly the manifests whose `subject` is that image digest, each tagged with its
`artifactType`. You then fetch the signature, SBOM, or provenance you want and verify it.

```mermaid
flowchart BT
  IMG["Image manifest<br/>sha256:4b2c9e6f...<br/>(immutable identity)"]
  SIG["Signature manifest<br/>artifactType: cosign sig<br/>subject -> sha256:4b2c..."]
  SBOM["SBOM manifest<br/>artifactType: spdx+json<br/>subject -> sha256:4b2c..."]
  PROV["Provenance manifest<br/>artifactType: slsa provenance<br/>subject -> sha256:4b2c..."]
  SIG -->|subject| IMG
  SBOM -->|subject| IMG
  PROV -->|subject| IMG
  Q["crane referrers sha256:4b2c...<br/>GET /v2/.../referrers/&lt;digest&gt;"] -.->|returns index of| SIG
  Q -.-> SBOM
  Q -.-> PROV
```

Before the Referrers API existed, cosign (Book 5, Chapter 3 — Sigstore) solved the same problem with
a **tag convention**: for an image with digest `sha256:4b2c...`, cosign stores the signature as an
ordinary image **tagged `sha256-4b2c….sig`** in the same repository (note the `sha256-` prefix and the
`.sig` suffix — a tag, because the digest character `:` is not tag-legal). Attestations went to
`…​.att`, SBOMs to `…​.sbom`. It works on any Distribution-conformant registry — no v1.1 support
needed — which is why it is still widespread, but it clutters the tag namespace and does not let a
registry answer "what refers to this?" natively. The Referrers API is the successor: metadata is
discoverable by a first-class API, GC understands the `subject` link, and (via a fallback where the
registry doesn't yet support referrers) tooling can emulate it with a `sha256-<hex>` referrers tag
that holds the index.

The load-bearing point for the rest of Book 6: **the image digest is the join key for the entire
security ecosystem.** Signatures (Book 5), SBOMs (Book 3), VEX (Book 3, Chapter 6), and SLSA
provenance (Book 4, Chapter 3) all reference the image by the same immutable `sha256:...`, stored
alongside it, and admission control (Chapter 6) resolves an image to its digest, fetches its
referrers, and enforces policy on them. None of that works if you cannot say precisely what "the
image" is — which is why the format had to come first.

## Distributed-systems lens

At the scale you operate — thousands of services, hundreds of teams, images rebuilt many times a day —
the format's properties stop being trivia and become fleet dynamics.

**Shared base layers concentrate risk.** Content-addressed layers mean your entire fleet's images
are almost certainly built on a small number of shared base images, and the registry and every node
store each base blob *once*. This is wonderful for cost and cache-hit rate, and dangerous for blast
radius: a single CVE in a widely used base layer is instantly a vulnerability in *every* image built
on it, and a *poisoned* shared base layer (Chapter 3) spreads to everything downstream with no further
attacker effort. This is the concentration argument of Book 1, Chapter 9 — Distributed Systems Lens,
in container form: the same sharing that gives you leverage gives an attacker leverage. Govern base
images centrally (a small set of vetted, signed, continuously rebuilt bases), because a good base is a
fleet-wide control and a bad one is a fleet-wide incident.

**Dedup and caching cut both ways.** The digest-keyed blob store that lets a 4 GB base image cost one
pull per node also means that if a bad blob lands under a trusted digest — which content-addressing
*prevents* for a fixed digest but not against a *newly pushed* malicious layer reused across images —
it, too, propagates by the same efficient machinery. Integrity (the digest is what it says) is not
the same as trust (the digest should be there); the fleet needs both.

**Deploy-by-digest is the fleet's core integrity practice.** Mutable tags create a TOCTOU window at
*every* deployment across the fleet; the only immutable coordinate is the digest. Resolving to digests
at build/release time, recording them, and admitting only digest-pinned images (Chapters 5–6) closes
that window uniformly. It also makes the fleet *auditable*: a digest is a precise, global name you can
correlate across the registry, the transparency log (Book 5, Chapter 5), your SBOM inventory (Book 3,
Chapter 9), and your admission logs.

**The registry is the shared substrate, and referrers are its metadata backbone.** Every image, layer,
signature, SBOM, and provenance for the whole fleet lives in the registry (Chapter 2), keyed by digest,
with attestations hanging off images via `subject`. The referrers graph *is* the fleet's software
supply chain metadata layer (Book 3, Chapter 5 — SBOMs at scale; Book 5). Understanding the OCI format
is the prerequisite to securing any of it: signing signs a manifest digest, scanning enumerates a
config's layers, admission checks a subject-linked signature, and all of them agree on identity only
because the format defines it precisely.

## Key takeaways

- An **OCI image is a content-addressed graph**: a **manifest** (JSON of descriptors) pointing to a
  **config** (JSON: env/entrypoint/user, `rootfs.diff_ids`, `history`) and an ordered list of
  **layer** tar blobs, optionally under an **index** for multi-platform. All named by **SHA-256**.
- The **manifest's own digest is the image's identity** — the thing you sign, pin, and deploy. It
  differs from a layer's `diff_id`: **manifest layer digests are of the *compressed* blob; config
  `diff_id`s are of the *uncompressed* tar.**
- Layers stack via an **overlay/union filesystem**; they are read-only and immutable. **Deletion is a
  whiteout, not an erasure** — a secret added in one layer and "removed" in a later `RUN` is **still
  in the earlier layer's blob and fully recoverable**. Use **build secrets** and **multi-stage builds**
  to keep secrets and build junk out of shipped layers.
- The **image attack surface** is base OS packages (usually the bulk of vulns and components), app
  dependencies, added tooling, and embedded secrets/config. **Bloat is attack surface**; minimal and
  distroless bases (Chapter 3) shrink it.
- **Content-addressing defends integrity** (any tampered byte changes the digest) but not goodness. A
  **tag is a mutable pointer; a digest is immutable.** Deploying by tag is a **TOCTOU hole** — verify
  and run the *same digest*. Deploy by digest across the fleet.
- **Image-config hygiene** (non-root `USER`, exec-form entrypoint, **no secrets in `ENV`**) is baked
  into the artifact and is in scope for supply chain.
- Signatures, SBOMs, and provenance attach to an image **by its digest** via the **OCI 1.1 Referrers
  API** (a manifest with a **`subject`** descriptor pointing at the image) or the older cosign
  **`sha256-…​.sig` tag convention**. **The image digest is the join key for the whole security
  ecosystem.**

## Further reading

- **OCI Image Format Specification** — manifest, config, descriptor, index, and layer media types and
  the content-addressing model; the `subject` field and `artifactType` in v1.1.
  <https://github.com/opencontainers/image-spec>.
- **OCI Distribution Specification** — the `/v2/` pull/push API, pulling by tag vs digest, and the
  **Referrers API** and its tag-schema fallback (v1.1). <https://github.com/opencontainers/distribution-spec>.
  Registry architecture and threats are Chapter 2.
- **OCI Runtime Specification** — the on-disk bundle and `config.json` a runtime executes.
  <https://github.com/opencontainers/runtime-spec>.
- **go-containerregistry / `crane`** — `crane manifest`, `crane config`, `crane digest`,
  `crane referrers`, `crane blob`, `crane export`; the cleanest way to inspect the format directly.
  <https://github.com/google/go-containerregistry>.
- **Docker `history` and image spec** — `docker history --no-trunc` for reading the build record and
  spotting secret-leak layers. <https://docs.docker.com/reference/cli/docker/image/history/>.
- **BuildKit build secrets and multi-stage builds** — `RUN --mount=type=secret` and `COPY --from`;
  the correct way to keep secrets and toolchains out of shipped layers. <https://docs.docker.com/build/>.
  Reproducibility and hermeticity are Book 4, Chapter 2.
- **cosign and the OCI referrers/sig conventions** — how signatures, attestations, and SBOMs are stored
  against an image digest. <https://docs.sigstore.dev/> (Book 5, Chapter 3 — Sigstore Architecture).
- Cross-references: Book 5, Chapter 1 (content addressing, digests), Chapters 3 and 8 (signing and
  verifying by digest); Book 4, Chapters 2–3 (reproducible builds, SLSA provenance); Book 3
  (SBOMs — Chapters 5, 6, 9); Book 2 (dependency supply chain); Book 1, Chapter 9 (distributed-systems
  lens, concentration); Book 6, Chapters 2–6 (registries, base images, scanning, signing in Kubernetes,
  admission and policy).
