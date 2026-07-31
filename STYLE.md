# Style and Quality Guide for Authors

Every chapter in this suite must follow these conventions.

## Audience and voice

- Reader: a **senior backend software engineer** building distributed systems. Assume
  fluency in Linux, containers, Kubernetes, CI/CD, HTTP/gRPC, databases, and at least two
  mainstream languages. Do **not** explain basic programming or basic networking.
- Depth over breadth: explain *mechanisms*, not just names of tools. When a tool is
  discussed, explain the architecture and protocol underneath it.
- Voice: direct, technical, precise. No marketing language. It is fine to state trade-offs
  and to criticize weak practices, with justification.

## Accuracy

- Real incidents (SolarWinds, xz-utils, Codecov, event-stream, Log4Shell, 3CX, …) must be
  described accurately: correct dates, correct mechanism, correct scope. If a detail is
  uncertain, describe it at the level of certainty you actually have.
- Standards and specs (SLSA, SPDX, CycloneDX, in-toto, TUF, Sigstore, NIST SSDF, EU CRA)
  must be described per their actual published versions; name the version you describe
  (e.g., "SLSA v1.0", "CycloneDX 1.6", "SPDX 3.0").
- Never invent CVE numbers, dates, statistics, or quotes. Prefer "roughly" or omission
  over fabricated precision.

## Structure of a chapter

1. Title as `# Chapter N — Title`.
2. A short *What this chapter covers* paragraph plus a bulleted list of learning goals.
3. Body in `##` sections, with `###` subsections as needed.
4. Concrete examples: real commands, real config, real code, realistic outputs.
5. A **distributed-systems lens**: every chapter should connect the topic to the realities
   of large-scale backend engineering (many services, many teams, many repos, high deploy
   frequency).
6. End with `## Key takeaways` (bulleted) and `## Further reading` (real specs, papers,
   posts — no fabricated links; prefer stable URLs like specs and official docs).

## Diagrams

- Use **Mermaid** fenced blocks (```` ```mermaid ````) for diagrams; GitHub renders them.
- Use diagrams wherever they genuinely aid explanation: attack flows (`sequenceDiagram`),
  architectures (`flowchart`/`graph`), state machines, trust relationships. Aim for at
  least 2–4 meaningful diagrams per chapter — but only where they help.
- Keep Mermaid syntax simple and valid. Avoid exotic features that GitHub's renderer may
  not support. Quote node labels containing special characters. Avoid `&`, `(`, `)` in
  unquoted labels.
- ASCII tables (GitHub Markdown tables) for comparisons.

## Code and config examples

- Fence with correct language tags (`yaml`, `bash`, `go`, `python`, `json`, `rego`, …).
- Examples must be plausible and syntactically correct; prefer real tool syntax
  (`cosign sign`, `syft`, `osv-scanner`, GitHub Actions YAML, Kyverno policies, …).
- Show *outputs* where instructive, trimmed for readability.

## Length

- Target **4,000–7,000 words** per chapter (excluding code/diagrams). Comprehensive, not
  padded. Every section must earn its place.

## Cross-referencing

- Refer to other books/chapters by their number and title in prose (e.g., "see Book 5,
  Chapter 3 — Sigstore Architecture"). Relative links when the target file is known.
