# miniGiraffe: A Pangenomic Mapping Proxy App

**Authors:** J. I. Dagostini, J. B. Manzano, T. Sorensen, S. Beamer  
**Venue:** IISWC, 2025  
**PDF:** [miniGiraffe.pdf](../miniGiraffe.pdf) | **Full Markdown:** [miniGiraffe_full.md](miniGiraffe_full.md)

This paper presents miniGiraffe, a proxy application for Giraffe, a complex pangenomic mapping tool that operates over graph-based structures capturing genetic variation across a species.

## Key Contributions

- **Extreme code reduction**: miniGiraffe contains only 2% of Giraffe's codebase (~1K vs ~50K lines of code, 2 vs ~350 source files) while faithfully reproducing key computational features.
- **Output fidelity**: Produces identical outputs for the most computationally intensive regions and closely matches execution time and scaling behavior.
- **Practical utility**: The simplified design enabled rapid autotuning across multiple architectures, finding a geomean speedup of 1.15x and up to 3.32x by specializing parameters to inputs and architectures.

## Summary

Large scientific applications like pangenome mapping tools are complex and difficult to analyze due to intricate I/O patterns and library dependencies. miniGiraffe uses a principled methodology to distill Giraffe into a lightweight proxy that captures its essential computational characteristics, enabling the computational research community to study and optimize this important genomics workload.
