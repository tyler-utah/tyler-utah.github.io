# MC Mutants: Evaluating and Improving Testing for Memory Consistency Specifications

**Authors:** R. Levine, T. Guo, M. Cho, A. Baker, R. Levien, D. Neto, A. Quinn, T. Sorensen  
**Venue:** ASPLOS, 2023 (Distinguished Paper Award, Distinguished Artifact Award)  
**PDF:** [mcmutants2023.pdf](../mcmutants2023.pdf) | **Full Markdown:** [mcmutants2023_full.md](mcmutants2023_full.md)

This paper proposes MC Mutants, a mutation testing approach for evaluating and improving memory consistency specification (MCS) testing environments.

## Key Contributions

- **Mutation testing for MCS**: Mutates MCS litmus tests to simulate potential platform bugs, providing a mutation score metric to evaluate testing environments — solving the problem that real MCS violations are too rare to use as an efficacy metric.
- **Parallel testing environment**: Improves testing speed by three orders of magnitude over prior work.
- **Confidence strategy**: Parameterized over a time budget and confidence threshold, requiring only 64 seconds per test.
- **Practical impact**: Identified two bugs in WebGPU implementations (one leading to a specification change), and the WebGPU conformance test suite adopted this approach.

## Summary

The effectiveness of memory consistency testing depends heavily on the testing environment (e.g., whether stress is applied), but evaluating these environments has been difficult since real violations are extremely rare. MC Mutants creates synthetic but realistic mutations that simulate bugs, enabling rigorous evaluation and improvement of testing strategies. Implemented in WebGPU, the approach achieved broad adoption in the official conformance test suite.
