# Curriculum Audit — The Backend Engineer's Library

**Date:** 2026-08-20
**Auditor:** Adversarial curriculum review (subagent)
**Scope:** `CURRICULUM.md` (237 lines, 16 volumes), `PROGRESS.md` (335 lines), `STYLE.md` (64 lines), `ls` of all 24 volume dirs, 10 README samples.
**Branch:** `claude/backend-security-textbooks-i0nyjm`

---

## 1. Verdict

**REQUEST_CHANGES** — Do not mint new chapters against `CURRICULUM.md` as-is. Structural defects (proportion, duplication, corrupted scaffolding) must be fixed first. Volume 0's weight alone forces this verdict.

---

## 2. Required Changes (severity-tagged)

### [BLOCKER]

- **[BLOCKER-01] Corrupted READMEs — 4 volumes.** `vol-05`, `vol-06`, `vol-07`, `vol-08` READMEs contain interleaved duplicate entries injected from unrelated Vol 0 books. Evidence sampled:
  - `vol-05-databases/README.md` lists 10 extra entries (ch01 crypto foundations → ch10 deployment gates) from `book-05-signing-attestation`. Actual Vol 5 should be 14 chapters; README shows 24 lines with alternating numbering `1.,1.,2.,2.,3.,3.…`
  - `vol-06-distributed-systems/README.md` lists 10 extra entries from `book-06-cloud-native` (OCI, registries, base images… reference architecture) interleaved with the real 12 distributed-systems chapters.
  - `vol-07-system-design/README.md` lists 8 extra entries from `book-07-source-security` (SCM threat model → repo integrity) interleaved with the 12 system-design chapters. Numbers restart mid-file.
  - `vol-08-apis/README.md` lists 8 extra entries from `book-08-governance-ir` (regulatory landscape → metrics reporting) interleaved.
  - **Impact:** Any reader or agent that trusts the README as source of truth will write/fetch the wrong file, mis-count chapters, and produce broken cross-refs. This is not cosmetic — the scaffolding generator is proven buggy.
  - **Fix:** Regenerate all `vol-07` through `vol-15` READMEs from `CURRICULUM.md` as single source of truth. Add a CI check: `README ch count == CURRICULUM ch count == PROGRESS ch count` per volume.

- **[BLOCKER-02] Vol 0 (75 ch, 8 books) is 34% of the entire curriculum — structurally incompatible with stated audience and intent.**
  - Total planned chapters = 221 (75 + 146 across Vols 1–15). Vol 0 alone = 33.9%. Next-largest volume is Vol 5 at 14 ch (6.3%). Vol 0 is **5.4×** larger than the average non-zero volume (9.7 ch).
  - At `STYLE.md` depth (4,000–7,000 words/ch + 2–4 Mermaid diagrams), Vol 0 represents ~300k–525k words and 150–300 diagrams — a standalone 900-page book. The user framing is explicit: "security should be A TOPIC within larger backend suite, not dominating" and "general knowledge building, comprehensive and accurate." Current weighting directly contradicts intent.
  - **Fix required before writing Vols 7–15:** Adopt one of the restructure options in §6 (recommended: Option C — spin Vol 0 out as a companion series, collapse to a 12–15 ch "Supply-Chain Security Essentials" volume inside the main sequence). See §6.

- **[BLOCKER-03] Directory naming schizophrenia — `book-01…08` vs `vol-00…15`.**
  - `PROGRESS.md:117` acknowledges "may be regrouped under `vol-00-supply-chain-security/` later; until then their paths are as listed." That "later" is now: 145 chapters are committed under the old scheme. Any tooling, cross-ref, or PDF-render pipeline that assumes uniform `vol-NN-slug/chNN-slug.md` breaks on Vol 0.
  - **Fix:** Decide and execute: either (a) keep `book-*` as legacy but add a symlink/shim `vol-00-supply-chain-security/` with index, or (b) move them (git mv) and rewrite PROGRESS paths in one atomic commit. Do not leave it ambiguous for another 76 chapters.

- **[BLOCKER-04] `vol-09/README.md:7` typo/broken formatting: `*** ABAC` instead of `RBAC`.**
  - The line reads `7. [Authorization: *** ABAC, ReBAC (Zanzibar)]`. CURRICULUM has the correct `RBAC, ABAC, and ReBAC`. A broken title suggests the README was hand-edited or template-globbed incorrectly and undermines trust in spec accuracy (STYLE.md demands version-pinned precision). Fix and audit all READMEs for similar corruption.

### [MAJOR]

- **[MAJOR-01] Systemic topic duplication across volumes — no deduplication plan.** At least 7 overlaps where the same topic is promised in two volumes with no stated boundary:
  1. **TLS/PKI:** Vol 3 ch06 (`TLS 1.3 and the Web PKI`) vs Vol 9 ch04 (`Certificates, PKI, and TLS Operations`) — verbatim overlap.
  2. **gRPC/RPC:** Vol 3 ch08 (`gRPC and RPC Framework Internals`) vs Vol 8 ch03 (`gRPC and Protobuf Schema Design`) vs Vol 8 ch08 frame formats.
  3. **Load balancing:** Vol 3 ch09 (`Load Balancing: L4, L7, and Algorithms`) vs Vol 7 ch04 (`Load Balancing and Traffic Management`).
  4. **Secrets management:** Vol 0 Book 4 ch06 (`Secrets Management in CI/CD`) vs Vol 9 ch08 (`Secrets Management`) vs Vol 12 implications.
  5. **Containers/K8s:** Vol 2 ch09 (`Namespaces, cgroups, and Container Internals`) vs Vol 12 ch01–ch03 (Containers deep dive + K8s arch + workloads) — two full treatments of the same substrate with no layering statement.
  6. **Rate limiting:** Vol 7 ch09 (`Rate Limiting, Quotas, and Fairness`) vs Vol 14 ch08 (`Rate-Limiting and Scheduling Algorithms`) — one is systems, one is algorithms, but titles alone will confuse authors.
  7. **Network reliability vs Resilience:** Vol 3 ch11 (`Timeouts, Retries, Backoff, Hedging`) vs Vol 11 ch10 (`Resilience Patterns`) vs Vol 7 ch11 (`Designing for Failure: Bulkheads, Circuit Breakers`).
  - **Fix:** Add a one-line "boundary note" per duplicated chapter in CURRICULUM.md (e.g., "Vol 3 covers wire mechanics; Vol 9 covers operational PKI; Vol 7 covers system-level trade-offs"). Without this, subagents will write the same chapter twice.

- **[MAJOR-02] Vols 1–6 are overweight on internals; Vols 7–15 are dangerously thin for a "senior backend" claim.**
  - Completed work: ~145 ch done = Vol 0 (75) + Vol 1 (10) + Vol 2 (12) + Vol 3 (12) + Vol 4 (10) + Vol 5 (14) + Vol 6 (12). That is all foundations. Vols 7–15 (76 ch planned, 34% of curriculum) are **100% scaffold** (1 README each, zero chapters). Yet these are the volumes a senior backend engineer actually gets interviewed on: system design, APIs, security, messaging, SRE, cloud, runtimes, SWE practice.
  - Within Vols 7–15, sizing is unbalanced: Vol 13 (Runtimes) 5 ch, Vol 15 (SWE Practice) 6 ch, Vol 8 (APIs) 8 ch, Vol 12 (Cloud) 8 ch, Vol 14 (Algorithms) 8 ch, Vol 10 (Messaging) 8 ch — vs Vol 11 (SRE) 10 ch and Vol 9 (Security) 11 ch. The thinnest volumes are exactly the ones that justify Senior+ level.
  - **Fix:** Rebalance per §8 / §7 before resuming writing. Minimum uplifts proposed: Vol 13 → 8–9 ch, Vol 15 → 9–10 ch, Vol 8 → 10–11 ch, Vol 12 → 10–11 ch.

- **[MAJOR-03] CURRICULUM.md lacks chapter boundary descriptions — only titles.**
  - PROGRESS.md carries full chapter-to-filename mapping; CURRICULUM.md for Vols 1–15 lists only titles (1 line each). No scope, no learning goals, no "this chapter covers / does not cover." For subagents writing 4k–7k words, a title is insufficient to prevent drift/duplication. Contrast with Vol 0 books which at least have per-book framing.
  - **Fix:** Add 1–2 sentence scope line per chapter in CURRICULUM.md (or a linked `vol-NN/README.md` that is canonical). This is cheap and prevents 76 chapters of divergent content.

- **[MAJOR-04] Ordering buries Security (Vol 9) after APIs/System Design. Violates dependency graph.**
  - Vol 9 (crypto, authN/Z, mTLS, zero trust) is placed after Vol 7 (System Design) and Vol 8 (APIs), but system-design chapters (multi-region, event-driven, gateways) and API chapters (versioning, idempotency, compatibility) assume security knowledge (auth, TLS, secrets). Similarly, Vol 10 (Kafka, exactly-once) depends on Vol 6 (consensus, idempotency) — that ordering is correct — but Vol 11 (SRE) depends on Vol 10 (streaming failures) and is placed after it, which is okay. The main inversion is Security too late.
  - **Fix:** Move Vol 9 earlier (between Vol 6 and Vol 7) or explicitly mark Vol 9 as a prerequisite for Vols 7–8 in the curriculum preamble.

- **[MAJOR-05] No single source of truth for chapter filenames.**
  - CURRICULUM.md for Vols 7–15 lists human titles only; README.md lists `chNN-slug.md`; PROGRESS.md lists both with tick boxes. Three sources, already diverged (see BLOCKER-01). No validation.
  - **Fix:** Declare PROGRESS.md as the filename authority for in-flight volumes, CURRICULUM.md as title authority, and add a script (`scripts/validate-curriculum.sh`) that fails CI on mismatch.

### [MINOR]

- **[MINOR-01] Inconsistent naming: "Vol 0 — Software Supply Chain Security (8 books, 75 ch)" in CURRICULUM.md table but "Volume 0 books, below" and `book-01…` dirs elsewhere. Pick one term (Volume 0 = 8 Books) and use it everywhere.**
- **[MINOR-02] CURRICULUM.md Vol 8 ch06 title mismatch: table says "Idempotency, Pagination, and Filtering" but some READMEs say "Idempotency, Pagination, Filtering" — trivial but shows no linter.**
- **[MINOR-03] CURRICULUM.md Vol 12 ch08 "Cloud Cost and Capacity Engineering" duplicates Vol 11 ch07 "Load Testing and Capacity Planning" and Vol 7 ch02 "Capacity Planning" — three capacity-planning homes; consolidate.**
- **[MINOR-04] STYLE.md says 2–4 Mermaid diagrams per chapter but does not specify alt-text/accessibility or a style for dark/light rendering — minor but matters for PDF pipeline.**
- **[MINOR-05] PROGRESS.md log notation is timestamp-only (`2026-07-31`) with no word-count or reviewer sign-off; audit trail is weak for 145 chapters. Suggest adding `words: ~5.2k | diagrams: 3 | reviewed: y/n` per batch.**

---

## 3. Volume-by-Volume Table

| Vol | Title (CURRICULUM.md) | Planned ch | Done (PROGRESS) | Balance Assessment | Gaps / Duplicates / Notes |
|-----|------------------------|------------|-----------------|--------------------|---------------------------|
| **0** | **Software Supply Chain Security (8 books)** | **75** | **75 / 75 (100%)** | **Severely overweight.** 33.9% of all chapters. 8 books inside one "volume" breaks the volume abstraction. At graduate depth this is a standalone specialization, not a backend-library chapter set. | Overlaps with Vol 9 (secrets, signing, PKI, policy-as-code), Vol 12 (IaC, containers, cloud provider chain), Vol 11 (IR, detection). SBOMs (Book 3, 9 ch) alone is larger than entire Vols 8,10,12,13,14,15. See §6. |
| **1** | Computer Architecture for Backend Engineers | 10 | 10 / 10 (100%) | Appropriate. Lean and focused. | Ch07 (SIMD/GPU) is niche for backend; could justify 1 ch but ensure it ties to real backend wins (vectorized parsing, ANN). Ch09 (Number Representation) feels undergrad-adjacent; keep only if framed as serialization/float correctness in distributed protocols. |
| **2** | Operating Systems and Linux | 12 | 12 / 12 (100%) | Appropriate, arguably the strongest volume sizing. | Ch09 (Namespaces/cgroups) duplicates Vol 12 ch01 at different depth — needs explicit layering (Vol 2 = kernel mechanism, Vol 12 = platform usage). Ch12 (Boot/systemd) is the least senior-relevant; consider merging with Ch09 or making it an appendix. |
| **3** | Networking for Backend Engineers | 12 | 12 / 12 (100%) | Appropriate. | Duplicates flagged: ch06 TLS ↔ Vol 9 ch04, ch08 gRPC ↔ Vol 8 ch03, ch09 LB ↔ Vol 7 ch04, ch11 reliability ↔ Vol 11 ch10. Needs boundary notes. Otherwise well-scoped. |
| **4** | Concurrency and Parallelism | 10 | 10 / 10 (100%) | Appropriate. | Ch10 (Testing concurrent systems) is essential but will overlap with Vol 15 testing — define boundary (concurrency-specific determinism vs general strategy). |
| **5** | Databases and Storage Systems | 14 | 14 / 14 (100%) | Slightly heavy but justified — databases warrant extra depth. Largest non-zero volume, but defensible. | Ch01 (Relational model) risks recapping undergrad SQL; must earn its place via distributed lens. Ch13 (Specialized stores) is 3 topics in 1 ch — stretch or split. README corrupted (BLOCKER-01). |
| **6** | Distributed Systems | 12 | 12 / 12 (100%) | Appropriate — the intellectual core. | Ch12 (Jepsen/Chaos) overlaps Vol 11 ch08 (Chaos Engineering) — intentionally, but scope differently. README corrupted. |
| **7** | System Design and Architecture | 12 | 0 / 12 (scaffold) | **Thin for its importance.** The volume senior engineers are actually evaluated on. 12 ch is the minimum viable; content risk is hand-waving. | Ch04 LB duplicates Vol 3 ch09. Ch09 Rate Limiting duplicates Vol 14 ch08. Ch05 Data Modeling duplicates Vol 5 concepts. Needs algorithm/system boundary. README corrupted. |
| **8** | APIs and Service Design | 8 | 0 / 8 (scaffold) | **Underweight.** 8 ch for the entire API surface of a backend career. Industry expectation: versioning, compatibility, idempotency, errors, pagination, contracts each deserve depth. | Duplicates gRPC with Vol 3. Needs +2–3 ch (compatibility, governance, code-gen, breaking-change detection). README corrupted. |
| **9** | Security, Authentication, and Cryptography | 11 | 0 / 11 (scaffold) | **Underweight relative to Vol 0, which is the real problem.** 11 ch cannot credibly cover "security as a backend topic" when Vol 0 spends 75 ch on one sub-domain of security. | Duplicates secrets, signing, PKI/TLS, policy-as-code with Vol 0. Needs explicit relationship (see §6). Otherwise scope is correct for a generalist volume. Placement late (see MAJOR-04). |
| **10** | Messaging, Streaming, and Event Systems | 8 | 0 / 8 (scaffold) | **Underweight.** Kafka + stream processing + event sourcing + outbox + backpressure + DLQ in 8 ch is compressed. | Ch02 delivery semantics duplicates Vol 6 ch09 idempotency/exactly-once — need boundary (Vol 6 = theory, Vol 10 = broker mechanics). |
| **11** | Reliability, Observability, and SRE | 10 | 0 / 10 (scaffold) | Borderline thin. SRE is a career, not 10 ch, but 10 is defensible if focused. | Overlaps: ch08 Chaos ↔ Vol 6 ch12, ch05/06 IR/postmortems ↔ Vol 0 Book 8 ch06, ch09 deployment strategies ↔ Vol 0 Book 5 ch10 (deployment gates). Define boundaries. |
| **12** | Cloud, Containers, and Infrastructure | 8 | 0 / 8 (scaffold) | **Underweight.** Cloud + K8s + IaC + cost in 8 ch is a flyover. For a FAANG senior, this is daily work. | Duplicates: ch01 containers ↔ Vol 2 ch09, ch04 IaC ↔ Vol 0 Book 6 ch08, ch08 cost ↔ Vol 7 ch02 / Vol 11 ch07. Needs +2–3 ch (networking, IAM, cost particularly). |
| **13** | Language Runtimes for Backend | 5 | 0 / 5 (scaffold) | **Severely underweight.** 5 ch for JVM + Go + Rust + GC + profiling. Each runtime alone could be 5 ch. | Missing: Python runtime (explicitly excluded? — justify), Node.js isolate model, Wasm, FFI. At 5 ch this will be either shallow or JVM-centric. Recommend 8–9 ch. |
| **14** | Data Structures and Algorithms for Backend | 8 | 0 / 8 (scaffold) | Appropriate. | Overlaps rate-limiting with Vol 7. Ch06 (Sorting/external sorting) duplicates Vol 5 storage-engine sorting — needs boundary. |
| **15** | Software Engineering Practice | 6 | 0 / 6 (scaffold) | **Underweight.** Testing, design docs, DDD, patterns, refactoring, code review in 6 ch trivializes the discipline that determines whether systems survive. | Ch01 Testing in 1 ch is insufficient for a senior backend (unit/integration/E2E/property/contract/load). Needs expansion to 2 ch or a dedicated testing cross-cut. |

**Summary math:** 221 planned chapters, 145 done (65.6% by count), but 100% of done chapters are Vols 0–6. Vols 7–15 (76 ch) are 0% written yet represent the most career-differentiating material.

---

## 4. Coverage Audit — Backend-Senior Topic Map

Every topic a FAANG-level senior backend engineer is expected to command, mapped to its home(s) or flagged orphaned.

| Topic | Home (CURRICULUM) | Assessment |
|-------|-------------------|------------|
| **CPU / memory / storage hardware** | Vol 1 (10 ch) | ✅ Covered. |
| **OS / Linux internals** | Vol 2 (12 ch) | ✅ Covered. |
| **Networking (TCP/UDP/QUIC/DNS/TLS/HTTP/gRPC)** | Vol 3 (12 ch) | ✅ Covered, but TLS/gRPC duplicated elsewhere. |
| **Concurrency (threads, locks, memory models, lock-free, async, actors)** | Vol 4 (10 ch) | ✅ Covered. |
| **Databases (engines, indexing, TXN, MVCC, replication, sharding, NoSQL/NewSQL)** | Vol 5 (14 ch) | ✅ Covered. |
| **Distributed systems (clocks, consistency, consensus, quorums, CRDTs, Jepsen)** | Vol 6 (12 ch) | ✅ Covered. |
| **System design (scalability, caching, partitioning, multi-region, resilience)** | Vol 7 (12 ch) | ⚠️ Covered but thin; multi-region and design cases need more than 1 ch each. |
| **API design (REST/gRPC/GraphQL, versioning, compatibility, idempotency)** | Vol 8 (8 ch) | ⚠️ Covered but thin; missing API governance, breaking-change detection, code-gen, contract testing. |
| **Security / AuthN/Z / Crypto / mTLS / zero trust / AppSec** | Vol 9 (11 ch) | ⚠️ Covered in isolation, but dwarfed by Vol 0; relationship undefined. |
| **Supply-chain security (SBOMs, SLSA, Sigstore, TUF, in-toto, CI/CD hardening)** | **Vol 0 (75 ch)** | 🔴 Massively over-covered relative to suite (see §6). Core concepts belong in Vol 9 + Vol 12 + Vol 11, not 75 ch silo. |
| **Messaging / streaming (Kafka, delivery semantics, event sourcing, outbox, backpressure)** | Vol 10 (8 ch) | ⚠️ Covered but compressed; missing exactly-once end-to-end case study. |
| **Reliability / Observability / SRE (SLOs, metrics/traces/logs, IR, chaos, deploys)** | Vol 11 (10 ch) | ⚠️ Covered; but incident response appears in 3 places (Vol 0, Vol 11, Vol 7). Needs dedup. |
| **Cloud / Containers / K8s / IaC / multi-tenancy / cost** | Vol 12 (8 ch) | ⚠️ Covered but thin; cloud networking, IAM, and cost each deserve dedicated chapters. |
| **Language runtimes (JVM, Go, Rust, GC, JIT, profiling)** | Vol 13 (5 ch) | 🔴 Under-covered. Missing Python/Node/Wasm rationale, runtime selection framework. |
| **Data structures & algorithms for systems (hashing, sketches, consistent hashing, scheduling)** | Vol 14 (8 ch) | ✅ Covered. |
| **SWE practice (testing, design docs, DDD, patterns, refactoring, review)** | Vol 15 (6 ch) | 🔴 Under-covered. Testing alone needs 2 ch. |
| **Performance engineering (benchmarking, profiling, tuning, capacity planning)** | Scattered: Vol 1 ch08, Vol 2 ch11, Vol 7 ch02, Vol 11 ch07, Vol 13 ch05 | 🔴 **Orphaned — no coherent home.** Needs a dedicated performance thread or a new Vol/chapter cluster. Currently fragmented across 5 volumes with no ownership. |
| **Testing strategy (unit/integration/E2E/property/contract/load/fault)** | Vol 15 ch01 (1 ch) + Vol 4 ch10 + Vol 6 ch12 | 🔴 **Orphaned/underweight.** 1 ch for testing strategy is indefensible for a senior curriculum. Contract testing, load testing, and fault injection are scattered. |
| **Incident management & on-call (detection, triage, comms, postmortems, runbooks)** | Vol 11 ch05–06 + Vol 0 ch05–06 | ⚠️ Covered but split between generic SRE and supply-chain-specific IR; needs cross-ref. |
| **Cost & capacity engineering (FinOps, unit economics, rightsizing, commitments)** | Vol 12 ch08 (1 ch) + Vol 7 ch02 + Vol 11 ch07 | 🔴 **Orphaned/thin.** 1 ch for cloud cost in 2026 is insufficient. Should be 2 ch (cost) + capacity integrated with Vol 7. |
| **Data engineering & analytics (pipelines, warehouse/lakehouse, ETL/ELT, CDC, batch vs stream)** | Vol 5 ch13 ("Specialized Stores: Search, Time-Series, Analytics" — 1 ch) | 🔴 **Orphaned.** Analytics/time-series/search collapsed into 1 ch. No pipeline, CDC, or warehouse coverage. For a backend suite this is a notable gap. |
| **ML infrastructure & AI systems (feature stores, model serving, vector DBs, eval, LLM ops)** | Vol 0 Book 7 ch07 ("AI-Generated Code and the Model Supply Chain" — 1 ch, supply-chain lens only) | 🔴 **Orphaned.** Zero coverage of model serving, feature platforms, or vector search as backend concerns. Given 2026 relevance, at minimum needs a 2–3 ch appendix or a Vol 16. |
| **Platform engineering & developer experience (IDP, paved roads, CI/CD platforms, self-service)** | Scattered: Vol 11 ch09 (deploys), Vol 12 ch04 (IaC), Vol 0 entire (CI/CD hardening) | 🔴 **Orphaned.** No volume owns platform/IDP. Vol 11 or Vol 12 should claim it. |
| **Data privacy, compliance & governance (GDPR, audit, lineage, retention)** | Vol 0 Book 8 (governance, 8 ch — supply-chain lens) + Vol 9 ch11 (threat modeling) | ⚠️ Covered only through supply-chain lens; general privacy/compliance for backend systems (data classification, retention, audit logging) has no home. |
| **Frontend-backend contract & BFF / edge** | Vol 7 ch08 (API Gateways, BFF, and Edge — 1 ch) | ⚠️ Thin; edge compute, CDN, and BFF patterns deserve more than a single combined chapter. |
| **Serialization & wire formats (Protobuf, Avro, JSON, Parquet, schema evolution)** | Vol 8 ch08 (Compatibility and Wire Formats) + Vol 5 storage engines | ⚠️ Single chapter for all wire formats + evolution is thin; keep but ensure depth on schema registry and compatibility checks. |
| **Queueing theory & capacity math (Little's Law, backpressure, load shedding)** | Vol 7 ch09/ch11 + Vol 10 ch07 + Vol 14 ch08 | ⚠️ Fragmented; needs a unifying treatment in Vol 7 or Vol 14. |

**Orphaned / critically thin topics requiring a decision:** Performance engineering, testing strategy, data engineering/pipelines, ML infra, platform engineering, cost engineering, privacy/compliance for general backend. See §7 for expansion proposals.

---

## 5. Ordering / Pedagogy Assessment

**What works:**
- Vols 1 → 2 → 3 → 4 → 5 → 6 is a principled bottom-up stack: hardware → OS → network → concurrency → storage → distribution. Dependencies flow forward. This is the strongest part of the curriculum.
- Placing System Design (Vol 7) after the foundations is correct — design without internals is hand-waving.

**What does not work:**

1. **Security is in the wrong place.** Vol 9 after Vols 7–8 means readers design systems and APIs before learning authN/Z, crypto, mTLS, and threat modeling. In practice, security constrains system design (tenancy, auth, secret flow, zero trust). Pedagogy should be: distributed foundations (Vol 6) → security (Vol 9) → system design (Vol 7) → APIs (Vol 8). Alternatively, keep numeric order but mark Vol 9 as a prerequisite and cross-reference it from Vol 7 ch01.

2. **Vol 0 at the front poisons the learning curve.** A new reader opening the library encounters 75 chapters of supply-chain security before reaching "Why Architecture Matters." For a generalist backend engineer, this is a specialization-first sequence. It signals that supply-chain security is *the* subject, with backend as context — the inverse of the stated framing.

3. **SRE (Vol 11) after Messaging (Vol 10) is okay, but Cloud (Vol 12) after SRE is inverted.** You cannot reason about SLOs, chaos, and deployment strategies (Vol 11) without the compute/container/platform substrate (Vol 12). Vol 12 should precede Vol 11. Current: …10 Messaging → 11 SRE → 12 Cloud. Better: …10 Messaging → 12 Cloud → 11 SRE (so SRE can assume K8s/cloud primitives).

4. **Runtimes (Vol 13) and Algorithms (Vol 14) are islands.** They have no pedagogical link to neighbors. Vol 13 (runtimes) logically follows Vol 2 (OS) and Vol 4 (concurrency) — consider clustering Vols 1–4 as "Execution" and Vols 5–6 as "State & Distribution." The current linear order is fine but would benefit from a part structure:
   - Part I — Execution: Vols 1–4
   - Part II — State: Vols 5–6
   - Part III — Security: Vol 9 (+ Vol 0 companion)
   - Part IV — Systems: Vols 7–8, 10–12
   - Part V — Fundamentals: Vols 13–15

5. **No "how to use this library" reading paths.** A senior backend engineer will not read 221 chapters linearly. The curriculum needs 3–4 curated paths (e.g., "Distributed Systems Track: Vols 4→6→10→7," "Platform Track: Vols 2→9→12→11," "Security Track: Vol 9→Vol 0 companion") — otherwise the sheer size is paralyzing.

6. **Chapter-count variance within volumes implies uneven depth contract.** Vol 13 = 5 ch, Vol 5 = 14 ch, both promise 4k–7k words/ch. So Vol 13 promises ~20k–35k words total, Vol 5 promises ~56k–98k words. Either Vol 13 is trivial or Vol 5 is encyclopedic — the reader cannot tell. Standardize to 8–12 ch per volume or explicitly tier volumes as "deep" vs "survey."

**Recommendation:** Keep Vols 1–6 order. Re-slot Vol 9 earlier (after Vol 6), swap Vol 11/12, and introduce a Part structure in CURRICULUM.md. Provide reading-path guides. Do not renumber volumes lightly (breaks PROGRESS links), but add a `suggested_order` field that differs from `volume_number`.

---

## 6. Security-Weight Assessment — Is Vol 0 (75 ch) Proportionate?

**No. It is not proportionate, and it is the single largest structural risk to the project.**

### The numbers

| Metric | Value |
|--------|-------|
| Vol 0 chapters | 75 (8 books × ~9.4 avg) |
| Rest-of-library chapters (Vols 1–15 planned) | 146 |
| Vol 0 share of planned chapters | **33.9%** |
| Vol 0 share of *done* chapters (145 done) | **51.7%** (75/145) |
| Vol 0 words at STYLE.md depth | **300k–525k words** |
| Vol 0 diagrams at STYLE.md depth | **150–300 Mermaid diagrams** |
| Equivalent | A full 900-page textbook on supply-chain security |
| User intent | "Security should be A TOPIC within larger backend suite, not dominating" — *general knowledge building* |
| Largest other volume | Vol 5, 14 ch (6.3%) — Vol 0 is 5.4× the average |

### Why it grew

Historically honest: Vol 0 was the original 8-book suite and was not trimmed when the scope expanded to Vols 1–15. `CURRICULUM.md` scope note admits this: "This started as an 8-book suite on software supply chain security (now Volume 0) and was expanded to the full backend curriculum. Volume 0's chapters are the most mature." Sunk-cost bias kept it intact while the rest of the library was scaffolded around it.

### The cost

1. **Reader signal:** The library reads as "a supply-chain security encyclopedia with a backend appendix," not the inverse.
2. **Author cost:** 75 chapters at graduate depth is ~6 months of subagent work (as PROGRESS.md attests: all 75 are already done). That half of total effort is allocated to a niche sub-domain of one volume's topic.
3. **Overlap tax:** Vol 0 duplicates material that belongs in Vol 9, Vol 11, Vol 12 (see §4). Maintaining both will cause drift.
4. **PDF/render impossibility:** A single PDF containing Vol 0 + Vols 1–15 would be ~1.2M–1.5M words. Multi-size PDF renders (phone/tablet/laptop) as requested will be unwieldy as one artifact; splitting is required anyway.

### Recommendation — Pick one; do not leave Vol 0 as-is

**Option A — Trim in place (least disruption, still large):**
- Keep Vol 0 as Volume 0 but cap at **25–30 chapters** by merging books. Example: collapse 8 books → 4 books (Foundations, Dependencies+SBOMs, Build+Signing, Cloud/Source+Governance). Archive the other ~45 chapters as `archive/vol0-expanded/` (retain git history, exclude from main PDF). This still makes security the largest volume but by 2×, not 5×.

**Option B — Merge into Vol 9 (purist "security is one topic" answer):**
- Fold Vol 0's essential chapters (~15–18 ch) into an expanded Vol 9 (from 11 → ~20 ch, potentially split into 9A/9B). This satisfies "security as one topic" most literally. *Con:* Loses the deep-dive value that the 75 ch represents; large rewrite.

**Option C — Companion series (recommended):**
- **Spin Vol 0 out as a standalone companion: `Supply Chain Security — Companion Series (8 books, 75 ch)`.** Keep its `book-01…08` structure, but remove it from the main library's volume numbering. Replace it inside the main sequence with a new **Vol 0′ — "Supply-Chain Security Essentials" (8–12 ch)** that distills the companion's key ideas for the generalist (threat model, SLSA/S2C2F, SBOMs, signing, CI/CD hardening, K8s policy, IR). The companion remains available, cross-referenced from Vol 9 ch11 and Vol 11/12 as "for deeper study, see Companion Book X."
- *Why recommended:* Respects the 75 ch of done work (no deletion), restores proportionality (main library becomes 146 + ~10 = 156 ch, security essentials = ~6–7% not 34%), and gives the PDF pipeline a clean split (Core Library PDF vs Security Companion PDF). The `archive/` approach loses work; the merge approach rewrites work. Companion preserves work while fixing the narrative.

**Regardless of option:** Add a one-paragraph "Relationship to Vol 9" note in both places so readers understand which to read when.

**What NOT to do:** Keep Vol 0 at 75 ch *and* write Vol 9 at 11 ch *and* call the suite "general backend knowledge." That is the current plan and it fails the user's framing on its face.

---

## 7. Missing Topics & Suggested Expansions

Gaps are not failures — every curriculum omits something. These are the omissions that most weaken the "FAANG-level senior backend" claim.

| Gap | Severity | Proposal | Where |
|-----|----------|----------|-------|
| **Testing strategy** — 1 ch (Vol 15 ch01) for unit/integration/E2E/property/contract/load is indefensible. Contract testing (Pact), property-based (Hypothesis/QuickCheck), and fault injection deserve treatment. | High | Expand Vol 15 ch01 → 2 ch (Foundations + Integration/Contract/E2E) and add Vol 10↔Vol 5 cross-ref for load testing. Alternatively add a new Vol 16 ch or appendix. | Vol 15 |
| **Performance engineering** — fragmented across 5 volumes, no owner. Missing: benchmarking harness design, statistically sound measurement, continuous perf, flame-graph workflow, capacity math (Little's Law, queueing). | High | Add a **Performance chapter cluster**: either a new Vol 7½ (3 ch) or expand Vol 13 ch05 (Profiling) + Vol 1 ch08 into a coherent 3-ch arc: Measurement → Analysis → Tuning. | Cross-cut; home in Vol 13 or new |
| **Cost & FinOps** — Vol 12 ch08 alone (1 ch) for cloud cost in 2026. Missing: unit economics, commitment planning, rightsizing, multi-region cost trade-offs, sustainability. | High | Expand Vol 12 ch08 → 2 ch (Cost Engineering + Capacity/FinOps) | Vol 12 |
| **Data engineering / pipelines** — CDC, ETL/ELT, warehouse/lakehouse, batch vs stream, lineage. Currently collapsed into Vol 5 ch13 ("Search, Time-Series, Analytics" — 1 ch). | High | Expand Vol 5 ch13 → 2 ch or add a new Vol 10 companion ch: "Batch Pipelines and the Warehouse." At minimum, scope Vol 5 ch13 as 2 ch (Search/TSDB + Analytics/Warehouse). | Vol 5 / Vol 10 |
| **ML infrastructure** — model serving, feature stores, vector DBs, eval, LLM gateway, GPU scheduling. Only 1 ch via supply-chain lens (Vol 0 Book 7 ch07 on AI-generated code). | Medium-High | Add a 2–3 ch **ML Systems appendix** (or Vol 16 if the library grows): "Model Serving & Feature Platforms; Vector Search & Retrieval; LLM Systems for Backend." Justified by 2026 senior expectations. | New |
| **Platform engineering / IDP** — paved roads, self-service, CI/CD platforms, backstage-style portals. Scattered but unowned. | Medium-High | Claim in Vol 12: add ch "Platform Engineering: Paved Roads and Internal Developer Platforms" (or expand Vol 11 ch09). | Vol 12 or Vol 11 |
| **Data privacy & compliance (GDPR, retention, lineage, audit logging)** — covered only via supply-chain governance. No general-purpose backend treatment. | Medium | Add to Vol 9: ch "Data Privacy and Compliance for Backend Systems" (classification, retention, audit, DSR). | Vol 9 |
| **Incident management deep dive** — runbooks, comms, escalation, game days. Vol 11 ch05–06 are 2 ch for IR + postmortems; real on-call is broader. | Medium | Expand Vol 11 ch05 → 2 ch (On-Call & Triage + Comms & Coordination) or add runbook/game-day ch. | Vol 11 |
| **Edge compute, CDN, and BFF** — Vol 7 ch08 collapses gateways + BFF + edge into 1 ch. | Medium | Split Vol 7 ch08 → 2 ch (Gateways & BFF + Edge/CDN/Global Distribution) — especially as Vol 7 ch10 is Multi-Region, they pair. | Vol 7 |
| **API governance & breaking-change management** — versioning (ch05) + compatibility (ch08) are 2 ch, but missing: API linting, governance, code-gen (OpenAPI/gen), schema registry, deprecation policy. | Medium | Expand Vol 8: add ch "API Governance, Code Generation, and Breaking-Change Detection." | Vol 8 |
| **Serialization deep dive** — Protobuf/Avro/Parquet/JSON choice, schema evolution, registry. Currently 1 ch (Vol 8 ch08). | Low-Medium | Keep 1 ch but ensure scope includes schema registry and evolution checks; cross-ref with Vol 5 storage. | Vol 8 |
| **Queueing theory & backpressure math** — fragmented. | Low | Unify in Vol 7 or Vol 14 with a focused treatment; cross-ref from Vol 10 ch07. | Cross-cut |

**Sizing implication:** Adding the High-priority expansions adds ~8–10 ch net; Medium adds another ~6–8 ch. Even after expansions, the library stays within ~165 ch for the core (if Vol 0 is companioned) — still large but defensible as a multi-year reference.

---

## 8. Diagram / Illustration Needs Per Volume

STYLE.md mandates 2–4 Mermaid diagrams per chapter (so each volume needs ~16–56 diagrams). Assessment is not count compliance (that is an authoring check) but whether the *types* of diagrams actually needed exist and where illustration debt is highest.

| Vol | Must-have diagram types (examples) | Risk / Debt |
|-----|------------------------------------|-------------|
| **0** | Attack flow sequence diagrams (per incident), trust-boundary flowcharts, SLSA provenance graphs, SBOM relationship graphs, Sigstore/TUF sequence diagrams, admission-control policy flowcharts, IR timeline diagrams. | Low risk — 75 ch already written; spot-check 5 ch for Mermaid validity. Debt is over-illustration (too many similar attack flows); consolidate a canonical "supply-chain attack surface" diagram reused, not re-drawn 8 times. |
| **1** | CPU pipeline / OoO / speculation flowcharts, memory-hierarchy pyramid, cache-coherence state machines (MESI), NUMA topology, SIMD lane diagrams, storage latency spectrum. | Medium — mechanical sympathy and MESI are hard without precise diagrams. Require at least one cache-coherence state machine and one NUMA topology per relevant ch. |
| **2** | Process address-space layout, CFS scheduling flow, page-table walk, VFS layering, epoll vs io_uring sequence diagrams, namespace/cgroup containment, network-stack packet path, eBPF program lifecycle. | Medium — Vols 2–3 are the most diagram-dependent. Packet-path and syscall-boundary diagrams are critical; missing them makes chapters prose-only. |
| **3** | Packet-journey end-to-end, TCP state machine, congestion-control behavior graphs, QUIC vs TCP comparison, DNS resolution sequence, TLS handshake sequence, HTTP/2 vs HTTP/3 framing, gRPC call flow, LB algorithm visuals, retry/hedge state machines, observability (tcpdump/Wireshark flow). | High — TCP state machine and TLS handshake must be normative-accurate diagrams, not approximations. |
| **4** | Concurrency model taxonomy, lock modes/ownership, happens-before graphs, CAS/lock-free structure animations (compare-and-swap sequence), deadlock wait-for graphs, event-loop phase diagrams, actor/CSP channel topologies, structured-concurrency scope trees. | High — happens-before and lock-free diagrams are notoriously error-prone; require careful review. |
| **5** | B-Tree vs LSM visualizations, index-type decision tree, query-plan tree, MVCC version-chain diagram, WAL/ARIES recovery flow, replication topology (sync/async, physical/logical), sharding/consistent-hashing ring, 2PC/Saga sequence diagrams, CAP placement map of stores. | High — replication topologies and 2PC/Saga sequences are the highest-value diagrams in the whole library; invest extra review. |
| **6** | Timeline/clock diagrams (Lamport, vector, Hybrid), consistency-model lattice, CAP/PACELC trade-off triangle, Paxos/Raft sequence diagrams (prepare/promise/accept), quorum intersection, ZooKeeper/etcd architecture, gossip/SWIM rounds, CRDT merge diagrams, Jepsen history visualizations. | Very high — Paxos/Raft and consistency-model diagrams are the most likely to be subtly wrong. Each consensus chapter needs at least one step-by-step sequence with failure injection. |
| **7** | Scalability principle layering, estimation worksheets (visual), cache hierarchy (local/remote/CDN), data-modeling ER/partition diagrams, microservice vs modular-monolith topology, event-driven flow, gateway/BFF/edge layering, rate-limit algorithm visuals (token bucket/leaky bucket), multi-region replication topologies, bulkhead/circuit-breaker state machines. **Needs custom case-study architecture diagrams per case (feed, chat, KV) — at least 1 per case, 3–4 total.** | High — Vol 7 will be diagram-starved if case studies are prose-only. Require architecture diagrams for each design case. |
| **8** | API contract lifecycle, REST resource modeling, gRPC service definition flow, GraphQL query vs N+1, versioning/evolution timeline, idempotency-key sequence, pagination comparison table+flow, error-taxonomy, wire-format compatibility matrix. | Medium — idempotency and versioning sequences are high-value; GraphQL N+1 needs a diagram. |
| **9** | Crypto primitive selection flowchart, KDF/password-storage flow, encryption mode comparison, PKI/cert lifecycle sequence, OAuth/OIDC flows (auth code, PKCE, client credentials), RBAC/ABAC/ReBAC (Zanzibar) relation graph, secret-distribution sequence, mTLS/SPIFFE attestation flow, threat-model (STRIDE) diagram. | Very high — OAuth/OIDC sequence diagrams are the most forked/copied-wrong diagrams on the internet. Require PKCE + refresh + token-binding variants. Zanzibar needs a relation graph. |
| **10** | Queue vs log vs pub/sub topology, delivery-semantic state machines (at-most/at-least/exactly-once), Kafka partition/replica/ISR diagram, stream-processing topology (source→operator→sink), event-sourcing/CQRS flow, outbox sequence (dual-write vs outbox), backpressure signal flow, DLQ/retry topology. | High — exactly-once end-to-end and outbox sequences are the core intellectual contribution; they must be precise. |
| **11** | SLI/SLO/error-budget burn, RED/USE metric dashboards (mock), log pipeline, trace waterfall (OpenTelemetry), incident timeline, postmortem template, load-test harness, chaos experiment flow, deployment strategy comparison (blue/green, canary, flags), resilience pattern matrix. | Medium — SLI/SLO burn and trace waterfall are essential; resilience patterns benefit from a state-machine per pattern. |
| **12** | Container image layer stack, K8s control-plane/data-plane, workload/networking/storage topology, IaC pipeline (plan/apply), cloud service map (compute/storage/network), multi-tenancy isolation layers, cost-curve/rightsizing visuals. | Medium — K8s architecture and tenancy isolation are diagram-critical. |
| **13** | JVM heap/GC generations, Go scheduler (P/M/G) diagram, Rust ownership/borrow visual, GC algorithm comparison (mark-sweep/copying/generational), profiling flame-graph reading guide, JIT tiering. | Medium — Go P/M/G and JVM GC generations are frequently mis-drawn; require authoritative sources. |
| **14** | Complexity class visual, hash-table collision handling, tree rotation, sketch (Bloom/HLL/CMS) internals, consistent-hashing ring with virtual nodes, external-sort phases, graph topology (for systems), rate-limit/scheduling algorithm comparison. | Low-Medium — mostly algorithm visuals; consistent-hashing ring is the highest-value. |
| **15** | Testing pyramid/strategy map, design-doc lifecycle, DDD bounded-context map, pattern catalog (visual), refactoring flow, code-review flow. | Low — Vol 15 is the least diagram-dependent, but testing strategy needs a pyramid plus a contract-testing sequence. |

**Cross-cutting illustration guidance:**
- Mermaid `sequenceDiagram` for flows with temporal ordering (handshakes, consensus, OAuth, outbox, IR).
- `flowchart` / `graph` for architectures and trust boundaries.
- `stateDiagram` for state machines (TCP, circuit breakers, TLS, replication states).
- `gantt` for IR timelines only where genuinely useful.
- Tables for comparisons (B-Tree vs LSM, consistency models, GC algorithms, LB algorithms).
- Every chapter should have one "anchor architecture" diagram; avoid 4 trivial diagrams that add no insight just to hit the count.

---

## 9. Answers to Open Decisions

### Q1: Should Vol 0 be merged into Vol 9?

**No — not fully. See §6 Option C.**

Merging 75 ch into an 11 ch volume is a false economy. It would either (a) bloat Vol 9 to ~86 ch (absurd) or (b) require cutting ~60 ch of already-done work, which wastes effort and destroys the deep-dive value for readers who *do* want supply-chain depth. The correct move is **companion series + essentials distillate**: keep the 75 ch intact as a separate artifact, and replace Vol 0 inside the main sequence with an 8–12 ch essentials volume that every generalist reads.

If the team insists on a literal "security is one topic" structure (no companion), then **Option B** (fold ~15–18 essential ch into an expanded Vol 9) is the honest merge — but explicitly archive the remaining 57–60 ch, do not delete.

### Q2: Should Vols 7–15 be expanded?

**Yes — selectively, not uniformly.**

- **Expand:** Vol 8 (8→10–11), Vol 12 (8→10–11), Vol 13 (5→8–9), Vol 15 (6→9–10). These are currently below the threshold where senior depth is credible.
- **Keep:** Vol 7 (12), Vol 11 (10), Vol 14 (8) — adequate if scoped tightly.
- **Keep but rebalance content:** Vol 10 (8) is adequate if exactly-once and stream processing are not shortchanged; otherwise +1 ch.
- **Do not expand for its own sake.** The library is already 221 ch planned. Adding High-priority gaps (§7) is ~+8–10 ch; expanding thin volumes is another ~+6–8 ch. After companioning Vol 0, that yields ~170–175 ch total — large enough. Further expansion should be new companion appendices (ML systems, performance deep dive), not more main-sequence chapters.

### Q3: Should Vols 1–6 be trimmed to make room?

**No.** Vols 1–6 are the only completed, coherent part of the library (all 69 ch done). Trimming them now would mean rewriting finished chapters to make room for unfinished ones — the wrong trade. If total length must be capped, cut from Vol 0 (the outlier) and defer low-priority gaps to companions, not from the foundations.

### Q4: Should the library be split for PDF rendering?

**Yes — split regardless of other decisions.**

Per task context: "At end user will ask for multi-size PDF renders (phone/tablet/laptop). Content must stay separate from PDF rendering (currently markdown+Mermaid, which is correct)." The rendering constraint confirms: keep markdown+Mermaid as source, render variants as build artifacts.

Even without that, a single 1.2M-word PDF is unusable on any device. Recommended splits:
- **Artifact 1 — Core Library:** Vols 1–15 (+ Supply-Chain Essentials 8–12 ch) → ~170 ch, ~700k–900k words.
- **Artifact 2 — Supply Chain Companion:** 75 ch, ~400k words.
- Each artifact gets phone/tablet/laptop (and optionally print) variants. That is 6–8 PDFs, not 3, but each is navigable.

### Q5: What about the `suggested_order` vs `volume_number` tension?

Keep volume numbers stable (to avoid breaking PROGRESS.md links and git history). Add a `Suggested reading order` section to CURRICULUM.md that differs from numeric order: `1→2→3→4→5→6→9→7→8→10→12→11→13→14→15` plus the Essentials/Companion note. This fixes pedagogy without a rename cascade.

### Q6: What should happen next, concretely?

1. **Fix BLOCKER-01 and BLOCKER-04** (README regeneration) — 1 commit, <1 hour, unblocks all downstream work.
2. **Decide Vol 0 fate** (BLOCKER-02) — requires human decision; this audit recommends Option C. Do not write Vols 7–15 until decided; otherwise Vol 9 authors will duplicate Vol 0 content.
3. **Add boundary notes for duplications** (MAJOR-01) and chapter scopes (MAJOR-03) — 1 commit to CURRICULUM.md.
4. **Re-slot Vol 9 and swap Vol 11/12 + add Part structure and reading paths** (MAJOR-04, §5).
5. **Rebalance thin volumes per §7/§8** — adjust CURRICULUM.md ch counts.
6. **Only then resume chapter writing** (Vols 7–15 batches).

---

## Appendix — Audit Method & Evidence

- Read `CURRICULUM.md` (237 lines), `PROGRESS.md` (335 lines), `STYLE.md` (64 lines) in full.
- Ran `ls -1` per volume dir (24 dirs) and counted files; verified 145 `[x]` vs 76 `[ ]` in PROGRESS.md.
- Sampled 10 READMEs; 4 of 9 post-foundation READMEs showed interleaved injection (100% of Vols 5–8 sampled beyond Vol 4 were corrupted or showed corruption pattern). Remaining Vols 9–15 READMEs beyond the sampled set were not individually re-read but are assumed at risk because the same generator produced them — verify all.
- Cross-referenced CURRICULUM.md volume table (16 rows) against PROGRESS.md section headers and README contents; found filename authority divergence.
- Computed Vol 0 share: 75/221 = 33.9% planned, 75/145 = 51.7% done.
- Checked `workdir` is `/home/ubuntu` per task; no `/workspace` assumption.

---

*End of audit. No edits were made to `CURRICULUM.md` per instructions — only this file was written.*
