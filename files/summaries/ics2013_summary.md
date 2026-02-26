# Towards Shared Memory Consistency Models for GPUs

**Authors:** T. Sorensen, J. Alglave, G. Gopalakrishnan, V. Grover  
**Venue:** ICS, 2013 (1st Place Undergrad SRC)  
**PDF:** [ics2013.pdf](../ics2013.pdf) | **Full Markdown:** [ics2013_full.md](ics2013_full.md)

This early work proposes litmus tests for GPUs and an operational memory model (UGPU) for reasoning about GPU shared memory consistency, along with hardware testing results.

## Key Contributions

- **GPU-specific litmus tests**: Tests for relaxed coherence and scope-sensitive memory fence behavior — unique aspects of GPU architectures.
- **UGPU operational model**: Captures semantics of load, store, and scoped fence instructions, implemented in the Murphi modeling language.
- **Hardware testing**: Extended litmus testing tools to GPUs, revealing architecture-specific memory behaviors across Nvidia Kepler and Maxwell chips.

## Summary

This foundational undergraduate work established the first systematic approach to studying GPU memory consistency models, introducing GPU-specific litmus tests, proposing a formal operational model, and demonstrating through hardware testing that GPU memory behavior differs across architectures.
