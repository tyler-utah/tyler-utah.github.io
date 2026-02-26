# SHADOW: Simultaneous Multi-Threading Architecture with Asymmetric Threads

**Authors:** I. Chaturvedi, B. R. Godala, T. Sorensen, A. Gangavaram, T. M. Aamodt, D. Flyer, D. I. August  
**Venue:** MICRO, 2025  
**PDF:** [shadow.pdf](../shadow.pdf) | **Full Markdown:** [shadow_full.md](shadow_full.md)

This paper presents SHADOW, the first asymmetric SMT core that dynamically balances instruction-level parallelism (ILP) and thread-level parallelism (TLP) by running out-of-order (OoO) and in-order (InO) threads simultaneously on the same core.

## Key Contributions

- **Asymmetric SMT design**: Executes a heavyweight OoO thread alongside lightweight InO threads on the same core, maximizing CPU utilization.
- **Runtime-configurable**: Applications can optimize the mix of OoO and InO execution based on workload characteristics.
- **Strong performance**: Up to 3.16x speedup and 1.33x average improvement over OoO CPU across nine diverse benchmarks, with only 1% area and power overhead.
- **Dynamic adaptation**: Automatically redistributes work as ILP changes without software intervention.

## Summary

Many applications exhibit shifting demands between ILP and TLP due to irregular sparsity and unpredictable memory accesses. SHADOW leverages deep ILP in the OoO thread and high TLP in lightweight InO threads, dynamically adapting to workload variations. This outperforms conventional architectures and efficiently accelerates memory-bound workloads without compromising compute-bound performance.
