#!/usr/bin/env python3
"""
Render Markdown chapters → A5 PDF (narrow margins) via weasyprint.

Usage:
  python3 scripts/build_a5_pdf.py                    # all volumes
  python3 scripts/build_a5_pdf.py vol-07-system-design  # one volume
  python3 scripts/build_a5_pdf.py --companion          # companion series only

Output: ~/textbooks/output/a5/<volume-slug>.pdf
"""

import sys, os, re, subprocess, tempfile, hashlib, shutil, time
from pathlib import Path
from textwrap import dedent

# ── Paths ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output" / "a5"
MERMAID_CACHE = ROOT / "output" / ".mermaid-cache"
MERMAID_CACHE.mkdir(parents=True, exist_ok=True)

# ── Volume order and titles ──────────────────────────────────────────────
VOLUMES = [
    ("vol-01-computer-architecture",       "Computer Architecture"),
    ("vol-02-operating-systems-linux",     "Operating Systems and Linux"),
    ("vol-03-networking",                  "Networking"),
    ("vol-04-concurrency",                 "Concurrency and Parallelism"),
    ("vol-05-databases",                   "Databases and Storage Systems"),
    ("vol-06-distributed-systems",         "Distributed Systems"),
    ("vol-07-system-design",               "System Design and Architecture"),
    ("vol-08-apis",                        "APIs and Service Design"),
    ("vol-09-security-auth",               "Security, Authentication, and Cryptography"),
    ("vol-10-messaging-streaming",         "Messaging, Streaming, and Event Systems"),
    ("vol-11-reliability-sre",             "Reliability, Observability, and SRE"),
    ("vol-12-cloud-infra",                 "Cloud, Containers, and Infrastructure"),
    ("vol-13-runtimes",                    "Language Runtimes"),
    ("vol-14-algorithms",                  "Data Structures and Algorithms"),
    ("vol-15-swe-practice",                "Software Engineering Practice"),
]

COMPANION = [
    ("book-01-foundations",                "Foundations of Software Supply Chain Security"),
    ("book-02-dependencies",              "Dependency Management and Open Source Risk"),
    ("book-03-sboms",                     "SBOMs and Software Transparency"),
    ("book-04-build-cicd",                "Build and CI/CD Security"),
    ("book-05-signing-attestation",       "Signing, Provenance, and Attestation"),
    ("book-06-cloud-native",              "Cloud-Native Supply Chain Security"),
    ("book-07-source-security",           "Source, Code, and Insider Threat Security"),
    ("book-08-governance-ir",             "Governance, Compliance, and Incident Response"),
]


# ── CSS ──────────────────────────────────────────────────────────────────
CSS = dedent("""\
@page {
    size: A5;
    margin: 12mm 12mm 14mm 12mm;
    @bottom-center {
        content: counter(page);
        font-family: "DejaVu Sans", sans-serif;
        font-size: 8pt;
        color: #666;
    }
}

body {
    font-family: "DejaVu Serif", "Noto Serif", serif;
    font-size: 9pt;
    line-height: 1.45;
    color: #1a1a1a;
}

h1 {
    font-family: "DejaVu Sans", sans-serif;
    font-size: 16pt;
    font-weight: bold;
    margin-top: 0;
    margin-bottom: 6mm;
    page-break-before: always;
    color: #111;
    border-bottom: 1.5pt solid #333;
    padding-bottom: 3mm;
}
h1:first-of-type { page-break-before: avoid; }

h2 {
    font-family: "DejaVu Sans", sans-serif;
    font-size: 11pt;
    font-weight: bold;
    margin-top: 5mm;
    margin-bottom: 3mm;
    color: #222;
    page-break-after: avoid;
}

h3 {
    font-family: "DejaVu Sans", sans-serif;
    font-size: 9.5pt;
    font-weight: bold;
    margin-top: 4mm;
    margin-bottom: 2mm;
    color: #333;
    page-break-after: avoid;
}

p { margin: 0 0 2mm 0; text-align: justify; hyphens: auto; }

ul, ol { margin: 0 0 2mm 4mm; padding-left: 3mm; }
li { margin-bottom: 1mm; }

blockquote {
    border-left: 2pt solid #999;
    padding: 1mm 3mm;
    margin: 2mm 0 2mm 0;
    background: #f8f8f8;
    font-size: 8.5pt;
    color: #444;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 2mm 0 3mm 0;
    font-size: 8pt;
    page-break-inside: auto;
}
th, td {
    border: 0.5pt solid #bbb;
    padding: 1.5mm 2mm;
    text-align: left;
    vertical-align: top;
}
th {
    background: #eee;
    font-weight: bold;
    font-family: "DejaVu Sans", sans-serif;
}
tr { page-break-inside: avoid; }

pre {
    background: #f4f4f4;
    border: 0.5pt solid #ddd;
    border-radius: 2pt;
    padding: 2mm 3mm;
    margin: 2mm 0 3mm 0;
    font-family: "DejaVu Sans Mono", "Noto Sans Mono", monospace;
    font-size: 7.5pt;
    line-height: 1.35;
    overflow-wrap: break-word;
    white-space: pre-wrap;
    page-break-inside: avoid;
}

code {
    font-family: "DejaVu Sans Mono", "Noto Sans Mono", monospace;
    font-size: 8pt;
    background: #f0f0f0;
    padding: 0.2mm 1mm;
    border-radius: 1pt;
}

pre code {
    background: none;
    padding: 0;
    font-size: inherit;
}

img, .mermaid-img {
    display: block;
    max-width: 100%;
    margin: 2mm auto 3mm auto;
    page-break-inside: avoid;
}

.mermaid-img img {
    max-width: 100%;
    height: auto;
}

hr {
    border: none;
    border-top: 0.5pt solid #ccc;
    margin: 4mm 0;
}

/* TOC */
.toc { page-break-after: always; }
.toc h2 { font-size: 13pt; margin-bottom: 4mm; }
.toc ul { list-style: none; padding: 0; }
.toc li { margin-bottom: 1.5mm; font-size: 9pt; }
.toc li a { text-decoration: none; color: #333; }

/* Title page */
.title-page {
    page-break-after: always;
    text-align: center;
    padding-top: 30mm;
}
.title-page h1 {
    font-size: 20pt;
    border: none;
    page-break-before: avoid;
    margin-bottom: 5mm;
}
.title-page .subtitle {
    font-size: 12pt;
    color: #555;
    margin-bottom: 10mm;
}
.title-page .meta {
    font-size: 9pt;
    color: #777;
}
""")


# ── Mermaid rendering ────────────────────────────────────────────────────
def render_mermaid(code: str, index: int) -> str:
    """Render a mermaid code block to a PNG, return the <img> tag."""
    h = hashlib.md5(code.encode()).hexdigest()[:12]
    out = MERMAID_CACHE / f"mm_{h}.png"
    # If already cached, return immediately
    if out.exists() and out.stat().st_size > 0:
        return f'<div class="mermaid-img"><img src="file://{out}" alt="diagram"></div>'
    # Retry loop for transient Puppeteer/Chromium failures (concurrent mmdc collisions)
    for attempt in range(3):
        if out.exists() and out.stat().st_size > 0:
            return f'<div class="mermaid-img"><img src="file://{out}" alt="diagram"></div>'
        # Small jitter to de-conflict concurrent Chromium launches
        if attempt > 0:
            time.sleep(0.5 * attempt)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                subprocess.run(
                    ["mmdc", "-i", f.name, "-o", str(out), "-w", "800", "-b", "white",
                     "--puppeteerConfigFile", "/tmp/pptr.json"],
                    capture_output=True, timeout=45, check=True
                )
                if out.exists() and out.stat().st_size > 0:
                    return f'<div class="mermaid-img"><img src="file://{out}" alt="diagram"></div>'
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                # Remove zero-byte file on failure so retry can recreate
                try:
                    if out.exists() and out.stat().st_size == 0:
                        out.unlink()
                except:
                    pass
                if attempt == 2:
                    print(f"  WARN: mermaid render failed after 3 attempts (block {index}): {str(e)[:120]}", flush=True)
            finally:
                try:
                    os.unlink(f.name)
                except:
                    pass
    # Final fallback only after 3 failures — include error hint
    print(f"  WARN: mermaid block {index} fell back to raw code", flush=True)
    return f'<pre><code>{code}</code></pre>'


# ── Markdown → HTML ──────────────────────────────────────────────────────
def md_to_html(md_text: str) -> str:
    """Convert markdown to HTML, rendering mermaid blocks to images."""
    import markdown as md_mod
    from markdown.extensions.codehilite import CodeHiliteExtension
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.fenced_code import FencedCodeExtension
    from markdown.extensions.toc import TocExtension

    # Pre-process: extract mermaid blocks and replace with placeholders
    mermaid_blocks = []
    def replace_mermaid(m):
        idx = len(mermaid_blocks)
        mermaid_blocks.append(m.group(1))
        return f"MERMAID_PLACEHOLDER_{idx}"

    processed = re.sub(r'```mermaid\n(.*?)```', replace_mermaid, md_text, flags=re.DOTALL)

    # Convert markdown to HTML
    html = md_mod.markdown(
        processed,
        extensions=[
            FencedCodeExtension(),
            CodeHiliteExtension(css_class="highlight", guess_lang=True),
            TableExtension(),
            TocExtension(permalink=False),
            "md_in_html",
        ]
    )

    # Replace placeholders with rendered mermaid images
    for idx, code in enumerate(mermaid_blocks):
        img_tag = render_mermaid(code, idx)
        html = html.replace(f"MERMAID_PLACEHOLDER_{idx}", img_tag)

    return html


# ── Build one volume ─────────────────────────────────────────────────────
def build_volume(slug: str, title: str, output_dir: Path):
    vol_dir = ROOT / slug
    if not vol_dir.exists():
        print(f"  SKIP {slug} — directory not found")
        return

    # Collect chapter files in order
    chapters = sorted(vol_dir.glob("ch*.md"))
    if not chapters:
        print(f"  SKIP {slug} — no ch*.md files")
        return

    print(f"  Building {slug} ({len(chapters)} chapters)...")

    # Build HTML
    body_parts = []

    # Title page
    body_parts.append(f"""
    <div class="title-page">
        <h1>The Backend Engineer's Library</h1>
        <div class="subtitle">{title}</div>
        <div class="meta">Volume {slug.split('-')[1].lstrip('0') if slug.startswith('vol-') else 'C' + slug.split('-')[1]}</div>
    </div>
    """)

    # TOC
    body_parts.append('<div class="toc"><h2>Contents</h2><ul>')
    for ch in chapters:
        name = ch.stem  # e.g. ch01-principles
        # Try to extract title from first line
        first_line = ch.read_text(errors="ignore").split("\n")[0]
        ch_title = first_line.lstrip("# ").strip()
        if ch_title.startswith("Chapter"):
            ch_title = ch_title.split("—", 1)[-1].strip() if "—" in ch_title else ch_title
        body_parts.append(f'<li><a href="#{name}">{ch_title}</a></li>')
    body_parts.append('</ul></div>')

    # Chapters
    for ch in chapters:
        name = ch.stem
        md_text = ch.read_text(errors="ignore")
        html_content = md_to_html(md_text)
        body_parts.append(f'<div id="{name}">{html_content}</div>')

    full_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{"".join(body_parts)}</body></html>"""

    # Write temp HTML
    html_path = output_dir / f"{slug}.html"
    pdf_path = output_dir / f"{slug}.pdf"
    html_path.write_text(full_html, encoding="utf-8")

    # Render PDF via weasyprint
    try:
        import weasyprint
        doc = weasyprint.HTML(filename=str(html_path), base_url=str(ROOT))
        doc.write_pdf(str(pdf_path))
        size_kb = pdf_path.stat().st_size // 1024
        # Count pages
        r = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True, text=True)
        pages = "?"
        for line in r.stdout.splitlines():
            if "Pages:" in line:
                pages = line.split(":")[-1].strip()
        print(f"  ✓ {slug}: {pdf_path.name} ({size_kb}KB, {pages} pages)")
    except Exception as e:
        print(f"  ✗ {slug}: {e}")


# ── Main ─────────────────────────────────────────────────────────────────
def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    targets = sys.argv[1:] if len(sys.argv) > 1 else []

    if "--companion" in targets:
        vols = COMPANION
        print("Building Companion Series PDFs (A5)...")
    elif targets:
        # Filter to specific volumes
        vols = [(s, t) for s, t in VOLUMES + COMPANION if s in targets]
        if not vols:
            print(f"No matching volumes for: {targets}")
            sys.exit(1)
        print(f"Building {len(vols)} volume(s)...")
    else:
        vols = VOLUMES
        print("Building Main Library PDFs (A5)...")

    for slug, title in vols:
        build_volume(slug, title, OUTPUT)

    print(f"\nDone. PDFs in: {OUTPUT}")


if __name__ == "__main__":
    main()
