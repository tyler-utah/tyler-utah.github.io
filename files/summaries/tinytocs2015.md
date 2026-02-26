# I Compute, Therefore I Am (Buggy): Methodic Doubt Meets Multiprocessors

**Authors:** J. Alglave, L. Maranget, D. Poetzl, T. Sorensen  
**Venue:** TinyToCS, 2015  
**PDF:** [tinytocs2015.pdf](../tinytocs2015.pdf) | **Full Markdown:** [tinytocs2015.md](../markdown/tinytocs2015.md)

This short paper, inspired by Descartes' methodic doubt, advocates for systematically testing the memory ordering behavior of multi- and manycore chips rather than trusting folklore claims.

## Key Contributions

- **Demonstration by example**: The paper's own text is passed through a GPU cipher program using a published (buggy) mutex from *CUDA by Example*, producing visibly corrupted output — then corrected with proper synchronization.

## Summary

A creative demonstration that common GPU programming examples contain memory ordering bugs. By literally passing the paper's text through a broken cipher program, the authors make the abstract concept of weak memory bugs tangible, while advocating for rigorous testing over trusting published folklore.
