# Bitter Lesson exploratory batch: BL-05–BL-09

This is a new exploratory batch, not a preregistered scientific result or a modification of any existing repository. Its purpose is to probe compounding discovery and correction under explicit information-access and representation constraints. No claim of beating the Bitter Lesson or inventing new mathematics is made.

## Reproduction

Python 3.10+ with NumPy. Run from this directory:

```sh
python bl05.py
python bl06.py
python bl07.py
python bl08.py
python bl09.py
```

BL05's final complete execution uses 16 seeds, 48 tasks and ambient dimensions 8, 10, 12. An earlier, larger attempt was interrupted before full result persistence; its output is not included or merged. BL06 uses 20 seeds and 96 tasks per world. BL07 uses 48 seeds and 96 tasks. Each script writes its own raw JSON; BL05–07 also write summary CSVs. Elapsed times are machine-specific. Query counts, abstract work counters, and wall times are not interchangeable. All five experiments use seeded synthetic generators and supplied mathematical or algorithmic inductive biases. They are not independent tests of a general scaling law.

## Result ledger

| Experiment | Main observation | Claim ceiling |
|---|---|---|
| BL05 | Learned affine support reduces late-stage membership-query costs from ~2097 to ~33.3 at 4096 locations. Lifetime costs ~99141 vs ~16206. | A class-scoped query-complexity advantage. No overall compute or novel-learning mechanism claim. Every localization is completed, so prior defect observations are not free. A known-dimensional affine model and a generic predictive portfolio are supplied. |
| BL06 | Under a 32-query cap at 1024 locations, affine priority attains 80.3% late recall in stable worlds, 1.2% after a full support replacement, and 1.4% recall in the new region of mixed-tail worlds. | Positive-only update under selective observations can miss drift. No claim that all learners share this limitation; the tested learners do not use full negative-query likelihoods. |
| BL07 | Exact finite model inference over 1240 affine flats, with negative likelihood updates and switching prior, raises late shift recall from 1.7% to 40.6% compared with a positive-only switching filter. It loses recall under lower prevalence without support change. | Generic inference partially rescues the BL06 mechanism in a different, smaller environment. Pathwise local observation equivalence for a hidden-tail world and reduced-incidence world is exact by construction. The support-informed oracle is not Bayes-optimal in the unequal-density hidden-tail regime. |
| BL08 | Known finite-field parity construction identifies 0–2 defects among 1024 locations with 21 ideal pooled bits (lower bound 20), whereas individual observations need 1024 in worst case. Reuse of successful monomial constructions cuts pair-check costs, and a symbolic sufficient proof schema identifies four portable exponents. | Coding theory, not a new discovery. Pooled information access is a distinct assumption. Naive emulation reads 11280 bits, and caching the raw full scan also costs N reads. Pair counts exclude decoding/planning and physical measurement cost. Uniform ideal error-set assumptions apply. |
| BL09 | Generic GF(2) polynomial-span search constructs verified algebraic decoder certificates for 96 of 263 polynomial specimens, then decodes 576 sampled pairs across newly generated fields of degree 16,32,64. | All 96 successes are in designed positive-control/monomial families; none of 128 random polynomials is certified. Certificate existence is sufficient, not necessary. The proof target and algebraic machinery are supplied. Large fields use a sparse-index mathematical simulation, not real arrays or aggregate hardware. |

## Strongest surviving observation

A concrete mathematical certificate can replace size-dependent empirical revalidation of an ideal instrument with a proof under specified assumptions. The BL09 search derives identities of the form

`(x+y)^a (xy)^(2^r) = P(x+y, h(x)+h(y))`.

For distinct x,y in a characteristic-two finite field, s=x+y is nonzero, so this identifies `(xy)^(2^r)`. Frobenius inversion recovers xy, and sum/product determine the unordered pair. This is standard algebra. The algorithm finds the polynomial P by linear-span elimination, not by installing the specific inverse formula. The proof schema, field arithmetic and sufficient target are supplied. Independent symbolic expansion checks every accepted identity. Finite-field construction uses the standard Rabin irreducibility criterion. Actual decoder tests at large field sizes are samples, not exhaustive tests of implementation correctness.

The main unresolved question is whether a general learner can acquire useful *new certificate schemas*, not just select or instantiate existing ones, and whether this improves lifetime resource scaling against strong symbolic, learned and library-based baselines. A future experiment should be independently generated, with explicit training costs and a held-out test of proof-schema transfer, rather than more demonstrations within this supplied algebraic family.
