import pymupdf
import os
import json

papers = [
    "disorder.pdf",
    "parallelx2025.pdf",
    "saferace.pdf",
    "shadow.pdf",
    "peak2025.pdf",
    "bettertogether2025.pdf",
    "miniGiraffe.pdf",
    "ghost.pdf",
    "mix_testing.pdf",
    "leftoverlocals2024.pdf",
    "gpuharbor2023.pdf",
    "mcmutants2023.pdf",
    "redwood2023.pdf",
    "oopsla2021b.pdf",
    "oopsla2021a.pdf",
    "taco2021.pdf",
    "oopsla2020.pdf",
    "rtas2020.pdf",
    "ispass2020.pdf",
    "iiswc2019.pdf",
    "concur2018.pdf",
    "pldi2018.pdf",
    "fse2017.pdf",
    "popl2017.pdf",
    "oopsla2016.pdf",
    "pldi2016.pdf",
    "asplos2015.pdf",
    "iccad2020.pdf",
    "iwocl2019.pdf",
    "iwocl2016.pdf",
    "tinytocs2015.pdf",
    "ics2013.pdf",
]

files_dir = os.path.join(os.path.dirname(__file__), "files")
results = {}

for paper in papers:
    path = os.path.join(files_dir, paper)
    if not os.path.exists(path):
        results[paper] = "FILE NOT FOUND"
        continue
    try:
        doc = pymupdf.open(path)
        # Extract first 3 pages (usually enough for abstract + intro)
        text = ""
        for i in range(min(3, len(doc))):
            text += doc[i].get_text()
        doc.close()
        results[paper] = text[:8000]  # Cap at 8000 chars
    except Exception as e:
        results[paper] = f"ERROR: {e}"

# Write each paper's text to a separate file for review
out_dir = os.path.join(os.path.dirname(__file__), "_extracted")
os.makedirs(out_dir, exist_ok=True)

for paper, text in results.items():
    out_path = os.path.join(out_dir, paper.replace(".pdf", ".txt"))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

print(f"Extracted text from {len([v for v in results.values() if not v.startswith('FILE') and not v.startswith('ERROR')])} papers")
print(f"Errors: {[k for k, v in results.items() if v.startswith('ERROR') or v.startswith('FILE')]}")
