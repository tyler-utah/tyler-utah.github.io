# Kuiper: Correct and Efficient GPU Programming with Dependent Types and Separation Logic

**Authors:** G. Martínez, B. Köpcke, J. Fiala, G. Ebner, T. Ramananandro, M. Steuwer, T. Sorensen, N. Swamy  
**Venue:** PLDI, 2026  
**PDF:** [kuiper.pdf](../kuiper.pdf) | **Full Markdown:** [kuiper.md](../markdown/kuiper.md)

This paper introduces Kuiper, a language for safe and verified efficient CPU/GPU programming embedded within the F* dependently typed language.

## Key Contributions

- **Located resources**: A novel extension to the Pulse program logic with located resources and a new connective to structure reasoning about massively parallel programs.
- **Kernel descriptions**: New proof rules to lift the per-thread view of GPU kernels to an end-to-end correctness specification.
- **Full functional correctness proofs**: Including an optimized matrix multiplication using two levels of block tiling and tensor cores.
- **Verified auto-tuning**: Programs can be polymorphic (over types, operations, memory layout) and compile to efficient, specialized CUDA code.
- **Performance parity**: Kuiper programs match the performance of handwritten CUDA counterparts and are competitive with cuBLAS.

## Summary

Mainstream GPU programming languages like CUDA are low-level and unsafe, relying on programmers to handle memory management, indexing, and synchronization between thousands of threads. Kuiper addresses this by embedding GPU programming as library constructs within F*, using its dependent types and Pulse concurrent separation logic to prove programs safe, data-race free, and functionally correct. The model covers the memory hierarchy, kernel launches, and synchronization within a single comprehensive framework, while libraries enable high-level abstraction without runtime overhead.
