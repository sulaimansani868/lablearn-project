#!/usr/bin/env python3
"""
apply-missing-tutorial-footer-toc.py

Run this inside the tutorials/ folder.

What it fixes:
1) Adds a standard footer if a page is missing it.
2) Adds the mobile floating "On this page" control if a page is missing it.
3) Reuses the existing desktop TOC list so each page keeps its own section links.

Safe to run multiple times:
- already-updated pages are skipped
- HTML backups are saved as .bak on first edit
"""

from __future__ import annotations

import re
from pathlib import Path

SKIP_FILES = {"index.html"}
SHARED_JS_TAG = '<script src="../shared.js" defer></script>'

FOOTER_HTML = """\
  <footer>
    <div class="footer-logo">Lab<span>Learn</span></div>
    <ul class="footer-links">
      <li><a href="index.html">Tutorials</a></li>
      <li><a href="../calculator.html">Calculators</a></li>
      <li><a href="../contact.html">Contact</a></li>
      <li><a href="../index.html#donate">Donate</a></li>
    </ul>
    <div class="footer-copy">© 2025 LabLearn.</div>
  </footer>
"""

MOBILE_TOC_TEMPLATE = """\
  <!-- MOBILE FLOATING TOC (visible ≤ 900px) -->
  <button class="mob-toc-btn" id="mobTocBtn"
          aria-label="Open table of contents" aria-expanded="false"
          aria-controls="mobTocPanel">
    <span class="mob-toc-icon">☰</span> On this page
  </button>

  <div class="mob-toc-overlay" id="mobTocOverlay" aria-hidden="true"></div>

  <div class="mob-toc-panel" id="mobTocPanel" role="dialog"
       aria-label="Table of contents" aria-modal="true">
    <div class="mob-toc-handle"></div>
    <div class="mob-toc-head">
      <span class="mob-toc-head-label">On this page</span>
      <button class="mob-toc-close" id="mobTocClose" aria-label="Close">✕</button>
    </div>
    <div class="mob-toc-body">
      {toc_list_html}
    </div>
  </div>
"""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def extract_toc_list(html: str) -> str | None:
    """Grab the existing desktop toc list from the page and reuse it in the mobile panel."""
    m = re.search(
        r'<aside class="toc-sidebar">.*?<ul class="toc-list">(.*?)</ul>.*?</aside>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not m:
        return None
    return "      <ul class=\"toc-list\">\n" + m.group(1).strip("\n") + "\n      </ul>"


def ensure_footer(html: str) -> tuple[str, bool]:
    if "<footer>" in html.lower():
        return html, False

    body_close = re.search(r"\n\s*</body\s*>", html, flags=re.IGNORECASE)
    if not body_close:
        return html, False

    insert_at = body_close.start()
    updated = html[:insert_at].rstrip() + "\n\n" + FOOTER_HTML + "\n"
    updated += html[insert_at:]
    return updated, True


def ensure_mobile_toc(html: str) -> tuple[str, bool]:
    if 'id="mobTocBtn"' in html or "id='mobTocBtn'" in html:
        return html, False

    toc_list_html = extract_toc_list(html)
    if toc_list_html is None:
        return html, False

    mobile_block = MOBILE_TOC_TEMPLATE.format(toc_list_html=toc_list_html)

    # Prefer placing after the shared.js script tag if present.
    if SHARED_JS_TAG in html:
        updated = html.replace(SHARED_JS_TAG, SHARED_JS_TAG + "\n\n" + mobile_block, 1)
        return updated, True

    # Fallback: insert before </body>
    body_close = re.search(r"\n\s*</body\s*>", html, flags=re.IGNORECASE)
    if not body_close:
        return html, False

    insert_at = body_close.start()
    updated = html[:insert_at].rstrip() + "\n\n" + mobile_block + "\n" + html[insert_at:]
    return updated, True


def process_file(path: Path) -> str:
    if path.name in SKIP_FILES:
        return "– skipped"

    try:
        original = read_text(path)
    except Exception:
        return "✗ failed"

    updated = original
    changed = False

    updated, footer_changed = ensure_footer(updated)
    changed = changed or footer_changed

    updated, toc_changed = ensure_mobile_toc(updated)
    changed = changed or toc_changed

    if not changed:
        return "– skipped"

    backup = path.with_suffix(path.suffix + ".bak")
    if not backup.exists():
        write_text(backup, original)

    try:
        write_text(path, updated)
        return "✓ updated"
    except Exception:
        return "✗ failed"


def main() -> int:
    base = Path.cwd()
    html_files = sorted(p for p in base.glob("*.html") if p.name not in SKIP_FILES)

    if not html_files:
        print("No HTML files found. Run this from the tutorials/ folder.")
        return 1

    for path in html_files:
        result = process_file(path)
        icon = "✓" if result == "✓ updated" else "–" if result.startswith("–") else "✗"
        print(f"{icon}  {path.name}  {result}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
