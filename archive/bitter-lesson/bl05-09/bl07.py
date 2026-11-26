"""BL07: negative evidence, hidden fault regimes, and generic Bayesian rescue.
Exact finite affine-support posterior, with fully specified likelihoods. Exploratory.
All algorithms use the same four-query sets, five (WARM=5) complete
warmup localizations, and paired hidden outcomes. No current support is given
except to oracle. Unknown incidence is separately modeled by a finite mixture.
Reported posterior is exact for the specified model, not for mismatched worlds.
"""
import numpy as np, random, itertools, csv, pathlib, json, statistics, math
from bl05 import random_flat
N=32; n=5; d=2; K=4; B=4; T=96; WARM=5; SEEDS=48; P=.7; EPS=.02; HAZARD=.04
REGIMES=('stable','switch','hidden_tail','lower_incidence','uniform')
POLICIES=('uniform','positive_static','negative_static','positive_switch','negative_switch','negative_thompson','unknown_incidence','oracle')

def flats():
    linear=set()
    for a,b in itertools.combinations(range(1,N),2): linear.add(tuple(sorted((0,a,b,a^b))))
    out=sorted({tuple(sorted(x^v for v in S)) for S in linear for x in range(N)})
    arr=np.array(out,dtype=np.int16)
    assert len(arr)==1240 and len({tuple(a) for a in arr})==1240
    return arr
F=flats();M=len(F);IND=np.zeros((N,M),dtype=np.float64)
for i,s in enumerate(F):IND[s,i]=1
assert np.all(IND.sum(axis=0)==K)

def world(seed,regime):
    rng=random.Random(61301+seed);a=random_flat(n,d,rng);b=random_flat(n,d,rng)
    while np.intersect1d(a,b).size:b=random_flat(n,d,rng)
    rows=[]
    for t in range(T):
        u=rng.random();xa=int(rng.choice(a));xb=int(rng.choice(b));xu=rng.randrange(N)
        # All regimes share prefix. The hidden_tail and lower_incidence arms
        # are coupled pathwise: every query in A receives exactly same response.
        if t<WARM:target=xa;sup=a
        elif t<T//2 or regime=='stable':target=xa if u<P else -1;sup=a
        elif regime=='switch':target=xb if u<P else -1;sup=b
        elif regime=='hidden_tail':target=xa if u<.49 else xb if u<P else -1;sup=np.union1d(a,b)
        elif regime=='lower_incidence':target=xa if u<.49 else -1;sup=a
        else:target=xu if u<P else -1;sup=np.arange(N)
        order=np.random.default_rng(197721*seed+t+177).permutation(N)
        rows.append((target,order,sup,a,b))
    return rows

def normalize(w):
    s=w.sum();assert s>0 and np.isfinite(s);return w/s

def topk(prob,order,b=B):
    return order[np.argsort(-np.round(prob[order],14),kind='stable')[:b]]

def run(rows,policy,seed):
    w=np.full(M,1/M);rates=np.array([.3,.49,.7,.9]);j=np.full((len(rates),M),1/(len(rates)*M));out=[]
    rng=np.random.default_rng(773+seed)
    for t,(target,order,sup,a,b) in enumerate(rows):
        if t<WARM:
            # Exact query rank in common random order, not free labels.
            q=int(np.where(order==target)[0][0])+1;found=True;qs=np.array([target]);lik= (1-EPS)*IND[target]/K+EPS/N
            w=normalize(w*lik);j=normalize(j*lik[None,:])
        else:
            sw=policy in ('positive_switch','negative_switch','negative_thompson')
            if sw:w=(1-HAZARD)*w+HAZARD/M
            if policy=='unknown_incidence':
                j=(1-HAZARD)*j+HAZARD*j.sum(axis=1,keepdims=True)/M
                j=.98*j+.02*j.sum(axis=0,keepdims=True)/len(rates)
                prob=(rates@j)@IND.T/K
            else:prob=IND@w/K
            if policy=='uniform':qs=order[:B]
            elif policy=='oracle':qs=np.concatenate((order[np.isin(order,sup)],order[~np.isin(order,sup)]))[:B]
            elif policy=='negative_thompson':qs=F[rng.choice(M,p=w)]
            else:qs=topk(prob,order)
            assert len(set(qs))==B
            q=B;found=target in qs
            count=IND[qs].sum(axis=0)
            mass=(1-EPS)*count/K+EPS*B/N
            lik=((1-EPS)*IND[target]/K+EPS/N) if found else None
            if policy=='unknown_incidence':
                j=normalize(j*(rates[:,None]*lik[None,:] if found else (1-rates[:,None]*mass[None,:])))
            elif policy.startswith('positive') or policy.startswith('negative'):
                if found:w=normalize(w*lik)
                elif policy.startswith('negative'):w=normalize(w*(1-P*mass))
        # External evaluation: not provided to any policy.
        out.append(dict(t=t,present=target>=0,found=bool(found),alternate=bool(target>=0 and target not in a),queries=q,queries_outside=int(np.count_nonzero(~np.isin(qs,a))),estimated_rate=float((rates@j).sum()) if policy=='unknown_incidence' else P))
    return out

def main():
    # Verify the pathwise information boundary for 48 independent pairs.
    for seed in range(SEEDS):
        A=world(seed,'lower_incidence');B0=world(seed,'hidden_tail')
        for (x,_,_,a,_),(y,_,_,a2,_) in zip(A,B0):
            assert np.array_equal(a,a2) and all((q==x)==(q==y) for q in a)
    # Validate the negative likelihood for all singleton outcomes on a sample flat.
    s=F[11];qs=np.array([0,1,2,3]);dist=np.full(N,P*EPS/N);dist[s]+=P*(1-EPS)/K
    assert abs(1-dist[qs].sum()-(1-P*((1-EPS)*len(set(s)&set(qs))/K+EPS*B/N)))<1e-12
    data={};summary=[]
    for regime in REGIMES:
        data[regime]={p:[] for p in POLICIES}
        for seed in range(SEEDS):
            rows=world(seed,regime)
            for p in POLICIES:data[regime][p].append(run(rows,p,seed))
        for p,hs in data[regime].items():
            late=[r for h in hs for r in h if r['t']>=T//2];present=[r for r in late if r['present']];alt=[r for r in present if r['alternate']]
            per=[sum(r['found'] for r in h if r['t']>=T//2)/max(1,sum(r['present'] for r in h if r['t']>=T//2)) for h in hs]
            item=dict(regime=regime,policy=p,late_recall=sum(r['found'] for r in present)/len(present),alternate_recall=sum(r['found'] for r in alt)/max(1,len(alt)),mean_outside_queries=statistics.mean(r['queries_outside'] for r in late),mean_queries=statistics.mean(sum(r['queries'] for r in h) for h in hs),ci95=1.96*statistics.stdev(per)/math.sqrt(SEEDS),mean_estimated_rate=statistics.mean(r['estimated_rate'] for r in late));summary.append(item)
        print(regime,[(s['policy'],round(s['late_recall'],3),round(s['alternate_recall'],3),round(s['mean_outside_queries'],2)) for s in summary if s['regime']==regime],flush=True)
        root=pathlib.Path(__file__).parent
        (root/'bl07_results.json').write_text(json.dumps(data,separators=(',',':')))
        with (root/'bl07_summary.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=summary[0]);w.writeheader();w.writerows(summary)
    print('Verified local observation equivalence for all paired lower-incidence/hidden-tail histories.')
if __name__=='__main__':main()
