import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np,json
from pathlib import Path
exec(Path(__file__).with_name('dragon.py').read_text().split('def simulate')[0])
W=[10,30,80,200]; specs=[(w,op) for w in W for op in [False,True]]; E=len(specs); step=10
names=[f'{w}/{"open" if op else "fixed"}' for w,op in specs]+['hedge','context_meta','discount_meta']
def run(seed,kind):
 rng=np.random.default_rng(seed); T=1200; qs=[]; b=0
 while len(qs)<T:
  d=30 if kind=='fast' else 200 if kind=='slow' else int(rng.choice([20,40,100,200,400])) if kind=='mixed' else (30 if len(qs)<T//2 else 200)
  g=groups[b%4]; chosen=rng.choice(g,min(4,len(g)),replace=False);w=np.zeros(K);w[chosen]=1/len(chosen);qs.extend(rng.choice(K,d,p=w));b+=1
 qs=np.array(qs[:T]); active=np.full(len(names),base); owned=[set(fixed) for _ in names];net=np.zeros(len(names));half=np.zeros((2,len(names)));shadow=np.zeros(E);context=np.zeros((3,E));disc=np.zeros(E)
 prefix=np.vstack([np.zeros(K),np.cumsum(np.eye(K)[qs],axis=0)]).astype(np.float32)
 def dist(t,w):return (prefix[t]-prefix[max(0,t-w)])/max(1,min(t,w))
 def pick(v):
  p=np.exp(v-v.max());return int(rng.choice(E,p=p/p.sum()))
 for t in range(0,T,step):
  rec=[]
  for i,(w,op) in enumerate(specs):
   allowed=np.arange(len(M)) if op else fixed
   scores=M[allowed]@(dist(t,w) if t else prior)*step
   penalties=.25+(~np.isin(allowed,list(owned[i])))*(2+cost[allowed]/100);penalties[allowed==active[i]]=0
   rec.append(int(allowed[np.argmax(scores-penalties)]))
  divergence=np.abs(dist(t,20)-dist(t-20,80)).sum()/2 if t>=40 else 0;c=int(divergence>.4)+int(divergence>.7)
  actions=rec+[rec[pick(.7*shadow)],rec[pick(.9*context[c])],rec[pick(.9*disc)]];rewards=[]
  for i,j in enumerate(actions):
   charge=0
   if j!=active[i]:
    charge=.25
    if j not in owned[i]:charge+=2+cost[j]/100;owned[i].add(j)
   active[i]=j;r=float(M[j,qs[t:t+step]].sum())-charge;net[i]+=r;half[int(t>=T//2),i]+=r;rewards.append(r)
  er=np.array(rewards[:E])/step;shadow+=er;context[c]=.97*context[c]+er;disc=.9*disc+er
 return net/T,half/(T/2)
if __name__=='__main__':
 out={}
 for kind in ['fast','slow','mixed','meta_shift']:
  runs=[run(s+100,kind) for s in range(8)];a=np.array([r[0] for r in runs]);best=np.argmax(a[:,:E].mean(0));delta=a[:,E+1]-a[:,best];out[kind]={'mean':dict(zip(names,a.mean(0).tolist())),'context_minus_best_fixed':float(delta.mean()),'paired_se':float(delta.std(ddof=1)/np.sqrt(len(delta))),'best_fixed':names[best],'half':np.mean([r[1] for r in runs],0).tolist(),'per_seed':a.tolist()};print(kind,out[kind]['mean'],flush=True)
 Path(__file__).with_name('recursive_adaptation_results.json').write_text(json.dumps({'names':names,'seeds':8,'requests':1200,'results':out},indent=2))
