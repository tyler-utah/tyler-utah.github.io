# GPU Concurrency: Weak Behaviours and Programming Assumptions

**Authors:** J. Alglave, M. Batty, A. F. Donaldson, G. Gopalakrishnan, J. Ketema, D. Poetzl, T. Sorensen, J. Wickerson  
**Venue:** ASPLOS, 2015  
**PDF:** [asplos2015.pdf](../asplos2015.pdf) | **Full Markdown:** [asplos2015_full.md](asplos2015_full.md)

This paper presents the first large-scale empirical study of concurrent memory behavior on deployed GPUs, exposing false assumptions in vendor documentation and programming guides.

## Key Contributions

- **Massive litmus testing campaign**: Thousands of generated litmus tests executed under stressful workloads on deployed Nvidia and AMD GPUs across multiple architectures.
- **False beliefs exposed**: Folklore assumptions about GPU memory ordering — often supported by official tutorials — proven false.
- **Formal GPU memory model**: A variant of SPARC Relaxed Memory Order (RMO), structured for the GPU concurrency hierarchy, correctly modeling every observed behavior.

## Summary

GPU concurrency was poorly specified, forcing programmers to rely on unstated assumptions. This foundational paper conducted the first systematic empirical study of GPU memory behavior, exposing many false assumptions in vendor documentation and providing the first formal memory model for Nvidia GPUs.
