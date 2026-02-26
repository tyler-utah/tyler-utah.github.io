# Portable Inter-workgroup Barrier Synchronisation for GPUs

**Authors:** T. Sorensen, A. F. Donaldson, M. Batty, G. Gopalakrishnan, Z. Rakamaric  
**Venue:** OOPSLA, 2016  
**PDF:** [oopsla2016.pdf](../oopsla2016.pdf) | **Full Markdown:** [oopsla2016.md](../markdown/oopsla2016.md)

This paper presents the first portable and formally-specified inter-workgroup barrier for GPUs, addressing the deadlock risk from occupancy-bound execution.

## Key Contributions

- **Occupancy discovery protocol**: Dynamically discovers a safe occupancy estimate for a given GPU and kernel, enabling starvation-free (and deadlock-free) barriers.
- **Formal verification**: Barrier proven to meet its synchronization specification using OpenCL 2.0 atomic operations.
- **Portability**: Evaluated across 8 GPUs from 4 vendors; discovery protocol achieves nearly 100% recall.

## Summary

Inter-workgroup barriers are essential for many GPU applications but not supported by GPU programming models because occupancy-bound execution can cause deadlock. This paper solves the problem by dynamically discovering how many workgroups can safely execute concurrently, then restricting the barrier accordingly. The approach is formally verified, portable across vendors, and evaluated on practical applications.
