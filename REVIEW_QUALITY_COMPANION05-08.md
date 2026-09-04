# Quality Review — Companion Books 5–8 (36 ch)

**Date:** 2026-08-20
**Auditor:** subagent (muse-spark-1.2, automated + full file read)
**Scope:** Books 5–8 only — 36 chapters (book-05 10 ch, book-06 10 ch, book-07 8 ch, book-08 8 ch). Enriched 4.4 → 7.0/ch.
**Sample:** 8 chapters, 2 per book, covering mandated themes: cosign/Fulcio/Rekor, OCI/TUF, commit signing, S2C2F/governance.
**Standard:** `STYLE.md` (4 000–7 000 words/ch, 2–4 Mermaid diagrams/ch, `# Chapter N — Title` / *What this chapter covers* + learning goals / `## Key takeaways` / `## Further reading`, real code/config, correct dates/specs, no invented facts, distributed-systems lens, senior backend depth).
**Outcome:** Do NOT edit — audit only. Correction list prioritized for next pass.

---

## 1. Executive Summary

Books 5–8 are **structurally complete and factually strong** — every sampled chapter passes the STYLE contract, every factual spot-check on Sigstore/TUF/OCI/governance claims passes, and depth is consistently senior-level. Two of the eight sampled chapters are exemplary (TUF, OCI images), four are strong, two are adequate with gaps.

Three systemic issues require a correction pass before sign-off:

1. **Length discipline** — 36-ch mean is **7 012 words** (ceiling 7 000); **17/36 (47%) exceed 7 000**, with a tail to 8 678. This is *better* than the 145-file corpus mean of 7 095 (57% over), but still non-compliant and concentrated in Books 7–8.
2. **Diagram inflation** — every one of the 36 chapters has **7–8 Mermaid blocks** (mean 7.08). STYLE asks for 2–4 *meaningful* diagrams. The enrichment (4.4 → 7.0/ch) overshot: all 36 exceed the guideline. Content of diagrams is sound; count is inflated.
3. **Further-reading URL hygiene + code-fence tags + recency pins** — 12/36 chapters have **zero `https://` URLs in Further reading** (citation-style entries without hyperlinks, concentrated in governance/IaC/regulatory chapters); many code fences are **unlabeled** (empty language tag); only **9/36** carry an explicit 2025–2026 recency pin.

No BLOCKER: no invented CVEs/specs/stats, no marketing language, no security anti-guidance found in the sample.

---

## 2. Methodology

1. Enumerated all `ch*.md` under `~/code/textbooks/backend-engineer-library/book-0{5,6,7,8}` — 36 files.
2. Computed per-file `split()` word count, `grep -c '```mermaid'`, regex checks for title / covers / goals / takeaways / Further reading / distributed-systems lens, code-fence inventory with language tags, heading counts, trailing-`>` link scan, marketing-language scan, CVE/percent scan.
3. Selected 8 samples to cover all four books and the four mandated theme areas:
   - **Book 5 — Signing & Attestation:** `ch03-sigstore-architecture` (cosign/Fulcio/Rekor, ~10-min certs, verify-after-expiry, TUF) and `ch07-tuf` (TUF roles/thresholds/PEP 458/480, Sigstore TUF root)
   - **Book 6 — Cloud-Native:** `ch01-oci-images` (OCI manifest/config/diff_id/referrers) and `ch05-image-signing-k8s` (OCI + admission, verify-and-run-the-same-digest)
   - **Book 7 — Source Security:** `ch02-commit-signing-identity` (GPG/SSH 2.34/gitsign, Verified badge) and `ch03-branch-protection-review` (CODEOWNERS, two-person, dismiss-stale)
   - **Book 8 — Governance & IR:** `ch02-adopting-slsa-s2c2f` (SLSA v1.0 L0–L3 + S2C2F 8 practices) and `ch06-incident-response` (PICERL/NIST, Log4Shell/SolarWinds/Codecov)
4. For each sampled chapter: **full file read** (not excerpt), diagram-by-diagram validity scan, factual spot-checks (2–4 claims per chapter) against known 2026 references, depth rubric.

---

## 3. Aggregate Stats — Books 5–8 (36 files)

| Metric | Value | STYLE Target | Compliance |
|--------|-------|-------------|------------|
| **Total files** | 36 | — | — |
| **Total words** | ~252 446 | — | — |
| **Mean words / file** | **7 012** | 4 000–7 000 | **+12 over ceiling** |
| **Median (estimated)** | ~6 930 | 4 000–7 000 | near ceiling |
| **Files within 4 000–7 000** | 19 / 36 (**53%**) | 100% | 47% non-compliant |
| **Files > 7 000** | **17 / 36 (47%)** | 0% | Heavy tail, but better than corpus 57% |
| **Files < 4 000** | 0 / 36 (0%) | 0% | No shortfall |
| **Lightest** | 5 516 (`book-05/ch08`) | — | Compliant |
| **Heaviest** | 8 678 (`book-08/ch08`) | — | +24% |
| **Top 5 heaviest** | 8 678 (`b08/ch08`), 8 383 (`b08/ch06`), 7 879 (`b05/ch05`), 7 844 (`b07/ch05`), 7 835 (`b08/ch04`) | — | Up to +24% |
| **Mermaid blocks — mean / file** | **7.08** | 2–4 | **Mean exceeds guideline by ~3** |
| **Files with ≥2 diagrams** | 36 / 36 (**100%**) | 100% | Perfect floor |
| **Files with 2–4 diagrams** | **0 / 36 (0%)** | — | **Zero within guideline** |
| **Files with 5–6 diagrams** | 0 / 36 | — | — |
| **Files with 7–8 diagrams** | **36 / 36 (100%)** | — | **Systemic overshoot** |
| **Files with labeled code fences** | 26 / 36 (72%) | — | 10 files have zero *labeled* fences |
| **Files with zero https in Further reading** | 12 / 36 (33%) | — | Governance/IaC/regulatory cluster |
| **Files with recency pin (2025/2026/as of 2026)** | 9 / 36 (25%) | — | Low |
| **Structure contract (sampled 8)** | 8 / 8 (**100%**) | 100% | All sections present |
| **Marketing-language hits (sampled)** | 0 | 0 | Clean |
| **Invented CVE/stat/quote (sampled)** | 0 confirmed | 0 | Clean |

**All 36 chapters — per-file detail:**

| # | File | Words | Mermaid | Labeled code | Further-reading URLs | Recency pin? |
|---|------|------:|--------:|-------------:|---------------------:|--------------|
| 1 | `book-05/ch01-crypto-foundations` | 7 487 | 7 | 0 | 0 | ✅ |
| 2 | `book-05/ch02-classic-code-signing` | 6 895 | 7 | 1 | 0 | ❌ |
| 3 | `book-05/ch03-sigstore-architecture` | 6 609 | 7 | 2 | 8 | ✅ |
| 4 | `book-05/ch04-keyless-signing` | 7 422 | 7 | 7 | 9 | ❌ |
| 5 | `book-05/ch05-transparency-logs` | 7 879 | 7 | 1 | 10 | ❌ |
| 6 | `book-05/ch06-in-toto` | 6 121 | 8 | 4 | 10 | ❌ |
| 7 | `book-05/ch07-tuf` | 7 227 | 7 | 0 | 8 | ❌ |
| 8 | `book-05/ch08-provenance-verification` | 5 516 | 7 | 7 | 10 | ❌ |
| 9 | `book-05/ch09-key-management` | 6 930 | 7 | 3 | 18 | ❌ |
| 10 | `book-05/ch10-deployment-gates` | 6 005 | 7 | 4 | 15 | ❌ |
| 11 | `book-06/ch01-oci-images` | 5 895 | 7 | 14 | 7 | ✅ |
| 12 | `book-06/ch02-registries` | 7 276 | 7 | 3 | 11 | ❌ |
| 13 | `book-06/ch03-base-images` | 7 707 | 7 | 7 | 11 | ❌ |
| 14 | `book-06/ch04-image-scanning` | 6 969 | 7 | 2 | 20 | ❌ |
| 15 | `book-06/ch05-image-signing-k8s` | 6 274 | 7 | 7 | 10 | ❌ |
| 16 | `book-06/ch06-admission-policy` | 6 499 | 7 | 13 | 10 | ✅ |
| 17 | `book-06/ch07-k8s-delivery-chains` | 6 247 | 7 | 7 | 20 | ❌ |
| 18 | `book-06/ch08-iac-risks` | 6 861 | 7 | 7 | 0 | ❌ |
| 19 | `book-06/ch09-serverless-managed` | 6 874 | 7 | 0 | 0 | ❌ |
| 20 | `book-06/ch10-reference-architecture` | 7 105 | 7 | 2 | 0 | ✅ |
| 21 | `book-07/ch01-scm-threat-model` | 6 745 | 7 | 1 | 8 | ❌ |
| 22 | `book-07/ch02-commit-signing-identity` | 6 341 | 7 | 9 | 9 | ❌ |
| 23 | `book-07/ch03-branch-protection-review` | 7 718 | 7 | 4 | 10 | ❌ |
| 24 | `book-07/ch04-secrets-in-source` | 7 714 | 7 | 5 | 10 | ❌ |
| 25 | `book-07/ch05-backdoors-malicious-code` | 7 844 | 7 | 1 | 9 | ❌ |
| 26 | `book-07/ch06-insider-threats-ato` | 6 532 | 7 | 0 | 10 | ❌ |
| 27 | `book-07/ch07-ai-code-model-supply-chain` | 7 050 | 7 | 0 | 0 | ✅ |
| 28 | `book-07/ch08-repo-integrity-at-scale` | 6 832 | 7 | 4 | 14 | ❌ |
| 29 | `book-08/ch01-regulatory-landscape` | 7 116 | 8 | 0 | 0 | ✅ |
| 30 | `book-08/ch02-adopting-slsa-s2c2f` | 7 500 | 8 | 0 | 0 | ❌ |
| 31 | `book-08/ch03-vendor-risk` | 7 306 | 7 | 0 | 0 | ❌ |
| 32 | `book-08/ch04-policy-as-code` | 7 835 | 7 | 5 | 11 | ✅ |
| 33 | `book-08/ch05-detecting-compromise` | 6 276 | 7 | 0 | 0 | ❌ |
| 34 | `book-08/ch06-incident-response` | 8 383 | 7 | 2 | 0 | ✅ |
| 35 | `book-08/ch07-threat-intelligence` | 6 778 | 7 | 2 | 0 | ❌ |
| 36 | `book-08/ch08-metrics-reporting` | 8 678 | 7 | 0 | 10 | ❌ |

*Labeled code* counts fences with an explicit language tag (`bash`/`yaml`/`json`/`rego`/`dockerfile`/…); many unsampled chapters use unlabeled ` ``` ` fences for outputs/tables. Further-reading URLs counts `https://` occurrences *inside* the `## Further reading` section only.

---

## 4. Per-Chapter Findings (Sampled 8)

> Words = `split()` count. Mermaid = ` ```mermaid` blocks. Depth: Exemplary / Strong / Adequate / Shallow. Factual: PASS / SOFT / FLAG.

| # | File | Words | Mermaid | Structure | Factual | Depth | Issues (summary) |
|---|------|------:|--------:|-----------|---------|-------|------------------|
| 1 | `book-05/ch03-sigstore-architecture` | 6 609 | 7 | ✅ PASS — Title, covers + 7 learning goals, `## Key takeaways` (bulleted), `## Further reading` (8 URLs), distributed lens (§ TUF-as-root-of-trust + fleet signing), 2 labeled code + 9 empty fences | **PASS** — Fulcio ~10-min cert validity correct; Rekor = Merkle-tree log with inclusion proof + SET + integratedTime correct; verify-after-expiry `NotBefore ≤ integratedTime ≤ NotAfter` correct; CT log vs Rekor distinction correct; `sigstore/root-signing` + TUF root correct; cosign v2 mandatory `--certificate-identity`/`--certificate-oidc-issuer` correct; sign-digests-not-tags correct; sigstore 2021 + GA 2022 correct | **Strong** — end-to-end sign + verify sequence diagrams are the series' strongest pedagogical spine; trust-model reframing (key → identity + log) is senior-correct; honestly scopes "signed ≠ safe" | 7 diagrams vs 2–4 guideline (over by ~3); 9 empty fences (outputs without language tag); 1 raw `&` in Mermaid label (minor render risk) |
| 2 | `book-05/ch07-tuf` | 7 227 | 7 | ✅ PASS — all sections; learning goals 6; takeaways + Further reading (8 URLs); distributed lens (TUF for Sigstore root, PEP 458/480, Notary) | **PASS** — 4 roles (root/targets/snapshot/timestamp) with correct responsibilities, online/offline split, thresholds, client order (root→timestamp→snapshot→targets→download) correct; rollback/freeze/fast-forward/mix-and-match/endless-data defenses correctly mapped; delegation scoping + path_hash_prefixes correct; PEP 458 accepted 2019 + not fully deployed + PEP 480 draft/deferred correctly caveated; Sigstore TUF via go-tuf + `tuf-repo-cdn.sigstore.dev` correct | **Exemplary** — the most precise mechanisms chapter in Books 5–8; attack→defense table + role-damage table are textbook-quality; Sigstore-as-TUF-client section closes the loop on ch03 | **Length FLAG: 7 227 (~3% over)** — trimmable by ~250 words (compress consistent-snapshot detail); 0 labeled code fences (only Mermaid + empty fences) — for a framework spec chapter, 1–2 `json` metadata examples would close the STYLE code gap; no version pin for TUF spec |
| 3 | `book-06/ch01-oci-images` | 5 895 | 7 | ✅ PASS — all sections; 9 learning goals; takeaways + Further reading (7 URLs); distributed lens (content-addressing as blast-radius multiplier) | **PASS** — OCI specs (Image/Distribution/Runtime) + Docker→OCI handoff correct; manifest digest = image identity correct; compressed blob digest vs `diff_id` (uncompressed) + chain ID correct; whiteout/overlayfs + secret-leak via layer history correct; multi-stage builds + Referrers API (`subject` field) correct; mutable-tag TOCTOU correct | **Exemplary** — best "format as security property" exposition in Book 6; layer-model → secret-leak → min-base-arc is senior-complete; consistently ties format facts to signing/scanning/admission | 7 diagrams over guideline (but justified — index/manifest/layer graphs each earn theirs); no factual flags |
| 4 | `book-06/ch05-image-signing-k8s` | 6 274 | 7 | ✅ PASS — all sections; 7 learning goals; takeaways + Further reading (10 URLs); distributed lens (paved-road signing + platform inheritance) | **PASS** — cosign sign-by-digest + `.sig` tag vs OCI 1.1 Referrers distinguished correctly; keyless via Fulcio ~10-min cert + Rekor + SAN/issuer policy correct; admission flow (mutating → validate → etcd, `failurePolicy`) correct; **verify-and-run-the-same-digest** + TOCTOU mutating-webhook analysis correct; policy-controller vs Kyverno vs Connaisseur vs Ratify+Gatekeeper vs Binary Authorization correctly characterized; `mutateDigest: true` and `subjectRegExp`/`issuer` fields correct | **Strong** — the operational heart of Book 6; TOCTOU section with with/without pinning sequence diagram is the chapter's load-bearing contribution; tiered-rollout and fail-closed guidance is production-grade | 7 diagrams over guideline; `ClusterImagePolicy` `subjectRegExp` regex in example contains escaped dots — verify string renders correctly in YAML (minor); no factual flags |
| 5 | `book-07/ch02-commit-signing-identity` | 6 341 | 7 | ✅ PASS — all sections; 6 learning goals; takeaways + Further reading (9 URLs); distributed lens (identity fabric, SSO/SAML + workload identity for bots) | **PASS** — git `author`/`committer` unauthenticated + spoof via `user.name`/`--author` correct; GPG (`commit.gpgsign`/`user.signingkey`) vs SSH signing git 2.34 (Nov 2021) + `gpg.format ssh` + `gpg.ssh.allowedSignersFile` correct; `ssh-keygen -Y sign` + SSHSIG correct; S/MIME `gpg.format x509` correct; gitsign as `gpg.x509.program gitsign` + Fulcio/Rekor keyless commit flow correct; GitHub Verified = signature-valid + key-linked-to-account (not code-good, not account-uncompromised, not author) correctly scoped; `web-flow` key caveat correct; vigilant mode + `Require signed commits` correct | **Strong** — honest "what signing does and does not give you" + `Signed ≠ safe` with xz `Jia Tan` example is senior-appropriate anti-hype; bot-identity (GitHub App vs workload OIDC) is fleet-correct | 7 diagrams over guideline; no invented guidance; one link to `man.openbsd.org` should carry section anchor for stability (minor) |
| 6 | `book-07/ch03-branch-protection-review` | 7 718 | 7 | ✅ PASS — all sections; 6 learning goals; takeaways + Further reading (10 URLs); distributed lens (org-level rulesets + fleet enforcement) | **PASS** — two-person/separation-of-duties + SLSA Source track framing correct; GitHub classic protection vs rulesets (org-level, layering, bypass lists, evaluate mode) correct; GitLab protected branches + `prevent approval by author/committers/editing` correctly characterized; CODEOWNERS path-scoped review correct; dismiss-stale-approvals + enforce-for-admins gap correctly called out; xz social-engineering limit honestly scoped; `CVE-2024-3094` correct | **Strong** — most actionable Book 7 chapter; per-setting bypass-surface table + ruleset JSON example are production-grade; limits-of-review (§ underhanded C, review fatigue) are honest | **Length FLAG: 7 718 (~10% over)** — heaviest Book 7 sampled; trimmable ~700 words by compressing GitLab approval-rule API example and CODEOWNERS catalog; 7 diagrams over guideline |
| 7 | `book-08/ch02-adopting-slsa-s2c2f` | 7 500 | 8 | ✅ PASS — all sections; 6 learning goals; takeaways + Further reading (0 URLs — citation-style without hyperlinks); distributed lens (paved-road inheritance) | **PASS** — SLSA v1.0 Build track L0–L3 (L4 dropped in v1.0) + `slsa.dev/provenance/v1` + DSSE/in-toto framing correct; `slsa-github-generator` / `actions/attest-build-provenance` + OIDC keyless correct; S2C2F 8 practices + L1–L4 + 2022 Microsoft→OpenSSF donation correct; SSDF v1.1 (`csrc.nist.gov`) + PS/PW.4 + EO 14028 mapping correct; warn-then-enforce + risk-sequencing correctly prescribed | **Adequate** — strong roadmap structure (four phases) but 0 labeled code fences — as a *program* chapter this is understandable, but even 1 `yaml` paved-road template or `rego` policy snippet would meet STYLE's "real config" bar; SLSA "L3 for free-ish via hosted CI" correctly hedged | **Length FLAG: 7 500 (~7% over)**; 8 diagrams (highest sampled) — the S2C2F↔control-mapping flowchart duplicates the table and could be consolidated; Further reading has **0 hyperlinks** (all citations are prose names like `slsa.dev`, `github.com/...`, `csrc.nist.gov` without `https://`) — violates STYLE's Further-reading hyperlink bar |
| 8 | `book-08/ch06-incident-response` | 8 383 | 7 | ✅ PASS — all sections; 6 learning goals; takeaways + Further reading (0 URLs — citation-style); distributed lens (§ Preparation as fleet capability) | **PASS** — NIST SP 800-61 Rev2 + Rev3 (2025) + SANS PICERL correctly mapped; Log4Shell CVE-2021-44228 (Dec 9–10 2021) + 45046/45105/44832 cascade correct; SolarWinds SUNBURST/SUNSPOT ~18k vs ~100 presence-vs-exploitation gap + DGA `avsvmcloud[.]com` correct; Codecov Jan 31–Apr 1 2021 dwell correct; event-stream/flatmap-stream 2018 correct; mass credential rotation + rebuild-everything + transparency-log-for-key-compromise all correct | **Strong** — best incident pedagogy in Book 8; mode-A vs mode-B framing + per-incident scoping table are senior-complete; consistently ties response capability to the same platform built for prevention (SBOM inventory, registry chokepoint, ephemeral builds) | **Length FLAG: 8 383 (~20% over, heaviest sampled)** — needs ~1 300 words trimmed (compress worked-scenario narratives that repeat the § lifecycle); 7 diagrams over guideline; Further reading has **0 hyperlinks** (citations without `https://`, e.g., `NIST SP 800-61`, `FireEye/Mandiant`, `Apache Log4j` without URLs); only 2 labeled code fences (`bash`) for a chapter that could show `osv-scanner`/`jq`/`registry-admin` outputs more fully |

> Appendix-style notes per chapter (Mermaid validity, code coverage, link hygiene) are in §8.

---

## 5. Factual Verification Summary (2–4 Claims per Sampled Chapter — Reasoning Check)

> No live `web_extract` per claim in this pass; verification is reasoning + known 2026 references. Items marked `VERIFY LIVE` should be re-checked with `web_extract` before FINAL.

| Chapter | Claim 1 | Verdict | Claim 2 | Verdict | Claim 3 | Verdict | Claim 4 | Verdict |
|---------|---------|---------|---------|---------|---------|---------|---------|---------|
| **book-05/ch03** | Fulcio cert ~10 min | ✅ Correct | Rekor = Merkle-tree log, inclusion proof + SET + `integratedTime` inside window | ✅ Correct | CT log vs Rekor = two different logs (certs vs signing events) | ✅ Correct | `sigstore/root-signing` + TUF CDN + `cosign initialize` | ✅ Correct |
| **book-05/ch07** | 4 TUF roles + responsibilities (root/targets/snapshot/timestamp) + online/offline split | ✅ Correct | Thresholds + delegation scoping (`path_hash_prefixes`, terminating) | ✅ Correct | Client order root→timestamp→snapshot→targets→download | ✅ Correct | PEP 458 accepted 2019 not fully deployed + PEP 480 draft | ✅ Correct, honestly caveated |
| **book-06/ch01** | OCI Image/Dist/ Runtime specs; manifest digest = image identity; `diff_id` (uncompressed) vs blob digest (compressed) | ✅ Correct | Whiteout + overlayfs + `RUN rm` does not delete (secret leak) | ✅ Correct | Referrers API + `subject` field + `.sig` tag fallback | ✅ Correct | — | — |
| **book-06/ch05** | Admission flow: mutating→validate→etcd + `failurePolicy` Fail/Ignore | ✅ Correct | Verify-and-run-the-same-digest TOCTOU + mutating webhook pin | ✅ Correct | Keyless identity policy (`subjectRegExp`/`issuer` + Rekor) | ✅ Correct | Tool comparison (policy-controller/Kyverno `mutateDigest`/Connaisseur/Ratify+Gatekeeper gap/Binary Authorization) | ✅ Correct |
| **book-07/ch02** | SSH signing since git 2.34 (Nov 2021) + `allowedSignersFile` + `ssh-keygen -Y sign` | ✅ Correct | gitsign = keyless Fulcio/Rekor commit signing (`gpg.x509.program gitsign`) | ✅ Correct | GitHub Verified = sig-valid + key↔account (not code-good, not author) + `web-flow` key caveat | ✅ Correct | GPG vs SSH vs S/MIME vs gitsign friction table | ✅ Correct |
| **book-07/ch03** | Rulesets vs classic protection + CODEOWNERS + dismiss-stale + enforce-for-admins | ✅ Correct | GitLab `prevent approval by author/committers` + `disable_overriding_approvers` | ✅ Correct | Two-person → SLSA Source track | ✅ Correct | CVE-2024-3094 (xz) | ✅ Correct |
| **book-08/ch02** | SLSA v1.0 Build L0–L3 (L4 dropped), `slsa-framework/slsa-github-generator` reaches L3 via isolation | ✅ Correct | S2C2F 8 practices + 4 levels + internal-registry chokepoint | ✅ Correct | SSDF v1.1 + EO 14028 mapping | ✅ Correct | Aug 2022 Microsoft→OpenSSF donation | ✅ Correct |
| **book-08/ch06** | CVE-2021-44228 Dec 9–10 2021 + follow-ons 45046/45105/44832 + 2.17.1 | ✅ Correct | SolarWinds SUNBURST 18k vs ~100 + DGA + Golden SAML | ✅ Correct | Codecov Jan 31–Apr 1 2021 + mass rotation | ✅ Correct | event-stream/flatmap-stream 2018 targeted payload | ✅ Correct |

**Aggregate:** 0 confirmed hallucinations, 0 invented CVEs/stats/quotes, 0 marketing-language hits. Factual posture is the strongest dimension, matching the 145-ch audit.

---

## 6. Systemic Issues (Severity-Tagged)

### [MAJOR] Length discipline — 47% of Books 5–8 over 7 000; tail to 8 678

- **Evidence:** §3; sampled flags at 7 227 / 7 500 / 7 718 / 8 383. Even the *sample* mean is 7 093 — above the ceiling.
- **Risk:** At 36 ch the overage is ~10–20 k words of excess reading; at the series scale (145 ch) the same discipline failure compounds to 50–150 k words. Masks the guideline's "comprehensive not padded" intent. Book 8 is the heaviest (mean 7 460, 4 of 8 files over 7 000, 2 over 8 000).
- **Fix:** Trim pass targeting ≤7 000, with the 5 heaviest first (see Priority 1). Do not pad the 19 compliant files.

### [MAJOR] Diagram inflation — 100% of Books 5–8 at 7–8 Mermaid blocks (mean 7.08)

- **Evidence:** All 36 files at 7–8; guideline is 2–4 meaningful. Sampled diagrams are individually valid and pedagogically sound — the *count* is the problem, not the quality. Reflects the 4.4→7.0 enrichment overshooting.
- **Risk:** Visual fatigue; renderer load; authors of future volumes copying the inflated count. Not a correctness issue but a consistency and cost issue.
- **Fix:** Consolidate related flowcharts (e.g., Book 8 Ch 2's S2C2F mapping table vs flowchart duplicate), keep sequence diagrams and merge decorative flowcharts. Target 2–5 per chapter, 5 only for protocol-heavy chapters (TUF, admission, SLSA).

### [MINOR] Further-reading hyperlink gap — 12/36 have zero `https://` in Further reading

- **Evidence:** `book-05/ch01`, `ch02`, `book-06/ch08`, `ch09`, `ch10`, `book-07/ch07`, `book-08/ch01`, `ch02`, `ch03`, `ch05`, `ch06`, `ch07`. These entries are citation-style (RFC names, repo names, paper titles) without resolvable URLs. STYLE allows citation-style for unstable sources but requires stable URLs where they exist; these chapters omit them even for stable specs (SLSA, NIST, OCI). The 8 sampled governance chapters both lack URLs.
- **Risk:** Reader cannot verify or navigate to the spec version discussed — breaks the "name the version + provide a version-pinned URL" contract. Also breaks the `web_extract` pre-FINAL verification gate.
- **Fix:** Add `https://` hyperlinks for every versioned spec in Further reading; pin to the discussed version (e.g., `https://slsa.dev/spec/v1.0/`, `https://opencontainers.org/`).

### [MINOR] Code-fence language tags — many empty ` ``` ` fences

- **Evidence:** Per-file inventory shows 7–18 empty fences per file in Books 5–8 (e.g., `book-05/ch01` 9 empties, `book-05/ch04` 18 empties, `book-05/ch07` 7 empties with no labeled fences at all). These are outputs, tables, or JSON without a language tag.
- **Risk:** Low for rendering, but violates STYLE's "fence with correct language tags (`yaml`, `bash`, `json`, `rego`, …)" and breaks syntax highlighting and linting (`yamllint`/`go vet`) gates.
- **Fix:** Tag every fence: `json` for metadata, `text` for outputs where no better tag fits, `bash`/`yaml`/`rego` where applicable. Zero-labeled-code chapters (`ch01-crypto-foundations`, `ch07-tuf`, `book-08/ch01–03`, `ch05`) need 1–2 labeled examples added.

### [MINOR] Recency stamp — only 25% of Books 5–8 carry a 2025–2026 pin

- **Evidence:** Only 9/36 contain `2025`, `2026`, or `as of 2026`. Fast-moving areas (Sigstore endpoints, SLSA, PKI, regulatory landscape) lack an explicit freshness signal.
- **Risk:** Reader cannot tell if a claim was frozen at 2023 vs verified at 2026 — important for Sigstore, PKI policy, OCI 1.1 Referrers rollout.
- **Fix:** Add "(as of early 2026)" or version tag in intro + Further reading for Sigstore/PKI/OCI/governance chapters.

### [MINOR] Unlabeled-diagram redundancy + one raw `&` in Mermaid

- **Evidence:** Sampled scan found one `&` in a Mermaid label in `book-05/ch03` (`flowchart LR` with `&` in unquoted text). Otherwise Mermaid validity is high (all blocks parse, no `&`/`()` in unquoted labels beyond that one).
- **Risk:** GitHub Mermaid renderer may misrender that label.
- **Fix:** Quote or escape `&` in that label; otherwise diagram syntax is sound.

> No [BLOCKER] found in Books 5–8 sample: no mass factual error, no fabricated CVEs/specs, no structural non-compliance, no security anti-guidance.

---

## 7. Prioritized Correction List (What Must Be Fixed Before FINAL)

**Do not edit sampled chapters' substance for new volumes until Priorities 1–2 are landed. Priorities 3–4 are half-day each and should land in the same branch.**

### Priority 1 — Trim the heavy tail (MAJOR, ~1 day for 17 files)

- **Target:** All 17 files > 7 000 down to ≤ 7 000. Target Books 5–8 mean ~6 600. Do not trim the 19 compliant files.
- **How:** (a) collapse overlapping "why it matters" / distributed-lens paragraphs that restate the same thesis, (b) merge adjacent flowcharts (table→flowchart duplicates), (c) trim historical throat-clearing where the protocol section already covers it (Book 8 Ch 2 S2C2F history; Ch 6 worked scenarios repeat the lifecycle).
- **Trim order (heaviest first):**
  1. `book-08-governance-ir/ch08-metrics-reporting.md` (8 678 → ≤ 7 000)
  2. `book-08-governance-ir/ch06-incident-response.md` (8 383 → ≤ 7 000) — compress worked scenarios that repeat § lifecycle
  3. `book-05-signing-attestation/ch05-transparency-logs.md` (7 879 → ≤ 7 000)
  4. `book-07-source-security/ch05-backdoors-malicious-code.md` (7 844 → ≤ 7 000)
  5. `book-08-governance-ir/ch04-policy-as-code.md` (7 835 → ≤ 7 000)
  6. `book-07-source-security/ch03-branch-protection-review.md` (7 718 → ≤ 7 000)
  7. `book-07-source-security/ch04-secrets-in-source.md` (7 714)
  8. `book-06-cloud-native/ch03-base-images.md` (7 707)
  9. `book-08-governance-ir/ch02-adopting-slsa-s2c2f.md` (7 500 → ≤ 7 000) — consolidate 8 Mermaid blocks
  10. Then remaining 7 files > 7 000.
- **Verification:** Re-run `split()` wc per file + mean; commit with `PROGRESS.md` unchanged.

### Priority 2 — Consolidate diagrams + tag code fences (MAJOR, half-day automatable)

- **Diagrams:** For each of the 36 files, consolidate 7–8 → 2–5 by merging related flowcharts (especially governance chapters where a table and a flowchart say the same thing). Keep sequence diagrams (Sigstore sign/verify, TUF client workflow, admission TOCTOU) and collapse decorative variants. Guidance for future volumes: "5 only if a protocol demands it (TUF/admission-level) and you can justify each."
- **Fences:** Regex-tag every empty ` ``` ` that wraps JSON/YAML/bash/text with the correct language. Add 1–2 labeled examples to the 10 zero-labeled-code files. Priority: `book-05/ch07-tuf` (add `json` root/targets/snapshot example), `book-08/ch02` (add `yaml` ClusterImagePolicy or `rego`), `book-08/ch06` (add `bash` `osv-scanner`/`jq` output already in text but untagged).
- **Verification:** `grep -c '```mermaid'` mean should be 3–4; `grep -c '```$'` (empty fence) should be 0; `grep -c '```(bash|yaml|json|rego|…)'` should be ≥1 per chapter.

### Priority 3 — Further-reading hyperlink + recency pins (MINOR but high value, half-day)

- Add version-pinned `https://` URLs for every spec cited in Further reading where the spec has a stable URL:
  - `book-05/ch01–02`, `book-06/ch08–10`, `book-07/ch07`, `book-08/ch01–03`, `ch05–07` — add `https://slsa.dev/spec/v1.0/`, `https://www.opencontainers.org/`, `https://csrc.nist.gov/`, `https://spdx.dev/` / `https://cyclonedx.org/`, `https://www.sigstore.dev/` as appropriate.
  - Pin per sampled chapter: `book-05/ch03` add cosign/Fulcio/Rekor versions or "as of 2025–2026"; `book-05/ch07` add TUF spec version; `book-06/ch01` add OCI 1.1.
- Add "(verified against spec as of early 2026)" or explicit version tag in intro for every fast-moving chapter.
- **Verification:** No chapter's Further reading should have zero `https://` where a stable spec URL exists; spot-check 12 random URLs with `web_extract` must all 200.

### Priority 4 — Mermaid and link hygiene (MINOR, 1 hour)

- Fix the one raw `&` in `book-05/ch03`'s Mermaid label (quote the label).
- Confirm no trailing `>` artifacts remain: `grep -n 'https://.*>'` returned only 2 hits in the full 36 (both inside HTML/Mermaid, not autolink) — already clean, no action needed beyond the Mermaid quote fix.
- Verify every SLSA/Sigstore/SPDX citation in prose names the version (sampled chapters already do — `SLSA v1.0`, `SPDX`, `CycloneDX`).

### Priority 5 — Author guidance for remaining Books 5–8 maintenance

- **Length budget:** Enforce 4 000–7 000 hard ceiling in review — reject drafts > 7 300 at batch-review time.
- **Diagram budget:** "2–4 meaningful; 5 only if a protocol demands it and you can justify each in review." Reject 6+ without justification.
- **Further-reading bar:** Every chapter ≥6 entries with ≥4 resolvable URLs pinned to the discussed version. Citation without URL allowed only for mailing-list disclosures where URL is unstable.
- **Code bar:** Every chapter ≥2 labeled fences (`bash`/`yaml`/`json`/`rego`/`text`) with realistic, syntax-correct outputs.

---

## 8. Appendix — Detailed Per-Chapter Notes (Sampled)

### book-05/ch03 — Sigstore Architecture
- **Mermaid validity:** 7 flowcharts/sequences, all valid except one raw `&` in a label — quote it. `sequenceDiagram` with `autonumber` renders correctly.
- **Code:** 2 labeled (`bash`, `yaml`) + 9 empty (mostly annotated outputs/tables). Tag the empties as `text`/`json`/`bash` where applicable.
- **Further reading:** 8 entries, all with `https://` and version context (`sigstore.dev`, `fulcio.sigstore.dev`, `rekor.sigstore.dev`, `sigstore/root-signing`, `go-tuf`). Strong.
- **Risk framing:** Correctly states xz would have been signed by legitimate identity — no overclaim. `COSIGN_EXPERIMENTAL=1` correctly marked obsolete.

### book-05/ch07 — TUF
- **Mermaid validity:** 7 diagrams (attack→defense table companion flowcharts, online vs offline split, client `sequenceDiagram`). All labels quoted, no `&` issues.
- **Code gap:** 0 labeled fences — the one gap in the sample. A `json` root/targets/snapshot snippet would close it (e.g., `root.json` `keys`/`roles`/`threshold`).
- **Further reading:** 8 entries with URLs (TUF spec, PEP 458/480, Notary, Sigstore TUF CDN).
- **Terminology:** `consistent_snapshot` flag correctly tied to version-prefixed filenames — precise.

### book-06/ch01 — OCI Images
- **Mermaid validity:** 7 diagrams (index→manifest→layers graph, overlayfs stack, secret-leak flow). All valid, `flowchart TD/LR/TB` with `style` directives correct.
- **Code:** 14 labeled rich coverage (`bash`/`json`/`dockerfile`) — best in the sample.
- **Further reading:** 7 URLs (OCI specs, Distribution, crane/skopeo). Strong.
- **Length:** Lightest sampled (5 895) — demonstrates the guideline is achievable even for a format-heavy topic.

### book-06/ch05 — Image Signing in K8s
- **Mermaid validity:** 7 diagrams (build→registry→trust→cluster, admission flow, TOCTOU with/without pinning). All valid.
- **Code:** 7 labeled (`bash`/`yaml`) including complete `ClusterImagePolicy` with `subjectRegExp`/`issuer`/`ctlog`/`attestations`/`CUE`. Syntactically plausible; verify regex escaping in YAML single-quotes.
- **Further reading:** 10 URLs (policy-controller, Kyverno, Connaisseur, Rekor). Strong.
- **TOCTOU:** The "does it mutate the pod spec to the verified digest? is a gating question" framing is the right fleet lesson.

### book-07/ch02 — Commit Signing
- **Mermaid validity:** 7 diagrams (unsigned vs signed commit, GPG/SSH/gitsign comparison, Verified badge truth table). All valid.
- **Code:** 9 labeled rich (`bash`/`text`) — GPG, SSH signing config, `allowed_signers`, `gitsign verify`. Best CLI coverage in Book 7 sample.
- **Further reading:** 9 entries with URLs. One `man.openbsd.org/ssh-keygen.1` link should pin the section anchor for stability (minor).
- **Sensitive detail:** Honest about signing not preventing a compromised-laptop insider — correct.

### book-07/ch03 — Branch Protection
- **Mermaid validity:** 7 diagrams (direct-push→reject vs PR→gate, CODEOWNERS router, bypass-surface). All valid.
- **Code:** 4 labeled (`json` ruleset payload, `bash` GitLab API). Curly-quote hygiene in `json` — verify `—` vs `--` not mangled.
- **Further reading:** 10 entries with URLs.
- **Length note:** The GitLab approval-rule API example repeats the GitHub ruleset payload's structure — one could be trimmed.

### book-08/ch02 — Adopting SLSA & S2C2F
- **Mermaid validity:** 8 diagrams (six-ways-adoption-dies, SLSA ladder, S2C2F↔control mapping, phased roadmap). 8 is the highest in the sample; the S2C2F mapping duplicates the adjacent table — consolidate.
- **Code gap:** 0 labeled fences — understandable for a program/roadmap chapter, but 1 template (`yaml` pipeline or `rego` ingestion policy) would meet the bar.
- **Further reading:** 0 URLs — the one structural gap. Entries name `slsa.dev`, `github.com/slsa-framework/...`, `ossf/s2c2f`, `csrc.nist.gov` without `https://` hyperlinks. Must add them.
- **Stats:** `84%`/`5%` percentages are in the measurement section with correct "coverage tied to risk" framing — not fabricated global claims.

### book-08/ch06 — Incident Response
- **Mermaid validity:** 7 diagrams (mode A vs B, PICERL lifecycle, scoping via inventory, without/with C2 cut). All valid.
- **Code:** 2 labeled (`bash` `osv-scanner`/`jq` + pseudo-SQL). `registry-admin block` example is illustrative but plausible.
- **Further reading:** 0 URLs — same gap as Ch02. NIST SP 800-61, FireEye/Mandiant, Codecov post-mortem, Apache Log4j advisories, event-stream write-ups are all real sources cited without hyperlinks — add them.
- **Length note:** Heaviest sampled (8 383) — worked scenarios (Log4Shell, SolarWinds, Codecov, event-stream) each re-walk the lifecycle already in § lifecycle; compress by ~1 300 words by moving repeated steps to cross-refs.

---

## 9. What Was NOT Audited (and Should Be Before FINAL)

- **Full live verification of every Further-reading URL** (sampled reasoning only; recommend `web_extract` batch over all 36 Further-reading sections before FINAL — especially the 12 zero-URL chapters after they are patched).
- **Mermaid render test** (GitHub renderer not invoked; syntax checked via pattern — one raw `&` flagged).
- **Code execution** (`bash`/`yaml`/`json`/`rego` snippets are plausible but not executed; recommend `yamllint` + `go vet` / `opa check` batch before FINAL, especially for Book 6 admission policies and Book 5 in-toto provenance).
- **Cross-chapter terminology consistency** (e.g., `provenance` vs `attestation` vs `predicate` across Book 4/Ch03 and Book 5/Ch06/08 — spot-checked consistent, but a corpus-wide `search_files` for conflicting definitions is prudent).
- **Security anti-guidance scan at scale** (sampled chapters pass — no `curl | bash` without checksum, no broad `actions: write-all` — but a `search_files` for `curl.*|.*bash` and `permissions:` across all 36 should be run).

---

*Audit complete. No chapters were edited. Awaiting approval to proceed to correction pass on Priorities 1–4.*
