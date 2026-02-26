# BetterTogether: An Interference-Aware Framework for Fine-grained Software Pipelining on Heterogeneous SoCs

**Authors:** Y. Xu, R. Sharma, Z. Chen, S. Mistry, T. Sorensen  
**Venue:** IISWC, 2025 (Best Paper Award)  
**PDF:** [bettertogether2025.pdf](../bettertogether2025.pdf) | **Full Markdown:** [bettertogether2025_full.md](bettertogether2025_full.md)

This paper presents BetterTogether, a scheduling framework that enables fine-grained software pipelining on heterogeneous edge SoCs while accounting for inter-processing-unit interference.

## Key Contributions

- **Interference-aware performance model**: Captures execution time under representative intra-application interference, producing predictions that strongly correlate with measured results.
- **Flexible pipeline scheduling**: Applications are decomposed into stages with CPU and GPU implementations, then pipelined across the SoC's various processing units.
- **Cross-vendor portability**: Evaluated on three SoCs with GPUs from NVIDIA, Arm, and Qualcomm using three computer vision workloads.
- **Strong speedups**: Geomean 2.14x and maximum 7.59x speedup over homogeneous GPU baselines.

## Summary

Edge SoCs contain diverse processing units (big.LITTLE CPUs, GPUs, accelerators) with varying performance characteristics. BetterTogether exploits this heterogeneity through pipeline parallelism, where stages are mapped to the most suitable processing units. Its key innovation is a profile-guided model that accounts for the interference between simultaneously active processing units — a critical factor on resource-constrained edge devices.
