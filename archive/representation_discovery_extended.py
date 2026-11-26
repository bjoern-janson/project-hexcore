"""Expand NAND formula grammar from 2 to 3 input variables; bounded beam search.
Uses exact query recovery on all 64 binary input states, not held-out state generalization.
"""
import itertools as it, random, json
from pathlib import Path
N=6; S=64; MASK=(1<<S)-1; X=[sum(((s>>i)&1)<<s for s in range(S)) for i in range(N)]
# Complete formula library on 3 abstract variables, via NAND relaxation.
T=[sum(((s>>i)&1)<<s for s in range(8)) for i in range(3)]; D={t:(4,str(i)) for i,t in enumerate(T)}
while True:
    old=list(D.items()); change=False
    for a,(ca,ea) in old:
        for b,(cb,eb) in old:
            f=255^(a&b); cost=1+ca+cb
            if f not in D or cost<D[f][0]: D[f]=(cost,('N',ea,eb)); change=True
    if not change:break
assert len(D)==256
triples=list(it.combinations(range(N),3)); pairs=list(it.combinations(range(N),2)); C={}
def show(e,inds):return 'x'+str(inds[int(e)]) if isinstance(e,str) else 'NAND('+show(e[1],inds)+','+show(e[2],inds)+')'
for inds in triples:
    idx=[sum(((s>>v)&1)<<i for i,v in enumerate(inds)) for s in range(S)]
    for f,(cost,e) in D.items():
        if f in (0,255):continue
        g=sum(((f>>k)&1)<<s for s,k in enumerate(idx)); k=min(g,MASK^g)
        if k not in C or cost<C[k][0]: C[k]=(cost,show(e,inds),g)
C=sorted(C.values()); sp=list(it.combinations(range(S),2)); ALL=(1<<len(sp))-1
# Query labels supplied to search as answer vectors only.
def diff(f):return sum((((f>>a)^(f>>b))&1)<<k for k,(a,b) in enumerate(sp))
uncut=[ALL^diff(f) for _,_,f in C]
Q={'majority3':[(X[i]&X[j])|(X[i]&X[k])|(X[j]&X[k]) for i,j,k in triples], 'parity':[X[i]^X[j] for i,j in pairs], 'conjunction':[X[i]&X[j] for i,j in pairs], 'single':X}
QD={k:[diff(f) for f in v] for k,v in Q.items()}; rng=random.Random(20261126); W={k:[0]*len(v) for k,v in Q.items()}
for k,v in W.items():
    for _ in range(600):v[rng.randrange(len(v))]+=1
# Fixed beam width, no oracle access to expression meanings. Sort by training coverage, then cheaper.
def run(task,width=24):
    beam=[((),ALL,0,0)]; evals=0
    for depth in range(3):
        nxt={}
        for inds,u,c,score in beam:
            for i,z in enumerate(uncut):
                if i in inds:continue
                key=tuple(sorted((*inds,i)))
                if key in nxt:continue
                v=u&z; cost=c+C[i][0]; score=sum(w for w,d in zip(W[task],QD[task]) if not (v&d)); evals+=1
                nxt[key]=(key,v,cost,score)
        # Prefer different collision patterns to avoid equivalent permutations crowding beam.
        uniq={}
        for r in nxt.values():
            if r[1] not in uniq or r[2]<uniq[r[1]][2]:uniq[r[1]]=r
        beam=sorted(uniq.values(),key=lambda r:(r[3],-r[2]),reverse=True)[:width]
    inds,u,c,s=beam[0]
    return {'encoder':[C[i][1] for i in inds],'description_bits':c,'train_score':s/600,'coverage':{k:sum(not (u&d) for d in v) for k,v in QD.items()},'evaluations':evals}
R={'candidate_count':len(C),'beam_width':24,'results':{k:run(k) for k in Q}}
Path(__file__).with_name('representation_discovery_extended_results.json').write_text(json.dumps(R,indent=2));print(json.dumps(R,indent=2))
