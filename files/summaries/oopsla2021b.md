# Specifying and Testing GPU Workgroup Progress Models

**Authors:** T. Sorensen, L. F. Salvador, H. Raval, H. Evrard, J. Wickerson, M. Martonosi, A. F. Donaldson  
**Venue:** OOPSLA, 2021  
**PDF:** [oopsla2021b.pdf](../oopsla2021b.pdf) | **Full Markdown:** [oopsla2021b.md](../markdown/oopsla2021b.md)

This paper provides a collection of tools and experimental data to aid specification designers in reasoning about forward progress guarantees for GPU workgroups.

## Key Contributions

- **Formal framework**: A small parallel programming language capturing fine-grained synchronization, with formal progress model specifications and a termination oracle.
- **Test synthesis**: 483 progress litmus tests synthesized from formal constraints describing programs requiring forward progress to terminate.
- **Large experimental campaign**: Tests run across 8 GPUs from 5 vendors, revealing significantly different termination behaviors.
- **Key finding**: Apple and ARM GPUs do not support the linear occupancy-bound model hypothesized by prior work.

## Summary

GPU programming specifications say almost nothing about forward progress guarantees between workgroups, yet developers routinely rely on informal assumptions to build blocking synchronization idioms like mutexes and barriers. This work formalizes progress models, synthesizes comprehensive test suites, and empirically shows that GPU vendors provide significantly different levels of progress guarantees — information critical for writing portable GPU programs.
