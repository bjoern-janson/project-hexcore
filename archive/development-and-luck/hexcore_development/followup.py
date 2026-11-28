"""DEV-02: ordinary learned selection of existing growth priors."""
import json, math, random, statistics, time
from collections import Counter
from pathlib import Path
from development import CAT, unit, run, shape, ci
HERE=Path(__file__).parent
LAWS=('uniform','edge','balanced')
def tuple_tree(t):return None if t is None else tuple(tuple_tree(s) for s in t)
def likelihood(s,law):
    if s is None:return 1,1.,1
    a,p,u=likelihood(s[0],law);b,q,v=likelihood(s[1],law);n=a+b
    if law=='uniform':w=CAT[a-1]*CAT[b-1]/CAT[n-1]
    elif law=='edge':w=(1. if n==2 else .5) if min(a,b)==1 else 0.
    else:w=(1. if a==b else .5) if abs(a-b)<=1 else 0.
    return n,p*q*w,u+v+1
def fit(records):
    scores={k:0. for k in LAWS};work=0;t0=time.perf_counter()
    for s in records:
        n,p,u=likelihood(s,'uniform')
        for k in LAWS:
            _,q,v=likelihood(s,k);work+=v+1;scores[k]+=math.log(.95*q+.05*p)
        work+=u
    winner=max(LAWS,key=scores.get)
    def gen(n,r):return shape(n,r,'uniform' if r.random()<.05 else winner)
    return gen,{'expert':winner,'fit_work':work,'scores':scores,'fit_seconds':time.perf_counter()-t0}
def main():
    prev=json.loads((HERE/'results.json').read_text());rows=[]
    for row in prev['runs']:
        seed=row['seed'];law=row['train_law'];n=row['n'];training=row['training'];rec=[tuple_tree(s) for t in training for s in t['success_shapes']]
        gen,fitinfo=fit(rec);tw=sum(t['work'] for t in training);steps=prev['config']['test_proposals'];life=(row['pooled_lifetime_budget']-tw-fitinfo['fit_work'])//unit(n);assert life>0
        suites={k:set(v) for k,v in prev['targets'][str(seed)][str(n)].items()};shared=700000+10000*seed+100*n
        same=run(n,gen,steps,suites,shared);equal=run(n,gen,life,suites,shared)
        for r in (same,equal):r['total_work']=r['work']+tw+fitinfo['fit_work']
        assert equal['total_work']<=row['pooled_lifetime_budget']
        rows.append({'seed':seed,'train_law':law,'n':n,'fit':fitinfo,'same':same,'equal':equal,'pooled':row['outcomes']['pooled_grammar']})
    summary={}
    for law in ('edge','balanced'):
        for n in (7,8):
            g=[r for r in rows if r['train_law']==law and r['n']==n];k=f'{law}_{n}';summary[k]={'expert_selection':dict(Counter(r['fit']['expert'] for r in g))}
            for arm in ('same','equal','pooled'):
                summary[k][arm]={'hits':{a:statistics.mean(r[arm]['hits'][a] for r in g) for a in LAWS},'work':statistics.mean(r[arm]['total_work'] for r in g),'seconds':statistics.mean(r[arm]['seconds'] for r in g)}
            summary[k]['equal_minus_pooled']={a:ci([r['equal']['hits'][a] for r in g],[r['pooled']['hits'][a] for r in g]) for a in LAWS}
            print(k,summary[k],flush=True)
    (HERE/'followup_results.json').write_text(json.dumps({'summary':summary,'runs':rows},indent=2)+'\n')
if __name__=='__main__':main()
