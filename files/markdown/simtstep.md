# SIMT-Step Execution: A Flexible Operational Semantics for GPU Subgroup Behavior

**Authors:** Z. Chen, N. Rehman, G. Martínez, T. Sorensen  
**Venue:** PLDI, 2026  
**PDF:** [simtstep.pdf](../simtstep.pdf)

---

## Abstract

GPU hardware implements a SIMT execution model, where small groups of threads, called subgroups (or warps in CUDA), execute synchronously. Languages expose this through high-performance subgroup-level APIs. However, providing precise subgroup semantics in languages is challenging, as compilers may transform the program, potentially disrupting source-level synchronous behavior even if the hardware is synchronous. As a result, no GPU programming language provides rigorous semantics for subgroup execution.

In this work, we present SIMT-Step, a formal and flexible operational semantics for subgroup execution. At its core is a new semantic object, dynamic basic blocks, which enables precise specification of converged subgroup execution. SIMT-Step then provides flexibility for the execution of instructions, which can be collective, synchronous, or independent. We propose several candidate instantiations of SIMT-Step and design a suite of idiomatic tests to distinguish them, highlighting counter-intuitive behavior that arises under relaxed variants. We implement SIMT-Step in TLA+ and validate the behavior of the tests. To investigate how closely SIMT-Step models real-world GPU behavior, we conduct a fuzzing campaign, spanning ten GPUs and eight vendors. Our empirical study shows that non-synchronous behaviors are rare and appear on only a small number of devices; however, detailed investigation into these behaviors was inconclusive as to whether they are intentional or not. Combined, these contributions provide both a theoretical foundation and practical tools for reasoning about subgroup semantics in GPU programming languages.

## 1 Introduction

GPUs are now essential to modern computing, driving workloads in machine learning, graphics, and scientific simulation. Their impressive efficiency stems from a massively parallel execution model, but comes at a cost: GPU programming models are complex, evolve rapidly, and often leave important behaviors underspecified. As GPUs grow in importance, the need for precise, formal semantics becomes critical. Specification designers must balance abstraction, portability, and implementation flexibility. Without rigorous foundations, the community is left to rely on fragile assumptions, risking subtle bugs and missed optimizations.

Over the years, components of the GPU programming model have been formalized. For example, given the complexity of the GPU hierarchy, much attention has been given to the memory consistency model. This includes formalizations of existing language specifications, new model proposals, and empirical investigations. Notably, both PTX (NVIDIA's IR for CUDA) and SPIR-V now include formal specifications. Other works have formalized control flow properties and forward progress guarantees for GPU systems. Still, many aspects of the GPU programming model remain underspecified. One increasingly critical example is **subgroup behavior**.

Subgroups (warps in CUDA) are small groups of threads that execute together in a SIMT (Single Instruction, Multiple Threads) manner. Due to their close proximity in hardware, subgroup threads can efficiently cooperate; these capabilities are exposed to programmers through subgroup APIs in GPU languages, and they are widely used in performance-critical code.

Although subgroup threads nominally execute together under the SIMT model, two compounding issues complicate their specification:
1. Subgroup operations may appear in divergent control flow, where threads within a subgroup take different control flow paths, making it unclear which threads are required to participate.
2. The degree of implicit synchronization provided within a subgroup, both in regular execution and during subgroup operations, is not well specified, and compiler transformations might further obscure these behaviors.

### 1.1 Examples: Intuition and Nuance

**Converged, Diverged, and Merged.** We start by providing intuition about subgroup operations with examples executed by two threads in the same subgroup. The `subgroupAdd` operation simply adds the provided values across the subgroup from participating threads. When both threads execute an operation, each contributes 1 and the result is 2. However, when the program contains divergent behavior where threads take different paths, operations become *non-uniform*—executed by a subset of a subgroup.

**Lockstep or Independent?** Many prior works modeled *lockstep* subgroup execution, with all converged threads advancing together instruction by instruction. This assumption seems to remain common among developers. However, GPU specifications have shifted toward allowing *independent* intra-subgroup execution, where threads do not have to execute synchronously.

Even with lockstep hardware, a relaxed specification can still be exploited by an optimizing compiler via the *as-if* rule and cross-thread reasoning. Platform implementers may favor more permissive specifications that enable optimizations, even on synchronous hardware.

### 1.2 SIMT-Step Execution: A Flexible Operational Semantics for Subgroups

In this paper, we introduce **SIMT-Step Execution**, a flexible operational semantics for specifying subgroup behavior in GPU programming languages. SIMT-Step can be instantiated in multiple ways to account for a range of behaviors and optimizations. SIMT-Step was developed in discussion with official GPU specification groups.

**Dynamic Blocks.** Subgroup operations are unusual because they are both *collective* (combining inputs across threads) and *non-uniform* (not all threads are required to participate). SIMT-Step provides the semantic foundations to specify the set of participating threads in subgroup operations, even under divergence, through *dynamic blocks*.

**Flexible Instruction Execution.** SIMT-Step provides flexibility on how instructions are executed:
1. **Independently**: Threads execute these instructions independently under a standard concurrency model
2. **Synchronously**: These instructions implicitly synchronize active threads
3. **Collectively**: The operations execute collectively (atomically) across active threads

**SIMT-Step Instantiations.** By specifying different sets of independent, synchronous, and collective instructions, we define several instantiations:

| SIMT-Step Model | Description |
|-----------------|-------------|
| Collective Memory (CM) | Memory/subgroup ops, branches, and labels are collective |
| Sync. Memory (SM) | Memory is synchronous but not collective |
| Sync. Control Flow (SCF) | Synchronizes at basic block entry, exits via collectives |
| Sync. SG Op (SSO) | Synchronizes at SG ops and associated control dependencies |
| Speculative SG Op (Spec) | May speculatively run SG ops before synchronization |
| Symbolic SG op (Symb) | SG Ops don't synchronize and return symbolic values |

## Contributions

In summary, our contributions are:

- We introduce **SIMT-Step**, a flexible operational semantics for subgroup behavior in GPU programming languages. It is built around a new semantic object, the dynamic block, and can support varying degrees of independent, synchronous, and collective execution.
- We define a range of SIMT-Step models, ranging from fully lockstep to symbolic execution. We verify the behavior of a pragmatic subset of the models using TLA+.
- To understand real-world behaviors, we conduct a large empirical study across 10 GPUs from 8 vendors with 100k fuzzed tests. The tested platforms largely showed strongly synchronous behavior, although we also observed rare violations of lockstep execution whose root causes we were unable to determine.

## 2 Background

### 2.1 GPU Architecture and Programming Models

GPUs are high-throughput, massively parallel accelerators composed of many *compute units* (CUs), called *streaming multiprocessors* by NVIDIA. Each CU contains many lightweight *processing elements* (PEs) that execute instructions in parallel.

The corresponding programming model is also organized hierarchically: *threads* execute instructions on a PE. Threads are grouped into *subgroups* (*warps* in CUDA), which typically contain 16–128 threads depending on the architecture. Multiple subgroups that execute on a single CU form a *workgroup*, and all workgroups together constitute the *grid*.

Within a subgroup, threads execute according to the **SIMT** (Single Instruction, Multiple Threads) model. Conceptually, all these threads follow the same instruction stream and typically execute instructions together. When control-flow differs among threads, the subgroup *diverges*—some threads take one branch while others take another—and later *reconverge* (or merge) to resume joint execution.

### 2.2 Structured Control Flow and Maximal Reconvergence

SIMT-Step relies on two key features, both provided by SPIR-V: structured control flow and *maximal reconvergence*, which dictates how threads merge after divergence.

**Structured Control Flow.** SPIR-V basic blocks begin with `OpLabel` and end with a terminator such as `OpBranch`. A branch instruction is preceded by a merge instruction, which names the reconvergence block. Unstructured control flow (e.g., `goto`) is disallowed; all control flow must be statically nested and explicitly merged.

**Maximal Reconvergence.** SPIR-V specifies a model for handling divergent control flow known as *maximal reconvergence*. Under this model, all subgroup threads that execute a merge instruction reconverge the first time they reach the merge target.

## 3 SIMT-Step Foundations: Dynamic Blocks

We build on standard operational semantics, where a program execution E is a sequence of *atomic steps*. Each step corresponds to a static instruction execution, called a *dynamic instance* in SPIR-V. In a concurrent program, E interleaves dynamic instances from all threads, subject to synchronization constraints.

**Dynamic blocks** extend the notion of dynamic instances to basic blocks. A static basic block b, when executed, produces a dynamic block instance db. Multiple threads may execute the same dynamic block, which captures convergent thread execution.

A dynamic block db extends a basic block with:
- **Basic Block** (db.b): The associated static basic block
- **ID** (db.id): A unique ID as there can be multiple dynamic blocks for a given basic block
- **Threads** (db.T): The set of all threads that execute db
- **Children** (db.C): The children dynamic blocks of db in the dynamic execution graph
- **Dynamic Block Merge Target** (db.merge): The dynamic block where db.T will reconverge after any potential divergence

### Convergence and Divergence Rules

- **Initial**: There exists a single initial dynamic block db₀ corresponding to the first basic block; db₀.T contains all the threads
- **No spurious divergence**: Once a thread starts executing a dynamic block, it will continue executing the same dynamic block until a block terminating instruction
- **Branching**: If two threads are executing the same dynamic block and then branch to the same basic block, they must also branch to the same dynamic block
- **Reconvergence**: Threads must reconverge at a merge block as early as possible (maximal reconvergence)
- **Non repeating**: A thread t cannot execute the same dynamic basic block twice
- **Acyclic**: The dynamic execution graph must be acyclic

## 4 SIMT-Step Operational Semantics for Subgroup Behavior

Utilizing dynamic blocks, we design a flexible operational semantics for subgroup execution. The different instantiations are realized by statically partitioning instructions into three sets:
1. **Independent**: these instructions execute independently, as in traditional concurrency semantics
2. **Synchronous**: these instructions require all active threads to align on the instruction, but do not execute atomically
3. **Collective**: these instructions synchronize *and* execute atomically across the active threads

### 4.1 Executing Within a Dynamic Block

Instructions internal to a basic block are straightforward to execute because they do not require reasoning about divergence.

**Independent execution** is the most relaxed way these instructions can be executed. For loads and stores, allowing independent execution permits interleaved behaviors.

**Synchronous execution** is implemented in two steps: first all threads align on the instruction, then each thread may take a step individually.

**Collective execution** requires all active threads in a dynamic block to align at the same instruction, then execute atomically as a single group-level operation.

### 4.2 Collective Control Flow

Control flow instructions add complexity as they must account for potential divergence and prepare for reconvergence at merge blocks. Collective control flow instructions ensure that all threads within a dynamic block leave and enter basic blocks together.

### 4.3 Independent Branches

If threads are allowed to branch in a non-collective manner, dynamic blocks may not know their complete set of executing threads at creation time. To account for this, we add an *Unknown Thread Set* to track threads for which it is not yet known whether they will execute the block.

### 4.4 Further Relaxations

**Speculative Subgroup Operations**: Subgroup operations could be speculatively executed, assuming that the current view of active threads remains valid. This enables counterintuitive behaviors where speculation effectively justifies itself.

**Symbolic Subgroup Operations**: Each subgroup operation could execute independently and return a symbolic value, constrained and concretized later. However, this introduces thin-air behaviors, just as in relaxed memory models.

## 7 Empirical Study

We conduct a large-scale empirical study across real-world devices. We generalize our direct model tests across different memory access patterns, yielding 10 base tests. To test for behaviors introduced by compiler transformations, we apply a semantics-preserving fuzzer to each test, generating 100k fuzzed tests.

**Tested Platforms**: 10 GPUs spanning 8 vendors including NVIDIA, AMD, Intel, Apple, Qualcomm, ARM, Samsung, and PowerVR.

**Results**: Most GPUs exhibit strongly synchronous subgroup behavior across our tests. We performed detailed follow-up investigation on the rare non-synchronous behaviors, but were unable to conclusively determine whether they reflect intentional behavior or unintended anomalies. A clear exception is that nearly all GPUs do *not* treat memory operations as collective.

## Scope and Limitations

This work focuses on intra-subgroup behavior. To separate execution behavior from memory effects, we assume a sequentially consistent (SC) memory model for most of the paper. Future work includes extending SIMT-Step toward more complete relaxed memory models and integrating it into GPU verification frameworks.

Although we utilize many components and syntax from SPIR-V and rely on some of its control flow properties, SIMT-Step is designed to be general. CUDA does not provide the structured control flow or merge properties that SIMT-Step requires, so general CUDA cannot be modeled using SIMT-Step; however, there are likely pragmatic subsets that could be targeted.
