# Performance Evaluation of OpenCL Standard Support (and Beyond)

**Authors:** T. Sorensen, S. Pai, A. F. Donaldson  
**Venue:** IWOCL, 2019 (Best Paper Award)  
**PDF:** [iwocl2019.pdf](../iwocl2019.pdf) | **Full Markdown:** [iwocl2019_full.md](iwocl2019_full.md)

This paper evaluates how support for various OpenCL features across GPU vendors affects the performance of graph applications.

## Key Contributions

- **Controlled study**: 6 optimizations x 17 applications x 3 graph inputs x 6 GPUs from 4 vendors (Nvidia, AMD, Intel, ARM).
- **Key finding**: Limiting to OpenCL 2.0 features fails to achieve speedups in 70%+ of benchmarks; forward progress guarantees (beyond the standard) unlock the best optimizations.
- **Cross-vendor portability**: All optimizations can be beneficial across different GPUs despite significant architectural differences.

## Summary

OpenCL promises platform portability, but adoption of features varies widely across vendors. This paper quantifies the performance impact of progressively more advanced OpenCL features on graph applications, providing concrete motivation for vendors to adopt newer features and for the standard to include forward progress guarantees.
