import numpy as np,json
from concurrent.futures import ProcessPoolExecutor
N=80; G=12; P=4; T=1800
# Generic recurrent NAND network. All nodes use same update rule; every edge and output tap mutable.
# External ports: local cue (one bit), cue available, encounter phase, partner signal.
def step(g,s,ports):
 v=np.concatenate((s,ports),axis=1); k=np.arange(len(s))[:,None]
 return ~(v[k,g[:,:,0]] & v[k,g[:,:,1]])
def encounter(g,taps,cue,role,partner,mode='normal'):
 n=len(g); k=np.arange(n); s=np.zeros((n,G),bool)
 ports=np.stack((cue&role,role,np.zeros(n,bool),np.zeros(n,bool)),1)
 s=step(g,s,ports); msg=s[k,taps[:,1]].copy()
 if mode in ('no_memory','neither'): s[:]=False
 incoming=msg[partner] if mode not in ('no_signal','neither') else np.zeros(n,bool)
 s=step(g,s,np.stack((np.zeros(n,bool),np.zeros(n,bool),np.ones(n,bool),incoming),1))
 return s[k,taps[:,0]]
def trial(g,taps,seed):
 r=np.random.default_rng(seed); n=len(g); out={m:[0,0] for m in ('normal','no_memory','no_signal','neither')}; den=[0,0]
 for _ in range(100):
  p=r.permutation(n).reshape(-1,2); partner=np.empty(n,int); partner[p[:,0]]=p[:,1];partner[p[:,1]]=p[:,0]
  role=np.zeros(n,bool); role[p[:,0]]=1; cue=np.zeros(n,bool);cue[p[:,0]]=r.integers(2,size=len(p));cue[p[:,1]]=cue[p[:,0]]
  for j in (0,1):den[j]+=np.sum(role==j)
  for m in out:
   a=encounter(g,taps,cue,role,partner,m)
   for j in (0,1):out[m][j]+=int(np.sum((a==cue)&(role==j)))
 return {m:[v[j]/den[j] for j in (0,1)] for m,v in out.items()}
def run(seed,signal):
 r=np.random.default_rng(seed); g=r.integers(G+P,size=(N,G,2));taps=r.integers(G,size=(N,2)); energy=np.full(N,8.); alive=np.arange(N)<40
 initial=trial(g[:40],taps[:40],seed+10000); births=deaths=0; trace=[]
 for t in range(T):
  ids=np.flatnonzero(alive); n=len(ids)//2*2
  if n<2:break
  ids=r.permutation(ids)[:n]; partner=np.arange(n)^1;role=np.arange(n)%2==0;cue=np.repeat(r.integers(2,size=n//2).astype(bool),2)
  a=encounter(g[ids],taps[ids],cue,role,partner,'normal' if signal else 'no_signal')
  # two travel actions; only one destination contains food. No performance ranking.
  energy[ids]+=np.where(a==cue,2.,-2.); energy[ids]-=.25
  dead=ids[energy[ids]<=0];alive[dead]=False;deaths+=len(dead)
  parents=ids[(energy[ids]>=14)&alive[ids]]; slots=np.flatnonzero(~alive)
  for p,c in zip(r.permutation(parents),slots):
   energy[p]-=7;energy[c]=7;alive[c]=True;g[c]=g[p];taps[c]=taps[p]
   if r.random()<.8:g[c,r.integers(G),r.integers(2)]=r.integers(G+P)
   if r.random()<.3:taps[c,r.integers(2)]=r.integers(G)
   births+=1
  energy=np.minimum(energy,18)
  if t%100==0:trace.append(int(alive.sum()))
 ids=np.flatnonzero(alive);ids=ids[:len(ids)//2*2]; final=trial(g[ids],taps[ids],seed+20000) if len(ids) else None
 return dict(seed=seed,signal=signal,births=births,deaths=deaths,pop=int(alive.sum()),initial=initial,final=final,trace=trace,genomes=g[ids].tolist(),taps=taps[ids].tolist())
if __name__=='__main__':
 jobs=[(s,b) for s in range(8) for b in (True,False)]
 with ProcessPoolExecutor(max_workers=8) as ex: results=list(ex.map(run,*zip(*jobs)))
 json.dump(results,open('/mnt/data/port_ecology_results.json','w'),indent=2)
 for b in (True,False):
  rr=[x for x in results if x['signal']==b];live=[x for x in rr if x['final']];print(b,'births',sum(x['births'] for x in rr),'survived',len(live));print('initial',np.mean([x['initial']['normal'] for x in rr],0));print({m:np.mean([x['final'][m] for x in live],0).tolist() for m in rr[0]['initial']} if live else {})
