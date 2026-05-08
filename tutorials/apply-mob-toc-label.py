#!/usr/bin/env python3
import os
import re

TUTORIALS_DIR = "."
SKIP_FILES = {"index.html"}

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    if "mob-toc-btn" not in html:
        return "skipped - no mob-toc-btn found"

    original = html

    span_pattern = re.compile(
        r'(<button[^>]*mob-toc-btn[^>]*>.*?)'
        r'<span class="mob-toc-label">([^<]*)</span>'
        r'(.*?</button>)',
        re.DOTALL
    )

    if span_pattern.search(html):
        new_html = span_pattern.sub(
            lambda m: m.group(1)
                      + '<span class="mob-toc-label">Contents</span>'
                      + m.group(3),
            html
        )
        if new_html == html:
            return "skipped - label already reads Contents"
        html = new_html
    else:
        bare_pattern = re.compile(
            r'(<button[^>]*mob-toc-btn[^>]*>)'
            r'(\s*<span class="mob-toc-icon">[^<]*</span>)'
            r'[^<]*'
            r'(\s*</button>)',
            re.DOTALL
        )
        if bare_pattern.search(html):
            new_html = bare_pattern.sub(
                lambda m: (m.group(1)
                           + m.group(2)
                           + '\n    <span class="mob-toc-label">Contents</span>'
                           + m.group(3)),
                html
            )
            html = new_html
        else:
            return "FAILED - pattern not recognised"

    if html == original:
        return "skipped - no change needed"

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return "updated"


print("Script started.")
print("Looking in: " + os.path.abspath(TUTORIALS_DIR))
print("Directory exists: " + str(os.path.isdir(TUTORIALS_DIR)))

html_files = sorted(
    f for f in os.listdir(TUTORIALS_DIR)
    if f.lower().endswith(".html") and f not in SKIP_FILES
)

print("HTML files found: " + str(len(html_files)))
print("")

if not html_files:
    print("No HTML files found. Make sure you are running this script")
    print("from inside the tutorials folder.")
else:
    updated = skipped = failed = 0
    for fname in html_files:
        path = os.path.join(TUTORIALS_DIR, fname)
        result = process_file(path)
        if result == "updated":
            icon = "OK"; updated += 1
        elif result.startswith("FAILED"):
            icon = "!!"; failed += 1
        else:
            icon = "--"; skipped += 1
        print("  " + icon + "  " + fname.ljust(52) + "  " + result)

    print("")
    print("Done.  Updated: " + str(updated) + "  Skipped: " + str(skipped) + "  Failed: " + str(failed))

input("\nPress Enter to close...")
