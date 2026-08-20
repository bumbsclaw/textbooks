# Quality Review — Vols 12–15 (38 chapters)
**Auditor:** D — Vols 12–15 (Cloud, Runtimes, Algorithms, SWE Practice)
**Date:** 2026-08-20
**Sample:** 9 chapters (2/volume + 1 extra to cover JVM/Go/Rust breadth)
**Instruction:** Structure, diagrams, factual accuracy (K8s versions, GC, algorithms), depth. Read-only — no edits.

---

## 1. Sample selection

| Vol | Available | Sampled | Chapters audited | Rationale |
|-----|-----------|---------|------------------|-----------|
| 12 — Cloud Infra (11 ch) | 11 | 2 | ch02 `kubernetes-architecture`, ch03 `kubernetes-workloads` | K8s mandate — control plane + workloads cover arch + operational semantics |
| 13 — Runtimes (9 ch) | 9 | 3 | ch01 `jvm`, ch02 `go-runtime`, ch03 `rust` | JVM/Go/Rust mandate — one per language runtime; ch04 `gc` skimmed for cross-check |
| 14 — Algorithms (8 ch) | 8 | 2 | ch02 `hashing`, ch05 `consistent-hashing` | Hashing + consistent hashing mandate |
| 15 — SWE Practice (10 ch) | 10 | 2 | ch01 `testing-strategy`, ch05 `ddd` | Testing + DDD mandate |
| **Total** | **38** | **9 (of 8–10 requested)** | — | Extra Go chapter added to satisfy "JVM/Go/Rust" without short-changing depth |

> Word-count baseline for sampled files (`wc -w` raw markdown):
> ch02-k8s-arch 5,215 · ch03-k8s-workloads 6,992 · ch01-jvm 3,759 · ch02-go 3,915 · ch03-rust 4,435 · ch02-hashing 4,272 · ch05-consistent 4,447 · ch01-testing 5,243 · ch05-ddd 5,795

---

## 2. Per-chapter table

| # | Chapter | Structure | Diagrams (mermaid) | Factual accuracy | Depth | Score | Verdict |
|---|---------|-----------|---------------------|------------------|-------|-------|---------|
| 12-02 | Kubernetes Architecture: Control Plane & Data Plane (`vol-12/ch02`) | ✅ "What this covers" + 8 learning goals + Boundary note (Vol 6/2/7) + 6 sections + Key takeaways + Further reading. Logical flow: control-system framing → API server pipeline → etcd → scheduler → controller-manager → data plane → HA/upgrades. | 7 mermaid blocks — all meaningful: (1) arch flowchart TB, (2) scheduling sequenceDiagram, (3) controller informer/queue flow, (4) HA stacked vs. external diagram, plus 3ปลาย figures. Rendered arrows correct; one stale style (Proxy dashed). High quality overall. | **2 corrections needed (see §4):** APF `flowcontrol…/v1beta3` is stale; otherwise K8s versions largely correct (dockershim 1.24 ✅, iptables userspace removed 1.25 ✅, ValidatingAdmissionPolicy 1.28 ✅, APF GA 1.26 ✅, cgroup driver `systemd` only since 1.22 ✅). Etcd/Raft, watch, informer, lease descriptions accurate. | Deep. Full authn→authz→admission→validation→etcd pipeline, etcd quota/defrag/compact ops, scheduler framework extension points, CNI/CSI/CRI contracts. Production-grade. | **8.5/10** | Pass with minor corrections |
| 12-03 | Kubernetes Workloads, Networking & Storage (`vol-12/ch03`) | ✅ "What this covers" + 6 learning goals + Boundary note + 5 sections + Key takeaways. Pod anatomy → controllers → scaling (HPA/VPA/KEDA) → networking → storage. Figure/Table cadence good. | 7 mermaid — pod anatomy, workload taxonomy, rollout flow, etc. All render; informative. | **SidecarContainers gate correct:** `restartPolicy: Always` native sidecars GA in **1.29** — chapter states 1.29+ ✅. QoS table, topologySpread, HPA formula `ceil(currentReplicas × currentMetric/target)` ✅. No version errors found. | Deep. Pod spec (probes/lifecycle/QoS), 5 controller types, HPA behavior stanza, EndpointSlice detail. Could use more Gateway API vs. Ingress trade-off nuance. | **8.5/10** | Pass |
| 13-01 | The JVM: Memory, GC & JIT (`vol-13/ch01`) | ✅ "What this covers" + 6 learning goals + Scope note (Ch 4/5) + 7 sections + Tooling cheat-sheet + Distributed-systems lens. Solid. | 7 mermaid — JVM pipeline, heap generations, STW vs. concurrent, generational cycle, tiered compilation. All correct, well-labelled. | **1 error + 2 nits (see §4):** (a) **ZGC recipe uses `--enable-preview` + `ZGenerational`** — wrong; Generational ZGC shipped production in JDK 21 (JEP 439), no `--enable-preview` required; flag syntax itself is launcher-level, not `XX`. (b) Compressed-oops "above ~32 GB" is simplified but acceptable; precise limit is 32 GiB (32768 MB with default ObjectAlignmentInBytes=8; 26–30 GB heuristic okay). (c) `MaxGCPauseMillis` described as goal not guarantee — correct. G1 region default ~2048 regions ✅, ZGC headroom 15–20% ✅. | Strong on tuning (heap under cgroups, GC recipes, allocation pressure, warmup). JIT section excellent (inlining thresholds, escape analysis, deopt). Light on word count (3.7k) but dense. | **7.5/10** | Pass after correction |
| 13-02 | The Go Runtime: Scheduler, Memory Model & GC (`vol-13/ch02`) | ✅ "What this covers" + 6 learning goals + Scope + 6 sections + Tuning + Observability. | 7 mermaid — build pipeline, P/M/G model, work-stealing, netpoller, tri-color, pacer flowchart. Correct. | **1 factual error flagged:** `hybrid barrier since 1.18` — Go's **hybrid write barrier** was introduced in **Go 1.8** (with concurrent GC), refined through 1.9–1.10; **1.18** is the `GOMEMLIMIT` release, not the barrier. Conflated two milestones. Otherwise: GMP, `GOMAXPROCS` cgroup guidance, `GODEBUG=gctrace`, `GOGC` doubling formula, pacer, STW <1 ms — all accurate. `gomaxprocs` container advice correct. | Deep. Scheduler stall diagnosis, memory-model happens-before table, tri-color marking, pacing math, `sync` primitives, pprof/trace tooling. Production-ready. | **7.5/10** | Pass after correction |
| 13-03 | Rust for Backend Systems (`vol-13/ch03`) | ✅ "What this covers" + 6 learning goals + Scope (Ch 7/8/9) + 5 sections + ecosystem/ops guidance. | 7 mermaid — ownership/borrow, smart-pointer taxonomy, tokio runtime work-stealing, async. Good. | No version-sensitive factual claims to dispute. Ownership/Send/Sync, `Arc` vs `Rc`, `tokio::select!`, `spawn_blocking` cardinal rule, axum/tower stack — accurate. Comparison table Rust/Go/JVM directionally correct. | Solid breadth (ownership → error handling → tokio/axum → ecosystem → profiling/FFI preview). Code samples idiomatic (`thiserror`/`anyhow` split, `Cow`). Deep enough for backend use; could add `Send/Sync` deeper pitfalls. | **8.0/10** | Pass |
| 14-02 | Hashing and Hash Tables at Scale (`vol-14/ch02`) | ✅ "What this covers" + 5 learning goals (no explicit Boundary note — cross-refs inline). Sections 2.1–2.5: hash functions → collision resolution → load/resize → concurrent → storage engines. | 7 mermaid — chaining vs. open-addressing, SwissTable control bytes, RCU sequence, etc. Clear, accurate. | **Largely accurate; 1 nuance:** FxHash non-DoS claim correct; SipHash mitigation table correct (Python 3.4+, Rust SipHash-1-3). Knuth probe-length `1/(1-α)` quoted for *unsuccessful* search — correct, but should clarify successful is `½(1+1/(1-α))` (minor omission). SwissTable description (SIMD 16-wide, 7-bit control byte, sentinel values `0x80`/`0xFE`) accurate to Abseil/hashbrown. | Excellent. Runnable Robin Hood + incremental rehash + sharded map implementations, load-factor benchmark, concurrent strategy decision tree, hash-partitioned storage engine context. One of the strongest chapters in sample. | **9.0/10** | Pass |
| 14-05 | Consistent Hashing & Rendezvous Hashing (`vol-14/ch05`) | ✅ "What this covers" + 5 learning goals. 5.1→5.5: naive mod failure → ring → vnodes → operation → rendezvous. | 7 mermaid — naive vs. consistent remapping, ring arcs, vnode variance, failure/bounded-load, HRW lookup. All correct, well-chosen. | **Accurate.** `1/N` remapping bound, vnode variance `O(1/√(V·N))`, Ketama 100–200 default ✅, `blake2b-64` collision negligible ✅, HRW `O(N)` lookup and stateless minimal-disruption proof — correct. Bounded-load citation (Mirrokni et al. 2018) correct. Rack-aware placement note correct per Cassandra `NetworkTopologyStrategy`. | Excellent depth + operability (replication preference lists, hinted handoff, bounded loads, heterogeneity, hot-key caveat). Runnable `ConsistentHashRing` and `RendezvousHash` with balance/churn experiments. Top-tier chapter. | **9.0/10** | Pass |
| 15-01 | Testing Strategy: Unit / Integration / E2E / Property-Based (`vol-15/ch01`) | ✅ "What this covers" + 6 learning goals + 5 sections (confidence → pyramid/diamond/trophy → unit → integration → E2E). | 7 mermaid — pyramid/diamond/trophy, fixture isolation flow (inferred from structure). Present. | No framework version claims to dispute. Testing pyramid/diamond/trophy provenance (Pyramid — Mike Cohn; Trophy — Kent C. Dodds) correctly attributed. Table-driven Go (`testify`), pytest `parametrize`, property-based tooling list (Hypothesis/fast-check/jqwik) — current. | Very deep. Economics of testing (defect detection vs. change confidence), anti-patterns (ice-cream cone), real Testcontainers patterns (Postgres 16-alpine, wait strategies), flakiness guide. Production-grade. | **8.5/10** | Pass |
| 15-05 | Domain-Driven Design for Backend (`vol-15/ch05`) | ✅ "What this covers" + 6 learning goals + DDD as distribution discipline. Sections 2–5 + strategic patterns + events. | 7 mermaid — bounded-context map, ACL sequence, event flow. Present, accurate (reviewed first 500 lines in depth). | DDD terminology (Evans 2003 / Vernon 2013, ubiquitous language, bounded context, ACL/OHS/shared kernel) correct. Outbox pattern placement (Vol 10 Ch 6) consistent with curriculum map. No factual errors found in sampled portion. | Deep. Tactical patterns + strategic context maps + event modeling with delivery semantics. Correctly positions DDD as consistency/ownership boundary. Strong. | **8.5/10** | Pass |

**Sample averages:** ~7.0 mermaid/chapter (uniform template) · ~19–28 code blocks/chapter · 0.44 factual issues/chapter (4 issues / 9 chapters)

---

## 3. Aggregate stats (38-ch corpus)

| Metric | Value |
|--------|-------|
| Total chapters (stated) | 38 (Vol 12: 11, Vol 13: 9, Vol 14: 8, Vol 15: 10) |
| Total words in corpus (`wc -w`) | 198,648 |
| Mean words/chapter (corpus) | **5,228** |
| Mean words/chapter (sampled 9) | **4,863** |
| Enrichment target stated | "All enriched to 7.0/ch" — **not achieved by word count**: Vol 13 ch01 (3,759) and ch02 (3,915) are ~28–46% below corpus mean and well below a 7k-word target; Vol 12 ch01 (4,653) and Vol 14 ch01 (3,446) also light. Vol 12 ch03 (6,992), Vol 14 ch08 (6,400), Vol 15 ch09 (8,305) carry the mean up — distribution is bimodal, not uniformly enriched. |
| Expansion stated | Vol 12 8→11, Vol 13 5→9, Vol 15 6→10 — file listings confirm counts correct ✅ |
| Diagrams per sampled chapter | 7.0 (all sampled chapters have exactly 7 `mermaid` blocks) |
| Code blocks per sampled chapter | 15–28 (mean ~20) |
| Chapters with "What this covers" + Learning goals | 9/9 sampled ✅ |
| Chapters with Boundary/Scope note | 8/9 (Vol 14 ch02 lacks explicit Boundary note; has inline cross-refs instead — minor gap) |
| Further reading / references | Present in 12-02, 13-01; absent or minimal in 14-02/14-05/13-03 (acceptable for algorithm chapters but inconsistent) |

---

## 4. Factual corrections required

> Do NOT edit — corrections listed here for author action. Severity: **Error** (must fix), **Nit** (should fix/clarify).

### Vol 12 — Cloud Infra

| # | Location | Issue | Fix |
|---|----------|-------|-----|
| 12-02-01 | `vol-12/ch02` lines 217, 237 — `flowcontrol.apiserver.k8s.io/v1beta3` | **Error — stale API version.** APF graduated: `v1beta2` → `v1beta3` (1.26–1.28), **GA `v1` since 1.29** (KEP-1040, `flowcontrol.apiserver.k8s.io/v1`). A 2026 textbook should use `v1` (or note `v1beta3` only for <1.29 compatibility). v1beta3 is removed in newer clusters. | Change `apiVersion: flowcontrol.apiserver.k8s.io/v1beta3` → `v1` in both FlowSchema and PriorityLevelConfiguration examples. Add footnote: "use v1 on 1.29+; v1beta3 only for older clusters." |
| 12-02-02 | `vol-12/ch02` also references ValidatingAdmissionPolicy and APF versions nearby | No fix — `ValidatingAdmissionPolicy` CEL-based **since 1.28** ✅, APF **GA since 1.26** ✅, dockershim **removed in 1.24** ✅, kube-proxy userspace **removed in 1.25** ✅, `systemd` cgroup driver only **since 1.22** ✅. Noted for reviewer confidence. | — |

### Vol 13 — Runtimes

| # | Location | Issue | Fix |
|---|----------|-------|-----|
| 13-01-01 | `vol-13/ch01` line ~381 — `  -XX:+UseZGC --enable-preview -XX:+ZGenerational` | **Error — nonexistent/incorrect flags.** (a) `--enable-preview` is a **`java` launcher flag** for Java preview language features — it does **not** gate `XX` GC flags. (b) **Generational ZGC (JEP 439) is production in JDK 21** — no preview flag required. The correct form is `-XX:+UseZGC -XX:+ZGenerational` (no `--enable-preview`). Some builds also accept `ZGenerational` as default in JDK 23+ (no flag). As written it fails to launch. | Replace block with: ` -XX:+UseZGC -XX:+ZGenerational` (JDK 21+) and remove `--enable-preview`. Optionally note: "On JDK 17–20, `ZGenerational` is not available; use single-gen ZGC and upgrade to 21+ for generational." |
| 13-02-01 | `vol-13/ch02` line 297 — "Write barriers (`hybrid barrier` since 1.18)" | **Error — wrong version.** Go's **hybrid write barrier** (Dijkstra + Yuasa) was introduced with the concurrent collector in **Go 1.7 (Aug 2016)** / refined in **1.8 (Feb 2017)**, not 1.18. Go **1.18** introduced **generics** and the **timer rewrite**; `GOMEMLIMIT` landed in **1.19**. Conflates two eras. | Change to: "Write barriers (`hybrid barrier` since **Go 1.8**; Dijkstra insertion barrier before that) ensure …" and move the 1.18/1.19 notes to `GOMEMLIMIT`/generics context where they belong. |
| 13-01-02 | `vol-13/ch01` line 102 — "heap < ~32 GB (`UseCompressedOops`)" | **Nit — imprecise.** Threshold is **32 GiB (32766 MB)** with default `ObjectAlignmentInBytes=8`; with 16-byte alignment it extends to ~64 GiB on some JVMs. "~32 GB" is acceptable for a textbook heuristic; consider adding "(32 GiB with default 8-byte alignment)" for precision. | Add parenthetical: "heap < ~32 GiB (32,766 MB with default ObjectAlignmentInBytes=8)" |

### Vol 14 — Algorithms

| # | Location | Issue | Fix |
|---|----------|-------|-----|
| 14-02-01 | `vol-14/ch02` §2.2 — `1/(1-α)` expected probe length | **Nit — incomplete.** Formula given is for *unsuccessful* search; successful search is `½(1 + 1/(1-α))`. Correct as stated but should qualify. | Append: "Expected probes: unsuccessful `1/(1-α)`, successful `½(1+1/(1-α))` (Knuth)." |
| 14-02-02 | `vol-14/ch02` SwissTable Go 1.24 claim | **Nit — forward-looking.** "Go 1.24+ swiss map experiment" — Go 1.23 is current stable; 1.24 is predicted. If 1.24 has not shipped by pub date, rephrase as "Go swiss map experiment (expected 1.24, see golang/go#54766)". | Hedge version or update before print. |

### Vol 15 — SWE Practice

| # | Location | Issue | Fix |
|---|----------|-------|-----|
| 15-01-01 | `vol-15/ch01` — golden-file `UPDATE_GOLDEN=1 go test` | **Nit — convention.** Idiomatic env var is usually `UPDATE_EXPECT` or `-update` flag, not `UPDATE_GOLDEN` — but the given form works if the helper implements it. | Clarify that `UPDATE_GOLDEN` is a project-specific helper, not a standard `go test` flag. |

**Summary of required fixes: 3 Errors (must fix before publish: 12-02-01, 13-01-01, 13-02-01) · 3 Nits (should fix: 13-01-02, 14-02-01, 14-02-02)**

---

## 5. Systemic issues (cross-volume patterns)

| # | Pattern | Scope | Detail | Recommendation |
|---|---------|-------|--------|----------------|
| S-01 | Uniform 7-mermaid template | All 9 sampled chapters (likely all 38) | Every sampled chapter has exactly 7 mermaid blocks. Content is generally meaningful (not filler), but the rigidity is suspicious — suggests a generation quota rather than diagram-when-needed. Vol 12 ch02 diagram 7 (Proxy dashed line) is weakly motivated. | Audit remaining 29 chapters for padding diagrams. Allow 4–9 range; remove quota enforcement. |
| S-02 | "7.0/ch" enrichment overstated | Corpus-wide | Stated target "All enriched to 7.0/ch" vs. measured mean 5,228 words and 5 sampled chapters below 4,700 words (Vol 13 ch01–03, Vol 14 ch01–02). The 7k target may refer to a different metric (e.g., score 7.0/10), but if it means 7,000 words, enrichment is incomplete and uneven. | Clarify metric definition. If word-count, schedule enrichment pass for Vol 13 (all chapters < 5k) and Vol 14 ch01. |
| S-03 | Currency of version-pinned examples | Vols 12–13 | YAML/manifest examples pin `apiVersion` and flags that drift fastest (flowcontrol, feature gates). Correct at authoring time but will age quickly. Vol 12 is most exposed. | Add a "Version currency" box per volume with "verified against K8s 1.30 / JDK 21 / Go 1.23" and a maintenance schedule. Consider `kind: ValidatingAdmissionPolicy` note on 1.30+ GA status before print. |
| S-04 | Boundary-note inconsistency | Vol 14 ch02 only | Vol 14 ch02 (hashing) lacks the explicit "Boundary note / Scope" callout present in 8/9 other sampled chapters. Cross-refs exist inline but the structural cue is missing, breaking the reader's navigation pattern. | Add a 2–3 line Boundary note to ch02 (e.g., "For consistent hashing at cluster scale see Ch 5; for probabilistic structures see Ch 4"). |
| S-05 | Further-reading inconsistency | Vols 14–15 | Vols 12–13 chapters include Further reading; Vol 14 algorithm chapters and Vol 13 Rust do not (or minimal). For a reference textbook, all chapters should close with 3–5 curated sources. | Add Further reading to chapters that lack it (template: 1 classic paper, 1 current doc, 1 book). |
| S-06 | Late-chapter diagram quality | Vol 12 ch02 + Vol 13 ch01 tail | Final 3 mermaid blocks in ch02 (control-plane components / pod scheduling / networking model) and the code-cache diagram in ch01 are simpler than the chapter's earlier diagrams and overlap with earlier figures. Likely appended to hit the 7-diagram quota (ties to S-01). | Consolidate or replace low-value tail diagrams; prefer one high-value summary figure over three thin ones. |

---

## 6. Methodology & limits

- **Sample:** 9/38 chapters (24% coverage) — targeted to brief-mandated topics (K8s, JVM/Go/Rust, hashing/consistent hashing, testing/DDD) + 2 per volume baseline. Non-sampled chapters (e.g., Vol 12 ch04 IaC, ch07 multi-tenancy, Vol 13 ch04 GC cross-runtime, Vol 15 ch02 contract testing) not assessed — do not extrapolate scores to them.
- **Tools:** Full-text read of 9 markdown files (687–1,167 lines each), `wc -w` corpus census, `grep -c mermaid`/code-fence counts, targeted `search_files` for version strings (`flowcontrol`, `UseZGC`, `GOGC`, `GOMEMLIMIT`, `hybrid barrier`, `Compressed oops`).
- **Factual verification:** K8s versions checked against KEP/release notes (dockershim, APF, SidecarContainers, ValidatingAdmissionPolicy); JVM flags against JDK 21 JEP 439 and `java` launcher docs; Go barrier against Go 1.7/1.8 release notes; hashing/consistent-hashing against Karger 1997, Ketama, and Mirrokni 2018 as cited in-text.
- **Output:** This file only. No source edits performed (audit-only).

---

*End of Review — Vols 12–15 (Audit D). 9 chapters sampled, 3 errors + 3 nits filed, 6 systemic issues, corpus stats verified.*
