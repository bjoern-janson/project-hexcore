# Causal boundaries, gluing, and the cost of consistency

Status: source reading and a finite classical mathematical illustration, 2026-11-28. The gravitational argument has not been independently validated. This is not a derivation of physics from Hexcore, a priority or influence claim, or a simulation-hypothesis result.

## Source and claim boundary

Venkatesa Chandrasekaran, [An algebraic quantization of gravity from the null cone](https://arxiv.org/abs/2611.34924v1), arXiv:2611.34924v1, submitted November 25, 2026. [Full HTML](https://arxiv.org/html/2611.34924v1). Read the introduction, JT comparison, §§5.1–5.2, Eq. (4.29)–(4.31) and relevant portions of Appendix D.2. Not an exhaustive technical or literature review.

The paper constructs boundary-dressed observables and a quantum representation of four-dimensional vacuum gravity. The argument for finite-dimensional macroscopic causal diamonds (§5.2) is especially interesting because:

- In the JT comparison (§2), bounding the clock does not exclude infinitely many orthogonal states.
- In four dimensions, radiative shear changes the clock reading; the projected clock bound limits corner area (5.21). This is an operator bound in the selected subspace, not a dimension bound by itself.
- The area-dependent gluing weight (5.23) has a positive lower bound on the bounded-area subspace (5.30).
- A relative boost changes a two-sided radiative correlator (5.29). The bounded observable argument (5.32–5.38) uses narrow-area sectors, grouped finite projections and cut/uncut consistency to derive a sign contradiction under the infinite-dimensional hypothesis. Appendix D.3 provides a one-loop check.

The key audit questions are whether the clock and area operators and their domains are controlled in the required representation; whether the approximation and remainder bounds used in D.2 survive the assumed limiting procedure; and whether the cut/uncut gluing identity applies to the trace-like amplitude in (5.38) independently of finite dimensionality. Eq. (4.29) for matrix elements of norm-finite vectors is not by itself an assertion of trace-class convergence. This is a question about the extra hypotheses and proof, not a demonstrated error in the preprint. Representation independence is explicitly left open in footnote 20.

If finite dimensionality holds, it bounds the number of mutually orthogonal states, not the cardinality of all pure states or the complexity of computing arbitrary amplitudes. Even a finite-dimensional Hilbert space can have a continuum of pure states. No efficiency or discrete-spacetime conclusion follows just from finiteness.

## Translation ledger

| Physics object | Hexcore comparison | Standing |
|---|---|---|
| Boundary-dressed observable | A measurement defined through an interaction interface | Analogy; no shared construction map |
| Causal diamond, clock and focusing | Admissible interaction domain with costs affected by dynamics | Analogy; not equivalent to a software budget |
| Cut and uncut amplitudes | Local simulations joined to reproduce a joint observation law | Structural analogy; quantum amplitudes are not classical probabilities |
| Finite-dimensional state space | Finite sufficient interface or state description | Distinct mathematical objects; NO TRANSLATION EARNED |
| Boost-sensitive cross-boundary correlator | Joint observational test exposing dependence absent in local tests | Motivating analogy; exact classical example below |

The gravitational result is not established prior art for the Hexcore medium. Its narrower relevance is as an example of a proposed physical constraint on consistent composition. The classical construction below is entirely independent of the paper's truth.

## Classical boundary information: exact construction

Declare two regions with outputs X and Y. Each is an m-bit string. Under the proposed compositional simulator, a shared finite latent state Z is the only dependence between the regions: X and Y are conditionally independent given Z. Count every shared randomness source, hidden dependency or state that couples their generation as part of Z; independent private randomness is allowed. This is a model of one cut, not a claim about all possible simulation implementations.

For a finite joint probability matrix P, the minimum alphabet size of Z is the nonnegative rank of P. Indeed,

    P(x,y) = sum_z P(z) P(x|z) P(y|z).

Each term has rank at most one. Conversely, normalizing each nonzero term of a nonnegative factorization gives such a mixture. See the established literature on nonnegative rank and latent-variable mixtures, e.g. [From Common Information to Canonical Correlation Analysis and Beyond](https://pmc.ncbi.nlm.nih.gov/articles/PMC13703381/), §2.4. This is standard mathematical machinery, not a novelty claim.

### Two worlds, identical pairwise statistics

Let m >= 3 and N = 2^m. In world I, X and Y are independent uniform strings. In world II, X is uniform and Y = T(X), where the GF(2) linear transformation is

    y_i = x_i XOR x_m       (1 <= i < m)
    y_m = x_1 XOR x_2 XOR x_m.

It is invertible: x_m = y_m XOR y_1 XOR y_2; recover every other x_i from y_i and x_m.

All 2m coordinate functions on X are distinct nonzero binary linear forms: the x_i have weight one, the first m-1 y_i have weight two, and y_m has weight three. Any two distinct nonzero forms over GF(2) are linearly independent, so every two coordinates have a uniform joint distribution. Both worlds therefore agree on every singleton and pair of individual bits, including cross-region pairs. The full marginal string distribution on each side is also uniform in both worlds.

World I has probability matrix J/N^2 (rank 1). World II has a permutation matrix divided by N (rank N). Thus the minimum shared boundary alphabet is 1 versus N, achieved respectively by constant Z and Z=X. A fixed-width boundary needs 0 versus m bits. Equivalently I(X;Y) is 0 versus m bits. Neither fact implies that the required map T is computationally difficult.

### An exact error/capacity frontier

Let a candidate Q use at most K shared states with conditional independence and retain the uniform left marginal. On the event E = {Y=T(X)},

    Q(E) = (1/N) sum_z sum_x Q(z|x) Q(Y=T(x)|z)
         <= K/N.

Here Q(z|x) <= 1 and T is bijective. The true world assigns E probability one. Thus for K <= N,

    TV(P,Q) >= 1 - K/N.

The bound is tight, even with the right marginal also uniform: partition the N strings into K nonempty groups, draw group Z with probability equal to its size divided by N, then independently draw two uniform indexes in the group and apply T to the right index. Each group contributes exactly 1/N match probability. On E the candidate probability at each pair is no greater than the true 1/N; outside E the true probability is zero. Hence TV = 1-Q(E) = 1-K/N. With K >= N the optimum error is zero.

For b shared fixed-width bits and 0 <= b <= m, the exact minimum total variation error in this model is 1-2^(b-m). This is a finite-model resource separation, not a bound on time, hardware, energy or universal world simulation. The proof holds for arbitrary K; the accompanying program checks powers-of-two K only.

## Verification and use

[boundary_check.js](../experiments/boundary-information/boundary_check.js) is a standalone Node.js script; run from any directory with `node boundary_check.js` to reproduce JSON on stdout. [results.json](../experiments/boundary-information/results.json) records an executed deterministic enumeration for m=3,...,12. The program checks bijectivity, all coordinate-pair counts, both uniform marginals of the partition simulator, and exact match counts for every b=0,...,m. Matrix rank and the lower bound follow from the proof, not from numerically estimating matrix rank or exhaustively optimizing all possible simulators.

At m=12, the reference worlds agree on 276 pairwise coordinate tests. The correlated world's exact interface needs 4096 labels. With 11 bits the best total variation error is 1/2; with 8 bits it is 15/16. The independent world's exact interface needs one label.

The result refines the earlier streamed-reality example into a quantitative boundary constraint. It also connects to C0p: sharing a seed, oracle or uncharged global data structure bypasses the proposed budget, not the bound. Conditional independence is essential; interactive protocols or additional shared information require a different contract.

Next: specify a family of adaptive interactions whose allowable cuts change over time. For each cut compare required shared state, actual encoding cost, restoration cost, and whether a compressed boundary preserves future joint tests. Include independent and low-rank baselines, not just constructed hard cases. Do not equate nonnegative rank with ordinary Hankel rank, quantum dimension, gravitational entropy, or a universal computational cost. The substantive open question is whether a medium can discover and maintain suitable boundary representations under independently changing interactions without hiding cost elsewhere.
