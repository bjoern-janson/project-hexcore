"""Round 16–19. Exact finite checks of mutable reachability certificates.
Python 3.10+, stdlib. A version is a finite undirected connected graph.
Environment selects a version (possibly the current one), reveals it, then
controller moves along a current edge or waits. Goal 0. Unit movement cost;
version replacement has zero cost in this model. All distances observable.
"""
from collections import deque
from functools import lru_cache
from pathlib import Path
import json, random

checks=0
def check(x):
    global checks
    checks+=1
    assert x

def graph(n,edges):
    a=[set() for _ in range(n)]
    for i,j in edges:
        a[i].add(j);a[j].add(i)
    return tuple(tuple(sorted(x)) for x in a)

def distances(g):
    d=[None]*len(g);d[0]=0;q=deque([0])
    while q:
        s=q.popleft()
        for u in g[s]:
            if d[u] is None:d[u]=d[s]+1;q.append(u)
    assert None not in d
    return tuple(d)

def random_graph(n,rng):
    order=list(range(n));rng.shuffle(order)
    edges=[(order[i],order[rng.randrange(i)]) for i in range(1,n)]
    p=rng.choice((0,.12,.3))
    edges += [(i,j) for i in range(n) for j in range(i) if rng.random()<p]
    return graph(n,edges)

# Independent finite-state attractor computation for graph families.
def ranks(states, choices, goal):
    w={s:0 for s in states if goal(s)}
    i=0
    while True:
        i+=1
        new=[s for s in states if s not in w and all(any(t in w for t in successors) for successors in choices(s))]
        if not new: return w
        w.update({s:i for s in new})

# X=1, Y=2. A: X-Y-0, B: Y-X-0.
G=(graph(3,[(1,2),(2,0)]), graph(3,[(1,2),(1,0)]))
D=tuple(map(distances,G))
check(D==((0,2,1),(0,1,2)))

# Bounded credit, paid on upward rank handoffs; no refunds. Optional
# replenishment from descent (in units of credit); cap is original budget.
def credit_game(gs,cap,refill=0):
    ds=tuple(map(distances,gs)); n=len(gs[0]); m=len(gs)
    states=[(v,s,b) for v in range(m) for s in range(n) for b in range(cap+1)]
    def choices(z):
        v,s,b=z
        for j,g in enumerate(gs):
            delta=max(0,ds[j][s]-ds[v][s])
            if delta>b:continue
            yield tuple((j,u,min(cap,b-delta+refill*max(0,ds[j][s]-ds[j][u]))) for u in (*g[s],s))
    return ranks(states,choices,lambda z:z[1]==0)

cycle=[]
for b in range(21):
    w=credit_game(G,b)
    t=w[(0,1,b)]
    check(t==b+2)
    cycle.append({'credit':b,'worst_moves':t,'refill_one_worst_moves':credit_game(G,b,1).get((0,1,b))})
    if b: check(cycle[-1]['refill_one_worst_moves'] is None)

# Exact deadline guard. Independent recursive search across all legal
# environment choices, with a separate "freeze here" falsification control.
# At a switch with d remaining, allow only new shortest-distance <= d.
def audit_family(gs,extra=3):
    ds=tuple(map(distances,gs));n=len(gs[0]);m=len(gs);h=max(map(max,ds))+extra
    @lru_cache(None)
    def freeze(j,s,t):
        if s==0:return True
        if t==0:return False
        return any(freeze(j,u,t-1) for u in (*gs[j][s],s))
    @lru_cache(None)
    def win(s,t):
        if s==0:return True
        if t==0:return False
        admissible=[j for j in range(m) if ds[j][s]<=t]
        if not admissible:return False
        return all(any(win(u,t-1) for u in (*gs[j][s],s)) for j in admissible)
    counts={'handoffs':0,'admitted':0,'rejected':0,'admitted_nonconstant':0,'deadline_states':0}
    for s in range(1,n):
        for t in range(h+1):
            check(win(s,t)==any(d[s]<=t for d in ds))
            counts['deadline_states']+=1
            for old in range(m):
                if ds[old][s]>t:continue # only states with a valid prior guarantee
                for new in range(m):
                    counts['handoffs']+=1
                    admitted=ds[new][s]<=t
                    check(freeze(new,s,t)==admitted)
                    if admitted:
                        counts['admitted']+=1
                        if new!=old:counts['admitted_nonconstant']+=1
                        check(any(win(u,t-1) for u in (*gs[new][s],s)))
                    else:
                        counts['rejected']+=1
                        check(not any(freeze(new,u,t-1) for u in (*gs[new][s],s)))
    # Credit potential: every state can force completion within rank + credit.
    for cap in (0,1,3):
        w=credit_game(gs,cap)
        for v in range(m):
            for s in range(n):
                for b in range(cap+1):check(w[(v,s,b)]<=ds[v][s]+b)
    return counts

rng=random.Random(712039)
aggregate={};families=[]
for i in range(200):
    n=rng.randint(3,9);m=rng.randint(2,5)
    gs=tuple(random_graph(n,rng) for _ in range(m));c=audit_family(gs)
    for k,v in c.items():aggregate[k]=aggregate.get(k,0)+v
    families.append({'n':n,'versions':m,**c})

# Authority and observability: all versions share exactly the same shortest
# rank on all physical locations, but action labels differ. At start s=1,
# action a reaches goal in A and waits in B; b does the opposite. The mode
# may be fixed, revealed every round, or freshly adversarially chosen and
# hidden. The controller sees physical state and action outcomes.
# Exact finite-horizon boolean recursions over possible fixed modes.
@lru_cache(None)
def fixed_hidden(modes,t):
    if t==0:return False
    for a in (0,1):
        survivors=tuple(v for v in modes if a!=v)
        if not survivors or fixed_hidden(survivors,t-1):return True
    return False
@lru_cache(None)
def changing_hidden(t):
    if t==0:return False
    return any(all(a==v or changing_hidden(t-1) for v in (0,1)) for a in (0,1))
@lru_cache(None)
def changing_revealed(t):
    if t==0:return False
    return all(any(a==v or changing_revealed(t-1) for a in (0,1)) for v in (0,1))
visibility=[]
for t in range(1,65):
    row={'deadline':t,'fixed_hidden':fixed_hidden((0,1),t),'changing_hidden':changing_hidden(t),'changing_revealed':changing_revealed(t)}
    check(row['fixed_hidden']==(t>=2));check(not row['changing_hidden']);check(row['changing_revealed'])
    visibility.append(row)

out={'cycle':cycle,'random_families':len(families),'aggregate':aggregate,'families':families,'visibility':visibility,'assertion_evaluations':checks,'failed_assertions':0}
Path(__file__).with_name('hexcore_rank_transfer_results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('families','visibility','cycle')},indent=2))
print('cycle samples:',[cycle[i] for i in (0,1,2,5,10,20)])
