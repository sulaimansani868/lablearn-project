#!/usr/bin/env python3
# audit-layout.py
# Checks every tutorial HTML file for two structural bugs:
#   Bug 1 - article tag opened but never explicitly closed
#   Bug 2 - tutorial-layout div not balanced (mob-toc or footer trapped inside)
#
# Usage:
#   cd into the tutorials folder, then run:
#   python audit-layout.py

import os
import re

TUTORIALS_DIR = "."
SKIP_FILES    = {"index.html"}


def audit_file(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    lines = html.splitlines()

    issues = []

    # Bug 1: explicit </article> present?
    has_article_open  = bool(re.search(r'<article\b', html))
    has_article_close = "</article>" in html

    if has_article_open and not has_article_close:
        issues.append("Bug 1 -- <article> opened but </article> never written")

    # Bug 2: track div depth through tutorial-layout
    depth            = 0
    layout_depth     = None
    layout_closed_at = None
    mob_toc_line     = None
    footer_line      = None

    for i, line in enumerate(lines, 1):
        opens  = len(re.findall(r'<div\b', line))
        closes = len(re.findall(r'</div>', line))

        if "tutorial-layout" in line:
            layout_depth = depth + 1

        depth += opens - closes

        if mob_toc_line is None and (
            'mob-toc-panel' in line or 'mob-toc-overlay' in line
        ):
            mob_toc_line = (i, depth)

        if footer_line is None and re.search(r'<footer\b', line):
            footer_line = (i, depth)

        if layout_depth is not None and layout_closed_at is None:
            if depth < layout_depth:
                layout_closed_at = (i, depth)

    if layout_depth is not None and layout_closed_at is None:
        issues.append(
            "Bug 2 -- tutorial-layout closing </div> never found"
        )
    elif mob_toc_line and layout_closed_at:
        if mob_toc_line[0] < layout_closed_at[0]:
            issues.append(
                "Bug 2 -- mob-toc-panel is inside tutorial-layout "
                "(layout closes line " + str(layout_closed_at[0]) +
                ", mob-toc line " + str(mob_toc_line[0]) + ")"
            )

    if footer_line and footer_line[1] > 0:
        issues.append(
            "Bug 2 -- <footer> is nested inside another element "
            "(depth=" + str(footer_line[1]) +
            " on line " + str(footer_line[0]) + ")"
        )

    return issues


def main():
    if not os.path.isdir(TUTORIALS_DIR):
        print("ERROR: Directory not found.")
        print("Run this script from inside the tutorials folder.")
        input("\nPress Enter to close...")
        return

    html_files = sorted(
        f for f in os.listdir(TUTORIALS_DIR)
        if f.lower().endswith(".html") and f not in SKIP_FILES
    )

    print("audit-layout.py")
    print("=" * 70)
    print("Scanning " + str(len(html_files)) + " file(s) in: " + os.path.abspath(TUTORIALS_DIR))
    print("")

    clean  = []
    bugged = []

    for fname in html_files:
        path   = os.path.join(TUTORIALS_DIR, fname)
        issues = audit_file(path)
        if issues:
            bugged.append((fname, issues))
        else:
            clean.append(fname)

    if bugged:
        print("FILES WITH ISSUES  (" + str(len(bugged)) + ")")
        print("-" * 70)
        for fname, issues in bugged:
            print("  !! " + fname)
            for issue in issues:
                print("       -> " + issue)
        print("")

    print("CLEAN FILES  (" + str(len(clean)) + ")")
    print("-" * 70)
    for fname in clean:
        print("  OK " + fname)

    print("")
    print("=" * 70)
    print("Summary:  " + str(len(bugged)) + " file(s) need fixing  |  " + str(len(clean)) + " file(s) are clean")

    input("\nPress Enter to close...")


if __name__ == "__main__":
    main()
