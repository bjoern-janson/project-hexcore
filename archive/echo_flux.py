import numpy as np,json
# Hidden world: passive reflected signal e = A u, where A is symmetric positive definite.
# The medium receives e, emits u, and changes recurrent connections by local Hebbian activity.
# No target or reward is used in updates. Alignment is measured only by the experimenter.
N=16; T=2400; S=24

def run(seed,mode):
 r=np.random.default_rng(seed); q,_=np.linalg.qr(r.normal(size=(N,N))); v=q[:,0]; w=q[:,1]
 A0=.18*np.eye(N)+.72*np.outer(v,v); A1=.18*np.eye(N)+.72*np.outer(w,w)
 W=r.normal(0,.08,(N,N)); W=(W+W.T)/2; x=r.normal(0,.2,N)
 noise=r.normal(0,.16,(T,N)); perm=r.permutation(N); hist=[]; energy=[]; flux=[]
 for t in range(T):
  A=A0 if t<T//2 else A1; target=v if t<T//2 else w
  u=x/(np.linalg.norm(x)+1e-12); echo=A@u
  if mode=='scrambled': echo=echo[perm]
  if mode=='uncoupled': echo=np.zeros(N)
  old=x.copy(); x=.55*x+.45*np.tanh(W@x+1.8*echo+noise[t]);
  if mode!='frozen':
   # local correlation and leakage; bounded synaptic magnitudes, no global fitness
   W=.997*W+.025*np.outer(x,x); W=np.clip(W,-.6,.6)
  hist.append(float((u@target)**2)); energy.append(float(np.linalg.norm(A@u)**2)); flux.append(float(np.linalg.norm(x-old)))
 return {'first':np.mean(hist[900:1200]),'early_shift':np.mean(hist[1200:1300]),'late_shift':np.mean(hist[2100:]),'echo_power':np.mean(energy[2100:]),'flux':np.mean(flux[2100:]),'trace':[float(np.mean(hist[i:i+100])) for i in range(0,T,100)]}
if __name__=='__main__':
 out={m:[run(s,m) for s in range(S)] for m in ['coupled','frozen','scrambled','uncoupled']}
 summary={m:{k:float(np.mean([r[k] for r in rs])) for k in ['first','early_shift','late_shift','echo_power','flux']} for m,rs in out.items()}
 print(json.dumps(summary,indent=2)); json.dump({'summary':summary,'runs':out},open('/mnt/data/echo_flux_results.json','w'),indent=2)
