# The Semantics of Shared Memory in Intel CPU/FPGA Systems

**Authors:** D. Iorga, A. F. Donaldson, T. Sorensen, J. Wickerson  
**Venue:** OOPSLA, 2021  
**PDF:** [oopsla2021a.pdf](../oopsla2021a.pdf) | **Full Markdown:** [oopsla2021a.md](../markdown/oopsla2021a.md)

This paper provides the first formal study of shared memory semantics for heterogeneous CPU/FPGA systems, focusing on Intel's Xeon+FPGA platform.

## Key Contributions

- **Dual formal models**: Both operational and axiomatic memory models for the Intel Xeon+FPGA system, capturing fine-grained shared memory interactions through Intel's Core Cache Interface (CCI-P).
- **Cross-validation**: Operational model mechanized in CBMC model checker; axiomatic model in Alloy. Models cross-checked against each other and validated against real hardware via 583 litmus tests.
- **Custom hardware**: A 'litmus-test processor' synthesized in FPGA to avoid the prohibitive cost of per-test hardware synthesis.

## Summary

CPU/FPGA systems with fine-grained shared memory are gaining popularity but present complex memory semantics that combine challenges of CPU concurrency with new FPGA-specific behaviors. This paper provides rigorous formal foundations through two complementary models, validated against real hardware, to help programmers and compiler writers reason about shared memory interactions in these heterogeneous systems.
