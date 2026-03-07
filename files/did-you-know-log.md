# Did You Know — Historic Log

<!-- Most recent entries appear at the top. -->

## 2026-03-02

<strong>Did you know?</strong> There is no official ABI (Application Binary Interface) for concurrent programs — meaning that mixing binaries compiled by different compilers (e.g., LLVM and GCC) using different mappings of C/C++ atomic operations to assembly is technically undefined, yet it happens routinely in industry. The <em>Mix Testing</em> technique exposed this gap by discovering four previously-unknown concurrency bugs in LLVM and GCC, and one prospective bug in proposed JVM mappings, simply by compiling different parts of a test program with different atomic-operation mappings and linking them together. <em>(from: <a href="files/markdown/mix_testing.md">Mix Testing: Specifying and Testing ABI Compatibility of C/C++ Atomics Implementations</a>)</em>

## 2026-03-01

<strong>Did you know?</strong> The <em>MEMORY DISORDER</em> attack turns the CPU/GPU's own relaxed memory model into a <em>timerless</em> side-channel: by repeatedly running tiny two-thread "litmus tests" and counting how often memory operations are observed out-of-order, an attacker process can detect what a victim process is doing — with no clock needed at all. The technique achieves a covert channel of nearly 30,000 bits/second on x86 CPUs and can reliably fingerprint which deep neural network architecture (e.g., ResNet-50 vs. VGG-16) a victim is running on an Apple M3 GPU. <em>(from: <a href="files/markdown/disorder.md">Memory DisOrder: Memory Re-orderings as a Timerless Side-channel</a>)</em>

## 2026-02-28

<strong>Did you know?</strong> The <em>LeftoverLocals</em> vulnerability (CVE-2023-49691) allows any co-resident process to eavesdrop on GPU local memory left behind by another process — on Apple, AMD, and Qualcomm GPUs. On an AMD Radeon RX 7900 XT running a 7B LLM (llama.cpp), this leaks ~181 MB per query, enough to reconstruct the full LLM response with high fidelity, and the attack requires fewer than 10 lines of GPU code. Many affected GPUs have since been patched, but at the time of the paper's writing this vulnerability was present across a wide range of hardware. <em>(from: <a href="files/markdown/leftoverlocals2024.md">LeftoverLocals: Listening to LLM Responses Through Leaked GPU Local Memory</a>)</em>
