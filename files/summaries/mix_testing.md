# Mix Testing: Specifying and Testing ABI Compatibility of C/C++ Atomics Implementations

**Authors:** L. Geeson, J. Brotherston, W. Dijkstra, A. F. Donaldson, L. Smith, T. Sorensen, J. Wickerson  
**Venue:** OOPSLA, 2024  
**PDF:** [mix_testing.pdf](../mix_testing.pdf) | **Full Markdown:** [mix_testing.md](../markdown/mix_testing.md)

This paper presents mix testing, a technique for finding compiler bugs that arise when concurrently compiled binaries from different compilers (or compiler versions) are composed together.

## Key Contributions

- **Mixing bugs**: Defines a new class of bugs that arise when parts of a concurrent program are compiled using different atomics mappings from C/C++ to assembly — a scenario that occurs in real industry applications (e.g., Windows on Arm mixing MSVC and LLVM code).
- **atomic-mixer tool**: Implements mix testing and was used to find four previously unknown mixing bugs in LLVM and GCC, and one prospective bug in proposed JVM mappings.
- **First atomics ABI for Armv8**: Worked with Arm engineers to specify, for the first time, a concurrency ABI for the Arm architecture, and validated LLVM and GCC compilers against it.

## Summary

While ABIs ensure binary compatibility, there are no official ABIs for concurrent programs. Different compilers may use different (individually correct) mappings from C/C++ atomics to assembly, but composing these binaries can introduce subtle bugs. Mix testing systematically finds these composition bugs, addressing a real-world problem that kernel and application developers face today.
