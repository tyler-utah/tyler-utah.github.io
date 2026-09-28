"""Rebuild files/summaries.md from the per-paper summaries in files/summaries/.

Papers are ordered to match the publications list in index.html, and the script
fails loudly if a summary exists that the page never links (or vice versa).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SUMMARIES_DIR = os.path.join(ROOT, "files", "summaries")
INDEX_PATH = os.path.join(ROOT, "files", "summaries.md")

HEADER = """# Papers in Markdown

All research papers by Tyler Sorensen and collaborators are provided in two markdown formats:

- **Full Markdown** (in [files/markdown/](markdown/)): Complete paper text converted from PDF.
- **Summary Markdown** (in [files/summaries/](summaries/)): Concise summaries highlighting key contributions.

These markdown versions are designed to make the papers easily accessible to both humans and AI agents.

---
"""


def order_from_index():
    with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as f:
        html = f.read()
    publications = html.split('<section id="publications">')[1]

    order = []
    for match in re.finditer(r'href="files/summaries/(\w+)\.md"', publications):
        if match.group(1) not in order:
            order.append(match.group(1))
    return order


def main():
    order = order_from_index()
    on_disk = {
        os.path.splitext(f)[0] for f in os.listdir(SUMMARIES_DIR) if f.endswith(".md")
    }

    missing_file = [p for p in order if p not in on_disk]
    unlinked = sorted(on_disk - set(order))
    if missing_file or unlinked:
        for p in missing_file:
            print(f"ERROR: index.html links {p} but files/summaries/{p}.md is missing")
        for p in unlinked:
            print(f"ERROR: files/summaries/{p}.md exists but index.html never links it")
        return 1

    parts = [HEADER]
    for paper_id in order:
        with open(os.path.join(SUMMARIES_DIR, f"{paper_id}.md"), encoding="utf-8") as f:
            parts.append(f.read().strip())
        parts.append("\n---\n")

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))

    print(f"Wrote {len(order)} papers to files/summaries.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
