# The Semantics of Transactions and Weak Memory in x86, Power, ARM, and C++

**Authors:** N. Chong, T. Sorensen, J. Wickerson  
**Venue:** PLDI, 2018 (Best Paper Award)  
**PDF:** [pldi2018.pdf](../pldi2018.pdf) | **Full Markdown:** [pldi2018_full.md](pldi2018_full.md)

This paper extends existing axiomatic weak memory models for x86, Power, ARMv8, and C++ with new rules for transactional memory (TM), clarifying their combined semantics.

## Key Contributions

- **Formal TM extensions**: Axiomatic weak memory models extended with transactional memory rules for four major architectures/languages.
- **Automated tooling**: Enables synthesis of validation tests and model-checking of TM-related transformations (lock elision, compiling C++ transactions to hardware).
- **Key finding**: A proposed TM extension to ARMv8 is incompatible with lock elision without sacrificing portability or performance.

## Summary

Both weak memory models and transactional memory are well-studied individually, but their interaction is poorly understood — problematic because x86, Power, and C++ all support both. This paper provides the first formal treatment of their combined semantics, backed by automated tools that found a significant incompatibility in an ARM research proposal.
