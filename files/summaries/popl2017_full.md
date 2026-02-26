# Automatically Comparing Memory Consistency Models

**Authors:** J. Wickerson, M. Batty, T. Sorensen, G. Constantinides  
**Venue:** POPL, 2017  
**PDF:** [popl2017.pdf](../popl2017.pdf)

---

C
o
n
s
i
s
t
e
n
t
*
C
o
m
p
l
e
t
e
*
W
e
l
l
D
o
c
u
m
e
n
t
e
d
*
E
a
s
y
t
o
R
e
u
s
e
*
*
E
v
a
l
u
a
t
e
d
*
P
O
P
L
*
A
r
t
i
f
a
c
t
*
A
E
C
Automatically Comparing Memory Consistency Models
John Wickerson
Imperial College London, UK
j.wickerson@imperial.ac.uk
Mark Batty
University of Kent, UK
m.j.batty@kent.ac.uk
Tyler Sorensen
Imperial College London, UK
t.sorensen15@imperial.ac.uk
George A. Constantinides
Imperial College London, UK
g.constantinides@imperial.ac.uk
Abstract
A memory consistency model (MCM) is the part of a programming
language or computer architecture speciﬁcation that deﬁnes which
values can legally be read from shared memory locations. Because
MCMs take into account various optimisations employed by archi-
tectures and compilers, they are often complex and counterintu-
itive, which makes them challenging to design and to understand.
We identify four tasks involved in designing and understanding
MCMs: generating conformance tests, distinguishing two MCMs,
checking compiler optimisations, and checking compiler map-
pings. We show that all four tasks are instances of a general
constraint-satisfaction problem to which the solution is either a pro-
gram or a pair of programs. Although this problem is intractable for
automatic solvers when phrased over programs directly, we show
how to solve analogous constraints over program executions, and
then construct programs that satisfy the original constraints.
Our technique, which is implemented in the Alloy modelling
framework, is illustrated on several software- and architecture-level
MCMs, both axiomatically and operationally deﬁned. We automat-
ically recreate several known results, often in a simpler form, in-
cluding: distinctions between variants of the C11 MCM; a fail-
ure of the ‘SC-DRF guarantee’ in an early C11 draft; that x86 is
‘multi-copy atomic’ and Power is not; bugs in common C11 com-
piler optimisations; and bugs in a compiler mapping from OpenCL
to AMD-style GPUs. We also use our technique to develop and
validate a new MCM for NVIDIA GPUs that supports a natural
mapping from OpenCL.
Categories and Subject Descriptors
C.1.4 [Processor Archi-
tectures]: Parallel processors; D.3.4 [Programming Languages]:
Compilers; F.3.2 [Logics and Meanings of Programs]: Semantics
of Programming Languages
Keywords
C/C++, constraint solving, graphics processor (GPU),
model checking, OpenCL, program synthesis, shared memory con-
currency, weak memory models
[Copyright notice will appear here once ’preprint’ option is removed.]
1.
Introduction
In the speciﬁcation of a concurrent programming language or a par-
allel architecture, the memory consistency model (MCM) deﬁnes
which values can legally be read from shared memory locations [4].
MCMs have to be general enough to enable portability, but speciﬁc
enough to enable efﬁcient implementations. They must also admit
optimisations employed by architectures (such as store buffering
and instruction reordering [30]) and by compilers (such as com-
mon subexpression elimination and constant propagation [7]). This
profusion of design goals has led to MCMs for languages (such as
C11 [38] and OpenCL 2.0 [42]), for CPU architectures (such as
x86, ARM, and IBM Power), and for GPU architectures (such as
AMD and NVIDIA), that are complicated and counterintuitive. In
particular, all of these MCMs permit executions that are not sequen-
tially consistent (SC), which means that they do not correspond to
a simple interleaving of concurrent instructions [45]. As a result,
designing and reasoning about MCMs is extremely challenging.
Responding to this challenge, researchers have built numerous
automatic tools (see §8). These typically address the question of
whether a program P, executed under an MCM M , can reach the
ﬁnal state σ. Put another way: can the litmus test (P, σ) pass under
M ? While useful, there are several other questions whose answers
are valuable for MCM reasoning and development. Four that have
appeared frequently in the literature are:
Q1
Which programs can be run to test whether a compiler or
machine conforms to a given MCM? [11, 24]
Q2
Is one MCM more permissive than another? That is, is there
a litmus test that can pass under one but must fail under the
other? [11, 14, 43, 48, 50, 58, 63]
Q3
Can ‘strengthening’ a program (syntactically) ever enable ad-
ditional behaviours? For instance, can we take a litmus test that
must fail, impose additional sequencing or dependencies be-
tween its instructions (or, in the C11 case, give an atomic op-
eration a stronger ‘memory order’ [38 (§7.17.3)]), and thereby
allow it to pass? [21, 22, 55, 77, 79, 80]
Q4
Is a given software/architecture compiler mapping correct?
Or is there a litmus test that must fail under the software-
level MCM, but which, when compiled, can pass under the
architecture-level MCM? [15, 16, 46, 47, 81, 82]
1.1
Key Idea 1: Generalising the Question
Our ﬁrst key idea is the observation that all four of the questions
listed above can be answered, sometimes positively and sometimes
negatively, by exhibiting programs P and Q and state σ such that
the litmus test (P, σ) must fail under a given MCM M , P and Q
1
Compiled at 10:09 on November 8, 2016


(P, σ)
(Q, σ)
X /∈consistentM
X ′
Y ∈consistentN
Y ′
▷
▶
Figure 1. Diagram for explaining Key Idea 2
are related by a given binary relation ▶on programs, and (Q, σ)
can pass under a given MCM N . That is, each corresponds to
ﬁnding inhabitants of the following set.
Deﬁnition 1 (General problem). g(M , N , ▶)
def=
{(P, Q, σ) | σ /∈obsM (P) ∧P ▶Q ∧σ ∈obsN (Q)}
where obs returns the set of ﬁnal states that can be observed after
executing a given program under a given MCM.1
Our four questions correspond to the following specialisations
of g’s parameters:
Q1
g(M , 0, id) consists of tests that check conformance to M ,
where 0 is the MCM that allows all executions and id is the
identity relation;
Q2
g(M , N , id) consists of tests that cannot pass under M but
can under N ;
Q3
g(M , M , ‘is weaker than’) consists of monotonicity viola-
tions in M , given a relation that holds when one program is
(syntactically) ‘weaker than’ another; and
Q4
g(M , N , ‘compiles to’) consists of bugs in a compiler map-
ping from M to N , given a relation that holds when one pro-
gram ‘compiles to’ another.
1.2
Key Idea 2: Constraining Executions, not Programs
Having captured in Def. 1 our four questions, we now ask whether
answers can be generated using an automatic constraint solver. Un-
fortunately, Def. 1 is problematic because showing that a litmus
test must fail under M requires universal quantiﬁcation over exe-
cutions. That is, we must show that there exists a litmus test (P, σ)
such that all possible executions of P under M do not reach σ. As
Milicevic et al. observe, ‘this “∃∀” quantiﬁer pattern is a particu-
larly difﬁcult instance of higher-order quantiﬁcation’ [52], and our
pilot experiments conﬁrmed it to be intractable in practice.
Our second ‘key idea’, then, involves rephrasing the constraints
to be not over programs, but over program executions, where they
become much cheaper to solve (see Def. 2, below), and then to
recover litmus tests from these executions. We explain how this is
possible with reference to Fig. 1.
We start by ﬁnding individual executions X and Y , such that
X is inconsistent under M , Y is consistent under N , and X ▷Y .
From X , we construct a litmus test (P, σ) that can behave like X ,
and from Y , we construct a litmus test (Q, σ) that can behave like
Y . The ▷relation between X and Y ensures that these litmus tests
will have the same ﬁnal state σ and that P ▶Q. We now have a
litmus test that can fail under M and another that can pass under
N . But g requires a litmus test that must fail under M , and perhaps
(P, σ) can still pass by taking a different execution X ′. Example 1
illustrates how such a situation can arise.
Example 1. The diagram below (left) depicts a C11 execution.
Dotted rectangles group events into threads; W and R denote write
and read events; REL and ACQ denote atomic ‘release’ and ‘acquire’
1 Elements of g(M , N , ▶) can also be seen as counterexamples to ▶imply-
ing observational reﬁnement [33]: P ▶Q ⇏obsN (Q) ⊆obsM (P).
accesses; na denotes a non-atomic memory access; rf is the ‘reads
from’ relation; and sb means ‘sequenced before’. We extract a
litmus test from this executions (below right), by mapping write
events to store instructions, reads to loads, and having the ﬁnal state
enforce the desired rf relation.
a: Rna a 1
b: WREL x 1
c: RACQ x 1
d: Wna a 1
rf
rf
sb
sb
int a=0; atomic_int x=0;
r0=a; x.store(1,REL);
r1=x.load(ACQ); a=1;
r0==1 && r1==1
The execution is deemed inconsistent in C11. This is because the
successful release/acquire synchronisation implies that b ‘happens-
before’ c, hence that a happens-before d, and hence that it is
impossible for a to read from d. As a result, it is tempting to use
the litmus test derived from this execution for conformance testing
(Q1). In fact, the litmus test is not useful for this purpose because
it has a data race: the non-atomic store to a goes ahead even if
the release/acquire synchronisation on x fails. Racy C11 programs
have undeﬁned semantics, so non-conformance cannot be deduced
from the test passing.
To guard against situations like the one above, we require that
X is also ‘dead’. Semantically, X is dead if whenever X is incon-
sistent, and (P, σ) is a ‘minimal’ litmus test constructed from X ,
then no execution of P that leads to σ is allowed (which implies,
in particular, that P is race-free). This ensures that P not only can
fail, but must fail, as required. We obtain semantic deadness via
a syntactic approximation (deadM ), which simply involves a few
MCM-speciﬁc constraints on the shape of X . For instance, we re-
quire that whenever two non-atomic accesses are prevented from
racing by release/acquire synchronisation (as a and d are in Exam-
ple 1), one of the accesses must have a control dependency on the
acquire event. That is, if we add a control dependency edge from c
to d, then this execution would be in deadM . This ensures semantic
deadness because the resultant litmus test, now having if(r1==1)
a=1 rather than just a=1, is now race-free. It therefore becomes a
useful conformance test.
Formally, we reduce our general constaint-solving problem to
ﬁnding inhabitants of the following set.
Deﬁnition 2 (General problem over executions). ˜g(M , N , ▷)
def=
{(X , Y ) ∈X2 | X /∈consistentM ∧
X ∈deadM ∧X ▷Y ∧Y ∈consistentN }.
Analogies to our four speciﬁc problems, Q1–Q4, can be ob-
tained by specialising ˜g’s parameters like we did in §1.1.
We remark that deadness ensures the soundness of our solv-
ing strategy, but because we obtain semantic deadness via a syn-
tactic approximation, it may spoil its completeness. Nonetheless,
although our technique is incomplete, we demonstrate in the fol-
lowing subsection that it is useful.
1.3
Applications
We have implemented our technique in the Alloy modelling frame-
work [39]. An Alloy model comprises a set of classes plus a set of
constraints that relate objects and ﬁelds in those classes. If further
provided with upper bounds on the number of objects in each class,
Alloy can compile the constraints down to a SAT query, and then
invoke a SAT solver to search for a satisfying instance.
We have applied our technique to a range of MCMs, including
both software-level and architecture-level MCMs, both CPU and
GPU varieties, and both operationally-deﬁned and axiomatically-
deﬁned. Our results fall into two categories: automatic recreations
of results that have previously been manually generated, and new
results.
2
Compiled at 10:09 on November 8, 2016


Recreated results
We have rediscovered litmus tests that witness:
• the impact of three proposed changes to the C11 axioms (§4.1,
§4.2, §4.3) – and our distinguishing litmus tests are substan-
tially simpler than the originals in two cases;
• a violation of the supposedly guaranteed sequentially-consistent
semantics for data-race-free programs (the ‘SC-DRF guaran-
tee’ [5]) in a early draft of the C11 standard (§4.5) – similar to
that reported by Batty et al. [16];
• that x86 is ‘multi-copy atomic’ [23, 72] but Power is not (§4.4);
• the C11 MCM behaving non-monotonically, by allowing tests
to pass only if sequencing is added or a memory order is
strengthened (§5) – and in the second case, our litmus test is
simpler than that found manually by Vafeiadis et al. [77]; and
• two bugs in a published compiler mapping from OpenCL to
AMD-style GPUs [62] (§6.1) – one of which is substantially
simpler than the original found by Wickerson et al. [82].
New results
Our main new result (§6.2) concerns the map-
ping of OpenCL to PTX, an assembly-like language for NVIDIA
GPUs [61]. We ﬁrst use Q4 to show that a ‘natural’ OpenCL/PTX
compiler mapping is unsound for an existing formalisation of the
PTX MCM by Alglave et al. [9], but sound for a stronger PTX
MCM that we propose. We then use Q2 to generate litmus tests
that distinguish the two PTX MCMs, which we use to validate our
stronger MCM experimentally against actual NVIDIA GPUs.
In summary, we make the following contributions.
1. We show that four frequently-asked questions about MCMs can
be viewed as instances of one general formula (g, Def. 1).
2. We rephrase the formula to constrain executions rather than
litmus tests (˜g, Def. 2), so that it can be tractably explored using
a constraint-solving tool.
3. We implement our approach in Alloy, and use it to automati-
cally reproduce several results obtained manually in previous
work, often ﬁnding simpler examples.
4. We present a new, experimentally-validated MCM for PTX, and
an OpenCL/PTX compiler mapping, and use Alloy to validate
the mapping against the PTX MCM.
Our supplementary material [1] contains our Alloy models and
our PTX testing results.
2.
Executions
The semantics of a program is a set of executions. This section de-
scribes our formalisation of executions, both in general (§2.1) and
speciﬁcally for C11, OpenCL, and PTX (§2.2), and then explains
how MCMs decide which executions are allowed (§2.3).
Program executions are composed of events, each representing
the execution of a program instruction. Most existing MCM frame-
works embed several pieces of information within each event, such
as the location it accesses, the thread it belongs to, and the value it
reads and/or writes (e.g., [5, 11, 16, 55, 68]). In our work, events
are pure, in Needham’s sense [57]: they are given meaning sim-
ply by their membership of, for instance, the ‘read events’ set, or
the ‘same location’ relation. This formulation brings three beneﬁts.
First, it means that we can easily build a hierarchy of executions to
unify several levels of abstraction. For instance, starting with a top-
level ‘execution’ class, we can obtain a class of ‘C11 executions’
just by adding extra ﬁelds such as ‘the set of events with acquire se-
mantics’; we need not modify the type of events. Second, it means
that the same events can appear (with different meanings) in two
executions, thus reducing the total number of events needed in our
E
⊆E
all events in the execution
R, W
⊆E
events that read (resp. write) a location
F
⊆E
fence events
nal
⊆E
events that access a non-atomic location
sb
⊆E2
sequenced-before
ad, cd, dd ⊆E2
address/control/data dependency
sthd, sloc ⊆E2
same thread, same location
rf , co
⊆E2
reads-from, coherence order
rfe
⊆E2
def= rf −sthd
1 R ∪W ∪F ∪nal ⊆E
2 (R ∪W ) ̸∩F
3 sb ⊆sthd
4 strict-po(sb)
5 ad ⊆[R] ; sb ; [R ∪W ]
6 dd ⊆[R] ; sb ; [W ]
7 cd ⊆[R] ; sb
8 equiv(sthd, E)
9 equiv(sloc, R ∪W )
10 nal ; sloc = nal
11 rf ⊆(W × R) ∩sloc
12 rf ; rf −1 ⊆id
13 strict-po(co)
14 co ∪co−1 = (W −nal)2 ∩sloc −id
Figure 2. Basic executions, X
search space. Third, we avoid the need to deﬁne (and therefore, in
a bounded search query, set the number of) locations, threads, and
values.
Notation
Our MCMs are written in Alloy’s modelling language,
but in this paper we opt for more conventional set-theoretic nota-
tion. For a binary relation r, r is its complement, r −1 is its inverse,
r ? is its reﬂexive closure, r + is its transitive closure, and r ∗is its
reﬂexive, transitive closure. The strict-po predicate holds of bi-
nary relations that are acyclic and transitive, and equiv(r, s) holds
when r is a subset of s2, reﬂexive over s, symmetric, and transi-
tive. We compose an m-ary relation r1 with an n-ary relation r2
(where m, n ≥1) via r1 ; r2
def= {(x1, . . . , xm−1, z1, . . . , zn−1) |
∃y. (x1, . . . , xm−1, y) ∈r1 ∧(y, z1, . . . , zn−1) ∈r2}, and we lift
a set to a subset of the identity relation via [s]
def= {(e, e) | e ∈s}.
We write imm(r) for r −(r ; r +), and s1 ̸∩s2 for s1 ∩s2 = ∅.
2.1
Basic Executions
Let E be a set of events.
Deﬁnition 3 (Basic executions). The set X of basic executions
comprises structures with fourteen ﬁelds, governed by well-formed-
ness constraints (Fig. 2). We write fX for the ﬁeld f of execution X ,
omitting the subscript when it is clear from the context. The con-
straints can be understood as follows. The subsets R, W , F, and
nal are all drawn from the events E that appear in the execution
1 .
In particular, compound read-modify-write (RMW) events belong
to both R and W . Fences are distinct from reads and writes
2 .
Sequenced before is an intra-thread strict partial order
3
4 . (We
allow sb within a thread to be partial because in C-like languages,
the evaluation order of certain components, such as the operands of
the +-operator, is not speciﬁed.) Address dependencies are either
read-to-read or read-to-write
5 , data dependencies are read-to-
write
6 , and control dependencies originate from reads
7 . The
sthd relation forms an equivalence among all events
8 , while sloc
forms an equivalence among reads and writes
9 . We allow a dis-
tinction between ‘atomic’ and ‘non-atomic’ locations; MCMs that
do not make this distinction (such as architecture-level MCMs)
simply constrain the set of non-atomic locations to be empty. The
nal set consists only of complete sloc-classes 10. A relation rf is
a well-formed reads-from if it relates writes to reads at the same
location 11 and is injective 12. The inter-thread reads-from (rfe) is
derived from rf . A relation co is a well-formed coherence order
if when restricted to writes on a single atomic location it forms a
3
Compiled at 10:09 on November 8, 2016


A
⊆E
atomic events
acq, rel ⊆E
events that have acquire (resp. release) semantics
sc
⊆E
events that have SC semantics
15 acq ∪rel ∪sc ∪(R ∩W ) ∪F ⊆A ⊆E
16 R ∩sc ⊆acq ⊆R ∪F
17 W ∩sc ⊆rel ⊆W ∪F
18 F ∩sc ⊆acq ∩rel
19 R −A ⊆nal ⊆E −A
Figure 3. C11 executions, XC11 (extending X)
dv
⊆E
events that have whole-device scope
swg ⊆E2
same workgroup
20 sthd ⊆swg
21 equiv(swg, E)
22 dv ⊆A
Figure 4. OpenCL executions, XOpenCL (extending XC11)
strict total order; that is, it is acyclic and transitive 13, and it relates
every pair of distinct writes to the same atomic location 14.
Remark 4. We emphasise that elements of E have no intrinsic
structure, only identity. Nevertheless, when drawing executions,
we tag events with their type: R for elements of R −W , W for
elements of W −R, and C (for ‘compound’) for elements of R ∩
W . We indicate sthd equivalence classes with dotted rectangles,
and sloc equivalence classes using named representatives, e.g. x
and y. We also tag events with the values read/written, but this is
purely for readability.
Remark 5 (Initial writes). Like some prior MCM formalisa-
tions [50, 69], but unlike most (e.g. [10, 11, 16, 43]), our exe-
cutions exclude initial writes. We found that Alloy’s performance
degrades rapidly as the upper bound on |E| increases; by avoiding
initial writes, this bound can be lowered. Removing initial writes
makes rf −1 a partial function, which complicates the deﬁnition of
from-read, as described below.
Deﬁnition 6. From-read relates each read to all of the writes that
are co-later than the write that the read observed [6]:
fr
def= ((rf −1 ; co) ∪frinit) −id
where frinit
def= ([R] −(rf −1 ; rf )) ; sloc ; [W ]. In the absence of
initial writes, frinit handles reads that observe the initial value.
2.2
Language-Speciﬁc Executions
We can obtain executions for various languages as subclasses of X.
Deﬁnition 7 (C11 executions). C11 executions (XC11) are struc-
tures that inherit all the ﬁelds and well-formedness conditions from
basic executions, and add those listed in Fig. 3. The new ﬁelds orig-
inate from the ‘memory orders’ that are attached to atomic oper-
ations in C11 [38 (§7.17.3)]. Acquire events, release events, SC
events, RMWs, and fences are all atomic 15. Atomic events that are
neither acquires nor releases correspond to C11’s ‘relaxed’ mem-
ory order. Acquire semantics is given to all SC reads and only reads
and fences 16. Release semantics is given to all SC writes and only
writes and fences 17. SC fences have both acquire and release se-
mantics
18. Non-atomic reads access only non-atomic locations,
and atomic operations never access non-atomic locations 19.
Deﬁnition 8 (OpenCL executions). OpenCL [42] extends C11
with hierarchical models of execution and memory that reﬂect the
GPU architectures it was primarily designed to target. Accordingly,
OpenCL executions (XOpenCL, Fig. 4) extend C11 executions ﬁrst
by partitioning threads into one or more workgroups via the swg
equivalence 20
21, and second by allowing some atomic operations
to be tagged as ‘device scope’
22, which ensures they are visible
dv
⊆E
events that have whole-device scope
swg ⊆E2
same workgroup (‘co-operative thread array’)
23 sthd ⊆swg
24 equiv(swg, E)
25 dv ⊆F
26 nal = ∅
27 sthd −id ⊆sb ∪sb−1
28 R ̸∩W
Figure 5. PTX executions, XPTX (extending X)
throughout the device. Other atomics (i.e., with only ‘workgroup
scope’) can efﬁciently synchronise threads within a workgroup
but are unsuitable for inter-workgroup synchronisation. We do not
consider OpenCL’s local memory in this work, and we restrict our
attention to the single-device case.
Deﬁnition 9 (PTX executions). Like OpenCL executions, PTX
executions (XPTX, Fig. 5) gather threads into groups 23
24. Some
PTX fences (membar.gl) have whole-device scope 25, and others
(membar.cta) have only workgroup scope. There are no non-
atomic locations 26, sequencing is total within each thread 27, and
we do not consider RMWs 28.
Remark 10. When drawing C11 executions, we identify the sets
A, acq, rel and sc by tagging events in E −A with na, those in
A −acq −rel with RLX, those in acq −rel −sc with ACQ, those
in rel −acq −sc with REL, those in acq ∩rel −sc with AR, and
those in sc with SC. In OpenCL or PTX executions, we tag events
in A −dv with WG, and those in dv with DV.
2.3
Consistent, Race-Free, and Allowed Executions
Each MCM M deﬁnes sets consistentM and racefreeM of execu-
tions. (For architecture-level MCMs, which do not deﬁne races, the
latter contains all executions.) The sets work together to deﬁne the
executions allowed under M , as follows.
Deﬁnition 11 (Allowed executions). The executions of a program
P that are allowed under an MCM M are
JPKM
def=





JPK0 ∩consistentM
if JPK0 ∩consistentM ⊆racefreeM
⊤
otherwise
where ⊤stands for an appropriate universal set. Here, JPK0 is the
set of P’s candidate executions. These can be thought of as the
executions allowed under an MCM that imposes no constraints, and
are discussed separately (see Def. 16). The equation above says that
the allowed executions of P are its consistent candidates, unless a
consistent candidate is racy, in which case any execution is allowed.
(This is sometimes called ‘catch-ﬁre’ semantics [19].)
The consistency and race-freedom axioms for C11 and OpenCL
(minus ‘consume’ atomics) are deﬁned in Figure 6 and explained
below. We have included some recently-proposed simpliﬁcations.
In particular, the simpler release sequence (proposed by Vafeiadis
et al. [77]) makes deadness easier to deﬁne (§3.4), and omitting the
total order ‘S’ over SC events (as proposed by Batty et al. [14])
avoids having to iterate over all total orders when showing an
execution to be inconsistent.
Happens before (hb) edges are created by sequencing and by
a release synchronising with (sw) an acquire in a different thread.
Synchronisation begins with a release write (or a release fence that
precedes an atomic write) and ends with an acquire read (or an
acquire fence that follows an atomic read) and the read observes
either that write or a member of the write’s release sequence (rs).
An event’s release sequence comprises all the writes to the same
location that are sequenced after the event, as well as the RMWs
(which may be in another thread) that can be reached from one
of those writes via a chain of rf edges [77 (§4.3)]. In OpenCL,
4
Compiled at 10:09 on November 8, 2016


consistentC11
29 acyclic((hb ∩sloc) ∪rf ∪co ∪fr)
30 rf ; [nal] ⊆imm([W ] ; (hb ∩sloc))
31 acyclic((Fsb? ; (co ∪fr ∪hb) ; sbF ?) ∩sc2 ∩incl )
racefreeC11
32 cnf −A2 −sthd ⊆hb ∪hb−1
33 cnf ∩sthd ⊆sb ∪sb−1
34 cnf −incl ⊆hb ∪hb−1
Fsb
def= [F] ; sb
sbF
def= sb ; [F]
rs
def= (sb ∩sloc)∗; rf ∗
sw
def= [rel] ; Fsb? ; [W ∩A] ; rs ; rf ; [R ∩A] ; sbF ? ; [acq]
incl
def= dv 2 ∪swg
hb
def= ((sw
∩incl −sthd) ∪sb)+
cnf
def= ((W × W ) ∪(R × W ) ∪(W × R)) ∩sloc −id
Figure 6. The C11 and OpenCL MCMs
synchronisation only occurs between events with inclusive scopes
(incl), which means that if the events are in different workgroups
they must both be annotated with ‘device’ scope. Happens-before
edges between events accessing the same location, together with
rf , co, and fr edges, must not form cycles 29 [77 (§5.3)]. A read
of a non-atomic location must observe a write that is still visible
(vis) 30. The sequential consistency (SC) axiom 31 requires, essen-
tially, that the co, hb and fr edges between sc events do not form
cycles [14 (§3.2)] An execution has a data race unless every pair of
conﬂicting (cnf ) events in different threads, not both atomic, is in
hb
32. It has an unsequenced race unless every pair of conﬂicting
events in the same thread is in sb
33. An OpenCL execution has
a heterogeneous race [34] unless every pair of conﬂicting events
with non-inclusive scopes is in hb 34.
3.
Obtaining Litmus Tests
If we ﬁnd executions that solve ˜g (Def. 2), we need to ‘lift’ these
executions up to the level of programs in order to obtain a solution
to the original problem, g (Def. 1).
We begin this section by deﬁning a language for these generated
programs (§3.1). The language is designed to be sufﬁciently expres-
sive that for any discovered execution X , there exists a program
in the language that can behave like X . In particular, the program
must be able to create arbitrary sequencing patterns and dependen-
cies. Beyond this, we keep the language as small as possible to keep
code generation simple. The language is also generic, so that it can
be used to generate both assembly and high-level language tests.
We go on to deﬁne a function that obtains litmus tests from exe-
cutions (§3.2), and show that, under an additional assumption about
executions, the function is total (§3.3). We then deﬁne our deadness
constraint on executions (§3.4), and conclude with a discussion of
some of the practical aspects of generating litmus tests (§3.5).
3.1
Programming Language
The syntax of our generic programming language is deﬁned in
Fig. 7. We postulate a set V of values (containing zero), a set R of
registers, and a set L of (shared) locations, which is subdivided into
atomic (La) and non-atomic (Lna) locations. Every register and lo-
cation is implicitly initialised to zero. Let As denote a language of
expressions over a set s. Observe that since the only construction is
the addition of a register multiplied by zero, these expressions only
As ::= s | As + 0 × R
I ::= st(AL, AV) | ld(R, AL) | cas(AL, V, AV) | fe
C ::= Iℓ| C +ℓC | C ;ℓC | if ℓR = V then C
P ::= C ll . . . ll C
Figure 7. A programming language
evaluate to elements of s. We use them to create artiﬁcial dependen-
cies (i.e. syntactic but not semantic dependencies). The set I of in-
structions includes stores, loads, compare-and-swaps (CAS’s), and
fences. The cas(x, v, v ′) instruction compares x to v (and if the
comparison succeeds, sets x to v ′), returning the observed value of
x in either case. Observe that, artiﬁcial dependencies notwithstand-
ing, stores and CAS’s write only constant values to locations. Let
C denote a set of components, each formed from sequenced (;) or
unsequenced (+) composition, or one-armed conditionals that test
for a register having a constant value. We have no need for loops
because the executions we generate are ﬁnite. Each component has
a globally-unique label, ℓ. Let P be the set of programs, each a par-
allel composition of components. The top-level components in a
program are called threads.
Some languages attach extra information to instructions, such
as their atomicity and memory order (in C11), their memory scope
(in OpenCL), or whether they are ‘locked’ (in x86). Accordingly,
when using the generic language in Fig. 7 to represent one of these
languages, we introduce an additional function that stores extra
information for each instruction label.
We ensure that the programs we generate are well-formed – this
is necessary for ensuring that they provide valid solutions to g.
Deﬁnition 12 (Well-formed programs). A program is well-formed
if: (1) different stores/CAS’s to the same location store different
values, (2) each register is written at most once, (3) stores/CAS’s
never store zero, (4) if-statements never test for zero, and (5) when-
ever an if-statement tests register r, there is a load/CAS into r se-
quenced earlier in the same thread.
3.2
From Executions to Litmus Tests
Our strategy for solving g, as outlined in §1.2, is summarised by
the following ‘proof rule’:
Step 1:
(X , Y ) ∈˜g(M , N , ▷)
Step 2: (P, σ) ∈litmin(X )
(Q, σ′) ∈lit(Y ) σ = σ′
P ▶Q
Result:
(P, Q, σ) ∈g(M , N , ▶)
(1)
The purpose of this subsection is to deﬁne the lit and litmin func-
tions. We begin by deﬁning a more general constraint, lit′.
Deﬁnition 13.
The predicate lit′(X , P, σ, disabled, failures)
serves to connect executions X with litmus tests (P, σ). The
disabled argument is a subset of P’s components, which we in-
terpret as those that do not actually execute when creating the
execution X (because they are guarded by an if-statement whose
test failed). The failures argument is a subset of P’s CAS in-
structions, which we interpret as those that fail to carry out the
‘swap’ when creating execution X . (Characterising executions by
which instructions fail and which are disabled is only sensible
because of our restriction to loop-free programs.) The predicate
lit′(X , P, σ, disabled, failures) holds whenever there exists a bi-
jection µ between P’s enabled instructions and X ’s events such
that the following conditions all hold (in which we abbreviate µ(i)
as µi):
Conditionals
For an if-statement with condition ‘r = v’, the body
is enabled iff both the if-statement is enabled and σ(r) = v.
5
Compiled at 10:09 on November 8, 2016


Disabled loads
If a load/CAS into register r is disabled, then
σ(r) = 0.
Unguarded components
Any component not guarded by an if-
statement is enabled.
CAS failures
For every enabled CAS i in P: i is in failures iff
there is no j with (µj , µi) ∈rf that writes the value i expects.
Instruction types
For every enabled instruction i in P: i is a store
iff µi ∈W −R; i is a load or a failed CAS iff µi ∈R−W ; i is
a successful CAS iff µi ∈R ∩W ; and i is a fence iff µi ∈F.
Non-atomic locations
If i is an enabled non-fence instruction in
P then µi ∈nal iff i’s location is in Lna.
Threading, locations, and dependencies
For every enabled in-
structions i and j in P: (µi, µj ) ∈sthd iff i and j are in
the same thread in P; (µi, µj ) ∈sloc iff i and j both access
the same location; (µi, µj ) ∈cd iff there is an enabled if-
statement, say T, such that i is sequenced before T, i writes to
the register T tests, and j is in T’s body; (µi, µj ) ∈ad iff the
expression for j’s location depends (syntactically) on the reg-
ister written by i; and (µi, µj ) ∈dd iff j writes an expression
that depends (syntactically) on the register i writes.
Sequenced composition
For every enabled ;-operator in P: if i
and j are enabled instructions in the left and right operands
(respectively), then (µi, µj ) ∈sb.
Unsequenced composition
For every enabled +-operator in P: if
i and j are enabled instructions in the left and right operands
(respectively), then {(µi, µj ), (µj , µi)} ̸∩sb.
Final registers
For every enabled load/CAS j in P on location
x into register r: either (1) there exists an enabled store/CAS i
that writes v to x, (µi, µj ) ∈rf and σ(r) = v, or (2) σ(r) = 0
and µj is not in the range of rf .
Final locations
For every location x: either (1) there is an enabled
store/CAS i that writes v to x, µi has no successor in co, and
σ(x) = v, or (2) x is never written and σ(x) = 0.
Deﬁnition 14 (Obtaining litmus tests). Let lit(X ) be the set of
all litmus tests (P, σ) for which lit′(X , P, σ, disabled, failures)
holds for some instantiation of disabled and failures.
Deﬁnition 15 (Obtaining minimal litmus tests). Let litmin(X ) be
the set of all litmus tests (P, σ) for which lit′(X , P, σ, ∅, ∅) holds.
That is, when P behaves like X , all of its instructions are executed
and all of its CAS’s succeed. We say that the litmus test (P, σ) is
minimal for X , or, dually, X is a maximal execution of P.
Deﬁnition 16 (Candidate executions). We deﬁne P’s candidate
executions by inverting lit: JPK0
def= {X | ∃σ. (P, σ) ∈lit(X )}.
Deﬁnition 17 (Observable ﬁnal states). We can now formally de-
ﬁne the notion of observation we employed in Def. 1: obsM (P)
is the set of ﬁnal states σ for which (P, σ) ∈lit(X ) for some
X ∈JPKM .
3.3
Totality of litmin
We now explain why the litmin function is currently not total (that
is: there exist well-formed executions X for which litmin(X ) is
empty), and how we can impose an additional restriction on execu-
tions to make it become total.
The problem is: our programming language cannot express all
of the sequencing patterns that an execution can capture in a valid
sb relation. For instance, it is not possible to write a program that
generates exactly the following sb edges:
a
b
c
d
sb
sb sb
(2)
dead
35 domain(cd) ⊆range(rf )
36 imm(co);imm(co);imm(co−1) ⊆rf ?;(sb ;(rf −1)?)?
deadC11
37 dead
38 cnf ∩sthd ⊆sb ∪sb−1
39 pdr ⊆dhb ∪dhb−1 ∪(narf ; ssc) ∪(ssc ; narf −1)
pdr
def= cnf −A2
cde
def= (rfe ∪cd)∗;cd
drs
def= rs −([R];cde)
dsw
def= sw ∩(((Fsb? ; [rel] ; drs?) −(cd −1 ; cde)) ; rf )
dhb
def= sb? ;(dsw ;cd)∗
ssc
def= id ∩cde
narf
def= rf ∩nal 2 −hb
Figure 8. The dead constraint and its specialisation for C11
This is because, armed only with sequenced (‘;’) and unsequenced
(‘+’) composition (see Fig. 7), it is only possible to produce sb re-
lations that are in the set of series–parallel partial orders [53].2
Helpfully, series–parallel partial orders are characterised exactly
by a simple check: that they do not contain the ‘N’-shaped sub-
graph shown in (2) [78]. Accordingly, we impose one further well-
formedness constraint on executions:
∄a, b, c, d ∈E.
{(a, c), (a, d), (b, c)} ∈sb ∧{(a, b), (b, c), (c, d)} ̸∩sb?.
Our litmin function now becomes total (and hence lit too). In-
deed, it is straightforward to determinise the constraints listed in
Def. 13 into an algorithm for constructing litmus tests from execu-
tions (and we have implemented this algorithm, in Java).
3.4
Dead Executions
When searching for inconsistent executions, we restrict our search
to those that are also dead.
Deﬁnition 18 (Semantic deadness). The set of executions that are
(semantically) dead under MCM M is given by semdeadM
def=
{X ∈X | X /∈consistentM ⇒∀P, σ, X ′, σ′.
((P, σ) ∈litmin(X ) ∧(P, σ′) ∈lit(X ′) ∧X ′ ∈consistentM )
⇒(X ′ ∈racefreeM ∧σ′ ̸= σ)}.
That is, for any minimal litmus test (P, σ) for X , no consistent
candidate execution of P is racy or reaches σ. In other words:
(P, σ) must fail under M .
We employ syntactic approximations of semantic deadness. Fig-
ure 8 shows how this approximation is deﬁned for any architecture-
level MCM that enforces coherence (dead), and how it is strength-
ened to handle the C11 MCM (deadC11).
At the architecture level, we need not worry about races, so
ensuring deadness is straightforward. In what follows, let X be an
inconsistent execution, (P, σ) be a minimal litmus test of X , and
X ′ be another candidate execution of P. First, we require every
event that is the source of a control dependency to read from a non-
initial write 35. This ensures that P need not contain ‘if r = 0’.
Such programs are problematic because we cannot tell whether the
condition holds because r was set to zero or because r was never
assigned. Second, we require that every co edge (except the last) is
justiﬁed by an sb edge 36. This condition ensures that X ′ cannot be
made consistent simply by inverting one or more of X ’s co edges.
2 That said, if we extended our language to support fork/join parallelism,
then the execution in (2) would become possible: t1=fork(b); a;
t2=fork(c); join(t1); d; join(t2).
6
Compiled at 10:09 on November 8, 2016


The construction imm(co) obtains event pairs (e1, e2) that are
consecutive in co; composing this with ‘imm(co) ; imm(co−1)’
restricts our attention to those pairs for which it is possible to take
a further co step from e2. The last co edge does not need justifying
with an sb edge because it is directly observable in σ.
Example 2. The basic execution below (left) is inconsistent in any
MCM that imposes coherence (because co is contradicting sb), but
the litmus test obtained from it (below right) does not necessarily
fail because its ﬁnal state can be obtained via a consistent execution
that simply reverses the co edge from (b, a) to (a, b).
a: W x 2
b: W x 1
c: W x 3
d: R x 3
rf
sb
sb
co
co
int x=0;
x=2; x=1;
x=3; r0=x;
x==3 && r0==3
At the software level, we must also worry about races. First,
we forbid all unsequenced races 38, because if X does not have an
unsequenced race, then neither will X ′, because unsequenced races
are not affected by runtime synchronisation behaviour. Second,
condition
39 is concerned with potential data races (pdr): events
that conﬂict and are not both atomic. Although X is inconsistent
(which renders any races in X irrelevant) we worry that X ′ might
be consistent and racy. So, we require pdr-linked events to be also
in the dependable happens-before (dhb) relation, or to exhibit a
self-satisfying cycle (ssc), both of which we explain below.
Dependable happens-before
This is a restriction of ordinary
happens-before (hb). Essentially: if e1 and e2 are in dhb in X ,
and they map to instructions i1 and i2 respectively in P, then if i1
and i2 are represented by events in X ′, those events are guaranteed
to be related by happens-before.
Example 3. The execution below (left) has ﬁxed the shortcoming
in Example 1 by adding control dependencies, but it has introduced
the C11 release sequence as a further complexity.
a: Rna a 1
b: WREL x 1
c: WRLX x 2
d: RACQ x 2
e: Wna a 1
rf
rf
sb,cd
sb
co
sb,cd
int a=0; atomic_int x=0;
r0=a;
if(r0==1) x.store(1,REL);
x.store(2,RLX);
r1=x.load(ACQ);
if(r1==2) a=1;
r0==1 && r1==1
Although event d synchronises with b, it actually obtains its value
from c, in b’s release sequence. The execution is not semantically
dead because its litmus test (above right) is racy: if r0 is not
assigned 1, then the release store is not executed; this means that
r1 can read 2 without synchronisation having occurred; this leads
to a race on a. By subtracting (cd −1 ;cde) in the deﬁnition of dsw,
we ensure that whatever controls b also controls c, and this rules
out undesirable executions like the one above.
Moreover, the ([R] ; cde) in the deﬁnition of drs ensures that if
b is an RMW, it controls the execution of c. The effect is that c is
not executed if the CAS corresponding to the RMW fails.
Self-satisfying cycles
An event occurs in a self-satisfying cycle
(ssc) if it is connected to itself via a chain of cd and rf edges
that ends with a control dependency. The if-statements that create
these dependencies are constructed such that their bodies are only
executed if the desired rf edges are present (cf. Def. 13).
A potential race between e1 and e2 is deemed dead if both ac-
cess a non-atomic location, e1 is observed by e2 but does not hap-
pen before it, and e2 is in a self-satisfying cycle. The reasoning is as
follows. First, note that the execution is inconsistent, because reads
of non-atomic locations cannot observe writes that do not happen
before them (c.f. 30). Second, the self-satisfying cycle ensures that
e2 reads from e1 in every candidate execution that includes those
events. Therefore, every candidate execution is inconsistent and any
data races can be safely ignored. We illustrate this reasoning in the
following example.
Example 4. The execution below (left) is inconsistent because f
reads a non-atomic location from a write (a) that does not happen
before f . It is dead because f is in a self-satisfying cycle. Its litmus
test (below right) is not racy because the conditionals ensure that
the right-hand thread’s load of a is only executed if it obtains the
value 1, which means that it reads from the left-hand thread’s store
to a, which means that the execution is inconsistent and hence that
any races can be ignored.
a: Wna a 1
b: FRLX
c: RRLX y 1
d: WRLX x 1
e: RACQ x 1
f : Rna a 1
g: WRLX y 1
sb
sb
sb,cd
sb,cd
sb,cd
rf
rf
rf
int a=0; atomic_int x,y=0;
a=1; fence(RLX);
r0=y.load(RLX);
if(r0==1) x.store(1,RLX);
r1=x.load(ACQ);
if(r1==1) r2=a;
if(r2==1) y.store(1,RLX);
r0==1 && r1==1 && r2==1
Checking deadness
The constraints that deﬁne deadM are quite
subtle, particularly for complex MCMs like C11. Fortunately, we
can use Alloy to check that these constraints imply semantic dead-
ness, by seeking elements of deadM −semdeadM . That is: we
search for an execution X that is deemed dead, but which gives
rise to a litmus test (P, σ) that has, among its candidates, a consis-
tent execution X ′ that is either racy or reaches σ. We were able to
check that deadM ⊆semdeadM holds for all executions with no
more than 8 events; beyond this, Alloy timed out (after four hours).
Remark 19. We are using Alloy here to search all candidate exe-
cutions of a program, yet in §1.2 we argued that it is impractical to
phrase constraints over programs because to do so would necessi-
tate an expensive search over all candidate executions of a program.
We emphasise that this is not a contradiction. The formula to which
we objected had a problematic ∃∀pattern: ‘show that there exists
a program such that for all of its candidate executions, a certain
property holds’, whereas satisfying deadM −semdeadM requires
only existential quantiﬁcation.
3.5
Practical Considerations
We have found that Step 2 of our proof rule (1) can still be hard
for Alloy to solve, often leading to timeouts, particularly when X
and Y are large. The search space is constrained quite tightly by the
values of X and Y , but there are still many variables involved. One
of the degrees of ﬂexibility in choosing P and Q is in the handling
of if-statements. For instance, both
40 and
41 below give rise to
the same executions because of our well-formedness restrictions
on programs (Def. 12):
40 if b then (C1 ; C2)
41 (if b then C1) ; (if b then C2).
In response to these difﬁculties, we designed (and implemented
in Java) a deterministic algorithm for litmin (as mentioned in §3.3),
called LIT. In particular, it always chooses option 41 over option 40.
In practice, we ﬁnd it quicker to obtain (P, Q, σ) by constructing
(P, σ) = LIT(X ) and (Q, σ′) = LIT(Y ), rather than by solving
the four constraints in Step 2 of (1). This approach satisﬁes the third
constraint of Step 2 (σ = σ′) because all of the ▷relations that we
consider in this work ensure that X and Y have the same co and
rf edges and hence reach the same ﬁnal state. It does not, however,
guarantee P ▶Q. In particular, if a compiler mapping sends ‘A’
7
Compiled at 10:09 on November 8, 2016


to ‘B ; C’, then our algorithm would suggest, unrealistically, that
‘if b then A’ can compile to ‘(if b then B) ; (if b then C)’. In
our experience, the generated P’s and Q’s are sufﬁciently close to
being related by ▶that the discrepancy does not matter.
In fact, we do not even prove that (1) is guaranteed to provide a
valid solution to g, nor that a solution even necessarily exists. Such
a proof would be highly fragile, being dependent on intricacies
of the deadness constraint, which in turn depends on intricacies
of various MCMs, many of which may be revised in the future.
Instead, we follow the ‘lightweight, automatic’ approach extolled
elsewhere in this paper. Besides using Alloy to check the deﬁnition
of dead (as described in §3.4), we also implemented (in Java) a
basic MCM simulator to enumerate the candidate executions of
each litmus test we generate, to ensure that must-fail litmus tests
really must fail. We would have preferred to have used an existing
simulator like herd [12] or CppMem [16], but we found both tools
to be unsuitable because of restrictions they impose on litmus tests:
herd cannot handle sb being partial within a thread, and CppMem
cannot handle if-statements that test for particular values.
4.
Application: Comparing MCMs (Q2)
In this section, we use Alloy to generate litmus tests that distinguish
three proposed variants of the C11 MCM (§4.1, §4.2, §4.3). Such
distinguishing tests, particularly the simplest distinguishing tests,
are difﬁcult to ﬁnd by hand, but are very useful for illustrating
the proposed changes. We go on to check two generic properties
of MCMs – multi-copy atomicity (§4.4) and SC-DRF (§4.5) – by
encoding the properties as MCMs themselves and comparing them
against software- and architecture-level MCMs.
4.1
Strong Release/Acquire Semantics in C11
Lahav et al. have proposed a stronger semantics for release/acquire
atomics [43]. For the release/acquire fragment of C11 (no non-
atomics and no relaxed or SC atomics), their semantics amounts
to adding the axiom acyclic(sb ∪co ∪rf ). We used Alloy to
compare their MCM, which we call C11-SRA, to C11 over the
release/acquire fragment.
Lahav et al. provide a 10-event (and 4-location) execution that
distinguishes the MCMs [43 (Fig. 5)]. Alloy, on the other hand,
found a execution that requires just 6 events (and 2 locations) and
serves the same purpose.3
WREL x 1
WREL y 2
RACQ y 1
WREL y 1
WREL x 2
RACQ x 1
co
co
rf
rf
sb
sb
sb
sb
atomic_int x=0,y=0;
x.store(1,REL);
y.store(2,REL);
r0=y.load(ACQ);
y.store(1,REL);
x.store(2,REL);
r1=x.load(ACQ);
r0==1 && r1==1
4.2
Forbidding Reading/Synchronisation Cycles in C11
Nienhuis et al. [58 (Fig. 12)] have suggested strengthening the C11
MCM with the axiom acyclic(sw ∪rf ). Let us call that MCM C11-
SwRf. We used Alloy to search for litmus tests that could witness
such a change, and discovered a solution requiring 12 events and 6
3 Lahav et al. impose an additional technical requirement that postcondi-
tions should not need to refer to shared locations (only to registers), which
rules out the even-simpler ‘2+2W’ litmus test [67].
consistentMCA(ppo)
42 acyclic((sb ∩sloc) ∪co)
43 acyclic(wo(ppo))
wo(ppo)
def= (((rfe ; ppo ; rfe−1) −id) ; co) ∪(rfe ; ppo ; frinit)
Figure 9. Multi-copy atomicity as an MCM
threads
CRLX y 4/5
FREL
WRLX x 1
CREL y 2/3
WRLX y 4
CACQ x 1/2
CREL x 2/3
WSC x 4
CSC y 1/2
CREL x 4/5
FAR
WRLX y 1
sb
sb
sb
sb
sb
sb
co
co
co
rf
co
rf
co
rf
co
rf
co
rf
co
rf
that is virtually identical to the one provided by Nienhuis et al., if
a little less symmetrical. We sought smaller solutions, and found
none with fewer than 8 events that could distinguish C11-SwRf
from C11. For executions with 8 to 11 events, the SAT solver could
not return a result in a reasonable time.
4.3
Simplifying the SC Axioms in C11
Batty et al. have proposed a change to the C11 consistency axioms
that enables them to be simpliﬁed, and also avoids the need for a
total order, S, over all SC events [14]. Having already incorporated
their proposal in our Fig. 6, let us call the original MCM C11-Orig.
Batty et al. present a litmus test to distinguish C11 from C11-
Orig, which uses 7 instructions across 4 threads [14 (Example 1)].
Alloy, on the other hand, found one (below) that needs only 5
instructions and 3 threads.
WRLX x 1
CSC x 1/2
RSC y 0
WSC y 1
RSC x 1
S
S
sb
sb
S
co
rf
rf
atomic_int x=0,y=0;
x.store(1,RLX);
r0=x.cas(1,2,SC,RLX);
r1=y.load(SC);
y.store(1,SC);
r2=x.load(SC);
r0==true && r1==0 && r2==1
4.4
Multi-copy atomicity
The property of multi-copy atomicity4 (MCA) [23] ensures that, in
the absence of thread-local reordering, different threads cannot ob-
serve writes in conﬂicting orders – i.e., there is a single copy of
the memory that serialises all writes. The canonical MCA violation
is given by the IRIW test [19] (below) where thread-local reorder-
ing has been disabled by inducing ‘preserved program order’ (ppo)
edges, perhaps using dependencies or fences. That the ﬁnal reads
observe 0 betrays a disagreement in the order the writes occurred:
W y 1
R y 1
R x 0
R x 1
R y 0
W x 1
ppo
ppo
rf
rf
(3)
We formalise MCA – for the ﬁrst time in the axiomatic style – in
Fig. 9. The model comprises write/write coherence 42 [72] and the
acyclicity of the write order relation, wo
43. Write order captures
the intuition that if two reads, say r1 and r2 (with (r1, r2) ∈ppo),
observe two writes, say w1 and w2 respectively, then any write co-
later than w2 must follow w1 in the single copy of memory. The wo
relation is the union of two cases: in the ﬁrst, both reads observe
write events, and in the second, one reads from the initial value
4 This is also known as store atomicity [72] or write atomicity [4].
8
Compiled at 10:09 on November 8, 2016


consistentSC
44 acyclic(rf ∪co ∪fr ∪sb)
Figure 10. The SC MCM (following Shasha et al. [70])
strengthen(X , Y )
45 EX = EY
46 RX = RY
47 WX = WY
48 FX = FY
49 nal X = nal Y
50 sbX ⊆sbY
51 ad X ⊆ad Y
52 cd X ⊆cd Y
53 dd X ⊆dd Y
54 sthd X ⊆sthd Y
55 slocX = slocY
56 rf X = rf Y
57 coX = coY
Figure 11. ‘Strengthening’ an execution
(reusing our deﬁnition of frinit from Def. 6). Note that MCA is
parameterised by the given model’s ppo.5
With this formal deﬁnition of MCA, we can seek executions
allowed by a given MCM but disallowed by MCA. We tested x86
and Power, and as expected, Power does not guarantee MCA (Alloy
ﬁnds a counterexample similar to (3)) but x86 does.
4.5
Seeking SC-DRF Violations
We used Alloy to seek violations of the SC-DRF guarantee [5] in
an early draft of the C11 MCM [37]. The SC-DRF guarantee, in
the C11 context, states that if a program is race-free and contains
no non-SC atomic operations, then it has only SC semantics.
We sought an execution X that is dead (so that its corresponding
litmus test is race-free), uses no non-SC atomics, and is consistent
under the (draft) C11 MCM but inconsistent under SC:
AX ⊆scX ∧X ∈deadC11 ∩consistentC11-Draft −consistentSC
where the SC MCM is characterised in Fig. 10 and C11-Draft has
all the axioms listed by Batty et al. [14 (Def. 11)], minus their ‘S4’
axiom. Alloy found an example similar to that reported by Batty et
al. [16 (§4, Sequential consistency for SC atomics)]. The non-SC
execution is consistent under C11-Draft because no rule forbids
SC reads to observe initial writes. The ‘S4’ axiom was added [16
(§2.7)] to ﬁx exactly this issue.
5.
Application: Checking Monotonicity (Q3)
In this section, we rediscover two monotonicity violations in the
C11 MCM, whereby a new behaviour is enabled either by sequen-
tialisation (§5.1) or by strengthening a memory order (§5.2).
Checking monotonicity requires the relation deﬁned in Fig. 11,
which holds when one execution is ‘stronger’ than another. There is
almost an isomorphism between X and Y , except that Y may have
extra sb and dependency edges 50
51
52
53, and it may interleave
multiple threads together 54.
5.1
Monotonicity of C11 w.r.t. Sequencing
One way to extend the strengthen relation to the C11 setting is to
add the following constraints:
AX = AY
acqX = acqY
rel X = rel Y
scX = scY .
With this notion of strengthening, Alloy found a pair of 6-event
executions that witness a monotonicity violation in C11. They are
almost identical to those given by Vafeiadis et al. [77 (Fig. 1)],
5 We have an alternative formulation for happens-before-based models.
compile(π, X , Y )
58 [EX ] = π ; π−1
59 [EY ] ⊆π−1 ; π
60 π−1 ; sb?
X ; π = sb?
Y
61 ad X = π ; ad Y ; π−1
62 dd X = π ; dd Y ; π−1
63 cd X ; π = π ; cd Y
64 slocX = π ; slocY ; π−1
65 π−1 ; sthd X ; π = sthd Y
66 rf X = π ; rf Y ; π−1
67 coX = π ; coY ; π−1
Figure 12. Compiling an execution
though slightly less elegant: Alloy chose one of the writes to be
SC when a relaxed write would have sufﬁced.
5.2
Monotonicity of C11 w.r.t. Memory Orders
Another way to extend the strengthen relation is to add
AX = AY
acqX ⊆acqY
rel X ⊆rel Y
scX ⊆scY
sbX = sbY
ad X = ad Y
cd X = cd Y
dd X = dd Y
sthd X = sthd Y
which allows memory orders to be strengthened but forbids changes
to sequencing or threading. Using this notion of strengthening, Al-
loy found a 7-event monotonicity violation in C11: the execution
previously given in Example 4. That execution is inconsistent, but
if the relaxed fence is strengthened to a release fence, it becomes
consistent. This example is similar to one due to Vafeiadis et al. [77
(§3, Strengthening is Unsound)], but it is simpler: where theirs re-
quires 8 events, 4 locations, and 3 threads, our Alloy-generated
example requires only 7 events, 3 locations, and 2 threads.
6. Application: Checking Compiler Mappings (Q4)
We now report on our use of Alloy to investigate OpenCL compiler
mappings for AMD-style GPUs (§6.1) and NVIDIA GPUs (§6.2),
and a C11 compiler mapping for Power (§6.3).
Checking compiler mappings requires a relation that holds
when one execution ‘compiles’ to another. Of course, real com-
pilers do not compile on a ‘per-execution’ level, but from a pair of
executions related in this way, we can obtain a pair of programs that
are related by the compiler mapping at the level of program code.
Compiler mappings are more complicated than the strengthenings
considered in §5, because they may introduce additional events,
such as fences. For this reason, we introduce an additional relation,
π, to connect each original event to its compiled event(s). (In §5, π
is the identity relation.)
We are able to handle ‘straight line’ mappings like C11/x86 [16],
OpenCL/AMD (§6.1) and OpenCL/PTX (§6.2). We can also han-
dle more complicated mappings like C11/Power [15, 66], which
includes RMWs and introduces control dependencies, but our ex-
amples are limited to the execution level, because at the code level,
C11 RMWs map to Power loops, which our loop-free output pro-
gramming language cannot express.
Execution X maps to execution Y if there exists a π for which
compile(π, X , Y ) holds, as deﬁned in Fig. 12. Here, π is an in-
jective, surjective, multivalued function from X ’s events to Y ’s
events 58
59, that preserves sequencing 60, dependencies 61
62
63,
locations 64, threads 65, the reads-from relation 66, and the coher-
ence order
67. The location-preservation and thread-preservation
constraints have different shapes because, for instance, when a
mapping sends source event e to a set {e′
i}i of target events, it
must ensure that one e′
i has e’s location (the other events will be
fences), but that every e′
i is in the same thread.
9
Compiled at 10:09 on November 8, 2016


a: CAR,WG x 0/1
b: WREL,DV,REM x 2
co
x 7→vd 2
x 7→L 0

InvA
x 7→vd 2
x 7→L 0


x 7→L 0

W x 2
x 7→vd 2
x 7→L 0


x 7→L 0

Flu

x 7→L 0


x 7→0

Lk x

x 7→L 0

x 7→vd 2
x 7→L 0

Uk x
x 7→vd 2
x 7→0


x 7→0

fet x
x 7→vc 0
x 7→0

x 7→vc 0
x 7→0

C x 0/1
x 7→vd 1
x 7→0

x 7→vd 2
x 7→0

ﬂu x
x 7→vc 2
x 7→2

x 7→vd 1
x 7→2

ﬂu x
x 7→vc 1
x 7→1

co
π
π
Figure 13. RMW atomicity bug in the OpenCL/AMD mapping
6.1
Compiling OpenCL to AMD-Style GPUs
Orr et al. [62] describe a compiler mapping from OpenCL to an
AMD-style GPU architecture. Actually, they support OpenCL ex-
tended with ‘remote-scope promotion’, in which a workgroup-
scoped event a can synchronise with an event b in a different work-
group if b is annotated as ‘remote’. Wickerson et al. [82] report on
two bugs in this scheme: a failure to implement message-passing,
and a failure of RMW atomicity.
We have formalised Orr et al.’s architecture-level MCM and
compiler mapping in Alloy [1], following the formalisation by
Wickerson et al., and then used Alloy to search for bugs – essen-
tially automating the task that Wickerson et al. conducted manu-
ally. The architecture-level MCM is operational, which means that
consistent executions are obtained constructively, not merely char-
acterised by axioms. This means that the MCM is more complex
to express in Alloy. Essentially, the MCM involves a single global
memory in which entries can be temporarily locked, several pro-
cessing elements partitioned into compute units, and a write-back
write-allocate cache per compute unit.
Fig. 13 depicts the RMW atomicity bug discovered by Alloy.
The top left of the ﬁgure shows a 2-event execution that is incon-
sistent (and dead) in OpenCL, and the right shows a corresponding
9-event execution that is observable on hardware. (Wickerson et
al.’s bug is similar, but requires an extra ‘fetch’ event.) All events
are grouped by thread (inner dotted rectangles) and by workgroup
(outer dotted rectangles). Events in the architecture-level execu-
tion are totally ordered (thick black arrows). We track the local and
global state before and after each event, writing
  σl
σg

for local state
σl and global state σg. The global state comprises global memory
entries, some of which are locked (L). The local state comprises
the compute unit’s cache entries, each either valid (v) or invalid
(i), and either clean (c) or dirty (d). The π edges show how the
software-level events are mapped to architecture-level events. The
RMW at workgroup scope (a) maps to a single RMW, while the re-
mote (REM) write to x (b) is implemented by ﬁrst ﬂushing all dirty
local cache entries (Flu), then doing the write (W), then invalidat-
ing all entries in all caches (InvA), all while preventing concurrent
access to x in the global memory (Lk, Uk). Architecture-level exe-
cutions also include the actions of the ‘environment’ fetching (fet)
and ﬂushing (ﬂu) entries to and from global memory, as well as
derived rf and co relations. The undesirable but observable execu-
tion, in which x = 1 in the ﬁnal state, arises because the mapping
fails to propagate x = 2 to the global memory before releasing the
lock on x. The ﬁx is to ﬂush immediately after the write.
To make Alloy’s search for OpenCL/AMD compiling bugs
tractable, we found it necessary to make several simpliﬁcations:
we deleted the QuickRelease buffers [29]; we allowed multiple lo-
cations to be fetched and ﬂushed in a single action (which reduces
consistentPTX1
68 acyclic((sb ∩sloc −R2) ∪rf ∪co ∪fr)
69 acyclic(hbwg)
70 acyclic(hbdv)
rmo
def= rfe ∪co ∪fr
fdv
def= sb ;[F ∩dv];sb
fany
def= sb ;[F];sb
hbwg
def= (rmo ∪fany) ∩swg
hbdv
def= rmo ∪fdv
Figure 14. The PTX1 MCM
71 store(na|RLX, s) ⇝st.cg
72 store(REL, s)
⇝Fs ; st.cg
73 store(SC, s)
⇝Fs ; st.cg ; Fs
74 load(na, s)
⇝ld.cg
75 load(RLX|ACQ, s) ⇝ld.cg ; Fs
76 load(SC, s)
⇝Fs ; ld.cg ; Fs
77 fence(s)
⇝Fs
where
FWG
def= membar.cta
FDV
def= membar.gl
Table 1. OpenCL/PTX compiler mapping, program code level
the total number of actions required); we hard-coded the system to
have exactly two workgroups with one thread each; and we max-
imised sharing between global and local memory entry objects.
These changes are not necessarily semantics-preserving, but any
bogus solutions found using the simpliﬁed MCM can be simply
tested manually against the full one.
6.2
Compiling OpenCL to PTX
In this subsection, we develop and check a compiler mapping from
OpenCL to PTX. First, using Q4, we show that a natural mapping is
invalid for an existing formalisation of the PTX MCM (PTX1) [9],
but valid for a stronger model that we develop (PTX2). Then, we
use Q2 to generate litmus tests that distinguish PTX2 from PTX1,
which we use to conﬁrm that our PTX2 remains empirically sound
for NVIDIA GPUs.
Figure 14 deﬁnes the PTX1 MCM. The model enforces co-
herence (but not between reads, à la Sparc RMO [8])
68, allows
any fence to restore SC within a workgroup 69, and allows device-
scoped fences to restore SC throughout the device
70. We omit
dependencies because they are difﬁcult to test: the PTX compiler
often removes our artiﬁcially-inserted dependencies.
Table 1 deﬁnes the OpenCL/PTX mapping we use. OpenCL
stores are mapped to PTX stores (st.cg)
71
72
73, and OpenCL
loads are mapped to PTX loads (ld.cg)
74
75, with fences
(membar) placed before and/or after the memory access depending
on whether the OpenCL instruction is non-atomic, relaxed, acquire,
release, or SC. PTX fences are required even for relaxed OpenCL
loads because PTX allows consecutive loads from the same address
to be re-ordered (see 68). The PTX fences are scoped to match the
scope s of the OpenCL instruction. In line with prior work on the
PTX MCM [9], we exclude RMWs, local memory, and multi-GPU
interactions.
Figure 15 shows how the code-level mappings in (the ﬁrst two
rows of) Tab. 1 are encoded at the execution level. OpenCL work-
groups correspond to PTX workgroups 79. An OpenCL write with-
out release semantics (e) maps to a single PTX write (e′)
80,
while an OpenCL workgroup-scoped release write (e) maps to
a workgroup-scoped fence (e′
1) sequenced before a PTX write
(e′
2) 81. The other rows are handled similarly.
We used Alloy to check this mapping against PTX1, and found
an execution that is disallowed by OpenCL (Fig. 16, top) but al-
lowed, after compilation, by PTX1 (Fig. 16, bottom). Note that
the outer dotted rectangles group threads by workgroup. The crux
10
Compiled at 10:09 on November 8, 2016


compileOpenCL/PTX(π, X , Y )
78 compile(π, X , Y )
79 swgX = π;swgY ;π−1
80 ∀e ∈WX −rel X .
∃e′ ∈WY .
{e};π = {e′}
81 ∀e ∈WX ∩rel X −scX −dv X .
∃e′
1 ∈FY −dv Y . ∃e′
2 ∈WY .
(e′
1, e′
2) ∈imm(sbY ) ∧
{e};π = {e′
1} ⊎{e′
2}
Figure 15. OpenCL/PTX mapping, execution level (excerpt)
a: WREL,DV x 1
b: RACQ,DV x 1
c: WREL,WG y 1
d: RACQ,WG y 1
e: RACQ,WG x 0
sb
sb,cd
rf
rf
a′: FDV
b′: W x 1
c′: R x 1
d ′: FDV
e′: FWG
f ′: W y 1
g′: R y 1
h′: FWG
i′: R x 0
j ′: FWG
sb
sb
sb
sb
sb
cd
sb
sb
rf
rf
π
π
π
π
π
Figure 16. A WRC bug in the OpenCL/PTX1 mapping
here is cumulative synchronisation across scopes [36 (§1.7.1)]. The
left thread synchronises at workgroup scope with the middle thread
(via a and b), which synchronises at device scope with the right
thread (via c and d). If PTX1 supported cumulative synchronisa-
tion across scopes, the left and right threads would now be syn-
chronised, and the execution above, in which e observes a stale y,
would be forbidden, just as it is in OpenCL.
We could ﬁx the mapping for PTX1 by upgrading all the PTX
fences in Tab. 1 to device scope. However, because widely-scoped
fences incur high performance overhead on NVIDIA GPUs [71],
we opt instead to strengthen PTX1 to support our mapping, by
enforcing cumulative synchronisation across scopes (obtaining
PTX2). This entails changing the deﬁnition of hbdv (Fig. 14) to
hbdv
def= rmo ∪(hb∗
wg ; fdv ; hb∗
wg)
so that device-scoped fences (fdv) can restore SC throughout the
device even if they are preceded or followed by workgroup-scoped
synchronisation (hbwg). After this change, Alloy ﬁnds no bugs in
our mapping with up to 5 software-level events. It times out (after
four hours) when checking larger executions.
It remains to show that PTX2 is sound w.r.t. empirical GPU
testing data. To do this, we use Q2 to ﬁnd litmus tests (P, σ) that
are allowed under PTX1 but disallowed under PTX2. We wish to
ﬁnd not just a single litmus test (as in §4), but as many as possible,
so we run Alloy iteratively, each time disallowing the execution
shape found previously, until it is unable to ﬁnd more. We then
check testing results (or if results do not exist for a given test, we
run new tests) to conﬁrm that (P, σ) cannot pass on actual GPUs.
Using this method, Alloy ﬁnds all 14 distinguishing 7-event
tests (e.g. WRC [50]), plus 12 of the distinguishing 8-event tests
(e.g. IRIW [19]) before timing out. We are able to query Alglave
et al.’s experimental results [9] for 22 of these 26 tests. The rest
are single-address tests (which arise because PTX does not guaran-
tee coherence in general). These we ran on an NVIDIA GTX Titan
using the GPU-litmus tool [9]. We found no behaviours that are al-
Task
|E| tenc/s
tsol/s
1 Q2 C11-SRA vs. C11 (§4.1)
6
0.7
0.6
G 
2 Q2 C11-SwRf vs. C11 (§4.2)
7
0.8
625
G 
3 Q2 C11-SwRf vs. C11 (§4.2)
12
2
214
P 
4 Q2 C11 vs. C11-Orig (§4.3)
5
0.4
0.3
G 
5 Q2 MCA vs. x86 (§4.4)
9
0.8
607
P 
6 Q2 MCA vs. Power (§4.4)
6
2
0.06 G 
7 Q2 SC vs. C11-Draft (§4.5)
4
0.4
0.04 G 
8 Q2 PTX2 vs. PTX1 (§6.2)
7
0.7
4
G 
9 Q3 C11 (sequencing) (§5.1)
5
0.5
163
M 
10 Q3 C11 (sequencing) (§5.1)
6
0.7
5
P 
11 Q3 C11 (mem. orders) (§5.2)
7
0.9
51
G 
12 Q4 C11 / x86
5 + 5
0.7 13029
P 
13 Q4 C11 / Power (§6.3)
6 + 8
8
91
P 
14 Q4 OpenCL / AMD (§6.1)
2 + 9
6
1355
G 
15 Q4 OpenCL / AMD (§6.1)
4 + 10
16
4743
P 
16 Q4 OpenCL / PTX1 (§6.2)
5 + 8
2
11
P 
17 Q4 OpenCL / PTX2 (§6.2) 5 + 15
4
9719
P 
Table 2. Summary of tasks. We record the number (|E|) of events
in the search space, the time taken (in seconds) to encode (tenc)
and then solve (tsol) the SAT query, whether the fastest solver was
MiniSat (M), Glucose (G), or Plingeling (P), and whether a solution
was found () or not (). For Q4 tasks, m + n means that E is
partitioned into m software-level and n architecture-level events.
lowed by PTX1, disallowed by PTX2, and empirically observable
on a GPU [1]. Thus, subject to the available testing data, strength-
ening PTX1 to PTX2 is sound, and thus the natural OpenCL/PTX
compiler mapping can be used.
6.3
Compiling C11 to Power
Work in progress by Lahav et al. [44] has uncovered a bug in the
C11/Power mapping previously thought to have been proven sound
by Batty et al. [15].6 Before becoming aware of their work, we
had used Alloy to verify the soundness of the mapping for up to
6 software-level events and up to 6 architecture-level events. In-
crementing these bounds any further resulted in intractable solving
times, which explains why the bug, which requires 6 software-level
events and 13 architecture-level events, had not previously been
found by Alloy. In order to recreate Lahav et al.’s result, we mod-
iﬁed the C11/Power mapping so as not to place fences at the start
or the end of a thread. Removing these redundant fences allows
the bug to be expressed using just 8 architecture-level events, and
found automatically by Alloy in a reasonable time (see Tab. 2 in the
next section).
7.
Performance Evaluation
In this section, we report on an empirical investigation of how our
design decisions affect Alloy’s SAT-solving performance.
Table 2 summarises the tasks on which we have evaluated our
technique. We used a machine with four 16-core 2.1 GHz AMD
Opteron processors and 128 GB of RAM.
7.1
Choice of SAT Solver
Figure 17 summarises the performance of three SAT solvers on
our tasks: Glucose (version 2.1) [13], MiniSat (version 2.2) [26],
and Plingeling [17]. Each bar shows the mean solve time over 4
runs, plus the minimum and maximum time.7 Plingeling is able
6 Concurrent work by Manerkar et al. [51] has shown the C11/ARMv7
mapping to be similarly ﬂawed.
7 A more thorough comparison of SAT solvers would control for the order
of clauses, which greatly inﬂuences performance [59].
11
Compiled at 10:09 on November 8, 2016


1
2
3
4
5
6
7
8
9 10 11 12 13 14 15 16 17
1
100
10000
4-hour timeout
Task:
Solve time /s
Figure 17. Comparing MiniSat ( ), Glucose ( ) and Plingeling ( )
2
3
4
5
6
∞
200
1000
5000
k:
Solve time /s
Figure 18. Performance of Task 13 with ﬁxpoints unrolled k times
to complete all tasks, whereas Glucose and MiniSat time out on
three and ﬁve of them respectively. On the tasks all three solvers
complete, MiniSat takes an average of 9 minutes, Glucose takes 8,
and Plingeling takes 6. Plingeling’s relatively high startup overhead
is evident on the quicker tasks.
7.2
Combined vs. Separate Event Sets
For Q4 tasks (§6), we can choose to draw software-level and
architecture-level events either from a single set E or from dis-
joint partitions Esw and Earch. The former approach is attractive
because it gives the user one fewer parameter to control, and it min-
imises the total number of events required to ﬁnd solutions because
a single element of E can represent both a software-level event and
an architecture-level event. However, as shown in Tab. 2, we choose
the latter approach. To see why, consider Task 17. To validate the
OpenCL/PTX mapping for OpenCL executions of up to 5 events,
we must consider PTX executions of up to 15 events (since each
OpenCL event can map to up to three PTX events). We found that
setting |Esw| = 5 and |Earch| = 15 led to a tractable constraint-
solving problem for Alloy, but that merely setting |E| = 15, which
involves fewer events in total but includes OpenCL executions with
more than 5 events, rendered the problem insoluble.
7.3
Recursive Deﬁnitions vs. Fixed Unrolling
Alglave et al.’s formalisation of the Power MCM in the .cat for-
mat involves several recursively-deﬁned relations, but Alloy does
not support deﬁnitions of the form ‘let rec r = f (r)’. Accord-
ingly, in our formalisation of the Power MCM [1], we expand the
recursive construction explicitly, by requiring the existence of an
r satisfying f (r) ⊆r and ∀r ′. f (r ′) ⊆r ′ ⇒r ⊆r ′. The lat-
ter constraint involves universal quantiﬁcation over relations and
hence requires the higher-order AlloyStar solver [52]. A ﬁrst-order
alternative is simply to unroll the recursive deﬁnitions a few times;
that is, to set r
def= f k(∅) for a ﬁxed k. We found, for the small
search scopes involved in our work, that k ≥2 is sufﬁcient for
avoiding false positives when checking a compiler mapping from
C11 (Task 13). Figure 18 shows that the proper ﬁxpoint construc-
tion (i.e., k = ∞) is much more expensive than a ﬁxed unrolling.
8.
Related Work
Existing tools for MCM reasoning typically take a concurrent pro-
gram as input, and produce all of the executions allowed under a
given MCM. Some rely on SAT solvers to discover executions [18,
25, 75, 83], while others enumerate them explicitly [10, 12, 16, 60,
67, 68]. Our work tackles, in a sense, the ‘inverse’ problem: we
start with executions that witness interesting MCM properties, and
go on to produce programs that can give rise to these executions.
Other works tackling Q1–Q4
Regarding Q1, Darbari et al. [24]
have automatically generated conformance tests for HSA [35]
from an Event-B speciﬁcation [2] of its MCM. Alglave et al.’s diy
tool [11] generates conformance tests for a range of MCMs based
on critical cycles [70]. We ﬁnd that our Alloy-based approach has
several advantages over diy when generating conformance tests.
First, we can straightforwardly handle custom MCM constructs
(e.g., C11 memory orders) while diy currently does not. Second,
we generate only tests needed for conformance, while diy gener-
ates many more. Third, diy can also miss some tests required to
distinguish two MCMs (such as the single-address tests we saw in
§6.2), if not guided carefully through user-supplied critical cycles.
Regarding Q2, there is a long history of unifying frameworks
for comparing MCMs [3, 23, 28, 31, 32, 70], and of manual proofs
that different formulations of the same MCM are equivalent [50,
63]. On the automation side, Mador-Haim et al. [48] have, like
ourselves, used a SAT solver as part of a tool for generating litmus
tests that distinguish MCMs. However, where we use the solver
to generate tests, they just use it to check the behaviour of pre-
generated tests. Given that generating all 6-instruction litmus tests
takes them ‘a few minutes’ (in 2010), we expect that their approach
of explicit enumeration would not scale to ﬁnd the 12-instruction
litmus tests that are sometimes necessary to distinguish MCMs
(see §4.2), and which Alloy is able to ﬁnd in just 4 minutes.
Prior work has proved (manually) the validity of compiler opti-
misations in non-SC MCMs [79, 80]. Since optimisations should
not introduce new behaviours, this problem is related to mono-
tonicity (Q3). On the automation side, the Traver tool [21] uses
an automated theorem prover to verify/falsify a given program
transformation against a non-SC MCM. Unlike our work, Traver
does not support multi-threaded optimisations such as linearisation.
Chakraborty et al. have built a tool [22] that automatically veri-
ﬁes that LLVM optimisations preserve C11 semantics. Like Traver,
their tool only checks speciﬁc instances of an optimisation, while
our approach is able to check optimisations themselves. Morisset
et al. [55] use random testing to validate optimisations (albeit those
not involving atomic operations) against the C11 MCM; Vafeiadis
et al. [77] then show (manually) that several of these optimisations
are invalid when atomic operations are involved. Our work, in turn,
shows how several of Vafeiadis et al.’s results can be recreated au-
tomatically, often in a simpler form (§5).
Regarding Q4, prior work has proved (manually) the correct-
ness of both compiler mappings [15, 16, 82] and full compilers [81]
in a non-SC context. These proofs all involve intensive manual
effort, in contrast to our lightweight automatic checking, though
our checking can of course only guarantee the absence of bugs
within Alloy’s search scope. On the automation side, Lustig et
al. have built tools for ﬁnding and verifying semantics-preserving
translations, but where we focus on language/architecture trans-
lation, they focus on architecture/microarchitecture [46] and ar-
chitecture/architecture [47] translation. Very recent work by Trip-
pel et al. [76] has produced a framework that can check lan-
guage/architecture mappings; this works by enumerating standard
litmus tests and then simulating each one against both the language-
level MCM and, after compilation, the architecture-level MCM.
Reﬂections on Alloy
Alloy is a mature, open-source, and widely-
used modelling application, and its trio of features – a modular and
object-oriented modelling language, an automatic constraint solver,
and a graphical visualiser – makes it ideal for MCM development.
12
Compiled at 10:09 on November 8, 2016


Although Tab. 2 shows several lengthy solving times, those ﬁgures
are obtained once the search space has been set as large as compu-
tational feasibility allows. Given smaller search spaces, as would
be appropriate during MCM prototyping, Alloy is suitable for in-
teractive use.
When does Alloy’s failure to distinguish two MCMs become a
proof that they are equivalent? Mador-Haim et al. [49] prove that
6 events are enough, but their result applies only to multi-copy
atomic, architecture-level MCMs (see §4.4). Momtahan [54] gives
a result for general Alloy models, but imposes strong restrictions
on quantiﬁers that our models do not meet.
Ivy [64] deﬁnes a relational modelling language similar to Al-
loy’s. Where Alloy ensures the decidability of instance-ﬁnding by
restricting to a ﬁnite search scope (which limits its usefulness for
veriﬁcation), Ivy instead restricts formulas to the form ∃¯x. ∀¯y. φ
(for quantiﬁer-free φ). If our models can be rephrased to ﬁt into
Ivy’s restricted language, there is the potential not just to ‘debug’
MCM properties, but to verify them. Another language related to
Alloy, Rosette [74], is used in very recent work by Bornholt et
al. [20] to solve the problem of synthesising a MCM from a set
of desired litmus test outcomes.
We ﬁnd that Alloy has several advantages over other frame-
works that have been used to reason about MCMs, such as Isabelle
(e.g., [16]), Lem [56] (e.g., [15]), Coq (e.g., [77]), and .cat [12]
(e.g., [14]). A key advantage is that the entire memory modelling
process can be conducted within Alloy: the Alloy modelling lan-
guage can express programming languages, compiler mappings,
MCMs, and properties to test, the Alloy Analyzer can discover so-
lutions, and the Alloy Visualizer can display solutions using them-
ing customised for the model at hand. Alglave et al.’s .cat frame-
work, like Alloy, allows MCM axioms to be expressed in the con-
cise propositional relation calculus [73], but Alloy also supports
the more powerful predicate calculus as a fallback. As such, Al-
loy is expressive enough to capture both axiomatic and operational
MCMs, while remaining sufﬁciently restrictive that fully-automatic
property checking is computationally tractable.
9.
Conclusion
By solving relational constraints between executions and then lift-
ing solutions to litmus tests, Alloy can generate conformance tests,
compare MCMs (against each other and against general properties
like SC-DRF and multi-copy atomicity), and check monotonicity
and compiler mappings. As such, we believe that Alloy should be-
come an essential component of the memory modeller’s toolbox.
Indeed, we are already working with two large processor vendors
to apply our technique to their recent and upcoming architectures
and languages. Other future work includes applying our technique
to more recent MCMs that are deﬁned in a non-axiomatic style [27,
40, 41, 65].
Although Alloy’s lightweight, automatic approach cannot give
the same universal assurance as fully mechanised theorems, we
have found it invaluable in practice, because even (and perhaps
especially) in the complex and counterintuitive world of non-SC
MCMs, Jackson’s maxim [39] holds true: Most bugs have small
counterexamples.
Acknowledgements
We thank Alastair Donaldson, Carsten Fuhs, Daniel Jackson, Luc
Maranget, and Matthew Parkinson for their valuable feedback.
We acknowledge the support of a Research Fellowship from the
Royal Academy of Engineering and the Lloyd’s Register Founda-
tion (Batty), a Research Chair from the Royal Academy of En-
gineering and Imagination Technologies (Constantinides), an EP-
SRC Impact Acceleration Award, EPSRC grants EP/I020357/1,
EP/K034448/1, and EP/K015168/1, and a gift from Intel Corpo-
ration.
References
[1] Supplementary material for this paper is available in the
ACM digital library, and in the following GitHub repository.
URL: https://johnwickerson.github.io/memalloy.
[2] Jean-Raymond Abrial, Michael Butler, Stefan Hallerstede,
Thai Son Hoang, Farhad Mehta, and Laurent Voisin. “Rodin:
an open toolset for modelling and reasoning in Event-B”. In:
Int. J. Softw. Tools Technol. Transfer 12 (2010).
[3] Sarita V. Adve. “Designing Memory Consistency Models For
Shared-Memory Multiprocessors”. PhD thesis. University of
Wisconsin-Madison, 1993.
[4] Sarita V. Adve and Kourosh Gharachorloo. “Shared memory
consistency models: A tutorial”. In: IEEE Computer 29.12
(1996).
[5] Sarita V. Adve and Mark D. Hill. “Weak Ordering - A New
Deﬁnition”. In: Int. Symp. on Computer Architecture (ISCA).
1990.
[6] Mustaque Ahamad, Rida A. Bazzi, Ranjit John, Prince Kohli,
and Gil Neiger. “The Power of Processor Consistency”. In:
ACM Symp. on Parallelism in Algorithms and Architectures
(SPAA). 1993.
[7] Alfred V. Aho, Monica S. Lam, Ravi Sethi, and Jeffrey D.
Ullman. Compilers: Principles, Techniques, & Tools. Second
edition. Addison-Wesley, 2006.
[8] Jade Alglave. “A formal hierarchy of weak memory models”.
In: Formal Methods in System Design 41 (2012).
[9] Jade Alglave, Mark Batty, Alastair F. Donaldson, Ganesh
Gopalakrishnan, Jeroen Ketema, Daniel Poetzl, Tyler Soren-
sen, and John Wickerson. “GPU concurrency: weak be-
haviours and programming assumptions”. In: Int. Conf. on
Architectural Support for Programming Languages and Op-
erating Systems (ASPLOS). 2015.
[10] Jade Alglave, Daniel Kroening, and Michael Tautschnig.
“Partial Orders for Efﬁcient Bounded Model Checking of
Concurrent Software”. In: Computer Aided Veriﬁcation (CAV).
2013.
[11] Jade Alglave, Luc Maranget, Susmit Sarkar, and Peter
Sewell. “Fences in Weak Memory Models”. In: Computer
Aided Veriﬁcation (CAV). 2010.
[12] Jade Alglave, Luc Maranget, and Michael Tautschnig. “Herd-
ing cats: modelling, simulation, testing, and data-mining for
weak memory”. In: ACM Trans. on Programming Languages
and Systems (TOPLAS) 36.2 (2014).
[13] Gilles Audemard and Laurent Simon. “Predicting Learnt
Clauses Quality in Modern SAT Solvers”. In: Int. Joint Conf.
on Artiﬁcial Intelligence (IJCAI). 2009.
[14] Mark Batty, Alastair F. Donaldson, and John Wickerson.
“Overhauling SC atomics in C11 and OpenCL”. In: ACM
Symp. on Principles of Programming Languages (POPL).
2016.
[15] Mark Batty, Kayvan Memarian, Scott Owens, Susmit Sarkar,
and Peter Sewell. “Clarifying and Compiling C/C++ Concur-
rency: from C++11 to POWER”. In: ACM Symp. on Princi-
ples of Programming Languages (POPL). 2012.
[16] Mark Batty, Scott Owens, Susmit Sarkar, Peter Sewell, and
Tjark Weber. “Mathematizing C++ Concurrency”. In: ACM
Symp. on Principles of Programming Languages (POPL).
2011.
13
Compiled at 10:09 on November 8, 2016


[17] Armin Biere. Lingeling, Plingeling, PicoSAT and PrecoSAT
at SAT Race 2010. Tech. rep. 10/1. Institute for Formal Mod-
els and Veriﬁcation, Johannes Kepler University, 2010.
[18] Jasmin Christian Blanchette, Tjark Weber, Mark Batty, Scott
Owens, and Susmit Sarkar. “Nitpicking C++ Concurrency”.
In: Int. Symp. on Principles and Practice of Declarative
Programming (PPDP). 2011.
[19] Hans-J. Boehm and Sarita V. Adve. “Foundations of the C++
Concurrency Memory Model”. In: ACM Conf. on Program-
ming Language Design and Implementation (PLDI). 2008.
[20] James Bornholt and Emina Torlak. Synthesizing Memory
Models from Litmus Tests. Tech. rep. UW-CSE-16-10-01.
University of Washington, 2016.
[21] Sebastian Burckhardt, Madanlal Musuvathi, and Vasu Singh.
“Verifying Local Transformations on Relaxed Memory Mod-
els”. In: Int. Conf. on Compiler Construction (CC). 2010.
[22] Soham Chakraborty and Viktor Vafeiadis. “Validating Opti-
mizations of Concurrent C/C++ Programs”. In: Int. Symp. on
Code Generation and Optimization (CGO). 2016.
[23] William W. Collier. Reasoning about Parallel Architectures.
Prentice Hall, 1992.
[24] Ashish Darbari, Iain Singleton, Michael Butler, and John
Colley. “Formal Modelling, Testing and Veriﬁcation of HSA
Memory Models using Event-B”. Draft. 2016. URL: http:
//arxiv.org/pdf/1605.04744v1.pdf.
[25] Brian Demsky and Patrick Lam. “SATCheck: SAT-Directed
Stateless Model Checking for SC and TSO”. In: ACM
Int. Conf. on Object-Oriented Programming, Systems, Lan-
guages, and Applications (OOPSLA). 2015.
[26] Niklas Eén and Niklas Sörensson. “An Extensible SAT-
solver”. In: Theory and Applications of Satisﬁability Testing
(SAT). 2003.
[27] Shaked Flur, Kathryn E. Gray, Christopher Pulte, Susmit
Sarkar, Ali Sezgin, Luc Maranget, Will Deacon, and Peter
Sewell. “Modelling the ARMv8 Architecture, Operationally:
Concurrency and ISA”. In: ACM Symp. on Principles of
Programming Languages (POPL). 2016.
[28] Kourosh Gharachorloo. “Memory Consistency Models for
Shared-Memory Multiprocessors”. PhD thesis. Stanford
University, 1995.
[29] Blake A. Hechtman, Shuai Che, Derek R. Hower, Yingying
Tian, Bradford M. Beckmann, Mark D. Hill, Steven K. Rein-
hardt, and David A. Wood. “QuickRelease: A Throughput-
oriented Approach to Release Consistency on GPUs”. In:
IEEE Int. Symp. on High Performance Computer Architec-
ture (HPCA). 2014.
[30] John L. Hennessy and David A. Patterson. Computer Ar-
chitecture: A Quantitative Approach. Fifth edition. Morgan
Kaufmann, 2012.
[31] Lisa Higham, LillAnne Jackson, and Jalal Kawash. “Specify-
ing Memory Consistency of Write Buffer Multiprocessors”.
In: ACM Trans. on Programming Languages and Systems
(TOPLAS) 25.1 (2007).
[32] Lisa Higham, Jalal Kawash, and Nathaly Verwaal. “Deﬁning
and Comparing Memory Consistency Models”. In: Int. Conf.
on Parallel and Distributed Computing Systems (PDCS).
1997.
[33] C. A. R. Hoare. “Proof of Correctness of Data Representa-
tions”. In: Acta Informatica 1 (1972).
[34] Derek R. Hower, Blake A. Hechtman, Bradford M. Beck-
mann, Benedict R. Gaster, Mark D. Hill, Steven K. Rein-
hardt, and David A. Wood. “Heterogeneous-race-free Mem-
ory Models”. In: Int. Conf. on Architectural Support for
Programming Languages and Operating Systems (ASPLOS).
2014.
[35] HSA Foundation. HSA Platform System Architecture Speciﬁ-
cation. Version 1.0, 2015. URL: http://www.hsafoundation.
com/standards/.
[36] IBM. Power ISA (Version 2.06B). 2010.
[37] ISO/IEC. Programming languages – C++. Draft N3092,
2010. URL: http://www.open-std.org/jtc1/sc22/
wg21/docs/papers/2010/n3092.pdf.
[38] ISO/IEC. Programming languages – C. International stan-
dard 9899:2011, 2011.
[39] Daniel Jackson. Software Abstractions – Logic, Language,
and Analysis. Revised edition. MIT Press, 2012.
[40] Alan Jeffrey and James Riely. “On Thin Air Reads: To-
wards an Event Structures Model of Relaxed Memory”. In:
ACM/IEEE Symp. on Logic in Computer Science (LICS).
2016.
[41] Jeehoon Kang, Chung-Kil Hur, Ori Lahav, Viktor Vafeiadis,
and Derek Dreyer. “A Promising Semantics for Relaxed-
Memory Concurrency”. In: ACM Symp. on Principles of Pro-
gramming Languages (POPL). 2017.
[42] Khronos Group. The OpenCL Speciﬁcation. Version 2.0,
2013. URL: https://www.khronos.org/registry/cl/.
[43] Ori Lahav, Nick Giannarakis, and Viktor Vafeiadis. “Taming
Release-Acquire Consistency”. In: ACM Symp. on Principles
of Programming Languages (POPL). 2016.
[44] Ori Lahav, Viktor Vafeiadis, Jeehoon Kang, Chung-Kil Hur,
and Derek Dreyer. Repairing Sequential Consistency in
C/C++11. Tech. rep. MPI-SWS-2016-011. MPI-SWS, 2016.
[45] Leslie Lamport. “How to Make a Multiprocessor Computer
That Correctly Executes Multiprocess Programs”. In: IEEE
Transactions on Computers C-28.9 (1979).
[46] Daniel Lustig, Michael Pellauer, and Margaret Martonosi.
“PipeCheck: Specifying and Verifying Microarchitectural
Enforcement of Memory Consistency Models”. In: Int.
Symp. on Microarchitecture (MICRO). 2014.
[47] Daniel Lustig, Caroline Trippel, Michael Pellauer, and Mar-
garet Martonosi. “ArMOR: Defending Against Memory
Consistency Model Mismatches in Heterogeneous Archi-
tectures”. In: Int. Symp. on Computer Architecture (ISCA).
2015.
[48] Sela Mador-Haim, Rajeev Alur, and Milo M. K. Martin.
“Generating Litmus Tests for Contrasting Memory Consis-
tency Models”. In: Computer Aided Veriﬁcation (CAV). 2010.
[49] Sela Mador-Haim, Rajeev Alur, and Milo M. K. Martin.
“Litmus Tests for Comparing Memory Consistency Models:
How Long Do They Need to Be?” In: Design Automation
Conference (DAC). 2011.
[50] Sela Mador-Haim, Luc Maranget, Susmit Sarkar, Kayvan
Memarian, Jade Alglave, Scott Owens, Rajeev Alur, Milo M.
K. Martin, Peter Sewell, and Derek Williams. “An Axiomatic
Memory Model for POWER Multiprocessors”. In: Computer
Aided Veriﬁcation (CAV). 2012.
[51] Yatin A. Manerkar, Caroline Trippel, Daniel Lustig, Michael
Pellauer, and Margaret Martonosi. “Counterexamples and
Proof Loophole for the C/C++ to POWER and ARMv7
Trailing-Sync Compiler Mappings”. 2016. URL: http://
arxiv.org/pdf/1611.01507v1.pdf.
[52] Aleksandar Milicevic, Joseph P. Near, Eunsuk Kang, and
Daniel Jackson. “Alloy*: A General-Purpose Higher-Order
Relational Constraint Solver”. In: Int. Conf. on Software En-
gineering (ICSE). 2015.
14
Compiled at 10:09 on November 8, 2016


[53] Rolf H. Möhring. “Computationally tractable classes of or-
dered sets”. In: Algorithms and Order. Ed. by Ivan Rival.
Springer, 1989.
[54] Lee Momtahan. “Towards a Small Model Theorem for Data
Independent Systems in Alloy”. In: Electronic Notes in The-
oretical Computer Science 128 (2005).
[55] Robin Morisset, Pankaj Pawan, and Francesco Zappa Nar-
delli. “Compiler Testing via a Theory of Sound Optimisa-
tions in the C11/C++11 Memory Model”. In: ACM Conf. on
Programming Language Design and Implementation (PLDI).
2013.
[56] Dominic P. Mulligan, Scott Owens, Kathryn E. Gray, Tom
Ridge, and Peter Sewell. “Lem: reusable engineering of real-
world semantics”. In: ACM Int. Conf. on Functional Pro-
gramming (ICFP). 2014.
[57] Roger M. Needham. “Names”. In: Distributed Systems. Ed.
by Sape Mullender. ACM Press, 1989.
[58] Kyndylan Nienhuis, Kayvan Memarian, and Peter Sewell.
“An Operational Semantics for C/C++11 Concurrency”. In:
ACM Int. Conf. on Object-Oriented Programming, Systems,
Languages, and Applications (OOPSLA). 2016.
[59] Mladen Nikoli´c. “Statistical Methodology for Comparison of
SAT Solvers”. In: Theory and Applications of Satisﬁability
Testing (SAT). 2010.
[60] Brian Norris and Brian Demsky. “CDSChecker: Checking
Concurrent Data Structures Written with C/C++ Atomics”.
In: ACM Int. Conf. on Object-Oriented Programming, Sys-
tems, Languages, and Applications (OOPSLA). 2013.
[61] NVIDIA. Parallel Thread Execution ISA, version 4.3. 2015.
URL: http://docs.nvidia.com/cuda/pdf/ptx_isa_
4.3.pdf.
[62] Marc S. Orr, Shuai Che, Ayse Yilmazer, Bradford M. Beck-
mann, Mark D. Hill, and David A. Wood. “Synchronization
Using Remote-Scope Promotion”. In: Int. Conf. on Architec-
tural Support for Programming Languages and Operating
Systems (ASPLOS). 2015.
[63] Scott Owens, Susmit Sarkar, and Peter Sewell. “A Better x86
Memory Model: x86-TSO”. In: Theorem Proving in Higher
Order Logics (TPHOLs). 2009.
[64] Oded Padon, Kenneth L. McMillan, Aurojit Panda, Mooly
Sagiv, and Sharon Shoham. “Ivy: Safety Veriﬁcation by In-
teractive Generalization”. In: ACM Conf. on Programming
Language Design and Implementation (PLDI). 2016.
[65] Jean Pichon-Pharabod and Peter Sewell. “A Concurrency Se-
mantics for Relaxed Atomics that Permits Optimisation and
Avoids Thin-Air Executions”. In: ACM Symp. on Principles
of Programming Languages (POPL). 2016.
[66] Susmit Sarkar, Kayvan Memarian, Scott Owens, Mark Batty,
Peter Sewell, Luc Maranget, Jade Alglave, and Derek Wil-
liams. “Synchronising C/C++ and POWER”. In: ACM Conf.
on Programming Language Design and Implementation
(PLDI). 2012.
[67] Susmit Sarkar, Peter Sewell, Jade Alglave, Luc Maranget,
and Derek Williams. “Understanding POWER Multiproces-
sors”. In: ACM Conf. on Programming Language Design and
Implementation (PLDI). 2011.
[68] Susmit Sarkar, Peter Sewell, Francesco Zappa Nardelli, Scott
Owens, Tom Ridge, Thomas Braibant, Magnus O. Myreen,
and Jade Alglave. “The Semantics of x86-CC Multiprocessor
Machine Code”. In: ACM Symp. on Principles of Program-
ming Languages (POPL). 2009.
[69] Ali Sezgin. “Formalization and Veriﬁcation of Shared Mem-
ory”. PhD thesis. University of Utah, 2004.
[70] Dennis Shasha and Marc Snir. “Efﬁcient and Correct Exe-
cution of Parallel Programs that Share Memory”. In: ACM
Trans. on Programming Languages and Systems (TOPLAS)
10.2 (1988).
[71] Tyler Sorensen and Alastair F. Donaldson. “Exposing Errors
Related to Weak Memory in GPU Applications”. In: ACM
Conf. on Programming Language Design and Implementa-
tion (PLDI). 2016.
[72] Daniel J. Sorin, Mark D. Hill, and David A. Wood. A Primer
on Memory Consistency and Cache Coherence. Ed. by Mark
D. Hill. Vol. 16. Synthesis Lectures on Computer Architec-
ture. Morgan & Claypool, 2011.
[73] Alfred Tarski. “On the Calculus of Relations”. In: Journal of
Symbolic Logic 6.3 (1941), pp. 73–89.
[74] Emina Torlak and Rastislav Bodik. “Growing Solver-Aided
Languages with Rosette”. In: Onward! 2013.
[75] Emina Torlak, Mandana Vaziri, and Julian Dolby. “Mem-
SAT: Checking Axiomatic Speciﬁcations of Memory Mod-
els”. In: ACM Conf. on Programming Language Design and
Implementation (PLDI). 2010.
[76] Caroline Trippel, Yatin A. Manerkar, Daniel Lustig, Michael
Pellauer, and Margaret Martonosi. “Exploring the Trisection
of Software, Hardware, and ISA in Memory Model Design”.
Draft. 2016. URL: http : / / arxiv . org / pdf / 1608 .
07547v1.pdf.
[77] Viktor Vafeiadis, Thibaut Balabonski, Soham Chakraborty,
Robin Morisset, and Francesco Zappa Nardelli. “Common
compiler optimisations are invalid in the C11 memory model
and what we can do about it”. In: ACM Symp. on Principles
of Programming Languages (POPL). 2015.
[78] Jacobo Valdes, Robert E. Tarjan, and Eugene L. Lawler. “The
recognition of Series Parallel digraphs”. In: ACM Symp. on
Theory of Computing (STOC). 1979.
[79] Jaroslav Ševˇcík. “Safe Optimisations for Shared-Memory
Concurrent Programs”. In: ACM Conf. on Programming Lan-
guage Design and Implementation (PLDI). 2011.
[80] Jaroslav Ševˇcík and David Aspinall. “On Validity of Program
Transformations in the Java Memory Model”. In: Europ.
Conf. on Object-Oriented Programming (ECOOP). 2008.
[81] Jaroslav Ševˇcík, Viktor Vafeiadis, Francesco Zappa Nardelli,
Suresh Jagannathan, and Peter Sewell. “Relaxed-Memory
Concurrency and Veriﬁed Compilation”. In: ACM Symp. on
Principles of Programming Languages (POPL). 2011.
[82] John Wickerson, Mark Batty, Alastair F. Donaldson, and
Bradford M. Beckmann. “Remote-scope promotion: clari-
ﬁed, rectiﬁed, and veriﬁed”. In: ACM Int. Conf. on Object-
Oriented Programming, Systems, Languages, and Applica-
tions (OOPSLA). 2015.
[83] Yue Yang, Ganesh Gopalakrishnan, Gary Lindstrom, and
Konrad Slind. “Nemos: A Framework for Axiomatic and
Executable Speciﬁcations of Memory Consistency Models”.
In: Int. Parallel and Distributed Processing Symp. (IPDPS).
2004.
15
Compiled at 10:09 on November 8, 2016
