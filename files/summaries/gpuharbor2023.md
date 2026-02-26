# GPUHarbor: Testing GPU Memory Consistency at Large (Experience Paper)

**Authors:** R. Levine, M. Cho, D. McKee, A. Quinn, T. Sorensen  
**Venue:** ISSTA, 2023 (Distinguished Artifact Award)  
**PDF:** [gpuharbor2023.pdf](../gpuharbor2023.pdf) | **Full Markdown:** [gpuharbor2023.md](../markdown/gpuharbor2023.md)

This paper presents GPUHarbor, a widescale GPU memory consistency specification (MCS) testing tool with web and Android interfaces that enabled the largest study of weak memory behaviors to date.

## Key Contributions

- **Accessible testing**: Web interface and Android app allow crowd-sourced collection of GPU memory consistency testing data.
- **Massive scale**: Collected data from 106 devices spanning seven vendors — at least 10x larger than prior studies.
- **Bug discovery**: Conformance tests identified two new bugs on embedded Arm and NVIDIA devices.
- **Behavioral insights**: AMD GPUs show 25.3x more weak behaviors on average than Intel; devices can be clustered according to stress testing sensitivity.

## Summary

Memory consistency specifications are critical but testing tools have historically been inaccessible, limiting studies to few platforms. GPUHarbor democratized MCS testing through web and mobile interfaces, enabling crowd-sourced data collection. The resulting dataset provides unprecedented insight into how different GPU vendors and architectures handle memory ordering, revealing significant behavioral differences across the ecosystem.
