# Kuiper: Correct and Efficient GPU Programming with Dependent Types and Separation Logic

**Authors:** G. Martínez, B. Köpcke, J. Fiala, G. Ebner, T. Ramananandro, M. Steuwer, T. Sorensen, N. Swamy  
**Venue:** PLDI, 2026  
**PDF:** [kuiper.pdf](../kuiper.pdf)

---

## Abstract

We introduce Kuiper, a language for safe and verified efficient CPU/GPU programming embedded as an extensible library within the F* dependently typed language. We rely on F*'s support for dependent types and its associated Pulse concurrent separation logic to develop a program logic in which to prove CPU/GPU programs safe, data-race free, and functionally correct. Our model of the GPU includes several intricacies, including the memory hierarchy, kernel launches, and synchronization within a single comprehensive framework. To do so, we extend the Pulse program logic with a novel notion of *located resources* and a new connective to structure reasoning about massively parallel programs, and present new proof rules to lift the per-thread view of GPU kernels to an end-to-end correctness specification.

We have used Kuiper to program and prove correct a variety of GPU kernels, including full functional correctness proofs of an optimized matrix multiplication using two levels of block tiling and tensor cores. In doing so, we have developed a range of libraries to enable programs and proofs at a high level of abstraction but without imposing any runtime overhead. These allow Kuiper programs to be polymorphic (over types, operations, memory layout, and more) and compile to efficient, specialized CUDA code, while enabling a novel form of verified auto-tuning. Our experimental evaluation confirms that Kuiper programs match the performance of their handwritten CUDA counterparts and are competitive with closed source, state-of-the-art kernels in cuBLAS.

## 1 Introduction

With the vast compute resources being spent training and serving large language models (LLMs) on GPUs, the incentives to develop optimized GPU programs are higher than ever. However, mainstream GPU programming languages, such as CUDA and HIP, are low-level and unsafe, relying on the programmer to do proper memory management, indexing, and synchronization between thousands of threads accessing shared resources in various parts of the GPU's memory hierarchy. The low-level aspect is appreciated by expert GPU programmers, as it allows for fine-grained control to extract maximum performance, particularly as small details can account for large performance differences. However, as the devil is also in the details, writing correct programs remains a challenge, and even experts spend a significant portion of their development effort debugging memory bugs, data races, and functional correctness issues.

### Example: Naïve Matrix Multiplication in CUDA

Consider a matrix multiplication in CUDA in its most basic form. This kernel multiplies two matrices A and B (of sizes M×K and K×N, respectively), storing the result in C. This is done by spawning enough threads to cover all the cells of C, where each thread computes one cell by iterating over the K dimension.

There are several subtleties for even this simplest kernel to work correctly:
- The grid configuration (number of blocks and threads) must cover all the cells of C exactly
- Every thread must write to a distinct cell of C to avoid data races
- The input matrices must not be modified while the kernel is running
- The accesses to the arrays must be in bounds

As kernels become more complicated (involving synchronization, matrix tiling, block-wide shared memory, tensor core operations, etc), these challenges are exacerbated.

### Safe GPU Programming

Making GPU programming safer and easier is an active area of research, with two main themes of work:

1. **Analysis tools**: A variety of analysis tools have been developed to check GPU programs for memory safety and race conditions, e.g., PUG, GKLEE, GPUVerify, and Faial. These tools offer a high level of automation for checking certain classes of bugs, but they can also time out, report false positives, and are hard to extend to handle the latest features of the rapidly-evolving GPU hardware and programming model.

2. **Domain-specific languages**: Languages like Triton and Cutlass/CuTe offer higher level languages embedded within Python or C++, aiming to simplify GPU programming but without trying to catch all potential errors at compile time. From the research community, languages like Halide, Lift, RISE, Descend, and Futhark offer new programming languages to raise the level of abstraction and improve safety, but they often sacrifice low-level control and performance.

## 1.1 Kuiper: An Extensible Framework for Correct & Efficient GPU Programming

We seek an extensible framework for GPU programming that offers high-level abstractions but with full control over low-level details, allowing programmers to eke out performance, while still providing strong static guarantees early in the development process, ranging from memory safety and data race freedom to full functional correctness.

Our approach is to embed support for CPU/GPU heterogeneous programming as library constructs (a so-called "shallow embedding") within the F* dependently typed programming language.

### Architecture

Kuiper programs are written in the Pulse sub-language of F*, a C-like imperative, concurrent, higher-order language with full low-level control of memory management and layout. Kuiper libraries in Pulse model a reference GPU programming model, including for blocks, warps, threads, tensor cores, barriers, shared memory, and vectorized memory access.

With GPU features described just as libraries, one can easily adjust or extend them to accommodate new features as the hardware evolves. On top of this model, we use Pulse's program logic to build abstract reasoning principles, so-called *kernel descriptions*, that relate CUDA's per-thread programming model to a global view of the entire kernel.

## Key Technical Contributions

### Located Resources

We extend the Pulse program logic with a novel notion of *located resources*. This allows us to reason about resources that are associated with specific locations in the GPU hierarchy (e.g., per-thread, per-block, or global).

### Kernel Descriptions

We present new proof rules to lift the per-thread view of GPU kernels to an end-to-end correctness specification. This bridges the gap between how GPU programs are written (per-thread) and how they are reasoned about (globally).

### Verified Auto-tuning

Kuiper programs can be polymorphic over types, operations, memory layout, and more. This enables a novel form of verified auto-tuning, where programs compile to efficient, specialized CUDA code while maintaining correctness guarantees.

## Evaluation

We have used Kuiper to program and prove correct a variety of GPU kernels, including:

- Full functional correctness proofs of an optimized matrix multiplication using two levels of block tiling and tensor cores
- A range of libraries to enable programs and proofs at a high level of abstraction

Our experimental evaluation confirms that:
- Kuiper programs match the performance of their handwritten CUDA counterparts
- Kuiper programs are competitive with closed source, state-of-the-art kernels in cuBLAS

## Conclusion

Kuiper demonstrates that it is possible to have both high-level abstractions and low-level control in GPU programming, while still providing strong static guarantees including memory safety, data race freedom, and full functional correctness. By embedding GPU programming within a dependently typed language with concurrent separation logic, we can reason about massively parallel programs in a principled way.
