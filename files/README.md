# files/

Papers and supporting documents for the site.

## Layout

| Path | Contents |
| --- | --- |
| `*.pdf` | Paper PDFs, plus slides/posters/preprints (`*_slides`, `*_poster`, `*_preprint`) |
| `markdown/` | Full paper text converted from PDF, one file per paper |
| `summaries/` | Short summaries, one file per paper |
| `summaries.md` | Combined index — every summary concatenated, ordered to match the page |
| `did-you-know-log.md` | Archive of the retired daily "Did you know?" feature |

Each paper uses one id across all three locations, e.g. `saferace.pdf`,
`markdown/saferace.md`, `summaries/saferace.md`. The id is what `index.html`
links to, so it must match exactly.

## Adding a paper

1. Drop the PDF in this directory as `<id>.pdf`.
2. Add the `<div class="pub">` entry to `index.html`, including both links:
   `files/markdown/<id>.md` and `files/summaries/<id>.md`.
3. Run `python pdf_to_markdown.py` from the repo root to generate the full markdown.
4. Write `summaries/<id>.md` by hand, matching the header format of the others.
5. Run `python regenerate_index.py` to rebuild `summaries.md`.

Step 5 also acts as a consistency check: it errors if a summary is missing for a
paper the page links, or if a summary exists that the page never links.

Theses are intentionally PDF-only and have no markdown versions.
