"""BL05 exploratory: acquire error-localization instruments from prior corrections.
Equal prior error locations in every arm: every task has exactly one defect and
all policies search until they find it. The evaluator calculates the exact
membership-query rank in a policy's ordering; learner never sees the target
until that point. No error-location oracle outside the search. Public flat
rank d=floor(n/2) is an inductive bias, not an inferred fact. Query costs are
not FLOPs; planning costs and training history are included separately.
"""
import random, json, math, time, statistics, pathlib, csv
from collections import Counter
import numpy as np
SIZES=(8,10,12); SEEDS=16; T=48
POLICIES=('uniform','frequency','affine_all','affine_window','affine_restart','portfolio','oracle_support')
REGIMES=('affine','uniform','random_support','switch','outliers')
def basis(vs):
    piv={}; xors=0
    for v in vs:
        while v:
            k=v.bit_length()-1
            if k in piv: v ^= piv[k]; xors+=1
            else: piv[k]=v;break
    return list(piv.values()),xors

def span(bs):
    result=[0]
    for v in bs: result += [x^v for x in result]
    return result

def random_flat(n,d,rng):
    vs=[]
    while len(vs)<d:
        v=rng.randrange(1,1<<n)
        if len(basis(vs+[v])[0])>len(vs): vs.append(v)
    a=rng.randrange(1<<n)
    return np.array(sorted(a^v for v in span(vs)),dtype=np.int32)

def ecology(n,seed,regime):
    rng=random.Random(200000*n+seed);N=1<<n;d=n//2
    a=random_flat(n,d,rng);b=random_flat(n,d,rng)
    if regime=='random_support': a=np.array(rng.sample(range(N),1<<d),dtype=np.int32)
    rows=[]
    for t in range(T):
        support= a if regime!='switch' or t<T//2 else b
        if regime=='uniform' or (regime=='outliers' and rng.random()<.1): support=np.arange(N,dtype=np.int32)
        target=int(rng.choice(support))
        order=np.random.default_rng(10000000*n+10000*seed+t).permutation(N)
        ranks=np.empty(N,dtype=np.int32);ranks[order]=np.arange(N,dtype=np.int32)
        rows.append((target,support,ranks))
    return rows

def affine(history):
    if not history:return np.array([],dtype=np.int32),0,0
    a=history[0];bs,xors=basis([v^a for v in history]);
    return np.array([a^v for v in span(bs)],dtype=np.int32),xors+len(history)+2*(1<<len(bs)),len(bs)

def ranked_query(target,ranks,pred):
    """Exact query count for deterministic priority-set ordering then random complement."""
    if len(pred)==0:return int(ranks[target])+1
    k=int(np.count_nonzero(ranks[pred]<ranks[target]))
    return k+1 if np.any(pred==target) else len(pred)+int(ranks[target])-k+1

def probability_vector(pred,N,K,noise=.05):
    # Posterior predictive for a uniform hidden K-set or K-sized affine flat
    # given the appropriate observed set/hull. Invalid model -> uniform.
    if len(pred)>K or len(pred)==0 or K==N:return np.full(N,1/N)
    p=np.full(N,(1-noise)*(K-len(pred))/(K*(N-len(pred)))+noise/N)
    p[pred]=(1-noise)/K+noise/N
    assert abs(float(p.sum())-1)<1e-10
    return p

def run(n,rows,policy):
    hist=[];restart=[];counts=Counter();out=[];N=1<<n;d=n//2;K=1<<d
    weights=np.ones(5)/5
    for t,(target,true_support,ranks) in enumerate(rows):
        start=time.perf_counter_ns();work=0;rank=None;hit=False;predsize=0
        if policy=='uniform':q=int(ranks[target])+1
        elif policy=='frequency':
            # Generic categorical counts; unseen positions are exchangeable.
            ct=counts[target];better=sum(c>ct for c in counts.values())
            if ct:
                ties=sum(c==ct and ranks[x]<ranks[target] for x,c in counts.items());q=better+ties+1
            else:
                q=len(counts)+int(ranks[target])-sum(ranks[x]<ranks[target] for x in counts)+1
            work=len(counts);hit=bool(ct);predsize=len(counts)
        elif policy=='oracle_support':
            q=ranked_query(target,ranks,true_support);predsize=len(true_support);hit=True
        elif policy=='portfolio':
            # Strong generic Bayesian predictive portfolio (fixed-share mixture).
            # Experts: iid uniform, arbitrary support, affine all/window/restart.
            ps=[np.full(N,1/N), probability_vector(np.array(list(counts),dtype=np.int32),N,K)]
            for h in [hist,hist[-2*(d+1):],restart]:
                p,w,r=affine(h);work+=w;ps.append(probability_vector(p,N,K))
            P=np.stack(ps);prob=weights@P
            # Fully specify query ordering before evaluator computes target rank.
            # Rounded scores ensure mathematically equal probabilities tie fairly.
            prob=np.round(prob,15);p=prob[target]
            q=1+int(np.count_nonzero(prob>p))+int(np.count_nonzero((prob==p)&(ranks<ranks[target])))
            weights=weights*P[:,target];weights/=weights.sum();weights=.95*weights+.05/5
            work+=5*N;hit=True;predsize=N
        else:
            use=hist if policy=='affine_all' else hist[-2*(d+1):] if policy=='affine_window' else restart
            pred,work,rank=affine(use)
            q=ranked_query(target,ranks,pred);hit=bool(np.any(pred==target));predsize=len(pred)
        assert 1<=q<=N
        hist.append(target);counts[target]+=1;restart.append(target)
        if len(restart)>1 and len(basis([v^restart[0] for v in restart])[0])>d:
            restart=[target]
        out.append(dict(t=t,queries=int(q),work=int(work),rank=rank,hit=hit,pred_size=predsize,ns=time.perf_counter_ns()-start))
    return out

def tests():
    rng=random.Random(172)
    for n in range(2,7):
        N=1<<n
        for _ in range(50):
            order=list(range(N));rng.shuffle(order);ranks=np.argsort(order)
            pred=np.array(rng.sample(range(N),rng.randrange(N+1)),dtype=np.int32)
            ordered=[x for x in order if x in pred]+[x for x in order if x not in pred]
            for x in range(N):assert ranked_query(x,ranks,pred)==ordered.index(x)+1

def main():
    tests();data={};summary=[]
    for n in SIZES:
        for regime in REGIMES:
            key=f'{n}:{regime}';data[key]={p:[] for p in POLICIES}
            for seed in range(SEEDS):
                rows=ecology(n,seed,regime)
                for p in POLICIES:data[key][p].append(run(n,rows,p))
            print(key,flush=True)
            for p,hist in data[key].items():
                vals=[sum(r['queries'] for r in h) for h in hist]
                late=[statistics.mean(r['queries'] for r in h[-16:]) for h in hist]
                early=[statistics.mean(r['queries'] for r in h[:16]) for h in hist]
                base=[sum(r['queries'] for r in h) for h in data[key]['uniform']]
                diff=[a-b for a,b in zip(base,vals)]
                item=dict(n=n,regime=regime,policy=p,mean_queries=statistics.mean(vals),early=statistics.mean(early),late=statistics.mean(late),paired_gain=statistics.mean(diff),ci95=1.96*statistics.stdev(diff)/math.sqrt(SEEDS),mean_work=statistics.mean(sum(r['work'] for r in h) for h in hist),mean_ns=statistics.mean(sum(r['ns'] for r in h) for h in hist))
                summary.append(item); print(p,round(item['mean_queries'],1),round(item['late'],1),flush=True)
            # Persist complete conditions, even if a later condition is interrupted.
            root=pathlib.Path(__file__).parent
            (root/"bl05_results.json").write_text(json.dumps(data,separators=(",",":")))
            with (root/"bl05_summary.csv").open("w") as f:
                w=csv.DictWriter(f,fieldnames=summary[0]);w.writeheader();w.writerows(summary)
    root=pathlib.Path(__file__).parent
    (root/'bl05_results.json').write_text(json.dumps(data,separators=(',',':')))
    with (root/'bl05_summary.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=summary[0]);w.writeheader();w.writerows(summary)
if __name__=='__main__':main()
