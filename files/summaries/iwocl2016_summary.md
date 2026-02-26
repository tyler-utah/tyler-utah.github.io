# The Hitchhiker's Guide to Cross-Platform OpenCL Application Development

**Authors:** T. Sorensen, A. F. Donaldson  
**Venue:** IWOCL, 2016  
**PDF:** [iwocl2016.pdf](../iwocl2016.pdf) | **Full Markdown:** [iwocl2016_full.md](iwocl2016_full.md)

This experience report examines portability issues encountered when running OpenCL benchmarks across multiple GPU platforms from different vendors.

## Key Contributions

- **Portability audit**: Two sets of open-source benchmarks tested across a variety of GPU platforms; issues classified into framework bugs, specification limitations, and programming bugs.
- **Community analysis**: 58% of recent GPU papers evaluate GPUs from a single vendor only.
- **Practical guidance**: Lessons learned and recommendations for improving cross-platform OpenCL development.

## Summary

While OpenCL promises cross-platform portability, in practice many applications fail on platforms from different vendors. This paper systematically documents the portability issues encountered and provides practical insights for developers seeking genuinely portable GPU code.
