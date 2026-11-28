# Hexcore: geometry of affordable discovery — exploratory mathematical note

## Scope and status

This is a deterministic finite hypothesis-identification construction. It is not a new law of intelligence, an independently authored benchmark, a proof of P=NP, or a simulation of Hexcore's proposed medium. The constructions were designed for this investigation. Costs count ideal binary queries and a separately declared interface-switch charge; they do not include model construction, physical sensing, policy planning, or storage. The decision-tree recurrence is standard. Novelty of the particular construction has not been established.

## Construction

Let k >= 3, N=2^k and m=N/2. The world is one of N known hypotheses, represented by a k-bit label w, initially unknown. All tests are deterministic and cost one. We require zero-error identification in the worst case.

Fast family F: for each integer mask a in 1,...,m+1, output the parity of the bitwise intersection a & w. The family includes all k coordinate tests. All m+1 queries are distinct and balanced.

Slow family S: represent a world as (g,j), with group g in {0,1} and index j in {0,...,m-1}. Define q0(g,j)=g and q_i(g,j)=g XOR [j=i] for each i=0,...,m-1 (here q0 denotes the base separately from the indexed swap queries; the code stores the base first). Each swap flips one world in each group. All m+1 queries are distinct and balanced.

Both families therefore have the same count of probes and one bit of single-query mutual information under a uniform prior. Each pair of distinct worlds is separated by some query in each family. This does not say that the discriminating query can be selected from the unknown world's identity, nor that mutual information remains one bit conditional on prior observations.

## Exact minimax depth

F: a binary decision tree with N leaves has worst-case depth >= k. Reading the coordinate queries attains k.

S: consider a transcript of zero outcomes. Every query excludes at most one candidate from the g=0 group. Therefore fewer than m-1 queries cannot distinguish the world: at least two group-0 candidates remain. For the matching upper bound, query any m-1 distinct swap probes. Group-0 response strings have weight at most 1 and group-1 strings have weight at least m-2. Since m>=4, these sets are disjoint. Within a group the one-flip position identifies the index, and no flips identifies the omitted index. Thus m-1 nonadaptive probes suffice. Exact depth is m-1.

The ratio (2^(k-1)-1)/k diverges. Equal initial entropy reductions and pairwise separation costs do not bound global identification complexity by a constant factor.

## Adaptive interface change

Start in S. Allow one irreversible switch to F at known nonnegative integer charge r, preserving the entire past transcript, without revealing new information at the switch. Both configurations can support an unrelated constant present task perfectly (a deliberately trivial present task control).

Exact minimum worst-case cost is min(m-1, r+k).

Upper bound: either solve in S, or switch immediately and read k coordinate queries.

Lower bound: follow an all-zero slow-query path until switching or until m-1 probes. If no switch occurs before m-1, cost is at least m-1. If switching happens immediately, at least k binary observations are required afterward. After one slow query the posterior has m candidates, so one plus ceil(log2(m)) equals k. After b>=2 slow queries, at least m-b candidates remain. If b<m-1, then b+ceil(log2(m-b)) >= k (the integer function b+ceil(log2(m-b)) is nondecreasing for 1<=b<=m-2 and equals k at b=1). Subsequent binary identification needs at least ceil(log2(m-b)) observations on some continuation. Hence any switch on that path costs at least r+k in the worst case, unless the policy has already paid at least m-1. This proves the bound.

Relative to starting in F, correction debt in ideal query-cost units is min(r, m-1-k). It is zero if restoration is free and grows with restoration cost until the slow alternative becomes preferable. This is not a universal definition of debt.

## Irreversible probe lock

Construct a third interface with the same initial query family S, but after its first query it allows only repetitions of that query. Its static list of probes is jointly separating, every pair has an initial separating probe, and each first probe has one bit of information. Yet every possible first observation leaves m indistinguishable worlds and no future distinction can be observed. Full exact identification is impossible, even with unlimited repeated-query budget. This is a deliberately designed one-shot channel, not a statement about all mutable media.

## External instrument

With known interface mode c, compatible world set H and deterministic binary queries, the static optimal worst-case decision-tree depth is

V(H)=0 if |H|<=1; otherwise min_q [1+max(V(H0), V(H1))], over nontrivial splits.

For the switch example include r+V_F(H) as an alternative in V_S. In a general finite state-dependent interface, use the set of compatible joint states (world, configuration) rather than H alone when configuration is hidden. This is standard contingent planning / belief-state reachability. A full planner can itself be expensive; the recurrence is an evaluator, not an implementation claim.

## Execution

Run `python hexcore_geometry.py` (Python 3.10+, standard library only). It checks exact DP for k=3,4,5, switch DP for k=3,4 and integer costs 0..m+1, and exhaustively checks unique response signatures and explicit policies for k=3..10. Analytic lower bounds, not DP enumeration, cover the larger cases. The one-shot impossibility follows from balanced queries and the declared lock transition, not a separately simulated dynamical medium.

## Prior-art map and next test

- Arrow–Fisher–Henry quasi-option value: preservation of future decision flexibility and information use. https://doi.org/10.1016/0095-0696(89)90042-9
- Boyd & Sastry (1986): parameter identification depends on sufficient richness in feedback. https://web.stanford.edu/~boyd/papers/para_conv_adaptive.html
- Golovin & Krause (2011): adaptive submodularity and cost-aware acquisition. https://ocs.aaai.org/Library/JAIR/Vol42/jair42-012.php
- Nowak (2009): geometry of generalized binary search, conditions for logarithmic identification. https://arxiv.org/abs/0910.4397
- Cicalese, Laber & Saettler (2014): optimal diagnostic decision-tree costs. https://proceedings.mlr.press/v32/cicalese14.html

The next open question is not whether these known ideas can be renamed. It is whether a compact, transferable certificate can measure how an adaptive transformation changes the future cost of identifying and repairing a relevant distinction, including changes to the instruments themselves. Compare any candidate to ordinary belief-state planning and sequential experimental design; reject a new measure if these absorb it at equal cost. Freeze correction targets, world classes, admissible interventions and resources before evaluation. A transformation can leave the reachable set unchanged, so a universal strict-change law is already false. An information-preserving reversible transformation need not impose correction debt.
