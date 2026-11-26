"""Exploratory BL04: reuse and audit learned symmetry quotients.
24 streams x 32 tasks x four regimes, seven paired policies. Fixed 10-bit
ambient space, rank 5. Each task has a fresh Boolean table. Rare shifts
flip one raw input. Only queried values enter learner. Exact external scoring.
Cost counts unique oracle calls, including audits and recovery, not FLOPs.
"""
import random,json,statistics,math
from pathlib import Path
import numpy as np
from bl03_quotient import independent,reps,support,table
N=10; SIZE=1<<N; R=5; T=32; SEEDS=24
POLICIES=['fresh','blind','audit4','audit16','audit64','adaptive','periodic']
FULL=[1<<i for i in range(N)]; X=np.arange(SIZE); PAR=np.array([i.bit_count()%2 for i in range(SIZE)])
def enc(b):
 a=np.zeros(SIZE,dtype=int)
 for i,v in enumerate(b):a|=PAR[X&v]<<i
 return a
def ecology(seed,regime):
 rng=random.Random(seed+98173);h=independent(N,R,rng);out=[]
 for t in range(T):
  shift=t>0 and rng.random()<{'stable':0,'mixed':.15,'volatile':.5,'rare':.15}[regime]
  if shift and regime!='rare':h=independent(N,R,rng)
  truth=np.array(table(R,rng))[enc(h)]
  if shift and regime=='rare':truth[rng.randrange(SIZE)]^=1
  out.append((truth,shift))
 return out
def run(tasks,policy,seed):
 b=FULL[:];rows=[];alpha=1;beta=9
 for t,(truth,shift) in enumerate(tasks):
  if policy=='fresh' or (policy=='periodic' and t%5==0):b=FULL[:]
  old=b[:];xs,_,_=reps(N,old);index=enc(old);obs=truth[xs];queries=len(xs);audit=0;recovery=0;found=False
  rng=random.Random(1000003*seed+7919*t+123)
  k={'fresh':0,'blind':0,'audit4':4,'audit16':16,'audit64':64,'periodic':16}.get(policy,0)
  if policy=='adaptive':k=min(128,max(4,math.ceil(16*math.sqrt((alpha/(alpha+beta))/.1))))
  if len(xs)<SIZE:
   candidates=sorted(set(range(SIZE))-set(xs))
   # Same random ordering for all audit policies, irrespective of k.
   rng.shuffle(candidates)
   for x in candidates[:k]:
    audit+=1;queries+=1
    if truth[x]!=obs[index[x]]:found=True;break
   if policy=='adaptive':alpha+=int(found);beta+=int(not found)
  if found:
   recovery=SIZE-queries;queries=SIZE;old=FULL[:];obs=truth;index=X
  new=[]
  for v in support(obs.tolist()):
   w=0
   for i,z in enumerate(old):
    if v>>i&1:w^=z
   new.append(w)
  b=new;errors=int(np.count_nonzero(truth!=obs[index]))
  assert not found or errors==0
  assert policy!='fresh' or errors==0
  rows.append(dict(t=t,shift=shift,queries=queries,audit=audit,recovery=recovery,errors=errors,rank=len(b),detected=found))
 return rows
def main():
 data={}
 for regime in ['stable','mixed','volatile','rare']:
  data[regime]={p:[] for p in POLICIES}
  for seed in range(SEEDS):
   tasks=ecology(seed,regime)
   for p in POLICIES:data[regime][p].append(run(tasks,p,seed))
  print(regime,flush=True)
  for p,hist in data[regime].items():
   flat=[r for h in hist for r in h];q=statistics.mean(sum(r['queries'] for r in h) for h in hist);err=sum(r['errors'] for r in flat)/(len(flat)*SIZE);bad=sum(r['errors']>0 for r in flat)/len(flat)
   print(p,round(q,1),round(err*100,6),round(bad*100,3),flush=True)
  Path(__file__).with_name('bl04_audit_results.json').write_text(json.dumps(data,separators=(',',':')))
if __name__=='__main__':main()
