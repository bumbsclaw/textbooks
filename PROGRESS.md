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
- [ ] 1.04 Case Studies II: Dependency Attacks — event-stream, ua-parser-js, node-ipc, PyTorch — `ch04-case-studies-dependency-attacks.md`
- [ ] 1.05 Case Studies III: xz-utils, Codecov, and Log4Shell — `ch05-case-studies-xz-codecov-log4shell.md`
- [ ] 1.06 Trust, Threat Models, and the Economics of Supply Chain Risk — `ch06-trust-threat-models.md`
- [ ] 1.07 Risk Frameworks and Maturity Models: SLSA, SSDF, S2C2F — `ch07-frameworks-overview.md`
- [ ] 1.08 The Open Source Ecosystem: Sustainability, Maintainership, and Risk — `ch08-open-source-ecosystem.md`
- [ ] 1.09 Supply Chain Security in Distributed Backend Systems — `ch09-distributed-systems-lens.md`
- [ ] 1.10 Building a Supply Chain Security Program — `ch10-building-a-program.md`

## Book 2 — Dependency Management and Open Source Risk (`book-02-dependencies/`)

- [ ] 2.01 Package Managers and Registries: Architecture and Trust Models — `ch01-registries-trust-models.md`
- [ ] 2.02 Versioning, Resolution, and Lockfiles — `ch02-versioning-resolution-lockfiles.md`
- [ ] 2.03 Dependency Confusion, Typosquatting, and Namespace Attacks — `ch03-confusion-typosquatting.md`
- [ ] 2.04 Malicious Packages: Anatomy, Detection, and Analysis — `ch04-malicious-packages.md`
- [ ] 2.05 Vulnerability Databases and Identifiers: CVE, NVD, OSV, GHSA — `ch05-vulnerability-databases.md`
- [ ] 2.06 Software Composition Analysis in Depth — `ch06-sca-in-depth.md`
- [ ] 2.07 Reachability, Exploitability, and Prioritization — `ch07-reachability-prioritization.md`
- [ ] 2.08 Vendoring, Mirroring, and Internal Registries — `ch08-vendoring-internal-registries.md`
- [ ] 2.09 Dependency Update Strategy and Automation — `ch09-update-automation.md`
- [ ] 2.10 Evaluating Dependencies: Scorecards, Signals, and Policy — `ch10-evaluating-dependencies.md`

## Book 3 — SBOMs and Software Transparency (`book-03-sboms/`)

- [ ] 3.01 Why SBOMs: Transparency and the Regulatory Landscape — `ch01-why-sboms.md`
- [ ] 3.02 SPDX in Depth — `ch02-spdx.md`
- [ ] 3.03 CycloneDX in Depth — `ch03-cyclonedx.md`
- [ ] 3.04 SBOM Generation: Tools, Techniques, and Accuracy — `ch04-sbom-generation.md`
- [ ] 3.05 SBOM Distribution, Storage, and Querying at Scale — `ch05-sbom-at-scale.md`
- [ ] 3.06 VEX and Vulnerability Correlation — `ch06-vex.md`
- [ ] 3.07 SBOM Quality, Completeness, and Limitations — `ch07-sbom-quality-limitations.md`
- [ ] 3.08 SBOMs for Services: Containers, Serverless, and SaaS — `ch08-sboms-for-services.md`
- [ ] 3.09 Operationalizing SBOMs in the Enterprise — `ch09-operationalizing-sboms.md`

## Book 4 — Build and CI/CD Security (`book-04-build-cicd/`)

- [ ] 4.01 Build Systems: Architecture and Threat Model — `ch01-build-threat-model.md`
- [ ] 4.02 Hermetic and Reproducible Builds — `ch02-hermetic-reproducible-builds.md`
- [ ] 4.03 SLSA Build Levels and Provenance — `ch03-slsa-provenance.md`
- [ ] 4.04 CI/CD Platform Threat Models: Actions, GitLab, Jenkins, Tekton — `ch04-cicd-platform-threats.md`
- [ ] 4.05 Hardening GitHub Actions — `ch05-hardening-github-actions.md`
- [ ] 4.06 Secrets Management in CI/CD — `ch06-secrets-in-cicd.md`
- [ ] 4.07 Pipeline Poisoning: PPE, Cache, and Artifact Attacks — `ch07-pipeline-poisoning.md`
- [ ] 4.08 Ephemeral and Isolated Build Environments — `ch08-ephemeral-build-environments.md`
- [ ] 4.09 Build Observability and Anomaly Detection — `ch09-build-observability.md`
- [ ] 4.10 Designing a Secure Build Platform at Scale — `ch10-secure-build-platform.md`

## Book 5 — Signing, Provenance, and Attestation (`book-05-signing-attestation/`)

- [ ] 5.01 Cryptographic Foundations for Supply Chain Security — `ch01-crypto-foundations.md`
- [ ] 5.02 Classic Code Signing and Its Failure Modes — `ch02-classic-code-signing.md`
- [ ] 5.03 Sigstore Architecture: Cosign, Fulcio, Rekor — `ch03-sigstore-architecture.md`
- [ ] 5.04 Keyless Signing and Workload Identity — `ch04-keyless-signing.md`
- [ ] 5.05 Transparency Logs: Merkle Trees, Rekor, and CT Lessons — `ch05-transparency-logs.md`
- [ ] 5.06 in-toto: Attestations, Layouts, and Policies — `ch06-in-toto.md`
- [ ] 5.07 TUF: The Update Framework — `ch07-tuf.md`
- [ ] 5.08 Provenance Verification in Practice — `ch08-provenance-verification.md`
- [ ] 5.09 Key Management and PKI for the Enterprise — `ch09-key-management.md`
- [ ] 5.10 Designing Attestation-Based Deployment Gates — `ch10-deployment-gates.md`

## Book 6 — Container and Cloud-Native Supply Chain Security (`book-06-cloud-native/`)

- [ ] 6.01 Container Images: OCI Format, Layers, and Attack Surface — `ch01-oci-images.md`
- [ ] 6.02 Registries: Architecture, Trust, and Threats — `ch02-registries.md`
- [ ] 6.03 Base Image Strategy: Minimal, Distroless, Hardened — `ch03-base-images.md`
- [ ] 6.04 Image Scanning and Vulnerability Management — `ch04-image-scanning.md`
- [ ] 6.05 Image Signing and Verification in Kubernetes — `ch05-image-signing-k8s.md`
- [ ] 6.06 Admission Control and Policy Engines: OPA and Kyverno — `ch06-admission-policy.md`
- [ ] 6.07 Kubernetes Delivery Chains: Helm, Operators, GitOps — `ch07-k8s-delivery-chains.md`
- [ ] 6.08 Infrastructure as Code Supply Chain Risks — `ch08-iac-risks.md`
- [ ] 6.09 Serverless, Managed Services, and the Cloud Provider Chain — `ch09-serverless-managed.md`
- [ ] 6.10 A Cloud-Native Supply Chain Reference Architecture — `ch10-reference-architecture.md`

## Book 7 — Source, Code, and Insider Threat Security (`book-07-source-security/`)

- [ ] 7.01 Source Code Management: Threat Model and Integrity — `ch01-scm-threat-model.md`
- [ ] 7.02 Commit Signing and Developer Identity — `ch02-commit-signing-identity.md`
- [ ] 7.03 Branch Protection, Review, and Two-Person Rules — `ch03-branch-protection-review.md`
- [ ] 7.04 Secrets in Source: Detection and Remediation — `ch04-secrets-in-source.md`
- [ ] 7.05 Backdoors and Malicious Code: From Underhanded C to Trusting Trust — `ch05-backdoors-malicious-code.md`
- [ ] 7.06 Insider Threats and Account Takeover — `ch06-insider-threats-ato.md`
- [ ] 7.07 AI-Generated Code and the Model Supply Chain — `ch07-ai-code-model-supply-chain.md`
- [ ] 7.08 Repository Integrity at Scale — `ch08-repo-integrity-at-scale.md`

## Book 8 — Governance, Compliance, and Incident Response (`book-08-governance-ir/`)

- [ ] 8.01 The Regulatory Landscape: EO 14028, NIST SSDF, EU CRA — `ch01-regulatory-landscape.md`
- [ ] 8.02 Adopting SLSA and S2C2F: Roadmaps That Work — `ch02-adopting-slsa-s2c2f.md`
- [ ] 8.03 Vendor and Third-Party Software Risk — `ch03-vendor-risk.md`
- [ ] 8.04 Policy as Code and Continuous Compliance — `ch04-policy-as-code.md`
- [ ] 8.05 Detecting Supply Chain Compromise — `ch05-detecting-compromise.md`
- [ ] 8.06 Incident Response for Supply Chain Events — `ch06-incident-response.md`
- [ ] 8.07 Threat Intelligence and Information Sharing — `ch07-threat-intelligence.md`
- [ ] 8.08 Metrics, Audits, and Executive Reporting — `ch08-metrics-reporting.md`

## Log

- 2026-07-31: Repo initialized; plan, style guide, and book scaffolding created.
- 2026-07-31: Batch 1 done (1.01–1.03), committed and pushed. Next: batch 2 = 1.04, 1.05, 1.06.
