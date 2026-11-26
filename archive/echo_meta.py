import numpy as np,json
N=16; T=2400; S=64
def run(mode,world):
 rngs=[np.random.default_rng(s+1000) for s in range(S)]
 Q=np.array([np.linalg.qr(r.normal(size=(N,N)))[0] for r in rngs]); W=np.array([r.normal(0,.08,(N,N)) for r in rngs]); W=(W+W.transpose(0,2,1))/2
 x=np.array([r.normal(0,.2,N) for r in rngs]); noise=np.array([r.normal(0,.16,(T,N)) for r in rngs]); en=np.array([r.normal(0,.12,(T,N)) for r in rngs]); mask=np.array([r.random(T) for r in rngs]); rate=np.full((S,N),.001); hist=[]; flux=[]; rates=[]
 for t in range(T):
  j=(t//400)%6 if world=='rapid' else int(t>=T//2); v=Q[:,:,j]; u=x/(np.linalg.norm(x,axis=1,keepdims=True)+1e-12); dot=np.sum(u*v,axis=1); e=.18*u+.72*dot[:,None]*v
  if world=='noisy': e=e+en[:,t]
  if world=='intermittent': e=e*(mask[:,t,None]>.6)
  if mode=='scrambled': e=np.roll(e,1,axis=1)
  old=x.copy(); x=.55*x+.45*np.tanh(np.einsum('sij,sj->si',W,x)+1.8*e+noise[:,t]);
  if mode=='frozen': pass
  elif mode=='weak': W=.97*W+.001*x[:,:,None]*x[:,None,:]
  elif mode=='strong': W=.97*W+.025*x[:,:,None]*x[:,None,:]
  else:
   agreement=np.maximum(0,u*e); disagreement=np.maximum(0,-u*e)
   rate=.95*rate+.05*np.clip(.0002+.06*agreement,0,.008)
   decay=.03+.4*disagreement
   eta=np.sqrt(rate[:,:,None]*rate[:,None,:]); d=(decay[:,:,None]+decay[:,None,:])/2
   W=(1-d)*W+eta*x[:,:,None]*x[:,None,:]
  W=np.clip(W,-.6,.6); hist.append(dot**2); flux.append(np.linalg.norm(x-old,axis=1)); rates.append(rate.mean(axis=1))
 a=np.array(hist); f=np.array(flux); rr=np.array(rates); starts=[400,800,1200,1600,2000] if world=='rapid' else [1200]; early=np.concatenate([a[t:t+50] for t in starts]).mean(axis=0)
 return {'late':a[2100:].mean(axis=0).tolist(),'early':early.tolist(),'all':a.mean(axis=0).tolist(),'flux':f[2100:].mean(axis=0).tolist(),'rate':rr[2100:].mean(axis=0).tolist()}
if __name__=='__main__':
 out={}
 for world in ['clean','noisy','intermittent','rapid']:
  out[world]={}
  for mode in ['frozen','weak','strong','adaptive','scrambled']:
   z=run(mode,world); out[world][mode]=z; print(world,mode,{k:round(float(np.mean(v)),4) for k,v in z.items()},flush=True)
 json.dump(out,open('/mnt/data/echo_meta_results.json','w'),indent=2)
