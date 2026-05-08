#!/usr/bin/env python3
"""
apply-tut-panel.py
──────────────────
Inserts the tutorial list panel into every HTML file in the LabLearn
tutorials folder that already has the nav-tut-btn but is missing the panel.

Files that already have the panel are skipped untouched.
Files that have neither the button nor the panel are also skipped and
reported so you can investigate them separately.

Usage:
    python apply-tut-panel.py
"""

import os, re

TUTORIALS_DIR = r"C:\Users\User\Downloads\LabLearn (16)\LabLearn\tutorials"
SKIP_FILES    = {"index.html"}

# ── Panel snippet to insert ────────────────────────────────────────────────────
PANEL = """
  <!-- TUTORIAL LIST PANEL -->
  <div class="tut-list-overlay" id="tutListOverlay"></div>
  <div class="tut-list-panel" id="tutListPanel" aria-hidden="true">
    <div class="tut-list-head">
      <span class="tut-list-head-label">All Tutorials</span>
      <button class="tut-list-close" id="tutListClose" aria-label="Close">&#x2715;</button>
    </div>
    <div class="tut-list-body">
      <div class="tut-list-level">Beginner</div>
      <ul class="tut-list-links">
        <li><a href="molarity-concentration.html"      data-tut>Molarity, Molality &amp; Normality</a></li>
        <li><a href="serial-dilutions.html"            data-tut>Serial Dilutions: Technique &amp; Calculation</a></li>
        <li><a href="lab-safety.html"                  data-tut>Lab Safety: Chemical Hazard Classes</a></li>
        <li><a href="molar-solutions-bench-guide.html" data-tut>Preparing Molar Solutions: Bench Guide</a></li>
        <li><a href="serum-plasma-separation.html"     data-tut>Serum and Plasma Separation</a></li>
        <li><a href="ph-meter-calibration.html"        data-tut>pH Meter Calibration and Use</a></li>
        <li><a href="micropipette-technique.html"      data-tut>Micropipette Technique: Selection &amp; Calibration</a></li>
        <li><a href="centrifuge-operation.html"        data-tut>Centrifuge: Operation, Safety &amp; Protocol</a></li>
        <li><a href="acid-base-safe-handling.html"     data-tut>Safe Handling of Acids, Bases &amp; Corrosives</a></li>
        <li><a href="balance-weighing-technique.html"  data-tut>Accurate Weighing: Balance Technique</a></li>
      </ul>
      <div class="tut-list-level">Intermediate</div>
      <ul class="tut-list-links">
        <li><a href="uv-vis-spectrophotometry.html"    data-tut>UV-Vis Spectrophotometry Explained</a></li>
        <li><a href="standard-solutions.html"          data-tut>Preparing Standard Solutions Accurately</a></li>
        <li><a href="buffer-preparation.html"          data-tut>Preparing Buffer Solutions: Calculation to Bench</a></li>
        <li><a href="acid-base-titration.html"         data-tut>Acid-Base Titration: Technique &amp; Endpoints</a></li>
        <li><a href="blood-glucose-determination.html" data-tut>Blood Glucose: Glucometer &amp; GOD Methods</a></li>
        <li><a href="kjeldahl-protein.html"            data-tut>Protein Estimation by the Kjeldahl Method</a></li>
        <li><a href="biological-sample-handling.html"  data-tut>Biological Sample Handling and Storage</a></li>
        <li><a href="bradford-biuret-protein.html"     data-tut>Spectrophotometric Protein Determination</a></li>
        <li><a href="enzyme-activity-assays.html"      data-tut>Enzyme Activity Assays: Principles &amp; Methods</a></li>
        <li><a href="reagent-grade-water.html"         data-tut>Reagent-Grade Water: Preparation &amp; Quality</a></li>
      </ul>
      <div class="tut-list-level">Advanced</div>
      <ul class="tut-list-links">
        <li><a href="hplc-method-development.html"        data-tut>HPLC Method Development Fundamentals</a></li>
        <li><a href="atomic-absorption-spectroscopy.html" data-tut>Mineral Analysis by Atomic Absorption Spectroscopy</a></li>
        <li><a href="hplc-validation.html"                data-tut>HPLC Method Validation: Linearity &amp; Precision</a></li>
        <li><a href="enzyme-kinetics.html"                data-tut>Enzyme Kinetics: Michaelis-Menten &amp; Inhibition</a></li>
        <li><a href="sds-page-electrophoresis.html"       data-tut>Electrophoresis: SDS-PAGE and Agarose Gel</a></li>
        <li><a href="spectrofluorimetry.html"             data-tut>Spectrofluorimetry: Principles &amp; Applications</a></li>
        <li><a href="elisa-immunoassay.html"              data-tut>Immunoassay Techniques: ELISA Principles &amp; Protocol</a></li>
      </ul>
    </div>
  </div>"""

# ── Insertion-point strategies, tried in order ────────────────────────────────
# 1. Right after the closing </div> of nav-mobile
# 2. Right after the closing </nav> tag
# 3. Right before the page-header div
# 4. Right before the first <div class="tutorial-layout"> or <div class="page-header">
STRATEGIES = [
    # (description, regex pattern, insert-before-match-group)
    ("after nav-mobile closing tag",
     r'(</div>\s*\n)(\s*\n\s*<div class="page-header")',
     1),
    ("after </nav>",
     r'(</nav>\s*\n)',
     1),
    ("before page-header",
     r'(\s*)(<div class="page-header">)',
     0),
    ("before tutorial-layout",
     r'(\s*)(<div class="tutorial-layout">)',
     0),
]


def find_insertion_point(html):
    """Return (match_end_pos, strategy_name) or (None, None)."""
    # Strategy 1: after nav-mobile </div>, before page-header blank line
    m = re.search(r'id="navMobile".*?</div>', html, re.DOTALL)
    if m:
        return m.end(), "after nav-mobile </div>"

    # Strategy 2: after </nav>
    m = re.search(r'</nav>', html)
    if m:
        return m.end(), "after </nav>"

    # Strategy 3: before page-header
    m = re.search(r'<div class="page-header">', html)
    if m:
        return m.start(), "before page-header"

    # Strategy 4: before tutorial-layout
    m = re.search(r'<div class="tutorial-layout">', html)
    if m:
        return m.start(), "before tutorial-layout"

    return None, None


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    has_panel  = 'id="tutListPanel"' in html
    has_button = 'id="navTutBtn"'    in html

    # ── Already complete ───────────────────────────────────────────────────
    if has_panel:
        return "skipped — panel already present"

    # ── Button missing too: leave alone, report for manual review ─────────
    if not has_button:
        return "skipped — nav-tut-btn also missing (needs manual review)"

    # ── Button present, panel missing: insert panel ────────────────────────
    pos, strategy = find_insertion_point(html)

    if pos is None:
        return "FAILED — no suitable insertion point found"

    html = html[:pos] + "\n" + PANEL + "\n" + html[pos:]

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    return "inserted  [" + strategy + "]"


def main():
    if not os.path.isdir(TUTORIALS_DIR):
        print("ERROR: Directory not found:")
        print("  " + TUTORIALS_DIR)
        print("Edit TUTORIALS_DIR at the top of this script and try again.")
        return

    html_files = sorted(
        f for f in os.listdir(TUTORIALS_DIR)
        if f.lower().endswith(".html") and f not in SKIP_FILES
    )

    if not html_files:
        print("No HTML files found.")
        return

    print("Found " + str(len(html_files)) + " HTML file(s).\n")

    inserted = skipped = failed = review = 0

    for fname in html_files:
        path   = os.path.join(TUTORIALS_DIR, fname)
        result = process_file(path)

        if result.startswith("inserted"):
            icon = "+"
            inserted += 1
        elif result.startswith("FAILED"):
            icon = "✗"
            failed += 1
        elif "manual review" in result:
            icon = "?"
            review += 1
        else:
            icon = "–"
            skipped += 1

        print("  " + icon + "  " + fname.ljust(52) + "  " + result)

    print("")
    print("Done.")
    print("  +  Panel inserted        : " + str(inserted))
    print("  –  Skipped (had panel)   : " + str(skipped))
    print("  ?  Needs manual review   : " + str(review))
    print("  ✗  Failed                : " + str(failed))

    if review:
        print("\n? files are missing BOTH the button and the panel.")
        print("  Open them in a text editor and add both manually,")
        print("  or re-run apply-tutorial-nav.py on them first.")
    if failed:
        print("\n✗ files had the button but no recognisable insertion point.")
        print("  Open them and paste the panel snippet manually after </nav>.")


if __name__ == "__main__":
    main()
