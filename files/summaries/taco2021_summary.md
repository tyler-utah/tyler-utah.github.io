# GraphAttack: Optimizing Data Supply for Graph Applications on In-Order Multicore Architectures

**Authors:** A. Manocha, T. Sorensen, E. Tureci, O. Matthews, J. L. Aragón, M. Martonosi  
**Venue:** TACO, 2021  
**PDF:** [taco2021.pdf](../taco2021.pdf) | **Full Markdown:** [taco2021_full.md](taco2021_full.md)

This paper presents GraphAttack, a hardware-software approach that accelerates graph applications on in-order (InO) multicore architectures by optimizing data supply.

## Key Contributions

- **Compiler-driven decoupling**: Compiler passes identify long-latency loads and slice programs into Producer/Consumer thread pairs mapped onto parallel cores, drastically increasing memory-level parallelism.
- **Strong performance**: 2.87x speedup and 8.61x energy efficiency gain over OoO cores in equal-area comparisons; 3x speedup over 64 parallel cores.
- **Outperforms alternatives**: Beats OoO cores, do-all parallelism, prefetching, and prior decoupling approaches across a range of graph applications.

## Summary

Graph applications suffer from irregular memory access patterns that stall even powerful out-of-order processors. GraphAttack addresses this by using compiler analysis to split graph computations into producer threads (that prefetch data) and consumer threads (that compute), communicating through shared queues on adjacent in-order cores.
