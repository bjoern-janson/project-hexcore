"""Online representation selection, exact recoverability, six input bits.
Uses prior experiment's generic two-input NAND grammar; no novel primitive discovery.
All query truth tables calibrated, request identity revealed only AFTER encoder selection.
"""
import itertools as it, numpy as np, json
from pathlib import Path
p=Path(__file__).with_name('representation_discovery.py')
exec(p.read_text().split('# Use 600')[0])
D=[d for ds in qd.values() for d in ds]; K=len(D)
lib={}
for inds in it.combinations(range(len(C)),3):
 u=uncut[inds[0]]&uncut[inds[1]]&uncut[inds[2]]
 mask=sum((not bool(u&d))<<i for i,d in enumerate(D)); cost=sum(C[i][0] for i in inds)
 if mask not in lib or cost<lib[mask][0]:lib[mask]=(cost,inds)
M=np.array([[(m>>i)&1 for i in range(K)] for m in lib],dtype=np.float32)
cost=np.array([v[0] for v in lib.values()]); raw=np.flatnonzero(cost==12)
# Prior training uses uniform within each of first three families, plus pooled distribution.
lengths=[len(v) for v in qd.values()]; groups=np.split(np.arange(K),np.cumsum(lengths)[:-1]); priors=[]
for g in groups[:3]:
 w=np.zeros(K);w[g]=1/len(g);priors.append(w)
prior=np.mean(priors,axis=0); base=int(np.argmax(M[raw]@prior)); base=int(raw[base]); fixed=np.unique(np.r_[raw,[np.argmax(M@w-1e-6*cost) for w in priors]])
# Deduplicated library may be evaluated offline; charge runtime acquisition separately.
def simulate(seed,scenario,acq):
 rng=np.random.default_rng(seed); T=1200; block=100; distributions=[]
 for b in range(T//block):
  w=np.zeros(K)
  if scenario=='stationary':w=prior.copy()
  elif scenario=='switch':w[groups[b%4]]=1/len(groups[b%4])
  elif scenario=='localized':
   g=groups[b%4]; chosen=rng.choice(g,min(4,len(g)),replace=False);w[chosen]=1/len(chosen)
  elif scenario=='iid':w[:]=1/K
  distributions.append(w)
 qs=np.concatenate([rng.choice(K,block,p=w) for w in distributions]); out={}
 for mode in ['raw_fixed','raw_online','fixed_library','open_library','oracle']:
  active=base; owned=set(fixed if mode in ['fixed_library','open_library'] else raw); gross=fees=0.; buys=sw=0; hist=np.zeros(K,dtype=np.float32)
  for t,q in enumerate(qs):
   if mode=='oracle':active=int(np.argmax(M@distributions[t//block])) if t%block==0 else active
   elif mode!='raw_fixed' and t>=40 and t%20==0:
    allowed=raw if mode=='raw_online' else fixed if mode=='fixed_library' else np.arange(len(M))
    scores=M[allowed]@hist; penalties=np.full(len(allowed),.25); penalties+= (~np.isin(allowed,list(owned)))*(acq+cost[allowed]/100); penalties[allowed==active]=0; j=int(allowed[np.argmax(scores-penalties)])
    if j!=active:
     fees+=.25;sw+=1
     if j not in owned:fees+=acq+cost[j]/100; buys+=1;owned.add(j)
     active=j
   gross+=M[active,q];hist[q]+=1
   if t>=40:hist[qs[t-40]]-=1
  out[mode]=[gross/T,(gross-fees)/T,buys,sw]
 return out
R={}
for scenario in ['stationary','switch','localized','iid']:
 for fee in [0,2,8]:
  runs=[simulate(s,scenario,fee) for s in range(8)];R[f'{scenario}/{fee}']={k:np.mean([r[k] for r in runs],axis=0).tolist() for k in runs[0]}
result={'library':len(M),'fixed_library':len(fixed),'queries':K,'seeds':8,'episodes_per_seed':1200,'metrics':['gross','net','acquisitions','switches'],'results':R}
Path(__file__).with_name('dragon_results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
