# MosaicSim: A Lightweight, Modular Simulator for Heterogeneous Systems

**Authors:** O. Matthews, A. Manocha, D. Giri, M. Orenes-Vera, E. Tureci, T. Sorensen, T. Ham, J. L. Aragón, L. Carloni, M. Martonosi  
**Venue:** ISPASS, 2020 (Best Paper Nomination)  
**PDF:** [ispass2020.pdf](../ispass2020.pdf) | **Full Markdown:** [ispass2020_full.md](ispass2020_full.md)

This paper introduces MosaicSim, a lightweight modular simulator for heterogeneous systems designed for hardware-software co-design exploration.

## Key Contributions

- **LLVM integration**: Uses the LLVM toolchain for efficient modeling of instruction dependencies and flexible additions across the software stack.
- **Modular composition**: Different hardware components (cores, accelerators, memory hierarchies) can be composed and integrated flexibly.
- **Validated accuracy**: Captures architectural bottlenecks and accurately models multicore scaling trends and accelerator behavior.

## Summary

As heterogeneous systems become mainstream, simulation tools must support rich combinations of general-purpose cores and specialized processing units while enabling agile hardware-software co-design exploration. MosaicSim meets these needs through a modular, lightweight design integrated with LLVM, enabling researchers to quickly evaluate architectural ideas across the full system stack.
