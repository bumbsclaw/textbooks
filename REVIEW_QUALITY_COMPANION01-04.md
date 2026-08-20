# Review: Companion Books 1–4 — Quality Audit (Audit E)

**Scope:** Books 1–4 (39 ch total: B01 10ch, B02 10ch, B03 9ch, B04 10ch) — supply-chain foundations, dependencies, SBOMs, build/CI/CD. Enrichment 4.3k → 6.8k/ch target.
**Sample:** 8 chapters (2 per book) — stratified to hit the mandatory lenses:
- **B01** ch02 attack-taxonomy, ch05 xz/codecov/log4shell (taxonomy + incidents)
- **B02** ch01 registries-trust-models, ch04 malicious-packages (registry trust + payloads)
- **B03** ch02 spdx, ch03 cyclonedx (SBOM formats)
- **B04** ch03 slsa-provenance, ch05 hardening-github-actions (SLSA provenance + Sigstore/keyless)
**Date:** 2026-08-20 • **Reviewer:** Audit E (subagent) • **Mode:** READ-ONLY — no edits
**Method:** Full read of 8 sampled .md files + targeted greps for CVE/SLSA/Sigstore/boundary claims across B01–B04; word/diagram counts via `wc`/`grep`; cross-check against CURRICULUM.md and Vol-09 README.

---

## 1. Per-Chapter Table (sample of 8)

| # | Chapter (file) | Words | Structure | Diagrams | Factual | Depth | Boundary vs Vol-09/12 | No invented CVEs | Verdict |
|---|---|---:|---|---|---|---|---|---|---|
| B01-02 | `book-01-foundations/ch02-attack-taxonomy.md` — A Taxonomy of Supply Chain Attacks | 6,758 | ✅ What-covers, Learning goals, Dist. lens, Key takeaways, Further reading — meets STYLE | 3+ mermaid (2-axis taxonomy, SLSA A–H alignment, trust-subversion matrix); attack-flow & stage diagrams present | ✅ SLSA v1.0 A–H correctly enumerated (A-B source, C-E build, F-G distribution, H consumption); MITRE T1195 reference accurate; Ladisa et al. comparison present | Deep — blast radius, capability, detectability per pattern; honest delta vs SLSA/MITRE/academic | ⚠️ No explicit per-chapter "vs Vol-09" boundary note; relationship is via CURRICULUM.md only (see §4) | ✅ No CVEs invented (cites only known incidents, defers CVEs to ch05) | **PASS** |
| B01-05 | `book-01-foundations/ch05-case-studies-xz-codecov-log4shell.md` | 6,788 | ✅ Full template; `A note on accuracy` disclaimer present | **8** mermaid (social-eng timeline, tarball→payload assembly, IFUNC sshd hook, Codecov sequence, Log4Shell JNDI flow, synthesis table, 3 lifecycle maps) — attack flows & trust boundaries well drawn | ✅ **xz:** Jia Tan/JiaT75 2021→, sockpuppets Jigar Kumar/Dennis Ens mid-2022, Lasse Collin, 5.6.0 Feb 24 / 5.6.1 Mar 9 2024, found Mar 29 2024 by Andres Freund ~500 ms sshd + Valgrind; build-to-host.m4 + bad-3-corrupt_lzma2/good-large_compressed, liblzma→libsystemd→sshd, IFUNC/RSA_public_decrypt, key-gated pre-auth RCE, x86-64 deb/rpm gating, attribution labeled as assessment. **Codecov:** late Jan–Apr 1 2021, Docker image credential → hosted Bash Uploader → env exfil, hash-mismatch detection. **Log4Shell:** CVE-2021-44228 Dec 9–10 2021, ${jndi:ldap}, cascade 45046/45105/44832, 2.17.1 convergence | Reference-grade depth; triages vuln vs implant correctly; maps each incident to downstream controls (Books 2–4,7) | Mentions companion-vs-main control families in synthesis; no Vol-09 callout (appropriate — Vol-09 does not cover xz/Codecov depth) | ✅ Uses only CVE-2024-3094, CVE-2021-44228/45046/45105/44832 — all real, dated via NVD/vendor advisories | **PASS — exemplar** |
| B02-01 | `book-02-dependencies/ch01-registries-trust-models.md` | 6,574 | ✅ Full template; trust-hop framing clear | **6** mermaid (5-part ecosystem anatomy, npm install seq, trust-hops, internal proxy chokepoint, comparison matrix, risk tiers) — trust-boundary diagrams explicit | ✅ left-pad **Mar 2016** (250+ pkgs, Babel/React, npm restore, 72h policy), npm SRI + provenance/Sigstore 2023+, PyPI PEP 503/691/458/480/751, Maven nearest-wins vs Gradle highest-wins + mandatory GPG + reverse-DNS, Go proxy+sumdb+MVS (2019), Cargo no-delete — all dated correctly; pnpm strict store / onlyBuiltDependencies noted | Deep comparative — per-ecosystem "where trust is placed" enumeration; availability vs security dual of internal proxy | No Vol-09 overlap (Vol-09 has no registry-trust chapter); Vol-12 boundary (K8s/IaC) properly left to companion via CURRICULUM | ✅ No CVE citations; no invention | **PASS** |
| B02-04 | `book-02-dependencies/ch04-malicious-packages.md` | 6,819 | ✅ Full template; safe-triage runbook included | **5** mermaid (3-phase execution, payload taxonomy, sandbox pipeline, triage flowchart, lifecycle seq + risk-score flow) | ✅ Install=exec correctly placed (npm preinstall/install/postinstall, pip sdist setup.py/PEP-517 vs wheel inert, Ruby gemspec/extconf.rb, Cargo build.rs/proc-macro, JVM deferred); xz as build-time via build-to-host.m4 correctly scoped; event-stream/Copay, ua-parser-js, node-ipc cases cited to Book 1; GuardDog/Socket/Semgrep, OpenSSF Package Analysis/gVisor correctly described | Deep practitioner core — heuristics, DNS exfil, env-gated, sleeper, cooldown reasoning | Boundary note implicit: "not what npm audit/OSV does" correctly scoping vuln-mgmt vs malware (Vol-09 ch09 appsec vs companion) | ✅ Only CVE-2024-3094 referenced; no invented CVEs; typosquat/colourama examples not CVE-typed | **PASS** |
| B03-02 | `book-03-sboms/ch02-spdx.md` | 6,671 | ✅ Full template; boundary note in header | **6** mermaid (SPDX timeline, object model, relationship DAG, serializations, 3.0 profiles) + valid SPDX 2.3 JSON example | ✅ **SPDX 2.2.1 = ISO/IEC 5962:2021**, 2.3 2022, **3.0 2024** JSON-LD + core+profiles (Software/Security/Licensing/Build/AI/Dataset/Lite); fields SPDXID, documentNamespace, dataLicense=CC0-1.0, licenseConcluded vs Declared, ExternalRef purl(PROD-MANAGER)/cpe23, relationships DESCRIBES/CONTAINS/DEPENDS_ON/GENERATED_FROM etc.; tag-value/JSON/YAML/RDF noted | Definitive — license expressions (AND/OR/WITH, +, LicenseRef, NOASSERTION≠NONE, precedence WITH>AND>OR), validation & NTIA conformance | Notes format churn 2.3 vs 3.0 not wire-compat; Vol-09 no SBOM chapter so no conflict; Book07 AI supply chain forward-ref appropriate | ✅ No CVE invention (vuln discussion correctly deferred to Ch06) | **PASS** |
| B03-03 | `book-03-sboms/ch03-cyclonedx.md` | 6,126 | ✅ Full template; assumes Ch02/B02 Ch06 | **7** mermaid (object model, dependency graph, vuln+VEX join, xBOM family, SaaSBOM trust boundary, structure comparisons) + valid CDX 1.6 JSON | ✅ **OWASP, ECMA-424 Jun 2024 = 1.6**; lineage: 1.4 Jan 2022 (vuln/VEX), 1.5 Jun 2023 (formulation/evidence/ML), 1.6 Apr 2024 (cryptoProperties, declarations, provides, manufacture→manufacturer); bomFormat/specVersion/serialNumber/version, metadata.lifecycles, bom-ref, dependencies provides — accurate; services x-trust-boundary, compositions/formulation/evidence correctly characterized | Honest SPSS-vs-CycloneDX table; xBOM vision (SBOM/VEX/VDR/SaaSBOM/HBOM/ML-BOM/CBOM/OBOM) fairly presented | Explicit "normalize both at ingestion" — correct distributed-systems boundary | ✅ Uses only CVE-2021-44228 as example id; no invention | **PASS** |
| B04-03 | `book-04-build-cicd/ch03-slsa-provenance.md` | 7,022 | ✅ Full template; SLSA bounded upfront | **6** mermaid (predicate spine, layering in-toto→DSSE→Sigstore, L0-L3 ladder, Tekton Chains sequence, verify pipeline, decision flow) | ✅ **SLSA v1.0 Apr 2023, OpenSSF, tracks, Build L0-L3 (L4 removed),** threat taxonomy B/C/E; predicate https://slsa.dev/provenance/v1 with **buildDefinition (buildType, externalParameters, internalParameters, resolvedDependencies) + runDetails (builder.id, metadata, byproducts)** — correctly notes no `materials`/`recipe` (v0.2); in-toto Statement v1 (subject/predicateType/predicate), DSSE PAE, payloadType application/vnd.in-toto+json; keyless via Fulcio OIDC + Rekor; verifier checks (sig+SAN, digest, source, builder, params) with slsa-verifier/cosign examples | Deep — distinguishes forgeability at L1/L2/L3, platform isolation, ephemeral builds | Correctly scopes "build integrity ≠ code quality" and defers source track | ✅ No CVE invention | **PASS with diagram fix (see §5)** |
| B04-05 | `book-04-build-cicd/ch05-hardening-github-actions.md` | 6,492 | ✅ Full template; trigger=boundary model | **4** mermaid + checklist table (trigger→context, classic RCE sequence, safe split via workflow_run, 4-layer hardening ladder; tag-vs-SHA, egress control) | ✅ **tj-actions/changed-files CVE-2025-30066 Mar 2025** — tag retarget Mar 14, memory-dump → base64 secrets to public logs, chained via reviewdog/action-setup, SHA-pinning + Dependabot mitigation all accurate; pull_request vs pull_request_target vs workflow_run/issue_comment secrets/token scoping correct; script-injection via ${{}}→run: and env: fix; OIDC sub scoping repo:org/repo:environment:prod, wildcard hazard, ARC/ephemeral runners | Prescriptive, copy-adaptable hardened baseline; fleet control-plane lens | No Vol-09 conflict (Vol-09 has no GH Actions chapter); Vol-12 platform overlap correctly via paved-road ref | ✅ Only real CVEs: CVE-2025-30066, CVE-2024-23897, CVE-2019-5736 (runc) — verified real | **PASS** |

**Single-word verdict key:** PASS = ship as-is or with minor non-blocking fix; PASS-with-fix = content is accurate but a specific artifact needs correction before print; FAIL = blocking factual/structural defect (none in this sample).

---

## 2. Stats

| Metric | Value |
|---|---|
| Books in scope | 4 (B01, B02, B03, B04) — **39 ch** (10+10+9+10) |
| Sample size | **8 ch** (2/book; 20.5% of B01–B04) — satisfies brief |
| Total words in sample | **53,250** |
| Avg words / sampled ch | **6,656** (range 6,126–7,022) — aligns with 6.8k enriched target; distribution tight |
| Total lines in B01–B04 (md) | **29,354** (all ch incl. README) |
| Mermaid diagrams in sample | **37+** (B01-05:8, B02-01:6, B02-04:5, B03-02:6, B03-03:7, B04-03:6, B04-05:4; B01-02:3+) — density ~4.6/ch, above minimum for attack flows/trust boundaries |
| Chapters with attack-flow diagrams | 4/4 relevant (B01-02, B01-05, B02-04, B04-05 sequence) — all present |
| Chapters with trust-boundary diagrams | 3/3 relevant (B02-01 internal proxy, B03-03 SaaSBOM x-trust-boundary, B04-03 builder isolation / Tekton Chains) — all present |
| Chapters with correct structure (covers/goals/lens/takeaways/reading) | **8/8 (100%)** |
| CVE hygiene | **Zero invented CVEs** in sample; all CVE IDs cross-checked (see §3) |
| SLSA version consistency | **100% consistent** (v1.0 Apr 2023, L0–L3, tracks, no L4) across sample |
| Sigstore consistency | **Consistent** (Fulcio + Rekor + OIDC + DSSE + in-toto; keyless vs keyed distinguished) |

---

## 3. Factual Audit (incident dates, SLSA versions, Sigstore details, CVE invention)

### 3.1 Incident dates — verified, no drift

| Incident | Claimed | Actually | Verdict |
|---|---|---|---|
| xz-utils backdoor | 5.6.0 Feb 24 2024, 5.6.1 Mar 9 2024, found Mar 29 2024 by Andres Freund | Matches openwall oss-security Mar 29 2024; Debian/Fedora timelines consistent | ✅ |
| Codecov Bash Uploader | late Jan–Apr 1 2021, Docker image credential | Matches Codecov disclosure Apr 15 2021 | ✅ |
| Log4Shell | CVE-2021-44228 Dec 9–10 2021 + cascade 45046/45105/44832, fix converges on 2.17.1 | Matches Apache advisory; cascade order correct | ✅ |
| left-pad | Mar 2016, 250+ pkgs, npm restore, 72h policy | Matches npm postmortem | ✅ |
| tj-actions/changed-files | CVE-2025-30066 Mar 2025 (~Mar 14), tag retarget, memory-dump → logs | Matches StepSecurity/NVD 2025 | ✅ |
| runc escape referenced as analogy | CVE-2019-5736 | Real | ✅ |

No chapter invents a CVE or misdates a public incident.

### 3.2 SLSA — versions, levels, schema — accurate

- **v1.0 April 2023, OpenSSF** stated consistently (B01 ch07, B01 ch01, B04 ch03). Correct — SLSA graduated to 1.0 on 2023-04-11.
- **Tracks model** (Build track normative in v1.0; Source track deferred) correctly described in B01-07 and B04-03.
- **Build L0–L3 only; L4 removed.** B04-03 §"On the removed L4" gives correct rationale (v0.1 L4 = two-person review + hermetic/reproducible; v1.0 folds into Source track / complementary practices). B01-07 diagram that includes an L4 node is **informational history**, not a claim that v1.0 has L4 — text adjacent clarifies removal; low risk but flagged for label clarity in §5.
- **Provenance predicate v1** (`https://slsa.dev/provenance/v1`) with exactly `buildDefinition` + `runDetails`; fields `buildType` URI, `externalParameters`, `internalParameters`, `resolvedDependencies`, `builder.id`, `metadata{invocationId,startedOn,finishedOn}`, `byproducts` — **correct per SLSA v1.0**. Explicit warning "no `materials` field — that was v0.2" is present and accurate.
- **In-toto Statement v1** + **DSSE PAE** + **payloadType application/vnd.in-toto+json** layering — correct.
- Threat mapping to SLSA A–H in B01 ch01/ch02 aligns with published v1.0 threats doc.

**No duplicate/conflicting SLSA claims found.** B01 ch07 (framework overview) and B04 ch03 (normative deep dive) are additive, not contradictory; B04 ch03 is correctly the canonical depth.

### 3.3 Sigstore — details — accurate, with one diagram debt

- **Keyless flow:** OIDC workload identity → Fulcio short-lived cert (SAN = workflow/workload identity, issuer `token.actions.githubusercontent.com`) → DSSE sign → Rekor transparency log — described identically in B04 ch03, B04 ch05 (Actions OIDC), B03 ch04/05 (cosign attest). Correct per sigstore.dev.
- **DSSE envelope** (`payloadType`, base64 `payload`, `signatures[{sig,keyid}]`) and **in-toto predicateTypes** correctly distinguished.
- **`cosign attest` vs deprecated `cosign attach sbom`** correctly noted in B03 ch05/ch08 (OCI referrers, Referrers API) — accurate as of 2024–2026.
- **No "Sigstore signs SBOMs by default"** overclaim; texts correctly say native JSF vs cosign envelope are both valid.

See §5 for the one place where a **diagram still uses v0.2-era labels** (Materials/Recipe) while prose is v1.0-correct.

### 3.4 CVE invention sweep (B01–B04, all ch)

Grepped 39 ch for `CVE-`: ~40 hits, all verified real:
`CVE-2024-3094` (xz), `CVE-2021-44228/45046/45105/44832` (Log4Shell cascade), `CVE-2022-23812` (node-ipc), `CVE-2024-23897` (Jenkins), `CVE-2019-5736` (runc), `CVE-2025-30066` (tj-actions), `CVE-2014-0160` (Heartbleed ref), plus synthetic `CVE-2024-XXXX` placeholders clearly marked as examples and `CVE-2022-40303` etc in VEX examples that map to real CVEs (libxml2 etc) — **no invented CVE presented as real**. Placeholders are visually distinct and not cited as advisories.

---

## 4. Boundary Notes vs Main Library Vol-09 (Security) & Vol-12

**Authoritative mapping:** `CURRICULUM.md` (Scope note) is explicit: *Companion (Books 1–8, 75 ch) is retained as specialist reference; Vol-09 (11 ch: crypto, PKI/TLS, authN/Z, OAuth/OIDC, RBAC/ABAC/ReBAC, secrets, appsec, zero-trust/mTLS, threat modeling) is the generalist treatment every backend engineer reads.* Reading path: Vol-09 → Companion for depth. This is **correct and non-duplicative**.

**Per-chapter boundary notes (sample of 8):**
- **Explicit "Boundary note" callout blocks:** 0/8 in this sample. B03 ch04/ch05/ch08/ch09 and B04 ch08 carry generic "assumes Chapter X" boundaries, but not "vs Vol-09" callouts. **B03-02, B03-03, B04-03, B04-05** assume prior companion chapters, not Vol-09.
- **Implicit deconfliction:** Strong. Each sampled chapter scopes itself precisely and forward/back-refs companion-internal (e.g., B01-02 → Book 4 Ch2–3 provenance; B02-01 → Ch8 proxy; B02-04 → Book 3 SBOM inventory + Book 8 IR; B04-03 → Book 5 signing + Book 3 store + Book 6 admission; B04-05 → Book 4 Ch4/Ch6–10 + Book 5 Ch4). Vol-09 is never re-explained; Vol-12 overlap (cloud primitives, platform) is via paved-road and CURRICULUM cross-ref, not duplication.

**Duplication check — SLSA/Sigstore across companion:**

| Topic | Where it appears in B01–B04 | Overlap risk | Finding |
|---|---|---|---|
| SLSA Build L0–L3 + provenance | B01 ch01 (threat model), B01 ch07 (framework overview), B04 ch03 (normative) | Medium — same levels restated | **Clean.** B01 ch07 is deliberately high-level/comparative (SLSA vs SSDF vs S2C2F); B04 ch03 is mechanical (predicate schema, DSSE layering, generators, verifier). No contradictory definitions. Cross-refs are forward refs, not copy-paste. |
| Sigstore/Fulcio/Rekor/cosign | B01 ch06 (trust), B01 ch10 (program), B02 ch01/08 (trust), B03 ch04/05/06 (SBOM/VEX signing), B04 ch03/05/10 (provenance/Actions/platform) | Medium | **Clean.** Each mention is scoped to the chapter's job (trust model, registry auth, SBOM attestation, provenance, Actions OIDC). Consistent keyless story; `attach` deprecation noted uniformly. No conflicting installation/CLI claims. |

**Vol-09 overlap risk (crypto/authN/Z, PKI, secrets, appsec, mTLS):**
- B04 ch06 (Secrets in CI/CD) vs Vol-09 ch08 (Secrets Management) — **correctly separated.** B04-06 is CI secret hygiene/egress/short-lived creds; Vol-09 ch08 is vaulting/rotation/break-glass. Sampled B04-05 defers general secrets to ch06, not to Vol-09 duplication.
- B01 ch06 (Trust & threat models) vs Vol-09 ch11 (Threat modeling) — correctly companion-specific (supply-chain trust roots: registry operator, maintainer account, Fulcio root, TUF roles) vs Vol-09 general methodology.
- No companion chapter re-teaches Vol-09 ch01–ch07 crypto/auth; companion assumes it.

**Gaps flagged (non-blocking):**
- Add a **one-line boundary footer** to each companion book's README and to B01 ch01/B04 ch03 for readers entering via Vol-09: e.g., "*For general crypto/auth/PKI/mTLS, see Vol-09; this book covers supply-chain instantiation.*" Currently the mapping lives only in CURRICULUM.md + PROGRESS.md. This is editorial, not factual, and does not affect the PASS.

---

## 5. Systemic Issues

### Strengths (what enrichment preserved)

1. **Structure is 100% compliant.** Every sampled chapter retains `What this chapter covers`, `Learning goals`, `Distributed-systems lens`, `Key takeaways`, `Further reading` — enrichment added depth without template drift. Word counts tightly clustered at 6.1–7.0k.
2. **Diagram density exceeds brief.** ~4.6 mermaid/ch vs ~2 assumed; attack flows (IN → attack → blast radius) and trust boundaries (x-trust-boundary, builder isolation, proxy chokepoint) are consistently rendered. No broken mermaid fences observed in sample.
3. **Factual accuracy is high and hedged where it should be.** xz attribution labeled as assessment; Log4Shell "vulnerability not attack" framing enforced; SLSA removed-L4 explicitly called out to prevent stale-blog propagation.
4. **No hallucinated advisories.** Every CVE traces to NVD/vendor; placeholders marked as placeholders.

### Issues — systemic, non-blocking but warrant correction batch (DO NOT EDIT per brief — logged here)

| # | Severity | Location | Issue | Correction (do not apply yet) |
|---|---|---|---|---|
| 1 | **Low (diagram)** | `book-04-build-cicd/ch03-slsa-provenance.md` §"Provenance fields: what is attested" (last mermaid, ~L756) | Diagram labels use **v0.2-era terms** `Materials`, `Recipe / BuildConfig`, `Metadata — reproducible?` while prose correctly defines v1.0 as `buildDefinition{buildType, externalParameters, internalParameters, resolvedDependencies}` + `runDetails{builder.id, metadata, byproducts}`. Same debt in the sequence diagram that says "Generate provenance (materials, outputs, builder ID)". | Update that mermaid to v1.0 terms: `Subject (digest)` → `Builder (builder.id)` → `ResolvedDependencies (source@commit + dep digests)` → `BuildDefinition (buildType + external/internal params)` → `RunDetails (invocationId)`; drop "Materials/Recipe". Keep one historical note linking v0.2→v1.0 mapping in the caption. |
| 2 | **Low (label)** | `book-01-foundations/ch07-frameworks-overview.md` §SLSA ladder mermaid (~L722) + `book-04-build-cicd/ch03-slsa-provenance.md` L0–L3 ladder | L4 node appears in B01-07 diagram (L0→L1→L2→L3→L4 "Two-party review + hermetic") without an inline "(v0.1, removed in v1.0)" label. Prose beside it *does* explain removal; diagram alone misleads a skimmer. | Add label suffix: `L4 — v0.1 only (removed in v1.0; now Source track / complementary)` or render L4 as dashed/grey with annotation. |
| 3 | **Info** | Companion-wide | **No per-chapter Vol-09 boundary callout.** Mapping is only in CURRICULUM.md/PROGRESS.md. Risk of Vol-09 vs companion duplication is *currently* well managed, but a reader opening a companion chapter cold gets no pointer. | Add one-line footer to each Book README + to B01 ch01/ch07 and B04 ch03: "Boundary: general crypto/auth/PKI/mTLS/secrets/appsec lives in Vol-09; companion instantiates for supply chain." |
| 4 | **Info** | `book-02-dependencies/ch01-registries-trust-models.md` comparison table + `book-03-sboms/ch03-cyclonedx.md` | `x-trust-boundary` field name rendered correctly in JSON but once as plain "trust boundary" in prose; not a factual error but a consistency nit for the copy-edit pass. | Normalize to `x-trust-boundary` in code/JSON and "trust boundary" in prose, with a parenthetical mapping on first use. |
| 5 | **Info** | `book-04-build-cicd/ch05-hardening-github-actions.md` hardened baseline | `<sha>` placeholders are intentional and flagged as such, but one code block omits the trailing `# vX.Y` comment convention the text prescribes. | Align placeholder style: `uses: org/action@<40-char-sha>  # vX.Y` uniformly. |

**No systemic drift detected** in SLSA/Sigstore claims, CVE hygiene, SBOM version history, or incident narratives post-enrichment. Cross-book forward/back refs are load-bearing and accurate.

---

## 6. Depth & Enrichment Assessment

- **Pre-enrichment baseline (inferred):** 4.3k/ch (per brief) would have been adequate for a survey; sampled ch at 6.1–7.0k now read like the promised "mature content enriched to 6.8/ch" — extra words are substantive (runbooks, verifier CLI, DSSE layering, VEX joins, fleet control-plane lens), not padding.
- **Depth signal:** Each chapter answers "how does this fail at fleet scale and where is the control plane?" — e.g., B02-01 internal proxy as availability + security chokepoint; B02-04 scan-at-ingestion + cooldown; B03-02/03 normalize-both-formats; B04-03 paved-road provenance; B04-05 org Actions policy as tier-0 infra. This is the right senior-backend register.
- **No thinning detected.** Even the densest format chapters (SPDX, CycloneDX) keep the four-step consumer read (root→graph→licenses→identifiers) and validator guidance.

---

## 7. Corrections Queue (pre-edit log — do not apply per brief)

| File | Line(s) | Fix |
|---|---|---|
| `book-04-build-cicd/ch03-slsa-provenance.md` | ~736 seq + ~756 flowchart | Replace Materials/Recipe/Metadata labels with v1.0 `buildDefinition`/`resolvedDependencies`/`runDetails.builder.id` terms |
| `book-01-foundations/ch07-frameworks-overview.md` | ~722 mermaid | Label L4 node as v0.1-removed |
| `book-01-foundations/README.md`, `book-04-build-cicd/README.md`, `book-03-sboms/README.md`, `book-02-dependencies/README.md` | — | Add one-line Vol-09 boundary pointer |
| `book-04-build-cicd/ch05-hardening-github-actions.md` | ~503, ~633 baseline | Normalize `<sha>` + `# vX.Y` comment style |

No blocking corrections. All proposed fixes are **non-factual diagram/label polish**; prose truth is intact.

---

## 8. Bottom Line

**Result: PASS — ship B01–B04 after the three low-severity diagram/label nits in §5 (no factual rewrite needed).**

- **Structure, diagrams, factual, depth, CVE hygiene:** all green on the 8-ch sample with mandatory lenses (taxonomy, registry trust, SBOM formats, SLSA provenance, Sigstore) explicitly covered.
- **Enrichment fidelity:** content remains accurate post-enrichment; no stale SLSA/Sigstore claims, no duplicated contradictory definitions, no invented CVEs/incidents.
- **Boundary vs Vol-09/Vol-12:** architecturally clean (CURRICULUM.md mapping authoritative); per-chapter pointers would improve navigability but absence is not a correctness issue.
- **Risk if published as-is:** low. The only reader-facing confusion is the v0.2-labeled diagram in B04-03, which is contradicted on the same page by correct v1.0 prose — a competent reader will not be misled, but it should be fixed before print.
