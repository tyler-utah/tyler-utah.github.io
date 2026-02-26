# Foundations of Empirical Memory Consistency Testing

**Authors:** J. Kirkham, T. Sorensen, E. Tureci, M. Martonosi  
**Venue:** OOPSLA, 2020  
**PDF:** [oopsla2020.pdf](../oopsla2020.pdf) | **Full Markdown:** [oopsla2020.md](../markdown/oopsla2020.md)

This paper rigorously investigates empirical memory model testing methodology, proposing techniques for efficient tuning of stressing parameters and analysis of large numbers of testing observations.

## Key Contributions

- **Meta-study of prior work**: Reveals prior results with low reproducibility and inefficient use of testing time.
- **Data peeking**: Enables lossless speedups of more than 5x in tuning stressing parameters.
- **Portable stressing**: Defines parameters losing only 12% efficiency when generalized across different GPU platforms.
- **Bug discovery**: Stress-tested an OpenCL 2.0 memory model conformance test suite and discovered a bug in Intel's compiler.

## Summary

Memory consistency testing relies on litmus tests run many times to detect exceedingly rare violations. The effectiveness depends heavily on stressing parameters, yet prior work lacked rigorous methodology for tuning these parameters. This paper provides practical foundations — including efficient tuning, portable parameter selection, and confidence metrics — evaluated across 3 GPUs from 3 vendors.
