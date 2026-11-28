# Hexcore: reversible dynamics, moving interfaces, and common correction ranks

Status: exact designed examples and finite computational audits; not an independent novelty result, physical thermodynamic model, emergent cognition, or completed mutable medium. Extends `hexcore_geometry_notes.md` and `hexcore_commitment_notes.md`. The earlier commitment examples concern irreversible instrument selection; here the central distinction is between reversible snapshots and the time-dependent availability of a successful policy.

## A. Frozen reversible instruments

The unknown world w is fixed. The observable instrument configuration s is a vertex of a finite undirected graph. Motion is silent, independent of w, and costs one unit per edge. At each vertex a known finite collection of binary readouts of w is available, each costing one unit. Queries do not move the instrument. The controller knows the graph and readout functions, retains the transcript and must identify w exactly from a declared nonempty candidate set H. Costs are deterministic worst-case motion plus query counts, not computational work to plan, build or maintain the graph.

For a fixed graph, let V(s,H) denote optimal cost, infinity if no exact policy exists. With d the graph distance and H_{q,b} the candidate subset consistent with outcome b,

V(s,H) = 0 if |H|=1; otherwise
V(s,H) = min_{p,q informative on H at p} [d(s,p)+1+max_b V(p,H_{q,b})].

In the recurrence inaccessible vertices are excluded and min of the empty set is infinity. The next informative query can be reached by a shortest silent path, because all motion and useless probes reveal nothing. This establishes the recurrence by induction on |H|.

For any reachable anchor a,

V(s,H) <= d(s,a) + V(a,H).

When the only informative readouts are k independent bits at a, and H contains all 2^k worlds, equality holds: no other location provides a bit, and all k must be read. Reversibility alone does not bound d in terms of the bit length of a description.

### A1. Exact exponential separation

For m>=3, label vertices of a cycle of length M=2^m by the binary reflected Gray code g(i)=i XOR (i>>1). Each undirected edge flips one bit, including the closing edge. Both systems start at the physical bitstring s=2^(m-1), have their sole informative readouts at a=0, and provide the same three independent bits of the hidden world at a. A uses ordinary Gray labels, B swaps the highest and second-highest coordinates of every Gray label. Graphs have identical state counts, degrees, edge costs and readout functions. They are isomorphic as unmarked graphs, not as graphs preserving both marked start and anchor. No claim of identical fully labeled local transitions is made.

In A, g(M-1)=s, so the distance to a is one. In B, the Gray inverse of the coordinate-swapped start 2^(m-2) is 2^(m-1)-1, so that is the shortest cyclic distance. Exact costs are C_A=4 and C_B=2^(m-1)+2. This is exponential in the configuration bit count, not in the number of explicit graph vertices. The cycle adjacency can be computed from Gray inversion and increment/decrement using polynomial bit operations; the exponential motion cannot be replaced by a jump because jumps are outside the declared action set. If a new action were allowed to teleport or change coordinates freely, this result would not apply.

### A2. Pairwise witness radius and composition

For |H|=n>=2 define R(s,H) as the maximum over distinct w,w' in H of the minimum travel distance from s to a probe that separates them. R is infinite when no separating probe is reachable. In this fixed undirected model,

V(s,H) finite iff R(s,H) finite.

If R finite, R+1 <= V(s,H) <= (n-1)(2R+1)-R.

Proof: some pair requires travel at least R and one separating observation. For the upper bound choose an unresolved pair, travel from s to a separating probe within R, query, and if unresolved return to s. Every informative query removes at least one candidate; at most n-1 are needed, with no return after the final one. This is an executable strategy, not a guarantee of logarithmic cost. At R=0 singleton probes can require n-1 queries while binary-coordinate probes require log2(n) for n a power of two. This repeats the earlier geometry distinction in a reversible setting.

If, for every non-singleton H' subset of H, a probe within distance B of s splits H' into branches of size at most ceil(|H'|/2), then the same return strategy gives

V(s,H) <= ceil(log2(n)) (2B+1) - B.

This stronger condition is global over subsets. Computing it may be expensive; it must not be advertised as a cheap local diagnostic merely because verifying a chosen split is simple. Generalized binary search and optimal decision-tree literature contain the underlying static ideas.

## B. Time-dependent instruments: the moving maze

Fix a finite set of locations, a protected goal a=0, and a nonempty family G(s) of allowed graph snapshots at each location. In each round the environment chooses a graph from G(s), reveals it, and the controller moves along one current edge or waits. Then the environment can choose anew. Each move or wait costs one unit. The controller knows the current graph, not future choices. The environment is adversarial in the guarantee (it can respond to location); it is not assumed random or oblivious. The allowed family is fixed and history-free in this model. The world w never changes and the graph choices need not depend on w. At a there are three permanently available binary bit probes that identify w in three queries without moving. The correction task is to reach a and read those bits. To extend to actual diagnosis where motion can reveal information, the joint information state must be included explicitly; we do not treat it as a known physical location.

Take N>=3, all star graphs centered at any nonanchor vertex. At nonanchor s choose a center c != s,0. Then s is a leaf whose only neighbor is c, which is also not the anchor. Waiting also stays outside. Repeat after every step. Every snapshot is connected, undirected and has diameter 2; every location has a frozen route of at most two moves to a. Yet the environment can keep the controller outside a indefinitely. Thus the snapshot cost of identification is <=5, while no finite guaranteed cost exists in the switching model. An adversarial schedule reacting to the controller is essential to this particular claim; it is not an impossibility theorem for advance-known schedules, stochastic graphs or all temporal paths. In particular, a prescribed fixed sequence of connected graphs with advance knowledge has different reachability properties. The edges of the snapshot are reversible, not necessarily the whole coupled evolution of graph and location.

## C. A common correction rank is a local progress certificate

For the switching model, define W_0={a},

W_{t+1}= W_t union {s : for every G in G(s), there exists t' in neighbors_G(s) union {s} with t' in W_t}.

Induction shows W_t contains exactly the states from which a policy can reach a within t moves for every admissible graph selection. The quantifier order is environment first and observed, controller second; reversing it changes the problem. The sequence stabilizes after at most |S|-1 strict expansions. For a state outside the fixed point, some admissible graph leaves all allowed moves outside the fixed point. Hence an adversary can avoid the anchor forever. This is the standard reachability-game attractor construction, applied to an instrument that reconfigures between actions.

Define the rank rho(s)=min{t:s in W_t}, infinity outside the attractor. For each finite positive rank and every allowed graph there is a move with strictly smaller rank. Conversely, any nonnegative integer rank with zero only at a and such a descending move at every nonanchor state in its certified domain gives a guaranteed route in at most rho(s) steps; all chosen successors must stay in the domain. The exact rank is the smallest guaranteed deadline. No single common next edge is required: the controller can choose different lower-rank neighbors in different graphs. A different shortest-path distance computed at each snapshot is not sufficient, since changing the graph can increase the next rank before the next action. This resembles a common control Lyapunov/ranking function, not a new general stability theorem.

### C1. Design consequence for Hexcore

A possible fixed external guard is to preserve a bounded, well-founded correction rank even while freely changing the rest of the graph. Each edit must leave, at every certified state, at least one admissible rank-decreasing correction action in every allowed post-edit graph. If this rank is held fixed, the check is local to affected outgoing edges. It permits state-dependent rewiring and alternative routes, rather than freezing the entire organization. It requires an immutable goal, a known/observable state and a controller with access to the appropriate action. It also requires verification that concurrent mutations cannot remove an edge after choice and before execution. Rank construction and maintenance costs are excluded from the numerical toy model; computing a compact certificate can be difficult. This is a prescribed guard, not emergent physics. In a genuine medium, the goal must embody a valid external corrective instrument, not merely a switch that shuts down the medium. Changing the rank itself requires a new global guarantee (or protected transfer rule); local monotonicity in a moving rank is not enough.

An independent boundary condition could instead reserve two consecutive movement steps without rewiring in the star example, making the anchor reachable in <=2 moves. The fixed snapshot distance was verified in code; no physical stoppability, safety or energy claim follows. Future work should compare a protected progress certificate with bounded dwell time, resource-matched checkpoint restoration and no safeguard in a minimal mutable substrate.

## D. Executed checks

Run `python hexcore_reversible.py` and `python hexcore_flux_guard.py` (Python 3.10+ standard library). JSON output is stored next to each script. The static experiment enumerates Gray cycles m=3..8 and checks all full-world starting locations; larger dimensions use the algebraic formula, not materialized graphs. It also audits 100 seeded random small undirected instruments (including disconnected graphs and observational aliasing) across 18,056 non-singleton belief/location cases: 12,483 finite, 5,573 infinite. It verifies pairwise radius equivalence and bounds, 11,746 finite uniform balanced-split bounds, 51,575 anchor inequalities, and three exact radius-zero separations. 94,918 assertion evaluations are counted.

The dynamic experiment verifies all-star adversarial families for 3..12 locations, 150 generated layered families (1,438 states including anchors, 751 nonanchor states with no single common descending neighbor), and 250 additional generated connected-snapshot families (1,366 states; 207 families contain a losing state, 935 losing states). Each rank is checked against an independent finite-horizon minimax recursion and a local winning/losing certificate. The generated family counts are descriptive of that generator only, not estimates for natural systems. 32,639 assertion evaluations are counted. All checks passed. They corroborate finite instances; the proofs supply generality.

## E. Rediscovery ledger and remaining gap

- Transition-system diameter and plan lengths: Abdulaziz et al., *Computing Plan-Length Bounds Using Lengths of Longest Paths* (2021), https://cdn.aaai.org/ojs/17392/17392-13-20886-1-2-20210518.pdf . The exponential construction instantiates this phenomenon for corrective access under unit reversible steps.
- Generalized binary search: Nowak, *The Geometry of Generalized Binary Search*, https://nowak.ece.wisc.edu/GBS_arxiv_v4.pdf . Pairwise separability, balanced splitting and decision-tree costs are established ideas. Added travel/return costs are the declared model here.
- Reachability games and controlled predecessor: Finkbeiner et al., *Causal Solving of Reachability Games*, https://finkbeiner.groups.cispa.de/_assets/paper.xpkOUN7d.pdf . The rank recurrence is directly absorbed into standard attractor theory.
- Temporal exploration under reactive adversaries: *Natural Calamities Demand More Rescuers* (DISC 2025), https://drops.dagstuhl.de/storage/00lipics/lipics-vol356-disc2025/html/LIPIcs.DISC.2025.41/LIPIcs.DISC.2025.41.html . Related examples use changing connectivity to undo progress. Advance-known temporal graphs differ; see https://drops.dagstuhl.de/storage/00lipics/lipics-vol373-sand2026/html/LIPIcs.SAND.2026.20/LIPIcs.SAND.2026.20.html .
- Switched systems: Mason, Boscain & Chitour, *Common Polynomial Lyapunov Functions for Linear Switched Systems* (2006), https://doi.org/10.1137/040613147 . Individual stable modes need not produce stable switched dynamics; common Lyapunov functions certify a form of uniform stability. The discrete controlled rank here is analogous, not a proven translation to that paper's continuous model.

No novelty or universal-law claim is earned. The strongest surviving research direction is the economics of retaining a bounded certificate of common corrective access under allowed self-reorganization, including the cost of constructing and revising the certificate and the uncertainty of its own observation interface. The guard should be evaluated against standard reachability-game synthesis, not renamed as a new cognitive law. No repository changes made in this round.
