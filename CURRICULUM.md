# The Backend Engineer's Library — Master Curriculum

A comprehensive, in-depth textbook program for a **FAANG-level senior backend software
engineer** working on distributed backend systems. It spans the full stack of knowledge such
an engineer is expected to command — from silicon to distributed consensus to running a
security program — treating each domain with the depth of a graduate course, grounded in real
systems, real incidents, and real tooling.

The program is organized into **volumes**. Each volume is a self-contained book of chapters;
each chapter targets 4,000–7,000 words with diagrams (Mermaid), real code/config, and a
distributed-systems lens (see [`STYLE.md`](STYLE.md)). Volumes can be read independently, but
within a volume chapters build on each other.

> **Scope note.** This started as an 8-book suite on software supply chain security (now
> **Volume 0**) and was expanded to the full backend curriculum. Volume 0's chapters are the
> most mature; other volumes are written in batches. See [`PROGRESS.md`](PROGRESS.md) for live
> status and the resumable batch plan.

## Volumes

| Vol | Title | Focus |
|-----|-------|-------|
| 0 | Software Supply Chain Security (8 books, 75 ch) | Threats, dependencies, SBOMs, build/CI-CD, signing, cloud-native, source, governance |
| 1 | Computer Architecture for Backend Engineers | CPU, memory hierarchy, storage, NUMA, mechanical sympathy |
| 2 | Operating Systems and Linux | Processes, scheduling, VM, syscalls, I/O, cgroups/namespaces, perf/eBPF |
| 3 | Networking for Backend Engineers | TCP/IP, TLS, HTTP/1-2-3, gRPC, DNS, load balancing, service mesh |
| 4 | Concurrency and Parallelism | Threads, locks, memory models, lock-free, async, actors/CSP |
| 5 | Databases and Storage Systems | Storage engines, indexing, transactions, MVCC, replication, sharding, NoSQL/NewSQL |
| 6 | Distributed Systems | Clocks, consistency, consensus (Paxos/Raft), quorums, CRDTs, testing |
| 7 | System Design and Architecture | Scalability, caching, event-driven, multi-region, resilience, design cases |
| 8 | APIs and Service Design | REST, gRPC, GraphQL, versioning, idempotency, contracts |
| 9 | Security, Authentication, and Cryptography | Applied crypto, authN/Z, OAuth/OIDC, RBAC/ABAC/ReBAC, zero trust, appsec |
| 10 | Messaging, Streaming, and Event Systems | Queues vs logs, Kafka, delivery semantics, event sourcing, outbox, backpressure |
| 11 | Reliability, Observability, and SRE | SLOs, metrics/traces/logs, incident response, chaos, deployment strategies |
| 12 | Cloud, Containers, and Infrastructure | Container/K8s internals, IaC, cloud primitives, multi-tenancy, cost |
| 13 | Language Runtimes for Backend | JVM, Go runtime, Rust, GC, JIT, profiling |
| 14 | Data Structures and Algorithms for Backend | Complexity, hashing, probabilistic structures, consistent hashing, external algorithms |
| 15 | Software Engineering Practice | Testing, design docs, DDD, patterns, refactoring, code review |

---

## Volume 0 — Software Supply Chain Security

Eight books, 75 chapters. Full breakdown in [`PROGRESS.md`](PROGRESS.md). Books: Foundations;
Dependency Management; SBOMs; Build & CI/CD; Signing & Attestation; Cloud-Native; Source &
Insider; Governance & IR.

## Volume 1 — Computer Architecture for Backend Engineers

1. Why Architecture Matters to Backend Engineers: Mechanical Sympathy
2. The Modern CPU: Pipelines, Superscalar, Out-of-Order, Speculation
3. The Memory Hierarchy and Caches
4. Cache Coherence and Hardware Memory Consistency
5. Storage Hardware: HDD, SSD, NVMe, and Persistent Memory
6. Multi-Socket Systems and NUMA
7. Data Parallelism: SIMD, Vectorization, and GPUs for Backend
8. Performance Anti-Patterns: False Sharing, Branch Misprediction, Cache Thrashing
9. Number Representation and Floating Point
10. Hardware Support for Virtualization and Isolation

## Volume 2 — Operating Systems and Linux

1. The Process Model: Processes, Threads, and Address Spaces
2. CPU Scheduling: CFS, Real-Time, and cgroup CPU Control
3. Virtual Memory and Paging
4. Memory in Practice: Allocators, Page Cache, Huge Pages, OOM
5. System Calls and the Kernel Boundary
6. File Systems and the VFS
7. Linux I/O Models: Blocking, epoll, and io_uring
8. Signals, Pipes, and IPC
9. Namespaces, cgroups, and Container Internals
10. The Linux Network Stack
11. Performance Analysis: perf, ftrace, and eBPF
12. Boot, init, and systemd

## Volume 3 — Networking for Backend Engineers

1. The Journey of a Packet: The Stack End to End
2. IP, Routing, Subnetting, and NAT
3. TCP in Depth: Handshake, State Machine, Flow and Congestion Control
4. UDP and QUIC
5. DNS in Depth
6. TLS 1.3 and the Web PKI
7. HTTP/1.1, HTTP/2, and HTTP/3
8. gRPC and RPC Framework Internals
9. Load Balancing: L4, L7, and Algorithms
10. Proxies, Reverse Proxies, Service Mesh, and CDNs
11. Network Reliability: Timeouts, Retries, Backoff, and Hedging
12. Debugging and Observing Networks

## Volume 4 — Concurrency and Parallelism

1. Models of Concurrency: A Map of the Territory
2. Threads, Mutual Exclusion, and Locks
3. Memory Models and Happens-Before
4. Atomics, CAS, and Lock-Free Data Structures
5. Deadlock, Livelock, and Starvation
6. Asynchronous I/O and Event Loops
7. The Actor Model, CSP, and Channels
8. Coroutines and Structured Concurrency
9. Concurrency Patterns for Backend Services
10. Testing and Debugging Concurrent Systems

## Volume 5 — Databases and Storage Systems

1. The Relational Model and SQL Semantics
2. Storage Engines: B-Trees vs LSM-Trees
3. Indexing in Depth
4. Query Processing and Optimization
5. Transactions and ACID
6. Isolation Levels and MVCC
7. Write-Ahead Logging and Crash Recovery
8. Replication: Physical, Logical, Sync, and Async
9. Partitioning and Sharding
10. Distributed Transactions: 2PC, Sagas, and Alternatives
11. NoSQL: Key-Value, Document, Wide-Column, and Graph
12. NewSQL and Distributed SQL
13. Specialized Stores: Search, Time-Series, and Analytics
14. Operating Databases: Pooling, Migrations, and Scaling

## Volume 6 — Distributed Systems

1. Foundations: System Models, Failures, and Assumptions
2. Time, Clocks, and the Ordering of Events
3. Replication and Consistency Models
4. CAP, PACELC, and the Real Trade-Offs
5. Consensus I: Paxos
6. Consensus II: Raft
7. Quorum Systems and Dynamo-Style Replication
8. Coordination Services: ZooKeeper and etcd
9. Idempotency, Deduplication, and Exactly-Once
10. Failure Detection and Membership: Gossip and SWIM
11. CRDTs and Eventual Consistency
12. Testing Distributed Systems: Jepsen, Chaos, and Simulation

## Volume 7 — System Design and Architecture

1. Principles of Scalable System Design
2. Back-of-the-Envelope Estimation and Capacity Planning
3. Caching Strategies at Scale
4. Load Balancing and Traffic Management
5. Data Modeling for Scale
6. Monolith, Microservices, and the Space Between
7. Event-Driven Architecture
8. API Gateways, BFF, and Edge
9. Rate Limiting, Quotas, and Fairness
10. Multi-Region and Geo-Distributed Systems
11. Designing for Failure: Bulkheads, Circuit Breakers, Load Shedding
12. Design Case Studies: Feed, Chat, Notifications, and a Global KV Store

## Volume 8 — APIs and Service Design

1. API Design Principles and Contracts
2. REST in Depth
3. gRPC and Protobuf Schema Design
4. GraphQL for Backend Engineers
5. Versioning and Evolution
6. Idempotency, Pagination, and Filtering
7. Error Handling and Status Semantics
8. Compatibility: Backward, Forward, and Wire Formats

## Volume 9 — Security, Authentication, and Cryptography

1. Applied Cryptography for Engineers
2. Hashing, MACs, KDFs, and Password Storage
3. Symmetric and Asymmetric Encryption in Practice
4. Certificates, PKI, and TLS Operations
5. Authentication: Sessions, Tokens, and JWTs
6. OAuth 2.0 and OpenID Connect
7. Authorization Models: RBAC, ABAC, and ReBAC (Zanzibar)
8. Secrets Management
9. Application Security: OWASP, Injection, SSRF, and Deserialization
10. Zero Trust and Service-to-Service Auth: mTLS and SPIFFE/SPIRE
11. Threat Modeling and Secure Design

## Volume 10 — Messaging, Streaming, and Event Systems

1. Messaging Fundamentals: Queues, Logs, and Pub/Sub
2. Delivery Semantics: At-Most/At-Least/Exactly-Once
3. Apache Kafka Architecture
4. Stream Processing
5. Event Sourcing and CQRS
6. The Outbox Pattern and the Dual-Write Problem
7. Backpressure and Flow Control
8. Dead Letters, Retries, and Poison Messages

## Volume 11 — Reliability, Observability, and SRE

1. SLIs, SLOs, and Error Budgets
2. Metrics and the Golden Signals
3. Logging at Scale
4. Distributed Tracing and OpenTelemetry
5. Incident Response and On-Call
6. Blameless Postmortems
7. Load Testing and Capacity Planning
8. Chaos Engineering
9. Deployment Strategies: Blue/Green, Canary, and Feature Flags
10. Resilience Patterns in Production

## Volume 12 — Cloud, Containers, and Infrastructure

1. Containers Deep Dive: Images, Runtimes, and Isolation
2. Kubernetes Architecture: Control Plane and Data Plane
3. Kubernetes Workloads, Networking, and Storage
4. Infrastructure as Code
5. Cloud Primitives: Compute, Storage, and Network
6. Managed Data and Platform Services
7. Multi-Tenancy and Isolation
8. Cloud Cost and Capacity Engineering

## Volume 13 — Language Runtimes for Backend

1. The JVM: Memory, Garbage Collection, and the JIT
2. The Go Runtime: Scheduler, Memory Model, and GC
3. Rust for Backend Systems
4. Garbage Collection Across Runtimes
5. Profiling and Performance Tuning

## Volume 14 — Data Structures and Algorithms for Backend

1. Complexity That Matters in Practice
2. Hashing and Hash Tables at Scale
3. Balanced Trees and Ordered Structures
4. Probabilistic Structures: Bloom, HyperLogLog, Count-Min Sketch
5. Consistent Hashing and Rendezvous Hashing
6. Sorting, External Sorting, and Streaming
7. Graphs in Systems
8. Rate-Limiting and Scheduling Algorithms

## Volume 15 — Software Engineering Practice

1. Testing Strategy: Unit, Integration, E2E, and Property-Based
2. Design Docs, RFCs, and Technical Decision-Making
3. Domain-Driven Design for Backend
4. Design Patterns and Anti-Patterns for Services
5. Refactoring and Managing Technical Debt
6. Code Review and Engineering Culture
