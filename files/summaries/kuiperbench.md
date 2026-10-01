# The Next Frontier for AI-Generated Kernels: Correctness

**Authors:** G. Martínez, T. Sorensen

**Venue:** PAgE @ PLDI, 2026

**PDF:** [kuiperbench.pdf](../kuiperbench.pdf) | **Full Markdown:** [kuiperbench.md](../markdown/kuiperbench.md) | **DOI:** [10.1145/3819802.3820580](https://doi.org/10.1145/3819802.3820580)

This paper argues that test suites are an inadequate correctness boundary for
AI-generated GPU kernels and demonstrates a proof-carrying alternative using
Kuiper, a verified GPU programming framework embedded in F* and Pulse.

## Key Contributions

- **KernelBench oracle audit**: Demonstrates both false positives, where buggy
  kernels pass, and false negatives caused by numerical tolerances and precision
  contracts.
- **Agentic verification workflow**: Coding agents generate and test Kuiper
  implementations, write functional specifications, and iteratively complete
  proofs using verifier feedback.
- **Complete Level 1 coverage**: Provides verified implementations for all 100
  KernelBench Level 1 tasks, written almost entirely by coding agents.
- **Reusable verified infrastructure**: Develops compositional support for
  reductions, matrix operations, pooling, convolutions, layouts, and
  floating-point reasoning.

## Summary

KernelBench accepts generated kernels by comparing them with reference outputs
on a limited set of inputs. The paper shows that this approach can accept real
semantic bugs and reject valid implementations whose operation ordering or
precision differs from the reference. Its alternative makes Kuiper programs the
generation target, providing memory safety, data-race freedom, and functional
correctness through machine-checked specifications and proofs before extraction
to CUDA.

The results show that coding agents can produce verified kernels across an
entire benchmark level, but also identify important limits. The generated
kernels are correctness-first and not yet competitive with hand-tuned CUDA on
KernelBench performance metrics, specifications still require review, and the
paper reports a small amount of residual proof debt.

