# Behind Bars: A Side-Channel Attack on NVIDIA MIG Cache Partitioning Using Memory Barriers

**Authors:** C. Gu, R. Levine, Z. Zhang, T. Sorensen, Y. Guo  
**Venue:** USENIX Security, 2026  
**PDF:** [behindbars.pdf](../behindbars.pdf)

---

## Abstract

NVIDIA Multi-Instance GPU (MIG) is a feature designed to enable isolation and secure multi-tenancy on large data center GPUs. MIG partitions a single GPU into multiple instances, each with dedicated hardware resources such as L2 cache slices. MIG is also documented to form the foundation of NVIDIA's confidential computing stack by providing hardware-isolated trusted execution environments. However, the security claims of MIG deserve closer investigation, especially given the complexity of the GPU memory system and its many (sparsely documented) memory instructions.

In this work, we empirically examine the behavior of GPU L2 cache with MIG enabled. We find that despite the partitioning design, cross-instance L2 cache interference still occurs. Specifically, memory barriers (membars) generated in one MIG instance have side effects that propagate across L2 partitions and affect the timing of certain load operations in other instances. We also find that these membars can be triggered by specific GPU activities, such as kernel launches.

Building on these observations, we develop a new timing-based side-channel attack in which an attacker in one MIG instance can infer the kernel launch patterns of a victim in another instance. We show that this attack compromises the confidentiality of widely used GPU applications, such as large language model inference, because kernel launch patterns in these applications are correlated with sensitive information.

## 1 Introduction

The demand for GPU-accelerated computing continues to grow, driven by advances in AI, data science, and high-performance computing. As a result, GPU data centers are now a critical part of our computational infrastructure. Due to the high cost of GPUs, both in terms of acquisition and operation, providers must ensure high utilization for their GPUs. A common method for improving hardware utilization is multi-tenancy, where multiple users share the same physical resources.

However, allowing multiple users to share a GPU introduces performance and security concerns. For example, on NVIDIA GPUs, the L2 cache is shared across all the compute units. When workloads from different users execute in parallel, contention in this shared cache can degrade performance and bring opportunities for cache timing side-channel attacks (a.k.a., cache attacks).

To address these issues, NVIDIA introduced the Multi-Instance GPU (MIG) feature starting with its Ampere-generation data center GPUs (e.g., the A100). MIG enables a single GPU to be partitioned into isolated instances, each with its own dedicated compute and memory resources. In particular, the L2 cache is partitioned between instances. With the release of its next architecture, Hopper (e.g., the H100), NVIDIA introduced the second generation of MIG, intended to support its confidential computing framework. This new MIG version still partitions the L2 cache and is therefore documented to provide a trusted execution environment with cache side channels mitigated.

### Key Findings

**Triggering membars.** On GPUs, membars are used to enforce ordering of memory operations. NVIDIA GPUs provide a MEMBAR instruction; GPU programs can directly execute this instruction to trigger membars. In addition, our investigation reveals that certain program activities that invoke GPU driver operations also trigger membars. These activities fall into three categories:
1. Launching CUDA kernels
2. Calling certain CUDA memory management APIs
3. Creating or destroying CUDA contexts (i.e., processes)

**Detecting membars across MIG instances.** The above observation raises security concerns: the attacker in one MIG instance can detect membars issued by the victim in another instance simply by profiling the attacker's workload. However, the profiler typically requires privileged access and is entirely disabled in security-sensitive environments. To overcome this limitation, we investigate whether the cross-instance effects of membars can be detected through timing. Our results show that a specific annotated load instruction, `LD.STRONG.GPU`, consistently runs slower in the presence of membars. This means that, instead of relying on the profiler, the attacker could detect membars issued in a separate MIG instance by measuring the latency of `LD.STRONG.GPU`.

**Covert channels.** Based on the above findings, we develop a new timing-based covert channel, **Membar+Load**, which operates across MIG instances. The sender in one instance transmits a bit by either repeatedly issuing membars (to send a "1") or remaining idle (to send a "0"). The receiver in another instance receives the bit by timing the execution of the `LD.STRONG.GPU` instruction: longer execution time indicates a bit "1" and shorter execution time indicates a bit "0".

**Side-channel attacks.** We then show that Membar+Load can also be exploited as a side-channel attack. In practice, we find that common GPU applications, such as machine learning applications, rarely execute the MEMBAR instruction directly. However, they very frequently launch CUDA kernels. Moreover, the kernel launch patterns often reflect sensitive application information. Therefore, using Membar+Load, the attacker can detect the kernel launches in the victim workload and infer private information correlated with the kernel launch patterns.

## 2 Background

### 2.1 GPU Architecture and Programming

**GPU architecture.** GPUs are designed to handle highly parallel workloads efficiently. The basic compute units in a GPU are called streaming multiprocessors (SMs). Each SM contains an array of simple cores and can execute a group of 32 threads—known as a warp—in an SIMT (single-instruction, multiple-thread) fashion. A GPU includes many SMs that operate in parallel to support massive thread-level parallelism. For example, NVIDIA H100 contains 132 SMs.

GPUs usually use their own on-board memory to store data and program state. This memory typically uses special DRAM technologies that are designed to achieve high bandwidth, such as HBM. The latency of accessing GPU memory is very high—much higher than that of main memory. To reduce the impact of this significant latency and improve performance, modern GPUs typically use a two-level cache hierarchy.

**GPU programming & kernel execution.** In CUDA, GPU tasks are written as kernels, which are special functions launched from the CPU but executed on the GPU. To launch a kernel, the CPU program calls the kernel function using a special syntax that specifies the number of thread blocks and the number of threads per block. The CUDA runtime forwards this request to the GPU driver, which then sets up the execution of the thread blocks on the GPU.

**GPU context & GPU sharing.** A GPU context is conceptually similar to a CPU process: every CUDA program runs within a context on the GPU, and the context provides isolation between different programs. On NVIDIA GPUs, multiple contexts time-share the GPU by default. However, when advanced features such as Multi-Instance GPU are enabled, contexts can run in parallel on the GPU.

### 2.2 NVIDIA Multi-Instance GPU

Multi-Instance GPU (MIG) is a feature introduced by NVIDIA with the A100 GPUs in 2020. It is designed to improve GPU resource utilization and isolation in multi-tenant environments. MIG allows a single GPU to be partitioned into multiple independent instances, and workloads can run in parallel in different instances. Each instance has its own compute resources (SMs) and is allocated a dedicated set of memory-system resources, including on-chip crossbar ports, L2 cache slices, memory controllers, and DRAM channels.

In 2022, with the release of H100 GPUs, NVIDIA introduced the second-generation MIG. Beyond hardware partitioning, this second-generation design includes additional hardware features to support NVIDIA's confidential computing (CC) technology. NVIDIA CC ensures that each confidential virtual machine is provided with a hardware-isolated trusted execution environment (TEE). With MIG enabled, a TEE can be assigned to just a single MIG instance instead of the whole GPU, significantly improving efficiency.

### 2.3 GPU Cache Attacks

Cache attacks have been extensively studied on CPUs. Most cache attacks are based on cache evictions. For example, in Prime+Probe, the attacker first fills specific cache sets with its own cache lines. Then, the attacker detects the victim's accesses in these sets by observing evictions of the attacker's cache lines. More recently, researchers have shown that eviction-based cache attacks such as Prime+Probe are also feasible on GPUs. However, these attacks have only been demonstrated without MIG; with MIG enabled, the attacker and victim no longer share any cache sets if they are running in different instances.

## 3 Goal of Behind Bars

The goal of this work is to examine the extent of MIG's mitigation—specifically, whether cross-instance L2 cache interference can still occur under the partitioning design and lead to security concerns. This investigation is critical since MIG has become a key feature in modern GPUs:

1. MIG plays an important role in multi-tenant GPU environments, since it introduces hardware-enforced isolation that provides both performance and security benefits for GPU applications.
2. The significance of MIG is further amplified in NVIDIA CC: the second-generation MIG is specifically designed to provide hardware-isolated TEEs to support NVIDIA CC.

## 4 Characterization of MIG L2 Cache Isolation

We conduct experiments to examine the L2 partitioning design in MIG on NVIDIA GPUs. The physical L2 cache partitioning design in MIG makes cross-instance L2 cache evictions theoretically infeasible. However, other forms of cross-instance interference may still occur.

### 4.1 Cross-Instance Cache Interference

To detect cross-instance L2 cache interference, we profile the L2 cache behavior of a simple GPU program (the detector) in one MIG instance, while a workload with various GPU activities (the stressor) is running in another instance.

**Results:** We find that none of the tested user-level activities—via the LD, ST, and ATOM instructions—have any observable impact on the profiling results. However, several driver-level activities substantially affect the profiling results:

1. Launching CUDA kernels
2. Calling `cudaFree`, `cudaMemcpy`, or `cudaMemset` APIs
3. Creating or destroying CUDA contexts

Further examination reveals these additional L2 requests are **memory barrier requests** (membars). Membars are used to enforce the ordering of memory operations. They guarantee that all memory accesses issued before a membar are globally visible before any memory access issued after it.

## 5 The Membar+Load Attack

### 5.1 Timing-Based Detection

We show that `LD.STRONG.GPU` instructions consistently run slower in the presence of membars from another MIG instance. This enables timing-based detection without requiring privileged profiler access.

### 5.2 Covert Channel

We develop Membar+Load as a covert channel:
- **Sender**: Transmits a "1" by repeatedly issuing membars, or a "0" by remaining idle
- **Receiver**: Detects bits by timing `LD.STRONG.GPU` instructions

### 5.3 Side-Channel Attacks

We demonstrate two practical side-channel attacks:

**Attack 1: LLM Inference Fingerprinting**
- Different LLMs exhibit different kernel launch patterns
- The attacker can fingerprint the LLM in use
- Given a specific LLM, the prefill and decode phases have distinct patterns
- By separating these phases, the attacker can estimate input/output token counts
- This information can reveal characteristics of the inference, such as the topic of the task

**Attack 2: Graph Processing Fingerprinting**
- The kernel launch pattern of a graph processing workload varies depending on the input graph
- The attacker can fingerprint the graph being processed from a set of candidates

## 7 Discussion and Generalization

We tested our findings on multiple systems with different GPUs (A100, H100) and driver versions. The cross-instance membar interference is consistently observable across all tested configurations.

## Responsible Disclosure

We disclosed our findings to NVIDIA on June 30, 2025. NVIDIA acknowledged our report and requested a three-month embargo on July 25, and lifted the embargo on October 13. In addition, AMD MI300X GPUs feature a design called Core Partitioned X-celerator (CPX), which is similar to NVIDIA's MIG. Although we were unable to test CPX due to lack of access to AMD GPUs, we disclosed our findings to AMD as well.

## Conclusion

To the best of our knowledge, Membar+Load is the first cache attack method that works across MIG instances. This work demonstrates that despite NVIDIA's claims about cache isolation in MIG, cross-instance interference via memory barriers creates an exploitable side channel that can compromise the confidentiality of GPU applications in supposedly isolated environments.
