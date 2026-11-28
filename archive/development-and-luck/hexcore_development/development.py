"""DEV-01, Python 3.10+, NumPy for bootstrap."""
import argparse,itertools,json,math,random,statistics,time
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
CAT=[math.comb(2*i,i)//(i+1) for i in range(9)]
SPLITS={n:tuple(range(1,n)) for n in range(2,9)}
WEIGHTS={n:[CAT[k-1]*CAT[n-k-1] for k in SPLITS[n]] for n in SPLITS}
TRAIN=((4,500),(5,1000))
def cat(n,k):return 'edge' if min(k,n-k)==1 else 'central' if abs(n-2*k)<=1 else 'other'
GROUPS={n:{c:tuple(k for k in SPLITS[n] if cat(n,k)==c) for c in ('edge','central','other')} for n in SPLITS}
GROUPS={n:{c:ks for c,ks in g.items() if ks} for n,g in GROUPS.items()}
def split(n,r,law):
    if law=='edge':return r.choice((1,n-1))
    if law=='balanced':return r.choice((n//2,n-n//2))
    return r.choices(SPLITS[n],WEIGHTS[n])[0]
def shape(n,r,law='uniform'):
    if n==1:return None
    k=split(n,r,law);return shape(k,r,law),shape(n-k,r,law)
PAT={n:[sum(((x>>i)&1)<<x for x in range(1<<n)) for i in range(n)] for n in range(4,9)}
MASK={n:(1<<(1<<n))-1 for n in PAT}
def evaluate(s,p,n):
    it=iter(p);pat=PAT[n];mask=MASK[n]
    def go(t):return pat[next(it)] if t is None else mask^(go(t[0])&go(t[1]))
    return go(s)
def scalar(s,p,n):
    y=0
    for x in range(1<<n):
        it=iter(p)
        def go(t):return (x>>next(it))&1 if t is None else 1-(go(t[0])&go(t[1]))
        y|=go(s)<<x
    return y
def target(n,law,count,seed):
    r=random.Random(seed);p=list(range(n));d={};attempts=0
    while len(d)<count:
        attempts+=1
        if attempts>100000:raise RuntimeError((n,law,count,len(d)))
        s=shape(n,r,law);r.shuffle(p);y=evaluate(s,p,n)
        if y not in d:
            assert scalar(s,p,n)==y;d[y]=(s,tuple(p))
    return d
def unit(n):return n*(1<<n)+3*n-1
def collect(n,count,steps,law,seed):
    ts=target(n,law,count,seed+10);r=random.Random(seed+20);p=random.Random(seed+30)
    records={};rnd=[];t0=time.perf_counter()
    for _ in range(steps):
        s=shape(n,r);perm=p.sample(range(n),n);y=evaluate(s,perm,n)
        if y in ts and y not in records:
            assert scalar(s,perm,n)==y;records[y]=s
        rnd.append(s)
    return list(records.values()),random.Random(seed+40).sample(rnd,len(records)),{'n':n,'target_count':count,'proposals':steps,'successes':len(records),'work':steps*unit(n),'seconds':time.perf_counter()-t0,'target_functions':list(ts),'success_shapes':list(records.values())}
def fit(records,method):
    t0=time.perf_counter();lib=defaultdict(list);sc=defaultdict(Counter);pooled=Counter();visits=0
    def walk(s):
        nonlocal visits
        visits+=1
        if s is None:return 1
        a=walk(s[0]);b=walk(s[1]);n=a+b;lib[n].append(s);sc[n][a]+=1
        if len(GROUPS[n])>1:pooled[cat(n,a)]+=1
        return n
    for s in records:walk(s)
    if method=='fragment_library':
        model={n:list(dict.fromkeys(v)) for n,v in lib.items()}
        def gen(n,r):
            if n==1:return None
            if n in model and r.random()<.8:return r.choice(model[n])
            k=split(n,r,'uniform');return gen(k,r),gen(n-k,r)
        entries=sum((2*n-1)*len(v) for n,v in model.items())
    elif method=='size_grammar':
        model={n:dict(v) for n,v in sc.items()}
        probs={n:[sc[n][k]+w/sum(WEIGHTS[n]) for k,w in zip(SPLITS[n],WEIGHTS[n])] for n in SPLITS}
        def gen(n,r):
            if n==1:return None
            k=r.choices(SPLITS[n],probs[n])[0];return gen(k,r),gen(n-k,r)
        entries=sum(map(len,probs.values()))
    else:
        model={c:pooled[c]+1 for c in ('edge','central','other')}
        cs={n:tuple(g) for n,g in GROUPS.items()};ws={n:[model[c] for c in g] for n,g in GROUPS.items()}
        def gen(n,r):
            if n==1:return None
            c=r.choices(cs[n],ws[n])[0];k=r.choice(GROUPS[n][c]);return gen(k,r),gen(n-k,r)
        entries=sum(map(len,cs.values()))
    return gen,{'fit_work':visits+entries,'model_bytes':len(json.dumps(model,sort_keys=True,separators=(',',':')).encode()),'fit_seconds':time.perf_counter()-t0,'model':model}
def uniform(n,r):return shape(n,r)
def mixture(n,r):return shape(n,r,r.choice(('uniform','edge','balanced')))
def run(n,gen,steps,suites,seed):
    r=random.Random(seed);p=random.Random(seed+1);hits={k:set() for k in suites};counts=Counter();first={k:None for k in suites};t0=time.perf_counter();candidates={};seen=set()
    for i in range(steps):
        s=gen(n,r);perm=p.sample(range(n),n);y=evaluate(s,perm,n);seen.add(y)
        for k,ts in suites.items():
            if y in ts:
                counts[k]+=1
                if first[k] is None:first[k]=i+1
                if y not in hits[k]:hits[k].add(y);candidates.setdefault(y,(s,perm))
    elapsed=time.perf_counter()-t0
    for y,(s,perm) in candidates.items():assert scalar(s,perm,n)==y
    return {'proposals':steps,'work':steps*unit(n),'seconds':elapsed,'unique':len(seen),'hits':{k:len(v) for k,v in hits.items()},'hit_draws':dict(counts),'first_hit':first,'verified_unique_hits':len(candidates)}
def ci(a,b):
    d=np.array(a,float)-np.array(b,float);r=np.random.default_rng(82361);s=d[r.integers(0,len(d),size=(10000,len(d)))].mean(axis=1)
    return {'difference':float(d.mean()),'lo':float(np.quantile(s,.025)),'hi':float(np.quantile(s,.975))}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seeds',type=int,default=24);ap.add_argument('--test',type=int,default=2500);ap.add_argument('--output',type=Path,default=Path(__file__).with_name('results.json'));args=ap.parse_args()
    rows=[];meta={}
    for seed in range(args.seeds):
        suites={n:{law:target(n,law,64,900000+10000*seed+100*n+j) for j,law in enumerate(('edge','balanced','uniform'))} for n in (7,8)}
        meta[str(seed)]={str(n):{law:sorted(t) for law,t in s.items()} for n,s in suites.items()}
        for j,law in enumerate(('edge','balanced')):
            records=[];neutral=[];training=[]
            for n,steps in TRAIN:
                cnt={(4,'edge'):8,(5,'edge'):24,(4,'balanced'):3,(5,'balanced'):15}[n,law]
                a,b,t=collect(n,cnt,steps,law,100000+10000*seed+1000*j+100*n);records.append(a);neutral.extend(b);training.append(t)
            methods={};models={}
            for m,rr in [('fragment_library',sum(records,[])),('size_grammar',sum(records,[])),('pooled_grammar',sum(records,[])),('neutral_grammar',neutral),('pooled4',records[0])]:methods[m],models[m]=fit(rr,m)
            methods['uniform']=uniform;methods['fixed_mixture']=mixture
            tw=sum(t['work'] for t in training)
            for n in (7,8):
                budget=tw+models['pooled_grammar']['fit_work']+args.test*unit(n);life=budget//unit(n);shared=700000+10000*seed+100*n
                outcomes={m:run(n,g,args.test,suites[n],shared) for m,g in methods.items()}
                outcomes['uniform_lifetime']=run(n,uniform,life,suites[n],shared);outcomes['mixture_lifetime']=run(n,mixture,life,suites[n],shared)
                for m,r in outcomes.items():
                    overhead=(training[0]['work'] if m=='pooled4' else tw)+models[m]['fit_work'] if m in models else 0
                    r['total_work']=r['work']+overhead
                    assert r['work']<=budget if m.endswith('lifetime') else r['work']==args.test*unit(n)
                rows.append({'seed':seed,'train_law':law,'n':n,'training':training,'models':models,'outcomes':outcomes,'pooled_lifetime_budget':budget})
        if (seed+1)%4==0:print('completed',seed+1,'seeds',flush=True)
    summary={}
    for law,n in itertools.product(('edge','balanced'),(7,8)):
        group=[r for r in rows if r['train_law']==law and r['n']==n];ms=group[0]['outcomes'];k=f'{law}_{n}';summary[k]={}
        for m in ms:
            summary[k][m]={**{f:statistics.mean(r['outcomes'][m][f] for r in group) for f in ('work','total_work','seconds','unique','proposals','verified_unique_hits')},'hits':{a:statistics.mean(r['outcomes'][m]['hits'][a] for r in group) for a in ('edge','balanced','uniform')}}
        summary[k]['paired_pooled']={a:{m:ci([r['outcomes']['pooled_grammar']['hits'][a] for r in group],[r['outcomes'][m]['hits'][a] for r in group]) for m in ms if m!='pooled_grammar'} for a in ('edge','balanced','uniform')}
        print(k,[(m,round(summary[k][m]['hits'][law],2)) for m in ms],flush=True)
    args.output.write_text(json.dumps({'config':{'seeds':args.seeds,'test_proposals':args.test,'train':TRAIN,'target_count':64},'summary':summary,'targets':meta,'runs':rows},indent=2)+'\n')
if __name__=='__main__':main()
