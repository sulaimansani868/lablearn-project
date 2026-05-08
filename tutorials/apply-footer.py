#!/usr/bin/env python3
"""
apply-footer.py
───────────────
Inserts or replaces the <footer> in every HTML file in the LabLearn
tutorials folder.

Usage:
    python apply-footer.py

No dependencies beyond the Python standard library.
"""

import os, re

TUTORIALS_DIR = r"C:\Users\User\Downloads\LabLearn (16)\LabLearn\tutorials"

FOOTER = """\
<footer>
  <div class="footer-logo">Lab<span>Learn</span></div>
  <ul class="footer-links">
    <li><a href="index.html">Tutorials</a></li>
    <li><a href="../calculator.html">Calculators</a></li>
    <li><a href="../apps.html">Apps</a></li>
    <li><a href="../about.html">About</a></li>
    <li><a href="../contact.html">Contact</a></li>
    <li><a href="../index.html#donate">Donate</a></li>
  </ul>
  <div class="footer-copy">&copy; 2025 LabLearn. Free for students &amp; researchers.</div>
</footer>"""


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    has_footer = bool(re.search(r'<footer[\s>]', html, re.IGNORECASE))

    if has_footer:
        # Replace everything from <footer …> to </footer>
        new_html, count = re.subn(
            r'<footer[\s\S]*?</footer>',
            FOOTER,
            html,
            flags=re.IGNORECASE
        )
        if count == 0:
            return "FAILED — footer tag found but replacement failed"
        action = "replaced"
    else:
        # Insert before </body>
        if "</body>" not in html.lower():
            return "FAILED — no </body> tag found"
        new_html = re.sub(
            r'</body>',
            "\n" + FOOTER + "\n</body>",
            html,
            count=1,
            flags=re.IGNORECASE
        )
        action = "inserted"

    if new_html == html:
        return "skipped (no change needed)"

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    return action


def main():
    if not os.path.isdir(TUTORIALS_DIR):
        print(f"ERROR: Directory not found:\n  {TUTORIALS_DIR}")
        print("Edit the TUTORIALS_DIR variable at the top of this script and try again.")
        return

    html_files = sorted(
        f for f in os.listdir(TUTORIALS_DIR) if f.lower().endswith(".html")
    )

    if not html_files:
        print("No HTML files found in the tutorials folder.")
        return

    print(f"Found {len(html_files)} HTML file(s) in:\n  {TUTORIALS_DIR}\n")

    replaced = inserted = skipped = failed = 0

    for fname in html_files:
        path = os.path.join(TUTORIALS_DIR, fname)
        result = process_file(path)

        if result == "replaced":
            icon = "✓"; replaced += 1
        elif result == "inserted":
            icon = "+"; inserted += 1
        elif "skipped" in result:
            icon = "–"; skipped += 1
        else:
            icon = "✗"; failed += 1

        print(f"  {icon}  {fname:55s}  {result}")

    print(f"""
Done.
  ✓  Replaced existing footer : {replaced}
  +  Inserted new footer       : {inserted}
  –  Skipped (no change)       : {skipped}
  ✗  Failed (manual fix needed): {failed}
""")
    if failed:
        print("Open any ✗ files in a text editor and check that they have a</body> tag.")


if __name__ == "__main__":
    main()
