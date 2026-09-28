"""Convert paper PDFs to full markdown in files/markdown/.

Papers and their metadata are read from index.html, so newly added papers are
picked up automatically. Existing markdown is left alone unless --force is given.
Does not touch files/summaries.md (see regenerate_index.py).
"""
import argparse
import os
import re

import pymupdf

ROOT = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(ROOT, "files")
OUT_DIR = os.path.join(FILES_DIR, "markdown")

PUB_BLOCK = re.compile(r'<div class="pub">(.*?)</div>', re.S)
FIELD = {
    "title": re.compile(r'pub-title">(.*?)</span>', re.S),
    "authors": re.compile(r'pub-authors">(.*?)</span>', re.S),
    "venue": re.compile(r'pub-venue">(.*?)</span>', re.S),
}
MARKDOWN_LINK = re.compile(r'href="files/markdown/(\w+)\.md"')


def strip_tags(text):
    return re.sub(r"<[^>]+>", "", text).strip()


def papers_from_index():
    """Yield (paper_id, title, authors, venue) for every paper linked on the page."""
    with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as f:
        html = f.read()

    for block in PUB_BLOCK.findall(html):
        match = MARKDOWN_LINK.search(block)
        if not match:
            continue  # theses and other PDF-only entries
        fields = {}
        for name, pattern in FIELD.items():
            found = pattern.search(block)
            fields[name] = strip_tags(found.group(1)) if found else ""
        yield match.group(1), fields["title"], fields["authors"], fields["venue"]


def convert(paper_id, title, authors, venue):
    pdf_path = os.path.join(FILES_DIR, f"{paper_id}.pdf")
    doc = pymupdf.open(pdf_path)
    try:
        pages = [page.get_text("text") for page in doc]
        page_count = len(doc)
    finally:
        doc.close()

    body = "\n\n".join(p for p in pages if p.strip()).strip()
    content = (
        f"# {title}\n\n"
        f"**Authors:** {authors}  \n"
        f"**Venue:** {venue}  \n"
        f"**PDF:** [{paper_id}.pdf](../{paper_id}.pdf) | "
        f"**Summary:** [{paper_id}.md](../summaries/{paper_id}.md)\n\n"
        "---\n\n"
        f"{body}\n"
    )

    with open(os.path.join(OUT_DIR, f"{paper_id}.md"), "w", encoding="utf-8") as f:
        f.write(content)
    return page_count, len(body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true", help="regenerate markdown that already exists"
    )
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    converted = skipped = 0

    for paper_id, title, authors, venue in papers_from_index():
        if not os.path.exists(os.path.join(FILES_DIR, f"{paper_id}.pdf")):
            print(f"  {paper_id}: SKIPPED (no PDF)")
            continue
        if os.path.exists(os.path.join(OUT_DIR, f"{paper_id}.md")) and not args.force:
            skipped += 1
            continue
        try:
            pages, chars = convert(paper_id, title, authors, venue)
            print(f"  {paper_id}: {pages} pages, {chars:,} chars")
            converted += 1
        except Exception as exc:
            print(f"  {paper_id}: ERROR {exc}")

    print(f"\nConverted {converted}, skipped {skipped} existing (use --force to redo).")


if __name__ == "__main__":
    main()
