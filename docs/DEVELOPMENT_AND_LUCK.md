# How the products of interaction change later interactions

Status: exploratory synthesis, 2026-11-28. No universal law, solution to P versus NP, account of consciousness, demonstration of open-ended improvement, or autonomous discovery of a computational substrate is established. This document connects the results of four historical experiment batches without changing them. It is not a new completed experiment.

## 1. What the experiments actually changed

| Batch | Object retained across stages | Observation | Strongest surviving qualification |
|---|---|---|---|
| [Chemistry](../archive/development-and-luck/hexcore_chemistry/README.md) | Fully constructed Boolean expressions | At an input-vocabulary expansion from four to five, all six inheritance variants lose to their corresponding cold starts in mean target coverage. | Inherited small fragments do not clearly beat matched random fragments. Not evidence against all cumulative evolution. |
| [Development](../archive/development-and-luck/hexcore_development/README.md) | Statistical construction rules inferred from successful small trees | Balanced eight-input coverage reaches 63.96/64 versus 1.62 for lifetime uniform search and 17.79 for literal fragment reuse. | A stronger fixed mixture reaches 60.75; ordinary expert selection matches the learned grammar and runs faster. Shifting the family can erase the entire advantage. |
| [Law discovery](../archive/development-and-luck/hexcore_law_discovery/README.md) | Compact arithmetic law within a supplied grammar | All 48 held-out trees match in each of six deliberately expressible environments after five observations. | Four of the six selected laws are not uniquely identified by five observations. Out-of-language and observationally aliased worlds fail. Active observation incurs additional fitting costs. |
| [Luck](../archive/development-and-luck/hexcore_luck/README.md) | Randomly encountered reusable NAND templates | At five inputs, mixed-generator coverage rises from 8.19 to 14.09 on the fresh follow-up bank. | NAND-only coverage falls from 160.84 to 83.31; total full-support coverage falls from 6236.22 to 4377.22. Systematically constructed templates match or exceed accidental reuse on the mixed banks. |

The first and follow-up protocols, original source code, available logs, and original-file custody status are in [the archive](../archive/development-and-luck/README.md). The table is a reading guide to previously executed work, not a new comparison under one common experimental contract.

## 2. The smallest common construction

Let S be an organization's current state, E its environment, and I an admissible interaction. A fixed external contract specifies costs, observation access and resources. An interaction has a consequence

    (S', E') ~ K(. | S, E, I).

There is no assumption that the available interactions or their probabilities remain unchanged. Products may enter S or E, altering the admissible and affordable interactions that follow. This is a framework, not a claim that every transformation changes those possibilities or that all such changes are beneficial.

For a declared finite set X of candidate discoveries, let p_A(x; B) be the probability that a policy A has encountered x at least once by budget B. This is an inclusion probability; the p_A values need not sum to one. For nonnegative weights v(x), linearity of expectation gives

    E[sum of v(x) over distinct discoveries] = sum_x v(x) p_A(x; B).

A policy can improve this expectation for one valuation and reduce it for another. It is at least as good for every nonnegative valuation if and only if it weakly increases every inclusion probability. Necessity follows by taking a valuation supported on one x; sufficiency follows term by term. In particular, increased coverage on a target bank together with decreased total coverage rules out universal improvement on the measured domain in expectation. This elementary identity explains the luck experiment's trade-off without asserting a new law of intelligence.

The distinction between a possibility existing in the language and being found within a budget is the same operational distinction studied in [SYNTHESIS.md](SYNTHESIS.md). Execution closure need not change for the distribution of affordable discoveries to change.

## 3. Retention is not activation

The recent discussion isolated a distinction absent from the initial framing: preserving a lucky discovery need not require repeatedly using it. Separate:

- The live organization, whose interactions generate further variation.
- Stored structures or reconstructive descriptions, including access and retrieval cost.
- The policy allocating work between new exploration and reuse.

An archive can protect gains while exploration continues elsewhere. But it is not free: maintenance consumes resources; retrieving or reconstructing a structure costs time; a once-useful record can become obsolete. Preservation without use may retain an option, not realized capability. A stored code, trace or key must not be treated as equivalent to the full structure if the reconstruction cost has disappeared from the ledger.

A monotonic best-so-far score is possible by definition under fixed scoring, unlimited or sufficient memory, and exact recall of earlier artifacts. It does not prove monotonic deployed capability under changing tasks, limited storage or changing validation conditions. Keep historical discovery, simultaneously resident capability, and affordably recoverable capability separate.

## 4. Development reconstructs rather than merely retains

A finished construction need not survive if a procedure for constructing it remains affordable. Such a procedure can alter the distribution over later forms even when it does not expand the underlying computational language.

The biological comparison is deliberately narrow: heredity preserves information and cellular machinery used in development, rather than transmitting the complete developed adult. Modern biological learning, development and evolution interact at different scales; neither the statistical grammar nor the arithmetic-law search in this archive reproduces those mechanisms. Cells and tissues also regulate further growth through chemical and mechanical feedback. A resulting structure may change the constraints on its own continuation.

This gives the medium a possible additional design question: can its products alter the conditions of reconstruction without an evaluator installing a new growth law? Distinguish the cost of acquiring a rule, maintaining it, expressing it, and finding when it no longer applies.

## 5. Commitments can be profitable without being universally safe

The latest discussion rejects a requirement that every lineage remain optimal in every environment. Specialization is not automatically failure; it can be beneficial under an explicit ecology and lifetime resource contract. But a claim that subsequent gains will compensate earlier losses is a hypothesis, not an accounting identity.

If r_t is a resource reserve, g_t a realized gain and c_t a realized cost, then

    r_(t+1) = r_t + g_t - c_t.

With a hard failure boundary at r < 0, an ultimately positive hypothetical sum is insufficient: the process must remain viable until the compensating gains arrive. The order, size, cost and dependence of opportunities matter. Rare discoveries may dominate cumulative gains; they may also be too rare to occur before failure. These statements require distributions or worst-case schedules to become quantitative.

Let A_i(B_i) denote the random set found by lineage i. Population discovery is the union of these sets; it is not the sum of their cardinalities. Shared ancestry, communication and selection may make them strongly dependent. Independent lineages with equal probability p of an event would produce it at least once with probability 1-(1-p)^L for L lineages, but independence and equal per-lineage budgets cannot simply be assumed. At fixed total budget, partitioning resources can hurt as well as help.

The animal analogy motivates parallel specialization, niche differentiation, persistence and extinction, rather than one universal best architecture. It does not establish that artificial diversification has a net benefit. Protection of evaluation and external intervention remains a separate requirement; ecological survival is not a substitute for truth, cooperation, or correctability.

## 6. Why the process can accelerate

The output of one construction may reduce the cost of further constructions. That possibility appears in our earlier computational leverage work, the use of reusable operations, the transfer of developmental rules, and the web's use of common interaction standards.

For a simple reuse calculation, an operation with one-time construction cost a and subsequent use cost c is cheaper over k equivalent uses than an alternative with per-use cost d only if a + kc < kd, with storage, validation and coordination included in the relevant costs. The savings can be reinvested in discovering other operations. It does not follow that the rate of discovery must increase indefinitely.

Common interfaces can reduce the number of distinct adapters needed to connect many parties, at the cost of shared protocol requirements. This is an illustration of constraints enabling combinations. In a simplified model with one adapter per participant, n adapters replace up to n(n-1)/2 pair-specific adapters; the conclusion depends on the shared interface actually supporting those interactions and on its implementation costs. The transcript about the development of the web was a source of this architectural analogy, not an empirical study of Hexcore.

There is an equally important reverse effect. An interaction that consumes useful products but reduces the resources sustaining their production may raise current utility and diminish future availability. This is the same general question of how success modifies the conditions of subsequent success. The specific contemporary claims about web publishers, frontier AI research and mathematical breakthroughs are not established by these experiments.

The later conversation compared accelerating evolutionary, cultural and computational feedback cycles. Treat this as motivation for measuring how discoveries affect the rate and cost of further discovery, not as evidence of a singularity, recursive self-improvement at scale, or a timeline to any particular breakthrough. No rumored solution to a mathematical problem is recorded as a result here.

## 7. Next experiment: lifetime discovery across niches

**Proposed only.** The new experimental target is whether persistent, differentially activated, and composable discoveries improve the lifetime distribution of discoveries in a changing environment at fixed aggregate cost.

Before execution, declare a finite construction language and an independently generated sequence of task or observation families, with distinct periods of stability, abrupt replacement, recurrence and interference. Hide held-out target families from the search. Define a resource ledger covering primitive execution, search, storage, acquisition, reconstruction, migration, messaging and evaluation. If targets affect resource allocation, record that access contract separately from a blind search.

Use matched arms: fresh search; cumulative live reuse; a retained but independently activated archive; ordinary systematic library learning; multiple independent populations; interacting specialized populations with the same total resources; and a fixed portfolio baseline. Separate population diversity from the advantage of simply running more programs. Preserve unsuccessful and extinct runs rather than conditioning on survivors.

Measure total and distribution-specific distinct coverage; affordable reconstruction after recurrence; elapsed work before first rare success; survival and extinction; retained vs active information; correlation and overlap between lineages; and transfer to independently authored held-out families. Report lifetime costs and robustness across change schedules, not merely the strongest realized run. Strong conventional comparators, genuine held-out evidence and the earlier correction/visibility instruments remain necessary.

A positive result is scoped if it only changes proposal probabilities. If expansion costs, storage or interference erase the advantage, record that. If conventional selection, program synthesis or library learning matches, record absorption. If the population preserves its score by making relevant failures unobservable, withdraw the claimed correction advantage.

The aim is not to engineer a requirement that every discovery be useful. It is to investigate the conditions under which finite, fallible processes can retain, combine and sometimes relinquish discoveries so that future useful discoveries become more accessible.
