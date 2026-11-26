import numpy as np, json
N=4; G=24; P=64; STEPS=250; SEEDS=12
X=np.array([sum(((i>>j)&1)<<i for i in range(16)) for j in range(N)],dtype=np.uint32); MASK=65535
popcount=np.array([i.bit_count() for i in range(65536)],dtype=np.uint8)
def run(seed,target,selection):
 r=np.random.default_rng(seed); a=np.empty((P,G,2),dtype=np.int16)
 for j in range(G): a[:,j,:]=r.integers(0,N+j,size=(P,2))
 def score(a):
  v=np.empty((P,N+G),dtype=np.uint32); v[:,:N]=X
  for j in range(G): v[:,N+j]=MASK^(v[np.arange(P),a[:,j,0]]&v[np.arange(P),a[:,j,1]])
  return 16-popcount[v[:,-1]^target].astype(int)
 best=0; hit=None; genome=None
 for t in range(STEPS):
  s=score(a)
  if int(s.max())>best: best=int(s.max()); genome=a[s.argmax()].tolist()
  if best==16 and hit is None: hit=(t+1)*P
  if selection:
   ids=r.integers(P,size=(P,4)); parents=ids[np.arange(P),s[ids].argmax(axis=1)]; b=a[parents].copy(); b[0]=a[s.argmax()]
  else: b=a[r.integers(P,size=P)].copy()
  start=1 if selection else 0
  for _ in range(2):
   k=np.arange(start,P); j=r.integers(G,size=len(k)); b[k,j,r.integers(2,size=len(k))]=(r.random(len(k))*(N+j)).astype(int)
  a=b
 return dict(best=best,hit=hit,genome=genome)
if __name__=='__main__':
 parity=int(X[0]^X[1]^X[2]^X[3]); out={}
 for name,target in [('parity',parity),('majority',sum((i.bit_count()>=3)<<i for i in range(16))),('random',0x9a37)]:
  out[name]={}
  for sel in [False,True]:
   rows=[run(s,target,sel) for s in range(SEEDS)]; out[name][str(sel)]=rows; print(name,sel,sum(x['hit'] is not None for x in rows),np.mean([x['best'] for x in rows]),flush=True)
 with open('/mnt/data/emergent_circuits_results.json','w') as f: json.dump(out,f,indent=2)
