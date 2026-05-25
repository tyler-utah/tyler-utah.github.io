# Behind Bars: A Side-Channel Attack on NVIDIA MIG Cache Partitioning Using Memory Barriers

**Authors:** C. Gu, R. Levine, Z. Zhang, T. Sorensen, Y. Guo  
**Venue:** USENIX Security, 2026  
**PDF:** [behindbars.pdf](../behindbars.pdf) | **Full Markdown:** [behindbars.md](../markdown/behindbars.md)

This paper demonstrates that NVIDIA's MIG (Multi-Instance GPU) cache partitioning can be bypassed through a novel timing side-channel attack using memory barriers.

## Key Contributions

- **Cross-instance L2 cache interference discovery**: Despite MIG's physical cache partitioning, memory barriers (membars) issued in one instance affect load timing in other instances.
- **Membar triggering mechanisms identified**: Membars can be triggered by kernel launches, certain CUDA memory management APIs, and CUDA context creation/destruction.
- **Membar+Load covert channel**: A new timing-based attack where senders transmit bits by issuing membars, and receivers detect them by timing LD.STRONG.GPU instructions.
- **LLM inference fingerprinting attack**: Demonstrates that different LLMs have distinct kernel launch patterns, allowing attackers to identify the model in use and estimate input/output token counts.
- **Graph processing fingerprinting**: Shows kernel launch patterns vary by input graph, enabling graph identification attacks.

## Summary

NVIDIA MIG is designed to provide hardware isolation for secure multi-tenancy on data center GPUs, forming the foundation of NVIDIA's confidential computing stack. This work shows that despite L2 cache partitioning, cross-instance interference via memory barriers creates an exploitable side channel. The Membar+Load attack can fingerprint LLM inference workloads and infer sensitive information about GPU applications running in supposedly isolated MIG instances.
