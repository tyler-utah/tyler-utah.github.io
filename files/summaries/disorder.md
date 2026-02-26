# Memory DisOrder: Memory Re-orderings as a Timerless Side-channel

**Authors:** S. Siddens, S. Srivastava, R. Levine, J. Dykstra, T. Sorensen  
**Venue:** ArXiv, 2026  
**PDF:** [disorder.pdf](../disorder.pdf) | **Full Markdown:** [disorder.md](../markdown/disorder.md)

This paper presents MEMORY DISORDER, a novel timerless side-channel attack that exploits memory re-orderings arising from hardware relaxed memory consistency models. The attack requires only the ability to launch threads and execute basic memory loads and stores — no timers needed.

## Key Contributions

- **Fuzzing campaign** across mainstream processors (x86/Arm/Apple CPUs, NVIDIA/AMD/Apple GPUs) showing cross-process re-ordering signals on many devices.
- **Covert channel** achieving up to 16 bits/second with 95% accuracy on an Apple M3 GPU.
- **Application fingerprinting** with reliable closed-world DNN architecture fingerprinting on several CPUs and an Apple M3 GPU.
- **Exploitation of low-level system details** to amplify re-orderings, showing potential for nearly 30K bits/second on x86 CPUs.

## Summary

The key insight is that memory re-orderings — which arise naturally from hardware optimizations in relaxed memory models — occur more frequently when other cores are active. By repeatedly executing litmus tests (small concurrent programs that detect re-orderings), an attacker process can infer activity on victim processes without requiring any timer access. This makes DISORDER a low-capability attack deployable in more situations than traditional timer-based side-channels.
