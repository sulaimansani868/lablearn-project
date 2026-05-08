#!/usr/bin/env python3
# audit-internal-css.py
# Scans every HTML file in the project recursively and reports any
# internal <style> blocks found, along with their content.
# Also generates a ready-to-review report file: css-audit-report.txt
#
# Usage:
#   python audit-internal-css.py
#   (run from anywhere - path is set in ROOT_DIR below)

import os
import re

ROOT_DIR    = r"C:\Users\User\WebDevelopment\lablearn-project\LabLearn"
REPORT_FILE = "css-audit-report.txt"
SKIP_DIRS   = {".git", "node_modules", "__pycache__"}


def extract_styles(html):
    # Returns list of (style_content, line_number) tuples
    results = []
    lines   = html.splitlines()
    in_style = False
    start_line = 0
    current = []

    for i, line in enumerate(lines, 1):
        if re.search(r'<style\b[^>]*>', line, re.IGNORECASE):
            in_style = True
            start_line = i
            # Capture anything after the opening tag on the same line
            after = re.sub(r'.*?<style\b[^>]*>', '', line, flags=re.IGNORECASE)
            if after.strip():
                current.append(after)
            continue
        if in_style:
            if re.search(r'</style>', line, re.IGNORECASE):
                # Capture anything before the closing tag
                before = re.sub(r'</style>.*', '', line, flags=re.IGNORECASE)
                if before.strip():
                    current.append(before)
                block = "\n".join(current).strip()
                if block:
                    results.append((block, start_line))
                current   = []
                in_style  = False
            else:
                current.append(line)

    return results


def classify(css_block, filepath):
    # Heuristic: guess whether a rule belongs in shared.css or tutorial.css
    tutorial_hints = [
        'toc', 'tutorial', 'article', 'tut-nav', 'mob-toc',
        'tut-list', 'page-header-meta', 'takeaways', 'box-',
        'data-table', 'level-badge', 'breadcrumb'
    ]
    shared_hints = [
        'nav', 'footer', 'btn', 'button', 'body', ':root',
        'variable', 'font', 'color', 'hero', 'card', 'grid',
        'section', 'container', 'page-layout'
    ]

    lower = css_block.lower()
    is_tutorial_page = 'tutorial' in filepath.lower() or \
                       os.path.dirname(filepath).endswith('tutorials')

    tutorial_score = sum(1 for h in tutorial_hints if h in lower)
    shared_score   = sum(1 for h in shared_hints   if h in lower)

    if tutorial_score > shared_score or is_tutorial_page:
        return "tutorial.css"
    elif shared_score > tutorial_score:
        return "shared.css"
    else:
        return "shared.css (or tutorial.css — review needed)"


def main():
    if not os.path.isdir(ROOT_DIR):
        print("ERROR: ROOT_DIR not found: " + ROOT_DIR)
        input("\nPress Enter to close...")
        return

    print("audit-internal-css.py")
    print("=" * 70)
    print("Scanning: " + ROOT_DIR)
    print("")

    files_with_style = []
    total_scanned    = 0

    for dirpath, dirnames, filenames in os.walk(ROOT_DIR):
        # Skip unwanted directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for fname in sorted(filenames):
            if not fname.lower().endswith(".html"):
                continue
            total_scanned += 1
            full_path = os.path.join(dirpath, fname)
            rel_path  = os.path.relpath(full_path, ROOT_DIR)

            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                html = f.read()

            blocks = extract_styles(html)
            if blocks:
                files_with_style.append((rel_path, blocks))

    # ── Console summary ───────────────────────────────────────────────────
    print("Scanned  : " + str(total_scanned) + " HTML file(s)")
    print("With <style> tags : " + str(len(files_with_style)))
    print("")

    if not files_with_style:
        print("No internal <style> blocks found. All CSS is already external.")
        input("\nPress Enter to close...")
        return

    print("FILES WITH INTERNAL STYLE BLOCKS")
    print("-" * 70)
    for rel_path, blocks in files_with_style:
        total_lines = sum(b.count("\n") + 1 for b, _ in blocks)
        suggestion  = classify(blocks[0][0], rel_path)
        n = str(len(blocks)) + " block" + ("s" if len(blocks) > 1 else "")
        print("  !! " + rel_path.ljust(55) + n.ljust(10) + "-> " + suggestion)

    # ── Detailed report file ──────────────────────────────────────────────
    report_path = os.path.join(ROOT_DIR, REPORT_FILE)
    with open(report_path, "w", encoding="utf-8") as r:
        r.write("CSS AUDIT REPORT\n")
        r.write("=" * 70 + "\n")
        r.write("Project: " + ROOT_DIR + "\n")
        r.write("Files scanned    : " + str(total_scanned) + "\n")
        r.write("Files with <style>: " + str(len(files_with_style)) + "\n\n")

        for rel_path, blocks in files_with_style:
            r.write("\n" + "=" * 70 + "\n")
            r.write("FILE: " + rel_path + "\n")
            r.write("=" * 70 + "\n")

            for idx, (block, line_no) in enumerate(blocks, 1):
                suggestion = classify(block, rel_path)
                r.write("\n  --- Style block " + str(idx) +
                        " (found at line " + str(line_no) + ") ---\n")
                r.write("  Suggested destination: " + suggestion + "\n\n")

                # Indent each line for readability
                for css_line in block.splitlines():
                    r.write("    " + css_line + "\n")

            r.write("\n")

    print("")
    print("=" * 70)
    print("Full report saved to:")
    print("  " + report_path)
    print("")
    print("Next step: share the report here and we will generate a script")
    print("to move the styles into shared.css and tutorial.css, and remove")
    print("the <style> blocks from each HTML file.")

    input("\nPress Enter to close...")


if __name__ == "__main__":
    main()
