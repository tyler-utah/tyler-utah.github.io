# Llamas on the Web: Memory-Efficient, Performance-Portable, and Multi-Precision LLM Inference with WebGPU

**Authors:** R. Levine, R. Sharma, N. Jain, A. Ramesh, Z. Chen, N. Abbas, J. Contini, T. Sorensen  
**Venue:** ArXiv, 2026  
**PDF:** [llamaweb.pdf](../llamaweb.pdf) | **arXiv:** [2605.20706](https://arxiv.org/abs/2605.20706)

---

## Abstract

Running language models in the browser presents a unique opportunity to build efficient, private, and portable AI applications, but requires contending with constrained memory availability and heterogeneous hardware targets. To realize this opportunity, we present Llamas on the Web (LlamaWeb), a WebGPU backend for llama.cpp that enables memory-efficient and performance-portable LLM inference across a wide range of model weight formats in the browser.

Our design significantly reduces memory overhead through static memory planning and efficient model loading, addresses cross-device variability through a tunable kernel library, and introduces templated GPU kernels that support performant implementations of numerous quantization formats, enabling broad model support and extensibility to new formats.

We evaluate LlamaWeb on 16 devices from 8 vendors, collecting data from 10 language models and four model weight formats. We compare LlamaWeb against existing browser-based LLM frameworks and find that LlamaWeb requires 29-33% less memory across several combinations of device, browser, and operating system. We also evaluate LlamaWeb's performance against these frameworks and find that it increases decode throughput by 45-69% across four GPUs from separate vendors. In addition, we compare LlamaWeb's performance against other llama.cpp backends, where it is competitive with and even beats vendor-specific backend performance on some devices.

## Introduction

The demand for running large language models (LLMs) in web browsers has grown significantly, driven by the desire for:
- **Privacy**: Local inference keeps data on the user's device
- **Portability**: Web applications run across all platforms
- **Efficiency**: No server infrastructure needed

However, browser-based LLM inference faces unique challenges:
- **Memory constraints**: Browsers have limited GPU memory access
- **Hardware heterogeneity**: Must work across diverse GPU vendors and architectures
- **Performance variability**: Cross-device performance can vary dramatically

## LlamaWeb Design

LlamaWeb is built as a WebGPU backend for the popular llama.cpp framework, bringing its extensive model support and optimizations to the browser.

### Static Memory Planning

Unlike traditional approaches that allocate memory dynamically during inference, LlamaWeb uses static memory planning to:
- Pre-compute all memory requirements before inference
- Minimize memory fragmentation
- Reduce peak memory usage by 29-33%

### Tunable Kernel Library

To address cross-device variability, LlamaWeb includes a tunable kernel library that:
- Automatically selects optimal kernel configurations per device
- Adapts to different GPU architectures
- Balances occupancy and register pressure

### Templated GPU Kernels

LlamaWeb introduces templated GPU kernels that:
- Support multiple quantization formats (Q4_0, Q4_K, Q8_0, F16, etc.)
- Enable code reuse across formats
- Allow easy extensibility to new quantization schemes

## Evaluation

### Experimental Setup

- **Devices**: 16 devices from 8 vendors (NVIDIA, AMD, Intel, Apple, Qualcomm, etc.)
- **Models**: 10 language models (Llama 3, Phi-3, Gemma, etc.)
- **Formats**: 4 model weight formats

### Memory Efficiency

Compared to existing browser-based LLM frameworks:
- **29-33% less memory** across various device/browser/OS combinations
- Enables running larger models that previously exceeded memory limits

### Performance

Compared to existing browser-based frameworks:
- **45-69% higher decode throughput** across four GPUs from separate vendors

Compared to native llama.cpp backends:
- Competitive performance with vendor-specific backends
- Beats native backend performance on some devices

## Conclusion

LlamaWeb demonstrates that high-performance, memory-efficient LLM inference is achievable in the browser through careful system design. By combining static memory planning, tunable kernels, and templated GPU code generation, LlamaWeb significantly improves both memory efficiency and performance over existing browser-based solutions while maintaining broad compatibility across diverse hardware platforms.
