"""Exact finite counterexamples to marginal information as a correction-cost proxy.
No model training. All costs are ideal binary oracle queries; switching is separately
charged. The analytic proof is in the accompanying notes, not inferred from runs.
Python 3.10+; standard library only.
"""
import json
from functools import lru_cache
from pathlib import Path


def probes(k):
    n = 1 << k
    m = n // 2
    # Equal numbers of distinct, balanced binary queries. Coordinates included.
    fast = tuple(sum(((w & a).bit_count() & 1) << w for w in range(n))
                 for a in range(1, m + 2))
    # Group bit, with optional flip at one paired index in both groups.
    base = ((1 << m) - 1) << m
    slow = (base,) + tuple(base ^ (1 << j) ^ (1 << (m + j)) for j in range(m))
    return fast, slow


def exact_cost(n, queries):
    @lru_cache(None)
    def v(s):
        if s.bit_count() <= 1:
            return 0
        best = n + 1
        for q in queries:
            a, b = s & q, s & ~q
            if a and b:
                best = min(best, 1 + max(v(a), v(b)))
        return best
    return v


def switching_cost(n, fast, slow, r):
    f = exact_cost(n, fast)
    @lru_cache(None)
    def v(s):
        if s.bit_count() <= 1:
            return 0
        best = r + f(s)
        for q in slow:
            a, b = s & q, s & ~q
            if a and b:
                best = min(best, 1 + max(v(a), v(b)))
        return best
    return v((1 << n) - 1)


def run():
    rows = []
    for k in range(3, 11):
        n = 1 << k
        m = n // 2
        f, s = probes(k)
        assert len(set(f)) == len(set(s)) == m + 1
        assert all(q.bit_count() == m for q in (*f, *s))
        # A unique response signature is equivalent to every pair being
        # distinguished by at least one query. Here each query costs one.
        for qs in (f, s):
            signatures = {tuple((q >> w) & 1 for q in qs) for w in range(n)}
            assert len(signatures) == n
        # Explicit nonadaptive optimal upper bounds, verified on all worlds.
        for qs, depth in ((tuple(f[(1 << j) - 1] for j in range(k)), k),
                          (s[1:m], m - 1)):
            assert len(qs) == depth
            assert len({tuple((q >> w) & 1 for q in qs) for w in range(n)}) == n
        row = dict(k=k, worlds=n, distinct_queries=m+1,
                   single_query_bits=1, max_pairwise_cost=1,
                   fast_proven=k, slow_proven=m-1,
                   one_shot_identification_possible=False)
        if k <= 5:
            full = (1 << n) - 1
            vf, vs = exact_cost(n, f), exact_cost(n, s)
            row['fast_exact_dp'] = vf(full)
            row['slow_exact_dp'] = vs(full)
            assert (row['fast_exact_dp'], row['slow_exact_dp']) == (k, m-1)
            row['dp_states'] = [vf.cache_info().currsize, vs.cache_info().currsize]
        if k <= 4:
            # Include costs exceeding the entire slow-query alternative.
            row['switch_costs'] = []
            for r in range(m+2):
                value = switching_cost(n, f, s, r)
                assert value == min(m-1, r+k)
                row['switch_costs'].append({'r':r, 'exact_dp':value})
        # In the locked interface only one chosen query is ever observable;
        # repeating it yields no new info, so each posterior is size n/2.
        assert all(q.bit_count() == m for q in s)
        rows.append(row)
        print(n, row['fast_proven'], row['slow_proven'], row.get('dp_states', 'analytic + exhaustive policy check'))
    out = {'scope':'deterministic, known finite world class; noiseless unit-cost binary oracle; exact worst-case identification', 'rows':rows}
    Path(__file__).with_name('hexcore_geometry_results.json').write_text(json.dumps(out, indent=2)+'\n')

if __name__ == '__main__':
    run()
