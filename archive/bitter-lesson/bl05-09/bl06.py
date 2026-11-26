"""BL06: partial-feedback correction, audit-selection bias and drift.
Exploratory simulation, paired seeded worlds. A task has no defect or exactly
one. A fixed affordable query budget is imposed; a missed defect is not labeled
as a failure to the learner. Evaluator knows truth. Models learn only found
locations. Initial warmup observes six complete localizations, charged equally.
Compare uniform, frequency, affine priority, affine with uniform sentinels,
and independent full-audit calibration. All deployment arms have identical
query budget, except oracle control. No hidden-state or regime labels exposed.
"""
import numpy as np, random, json, csv, math, statistics, pathlib
from collections import Counter
from bl05 import random_flat, affine, ranked_query
N=1024; n=10; K=32; SEEDS=20; T=96; WARM=8; BUDGETS=(16,32,64)
POLICIES=('uniform','frequency','affine','sentinel25','sentinel50','independent_audit','oracle')
REGIMES=('stable','switch','hidden_tail','unstructured')
def make_world(seed,regime):
    rng=random.Random(6801+seed);a=random_flat(n,5,rng);b=random_flat(n,5,rng)
    # Select alternate support disjoint from the initial flat to cleanly test shift.
    while np.intersect1d(a,b).size:b=random_flat(n,5,rng)
    out=[]
    for t in range(T):
        if t<WARM: support=a; present=True
        else:
            present=rng.random()<.7
            support=a
            if regime=='switch' and t>=T//2:support=b
            if regime=='hidden_tail' and t>=T//2 and rng.random()<.3:support=b
            if regime=='unstructured' and t>=WARM:support=np.arange(N)
        target=int(rng.choice(support)) if present else -1
        order=np.random.default_rng(991*seed+t+73291).permutation(N)
        out.append((target,order,support))
    return out

def choose(history,order,budget,policy,t,support):
    if policy=='uniform':return order[:budget]
    if policy=='oracle':return np.concatenate((order[np.isin(order,support)],order[~np.isin(order,support)]))[:budget]
    if policy=='frequency':
        counts=Counter(history[-32:]);scores=np.array([counts.get(int(x),0) for x in order]);return order[np.argsort(-scores,kind="stable")[:budget]]
    pred,_,_=affine(history[-12:]);mask=np.isin(order,pred)
    # Priority uses only historical observations. Sentinels are disjoint uniform
    # positions reserved before exploitation; never adapt to the current target.
    reserve={'affine':0,'sentinel25':budget//4,'sentinel50':budget//2,'independent_audit':budget if t%4==0 else 0}[policy]
    random_part=order[:reserve];remaining=order[reserve:];m=mask[reserve:]
    return np.concatenate((random_part,remaining[m],remaining[~m]))[:budget]

def run(world,budget,policy):
    hist=[];rows=[]
    for t,(target,order,support) in enumerate(world):
        if t<WARM:
            q=int(np.where(order==target)[0][0])+1;found=True;hist.append(target)
        else:
            selected=choose(hist,order,budget,policy,t,support)
            assert len(set(selected))==budget
            found=target in selected;q=budget # entire audit set always charged
            if found and (policy!='independent_audit' or t%4==0):hist.append(target)
        rows.append(dict(t=t,defect=target>=0,found=bool(found),queries=q,alternate=bool(target>=0 and target not in world[0][2]),history=len(hist)))
    return rows

def main():
    data={};summary=[]
    for budget in BUDGETS:
        for regime in REGIMES:
            key=f'{budget}:{regime}';data[key]={p:[] for p in POLICIES}
            for seed in range(SEEDS):
                world=make_world(seed,regime)
                for p in POLICIES:data[key][p].append(run(world,budget,p))
            for p,hs in data[key].items():
                rr=[r for h in hs for r in h if r['t']>=WARM and r['defect']];late=[r for r in rr if r['t']>=T//2];alt=[r for r in late if r['alternate']]
                summary.append(dict(budget=budget,regime=regime,policy=p,recall=sum(r['found'] for r in rr)/len(rr),late_recall=sum(r['found'] for r in late)/len(late),alternate_recall=sum(r['found'] for r in alt)/max(1,len(alt)),mean_queries=statistics.mean(sum(r['queries'] for r in h) for h in hs)))
            print(key,[(s['policy'],round(s['late_recall'],3),round(s['alternate_recall'],3)) for s in summary if s['budget']==budget and s['regime']==regime],flush=True)
    root=pathlib.Path(__file__).parent
    (root/'bl06_results.json').write_text(json.dumps(data,separators=(',',':')))
    with (root/'bl06_summary.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=summary[0]);w.writeheader();w.writerows(summary)
if __name__=='__main__':main()
