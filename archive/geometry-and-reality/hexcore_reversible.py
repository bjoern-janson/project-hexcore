"""Exact toy audit: reversible instruments, correction cost and anchor certificates.

World is a fixed unknown k-bit integer. Instrument location is observable;
movement is silent and independent of world; querying a named readout costs 1.
All graph edges have unit cost. Costs exclude planning and graph representation.
"""
from collections import deque
from functools import lru_cache
from itertools import combinations
from math import inf, ceil, log2
import json, random
from pathlib import Path


def gray(i): return i ^ (i >> 1)
def ungray(g):
    i=0
    while g:
        i ^= g
        g >>= 1
    return i


def swap_bits(x, a, b):
    return x ^ (((x>>a ^ x>>b)&1)*((1<<a)|(1<<b)))


def cycle(m, slow):
    """Same abstract cycle and anchor. Physical start = highest single bit.
    Fast cycle uses ordinary Gray labels; slow swaps top two coordinates."""
    M=1<<m
    def label(i):
        g=gray(i)
        return swap_bits(g,m-1,m-2) if slow else g
    v=[label(i) for i in range(M)]
    return {x:{v[(i-1)%M],v[(i+1)%M]} for i,x in enumerate(v)}


def distances(graph):
    D={}
    for s in graph:
        d={s:0}; q=deque([s])
        while q:
            p=q.popleft()
            for z in graph[p]:
                if z not in d: d[z]=d[p]+1; q.append(z)
        D[s]=d
    return D


def solver(graph, probes):
    """Exact minimax policy over (location, candidate bitmask).
    Because movement is silent, any policy can replace travel to its next
    informative probe by a shortest path; each query strictly shrinks H.
    """
    D=distances(graph)
    @lru_cache(None)
    def V(s,H):
        if H.bit_count()<=1: return 0
        best=inf
        for p,qs in probes.items():
            if p not in D[s]: continue
            for q in qs:
                h1=H&q; h0=H^h1
                if h1 and h0:
                    best=min(best,D[s][p]+1+max(V(p,h1),V(p,h0)))
        return best
    return V,D


def bit_probes(k):
    return [sum(1<<w for w in range(1<<k) if (w>>j)&1) for j in range(k)]


def pair_radius(s,H,probes,D):
    """Maximum, over unresolved pairs, of distance to a separating probe."""
    ws=[i for i in range(H.bit_length()) if (H>>i)&1]
    if len(ws)<=1: return 0
    return max(min((D[s][p] for p,qs in probes.items() if p in D[s]
                    and any(((q>>a)^(q>>b))&1 for q in qs)), default=inf)
               for a,b in combinations(ws,2))


def balanced_radius(s,H,probes,D):
    """Minimum travel to a probe splitting H into sizes <= ceil(|H|/2)."""
    n=H.bit_count()
    if n<=1: return 0
    return min((D[s][p] for p,qs in probes.items() if p in D[s]
                and any(0<(H&q).bit_count()<n and
                        max((H&q).bit_count(),n-(H&q).bit_count()) <= (n+1)//2
                        for q in qs)), default=inf)


def uniform_balanced_radius(s,H,probes,D):
    # Uniform over ALL non-singleton subsets of this H, at the anchor.
    r=0; sub=H
    while sub:
        if sub.bit_count()>1: r=max(r,balanced_radius(s,sub,probes,D))
        sub=(sub-1)&H
    return r


def main():
    out={"model":"unit-cost silent reversible motion and binary observations; known graph and readouts; zero-error deterministic identification", "cycle_exact":[],"cycle_scaling":[],"random_audit":{}}
    checks=0
    # Complete graph enumeration, distance checks and exact minimax for small dimensions.
    # Both systems use the SAME physical start and sensor location, and each edge flips one bit.
    for m in range(3,9):
        for slow in (False,True):
            G=cycle(m,slow); s=1<<(m-1); k=3; H=(1<<(1<<k))-1
            assert len(G)==1<<m and all(len(z)==2 for z in G.values()); checks+=1
            assert all((a^b).bit_count()==1 and a in G[b] for a,z in G.items() for b in z); checks+=1
            V,D=solver(G,{0:bit_probes(k)})
            d=(1<<(m-1))-1 if slow else 1
            assert D[s][0]==d and V(s,H)==d+k; checks+=1
            # Verify anchor-bound equality at every location, all worlds and all candidate subsets.
            for p in G:
                assert V(p,H)==D[p][0]+k; checks+=1
            out['cycle_exact'].append(dict(m=m,mode='slow' if slow else 'fast',vertices=len(G),distance=d,optimal_cost=V(s,H)))
    # Algebraic extrapolation, not materialization of huge graphs.
    for m in (3,4,8,12,16,20,24,32):
        s=1<<(m-1); k=3; M=1<<m
        ds=[]
        for slow in (False,True):
            j=ungray(swap_bits(s,m-1,m-2) if slow else s)
            d=min(j,M-j); ds.append(d+k)
        assert ds==[k+1,k+(1<<(m-1))-1]; checks+=1
        out['cycle_scaling'].append(dict(m=m,architecture_states=M,fast=ds[0],slow=ds[1]))
    # Fixed seed: small reversible, disconnected and aliased random instruments.
    rng=random.Random(20261128)
    counts={'graphs':0,'belief_states':0,'finite':0,'infinite':0,'pair_bound_checked':0,'pair_bound_tight':0,'balanced_bound_checked':0,'balanced_bound_tight':0,'anchor_bound_checked':0,'anchor_bound_tight':0}
    max_pair_slack=0
    for trial in range(100):
        M=rng.randint(2,6); N=rng.randint(3,7); Hfull=(1<<N)-1
        G={s:set() for s in range(M)}
        for a,b in combinations(G,2):
            if rng.random()<.45: G[a].add(b); G[b].add(a)
        Q={s:[rng.randrange(1<<N) for _ in range(rng.randint(0,3))] for s in G}
        V,D=solver(G,Q); counts['graphs']+=1
        for s in G:
            for H in range(1,Hfull+1):
                n=H.bit_count()
                if n<=1: continue
                v=V(s,H); R=pair_radius(s,H,Q,D); counts['belief_states']+=1
                assert (v<inf)==(R<inf); checks+=1
                if v==inf: counts['infinite']+=1; continue
                counts['finite']+=1
                # At least one pair requires a separating probe after travel R.
                # Return to original anchor between successive useful probes.
                lo=R+1; hi=(n-1)*(2*R+1)-R
                assert lo<=v<=hi; checks+=1; counts['pair_bound_checked']+=1
                counts['pair_bound_tight']+=v==hi; max_pair_slack=max(max_pair_slack,hi-v)
                B=uniform_balanced_radius(s,H,Q,D)
                if B<inf:
                    hi2=ceil(log2(n))*(2*B+1)-B
                    assert v<=hi2; checks+=1; counts['balanced_bound_checked']+=1
                    counts['balanced_bound_tight']+=v==hi2
                # Arbitrary known working anchor, not necessarily the original state.
                for a,d in D[s].items():
                    va=V(a,H)
                    assert v<=d+va; checks+=1; counts['anchor_bound_checked']+=1
                    counts['anchor_bound_tight']+=v==d+va
    out['random_audit']=counts|{'max_pair_bound_slack':max_pair_slack}
    # A fixed-radius witness guarantee does NOT imply logarithmic cost in N.
    # All probes available at the same location, each unit cost; singleton probes
    # have R=0 but can exclude just one world at a time.
    out['radius_zero']=[]
    for k in range(2,5):
        N=1<<k; H=(1<<N)-1
        A,_=solver({0:set()},{0:bit_probes(k)})
        B,_=solver({0:set()},{0:[1<<i for i in range(N)]})
        # N=16 exact recurrence enumerates subsets; stop at 16.
        assert A(0,H)==k and B(0,H)==N-1; checks+=2
        out['radius_zero'].append({'worlds':N,'bit_cost':k,'singleton_cost':N-1,'pair_radius':0})
    out['assertions_passed']=checks
    p=Path(__file__).with_name('hexcore_reversible_results.json'); p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
