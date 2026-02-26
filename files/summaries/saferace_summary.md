# SafeRace: Assessing and Addressing WebGPU Memory Safety in the Presence of Data Races

**Authors:** R. Levine, A. Lee, N. Abbas, K. Little, T. Sorensen  
**Venue:** OOPSLA, 2025  
**PDF:** [saferace.pdf](../saferace.pdf) | **Full Markdown:** [saferace_full.md](saferace_full.md)

This paper identifies a specification vulnerability in the WebGPU Shading Language (WGSL) where data races can compromise memory safety, and proposes the SafeRace framework to address it.

## Key Contributions

- **Specification vulnerability discovery**: Data races in WGSL can cause optimizing compilers to legitimately remove memory safety bounds-checks, creating a "ticking time bomb" as compilers evolve.
- **SafeRace Memory Safety Guarantee (SMSG)**: A two-component solution — (1) a compiler pass ensuring race-free memory indexing slices, and (2) requirements on intermediate representations to limit data race effects.
- **81-hour fuzzing campaign** across 21 compilation stacks validating the approach; violations found on only one (likely buggy) machine.
- **Security discoveries**: GPU memory isolation vulnerabilities in Apple and AMD GPUs, plus a security-critical miscompilation in a pre-release Firefox.

## Summary

WebGPU enables powerful GPU computation in web browsers, but WGSL's compilation through lower-level intermediate representations creates risks. SafeRace shows that data races can undermine bounds-checks that enforce memory safety, and proposes practical solutions with minimal performance overhead on important WebGPU applications.
