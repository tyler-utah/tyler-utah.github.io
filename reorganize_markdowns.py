"""
Reorganize markdown files:
- Rename existing full-text .md files to _full.md
- Re-create summary .md files as _summary.md
"""
import os
import shutil

summaries_dir = os.path.join(os.path.dirname(__file__), "files", "summaries")

papers = {
    "disorder": {
        "title": "Memory DisOrder: Memory Re-orderings as a Timerless Side-channel",
        "authors": "S. Siddens, S. Srivastava, R. Levine, J. Dykstra, T. Sorensen",
        "venue": "ArXiv, 2026",
        "summary": """This paper presents MEMORY DISORDER, a novel timerless side-channel attack that exploits memory re-orderings arising from hardware relaxed memory consistency models. The attack requires only the ability to launch threads and execute basic memory loads and stores — no timers needed.

## Key Contributions

- **Fuzzing campaign** across mainstream processors (x86/Arm/Apple CPUs, NVIDIA/AMD/Apple GPUs) showing cross-process re-ordering signals on many devices.
- **Covert channel** achieving up to 16 bits/second with 95% accuracy on an Apple M3 GPU.
- **Application fingerprinting** with reliable closed-world DNN architecture fingerprinting on several CPUs and an Apple M3 GPU.
- **Exploitation of low-level system details** to amplify re-orderings, showing potential for nearly 30K bits/second on x86 CPUs.

## Summary

The key insight is that memory re-orderings — which arise naturally from hardware optimizations in relaxed memory models — occur more frequently when other cores are active. By repeatedly executing litmus tests (small concurrent programs that detect re-orderings), an attacker process can infer activity on victim processes without requiring any timer access. This makes DISORDER a low-capability attack deployable in more situations than traditional timer-based side-channels.""",
    },
    "parallelx2025": {
        "title": "Parallel X: Redesigning of a Parallel Programming Educational Game with Semantic Foundations and Transfer Learning",
        "authors": "D. McKee, Z. Lin, B. Fox, J. Li, J. Zhu, M. Seif El-Nasr, T. Sorensen",
        "venue": "SIGCSE, 2026",
        "summary": """This paper presents Parallel X, a redesigned educational game for teaching parallel programming concepts to college students.

## Key Contributions

- **Semantic grounding** in classic concurrency theory, incorporating interleaved execution semantics with the ability to pause and resume execution — connecting gameplay to how real parallel programs behave.
- **Transfer learning activities** that bridge in-game visual states to actual C++ code, addressing the gap between conceptual understanding and practical implementation.
- **Focus on debugging skills**, an increasingly important capability as AI-generated code becomes more prevalent and error-prone.

## Summary

Prior educational games for parallelism suffered from weak semantic foundations and poor transfer from visual gameplay to real coding. Parallel X addresses both limitations by grounding its puzzles in formal concurrency semantics and explicitly connecting in-game states to C++ code. A usability study with undergraduate CS majors showed improved usability scores and significantly higher ratings for information accessibility compared to an earlier version of the game.""",
    },
    "saferace": {
        "title": "SafeRace: Assessing and Addressing WebGPU Memory Safety in the Presence of Data Races",
        "authors": "R. Levine, A. Lee, N. Abbas, K. Little, T. Sorensen",
        "venue": "OOPSLA, 2025",
        "summary": """This paper identifies a specification vulnerability in the WebGPU Shading Language (WGSL) where data races can compromise memory safety, and proposes the SafeRace framework to address it.

## Key Contributions

- **Specification vulnerability discovery**: Data races in WGSL can cause optimizing compilers to legitimately remove memory safety bounds-checks, creating a "ticking time bomb" as compilers evolve.
- **SafeRace Memory Safety Guarantee (SMSG)**: A two-component solution — (1) a compiler pass ensuring race-free memory indexing slices, and (2) requirements on intermediate representations to limit data race effects.
- **81-hour fuzzing campaign** across 21 compilation stacks validating the approach; violations found on only one (likely buggy) machine.
- **Security discoveries**: GPU memory isolation vulnerabilities in Apple and AMD GPUs, plus a security-critical miscompilation in a pre-release Firefox.

## Summary

WebGPU enables powerful GPU computation in web browsers, but WGSL's compilation through lower-level intermediate representations creates risks. SafeRace shows that data races can undermine bounds-checks that enforce memory safety, and proposes practical solutions with minimal performance overhead on important WebGPU applications.""",
    },
    "shadow": {
        "title": "SHADOW: Simultaneous Multi-Threading Architecture with Asymmetric Threads",
        "authors": "I. Chaturvedi, B. R. Godala, T. Sorensen, A. Gangavaram, T. M. Aamodt, D. Flyer, D. I. August",
        "venue": "MICRO, 2025",
        "summary": """This paper presents SHADOW, the first asymmetric SMT core that dynamically balances instruction-level parallelism (ILP) and thread-level parallelism (TLP) by running out-of-order (OoO) and in-order (InO) threads simultaneously on the same core.

## Key Contributions

- **Asymmetric SMT design**: Executes a heavyweight OoO thread alongside lightweight InO threads on the same core, maximizing CPU utilization.
- **Runtime-configurable**: Applications can optimize the mix of OoO and InO execution based on workload characteristics.
- **Strong performance**: Up to 3.16x speedup and 1.33x average improvement over OoO CPU across nine diverse benchmarks, with only 1% area and power overhead.
- **Dynamic adaptation**: Automatically redistributes work as ILP changes without software intervention.

## Summary

Many applications exhibit shifting demands between ILP and TLP due to irregular sparsity and unpredictable memory accesses. SHADOW leverages deep ILP in the OoO thread and high TLP in lightweight InO threads, dynamically adapting to workload variations. This outperforms conventional architectures and efficiently accelerates memory-bound workloads without compromising compute-bound performance.""",
    },
    "peak2025": {
        "title": "PEAK: A Performance Engineering AI-Assistant for GPU Kernels Powered by Natural Language Transformations",
        "authors": "M. U. Tariq, A. Jangda, A. Moreira, M. Musuvathi, T. Sorensen",
        "venue": "ArXiv, 2025",
        "summary": """This paper introduces Peak, an AI-powered framework for optimizing GPU kernels using natural language transformation specifications executed by LLMs.

## Key Contributions

- **Natural transformations**: Optimization strategies expressed in natural language (from general "unroll a loop" to specific "tile the inner loop over the K dimension"), easily specialized to specific kernels and hardware.
- **Modular infrastructure**: Kernel contexts, correctness validators, and performance evaluators provide rigorous checking of LLM-generated transformations.
- **Cross-backend support**: Instantiated for three backends — CUDA, HIP, and HLSL — with 16 natural transformations for matrix multiplication.
- **Competitive results**: Implementations match vendor libraries when available, and for HLSL (without a library) match hardware-documented FLOPS.

## Summary

Peak captures the workflow of expert performance engineers by expressing iterative code optimizations as natural language specifications that LLMs execute. Unlike prior all-or-nothing automation approaches, Peak supports human-AI collaboration, interpretable iterative refinement, and extensible modular interfaces. It can be used interactively by performance engineers or driven autonomously by AI agents.""",
    },
    "bettertogether2025": {
        "title": "BetterTogether: An Interference-Aware Framework for Fine-grained Software Pipelining on Heterogeneous SoCs",
        "authors": "Y. Xu, R. Sharma, Z. Chen, S. Mistry, T. Sorensen",
        "venue": "IISWC, 2025 (Best Paper Award)",
        "summary": """This paper presents BetterTogether, a scheduling framework that enables fine-grained software pipelining on heterogeneous edge SoCs while accounting for inter-processing-unit interference.

## Key Contributions

- **Interference-aware performance model**: Captures execution time under representative intra-application interference, producing predictions that strongly correlate with measured results.
- **Flexible pipeline scheduling**: Applications are decomposed into stages with CPU and GPU implementations, then pipelined across the SoC's various processing units.
- **Cross-vendor portability**: Evaluated on three SoCs with GPUs from NVIDIA, Arm, and Qualcomm using three computer vision workloads.
- **Strong speedups**: Geomean 2.14x and maximum 7.59x speedup over homogeneous GPU baselines.

## Summary

Edge SoCs contain diverse processing units (big.LITTLE CPUs, GPUs, accelerators) with varying performance characteristics. BetterTogether exploits this heterogeneity through pipeline parallelism, where stages are mapped to the most suitable processing units. Its key innovation is a profile-guided model that accounts for the interference between simultaneously active processing units — a critical factor on resource-constrained edge devices.""",
    },
    "miniGiraffe": {
        "title": "miniGiraffe: A Pangenomic Mapping Proxy App",
        "authors": "J. I. Dagostini, J. B. Manzano, T. Sorensen, S. Beamer",
        "venue": "IISWC, 2025",
        "summary": """This paper presents miniGiraffe, a proxy application for Giraffe, a complex pangenomic mapping tool that operates over graph-based structures capturing genetic variation across a species.

## Key Contributions

- **Extreme code reduction**: miniGiraffe contains only 2% of Giraffe's codebase (~1K vs ~50K lines of code, 2 vs ~350 source files) while faithfully reproducing key computational features.
- **Output fidelity**: Produces identical outputs for the most computationally intensive regions and closely matches execution time and scaling behavior.
- **Practical utility**: The simplified design enabled rapid autotuning across multiple architectures, finding a geomean speedup of 1.15x and up to 3.32x by specializing parameters to inputs and architectures.

## Summary

Large scientific applications like pangenome mapping tools are complex and difficult to analyze due to intricate I/O patterns and library dependencies. miniGiraffe uses a principled methodology to distill Giraffe into a lightweight proxy that captures its essential computational characteristics, enabling the computational research community to study and optimize this important genomics workload.""",
    },
    "ghost": {
        "title": "GhOST: a GPU Out-of-Order Scheduling Technique for Stall Reduction",
        "authors": "I. Chaturvedi, B. R. Godala, Y. Wu, Z. Xu, K. Iliakis, P.-E. Eleftherakis, S. Xydis, D. Soudris, T. Sorensen, S. Campanoni, T. M. Aamodt, D. I. August",
        "venue": "ISCA, 2024",
        "summary": """This paper introduces GhOST, a minimal yet effective out-of-order (OoO) execution technique for GPUs that reduces stall cycles without the costly hardware of prior proposals.

## Key Contributions

- **Lightweight OoO execution**: Leverages the decode stage's existing pool of decoded instructions and the issue stage's pipeline information to select instructions for OoO execution with minimal additional hardware (only 0.007% area increase).
- **Two surprising insights**: (1) Prior works used NVIDIA's intermediate representation PTX for evaluation, but optimized static scheduling of final binaries negates many purported OoO improvements; (2) The prior state-of-the-art OoO technique actually results in average slowdown.
- **No slowdowns**: Unlike prior approaches, GhOST never slows down any measured benchmark, achieving 36% maximum and 6.9% geomean speedup on GPU binaries.

## Summary

GPUs use massive multi-threading to hide instruction latencies, but memory instructions with variable latencies still cause stalls. Prior OoO GPU proposals required costly features like register renaming and load-store queues. GhOST achieves a substantial portion of idealized OoO reorderings without these expensive components, demonstrating that a write-back constraint used by other approaches is unnecessary and harmful.""",
    },
    "mix_testing": {
        "title": "Mix Testing: Specifying and Testing ABI Compatibility of C/C++ Atomics Implementations",
        "authors": "L. Geeson, J. Brotherston, W. Dijkstra, A. F. Donaldson, L. Smith, T. Sorensen, J. Wickerson",
        "venue": "OOPSLA, 2024",
        "summary": """This paper presents mix testing, a technique for finding compiler bugs that arise when concurrently compiled binaries from different compilers (or compiler versions) are composed together.

## Key Contributions

- **Mixing bugs**: Defines a new class of bugs that arise when parts of a concurrent program are compiled using different atomics mappings from C/C++ to assembly — a scenario that occurs in real industry applications (e.g., Windows on Arm mixing MSVC and LLVM code).
- **atomic-mixer tool**: Implements mix testing and was used to find four previously unknown mixing bugs in LLVM and GCC, and one prospective bug in proposed JVM mappings.
- **First atomics ABI for Armv8**: Worked with Arm engineers to specify, for the first time, a concurrency ABI for the Arm architecture, and validated LLVM and GCC compilers against it.

## Summary

While ABIs ensure binary compatibility, there are no official ABIs for concurrent programs. Different compilers may use different (individually correct) mappings from C/C++ atomics to assembly, but composing these binaries can introduce subtle bugs. Mix testing systematically finds these composition bugs, addressing a real-world problem that kernel and application developers face today.""",
    },
    "leftoverlocals2024": {
        "title": "LeftoverLocals: Listening to LLM Responses Through Leaked GPU Local Memory",
        "authors": "T. Sorensen, H. Khlaaf",
        "venue": "ArXiv, 2024",
        "summary": """This paper describes LeftoverLocals (CVE-2023-49691), a vulnerability that allows data recovery from GPU local memory created by another process, with particular implications for LLM and ML model security.

## Key Contributions

- **Vulnerability discovery**: GPU local memory — an optimized memory region — is not properly cleared between process invocations on Apple, Qualcomm, and AMD GPUs.
- **LLM eavesdropping PoC**: Demonstrated an attacker listening to another user's interactive LLM session (e.g., llama.cpp) across process or container boundaries, leaking ~5.5 MB per GPU invocation (~181 MB per LLM query on AMD Radeon RX 7900 XT).
- **Large-scale coordinated disclosure**: Worked with CERT Coordination Center to disclose to all major GPU vendors (NVIDIA, Apple, AMD, Arm, Intel, Qualcomm, Imagination).
- **Vendor response**: Apple's A17 and M3 processors contain fixes; AMD devices remain impacted; Qualcomm released firmware patches for some devices.

## Summary

As ML applications increasingly run on diverse GPUs (not just NVIDIA), the security of these devices is critical. LeftoverLocals shows that many GPUs fail to isolate local memory between processes, enabling an attacker to reconstruct LLM responses with high fidelity. The vulnerability highlights that many parts of the ML stack have not been rigorously reviewed by security experts.""",
    },
    "gpuharbor2023": {
        "title": "GPUHarbor: Testing GPU Memory Consistency at Large (Experience Paper)",
        "authors": "R. Levine, M. Cho, D. McKee, A. Quinn, T. Sorensen",
        "venue": "ISSTA, 2023 (Distinguished Artifact Award)",
        "summary": """This paper presents GPUHarbor, a widescale GPU memory consistency specification (MCS) testing tool with web and Android interfaces that enabled the largest study of weak memory behaviors to date.

## Key Contributions

- **Accessible testing**: Web interface and Android app allow crowd-sourced collection of GPU memory consistency testing data.
- **Massive scale**: Collected data from 106 devices spanning seven vendors — at least 10x larger than prior studies.
- **Bug discovery**: Conformance tests identified two new bugs on embedded Arm and NVIDIA devices.
- **Behavioral insights**: AMD GPUs show 25.3x more weak behaviors on average than Intel; devices can be clustered according to stress testing sensitivity.

## Summary

Memory consistency specifications are critical but testing tools have historically been inaccessible, limiting studies to few platforms. GPUHarbor democratized MCS testing through web and mobile interfaces, enabling crowd-sourced data collection. The resulting dataset provides unprecedented insight into how different GPU vendors and architectures handle memory ordering, revealing significant behavioral differences across the ecosystem.""",
    },
    "mcmutants2023": {
        "title": "MC Mutants: Evaluating and Improving Testing for Memory Consistency Specifications",
        "authors": "R. Levine, T. Guo, M. Cho, A. Baker, R. Levien, D. Neto, A. Quinn, T. Sorensen",
        "venue": "ASPLOS, 2023 (Distinguished Paper Award, Distinguished Artifact Award)",
        "summary": """This paper proposes MC Mutants, a mutation testing approach for evaluating and improving memory consistency specification (MCS) testing environments.

## Key Contributions

- **Mutation testing for MCS**: Mutates MCS litmus tests to simulate potential platform bugs, providing a mutation score metric to evaluate testing environments — solving the problem that real MCS violations are too rare to use as an efficacy metric.
- **Parallel testing environment**: Improves testing speed by three orders of magnitude over prior work.
- **Confidence strategy**: Parameterized over a time budget and confidence threshold, requiring only 64 seconds per test.
- **Practical impact**: Identified two bugs in WebGPU implementations (one leading to a specification change), and the WebGPU conformance test suite adopted this approach.

## Summary

The effectiveness of memory consistency testing depends heavily on the testing environment (e.g., whether stress is applied), but evaluating these environments has been difficult since real violations are extremely rare. MC Mutants creates synthetic but realistic mutations that simulate bugs, enabling rigorous evaluation and improvement of testing strategies. Implemented in WebGPU, the approach achieved broad adoption in the official conformance test suite.""",
    },
    "redwood2023": {
        "title": "Redwood: Flexible and Portable Heterogeneous Tree Traversal Workloads",
        "authors": "Y. Xu, A. Li, T. Sorensen",
        "venue": "ISPASS, 2023",
        "summary": """This paper presents Redwood, a framework for writing heterogeneous traverse-compute workloads that harness the complementary strengths of CPUs and accelerators on shared memory heterogeneous systems.

## Key Contributions

- **Traverse-compute decomposition**: Identifies a pragmatic class of applications where CPUs excel at tree traversal (irregular memory accesses) while accelerators excel at leaf-node computations.
- **Grove benchmark suite**: Nine tree-based applications (e.g., k-nearest neighbors) instantiated for CUDA, SYCL, and High-Level Synthesis across five heterogeneous systems.
- **Significant speedups**: Heterogeneous implementations provide up to 13.53x speedup (geomean 3.01x) over homogeneous implementations.

## Summary

Shared memory heterogeneous systems (SoCs) are mainstream but difficult to target with workloads that efficiently utilize their diverse processing units. Redwood identifies tree traversal applications as ideal candidates for heterogeneous execution, providing a simple abstraction and library that enables heterogeneous optimizations across CUDA, SYCL, and FPGA-based platforms.""",
    },
    "oopsla2021b": {
        "title": "Specifying and Testing GPU Workgroup Progress Models",
        "authors": "T. Sorensen, L. F. Salvador, H. Raval, H. Evrard, J. Wickerson, M. Martonosi, A. F. Donaldson",
        "venue": "OOPSLA, 2021",
        "summary": """This paper provides a collection of tools and experimental data to aid specification designers in reasoning about forward progress guarantees for GPU workgroups.

## Key Contributions

- **Formal framework**: A small parallel programming language capturing fine-grained synchronization, with formal progress model specifications and a termination oracle.
- **Test synthesis**: 483 progress litmus tests synthesized from formal constraints describing programs requiring forward progress to terminate.
- **Large experimental campaign**: Tests run across 8 GPUs from 5 vendors, revealing significantly different termination behaviors.
- **Key finding**: Apple and ARM GPUs do not support the linear occupancy-bound model hypothesized by prior work.

## Summary

GPU programming specifications say almost nothing about forward progress guarantees between workgroups, yet developers routinely rely on informal assumptions to build blocking synchronization idioms like mutexes and barriers. This work formalizes progress models, synthesizes comprehensive test suites, and empirically shows that GPU vendors provide significantly different levels of progress guarantees — information critical for writing portable GPU programs.""",
    },
    "oopsla2021a": {
        "title": "The Semantics of Shared Memory in Intel CPU/FPGA Systems",
        "authors": "D. Iorga, A. F. Donaldson, T. Sorensen, J. Wickerson",
        "venue": "OOPSLA, 2021",
        "summary": """This paper provides the first formal study of shared memory semantics for heterogeneous CPU/FPGA systems, focusing on Intel's Xeon+FPGA platform.

## Key Contributions

- **Dual formal models**: Both operational and axiomatic memory models for the Intel Xeon+FPGA system, capturing fine-grained shared memory interactions through Intel's Core Cache Interface (CCI-P).
- **Cross-validation**: Operational model mechanized in CBMC model checker; axiomatic model in Alloy. Models cross-checked against each other and validated against real hardware via 583 litmus tests.
- **Custom hardware**: A 'litmus-test processor' synthesized in FPGA to avoid the prohibitive cost of per-test hardware synthesis.

## Summary

CPU/FPGA systems with fine-grained shared memory are gaining popularity but present complex memory semantics that combine challenges of CPU concurrency with new FPGA-specific behaviors. This paper provides rigorous formal foundations through two complementary models, validated against real hardware, to help programmers and compiler writers reason about shared memory interactions in these heterogeneous systems.""",
    },
    "taco2021": {
        "title": "GraphAttack: Optimizing Data Supply for Graph Applications on In-Order Multicore Architectures",
        "authors": "A. Manocha, T. Sorensen, E. Tureci, O. Matthews, J. L. Aragón, M. Martonosi",
        "venue": "TACO, 2021",
        "summary": """This paper presents GraphAttack, a hardware-software approach that accelerates graph applications on in-order (InO) multicore architectures by optimizing data supply.

## Key Contributions

- **Compiler-driven decoupling**: Compiler passes identify long-latency loads and slice programs into Producer/Consumer thread pairs mapped onto parallel cores, drastically increasing memory-level parallelism.
- **Strong performance**: 2.87x speedup and 8.61x energy efficiency gain over OoO cores in equal-area comparisons; 3x speedup over 64 parallel cores.
- **Outperforms alternatives**: Beats OoO cores, do-all parallelism, prefetching, and prior decoupling approaches across a range of graph applications.

## Summary

Graph applications suffer from irregular memory access patterns that stall even powerful out-of-order processors. GraphAttack addresses this by using compiler analysis to split graph computations into producer threads (that prefetch data) and consumer threads (that compute), communicating through shared queues on adjacent in-order cores.""",
    },
    "oopsla2020": {
        "title": "Foundations of Empirical Memory Consistency Testing",
        "authors": "J. Kirkham, T. Sorensen, E. Tureci, M. Martonosi",
        "venue": "OOPSLA, 2020",
        "summary": """This paper rigorously investigates empirical memory model testing methodology, proposing techniques for efficient tuning of stressing parameters and analysis of large numbers of testing observations.

## Key Contributions

- **Meta-study of prior work**: Reveals prior results with low reproducibility and inefficient use of testing time.
- **Data peeking**: Enables lossless speedups of more than 5x in tuning stressing parameters.
- **Portable stressing**: Defines parameters losing only 12% efficiency when generalized across different GPU platforms.
- **Bug discovery**: Stress-tested an OpenCL 2.0 memory model conformance test suite and discovered a bug in Intel's compiler.

## Summary

Memory consistency testing relies on litmus tests run many times to detect exceedingly rare violations. The effectiveness depends heavily on stressing parameters, yet prior work lacked rigorous methodology for tuning these parameters. This paper provides practical foundations — including efficient tuning, portable parameter selection, and confidence metrics — evaluated across 3 GPUs from 3 vendors.""",
    },
    "rtas2020": {
        "title": "Slow and Steady: Measuring and Tuning Multicore Interference",
        "authors": "D. Iorga, T. Sorensen, J. Wickerson, A. F. Donaldson",
        "venue": "RTAS, 2020",
        "summary": """This paper explores the design and evaluation of techniques for empirically testing multicore interference using enemy programs, with focus on measurement reliability and portability.

## Key Contributions

- **Reliable measurement methodology**: A strategy based on percentiles and confidence intervals that provides competitive and reproducible observations.
- **Auto-tuning enemy programs**: Three tuning approaches (random search, simulated annealing, Bayesian optimization) evaluated on five chips spanning x86 and ARM architectures.
- **Practical evaluation**: Enemy programs evaluated on AutoBench and CoreMark benchmark suites, achieving statistically larger slowdown than prior work in 35/105 benchmark/chip combinations (max 3.8x).

## Summary

Multicore processors share resources (caches, buses, memory) that cause otherwise-independent programs to interfere with one another, which is critical for real-time systems. This paper provides reliable measurement methods and auto-tuning of "enemy programs" — specially crafted programs that maximize shared resource contention — to empirically bound interference effects across different architectures.""",
    },
    "ispass2020": {
        "title": "MosaicSim: A Lightweight, Modular Simulator for Heterogeneous Systems",
        "authors": "O. Matthews, A. Manocha, D. Giri, M. Orenes-Vera, E. Tureci, T. Sorensen, T. Ham, J. L. Aragón, L. Carloni, M. Martonosi",
        "venue": "ISPASS, 2020 (Best Paper Nomination)",
        "summary": """This paper introduces MosaicSim, a lightweight modular simulator for heterogeneous systems designed for hardware-software co-design exploration.

## Key Contributions

- **LLVM integration**: Uses the LLVM toolchain for efficient modeling of instruction dependencies and flexible additions across the software stack.
- **Modular composition**: Different hardware components (cores, accelerators, memory hierarchies) can be composed and integrated flexibly.
- **Validated accuracy**: Captures architectural bottlenecks and accurately models multicore scaling trends and accelerator behavior.

## Summary

As heterogeneous systems become mainstream, simulation tools must support rich combinations of general-purpose cores and specialized processing units while enabling agile hardware-software co-design exploration. MosaicSim meets these needs through a modular, lightweight design integrated with LLVM, enabling researchers to quickly evaluate architectural ideas across the full system stack.""",
    },
    "iiswc2019": {
        "title": "One Size Doesn't Fit All: Quantifying Performance Portability of Graph Applications on GPUs",
        "authors": "T. Sorensen, S. Pai, A. F. Donaldson",
        "venue": "IISWC, 2019 (Best Paper Award)",
        "summary": """This paper presents a methodology to automatically identify portable optimization policies for graph applications on GPUs, quantifying the trade-off between performance specialization and portability.

## Key Contributions

- **Large empirical study**: 17 graph applications x 3 graph inputs x 6 GPUs spanning multiple vendors, using a graph algorithm DSL compiler targeting OpenCL.
- **Statistical analysis methodology**: Characterizes optimizations and quantifies performance trade-offs at various degrees of specialization (chip, application, input).
- **Practical insights**: Fully portable approach provides 1.15x improvement; semi-specialization to application and input (not hardware) achieves 1.29x.

## Summary

Optimizing graph applications for GPUs is labor-intensive due to complex interactions between GPU architectures, applications, and inputs. This paper provides a rigorous methodology to quantify exactly how much performance is sacrificed for portability, and shows that semi-specialization offers a practical middle ground.""",
    },
    "concur2018": {
        "title": "GPU Schedulers: How Fair is Fair Enough?",
        "authors": "T. Sorensen, H. Evrard, A. F. Donaldson",
        "venue": "CONCUR, 2018",
        "summary": """This paper clarifies fairness properties of GPU schedulers, defining formal models for semi-fair scheduling that lies between fully fair and fully unfair.

## Key Contributions

- **Formal fairness framework**: A general temporal logic formula based on weak fairness, parameterized by predicates enabling per-thread fairness at specific execution points.
- **Three existing scheduler models analyzed**: HSA, OpenCL, and occupancy-bound execution — none strong enough for all existing GPU blocking applications.
- **Two new scheduler models**: Designed to support existing GPU applications; one enables more natural implementation of GPU protocols.

## Summary

GPU programming models like OpenCL provide almost no fairness guarantees, yet many useful applications rely on blocking synchronization (mutexes, barriers) that require some degree of fairness. This paper bridges the gap by formalizing semi-fair schedulers and proposing new scheduler models that capture the actual behavior of deployed GPUs more accurately than existing specifications.""",
    },
    "pldi2018": {
        "title": "The Semantics of Transactions and Weak Memory in x86, Power, ARM, and C++",
        "authors": "N. Chong, T. Sorensen, J. Wickerson",
        "venue": "PLDI, 2018 (Best Paper Award)",
        "summary": """This paper extends existing axiomatic weak memory models for x86, Power, ARMv8, and C++ with new rules for transactional memory (TM), clarifying their combined semantics.

## Key Contributions

- **Formal TM extensions**: Axiomatic weak memory models extended with transactional memory rules for four major architectures/languages.
- **Automated tooling**: Enables synthesis of validation tests and model-checking of TM-related transformations (lock elision, compiling C++ transactions to hardware).
- **Key finding**: A proposed TM extension to ARMv8 is incompatible with lock elision without sacrificing portability or performance.

## Summary

Both weak memory models and transactional memory are well-studied individually, but their interaction is poorly understood — problematic because x86, Power, and C++ all support both. This paper provides the first formal treatment of their combined semantics, backed by automated tools that found a significant incompatibility in an ARM research proposal.""",
    },
    "fse2017": {
        "title": "Cooperative Kernels: GPU Multitasking for Blocking Algorithms",
        "authors": "T. Sorensen, H. Evrard, A. F. Donaldson",
        "venue": "FSE, 2017 (Distinguished Paper Award)",
        "summary": """This paper proposes cooperative kernels, an extension to the GPU programming model that enables fair scheduling of workgroups and supports multitasking for blocking algorithms.

## Key Contributions

- **Cooperative kernel model**: Workgroups are fairly scheduled and can cooperate with the scheduler through language extensions, enabling blocking algorithms on GPUs.
- **GPU multitasking**: Kernels can flexibly resize to share the GPU with other workloads (e.g., graphics rendering).
- **OpenCL 2.0 prototype**: Implemented and evaluated with blocking GPU applications ported to cooperative kernels.

## Summary

Irregular data-parallel algorithms increasingly target GPUs but require blocking synchronization that demands fair scheduling. GPU programming models don't mandate fair scheduling. Cooperative kernels provide a principled solution through a small set of language extensions enabling kernel-scheduler cooperation, supporting both fair scheduling and GPU multitasking.""",
    },
    "popl2017": {
        "title": "Automatically Comparing Memory Consistency Models",
        "authors": "J. Wickerson, M. Batty, T. Sorensen, G. Constantinides",
        "venue": "POPL, 2017",
        "summary": """This paper presents a technique for automatically solving four key tasks in memory consistency model (MCM) design: generating conformance tests, distinguishing MCMs, checking compiler optimizations, and checking compiler mappings.

## Key Contributions

- **Unified constraint framework**: All four tasks formulated as instances of a general constraint-satisfaction problem, solved using the Alloy modeling framework.
- **Automated recreation of known results**: Distinctions between C11 variants, SC-DRF guarantee failures, x86 multi-copy atomicity, and bugs in C11 compiler optimizations.
- **New GPU MCM**: Developed and validated a memory consistency model for NVIDIA GPUs supporting natural OpenCL mapping.

## Summary

Memory consistency models are complex and counterintuitive, making them challenging to design and understand. This paper shows that four fundamental MCM reasoning tasks are instances of the same constraint-satisfaction problem, and provides an automated tool (based on Alloy) that can solve all four. The technique reproduced many known results and discovered new ones, including bugs in compiler mappings from OpenCL to AMD GPUs.""",
    },
    "oopsla2016": {
        "title": "Portable Inter-workgroup Barrier Synchronisation for GPUs",
        "authors": "T. Sorensen, A. F. Donaldson, M. Batty, G. Gopalakrishnan, Z. Rakamaric",
        "venue": "OOPSLA, 2016",
        "summary": """This paper presents the first portable and formally-specified inter-workgroup barrier for GPUs, addressing the deadlock risk from occupancy-bound execution.

## Key Contributions

- **Occupancy discovery protocol**: Dynamically discovers a safe occupancy estimate for a given GPU and kernel, enabling starvation-free (and deadlock-free) barriers.
- **Formal verification**: Barrier proven to meet its synchronization specification using OpenCL 2.0 atomic operations.
- **Portability**: Evaluated across 8 GPUs from 4 vendors; discovery protocol achieves nearly 100% recall.

## Summary

Inter-workgroup barriers are essential for many GPU applications but not supported by GPU programming models because occupancy-bound execution can cause deadlock. This paper solves the problem by dynamically discovering how many workgroups can safely execute concurrently, then restricting the barrier accordingly. The approach is formally verified, portable across vendors, and evaluated on practical applications.""",
    },
    "pldi2016": {
        "title": "Exposing Errors Related to Weak Memory in GPU Applications",
        "authors": "T. Sorensen, A. F. Donaldson",
        "venue": "PLDI, 2016",
        "summary": """This paper presents a systematic testing environment that uses stressing and fuzzing to reveal weak memory bugs in GPU applications.

## Key Contributions

- **Novel testing environment**: Sophisticated memory stressing strategy tuned per chip using nearly half a billion micro-benchmark executions — no prior knowledge of the application required.
- **Practical bug discovery**: Evaluated on 7 GPUs x 3 Nvidia architectures x 10 CUDA applications; discovered previously unknown weak memory issues in two applications.
- **Automatic fence suggestion**: Identifies root causes and suggests fence insertions to harden applications against weak memory bugs.

## Summary

GPU applications can exhibit subtle bugs due to weak memory effects. These bugs are extremely difficult to reproduce normally. This paper provides the first practical method for systematically provoking such bugs in real GPU applications, using a carefully tuned stressing environment that makes rare weak memory behaviors occur frequently.""",
    },
    "asplos2015": {
        "title": "GPU Concurrency: Weak Behaviours and Programming Assumptions",
        "authors": "J. Alglave, M. Batty, A. F. Donaldson, G. Gopalakrishnan, J. Ketema, D. Poetzl, T. Sorensen, J. Wickerson",
        "venue": "ASPLOS, 2015",
        "summary": """This paper presents the first large-scale empirical study of concurrent memory behavior on deployed GPUs, exposing false assumptions in vendor documentation and programming guides.

## Key Contributions

- **Massive litmus testing campaign**: Thousands of generated litmus tests executed under stressful workloads on deployed Nvidia and AMD GPUs across multiple architectures.
- **False beliefs exposed**: Folklore assumptions about GPU memory ordering — often supported by official tutorials — proven false.
- **Formal GPU memory model**: A variant of SPARC Relaxed Memory Order (RMO), structured for the GPU concurrency hierarchy, correctly modeling every observed behavior.

## Summary

GPU concurrency was poorly specified, forcing programmers to rely on unstated assumptions. This foundational paper conducted the first systematic empirical study of GPU memory behavior, exposing many false assumptions in vendor documentation and providing the first formal memory model for Nvidia GPUs.""",
    },
    "iccad2020": {
        "title": "A Simulator and Compiler Framework for Agile Hardware-Software Co-design Evaluation and Exploration",
        "authors": "T. Sorensen, A. Manocha, E. Tureci, M. Orenes-Vera, J. L. Aragón, M. Martonosi",
        "venue": "ICCAD, 2020 (Invited)",
        "summary": """This invited paper describes the DEC++ compiler and MosaicSim simulator pair, developed as part of the DECADES project for designing and taping out a new heterogeneous architecture.

## Key Contributions

- **Full-stack co-design**: Compiler (DEC++) and simulator (MosaicSim) designed specifically for agile hardware-software co-design exploration in heterogeneous systems.
- **DECADES project**: Multi-team effort to design and tape out a new heterogeneous architecture.
- **Case studies**: Design space explorations for data science application acceleration and heterogeneous parallel architectures.

## Summary

With the end of transistor scaling trends, performance improvements now come from specialization. This paper presents the DEC++ compiler and MosaicSim simulator as complementary tools for exploring the vast design space of heterogeneous architectures, enabling rapid evaluation of choices across programming models, compilers, ISAs, and specialized hardware.""",
    },
    "iwocl2019": {
        "title": "Performance Evaluation of OpenCL Standard Support (and Beyond)",
        "authors": "T. Sorensen, S. Pai, A. F. Donaldson",
        "venue": "IWOCL, 2019 (Best Paper Award)",
        "summary": """This paper evaluates how support for various OpenCL features across GPU vendors affects the performance of graph applications.

## Key Contributions

- **Controlled study**: 6 optimizations x 17 applications x 3 graph inputs x 6 GPUs from 4 vendors (Nvidia, AMD, Intel, ARM).
- **Key finding**: Limiting to OpenCL 2.0 features fails to achieve speedups in 70%+ of benchmarks; forward progress guarantees (beyond the standard) unlock the best optimizations.
- **Cross-vendor portability**: All optimizations can be beneficial across different GPUs despite significant architectural differences.

## Summary

OpenCL promises platform portability, but adoption of features varies widely across vendors. This paper quantifies the performance impact of progressively more advanced OpenCL features on graph applications, providing concrete motivation for vendors to adopt newer features and for the standard to include forward progress guarantees.""",
    },
    "iwocl2016": {
        "title": "The Hitchhiker's Guide to Cross-Platform OpenCL Application Development",
        "authors": "T. Sorensen, A. F. Donaldson",
        "venue": "IWOCL, 2016",
        "summary": """This experience report examines portability issues encountered when running OpenCL benchmarks across multiple GPU platforms from different vendors.

## Key Contributions

- **Portability audit**: Two sets of open-source benchmarks tested across a variety of GPU platforms; issues classified into framework bugs, specification limitations, and programming bugs.
- **Community analysis**: 58% of recent GPU papers evaluate GPUs from a single vendor only.
- **Practical guidance**: Lessons learned and recommendations for improving cross-platform OpenCL development.

## Summary

While OpenCL promises cross-platform portability, in practice many applications fail on platforms from different vendors. This paper systematically documents the portability issues encountered and provides practical insights for developers seeking genuinely portable GPU code.""",
    },
    "tinytocs2015": {
        "title": "I Compute, Therefore I Am (Buggy): Methodic Doubt Meets Multiprocessors",
        "authors": "J. Alglave, L. Maranget, D. Poetzl, T. Sorensen",
        "venue": "TinyToCS, 2015",
        "summary": """This short paper, inspired by Descartes' methodic doubt, advocates for systematically testing the memory ordering behavior of multi- and manycore chips rather than trusting folklore claims.

## Key Contributions

- **Demonstration by example**: The paper's own text is passed through a GPU cipher program using a published (buggy) mutex from *CUDA by Example*, producing visibly corrupted output — then corrected with proper synchronization.

## Summary

A creative demonstration that common GPU programming examples contain memory ordering bugs. By literally passing the paper's text through a broken cipher program, the authors make the abstract concept of weak memory bugs tangible, while advocating for rigorous testing over trusting published folklore.""",
    },
    "ics2013": {
        "title": "Towards Shared Memory Consistency Models for GPUs",
        "authors": "T. Sorensen, J. Alglave, G. Gopalakrishnan, V. Grover",
        "venue": "ICS, 2013 (1st Place Undergrad SRC)",
        "summary": """This early work proposes litmus tests for GPUs and an operational memory model (UGPU) for reasoning about GPU shared memory consistency, along with hardware testing results.

## Key Contributions

- **GPU-specific litmus tests**: Tests for relaxed coherence and scope-sensitive memory fence behavior — unique aspects of GPU architectures.
- **UGPU operational model**: Captures semantics of load, store, and scoped fence instructions, implemented in the Murphi modeling language.
- **Hardware testing**: Extended litmus testing tools to GPUs, revealing architecture-specific memory behaviors across Nvidia Kepler and Maxwell chips.

## Summary

This foundational undergraduate work established the first systematic approach to studying GPU memory consistency models, introducing GPU-specific litmus tests, proposing a formal operational model, and demonstrating through hardware testing that GPU memory behavior differs across architectures.""",
    },
}

# Step 1: Rename existing full-text files to _full.md
renamed = 0
for paper_id in papers:
    old_path = os.path.join(summaries_dir, f"{paper_id}.md")
    new_path = os.path.join(summaries_dir, f"{paper_id}_full.md")
    if os.path.exists(old_path):
        shutil.move(old_path, new_path)
        renamed += 1

print(f"Renamed {renamed} full-text files to _full.md")

# Step 2: Create summary files as _summary.md
created = 0
for paper_id, info in papers.items():
    filepath = os.path.join(summaries_dir, f"{paper_id}_summary.md")
    content = f"""# {info['title']}

**Authors:** {info['authors']}  
**Venue:** {info['venue']}  
**PDF:** [{paper_id}.pdf](../{paper_id}.pdf) | **Full Markdown:** [{paper_id}_full.md]({paper_id}_full.md)

{info['summary']}
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    created += 1

print(f"Created {created} summary files")

# Step 3: Update the combined index
combined_path = os.path.join(os.path.dirname(__file__), "files", "summaries.md")
with open(combined_path, "w", encoding="utf-8") as f:
    f.write("# Papers in Markdown\n\n")
    f.write("All research papers by Tyler Sorensen and collaborators are provided in two markdown formats:\n\n")
    f.write("- **Full Markdown**: Complete paper text converted from PDF to markdown, preserving the full content of each paper.\n")
    f.write("- **Summary Markdown**: Concise summaries highlighting key contributions and takeaways.\n\n")
    f.write("These markdown versions are designed to make the papers easily accessible to both humans and AI agents.\n\n")
    f.write("---\n\n")

    paper_list = list(papers.items())
    for paper_id, info in paper_list:
        f.write(f"### {info['title']}\n\n")
        f.write(f"**Authors:** {info['authors']}  \n")
        f.write(f"**Venue:** {info['venue']}  \n")
        f.write(f"[Full Markdown](summaries/{paper_id}_full.md) | [Summary](summaries/{paper_id}_summary.md) | [PDF](../{paper_id}.pdf)\n\n")

print(f"Updated combined index at {combined_path}")
