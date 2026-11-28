# Hexcore — the geometry of possible interactions

Status: **cross-lineage synthesis and research hypotheses**, November 2026. This is a new reading of the archive, not a claim that its theories have been unified or that the full mutable medium works. No universal law, general intelligence, P = NP result, consciousness theory, or physical simulation hypothesis is established.

## 1. Start with the shared problem

A bounded process cannot maintain or compute every detail. It therefore selects, compresses, specializes, or reorganizes. That changes what can be done and learned next. The recurring question is not whether adaptation always destroys possibilities (it need not), but whether its effects on future *operational* possibilities can be measured, predicted, and eventually constrained.

The July work began with computational leverage, changing representations and preserving correction. The current Hexcore archive contains several routes back to that question: synthesis and inverse search; evolutionary computation; self-modifying recurrent dynamics; causal attribution (C0); learning reusable mathematical structure (BL); exact finite identification and correction games; and interaction-driven simulation. They are not independent confirmations of one law.

The Claude conversation adds two crucial constraints: removing machinery can remove the instrument that detected its failures; and the medium's transformation rules cannot be allowed to redefine the external evaluation. Its hospital example illustrates a decision that stops collecting an observation and thereby removes the evidence that could challenge that decision. The conversation also distinguishes pattern existence from access and knowledge of access. Preserve those distinctions; do not promote metaphorical matches into typed equivalences without construction and tests.

## 2. Put the results next to each other

| Lineage / result | Distinction that survives | What remains unearned |
|---|---|---|
| Computational leverage / early representation experiments | A better encoding can change which tasks fit a fixed budget. | A general method that invents useful encodings at lower lifetime cost than existing methods. |
| Representation elasticity / bounded retention | Compressing for one task can remove correction paths for another. | Guaranteed preservation for genuinely unforeseen tasks. |
| Recursive controllers / synthesis portfolios | More sophisticated machinery can cost more than the benefit it delivers. | Open-ended improvement or superiority to strong ordinary baselines. |
| C0 causal attribution / communication | Causal participation, its observation, and its actionable identification are distinct; selective communication may pay. | Autonomous construction of self-models or emergent message semantics. |
| C0p closure audit | Apparent new reach disappears when macros are expanded and evidence access is matched. | A genuine resource-matched expansion of closure. |
| BL03–07 | Reusing structure saves work but selective observations can conceal changes to the underlying support. | Discovery of arbitrary useful structures or universal protection against drift. |
| BL08–09 | A different observation interface or transferable proof can reduce repeated acquisition/validation work. | Novel certificate schemas discovered without supplied algebraic bias; total compute advantage. |
| Echo flux | Strong reinforcement can saturate the medium; weak plasticity or multiple timescales can help under some noise and shift regimes. | Emergent reasoning; temporal organization without prescribed mechanisms. |
| Geometry | Equal single-probe entropy and pairwise separation do not determine joint discovery cost. | An efficient general instrument for policy-level discovery complexity. |
| Commitment | Every announced proper subset may have the same optimum profile as a safe system although full-set correction is impossible; mean debt can vanish while worst debt grows. | Transfer to natural task families without evaluator-announced side information. |
| Reversible graph | Retaining information and local reversibility do not bound the cost of reaching it. | A compact diagnostic of future repair costs in a large evolving medium. |
| Moving maze | Every frozen graph can be connected and cheaply solvable, yet the trajectory prevents correction indefinitely. | A general, cheaply maintainable guarantee under actual mutable dynamics. |
| Rank transfer | Locally valid certificates can reset progress; a protected deadline suffices in the declared game. | Useful guarantees when construction, validation, observability and timing have real costs. |
| Certificate visibility | A correct rank is not necessarily an actionable witness; stale information can be useless. | General endogenous discovery of timely corrective channels. |
| Streamed reality | Joint observation constraints can be generated lazily without instantiating all latent values. | Advantage over simpler lazy latent models; nonlinear generalization. |
| Interval reality | Compact sufficient statistics can answer large aggregate queries without enumerating the region. | General efficient inference over complex worlds. |

Primary sources: [42-experiment lineage](LINEAGE.md), [C0/BL evidence ledger](../archive/CHAT_EVIDENCE_LEDGER.md), [geometry and reality originals](../archive/geometry-and-reality/README.md). The table is a scope-aware translation, not a proof that mechanisms in different rows are equivalent.

## 3. The proposed common language: affordable experiments

Use a finite, declared model first. A history h contains the observations, actions, relevant exposed costs, and any information about the available interface. The underlying model M specifies how the world and interface respond. Define a policy class Pi(B) whose members can spend no more than budget B on every admissible trajectory. Include refusals, elapsed time and stopping outcomes in the transcript whenever those distinctions matter. The policy cannot depend on hidden true states.

Define the observable behavior of model M after h as the family

    T_B(M,h) = { Law_M(future transcript | h, pi) : pi in Pi(B) }.

The family is indexed by the same policies, not an unordered bag of possible distributions. In cross-model comparisons, specify a common externally available action language, including its cost and failure semantics. We cannot silently give a policy privileged access to a hidden model.

Two histories/models are B-equivalent if the transcript laws coincide for every policy in that common class. An approximate version requires an explicitly declared metric and tolerance. This is standard controlled predictive/trace equivalence specialized to the question of mutable interfaces; not a new theorem of statistical inference. The operational interpretation depends on the policy class, cost metric, horizon, and allowed interventions.

### Three elementary consequences worth keeping together

1. **Budget refinement.** With nested policy classes, equivalence at a large budget implies equivalence at every smaller budget; the converse is false. The large-budget distinction may be completely invisible to a short current test.
2. **Residual-budget consistency.** In finite models with a shared legal action of deterministic cost c, and policy classes closed under prefixing and conditional continuation, equivalence at B implies equal immediate outcome laws. After any shared positive-probability outcome, the two successor histories are equivalent for remaining budget B-c. Proof: prepend the action, then execute any chosen continuation on that outcome and terminate on the others; equality of joint transcript probabilities and nonzero conditioning probability give equality of the conditional suffix laws. If admissibility or costs differ, they must be included in the observable interface and the hypothesis checked. This result does not license discarding distinctions when the future policy class expands.
3. **Composability is a policy property.** Knowing every pair of worlds has some distinguishing experiment is weaker than having one history-dependent policy identifying all worlds within budget. The commitment and moving-maze constructions explicitly separate those statements.

The point is not to rediscover the definitions of predictive equivalence. It is to use a single declared interface for testing the changing ability to discover, act on, and recover distinctions.

## 4. Simulation and intelligence, placed on the same interface

The user proposed that a universe simulator might exploit the same economy as WoW's streamed world, since observers access reality through limited sensory channels and active investigations. This is an engineering analogy, not evidence that the universe is simulated.

A simulator can choose a cheap internal realization that generates the required joint transcript law under all admissible interactions. A learner can try to infer a cheap predictive representation from the transcripts it has encountered. The first has access to the model it implements; the second generally does not. The two optimization problems are not mathematical inverses without additional assumptions.

Nevertheless they share a target: preserve distinctions that matter to future interactions. For a simulator, losing a distinction risks inconsistency when observers zoom, intervene or compare notes. For a learner, losing it risks an obsolete or self-confirming prediction. A learner whose actions alter its own measurement apparatus faces both problems at once.

Established counterparts: [Littman, Sutton & Singh, Predictive Representations of State (2001)](https://proceedings.neurips.cc/paper_files/paper/2001/hash/1e4d36177d71bbb3558e43af9577d70e-Abstract.html) represents state through action-conditioned predictions; [Shalizi & Crutchfield, Computational Mechanics: Pattern and Prediction, Structure and Simplicity (2001)](https://arxiv.org/abs/cond-mat/9907176) develops predictive equivalence and minimal causal-state representations for stochastic processes. [Friston et al., Action and behavior: a free-energy formulation (2010)](https://doi.org/10.1007/s00422-010-0364-z) relates internal generative models to actively sampled sensory data. None proves that the particular Hexcore architecture works. Predictive processing is a theoretical account of cognition, not an exhaustive explanation of human minds.

### Important new connection: prediction is not correction

Predictive sufficiency relative to a fixed future interaction language can be valuable. But the system may itself change that language, by discarding an instrument, narrowing attention, rewriting code, or changing who controls an intervention.

Consequently a representation may be sufficient for the currently available experiments, yet insufficient to evaluate a proposed restoration or an independently expanded interface. Our correction experiments supply concrete examples. Exact equivalence with respect to the *full* extended language and cost budget would already include those tests; we cannot claim a distinction between truly equivalent objects under the very same declared test.

Research question: can a representation preserve cheap access to the distinctions needed when the interface changes, without paying to preserve all raw details indefinitely? Compare retaining the information, retaining a reconstructive handle, retaining only a probabilistic summary, and abandoning the handle. Charge each option for storage, operation, future acquisition and repair.

This is the candidate bridge between representation elasticity, correction debt, active sensing and streamed simulation.

## 5. Causal mass and joint histories

The user's proposed causal-divergence quantity was Phi = KL(P(X | you) || P(X | not-you)). Replace conditioning with a specifically defined intervention and a declared target X; removing a person or process is not a unique intervention. Do not identify this notation with integrated information theory or treat it as a universal scalar of personhood or consciousness.

For the two binary observations in the streamed-reality example, the intervention preserves both marginals but swaps joint agreement probability from 0.9 to 0.1. Each marginal KL is zero, while the joint KL is 0.8 log2(9), about 2.536 bits. Allocating compute independently to each observable misses the change. This is a standard joint/marginal and data-processing phenomenon, but it gives a sharp test for a causal-streaming instrument.

For a fixed policy shared across two finite interaction models, let h_t be its transcript before action a_t, and let P and Q denote the two induced laws. Under common support (or appropriate extended-real conventions), the KL chain rule gives

    KL(P(transcript) || Q(transcript))
      = sum_t E_P[ KL(P(o_t | h_t,a_t) || Q(o_t | h_t,a_t)) ].

The action-policy factors cancel because the same observation-based policy is used in both models. Include cost/refusal and any other relevant output in o_t; use a common fixed finite horizon or an explicit termination symbol. This is standard divergence decomposition, not a novel causal law. See Lattimore & Szepesvari, Bandit Algorithms (2020), Lemma 15.1 for a bandit specialization.

A useful candidate measurement is the supremum of that divergence over admissible policies at budget B. It is monotone under nested budgets, can be infinite, is directional, and is not in general a metric or a correction-cost bound. Supremizing over policies is itself potentially expensive. A transcript divergence under a selected policy can miss effects that a different policy or an expanded observation interface would expose.

## 6. Timing is part of information

A certificate may accurately describe what action was useful at observation time without helping at execution time. The hidden-mode experiment shows a switch from one-step correction to no deterministic finite guarantee when an adversary can select an unobserved mode on each round. The rank alone does not resolve which action works. In the one-step message model, the minimum number of labels is a hitting-set size, not necessarily the number of hidden modes.

This suggests three quantities to measure together: the timescale of architectural transformation, the latency and information cost of the observation, and the latency and work needed to execute a corrective intervention. No universal inequality between average rates follows. Relative phase, schedules, observability, mode persistence, action overlap and adversarial power can decide the outcome at the same mean rates. A protected deadline or atomic witness is a sufficient device only under the specified reachability model; it is not automatically a mechanism for intelligence.

## 7. A candidate organizing object, not a universal law

The emerging research object is the budget-indexed family of policies through which a system can discover distinctions, act on them and restore the ability to discover them after reorganization.

One possible scalar summary is a correction-cost profile C(S, target, environment, resource contract), including expected, worst-case and tolerated-error variants. Relative to a fixed reference, their differences can be called correction debt. Different variants need not agree, and costs may be infinite. There is no single canonical task distribution or unit of cost. Profiles may have different shape even when all measured present scores agree.

The candidate universal statement is deliberately weaker than "every adaptation changes its future options": adaptive transformations **may** change the structure of operationally reachable future interactions; current success alone does not guarantee its preservation. The negative examples demonstrate this under specific models. To become a substantive universal principle, the program needs an invariant or bound that survives explicit translations across independently chosen models, not just a definition that makes the conclusion true.

## 8. Where the next experiments should meet

Keep the original [topology protocol](PROTOCOL.md) distinct. A proposed bridge experiment is specified in [INTERACTION_TEST.md](INTERACTION_TEST.md). It gives simulation, active sensing, correction debt, multiobserver consistency and mutable interfaces a common finite assay with actual resource accounting. It does not prescribe the eventual Hexcore substrate and has not been executed or preregistered.

The long-term goal remains: make the subject fluid while the evidence, cost ledger and external intervention rights remain fixed. Don't mistake coherent mutual feedback for grounding. Don't mistake low measured error for preservation of corrective access. Don't confuse a cheaper representation with a cheaper world, or a new name with a new result.
