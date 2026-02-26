# Memory DisOrder: Memory Re-orderings as a Timerless Side-channel

**Authors:** S. Siddens, S. Srivastava, R. Levine, J. Dykstra, T. Sorensen  
**Venue:** ArXiv, 2026  
**PDF:** [disorder.pdf](../disorder.pdf)

---

MEMORY DISORDER: Memory Re-orderings as a Timerless Side-channel
Sean Siddens†
Sanya Srivastava
Reese Levine
University of Washington
Duke University
UC Santa Cruz
Josiah Dykstra†
Tyler Sorensen†
Raytheon BBN Technologies
Microsoft Research
UC Santa Cruz
Abstract
To improve efficiency, nearly all parallel processing units
(CPUs and GPUs) implement relaxed memory models in
which memory operations may be re-ordered, i.e., executed
out-of-order. Prior testing work in this area found that memory
re-orderings are observed more frequently when other cores
are active, e.g., stressing the memory system, which likely
triggers aggressive hardware optimizations.
In this work, we present MEMORY DISORDER: a timerless
side-channel that uses memory re-orderings to infer activ-
ity on other processes. We first perform a fuzzing campaign
and show that many mainstream processors (X86/Arm/Apple
CPUs, NVIDIA/AMD/Apple GPUs) are susceptible to cross-
process signals. We then show how the vulnerability can be
used to implement classic attacks, including a covert chan-
nel, achieving up to 16 bits/second with 95% accuracy on
an Apple M3 GPU, and application fingerprinting, achiev-
ing reliable closed-world DNN architecture fingerprinting on
several CPUs and an Apple M3 GPU. Finally, we explore
how low-level system details can be exploited to increase
re-orderings, showing the potential for a covert channel to
achieve nearly 30K bits/second on X86 CPUs. More precise
attacks can likely be developed as the vulnerability becomes
better understood.
1
Introduction
Modern shared memory parallel processors implement com-
plex pipelines and memory systems. This complexity in-
creases efficiency but has also led to security issues, especially
in multiprocessing systems, where sensitive information from
one process can be obtained by another (potentially malicious)
process. Side-channel attacks are especially nefarious, as the
attacker can utilize low-level device details to detect subtle
properties of an unassuming victim process.
There are many types of side-channels, utilizing many dif-
ferent system components. Some side-channels require physi-
†Work performed while at Trail of Bits.
cal access [49], while others require access to low-level APIs,
e.g., to monitor energy [14]. The attack requirements are
referred to as the capability of the attack. A low capability at-
tack has few requirements and, thus, can be deployed in more
situations. For example, classic cache-based side-channels
require precise timers [26]. However, the capability of the
attack can be lowered by removing the timers and instead
using other (seemingly innocent) mechanisms [38].
MEMORY DISORDER
In this work, we present MEMORY
DISORDER (or simply DISORDER): a low-capability side-
channel for parallel processors. DISORDER utilizes memory
re-orderings that arise due to hardware relaxed memory consis-
tency models (or MCMs) [32]. That is, to increase efficiency,
mainstream consumer parallel processors allow memory op-
erations to execute out-of-order, as specified by their MCM.
These behaviors occur both on CPUs [4,39] and GPUs [22].
Memory re-orderings can be observed in small parallel pro-
grams, often called litmus tests, which typically execute with
two threads with two memory operations each. By inspecting
certain variable and memory values after the test execution, it
can be determined if a re-ordering occurred.
Prior works have run these litmus tests across many dif-
ferent processors to test conformance to an MCM specifica-
tion. When testing GPUs, it was found that the number of
observed re-orderings could be amplified by utilizing addi-
tional threads that added stress to the system [3]. Inspired by
these results, this paper explores the potential of memory re-
orderings as a side-channel, where one (potentially malicious)
process repeatedly executes a litmus test, requiring only the
ability to launch threads and execute memory loads and stores.
Other (victim) processes may create identifiable patterns of
system pressure when executing certain programs, causing
re-orderings to be observed by another process.
1
arXiv:2601.08770v1  [cs.CR]  13 Jan 2026


Initially: *x == 0 && *y == 0
thread 0
thread 1
a
Write(x, 1)
c
v0 = Read(y)
b
Write(y, 1)
d
v1 = Read(x)
re-order check: v0 == 1 && v1 == 0
Figure 1: The Message Passing (MP) litmus test. Thread
0 writes to x and then y. Thread 1 reads the values in the
opposite order. If thread 1 observes the updated value for y
before the updated value for x, then a re-ordering occurred.
0
10
20
30
40
50
60
Memory Re-orderings
0%
1%
2%
3%
4%
5%
6%
7%
8%
Frequency
resnet50
googlenet
vgg16
mobilenetv3
alexnet
Figure 2: Histogram of re-ordering observations by an at-
tacker when a victim is running inference from common
DNN architectures on an Apple M3 GPU.
1.1
Example: DNN Architecture Fingerprint-
ing
We illustrate the potential of DISORDER using an example in
which there are two processes: a victim and an attacker. The
victim process repeatedly runs DNN inference on an Apple
M3 GPU, which is known to have a relaxed MCM [19]. The
attacker repeatedly executes a classic litmus test, known as
Message Passing (or MP), shown in Fig. 1. In order to satisfy
the re-order check for this test, either the writes on thread 0
or the reads on thread 1 must be re-ordered. Because these
tests are short, the attacker can execute many iterations while
the victim is executing DNN inference.
Figure 2 shows a histogram of the frequency of ob-
served memory re-orderings by the attacker when the vic-
tim is running 5 different (common) DNN architectures:
resnet50, googlenet, vgg16, mobilenetv3_small (reported as
mobilenetv3 in the figure), and alexnet. We see that each DNN
produces a unique signature, i.e., an approximate normal dis-
tribution of observed re-orderings. We then split these obser-
vations into a training and testing set (discussed in Sec. 5.2)
and show that an attacker can automatically classify which
DNN architecture a victim is running.
1.2
MEMORY DISORDER Overview
This paper provides a detailed investigation into the potential
of memory re-orderings as a side-channel. While there are
many low capability side-channels, e.g., see [51], we believe
MEMORY DISORDER has a range of unique properties:
1. Low capability: DISORDER only requires two threads
and shared memory; it does not require timers, perfor-
mance counters, or physical access.
2. Wide reach: Mainstream processors (CPUs and GPUs)
implement relaxed MCMs, which are accessible through
common programming languages, e.g., C++ [11].
3. Empirically based: Many side-channels target low-level
hardware components through meticulous reverse en-
gineering [2, 33, 51]. DISORDER attacks can be con-
structed using simple empirical fuzzing techniques.
4. Unknown potential and mitigations: The exact hardware
component(s) that cause a memory re-ordering are not
documented or well-understood. As such, it is difficult to
develop rigorous mitigations, and more targeted attacks
can likely be developed through detailed explorations.
This work focuses on the feasibility and breadth of DISOR-
DER: we show that six different architectures are impacted,
spanning both CPUs as well as GPUs; furthermore, we show
that this vulnerability crosses virtualization boundaries (KVM
on Linux). While it is not feasible to reverse engineer the com-
plex hardware interactions that cause memory re-orderings
across all these devices, we provide an initial investigation
into how more targeted approaches can improve re-ordering
observations (i.e., signals) by several orders of magnitude on
X86 CPUs (Sec. 5.3). In other cases, we provide hypothe-
ses and reference documentation when available and leave
more detailed explorations to future work. Thus, DISOR-
DER attacks can be developed with either (1) low precision
using only simple empirical data, or (2) higher-precision, con-
structed by thorough reverse engineering.
We found only one prior security work proposing re-
ordering side-channels [12]. However, they only run small
simple experiments on X86 CPUs and do not discuss how
to search for signals systematically across different architec-
tures. Additionally, DISORDER attacks require two threads
and shared memory; it has been shown that these ingredi-
ents are often sufficient to construct a high-resolution timer
(e.g., see [38]), and thus, re-enable classic cache-based side-
channels. However, given that the exact reasons for memory
re-orderings are still largely unexplored, we believe there is
novel potential in DISORDER and it should not be considered
only a proxy for cache-based side-channels.
Fuzzing for DISORDER
We begin by designing a fuzz test-
ing campaign to determine if it is possible to observe a signal
2


Table 1: The devices and configurations used in our study. We observe DISORDER on all of our devices. We construct additional
attacks for Arm, X86, M1-CPU and M3-GPU (highlighted in green).
Type
Vendor
Name
Short Name
Cores or CUs
Configurations
CPU
Apple
M1
M1-CPU
8
MacOS different processes
CPU
Arm
A78 (Nvidia Jetson Orin Nano)
Arm
6
Linux different processes, KVM
CPU
Intel
i7-12700K
X86
12
Linux different processes, KVM
GPU
Apple
M3
M3-GPU
10
MacOS different processes
GPU
NVIDIA
GeForce RTX 4070
NVIDIA
46
Linux different processes
GPU
AMD
Radeon RX 7900 XT
AMD
84
Linux different processes
across processes using memory re-orderings (Sec. 3). The
fuzz testing contains two parameterized processes: the Stres-
sor and the Listener. The Listener runs memory re-ordering
litmus tests, while the Stressor applies system stress. We
record the number of re-ordering observations both with and
without the Stressor executing and check if there is a differ-
ence. If so, it is possible for the Listener to determine if it is
running concurrently with the Stressor.
We explore six devices: three CPUs, and three GPUs, listed
in Tab. 1. Although the strength varies, we were able to ob-
serve signals across these devices and configurations. We say
that devices for which we can observe a signal are vulnerable
to DISORDER.
DISORDER Attacks
We then select a subset of our devices
(highlighted with green in Tab. 1) and utilize data from our
fuzzing campaign to implement two classic attacks: covert
channels (Sec. 5.1) and application fingerprinting (Sec. 5.2).
For the Arm and X86 devices, we carry out these attacks
across KVM virtualization boundaries.
To implement a covert channel, we identify test and stress
combinations that can provide a high and low signal, and
use that to implement a covert channel that can communi-
cate reliably at up to 16 bits/second (on an Apple M3 GPU).
To implement application fingerprinting, we run a selected
listener alongside the victim application. The collected data
is split into a training and test set to simulate an attack. We
show that a listener (attacker) needs roughly only 5 seconds
to successfully classify which candidate DNN architecture
is running with up to 100% accuracy on an Intel X86 CPU.
We also show that other application activity, e.g., launching
Google Chrome, provides significant DISORDER signals.
Section 5.3 concludes with an exploration on how low-
level system details can be exploited to increase re-orderings,
and thus, increase attack precision. We show that on X86
CPUs exercising certain L1 cache sets dramatically increases
the number of re-orderings, with the potential to increase the
covert channel rate to nearly 30k bits/second. This exploration
can serve as the foundation for constructing more precise
DISORDER attacks.
Contributions
In summary, our contributions are:
• MEMORY DISORDER: A novel low capability side-
channel attack that utilizes memory re-orderings.
• A fuzz testing campaign that shows many mainstream
CPUs and GPUs are vulnerable to DISORDER (Sec. 3).
• Illustrating how to construct DISORDER covert channels
(Sec. 5.1) and application fingerprinting (Sec. 5.2).
• An exploration of how low-level system details can be
exploited to dramatically increase re-orderings used in
DISORDER (Sec. 5.3).
Mitigations and remediations are discussed in Sec. 6 and
responsible disclosure is discussed in Sec. 9.
2
Background
Because we target both CPUs and GPUs, we give a brief
background on their multiprocessing capabilities and define
common terminologies. Next, we provide an overview of
memory consistency models and the re-orderings they allow.
2.1
Parallel Architectures and Multiprocessing
Nearly all mainstream computing devices (laptops, phones,
servers) contain parallel processing units (e.g., CPUs, GPUs)
that allow hardware resources to execute tasks simultaneously.
These processors typically allow multiprocessing, where tasks
from different processes can execute concurrently. Processes
provide a clear security boundary—each process should be
isolated from all other processes. Virtualization provides an
additional security boundary in that malicious processes are
not able to utilize operating system (OS) vulnerabilities.
CPUs
CPUs are the processing center of a system. They
execute most of the low-level system logic (e.g., the OS), and
are the main computational component for many interactive
applications, such as web browsers. CPUs are latency opti-
mized, where a small number of complex cores optimize a
single stream of instructions (commonly called a thread). Dif-
ferent threads are often mapped to different cores. In some
3


systems, such as Linux, software threads can be pinned to
cores using a low-level API. Mainstream CPU operating sys-
tems (Linux, MacOS) provide parallel multiprocessing where
different processes can execute in parallel on different cores.
GPUs
GPUs are highly parallel programmable accelera-
tors. Their parallelism is organized hierarchically, where the
base unit is a processing element which computes a stream of
computation (again, called a thread). Processing elements are
organized into compute units (CUs)1. As opposed to CPUs,
GPUs are throughput oriented, computing many tasks in par-
allel using simpler hardware components per task.
A GPU program is called a kernel; it is launched from a host
(CPU) program that specifies the hierarchical configuration of
threads, namely the total number of threads and a partition of
the threads into workgroups, which are guaranteed to execute
on the same CU. While GPUs have a complex execution
model, e.g., where some threads are executed synchronously,
these details are not required for DISORDER.
GPU multiprocessing capabilities and properties vary
across systems and configurations. Classically, GPUs do not
execute kernels from different processes in parallel; instead,
they execute different kernels sequentially [41]. However, it is
becoming more common for GPUs to support parallel kernel
execution, where different kernels are executed on different
compute units e.g., through configurations like NVIDIA’s
MPS [35] and MIG [34]. In Sec. 4.2 we empirically show that
Apple GPUs also provide parallel kernel execution.
CPU/GPU Commonalities
Both CPUs and GPUs provide
a general programming interface that allows many threads to
be launched and access memory without elevated privileges.
These memory accesses reliably get translated to hardware
memory accesses, i.e., without compiler optimizations, using
atomic libraries. Furthermore, both CPUs and GPUs con-
tain complex memory hierarchies, which contain at least two
levels of caches and a main memory. This common design
is likely somewhat responsible for observable memory re-
orderings on both devices.
2.2
Memory Consistency Models
A memory consistency model (MCM) defines the values
that load instructions are allowed to return in a shared mem-
ory parallel program. There are both language models (e.g.,
for C++ [11]) and hardware models (e.g., for X86 [37] and
Arm [13]). These models can be complex and have been de-
veloped and refined over many years. However, this work
does not require the full complexity of state-of-the-art MCMs.
Our initial exploration of DISORDER only requires a simple
foundation for empirical testing, which we describe below.
1Called streaming multiprocessors (SMs) in NVIDIA documentation;
however, we use the more portable Khronos terminology in this work
Table 2: Generalizing the MP test of Fig. 1 creates five addi-
tional classic litmus tests.
Test Name
a
b
c
d
re-order check
Message Passing (MP)
W
W
R
R
v0=1 & v1=0
Store Buffering (SB)
W
R
W
R
v0=0 & v1=0
Load Buffering (LB)
R
W
R
W
v0=1 & v1=1
2+2W
W
W
W
W
*x=1 & *y=2
Store (S)
W
W
R
W
*x=2 & v0=1
Read (R)
W
W
W
R
*y=2 & v0=0
Instruction Re-ordering MCMs
This work considers
MCMs that can be completely defined in terms of thread-
local re-orderings, a subset of the models described in [10],
which we will call IR (Instruction Re-ordering) models. For
example, an IR model might allow a Write-Read (or WR) re-
ordering. That is, if a program contains a write (W) followed
by a read (R), then they are allowed to be re-ordered. Given
that we only consider two memory instructions, write (W)
and read (R), there are only four possible pairs that are can be
re-ordered (RR, RW, WR, WW). An IR model can be defined
by enumerating which of these re-orderings are allowed.
IR models typically do not allow re-ordering of accesses
that target the same location, as this could break single-
threaded sequential execution. That is, an IR model that allows
RW re-orderings will only allow the re-ordering if the two ac-
cesses target different locations. When we discuss each of our
test processors (Sec. 3), we will discuss which IR MCM most
closely approximates the allowed behaviors for that processor.
IR Litmus Tests
The simplicity of IR models allows them
to be thoroughly tested using simple litmus tests. We can
generalize the MP test of Fig. 1 where each instruction ( a ,
b ,
c ,
d ) can be instantiated with an R or a W. There are always
two memory locations, x and y. Memory operations
a and
d target x and memory operations
b and
c target y. Write
operations store unique values (starting at 1 and incrementing
with each write), and read operations store to unique variables
(starting at v0 and incrementing with each load). Each test can
check for up to two re-orderings, one per thread. For example,
the MP test of Fig. 1 tests for both a WW re-ordering (thread
0) and RR re-ordering (thread 1).
Following this formula, we can construct 6 litmus tests,
where a post condition can be used to check for IR re-
orderings. These tests correspond to classic litmus tests used
throughout MCM literature, with admittedly cryptic names.
We describe these tests in Tab. 2, and they can be viewed
more concretely in prior works, e.g., [21]. Re-orderings are
not unique for each test, e.g., both SB and R test for the WR
re-ordering.
4


Table 3: The different testing frameworks (shaded in green),
and stresses (shaded in blue), the device they target (CPU or
GPU), and the number of fuzzed parameters.
Name
Device
Fuzzed Parameters
Basic
CPU
2
Litmus7 [6]
CPU
0
Perpetual [30]
CPU
2
GPU Parallel [23]
GPU
4
Memory [21]
CPU, GPU
6
Thread Launch
CPU
2
3
Fuzz Testing for DISORDER Vulnerabilities
We now detail a fuzz testing methodology that can check if de-
vices are vulnerable to DISORDER. The methodology consists
of two processes: the Listener, and the Stressor. The Listener
can be instantiated using one of four different memory or-
dering testing techniques and the Stressor can be instantiated
with one of two system stress techniques. For each technique
(testing and stressing), we summarize the approach and list
the fuzzed parameters, summarized in Tab. 3.
3.1
The Listener
The Listener process runs litmus tests for many iterations
(typically over 100K) and records the number of re-orderings.
Although litmus tests are simple, running the tests can be
complex, utilizing heuristics to increase throughput and re-
orderings. A testing framework takes a litmus test and some
tunable parameters. We use three frameworks from prior
works and provide one new framework.
Basic Testing Framework
We provide the basic testing
framework new to this work. While it is simple, it provides
some of the most reliable signals when combined with the
right stress (see the M1-CPU results in Sec. 4.1). This frame-
work implements the litmus test using C++ threads and re-
laxed atomic memory accesses, which allows all IR memory
re-orderings. For each test iteration, the threads are launched,
then joined, then the re-ordering condition is checked.
This framework contains two fuzzing parameters: the in-
dices of the two memory locations, i.e., x and y. Fuzzing the
indices allows them to be located across (or within) different
memory regions, such as cache lines or memory pages, which
could encourage different types of re-orderings to appear. We
only implement this framework for CPU systems, as GPUs
do not widely support C++ concurrency constructs.
Litmus7 Framework
The Litmus7 tool [6] implements
several heuristics on top of the basic framework. For example:
memory operations are implemented using inline assembly
and threads are not relaunched each iteration, instead using
inter-thread synchronization to perform the re-order check
and align the next iteration. Furthermore, Litmus7 performs
its own fuzzing, randomly assigning memory locations and
permuting how software threads map to test threads. Given
this, we run this framework with its default settings and do
not fuzz any of our own parameters. Because Litmus7 only
targets CPUs (previous GPU versions [3] are not publicly
available), we only test CPU systems with this framework.
Perpetual Framework
Perpetual testing was used in early
MCM testing [48], and has seen a recent resurgence [30,42].
This approach increases throughput by eliminating synchro-
nization by launching testing threads only once. Write oper-
ations store algebraic sequences, while the read operations
maintain a log of observed values. The log is analyzed at the
end of the run; traces that satisfy certain algebraic constraints
indicate that a memory re-ordering occurred. This approach
is attractive for DISORDER as it provides fine-grained obser-
vations, potentially enabling more precise attacks.
In order to enable wider testing, we re-implement the X86-
exclusive approach of [30] using C++ atomic operations and
threads. The fuzzed parameters for this approach are the same
as for the basic framework, i.e., two memory indices. Ad-
ditionally, without significant modifications, this approach
requires two read operations in the test; thus, we limit the
litmus tests for this testing framework to MP, SB, and LB. In
Sec. 4, we find that unfortunately, this framework does not
yield any re-ordering observations on Arm or X86 CPUs. It
may be the case that our implementation needs to be more
finely tuned, as prior work [30] was able to observe X86 re-
orderings. Because this framework works best executing a
small number of threads rapidly, it is more suited for CPUs,
and, thus, we do not provide a GPU implementation.
GPU Parallel Testing Framework
This framework [23]
utilizes GPU parallelism to enable high testing throughput.
Given N GPU threads, this framework instantiates N litmus
test to execute in parallel. Each thread executes two instances
of a test: acting first as thread 0, and next as thread 1. This
approach is implemented in WebGPU [45], making it portable
across many GPUs. There are four fuzzed parameters in
this framework: the number of workgroups, workgroup size,
padding between memory locations, and how frequently to
synchronize test threads. Litmus test threads are also ran-
domly mapped to GPU threads each iteration.
3.2
The Stressor
The Stressor executes a stress: a program designed to stress
the system and increase memory re-orderings observed by the
Listener. In this work, we explore two stress techniques that
we found increased memory re-orderings. One technique is
5


inspired by prior work, while the other is new to this work.
These stress processes execute indefinitely, until killed.
Memory Stress
As the name suggests, this stress targets the
memory system and closely follows prior work in GPU MCM
conformance testing [21]. This stress allocates a memory
buffer and partitions it into stress lines (conceptually similar
to cache lines). It then launches threads and maps them to an
initial stress line. The threads repeatedly access a stress line
with a pattern of loads and stores. After some iterations, the
threads move to another stress line.
We provide C++ and WebGPU implementations of memory
stress, applying memory stress to CPU memory model testing
for the first time. This technique has 6 fuzzed parameters: the
stress line size, a thread offset into the stress line, how many
iterations to target a given stress line, the stride used to update
the memory location, the memory access pattern (a sequence
of loads and stores), and the number of stressing threads.
Thread Launch Stress
This stress was discovered serendip-
itously as we were running early experiments. We found that
opening a new terminal while a test was running significantly
increased the number of re-orderings. We distilled this behav-
ior into a stress that repeatedly launches and joins threads.
We implement this stress in C++. Threads execute a loop
containing relaxed atomic memory accesses so that the com-
piler doesn’t optimize away the loop. The two fuzzed param-
eters for this stress are the number of threads and the thread
loop iterations, which controls the rate at which the threads
are re-launched. Given that GPUs don’t have a similar mech-
anism to launch threads, instead requiring a whole kernel to
be launched, we only provide this stress for the CPU.
3.3
Checking for MEMORY DISORDER
To check for DISORDER, the Listener is instantiated with a
testing framework and its inputs, i.e., a litmus test and any
required parameters. It then executes the litmus test for a
given number of litmus test iterations. This is called a test run.
After a test run, the Listener reports on how many re-orderings
were observed, i.e., the re-ordering frequency. The Stressor is
instantiated with a stress along with any required parameters.
We say that the Stressor is able to signal the Listener if the re-
ordering frequency observed in the Listener is reliably higher
when the Stressor is executing. If a signal is observed, then
we say that the system is vulnerable to DISORDER.
To check for a reliable signal, the Listener performs X test
runs in isolation, creating a set B (baseline) with X samples
of re-ordering frequencies. Then, the Stressor begins, running
indefinitely until killed. The Listener performs X test runs
again, executing simultaneously with the Stressor, creating
another set S (stressed) of samples. These sets are then com-
pared with a statistical method (Mann-Whitney U test [29]) to
determine if values in one set are larger than another. We also
compute the Common Language Effect Size (CLES), which
is the probability that a randomly selected element from S is
larger than a randomly selected element from B. If the CLES
is 100%, i.e., all elements in S are larger than B, then we say
that the signal is reliable. Furthermore, for each test in which
a signal is observed, we record the average percent increase in
observed memory re-orderings. Each of these statistical tests,
i.e., consisting of X test runs, both with and without stress, is
called a trial.
Fuzzing
To fuzz for DISORDER, a simple script can be run
that iterates through each stress s, each testing framework f
(Tab. 3), and each applicable litmus test t (Tab. 2). The script
instantiates the Listener with f, and uses t as the input test.
The Stressor is instantiated with s. The fuzzer then randomly
selects the additional parameters and performs a trial. The
fuzzer executes many signal tests and records their outcomes.
4
Fuzzing Results
We now detail the results of running the fuzz testing campaign
across the devices in Tab. 1, all of which we are able to see sta-
tistically significant (and reliable) signals. Thus, DISORDER
vulnerabilities exist widely on mainstream CPUs and GPUs.
We select 10 as the number of test runs to create the sample
sets (B and S) that are compared in the trial. We configure
the fuzzing campaign for each device such that it finishes
executing roughly in 8 hours (overnight); this includes setting
parameters like litmus test iterations and the number of trials.
We summarize our findings across all processors and con-
figurations in Tab. 4. For each configuration, we report on the
percent of trials that showed a signal, both any signal, i.e.,
there was a statistical difference in the observation sets, and a
reliable signal, i.e., the CLES was 100%. Note that the reliable
percent will be less than (or equal to) the any signal percent.
We summarize the percent increase in re-orderings observed,
both the average and the max. We then show the average
CLES across all the signals to understand how frequently
increases in re-orderings were observed. Finally, we show
how many trials were run. The number of trials are different
across devices and configuration given the different speed of
the processors and throughput of the testing framework.
On Arm and X86 CPUs running Linux, we are able to
explicitly set thread affinities, i.e., map program threads to
hardware cores. For these devices, we consider two configura-
tions related to the attacker capability: one where the affinities
can be explicitly mapped (called explicit pinning) and one
where affinities are managed by the OS. Explicit pinning is
strictly a higher capability than OS-managed, as it requires
an attacker to be able to explicitly map the Listener and Stres-
sor to specific device cores. To find an affinity mapping, we
ran several pilot experiments across a range of mappings and
selected the one that had the highest average CLES.
6


Given that each device contains its own quirks and consid-
erations, we discuss them separately below.
4.1
CPU results
Arm
The Arm processor we test has 6 cores and runs
Ubuntu 22.04. Arm devices have a famously relaxed memory
model [13], but the specification tends to be more permissive
than what is implemented in practice. The LB test is not ob-
servable on any Arm system, thus we omit it from the fuzzing
campaign for this processor. For the explicit affinity mapping,
we fixed the test threads to only run on cores 0 and 5, while
the stress threads were fixed to cores 1 through 4.
Thread launch stress coupled with the basic testing frame-
work provides the most reliable signals for this device. Reli-
able signals can be obtained roughly 12% or 64% of the time,
depending on whether the affinity is explicitly set, highlight-
ing the increased benefit of this capability. In both cases, the
maximum increase in re-orderings observed is in the order of
1K percent, providing easily distinguishable signals. Memory
stress provides signals less frequently, at most in 25% of tests
and reliable signals at most in 7% using the litmus7 testing
framework without explicit pinning; however, the maximum
increase in re-orderings is similar to thread launch stress. De-
spite the potential for increased precision of perpetual tests,
we were unable to observe any signals using this method.
X86
Our X86 processor is running on Ubuntu 22.04 and is
documented to have 12 cores, with 8 being hyper-threaded
(×2) performance cores and 4 being efficiency cores. X86
systems provide a stronger memory model than Arm [39],
only allowing WR re-orderings. Thus, we use SB and R in
this fuzzing campaign for this device. Similar to Arm, we test
with and without explicit pinning on this device. To determine
a good pinning, we ran pilot experiments across a range of
affinity mappings and found that the highest average CLES
occurred when both the test threads are pinned to performance
cores 0 and 1. Given that the performance cores are hyper-
threaded, these two cores (0 and 1) are hardware threads that
execute on the same core.
Unlike Arm, X86 provides documentation about the hard-
ware mechanisms that cause memory re-orderings. Each pro-
cessor contains a store buffer, which buffers writes before they
are flushed to the memory subsystem. Because store buffers
are processor-local, our initial hypothesis was that they would
not be susceptible to cross-process stress. However, our re-
sults, summarized in Tab. 4, show otherwise. When cores
are explicitly pinned, we can observe signals up to 100% of
the time, with 71% being reliable using the litmus7 testing
framework and thread launch stress. In fact, this test and stress
combination remains very effective even without explicit pin-
ning. However, memory stress is also able to provide many
signals with the basic framework but is more sensitive to ex-
plicit pinning (82% vs. 3%). Similarly to Arm, the perpetual
testing framework did not provide any signals for this device.
While store buffers are processor local, these results show
they are susceptible to cross-process memory traffic, which
seems to influence when a flush is triggered, e.g., to avoid
overloading the memory system. Our extra investigation into
X86 (Sec. 5.3) further explores this. These results illustrate
just how complicated low-level components are, and, thus,
how potentially subtle DISORDER attacks might be.
M1-CPU
The Apple M1-CPU has a total of 8 cores consist-
ing of 4 performance cores and 4 efficiency cores. Although
documentation for this processor is sparse, it implements the
Arm ISA, and thus allows similar re-orderings. A pilot study
revealed that we can observe all IR re-orderings on this device,
except for LB (just like Arm). Because of this, we similarly
omit LB from the fuzzing campaign for this device. Unlike
Linux, MacOS does not support thread affinity mappings, and,
thus, cannot run experiments with explicit pinning.
Reviewing the results for this device in Tab. 4, there are
several trends similar to Arm: for example, the most reliable
signals come from thread launch stress, particularly when
combined with litmus7. However, the largest percent increase
occurs with thread launch stress and the basic testing frame-
work, achieving the highest across our CPU experiments, with
a max of 770K percent increase. Similar to the other CPUs,
memory stress also provides relatively common signals and
high increase (more so using Litmus7 than the basic frame-
work). Unlike Arm and X86, perpetual tests show some sig-
nals on this processor. However, their reliability and percent
increases are low compared to other methods.
4.2
GPU Results
All GPUs we tested are documented to provide very relaxed
memory models [22]. We were able to observe memory re-
orderings on all tests in Tab. 2 on the GPUs in our study. The
percent increase in re-ordering observations on GPUs is very
high; in fact, memory re-orderings are often not observed at all
without some kind of stress (see [3]). To avoid infinite percent
increases when the baseline is zero, we treat the baseline
count as 1.
AMD Radeon RX 7900 XT
Our AMD GPU provides the
sequential kernel execution model (recall from Sec. 2.1). De-
spite the Listener and Stressor not executing in parallel on
the GPU, prior works have shown that memory effects across
GPU kernels can still be observed, e.g., in prime-and-probe
style attacks [15]. Our results, shown near the bottom of Tab. 4,
reveal that DISORDER can also be observed in this execu-
tion model. Signals on this device are rare, however, there
are some reliable signals (less than 6% of the time), and the
maximum percent increase is 170K.
7


Table 4: Results of the fuzz testing campaign across our devices.
Signal %
Increase %
Device
Pinning?
Testing F.
Stress
Any
Reliable
Avg.
Max
CLES (Avg.)
Trials
Arm
memory
10.93
0.94
519
1703
0.86
320
basic
thread launch
59.06
11.87
432
2700
0.92
320
memory
24.69
7.19
132
411
0.92
320
litmus7
thread launch
36.87
0.94
77
205
0.88
320
memory
0.00
0.00
0
0
0.00
256
no
perpetual
thread launch
0.00
0.00
0
0
0.00
256
memory
17.92
4.16
424
2590
0.93
240
basic
thread launch
85.00
64.16
296
1097
0.97
240
memory
0.83
0.41
27
38
0.90
240
litmus7
thread launch
22.92
0.42
33
106
0.86
240
memory
0.00
0.00
0
0
0.00
128
yes
perpetual
thread launch
0.00
0.00
0
0
0.00
128
X86
memory
3.12
0.00
109
170
0.84
128
basic
thread launch
0.00
0.00
0
0
0.00
128
memory
10.54
1.17
89
365
0.89
256
litmus7
thread launch
99.61
52.73
72
136
0.97
256
memory
0.00
0.00
0
0
0.00
128
no
perpetual
thread launch
0.00
0.00
0
0
0.00
128
memory
82.03
1.56
123
274
0.88
128
basic
thread launch
39.84
0.00
61
107
0.83
128
memory
2.34
0.00
21
25
0.83
256
litmus7
thread launch
100.00
71.28
50
72
0.99
256
memory
0.00
0.00
0
0
0.00
128
yes
perpetual
thread launch
0.00
0.00
0
0
0.00
128
M1-CPU
memory
41.56
20.93
1910
85814
0.95
320
basic
thread launch
83.43
67.81
8429
770700
0.98
320
memory
68.75
38.44
14725
208033
0.94
320
litmus7
thread launch
95.31
77.50
5354
120350
0.99
320
memory
5.07
1.17
101
326
0.87
256
no
perpetual
thread launch
19.53
4.69
40
125
0.88
256
GPUs
AMD
no
GPU Parallel
memory
13.8
5.9
7890
170300
0.89
708
NVIDIA
no
GPU Parallel
memory
5.6
2.8
27768
499600
0.88
726
M3-GPU
no
GPU Parallel
memory
52.4
20.5
92470
4921300
0.92
696
8


NVIDIA GeForce RTX 4070
Similar to the AMD,
NVIDIA GPUs provide the sequential kernel execution model
by default. Our results show that this device is also impacted
by DISORDER, however frequency and reliability of signals
are less than AMD (while the percent increase in re-ordering
observations ends up being higher than AMD).
NVIDIA
additionally
offers
Multi-Process
Service
(MPS) [35], which was developed for when kernels do not
contain enough parallelism to utilize the entire GPU. MPS
allows multiple kernels to execute on the GPU in parallel, but
the documentation warns that this mode will reduce security.
We were able to run some pilot experiments using this config-
uration and observed much higher DISORDER metrics, pro-
viding evidence that parallel kernel execution environments
cause GPUs to be more vulnerable to DISORDER.
M3-GPU
Similar to the M1-CPU, there is little documenta-
tion about this processor. To demystify its execution model,
we designed a small microbenchmark in which two distinct
processes each execute a small kernel for roughly the same
amount of time k. We spawn both processes simultaneously
and observe that the total time needed for both to finish is
also k. Thus, we can conclude that this GPU provides a par-
allel kernel execution model. Our results, at the bottom of
Tab. 4, show that this parallel kernel execution leads to more
frequent, reliable, and effective signals (by at least an order
of magnitude) than on the other GPU devices. Thus, if GPUs
move towards more parallel execution models, DISORDER
vulnerabilities may become more effective.
4.3
Virtualization Boundaries
Our results thus far have simply tested cross-process signals
on readily available consumer devices. However, it is impor-
tant to test other systems for DISORDER, especially multi-
tenant, security critical systems. While we showed that X86
systems (which are widely deployed in the cloud) are vulner-
able to DISORDER, Arm systems potentially have a larger
attack surface, given that they allow many more re-orderings.
We note that Arm-based systems are becoming more com-
mon in the cloud, such as Amazon’s Graviton processors [7]
executing on multi-tenant machines through the Nitro hy-
pervisor [8]. Similarly, Google Cloud provides Arm-based
Axiom processors [17] and potentially use KVM as the hy-
pervisor [16].
More recently, GPUs now have some virtualization support.
In these approaches, the physical GPU hardware is partitioned,
and each virtual GPU is given a physical slice of the GPU.
NVIDIA offers MIG [34], and AMD offers SR-IOV [9]. We
do not test those systems currently for two reasons: they re-
quire high-end recent GPUs, which we do not have immediate
access to, and they require re-writing some of our testing code.
5
Implementing DISORDER Attacks
Utilizing the data from the fuzzing campaign, we can identify
litmus tests, testing frameworks, and stress combinations that
expose reliable and easily identifiable signals. We show how
this can serve as a foundation for implementing two classic
attacks: a covert channel and application fingerprinting. Given
that these attacks require extensive hand-tuning and reliable
signals, we only implement them on a subset of our devices,
namely all of the CPUs and the Apple GPU.
Security boundaries
In this section, we increase the secu-
rity boundaries on our devices when possible. For the Apple
CPU and GPU, we show how DISORDER can cross process
boundaries. For Arm and X86, we implement these attacks
over a KVM virtualization boundary, launching the Listener
process on the host OS and the Stressor process on the guest.
Similar to the fuzzing campaign, we run some pilot experi-
ments to determine effective thread pinnings. On Arm, the
KVM instance is allocated three VCPUs, pinned to the host
cores 0, 2, and 4 while the Listener process runs the litmus
tests on host cores 1 and 3. On X86, all experiments allo-
cate ten VCPUs to the KVM instance, which are pinned to
even-numbered host cores. For the covert channel experiment
we pin the Listener to host cores 1 and 3 while for the DNN
fingerprinting experiment we pin them to host cores 1 and 11.
Our initial experiments show that thread launch stress be-
comes less reliable across KVM boundaries, which is intuitive
given the role of the OS in launching threads. However, mem-
ory stress remains reliable, and, thus, attacks on Arm and X86
will use memory stress.
5.1
DISORDER Covert Channels
DISORDER can be used to implement a covert channel in
the following way: a process receives communication by
running a litmus test and recording the number of observed re-
orderings. A time-series analysis is run to decode the signals
into high (↑), low (↓), and space (/0) signals. To send data, the
process executes different stress patterns which encode the ↑
and ↓signals, while a pause in stress encodes /0.
To ease implementation, we focus on a single direction
channel with one sender and receiver process. The receiver uti-
lizes a test configuration (litmus test and testing framework),
while the sender utilizes two types of stress configurations to
encode the two signals, which are chosen based on the results
from the fuzzing campaign. We summarize the configurations
in Tab. 5. We see that the MP and R litmus tests are the most
sensitive; each of the different testing frameworks and stress
techniques are used, except the perpetual testing framework.
We note that the X86-arch row in the table corresponds to
early experiments on exploiting low-level system details in
DISORDER and is described more thoroughly in Sec. 5.3.
9


Table 5: Details for DISORDER covert channel implementations. For each device, we show the testing framework and the
litmus test used. For each signal, we show the stress technique, the average number of re-orderings (Avg.) and the standard
deviation (Std.). The /0 does not have a stress technique as it is simply the absence of stress. X86-arch (highlighted in green) is
custom designed to low-level X86 system details and is described more in Sec. 5.3. It does not have a /0 signals
Device
Framework
Test
↑Stress
↑Avg.
↑Std.
↓Stress
↓Avg.
↓Std.
/0 Avg.
/0 Std.
Arm
litmus7
MP
mem
5859.1
1469.9
mem
3224.2
709.9
437.5
141.0
M1
basic
R
TL
137.7
20.3
TL
37.3
7.7
3.4
2.3
X86
litmus7
R
mem
803.6
46.7
mem
648.9
34.0
241.0
62.1
M3-GPU
GPU parallel
MP
mem
12.4
5.1
mem
2.4
1.9
0.0
0.0
X86-arch
arch-aware
SB
arch-aware
48.3
2.9
arch-aware
1.1
2.5
N/A
N/A
To decode signals, the receiver process must both classify
signals it receives and transition between signal states.
Signal Classification
We found that the number of re-
orderings with a reliable stress configuration is approximately
normally distributed, allowing us to calculate the mean and
standard deviation over a set of samples.The receiver main-
tains a window of test samples to account for the natural
variability of weak behaviors and lack of synchronization
between the sender and receiver.
The sender transmits signals by running the ↑, ↓, and /0
signals. The receiver calculates the likelihood of each sample
in the window coming from a given signal distribution using
a t-test parameterized by the signal’s mean and standard de-
viation. Each sample in the window is then classified as the
signal with the distribution that most closely matches the sam-
ple by ranking the p-values of the t-test results in descending
order. The receiver classifies a window as the signal matching
the classification of the majority of the samples in the window.
While this approach works well for CPUs, we found that on
the M3-GPU the number of memory re-orderings during a /0
signal is usually 0 and not normally distributed. Therefore,
we use a cutoff heuristic on this GPU and classify a sample as
a /0 signal if the number of re-orderings is less than the cutoff.
State Transition
The receiver implements a state machine
to transition between signals. It starts in a standby state, signi-
fying that it is waiting to see a ↑/ ↓signal. Once it has enough
samples to fill a window, the receiver classifies the window
and transitions to either the ↑or ↓state. The receiver stays in
the state until it classifies a window as the /0 signal, at which
point it records a bit and returns to the standby state. On the
M3-GPU, we observed that a ↑signal is sometimes misclassi-
fied, so we include a ↓′ state which the receiver transitions to
before transitioning to either the ↑or ↓state.
Experiments and Results
We test the accuracy and speed
of the covert channel by sending random bit strings from the
sender to the receiver. The accuracy of the channel can be
computed using the Levenshtein distance, i.e., the number of
Table 6: DISORDER Covert channel metrics. The X86-arch
system is highlighted because it is designed differently to
show-case the potential of DISORDER if low-level system
details can be exploited (see Sec. 5.3)
Device
Window Size
Accuracy
Bits/second
X86
5
98%
0.32
Arm
5
94%
0.36
M1
5
95%
0.66
M3-GPU
3
95%
16.05
X86-arch
5
94%
29448.90
single-bit edits (insertions, deletions, or swaps) between the
reference string and the received string. We attain a percentage
by dividing the distance by the length of the reference string.
Tab. 6 summarizes our results, showing the highest aver-
age bits per second (bps) we were able to achieve on the
covert channel on different devices while maintaining >90%
accuracy. The results were obtained by sending random 13-
character ASCII strings (104 bits) 10 times and calculating
the average speed and accuracy across the trials.
On the M3-GPU, we can achieve an average accuracy of
95% with a speed of 16 bps. Conversely, we see a much lower
bps on CPUs due to system noise from other processes on
the OS, requiring more test iterations and a larger window
size for increased reliability. These two factors mean that the
transmission rate is 2 orders of magnitude slower than the
GPU channel in order to reach a similar accuracy. We observe
that the M1-CPU covert channel is roughly 2× as fast as
the Arm and X86; this is because the M1-CPU had access
to the thread launch stress, which, recall from Sec. 4, yields
reliable high signals. Because Arm and X86 operate across
KVM boundaries, thread launch stress is less reliable and
thus, they use memory stress. Lastly, X86-arch (described in
Sec. 5.3) uses specialized stress that exploits low-level details
and achieves several orders of magnitude higher bps.
In relation to prior work, [12] implements a covert channel
for X86 based on re-orderings achieving roughly 1 bps while
utilizing a timer. Other timerless approaches achieve bps rates
10


similar to ours [24,25,47]. Finally, highly specialized timer-
less approaches can achieve kilobits per second [51]; we show
that DISORDER has the potential for this speed in X86-arch,
described more in Sec. 5.3.
5.2
DISORDER Fingerprinting
For application fingerprinting, we cannot rely on fine-tuned
stress signals from our fuzzing results. However, as illustrated
in Sec. 1.1, we show that certain application classes have
distinguishable signals that can be detected by DISORDER.
Deep Neural Networks Architectures
Different DNNs can
vary widely in their architectures, i.e., they can differ by layer
operation, depth, memory usage, and computational intensity.
These architectural differences manifest in their underlying
implementation on a given platform or accelerator, result-
ing in distinct memory access patterns. These differences
are akin to the different stress signals we search for in our
fuzzing campaign, especially related to memory stress. Thus,
a DISORDER fingerprinting attack may be able to distinguish
different DNN architectures running on different processes.
In these experiments, we select 5 common DNN architec-
tures, shown in Fig. 3. To select a test for the attack process,
we again consult our fuzzing data, looking for a configuration
that is reliably sensitive to memory stress. The attack process
then collects test samples while the victim simultaneously
runs DNN inference.
The details of our experiment are the following: let A be the
set of candidate models we wish to classify, let s be the system
we are testing (e.g., Arm, X86, M1-CPU, or M3-GPU), and
let t be the litmus test determined to be sensitive to memory
stress on s. For each DNN architecture d ∈A, we collect
4K observations of executing t on s while running d on a
different process. We designate the first 2K observations to be
the training set Sd, and the second 2K to be the test set Td. For
a DNN architecture d, we then randomly select z observations
from Td into sample t. We then compare t against each training
set Si for i ∈A using an independent samples t-test, classifying
t to whichever DNN provided the best fit.
We run these experiments across two different sample sizes:
small (30) and large (100). Figure 3 shows the results of
running 1000 trials per sample size, with each trial sampling
from a randomly chosen test set Td. As sample size increases,
classification accuracy improves, reaching over 80% at a size
of 100 on most devices. We tune the litmus test iterations such
that 30 samples takes less than 5 seconds on each device.
The mobilenetv3_small and alexnet architectures were eas-
ily classified across all devices, while vgg16 had comparably
lower accuracy on every device except the X86 CPU. Indeed,
the distributions of vgg16 and resnet50 shown in Fig. 2 are
relatively close on the M3-GPU. We find that the M1-CPU
has the lowest accuracy, however, pilot experiments showed
that increasing the litmus test iterations (as opposed to the
Figure 3: Results of classifying DNN architectures. This
graph shows the percentage of matched samples using an
independent sample t-test against a training set of memory
re-ordering observations with sample sizes of 30 and 100.
number of samples) appeared to increase its accuracy sub-
stantially. Thus, this attack requires tuning across multiple
dimensions, but high accuracy can be obtained across these
devices. Furthermore, utilizing more complex classification
techniques such as those in [14] could help to further refine
the accuracy of DNN classification using DISORDER.
Launching Applications
Given that our fuzzing results
show a high impact for thread launch stress, we now explore
if DISORDER can be used to fingerprint other types of system
behavior. We select the M1-CPU device since it is especially
sensitive to this stress type.
We select an application that might be conceptually simi-
lar to our thread launch stress, where threads are repeatedly
launched and joined. For this, we opted to use Google Chrome,
as it is heavily multithreaded. We explore if DISORDER can
be used to identify when an application like Google Chrome
is opened or closed. To do this, we execute a script that re-
peatedly opens and closes Chrome, with 3 seconds between
launching and closing and 2 seconds between re-launching.
The attacker uses the Read litmus test in the basic test-
ing framework, as that happens to be the most sensitive, and
constantly samples the number of re-orderings observed at
intervals of 1k iterations. Figure 4 shows the result of this
experiment, with the x-axis representing timestamps and the
y-axis showing the number of observed re-orderings. We see
very clear patterns when Google Chrome is launched (the
longer and taller region of re-orderings, colored in green),
when it is closed (shorter regions of re-orderings, colored in
red), and when the system is idle (lower re-orderings, colored
in black). This shows the potential for DISORDER to be used
to fingerprint other application behavior, especially related to
interactive applications on consumer devices.
Our pilot experiments show that many types of system
behavior increase the number of re-orderings observed on M
11


0
50K
100K
150K
200K
250K
Litmus Test Iterations
0
5
10
15
20
25
Weak Behaviors
Launch
Close
Figure 4: Memory re-orderings time series data across launch-
ing and closing Google Chrome on the M1-CPU.
series Apple devices. For example, even swapping tabs on a
terminal or launching an application dramatically increased
the number of observed re-orderings. Because the low-level
cause of these re-orderings has not yet been determined, it
is difficult to appreciate their full potential or offer rigorous
mitigation approaches. Given this, we believe future works
will be able to increase the fingerprinting precision and impact
of DISORDER.
5.3
Targeted Architectural Attacks
Up to this point, our attacks require no low-level architectural
knowledge, instead using our empirical fuzzing results. Now,
we show early results on the potential of DISORDER attacks
which exploit low-level hardware details. We show this on our
X86 processor, as it was the most straightforward platform
to run experiments on and X86 is typically well-documented.
Our experiments are in the context of a covert channel, where
we designed a custom sender and receiver framework called
arch-aware. We target the performance cores of this device,
where each core can execute two hardware threads (via hyper-
threading) and has its own 12-way set associative L1 cache
of size 48KB with a cache line size of 64 bytes.
Our hypothesis is that the X86 store buffer (responsible
for re-orderings) would be sensitive to whether the L1 cache
contains the x or y location in the litmus test. The receiver
(which implements the litmus test) is mapped to two distinct
cores. We found that by evicting one of the locations from the
L1 (say x), while ensuring the other location (say y) remained
in the L1 provided extremely high and reliable signals (i.e.,
re-orderings were observed in over 90% of iterations).
To implement a covert channel in this framework, we mimic
a sender in another thread which is mapped to the same core
as thread 0 in the receiver. To provide a signal, the sender
simply writes to 12 locations (the size of a cache set) that map
to the same cache set as memory location x, thus evicting x
from thread 0’s L1 cache. Table 5 shows that these signals are
very high and very reliable.
Extending this method, we are able to monitor multiple
cache sets: our X86 has 64 L1 cache sets, which allows us to
instantiate 63 litmus tests. The x locations map to different
cache sets, while the y locations all map the 64th cache set,
as it should not be evicted. These signals are so clear that the
tests only need to execute for 15 iterations. Furthermore, given
that multiple bits are sent at a time, there is no need for the
/0 signal as the first bit can act as a virtual clock, modulating
high and low between signals. This highly tuned configuration
is able to achieve nearly 30k bps, several orders of magnitude
higher than other approaches (see X86-arch in Tab. 5 and 6).
Towards a Full Attack
Our results from X86-arch are pre-
liminary and are meant to show the potential of DISORDER
when exploiting low-level system details. We were unable to
fully implement arch-aware as a full attack, as the re-orderings
seemed sensitive to more than simply cache sets. We found
that signals degraded in unpredictable ways as we tried to par-
tition the memory more fully across processes; and conversely,
strong reliable signals showed up in other configurations that
did not seem to correspond to any system documentation we
were aware of. Thus, we believe more detailed investigations
are necessary, and once the attack is more understood, then it
would likely be possible to fully implement high bandwidth
covert channels, as well as more fine-grained data extraction
attacks, e.g., cryptographic key extraction [51].
6
DISORDER Mitigations and Remediations
Similar to other side-channel attacks, e.g., prime-and-probe,
mitigations to DISORDER are difficult and invasive. Further-
more, unless vendors release precise explanations for memory
re-orderings (unlikely), then mitigations will be speculative or
empirical. For current systems, we see two mitigation paths:
Disallowing Memory Re-orderings
Program analysis tech-
niques have been used to disallow memory re-orderings by
automatically inserting fence instructions. To mitigate DIS-
ORDER using this approach, a system would have to force
all untrusted programs to be compiled in a way that removes
re-orderings, and disallow programming features that bypass
compiler analysis, e.g., inline assembly.
A naive approach can remove all re-orderings by placing a
fence after every memory instruction; however, this disallows
many hardware optimizations, and as such, has a high per-
formance overhead (as reported in [5,40]). Other approaches
perform more complex analysis to identify memory accesses
that are potentially shared across threads to prune the number
of fences. The overhead of these approaches is much less,
reportedly around 1.5× on average [27]. Some languages
follow a paradigm called sequential consistency for data-race
free programs (abbreviated as SC-DRF) [1]. Languages that
are SC-DRF guarantee that if programs follow certain rules
(i.e., they do not have data races) then no memory re-orderings
12


will be observable. If a system strictly enforced SC-DRF pro-
grams (such as in safe Rust), then memory re-orderings (and,
thus, DISORDER) would not be possible to observe.
Signal Obfuscation
A common side-channel mitigation
is to obfuscate compromised execution characteristics. For
example, a memory-based attacks can be mitigated if the
victim ensures input-oblivious memory accesses [36]. Other
approaches might insert random memory accesses in such
a way that the information leaked is no longer useful. Prior
work has proposed a variety of automated approaches that
accomplish this, from compiler techniques [44], to transparent
memory management techniques [52].
We show two characteristics that leak information through
DISORDER. The first is memory access patterns, which can
likely be mitigated similar to other memory side-channels.
The second is thread launching behaviors, which are novel for
DISORDER. Applications (e.g., Google Chrome) would need
to modify their thread management logic, e.g., to be uniform
with other applications. Given the complexity of large soft-
ware, combined with the complexity of parallel programming,
such mitigations will be difficult and invasive. Our pilot ex-
periments also found that DISORDER seems to be sensitive
to a variety of other system behavior (e.g., rapidly switching
terminal tabs). To implement a robust mitigation, the cause of
these re-orderings would need to be more fully understood.
Online Detection
A fingerprinting attack requires only two
cores to execute the litmus test, and <2MB of memory. The
overhead of running a DISORDER in the background varies
across systems and applications, but we found that for DNN
inference, DISORDER listeners caused only a 25% slowdown
on Apple CPUs. This overhead reduces for systems with more
parallelism, e.g., for the M3-GPU, the overhead of DISOR-
DER listeners was negligible. Thus, it is unlikely a resource
watchdog would flag a DISORDER attack as being an outlier.
7
Related Work
Memory-based Side-channels
Many recent works have
exploited a variety of different memory mechanisms as side-
channels; For example, [20] implements a side-channel by
measuring contention on storage devices on Linux systems.
They show how this can be used to implement a covert chan-
nel and do coarse-grained application fingerprinting. Other
works analyze implicit (and undocumented) memory compres-
sion techniques of different GPUs [46]; the memory traffic
produced by the compressed data can be used to reconstruct
images. Lastly, X86 prefetch instructions were shown to leak
cache coherence states [18], which can be used to implement
transient execution attacks more efficiently than prior works.
DISORDER distinguishes itself in two significant ways:
(1) DISORDER is lower capability, requiring no timers, no
hardware monitors, and no detailed reverse engineering for
low-precision configurations; (2) DISORDER exists across
many devices, whereas prior works are usually specialized.
Memory Model Testing and Modeling
Some prior works
have explored causes and characteristics of re-orderings. For
example, [31] uses empirical testing to determine the size of
the X86 store buffer; other works showed how memory bank
conflicts cause re-orderings on GPUs [3]. These low-level
details could greatly increase the precision of DISORDER
attacks (as shown in Sec. 5.3). However, they seem to exist
only for certain behaviors on (older) architectures.
Other work has modeled microarchitectural features that
cause re-orderings (such as cache protocols) [28]; utilizing
these models, they are able to validate conformance to higher-
level specifications. Similarly, another work used happens-
before relational models to capture many types of microar-
chitectural side-channels [43]. While this level of modeling
could yield insights into the cause of memory re-orderings,
it requires significant low-level knowledge, much of which
is proprietary, and as such, mainstream commercial systems
have not been modeled in this way.
DNN Architecture Fingerprinting
Other works have used
side-channels to extract/predict DNN architectures, similar to
how DISORDER is used in Sec. 5.2. For example, [50] use
Prime+Probe and Flush+Reload cache attacks to learn sizes
and number of matrices computed with high-performance
GEMM libraries. Other works use power consumption as
a side-channel in order to carry out a model extraction at-
tack [49]. More sophisticated model extraction attacks based
on power consumption were shown in [14], which recovered
network structure by analysing the time-dependent energy
trace. These works are highly specialized to certain devices
and require detailed timers or low-level power monitoring
APIs, whereas DISORDER is low capability and shown to be
widely applicable across many different devices.
8
Conclusion
We present a novel, timerless side-channel attack utilizing
memory re-orderings called MEMORY DISORDER. We show
that this attack impacts most mainstream processors, includ-
ing Arm, X86, and Apple CPUs, as well as NVIDIA, AMD,
and Apple GPUs. We show the potential for DISORDER to be
used in classic attacks such as covert channels and application
fingerprinting. If future work is able to more precisely iden-
tify the cause of memory re-orderings (possibly focusing on
a single processor), it will likely enable more targeted attacks,
as well as inform robust mitigation techniques.
13


9
Responsible Disclosure
We provided a pre-print and summary of this work to the
security teams at the following companies: Apple, Amazon,
AMD, ARM, Google, Intel, Microsoft, NVIDIA, Qualcomm,
and Samsung. All acknowledged the finding and approved of
the publishing timeline.
References
[1] Sarita V. Adve and Mark D. Hill. Weak ordering—a
new definition. In Proceedings of the 17th Annual Inter-
national Symposium on Computer Architecture. ACM,
1990.
[2] Jaeguk
Ahn,
Jiho
Kim,
Hans
Kasan,
Leila
Delshadtehrani, Wonjun
Song, Ajay
Joshi, and
John Kim.
Network-on-chip microarchitecture-
based covert channel in GPUs. In MICRO-54: 54th
Annual IEEE/ACM
International Symposium
on
Microarchitecture. ACM, 2021.
[3] Jade Alglave, Mark Batty, Alastair F. Donaldson,
Ganesh Gopalakrishnan, Jeroen Ketema, Daniel Poetzl,
Tyler Sorensen, and John Wickerson. GPU concurrency:
Weak behaviours and programming assumptions. In
Architectural Support for Programming Languages and
Operating Systems (ASPLOS). ACM, 2015.
[4] Jade Alglave, Anthony Fox, Samin Ishtiaq, Mag-
nus O. Myreen, Susmit Sarkar, Peter Sewell, and
Francesco Zappa Nardelli.
The semantics of power
and arm multiprocessor machine code. In Proceedings
of the 4th Workshop on Declarative Aspects of Multicore
Programming. ACM, 2009.
[5] Jade Alglave, Daniel Kroening, Vincent Nimal, and
Daniel Poetzl. Don’t sit on the fence: A static anal-
ysis approach to automatic fence insertion. ACM Trans.
Program. Lang. Syst., 2017.
[6] Jade Alglave, Luc Maranget, Susmit Sarkar, and Peter
Sewell. Litmus: Running tests against hardware. In
Tools and Algorithms for the Construction and Analysis
of Systems. Springer Berlin Heidelberg, 2011.
[7] Amazon. AWS Graviton2 for independent software
vendors. https://docs.aws.amazon.com/pdfs/w
hitepapers/latest/aws-graviton2-for-isv/a
ws-graviton2-for-isv.pdf, 2024.
[8] Amazon. The security design of the AWS nitro system.
https://docs.aws.amazon.com/pdfs/whitepape
rs/latest/security-design-of-aws-nitro-sys
tem/security-design-of-aws-nitro-system.pd
f, 2024.
[9] AMD. Consistency and security: AMD’s approach to
gpu virtualization. https://www.amd.com/system/f
iles/documents/gpu-consistency-security-w
hitepaper.pdf, 2017.
[10] Arvind Arvind and Jan-Willem Maessen.
Memory
model = instruction reordering + store atomicity. In
Proceedings of the 33rd Annual International Sympo-
sium on Computer Architecture. IEEE Computer Soci-
ety, 2006.
[11] Mark Batty, Scott Owens, Susmit Sarkar, Peter Sewell,
and Tjark Weber. Mathematizing C++ concurrency. In
Principles of Programming Languages (POPL). ACM,
2011.
[12] Sophia d’Antoine, Jeremy Blackthorne, and Bülent
Yener.
Out-of-order execution as a cross-VM side-
channel and other applications. In Proceedings of the 1st
Reversing and Offensive-Oriented Trends Symposium.
Association for Computing Machinery, 2017.
[13] Shaked Flur, Kathryn E. Gray, Christopher Pulte, Sus-
mit Sarkar, Ali Sezgin, Luc Maranget, Will Deacon, and
Peter Sewell. Modelling the ARMv8 architecture, oper-
ationally: concurrency and ISA. In Proceedings of the
43rd Annual ACM SIGPLAN-SIGACT Symposium on
Principles of Programming Languages. ACM, 2016.
[14] Y. Gao, H. Qiu, Z. Zhang, B. Wang, H. Ma, A. Abuadbba,
M. Xue, A. Fu, and S. Nepal. Deeptheft: Stealing dnn
model architectures through power side channel. In
2024 IEEE Symposium on Security and Privacy (SP).
IEEE Computer Society, 2024.
[15] Lukas Giner, Roland Czerny, Christoph Gruber, Fabian
Rauscher, Andreas Kogler, Daniel De Almeida Braga,
and Daniel Gruss. Generic and automated drive-by GPU
cache attacks from the browser. In Proceedings of the
19th ACM Asia Conference on Computer and Commu-
nications Security. ACM, 2024.
[16] Google. 7 ways we harden our KVM hypervisor at
Google cloud: security in plaintext. https://cloud.
google.com/blog/products/gcp/7-ways-we-har
den-our-kvm-hypervisor-at-google-cloud-sec
urity-in-plaintext, 2017.
[17] Google. Introducing Google axion processors, our new
arm-based CPUs. https://cloud.google.com/blo
g/products/compute/introducing-googles-new
-arm-based-cpu, 2024.
[18] Y. Guo, A. Zigerelli, Y. Zhang, and J. Yang. Adversarial
prefetch: New cross-core cache side channel attacks.
In Security and Privacy (SP). IEEE Computer Society,
2022.
14


[19] Apple Inc. Metal shading language specification. ht
tps://developer.apple.com/metal/Metal-Sha
ding-Language-Specification.pdf. Accessed:
2024-06-05.
[20] Qisheng Jiang and Chundong Wang. Sync+sync: A
covert channel built on fsync with storage.
In 33rd
USENIX Security Symposium (USENIX Security 24).
USENIX Association, 2024.
[21] Jake Kirkham, Tyler Sorensen, Esin Tureci, and Mar-
garet Martonosi.
Foundations of empirical memory
consistency testing. Proceedings of the ACM on Pro-
gramming Languages, 2020.
[22] Reese Levine, Mingun Cho, Devon McKee, Andrew
Quinn, and Tyler Sorensen. GPUHarbor: Testing GPU
memory consistency at large (experience paper). In
Proceedings of the 32nd ACM SIGSOFT International
Symposium on Software Testing and Analysis. ACM,
2023.
[23] Reese Levine, Tianhao Guo, Mingun Cho, Alan Baker,
Raph Levien, David Neto, Andrew Quinn, and Tyler
Sorensen. MC mutants: Evaluating and improving test-
ing for memory consistency specifications. In Proceed-
ings of the 28th ACM International Conference on Ar-
chitectural Support for Programming Languages and
Operating Systems, Volume 2. ACM, 2023.
[24] Moritz Lipp, Daniel Gruss, and Michael Schwarz. AMD
prefetch attacks through power and time. In USENIX
Security Symposium, 2022.
[25] Moritz Lipp, Andreas Kogler, David Oswald, Michael
Schwarz, Catherine Easdon, Claudio Canella, and
Daniel Gruss. PLATYPUS: Software-based power side-
channel attacks on x86. In 2021 IEEE Symposium on
Security and Privacy (SP), 2021.
[26] Fangfei Liu, Yuval Yarom, Qian Ge, Gernot Heiser, and
Ruby B. Lee. Last-level cache side-channel attacks are
practical. In 2015 IEEE Symposium on Security and
Privacy. IEEE, 2015.
[27] Lun Liu, Todd Millstein, and Madanlal Musuvathi. Ac-
celerating sequential consistency for Java with specu-
lative compilation. In Proceedings of the 40th ACM
SIGPLAN Conference on Programming Language De-
sign and Implementation. ACM, 2019.
[28] Yatin A. Manerkar, Daniel Lustig, Michael Pellauer, and
Margaret Martonosi. CCICheck: Using UHB graphs
to verify the coherence-consistency interface. In 2015
48th Annual IEEE/ACM International Symposium on
Microarchitecture (MICRO). ACM, 2015.
[29] Henry B Mann and Donald R Whitney. On a test of
whether one of two random variables is stochastically
larger than the other. The annals of mathematical statis-
tics, 1947.
[30] Themis Melissaris, Markos Markakis, Kelly Shaw, and
Margaret Martonosi. PerpLE: Improving the speed and
effectiveness of memory consistency testing. In 2020
53rd Annual IEEE/ACM International Symposium on
Microarchitecture (MICRO). IEEE, 2020.
[31] Adam Morrison and Yehuda Afek. Temporally bound-
ing TSO for fence-free asymmetric synchronization. In
Proceedings of the Twentieth International Conference
on Architectural Support for Programming Languages
and Operating Systems. ACM, 2015.
[32] Vijay Nagarajan, Daniel J. Sorin, Mark D. Hill, and
David A. Wood. A Primer on Memory Consistency and
Cache Coherence. Springer International Publishing,
2020.
[33] Hoda Naghibijouybari, Khaled N. Khasawneh, and Nael
Abu-Ghazaleh. Constructing and characterizing covert
channels on GPGPUs. In Proceedings of the 50th An-
nual IEEE/ACM International Symposium on Microar-
chitecture. ACM, 2017.
[34] NVIDIA. Multi-instance GPU user guide (user guide).
https://docs.nvidia.com/datacenter/tesla/p
df/NVIDIA_MIG_User_Guide.pdf, March 2024.
[35] NVIDIA. Multi-process service (release r550). https:
//docs.nvidia.com/deploy/pdf/CUDA_Multi_Pr
ocess_Service_Overview.pdf, June 2024.
[36] Dag Arne Osvik, Adi Shamir, and Eran Tromer. Cache
attacks and countermeasures: The case of AES. In David
Pointcheval, editor, Topics in Cryptology – CT-RSA 2006.
Springer Berlin Heidelberg, 2006.
[37] Scott Owens, Susmit Sarkar, and Peter Sewell. A better
x86 memory model: x86-TSO. In Proceedings of the
22nd International Conference on Theorem Proving in
Higher Order Logics. Springer-Verlag, 2009.
[38] Michael Schwarz, Clémentine Maurice, Daniel Gruss,
and Stefan Mangard.
Fantastic timers and where
to find them: High-resolution microarchitectural at-
tacks in JavaScript. In Financial Cryptography and
Data Security: 21st International Conference, FC 2017,
Sliema, Malta, April 3–7, 2017, Revised Selected Papers.
Springer-Verlag, 2023.
[39] Peter
Sewell,
Susmit
Sarkar,
Scott
Owens,
Francesco Zappa Nardelli, and Magnus O. Myreen.
x86-TSO: a rigorous and usable programmer’s model
for x86 multiprocessors. Commun. ACM, 2010.
15


[40] Tyler Sorensen and Alastair F. Donaldson. Exposing
errors related to weak memory in GPU applications. In
Proceedings of the 37th ACM SIGPLAN Conference on
Programming Language Design and Implementation.
ACM, 2016.
[41] Tyler Sorensen and Heidy Khlaaf. LeftoverLocals: Lis-
tening to LLM responses through leaked GPU local
memory, 2024.
[42] Sanya Srivastava. Testing memory models of heteroge-
neous CPU-GPU systems. Master’s thesis, University
of California, Santa Cruz, 2024. https://www.proq
uest.com/dissertations-theses/testing-mem
ory-models-heterogeneous-cpu-gpu/docview/3
082136707/se-2.
[43] Caroline
Trippel, Daniel
Lustig, and
Margaret
Martonosi.
CheckMate: Automated synthesis of
hardware exploits and security litmus tests. In 2018
51st Annual IEEE/ACM International Symposium on
Microarchitecture (MICRO). IEEE, 2018.
[44] Jeroen Van Cleemput, Bjorn De Sutter, and Koen
De Bosschere. Adaptive compiler strategies for mit-
igating timing side channel attacks. IEEE Transactions
on Dependable and Secure Computing, 2020.
[45] W3C. WebGPU specification. https://www.w3.org
/TR/webgpu/, 2023. Accessed: 2024-07-17.
[46] Y. Wang, R. Paccagnella, Z. Gang, W. Vasquez,
D. Kohlbrenner, H. Shacham, and C. Fletcher. Gpu.zip:
On the side-channel implications of hardware-based
graphical data compression. In Security and Privacy
(SP). IEEE Computer Society, 2024.
[47] Yingchen Wang, Riccardo Paccagnella, Elizabeth Tang
He, Hovav Shacham, Christopher W. Fletcher, and David
Kohlbrenner. Hertzbleed: Turning power Side-Channel
attacks into remote timing attacks on x86.
In 31st
USENIX Security Symposium (USENIX Security 22).
USENIX Association, 2022.
[48] William W. Collier. ARCHTEST. http://www.mpdi
ag.com/archtest.html, January 1994.
[49] Yun Xiang, Zhuangzhi Chen, Zuohui Chen, Zebin Fang,
Haiyang Hao, Jinyin Chen, Yi Liu, Zhefu Wu, Qi Xuan,
and Xiaoniu Yang.
Open DNN box by power side-
channel attack.
IEEE Transactions on Circuits and
Systems II: Express Briefs, 2020.
[50] Mengjia Yan, Christopher W. Fletcher, and Josep Tor-
rellas. Cache telepathy: Leveraging shared resource
attacks to learn DNN architectures. In 29th USENIX
Security Symposium (USENIX Security 20). USENIX
Association, 2020.
[51] Jiyong Yu, Aishani Dutta, Trent Jaeger, David Kohlbren-
ner, and Christopher W. Fletcher. Synchronization stor-
age channels (S2C): Timer-less cache Side-Channel
attacks on the Apple M1 via hardware synchroniza-
tion instructions. In 32nd USENIX Security Symposium
(USENIX Security 23). USENIX Association, 2023.
[52] Ziqiao Zhou, Michael K. Reiter, and Yinqian Zhang. A
software approach to defeating side channels in last-
level caches. In Proceedings of the 2016 ACM SIGSAC
Conference on Computer and Communications Security.
Association for Computing Machinery, 2016.
16
