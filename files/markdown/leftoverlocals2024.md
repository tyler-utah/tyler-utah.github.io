# LeftoverLocals: Listening to LLM Responses Through Leaked GPU Local Memory

**Authors:** T. Sorensen, H. Khlaaf  
**Venue:** ArXiv, 2024  
**PDF:** [leftoverlocals2024.pdf](../leftoverlocals2024.pdf)

---

LeftoverLocals: Listening to LLM Responses Through
Leaked GPU Local Memory
Tyler Sorensen
Trail of Bits
University of California, Santa Cruz
Santa Cruz, California, USA
Heidy Khlaaf
Trail of Bits
New York City, New York, USA
Abstract
This paper describes LeftoverLocals: a vulnerability that al-
lows data recovery from GPU memory created by another
process on Apple, Qualcomm, and AMD GPUs. Leftover-
Locals impacts the security posture of GPU applications,
with particular significance to LLMs and ML models that
run on impacted GPUs. By recovering local memory – an
optimized GPU memory region – we built a PoC where an at-
tacker can listen into another user’s interactive LLM session
(e.g., llama.cpp) across process or container boundaries.
1
Introduction
This paper is essentially a direct port (by the authors) from the
official Trail of bits blog post, which can be found here: https://
blog.trailofbits.com/2024/01/16/leftoverlocals-listening-to-llm-
responses-through-leaked-gpu-local-memory/. This document
was created because an archived paper may be better suited
for distribution and citation in some cases.
Given the rise of ML applications, especially for privacy
sensitive application domains, it is imperative to rigorously
examine security properties throughout the ML stack. This
includes the computational work horse of ML applications,
the GPU. While NVIDIA GPUs currently appear to domi-
nate the ML market, most other hardware vendors create
their own GPUs, which are becoming more widely used
for ML applications, especially for local computation. This
work discusses a data leak vulnerability found on many of
these GPUs, specifically, from AMD, Apple, Qualcomm and
Imagination. This leak, dubbed LeftoverLocals, was disclosed
earlier this year (CVE-2023-49691) and allows a co-resident
process to read leftover data in an optimized GPU memory
region called local memory.
LeftoverLocals can leak approximately 5.5 MB per GPU
invocation on an AMD Radeon RX 7900 XT which, when
running a 7B model on llama.cpp, adds up to 181 MB for
each LLM query. This is enough information to reconstruct
the LLM response with high precision, an example is shown
in Fig. 1. The vulnerability highlights that many parts of
the ML development stack have unknown security risks and
have not been rigorously reviewed by security experts.
Trail of Bits worked with CERT Coordination Center on a
large coordinated disclosure effort involving all major GPU
1https://kb.cert.org/vuls/id/446598
Figure 1. An example of an LLM response that an attacker
was able to reconstruct utilizing LeftoverLocals. The victim
terminal is on the left (black background), and the attacker
terminal is on the right (white backgroun). We can see that
the attacker is able to reconstruct the response with relatively
high fidelity. We believe that the listener could be more
finally tuned to be even more accurate. Details proof-of-
concept attack application, along with the system, can be
found in Sec. 5.
vendors, including: NVIDIA, Apple, AMD, Arm, Intel, Qual-
comm, and Imagination. As of writing (Feb. 1, 2024), the
status of the impacted vendors, Apple, AMD, and Qualcomm
are as follows:
• Apple: Despite multiple efforts to establish contact
through CERT/CC, we only received a response from
Apple on January 13, 2024. We re-tested the vulner-
ability on January 10 where it appears that some de-
vices have been patched, i.e., Apple iPad Air 3rd G
(A12). However, the issue still appears to be present
on the Apple MacBook Air (M2). Furthermore, the
recently released Apple iPhone 15 does not appear to
be impacted as previous versions have been. Apple
has confirmed that the A17 and M3 series processors
contain fixes, but we have not been notified of the
specific patches deployed across their devices.
• AMD: We have confirmed with AMD that their de-
vices remain impacted, although they continue to in-
vestigate potential mitigation plans. Their statement
on the issue can be read here2.
• Qualcomm: We received notice that there is a patch
to Qualcomm firmware v2.073 that addresses Leftover-
Locals for some devices. However, there may still be
2https://www.amd.com/en/resources/product-security/bulletin/amd-sb-
6010.html
3https://lore.kernel.org/linux-firmware/20240111114032.126035-1-
quic_akhilpo@quicinc.com/
arXiv:2401.16603v1  [cs.CR]  29 Jan 2024


Tyler Sorensen and Heidy Khlaaf
other devices impacted at this time. A Qualcomm rep-
resentative has provided the following comment: “De-
veloping technologies that endeavor to support robust
security and privacy is a priority for Qualcomm Tech-
nologies. We commend Dr. Tyler Sorensen and Dr.
Heidy Khlaaf from the AI/ML Assurance group at
Trail of Bits for using coordinated disclosure practices
and are in the process of providing security updates
to our customers. We encourage end users to apply
security updates as they become available from their
device makers.”
• Imagination: Despite not observing LeftoverLocals
ourselves across the Imagination GPUs that we tested
(see Sec. 6), Google has confirmed that some Imagina-
tion GPUs are indeed impacted. Imagination released
a fix in their latest DDK release, 23.3, made available
to customers in December 20234.
A list of tested and impacted devices can be found in Sec. 6
Other vendors have provided us the following details:
• NVIDIA: confirmed that their devices are not cur-
rently impacted. One reason for this could be that
researchers have explored various memory leaks on
NVIDIA GPUs previously, e.g., in [6], and thus, they
are aware of these types of issues.
• ARM: also confirmed that their devices are not cur-
rently impacted.
We did not hear a response from the remaining vendor,
Intel, we however, we tested two GPUs from them and did
not observe that they were impacted (see Sec. 6).
2
Exploit Brief
GPUs were initially developed to accelerate graphics com-
putations. In this domain, performance is critical, and pre-
viously uncovered security issues have generally not had
any significant consequences on applications. Historically,
this entailed that GPU hardware and software stacks iterated
rapidly, with frequent major architecture and programming
model changes. This has led to complex system stacks and
vague specifications. For example, while CPU ISAs have vol-
umes of documentation, NVIDIA simply provides a few short
tables5. This type of vague specification has led to alarming
issues, both previously [1] and currently, as LeftoverLocals
exemplifies.
2.1
Exploitation requirements
This is a co-resident exploit, meaning that a threat actor’s
avenue of attack could be implemented as another applica-
tion, app, or user on a shared machine. The attacker only
requires the ability to run GPU compute applications, e.g.,
through OpenCL, Vulkan, or Metal. These frameworks are
4https://www.imaginationtech.com/gpu-driver-vulnerabilities/
5https://docs.nvidia.com/cuda/cuda-binary-utilities/index.html#
instruction-set-reference
well-supported and typically do not require escalated privi-
leges. Using these, the attacker can read data that the victim
has left in the GPU local memory simply by writing a GPU
kernel that dumps uninitialized local memory. These attack
programs, as our code demonstrates, can be less than 10
lines of code. Implementing these attacks is thus not difficult
and is accessible to amateur programmers (at least in obtain-
ing stolen data). We note that it appears that browser GPU
frameworks (e.g., WebGPU) are not currently impacted, as
they insert dynamic memory checks into GPU kernels.
Unless the user inspects the application’s low-level GPU
source-code, it is not possible for them to uncover if their
application is utilizing GPU local memory; this matter is
further complicated as the GPU code is often hidden deep in
library calls, at low levels of deep software stacks (e.g., for
ML). Overall, there are very limited ways to observe that an
attacker is currently stealing data, or has stolen data. This
attack hinges on the attacker reading uninitialized memory
on the GPU, and while this is technically undefined behav-
ior, it is not currently checked dynamically, or logged. Any
additional defenses would be quite invasive, e.g., performing
code analysis on GPU kernels to check for undefined behav-
ior. We have released a PoC that vulnerability shows how
this vulnerability can be exploited6, and Sec. 5 describes how
it works.
2.2
Mitigations
Given the lack of comprehensive patches across impacted
GPU vendors, LeftoverLocals can be defended by modifying
the source code of all GPU kernels that use local memory.
Before the kernel ends, the GPU threads should clear mem-
ory (e.g., store 0s) to any local memory memory locations
that were used in the kernel. Additionally, the users should
ensure the compiler doesn’t remove these memory-clearing
instructions away (e.g., by annotating their local memory as
volatile), as the compiler may detect that the cleared mem-
ory is not used later in the kernel. This is difficult to verify
because GPU binaries are typically not stored explicitly, and
there are very few GPU binary analysis tools. Because of
reasons like this, we note that this mitigation may be difficult
for many users, and we discuss this further in Sec. 6.
3
Background: How GPUs work
GPUs are massively parallel, throughput-oriented co-processors.
While originally designed to accelerate graphics workloads,
their design, which balances flexible programming and high
computational throughput, has been highly effective in a
variety of applications. Perhaps the most impactful current
application domain is machine learning, where GPUs are the
computational workhorse and are used to achieve nearly all
major results in this area.
6https://github.com/trailofbits/LeftoverLocalsRelease


LeftoverLocals: Listening to LLM Responses Through Leaked GPU Local Memory
Local memory for 
Compute Unit 0
Local memory for 
Compute Unit N
Compute Unit 0
Compute Unit N
……..
Processing 
Elements
Global Memory
Figure 2. A simplified view of the GPU architecture: pro-
cessing elements are partitioned into compute unites. All
processing elements have access to global memory (often
located in VRAM for discrete GPUs), while only processing
elements in the same compute unit share the same local
memory.
GPUs are not only in large servers; they are in our phones,
our tablets, and our laptops. These GPUs come from a variety
of vendors, with almost all major hardware vendors (Apple,
AMD, Arm, Qualcomm, Intel, and Imagination) producing
their own GPU architecture. These GPUs are increasingly
used for ML tasks, especially because doing ML locally can
preserve users’ privacy, achieve lower latency, and reduce
computational burdens on service providers.
GPU architecture. GPU architecture has a parallel, hier-
archical structure, shown in Fig. 2. At the top level, a GPU
is made up of Compute Units (sometimes called Streaming
Multiprocessors in NVIDIA literature). Large, discrete GPUs
contain many compute units, and smaller, mobile GPUs have
fewer. For example, the large AMD Radeon RX 7900 XT
discrete GPU has 84 compute units, while the mobile Qual-
comm Adreno 740 GPU has 8. All compute units have access
to global memory. On discrete GPUs, global memory is im-
plemented using VRAM; on integrated GPUs, global memory
simply uses the CPU’s main memory.
Compute units encapsulate both compute and memory
components. Compute units contain an array of processing
elements; these simple cores are the fundamental units of
computation and execute a stream of GPU instructions. In
terms of memory, compute units often contain a cache for
global memory, but they also contain a special region of
memory called local memory. This is an optimized memory
region that is shared only across processing elements in the
same compute unit. This memory can be accessed with sig-
nificantly less latency than global memory, but also has much
smaller capacity. Different GPUs have varying amounts of
local memory per compute unit, typically ranging from 16KB
to 64KB. For example, the AMD Radeon RX 7900 XT GPU
has 84 compute units and a local memory size of 64KB; thus,
the total amount of local memory on the GPU is 5MB. Local
Table 1. A translation table between terminology used in
different GPU programming frameworks. This work uses
OpenCL terminology, but readers may by more familiar with
CUDA or Metal terminology.
CUDA
OpenCL
Metal
thread
work-item
thread
thread block
workgroup
threadgroup
shared memory
local memory
threadgroup memory
memory is a software-managed cache: the program execut-
ing on the processing elements is responsible for loading
values into local memory (e.g., values that will be repeatedly
used from global memory).
GPU execution model. A GPU program, called a (GPU)
kernel, is written in a shader language. Common examples
are SPIR-V (Vulkan), OpenCL C, (OpenCL), and Metal Shad-
ing Language (Metal). These kernels specify a single entry
point function, called the kernel function, which is executed
by many invocations (i.e., GPU threads). Invocations have
unique built-in identifiers (such as a global ID), which can be
used to index a unique data element in a data-parallel pro-
gram. Invocations are further partitioned into workgroups.
Each workgroup is mapped to a compute unit (although
many workgroups may execute on the same compute unit,
depending on resource requirements). All invocations have
access to the same global memory, but only invocations in
the same workgroup will share the same local memory.
Applications that use the GPU often launch many short-
running kernels. These kernels often correspond to basic
operations, such as matrix multiplication or convolution.
Kernels can then be executed in sequence; for example, each
layer in a deep neural network will be a kernel execution.
Local memory is statically allocated at each kernel launch
and is not specified to persist across kernel calls.
Platforms generally do not time-multiplex different GPU
kernels. That is, if multiple kernels are launched simulta-
neously (e.g., by different users), the GPU will execute one
kernel to competition before the next kernel starts. Because
GPU kernels are typically short running, sharing GPU re-
sources at kernel boundaries saves expensive preemption
overhead while also maintaining acceptable latency in prac-
tice.
Terminology. Because this blog post focuses on portable
GPU computing, it uses OpenCL GPU terminology. For read-
ers more familiar with GPU terminology from a different
framework (e.g., CUDA or Metal), we provide a translation
table in Tab. 1.


Tyler Sorensen and Heidy Khlaaf
4
The Vulnerability: LeftoverLocals
In this section we describe the vulnerability, named Leftover-
Locals, in more detail. Section 6 details our testing campaign
across a wide variety of GPU devices, which found that GPUs
from AMD, Apple, and Qualcomm are vulnerable to Left-
overLocals. We also note that while GPU memory leaks are
not new, e.g., see [6], LeftoverLocals has demonstrated both
deeper impact and wider breadth than previously discovered
vulnerabilities.
At a high level, we found that several GPU frameworks
do not sufficiently isolate memory in the same way that it is
traditionally expected in CPU-based frameworks. We have
observed that on impacted GPUs, it is possible for one ker-
nel—potentially from another user that is co-resident on the
same machine—to observe values in local memory that were
written by another kernel. Thus, an attacker who has access
to a shared GPU through its programmable interface (e.g.,
OpenCL) can steal memory from other users and processes,
violating traditional process isolation properties. This data
leaking can have severe security consequences, especially
given the rise of ML systems, where local memory is used to
store model inputs, outputs, and weights.
Previous academic work showed that NVIDIA GPUs leaked
memory across processes through a variety of memory re-
gions, including local memory and across virtualized envi-
ronments [4, 6]. However, they examined only GPUs from
NVIDIA (and we speculate that the results from this paper
may be part of the reason why we didn’t observe LocalLeft-
overs on NVIDIA GPUs). They also did not discuss the im-
pact on widely deployed use-cases, such as ML. Other works
have shown how GPUs leak graphics data, and that a co-
resident attacker can reconstruct partial visual information
from another process [2, 7, 8]. A good survey of existing
GPU vulnerabilities can be found in [5]. Despite these prior
works, LeftoverLocals shows that many GPUs remain vul-
nerable to local memory leaks and that this vulnerability
can be exploited in co-resident attacks on important ML
applications.
Overall, this vulnerability can be illustrated using two sim-
ple programs: a listener and a writer, where the writer stores
canary values in local memory, while a listener reads unini-
tialized local memory to check for the canary values. The
listener repeatedly launches a GPU kernel that reads from
uninitialized local memory. The writer repeatedly launches
a GPU kernel that writes canary values to local memory. Be-
low, we demonstrate how each of these operations is carried
out.
The listener. The listener launches a GPU kernel that
reads from uninitialized local memory and stores the result
in a persistent main memory region (i.e., global memory).
This can be accomplished with the OpenCL kernel shown in
Fig. 3.
1
__kernel
void
l i s t e n e r ( _ _g lo ba l
v o l a t i l e
2
int
∗dump )
3
{
4
5
l o c a l
v o l a t i l e
int lm [ L_SIZE ] ;
6
7
for
( int
i =
g e t _ l o c a l _ i d ( 0 ) ;
8
i <
L_SIZE ;
9
i +=
g e t _ l o c a l _ s i z e ( 0 ) )
10
{
11
12
dump[ L_SIZE ∗get_group_id ( 0 ) + i ]=lm [ i ] ;
13
}
14
}
Figure 3. An OpenCL kernel showing how to implement a
LeftoverLocals listener. Essentially the kernel dumps unini-
tialized local memory (from the lm array) into a persis-
tent (global) memory region (in dump) so that it can be
examined later by the host. The OpenCL builtin ids (e.g.,
get_local_id(0)), allow the entire local memory dump to
be done efficiently in parallel.
The keyword __kernel denotes that this is the GPU ker-
nel function. We pass a global memory array dump to the
function. Whatever the kernel writes to this array can be
read later by the CPU. We statically declare a local memory
array lm with a predefined size L_SIZE (which we set to be
the max size of local memory for each GPU we test). This
program technically contains undefined behavior, as it reads
from uninitialized local memory. Because of this, we use
the volatile qualifier to suppress aggressive compiler opti-
mizations that might optimize away the memory accesses.
In fact, the code in the github we provide contains a few
more code patterns included to further stop the compiler
from optimizing away our memory dump. This process is
guided by trial-and-error, rather than a systematic approach.
For each loop iteration, the work-item (thread) reads from
a location in local memory, and then stores that value to
a unique location in the global dump array. The only tricky
part of this code is the indexing, because local memory is
disjointed across workgroups, so workgroup local IDs need
to be mapped to a unique global ID in dump. The process
utilizes OpenCL built-in identifiers to achieve this, which are
documented in the OpenCL C specification7. At the end of
the kernel, dump contains every value that was stored in local
memory when the listener kernel started executing. Because
dump is in the global memory region, it can be copied back
to CPU memory and examined to check for canary values.
7https://registry.khronos.org/OpenCL/specs/3.0-unified/html/OpenCL_C.
html#work-item-functions


LeftoverLocals: Listening to LLM Responses Through Leaked GPU Local Memory
1
__kernel
void
w r i t e r ( __global
v o l a t i l e
2
int
∗canary )
3
{
4
l o c a l
v o l a t i l e
int lm [ L_SIZE ] ;
5
for
( uint
i =
g e t _ l o c a l _ i d ( 0 ) ;
6
i < L_SIZE ;
7
i +=
g e t _ l o c a l _ s i z e ( 0 ) )
8
{
9
lm [ i ] = canary [ i ] ;
10
}
11
}
Figure 4. An OpenCL kernel showing how to implement a
LeftoverLocals writer. Essentially the kernel writes a canary
value to all of local memory (in the lm array) so that a listener
can later check to see if it observes canary values. Similar to
the listener, the OpenCL builtin ids (e.g., get_local_id(0)),
allow the writer to write to the entirety of local memory
efficiently in parallel.
The writer. On the other hand, the writer launches a ker-
nel that writes a canary value to local memory (for example,
this work uses the value 123). We show an example of the
OpenCL kernel code in Fig. 4.
This code is very similar to the listener, except that rather
than dumping local memory, it writes to local memory. In
this case, the code is writing a value from a memory location
called canary. We use an extra location so that the compiler
does not optimize away the memory write (as it is prone to
do with constant values). At the end of the kernel, the writer
has filled all available local memory with the canary value.
The Host. The CPU host programs for both the listener
and the writer launch their respective kernels repeatedly. In
the case of the listener, at each iteration, the CPU analyzes
the values observed in the local memory and checks for the
canary value. On a server, these two programs can be run by
different users or in different Docker containers. On a mobile
device, these routines can be run in different apps. The apps
can be swapped in and out of focus to alternate reading and
writing. If the listener can reliably read the canary values, then
we say that the platform is vulnerable to LeftoverLocals.
Figure 5 shows a series of images on how the listener and
the writer interact, and how the listener may observe values
from the writer if local memory is not cleared.
5
Listening to LLM Responses
In this section, we provide an overview of how Leftover-
Locals can be exploited by a malicious actor (an attacker)
to listen to another user’s (the victim) LLM responses on a
multi-tenant GPU machine, followed by a detailed descrip-
tion of our proof-of-concept (PoC) attack.
At a high level, both actors are executed as co-resident
processes. The attack process implements the listener de-
scribed above, with the additional steps of comparing the
stolen values to various fingerprints. The victim process is
unknowingly the writer, where instead of canary values, the
values being written are sensitive components of an inter-
active LLM chat session. The attack ultimately follows two
steps, outlined in Fig. 6:
1. The attack process fingerprints the model that the
victim process is using by repeatedly dumping (i.e.,
stealing) the leftover local memory, which, in this
scenario, consists of sensitive components of linear al-
gebra operations used by the victim in the LLM model
architecture. This requires that the victim is using an
open-source model that the attacker can obtain.
2. The attacker then repeatedly dumps (i.e., steals) the
local memory again, specifically searching for the last,
i.e., output, layer in the LLM’s DNN, which can be
identified using weights or memory layout patterns
from the earlier fingerprinting.
Note that the output layer is a matrix-vector multiplication
with two inputs: the model weights, and the layer input—in
other words, the values derived from the user input that
propagated through the earlier levels of the deep neural
network (DNN). Given that the model weights of the output
layer are too large to comprehensively steal, an attacker
can inspect available open-source models to fully obtain the
weights through the exposed model fingerprint. We found
that the second input to the last layer (i.e., the layer input) is
subsequently small enough to fit into local memory. Thus,
the entire layer input can be stolen, and the attacker can
reproduce the final layer computation to uncover the final
result of the DNN.
We note that this is a fairly straightforward attack, and
with further creativity and ingenuity, a threat actor may be
able to construct further complex and sophisticated mali-
cious scenarios that may compromise ML applications in
more severe ways. Below we provide a detailed description
of the PoC, and the configuration and testing carried out
on various GPU platforms to uncover their susceptibility to
LeftoverLocals.
Our configuration. We outline our configuration in Tab. 2.
Our attack builds on the llama.cpp LLM due to its simplicity
and cross-vendor GPU acceleration support. In our example
we use a large discrete GPU that we found to be suscepti-
ble to LeftoverLocals: the AMD Radeon RX 7900 XT. We
configure llama.cpp to use OpenCL for GPU acceleration,
which uses the CLBLAST linear algebra library8. We use
the wizardLM-7B.ggmlv3.q5_0.bin model, which is open
source and can be obtained from Hugging Face9. This model
8https://github.com/CNugteren/CLBlast
9https://huggingface.co/TheBloke/wizardLM-7B-GGML/tree/main


Tyler Sorensen and Heidy Khlaaf
Local Memory
Local Memory
Compute Unit
Compute Unit
……..
Currently Executing Kernel
GPU
Writer Process
Listener Process
Global Memory
(a) Initial state of the GPU, where the writer process and the
listener process are co-resident, sharing one GPU device
……..
Currently Executing Kernel
Writer
Writer launches 
kernel
Local Memory
Local Memory
Compute Unit
Compute Unit
GPU
Writer Process
Listener Process
Global Memory
(b) The writer process launches it’s writer kernel, which becomes
the sole kernel that is executing on the GPU
…
ocal Memory
……..
Currently Executing Kernel
123
123
…
123
123
Writes canary values 
to local memory
Writer
Compute Unit
Compute Unit
GPU
Writer Process
Listener Process
Global Memory
(c) The writer kernel writes a canary value, in this case 123 to all
the local memory locations across all the compute units
……..
Canary values 
remain
Writer kernel 
finishes
…
123
123
…
123
123
Compute Unit
Compute Unit
Writer Process
Listener Process
Global Memory
Currently Executing Kernel
GPU
(d) The writer kernel finishes execution. In a system that is im-
pacted by LeftoverLocals, the canary values stay in local memory
……..
Currently Executing Kernel
Listener launches 
kernel
Listener
Compute Unit
Compute Unit
Writer Process
Listener Process
Global Memory
…
123
123
…
123
123
GPU
(e) The listener now gets a turn to execute its kernel, sololy occu-
pying the GPU
……..
Currently Executing Kernel
…
123
123
…
123
123
Local memory is 
copied to global 
memory
Listener
Compute Unit
Compute Unit
Writer Process
Listener Process
…
123
123
…
123
123
GPU
(f) The listener kernel copies all local memory on the GPU into
global memory
……..
Listener kernel 
finishes
…
123
123
…
123
123
Compute Unit
Compute Unit
Writer Process
Listener Process
…
123
123
…
123
123
GPU
Currently Executing Kernel
(g) The listener kernel finishes. At this point, global memory
(owned by the listener process) contains a dump of local memory
……..
Listener copies 
global memory 
region back to CPU 
to analyze
…
123
123
…
123
123
…
123
123
…
123
123
Compute Unit
Compute Unit
Writer Process
Listener Process
…
123
123
…
123
123
GPU
Currently Executing Kernel
(h) The listener can now copy global memory back to the CPU
and check for leaked data, e.g., canary values
Figure 5. A series of images illustrating how the listener and the writer interact, and how they can test for the LocalLeftover
vulnerability.


LeftoverLocals: Listening to LLM Responses Through Leaked GPU Local Memory
STEP 1: Fingerprint the model
STEP 2: Steal the LLM output
Steal local 
memory
Check against 
database of 
open-source 
models
Start
Steal local 
memory
Check against fingerprint 
of last DNN layer
Found 
match?
Perform last 
DNN layer 
computation 
using 
fingerprinted 
weights
Print token and listen 
for next token
Obtain 
open-source 
model
yes
no
Open-source 
model
yes
no
Found 
match?
Figure 6. A flow chart outlining the attack where a malicious listener (the attacker) steals the output of another process (the
victim) executing an interactive LLM application. These steps are exclusively followed by the attacker.
Table 2. The details of our PoC: code base and system
LLM code base
llama.cpp
Model
wizardLM-7B.ggmlv3.q5_0.bin
Layers
33
GPU backend
OpenCL
GPU BLAS Library
CLBLAST
GPU
AMD Radeon RX 7900 XT
Total local memory
5MB
was selected due to its reasonable size, which enabled rapid
prototyping and analysis; however, this attack is transferable
to many different models. In our threat model, we assume
that the victim is using the LLM in an interactive chat ses-
sion.
Modification. The attack requires an optimized GPU im-
plementation of matrix-vector multiplication. We found that
the current matrix-vector multiplication in llama.cpp (which
does not call into CLBLAST) is not implemented in an op-
timized idiomatic way. It stores partial dot product results
in local memory and then combines them at the end. While
there is a more complex approach using linear algebra to
achieve our same results, for the simplicity of our PoC and
demonstration, we replace the llama.cpp matrix-vector mul-
tiplication with our own that is more idiomatic (following
best GPU programming programming practices).
Step 1—Fingerprinting the model. An attacker can fin-
gerprint a model if it can listen to several inference queries
from the victim. In our configuration, the GPU contains
roughly 5MB of local memory. The model has roughly 33
layers, each of them consisting of a matrix multiplication
operation. Matrix multiplication is often optimized on GPUs
by using tiling: an approach that subdivides the matrices into
small matrices, performs the multiplication, and then com-
bines the results10. In many optimized libraries, including
CLBLAST, local memory is used to cache the smaller matri-
ces. Thus, for every layer, the attacker can steal 2.5MB of
weights, and 2.5MB of the inputs. While this is a significant
amount of data, we note that it is not enough to reconstruct
the entire computation. Many of these layers have weights
and inputs that are 100s of MB large.
However, for a whole inference computation (33 layers),
the attacker can steal around 80MB of the weights, which is
sufficient to fingerprint the model (assuming the user is us-
ing an open-source model, such as one that can be found on
Hugging Face). Given this, we assume that it is a straightfor-
ward task to fingerprint the model, and thus for the attacker
to obtain the full model being used by the victim.
Step 2—Listening to the LLM output. The attacker can
then turn their attention to the output layer of the DNN.
In our configuration, we found that the output layer is a
matrix-vector multiplication, rather than a matrix-matrix
multiplication. The weights matrix is large ( 128MB), but the
input vector is quite small ( 4KB). However, given that the
attacker has fingerprinted the model in step 1, the attacker
does not need to comprehensively steal the weights as they
are available from the fingerprinted model.
10https://cnugteren.github.io/tutorial/pages/page4.html


Tyler Sorensen and Heidy Khlaaf
Matrix-vector multiplication has a different GPU imple-
mentation than matrix-matrix multiplication. In the case
where the input vector fits in local memory, the most per-
formant implementation is often to cache the input vector
in local memory, as it is used repeatedly (i.e., for repeated
dot products). Because the input vector is stored entirely in
local memory, the attacker can steal this entire vector. In
determining whether the attacker has found local memory
from the output layer, we discovered that the attacker could
simply look for 4KB of floating point values with zeros on
either side. In our testing, this unique fingerprint was asso-
ciated with the output layer nearly every single time. For
different models and different GPUs, this fingerprint will
likely have to be recalibrated.
Putting it together. With an attacker in possession of
both the weights and the input vector to the final layer of the
DNN, they can perform the matrix-vector multiplication and
obtain the resulting token returned by the inference. This
allows the attacker to reproduce the output of the victim’s
LLM chat session with high fidelity, as demonstrated in the
introduction. In practice, we tuned the attacker to dump
the local memory very efficiently (that is, by using only a
small number of work-items and allocating only a small
amount of memory). This allows the attacker to listen to
long chat queries with only a small number of noticeable
output artifacts. Some of the artifacts observed include:
• Duplicate tokens: This occurs when the attacker steals
the same output layer twice due to circumstances such
as the attacker process being scheduled twice in a row,
thus the LLM was not scheduled to compute its next
token.
• Missing tokens: This occurs when the attacker kernel
isn’t scheduled at the right time, i.e., immediately after
the output layer computation kernel.
• Incorrect tokens This occurs due to the attacker mis-
identifying a stolen set of data to be the last layer. In
this case, it will print a junk token.
• Similar tokens These tokens are “close” to the original
output, even if they are not exact. That is, the attacker
may be unable to steal the exact token embedding
at the target layer. This results in a corrupted token
embedding which, when decoded, is semantically sim-
ilar (in the word2vec sense) to the original token. As
an example, in Fig. 1, the attacker extracts the incor-
rect word “Facebook”, which is semantically similar
to other Named Entities tokens (like “Google”, and
“Amazon”) in the generated text.
Despite these discrepant artifacts, the stolen text is more
than sufficient to uncover the LLM response. Additionally,
the attacker can be further tuned by, for example, having
multiple threads launch the listener kernel or by having a
more precise fingerprint of the last layer.
6
Testing GPU platforms for LeftoverLocals
Given the diversity of the GPU devices, we wrote several
applications to test for LeftoverLocals, provided in a variety
of GPU programming frameworks:
• Vulkan Command Line: A command line applica-
tion using Vulkan. The kernel is written in OpenCL
and compiled to SPIR-V using clspv11. It uses a simple
Vulkan wrapper called EasyVK12.
• OpenCL Command Line: A command line applica-
tion that uses the OpenCL framework.
• Apple App: An Apple app that can be deployed on
iOS or Mac OS. It targets the GPU using Apple’s Metal
framework.
• Android App: An Android app that uses Vulkan to
target mobile GPUs. The code uses Vulkan’s C API
(through EasyVK again) using JNI. The kernels are
the same as in the Vulkan command line app: they
are written in OpenCL and compiled to SPIR-V using
clspv.
Using the above programs, we tested 11 devices spanning
seven GPU vendors (and multiple GPU frameworks in some
cases). We observed LeftoverLocals on devices from three of
the vendors (Apple, Qualcomm, and AMD). The amount of
memory leaked depends on the size of the GPU. Larger GPUs
contain more physical memory, and thus, leak more data.
For the larger GPUs (e.g., an AMD Radeon RX 7900 XT), we
found that we can leak over 5MB per kernel. Table 3 shows
the system information in the cases where we were able able
to observe LeftoverLocals (QC refers to Qualcomm):
For some devices, specifically those from Arm, we were
not able to observe the canary value from the writer in the
listener, but we did observe non-zero data. Representatives
from Arm reviewed our observations and concluded that al-
though these values are not zero, they are not from a memory
leak. We outline these devices in Tab. 4.
Additionally, we tested some GPUs from NVIDIA, Intel,
and Imagination, outlined in Tab. 5 (IM refers to Immag-
ination). For these devices, we observed only zeros in lo-
cal memory, and thus did not observe LeftoverLocals. It is
unclear if all their devices are not impacted. For example,
although we did not observe the issue on our Imagination
device, Google notified us that they were able to observe it
on other Imagination devices.
We prepared a YouTube video that demonstrates the dif-
ferent interfaces and examples of LocalLeftovers—namely
the LLM PoC attack, covert communication channels, and
searching for canary values—on a few different platforms
using a few different applications13. All code is provided in
our github repository.
11https://github.com/google/clspv
12https://github.com/ucsc-chpl/easyvk
13https://www.youtube.com/watch?v=g2A7GvbnItg


LeftoverLocals: Listening to LLM Responses Through Leaked GPU Local Memory
Table 3. GPUs and systems that we observed to be impacted by LeftoverLocals. QC refers to Qualcomm.
Device (GPU)
Framework
OS/Driver/Build system
Apple iPhone 12 Pro (A14)
Metal
iOS 16.6, Xcode 14.3.1 (14E300c)
Apple iPad Air 3rd G (A12)
Metal
iOS 16.5.1, Xcode 14.3.1 (14E300c)
Apple MacBook Air (M2)
Metal
MacOS 13.4.1, Xcode 14.3.1 (14E300c)
AMD Radeon RX 7900 XT
Vulkan
Arch Linux, Mesa 23.1.4
AMD Radeon RX 7900 XT
OpenCL
Arch Linux, OpenCL 2.1 AMD-APP.dbg (3570.0)
AMD Ryzen 7 5700G (integrated GPU)
Vulkan
Arch Linux, Mesa 23.1.4
AMD RX 6700 XT
Vulkan
Windows 11 Pro 22H2, AMD Vulkan 2.0.270
HTC 1+ 11 (QC Snapdragon 8 g2)
Vulkan
Android 13, Android Studio (2022.3.1)
HTC 1+ 5T (QC Snapdragon 835)
Vulkan
Android 13, Android Studio (2022.3.1)
Table 4. GPUs and systems where the listener returned non–zero values, but we could not confirm that they came from
a different process. Arm representatives reviewed the results and confirmed that these values did not come from different
processes on their devices.
Device (GPU)
Framework
OS/Driver/Build system
Galaxy Tab A (Arm Mali G78)
Vulkan
Android 13, Android Studio (2022.3.1)
Google Pixel 6 (Arm Mali G71)
Vulkan
Android 11, Android Studio (2022.3.1)
Google Pixel 7 (Arm Mali G710)
Vulkan
Android 13, Android Studio (2022.3.1)
Table 5. GPUs and systems that we did NOT observe to be impacted by LeftoverLocals. However, later representatives from
Google notified us that they observed other devices from Imagination (IM) were impacted, and have subsequently been patched,
as documented in the paper introduction.
Device (GPU)
Framework
OS/Driver/Build system
Nvidia GeForce RTX 4070
Vulkan
Arch Linux, Mesa 23.1.4
Nvidia GeForce RTX 4070
OpenCL
Arch Linux, OpenCL 3.0 CUDA 12.2.128
Intel NUC (NUC10I5FNK)
Vulkan
Ubuntu 22.04, Mesa 20.3.2
Intel NUC (NUC10I5FNK)
OpenCL
Ubuntu 22.04, OpenCL 3.0 NEO (22.31.23852)
Motorola M.G (IM PowerVR GE8320)
Vulkan
Android 11, Android Studio (2022.3.1)
Vulnerable environments. An attack program must be
co-resident on the same machine and must be “listening”
at the same time that the victim is running a sensitive ap-
plication on the GPU. This could occur in many scenarios:
for example, if the attack program is co-resident with the
victim on a shared cloud computer with a GPU. On a mobile
device, the attack could be implemented in an app or a li-
brary. Listening can be implemented efficiently, and thus can
be done repeatedly and constantly with almost no obvious
performance degradation.
Next, we briefly discuss other environments where GPUs
are either deployed or where an attacker might have access to
sensitive information. Although it appears that some current
systems (e.g., WebGPU) are not currently impacted, the ever-
growing prevalence of ML and the diversity of modern GPUs
mean that the next iteration of these systems (or other near-
future systems) may be severely compromised by these types
of vulnerabilities.
• Cloud providers: Cloud providers (e.g., AWS and
Azure) are unlikely to provide shared GPU instances,
especially if users have dedicated access to the GPU
machine. In other cases, GPUs could be shared us-
ing very conservative GPU VM technology (such as
NVIDIA’s vGPU14 or AMD’s MxGPU15), which physi-
cally partitions the GPU and therefore prevents users
from sharing GPU resources (including local memory).
Given this, many current cloud GPU systems may not
currently be vulnerable to LeftoverLocals; however,
we do not have conclusive evidence to determine this
14https://docs.nvidia.com/grid/13.0/grid-vgpu-user-guide/index.html
15https://www.amd.com/system/files/documents/gpu-consistency-
security-whitepaper.pdf


Tyler Sorensen and Heidy Khlaaf
given the general lack of visibility into the specifica-
tion and implementation of these systems. We note
that we have observed LeftoverLocals on multi-user
Linux servers, as well as on desktop (Windows and
Mac) systems through traditional multi-processing.
This includes Docker containers on these systems.
• Mobile applications: In our experiments and explo-
rations in the mobile domain, we were able to run
concurrent GPU processes (from different apps on
iOS or Android) only in very specific instances. That
is, we were not able to run a GPU process (e.g., from a
malicious listener app) in the background while other
apps (e.g., the victim) were run in the foreground. As
with our analysis of cloud providers, we were unable
to find clear documentation that explicitly detailed
these constraints, and so we cannot definitively claim
whether they are vulnerable. However, as seen our
youtube video, LeftoverLocals can be exploited either
when a malicious listener app is run side-by-side with
a victim app, or if the malicious listener app is quickly
swapped from the background into the foreground
from a victim app.
• Remote attacks: We preliminarily investigated the
possibility of attacks originating from websites (e.g.,
those hosted by a remote attacker). To our knowledge,
web applications do not have the low-level features
required to listen to local memory using GPU graphics
frameworks, such as WebGL. We note that the new
WebGPU framework does provide low-level capabil-
ities that allow a webpage to access local memory.
Conservatively, WebGPU initializes and performs dy-
namic array bounds checking on local memory (and
global memory), which mitigates this vulnerability.
However, these checks cause significant overhead, as
documented in online discussions16. To test this fur-
ther, our code repo contains a simple listener in We-
bGPU. As expected, we have only observed zeros in
local memory, even on devices that are vulnerable to
LeftoverLocals through other frameworks. However,
GPU compilers are known to be fragile [3], and it is
not difficult to imagine finding a compiler bug that
could somehow bypass these checks (especially using
fuzzing techniques). Our position is that LocalLeft-
overs should be addressed at a lower level (e.g., the
driver).
How GPU vendors can resolve this vulnerability. To
defend against LocalLeftovers, GPUs should clear their lo-
cal memory between kernel calls. While this could cause
some performance overhead, our experiments show that
many GPU vendors (e.g., NVIDIA, Intel) currently appear
to provide this functionality. It even appears that some of
16https://github.com/gpuweb/gpuweb/issues/1202
this functionality is provided for impacted GPUs. For exam-
ple, Mesa drivers for AMD GPUs clears local memory after
a compute kernel launch17. However, this approach has a
fundamental flaw that makes it vulnerable to LeftoverLocals:
this memory wipe is done with a separate kernel, thus, the
GPU kernel queue may contain a malicious listener between
the computation kernel and the local memory wipe, allowing
the listener to steal memory. Instead, the computation kernel
and the local memory wipe need to occur atomically, i.e.,
without allowing any other kernel to be interleaved between
them. Otherwise, a user may attempt to preemptively defend
themselves against LeftoverLocals as described in the next
section.
Mitigations. Given the lack of comprehensive patches
across impacted GPU vendors, LeftoverLocals can be de-
fended by modifying the source code of all GPU kernels
that use local memory. As we’ve previously noted, before
the kernel ends, the GPU threads can store 0 to any local
memory locations that were used in the kernel. Given that
GPU tasks are typically interleaved at the kernel boundary,
this will prevent another user from being able to read left-
over values. We note that this mitigation may be difficult
for many users, especially because GPU code is often buried
deep in complex software stacks (e.g., for ML). Furthermore,
the GPU code may be part of a highly optimized library (e.g.,
ML linear algebra routines). In these cases, it is very difficult
to identify how local memory is used, and even more diffi-
cult to modify the kernel to zero it out. It may be possible to
augment a compiler to add this functionality, similar to how
WebGPU handles GPU memory accesses. These mitigations
do have a performance overhead that should be taken into
account. Another blunt mitigation involves simply avoiding
multi-tenant GPU environments.
7
Impact on LLMs and GPU platforms
LLM security. Our PoC attack examines only one applica-
tion: an interactive open-source LLM session. However, with
a little creativity, attackers could likely target many GPU
applications, including those used within privacy-sensitive
domains. Our motivation stems from the recent increased
use and support of open-source models, often accompanied
by claims that their “openness” inherently entails safety and
security through transparency. A recent article in Nature18
even alleges that only open-source generative AI models can
“safely” revolutionize health care, a safety-critical domain.
Yet, even if open-source models provide the opportunity to
be rigorously audited and assessed (which they have yet to
17https://github.com/Mesa3D/mesa/blob/
957009978ef6d7121fc0d710d03bc20097d4d46b/src/amd/vulkan/radv_
shader.c#L709
18https://www.nature.com/articles/d41586-023-03803-y


LeftoverLocals: Listening to LLM Responses Through Leaked GPU Local Memory
be19), their deployment still hinges on a closed-source stack
(i.e., GPUs). And as demonstrated by LeftoverLocals, open-
source LLMs are particularly susceptible to our vulnerability
given our ability to fingerprint these models to obtain remain-
ing weights as needed. Indeed, we have already observed
announcements regarding the deployment of open-source
models in collaboration with impacted GPU vendors, in-
cluding Hugging Face’s collaboration with AMD20, Lamini’s
deployment on AMD GPUs21, and the Qualcomm and Meta
partnership for edge devices 22.
Generally, the introduction of ML poses new attack sur-
faces that traditional threat models do not account for, and
that can lead to implicit and explicit access to data, model pa-
rameters, or resulting outputs, increasing the overall attack
surface of the system. It is crucial to identify and taxonomize
novel classes of failure modes that directly impact ML mod-
els, in addition to novel threats that can compromise the ML
Ops pipeline, as we have demonstrated with LeftoverLocals.
We discuss GPU-specific threat implications in the following
section.
GPU providers, applications, and vendors. While many
platforms are not currently impacted, we emphasize that the
GPU compute landscape is evolving rapidly. As some exam-
ples: there are a growing number of GPU cloud providers
have various policies and available configurations23; and
GPU programming frameworks, such as Vulkan and Metal,
are well-supported on mainstream platforms, and can be
used in apps without requiring extra privileges. While these
developments are exciting, they increase the threat potential
of GPU vulnerabilities, as LeftoverLocals illustrates. As far
as we are aware, there is no unified security specification
for how GPUs are required to handle sensitive data, and no
portable test suite to check if systems are vulnerable to sim-
ple memory leaks, like LeftoverLocals. Thus, GPU compute
environments should be rigorously scrutinized when used
for processing any type of sensitive data.
As mentioned throughout this paper, while we focus on
LLM applications, GPU local memory is one of the first tools
that a GPU developer uses when optimizing an application.
Although these attacks require analyzing the victim’s GPU
kernel code to identify local memory usage, it is likely possi-
ble to find similar application attacks in other GPU compute
domains, such as image processing and scientific computing.
It will be increasingly difficult for users to detect and defend
against these attacks since it’s unlikely they will know if
their application is vulnerable to LeftoverLocals; this would
19https://blog.trailofbits.com/2023/11/15/assessing-the-security-posture-
of-a-widely-used-vision-model-yolov7/
20https://twitter.com/AMD/status/1744831880241750112
21https://www.lamini.ai/blog/lamini-amd-paving-the-road-to-gpu-rich-
enterprise-llms
22https://www.qualcomm.com/news/releases/2023/07/qualcomm-works-
with-meta-to-enable-on-device-ai-applications-usi
23https://cloud-gpus.com/
require knowing the details of the exact GPU kernel code,
which are often hidden away in highly optimized linear al-
gebra libraries (e.g., CLBLAST). Additionally, an overall lack
of specification in up-and-coming GPU platforms makes it
difficult to determine whether the compiler or runtime will
use impacted memory regions without the user knowing. For
example, Apple GPUs have a new caching mechanism, called
dynamic caching24, which does not have a clear specification
regarding if local memory regions are being used for other
purposes.
8
Coordinated disclosure
Since September 2023, we have been working CERT/CC on
a large coordinated disclosure involving all major GPU ven-
dors, including NVIDIA, Apple, AMD, Arm, Intel, Qualcomm,
and Imagination. Trail of Bits provided vendors a total of 125
days to test their products and provide remediations. The
coordination gradually grew to include software stakehold-
ers, including Google, Microsoft, and others, which allowed
us to understand how LocalLeftovers impacts privacy re-
quirements and impact at different stages in the ML supply
chain. Apple did not respond or engage with us regarding
the disclosure until three days before the embargo ended.
A high-level timeline of the disclosure is provided below:
• September 8, 2023: Trail of Bits submitted report to
the CERT/CC
• September 11, 2023: CERT/CC acknowledged the sub-
mission of LeftoverLocals and began the process of
vendor outreach and CVE assignment with a prelimi-
nary disclosure date of December 11, 2023
• September 14, 2023: AMD acknowledged the CERT
disclosure
• September 15, 2023: Qualcomm acknowledged the
CERT disclosure
• September 22, 2023: The case report was shared with
the Khronos group, which produces the OpenCL and
Vulkan specifications and some corresponding infas-
tructure (such as conformance testing)
• September 29, 2023: NVIDIA acknowledged disclosure
and confirmed they were not affected by the vulnera-
bility
• November 22, 2023: ToB extended release of embargo
to January 16, 2024 to accommodate for vendor re-
quests for further time
• January 11, 2024: We received a notice that Qualcomm
provided a patch to their firmware that addresses
this issue only for some of their devices. Addition-
ally, Google noted that ChromeOS Stable 120 and LTS
114 will be released on January 16 to include AMD
and Qualcomm mitigations.
24https://www.digitaltrends.com/computing/apple-dynamic-caching-
explained/


Tyler Sorensen and Heidy Khlaaf
• January 13, 2024: Apple confirmed that the A17 and
M3 series processors contain fixes to the vulnerability.
• January 14, 2024: Google notified us that they ob-
served that that some Imagination GPUs are impacted.
• January 16, 2024: Embargo lift and public disclosure
of LeftoverLocals
9
Moving forward
Now that GPUs are being used in a wide range of applica-
tions, including privacy sensitive applications, we believe
that the wider GPU systems community (vendors, researchers,
developers) must work towards hardening the GPU system
stack and corresponding specifications. This should be ac-
complished through robust, holistic specifications that de-
scribe both GPU programs’ behavior and how GPU devices
integrate with the rest of the system stack (e.g., the OS or hy-
pervisor). Furthermore, these specifications should be rigor-
ously tested to account for the diversity of GPU systems and
safety requirements of diverse application domains. Looking
forward, a wide variety of new AI chips are being devel-
oped25 and will require rigorous security analysis.
There are positive developments in this direction. For
example, AMD’s ROCm stack26 is open, and thus available
for independent rigorous evaluation, and the Khronos Group
has safety critical specification groups27. Additionally, cross-
vendor programming frameworks, such as Vulkan, have been
incredibly useful for writing portable test suites, as opposed
to single-vendor programming frameworks.
While GPU security and privacy guarantees are scattered
and scarce, the Vulkan specification outlines a reasonable
definition of security for GPU platforms to adhere to—a
definition that several platforms clearly violate, as LocalLeft-
overs shows:28
...implementations must ensure that [...] an
application does not affect the integrity of the
operating system [...]. In particular, any guar-
antees made by an operating system about whether
memory from one process can be visible to an-
other process or not must not be violated by a
Vulkan implementation for any memory allo-
cation.
With the dust settling, our position is the following: given
the wide diversity of GPUs and their critical importance in
enabling machine learning applications, these devices, and
their ecosystems, are in need of (1) a detailed threat model
that considers the various types of data processed on GPUs
and how this data might be compromised; (2) an exploration
25https://www.theinformation.com/articles/the-twelve-startups-battling-
for-a-slice-of-nvidias-pie?utm_source=ti_app
26https://www.amd.com/en/products/software/rocm.html
27https://www.khronos.org/syclsc
28https://registry.khronos.org/vulkan/specs/1.3-extensions/html/vkspec.
html#fundamentals-validusage
of the GPU execution stack to determine where and how GPU
security properties should be specified and implemented; and
(3) significant testing and auditing to fortify GPU ecosystem,
which is the computational foundation of machine learning.
For full transparency, we note that Tyler Sorensen has been
an invited member of the Khronos group (sponsored by Google)
since 2019, and participates in the memory model technical
specification group.
Acknowledgements
We thank Dan Guido, Trent Brunson, Max Ammann, Do-
minik Czarnota, Kelly Kaoudis, Jay Little, and Adelin Travers
for their insightful comments and feedback on the vulnera-
bility, PoC, and throughout the disclosure process. We also
thank the Khronos Group for discussing technical specifi-
cation details with us, and providing an avenue for us to
engage with many vendors. We thank CERT/CC, specifically
Vijay Sarvepalli and Ben Koo, for organizing the coordinated
disclosure, especially considering the potential breadth of
the vulnerability. Finally, thank you to everyone who en-
gaged with us on this issue. This was a large project and we
had discussions with many people who provided valuable
insights and perspectives.
References
[1] Jade Alglave, Mark Batty, Alastair F. Donaldson, Ganesh Gopalakrish-
nan, Jeroen Ketema, Daniel Poetzl, Tyler Sorensen, and John Wickerson.
2015. GPU Concurrency: Weak Behaviours and Programming Assump-
tions. In Architectural Support for Programming Languages and Operat-
ing Systems (ASPLOS). ACM. https://doi.org/10.1145/2694344.2694391
[2] Sangho Lee, Youngsok Kim, Jangwoo Kim, and Jong Kim. 2014. Stealing
Webpages Rendered on Your Browser by Exploiting GPU Vulnerabilities.
In 2014 IEEE Symposium on Security and Privacy. https://doi.org/10.
1109/SP.2014.9
[3] Christopher Lidbury, Andrei Lascu, Nathan Chong, and Alastair F. Don-
aldson. 2015. Many-core compiler fuzzing. In Programming Language
Design and Implementation (PLDI ’15). ACM. https://doi.org/10.1145/
2737924.2737986
[4] Clémentine Maurice, Christoph Neumann, Olivier Heen, and Aurélien
Francillon. 2014. Confidentiality Issues on a GPU in a Virtualized
Environment. In Financial Cryptography and Data Security, Nicolas
Christin and Reihaneh Safavi-Naini (Eds.). Springer Berlin Heidelberg,
Berlin, Heidelberg.
[5] Sparsh Mittal, S. B. Abhinaya, Manish Reddy, and Irfan Ali. 2018. A Sur-
vey of Techniques for Improving Security of GPUs. CoRR abs/1804.00114
(2018). arXiv:1804.00114 http://arxiv.org/abs/1804.00114
[6] Roberto Di Pietro, Flavio Lombardi, and Antonio Villani. 2016. CUDA
Leaks: A Detailed Hack for CUDA and a (Partial) Fix. ACM Transactions
on Embedded Computing Systems 15, 1 (Jan. 2016), 1–25. https://doi.
org/10.1145/2801153
[7] Y. Wang, R. Paccagnella, Z. Gang, W. Vasquez, D. Kohlbrenner, H.
Shacham, and C. Fletcher. 2024. GPU.zip: On the Side-Channel Im-
plications of Hardware-Based Graphical Data Compression. In 2024
IEEE Symposium on Security and Privacy (SP). IEEE Computer Society,
84–84. https://doi.org/10.1109/SP54263.2024.00084
[8] Zhe Zhou, Wenrui Diao, Xiangyu Liu, Zhou Li, Kehuan Zhang, and Rui
Liu. 2016. Vulnerable GPU Memory Management: Towards Recovering
Raw Data from GPU. CoRR abs/1605.06610 (2016). arXiv:1605.06610
http://arxiv.org/abs/1605.06610
