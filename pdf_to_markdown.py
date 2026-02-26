import pymupdf
import os
import re

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

# Metadata for headers
metadata = {
    "disorder.pdf": ("Memory DisOrder: Memory Re-orderings as a Timerless Side-channel", "S. Siddens, S. Srivastava, R. Levine, J. Dykstra, T. Sorensen", "ArXiv, 2026"),
    "parallelx2025.pdf": ("Parallel X: Redesigning of a Parallel Programming Educational Game with Semantic Foundations and Transfer Learning", "D. McKee, Z. Lin, B. Fox, J. Li, J. Zhu, M. Seif El-Nasr, T. Sorensen", "SIGCSE, 2026"),
    "saferace.pdf": ("SafeRace: Assessing and Addressing WebGPU Memory Safety in the Presence of Data Races", "R. Levine, A. Lee, N. Abbas, K. Little, T. Sorensen", "OOPSLA, 2025"),
    "shadow.pdf": ("SHADOW: Simultaneous Multi-Threading Architecture with Asymmetric Threads", "I. Chaturvedi, B. R. Godala, T. Sorensen, A. Gangavaram, T. M. Aamodt, D. Flyer, D. I. August", "MICRO, 2025"),
    "peak2025.pdf": ("PEAK: A Performance Engineering AI-Assistant for GPU Kernels Powered by Natural Language Transformations", "M. U. Tariq, A. Jangda, A. Moreira, M. Musuvathi, T. Sorensen", "ArXiv, 2025"),
    "bettertogether2025.pdf": ("BetterTogether: An Interference-Aware Framework for Fine-grained Software Pipelining on Heterogeneous SoCs", "Y. Xu, R. Sharma, Z. Chen, S. Mistry, T. Sorensen", "IISWC, 2025"),
    "miniGiraffe.pdf": ("miniGiraffe: A Pangenomic Mapping Proxy App", "J. I. Dagostini, J. B. Manzano, T. Sorensen, S. Beamer", "IISWC, 2025"),
    "ghost.pdf": ("GhOST: a GPU Out-of-Order Scheduling Technique for Stall Reduction", "I. Chaturvedi et al.", "ISCA, 2024"),
    "mix_testing.pdf": ("Mix Testing: Specifying and Testing ABI Compatibility of C/C++ Atomics Implementations", "L. Geeson, J. Brotherston, W. Dijkstra, A. F. Donaldson, L. Smith, T. Sorensen, J. Wickerson", "OOPSLA, 2024"),
    "leftoverlocals2024.pdf": ("LeftoverLocals: Listening to LLM Responses Through Leaked GPU Local Memory", "T. Sorensen, H. Khlaaf", "ArXiv, 2024"),
    "gpuharbor2023.pdf": ("GPUHarbor: Testing GPU Memory Consistency at Large (Experience Paper)", "R. Levine, M. Cho, D. McKee, A. Quinn, T. Sorensen", "ISSTA, 2023"),
    "mcmutants2023.pdf": ("MC Mutants: Evaluating and Improving Testing for Memory Consistency Specifications", "R. Levine, T. Guo, M. Cho, A. Baker, R. Levien, D. Neto, A. Quinn, T. Sorensen", "ASPLOS, 2023"),
    "redwood2023.pdf": ("Redwood: Flexible and Portable Heterogeneous Tree Traversal Workloads", "Y. Xu, A. Li, T. Sorensen", "ISPASS, 2023"),
    "oopsla2021b.pdf": ("Specifying and Testing GPU Workgroup Progress Models", "T. Sorensen, L. F. Salvador, H. Raval, H. Evrard, J. Wickerson, M. Martonosi, A. F. Donaldson", "OOPSLA, 2021"),
    "oopsla2021a.pdf": ("The Semantics of Shared Memory in Intel CPU/FPGA Systems", "D. Iorga, A. F. Donaldson, T. Sorensen, J. Wickerson", "OOPSLA, 2021"),
    "taco2021.pdf": ("GraphAttack: Optimizing Data Supply for Graph Applications on In-Order Multicore Architectures", "A. Manocha, T. Sorensen, E. Tureci, O. Matthews, J. L. Aragón, M. Martonosi", "TACO, 2021"),
    "oopsla2020.pdf": ("Foundations of Empirical Memory Consistency Testing", "J. Kirkham, T. Sorensen, E. Tureci, M. Martonosi", "OOPSLA, 2020"),
    "rtas2020.pdf": ("Slow and Steady: Measuring and Tuning Multicore Interference", "D. Iorga, T. Sorensen, J. Wickerson, A. F. Donaldson", "RTAS, 2020"),
    "ispass2020.pdf": ("MosaicSim: A Lightweight, Modular Simulator for Heterogeneous Systems", "O. Matthews et al.", "ISPASS, 2020"),
    "iiswc2019.pdf": ("One Size Doesn't Fit All: Quantifying Performance Portability of Graph Applications on GPUs", "T. Sorensen, S. Pai, A. F. Donaldson", "IISWC, 2019"),
    "concur2018.pdf": ("GPU Schedulers: How Fair is Fair Enough?", "T. Sorensen, H. Evrard, A. F. Donaldson", "CONCUR, 2018"),
    "pldi2018.pdf": ("The Semantics of Transactions and Weak Memory in x86, Power, ARM, and C++", "N. Chong, T. Sorensen, J. Wickerson", "PLDI, 2018"),
    "fse2017.pdf": ("Cooperative Kernels: GPU Multitasking for Blocking Algorithms", "T. Sorensen, H. Evrard, A. F. Donaldson", "FSE, 2017"),
    "popl2017.pdf": ("Automatically Comparing Memory Consistency Models", "J. Wickerson, M. Batty, T. Sorensen, G. Constantinides", "POPL, 2017"),
    "oopsla2016.pdf": ("Portable Inter-workgroup Barrier Synchronisation for GPUs", "T. Sorensen, A. F. Donaldson, M. Batty, G. Gopalakrishnan, Z. Rakamarić", "OOPSLA, 2016"),
    "pldi2016.pdf": ("Exposing Errors Related to Weak Memory in GPU Applications", "T. Sorensen, A. F. Donaldson", "PLDI, 2016"),
    "asplos2015.pdf": ("GPU Concurrency: Weak Behaviours and Programming Assumptions", "J. Alglave, M. Batty, A. F. Donaldson, G. Gopalakrishnan, J. Ketema, D. Poetzl, T. Sorensen, J. Wickerson", "ASPLOS, 2015"),
    "iccad2020.pdf": ("A Simulator and Compiler Framework for Agile Hardware-Software Co-design Evaluation and Exploration", "T. Sorensen, A. Manocha, E. Tureci, M. Orenes-Vera, J. L. Aragón, M. Martonosi", "ICCAD, 2020"),
    "iwocl2019.pdf": ("Performance Evaluation of OpenCL Standard Support (and Beyond)", "T. Sorensen, S. Pai, A. F. Donaldson", "IWOCL, 2019"),
    "iwocl2016.pdf": ("The Hitchhiker's Guide to Cross-Platform OpenCL Application Development", "T. Sorensen, A. F. Donaldson", "IWOCL, 2016"),
    "tinytocs2015.pdf": ("I Compute, Therefore I Am (Buggy): Methodic Doubt Meets Multiprocessors", "J. Alglave, L. Maranget, D. Poetzl, T. Sorensen", "TinyToCS, 2015"),
    "ics2013.pdf": ("Towards Shared Memory Consistency Models for GPUs", "T. Sorensen, J. Alglave, G. Gopalakrishnan, V. Grover", "ICS, 2013"),
}

files_dir = os.path.join(os.path.dirname(__file__), "files")
out_dir = os.path.join(files_dir, "summaries")
os.makedirs(out_dir, exist_ok=True)

success = 0
errors = []

for paper in papers:
    path = os.path.join(files_dir, paper)
    basename = paper.replace(".pdf", "")
    
    if not os.path.exists(path):
        errors.append(f"{paper}: FILE NOT FOUND")
        continue
    
    try:
        doc = pymupdf.open(path)
        
        # Extract full text from all pages using markdown output
        full_md = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Try markdown extraction first (pymupdf4llm style)
            try:
                page_text = page.get_text("text")
            except:
                page_text = page.get_text()
            
            if page_text.strip():
                full_md += page_text + "\n\n"
        
        doc.close()
        
        # Get metadata
        title, authors, venue = metadata.get(paper, (basename, "", ""))
        
        # Build markdown file
        md_content = f"# {title}\n\n"
        md_content += f"**Authors:** {authors}  \n"
        md_content += f"**Venue:** {venue}  \n"
        md_content += f"**PDF:** [{paper}](../{paper})\n\n"
        md_content += "---\n\n"
        md_content += full_md.strip() + "\n"
        
        out_path = os.path.join(out_dir, f"{basename}.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        page_count = len(pymupdf.open(path))
        print(f"  {basename}: {page_count} pages, {len(full_md):,} chars")
        success += 1
        
    except Exception as e:
        errors.append(f"{paper}: {e}")

print(f"\nConverted {success}/{len(papers)} papers to markdown")
if errors:
    print(f"Errors: {errors}")

# Also create the combined file
combined_path = os.path.join(files_dir, "summaries.md")
with open(combined_path, "w", encoding="utf-8") as f:
    f.write("# Full Paper Texts (Markdown)\n\n")
    f.write("Full markdown versions of research papers by Tyler Sorensen and collaborators.  \n")
    f.write("Individual papers are available in the [summaries/](summaries/) directory.\n\n")
    f.write("---\n\n")
    for paper in papers:
        basename = paper.replace(".pdf", "")
        title, authors, venue = metadata.get(paper, (basename, "", ""))
        f.write(f"- [{title}](summaries/{basename}.md) — {venue}  \n")
    f.write("\n")

print(f"Updated combined index at {combined_path}")
