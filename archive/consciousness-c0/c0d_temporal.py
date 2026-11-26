"""C0d exploratory temporal attribution assay; standard library only.
The parity feature is inherited from C0c, not rediscovered. Candidate temporal
models are supplied. Predict z before seeing x,y; actions are randomized.
All models receive identical observations; no model receives the true mode.
"""
import random, math, statistics
N=2000; T=96; SWITCH=48; SEED=20261124; NOISE=.1; HAZARD=.06
MODES=('current','lagged','independent')
def normalize(v):
    s=sum(v); return [x/s for x in v]
def run():
    rng=random.Random(SEED)
    cases={'switch current->lagged':(0,1),'switch lagged->independent':(1,2),'stationary current':(0,0),'stationary independent':(2,2)}
    names=('current only','lag only','static mixture','window-12','switching mixture','oracle')
    for case,(before,after) in cases.items():
        losses={k:[] for k in names}; late={k:[] for k in names}; early={k:[] for k in names}; acc=[]; nullmass=[]; delays=[]
        for _ in range(N):
            prev=rng.randrange(2); static=[1/3]*3; dynamic=static[:]; hist=[]; ls={k:[] for k in names}; correct=[]; mass=[]; first=None
            for t in range(T):
                a=rng.randrange(2); u=rng.randrange(2); mode=before if t<SWITCH else after
                probs=[NOISE+(1-2*NOISE)*a,NOISE+(1-2*NOISE)*prev,.5]
                z=(a if mode==0 else prev if mode==1 else rng.randrange(2))
                if mode!=2 and rng.random()<NOISE: z^=1
                x=u; y=u^z; z=x^y
                prior=[(1-HAZARD)*p+HAZARD/3 for p in dynamic]
                window=normalize([math.prod(row[i] for row in hist[-12:]) for i in range(3)])
                predictions=[probs[0],probs[1],sum(p*q for p,q in zip(static,probs)),sum(p*q for p,q in zip(window,probs)),sum(p*q for p,q in zip(prior,probs)),probs[mode]]
                for k,p in zip(names,predictions): ls[k].append(-math.log2(p if z else 1-p))
                likelihood=[p if z else 1-p for p in probs]; hist.append(likelihood)
                static=normalize([p*q for p,q in zip(static,likelihood)]); dynamic=normalize([p*q for p,q in zip(prior,likelihood)])
                if t>=SWITCH:
                    correct.append(max(range(3),key=lambda i:dynamic[i])==mode); mass.append(dynamic[2]);
                    if first is None and dynamic[mode]>=.8: first=t-SWITCH+1
                prev=a
            for k in names:
                losses[k].append(statistics.mean(ls[k])); early[k].append(statistics.mean(ls[k][SWITCH:SWITCH+12])); late[k].append(statistics.mean(ls[k][-24:]))
            acc.append(statistics.mean(correct)); nullmass.append(statistics.mean(mass[-24:])); delays.append(first if first is not None else 49)
        print('\n'+case)
        print('model | whole loss | first 12 after midpoint | final 24 | paired delta vs window (whole), 95% MC CI')
        for k in names:
            d=[x-y for x,y in zip(losses[k],losses['window-12'])]; m=statistics.mean(d); se=statistics.stdev(d)/math.sqrt(N)
            print(f'{k:20} {statistics.mean(losses[k]):.4f} {statistics.mean(early[k]):.4f} {statistics.mean(late[k]):.4f} {m:+.4f} [{m-1.96*se:+.4f},{m+1.96*se:+.4f}]')
        print(f'post-midpoint mode accuracy={statistics.mean(acc):.4f}; final null posterior={statistics.mean(nullmass):.4f}; first >=.8 median (49=censored)={statistics.median(delays)}; reached by end={sum(d<49 for d in delays)/N:.4f}')
if __name__=='__main__':
    print(f'Exploratory simulation: {N} episodes/case, {T} steps, seed={SEED}, noise={NOISE}, switching hazard={HAZARD}; bits/step; paired episode-level normal MC intervals.')
    run()
