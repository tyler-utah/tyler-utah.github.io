# One Size Doesn't Fit All: Quantifying Performance Portability of Graph Applications on GPUs

**Authors:** T. Sorensen, S. Pai, A. F. Donaldson  
**Venue:** IISWC, 2019 (Best Paper Award)  
**PDF:** [iiswc2019.pdf](../iiswc2019.pdf) | **Full Markdown:** [iiswc2019_full.md](iiswc2019_full.md)

This paper presents a methodology to automatically identify portable optimization policies for graph applications on GPUs, quantifying the trade-off between performance specialization and portability.

## Key Contributions

- **Large empirical study**: 17 graph applications x 3 graph inputs x 6 GPUs spanning multiple vendors, using a graph algorithm DSL compiler targeting OpenCL.
- **Statistical analysis methodology**: Characterizes optimizations and quantifies performance trade-offs at various degrees of specialization (chip, application, input).
- **Practical insights**: Fully portable approach provides 1.15x improvement; semi-specialization to application and input (not hardware) achieves 1.29x.

## Summary

Optimizing graph applications for GPUs is labor-intensive due to complex interactions between GPU architectures, applications, and inputs. This paper provides a rigorous methodology to quantify exactly how much performance is sacrificed for portability, and shows that semi-specialization offers a practical middle ground.
