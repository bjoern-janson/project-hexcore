import numpy as np, json
# 2D torus; food diffuses via random deposition; local sensor and recurrent random circuit.
L=24; N=96; G=16; T=3000

def run(seed,blind=False,neutral=False):
 r=np.random.default_rng(seed); food=np.zeros((L,L),int); x=r.integers(L,size=N); y=r.integers(L,size=N); energy=np.full(N,15.); alive=np.arange(N)<24
 # input: four adjacent food presence, current food, previous internal bits, constant
 genes=r.integers(0,8+G,size=(N,G,2)); genes=np.minimum(genes,np.arange(G)[None,:,None]+7); out=r.integers(8+G,size=(N,4)); mem=np.zeros((N,2),bool); births=deaths=0; trace=[]; initial=[]
 for i in np.flatnonzero(alive):
  v=np.zeros((4,8+G),bool); v[:,:4]=np.eye(4,dtype=bool); v[:,7]=1
  for j in range(G): v[:,8+j]=~(v[:,genes[i,j,0]] & v[:,genes[i,j,1]])
  o=v[:,out[i]]; initial.append(float(np.mean(o[:,0].astype(int)+2*o[:,1]==np.arange(4))))
 for t in range(T):
  a,b=r.integers(L,size=(2,10)); np.add.at(food,(a,b),1); food=np.minimum(food,3)
  ids=np.flatnonzero(alive)
  if not len(ids): break
  xx=x[ids]; yy=y[ids]; sense=np.stack([food[(xx+1)%L,yy]>0,food[(xx-1)%L,yy]>0,food[xx,(yy+1)%L]>0,food[xx,(yy-1)%L]>0,food[xx,yy]>0],1)
  v=np.zeros((len(ids),8+G),bool); v[:,:5]=False if blind else sense; v[:,5:7]=mem[ids]; v[:,7]=True; k=np.arange(len(ids))
  for j in range(G): v[:,8+j]=~(v[k,genes[ids,j,0]] & v[k,genes[ids,j,1]])
  o=v[k[:,None],out[ids]]; mem[ids]=o[:,2:]; d=o[:,0].astype(int)+2*o[:,1]; x[ids]=(xx+np.array([1,-1,0,0])[d])%L; y[ids]=(yy+np.array([0,0,1,-1])[d])%L
  energy[ids]-=1
  for i in r.permutation(ids):
   if food[x[i],y[i]]: food[x[i],y[i]]-=1; energy[i]+=3
  dead=ids[energy[ids]<=0]; alive[dead]=False; deaths+=len(dead)
  parents=ids[(energy[ids]>=24)&alive[ids]]; slots=np.flatnonzero(~alive)
  for p,c in zip(r.permutation(parents),slots):
   if neutral: p=r.choice(np.flatnonzero(alive))
   energy[p]-=10; energy[c]=10; alive[c]=True; x[c]=x[p]; y[c]=y[p]; genes[c]=genes[p]; out[c]=out[p]; mem[c]=False
   j=r.integers(G); genes[c,j,r.integers(2)]=r.integers(8+j); out[c,r.integers(4)]=r.integers(8+G); births+=1
  if t%100==0: trace.append(int(alive.sum()))
 # measure frozen policy under balanced artificial sensor patterns; compare paired food-directed action to shuffled sensors
 ids=np.flatnonzero(alive); scores=[]
 for i in ids:
  v=np.zeros((4,8+G),bool); v[:,:4]=np.eye(4,dtype=bool) if not blind else False; v[:,7]=1
  for j in range(G): v[:,8+j]=~(v[:,genes[i,j,0]] & v[:,genes[i,j,1]])
  o=v[:,out[i]]; d=o[:,0].astype(int)+2*o[:,1]; scores.append(float(np.mean(d==np.arange(4))))
 return dict(seed=seed,blind=blind,neutral=neutral,births=births,deaths=deaths,pop=int(alive.sum()),trace=trace,initial=float(np.mean(initial)),probe=float(np.mean(scores)) if scores else None)
if __name__=='__main__':
 from concurrent.futures import ProcessPoolExecutor
 jobs=[(s,b,False) for s in range(8) for b in (False,True)]
 with ProcessPoolExecutor(max_workers=8) as ex: results=list(ex.map(run,*zip(*jobs)))
 print(results); json.dump(results,open('/mnt/data/ecology_results.json','w'),indent=2)
