# Chapter 2 — A Taxonomy of Supply Chain Attacks

*What this chapter covers.* Chapter 1 mapped the anatomy of a modern software supply chain — source, build, distribution, and consumption — and enumerated its attack surface. This chapter imposes order on the attacks themselves. We build a two-axis classification: **where in the chain the compromise occurs** (aligned with the SLSA v1.0 threat model's threats A–H) and **how trust is subverted** (technical compromise, social engineering, or legitimate-but-malicious action). We then catalog the named attack patterns you will encounter in incident reports and vendor pitches — typosquatting, dependency confusion, repojacking, build-time injection, update hijacking, and the rest — and pin each one to a precise mechanism, the attacker capability it requires, its blast radius, its detectability, and a real incident that exemplifies it. Finally, we compare our taxonomy honestly against MITRE ATT&CK, SLSA, and the academic literature, and close with the distributed-systems view: which classes actually dominate for organizations running large microservice fleets with internal registries.

Learning goals:

- Explain why a shared attack taxonomy matters for threat modeling, control mapping, and cross-incident comparison — and what a bad taxonomy costs you.
- Classify any supply chain incident along two axes: chain stage (source, build, distribution, consumption) and trust-subversion mode (technical, social, legitimate-but-malicious).
- Describe the precise mechanism of each named attack pattern, from typosquatting to compile-time backdoors, without hand-waving.
- For each pattern, state the attacker capability required, the typical blast radius, and how detectable it is in practice.
- Relate the SLSA v1.0 threats A–H, MITRE ATT&CK T1195, and the Ladisa et al. taxonomy to each other and know where each is silent.
- Identify which attack classes matter most for an organization with hundreds of services, internal packages, and an internal registry — and which team owns each class.

## Why taxonomy matters

Security engineering runs on shared vocabulary. When a colleague says "SQL injection," you know the mechanism, the preconditions, the fix, and roughly where to look in the codebase. Supply chain security in the early 2020s lacked that shared vocabulary: the same incident would be described as "a dependency attack," "a build compromise," or "an npm hack" depending on who wrote the postmortem, and the imprecision had real costs.

Three concrete costs, in order of how often they bite:

**Threat modeling degenerates into anecdote-matching.** Without a taxonomy, teams model "the SolarWinds scenario" and "the xz scenario" as monoliths. But SolarWinds (Book 1, Chapter 3) is a *build-process compromise via technical means*, and xz-utils (Book 1, Chapter 5) is a *source compromise via long-horizon social engineering*. The controls that address one do almost nothing against the other. A taxonomy lets you enumerate the classes systematically and ask, per class, "what stops this here?" — instead of replaying famous incidents and hoping the next attacker is unoriginal.

**Control mapping becomes unfalsifiable.** Vendors and internal platform teams alike claim their control "prevents supply chain attacks." Prevents *which*? Artifact signing (Book 5) does nothing against a malicious maintainer who signs their own backdoor. SCA scanning (Book 2, Chapter 6) does nothing against a compromised build platform. Provenance verification (Book 5, Chapter 8) does nothing against typosquatting, because the typosquatted package has perfectly valid provenance — for the wrong package. A taxonomy turns "we're covered" into a coverage matrix with visible holes.

**Incident comparison across organizations fails.** Information sharing (Book 8, Chapter 7) depends on comparable categories. If one org reports "npm account takeover with malicious patch release" and another reports "malicious update to a JavaScript library," an analyst cannot tell whether these are the same campaign, the same technique by different actors, or different techniques entirely. Taxonomies are what make incident corpora queryable.

A useful taxonomy for this domain must satisfy two requirements that are in mild tension. It must be **organized by defender-relevant structure** — controls attach to places in the chain, so the primary axis should be *where* the compromise occurs. And it must capture **attacker-relevant structure** — the same place can be reached by stolen credentials, by patient social engineering, or by a legitimate owner turning hostile, and those require different defenses (credential hygiene versus contributor vetting versus update gating). Hence two axes, not one.

## Axis one: where in the chain the compromise occurs

The primary axis follows the flow of software from a developer's intent to a consumer's runtime. This aligns with the SLSA v1.0 threat model, which labels its threats A through H along the same pipeline. We group them into four stages.

```mermaid
flowchart LR
    subgraph SRC["Source stage"]
        DEV["Developer"] --> SCM["Source repo"]
    end
    subgraph BLD["Build stage"]
        SCM --> CI["Build platform"]
        DEPS["External dependencies"] --> CI
    end
    subgraph DIST["Distribution stage"]
        CI --> REG["Registry / update channel"]
        REG --> CDN["Mirrors and CDNs"]
    end
    subgraph CONS["Consumption stage"]
        CDN --> USER["Consumer resolve + install"]
    end

    A1["A: unauthorized change<br/>B: repo compromise<br/>malicious maintainer"] -.-> SRC
    A2["C: modified source at build<br/>D: compromised dependency<br/>E: build process compromise"] -.-> BLD
    A3["F: