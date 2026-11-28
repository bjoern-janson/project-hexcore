"""Exact multiscale parity observations without materializing a binary lattice.
Uses hexcore_streamed_reality.py. The reference law is IID fair bits, not physical spacetime.
"""
from hexcore_streamed_reality import Relational, Latent
from bisect import bisect_left, insort
from pathlib import Path
import itertools, random, json

class IntervalWorld:
    def __init__(self): self.rel=Relational(); self.flipped=[]
    def flip(self,i):
        j=bisect_left(self.flipped,i)
        if j<len(self.flipped) and self.flipped[j]==i: self.flipped.pop(j)
        else: insort(self.flipped,i)
    def shift(self,l,r): return (bisect_left(self.flipped,r)-bisect_left(self.flipped,l))%2
    def prob(self,l,r):
        p=self.rel.prob(l,r)
        return 1-p if self.shift(l,r) else p
    def read(self,l,r,coin):
        z=self.shift(l,r)
        return self.rel.read(l,r,coin^z)^z

# Independent eager reference uses actual cells, never the prefix representation.
def exact_test(n=6,trials=100,steps=25):
    rng=random.Random(744); initial=list(itertools.product((0,1),repeat=n)); checks=0
    for trial in range(trials):
        model=IntervalWorld(); worlds=initial[:]
        for step in range(steps):
            if rng.random()<.25:
                i=rng.randrange(n); model.flip(i)
                worlds=[tuple(v^(j==i) for j,v in enumerate(w)) for w in worlds]
            # Every possible interval at every history. Then select an adaptively dependent interval.
            for l in range(n):
                for r in range(l+1,n+1):
                    p=sum(sum(w[l:r])%2 for w in worlds)/len(worlds)
                    assert p==model.prob(l,r); checks+=1
            l,r=sorted(rng.sample(range(n+1),2))
            bit=model.read(l,r,rng.randrange(2))
            worlds=[w for w in worlds if sum(w[l:r])%2==bit]
            assert worlds
    return dict(cells=n,initial_states=len(initial),trials=trials,steps_per_trial=steps,conditional_probability_checks=checks)

def zoom_test(m=40):
    n=2**m; rng=random.Random(745); model=IntervalWorld(); queries=0; checks=0
    def read(l,r):
        nonlocal queries
        queries+=1; return model.read(l,r,rng.randrange(2))
    # A observes whole world; B explores one of the two halves chosen using both answers.
    root=read(0,n); l,r=0,n; val=root
    for _ in range(m):
        mid=(l+r)//2; a=read(l,mid); b=read(mid,r)
        assert a^b==val; checks+=1
        if a and not b: r=mid; val=a
        else: l=mid; val=b
    assert r-l==1
    committed_before_flip=model.rel.draws; boundaries=len(model.rel.parent)
    # Intervene on one cell and verify effect on both scales; flip back and recheck.
    model.flip(l); assert read(l,r)==(val^1); assert read(0,n)==(root^1); checks+=2
    model.flip(l); assert read(l,r)==val; assert read(0,n)==root; checks+=2
    assert model.rel.draws==committed_before_flip
    return dict(cells=n,zoom_levels=m,queries=queries,stored_boundary_labels=boundaries,committed_random_bits=committed_before_flip,consistency_checks=checks,materialized_cell_values=0,finest_interval=[l,r])

if __name__=='__main__':
    out=dict(exact_audit=exact_test(),zoom=zoom_test())
    Path(__file__).with_name('hexcore_interval_reality_results.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
