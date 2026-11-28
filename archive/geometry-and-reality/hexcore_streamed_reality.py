"""Exact lazy relational world, controls and counterexamples.
Only standard library. Run: python hexcore_streamed_reality.py
All random draws are seeded for reproducibility; exact-law claims refer to ideal fair coins.
"""
import random, itertools, json, math, sys, time
from pathlib import Path

class Relational:
    # Hidden baseline bits x_i are IID fair. Observations read XOR; flips are public actions.
    # Store only relative bits on a parity union-find forest, plus flip offsets.
    def __init__(self):
        self.parent={}; self.rank={}; self.parity={}; self.offset=set(); self.draws=0
    def find(self,i):
        if i not in self.parent:
            self.parent[i]=i; self.rank[i]=0; self.parity[i]=0
        p=self.parent[i]
        if p==i: return i,0
        r,v=self.find(p); self.parity[i]^=v; self.parent[i]=r
        return r,self.parity[i]
    def flip(self,i): self.offset.symmetric_difference_update([i])
    def shift(self,i,j): return int((i in self.offset) != (j in self.offset))
    def prob(self,i,j):
        a,u=self.find(i); b,v=self.find(j)
        return .5 if a!=b else float(u^v^self.shift(i,j))
    def read(self,i,j,coin):
        a,u=self.find(i); b,v=self.find(j); z=self.shift(i,j)
        if a==b: return u^v^z
        # A coin chooses the observed parity; all unconstrained parities are equiprobable.
        d=coin^u^v^z; self.draws+=1
        if self.rank[a]<self.rank[b]: a,b=b,a
        self.parent[b]=a; self.parity[b]=d
        if self.rank[a]==self.rank[b]: self.rank[a]+=1
        return coin

class Latent:
    # Strong simple baseline: lazy sample individual latent bits instead of relations.
    def __init__(self,rng): self.x={}; self.offset=set(); self.rng=rng; self.draws=0
    def flip(self,i): self.offset.symmetric_difference_update([i])
    def val(self,i):
        if i not in self.x: self.x[i]=self.rng.randrange(2); self.draws+=1
        return self.x[i] ^ (i in self.offset)
    def read(self,i,j): return self.val(i)^self.val(j)

class Naive:
    # Cache each queried unordered pair and honor explicit flips, but ignore cross-edge constraints.
    def __init__(self,rng): self.cache={}; self.offset=set(); self.rng=rng; self.draws=0
    def flip(self,i): self.offset.symmetric_difference_update([i])
    def read(self,i,j):
        if i==j: return 0
        key=tuple(sorted((i,j)))
        if key not in self.cache: self.cache[key]=self.rng.randrange(2); self.draws+=1
        return self.cache[key] ^ (i in self.offset) ^ (j in self.offset)

def exact_audit():
    # Independent explicit possible-world enumeration, compare predictive probabilities at every step.
    # Enumerate every stochastic output path of an adaptive 2-observer protocol, including flips.
    n=5; allw=tuple(itertools.product(range(2), repeat=n)); leaves=0; checks=0; branches=0
    # Conditional choices depend on first and second observation; all observers share the same world.
    def actions(h):
        if len(h)==0: return ("A",0,1)
        if len(h)==1: return ("B",1,2 if h[0] else 3)
        if len(h)==2: return ("A",0,2 if h[0] else 3)
        if len(h)==3: return ("B",2 if h[1] else 3,4)
        if len(h)==4: return ("A",0,4)
        if len(h)==5: return ("B",1,4)
        if len(h)==6: return ("A",0,1)
        if len(h)==7: return ("B",0,0)
    import copy
    def visit(worlds, rel,h):
        nonlocal leaves,checks,branches
        if len(h)==8: leaves+=1; return
        if len(h)==2 and h[0]:
            rel.flip(1); worlds=tuple(tuple(x^(j==1) for j,x in enumerate(w)) for w in worlds)
        if len(h)==4:
            i=4 if h[2] else 0; rel.flip(i)
            worlds=tuple(tuple(x^(j==i) for j,x in enumerate(w)) for w in worlds)
        _,i,j=actions(h)
        buckets=[tuple(w for w in worlds if w[i]^w[j]==b) for b in range(2)]
        p=len(buckets[1])/len(worlds); q=rel.prob(i,j); assert p==q; checks+=1
        # Stronger: at each history, check every possible next pair, not just the scheduled pair.
        for u in range(n):
            for v in range(n):
                assert rel.prob(u,v)==sum(w[u]^w[v] for w in worlds)/len(worlds); checks+=1
        for bit in range(2):
            if buckets[bit]:
                r=copy.deepcopy(rel); assert r.read(i,j,bit)==bit
                branches+=1; visit(buckets[bit],r,h+(bit,))
    visit(allw,Relational(),())
    return dict(worlds=len(allw),terminal_transcripts=leaves,conditional_probability_checks=checks,branches=branches)

def triangle_audit(n=10000):
    rr=random.Random(321); rel=Relational(); latent=Latent(random.Random(322)); naive=Naive(random.Random(323)); bad=dict(relational=0,lazy_latent=0,independent_cache=0)
    # A sees a-b, B sees b-c, then compare notes and query a-c. Flip b between second and third reads.
    # The old observed parities still imply a-c, since the intervening flip affects neither endpoint.
    for t in range(n):
        a,b,c=3*t,3*t+1,3*t+2
        for key,m in (("relational",rel),("lazy_latent",latent),("independent_cache",naive)):
            read=(lambda i,j:m.read(i,j,rr.randrange(2))) if key=="relational" else m.read
            p,q=read(a,b),read(b,c); m.flip(b); s=read(a,c)
            bad[key]+=int((p^q)!=s)
            # Repeat with intervening flips: updated a-b must equal previous complement.
            assert read(a,b)==(p^1)
    assert bad['relational']==0 and bad['lazy_latent']==0
    return dict(triangles=n,contradictions=bad,committed_random_bits=dict(relational=rel.draws,lazy_latent=latent.draws,independent_cache=naive.draws))

def deep_size(obj,seen=None):
    if seen is None: seen=set()
    if id(obj) in seen: return 0
    seen.add(id(obj)); s=sys.getsizeof(obj)
    if isinstance(obj,dict): s+=sum(deep_size(k,seen)+deep_size(v,seen) for k,v in obj.items())
    elif isinstance(obj,(set,tuple,list)): s+=sum(deep_size(x,seen) for x in obj)
    return s

def scale_audit():
    out=[]
    for n in [2**20,2**30,2**40]:
        rng=random.Random(412); ids=rng.sample(range(n),1000)
        events=[('read',ids[i],ids[(i+1)%1000]) for i in range(1000)]
        for _ in range(5000):
            if rng.random()<.1: events.append(('flip',rng.choice(ids),None))
            else:
                i,j=rng.sample(ids,2); events.append(('read',i,j))
        rel=Relational(); r=random.Random(413); lat=Latent(random.Random(414)); times=[]
        for m in (rel,lat):
            t0=time.perf_counter()
            for op,i,j in events:
                if op=='flip': m.flip(i)
                elif m is rel: m.read(i,j,r.randrange(2))
                else: m.read(i,j)
            times.append(time.perf_counter()-t0)
        assert len(rel.parent)==len(lat.x)==1000 and rel.draws==999 and lat.draws==1000
        out.append(dict(world_sites=n,interactions=len(events),touched_sites=len(ids),eager_latent_packed_bytes=(n+7)//8,relational_random_bits=rel.draws,latent_random_bits=lat.draws,relational_python_state_bytes=deep_size((rel.parent,rel.rank,rel.parity,rel.offset)),latent_python_state_bytes=deep_size((lat.x,lat.offset)),relational_wall_seconds=times[0],latent_wall_seconds=times[1]))
    return out

def kl_example(e=.1):
    # A=0/1 intervention changes parity, but either bit individually is always fair.
    p=[(1-e)/2,e/2,e/2,(1-e)/2]; q=[e/2,(1-e)/2,(1-e)/2,e/2]
    assert sum(p[:2])==sum(q[:2])==.5
    assert p[0]+p[2]==q[0]+q[2]==.5
    return dict(noise=e,marginal_kl_bits=0,joint_kl_bits=sum(a*math.log2(a/b) for a,b in zip(p,q)))

if __name__=='__main__':
    out=dict(exact_audit=exact_audit(),triangle_audit=triangle_audit(),scaling=scale_audit(),causal_divergence=kl_example())
    path=Path(__file__).with_name('hexcore_streamed_reality_results.json'); path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
