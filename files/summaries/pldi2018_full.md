# The Semantics of Transactions and Weak Memory in x86, Power, ARM, and C++

**Authors:** N. Chong, T. Sorensen, J. Wickerson  
**Venue:** PLDI, 2018  
**PDF:** [pldi2018.pdf](../pldi2018.pdf)

---

The Semantics of Transactions and Weak Memory
in x86, Power, ARM, and C++
Nathan Chong
ARM Ltd., UK
Tyler Sorensen
Imperial College London, UK
John Wickerson
Imperial College London, UK
Abstract
Weak memory models provide a complex, system-centric se-
mantics for concurrent programs, while transactional mem-
ory (TM) provides a simpler, programmer-centric semantics.
Both have been studied in detail, but their combined seman-
tics is not well understood. This is problematic because such
widely-used architectures and languages as x86, Power, and
C++ all support TM, and all have weak memory models.
Our work aims to clarify the interplay between weak mem-
ory and TM by extending existing axiomatic weak memory
models (x86, Power, ARMv8, and C++) with new rules for
TM. Our formal models are backed by automated tooling that
enables (1) the synthesis of tests for validating our models
against existing implementations and (2) the model-checking
of TM-related transformations, such as lock elision and com-
piling C++ transactions to hardware. A key finding is that a
proposed TM extension to ARMv8 currently being consid-
ered within ARM Research is incompatible with lock elision
without sacrificing portability or performance.
CCS Concepts
• Theory of computation →Parallel
computing models; Program semantics;
Keywords
Shared Memory Concurrency, Weak Memory,
Transactional Memory, Program Synthesis
ACM Reference Format:
Nathan Chong, Tyler Sorensen, and John Wickerson. 2018. The Se-
mantics of Transactions and Weak Memory in x86, Power, ARM, and
C++. In Proceedings of 39th ACM SIGPLAN Conference on Program-
ming Language Design and Implementation (PLDI’18). ACM, New
York, NY, USA, 18 pages. https://doi.org/10.1145/3192366.3192373
1
Introduction
Transactional memory [28] (TM) is a concurrent program-
ming abstraction that promises scalable performance with-
out programmer pain. The programmer gathers instructions
into transactions, and the system guarantees that each ap-
pears to be performed entirely and instantaneously, or not
Permission to make digital or hard copies of part or all of this work for
personal or classroom use is granted without fee provided that copies are
not made or distributed for profit or commercial advantage and that copies
bear this notice and the full citation on the first page. Copyrights for third-
party components of this work must be honored. For all other uses, contact
the owner/author(s).
PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
© 2018 Copyright held by the owner/author(s).
ACM ISBN 978-1-4503-5698-5/18/06.
https://doi.org/10.1145/3192366.3192373
at all. To achieve this, a typical TM system tracks each trans-
action’s memory accesses, and if it detects a conflict (i.e.,
another thread concurrently accessing the same location, at
least one access being a write), resolves it by aborting the
transaction and rolling back its changes.
1.1
Motivating Example: Lock Elision in ARMv8
One important use-case of TM is lock elision [22, 46], in which
the lock/unlock methods of a mutex are skipped and the
critical region (CR) is instead executed speculatively inside
a transaction. If two CRs do not conflict, this method allows
them to be executed simultaneously, rather than serially. If
a conflict is detected, the transaction is rolled back and the
system resorts to acquiring the mutex as usual.
Lock elision may not apply to all CRs, so an implemen-
tation must ensure mutual exclusion between transactional
and non-transactional CRs. This is typically done by starting
each transactional CR with a read of the lock variable (and
self-aborting if it is taken) [31, §16.2.1]. If the mutex is sub-
sequently acquired by a non-transactional CR then the TM
system will detect a conflict on the lock variable and abort
the transactional CR.
Thus, reasoning about lock elision requires a concurrency
model that accounts for both modes, transactional and non-
transactional. In particular, systems with memory models
weaker than sequential consistency (SC) [39] must ensure
that the non-transactional lock/unlock methods synchronise
sufficiently with transactions to provide mutual exclusion.
In their seminal paper introducing lock elision, Rajwar and
Goodman argued that “correctness is guaranteed without any
dependence on memory ordering” [46, §9]. In fact, by draw-
ing on a decade of weak memory formalisations [5, 24, 45]
and by extending state-of-the-art tools [4, 40, 55], we show
it is straightforward to contradict this claim automatically.
Example 1.1 (Lock elision is unsound under ARMv8).
Consider the program below, in which two threads use
CRs to update a shared location x.
Initially: [X0] = x = 0
lock()
lock()
LDR W5,[X0]
x ←x + 2
MOV W7,#1
x ←1
ADD W5,W5,#2
STR W7,[X0]
STR W5,[X0]
unlock()
unlock()
Test: x = 2
1


PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
Nathan Chong, Tyler Sorensen, and John Wickerson
It must not terminate with x = 2, for this would violate
mutual exclusion. Now, let us instantiate the lock/unlock
calls with two possible implementations of those methods.
Initially: [X0] = x = 0, [X1] = m = 0
1 Loop:
atomically
update m
from 0
to 1
3 TXBEGIN
begin txn
LDAXR W2,[X1]
LDR W6,[X1] load m
and abort
if non-
zero
CBNZ W2,Loop
CBZ W6,L1
4 MOV W3,#1
TXABORT
STXR W4,W3,[X1]
L1:
CBNZ W4,Loop
MOV W7,#1
x ←1
2 LDR W5,[X0]
x ←x + 2
STR W7,[X0]
5 ADD W5,W5,#2
TXEND
end txn
STR W5,[X0]
STLR WZR,[X1]
m ←0
Test: x = 2
The left thread executes its CR non-transactionally, using
the recommended ARMv8 spinlock [7, K9.3], while the
right thread uses lock elision (with unofficial but represen-
tative TM instructions). This program can terminate with
x = 2, thus witnessing the unsoundness of lock elision, as
follows:
1 The left thread reads the lock variable m as 0 (free).
LDAXR indicates an acquire load, which means that
the read cannot be reordered with any later event in
program-order.
2 The left thread reads x as 0. This load can execute specu-
latively because ARMv8 does not require that the earlier
store-exclusive (STXR) completes first [45].
3 The right thread starts a transaction, sees the lock is
still free, updates x to 1, and commits its transaction.
4 The left thread updates m to 1 (taken). This is a store-
exclusive (STXR) [36], so it only succeeds if m has not
been updated since the last load-exclusive (LDAXR). It
does succeed, because the right thread only reads m.
5 Finally, the left thread updates x to 2, andm to 0. STLR is
a release store, which means that the update tom cannot
be reordered with any earlier event in program-order.
The crux of our counterexample is that a (non-transaction-
al) CR can start executing after the lock has been observed
to be free, but before it has actually been taken. Importantly,
this relaxation is safe if all CRs are mutex-protected (i.e.,
the spinlock in isolation is correct), since every lock acqui-
sition involves writing to the lock variable and at most one
store-exclusive can succeed. Rather, the counterexample only
arises when this relaxation is combined with any reasonable
TM extension to ARMv8. This includes a proposed extension
currently being considered within ARM Research.
Furthermore, there appears to be no easy fix. Re-implemen-
ting the spinlock by appending a DMB fence to the lock()
implementation would prevent the problematic reordering,
but would also inhibit compatibility with code that uses
the ARM-recommended spinlock, and may decrease perfor-
mance when lock elision is not in use. Otherwise, if software
portability is essential, transactional CRs could be made to
write to the lock variable (rather than just read it), but this
would induce serialisation, and thus nullify the potential
speedup from lock elision.
1.2
Our Work
In this paper, we use formalisation to tame the interaction
between TM and weak memory. Specifically, we propose
axiomatic models for how transactions behave in x86 [31],
Power [29], ARMv8 [7], and C++ [34]. As well as the lock
elision issue already explained, our formalisations revealed:
• an ambiguity in the specification of Power TM (§5.2),
• a bug in a register-transfer level (RTL) prototype imple-
mentation of ARMv8 TM (§6.2),
• a simplification to the C++ TM proposal (§7.2), and
• that coalescing transactions is unsound in Power (§8.1).
Although TM is conceptually simple, it is notoriously
challenging to implement correctly, as exemplified by In-
tel repeatedly having to disable TM in its processors due to
bugs [26, 30], IBM describing adding TM to Power as “ar-
guably the single-most invasive change ever made to IBM’s
RISC architecture” [1], and the C++ TM Study Group listing
“conflict with the C++ memory model and atomics” as one
of their hardest challenges [56]. To cope with the combined
complexity of transactions and weak memory that exist in
real systems, we build on several recent advances in auto-
mated tooling to help develop and validate our models. In
the x86 and Power cases, we use the SAT-based Memalloy
tool [55], extended with an exhaustive enumeration mode
à la Lustig et al. [40], to automatically synthesise exactly
the ‘minimally forbidden’ tests (up to a bounded size) that
distinguish our TM models from their respective non-TM
baselines. We then use the Litmus tool [4] to check that these
tests are never observed on existing hardware (i.e., that our
models are sound). We also generate a set of ‘maximally al-
lowed’ tests, which we use to assess the completeness of our
models (i.e., how many of the behaviours our models allow
are empirically observable).
Moreover, we investigate several properties of our mod-
els. For instance, C++ offers ‘atomic’ transactions and ‘re-
laxed’ transactions; we prove that atomic transactions are
strongly isolated, and that race-free programs with no non-
SC atomics and no relaxed transactions enjoy ‘transactional
SC’. Other properties of our models we verify up to a bound
using Memalloy; these are that introducing, enlarging, or
coalescing transactions introduces no new behaviours, and
that C++ transactions compile soundly to x86, Power, and
ARMv8.
Finally, we show how Memalloy can be used to check a
library implementation against its specification by encoding
it as a program transformation. We apply our technique to
check that x86 and Power lock elision libraries correctly
2


The Semantics of Transactions and Weak Memory
PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
implement mutual exclusion – but that this is not so, as we
have seen, in ARMv8.
Summary
Our contributions are as follows:
• a fully-automated toolflow for generating tests from
an axiomatic memory model and using them to vali-
date the model’s soundness, its completeness, and its
metatheoretical properties (§4);
• formalisations of TM in the SC (§3), x86 (§5), Power (§5),
ARMv8 (§6), and C++ (§7) memory models;
• proofs that the transactional C++ memory model guar-
antees strong isolation for atomic transactions, and trans-
actional SC for race-free programs with no non-SC atom-
ics or non-atomic transactions (§7);
• the automatic, bounded verification of transactional
monotonicity and compilation from C++ transactions
to hardware (§8); and
• a technique for validating lock elision against hardware
TM models, which is shown to be effective through the
discovery of the serious flaw of Example 1.1 (§8).
Companion Material
We provide all the models we pro-
pose (in the .cat format [5]), the automatically-generated
litmus tests used to validate our models, litmus tests corre-
sponding to all the executions discussed in our paper, and
Isabelle proofs of all statements marked with the
symbol.
2
Background: Axiomatic Memory Models
Here we give the necessary background on the formal frame-
work we use for reasoning about programs, which is standard
across several recent works [5, 40, 55].
A memory model defines how threads interact with shared
memory. An axiomatic memory model consists of constraints
(i.e., axioms) on candidate executions. An execution is a graph
representing a runtime behaviour, whose structure is defined
below. The candidate executions of a program are obtained
by assuming a non-deterministic memory system: each load
can observe a store from anywhere in the program. After
filtering away the candidates that fail the constraints, we are
left with the consistent executions; i.e., those that are allowed
in the presence of the actual memory system.
2.1
Executions
Let X be the set of all executions. Each execution is a graph
whose vertices, E, represent runtime memory-related events
and whose labelled edges represent various relations be-
tween them. The events are partitioned into R,W , and F, the
sets of read, write, and fence events.1 Events in an execution
are connected by the following relations:
• po, program order (a.k.a. sequenced-before);
1 We encode fences as events (rather than edges) because this simplifies
execution minimisation (§4.2). We then derive architecture-specific fence
relations that connect events separated by fence events, which we use in
our models and execution graphs.
a: W x
b: R x
c: W x
co
po
rf
Initially: [X0] = x = 0
a: [X0] ←1
c: [X0] ←2
b: r0 ←[X0]
Test: r0 = 2 ∧x = 2
Figure 1. An execution and its litmus test
• addr/ctrl/data, an address/control/data dependency;
• rmw, to indicate read-modify-write operations;
• sloc, between events that access the same location;
• rf , the ‘reads-from’ relation; and
• co, the ‘coherence’ order in which writes hit memory.
We restrict our attention to executions that are well-formed
as follows: po forms, for each thread, a strict total order over
that thread’s events; addr, ctrl, and data are within po and
always originate at a read; rmw links the read of an RMW
operation to its corresponding write; rf connects writes to
reads accessing the same location, with no read having more
than one incoming rf edge; and co connects writes to the
same location and forms, for each location, a strict total order
over the writes to that location.
Notation
Given a relationr,r −1 is its inverse,r ? is its reflex-
ive closure, r + is its transitive closure, and r ∗is its reflexive
transitive closure. We use ¬ for the complement of a set or
relation, implicitly with respect to the set of all events or
event pairs in the execution. We write ‘;’ for relational com-
position: r1 ;r2 = {(x,z) | ∃y. (x,y) ∈r1 ∧(y,z) ∈r2}. We
write [−] to lift a set to a relation: [s] = {(x,x) | x ∈s}. To
restrict a relation r to being inter-thread or intra-thread, we
use r e = r \(po ∪po−1)∗or r i = r ∩(po ∪po−1)∗, respectively.
Similarly, r loc = r ∩sloc.
Derived Relations
The from-read (fr) relation relates each
read event to all the write events on the same location that
are co-later than the write the read observed [40]. The com
relation captures three ways events can ‘communicate’ with
each other.
fr
=
([R];sloc ;[W ]) \ (rf −1 ;(co−1)∗)
com
=
rf ∪co ∪fr
Visualising Executions
We represent executions using
diagrams like the one in Fig. 1 (left). Here, the po-edges
separate the execution’s events into two threads, each drawn
in one column. Each event is labelled with the sets it belongs
to, such as R and W . We use location names such as x to
identify the sloc-classes.
2.2
From Executions to Litmus Tests
In order to test whether an execution of interest is observable
in practice, it is necessary to convert it into a litmus test (i.e.,
a program with a postcondition) [18]. This litmus test is
constructed so that the postcondition only passes when the
particular execution of interest has been taken [3, 55].
3


PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
Nathan Chong, Tyler Sorensen, and John Wickerson
a: W x
b: R x
c: W x
co
po
rf
Initially: [X0] = x = 0, [X1] = ok = 1
txbegin Lfail
c: [X0] ←2
a: [X0] ←1
b: r0 ←[X0]
txend
goto Lsucc
Lfail: [X1] ←0
Lsucc:
Test: ok = 1 ∧r0 = 2 ∧x = 2
Figure 2. A transactional execution and its litmus test
As an example, the execution on the left of Fig. 1 cor-
responds to the pseudocode litmus test on the right. Read
events become loads, writes become stores, and the po-edges
induce the order of instructions and their partitioning into
threads. To ensure that the litmus test passes only when the
intended rf -edges are present, we arrange that each store
writes a unique non-zero value, and then check that each
local register holds the value written by the store it was
intended to observe – this corresponds to the r0 = 2 in
the postcondition. To ensure that the intended co-edges are
present, we check the final value of each memory location –
this corresponds to the x = 2 in the postcondition.2
3
Axiomatising Transactions
Transactional memory (TM) can be provided either at the
architecture level (x86, Power, ARMv8) or in software (C++).
Since we are concerned only with the specification of TM,
and not its implementation, we can formalise both forms
within a unified framework. In this section, we describe how
program executions can be extended to express transactions
(§3.1) and how we can derive litmus tests to test for these
executions (§3.2). We then propose axioms for capturing the
isolation of transactions (§3.3), and for strengthening the SC
memory model to obtain transactional SC (§3.4).
3.1
Transactional Executions
To enable transactions in an axiomatic memory modelling
framework, we extend executions with an stxn relation that
relates events in the same successful (i.e., committed) trans-
action. For an execution to be well-formed, stxn must be a
partial equivalence relation (i.e., symmetric and transitive),
and each stxn-class must coincide with a contiguous sub-
set of po. When generating the candidate executions of a
program with transactions, each transaction is assumed to
succeed or fail non-deterministically. That is, each either
gives rise to a stxn-class of events, or vanishes as a no-op.
Diagrammatically, we represent stxn using boxes. For in-
stance, events a and b in Fig. 2 form a successful transaction.
2 When there are more than two writes to a location, extra constraints on
executions are needed to fix all the co-edges [55].
R x
R x
W x
fr
rf
po
(a)
R x
W x
W x
fr
co
po
(b)
W x
R x
W x
co
rf
po
(c)
W x
W x
R x
rf
fr
co po
(d)
Figure 3. Four SC executions that are allowed by weak iso-
lation but forbidden by strong isolation
Remark 3.1. To study the behaviour of unsuccessful trans-
actions in more detail, one could add an explicit representa-
tion of them in executions, perhaps using dashed boxes.
However, the behaviour of unsuccessful transactions is
tricky to ascertain on hardware because of the rollback
mechanism. Moreover, it is unclear how they should inter-
act with co, since co is the order in which writes hit the
memory, which writes in unsuccessful transactions never
do.
3.2
From Transactional Executions to Litmus Tests
A transactional execution can be converted into a litmus test
by extending the construction of §2.2. As an example, the
execution on the left of Fig. 2 corresponds to the litmus test
on the right. The instructions in the transaction simply need
enclosing in instructions that begin and end a transaction.
We write these as txbegin and txend here; our tooling spe-
cialises these for each target architecture. The postcondition
checks that the transaction succeeded using the ‘ok’ location,
which is zeroed in the transaction’s fail-handler, Lfail, the
label of which is provided with the txbegin instruction.
3.3
Weak and Strong Isolation
We now explain how the isolation property of transactions
can be captured as a property of an execution graph. A TM
system provides weak isolation if transactions are isolated
from other transactions; that is, their intermediate state can-
not affect or be affected by other transactions [12, 27]. It
provides strong isolation if transactions are also isolated
from non-transactional code.
The four 3-event SC executions in Fig. 3 illustrate the
difference between strong and weak isolation. In each, the
interfering event would need to be within a transaction to
be forbidden by weak isolation; strong isolation does not
make this distinction. Executions (a) and (d) correspond to
what Blundell et al. call non-interference and containment,
respectively, and (b) is similar to the standard axiom for
RMW isolation (cf. RMWIsol in Fig. 5).
Failures of isolation can be characterised as communica-
tion cycles between transactions. To define these cycles, the
following constructions are useful:
weaklift(r,t)
=
t ;(r \ t);t
stronglift(r,t)
=
t? ;(r \ t);t?.
4


The Semantics of Transactions and Weak Memory
PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
acyclic(hb)
where hb = po ∪com
(Order)
acyclic(stronglift(hb, stxn))
(TxnOrder)
Figure 4. SC axioms [49], with TSC extensions highlighted
If r relates events e1 and e2 in different transactions, then
weaklift(r, stxn) relates all the events in e1’s transaction to all
those in e2’s transaction. The stronglift version also includes
edges where the source and/or the target event are not in a
transaction. Weak and strong isolation can then be axioma-
tised by treating all the events in a transaction as a single
event whenever the transaction communicates with another
transaction (WeakIsol) or any other event (StrongIsol).
acyclic(weaklift(com, stxn))
(WeakIsol)
acyclic(stronglift(com, stxn))
(StrongIsol)
3.4
Transactional Sequential Consistency
Although isolation is a critical property for transactions, it
only provides a lower bound on the guarantees that real
architectures provide. Meanwhile, an upper bound on the
guarantees provided by a reasonable TM implementation is
transactional sequential consistency (TSC) [19]. The models
we propose in §5–7 all lie between these bounds.
TSC is a strengthening of the SC memory model in which
consecutive events in a transaction must appear consecu-
tively in the overall execution order. Where SC can be char-
acterised axiomatically (Fig. 4) by forbidding cycles in pro-
gram order and communication (Order) [49], we can obtain
TSC by additionally forbidding such cycles between transac-
tions and non-transactional events (TxnOrder). Note that
TxnOrder subsumes the StrongIsol axiom.
4
Methodology
We identify three components of a memory modelling method-
ology: (1) developing and refining axioms, (2) synthesising
and running conformance tests, and (3) checking metatheo-
retical properties. In this section, we explain our approach
to each of these components, and in particular, how we have
extended the Memalloy tool [55] to support each task.
Background on Memalloy
The original Memalloy tool,
built on top of Alloy [35], was developed for comparing
memory models. It takes two models (say, M and N), and
searches for a single execution that distinguishes them (i.e., is
inconsistent under M but consistent under N). Additionally,
if Memalloy is supplied with a translation on executions (e.g.,
representing a compiler mapping or a compiler optimisation),
then it searches for a witness that the translation is unsound.
This translation is defined by a relation, typically named π,
from ‘source’ events to ‘target’ events.
4.1
Developing and Refining Axioms
For each model, we make a first attempt at a set of axioms us-
ing information obtained from specifications, programming
manuals, research papers, and discussions with designers.
Then, for each proposed change to the model, we use Memal-
loy to generate tests that become disallowed or allowed as
a result. We decide whether to accept the change based on
discussing these tests with designers, and running them on
existing hardware (where available) using the Litmus tool [4].
In order to extend Memalloy to support the development
of transactional memory models in this way, we augmented
the form of executions as described in §3.1, and modified the
litmus test generator as described in §3.2.
4.2
Synthesising and Running Conformance Tests
To build confidence in a model, we compare the behaviours
it admits against those allowed by the architecture or lan-
guage being modelled. It is vital that no behaviour allowed
by the architecture/language is forbidden by the model, so
we exhaustively generate all litmus tests (up to a bounded
size) that our model forbids, and confirm using Litmus that
none can be observed on existing hardware.
To achieve this, we extended Memalloy with a mode for
exhaustively generating conformance tests for a given model
M. The key to exhaustive generation is a suitable notion of
minimality, without which we would obtain an infeasibly
large number of tests. We closely follow Lustig et al. [40], and
define execution minimality with respect to the following
partial order between executions. Let X ⊏Y hold when
execution X can be obtained from execution Y by:
(i) removing an event (plus any incident edges),
(ii) removing a dependency edge (addr, ctrl, data, rmw), or
(iii) downgrading an event (e.g. reducing an acquire-read to
a plain read in ARMv8).
We then calculate the set min-inconsistent(M) = {X ∈X |
X < consistent(M) ∧∀X ′ ⊏X. X ′ ∈consistent(M)}.
Extending Memalloy to support the synthesis of transac-
tional conformance tests requires minimality to take trans-
actions into account. To do this, we arrange that X ⊏Y also
holds when X can be obtained from Y by:
(v) making the first or last event in a transaction non-trans-
actional (i.e. removing all of its incident stxn edges).
(We avoid the ‘middle’ of a transaction so as not to create non-
contiguous transactions and hence ill-formed executions.)
Remark 4.1. While this is a slightly coarse notion of min-
imality – a more refined version would also allow a large
transaction to be chopped into two smaller ones – it is cheap
to implement in the constraint solver as it only requires
quantification over a single event. As a result, Memalloy
may generate some executions that appear non-minimal,
but as we show in §5.3, this does not impede our ability to
generate and run large batches of conformance tests.
5


PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
Nathan Chong, Tyler Sorensen, and John Wickerson
Generating Allowed Tests
Having generated the minimal-
ly-forbidden tests, the question naturally arises of whether
we can generate the maximally-allowed tests too. Where the
minimally-forbidden tests include just enough fences/depen-
dencies/transactions to be forbidden (and failing to observe
these tests empirically suggests that the model is not too
strong), the maximally-allowed tests include just not enough
(and observing them suggests that the model is not too weak).
We found the maximally-allowed tests valuable for commu-
nicating with engineers about the detailed relaxations per-
mitted by our models. However, in our experiments, allowed
tests are less conclusive than forbidden ones, because where
the observation of a forbidden test implies that the model
is unsound, the non-observation of an allowed test may be
caused by not performing enough runs, or by the machine
under test being implemented conservatively.
Moreover, the notion of execution maximality is not as nat-
ural as minimality. For instance, an inconsistent execution
is only considered minimally-inconsistent if removing any
event makes it consistent, yet it is not sensible to deem a con-
sistent execution maximally-consistent only when adding
any event makes it inconsistent – such a condition is almost
impossible to satisfy. Even with event addition/removal set
aside, maximal-consistency tends to require executions to
be littered with redundant fences and dependencies.
Therefore, we approximate the maximally-consistent exe-
cutions as those obtained via a single ⊏-step from a minimally-
inconsistent execution. That is, we let max-consistent(M) =
{X ∈X | ∃Y ∈min-inconsistent(M). X ⊏Y }.
4.3
Checking Metatheoretical Properties
As explained at the start of this section, Memalloy is able
to validate transformations between two memory models,
providing they can be encoded as a π-relation between ex-
ecutions. In §8, we exploit this ability to check several TM-
related transformations and compiler mappings.
In fact, Memalloy can also be used to check libraries under
weak memory. Prior work has (manually) verified that stack,
queue, and barrier libraries implement their specifications
under weak memory models [8, 52]; here we show how
checking these types of properties can be automated up to
a bounded number of library and client events. We see this
as a straightforward first-step towards a general verification
effort. The idea, which we apply to a lock elision library in
§8.3, is to treat the replacement of the library’s specification
with its implementation as a program transformation. To do
this, we first extend executions with events that represent
method calls. Second, we extend execution well-formedness
so that illegal call sequences (such as popping from an empty
stack) are rejected. Third, we strengthen the memory model’s
consistency predicate with axioms capturing the library’s
obligations (such as pops never returning data from later
pushes). Finally, we constrain π so that it maps each method
acyclic(poloc ∪com)
(Coherence)
empty(rmw ∩(fre ;coe))
(RMWIsol)
acyclic(hb)
(Order)
where ppo = ((W ×W ) ∪(R ×W ) ∪(R × R)) ∩po
tfence = po ∩((¬stxn;stxn) ∪(stxn;¬stxn))
L = domain(rmw) ∪range(rmw)
implied = [L];po ∪po ;[L] ∪tfence
hb = mfence ∪ppo ∪implied ∪rfe ∪fr ∪co
acyclic(stronglift(com, stxn))
(StrongIsol)
acyclic(stronglift(hb, stxn))
(TxnOrder)
Figure 5. x86 consistency axioms [5], with our TM additions
highlighted
call to an event sequence representing the implementation
of that method.
5
Transactions in x86 and Power
Over the next three sections, we show how our methodology
can be applied to four different targets. We begin with x86
and Power, which have both supported TM since 2013 [15,
32]. Intel’s Transactional Synchronisation Extensions (TSX)
provide XBEGIN, XEND, and XABORT instructions for starting,
committing, and aborting transactions, while Power provides
tbegin, tend, and tabort.
5.1
Background: the x86 and Power Memory Models
Both the x86 memory model [44] and the Power memory
model [5, 47, 48] allow certain instructions to execute out of
program order, with x86 allowing stores to be reordered with
later loads and Power allowing many more relaxations. Both
architectures provide fences (MFENCE in x86, and lwsync,
sync, and isync in Power) to allow these relaxations to be
controlled. The x86 architecture provides atomic RMWs via
LOCK-prefixed instructions, while Power implements RMWs
using exclusive instructions like those seen in Example 1.1.
Moreover, x86 is multicopy-atomic [18], which means that
writes are propagated to all other threads simultaneously.
Power does not have this property, so its memory model
includes explicit axioms to describe how writes propagate.
More formally, we extend executions with relations that
connect events in program order that are separated by a fence
event of a given type. For x86, we add an mfence relation,
and for Power, we add isync, lwsync, and sync.
An x86 execution is consistent if it satisfies all of the ax-
ioms in Fig. 5 (ignoring the highlighted regions for now).
The Coherence axiom forbids cycles in communication
edges and program order among events on the same location;
this guarantees programs that use only a single location to
have SC semantics. Happens-before (hb) imposes the event-
ordering constraints upon which all threads must agree, and
Order ensures that hb∗is a partial order. The constraints
6


The Semantics of Transactions and Weak Memory
PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
acyclic(poloc ∪com)
(Coherence)
empty(rmw ∩(fre ;coe))
(RMWIsol)
acyclic(hb)
(Order)
where ppo = (preserved program order, elided)
tfence = po ∩((¬stxn;stxn) ∪(stxn;¬stxn))
fence = sync ∪tfence ∪(lwsync \ (W × R))
ihb = ppo ∪fence
thb = (rfe∪((fre∪coe)∗;ihb))∗;(fre∪coe)∗;rfe?
hb = (rfe? ;ihb ;rfe?) ∪weaklift(thb, stxn)
acyclic(co ∪prop)
(Propagation)
where efence = rfe? ;fence ;rfe?
prop1 = [W ];efence ;hb∗;[W ]
prop2 = come∗;efence∗;hb∗;(sync ∪tfence );hb∗
tprop1 = rfe ;stxn;[W ]
tprop2 = stxn;rfe
prop = prop1 ∪prop2 ∪tprop1 ∪tprop2
irreflexive(fre ;prop ;hb∗)
(Observation)
acyclic(stronglift(com, stxn))
(StrongIsol)
acyclic(stronglift(hb, stxn))
(TxnOrder)
empty(rmw ∩tfence∗)
(TxnCancelsRMW)
Figure 6. Power consistency axioms [5], with our TM addi-
tions highlighted , and some details elided for brevity.
on hb arise from: fences placed by the programmer (mfence),
fences created implicitly by LOCK’d operations (implied), the
preserved fragment of the program order (ppo), inter-thread
observations (rfe) and communication edges (fr and co).
A Power execution is consistent if it satisfies all the axioms
in Fig. 6 (again, ignoring the highlights). The first axiom not
already seen is Order, which ensures that happens-before
(hb) is acyclic. In contrast to x86, the happens-before relation
in Power is formed from inter-thread observations (rfe), the
preserved fragment of the program order (ppo), and fences
(fence). We elide the definition of ppo as it is complex and
unchanged by our TM additions. The prop relation governs
how fences restrict “the order in which writes propagate” [5],
and the Propagation axiom ensures that this relation does
not contradict the coherence order. Observation governs
which writes a read can observe: if e1 propagates before
e2, then any read that happens after e2 is prohibited from
observing a write that precedes e1 in coherence order.
5.2
Adding Transactions
To extend the x86 and Power memory models to support
TM, we make the following amendments, each highlighted
in Figs. 5 and 6.
Strong Isolation (x86 and Power)
The Power manual says
that transactions “appear atomic with respect to both trans-
actional and non-transactional accesses performed by other
threads” [29, §5.1], and the TSX manual defines conflicts
not just between transactions, but between a transaction
and “another logical processor” (which is not required to
be executing a transaction) [31, §16.2]. We interpret these
statements to mean that x86 and Power transactions provide
strong isolation, so we add our StrongIsol axiom from §3.3.
Implicit Transaction Fences (x86 and Power)
In both
x86 and Power, fences are created at the boundaries of suc-
cessful transactions. In x86, “a successfully committed [trans-
action] has the same ordering semantics as a LOCK prefixed
instruction” [31, §16.3.6], and in Power, “[a] tbegin instruc-
tion that begins a successful transaction creates a [cumu-
lative] memory barrier”, as does “a tend instruction that
ends a successful transaction” [29, §1.8]. Hence, we define
tfence as the program-order edges that enter (¬stxn ; stxn)
or exit (stxn;¬stxn) a successful transaction, and add tfence
alongside the existing fence relations (mfence and sync).
Transaction Atomicity (x86 and Power)
We extend the
prohibition on hb cycles among events to include cycles
among transactions (TxnOrder). This essentially treats all
the transaction’s events as one indivisible event, and is justi-
fied by the atomicity guarantee given to transactions, which
in x86 is “that all memory operations [...] appear to have
occurred instantaneously when viewed from other logical
processors” [31, §16.2], and in Power is that each successful
transaction “appears to execute as an atomic unit as viewed
by other processors and mechanisms” [29, §1.8].
Barriers within Transactions (Power only)
Each trans-
action contains an “integrated memory barrier”, which en-
sures that writes observed by a successful transaction are
propagated to other threads before writes performed by the
transaction itself [29, §1.8]. This behaviour is epitomised by
the WRC-style execution below [15, Fig. 6],
a: W x
b: R x
c: W y
d: R y
e: R x
fr
rf
rf
po
ppo
(1)
which must be ruled out because the transaction’s write (c)
has propagated to the third thread before a write (a) that the
transaction observed. We capture this constraint by extend-
ing the prop relation so that it connects any write observed
by a transaction to any write within that transaction (tprop1).
In execution (1), this puts a prop edge from a to c. The execu-
tion is thus forbidden by the existing Observation axiom.
Remark 5.1. The following executions are similar to (1),
and like (1), they could not be observed empirically. How-
ever, the Power manual is ambiguous about whether they
should be forbidden.
W x
R x
R y
W y
R x
fr
rf
fr
po
sync
W x
R x
R y
W y
W x
co
rf
fr
po
sync
7


PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
Nathan Chong, Tyler Sorensen, and John Wickerson
In particular, because the transactions are read-only, we
cannot appeal to the integrated memory barrier. We have
reported this ambiguity to IBM architects, and while we
await a clarified specification, our model errs on the side
of caution by permitting these executions.
Propagation of Transactional Writes (Power only)
Al-
though Power is not multicopy-atomic in general, transac-
tional writes are multicopy-atomic; that is, the architecture
will “propagate the transactional stores fully before commit-
ting the transaction” [15, §4.2]. This behaviour is epitomised
by another WRC-style execution, in which the middle thread
sees the transactional write to x before the right thread does.
a: W x
b: R x
c: W y
d: R y
e: R x
fr
rf
rf
ppo
ppo
(2)
To rule out such executions, it suffices to extend the prop re-
lation with reads-from edges that exit a transaction (tprop2),
and then to invoke Observation again.
Read-modify-writes (Power only)
In Power, when a store-
exclusive is separated from its corresponding load-exclusive
by “a state change from Transactional to Non-transactional
or Non-transactional to Transactional”, the RMW operation
will always fail [29, §1.8]. Therefore, the TxnCancelsRMW
axiom ensures that no consistent execution has an rmw edge
crossing a transaction boundary.
Transaction Ordering (Power only)
The Power manual
states that “successful transactions are serialised in some
order”, and that it is impossible for contradictions to this
order to be observed [29, p. 824].
We capture this constraint by extending the hb relation
to include a new thb relation between transactions. The thb
relation imposes constraints on the order in which transac-
tions can be serialised. By including it in hb and requiring
thb to be a partial order, we guarantee the existence of a
suitable transaction serialisation order, without having to
construct this order explicitly.
The definition of the thb relation is a little convoluted,
but the intuition is quite straightforward: it contains all non-
empty chains of intra-thread happens-before edges (ihb) and
inter-thread communication edges (come), except those that
contain an fre or coe edge followed by an rfe edge that does
not terminate the chain. The rationale for excluding fre ;rfe
and coe ;rfe chains is that these do not provide ordering in a
non-multicopy-atomic architecture. That is, from
a
b
c
fre
rfe
or
a
b
c
coe
rfe
we cannot deduce that a happens before c, because this be-
haviour can also be attributed to the writeb being propagated
to c’s thread before a’s thread.
Table 1. Testing our transactional x86 and Power models
Arch.
|E|
Synthesis
time (s)
Forbid
Allow
T
S
¬S
T
S
¬S
x86
2
4
0
0
0
2
2
0
3
22
4
0
4
24
23
1
4
87
22
0
22
99
99
0
5
260
42
0
42
249
244
5
6
4402
133
0
133
895
832
63
7
>7200
307
0
307
2457
1901
556
Total (x86):
508
0
508
3726
3101
625
Power
2
13
2
0
2
7
7
0
3
58
9
0
9
44
44
0
4
318
60
0
60
184
175
9
5
9552
353
0
353
1517
1330
187
6
>7200
922
0
922
5043
4407
636
Total (Power):
1346
0
1346
6795
5963
832
Cain et al. epitomise the transaction-ordering constraint
using the IRIW-style execution reproduced below [15, Fig. 5].
a: W x
b: R x
c: R y
d: R y
e: R x
f : W y
fr
fr
rf
rf
ppo
ppo
(3)
The execution must be disallowed because different threads
observe incompatible transaction orders: the second thread
observes a before f , but the third observes f before a. Our
model disallows this execution on the basis of a thb cycle
between the two transactions.
We must be careful not to overgeneralise here, because
a behaviour similar to (3) but with only one write transac-
tional was observed during our empirical testing, and is duly
allowed by our model.
5.3
Empirical Testing
Table 1 gives the results obtained using our testing strategy
from §4.2. We use Memalloy to synthesise litmus tests that
are forbidden by our transactional models but allowed under
the non-transactional baselines (the Forbid set), up to a
bounded number of events (|E|). We then derive the Allow
sets by relaxing each test. We report synthesis times on a
4-core Haswell i7-4771 machine with 32GB RAM, using a
timeout of 2 hours. For both sets we give the number of tests
(T) found; we say this number is complete if synthesis did
not reach timeout and non-exhaustive otherwise. We say a
test is seen (S) if it is observed on any implementation, and
not seen (¬S) otherwise. Each x86 test is run 1M times on
four TSX implementations: a Haswell (i7-4771), a Broadwell-
Mobile (i7-5650U), a Skylake (i7-6700), and a Kabylake (i7-
7600U). Each Power test is run 10M times on an 80-core
POWER8 (TN71-BP012) machine. When testing this machine,
we use Litmus’s affinity parameter [4], which places threads
8


The Semantics of Transactions and Weak Memory
PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
0
5
10
15
20
25
30
0
50
100
34
Time (hours)
Tests
found
(%)
Figure 7. The distribution of synthesis times for the 7-event
x86 Forbid tests
incrementally across the logical processors to encourage
IRIW-style behaviours.
We were able to generate the complete set of x86 For-
bid executions that have up to 6 events, and the complete
set of Power Forbid executions up to 5 events. Regarding
these bounds: we remark that since our events only repre-
sent memory accesses and fences (not, for instance, starting
or committing transactions), we can capture many inter-
esting behaviours with relatively few events. For instance,
these bounds are large enough to include all the executions
discussed in this section.
Of our 508 x86 Forbid tests, 29% had one transaction, 44%
had two, and 27% had three, and of the 1346 Power Forbid
tests, 29% had one transaction, 54% had two, and 17% had
three. No Forbid test was empirically observable on either
architecture, which gives us confidence that our models are
not too strong. Of the x86 Allow tests, 83% could be observed
on at least one implementation, as could 88% of the Power
Allow tests; this provides some evidence that our models are
not excessively weak. Many of the unobserved Power Allow
tests are based on the load-buffering (LB) shape, which has
never actually been observed on a Power machine, even
without transactions [6].
Increasing the timeout to 48 hours is sufficient to generate
the complete set of x86 Forbid executions for 7 events. It
takes 34 hours for Memalloy to find all 313 tests. Figure 7
shows how the percentage of executions found is affected by
various caps on the synthesis time. We observe that many
tests are found quickly: 98% of the tests are found within
2 hours (i.e., 6% of the total synthesis time), and all of the
tests are found within 9 hours (the remaining synthesis time
is used to confirm that there are no further tests). During
the development process, we exploited this observation to
obtain preliminary test results more rapidly.
6
Transactions in ARMv8
The ARMv8 memory model sits roughly between x86 and
Power. Like x86, it is multicopy-atomic [45], but like Power, it
permits several relaxations to the program order. Unwanted
relaxations can be inhibited either using barriers (DMB, DMB LD,
DMB ST, ISB) or using release/acquire instructions (LDAR, STLR)
that act like one-way fences.
acyclic(poloc ∪com)
(Coherence)
acyclic(ob)
(Order)
where dob = (order imposed by dependencies, elided)
aob = (order imposed by atomic RMWs, elided)
bob = (order imposed by barriers, elided)
tfence = po ∩((¬stxn;stxn) ∪(stxn;¬stxn))
ob = come ∪dob ∪aob ∪bob ∪tfence
empty(rmw ∩(fre ;coe))
(RMWIsol)
acyclic(stronglift(com, stxn))
(StrongIsol)
acyclic(stronglift(ob, stxn))
(TxnOrder)
empty(rmw ∩tfence∗)
(TxnCancelsRMW)
Figure 8. ARMv8 consistency axioms [7, 21], with our TM
additions highlighted , and some details elided for brevity.
Formally, ARMv8 executions are obtained by adding six
extra fields: Acq and Rel, which are the sets of acquire and re-
lease events, and dmb/dmbld/dmbst/isb, which relate events
in program order that are separated by barriers.
An ARMv8 execution is consistent if it satisfies all of the
axioms in Fig. 8 (ignoring the highlighted regions). We have
seen the Coherence and RMWIsol axioms already. The
ordered-before relation (ob) plays the same role as happens-
before in x86: it imposes the event-ordering constraints upon
which all threads must agree, and must be free from cycles
(Order). These constraints arise from communication (come),
dependencies (dob), atomic RMWs (aob), and barriers (bob).
6.1
Adding Transactions
The ARMv8 architecture does not support TM, so the exten-
sions proposed below (highlighted in Fig. 8) are unofficial.
Nonetheless, the extensions we give are based upon a pro-
posal currently being considered within ARM Research and
upon extensive conversations with ARM architects.
• StrongIsol is a natural choice for hardware TM.
• As in x86 and Power, we place implicit fences (tfence) at
the boundaries of successful transactions.
• We bring the TxnOrder axiom from x86 and Power to
forbid ob-cycles among transactions.
• Like Power, ARMv8 has exclusive instructions, so it in-
herits the TxnCancelsRMW axiom to ensure the failure
of RMWs that straddle a transaction boundary.
6.2
Empirical Testing
ARM hardware does not support TM so we cannot test our
model as we did for x86 and Power. However, we generated
the Forbid and Allow suites anyway, and gave them to
ARM architects. They were able to use these to reveal a
bug (specifically, a violation of the TxnOrder axiom) in a
register-transfer level (RTL) prototype implementation.
9


PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
Nathan Chong, Tyler Sorensen, and John Wickerson
irreflexive(hb ;com∗)
(HbCom)
where sw = (synchronises-with, elided)
ecom = com ∪(co ;rf )
tsw = weaklift(ecom, stxn)
hb = (sw ∪tsw ∪po)+
empty(rmw ∩(fre ;coe))
(RMWIsol)
acyclic(po ∪rf )
(NoThinAir)
acyclic(psc)
(SeqCst)
where psc = (constraints on SC events, elided)
empty(cnf \ Ato2 \ (hb ∪hb−1))
(NoRace)
where cnf = ((W ×W ) ∪(R×W ) ∪(W ×R)) ∩sloc \ id
Figure 9. C++ consistency and race-freedom axioms [38],
with our TM additions highlighted , and some details elided.
7
Transactions in C++
We now turn our attention from hardware to software. TM is
supported in C++ via an ISO technical specification that has
been under development by the C++ TM Study Group since
2012 [34, 50]. In this section, we formalise how the proposed
TM extensions interact with the existing C++ memory model,
and detail a possible simplification to the specification.
C++ TM offers two main types of transactions: relaxed
transactions (written synchronized{...}) can contain arbi-
trary code, but only promise weak isolation, while atomic
transactions (written atomic{...}) promise strong isolation
but cannot contain certain operations, such as atomic opera-
tions [34, §8.4.4]. Some atomic transactions can be aborted by
the programmer, but we do not support these in this paper.
7.1
Background: the C++ Memory Model
Our presentation of the baseline C++ memory model follows
Lahav et al. [38]. We choose to build on their formalisation
because it incorporates a fix that allows correct compilation
to Power – without this, we could not check the compilation
of C++ transactions to Power transactions (§8.2).
C++ executions identify four additional subsets of events:
Ato contains the events from atomic operations, while Acq,
Rel, and SC contain events from atomic operations that use
the acquire, release, and SC consistency modes [33, §29.3].
Unlike the architecture-level memory models, the C++
memory model defines two predicates on executions (Fig. 9).
The first characterises the consistent candidate executions. If
any consistent execution violates a second race-freedom pred-
icate, then the program is completely undefined. Otherwise,
the allowed executions are the consistent executions.
A C++ execution is consistent if it satisfies all of the consis-
tency axioms given at the top of Fig. 9 (ignoring highlighted
regions for now). The first, HbCom, governs the happens-
before relation, which is constructed from the program order
and the synchronises-with relation (sw). Roughly speaking,
an sw edge is induced when an acquire read observes a re-
lease write; but it also handles fences and the ‘release se-
quence’ [9, 38]. The second axiom is standard for capturing
the isolation of RMW operations. The NoThinAir axiom is
Lahav et al.’s solution to C++’s ‘thin air’ problem [10]. Finally,
SeqCst forbids certain cycles among SC events; we omit its
definition as it does not interact with our TM extensions.
A consistent C++ execution is race-free if it satisfies the
NoRace axiom at the bottom of Fig. 9, which states that
whenever two conflicting (cnf ) events in different threads
are not both atomic, they must be ordered by happens-before.
7.2
Adding Transactions
The specification for C++ TM makes two amendments to
the C++ memory model: one for data races, and one for
transactional synchronisation.
Transactions and Data Races
The definition of a race is
unchanged in the presence of TM. In particular, the program
atomic{ x=1; }
atomic_store(&x,2);
is racy – which is perhaps contrary to the intuition that an
atomic transaction with a single non-atomic store should be
interchangeable with a non-transactional atomic store.
Remark 7.1. The specification also clarifies that although
events in an unsuccessful transaction are unobservable,
they can still participate in races. This implies that the
program
atomic{ x=1; abort(); }
atomic_store(&x,2);
must be considered racy. In our formalisation, transactions
either succeed (giving rise to an stxn-class) or fail, giving
rise to no events (cf. §3.1). This treatment correctly handles
races involving unsuccessful transactions, because the race
will be detected in the case where the transaction succeeds,
but it cannot handle transactions that never succeed, such as
the one above. Therefore, we leave the handling of abort()
for future work.
Transactional Synchronisation
The second amendment
by the C++ TM extension defines when two transactions
synchronise [34, §1.10]. An execution is deemed consistent
only if there is a total order on transactions such that:
1. this order does not contradict happens-before, and
2. if transactionT1 is ordered before conflicting transaction
T2, then the end of T1 synchronises with the start of T2.
We could incorporate these requirements into the formal
model by extending executions with a transaction-ordering
relation, to, that serialises all the stxn-classes in an order
that does not contradict happens-before (point 1), and up-
dating the synchronises-with relation to include events in
conflicting transactions that are ordered by to (point 2).
10


The Semantics of Transactions and Weak Memory
PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
However, this formulation is unsatisfying. It is awkward
that to is used to define happens-before but is also forbid-
den to contradict happens-before. Moreover, having the con-
sistency predicate involve quantification over all possible
transaction serialisations makes simulation expensive [9].
Fortunately, we can formulate the C++ TM memory model
without relying on a total order over transactions. The idea
is that if two transactions are in conflict, then their order can
be deduced from the existing rf , co, and fr edges, and if they
are not, then there is no need to order them.
In more detail, and with reference to the highlighted parts
of Fig. 9: observe that whenever two events in an execu-
tion conflict (cnf ), they must be connected one way or the
other by ‘extended communication’ (ecom), which is the
communication relation extended with co ;rf chains. That
is, cnf = ecom ∪ecom−1 [
]. We then say that transactions
synchronise with (tsw) each other in ecom order, and we
extend happens-before to include tsw.
By simply extending the definition of hb like this, we
avoid the need for the to relation altogether, and we avoid
adding any axioms to the consistency predicate. To make
our proposal concrete, we provide in §A some text that the
specification could incorporate (currently under review by
the C++ TM Study Group).
Strong Isolation for Atomic Transactions
The seman-
tics described thus far provides the desired weak-isolating
behaviour for relaxed transactions; that is, the WeakIsol
axiom follows from the other C++ consistency axioms [
].
However, atomic transactions must be strongly isolated. In
fact, atomic transactions enjoy strong isolation simply by
being forbidden to contain atomic operations. The idea is
that for a non-transactional event to observe or affect a trans-
action’s intermediate state, it must conflict with an event in
that transaction. If this event cannot be atomic, there must
be a race. Thus, for race-free programs, atomic transactions
are guaranteed to be strongly isolated.
To formalise this property, we extend C++ executions with
an stxnat relation that identifies a subset of transactions as
atomic. It satisfies stxnat ⊆stxn and (stxnat ; stxn) ⊆stxnat.
We then prove the following theorem.
Theorem 7.2 (Strong isolation for atomic transactions). If
NoRace holds, and atomic transactions contain no atomic
operations (i.e., domain(stxnat) ∩Ato = ∅), then
acyclic(stronglift(com, stxnat)).
Proof sketch. A cycle in stronglift(com, stxnat) is either a com-
cycle or an r-cycle, where r = stxnat ;(com \ stxnat)+ ;stxnat.
From NoRace, we have com \ Ato2 ⊆hb. Using this and the
expansion com+ = ecom ∪(fr ;rf ) we can obtain r ⊆hb. To
finish the proof, note that execution well-formedness forbids
com-cycles, and that r-cycles are forbidden too because they
are also hb-cycles, which violate HbCom.
Table 2. Summary of our metatheoretical results. Timings
are for a machine with four 16-core Opteron processors and
128GB RAM, using the Plingeling solver [11]. A ✗means the
property holds up to the given number of events, a ✓means
a counterexample was found, and U indicates a timeout.
Property
§
Target
Events Time C’ex?
Monotonicity 8.1 x86
6
20m
✗
Power
2
<1s
✓
ARMv8
2
<1s
✓
C++
6
91h
✗
Compilation
8.2 C++/x86
6
14h
✗
C++/Power
6
16h
✗
C++/ARMv8
6
20h
✗
Lock elision
8.3 x86
8
>48h
U
Power
9
>48h
U
ARMv8
7
63s
✓
ARMv8 (fixed)
8
>48h
U
A Transactional SC-DRF Guarantee
A central property
of the C++ memory model is its SC-DRF guarantee [2, 13]:
all race-free C++ programs that avoid non-SC atomic oper-
ations enjoy SC semantics. This guarantee can be lifted to
a transactional setting [19, 50]: all race-free C++ programs
that avoid relaxed transactions and non-SC atomic opera-
tions enjoy TSC semantics (cf. §3.4). This is formalised in the
following theorem, which we prove in §C.
Theorem 7.3 (Transactional SC-DRF guarantee). If a C++-
consistent execution has
• no relaxed transactions (i.e. stxn = stxnat),
• no non-SC atomics (i.e. Ato = SC), and
• no data races (i.e. NoRace holds),
then it is consistent under TSC.
8
Metatheory
We now study several metatheoretical properties of our pro-
posed models. For instance, one straightforward but impor-
tant property, which follows immediately from the model
definitions, is that our TM models give the same semantics to
transaction-free programs as the original models [
]. In this
section, we use Memalloy to check some more interesting
properties of our models, as summarised in Tab. 2.
8.1
Monotonicity
We check that adding stxn-edges can never make an in-
consistent execution consistent. This implies that all of the
following program transformations are sound: introducing
a transaction (e.g., •
• ), enlarging a transaction (e.g.,
• •
• • ), and coalescing two consecutive transactions
(e.g., •
•
• • ).
Memalloy confirmed that the transactional x86 and C++
models enjoy this monotonicity property for all executions
11


PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
Nathan Chong, Tyler Sorensen, and John Wickerson
with up to 6 events. For Power and ARMv8, it found the
following counterexample:
R x
W x
R x
W x
rmw
rmw
The left execution is inconsistent in both models because of
the TxnCancelsRMW axiom: that a store-exclusive sepa-
rated from its corresponding load-exclusive by a transaction
boundary always fails. The right execution, however, is con-
sistent. This counterexample implies that techniques that
involve transaction coalescing [17, 53] must be applied with
care in the presence of RMWs.
8.2
Mapping C++ Transactions to Hardware
We check that it is sound to compile C++ transactions to x86,
Power, and ARMv8 transactions. A realistic compiler would
be more complex – perhaps including fallback options for
when hardware transactions fail – but our direct mapping is
nonetheless instructive for comparing the guarantees given
to transactions in software and in hardware.
Specifically, we use Memalloy to search for a pair of execu-
tions, X and Y, such that X is an inconsistent C++ execution,
Y is a consistent x86/Power/ARMv8 execution, and X is re-
lated to Y via the relevant compilation mapping, encoded
in the relation π. Such a pair would demonstrate that the
compilation mapping is invalid. Wickerson et al. [55] have
encoded non-transactional compilation mappings; we only
need to extend them to handle transactions, which we do by
requiring π to preserve all stxn-edges:
stxnY
=
π −1 ;stxnX ;π.
Memalloy confirmed that compilation to x86, Power, and
ARMv8 is sound for all C++ executions with up to 6 events.
8.3
Checking Lock Elision
We now check the soundness of lock elision in x86, Power,
and ARMv8 using the technique proposed in §4.3.
First, we extend executions with four new event types:
• L, the lock() calls that will be implemented by acquir-
ing the lock in the ordinary fashion,
• U , the corresponding unlock() calls,
• Lt, the lock() calls that will be transactionalised, and
• U t, the corresponding unlock() calls.
When generating candidate executions from programs, we
assume that each lock()/unlock() pair gives rise to a L-U
pair or a Lt-U t pair. (Distinguishing these two modes at the
execution level eases the definition of the mapping relation.)
We obtain from these lock/unlock events a derived scr rela-
tion that forms an equivalence class among all the events
in the same CR. Similarly, scrt is a subrelation of scr that
comprises just those CRs that are to be transactionalised.
Table 3. Key constraints on π for defining lock elision
Source
event, e
Target event(s), π(e)
x86
Power
ARMv8
ARMv8 (fixed)
L
R
R
W
ctrl
rmw
R
W
isync
rmw, ctrl
ctrl
R, Acq
W
rmw, ctrl
R, Acq
W
dmb
rmw, ctrl
po
U
W
sync
W
po
W , Rel
W , Rel
Lt
R
R
R
R
U t
-
-
-
-
Moreover:
slocY = I 2 ∪((¬I)2 ∩(π −1 ;slocX ;π))
(LockVar)
where I = π(L ∪U ∪Lt ∪U t)
scrt \ (¬U t)2 = π ;stxnY ;π −1
(TxnIntro)
empty([L];π ;rf ;π −1 ;[Lt])
(TxnReadsLockFree)
Second, we extend execution well-formedness so that ev-
ery L event must be followed by a U event without an inter-
vening Lt or U t, and so on.
Third, the consistency predicates from Figs. 5, 6, and 8 are
extended with the following axiom that forces the serialis-
ability of CRs.
acyclic(weaklift(po ∪com, scr))
(CROrder)
Finally, we define a mapping π from the events of an
‘abstract’ execution X to those of a ‘concrete’ execution Y,
that captures the implementation of lock elision. Table 3
sketches the main constraints we impose on π so that it cap-
tures lock elision for x86, Power, and ARMv8. It preserves
all the execution structure except for lock/unlock events.
The LockVar constraint imposes that all the reads/writes
in Y that are introduced by the mapping (call these I) ac-
cess the same location (i.e., the lock variable) and that this
location is not accessed elsewhere in Y. The TxnIntro con-
straint imposes that events in the same transactionalised
CR in X become events in the same transaction in Y. The L
and U events are mapped to sequences of events that rep-
resent the recommended spinlock implementation for each
architecture. Each L event maps to a successful RMW on
the lock variable, which in ARMv8 is an acquire-RMW [7,
§K.9.3.1], in Power is followed by a control dependency3 and
an isync [29, §B.2.1.1], and in x86 is preceded by an addi-
tional read (the ‘test-and-test-and-set’ idiom) [31, §8.10.6.1].
Each U event maps to a write on the lock variable, which
in ARMv8 is a release-write [7, §K.9.3.2], and in Power is
3In Power, ctrl edges can begin at a store-exclusive [47].
12


The Semantics of Transactions and Weak Memory
PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
L
R x
W x
U
Lt
W x
U t
R, Acq m
W m
R x
W x
W , Rel m
R m
W x
fr
co
po
po, data
po
po
po
po, rmw, ctrl
po
po, data
po
po
fr
fr
co
co
fr
Figure 10. A pair of executions that demonstrates lock eli-
sion being unsound in ARMv8
preceded by a sync [29, §B.2.2.1]. Each Lt event maps to a
read of the lock variable. This read does not observe a write
from an L event (TxnReadsLockFree), to ensure that it sees
the lock as free. Finally, U t events vanish (because we do not
have explicit events for beginning/ending transactions).
Figure 10 shows a pair of ARMv8 executions, X (left) andY
(right), and a π relation (dotted arrows), that satisfy all of the
constraints above. From this example, which was automati-
cally generated using Memalloy in 63 seconds, we manually
constructed the pair of litmus tests shown in Example 1.1. It
thus demonstrates that lock elision is unsound in ARMv8.
This example is actually one of several found by Memalloy;
we provide another example in §B.
We also used Memalloy to check lock elision in x86 and
Power, and again in ARMv8 after applying the fix proposed
in §1.1 (appending a DMB to the lock() implementation).
Given that each architecture implements L events with a
different number of primitive events (Tab. 3), we ensured
that the event count was large enough in each case to allow
examples similar to Fig. 10 to be found. We were unable
to find bugs in any of these cases, but Memalloy timed out
before it could verify their absence. As such, we cannot claim
lock elision in x86 and Power to be verified, but the timeout
provides a high degree of confidence that these designs are
bug-free up to the given bounds because, as Tab. 2 shows,
when counterexamples exist they tend to be found quickly.
9
Related Work
In concurrent but independent work, Dongol et al. [23] have
also proposed adding TM to the x86, Power, and ARMv8
memory models. Like us, Dongol et al. build their axioms by
lifting relations from events to transactions. However, their
models are significantly weaker than ours, because they
capture only the atomicity of transactions, not the ordering
of transactions. Because of this, their Power model is too
weak to validate the natural compiler mapping from C++.
This is demonstrated by the following execution, which is
forbidden by C++ (owing to an hb cycle), but allowed by their
Power model (though not actually observable on hardware).
W x
W y
R y
R x
po
rf
po
fr
Moreover, unlike our work, Dongol et al.’s models have not
been empirically validated – and nor have earlier models that
combine TM and weak memory [20, 41]. Nonetheless, our
models being stronger than Dongol et al.’s implies that our
endeavours are complementary: our experiments validate
their models, and their proofs carry over to our models.
Cerone et al. [16] have studied the weak consistency guar-
antees provided by transactions in database systems. A key
difference is that for Cerone et al., weak behaviours are at-
tributed to weakly consistent transactions, but in our work,
weak behaviours are attributed to weakly consistent non-
transactional events surrounding strongly consistent trans-
actions. Nonetheless, similar axiomatisations can be used in
both settings, and similar weak behaviours can manifest.
Our models follow the axiomatic style, but there also ex-
ist operational memory models for x86 [44], Power [48],
ARMv8 [45], and C++ [43]. It would be interesting to con-
sider how these could be extended to handle TM.
Other architectures and languages that could be targetted
by our methodology include RISC-V, which plans to incorpo-
rate TM in the future [54], and Java. Indeed, Grossman et al.
[25] and Shpeisman et al. [51] identify several tricky corner
cases that arise when attempting to extend Java’s weak mem-
ory model to handle transactions, and our methodology can
be seen as a way to automate the generation of these.
Regarding the analysis of programs that provide TM, an
automatic tool for testing (software) TM implementations
above a weak memory model has been developed by Manovit
et al. [42]. Like us, they use automatically-generated litmus
tests to probe the implementations, but where our test suites
are constructed to be exhaustive and to contain only ‘interest-
ing’ tests, their tests are randomly generated. Regarding the
analysis of programs that use TM, we note that the formula-
tion of the C++ memory model by Lahav et al. [38] leads to an
efficient model checker for multithreaded C++ Kokologian-
nakis et al. [37]. Since our C++ TM model builds on Lahav
et al.’s model, it may be possible to get a model checker for
C++ TM similarly.
Regarding tooling for axiomatic memory models in gen-
eral: our methodology builds on tools due to Wickerson et al.
[55] and Lustig et al. [40], both of which build on Alloy [35].
Related tools include Diy [3], which generates litmus tests by
enumerating relaxations of SC. Compared to Diy, Memalloy
is more easily extensible with constructs such as transactions,
and only generates the tests needed to validate a model. Mem-
Synth [14] can synthesise memory models from a corpus of
litmus tests and their expected outcomes, though it does not
currently handle software models or control dependencies.
13


PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
Nathan Chong, Tyler Sorensen, and John Wickerson
10
Conclusion
We have extended axiomatic memory models for x86, Power,
ARMv8, and C++ to support transactions. Using our exten-
sions to Memalloy, we synthesised meaningful sets of litmus
tests that precisely capture the subtle interactions between
weak memory and transactions. These tests allowed us to
validate our new models by running them on available hard-
ware, discussing them with architects, and checking them
against technical manuals. We also used Memalloy to check
several metatheoretical properties of our models, including
the validity of program transformations and compiler map-
pings, and the correctness – or lack thereof – of lock elision.
Acknowledgements
We are grateful to Stephan Diestelhorst, Matt Horsnell, and
Grigorios Magklis for extensive discussions of TM and the
ARM architecture, to Nizamudheen Ahmed and Vishwanath
HV for RTL testing, and to Peter Sewell for letting us ac-
cess his Power machine. We thank the following people
for their insightful comments on various drafts of this work:
Mark Batty, Andrea Cerone, George Constantinides, Stephen
Dolan, Alastair Donaldson, Brijesh Dongol, Hugues Evrard,
Shaked Flur, Graham Hazel, Radha Jagadeesan, Jan Kończak,
Dominic Mulligan, Christopher Pulte, Alastair Reid, James
Riely, the anonymous reviewers, and our shepherd, Julian
Dolby. This work was supported by an Imperial College
Research Fellowship and the EPSRC (EP/K034448/1).
References
[1] Allon Adir, Dave Goodman, Daniel Hershcovich, Oz Hershkovitz,
Bryan Hickerson, Karen Holtz, Wisam Kadry, Anatoly Koyfman, John
Ludden, Charles Meissner, Amir Nahir, Randall R. Pratt, Mike Schliffli,
Brett St Onge, Brian Thompto, Elena Tsanko, and Avi Ziv. 2014. Verifi-
cation of Transactional Memory in POWER8. In Design Automation
Conference (DAC). https://doi.org/10.1145/2593069.2593241
[2] Sarita V. Adve and Mark D. Hill. 1990.
Weak Ordering - A New
Definition. In Int. Symp. on Computer Architecture (ISCA).
https:
//doi.org/10.1145/325096.325100
[3] Jade Alglave, Luc Maranget, Susmit Sarkar, and Peter Sewell. 2010.
Fences in Weak Memory Models. In Computer Aided Verification (CAV).
https://doi.org/10.1007/978-3-642-14295-6_25
[4] Jade Alglave, Luc Maranget, Susmit Sarkar, and Peter Sewell. 2011.
Litmus: Running Tests Against Hardware. In Int. Conf. on Tools and
Algorithms for Construction and Analysis of Systems (TACAS). https:
//doi.org/10.1007/978-3-642-19835-9_5
[5] Jade Alglave, Luc Maranget, and Michael Tautschnig. 2014. Herding
cats: modelling, simulation, testing, and data-mining for weak memory.
ACM Trans. on Programming Languages and Systems (TOPLAS) 36, 2
(2014). https://doi.org/10.1145/2627752
[6] Jade Alglave, Luc Maranget, and Michael Tautschnig. 2014. Herd-
ing cats: modelling, simulation, testing, and data-mining for weak
memory (online companion material). (2014). http://moscova.inria.fr/
~maranget/cats/model-power/all.html#sec4.
[7] ARM. 2017. ARMv8 Architecture Reference Manual. https://static.docs.
arm.com/ddi0487/b/DDI0487B_a_armv8_arm.pdf
[8] Mark Batty, Mike Dodds, and Alexey Gotsman. 2013. Library Abstrac-
tion for C/C++ Concurrency. In ACM Symp. on Principles of Program-
ming Languages (POPL). https://doi.org/10.1145/2429069.2429099
[9] Mark Batty, Alastair F. Donaldson, and John Wickerson. 2016. Over-
hauling SC atomics in C11 and OpenCL. In ACM Symp. on Principles
of Programming Languages (POPL). https://doi.org/10.1145/2914770.
2837637
[10] Mark Batty, Kayvan Memarian, Kyndylan Nienhuis, Jean Pichon-
Pharabod, and Peter Sewell. 2015. The Problem of Programming
Language Concurrency Semantics. In Europ. Symp. on Programming
(ESOP). https://doi.org/10.1007/978-3-662-46669-8_12
[11] Armin Biere. 2010. Lingeling, Plingeling, PicoSAT and PrecoSAT at
SAT Race 2010. Technical Report 10/1. Institute for Formal Models
and Verification, Johannes Kepler University. http://fmv.jku.at/papers/
Biere-FMV-TR-10-1.pdf
[12] Colin Blundell, E. C. Lewis, and Milo M. K. Martin. 2006. Subtleties of
Transactional Memory Atomicity Semantics. IEEE Computer Architec-
ture Letters 5, 2 (2006). https://doi.org/10.1109/L-CA.2006.18
[13] Hans-J. Boehm and Sarita V. Adve. 2008. Foundations of the C++
Concurrency Memory Model. In ACM Conf. on Programming Language
Design and Implementation (PLDI). https://doi.org/10.1145/1379022.
1375591
[14] James Bornholt and Emina Torlak. 2017. Synthesizing Memory Mod-
els from Framework Sketches and Litmus Tests. In ACM Conf. on
Programming Language Design and Implementation (PLDI).
https:
//doi.org/10.1145/3062341.3062353
[15] Harold W. Cain, Brad Frey, Derek Williams, Maged M. Michael, Cathy
May, and Hung Le. 2013. Robust Architectural Support for Transac-
tional Memory in the Power Architecture. In Int. Symp. on Computer
Architecture (ISCA). https://doi.org/10.1145/2485922.2485942
[16] Andrea Cerone, Giovanni Bernardi, and Alexey Gotsman. 2015. A
Framework for Transactional Consistency Models with Atomic Visi-
bility. In Int. Conf. on Concurrency Theory (CONCUR). https://doi.org/
10.4230/LIPIcs.CONCUR.2015.58
[17] JaeWoong Chung, Michael Dalton, Hari Kannan, and Christos
Kozyrakis. 2008.
Thread-Safe Dynamic Binary Translation using
Transactional Memory. In Int. Symp. on High Performance Computer
Architecture (HPCA). https://doi.org/10.1109/HPCA.2008.4658646
[18] William W. Collier. 1992. Reasoning about Parallel Architectures. Pren-
tice Hall.
[19] Luke Dalessandro and Michael L. Scott. 2009. Strong Isolation is a
Weak Idea. In ACM Workshop on Transactional Computing (TRANSACT).
http://transact09.cs.washington.edu/33_paper.pdf
[20] Luke Dalessandro, Michael L. Scott, and Michael F. Spear. 2010.
Transactions as the Foundation of a Memory Consistency Model. In
Int. Conf. on Distributed Computing (DISC). https://doi.org/10.1007/
978-3-642-15763-9_4
[21] Will Deacon. 2016.
The ARMv8 Application Level Memory
Model. https://github.com/herd/herdtools7/blob/master/herd/libdir/
aarch64.cat. (2016).
[22] Dave Dice, Yossi Lev, Mark Moir, and Dan Nussbaum. 2009. Early
Experience with a Commercial Hardware Transactional Memory Im-
plementation. In Int. Conf. on Architectural Support for Programming
Languages and Operating Systems (ASPLOS). https://doi.org/10.1145/
2528521.1508263
[23] Brijesh Dongol, Radha Jagadeesan, and James Riely. 2018. Transactions
in Relaxed Memory Architectures. In ACM Symp. on Principles of
Programming Languages (POPL). https://doi.org/10.1145/3158106
[24] Shaked Flur, Kathryn E. Gray, Christopher Pulte, Susmit Sarkar, Ali
Sezgin, Luc Maranget, Will Deacon, and Peter Sewell. 2016. Modelling
the ARMv8 Architecture, Operationally: Concurrency and ISA. In
ACM Symp. on Principles of Programming Languages (POPL). https:
//doi.org/10.1145/2837614.2837615
[25] Dan Grossman, Jeremy Manson, and William Pugh. 2006. What Do
High-Level Memory Models Mean for Transactions?. In ACM Workshop
on Memory Systems Performance & Correctness (MSPC). https://doi.org/
10.1145/1178597.1178609
14


The Semantics of Transactions and Weak Memory
PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
[26] Mark Hachman. 2014. Intel finds specialized TSX enterprise bug
on Haswell, Broadwell CPUs. PCWorld (August 2014). http://www.
pcworld.com/article/2464880
[27] Tim Harris, James Larus, and Ravi Rajwar. 2010.
Transactional
Memory (2nd ed.).
Morgan & Claypool.
https://doi.org/10.2200/
S00272ED1V01Y201006CAC011
[28] Maurice Herlihy and J. Eliot B. Moss. 1993. Transactional Memory:
Architectural Support for Lock-Free Data Structures. In Int. Symp. on
Computer Architecture (ISCA). https://doi.org/10.1145/173682.165164
[29] IBM. 2015. Power ISA (Version 3.0).
[30] Intel. 2017.
6th Generation Intel Processor Family: Specifica-
tion Update.
(June 2017).
https://www3.intel.com/content/
dam/www/public/us/en/documents/specification-updates/
desktop-6th-gen-core-family-spec-update.pdf
[31] Intel. 2017. Intel 64 and IA-32 Architectures: Software Developer’s Manual.
https://software.intel.com/en-us/articles/intel-sdm
[32] Intel Developer Zone. 2012. Transactional Synchronization in Haswell.
(February 2012). https://software.intel.com/en-us/blogs/2012/02/07/
transactional-synchronization-in-haswell
[33] ISO/IEC. 2011. Programming languages – C++. International standard
14882:2011.
[34] ISO/IEC. 2015. Technical Specification for C++ Extensions for Transac-
tional Memory. Draft technical specification. http://www.open-std.
org/jtc1/sc22/wg21/docs/papers/2015/n4514.pdf
[35] Daniel Jackson. 2012. Software Abstractions – Logic, Language, and
Analysis (revised ed.). MIT Press.
[36] Eric H. Jensen, Gary W. Hagensen, and Jeffrey M. Broughton. 1987.
A New Approach to Exclusive Data Access in Shared Memory Multi-
processors. Technical Report 97663. Lawrence Livermore National
Laboratory. https://e-reports-ext.llnl.gov/pdf/212157.pdf
[37] Michalis Kokologiannakis, Ori Lahav, Konstantinos Sagonas, and Vik-
tor Vafeiadis. 2018. Effective Stateless Model Checking for C/C++
Concurrency. In ACM Symp. on Principles of Programming Languages
(POPL). https://doi.org/10.1145/3158105
[38] Ori Lahav, Viktor Vafeiadis, Jeehoon Kang, Chung-Kil Hur, and Derek
Dreyer. 2017. Repairing Sequential Consistency in C/C++11. In ACM
Conf. on Programming Language Design and Implementation (PLDI).
https://doi.org/10.1145/3062341.3062352
[39] Leslie Lamport. 1979. How to Make a Multiprocessor Computer That
Correctly Executes Multiprocess Programs. IEEE Trans. Comput. C-28,
9 (1979). https://doi.org/10.1109/TC.1979.1675439
[40] Daniel Lustig, Andrew Wright, Alexandros Papakonstantinou, and
Olivier Giroux. 2017. Automated Synthesis of Comprehensive Memory
Model Litmus Test Suites. In Int. Conf. on Architectural Support for
Programming Languages and Operating Systems (ASPLOS). https://doi.
org/10.1145/3037697.3037723
[41] Jan-Willem Maessen and Arvind. 2007. Store Atomicity for Transac-
tional Memory. Electronic Notes in Theoretical Computer Science 174, 9
(2007). https://doi.org/10.1016/j.entcs.2007.04.009
[42] Chaiyasit Manovit, Sudheendra Hangal, Hassan Chafi, Austen McDon-
ald, Christos Kozyrakis, and Kunle Olukotun. 2006. Testing Implemen-
tations of Transactional Memory. In Int. Conf. on Parallel Architectures
and Compilation Techniques (PACT). https://doi.org/10.1145/1152154.
1152177
[43] Kyndylan Nienhuis, Kayvan Memarian, and Peter Sewell. 2016. An
Operational Semantics for C/C++11 Concurrency. In ACM Int. Conf.
on Object-Oriented Programming, Systems, Languages, and Applications
(OOPSLA). https://doi.org/10.1145/3022671.2983997
[44] Scott Owens, Susmit Sarkar, and Peter Sewell. 2009. A Better x86
Memory Model: x86-TSO. In Theorem Proving in Higher Order Logics
(TPHOLs). https://doi.org/10.1007/978-3-642-03359-9_27
[45] Christopher Pulte, Shaked Flur, Will Deacon, Jon French, Susmit Sarkar,
and Peter Sewell. 2018. Simplifying ARM Concurrency: Multicopy-
atomic Axiomatic and Operational Models for ARMv8. In ACM Symp.
on Principles of Programming Languages (POPL). https://doi.org/10.
1145/3158107
[46] Ravi Rajwar and James R. Goodman. 2001. Speculative Lock Elision:
Enabling Highly Concurrent Multithreaded Execution. In Int. Symp.
on Microarchitecture (MICRO). https://doi.org/10.1109/MICRO.2001.
991127
[47] Susmit Sarkar, Kayvan Memarian, Scott Owens, Mark Batty, Peter
Sewell, Luc Maranget, Jade Alglave, and Derek Williams. 2012. Syn-
chronising C/C++ and POWER. In ACM Conf. on Programming Lan-
guage Design and Implementation (PLDI).
https://doi.org/10.1145/
2254064.2254102
[48] Susmit Sarkar, Peter Sewell, Jade Alglave, Luc Maranget, and Derek
Williams. 2011. Understanding POWER Multiprocessors. In ACM
Conf. on Programming Language Design and Implementation (PLDI).
https://doi.org/10.1145/1993498.1993520
[49] Dennis Shasha and Marc Snir. 1988. Efficient and Correct Execution
of Parallel Programs that Share Memory. ACM Trans. on Programming
Languages and Systems (TOPLAS) 10, 2 (1988). https://doi.org/10.1145/
42190.42277
[50] Tatiana Shpeisman, Ali-Reza Adl-Tabatabai, Robert Geva, Yang Ni,
and Adam Welc. 2009. Towards Transactional Memory Semantics for
C++. In Symp. on Parallelism in Algorithms and Architectures (SPAA).
https://doi.org/10.1145/1583991.1584012
[51] Tatiana Shpeisman, Vijay Menon, Ali-Reza Adl-Tabatabai, Steven
Balensiefer, Dan Grossman, Richard L. Hudson, Katherine F. Moore,
and Bratin Saha. 2007. Enforcing Isolation and Ordering in STM.
In ACM Conf. on Programming Language Design and Implementation
(PLDI). https://doi.org/10.1145/1273442.1250744
[52] Tyler Sorensen, Alastair F. Donaldson, Mark Batty, Ganesh Gopalakr-
ishnan, and Zvonimir Rakamarić. 2016. Portable Inter-workgroup Bar-
rier Synchronisation for GPUs. In ACM Int. Conf. on Object-Oriented
Programming, Systems, Languages, and Applications (OOPSLA). https:
//doi.org/10.1145/2983990.2984032
[53] Srdan Stipić, Vesna Smiljković, Osman Unsal, Adrián Cristal, and Ma-
teo Valero. 2013. Profile-Guided Transaction Coalescing—Lowering
Transactional Overheads by Merging Transactions.
ACM Trans-
actions on Architecture and Code Optimization 10, 4 (2013). https:
//doi.org/10.1145/2541228.2555306
[54] Andrew Waterman and Krste Asanović (Eds.). 2017. The RISC-V In-
struction Set Manual, Volume I: User-Level ISA (version 2.2). RISC-V
Foundation. https://riscv.org/specifications/
[55] John Wickerson, Mark Batty, Tyler Sorensen, and George A. Con-
stantinides. 2017. Automatically Comparing Memory Consistency
Models. In ACM Symp. on Principles of Programming Languages (POPL).
https://doi.org/10.1145/3009837.3009838
[56] Michael Wong. 2014. Transactional Language Constructs for C++. In
C++ Conference (CppCon). http://bit.ly/2tWk4uz
A
Proposed Amendment to the
Transactional C++ Specification
A.1
Original Text
The original text is as follows [34, §1.10]:
1. There is a global total order of execution for all outer
blocks. If, in that total order, T1 is ordered before T2,
• no evaluation in T2 happens before any evaluation in
T1 and
• ifT1 andT2 perform conflicting expression evaluations,
then the end of T1 synchronizes with the start of T2.
15


PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
Nathan Chong, Tyler Sorensen, and John Wickerson
A.2
Proposed Text
To accommodate the proposal from §7, we propose the fol-
lowing replacement text:
1. An operation A communicates to a memory operation B
on the same object M if:
• A and B are both side effects and A precedes B in the
modification order of M;
• A is a side effect, B is a value computation, and the
value computed by B is the value stored either by
A or by another side effect C that follows A in the
modification order of M; or
• A is a value computation, B is a side effect, and B
follows in the modification order of M the side effect
that stored the value computed by A.
2. The end of outer transaction T1 synchronises with the
start of outer transaction T2 if an operation in T1 com-
municates to an operation in T2.
B
A Second Example of Lock Elision Being
Unsound in ARMv8
Memalloy found a second example of lock elision being un-
sound in ARMv8. It is a variant of Example 1.1, in which
rather than an external store interrupting a read-modify-
write operation, we have an external load observing an inter-
mediate write. Specifically, the program below must never
satisfy the given postcondition:
Initially: [X0] = x = 0
lock()
lock()
MOV W5,#1
store
twice
to x
LDR W7,[X0] load x
STR W5,[X0]
unlock()
MOV W5,#2
STR W5,[X0]
unlock()
Test: W7 = 1
However, if the left thread executes its CR non-transactionally
while the right thread uses lock elision, then the resultant
program can satisfy that postcondition:
Initially: [X0] = x = 0, [X1] = m = 0
1 Loop:
atomically
update m
from 0
to 1
3 TXBEGIN
begin txn
LDAXR W2,[X1]
LDR W6,[X1] load m
and abort
if non-
zero
CBNZ W2,Loop
CBZ W6,L1
4 MOV W3,#1
TXABORT
STXR W4,W3,[X1]
L1:
CBNZ W4,Loop
LDR W7,[X0] load x
2 MOV W5,#1
store
twice
to x
TXEND
end txn
STR W5,[X0]
5 MOV W5,#2
STR W5,[X0]
STLR WZR,[X1]
m ←0
Test: W7 = 1
As in Example 1.1, the numbers next to the instructions
indicate the order in which they can execute in order to
satisfy the postcondition. This example is interesting because
it shows that not only can loads be executed speculatively
before a successful store-exclusive (STXR) completes, but so
can stores.
C
Proof of Theorem 7.3
Theorem 7.3 (Transactional SC-DRF guarantee). If a C++-
consistent execution has
• no relaxed transactions (i.e. stxn = stxnat),
• no non-SC atomics (i.e. Ato = SC), and
• no data races (i.e. NoRace holds),
then it is consistent under TSC.
In order to prove this theorem, let us assume the three con-
ditions that the theorem assumes, and show that acyclic(po∪
com) and acyclic(stronglift(po ∪com, stxn)) both hold. In
what follows, we write pocom for po∪com, poloc for po∩sloc,
po,loc for po\sloc, poSC
loc for poloc ∩SC2, and rf SC for rf ∩SC2.
Lemma C.1. In race-free executions, communication (other
than that between two SC events) induces happens-before; i.e.,
com \ SC2
⊆
hb.
Proof. Consider two non-SC events related by com. If they
are in the same thread, then HbCom guarantees that they
are in po, and hence in hb. If they are in different threads,
then NoRace and HbCom guarantee that they are in hb.
□
Lemma C.2. In the absence of non-SC atomics, we can sim-
plify happens-before as follows:
hb
=
(po ∪rf SC ∪tsw)+.
Proof. Recall that happens-before is defined via hb = (po ∪
sw ∪tsw)+, where
sw
=
[Acq];([F];po)? ;[W ];poloc∗;[W ∩Ato];
(rf ;rmw)∗;rf ;[R ∩Ato];(po ;[F])? ;[Rel].
In the absence of non-SC atomics, this simplifies to
sw
⊆
po∗;(rf SC ;po)∗;rf SC ;po∗
from which the result follows.
□
Proof of acyclic(pocom)
Suppose toward a contradiction that there is a pocom cycle.
If the pocom cycle passes through no atomics, then each
edge of the cycle is either a po (and hence an hb), or a non-
atomic com edge (and hence an hb by Lemma C.1). Hence,
we have an hb cycle. These are forbidden by HbCom, so we
have a contradiction. So, we can henceforth assume that the
pocom cycle passes through at least one atomic.
Let us divide the cycle at each atomic event, so that each
segment of the cycle begins at an atomic, then passes through
a chain of zero or more non-atomics, before finishing at an
atomic. Each segment thus takes the form:
seg
=
[SC];pocom;([¬SC];pocom)∗;[SC].
(4)
Lemma C.3. seg ⊆hb ∪co ∪fr.
16


The Semantics of Transactions and Weak Memory
PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
Proof. If the segment is a single pocom edge between two SC
events, then that edge is either in po ∪rf SC (and hence in
hb) or is in co ∪fr, as required. Otherwise, the segment is of
the form
•
pocom;[¬SC]
−−−−−−−−−→•
([¬SC];pocom;[¬SC])∗
−−−−−−−−−−−−−−−−−→•
[¬SC];pocom
−−−−−−−−−→•,
and is hence in hb by Lemma C.1, as required.
□
If there are fewer than two non-hb segments in our cycle,
then we have an immediate violation of HbCom. So, we can
henceforth assume that at least two segments in our cycle
are in (co ∪fr) \ hb. Moreover, we can assume that these
segments are not consecutive, for if they were, the co ∪fr
edges would collapse together. We can hence consider our
cycle to be built from chains of segments of the following
form:
X ′ (co ∪fr) \ hb
−−−−−−−−−→X
hb
−−→Z
(co ∪fr) \ hb
−−−−−−−−−→Z ′
where X ′, X, Z, and Z ′ are all in SC. In fact, we can further
assume
(X ′,Z) < hb
(X,Z ′) < hb
(5)
for otherwise the cycle would still collapse into an HbCom
violation.
To complete the proof, it suffices to show that (X,Z) is in
psc+, for then the entire cycle becomes a psc cycle and hence
a violation of the SeqCst axiom. The precise definition of
psc is quite involved [38]; here we just rely on
[SC];po,loc ;hb ;po,loc ;[SC]
⊆
psc
(6)
[SC];pocom;[SC]
⊆
psc
(7)
Consider the hb chain from X to Z. If it passes through no
intermediate non-SC events, then it must be a sequence of po
and rf SC edges (by Lemma C.2). All of these edges are in psc,
so we have (X,Z) ∈psc+ as required. So, we can henceforth
assume that the hb chain passes through at least one non-SC
event.
Let Y be the last non-SC event in the chain (i.e., the closest
to Z). The following two lemmas analyse the (Y,Z) and
(X,Y) parts of the chain separately.
Lemma C.4. The hb chain from Y to Z contains a po,loc edge
that is followed only by rf SC and poSC
loc edges; i.e.,
(Y,Z) ∈hb∗;po,loc ;(rf SC ∪poSC
loc)∗.
Proof. Consider the final part of the hb chain. By Lemma C.2,
each edge in the chain is a tsw, a po, or an rf SC. Any suffix
of rf SC or poSC
loc edges can be removed, with the remaining
part of the chain still ending at an SC event. The last of the
remaining edges cannot be a tsw because we are at an SC
event, and atomics are forbidden inside atomic transactions.
Moreover, if it is a po,loc edge then we are done. Hence, it
remains only to consider the possibility that it is a poloc edge
that begins at a non-SC event. This would mean we have
Y
hb∗
−−→A
poloc ;(rf SC ∪poSC
loc)∗
−−−−−−−−−−−−−−−→Z
(co ∪fr) \ hb
−−−−−−−−−→Z ′
for some non-SC event A. Note that A and Z ′ cannot be
related by hb, because (Z ′,A) ∈hb would be a HbCom viola-
tion, and (A,Z ′) ∈hb would imply (X,Z ′) ∈hb, in contra-
diction of assumption (5). Since Z ′ is a write, it forms a data
race with A. This contradicts our NoRace assumption, and
hence the proof is complete.
□
Lemma C.5. The hb chain from X to Y contains a po,loc edge
that is preceded only by rf SC and poSC
loc edges; i.e.,
(X,Y) ∈(rf SC ∪poSC
loc)∗;po,loc ;hb∗.
Proof. Consider the initial part of the hb chain. By Lemma C.2,
each edge in the chain is a tsw, a po, or an rf SC. Any prefix
of rf SC or poSC
loc edges can be removed, with the remaining
part of the chain still beginning at an SC event. The first of
the remaining edges cannot be a tsw because we are at an
SC event, and atomics are forbidden inside atomic transac-
tions. Moreover, if it is a po,loc edge then we are done. Hence,
it remains only to consider the possibility that it is a poloc
edge ending at a non-SC event, say A. The next edge after
A cannot be another po because two consecutive po edges
would collapse together, and it cannot be an rf SC because A
is non-SC, so it must be a tsw edge. This implies that there
is another non-SC event between A and Z, and hence that A
is not Y. We therefore have
X ′
X
A
B
C
D
Y
(co ∪fr) \ hb
(rf SC ∪poSC
loc)∗;poloc
tsw
stxn
ecom
stxn
hb∗
for some non-SC events A, B, C, and D. Note that X ′ and B
cannot be related by hb, because (B,X ′) ∈hb would be a
HbCom violation, and (X ′, B) ∈hb would imply (X ′,Z) ∈hb,
in contradiction of assumption (5). This reasoning is also
valid with C substituted for B. At least one of B and C must
be a write, by the definition of ecom, and hence at least one of
them forms a data race with X ′. This contradicts our NoRace
assumption, and hence the proof is complete.
□
By combining Lemmas C.4 and C.5, we can deduce that
(X,Z) is in
(rf SC ∪poSC
loc)∗;po,loc ;hb∗;po,loc ;(rf SC ∪poSC
loc)∗
and is hence in psc∗;psc ;psc∗, as required.
17


PLDI’18, June 18–22, 2018, Philadelphia, PA, USA
Nathan Chong, Tyler Sorensen, and John Wickerson
Proof of acyclic(stronglift(pocom, stxn))
For this proof, we shall rely on one further lemma.
Lemma C.6. Happens-before edges can be lifted to relate
transactions; i.e.,
stxn∗;(hb \ stxn);stxn∗
⊆
hb \ stxn
Proof. It suffices to prove the following two inequalities:
stxn;(hb \ stxn)
⊆
hb \ stxn
(8)
(hb \ stxn);stxn
⊆
hb \ stxn.
(9)
We shall provide a proof of (8); that of (9) is similar. We begin
by noting that the following identity of Kleene algebra
(r ∪s)+
=
r + ∪(r ∗;s ;(r ∪s)∗)
can be combined with Lemma C.2 to give
hb \ stxn
⊆
(po ∩stxn)∗;(po \ stxn ∪rf SC ∪tsw);hb∗.
Hence, to show (8), it suffices to suppose a chain of the form
V
stxn
−−−→W
(po ∩stxn)∗
−−−−−−−−−→X
po \ stxn ∪rf SC ∪tsw
−−−−−−−−−−−−−−−−−→Y
hb∗
−−→Z
and deduce that (V,Z) ∈hb. We do so by a case-split on
the (X,Y) edge. First, the case (X,Y) ∈rf SC is impossible
because X is in an atomic transaction and hence cannot be
atomic. Second, if (X,Y) is in po \ stxn, then so is (V,Y), and
the result follows. Third, if (X,Y) is in tsw, then so is (V,Y)
and the result follows.
□
Now, suppose toward a contradiction that there is a cycle
in stronglift(pocom, stxn). Such a cycle is made up of stxn
and pocom edges, with at least one edge in pocom \ stxn.
Suppose the cycle passes through no atomics. If the cycle
includes no stxn edges, then we simply have a pocom cycle,
which is a contradiction because we have already proved
acyclic(pocom). If, on the other hand, the cycle includes at
least one stxn edge, then we can divide the cycle at the trans-
actions, so that each segment of the cycle is of the form
stxn;(pocom \ stxn)+ ;stxn
and hence, by Lemma C.1, of the form stxn;(hb \ stxn)+;stxn.
Lemma C.6 then implies that this cycle is in hb, and is hence
forbidden. So, we can henceforth assume that the cycle passes
through at least one atomic.
Let us divide the cycle at each atomic event, so that each
segment of the cycle begins at an atomic, then forms a chain
of pocom and stxn edges through zero or more non-atomics,
before finishing at an atomic. The first and last edge of each
segment cannot be an stxn, however, since each segment
begins and ends at an atomic. As a result, Lemma C.3 still
holds under the new definition of a segment, because any
stxn edges in the segment can be folded into the adjacent hb
edges using Lemma C.6. The rest of the proof is identical to
that of acyclic(pocom).
18
