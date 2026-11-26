import itertools as it, random, json, time
from pathlib import Path
from sealed_world import apply, variables

def close(seeds, ops, k, counts, key):
    mask=(1<<k)-1; seen=set(seeds); queue=list(sorted(seen)); i=0
    while i<len(queue):
        a=queue[i]
        for b in queue[:i+1]:
            for op in ops:
                for u,v in ((a,b),) if op in (0,1,6,7,8,9,14,15) or a==b else ((a,b),(b,a)):
                    counts[key]+=1; c=apply(op,u,v,mask)
                    if c not in seen: seen.add(c); queue.append(c)
        i+=1
        if len(seen)==1<<k: break
    return frozenset(seen)

def restrict(t,rows): return sum(((t>>r)&1)<<i for i,r in enumerate(rows))

def run(base, targets, mode):
    n=3; k=1<<n; vs=[v for v,_ in variables(n)]; seeds=vs+[0,255]
    c=dict(closure=0,certificate=0,filter=0,lookups=0); cache={}; certs=[]; probes=0; skipped=0; choices=[]; prefix={}
    start=time.perf_counter()
    def closure(ops):
        if ops not in cache: cache[ops]=close(seeds,ops,k,c,'closure')
        return cache[ops]
    initial=closure(base)
    for i,t in enumerate(targets):
        if t in initial: choices.append(None)
        else:
            if mode=='inverse':
                # Reuse a previous relation witness if it excludes this target.
                applicable=[(rows,allowed) for rows,rel,allowed in certs if restrict(t,rows) not in rel]
                if not applicable:
                    # Discover a local projection where the target is outside exact closure.
                    for size in range(2,5):
                        for rows in it.combinations(range(k),size):
                            rel=close([restrict(v,rows) for v in seeds],base,size,c,'certificate')
                            if restrict(t,rows) in rel: continue
                            allowed=set()
                            for op in range(16):
                                ok=True
                                for a,b in it.product(sorted(rel),repeat=2):
                                    c['filter']+=1
                                    if apply(op,a,b,(1<<size)-1) not in rel: ok=False;break
                                if not ok: allowed.add(op)
                            certs.append((rows,rel,allowed)); applicable=[(rows,allowed)];break
                        if applicable: break
                allowed=set.intersection(*(a for _,a in applicable)) if applicable else set(range(16))
            else: allowed=set(range(16))
            for op in range(16):
                if op in base: continue
                if op not in allowed: skipped+=1;continue
                probes+=1;c['lookups']+=1
                if t in closure(tuple(sorted((*base,op)))):
                    choices.append(op);break
            else: choices.append(-1)
        if i+1 in (1,8,32,128,256): prefix[str(i+1)]={**c,'total_gate_evals':sum(c[x] for x in ('closure','certificate','filter')),'probes':probes,'skipped':skipped}
    return dict(base=base,mode=mode,counts=c,total_gate_evals=sum(c[x] for x in ('closure','certificate','filter')),probes=probes,skipped=skipped,choices=choices,certificates=[dict(rows=r,relation=sorted(s),allowed=sorted(a)) for r,s,a in certs],cached_grammars=len(cache),prefix=prefix,seconds=time.perf_counter()-start)

def main():
    results=[]
    for base in [(8,14),(6,), (8,)]:
        targets=list(range(256));random.Random(31).shuffle(targets)
        a=run(base,targets,'forward');b=run(base,targets,'inverse');assert a['choices']==b['choices'];results.append(dict(base=base,forward=a,inverse=b))
        print(base,[(r['mode'],r['total_gate_evals'],r['probes'],r['skipped'],len(r['certificates']),r['seconds']) for r in (a,b)],flush=True)
    Path(__file__).with_name('inverse_synthesis_results.json').write_text(json.dumps(results,indent=2))
if __name__=='__main__':main()
