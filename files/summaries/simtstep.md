# SIMT-Step Execution: A Flexible Operational Semantics for GPU Subgroup Behavior

**Authors:** Z. Chen, N. Rehman, G. Martínez, T. Sorensen  
**Venue:** PLDI, 2026  
**PDF:** [simtstep.pdf](../simtstep.pdf) | **Full Markdown:** [simtstep.md](../markdown/simtstep.md)

This paper presents SIMT-Step, a formal and flexible operational semantics for specifying subgroup (warp) behavior in GPU programming languages.

## Key Contributions

- **Dynamic basic blocks**: A new semantic object that enables precise specification of converged subgroup execution, tracking which threads participate in subgroup operations even under divergent control flow.
- **Flexible instruction execution model**: Instructions can be classified as independent (standard interleaving), synchronous (implicit thread synchronization), or collective (atomic across active threads).
- **Six SIMT-Step instantiations**: Ranging from fully lockstep (Collective Memory) to highly relaxed (Symbolic SG Op), providing candidate specifications for language designers.
- **TLA+ implementation**: Executable semantics with a GLSL frontend for testing and exploration.
- **Large-scale empirical study**: Fuzzing campaign across 10 GPUs from 8 vendors with 100k tests; most GPUs exhibit strongly synchronous behavior, with rare exceptions requiring further investigation.

## Summary

GPU subgroup operations are powerful but poorly specified—compilers may transform code in ways that disrupt expected synchronous behavior. SIMT-Step addresses this by formalizing when threads converge, diverge, and merge through dynamic blocks, and by providing flexibility in how strictly instructions synchronize. The framework was developed in consultation with GPU specification groups and provides both theoretical foundations and practical tools for reasoning about subgroup semantics.
