#!/usr/bin/env python3
# fix-layout.py
# Automatically fixes two structural bugs in tutorial HTML files:
#   Bug 1 - inserts missing </article> before <div class="tut-nav">
#   Bug 2 - inserts missing </div> to close tutorial-layout after tut-nav
#
# A .bak backup of every file is saved before changes are made.
# Run audit-layout.py again afterwards to confirm all issues are resolved.
#
# Usage:
#   cd into the tutorials folder, then run:
#   python fix-layout.py

import os
import re
import shutil

TUTORIALS_DIR = "."
SKIP_FILES    = {"index.html"}


def fix_file(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    original = html
    actions  = []

    # ── Bug 1: insert </article> before <div class="tut-nav"> ────────────
    has_article_open  = bool(re.search(r'<article\b', html))
    has_article_close = "</article>" in html

    if has_article_open and not has_article_close:
        # Insert </article> on its own line just before the tut-nav div
        pattern = re.compile(r'(\s*)(<div class="tut-nav">)')
        if pattern.search(html):
            html = pattern.sub(
                lambda m: "\n\n      </article>\n" + m.group(1) + m.group(2),
                html,
                count=1
            )
            actions.append("inserted </article>")
        else:
            actions.append("SKIP Bug1 -- tut-nav div not found")

    # ── Bug 2: insert </div> to close tutorial-layout after tut-nav ───────
    # Re-check on the (possibly already patched) html
    lines        = html.splitlines()
    depth        = 0
    layout_depth = None
    closed       = False

    for line in lines:
        opens  = len(re.findall(r'<div\b', line))
        closes = len(re.findall(r'</div>', line))
        if "tutorial-layout" in line:
            layout_depth = depth + 1
        depth += opens - closes
        if layout_depth is not None and depth < layout_depth:
            closed = True
            break

    if layout_depth is not None and not closed:
        # Insert </div> immediately after the closing </div> of tut-nav
        # Pattern: the tut-nav closing tag followed by a blank line or mob-toc
        pattern = re.compile(
            r'([ \t]*</div>[ \t]*\n)'          # closing </div> of tut-nav
            r'(\s*\n|\s*<(?:button|div)\s+class="mob-toc)'  # blank line or mob-toc
        )
        # Find the tut-nav block first, then look for its closing tag
        tut_nav_match = re.search(r'<div class="tut-nav">', html)
        if tut_nav_match:
            search_from = tut_nav_match.start()
            m = pattern.search(html, search_from)
            if m:
                insert_at = m.start(2)
                html = html[:insert_at] + \
                       "\n  </div><!-- /tutorial-layout -->\n" + \
                       html[insert_at:]
                actions.append("inserted </div> for tutorial-layout")
            else:
                actions.append("SKIP Bug2 -- closing pattern after tut-nav not found")
        else:
            actions.append("SKIP Bug2 -- tut-nav div not found")

    if html == original:
        return "skipped -- no changes needed"

    # Save backup then write fixed file
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    return "fixed  [" + ", ".join(actions) + "]"


def main():
    if not os.path.isdir(TUTORIALS_DIR):
        print("ERROR: Run this script from inside the tutorials folder.")
        input("\nPress Enter to close...")
        return

    html_files = sorted(
        f for f in os.listdir(TUTORIALS_DIR)
        if f.lower().endswith(".html") and f not in SKIP_FILES
    )

    print("fix-layout.py")
    print("=" * 70)
    print("Processing " + str(len(html_files)) + " file(s)...")
    print("Backups saved as filename.html.bak before any changes.")
    print("")

    fixed = skipped = failed = 0

    for fname in html_files:
        path   = os.path.join(TUTORIALS_DIR, fname)
        result = fix_file(path)

        if result.startswith("fixed"):
            icon = "OK"; fixed += 1
        elif result.startswith("skipped"):
            icon = "--"; skipped += 1
        else:
            icon = "!!"; failed += 1

        print("  " + icon + "  " + fname.ljust(52) + "  " + result)

    print("")
    print("=" * 70)
    print("Summary:")
    print("  Fixed   : " + str(fixed))
    print("  Skipped : " + str(skipped) + "  (already correct)")
    print("  Failed  : " + str(failed)  + "  (check manually)")

    if failed:
        print("")
        print("For !! files, open them in a text editor and manually:")
        print("  1. Add </article> before <div class=\"tut-nav\">")
        print("  2. Add </div> after the tut-nav closing </div>")

    print("")
    print("Run audit-layout.py again to confirm all issues are resolved.")

    input("\nPress Enter to close...")


if __name__ == "__main__":
    main()
