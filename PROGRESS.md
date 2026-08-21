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
- [x] 5.10 Distributed Transactions: 2PC, Sagas — `ch10-distributed-transactions.md`
- [x] 5.11 NoSQL: KV, Document, Wide-Column, Graph — `ch11-nosql.md`
- [x] 5.12 NewSQL and Distributed SQL — `ch12-newsql.md`
- [x] 5.13 Specialized Stores: Search, Time-Series, Analytics — `ch13-specialized-stores.md`
- [x] 5.14 Operating Databases: Pooling, Migrations, Scaling — `ch14-operating-databases.md`

## Volume 6 — Distributed Systems (`vol-06-distributed-systems/`)

- [x] 6.01 Foundations: Models, Failures, Assumptions — `ch01-foundations.md`
- [x] 6.02 Time, Clocks, and Ordering — `ch02-time-clocks.md`
- [x] 6.03 Replication and Consistency Models — `ch03-consistency-models.md`
- [x] 6.04 CAP, PACELC, and Trade-Offs — `ch04-cap-pacelc.md`
- [x] 6.05 Consensus I: Paxos — `ch05-paxos.md`
- [x] 6.06 Consensus II: Raft — `ch06-raft.md`
- [x] 6.07 Quorum Systems and Dynamo-Style Replication — `ch07-quorums-dynamo.md`
- [x] 6.08 Coordination Services: ZooKeeper and etcd — `ch08-coordination.md`
- [x] 6.09 Idempotency, Deduplication, Exactly-Once — `ch09-idempotency.md`
- [x] 6.10 Failure Detection and Membership: Gossip, SWIM — `ch10-failure-detection.md`
- [x] 6.11 CRDTs and Eventual Consistency — `ch11-crdts.md`
- [x] 6.12 Testing Distributed Systems: Jepsen, Chaos, Simulation — `ch12-testing.md`

## Volume 7 — System Design and Architecture (`vol-07-system-design/`)

- [x] 7.01 Principles of Scalable System Design — `ch01-principles.md`
- [x] 7.02 Estimation and Capacity Planning — `ch02-estimation.md`
- [x] 7.03 Caching Strategies at Scale — `ch03-caching.md`
- [x] 7.04 Load Balancing and Traffic Management — `ch04-traffic-management.md`
- [x] 7.05 Data Modeling for Scale — `ch05-data-modeling.md`
- [x] 7.06 Monolith, Microservices, and Between — `ch06-monolith-microservices.md`
- [x] 7.07 Event-Driven Architecture — `ch07-event-driven.md`
- [x] 7.08 API Gateways, BFF, and Edge — `ch08-gateways-edge.md`
- [x] 7.09 Rate Limiting, Quotas, and Fairness — `ch09-rate-limiting.md`
- [x] 7.10 Multi-Region and Geo-Distributed Systems — `ch10-multi-region.md`
- [x] 7.11 Designing for Failure — `ch11-designing-for-failure.md`
- [x] 7.12 Design Case Studies — `ch12-case-studies.md`

## Volume 8 — APIs and Service Design (`vol-08-apis/`)

- [x] 8.01 API Design Principles and Contracts — `ch01-principles.md`
- [x] 8.02 REST in Depth — `ch02-rest.md`
- [x] 8.03 gRPC and Protobuf Schema Design — `ch03-grpc-protobuf.md`
- [x] 8.04 GraphQL for Backend Engineers — `ch04-graphql.md`
- [x] 8.05 Versioning and Evolution — `ch05-versioning.md`
- [x] 8.06 Idempotency, Pagination, Filtering — `ch06-idempotency-pagination.md`
- [x] 8.07 Error Handling and Status Semantics — `ch07-error-handling.md`
- [x] 8.08 Compatibility and Wire Formats — `ch08-compatibility.md`
- [x] 8.09 API Governance, Linting, and Breaking-Change Detection — `ch09-governance.md`
- [x] 8.10 Schema Registry, Code Generation, and SDK Delivery — `ch10-codegen.md`
- [x] 8.11 Contract Testing and API Evolution in Practice — `ch11-contract-testing.md`

## Volume 9 — Security, Authentication, and Cryptography (`vol-09-security-auth/`)

- [x] 9.01 Applied Cryptography for Engineers — `ch01-applied-crypto.md`
- [x] 9.02 Hashing, MACs, KDFs, Password Storage — `ch02-hashing-passwords.md`
- [x] 9.03 Symmetric and Asymmetric Encryption in Practice — `ch03-encryption.md`
- [x] 9.04 Certificates, PKI, and TLS Operations — `ch04-pki-tls-ops.md`
- [x] 9.05 Authentication: Sessions, Tokens, JWTs — `ch05-authentication.md`
- [x] 9.06 OAuth 2.0 and OpenID Connect — `ch06-oauth-oidc.md`
- [x] 9.07 Authorization: RBAC, ABAC, ReBAC (Zanzibar) — `ch07-authorization.md`
- [x] 9.08 Secrets Management — `ch08-secrets-management.md`
- [x] 9.09 Application Security: OWASP, Injection, SSRF — `ch09-appsec.md`
- [x] 9.10 Zero Trust and Service-to-Service Auth: mTLS, SPIFFE — `ch10-zero-trust-mtls.md`
- [x] 9.11 Threat Modeling and Secure Design — `ch11-threat-modeling.md`

## Volume 10 — Messaging, Streaming, and Event Systems (`vol-10-messaging-streaming/`)

- [x] 10.01 Messaging Fundamentals: Queues, Logs, Pub/Sub — `ch01-fundamentals.md`
- [x] 10.02 Delivery Semantics — `ch02-delivery-semantics.md`
- [x] 10.03 Apache Kafka Architecture — `ch03-kafka.md`
- [x] 10.04 Stream Processing — `ch04-stream-processing.md`
- [x] 10.05 Event Sourcing and CQRS — `ch05-event-sourcing-cqrs.md`
- [x] 10.06 The Outbox Pattern and the Dual-Write Problem — `ch06-outbox.md`
- [x] 10.07 Backpressure and Flow Control — `ch07-backpressure.md`
- [x] 10.08 Dead Letters, Retries, Poison Messages — `ch08-dead-letters.md`

## Volume 11 — Reliability, Observability, and SRE (`vol-11-reliability-sre/`)

- [x] 11.01 SLIs, SLOs, and Error Budgets — `ch01-slos.md`
- [x] 11.02 Metrics and the Golden Signals — `ch02-metrics.md`
- [x] 11.03 Logging at Scale — `ch03-logging.md`
- [x] 11.04 Distributed Tracing and OpenTelemetry — `ch04-tracing.md`
- [x] 11.05 Incident Response and On-Call — `ch05-incident-response.md`
- [x] 11.06 Blameless Postmortems — `ch06-postmortems.md`
- [x] 11.07 Load Testing and Capacity Planning — `ch07-load-testing.md`
- [x] 11.08 Chaos Engineering — `ch08-chaos.md`
- [x] 11.09 Deployment Strategies: Blue/Green, Canary, Flags — `ch09-deployment-strategies.md`
- [x] 11.10 Resilience Patterns in Production — `ch10-resilience-patterns.md`

## Volume 12 — Cloud, Containers, and Infrastructure (`vol-12-cloud-infra/`)

- [x] 12.01 Containers Deep Dive — `ch01-containers.md`
- [x] 12.02 Kubernetes Architecture — `ch02-kubernetes-architecture.md`
- [x] 12.03 Kubernetes Workloads, Networking, Storage — `ch03-kubernetes-workloads.md`
- [x] 12.04 Infrastructure as Code — `ch04-iac.md`
- [x] 12.05 Cloud Primitives: Compute, Storage, Network — `ch05-cloud-primitives.md`
- [x] 12.06 Managed Data and Platform Services — `ch06-managed-services.md`
- [x] 12.07 Multi-Tenancy and Isolation — `ch07-multi-tenancy.md`
- [x] 12.08 Cloud Cost and Capacity Engineering — `ch08-cost-capacity.md`
- [x] 12.09 Capacity Planning and Performance at Cloud Scale — `ch09-capacity-performance.md`
- [x] 12.10 Cloud Networking, IAM, and Security Foundations — `ch10-cloud-networking-iam.md`
- [x] 12.11 Platform Engineering: Paved Roads and IDPs — `ch11-platform-engineering.md`

## Volume 13 — Language Runtimes for Backend (`vol-13-runtimes/`)

- [x] 13.01 The JVM: Memory, GC, JIT — `ch01-jvm.md`
- [x] 13.02 The Go Runtime: Scheduler, Memory Model, GC — `ch02-go-runtime.md`
- [x] 13.03 Rust for Backend Systems — `ch03-rust.md`
- [x] 13.04 Garbage Collection Across Runtimes — `ch04-gc.md`
- [x] 13.05 Profiling and Performance Tuning — `ch05-profiling.md`
- [x] 13.06 Python and Node.js Runtimes for Backend — `ch06-python-node.md`
- [x] 13.07 WebAssembly and Emerging Runtimes — `ch07-wasm.md`
- [x] 13.08 FFI, Native Extensions, and Polyglot Interop — `ch08-ffi.md`
- [x] 13.09 Runtime Selection and Performance Trade-offs — `ch09-runtime-selection.md`

## Volume 14 — Data Structures and Algorithms for Backend (`vol-14-algorithms/`)

- [x] 14.01 Complexity That Matters in Practice — `ch01-complexity.md`
- [x] 14.02 Hashing and Hash Tables at Scale — `ch02-hashing.md`
- [x] 14.03 Balanced Trees and Ordered Structures — `ch03-trees.md`
- [x] 14.04 Probabilistic Structures: Bloom, HLL, Count-Min — `ch04-probabilistic.md`
- [x] 14.05 Consistent Hashing and Rendezvous Hashing — `ch05-consistent-hashing.md`
- [x] 14.06 Sorting, External Sorting, Streaming — `ch06-sorting.md`
- [x] 14.07 Graphs in Systems — `ch07-graphs.md`
- [x] 14.08 Rate-Limiting and Scheduling Algorithms — `ch08-rate-limiting-scheduling.md`

## Volume 15 — Software Engineering Practice (`vol-15-swe-practice/`)

- [x] 15.01 Testing Strategy: Unit, Integration, E2E, Property-Based — `ch01-testing-strategy.md`
- [x] 15.02 Contract Testing, Test Doubles, Testability — `ch02-contract-testing.md`
- [x] 15.03 Load, Performance, and Chaos Testing — `ch03-load-testing.md`
- [x] 15.04 Design Docs, RFCs, and Technical Decision-Making — `ch04-design-docs.md`
- [x] 15.05 Domain-Driven Design for Backend — `ch05-ddd.md`
- [x] 15.06 Design Patterns and Anti-Patterns for Services — `ch06-patterns.md`
- [x] 15.07 Refactoring and Managing Technical Debt — `ch07-refactoring.md`
- [x] 15.08 Code Review and Engineering Culture — `ch08-code-review.md`
- [x] 15.09 Debugging and Incident-Driven Learning — `ch09-debugging.md`
- [x] 15.10 Building High-Performing Engineering Teams — `ch10-teams.md`

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
- 2026-08-14: *** VOLUME 6 (Distributed Systems) COMPLETE — 12 chapters. *** Vol 7 batch 1 (7.01-7.06) in flight.
- 2026-08-20: Vol08 ch01-ch03 done (principles, REST, gRPC/protobuf). Next: 8.04-8.06.
- 2026-08-20: Heavy-tail trim batch 2 committed (20 files -> <=7300w, 17 remain >7300). Vol07 ch04-ch06 done (traffic, data modeling, monolith/microservices, ~4.0-4.3kw each, 3-4 Mermaid). Next: 7.07-7.09.
- 2026-08-20: Vol08 ch04-ch06 done (GraphQL, versioning, idempotency/pagination — ~4.1-5.0kw each, 3-4 Mermaid). Next: 8.07-8.09.
- 2026-08-20: Vol07 ch07-ch09 done (event-driven/Kafka/CDC/outbox/Saga, gateways/BFF/edge, rate limiting/quotas/fairness — ~4.4-5.4kw each, 4 Mermaid). Next: 7.10-7.12.
- 2026-08-20: Vol09 ch07-ch09 done (authorization RBAC/ABAC/ReBAC Zanzibar/SpiceDB, secrets management Vault, AppSec OWASP/injection/SSRF/deserialization — ~4.9-5.1kw each, 3-6 Mermaid). Next: 9.10-9.11.
- 2026-08-20: *** VOLUME 7 (System Design) COMPLETE — 12 chapters. *** Vol07 ch10-ch12 done (multi-region/geo-distributed, designing for failure bulkheads/breakers/shedding, case studies feed/chat/notifications/global KV — ~4.0-6.3kw each, 4-6 Mermaid). Next: 8.07-8.09 + 9.10 batch.
- 2026-08-20: Vol08 ch07-ch08 + Vol09 ch10 done (error handling/status semantics, compatibility/wire formats, zero trust/mTLS/SPIFFE — ~5.5-6.5kw each, 4-6 Mermaid). Next: 8.09-8.11 + 9.11.
- 2026-08-20: Vol10 ch04-ch06 done (stream processing Flink/Kafka Streams, event sourcing/CQRS Postgres+EventStoreDB, outbox/dual-write/Debezium CDC — ~4.6-5.4kw each, 4-5 Mermaid). Next: 10.07-10.08.
- 2026-08-20: *** VOLUME 9 (Security) COMPLETE — 11 chapters. *** *** VOLUME 10 (Messaging/Streaming) COMPLETE — 8 chapters. *** Vol10 ch07-ch08 + Vol09 ch11 done (backpressure/flow control, DLQ/retries/poison, threat modeling/STRIDE — ~4.5-5.5kw each, 3-6 Mermaid). Next: Vol11 ch04-ch06.
- 2026-08-20: *** VOLUME 8 (APIs) COMPLETE — 11 chapters. *** Vol08 ch09-ch11 done (governance/linting/breaking-change, schema registry/codegen/SDK delivery, contract testing/evolution — ~5.3-5.7kw each, 2-4 Mermaid). Next: Vol11 batch.
- 2026-08-20: Vol12 ch01-ch03 done (containers deep dive OCI/runc/gVisor/Kata, K8s control/data plane etcd/scheduler/controllers/kubelet, workloads/networking/storage Deployments/StatefulSets/Services/Gateway/CSI — ~5.0-8.0kw each, 4-6 Mermaid). Next: 12.04-12.06.
- 2026-08-20: Vol11 ch04-ch06 done (distributed tracing & OTel Collector agent+gateway/tail sampling/W3C propagation, incident response lifecycle/severity/on-call/Alertmanager/PagerDuty/runbooks, blameless postmortems template/facilitation/action items — ~6.8-8.5kw each, 4-5 Mermaid). Next: 11.07-11.10.
- 2026-08-20: Vol14 ch01-ch03 done (complexity/RAM vs I/O model/benchmarking, hashing/SwissTable/Robin Hood/concurrent maps, AVL/RB/B-tree/B+tree/skip list — ~3.3-4.6kw each, 3-5 Mermaid, real code + benchmarks). Next: 14.04-14.06.
- 2026-08-20: Vol13 ch01-ch03 done (JVM memory/G1/ZGC/JIT/tuning, Go scheduler P/M/G + memory model + tri-color GC, Rust ownership/borrowing/tokio/axum — ~5-8kw each, 4-6 Mermaid, real configs/traces). Next: 13.04-13.06.
- 2026-08-20: Vol11 ch07-ch09 done (load testing open/closed models/USL/k6+Vegeta+distributed, chaos hypothesis lifecycle/Chaos Mesh+Litmus+FIS/safety gates/game days, deployment strategies rolling/blue-green/canary Argo Rollouts+Flagger/Gateway API/feature flags OpenFeature — ~6-9kw each, 2-7 Mermaid). Next: 11.10.
- 2026-08-20: Vol12 ch04-ch06 done (IaC declarative/HCL/Terraform+OpenTofu/state/pipeline/policy/testing/secrets, cloud primitives EC2/S3+EBS+EFS/VPC+ALB+CloudFront, managed RDS+Aurora+ElastiCache+OpenSearch+SQS+SNS+Kinesis+Secrets+ECR+AppConfig — ~5.7-6.1kw each, 4-6 Mermaid). Next: 12.09-12.11.
- 2026-08-20: Vol12 ch09-ch11 done (capacity planning Little/USL/queueing + HPA/KEDA/Karpenter/ASG + Graviton, cloud networking VPC/subnets/PrivateLink + IAM least-privilege/IRSA/SPIFFE + GuardDuty, platform engineering paved roads/IDP/Backstage templates+TechDocs+scorecards — ~4.1-4.6kw each, 3-5 Mermaid). Vol 12 remaining tail: 12.07-12.08 (multi-tenancy, cost/FinOps).
- 2026-08-20: *** VOLUME 11 (Reliability/SRE) COMPLETE — 10 chapters. *** *** VOLUME 12 (Cloud/Infra) COMPLETE — 11 chapters. *** Vol11 ch10 done (resilience: timeouts/deadlines/hedging, retries with jitter+budgets, circuit breakers Resilience4j+Istio+Envoy state machine, bulkheads, adaptive concurrency limiting, fallbacks, composition order, chaos validation — ~5.5kw, 4 Mermaid). Vol12 ch07-ch08 done (multi-tenancy silo/pool/bridge/cells + K8s tenancy quotas/NetworkPolicy/gVisor/Kata + RLS/per-tenant KMS + noisy-neighbor; cloud cost CUR/Athena+tagging, pricing models RI/SP/spot/Graviton, right-sizing VPA/HPA/Karpenter, storage/transfer/managed costs, capacity math USL/Little's Law, FinOps budgets+OPA — ~4.2-4.6kw each, 3-4 Mermaid). Next: Vol13 13.04-13.09 + Vol14 14.04-14.08 + Vol15 15.01-15.10 (remaining 21).
- 2026-08-20: *** VOLUME 13 (Runtimes) COMPLETE — 9 chapters. *** Vol13 ch04-ch06 done (GC across runtimes G1/ZGC/Shenandoah/Go tri-color/V8 Orinoco/CPython/.NET generational, profiling sampling/eBPF perf/async-profiler/pprof/py-spy/clinic, Python GIL+free-threaded 3.13t/asyncio+ASGI and Node V8+libuv/event loop/workers/cluster — ~3.8-5.5kw each, 3-6 Mermaid). Vol13 ch07-ch09 done (Wasm sandbox/Component Model/WASI Wasmtime/WasmEdge/Spin+Fastly, FFI JNI/Panama/cgo/pyo3/N-API ownership+signal+thread failure modes, runtime selection benchmarks/TCO/selection matrix/strangler+shadow migration — ~4.3-6.2kw each, 2-4 Mermaid, real Wasm/JNI/FFI/bench configs).
- 2026-08-20: Vol14 ch04-ch06 done (probabilistic: Bloom sizing/FPR+vnode impl/Cuckoo+counting+blocked variants+LSM use+RocksDB, HLL harmonic mean+sparse/dense+bias correction+Redis PFADD+12KB@1M, CMS ε·N guarantee+conservative update+CMS+heap top-K; consistent hashing ring+vnodes V=100-200 balance/churn/weighted+bounded loads+rack-aware replication vs rendezvous HRW O(N) stateless + Jump; sorting Ω(n log n) bound/introsort+Timsort, counting/radix/bucket O(n), external sort runs+k-way heap merge+replacement selection, streaming top-K/reservoir/sliding windows — 3 Mermaid ch04, 5 Mermaid ch05, 3 Mermaid ch06, real runnable code each). Next: 14.07-14.08 + 15.01-15.10 (remaining 12).
- 2026-08-20: *** VOLUME 14 (Algorithms) COMPLETE — 8 chapters. *** Vol14 ch07-ch08 done (graphs: adj list/matrix/edge/CSR + BFS/DFS + Dijkstra/Bellman-Ford/Floyd comparison + topo sort Kahn+DFS + cycle/SCC Kosaraju + Union-Find+Kruskal MST; rate limiting: fixed/sliding log/sliding counter/token bucket/leaky bucket/GCRA TAT + distributed Redis GCRA Lua + local/hybrid sharding + concurrency+adaptive Vegas + scheduling FIFO/priority/WFQ/DRR/EDF — 6 Mermaid ch07, 7 Mermaid ch08, real runnable code each). Next: Vol15 15.01-15.10 (remaining 10).
- 2026-08-20: Vol15 ch01-ch03 done (testing strategy pyramid/diamond/trophy+unit table-driven/Testcontainers/Playwright E2E/property-based Hypothesis/fast-check/gopter+flakiness/CI staging; contract testing test-double taxonomy fakes> mocks+Pact consumer/provider/Broker can-i-deploy+OpenAPI/buf breaking/WireMock; load/perf/chaos k6/Vegeta/Gatling open/closed workload models+profiling hierarchy+Chaos Mesh/Litmus/Toxiproxy+Istio fault injection+staged pipeline — 3 Mermaid ch01, 4 Mermaid ch02, 4 Mermaid ch03, runnable k6/Pact/Chaos configs each). Next: 15.04-15.10 (remaining 7).
- 2026-08-20: Vol15 ch04-ch06 done (design docs/RFCs decision matrix+RFC lifecycle+full RFC+ADR templates+DACI/consent/lazy-consensus+async-first review+case study; DDD ubiquitous language+entities/value objects/aggregates+bounded contexts/context map 7 relationships+ACL translator+domain events outbox+strangler-fig decomposition+when-not-to-use; patterns/anti-patterns catalog hexagonal/clean ports-and-adapters+layered vs vertical slice+gateway/BFF/sidecar+idempotency+resilience composition order+outbox/saga/CQRS+strategy/decorator/observer+distributed-monolith/shared-DB/god-service/chatty/golden-hammer — 3 Mermaid ch04, 6 Mermaid ch05, 6 Mermaid ch06, real RFC/DDD/pattern templates each). Next: 15.07-15.10 (remaining 4).
- 2026-08-20: Vol15 ch07-ch09 done (refactoring catalog+branch-by-abstraction/expand-contract/strangler fig/flag-guarded cutover+schema/event/API expand-contract+hotspot×churn debt register+cost-of-delay+fitness functions+case study god-service strangling; code review authoring/PR template+layered reading+tiered checklists+automation gates/CODEOWNERS/SLAs+conventional comments+anti-patterns+DORA/psychological safety/paved road+rituals; debugging hypothesis log+trace/metrics/logs/profiles+eBPF/bpftrace/pprof+prod-safe flag/shadow+timeline/postmortem taxonomy+runbooks+knowledge base — 6 Mermaid ch07, 3 Mermaid ch08, 5 Mermaid ch09, ~5.5-8.2kw each, real templates each). Next: 15.10 (remaining 1).
- 2026-08-20: *** VOLUME 15 (Software Engineering Practice) COMPLETE — 10 chapters. *** *** MAIN LIBRARY COMPLETE — Volumes 1–15 (~142 ch) + Companion Series (75 ch supply-chain) — all chapters written. *** Vol15 ch10 done (high-performing teams: DORA four keys + SPACE five dimensions + DevEx/anti-Goodhart, Team Topologies 4 team types + 3 interaction modes, structured hiring scorecard/bar-raiser/bias audit, 30/60/90 onboarding with devcontainer+buddy, dual-track ladder IC2-6/M1-3 + SBI + calibration, async-first distributed operating model with decision logs/timezone rituals — 6 Mermaid, ~7.1kw, real scorecard/onboarding/charter/1:1 templates).

## Volume 16 — Python and CPython Internals (`vol-16-python-cpython-internals/`)

- [x] 16.01 CPython Architecture: Source to Execution — `ch01-cpython-architecture.md`
- [x] 16.02 Objects, Reference Counting, and the PyObject System — `ch02-objects-refcount.md`
- [x] 16.03 Bytecode, the ceval Loop, and Adaptive Specialization (PEP 659) — `ch03-bytecode-ceval.md`
- [x] 16.04 Memory Management: pymalloc, GC, Arenas, and Immortal Objects — `ch04-memory-management.md`
- [x] 16.05 The GIL: Mechanics, Evolution, Per-Interpreter GIL and Free-Threaded Python — `ch05-gil.md`
- [x] 16.06 The Type System: Classes, MRO, Descriptors, Slots, and the Attribute Protocol — `ch06-type-system.md`
- [x] 16.07 Functions, Closures, Generators, Coroutines, and async/await — `ch07-functions-closures-generators.md`
- [x] 16.08 Exceptions, Context Managers, and the Unwinding Machinery — `ch08-exceptions-context-managers.md`
- [x] 16.09 The Import System: importlib, Finders, Loaders, and Namespace Packages — `ch09-import-system.md`
- [x] 16.10 C Extensions, the C API, HPy, and Embedding CPython — `ch10-c-extensions.md`
- [x] 16.11 Performance: Profiling, the Copy-and-Patch JIT (PEP 744), Cython, and Alternative Runtimes — `ch11-performance.md`
- [x] 16.12 Packaging, Distribution, and Production Deployment at Scale — `ch12-packaging-deployment.md`

## Volume 17 — Golang and Go Internals (`vol-17-go-internals/`)

- [x] 17.01 The Go Toolchain: Modules, Build, Linker, and the Static Binary Model — `ch01-toolchain.md`
- [x] 17.02 Types, Memory Layout, and Generics Internals — `ch02-types-generics.md`
- [x] 17.03 Functions, Methods, Defer, Panic/Recover, and the ABI — `ch03-functions-abi.md`
- [x] 17.04 Goroutines, the Scheduler (G-M-P), and the Netpoller — `ch04-scheduler-netpoller.md`
- [x] 17.05 Memory Allocator, Stacks, and the Concurrent Tri-Color GC — `ch05-allocator-gc.md`
- [x] 17.06 The Go Memory Model, Atomics, and Synchronization Primitives — `ch06-memory-model.md`
- [x] 17.07 Interfaces, Reflection, and `unsafe` — `ch07-interfaces-reflection.md`
- [x] 17.08 Channels, Select, Timers, and Context Internals — `ch08-channels-select.md`
- [x] 17.09 Compiler Pipeline: SSA, Escape Analysis, and Optimizations — `ch09-compiler-ssa.md`
- [x] 17.10 Tooling Deep Dive: Race Detector, pprof, execution trace, and vet — `ch10-tooling.md`
- [x] 17.11 cgo, Assembly, and Foreign-Function Interoperability — `ch11-cgo-assembly.md`
- [x] 17.12 Production Go: Cross-Compilation, Workspaces, Telemetry, and Deployment at Scale — `ch12-production.md`

## Volume 18 — Java, Kotlin, and the JVM (`vol-18-jvm-kotlin/`)

- [ ] 18.01 The JVM Architecture: Classfiles, Bytecode, and the Execution Model — `ch01-jvm-architecture.md`
- [ ] 18.02 Class Loading, Linking, Verification, and Modules (JPMS) — `ch02-class-loading.md`
- [ ] 18.03 The Java Memory Model, Object Layout, and Heap Organization — `ch03-jmm-object-layout.md`
- [ ] 18.04 Garbage Collection: Serial, Parallel, G1, ZGC, Shenandoah, and Generational ZGC — `ch04-garbage-collection.md`
- [ ] 18.05 The JIT: Interpreters, C1, C2, and Graal — Deoptimization, Inlining, and Intrinsics — `ch05-jit-compilation.md`
- [ ] 18.06 Concurrency on the JVM: Threads, Monitors, VarHandles, Loom, and Structured Concurrency — `ch06-concurrency-loom.md`
- [ ] 18.07 Kotlin on the JVM: Interop, Null-Safety, Coroutines, and Compiler Intrinsics — `ch07-kotlin-interop.md`
- [ ] 18.08 The Kotlin Type System, Generics, and Reified Types — `ch08-kotlin-type-system.md`
- [ ] 18.09 Build Tooling, Dependency Management, and the Module/Artifact Ecosystem — `ch09-build-tooling.md`
- [ ] 18.10 Profiling, Observability, and Performance Tuning (JFR, async-profiler, JMC, heap dumps) — `ch10-profiling-observability.md`
- [ ] 18.11 Native Interop: JNI, Panama (FFM), and GraalVM Native Image — `ch11-native-interop.md`
- [ ] 18.12 Production JVM: Container-Aware Tuning, GC Sizing, Class-Data Sharing, and Deployment at Scale — `ch12-production-jvm.md`

## Volume 19 — JavaScript, Node.js, and Frontend Frameworks (`vol-19-javascript-frontend/`)

- [ ] 19.01 JavaScript Engines: V8, SpiderMonkey, JavaScriptCore — Parsing, Hidden Classes, Inline Caches — `ch01-js-engines.md`
- [ ] 19.02 The Event Loop, Microtasks, Macrotasks, and Timers — Browser vs Node — `ch02-event-loop.md`
- [ ] 19.03 Node.js Internals: libuv, the Thread Pool, and Native Addons — `ch03-nodejs-internals.md`
- [ ] 19.04 The JavaScript Type System, Prototypes, Proxies, and the Module System (ESM/CJS) — `ch04-type-system-modules.md`
- [ ] 19.05 Async JavaScript: Promises, async/await, Generators, and the Promise Job Queue — `ch05-async-promises.md`
- [ ] 19.06 Build Tooling and Bundlers: RSPack, Vite, esbuild — Treeshaking, Code Splitting, HMR — `ch06-bundlers-tooling.md`
- [ ] 19.07 React Internals: The Fiber Reconciler, Hooks, Suspense, and Concurrent Features — `ch07-react-internals.md`
- [ ] 19.08 Vue and Svelte Internals: Reactivity, Virtual DOM vs Compiled Output — `ch08-vue-svelte-internals.md`
- [ ] 19.09 Rendering at Scale: SSR, SSG, ISR, Streaming SSR, Hydration, Islands — `ch09-rendering-strategies.md`
- [ ] 19.10 State Management, Data Fetching, and Caching — `ch10-state-data-fetching.md`
- [ ] 19.11 Testing, Linting, and Tooling for Frontend at Scale — `ch11-testing-tooling.md`
- [ ] 19.12 Production Frontend: Observability, Performance, and Deployment — `ch12-production-frontend.md`

## Volume 20 — Rust for Backend Systems (`vol-20-rust-backend/`)

- [ ] 20.01 Rust Architecture: Toolchain, Crates, and the Compilation Model — `ch01-rust-architecture.md`
- [ ] 20.02 Ownership, Borrowing, and the Borrow Checker — The Core Invariants — `ch02-ownership-borrow-checker.md`
- [ ] 20.03 Lifetimes, Variance, and Interior Mutability — `ch03-lifetimes-variance.md`
- [ ] 20.04 Traits, Generics, and Monomorphization — `ch04-traits-generics.md`
- [ ] 20.05 Async Rust: Futures, Pin/Unpin, the Tokio Runtime, and Work-Stealing — `ch05-async-tokio.md`
- [ ] 20.06 Memory Management: Ownership vs Arc/Mutex, Allocators, and Zero-Copy — `ch06-memory-allocators.md`
- [ ] 20.07 Error Handling, Panics, and Unsafe Rust — `ch07-error-unsafe.md`
- [ ] 20.08 Concurrency Primitives: Send/Sync, Atomics, Channels, and Lock-Free — `ch08-concurrency-primitives.md`
- [ ] 20.09 Macros, Procedural Macros, and Code Generation — `ch09-macros-codegen.md`
- [ ] 20.10 FFI, Native Extensions, and Polyglot Interop — `ch10-ffi-interop.md`
- [ ] 20.11 Testing, Linting, and Tooling — `ch11-testing-linting.md`
- [ ] 20.12 Production Rust: Cross-Compilation, Workspaces, Telemetry, and Deployment at Scale — `ch12-production-rust.md`


Batch 39 — 2026-08-21: Vol18 ch01-ch03 + Vol19 ch01-ch02 landed (batch 1/6 of Vols 18-20).
- Vol18 ch01 JVM Architecture (HotSpot interpreter/C1/C2/Graal, classfile CAFEBABE, 202 opcodes, verification, ~7.2k words, 7 mermaid)
- Vol18 ch02 Class Loading/JPMS (delegation, StackMapTable, initialization deadlock, JPMS/jlink, ~6.1k words, 7 mermaid)
- Vol18 ch03 JMM/Object Layout (happens-before, visibility, safe publication, mark word, TLAB, ~9.1k words, 8 mermaid)
- Vol19 ch01 JS Engines (V8 Ignition/Maglev/TurboFan, hidden classes/ICs, SpiderMonkey/JSC, ~6.6k words, 8 mermaid)
- Vol19 ch02 Event Loop (browser vs libuv phases, microtasks, starvation, ~7.1k words, 8 mermaid — trimmed gantt)

Batch 40 — 2026-08-21: Vol18 ch04-ch06 + Vol19 ch04 + Vol20 ch02 landed (batch 2/6 — 5 ch retry pending 2).
- Vol18 ch04 GC (Serial→G1→ZGC/Shenandoah/Gen ZGC, Xlog, 9,428w, 8 mermaid)
- Vol18 ch05 JIT (interpreter/C1/C2/Graal, deopts, compilation logs, 7,199w, 7 mermaid)
- Vol18 ch06 Concurrency/Loom (monitors, VarHandle, carrier vs virtual, AQS, 7,171w, 8 mermaid)
- Vol19 ch04 Types/Prototypes/Modules (coercion, prototype chain, Proxy, CJS vs ESM, 10,833w, 8 mermaid)
- Vol20 ch02 Ownership/Borrow Checker (move, Copy/Clone, NLL/Polonius, 7,743w, 7 mermaid)

Batch 41 — 2026-08-21: Vol19 ch03, ch05-ch06 landed (batch 2b — 3 ch).
- Vol19 ch03 Node.js Internals (libuv 6 phases, threadpool, N-API/napi-rs, worker_threads vs cluster, AsyncLocalStorage, 11,152w, 8 mermaid)
- Vol19 ch05 Async JavaScript (Promise states, job queue, async/await desugaring, generators, 8,648w, 7 mermaid)
- Vol19 ch06 Bundlers (RSPack/Vite/esbuild, treesaking, code splitting, HMR, module federation, 7,634w, 8 mermaid — trimmed from 9)

Batch 42 — 2026-08-21: Vol19 ch06 + Vol20 ch04 landed (batch 2c — 2 ch).
- Vol19 ch06 Bundlers (RSPack/Vite/esbuild, pre-bundle, treesaking, splitChunks, HMR, 7,634w, 8 mermaid — trimmed from 9)
- Vol20 ch04 Traits/Generics/Monomorphization (orphan rule, vtable, const generics, 6,046w, 8 mermaid — trimmed from 9)
