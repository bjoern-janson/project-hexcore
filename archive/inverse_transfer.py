import json,itertools as it,time
from pathlib import Path
from sealed_world import search, parity, variables, apply
from inverse_synthesis import restrict
p=Path(__file__).parent
r=json.loads((p/'inverse_synthesis_results.json').read_text())[0]
cert=next(c for c in r['inverse']['certificates'] if len(c['rows'])==2)
rel=set(cert['relation']); allowed=set(cert['allowed']); assert all(apply(op,a,b,3) in rel for op in (8,14,0) for a,b in it.product(rel,repeat=2))
results=[]
for n in (4,6,8,10,12):
    t=parity(n); vs=[v for v,_ in variables(n)]; checks=0; witness=None
    # Reuse abstract relation, not original row numbers. Ordered row pairs.
    for a in range(1<<n):
        for b in range(1<<n):
            if a==b:continue
            checks+=1
            if restrict(t,(a,b)) in rel:continue
            if all(restrict(v,(a,b)) in rel for v in vs):witness=(a,b);break
        if witness:break
    assert witness and restrict(t,witness) not in rel
    start=time.perf_counter(); f=search(n,{8:'AND',14:'OR',0:'ZERO'},t,10000); elapsed=time.perf_counter()-start
    assert not f['found']
    results.append(dict(n=n,witness=witness,row_pairs_checked=checks,forward_gate_evals=f['attempts'],forward_closed=f.get('closed',False),forward_seconds=elapsed,certified=True))
print(cert,results)
(p/'inverse_transfer_results.json').write_text(json.dumps(dict(certificate=cert,results=results),indent=2))
