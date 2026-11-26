"""Exploratory finite pilot; no claim of novel learning mechanism.
Uniform permutation targets, independently randomized generators; a cycle and adjacent transposition guarantee reachability.
Training solutions and costs shared; library contains frequent length-2..4 words.
Independent held-out targets at each n/seed; no target feedback updates in test.
Cost unit: candidate transition (macro charged both as one and expanded length).
"""
import random, itertools, collections, json, time, statistics, math
from pathlib import Path
SIZES=(5,6,7,8); SEEDS=range(4); CHECKPOINTS=(0,8,32,80); TEST=24; CAP=8

def apply(p,g): return tuple(p[i] for i in g)
def inv(g): return tuple(g.index(i) for i in range(len(g)))
def make_ops(n,seed):
    rng=random.Random(919*n+seed); labels=list(range(n));rng.shuffle(labels)
    cycle=list(range(n));swap=list(range(n));extra=list(range(n));rng.shuffle(extra)
    for i in range(n):cycle[labels[i]]=labels[(i+1)%n]
    swap[labels[0]],swap[labels[1]]=labels[1],labels[0]
    gens=list(dict.fromkeys([tuple(cycle),inv(tuple(cycle)),tuple(swap),tuple(extra),inv(tuple(extra))]))
    return [(g,(i,)) for i,g in enumerate(gens)]

def verify(n,w,target,base):
    p=tuple(range(n))
    for i in w:p=apply(p,base[i][0])
    assert p==target

def bidir(n,target,ops):
    e=tuple(range(n)); f={e:()}; b={target:()}; F=[e];B=[target]; calls=weighted=0
    back=[(inv(g),w) for g,w in ops]
    if target==e:return (),0,0
    while F and B:
        forward=len(F)<=len(B); front=F if forward else B; own=f if forward else b; other=b if forward else f; nxt=[]
        for p in front:
            for g,w in (ops if forward else back):
                calls+=1;weighted+=len(w);q=apply(p,g)
                if q in own:continue
                own[q]=own[p]+w if forward else w+own[p]
                if q in other:return f[q]+b[q],calls,weighted
                nxt.append(q)
        if forward:F=nxt
        else:B=nxt
    raise AssertionError('unreachable')

class Cache:
    def __init__(self,n,base):
        e=tuple(range(n));self.base=base;self.paths={e:()};self.q=collections.deque([e]);self.calls=0
    def solve(self,target):
        old=self.calls
        while target not in self.paths:
            p=self.q.popleft()
            for g,w in self.base:
                self.calls+=1;q=apply(p,g)
                if q not in self.paths:self.paths[q]=self.paths[p]+w;self.q.append(q)
        return self.paths[target],self.calls-old

def library(n,base,words):
    counts=collections.Counter(); cost=0
    for w in words:
        for k in (2,3,4):
            for i in range(len(w)-k+1):counts[w[i:i+k]]+=1;cost+=1
    # Rank only using training frequencies. Build every observed candidate, charge each primitive composition.
    candidates=[]; seen={g for g,w in base}; e=tuple(range(n))
    for w,count in sorted(counts.items(),key=lambda kv:(-kv[1]*(len(kv[0])-1),kv[0])):
        g=e
        for i in w:g=apply(g,base[i][0]);cost+=1
        if count>=2 and g!=e and g not in seen:
            candidates.append((g,w));seen.add(g)
    return candidates[:CAP],cost

def run():
    rows=[]
    for n in SIZES:
      for seed in SEEDS:
        rng=random.Random(1000*n+seed); e=tuple(range(n)); base=make_ops(n,seed); targets=[]; seen={e}
        while len(targets)<max(CHECKPOINTS)+TEST:
            t=list(e);rng.shuffle(t);t=tuple(t)
            if t not in seen:seen.add(t);targets.append(t)
        train=targets[:max(CHECKPOINTS)];test=targets[max(CHECKPOINTS):]; words=[]; cache=Cache(n,base); train_cost=0
        for h in CHECKPOINTS:
            while len(words)<h:
                t=train[len(words)]; w,c=cache.solve(t);verify(n,w,t,base);words.append(w);train_cost+=c
            macros,mc=library(n,base,words)
            # clone cached state, so test cannot leak into later checkpoints
            shadow=Cache(n,base);shadow.paths=cache.paths.copy();shadow.q=cache.q.copy();shadow.calls=cache.calls
            r={'n':n,'seed':seed,'h':h,'train_cost':train_cost,'mining_cost':mc,'macros':len(macros),'cache_states':len(cache.paths)}
            for name,ops in [('fresh',base),('macro',base+macros)]:
                start=time.perf_counter();calls=weighted=length=0
                for t in test:
                    w,c,k=bidir(n,t,ops);verify(n,w,t,base);calls+=c;weighted+=k;length+=len(w)
                r.update({name+'_calls':calls,name+'_weighted':weighted,name+'_length':length,name+'_seconds':time.perf_counter()-start})
            start=time.perf_counter();cc=0;length=0
            for t in test:
                w,c=shadow.solve(t);verify(n,w,t,base);cc+=c;length+=len(w)
            r.update(cache_calls=cc,cache_length=length,cache_seconds=time.perf_counter()-start)
            rows.append(r)
    return rows

if __name__=='__main__':
    rows=run(); out=Path(__file__).with_name('discovery_random_results.json');out.write_text(json.dumps(rows,indent=2));
    for n in SIZES:
      for h in CHECKPOINTS:
        a=[r for r in rows if r['n']==n and r['h']==h]; avg=lambda k:statistics.mean(r[k] for r in a)
        print(n,h,*(round(avg(k),1) for k in ('train_cost','mining_cost','fresh_calls','macro_calls','macro_weighted','cache_calls','cache_states','macros')))
