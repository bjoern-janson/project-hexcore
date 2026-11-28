# Hexcore: global correction under irreversible instrument choice

Status: exact designed mathematical examples, not an empirical discovery of a universal law. No claim of new mathematics, physical thermodynamics, emergent cognition, or end-to-end computational advantage. This is an extension of `hexcore_geometry_notes.md`. The preceding switch-cost proof survives the mixed-policy objection: an all-zero slow transcript supplies its lower bound; the prior exact switching recurrence was also replayed for k=3,4,5 and all integer restoration charges from zero through N/2+2 (37 conditions).

## Model and comparator

Let N>=4 be even, with a fixed unknown world x in {0,...,N-1}. The evaluator announces a nonempty candidate subset H before the experiment. There is a silent one-unit commitment action selecting one of N/2 modes. In bad interface B, mode j makes exactly the pair (2j,2j+1) indistinguishable: the observed label is z=x except z=2j when x=2j+1. The world itself never changes, and no historical physical information is deleted. Subsequently the only observations are binary thresholds [z<t], t=1,...,N-1, each costing one. No return or mode switch is allowed, except a separately declared repair action at cost r, which sets z=x and is available only after commitment; r=infinity disables it. Repair does not reveal a bit, but all later thresholds observe the true label. All previously received outputs are retained. Interface A is identical except mode 0 uses z=x immediately. Both interfaces have the same action alphabet, cost schedule, world class and repair availability. No restart, cloning, outside measurement, or direct access to x is permitted. The instrument choices and repair semantics are supplied by the experimenter.

Costs are ideal query/action units. Binary-query planning, storage, precision, simulator construction, and implementation overhead are excluded. Candidate-set announcements are side information and need not be available in an actual deployment. Deterministic exact identification with known H and a uniform prior within H is the primary task. Expected and worst-case costs are optimized separately. All claims about the impossibility of exact identification apply to zero-error policies, not arbitrary tolerated error.

## Theorem 1: high-order obstruction

For every nonempty proper H, A and B have identical optimum worst-case and uniform expected costs (with or without repair). Singletons need no action. Otherwise, let h=|H| and k_h=ceil(log2 h). At least one matching pair has an endpoint outside H. Choosing its mode yields distinct z labels on H. Thresholds can implement a balanced alphabetic decision tree on the sorted labels. The minimum worst-case number of queries is k_h and the minimum total query cost over h equally likely worlds is h(k_h+1)-2^k_h. This is the standard minimum external path length of a binary prefix tree with h leaves (optimal depths k_h-1 and k_h). The silent commitment adds one to each world's cost, and the lower bounds follow because only binary observations reveal information and all commitments cost one. Thus the two cost profiles coincide for every proper subset, not just pairs.

For H equal to the whole world set, A solves using mode 0 and binary search. B without repair has no zero-error policy, because every possible first commitment merges a pair observationally forever. Adaptive choice of later thresholds cannot separate this pair. Randomization cannot guarantee zero error either: for every committed mode one pair remains indistinguishable, and a uniform prior assigns nonzero mass to that pair.

A predictor given only the complete proper-subset optimum cost profile cannot identify full-set correctability for this class. This is a restriction on a particular measurement interface, not an impossibility for a full structural audit; raw readout tables can distinguish A and B. Also, the policies on subsets are allowed to differ and know the announced subset. One common policy required to solve all subsets without that side information is a different test.

## Theorem 2: exact finite correction debt

Now take N=2^k, k>=2, and integer r>=0. For the full set, the optimal worst and uniform expected costs for A are k+1. For B the exact costs are:

- r=0: worst=mean=k+1.
- integer r>=1: worst = 1+max(k+1,r+2); mean = 1+k+2r/N.
- r=infinity: exact identification impossible.

Proof of worst case: Remove the initial unit commitment from the accounting. If r>=1, some world must incur repair, so a total remaining budget k cannot suffice: after removing unary repair transitions, the binary query tree would have N=2^k distinct leaves at depths <=k, with at least one leaf of depth <k, contradicting Kraft's inequality. A worst budget is an integer, so it is at least k+1. On the still-indistinguishable pair's branch, a repair before any informative query must be followed by a decision tree with worst depth >=k; if at least one query precedes repair, at least one must follow to separate the pair. Either case costs at least r+2 in the worst case. The two lower bounds apply to every initial mode. For a matching upper bound, choose mode 0 and ask whether z<2. If yes, repair and ask one threshold; otherwise binary-search the other N-2 labels without repair. Cost after commitment is at most max(r+2,1+ceil(log2(N-2)))<=max(r+2,k+1). For r=0 repair immediately and binary-search.

Proof of mean: Any zero-error tree for N equiprobable states needs >=k binary queries on average (Kraft or entropy); repair conveys no information itself. At least the two worlds of the chosen hidden pair must undergo repair, so mean repair cost is >=2r/N. This holds also under initial randomization independent of x. Choose mode 0, perform ordinary balanced binary search with thresholds, then repair only when the candidate set becomes {0,1}, before the last threshold. Every world uses exactly k queries, only the hidden pair incurs repair, and the lower bounds are simultaneously attained. Therefore the mean and worst optima above are exact, though not necessarily attained by the same policy.

Consequently relative to A, worst-case debt is max(1,r+2-k) for integer r>=1, and expected debt is 2r/N. Choosing r=2^floor(k/2) makes mean debt vanish with increasing k while worst debt diverges. For N=2^20 and r=1024, mean debt=0.001953125 query units and worst debt=1006 units. Proper-subset profiles still coincide. This separates global worst-case restoration cost from average restoration cost and all conditional proper-subset costs under the model.

## Corollary: near-perfect accuracy without zero-error correctability

With no repair and a uniform full-set prior, the best accuracy of B is exactly 1-1/N. Each instrument has N-1 observable equivalence classes; all singleton classes can be identified and one world in the doubleton correctly guessed. Random uniform commitment and an unbiased guess within the pair achieve probability of error 1/N for each world separately, while no policy can guarantee zero error. A high score and arbitrarily low per-world error probability therefore do not imply exact worst-case repairability. A does not have this obstruction.

## The information-preservation distinction

The full state (x,mode) retains x. The loss is not loss of physical state information, but loss of operational access to it. This does not claim a physically reversible thermodynamic process: commitment is an irreversible control transition without the external repair handle. A general sufficient guard, from classical finite-state testing, is to use only experiments that do not merge still-distinct candidates without revealing which was present. Even preserving physical labels is insufficient if all future observations alias them. Inspect the reachable behavioral quotient, not just physical injectivity. See references below.

## Verification

Run `python hexcore_commitment.py` using Python 3.10+ and the standard library. It uses a memoized exact minimax and expected-cost decision-tree recurrence over candidate subsets and all thresholds, with repair as a separate paid alternative. It checks 5,166 proper-subset comparisons (4,362 distinct nonempty proper subsets across N=4,8,12, plus finite repair repeats), 44 full-set cases over N=4,8,16,32 and finite/unavailable repair, and two explicit analytic policies over 786,408 world runs each for N up to 65,536. The proofs, not the tests, establish larger-size results. The exact recurrence optimizes worst and mean separately; expected cost is computed as an integer sum over all possible true worlds. `hexcore_commitment_results.json` contains the finite audit. No runtime comparison is claimed. 

## Rediscovery / prior-art ledger

- Moore-style machine identification and Lee & Yannakakis, *Testing finite-state machines: state identification and verification* (1994), https://doi.org/10.1109/12.272431: known distinction between pairwise separation, preset and adaptive distinguishing sequences; exact identification is a standard problem.
- Hierons & Türker, *Incomplete Distinguishing Sequences for Finite State Machines* (2015), https://doi.org/10.1093/comjnl/bxv041: explicitly studies distinguishable subsets when a full distinguishing sequence is absent. The high-order obstruction here belongs to that literature; no claim of priority.
- *State identification for labeled transition systems with inputs and outputs* (2021), https://doi.org/10.1016/j.scico.2021.102678: injective splitting and avoidance of transitions that erase relevant distinctions; closely related to the guard discussed above.
- Binary prefix codes and Kraft's inequality: exact query-cost bounds. The mean/worst distinction is standard. The conjunction of identical proper-subset optimum profiles, a reversible-access charge, and diverging mean/worst debt is a designed example to stress-test Hexcore's measurement instrument, not a verified new research contribution.
- Option value, active information acquisition, control and identifiability from the previous round remain relevant but have not been formally identified with this model. Translation status: analogy/related formalism, not identical.

## Next attack

Seek a compact certificate of a common *safe* information policy, rather than auditing all subfamilies. Compare a proposed local-to-global guard against standard adaptive distinguishing sequence algorithms, full joint-state belief planning, and behavioral equivalence. Freeze the declared target, admissible queries, side information, repair costs, and resource constraints. Do not treat restoring physical state, powering off the simulator, or a favorable average reward as a proof of retained corrective access. Record whether a proposed guard is merely a renaming of known theory; if absorbed, keep the counterexample as an evaluation control rather than promoting a new universal principle.
