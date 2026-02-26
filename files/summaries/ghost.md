# GhOST: a GPU Out-of-Order Scheduling Technique for Stall Reduction

**Authors:** I. Chaturvedi, B. R. Godala, Y. Wu, Z. Xu, K. Iliakis, P.-E. Eleftherakis, S. Xydis, D. Soudris, T. Sorensen, S. Campanoni, T. M. Aamodt, D. I. August  
**Venue:** ISCA, 2024  
**PDF:** [ghost.pdf](../ghost.pdf) | **Full Markdown:** [ghost.md](../markdown/ghost.md)

This paper introduces GhOST, a minimal yet effective out-of-order (OoO) execution technique for GPUs that reduces stall cycles without the costly hardware of prior proposals.

## Key Contributions

- **Lightweight OoO execution**: Leverages the decode stage's existing pool of decoded instructions and the issue stage's pipeline information to select instructions for OoO execution with minimal additional hardware (only 0.007% area increase).
- **Two surprising insights**: (1) Prior works used NVIDIA's intermediate representation PTX for evaluation, but optimized static scheduling of final binaries negates many purported OoO improvements; (2) The prior state-of-the-art OoO technique actually results in average slowdown.
- **No slowdowns**: Unlike prior approaches, GhOST never slows down any measured benchmark, achieving 36% maximum and 6.9% geomean speedup on GPU binaries.

## Summary

GPUs use massive multi-threading to hide instruction latencies, but memory instructions with variable latencies still cause stalls. Prior OoO GPU proposals required costly features like register renaming and load-store queues. GhOST achieves a substantial portion of idealized OoO reorderings without these expensive components, demonstrating that a write-back constraint used by other approaches is unnecessary and harmful.
