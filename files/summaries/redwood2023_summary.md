# Redwood: Flexible and Portable Heterogeneous Tree Traversal Workloads

**Authors:** Y. Xu, A. Li, T. Sorensen  
**Venue:** ISPASS, 2023  
**PDF:** [redwood2023.pdf](../redwood2023.pdf) | **Full Markdown:** [redwood2023_full.md](redwood2023_full.md)

This paper presents Redwood, a framework for writing heterogeneous traverse-compute workloads that harness the complementary strengths of CPUs and accelerators on shared memory heterogeneous systems.

## Key Contributions

- **Traverse-compute decomposition**: Identifies a pragmatic class of applications where CPUs excel at tree traversal (irregular memory accesses) while accelerators excel at leaf-node computations.
- **Grove benchmark suite**: Nine tree-based applications (e.g., k-nearest neighbors) instantiated for CUDA, SYCL, and High-Level Synthesis across five heterogeneous systems.
- **Significant speedups**: Heterogeneous implementations provide up to 13.53x speedup (geomean 3.01x) over homogeneous implementations.

## Summary

Shared memory heterogeneous systems (SoCs) are mainstream but difficult to target with workloads that efficiently utilize their diverse processing units. Redwood identifies tree traversal applications as ideal candidates for heterogeneous execution, providing a simple abstraction and library that enables heterogeneous optimizations across CUDA, SYCL, and FPGA-based platforms.
