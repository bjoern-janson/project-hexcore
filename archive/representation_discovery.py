"""Finite, exhaustive Boolean encoder discovery with NAND-only formula grammar.
6 input bits, 3 memory bits. Candidate expressions may use at most 2 inputs.
No task-specific gates or decoder provided: exact decoding is inferred from truth-table cells.
All possible input states are observed in training; sampled historical query frequencies drive selection.
"""
import itertools as it, json, math, random, time
from pathlib import Path
N=6; B=3; S=1<<N; MASK=(1<<S)-1
X=[sum(((s>>i)&1)<<s for s in range(S)) for i in range(N)]
pairs=list(it.combinations(range(N),2)); triples=list(it.combinations(range(N),3))
# Generate every two-input function via generic NAND composition, minimal tree description.
# Prefix code: input token 0 + 3-bit index; gate token 1, followed by its two children.
# Encoder outputs have fixed length three, so no per-formula delimiter needed.
exprs={}
for i,j in pairs:
    d={X[i]:(4,f'x{i}'),X[j]:(4,f'x{j}')}
    while True:
        old=list(d.items()); changed=False
        for a,(ca,ea) in old:
            for b,(cb,eb) in old:
                f=MASK^(a&b); cost=1+ca+cb
                if f not in d or cost<d[f][0]: d[f]=(cost,f'NAND({ea},{eb})'); changed=True
        if not changed: break
    assert len(d)==16
    for f,v in d.items():
        if f not in (0,MASK) and (f not in exprs or v[0]<exprs[f][0]): exprs[f]=v
# Complemented outputs induce the same information partitions. Keep cheaper representative.
cands={}
for f,v in exprs.items():
    k=min(f,MASK^f)
    if k not in cands or v[0]<cands[k][0]: cands[k]=(*v,f)
C=sorted(cands.values()); assert len(C)==81
state_pairs=list(it.combinations(range(S),2))
def diff(f): return sum((((f>>a)^(f>>b))&1)<<k for k,(a,b) in enumerate(state_pairs))
ALL=(1<<len(state_pairs))-1
uncut=[ALL^diff(f) for _,_,f in C]
# The evaluator supplies only query answer vectors, not algebraic expressions to the search.
queries={'parity':[X[i]^X[j] for i,j in pairs], 'conjunction':[X[i]&X[j] for i,j in pairs], 'single':X, 'majority3':[(X[i]&X[j])|(X[i]&X[k])|(X[j]&X[k]) for i,j,k in triples]}
qd={k:[diff(f) for f in v] for k,v in queries.items()}
# Use 600 sampled historical requests per task; full truth tables are known from exhaustive input calibration.
rng=random.Random(20261126); weights={k:[0]*len(v) for k,v in queries.items()}
for k,v in weights.items():
    for _ in range(600): v[rng.randrange(len(v))]+=1
# Also compare raw-only and unrestricted candidates at matched total description budgets.
limits=[12,22,32,42,52,62,72,1000]
best={k:{str(l):None for l in limits} for k in ['parity','conjunction','single','majority3','mixed']}
rawbest={k:None for k in best}; counts=0
for inds in it.combinations(range(len(C)),B):
    cost=sum(C[i][0] for i in inds)
    u=uncut[inds[0]]&uncut[inds[1]]&uncut[inds[2]]
    masks={k:[not bool(u&d) for d in ds] for k,ds in qd.items()}
    scores={k:sum(w for w,m in zip(weights[k],v) if m)/600 for k,v in masks.items()}
    scores['mixed']=(scores['parity']+scores['conjunction']+scores['single'])/3
    cov={k:sum(v) for k,v in masks.items()}
    counts+=1
    for k,score in scores.items():
        key=(score,-cost)
        rec=(key,inds,cost,cov)
        for l in limits:
            if cost<=l and (best[k][str(l)] is None or key>best[k][str(l)][0]): best[k][str(l)]=rec
        if cost==12 and (rawbest[k] is None or key>rawbest[k][0]): rawbest[k]=rec

def report(r):
    key,inds,cost,cov=r
    fs=[C[i][2] for i in inds]
    cells={}
    for s in range(S):
        code=sum(((f>>s)&1)<<i for i,f in enumerate(fs)); cells.setdefault(code,[]).append(s)
    acc={k:sum(sum(max(sum((q>>s)&1 for s in cell),sum(1-((q>>s)&1) for s in cell)) for cell in cells.values())/S for q in v)/len(v) for k,v in queries.items()}
    # Independent explicit decoder check against bitset method.
    for k,v in queries.items():
        exact=sum(all(len({(q>>s)&1 for s in cell})==1 for cell in cells.values()) for q in v)
        assert exact==cov[k]
    return {'encoder':[C[i][1] for i in inds],'description_bits':cost,'training_score':key[0], 'exact_coverage':cov,'mean_optimal_decoder_accuracy':acc,'occupied_memory_states':len(cells)}
result={'input_bits':N,'memory_bits':B,'candidate_count':len(C),'encoders_evaluated':counts,'query_counts':{k:len(v) for k,v in queries.items()},'best':{k:{l:report(r) for l,r in v.items() if r} for k,v in best.items()}}
Path(__file__).with_name('representation_discovery_results.json').write_text(json.dumps(result,indent=2))
for k,v in result['best'].items():
    print(k)
    for l in ['12','22','32','42','52','62','72','1000']:
        r=v.get(l); print(l,r['description_bits'],r['exact_coverage'],r['encoder'])
print('evaluated',counts)
