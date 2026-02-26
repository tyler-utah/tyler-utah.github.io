# GPU Schedulers: How Fair is Fair Enough?

**Authors:** T. Sorensen, H. Evrard, A. F. Donaldson  
**Venue:** CONCUR, 2018  
**PDF:** [concur2018.pdf](../concur2018.pdf) | **Full Markdown:** [concur2018.md](../markdown/concur2018.md)

This paper clarifies fairness properties of GPU schedulers, defining formal models for semi-fair scheduling that lies between fully fair and fully unfair.

## Key Contributions

- **Formal fairness framework**: A general temporal logic formula based on weak fairness, parameterized by predicates enabling per-thread fairness at specific execution points.
- **Three existing scheduler models analyzed**: HSA, OpenCL, and occupancy-bound execution — none strong enough for all existing GPU blocking applications.
- **Two new scheduler models**: Designed to support existing GPU applications; one enables more natural implementation of GPU protocols.

## Summary

GPU programming models like OpenCL provide almost no fairness guarantees, yet many useful applications rely on blocking synchronization (mutexes, barriers) that require some degree of fairness. This paper bridges the gap by formalizing semi-fair schedulers and proposing new scheduler models that capture the actual behavior of deployed GPUs more accurately than existing specifications.
