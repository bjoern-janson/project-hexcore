"""A finite reachability game for an instrument that changes between moves.

Each round: the environment chooses and reveals an allowed undirected graph;
controller chooses a move (or wait); then the environment can choose again.
A goal vertex has a fixed, protected readout. Worlds do not affect motion.
No hidden costs except explicitly counted movement/query units.
"""
from collections import deque
from functools import lru_cache
from itertools import combinations
import json, random
from pathlib import Path


def star(n,c):
    return tuple(frozenset(set(range(n))-{c} if i==c else {c}) for i in range(n))


def dist_to_anchor(g):
    d={0:0}; q=deque([0])
    while q:
        s=q.popleft()
        for t in g[s]:
            if t not in d: d[t]=d[s]+1; q.append(t)
    return d


def robust_rank(graphs_by_state):
    """Attractor iteration. None = no finite guaranteed deadline."""
    n=len(graphs_by_state); rank={0:0}; layers=[{0}]
    while True:
        W=set(rank)
        added={s for s in range(n) if s not in W and
               all((g[s]|{s})&W for g in graphs_by_state[s])}
        if not added: break
        for s in added: rank[s]=len(layers)
        layers.append(added)
    return [rank.get(s) for s in range(n)]


def horizon_check(graphs_by_state, rank):
    """Independent bounded-game minimax recursion, plus losing-region check."""
    n=len(rank)
    @lru_cache(None)
    def can(s,h):
        if s==0: return True
        if h==0: return False
        return all(any(can(t,h-1) for t in g[s]|{s}) for g in graphs_by_state[s])
    checks=0
    for s,r in enumerate(rank):
        for h in range(n+1):
            assert can(s,h)==(r is not None and r<=h); checks+=1
        if r is None:
            assert any(all(rank[t] is None for t in g[s]|{s}) for g in graphs_by_state[s]); checks+=1
        elif r>0:
            assert all(any(rank[t] is not None and rank[t]<r for t in g[s]) for g in graphs_by_state[s]); checks+=1
    return checks


def make_layered(rng, depth, width, count):
    # Every graph has at least one edge from each nonanchor to a lower rank.
    # Other edges are entirely variable; this preserves a common rank, not a route.
    ranks=[0]+[i for i in range(1,depth+1) for _ in range(width)]
    n=len(ranks); graphs=[]
    for _ in range(count):
        G=[set() for _ in ranks]
        for s in range(1,n):
            t=rng.choice([j for j,r in enumerate(ranks) if r==ranks[s]-1]); G[s].add(t); G[t].add(s)
        for s,t in combinations(range(n),2):
            if rng.random()<.12: G[s].add(t); G[t].add(s)
        graphs.append(tuple(map(frozenset,G)))
    return ranks,graphs


def main():
    checks=0; out={'model':'visible graph chosen adversarially before each action; undirected unit edges; wait allowed; goal vertex 0 fixed', 'stars':[], 'random_layered':{}, 'random_families':{}}
    for n in range(3,13):
        graphs=[star(n,c) for c in range(1,n)]
        fam=[graphs]*n; rank=robust_rank(fam); checks+=horizon_check(fam,rank)
        assert rank==[0]+[None]*(n-1); checks+=1
        maxd=max(max(dist_to_anchor(g).values()) for g in graphs); assert maxd==2; checks+=1
        # Freeze a snapshot long enough to reach goal: at most two moves.
        static_ranks=[robust_rank([[g]]*n) for g in graphs]
        assert all(r==[dist_to_anchor(g)[i] for i in range(n)] for g,r in zip(graphs,static_ranks)); checks+=1
        out['stars'].append({'vertices':n,'possible_snapshots':len(graphs),'max_frozen_distance':maxd,'robust_losing_nonanchor_states':n-1,'max_frozen_identification_cost_for_three_bits':maxd+3,'dynamic_identification_cost':None})
    rng=random.Random(90210); ncases=0; total_states=0; max_robust=0; different_next=0
    for _ in range(150):
        depth=rng.randint(2,5); width=rng.randint(2,3); count=rng.randint(2,7)
        rho,graphs=make_layered(rng,depth,width,count); n=len(rho); fam=[graphs]*n
        rank=robust_rank(fam); checks+=horizon_check(fam,rank)
        assert all(r is not None and r<=q for r,q in zip(rank,rho)); checks+=n
        for s in range(1,n):
            choices=[{t for t in g[s] if rho[t]<rho[s]} for g in graphs]
            assert all(choices); checks+=1
            if not set.intersection(*choices): different_next+=1
        ncases+=1; total_states+=n; max_robust=max(max_robust,max(rank))
    out['random_layered']={'families':ncases,'states':total_states,'max_robust_rank':max_robust,'states_without_one_common_descending_neighbor':different_next,'all_declared_rank_bounds_passed':True}
    # Random connected graph families, many without a shared ranking to anchor.
    stats={'families':0,'states':0,'winning':0,'losing':0,'families_with_losing_state':0}
    for _ in range(250):
        n=rng.randint(3,8); graphs=[]
        for j in range(rng.randint(2,8)):
            # random tree, then add edges
            order=list(range(n)); rng.shuffle(order); G=[set() for _ in order]
            for i in range(1,n):
                s=order[i]; t=rng.choice(order[:i]); G[s].add(t); G[t].add(s)
            for s,t in combinations(range(n),2):
                if rng.random()<.10: G[s].add(t); G[t].add(s)
            graphs.append(tuple(map(frozenset,G)))
        fam=[graphs]*n; rank=robust_rank(fam); checks+=horizon_check(fam,rank)
        assert all(len(dist_to_anchor(g))==n for g in graphs); checks+=1
        stats['families']+=1; stats['states']+=n; stats['winning']+=sum(r is not None for r in rank); stats['losing']+=sum(r is None for r in rank); stats['families_with_losing_state']+=None in rank
    out['random_families']=stats; out['assertions_passed']=checks
    Path(__file__).with_name('hexcore_flux_guard_results.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))

if __name__=='__main__': main()
