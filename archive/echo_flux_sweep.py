import numpy as np,json
N=16; T=2400; S=24
# exploratory sweep: local synaptic decay and activity-dependent plasticity

def run(seed,eta,decay):
 r=np.random.default_rng(seed); q,_=np.linalg.qr(r.normal(size=(N,N))); v,w=q[:,0],q[:,1]; A=[.18*np.eye(N)+.72*np.outer(z,z) for z in [v,w]]
 W=r.normal(0,.08,(N,N)); W=(W+W.T)/2; x=r.normal(0,.2,N); noise=r.normal(0,.16,(T,N)); h=[]; f=[]
 for t in range(T):
  j=int(t>=T//2); u=x/(np.linalg.norm(x)+1e-12); old=x.copy(); x=.55*x+.45*np.tanh(W@x+1.8*(A[j]@u)+noise[t]); W=np.clip((1-decay)*W+eta*np.outer(x,x),-.6,.6); h.append(float((u@([v,w][j]))**2)); f.append(float(np.linalg.norm(x-old)))
 return [np.mean(h[900:1200]),np.mean(h[1200:1300]),np.mean(h[2100:]),np.mean(f[2100:])]
if __name__=='__main__':
 out=[]
 for eta,decay in [(0,0),(.001,.03),(.005,.03),(.025,.03),(.025,.01),(.025,.003),(.025,.001)]:
  a=np.array([run(s,eta,decay) for s in range(S)]); row={'eta':eta,'decay':decay,'mean':a.mean(0).tolist(),'seeds':a.tolist()};out.append(row);print(eta,decay,row['mean'],flush=True)
 json.dump(out,open('/mnt/data/echo_flux_sweep_results.json','w'),indent=2)
