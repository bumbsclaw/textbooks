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

> **Scope note.** This started as an 8-book suite on software supply chain security (now the
> **Companion Series**, 75 chapters, 8 books under `book-01`…`book-08`). That work is retained
> as a companion — see *Companion Series* below. The main library is Volumes 1–15 plus an 8-ch
> Supply-Chain Essentials distillate. Security as a backend topic lives in Volume 9 (11 ch);
> the companion is for readers who want depth on supply-chain security. See
> [`PROGRESS.md`](PROGRESS.md) for live status and the resumable batch plan.

## Reading Paths and Suggested Order

Volume numbers are stable (to avoid breaking links and git history). Suggested reading order
differs from numeric order to respect dependencies:

- **Foundations track:** Vol 1 → 2 → 3 → 4 → 5 → 6 → 9 → 7 → 8 → 10 → 12 → 11 → 13 → 14 → 15
- **Distributed Systems track:** Vol 4 → 6 → 10 → 7 → 11
- **Platform track:** Vol 2 → 9 → 12 → 11
- **Security track:** Vol 9 → Companion Series (Books 1–8) for depth

Security (Vol 9) is a prerequisite for System Design (Vol 7) and APIs (Vol 8); Cloud (Vol 12)
is a prerequisite for SRE (Vol 11). Chapters note these explicitly.

## Part Structure

- **Part I — Execution:** Vol 1 (Architecture), Vol 2 (OS/Linux), Vol 3 (Networking), Vol 4 (Concurrency)
- **Part II — State:** Vol 5 (Databases), Vol 6 (Distributed Systems)
- **Part III — Security:** Vol 9 (Security/Auth/Crypto) + Companion Series (supply-chain depth)
- **Part IV — Systems:** Vol 7 (System Design), Vol 8 (APIs), Vol 10 (Messaging), Vol 12 (Cloud/Infra), Vol 11 (Reliability/SRE)
- **Part V — Fundamentals:** Vol 13 (Runtimes), Vol 14 (Algorithms), Vol 15 (SWE Practice)
- **Part VI — Language Internals:** Vol 16 (Python/CPython), Vol 17 (Go), Vol 18 (Java/Kotlin/JVM), Vol 19 (JavaScript/Node/Frontend), Vol 20 (Rust)

## Volumes — At a Glance

| Vol | Title | Chapters | Focus |
|-----|-------|----------|-------|
| — | **Companion: Supply Chain Security** (8 books, 75 ch) | 75 | Threats, dependencies, SBOMs, build/CI-CD, signing, cloud-native, source, governance — see below |
| — | Supply-Chain Security Essentials (distillate) | 8 | Threat model, SLSA/S2C2F, SBOMs, signing, CI/CD hardening, K8s policy, IR (for the generalist) |
| 1 | Computer Architecture for Backend Engineers | 10 | CPU, memory hierarchy, storage, NUMA, mechanical sympathy |
| 2 | Operating Systems and Linux | 12 | Processes, scheduling, VM, syscalls, I/O, cgroups/namespaces, perf/eBPF |
| 3 | Networking for Backend Engineers | 12 | TCP/IP, TLS, HTTP/1-2-3, gRPC, DNS, load balancing, service mesh |
| 4 | Concurrency and Parallelism | 10 | Threads, locks, memory models, lock-free, async, actors/CSP |
| 5 | Databases and Storage Systems | 14 | Storage engines, indexing, transactions, MVCC, replication, sharding, NoSQL/NewSQL |
| 6 | Distributed Systems | 12 | Clocks, consistency, consensus (Paxos/Raft), quorums, CRDTs, testing |
| 7 | System Design and Architecture | 12 | Scalability, caching, event-driven, multi-region, resilience, design cases |
| 8 | APIs and Service Design | 11 | REST, gRPC, GraphQL, versioning, idempotency, contracts, governance, contract testing |
| 9 | Security, Authentication, and Cryptography | 11 | Applied crypto, authN/Z, OAuth/OIDC, RBAC/ABAC/ReBAC, zero trust, appsec |
| 10 | Messaging, Streaming, and Event Systems | 8 | Queues vs logs, Kafka, delivery semantics, event sourcing, outbox, backpressure |
| 11 | Reliability, Observability, and SRE | 10 | SLOs, metrics/traces/logs, incident response, chaos, deployment strategies |
| 12 | Cloud, Containers, and Infrastructure | 11 | Container/K8s internals, IaC, cloud primitives, multi-tenancy, cost, platform eng |
| 13 | Language Runtimes for Backend | 9 | JVM, Go, Rust, Python/Node/Wasm, GC, JIT, profiling, runtime selection |
| 14 | Data Structures and Algorithms for Backend | 8 | Complexity, hashing, probabilistic structures, consistent hashing, external algorithms |
| 15 | Software Engineering Practice | 10 | Testing (3 ch), design docs, DDD, patterns, refactoring, code review, teams |
| 16 | Python and CPython Internals | 12 | Source→bytecode, ceval, objects, GIL/free-threading, types, GC/pymalloc, import, C API, JIT |
| 17 | Golang and Go Internals | 12 | Toolchain, types/generics, ABI/defer, scheduler/GC, memory model, interfaces, channels, SSA, tooling, cgo |
| 18 | Java, Kotlin, and the JVM | 12 | Bytecode/classfile, classloading, memory/GC, JIT tiered, concurrency/loom, Kotlin interop, build tooling |
| 19 | JavaScript, Node.js, and Frontend Frameworks | 12 | Engines (V8/JSC), event loop, async, bundles, React/Vue reactivity & rendering, SSR/hydration, prod deploy |
| 20 | Rust for Backend Systems | 12 | Ownership/borrow checker, lifetimes, async/tokio, traits/generics, memory/allocators, FFI & prod |


**Main library total:** ~202 chapters (Vols 1–20 + 8-ch Essentials). Companion adds 75 ch for reference. Vols 16–20 are post-Vol-13 deep dives.

---

## Companion Series — Supply Chain Security (75 ch, retained as reference)

Eight books, 75 chapters (dirs `book-01`…`book-08`). Full breakdown in [`PROGRESS.md`](PROGRESS.md).
Books: Foundations; Dependency Management; SBOMs; Build & CI/CD; Signing & Attestation;
Cloud-Native; Source & Insider; Governance & IR. Cross-referenced from Vol 9, Vol 11, Vol 12
as "for deeper study, see Companion Book X." Not part of the main-library page count.

**Relationship to Vol 9:** Vol 9 is the 11-ch generalist treatment every backend engineer reads.
The Companion is the specialist reference. Vol 9 ch 11 and Vol 12 ch 4 cross-ref the Companion.

---

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

> **Boundary note:** Vol 2 ch 9 covers kernel mechanisms (namespaces/cgroups) as the substrate.
> Vol 12 ch 1 covers their *platform usage* (images, runtimes, isolation at fleet scale).

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

> **Boundary notes:**
> - TLS/PKI mechanics → Vol 3 ch 6 (wire); TLS operations/PKI lifecycle → Vol 9 ch 4.
> - gRPC internals (HTTP/2 framing, flow control) → Vol 3 ch 8; gRPC schema/design → Vol 8 ch 3.
> - L4/L7 algorithms (wire) → Vol 3 ch 9; traffic policy at system scale → Vol 7 ch 4.
> - Timeouts/retries/hedging primitives → Vol 3 ch 11; resilience patterns (bulkheads, breakers) → Vol 11 ch 10 and Vol 7 ch 11.

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

> **Boundary note:** Concurrency-specific testing (determinism, races, linearizability) → Vol 4 ch 10;
> general testing strategy → Vol 15 ch 1–2.

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

> **Boundary note:** Vol 6 ch 9 covers theory (idempotency, exactly-once reasoning); Vol 10 ch 2/6
> covers broker mechanics (Kafka semantics, outbox).

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

> **Boundary notes:** Rate limiting algorithms (token bucket, leaky bucket) at system scale → Vol 7 ch 9;
> algorithmic analysis of rate-limiting/scheduling → Vol 14 ch 8. Capacity math (Little's Law,
> queueing) is introduced here and analyzed in Vol 14.

## Volume 8 — APIs and Service Design

1. API Design Principles and Contracts
2. REST in Depth
3. gRPC and Protobuf Schema Design
4. GraphQL for Backend Engineers
5. Versioning and Evolution
6. Idempotency, Pagination, and Filtering
7. Error Handling and Status Semantics
8. Compatibility: Backward, Forward, and Wire Formats
9. API Governance, Linting, and Breaking-Change Detection
10. Schema Registry, Code Generation, and SDK Delivery
11. Contract Testing and API Evolution in Practice

> **Boundary note:** Vol 3 ch 8 = gRPC wire mechanics; Vol 8 ch 3 = gRPC service/schema design.

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

> **Dependency note:** Read Vol 9 before Vol 7–8. System design and API chapters assume authN/Z,
> TLS, and secrets knowledge. For supply-chain depth, see Companion Books 1–8.

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

> **Boundary note:** Vol 6 ch 12 covers Jepsen/chaos as *verification of distributed correctness*;
> Vol 11 ch 8 covers chaos as *operational practice* (game days, fault injection in prod).
> Vol 0 / Companion IR is supply-chain-specific; this volume is general SRE.

## Volume 12 — Cloud, Containers, and Infrastructure

1. Containers Deep Dive: Images, Runtimes, and Isolation
2. Kubernetes Architecture: Control Plane and Data Plane
3. Kubernetes Workloads, Networking, and Storage
4. Infrastructure as Code
5. Cloud Primitives: Compute, Storage, and Network
6. Managed Data and Platform Services
7. Multi-Tenancy and Isolation
8. Cloud Cost Engineering and FinOps
9. Capacity Planning and Performance at Cloud Scale
10. Cloud Networking, IAM, and Security Foundations
11. Platform Engineering: Paved Roads and Internal Developer Platforms

> **Boundary note:** Vol 2 ch 9 = kernel mechanism; Vol 12 ch 1 = platform usage at scale.

## Volume 13 — Language Runtimes for Backend

1. The JVM: Memory, Garbage Collection, and the JIT
2. The Go Runtime: Scheduler, Memory Model, and GC
3. Rust for Backend Systems
4. Garbage Collection Across Runtimes
5. Profiling and Performance Tuning
6. Python and Node.js Runtimes for Backend
7. WebAssembly and Emerging Runtimes
8. FFI, Native Extensions, and Polyglot Interop
9. Runtime Selection and Performance Trade-offs

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
2. Contract Testing, Test Doubles, and Testability Design
3. Load, Performance, and Chaos Testing for Backend
4. Design Docs, RFCs, and Technical Decision-Making
5. Domain-Driven Design for Backend
6. Design Patterns and Anti-Patterns for Services
7. Refactoring and Managing Technical Debt
8. Code Review and Engineering Culture
9. Debugging and Incident-Driven Learning
10. Building High-Performing Engineering Teams and Processes

## Volume 16 — Python and CPython Internals

1. CPython Architecture: Source to Execution
2. Objects, Reference Counting, and the PyObject System
3. Bytecode, the ceval Loop, and Adaptive Specialization (PEP 659)
4. Memory Management: pymalloc, GC, Arenas, and Immortal Objects
5. The GIL: Mechanics, Evolution, Per-Interpreter GIL and Free-Threaded Python (PEP 684 / PEP 703)
6. The Type System: Classes, MRO, Descriptors, Slots, and the Attribute Protocol
7. Functions, Closures, Generators, Coroutines, and async/await
8. Exceptions, Context Managers, and the Unwinding Machinery
9. The Import System: importlib, Finders, Loaders, and Namespace Packages
10. C Extensions, the C API, HPy, and Embedding CPython
11. Performance: Profiling, the Copy-and-Patch JIT (PEP 744), Cython, and Alternative Runtimes
12. Packaging, Distribution, and Production Deployment at Scale

> **Dependency note:** Vol 13 ch06 is the prerequisite service-level view of Python/Node. Vol 16 is the internals deep dive. Vol 1 ch08–09 (data layout, floats) and Vol 2 ch04 (allocators) are useful background.

## Volume 17 — Golang and Go Internals

1. The Go Toolchain: Modules, Build, Linker, and the Static Binary Model
2. Types, Memory Layout, and Generics Internals
3. Functions, Methods, Defer, Panic/Recover, and the ABI
4. Goroutines, the Scheduler (G-M-P), and the Netpoller
5. Memory Allocator, Stacks, and the Concurrent Tri-Color GC
6. The Go Memory Model, Atomics, and Synchronization Primitives
7. Interfaces, Reflection, and `unsafe`
8. Channels, Select, Timers, and Context Internals
9. Compiler Pipeline: SSA, Escape Analysis, and Optimizations
10. Tooling Deep Dive: Race Detector, pprof, execution trace, and vet
11. cgo, Assembly, and Foreign-Function Interoperability
12. Production Go: Cross-Compilation, Workspaces, Telemetry, and Deployment at Scale

> **Dependency note:** Vol 13 ch02 is the prerequisite service-level view of the Go runtime. Vol 17 is the internals deep dive (toolchain → SSA → runtime → tooling). Vol 4 (Concurrency) and Vol 1 ch02 (CPU pipelining) are useful background for the scheduler and compiler chapters.

## Volume 18 — Java, Kotlin, and the JVM

1. The JVM Architecture: Classfiles, Bytecode, and the Execution Model
2. Class Loading, Linking, Verification, and Modules (JPMS)
3. The Java Memory Model, Object Layout, and Heap Organization
4. Garbage Collection: Serial, Parallel, G1, ZGC, Shenandoah, and Generational ZGC
5. The JIT: Interpreters, C1, C2, and Graal — Deoptimization, Inlining, and Intrinsics
6. Concurrency on the JVM: Threads, Monitors, VarHandles, Loom, and Structured Concurrency
7. Kotlin on the JVM: Interop, Null-Safety, Coroutines, and Compiler Intrinsics
8. The Kotlin Type System, Generics, and Reified Types
9. Build Tooling, Dependency Management, and the Module/Artifact Ecosystem (Maven, Gradle, sbt)
10. Profiling, Observability, and Performance Tuning (JFR, async-profiler, JMC, heap dumps)
11. Native Interop: JNI, Panama (FFM), and GraalVM Native Image
12. Production JVM: Container-Aware Tuning, GC Sizing, Class-Data Sharing, and Deployment at Scale

> **Dependency note:** Vol 13 ch01 is the prerequisite service-level view of the JVM. Vol 18 is the internals deep dive. Vol 1 (Architecture), Vol 2 (OS/Linux), and Vol 4 (Concurrency) are useful background for memory layout, GC, and the JMM.

## Volume 19 — JavaScript, Node.js, and Frontend Frameworks

1. JavaScript Engines: V8, SpiderMonkey, and JavaScriptCore — Parsing, Hidden Classes, and Inline Caches
2. The Event Loop, Microtasks, Macrotasks, and Timers — Browser vs Node
3. Node.js Internals: libuv, the Thread Pool, and Native Addons (N-API, napi-rs)
4. The JavaScript Type System, Prototypes, Proxies, and the Module System (ESM/CJS)
5. Async JavaScript: Promises, async/await, Generators, and the Promise Job Queue
6. Build Tooling and Bundlers: RSPack, Vite, esbuild — Treeshaking, Code Splitting, and HMR
7. React Internals: The Fiber Reconciler, Hooks, Suspense, and Concurrent Features
8. Vue and Svelte Internals: Reactivity (Proxy vs Signals vs Compile-Time), Virtual DOM vs Compiled Output
9. Rendering at Scale: SSR, SSG, ISR, Streaming SSR, Hydration, Islands, and Partial Hydration
10. State Management, Data Fetching, and Caching (TanStack Query, SWR, Zustand/Jotai, cache invalidation)
11. Testing, Linting, and Tooling for Frontend at Scale (Vitest, Playwright, ESLint, TypeScript)
12. Production Frontend: Observability, Performance (Core Web Vitals, Lighthouse), and Deployment (CDN, Edge, RSC)

> **Dependency note:** Vol 13 ch06 (Python/Node) and Vol 3 ch04 (HTTP) set context; Vol 19 is the full-stack deep dive. Vol 8 (APIs) and Vol 11 (SRE) complement the prod chapters.

## Volume 20 — Rust for Backend Systems

1. Rust Architecture: Toolchain, Crates, and the Compilation Model (rustc, Cargo, rustup)
2. Ownership, Borrowing, and the Borrow Checker — The Core Invariants
3. Lifetimes, Variance, and Interior Mutability (Cell, RefCell, OnceLock)
4. Traits, Generics, and Monomorphization — Dynamic vs Static Dispatch
5. Async Rust: Futures, Pin/Unpin, the Tokio Runtime, and Work-Stealing
6. Memory Management: Ownership vs Arc/Mutex, Allocators (jemalloc, mimalloc, tcmalloc), and Zero-Copy
7. Error Handling, Panics, and Unsafe Rust — Soundness, Miri, and Fuzzing
8. Concurrency Primitives: Send/Sync, Atomics, Channels, and Lock-Free Structures
9. Macros, Procedural Macros, and Code Generation — Build Scripts and build.rs
10. FFI, Native Extensions, and Polyglot Interop (C, Python, Node, WASM)
11. Testing, Linting, and Tooling (clippy, rustfmt, cargo-audit, criterion, cargo-nextest, Miri)
12. Production Rust: Cross-Compilation, Workspaces, Telemetry, and Deployment at Scale

> **Dependency note:** Vol 13 ch03 is the prerequisite service-level survey of Rust. Vol 20 is the internals deep dive. Vol 1 (Architecture) and Vol 4 (Concurrency) help with ownership/memory and async.

