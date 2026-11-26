# Next experiment: topology-derived temporal organization

Status: proposed; not executed or preregistered as a complete executable specification.

## Question
Can a recurrent medium with uniform local update laws acquire useful temporal organization through mutable topology, without assigned fast/slow roles or explicit novelty detection?

## Candidate construction
Use a finite directed graph of recurrent nodes with bounded activity. All nodes use the same local transition law. External ports emit and receive signals. Local changes to connections have resource costs and decay. A fixed external scheduler may implement asynchronous interactions. Cycles of differing lengths are possible, but no designated timescale registers. Record every supplied primitive, initialization distribution, scheduler and structural update rule. Freeze equations and numerical parameters before held-out evaluation.

## Controls
Matched fixed graph, randomized rewiring at equal cost, open-loop or shuffled echo (preserve marginal statistics), state reset, topology reset, and fixed/mutable filter bank; include optimized adaptive filtering (e.g. Kalman where appropriate), with tuning on separate training worlds. Match emitted energy, observation access, storage, update count and wall-clock budget or report Pareto comparisons. Same seeds and worlds across arms; log failures and extinctions.

## Evaluation
Separate training, calibration and held-out worlds: stable, abruptly switching, drifting, noisy, intermittent, nonlinear and interfering emitters. Measure whole-run alignment or externally defined task utility, post-shift recovery, energy/work/storage, robustness and causal effect of matched ablations. Measure impulse response and temporal structure with fixed external instruments, not self-reported labels. Use paired seed intervals, report all outcomes and distinguish exploratory sweeps from confirmation.

## Defeat criteria
- Persistence is not informative if randomized coupling produces equal persistence.
- Memory unsupported if historical-state erasure has no behavioral effect.
- Grounding unsupported if shuffled or disconnected echoes retain performance.
- Adaptive advantage unsupported if equal-resource fixed or conventional controls match it.
- Abstraction unsupported without held-out transfer.
- Meta-adaptation unsupported if gain is explained by supplied transformation rule or resource advantage.
- Correctability fails if admissible external interventions cannot change entrenched organization; shutdown alone does not count.
- Visual complexity is not evidence of cognition.

Before execution freeze exact metrics, thresholds, sample sizes, budgets and code revision. No claim of emergent reasoning without an operational definition and independently authored tasks. Preserve all raw outputs and negative results.
