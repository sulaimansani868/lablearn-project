#!/usr/bin/env python3
"""
apply-tutorial-nav.py
─────────────────────
Adds the three-zone mobile nav and tutorial list panel to every
tutorial HTML file in the LabLearn tutorials folder.

Usage:
    python apply-tutorial-nav.py

Run this script from inside the  tutorials/  folder, or set
TUTORIALS_DIR below to the full path of that folder.
"""

import os, re

# ── Configuration ─────────────────────────────────────────────────────────────
TUTORIALS_DIR = "."          # run from inside tutorials/, or set full path
SKIP_FILES    = {"index.html"}   # files to leave untouched
# ──────────────────────────────────────────────────────────────────────────────

NAV_TUT_BTN = '''\
    <button class="nav-tut-btn" id="navTutBtn" aria-label="Browse tutorials" aria-expanded="false">
      <svg class="nav-tut-icon" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <rect x="2" y="3" width="7" height="2" rx="1" fill="currentColor"/>
        <rect x="2" y="9" width="11" height="2" rx="1" fill="currentColor"/>
        <rect x="2" y="15" width="9" height="2" rx="1" fill="currentColor"/>
        <circle cx="16" cy="4" r="2" fill="currentColor" opacity=".45"/>
        <circle cx="16" cy="10" r="2" fill="currentColor" opacity=".45"/>
        <circle cx="16" cy="16" r="2" fill="currentColor" opacity=".45"/>
      </svg>
    </button>\n'''

TUT_LIST_PANEL = '''\

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
  </div>'''


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # ── Skip if already processed ──────────────────────────────────────────
    if "navTutBtn" in html:
        return "skipped (already updated)"

    changed = False

    # ── 1. Insert nav-tut-btn as first child of <nav> ──────────────────────
    # Finds <nav> then its first child element and inserts the button before it
    nav_match = re.search(r'(<nav[^>]*>)\s*\n', html)
    if nav_match:
        insert_at = nav_match.end()
        html = html[:insert_at] + NAV_TUT_BTN + html[insert_at:]
        changed = True
    else:
        return "FAILED — <nav> not found"

    # ── 2. Insert tutorial list panel after closing </div> of nav-mobile ───
    # Looks for the end of the nav-mobile div
    mob_end = re.search(r'(</div>)\s*\n(\s*\n\s*<div class="page-header")', html)
    if mob_end:
        insert_at = mob_end.start(1) + len('</div>')
        html = html[:insert_at] + TUT_LIST_PANEL + html[insert_at:]
        changed = True
    else:
        # Fallback: insert before page-header
        ph = html.find('<div class="page-header">')
        if ph != -1:
            html = html[:ph] + TUT_LIST_PANEL.lstrip('\n') + '\n\n  ' + html[ph:]
            changed = True
        else:
            return "FAILED — insertion point not found"

    if not changed:
        return "skipped (no changes made)"

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return "updated"


def main():
    html_files = [
        f for f in os.listdir(TUTORIALS_DIR)
        if f.endswith(".html") and f not in SKIP_FILES
    ]
    html_files.sort()

    if not html_files:
        print("No HTML files found. Make sure you're running this from the tutorials/ folder.")
        return

    print(f"Found {len(html_files)} tutorial file(s).\n")
    ok = skip = fail = 0
    for fname in html_files:
        path = os.path.join(TUTORIALS_DIR, fname)
        result = process_file(path)
        icon = "✓" if result == "updated" else ("–" if "skip" in result else "✗")
        print(f"  {icon}  {fname:50s}  {result}")
        if result == "updated":    ok   += 1
        elif "skip" in result:     skip += 1
        else:                      fail += 1

    print(f"\nDone.  Updated: {ok}  |  Skipped: {skip}  |  Failed: {fail}")
    if fail:
        print("Review any ✗ files manually — they may have a non-standard nav structure.")


if __name__ == "__main__":
    main()
