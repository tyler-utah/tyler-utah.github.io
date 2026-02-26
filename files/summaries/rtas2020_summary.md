# Slow and Steady: Measuring and Tuning Multicore Interference

**Authors:** D. Iorga, T. Sorensen, J. Wickerson, A. F. Donaldson  
**Venue:** RTAS, 2020  
**PDF:** [rtas2020.pdf](../rtas2020.pdf) | **Full Markdown:** [rtas2020_full.md](rtas2020_full.md)

This paper explores the design and evaluation of techniques for empirically testing multicore interference using enemy programs, with focus on measurement reliability and portability.

## Key Contributions

- **Reliable measurement methodology**: A strategy based on percentiles and confidence intervals that provides competitive and reproducible observations.
- **Auto-tuning enemy programs**: Three tuning approaches (random search, simulated annealing, Bayesian optimization) evaluated on five chips spanning x86 and ARM architectures.
- **Practical evaluation**: Enemy programs evaluated on AutoBench and CoreMark benchmark suites, achieving statistically larger slowdown than prior work in 35/105 benchmark/chip combinations (max 3.8x).

## Summary

Multicore processors share resources (caches, buses, memory) that cause otherwise-independent programs to interfere with one another, which is critical for real-time systems. This paper provides reliable measurement methods and auto-tuning of "enemy programs" — specially crafted programs that maximize shared resource contention — to empirically bound interference effects across different architectures.
