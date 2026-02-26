# Automatically Comparing Memory Consistency Models

**Authors:** J. Wickerson, M. Batty, T. Sorensen, G. Constantinides  
**Venue:** POPL, 2017  
**PDF:** [popl2017.pdf](../popl2017.pdf) | **Full Markdown:** [popl2017_full.md](popl2017_full.md)

This paper presents a technique for automatically solving four key tasks in memory consistency model (MCM) design: generating conformance tests, distinguishing MCMs, checking compiler optimizations, and checking compiler mappings.

## Key Contributions

- **Unified constraint framework**: All four tasks formulated as instances of a general constraint-satisfaction problem, solved using the Alloy modeling framework.
- **Automated recreation of known results**: Distinctions between C11 variants, SC-DRF guarantee failures, x86 multi-copy atomicity, and bugs in C11 compiler optimizations.
- **New GPU MCM**: Developed and validated a memory consistency model for NVIDIA GPUs supporting natural OpenCL mapping.

## Summary

Memory consistency models are complex and counterintuitive, making them challenging to design and understand. This paper shows that four fundamental MCM reasoning tasks are instances of the same constraint-satisfaction problem, and provides an automated tool (based on Alloy) that can solve all four. The technique reproduced many known results and discovered new ones, including bugs in compiler mappings from OpenCL to AMD GPUs.
