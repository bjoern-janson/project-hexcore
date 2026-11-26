import numpy as np
from itertools import combinations
from sklearn.linear_model import LogisticRegression
from scipy.special import softmax

N,K=12,4
pairs=np.array(list(combinations(range(N),2))); sets=np.array(list(combinations(range(N),K)))
cover=np.array([np.isin(pairs,s).all(1) for s in sets],dtype=np.float32)
inc=np.eye(N)[pairs].sum(1)
# Six latent contexts, each associated with a randomly chosen graph of correction queries.
# The learner sees contexts and historical requests, not the generator's weights.
def trial(seed, ntrain=6000, ntest=2500):
 r=np.random.default_rng(seed); C=6
 weights=r.normal(0,0.6,(C,len(pairs)))
 for c in range(C):
  hot=r.choice(N,4,replace=False)
  weights[c]+=3.5*np.isin(pairs,hot).all(1)+1.0*np.isin(pairs,hot).any(1)
 probs=softmax(weights,axis=1)
 def sample(n,shift):
  z=r.integers(C,size=n); x=np.eye(C)[z]+r.normal(0,.30,(n,C))
  if shift=='iid': p=probs[z]
  elif shift=='relabel': p=probs[(z+1)%C]
  elif shift=='uniform': p=np.full((n,len(pairs)),1/len(pairs))
  elif shift=='mixture': p=.5*probs[z]+.5/len(pairs)
  elif shift=='novel':
   # previously uncommon requests become common, while the observed contexts stay the same
   p=softmax(-weights[z],axis=1)
  q=(r.random(n)[:,None]>np.cumsum(p,axis=1)).sum(1)
  return x,q,p
 x,q,_=sample(ntrain,'iid'); model=LogisticRegression(C=1,max_iter=200).fit(x,q)
 globalp=np.bincount(q,minlength=len(pairs))/ntrain
 # marginal policy is optimal for individual-bit retention, not necessarily joint requests
 out={}
 for shift in ['iid','mixture','relabel','uniform','novel']:
  x,q,p=sample(ntest,shift); pred=np.zeros_like(p); pred[:,model.classes_]=model.predict_proba(x)
  policies={
   'random':r.integers(len(sets),size=ntest),
   'recency':np.full(ntest,len(sets)-1),
   'global_joint':np.full(ntest,np.argmax(cover@globalp)),
   'learned_marginal':np.argmax((pred@inc)[:,sets].sum(2),axis=1),
   'learned_joint':np.argmax(pred@cover.T,axis=1),
   'oracle_distribution':np.argmax(p@cover.T,axis=1),
  }
  # New random independent bits each episode. If either requested bit was dropped,
  # the XOR is unidentifiable; guessing succeeds with probability 1/2.
  out[shift]={k:float(cover[v,q].mean()) for k,v in policies.items()}
 return out
if __name__=='__main__':
 import json
 results=[trial(s) for s in range(12)]
 summary={shift:{k:{'mean':float(np.mean([r[shift][k] for r in results])),'seed_sd':float(np.std([r[shift][k] for r in results],ddof=1))} for k in results[0][shift]} for shift in results[0]}
 print(json.dumps(summary,indent=2));open('/mnt/data/correction_memory_results.json','w').write(json.dumps({'summary':summary,'seeds':results},indent=2))
