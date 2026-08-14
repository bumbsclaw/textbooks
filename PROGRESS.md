# Writing Progress

Status legend: `[ ]` not started · `[~]` in progress · `[x]` done (written + committed)

Process: chapters are written by subagents in **small batches (3 at a time)**; a batch must
fully complete before the next starts. After each batch: update this file, commit, push to
`claude/backend-security-textbooks-i0nyjm`. On resume after an interruption: read this file,
verify the last batch's files exist and are committed, and continue with the first unchecked
chapter.

## Book 1 — Foundations of Software Supply Chain Security (`book-01-foundations/`)

- [x] 1.01 The Software Supply Chain: Anatomy and Attack Surface — `ch01-anatomy-attack-surface.md`
- [x] 1.02 A Taxonomy of Supply Chain Attacks — `ch02-attack-taxonomy.md`
- [x] 1.03 Case Studies I: Build System Compromise — SolarWinds and 3CX — `ch03-case-studies-build-compromise.md`
- [x] 1.04 Case Studies II: Dependency Attacks — event-stream, ua-parser-js, node-ipc, PyTorch — `ch04-case-studies-dependency-attacks.md`
- [x] 1.05 Case Studies III: xz-utils, Codecov, and Log4Shell — `ch05-case-studies-xz-codecov-log4shell.md`
- [x] 1.06 Trust, Threat Models, and the Economics of Supply Chain Risk — `ch06-trust-threat-models.md`
- [x] 1.07 Risk Frameworks and Maturity Models: SLSA, SSDF, S2C2F — `ch07-frameworks-overview.md`
- [x] 1.08 The Open Source Ecosystem: Sustainability, Maintainership, and Risk — `ch08-open-source-ecosystem.md`
- [x] 1.09 Supply Chain Security in Distributed Backend Systems — `ch09-distributed-systems-lens.md`
- [x] 1.10 Building a Supply Chain Security Program — `ch10-building-a-program.md`

## Book 2 — Dependency Management and Open Source Risk (`book-02-dependencies/`)

- [x] 2.01 Package Managers and Registries: Architecture and Trust Models — `ch01-registries-trust-models.md`
- [x] 2.02 Versioning, Resolution, and Lockfiles — `ch02-versioning-resolution-lockfiles.md`
- [x] 2.03 Dependency Confusion, Typosquatting, and Namespace Attacks — `ch03-confusion-typosquatting.md`
- [x] 2.04 Malicious Packages: Anatomy, Detection, and Analysis — `ch04-malicious-packages.md`
- [x] 2.05 Vulnerability Databases and Identifiers: CVE, NVD, OSV, GHSA — `ch05-vulnerability-databases.md`
- [x] 2.06 Software Composition Analysis in Depth — `ch06-sca-in-depth.md`
- [x] 2.07 Reachability, Exploitability, and Prioritization — `ch07-reachability-prioritization.md`
- [x] 2.08 Vendoring, Mirroring, and Internal Registries — `ch08-vendoring-internal-registries.md`
- [x] 2.09 Dependency Update Strategy and Automation — `ch09-update-automation.md`
- [x] 2.10 Evaluating Dependencies: Scorecards, Signals, and Policy — `ch10-evaluating-dependencies.md`

## Book 3 — SBOMs and Software Transparency (`book-03-sboms/`)

- [x] 3.01 Why SBOMs: Transparency and the Regulatory Landscape — `ch01-why-sboms.md`
- [x] 3.02 SPDX in Depth — `ch02-spdx.md`
- [x] 3.03 CycloneDX in Depth — `ch03-cyclonedx.md`
- [x] 3.04 SBOM Generation: Tools, Techniques, and Accuracy — `ch04-sbom-generation.md`
- [x] 3.05 SBOM Distribution, Storage, and Querying at Scale — `ch05-sbom-at-scale.md`
- [x] 3.06 VEX and Vulnerability Correlation — `ch06-vex.md`
- [x] 3.07 SBOM Quality, Completeness, and Limitations — `ch07-sbom-quality-limitations.md`
- [x] 3.08 SBOMs for Services: Containers, Serverless, and SaaS — `ch08-sboms-for-services.md`
- [x] 3.09 Operationalizing SBOMs in the Enterprise — `ch09-operationalizing-sboms.md`

## Book 4 — Build and CI/CD Security (`book-04-build-cicd/`)

- [x] 4.01 Build Systems: Architecture and Threat Model — `ch01-build-threat-model.md`
- [x] 4.02 Hermetic and Reproducible Builds — `ch02-hermetic-reproducible-builds.md`
- [x] 4.03 SLSA Build Levels and Provenance — `ch03-slsa-provenance.md`
- [x] 4.04 CI/CD Platform Threat Models: Actions, GitLab, Jenkins, Tekton — `ch04-cicd-platform-threats.md`
- [x] 4.05 Hardening GitHub Actions — `ch05-hardening-github-actions.md`
- [x] 4.06 Secrets Management in CI/CD — `ch06-secrets-in-cicd.md`
- [x] 4.07 Pipeline Poisoning: PPE, Cache, and Artifact Attacks — `ch07-pipeline-poisoning.md`
- [x] 4.08 Ephemeral and Isolated Build Environments — `ch08-ephemeral-build-environments.md`
- [x] 4.09 Build Observability and Anomaly Detection — `ch09-build-observability.md`
- [x] 4.10 Designing a Secure Build Platform at Scale — `ch10-secure-build-platform.md`

## Book 5 — Signing, Provenance, and Attestation (`book-05-signing-attestation/`)

- [x] 5.01 Cryptographic Foundations for Supply Chain Security — `ch01-crypto-foundations.md`
- [x] 5.02 Classic Code Signing and Its Failure Modes — `ch02-classic-code-signing.md`
- [x] 5.03 Sigstore Architecture: Cosign, Fulcio, Rekor — `ch03-sigstore-architecture.md`
- [x] 5.04 Keyless Signing and Workload Identity — `ch04-keyless-signing.md`
- [x] 5.05 Transparency Logs: Merkle Trees, Rekor, and CT Lessons — `ch05-transparency-logs.md`
- [x] 5.06 in-toto: Attestations, Layouts, and Policies — `ch06-in-toto.md`
- [x] 5.07 TUF: The Update Framework — `ch07-tuf.md`
- [x] 5.08 Provenance Verification in Practice — `ch08-provenance-verification.md`
- [x] 5.09 Key Management and PKI for the Enterprise — `ch09-key-management.md`
- [x] 5.10 Designing Attestation-Based Deployment Gates — `ch10-deployment-gates.md`

## Book 6 — Container and Cloud-Native Supply Chain Security (`book-06-cloud-native/`)

- [x] 6.01 Container Images: OCI Format, Layers, and Attack Surface — `ch01-oci-images.md`
- [x] 6.02 Registries: Architecture, Trust, and Threats — `ch02-registries.md`
- [x] 6.03 Base Image Strategy: Minimal, Distroless, Hardened — `ch03-base-images.md`
- [x] 6.04 Image Scanning and Vulnerability Management — `ch04-image-scanning.md`
- [x] 6.05 Image Signing and Verification in Kubernetes — `ch05-image-signing-k8s.md`
- [x] 6.06 Admission Control and Policy Engines: OPA and Kyverno — `ch06-admission-policy.md`
- [x] 6.07 Kubernetes Delivery Chains: Helm, Operators, GitOps — `ch07-k8s-delivery-chains.md`
- [x] 6.08 Infrastructure as Code Supply Chain Risks — `ch08-iac-risks.md`
- [x] 6.09 Serverless, Managed Services, and the Cloud Provider Chain — `ch09-serverless-managed.md`
- [x] 6.10 A Cloud-Native Supply Chain Reference Architecture — `ch10-reference-architecture.md`

## Book 7 — Source, Code, and Insider Threat Security (`book-07-source-security/`)

- [x] 7.01 Source Code Management: Threat Model and Integrity — `ch01-scm-threat-model.md`
- [x] 7.02 Commit Signing and Developer Identity — `ch02-commit-signing-identity.md`
- [x] 7.03 Branch Protection, Review, and Two-Person Rules — `ch03-branch-protection-review.md`
- [x] 7.04 Secrets in Source: Detection and Remediation — `ch04-secrets-in-source.md`
- [x] 7.05 Backdoors and Malicious Code: From Underhanded C to Trusting Trust — `ch05-backdoors-malicious-code.md`
- [x] 7.06 Insider Threats and Account Takeover — `ch06-insider-threats-ato.md`
- [x] 7.07 AI-Generated Code and the Model Supply Chain — `ch07-ai-code-model-supply-chain.md`
- [x] 7.08 Repository Integrity at Scale — `ch08-repo-integrity-at-scale.md`

## Book 8 — Governance, Compliance, and Incident Response (`book-08-governance-ir/`)

- [x] 8.01 The Regulatory Landscape: EO 14028, NIST SSDF, EU CRA — `ch01-regulatory-landscape.md`
- [x] 8.02 Adopting SLSA and S2C2F: Roadmaps That Work — `ch02-adopting-slsa-s2c2f.md`
- [x] 8.03 Vendor and Third-Party Software Risk — `ch03-vendor-risk.md`
- [x] 8.04 Policy as Code and Continuous Compliance — `ch04-policy-as-code.md`
- [x] 8.05 Detecting Supply Chain Compromise — `ch05-detecting-compromise.md`
- [x] 8.06 Incident Response for Supply Chain Events — `ch06-incident-response.md`
- [x] 8.07 Threat Intelligence and Information Sharing — `ch07-threat-intelligence.md`
- [x] 8.08 Metrics, Audits, and Executive Reporting — `ch08-metrics-reporting.md`

---

# Volumes 1–15 — Broad Backend Curriculum

Scope expanded per user request to cover all topics a FAANG-level senior backend engineer
should know. Directory naming for new volumes: `vol-NN-<slug>/chNN-<slug>.md`. Full chapter
descriptions in `CURRICULUM.md`. Volume 0 above is the supply-chain-security series (its
existing dirs `book-01`…`book-08` may be regrouped under `vol-00-supply-chain-security/` later;
until then their paths are as listed above).

## Volume 1 — Computer Architecture for Backend Engineers (`vol-01-computer-architecture/`)

- [x] 1.01 Why Architecture Matters: Mechanical Sympathy — `ch01-mechanical-sympathy.md`
- [x] 1.02 The Modern CPU: Pipelines, OoO, Speculation — `ch02-modern-cpu.md`
- [x] 1.03 The Memory Hierarchy and Caches — `ch03-memory-hierarchy.md`
- [x] 1.04 Cache Coherence and Hardware Memory Consistency — `ch04-cache-coherence.md`
- [x] 1.05 Storage Hardware: HDD, SSD, NVMe, PMEM — `ch05-storage-hardware.md`
- [x] 1.06 Multi-Socket Systems and NUMA — `ch06-numa.md`
- [x] 1.07 Data Parallelism: SIMD, Vectorization, GPUs — `ch07-data-parallelism.md`
- [x] 1.08 Performance Anti-Patterns — `ch08-performance-antipatterns.md`
- [x] 1.09 Number Representation and Floating Point — `ch09-number-representation.md`
- [x] 1.10 Hardware Support for Virtualization and Isolation — `ch10-hardware-virtualization.md`

## Volume 2 — Operating Systems and Linux (`vol-02-operating-systems-linux/`)

- [x] 2.01 The Process Model — `ch01-process-model.md`
- [x] 2.02 CPU Scheduling: CFS, Real-Time, cgroups — `ch02-scheduling.md`
- [x] 2.03 Virtual Memory and Paging — `ch03-virtual-memory.md`
- [x] 2.04 Memory in Practice: Allocators, Page Cache, Huge Pages, OOM — `ch04-memory-practice.md`
- [x] 2.05 System Calls and the Kernel Boundary — `ch05-system-calls.md`
- [x] 2.06 File Systems and the VFS — `ch06-filesystems-vfs.md`
- [x] 2.07 Linux I/O: Blocking, epoll, io_uring — `ch07-linux-io.md`
- [x] 2.08 Signals, Pipes, and IPC — `ch08-ipc.md`
- [x] 2.09 Namespaces, cgroups, and Container Internals — `ch09-namespaces-cgroups.md`
- [x] 2.10 The Linux Network Stack — `ch10-linux-network-stack.md`
- [x] 2.11 Performance Analysis: perf, ftrace, eBPF — `ch11-perf-ebpf.md`
- [x] 2.12 Boot, init, and systemd — `ch12-boot-systemd.md`

## Volume 3 — Networking for Backend Engineers (`vol-03-networking/`)

- [x] 3.01 The Journey of a Packet — `ch01-journey-of-a-packet.md`
- [x] 3.02 IP, Routing, Subnetting, NAT — `ch02-ip-routing-nat.md`
- [x] 3.03 TCP in Depth — `ch03-tcp-in-depth.md`
- [x] 3.04 UDP and QUIC — `ch04-udp-quic.md`
- [x] 3.05 DNS in Depth — `ch05-dns.md`
- [x] 3.06 TLS 1.3 and the Web PKI — `ch06-tls-pki.md`
- [x] 3.07 HTTP/1.1, HTTP/2, HTTP/3 — `ch07-http.md`
- [x] 3.08 gRPC and RPC Framework Internals — `ch08-grpc-rpc.md`
- [x] 3.09 Load Balancing: L4, L7, Algorithms — `ch09-load-balancing.md`
- [x] 3.10 Proxies, Service Mesh, and CDNs — `ch10-proxies-mesh-cdn.md`
- [x] 3.11 Network Reliability: Timeouts, Retries, Backoff, Hedging — `ch11-network-reliability.md`
- [x] 3.12 Debugging and Observing Networks — `ch12-network-debugging.md`

## Volume 4 — Concurrency and Parallelism (`vol-04-concurrency/`)

- [x] 4.01 Models of Concurrency — `ch01-models.md`
- [x] 4.02 Threads, Mutual Exclusion, and Locks — `ch02-threads-locks.md`
- [x] 4.03 Memory Models and Happens-Before — `ch03-memory-models.md`
- [x] 4.04 Atomics, CAS, and Lock-Free Data Structures — `ch04-lock-free.md`
- [x] 4.05 Deadlock, Livelock, and Starvation — `ch05-deadlock.md`
- [x] 4.06 Asynchronous I/O and Event Loops — `ch06-async-io.md`
- [x] 4.07 The Actor Model, CSP, and Channels — `ch07-actors-csp.md`
- [x] 4.08 Coroutines and Structured Concurrency — `ch08-structured-concurrency.md`
- [x] 4.09 Concurrency Patterns for Backend Services — `ch09-patterns.md`
- [x] 4.10 Testing and Debugging Concurrent Systems — `ch10-testing-concurrency.md`

## Volume 5 — Databases and Storage Systems (`vol-05-databases/`)

- [x] 5.01 The Relational Model and SQL Semantics — `ch01-relational-sql.md`
- [x] 5.02 Storage Engines: B-Trees vs LSM-Trees — `ch02-storage-engines.md`
- [x] 5.03 Indexing in Depth — `ch03-indexing.md`
- [x] 5.04 Query Processing and Optimization — `ch04-query-optimization.md`
- [x] 5.05 Transactions and ACID — `ch05-transactions-acid.md`
- [x] 5.06 Isolation Levels and MVCC — `ch06-isolation-mvcc.md`
- [x] 5.07 Write-Ahead Logging and Crash Recovery — `ch07-wal-recovery.md`
- [x] 5.08 Replication: Physical, Logical, Sync, Async — `ch08-replication.md`
- [x] 5.09 Partitioning and Sharding — `ch09-partitioning-sharding.md`
- [ ] 5.10 Distributed Transactions: 2PC, Sagas — `ch10-distributed-transactions.md`
- [ ] 5.11 NoSQL: KV, Document, Wide-Column, Graph — `ch11-nosql.md`
- [ ] 5.12 NewSQL and Distributed SQL — `ch12-newsql.md`
- [ ] 5.13 Specialized Stores: Search, Time-Series, Analytics — `ch13-specialized-stores.md`
- [ ] 5.14 Operating Databases: Pooling, Migrations, Scaling — `ch14-operating-databases.md`

## Volume 6 — Distributed Systems (`vol-06-distributed-systems/`)

- [ ] 6.01 Foundations: Models, Failures, Assumptions — `ch01-foundations.md`
- [ ] 6.02 Time, Clocks, and Ordering — `ch02-time-clocks.md`
- [ ] 6.03 Replication and Consistency Models — `ch03-consistency-models.md`
- [ ] 6.04 CAP, PACELC, and Trade-Offs — `ch04-cap-pacelc.md`
- [ ] 6.05 Consensus I: Paxos — `ch05-paxos.md`
- [ ] 6.06 Consensus II: Raft — `ch06-raft.md`
- [ ] 6.07 Quorum Systems and Dynamo-Style Replication — `ch07-quorums-dynamo.md`
- [ ] 6.08 Coordination Services: ZooKeeper and etcd — `ch08-coordination.md`
- [ ] 6.09 Idempotency, Deduplication, Exactly-Once — `ch09-idempotency.md`
- [ ] 6.10 Failure Detection and Membership: Gossip, SWIM — `ch10-failure-detection.md`
- [ ] 6.11 CRDTs and Eventual Consistency — `ch11-crdts.md`
- [ ] 6.12 Testing Distributed Systems: Jepsen, Chaos, Simulation — `ch12-testing.md`

## Volume 7 — System Design and Architecture (`vol-07-system-design/`)

- [ ] 7.01 Principles of Scalable System Design — `ch01-principles.md`
- [ ] 7.02 Estimation and Capacity Planning — `ch02-estimation.md`
- [ ] 7.03 Caching Strategies at Scale — `ch03-caching.md`
- [ ] 7.04 Load Balancing and Traffic Management — `ch04-traffic-management.md`
- [ ] 7.05 Data Modeling for Scale — `ch05-data-modeling.md`
- [ ] 7.06 Monolith, Microservices, and Between — `ch06-monolith-microservices.md`
- [ ] 7.07 Event-Driven Architecture — `ch07-event-driven.md`
- [ ] 7.08 API Gateways, BFF, and Edge — `ch08-gateways-edge.md`
- [ ] 7.09 Rate Limiting, Quotas, and Fairness — `ch09-rate-limiting.md`
- [ ] 7.10 Multi-Region and Geo-Distributed Systems — `ch10-multi-region.md`
- [ ] 7.11 Designing for Failure — `ch11-designing-for-failure.md`
- [ ] 7.12 Design Case Studies — `ch12-case-studies.md`

## Volume 8 — APIs and Service Design (`vol-08-apis/`)

- [ ] 8.01 API Design Principles and Contracts — `ch01-principles.md`
- [ ] 8.02 REST in Depth — `ch02-rest.md`
- [ ] 8.03 gRPC and Protobuf Schema Design — `ch03-grpc-protobuf.md`
- [ ] 8.04 GraphQL for Backend Engineers — `ch04-graphql.md`
- [ ] 8.05 Versioning and Evolution — `ch05-versioning.md`
- [ ] 8.06 Idempotency, Pagination, Filtering — `ch06-idempotency-pagination.md`
- [ ] 8.07 Error Handling and Status Semantics — `ch07-error-handling.md`
- [ ] 8.08 Compatibility and Wire Formats — `ch08-compatibility.md`

## Volume 9 — Security, Authentication, and Cryptography (`vol-09-security-auth/`)

- [ ] 9.01 Applied Cryptography for Engineers — `ch01-applied-crypto.md`
- [ ] 9.02 Hashing, MACs, KDFs, Password Storage — `ch02-hashing-passwords.md`
- [ ] 9.03 Symmetric and Asymmetric Encryption in Practice — `ch03-encryption.md`
- [ ] 9.04 Certificates, PKI, and TLS Operations — `ch04-pki-tls-ops.md`
- [ ] 9.05 Authentication: Sessions, Tokens, JWTs — `ch05-authentication.md`
- [ ] 9.06 OAuth 2.0 and OpenID Connect — `ch06-oauth-oidc.md`
- [ ] 9.07 Authorization: RBAC, ABAC, ReBAC (Zanzibar) — `ch07-authorization.md`
- [ ] 9.08 Secrets Management — `ch08-secrets-management.md`
- [ ] 9.09 Application Security: OWASP, Injection, SSRF — `ch09-appsec.md`
- [ ] 9.10 Zero Trust and Service-to-Service Auth: mTLS, SPIFFE — `ch10-zero-trust-mtls.md`
- [ ] 9.11 Threat Modeling and Secure Design — `ch11-threat-modeling.md`

## Volume 10 — Messaging, Streaming, and Event Systems (`vol-10-messaging-streaming/`)

- [ ] 10.01 Messaging Fundamentals: Queues, Logs, Pub/Sub — `ch01-fundamentals.md`
- [ ] 10.02 Delivery Semantics — `ch02-delivery-semantics.md`
- [ ] 10.03 Apache Kafka Architecture — `ch03-kafka.md`
- [ ] 10.04 Stream Processing — `ch04-stream-processing.md`
- [ ] 10.05 Event Sourcing and CQRS — `ch05-event-sourcing-cqrs.md`
- [ ] 10.06 The Outbox Pattern and the Dual-Write Problem — `ch06-outbox.md`
- [ ] 10.07 Backpressure and Flow Control — `ch07-backpressure.md`
- [ ] 10.08 Dead Letters, Retries, Poison Messages — `ch08-dead-letters.md`

## Volume 11 — Reliability, Observability, and SRE (`vol-11-reliability-sre/`)

- [ ] 11.01 SLIs, SLOs, and Error Budgets — `ch01-slos.md`
- [ ] 11.02 Metrics and the Golden Signals — `ch02-metrics.md`
- [ ] 11.03 Logging at Scale — `ch03-logging.md`
- [ ] 11.04 Distributed Tracing and OpenTelemetry — `ch04-tracing.md`
- [ ] 11.05 Incident Response and On-Call — `ch05-incident-response.md`
- [ ] 11.06 Blameless Postmortems — `ch06-postmortems.md`
- [ ] 11.07 Load Testing and Capacity Planning — `ch07-load-testing.md`
- [ ] 11.08 Chaos Engineering — `ch08-chaos.md`
- [ ] 11.09 Deployment Strategies: Blue/Green, Canary, Flags — `ch09-deployment-strategies.md`
- [ ] 11.10 Resilience Patterns in Production — `ch10-resilience-patterns.md`

## Volume 12 — Cloud, Containers, and Infrastructure (`vol-12-cloud-infra/`)

- [ ] 12.01 Containers Deep Dive — `ch01-containers.md`
- [ ] 12.02 Kubernetes Architecture — `ch02-kubernetes-architecture.md`
- [ ] 12.03 Kubernetes Workloads, Networking, Storage — `ch03-kubernetes-workloads.md`
- [ ] 12.04 Infrastructure as Code — `ch04-iac.md`
- [ ] 12.05 Cloud Primitives: Compute, Storage, Network — `ch05-cloud-primitives.md`
- [ ] 12.06 Managed Data and Platform Services — `ch06-managed-services.md`
- [ ] 12.07 Multi-Tenancy and Isolation — `ch07-multi-tenancy.md`
- [ ] 12.08 Cloud Cost and Capacity Engineering — `ch08-cost-capacity.md`

## Volume 13 — Language Runtimes for Backend (`vol-13-runtimes/`)

- [ ] 13.01 The JVM: Memory, GC, JIT — `ch01-jvm.md`
- [ ] 13.02 The Go Runtime: Scheduler, Memory Model, GC — `ch02-go-runtime.md`
- [ ] 13.03 Rust for Backend Systems — `ch03-rust.md`
- [ ] 13.04 Garbage Collection Across Runtimes — `ch04-gc.md`
- [ ] 13.05 Profiling and Performance Tuning — `ch05-profiling.md`

## Volume 14 — Data Structures and Algorithms for Backend (`vol-14-algorithms/`)

- [ ] 14.01 Complexity That Matters in Practice — `ch01-complexity.md`
- [ ] 14.02 Hashing and Hash Tables at Scale — `ch02-hashing.md`
- [ ] 14.03 Balanced Trees and Ordered Structures — `ch03-trees.md`
- [ ] 14.04 Probabilistic Structures: Bloom, HLL, Count-Min — `ch04-probabilistic.md`
- [ ] 14.05 Consistent Hashing and Rendezvous Hashing — `ch05-consistent-hashing.md`
- [ ] 14.06 Sorting, External Sorting, Streaming — `ch06-sorting.md`
- [ ] 14.07 Graphs in Systems — `ch07-graphs.md`
- [ ] 14.08 Rate-Limiting and Scheduling Algorithms — `ch08-rate-limiting-scheduling.md`

## Volume 15 — Software Engineering Practice (`vol-15-swe-practice/`)

- [ ] 15.01 Testing Strategy — `ch01-testing-strategy.md`
- [ ] 15.02 Design Docs, RFCs, Decision-Making — `ch02-design-docs.md`
- [ ] 15.03 Domain-Driven Design for Backend — `ch03-ddd.md`
- [ ] 15.04 Design Patterns and Anti-Patterns for Services — `ch04-patterns.md`
- [ ] 15.05 Refactoring and Managing Technical Debt — `ch05-refactoring.md`
- [ ] 15.06 Code Review and Engineering Culture — `ch06-code-review.md`

## Log

- 2026-07-31: Repo initialized; plan, style guide, and book scaffolding created.
- 2026-07-31: Batch 1 done (1.01–1.03), committed and pushed. Next: batch 2 = 1.04, 1.05, 1.06.
- 2026-07-31: Scope expanded to full backend curriculum (Volumes 1–15 added; supply chain = Vol 0).
- 2026-07-31: Vol 0 Book 1 Ch 4–5 done and pushed; Ch 6 in progress.
- 2026-07-31: Batch 3 done (1.07–1.09). Next batch: 1.10 (finish Book 1) + 2.01 + 2.02.
- 2026-07-31: Book 1 complete (10/10). Batch 4 done (1.10, 2.01, 2.02). Next: 2.03, 2.04, 2.05.
- 2026-07-31: Book 2 complete (10/10). Batch 7 done (2.09, 2.10, 3.01). Next: 3.02, 3.03, 3.04.
- 2026-07-31: Book 3 complete (9/9). Batch 10 done (3.08, 3.09, 4.01). Next: 4.02, 4.03, 4.04.
- 2026-07-31: Book 4 complete (10/10). Batch 13 done (4.08, 4.09, 4.10). Next: 5.01, 5.02, 5.03.
- 2026-07-31: Book 5 complete (10/10). Batch 17 done (5.10, 6.01, 6.02). Next: 6.03, 6.04, 6.05.
- 2026-07-31: Book 6 complete (10/10). Batch 20 done (6.09, 6.10, 7.01). Next: 7.02, 7.03, 7.04.
- 2026-07-31: Book 7 complete (8/8). Batch 23 done (7.08, 8.01, 8.02). Next: 8.03, 8.04, 8.05.
- 2026-07-31: *** VOLUME 0 (Software Supply Chain Security) COMPLETE — all 8 books, 75 chapters. ***
- 2026-07-31: Batch 25 done (8.06, 8.07, 8.08). Next: begin Volume 1 (Computer Architecture): 1.01, 1.02, 1.03.
- 2026-07-31: Vol 1 batch 27 done (1.04, 1.05, 1.06). Next: 1.07, 1.08, 1.09.
- 2026-07-31: *** VOLUME 1 (Computer Architecture) COMPLETE — 10 chapters. *** Vol 2 started (2.01 done).
- 2026-07-31: Batches 28-29 done (1.07-1.10, 2.01). Next: 2.02, 2.03, 2.04.
- 2026-07-31: Vol 2 batch 31 done (2.05, 2.06, 2.07). Next: 2.08, 2.09, 2.10.
- 2026-08-14: Vol 4 batch 1 done (4.01-4.04). Written directly after the Workflow subagent
  harness failed three runs with permission-handler errors. Next: 4.05, 4.06, 4.07.
- 2026-08-14: *** VOLUME 4 (Concurrency) COMPLETE — 10 chapters. *** Vol 5 started: 5.01, 5.03-5.06 done
  (agent batch interrupted by session limit; 5.02, 5.07-5.10 to re-run). Volumes 5-15 scaffolded.
