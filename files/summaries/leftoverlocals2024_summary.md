# LeftoverLocals: Listening to LLM Responses Through Leaked GPU Local Memory

**Authors:** T. Sorensen, H. Khlaaf  
**Venue:** ArXiv, 2024  
**PDF:** [leftoverlocals2024.pdf](../leftoverlocals2024.pdf) | **Full Markdown:** [leftoverlocals2024_full.md](leftoverlocals2024_full.md)

This paper describes LeftoverLocals (CVE-2023-49691), a vulnerability that allows data recovery from GPU local memory created by another process, with particular implications for LLM and ML model security.

## Key Contributions

- **Vulnerability discovery**: GPU local memory — an optimized memory region — is not properly cleared between process invocations on Apple, Qualcomm, and AMD GPUs.
- **LLM eavesdropping PoC**: Demonstrated an attacker listening to another user's interactive LLM session (e.g., llama.cpp) across process or container boundaries, leaking ~5.5 MB per GPU invocation (~181 MB per LLM query on AMD Radeon RX 7900 XT).
- **Large-scale coordinated disclosure**: Worked with CERT Coordination Center to disclose to all major GPU vendors (NVIDIA, Apple, AMD, Arm, Intel, Qualcomm, Imagination).
- **Vendor response**: Apple's A17 and M3 processors contain fixes; AMD devices remain impacted; Qualcomm released firmware patches for some devices.

## Summary

As ML applications increasingly run on diverse GPUs (not just NVIDIA), the security of these devices is critical. LeftoverLocals shows that many GPUs fail to isolate local memory between processes, enabling an attacker to reconstruct LLM responses with high fidelity. The vulnerability highlights that many parts of the ML stack have not been rigorously reviewed by security experts.
