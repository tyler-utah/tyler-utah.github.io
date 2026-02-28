# Did You Know — Historic Log

<!-- Most recent entries appear at the top. -->

## 2026-02-28

<strong>Did you know?</strong> The <em>LeftoverLocals</em> vulnerability (CVE-2023-49691) allows any co-resident process to eavesdrop on GPU local memory left behind by another process — on Apple, AMD, and Qualcomm GPUs. On an AMD Radeon RX 7900 XT running a 7B LLM (llama.cpp), this leaks ~181 MB per query, enough to reconstruct the full LLM response with high fidelity, and the attack requires fewer than 10 lines of GPU code. Many affected GPUs have since been patched, but at the time of the paper's writing this vulnerability was present across a wide range of hardware. <em>(from: <a href="files/markdown/leftoverlocals2024.md">LeftoverLocals: Listening to LLM Responses Through Leaked GPU Local Memory</a>)</em>
