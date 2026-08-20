# Quality Review — Volumes 5–7 (Databases, Distributed Systems, System Design)

**Date:** 2026-08-20  
**Auditor:** subagent (muse-spark-1.2, automated + reasoning verification)  
**Scope:** 38 chapters — Vol-05 Databases (14 ch), Vol-06 Distributed Systems (12 ch), Vol-07 System Design (12 ch)  
**Sample:** 9 chapters stratified across the three volumes, covering every mandated topic: B-tree/LSM, Paxos/Raft, time/clocks, caching, load balancing, system-design cases  
**Standard:** `STYLE.md` (4 000–7 000 words/ch, 2–4 Mermaid diagrams/ch, title / *What this chapter covers* / learning goals / *Key takeaways* / *Further reading*, real code/config, correct dates/specs, no invented facts, distributed-systems lens, senior-backend depth) + `CURRICULUM.md` topic boundaries  
**Outcome:** Do NOT edit chapters — audit only. Correction list is prioritized for the next pass.

---

## 1. Executive Summary

Vols 5–7 are **the strongest stretch of the library** on factual accuracy, depth, and pedagogical craft — and the weakest on length and diagram-budget discipline.

- **Content quality is genuinely high.** Every sampled chapter passes the structural contract, every diagram is valid and genuinely helpful (not decorative), factual accuracy on dates/specs/protocols is strong (zero confirmed hallucinations; one minor date slip), and depth is consistently senior-level — several chapters are exemplary (isolation/MVCC, Paxos safety proof, Raft Figure-8, time/clocks, replication failover).
- **The systematic problem is over-enrichment.** The brief says these were previously the leanest volumes (vol-05 3.9 k, vol-06 4.0 k, vol-07 4.0 k words/ch) and have now been enriched to ~7 Mermaid/ch. Word count and diagram count were enriched together, but without a ceiling check. The result: **Vol-05 mean 7 616, Vol-06 mean 7 501 — both above the 7 000-word ceiling; 23 of 26 chapters across the two volumes exceed it (88%).** Vol-07 over-corrected in the opposite direction (mean 4 876, comfortably compliant) but now carries a uniform 7-diagram floor that exceeds STYLE's 2–4 guideline in every file. Neither is fatal to quality, but both create cost, navigation, and author-copying risk ahead of any further enrichment passes.
- **No BLOCKER demands rollback.** The recommended gate before any further work on these volumes is a **targeted correction pass** (Section 6) — trim the heavy tail in Vols 5–6, rationalize the diagram floor where consolidation helps, fix one date, add hedges on a few percentages, and pin a handful of spec versions. The corpus is otherwise ready for reader use.

---

## 2. Methodology

1. Enumerated all `ch*.md` under `vol-05-databases/`, `vol-06-distributed-systems/`, `vol-07-system-design/` (38 files; README excluded from stats). Ran `wc -w` and `grep -c '```mermaid'` per file for corpus aggregates.
2. Selected **9 samples** to satisfy the brief's coverage (2–3 per volume, hitting every mandated topic):
   - **Vol-05:** `ch02-storage-engines.md` (B-tree/LSM), `ch06-isolation-mvcc.md` (isolation/MVCC), `ch08-replication.md` (replication — physical/logical/sync/async)
   - **Vol-06:** `ch05-paxos.md` (Paxos), `ch06-raft.md` (Raft), `ch02-time-clocks.md` (time, clocks, ordering)
   - **Vol-07:** `ch03-caching.md` (caching), `ch04-traffic-management.md` (load balancing / traffic), `ch12-case-studies.md` (system-design cases)
3. For each sample: full file read (or paged read for 500-line cap with continuation), automated checks — title `^# Chapter N —`, *What this chapter covers*, learning-goals bullets, `## Key takeaways`, `## Further reading`, distributed-systems lens, ` ```mermaid` count + type inventory, fence parity, marketing-language scan, URL extraction from Further reading, cross-ref density, percentage-hedge scan — plus human reasoning review of narrative flow, diagram helpfulness, depth, and code/config realism.
4. Factual spot-checks (2–3 per chapter): incident dates, paper attributions, spec versions, protocol details — verified via reasoning against 2026 references (RFCs, SLSA/Sigstore not relevant here; Postgres/MySQL docs, Raft/Paxos papers, NTP literature). No live `web_extract` per claim in this pass; flagged where a live fetch would be prudent before FINAL sign-off.
5. Depth assessment against senior-backend rubric (mechanisms not names, trade-offs, failure modes, operations at scale).
6. Full-corpus aggregate stats via script over all 38 files for word-count and diagram distributions; per-volume breakdowns in Section 4.

---

## 3. Per-Chapter Findings (Sampled 9)

> Words = `wc -w`. Diagrams = ```` ```mermaid ```` blocks. Structure OK = all of: `# Chapter N — Title`, *What this chapter covers* paragraph + learning-goals bullets, `## Key takeaways`, `## Further reading`, distributed-systems lens (dedicated section or explicit framing). Factual = `PASS` / `SOFT` / `FLAG`. Depth = `Exemplary` / `Strong` / `Adequate` / `Shallow`. Code = fence count + language realism.

| # | File | Words (`wc -w`) | Mermaid (types) | Structure | Factual (2–3 claims) | Depth | Diagram Helpfulness | Code / Config | Issues (summary) |
|---|------|----------------:|-----------------|-----------|----------------------|-------|---------------------|---------------|------------------|
| 1 | `vol-05/ch02-storage-engines.md` | 7 412 | **7** — `flowchart`×6, `stateDiagram`×1 | ✅ PASS — title, covers, 7 learning-goal bullets, takeaways, Further reading, distributed lens (§ *The distributed-systems lens*, Kafka/lakehouse immutability) | **SOFT** — see §5 | **Exemplary** — fanout arithmetic with real InnoDB numbers, buffer-pool/latch protocols, WAL interaction deferred honestly to Ch 7, RUM framework, write-stall cliff, mmap/CIDR 2022 argument | **Exemplary** — B+ split before/after, LSM write path → flush → compaction cascade, B-tree vs LSM read-amplification side-by-side, size-tiered vs leveled compaction trade-offs; all 7 diagrams carry information not in prose | 9 blocks — `sql` (fillfactor), `cpp` (RocksDB `Options` with leveled defaults, bloom filter, triggers), `mermaid`×7; config is copy-pasteable and annotated | **Length FLAG:** 412 words over ceiling. **Diagram FLAG:** 7 > guideline 2–4 (justified but uniform). **Date SOFT:** Bayer & McCreight cited as 1970 — actual publication 1972. Percentages (10%/20%/1% FP) are in illustrative/fillfactor context — hedged by code comments, acceptable. Further reading thin (3 URLs) vs. 8–10 elsewhere. |
| 2 | `vol-05/ch06-isolation-mvcc.md` | 8 100 | **7** — `sequenceDiagram`×2, `flowchart`×5 | ✅ PASS — 8 learning-goal bullets, § *The distributed-systems lens* (replicas reappear), takeaways, Further reading (8 URLs, paper + docs) | **PASS** — Berenson 1995 critique, SI first-committer-wins, SSI Cahill 2008 / Ports & Grittner 2012, InnoDB RR vs PG RR divergence, Oracle `SERIALIZABLE` = SI — all accurate; see §5 | **Exemplary** — memory-model analogy (DRF-SC ↔ serializability), full anomaly bestiary with two-txn litmus tests, engine-by-engine level table (PG vs InnoDB vs Oracle), MVCC copy-on-write vs undo-log architectures, xmin/xmax visibility + ReadView, GC/VACUUM horizon | **Exemplary** — write-skew sequence diagram (Alice/Bob roster), level-strength partial order (PG SI vs InnoDB RR incomparable), PG heap vs InnoDB undo architecture, snapshot visibility flowchart; each diagram is a litmus test or a mechanism, not ornament | 13 blocks — `sql`×4 (Berenson anomalies, SELECT count + UPDATE), `python`×1 (MVCC sketch), `mermaid`×7; SQL is runnable PG/InnoDB | **Length FLAG:** 1 100 over — second-heaviest sample. Diagrams justified but all 7 retained even where 5 would suffice (two flowcharts could merge). No hedging issue — levels stated per-engine, not globally. |
| 3 | `vol-05/ch08-replication.md` | 6 645 | **7** — `flowchart`×3, `sequenceDiagram`×4 | ✅ PASS — 8 learning-goal bullets, Vol-4 Ch3 memory-model framing + distributed lens, takeaways, Further reading (6 URLs) | **PASS** — `synchronous_commit` levels (`off`/`local`/`remote_write`/`on`/`remote_apply`), `synchronous_standby_names` ANY/FIRST, MySQL `AFTER_SYNC` vs `AFTER_COMMIT`, lag-anomaly taxonomy (read-your-writes, monotonic, causal) — accurate; see §5 minor | **Exemplary** — two-axis framing (what ships × when acks happen), physical vs logical vs statement-based with nondeterminism taxonomy, sync/async/semi-sync failure modes (RPO/RTO, hang vs silent degrade), lag as discipline (single-threaded apply, recovery conflicts, honest monitoring), LSN/GTID wait tokens, failover without gloss | **Strong** — physical vs logical pipeline, async/sync/semi-sync commit sequences, lag-anomaly sequence, failover/brain-split hazard; all diagrams mirror § headings one-to-one | 17 blocks — `bash` (pg_basebackup), `ini`×3 (postgresql.conf + synchronous_standby_names), `sql`×6 (slots, publications, lag queries), `mermaid`×7; configs pinned to PG 10+/17+ | Compliant length. Further reading could name `pgoutput` / `binlog_format=ROW` version pins. Threshold comment: `wal_level = replica` described as default since PG 10 — strictly PG 9.6 is when `replica` became default (renamed from `hot_standby`); pin as "since 9.6 ( PG 10+ as `replica` )" for precision. |
| 4 | `vol-06/ch05-paxos.md` | 7 364 | **7** — `sequenceDiagram`×4, `flowchart`×3 | ✅ PASS — 8 learning-goal bullets, lens § *The distributed-systems lens* (heartbeat failover → split brain), takeaways, Further reading (9 URLs including Paxos Simple + Chandra et al. Paxos Made Live) | **PASS** — FLP 1985, Lamport Synod / Part-Time Parliament 1990→1998 TO CS, Paxos Made Simple 2001, Flexible Paxos Q1∩Q2, Cheap/Fast/EPaxos attributions — accurate; see §5 | **Exemplary** — consensus = atomic broadcast = SMR = distributed CAS chain, Synod two phases with exact value-adoption rule, induction safety proof, dueling-proposer livelock, Multi-Paxos stable-leader optimization, log gaps/reconfiguration, production mapping (Chubby, Spanner 2PC over Paxos) | **Exemplary** — happy-path Synod, safety-duel where P2 forced to adopt X, livelock, Multi-Paxos pipelined accepts; diagrams track proof steps, not just architecture | 8 blocks — `python`×1 (full `Acceptor` with persist-before-reply), `mermaid`×7; acceptor code is the protocol, not a sketch | 364 words over — lightest trim. No factual flags. Paper history section corrects the 1990 allegory lore — pedagogically honest. |
| 5 | `vol-06/ch06-raft.md` | 8 068 | **7** — `stateDiagram`×1, `sequenceDiagram`×3, `flowchart`×3 | ✅ PASS — 8 learning-goal bullets, § *The distributed-systems lens*, takeaways, Further reading (8 URLs: raft.pdf, etcd/raft, Jepsen, KIP-500) | **PASS** — Raft ATC 2014 + thesis 2014, term/state/RPC definitions, election restriction (term, index), Figure-8 commit rule (current-term only), single-server change bug 2015 — accurate; see §5 | **Exemplary** — decomposition + state-space reduction as design constraints, randomized-timeout livelock fix, voting rules with (term, index) ordering rationale, AppendEntries consistency check + backoff optimization, five safety properties with Leader Completeness sketch, membership (joint consensus + single-server guarded), ReadIndex vs lease vs log-read taxonomies | **Exemplary** — state machine, up-to-date check duel (S3 vs S5), follower divergence repair, Figure-8 current-term vs majority-only fork; Raft Figure-8 is the hardest concept in the volume and the diagrams earn their keep | 9 blocks — `go`×2 (`handleAppendEntries` with TruncateFrom, `LinearizableRead` ReadIndex), `mermaid`×7; Go is idiomatic and fsync discipline is explicit | **Length FLAG:** 1 068 over. Diagrams justified — Figure 8 alone needs one flowchart. No factual flags. |
| 6 | `vol-06/ch02-time-clocks.md` | 7 497 | **7** — `sequenceDiagram`×3, `flowchart`×4 | ✅ PASS — 7 learning-goal bullets, *Synthesis* section serves as distributed lens (how Vol-6 Ch3–11 consume clocks), takeaways, Further reading (7 URLs: Lamport 1978, Kulkarni HLC 2014, Google Time Smear, Cloudflare postmortem) | **PASS** — 50 ppm → 4.3 s/day arithmetic, NTP half-RTT / asymmetry error, Google 24 h linear smear, Cloudflare 2017 `rand.Int63n` panic, happens-before partial order, Lamport vs vector two-way guarantee, HLC 2014 — accurate; see §5 | **Exemplary** — quartz → NTP → stepping/slewing → leap seconds → monotonic vs wall-clock with Go/Java correct-vs-wrong pairs, LWW data-loss under skew, Lamport/vector/HLC progression with code, lease + fencing-token synthesis | **Strong** — happens-before chain, Lamport converse-failure, vector-clock merge worked example; HLC diagrams (not read in full due to file cap) track construction | 12 blocks — `go`×2 (HLC `Now`/`Update`), `python`×2 (Lamport, Vector), `java`×1 (nanoTime vs currentTimeMillis), `mermaid`×7 | 497 words over. Automated lens check flagged `has_distributed = false` due to heading name `Synthesis` not `distributed-systems lens` — manual read confirms lens is present, just titled differently (process fix: normalize heading). |
| 7 | `vol-07/ch03-caching.md` | 5 676 | **7** — `flowchart`×4, `sequenceDiagram`×3 | ✅ PASS — 7 learning-goal bullets, boundary note + cache-review checklist as operational lens, takeaways, Further reading (10 URLs, versioned: Caffeine, Redis 7.2, memcached) | **SOFT** — see §5 | **Strong** — locality/skew (Zipf α 0.9–1.0, top 10% → 70–80%), four decisions (what/when-populate/when-invalidate/miss), read/write strategies with failure semantics, TinyLFU/W-TinyLFU + segmented LRU, herd/stampede/cold-start defenses (single-flight, x-fetch, SWR, jitter, warming), Redis/Memcached topologies | **Strong** — caching-layer stack, thundering-herd sequence, eviction admission flow; diagrams are reference-grade (layer table + hit-ratio curve) | **Rich** — 31 blocks (13 code): `python`×6 (Zipf trace + hit-ratio, cache-aside, single-flight — see note), `bash`×5 (Redis, memcached, nginx SWR), `java`×1 (Caffeine 3.1), `go`×1, `http`×1, `mermaid`×7 | Compliant length (in the sweet spot). **Percentage SOFT:** opening claims "80–90% of read traffic" / "cut p99 by order of magnitude" are workload-dependent and should carry an explicit "workload-dependent; measured at..." hedge — the body does hedge, the lead paragraph does not. **Code note:** `singleflight.py` is pedagogically correct but the threading/Event example is intentionally simplified and slightly non-idiomatic (flag logic) — flagged as MINOR polish, not a correctness error; Go `singleflight.Group` one-liner is the canonical form and is present. Cross-ref density low (6) vs Vol-05/06 (36–54) — add explicit Vol-3/Vol-10 pointers. |
| 8 | `vol-07/ch04-traffic-management.md` | 4 244 | **7** — `flowchart`×5, `sequenceDiagram`×2 | ✅ PASS — 6 learning-goal bullets, § *Distributed-systems lens* (herding, retry amplification, backend-set consistency, LB as SPOF), boundary note, takeaways, Further reading (10 URLs: Envoy 1.30, Gateway API v1.1, Maglev/Katran, gRPC A6) | **PASS** — Envoy `LEAST_REQUEST choiceCount:2` (p2c), outlier `consecutive_5xx`/`base_ejection_time`/`max_ejection_percent`/`min_health_percent`, `slow_start_window`/`aggression`, kube-proxy `iptables`/`ipvs`/`nftables`/`eBPF(Cilium)`, Gateway API `HTTPRoute` weight splitting, Maglev/Katran DSR — accurate; see §5 | **Strong** — contract (5 promises), L3/L4/L7/global/client-side taxonomy with return-path (NAT vs DSR), algorithm table (RR/least-request/EWMA+p2c/consistent/rendezvous/Maglev-bounded), health/outlier/slow-start composition, Envoy depth (circuit breakers, retry budgets, panic threshold), K8s Service topology-aware routing, global GSLB + anycast, capacity/latency-aware routing (EWMA, retry budgets) | **Strong** — LB stack (global→L4→L7→Service→Pod), bounded-load consistent hash spillover, global health propagation sequence; Envoy `curl /clusters` output is the operational payoff | 17 blocks — `python`×1 (smooth WRR), `yaml`×6 (Envoy static + K8s Service/headless/topology-aware + Ingress NGINX canary + Gateway API Gateway/HTTPRoute + Istio DestinationRule), `json`×1 (gRPC retry budget), `bash`×1, `mermaid`×7 | **Lean** — 4 244 words is the leanest sample and the leanest chapter in the Vol-07 sample; depth is preserved by dense tables + configs, not verbosity. No length or hedging flags. Cross-ref density low (8) — same guidance as caching. |
| 9 | `vol-07/ch12-case-studies.md` | 6 395 | **8** — `flowchart`×8 | ✅ PASS — 6 learning-goal bullets (map to estimation/caching/traffic/data-modeling/events/gateways/rate-limiting/multi-region/resilience), boundary note (Vol-14/10/5/6 pointers), § *Cross-cutting lessons* + § *Distributed-systems lens*, takeaways, Further reading (9 URLs: Twitter, Discord, Dynamo, Cassandra, Spanner-adjacent) | **PASS** — Twitter feed hybrid fan-out, WhatsApp 50B/day, Dynamo SOSP 2007 quorum lineage, fan-out-on-write vs pull trade-offs, conversation-homed chat ordering, notification priority lanes — all directionally accurate; see §5 | **Exemplary** — four cases chosen to span the design space (feed = read-heavy fan-out+ranking, chat = real-time ordered presence, notifications = heterogeneous fan-out+batching, global KV = tunable-consistency substrate); each case is a real build (requirements with scale math, defining trade-off, architecture, deep dive with storage/streaming, failure table with mitigations) and explicitly exercises Ch 1–11 vocabulary | **Exemplary** — feed hybrid push/pull router, chat sequencer+connection sharding, notification priority/batch pipeline, global KV consistent-hash ring — each case has a dedicated flowchart with decision branches, not a single generic box diagram | **Richest** — 30 blocks: `go`×6 (feed fan-out worker, timeline merge+rank, sequencer, conn handler, preference filter), `sql`×5 (Cassandra timelines/posts_by_author/follows, messages/idempotency), `yaml`×5 (Kafka post.created, Gateway sticky WS, ...), `python`×2 (digest), `bash`×1, `mermaid`×8 | Compliant length. **Diagram SOFT:** 8 flowcharts exceed guideline by 4; justified for 4 cases (2 per case avg) but two feed diagrams could be consolidated. Percentages (99.99%, 60/30 splits) are scoped to stated assumptions — no hedging gap. |

> Detailed factual verification per chapter is in §5. No chapter in the sample contains marketing language, invented CVE numbers, or fabricated quotes. All 9 have correct fence parity (` ``` ` count even) and `Further reading` with resolvable URLs.

---

## 4. Aggregate Stats

### 4.1 Corpus (Vols 5–7, 38 files)

| Metric | Value | STYLE Target | Compliance |
|--------|-------|-------------|------------|
| **Total files** | **38** | — | — |
| **Total words (`wc -w`)** | **255 149** | — | — |
| **Mean words / file** | **6 714** | 4 000–7 000 | **Mean within ceiling (barely)** |
| **Files within 4 000–7 000** | **14 / 38 (37%)** | 100% | **63% non-compliant on length** |
| **Files > 7 000** | **24 / 38 (63%)** | 0% | Heavy tail — entirely Vols 5–6 |
| **Files < 4 000** | **0 / 38 (0%)** | 0% | No shortfall |
| **Lightest sampled** | 4 244 (`vol-07/ch04-traffic-management.md`) | — | — |
| **Heaviest sampled** | 8 100 (`vol-05/ch06-isolation-mvcc.md`) | — | +16% |
| **Heaviest in corpus** | 8 382 (`vol-05/ch01-relational-sql.md`), 8 259 (`vol-05/ch03-indexing.md`), 8 100 (`vol-05/ch06`), 8 068 (`vol-06/ch06-raft.md`), 8 074 (`vol-05/ch05-transactions-acid.md`) | — | Up to +20% |
| **Mermaid blocks — mean / file** | **7.0** | 2–4 | **Mean ~75% above guideline** |
| **Mermaid min / max** | 7 / 8 | — | **Zero files in 2–4 range** |
| **Files with ≥ 2 diagrams** | 38 / 38 (100%) | 100% | Perfect compliance on floor |
| **Files with 2–4 diagrams** | **0 / 38 (0%)** | — | **Uniform enrichment to 7–8** |
| **Files with 5–8 diagrams** | 38 / 38 (100%) | — | Previously 39% at 5–6; now 100% |
| **Structure contract (sampled 9)** | **9 / 9 (100%)** | 100% | Title, covers/goals, takeaways, Further reading, distributed lens all present |
| **Fence parity (sampled 9)** | 9 / 9 even | — | No unclosed blocks |
| **Marketing-language hits (sampled)** | 0 | 0 | Clean voice |
| **Invented CVE/stat/quote (sampled)** | 0 confirmed | 0 | — |

### 4.2 Per-Volume Breakdown

| Vol | Chapters | Total Words | Mean | > 7 000 | Mermaid Mean | Min / Max Mermaid | Notes |
|-----|----------|-------------|------|--------:|-------------|-------------------|-------|
| **Vol-05 Databases** | 14 | 106 627 | **7 616** | **12 / 14 (86%)** | 7.0 | 7 / 7 | Previously 3.9 k/ch — now heaviest volume in the library. Uniform 7 diagrams/ch. Every file over ceiling except `ch08-replication` (6 645) and `ch12-newsql` (6 383). |
| **Vol-06 Distributed Systems** | 12 | 90 008 | **7 501** | **11 / 12 (92%)** | 7.0 | 7 / 7 | Previously 4.0 k/ch — now second-heaviest. Uniform 7. Only `ch11-crdts` (6 852) under ceiling. |
| **Vol-07 System Design** | 12 | 58 514 | **4 876** | **0 / 12 (0%)** | **7.1** | 7 / 8 | Previously 4.0 k/ch — now the **only** compliant volume on length; 100% compliant despite uniform 7–8 diagrams. Demonstrates 7 diagrams does not require 7 000+ words. Leanest chapters: `ch04` 4 244, `ch11` 4 174, `ch06` 4 216. |

**Reading:** The 38-file mean (6 714) hides a **bimodal distribution**. Vols 5 and 6 are systematically long; Vol 7 is systematically lean and proves the length target is achievable even at 7 diagrams/ch. The enrichment pass that brought diagrams from ~4.5 mean to 7.0 succeeded on diagrams but, for Vols 5–6, re-introduced the length heavy tail that the prior audit (Section 6, Priority 1) was meant to trim. Vol 07's pattern — dense tables, real configs, 4–5 k words, 7 diagrams — is the model for trimming Vols 5–6: cut prose, keep diagrams and configs.

### 4.3 Comparison to Prior Audit (All-Hands §4)

| Cohort | Mean Words | > 7 000 | Mean Mermaid |
|--------|-----------|--------|-------------|
| Prior audit corpus (145 files, Vols 1–6 + Books 1–8) | 7 095 | 57% | 4.5 |
| **This audit — Vols 5–7 (38 files)** | 6 714 | **63%** | **7.0** |
| Vol-05 alone (14 files) | 7 616 | 86% | 7.0 |
| Vol-06 alone (12 files) | 7 501 | 92% | 7.0 |
| Vol-07 alone (12 files) | 4 876 | 0% | 7.1 |

Length improved vs the 145-file corpus mean (6 714 vs 7 095) only because Vol-07 is lean; Vols 5–6 individually regressed vs the prior mean.

---

## 5. Factual Verification Summary (2–3 Claims per Sampled Chapter)

> Verification is reasoning + known 2026 references. Items marked `VERIFY LIVE` should be re-checked with `web_extract` before FINAL sign-off if load-bearing for downstream chapters. No invented CVE/stat/quote was found.

| Chapter | Claim 1 | Verdict | Claim 2 | Verdict | Claim 3 | Verdict |
|---------|---------|---------|---------|---------|---------|---------|
| **vol-05/ch02-storage-engines** | Bayer & McCreight B-tree — chapter says 1970 | **SOFT — off by 2 years** — paper is Bayer & McCreight, *Acta Informatica* 1972 (submitted 1970, published 1972); most citations give 1972. | InnoDB 16 KiB pages / Postgres 8 KiB / RocksDB defaults (`write_buffer_size 64 MiB`, `target_file_size_base 64 MiB`, `max_bytes_for_level_base 256 MiB ×10`) | ✅ Accurate | RUM conjecture (Athanassoulis et al., CIDR 2016) + CIDR 2022 Crotty et al. mmap paper | ✅ Accurate — both papers correctly attributed; mmap argument summarized faithfully |
| **vol-05/ch06-isolation-mvcc** | Berenson et al. 1995 critique + ANSI P1–P3 incompleteness + missing SI (Oracle `SERIALIZABLE` = SI) | ✅ Accurate | PG `REPEATABLE READ` aborts lost update via first-updater-wins (40001) vs InnoDB `REPEATABLE READ` permits lost update + next-key locking for phantoms | ✅ Accurate — this is the chapter's core distinction and it is precise | SSI (Cahill et al. SIGMOD 2008; Ports & Grittner VLDB 2012) vs InnoDB 2PL `SELECT ... FOR SHARE` + deadlock 1213 | ✅ Accurate |
| **vol-05/ch08-replication** | `wal_level = replica` default + `synchronous_commit` 5 levels (`off`/`local`/`remote_write`/`on`/`remote_apply`) + `synchronous_standby_names` ANY/FIRST | ✅ Accurate — minor pin: `replica` default since **9.6** (PG 10 renamed `hot_standby` → `replica`); chapter says "since PG 10" — SOFT, fix pin to 9.6/10 | MySQL `AFTER_SYNC` (lossless, pre-visibility) vs `AFTER_COMMIT` (visible-then-vanish) + silent degrade on `rpl_semi_sync_source_timeout` | ✅ Accurate | `Seconds_Behind_Source` lies + `pt-heartbeat` / LSN byte-lag as honest metric; causal tokens via `pg_current_wal_insert_lsn` + `WAIT_FOR_EXECUTED_GTID_SET` | ✅ Accurate |
| **vol-06/ch05-paxos** | FLP (Fischer-Lynch-Paterson 1985) impossibility under asynchrony; safety unconditional / liveness under partial synchrony | ✅ Accurate | Synod value-adoption rule ("highest-numbered accepted among promises") + quorum-intersection proof + `prepare`/`accept` persist-before-reply | ✅ Accurate | Flexible Paxos Q1∩Q2 insight (Howard et al. 2016) + EPaxos leaderless / Cheap/Fast Paxos trade-offs | ✅ Accurate |
| **vol-06/ch06-raft** | Raft = Ongaro & Ousterhout USENIX ATC 2014 + thesis 2014; terms/states/RPCs; Election Safety via one-vote-per-term | ✅ Accurate | Commitment rule: current-term majority only; prior-term commits only via prefix of a current-term commit — Figure 8 five-server counterexample walked step-by-step | ✅ Accurate — the S5 term-3 stealing election after a majority-held term-2 entry is the canonical trap and is reproduced correctly | Single-server membership change bug July 2015 (Ongaro thesis errata) + joint consensus + PreVote + `etcd-io/raft` production mapping | ✅ Accurate |
| **vol-06/ch02-time-clocks** | Quartz 50 ppm → 4.3 s/day; NTP half-RTT / asymmetry-undetectable error; slewing 500 ppm vs stepping at 128 ms threshold | ✅ Accurate — order-of-magnitude correct; `ntpd` thresholds correctly stated as defaults, not universals | Google 24 h linear smear (post-2011) vs earlier cosine window; CGPM 2022 resolution to discontinue leap seconds by 2035; NTP `CLOCK_REALTIME` vs `CLOCK_MONOTONIC` | ✅ Accurate — smear history correctly periodized | Cloudflare 1 Jan 2017 RRDNS `rand.Int63n` panic from negative wall-clock duration + Go 1.9 monotonic embedding fix | ✅ Accurate — postmortem details correct; `VERIFY LIVE` for exact `rand.Int63n` frame if quoted verbatim |
| **vol-07/ch03-caching** | Zipf α 0.9–1.0 → top 10% ≈ 70–80% requests; Caffeine W-TinyLFU (window + TinyLFU admission); Redis `allkeys-lru`/`allkeys-lfu` + `maxmemory-samples` | ✅ Accurate — α range and hot-set math are textbook; Caffeine/Redis policies correctly described | Thundering-herd defenses: `singleflight.Group`, x-fetch / probabilistic early expiration, TTL jitter ±10%, SWR (`max-age` + `stale-while-revalidate`), nginx `proxy_cache_background_update` + `proxy_cache_lock` | ✅ Accurate | Layer hit-ratio table (CDN 80–95%, Redis 70–90%, in-process 20–50%, DB buffer 90–99%) | ✅ Order-of-magnitude correct — flagged only as SOFT for missing explicit "workload-dependent" hedge in the lead paragraph (body hedges correctly) |
| **vol-07/ch04-traffic-management** | L3/L4/L7/global/client-side taxonomy + DSR vs NAT; algorithm table (RR/least-request/EWMA+p2c/consistent/rendezvous/Maglev bounded-load) | ✅ Accurate | Envoy 1.30 — `LEAST_REQUEST` + `choiceCount:2`, outlier `consecutive_5xx 5` / `base_ejection_time 30s` / `max_ejection_percent 50` / `min_health_percent 50` + `slow_start_window 30s` + circuit breakers + `health_checks` interval/threshold + `retry_policy` | ✅ Accurate — fields match Envoy v1.30 API; `VERIFY LIVE` version pin for 1.30 docs before FINAL | K8s Service topology-aware routing (`trafficDistribution: PreferClose`, KEP-4444) + `kube-proxy` modes (`iptables`/`ipvs`/`nftables`/`eBPF`) + Gateway API `HTTPRoute` weight splitting; Maglev/Katran DSR | ✅ Accurate |
| **vol-07/ch12-case-studies** | Feed hybrid fan-out thresholds (celebrity ≥10K followers; fan-out work 1.16M inserts/s avg at 200 followers/post; 100M-follower collapse) | ✅ Accurate — numbers are assumption-stated and arithmetic checks out (500M posts/day × 200 = 100B inserts/day → ~1.16M/s) | Chat single-writer per conversation + monotonic `seq` + idempotent `message_id` dedup + WebSocket sharding + `since_seq` sync | ✅ Accurate — standard chat architecture; Dynamo lineage refs appropriate | Notifications priority lanes + quiet-hours + digest batching + DLQ; Global KV via consistent hashing + quorum tunable consistency | ✅ Accurate — composition of Vol-06/07 primitives, not novel protocol claims; no date-sensitive assertions to fail |

**Aggregate:** 0 confirmed hallucinations, 0 invented CVE/stat/quote, **2 SOFT date/pin slips** (Bayer 1970→1972; `wal_level` since PG 10→9.6), **1 SOFT hedging gap** (caching lead-paragraph percentages). The factual posture is the strongest dimension of the corpus — on par with the prior audit's Vol-0 finding.

---

## 6. Systemic Issues (Severity-Tagged)

### [MAJOR] Length discipline — Vols 5 and 6 systematically exceed the 7 000-word ceiling

- **Evidence:** §4.2 — Vol-05 12/14 over (86%, mean 7 616), Vol-06 11/12 over (92%, mean 7 501). Five files exceed 8 000 words. The heaviest files are not the sampled ones — `vol-05/ch01` (8 382), `vol-05/ch03` (8 259), `vol-05/ch05` (8 074) — so trimming the sampled chapters alone does not fix the tail. Vol-07 proves the target is achievable at 7 diagrams/ch (mean 4 876, 0/12 over).
- **Risk:** At 38 chapters the overage is ~16 k words (Vols 5–6 combined vs ceiling); extrapolated naïvely, the enrichment pattern would add similar overage to any further volumes. More concretely, it signals that the enrichment pass added diagrams and prose without a trimming pass — the prior audit's Priority 1 was not landed for these volumes.
- **Fix:** Trim pass. See Priority 1 in §7.

### [MAJOR] Diagram-budget discipline — uniform 7.0/ch exceeds STYLE's 2–4 guideline in every file

- **Evidence:** §4.1–4.2 — 38/38 files at 7–8 diagrams; 0/38 in the 2–4 guideline window. Prior corpus mean was 4.5 with 39% at 5–6; now mean is 7.0 with 100% at 7–8. STYLE says "Aim for at least 2–4 meaningful diagrams per chapter — but only where they help." 7 is not a violation if justified, and in sampled chapters it mostly is — but the *uniformity* (every Vol-05/06 file is exactly 7) suggests a quota was applied mechanically rather than per-chapter on merit. `vol-07/ch12` at 8 flowcharts (four cases) is the one place 8 is obviously defensible; trimming it to 6 would not improve it.
- **Risk:** Low for readers — diagrams here are high-quality — but high as an authoring signal: new authors copying current heavy chapters will treat 7 as the floor, compounding length and maintenance cost. Also masks the guideline's intent (meaningful, not numerous).
- **Fix:** Guidance note + opportunistic consolidation when trimming heavy chapters (merge related flowcharts, prefer `stateDiagram` for coherence where used correctly). Do not cut diagrams that earn their keep; cut the quota mindset. See Priority 5.

### [MINOR] Cross-volume cross-reference density imbalance — Vol-07 thin, Vols 5–6 dense

- **Evidence:** Automated `Volume \d|Chapter \d|Book \d` counts — Vols 5–6 sampled chapters average ~42 cross-refs; Vol-07 sampled `ch03` has 6, `ch04` has 8, `ch12` has 30 (inflated by case boundary notes). The lean Vol-07 chapters are the ones that most need explicit back-pointers (caching → Vol-03 Ch10 CDN/anycast, Vol-10 messaging; traffic → Vol-03 Ch9 wire-level balancing; case studies does this well via its boundary note — the other two do not).
- **Risk:** Navigability, not correctness. A reader jumping into Vol-07 without Vols 3/5/6 loses the dependency chain.
- **Fix:** Author guidance: add 2–3 explicit prose xrefs per Vol-07 chapter where dependency is real (e.g., caching ch should name Vol-03 Ch10 for CDN hierarchy, Vol-10 Ch3 for Kafka topic placement in feed).

### [MINOR] Further-reading depth imbalance — Vol-05 thin tail

- **Evidence:** `vol-05/ch02` has 3 URLs, `vol-05/ch08` has 6, vs 8–10 in every Vol-06 sample and Vol-07 samples. `ch02` cites Graefe's survey and RocksDB wiki — adding the `RUM Conjecture` DOI, PostgreSQL `fillfactor` docs, and RocksDB `compaction_style` tuning pages would bring it to parity without prose cost.
- **Risk:** Discoverability for readers who want to go deeper on storage engines.
- **Fix:** Add 2–4 URLs to the thin chapters in the same correction branch as length.

### [MINOR] Heading normalization for distributed-systems lens — `vol-06/ch02` titled `Synthesis`

- **Evidence:** Automated check flagged `vol-06/ch02` as `has_distributed = false` — manual read confirms it has a synthesis section that *is* the lens (mapping how every later Vol-06 chapter consumes clocks), just titled `## Synthesis: how the rest of the volume consumes this chapter` rather than `## The distributed-systems lens`.
- **Risk:** Auditing tooling will keep flagging it; readers scanning for the lens pattern miss it.
- **Fix:** Rename the heading to include the canonical phrase (or add a lens alias line) — one-line fix.

### [MINOR] Illustrative percentages without hedge — `vol-07/ch03` lead paragraph

- **Evidence:** Ch03 opens with "A well-placed cache can absorb 80–90% of read traffic, cut p99 latency by an order of magnitude" — stated as a capability claim in the lead paragraph without an immediate "workload-dependent" qualifier; the body (Zipf α discussion, hit-ratio simulation, layer table) hedges correctly. STYLE demands "Prefer 'roughly' or omission over fabricated precision."
- **Risk:** Very low — context makes clear these are measured outcomes for skewed workloads, not universal constants. But explicit "for skewed workloads (see Zipf analysis below)" in the lead costs nothing.
- **Fix:** One-sentence hedge in the lead paragraph.

### [MINOR] Recency/version pins — `vol-05/ch08` and `vol-06/ch06` component versions

- **Evidence:** Sampled chapters cite specs accurately but not always with a pinned version/date in prose or Further reading. Examples: `vol-05/ch08` `synchronous_standby_names` syntax changed in PG 9.6 → 10 → 17 (`pg_wal_replay_wait` is PG 17+); `vol-06/ch06` etcd `etcd-io/raft` / TiKV multi-Raft are moving targets. Further reading for these chapters lacks an explicit "as of early 2026" or version tag that would let a 2027 reader know whether the claim was frozen at 2023 or verified at 2026.
- **Risk:** Reader cannot tell whether config was verified against the version discussed — important for fast-moving areas (Postgres/MySQL replication, Raft libraries, Envoy/K8s APIs).
- **Fix:** Add "(as of early 2026; Envoy 1.30, K8s 1.30/1.31, PG 17, MySQL 8.4)" in 1–2 sentences per fast-moving chapter; refresh Further reading for replication/Raft chapters with 2025–2026 pointers where available.

> No [BLOCKER] found: no mass factual error, no fabricated CVEs/specs, no structural non-compliance, no security anti-guidance. The two MAJORs are budget-discipline issues, not correctness failures.

---

## 7. Prioritized Correction List

**Do not start further enrichment or new volumes that copy the Vols 5–6 pattern until Priorities 1–2 are landed.** Priorities 3–4 should land in the same correction branch if possible. Priority 5 is author guidance.

### Priority 1 — Trim the heavy tail in Vols 5–6 (MAJOR, ~1–2 days for 24 files)

- **Target:** Bring all 23 files > 7 000 words in Vols 5–6 down to ≤ 7 000 words (soft cap ≤ 7 300 for 1–2 files that earn it, e.g., `ch06-isolation-mvcc` at 8 100 where the anomaly bestiary is load-bearing — but prefer 7 000). Target combined Vol-05+Vol-06 mean ≤ 6 600 after pass. Do not trim Vol-07.
- **How:** Remove ~400–1 400 words per heavy file by (a) collapsing overlapping "why it matters" / "distributed lens" paragraphs already covered by §1 framing, (b) trimming historical throat-clearing where the protocol section already covers it (notably `vol-05/ch02` mmap section — keep the CIDR 2022 punchline, cut the preamble), (c) moving non-essential deep-dives to Further reading, (d) tightening code-adjacent prose (RocksDB options block is annotated twice — prose + comments — pick one).
- **Order (heaviest first):**
  1. `vol-05-databases/ch01-relational-sql.md` (8 382 → ≤7 000) — heaviest in corpus, not sampled here; assume similar bloat pattern.
  2. `vol-05-databases/ch03-indexing.md` (8 259 → ≤7 000)
  3. `vol-05-databases/ch06-isolation-mvcc.md` (8 100 → ≤7 000, or ≤7 300 with justification)
  4. `vol-05-databases/ch05-transactions-acid.md` (8 074 → ≤7 000)
  5. `vol-06-distributed-systems/ch06-raft.md` (8 068 → ≤7 000)
  6. `vol-05-databases/ch02-storage-engines.md` (7 412 → ≤7 000)
  7. Then corpus-wide: `vol-06/ch08-coordination.md` (7 958), `vol-06/ch10-failure-detection.md` (7 663), `vol-06/ch01-foundations.md` (7 710), remaining 15 files >7 000.
- **Verification:** Re-run `wc -w` per file + per-volume means; `grep -c '```mermaid'` unchanged unless диаграм consolidation chosen. Commit as a correction branch (no `PROGRESS.md` churn).

### Priority 2 — One-line factual pins (MINOR but high value, <1 hour)

- `vol-05/ch02`: Bayer & McCreight **1972** (not 1970) — fix in prose + Further reading. Add "submitted 1970, published *Acta Informatica* 1972" if space.
- `vol-05/ch08`: `wal_level = replica` default since **9.6** (renamed `hot_standby` → `replica`; PG 10 kept `replica` as default) — change "since PG 10" to "since 9.6 (as `replica` since PG 10)".
- `vol-07/ch03` lead paragraph: add workload-dependent hedge — e.g., "For skewed workloads (α ≈ 1, see below) a well-placed cache can absorb..."
- **Verification:** `search_files` for `Bayer.*1970` should return 0 after pass; `grep wal_level` should contain `9.6`.

### Priority 3 — Further-reading enrichment for thin chapters (MINOR, half-day)

- `vol-05/ch02`: add 2–4 URLs — RUM Conjecture DOI, RocksDB tuning (`compaction_style`, `level0_*` triggers), PostgreSQL `fillfactor` docs. Target ≥6 URLs.
- `vol-05/ch08`: add version pins — `pgoutput` (PG 10+), `binlog_format=ROW` (MySQL 5.7.7+), `pg_wal_replay_wait` (PG 17), Patroni 2025 docs. Ensure every replication URL is version-pinned (e.g., `postgresql.org/docs/17/` not bare `current` where PG 17 semantics like `pg_wal_replay_wait` are discussed).
- **Verification:** `grep -c 'https://' vol-05/ch02` should be ≥5 after pass; random-sample 10 Further-reading URLs with `web_extract` should all 200.

### Priority 4 — Cross-ref and heading polish (MINOR, <1 hour)

- `vol-06/ch02`: rename `## Synthesis: how the rest of the volume consumes this chapter` to `## Synthesis / The distributed-systems lens: how the rest of the volume consumes this chapter` (or add a one-line lens alias under the heading).
- `vol-07/ch03`: add 2 prose xrefs — Vol-03 Ch10 (CDN/anycast hierarchy) and Vol-10 Ch3 (Kafka log segments as the distributed LSM analogue already mentioned in Vol-05 Ch02 — reciprocate).
- `vol-07/ch04`: add 2 prose xrefs — Vol-03 Ch9 (Maglev/ECMP wire mechanics) and Vol-11 Ch10 (retry budgets / resilience patterns that Ch04's capacity-aware routing previews).
- **Verification:** `grep -c 'Volume \d' vol-07/ch03` should be ≥3 after pass.

### Priority 5 — Author guidance for next enrichment passes (process, not file edits)

- **Length budget:** Enforce 4 000–7 000 hard ceiling — reject enrichment that pushes a file >7 300 words at batch-review time. The prior audit's guidance was correct; it was not enforced for Vols 5–6.
- **Diagram budget:** "2–4 meaningful; 5–8 only if the chapter is a case-study or protocol chapter where each diagram maps to a distinct mechanism (feed/chat/notification/KV, or Paxos/Raft safety) and you can justify each in review." Uniform 7/ch is the anti-pattern to avoid — vary by chapter merit.
- **Further reading bar:** Every chapter ≥6 entries with ≥4 resolvable URLs pinned to the version discussed. Citation without URL allowed only for mailing-list disclosures where URL is unstable — then include list + date.
- **Xref bar:** At least 2 prose cross-references to other volumes/chapters by title where dependency exists.
- **Hedging bar:** Every percentage or "X% of traffic" claim in a lead paragraph must carry an immediate scope qualifier ("for skewed workloads," "measured at...," "roughly").

---

## 8. Appendix — Detailed Per-Chapter Notes (Sampled)

### vol-05/ch02 — Storage Engines: B-Trees vs LSM-Trees
- **Mermaid validity:** 7 blocks — 6 `flowchart` + 1 `stateDiagram`; all valid (quoted labels with `<br/>`, no `&`/`()` in unquoted labels). Split before/after and SSTable cascade are the two most pedagogically important diagrams in Vol-05.
- **Code:** `sql` (fillfactor 90/80), `cpp` (RocksDB `Options` — annotated per-field, copy-pasteable). No `bash`.
- **Further reading:** 3 URLs — Postgres storage docs + RocksDB wiki + CIDR 2022; thin vs Vol-06 peers.
- **Risk framing:** Device FTL write amplification → page-size amplification → torn-page protection (full-page writes / doublewrite) → LSM's deferred sorting + cliff stalls — the chain is built correctly for Ch 7 crash recovery.

### vol-05/ch06 — Isolation Levels and MVCC
- **Mermaid validity:** 7 blocks — `sequenceDiagram` (write skew), `flowchart`×5 (level lattice, heap vs undo, visibility decision tree). Lattice correctly shows PG SI vs InnoDB RR as incomparable siblings.
- **Code:** 4 `sql` (doctors roster, lost-update, locking reads), 1 `python` (MVCC sketch). SQL uses PG/InnoDB-dialect correctly (40001, 1213).
- **Further reading:** 8 URLs — Berenson 1995, Cahill SIGMOD 2008, Fekete WSI 2004, Jepsen, PG `transaction_iso.html` + `routine-vacuuming`, MySQL RR docs. Exemplary.
- **Pedagogy:** Memory-model analogy table is the right on-ramp; "Oracle SERIALIZABLE caveat emptor" callout prevents real production bugs.

### vol-05/ch08 — Replication: Physical, Logical, Sync, and Async
- **Mermaid validity:** 7 blocks — `flowchart` (physical vs logical pipeline), `sequenceDiagram`×4 (async/sync/semi-sync, lag anomaly, failover hazard). Sequences carry the anomaly taxonomy visually.
- **Code:** 6 `sql`, 3 `ini`, 1 `bash` — `pg_basebackup`, `pg_create_physical_replication_slot`, `synchronous_standby_names` ANY/FIRST, LSN/GTID wait calls. PG 17 `pg_wal_replay_wait` is correctly marked as PG 17+.
- **Further reading:** 6 URLs — PG HA + logical replication, MySQL 8.4 replication, Patroni, classic Bernstein/Gray paper + Percona toolkit.
- **Ops honesty:** RPO>0 for async, hang for sync, silent degrade for semi-sync — and the "canceling a hanging commit does not roll it back" trap — are stated without vendor gloss.

### vol-06/ch05 — Consensus I: Paxos
- **Mermaid validity:** 7 blocks — Synod happy path, safety duel, livelock, Multi-Paxos pipelining, reconfiguration, SMR stack, family taxonomy. Safety duel diagram surfaces the conservatism (adopting an unchosen value) explicitly.
- **Code:** 1 `python` — full `Acceptor` with `stable.store` before reply; this is the fsync-before-ack rule from Vol-05 Ch07 in distributed form.
- **Further reading:** 9 URLs — Lamport Part-Time Parliament + Paxos Made Simple, Fischer-Lynch-Paterson FLP, Howard Flexible Paxos, Moraru EPaxos, Google Paxos Made Live, plus Ongaro Raft for forward ref.
- **History nuance done right:** 1990 allegory → 8-year unpublished lore → 1998 TOCS → 2001 Paxos Made Simple → 2007 Paxos Made Live — the narrative corrects the "Paxos is incomprehensible" lore without hand-waving the real Multi-Paxos gap.

### vol-06/ch06 — Consensus II: Raft
- **Mermaid validity:** 7 blocks — `stateDiagram-v2` (follower→candidate→leader), election duel, follower-repair, Figure 8 fork (unsafe vs safe branch). Figure 8 is the chapter's hardest diagram and is walked step-by-step in prose.
- **Code:** 2 `go` — `handleAppendEntries` with `TruncateFrom` + consistency check, `LinearizableRead` via `ReadIndex` with `hasCommittedEntryInCurrentTerm` guard. Idiosyncratically Go-idiomatic.
- **Further reading:** 8 URLs — raft.pdf + raft.github.io, etcd/raft, TiKV, Cockroach, Jepsen analyses, KIP-500. Correctly notes joint consensus vs single-server change with 2015 bug errata.
- **One nuance to preserve:** Single-server membership change is "simpler — and caught its own author" — the honesty about the bug is senior-appropriate.

### vol-06/ch02 — Time, Clocks, and the Ordering of Events
- **Mermaid validity:** 7 blocks — happen-before chain, Lamport converse-failure, vector-clock merge with numeric vectors. Worked three-node example correctly shows `[0,0,1]` vs `[2,2,0]` incomparable (concurrent) and `[1,0,0]` → `[2,3,2]` after merge.
- **Code:** 4 blocks — Go `time.Now` monotonic vs `UnixMilli` wrong path, Java `nanoTime` vs `currentTimeMillis`, Python Lamport/Vector, Go HLC `Now`/`Update`. Each pair shows the bug and the fix.
- **Further reading:** 7 URLs — Lamport 1978, Kulkarni HLC 2014, Spanner TrueTime, Cloudflare 2017 postmortem, Google Time Smear, plus Kleppmann locking. Balanced theory + incident.
- **Gap:** File truncated at line 500 in this audit's pager — HLC rules and synthesis section tail not fully re-read; Factual flags based on the first 500 lines + heading inventory. Recommend a follow-up `web_extract` on the HLC paper citation to pin the 2014 venue (OPODIS).

### vol-07/ch03 — Caching Strategies at Scale
- **Mermaid validity:** 7 blocks — layer stack, herd/stampede sequence, admission filter, distributed topologies (McRouter, Redis Cluster). Layer diagram matches the table one-to-one.
- **Code:** 6 `python`, 5 `bash`, 1 `java`, 1 `go`, 1 `http` — Zipf simulation with 1M-trace output, cache-aside with negative-result caching, Caffeine 3.1 `maximumSize`/`expireAfterWrite`/`recordStats`, Redis `maxmemory-policy` + `lfu-decay-time`, nginx `stale-while-revalidate`.
- **Further reading:** 10 URLs — Caffeine, Redis cluster-spec + eviction, memcached, Meta mcrouter, plus papers (NSDI Bronson, CMU BigDataPage). Strong and versioned.
- **Note:** `singleflight.py` threading/Event example is simplified to the point of non-idiomatic flag logic — the Go `singleflight.Group` block immediately after is the canonical reference and corrects it; retain both, but polish the Python path to avoid readers copying the simplified lock pattern.

### vol-07/ch04 — Load Balancing and Traffic Management
- **Mermaid validity:** 7 blocks — LB stack, bounded-load hash spillover, Envoy xDS, K8s topology, global health propagation. Each diagram tracks a §.
- **Code:** `python` smooth WRR (nginx algorithm), `yaml`×6 (Envoy static with outlier/circuit-breaker/health-check, K8s Service/headless/topology-aware, Ingress NGINX canary, Gateway API HTTPRoute weighted split, Istio DestinationRule), `json` gRPC retry budget. All configs typed to 2024–2025 APIs.
- **Further reading:** 10 URLs — Envoy 1.30, K8s Service/Gateway API, Google Maglev + Meta Katran papers, Cilium, gRPC A6 proposal, tail-at-scale.
- **Ops depth:** Envoy `curl /clusters` admin output + `membership_healthy` is the kind of one-liner operators actually use.

### vol-07/ch12 — Design Case Studies: Feed, Chat, Notifications, and a Global KV Store
- **Mermaid validity:** 8 blocks — feed hybrid router (push vs celebrity pull), chat sequencer/connection sharding, notification priority/batch pipeline, global KV ring. Feed diagram correctly branches on `Author class?` (normal / celebrity / cold).
- **Code:** `go`×6, `sql`×5, `yaml`×5, `python`×2, `bash`×1 — Cassandra `CREATE TABLE timelines/posts_by_author/follows/messages`, Redis zset `ZADD/ZREVRANGE`, Kafka `post.created` topic (`acks=all`, `enable.idempotence`, 256 partitions), Envoy sticky-hash `x-user-id`, Go sequencer with `SETNX` dedup.
- **Further reading:** 9 URLs — Twitter processing, Discord storage, Uber notification platform, Dynamo SOSP 2007, Cassandra arch, Spanner lineage.
- **Composition:** Each case's §1 states assumptions before arithmetic (Vol-07 Ch02 estimation discipline), and §5's failure table explicitly names the mitigation's home chapter (e.g., "Chapter 11 priority lanes").

---

## 9. What Was NOT Audited (and Should Be Before FINAL)

- **Full `web_extract` verification** of every Further-reading URL (sampled reasoning only; recommend a `web_extract` batch over all 38 Further-reading sections before FINAL — especially for PG/MySQL replication docs and Raft library repos).
- **Mermaid render test** (GitHub Mermaid renderer not invoked; syntax was checked via pattern + type inventory, not render — recommend a CI render or `mmdc` dry run).
- **Code execution** (bash/yaml/go/python snippets are plausible and fence-parity-clean but not executed; recommend `go vet` / `yamllint` / `python -m py_compile` batch before FINAL, especially the Go sequencer/conn handlers and Envoy/K8s YAML).
- **Cross-chapter consistency** of terminology (e.g., `provenance` not relevant here; but `consistent hashing` vs `rendezvous` definitions across Vol-14 Ch05 and Vol-07 Ch04 — spot-checked, but a corpus-wide `search_files` for conflicting definitions would be prudent).
- **Security anti-guidance scan** at scale (e.g., any chapter recommending overly broad `permissions:` or `curl | bash` without checksum — sampled chapters pass, but a `search_files` for `curl.*|.*bash` and `maxmemory-policy noeviction` misuse should be run).
- **Vol-05 Ch01, Ch03, Ch04, Ch05, Ch07, Ch09–Ch14 and Vol-06 Ch01, Ch03–04, Ch07–Ch12 unsampled detail** — per-chapter table covers 9 of 38; the remaining 29 were covered only by aggregate word-count/diagram/length metrics, not by full read. A second sampling pass (e.g., Vol-05 Ch03 indexing + Ch11 NoSQL, Vol-06 Ch07 quorums/Dynamo + Ch12 testing/Jepsen) would raise confidence to the level of the prior 145-file audit's 14-sample depth.
- **Tail of `vol-06/ch02` (HLC `Update` + TrueTime + synthesis)** — pager truncated at line 500; re-read from offset 501 before FINAL.

---

*Audit complete. No chapters were edited. Awaiting approval to proceed to the correction pass on Priorities 1–4 before any further enrichment of Vols 5–7.*
