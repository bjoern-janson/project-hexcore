import numpy as np,json
N=16; T=1600; S=48
# Paired worlds, initial states and noise; no alignment information enters controller.
def run(world):
 rng=np.random.default_rng(4281); Q=np.linalg.qr(rng.normal(size=(S,N,N)))[0]; init=rng.normal(0,.2,(S,N)); noise=rng.normal(0,.16,(T,S,N)); en=rng.normal(0,world[0],(T,S,N)); mask=rng.random((T,S))>world[2]
 modes=['instant','fast','slow','fixed_mix','coupled','mutable','scrambled']; x=np.repeat(init[None],len(modes),0); fast=x*0; slow=x*0; gate=np.full((len(modes),S,1),.5); tau=np.full_like(gate,.035); hist=[]; gates=[]
 for t in range(T):
  v=Q[:,:,(t//world[1])%N]; u=x/(np.linalg.norm(x,axis=-1,keepdims=True)+1e-12); dot=np.sum(u*v,axis=-1); e=(.18*u+.72*dot[...,None]*v+en[t])*mask[t,:,None]; e[-1]=np.roll(e[-1],1,axis=-1)
  fast=.55*fast+.45*e; slow=(1-tau)*slow+tau*e
  # Local timescale disagreement; magnitude is dimensionless after normalization.
  d=np.linalg.norm(fast-slow,axis=-1,keepdims=True)/(np.linalg.norm(fast,axis=-1,keepdims=True)+np.linalg.norm(slow,axis=-1,keepdims=True)+1e-9)
  gate=.85*gate+.15*np.clip((d-.25)*2,0,1)
  tau[5:]=.95*tau[5:]+.05*(.015+.15*gate[5:])
  z=gate*fast+(1-gate)*slow; z[0]=e[0]; z[1]=fast[1]; z[2]=slow[2]; z[3]=.5*(fast[3]+slow[3]);
  x=.55*x+.45*np.tanh(1.8*z+noise[t]); hist.append(dot**2); gates.append(gate[...,0].copy())
 a=np.array(hist); g=np.array(gates); starts=list(range(world[1],T-50,world[1])); early=np.concatenate([a[t:t+50] for t in starts]).mean(0)
 return {m:{'all':a[:,i].mean(0).tolist(),'early':early[i].tolist(),'late':a[-100:,i].mean(0).tolist(),'gate':g[:,i].mean(0).tolist()} for i,m in enumerate(modes)}
if __name__=='__main__':
 worlds={'clean':(0,400,0),'noisy':(.20,400,0),'rapid':(.20,80,0),'intermittent':(.12,400,.6),'very_noisy':(.45,400,0)}; out={k:run(w) for k,w in worlds.items()}; json.dump(out,open('/mnt/data/echo_timescales_results.json','w'),indent=2)
 for k,r in out.items(): print(k,[(m,round(np.mean(v['all'])*100,2),round(np.mean(v['early'])*100,2)) for m,v in r.items()])
