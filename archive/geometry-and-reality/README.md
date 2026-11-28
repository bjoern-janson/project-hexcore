# Geometry of discovery and streamed reality — November 2026

Historical continuation of the Hexcore research conversations. The 20 original files in this directory were imported byte-for-byte and checked against their Git blob hashes. The four mathematical notes contain proofs, scope, execution details and prior-art references. This import did not independently replay or certify the experiments.

| Files | Subject | Historical result and claim ceiling |
|---|---|---|
| [Geometry](hexcore_geometry_notes.md), [code](hexcore_geometry.py), [results](hexcore_geometry_results.json) | Equal one-query information and pairwise separation, unequal composition | Exact finite construction: logarithmic vs linear worst-case discovery cost; repair-cost formula within the stated oracle model. |
| [Commitment](hexcore_commitment_notes.md), [code](hexcore_commitment.py), [results](hexcore_commitment_results.json) | Irreversible choice of instrument | Identical optimal-cost profiles on all announced proper subsets, but full-set identification impossible without repair; mean and worst-case repair debt can diverge. |
| [Reversibility and flux](hexcore_flux_guard_notes.md), [reversible code](hexcore_reversible.py), [results](hexcore_reversible_results.json), [flux code](hexcore_flux_guard.py), [results](hexcore_flux_guard_results.json) | Reversible movement; changing topology | Exponential separation in travel cost, frozen connected graphs that fail when switched, and sufficient common-rank conditions. Standard reachability-game machinery. |
| [Rank transfer and visibility](hexcore_rank_transfer_notes.md), [rank code](hexcore_rank_transfer.py), [results](hexcore_rank_transfer_results.json), [visibility code](hexcore_certificate_visibility.py), [results](hexcore_certificate_visibility_results.json) | Revision of certificates, deadlines, and observable witnesses | Valid certificates can fail to compose; externally conserved deadline prevents reset; identical ranks need not provide actionable information. |
| [Relational reality code](hexcore_streamed_reality.py), [results](hexcore_streamed_reality_results.json) | Joint observations and interventions | Relational and lazy-latent simulations preserve consistency in a parity world; independent observation caching fails. The lazy-latent baseline is cheaper in this implementation. |
| [Interval reality code](hexcore_interval_reality.py), [results](hexcore_interval_reality_results.json) | Hierarchical aggregate observations | A virtual 2^40-cell binary world can answer this restricted family of interval-parity queries lazily. Not a general-purpose simulation of 2^40 independent physical cells. |

Read [the synthesis](../../docs/SYNTHESIS.md) for connections to prior Hexcore lineages and established science. The archived results remain exploratory and model-scoped; newly proposed cross-domain statements do not replace the original notes. Some scripts use paths tied to the original execution environment; reproduce on a separate branch or in a disposable directory.

[GIT-BLOB-SHA1SUMS.txt](GIT-BLOB-SHA1SUMS.txt) records the original-file identities. No new license has been assigned.
