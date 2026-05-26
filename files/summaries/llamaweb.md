# Llamas on the Web: Memory-Efficient, Performance-Portable, and Multi-Precision LLM Inference with WebGPU

**Authors:** R. Levine, R. Sharma, N. Jain, A. Ramesh, Z. Chen, N. Abbas, J. Contini, T. Sorensen  
**Venue:** ArXiv, 2026  
**PDF:** [llamaweb.pdf](../llamaweb.pdf) | **Full Markdown:** [llamaweb.md](../markdown/llamaweb.md) | **arXiv:** [2605.20706](https://arxiv.org/abs/2605.20706)

This paper presents LlamaWeb, a WebGPU backend for llama.cpp that enables memory-efficient and performance-portable LLM inference in the browser.

## Key Contributions

- **Static memory planning**: Significantly reduces memory overhead through efficient memory management and model loading.
- **Tunable kernel library**: Addresses cross-device variability across heterogeneous hardware targets.
- **Templated GPU kernels**: Support performant implementations of numerous quantization formats, enabling broad model support.
- **29-33% less memory**: Compared to existing browser-based LLM frameworks across various device/browser/OS combinations.
- **45-69% higher decode throughput**: Compared to existing frameworks across four GPUs from separate vendors.
- **Competitive with native backends**: LlamaWeb performance is competitive with and even beats vendor-specific llama.cpp backend performance on some devices.

## Summary

Running language models in the browser presents a unique opportunity to build efficient, private, and portable AI applications, but requires contending with constrained memory availability and heterogeneous hardware targets. LlamaWeb addresses these challenges through static memory planning, a tunable kernel library, and templated GPU kernels supporting multiple quantization formats. Evaluated on 16 devices from 8 vendors with 10 language models, LlamaWeb demonstrates significant improvements in both memory efficiency and performance over existing browser-based LLM frameworks.
