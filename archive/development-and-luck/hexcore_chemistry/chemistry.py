"""Finite Boolean term chemistry; see protocol.md. Python 3.10+, NumPy."""
import argparse, json, random, time, statistics
from pathlib import Path
import numpy as np
NAND=5; POOL=64; CAP=63; BUDGET=160_000; SEEDS=24
MODES=[(law,ret) for law in ('nand','template','subtree') for ret in ('random','semantic')]
def inputs(n):
    return [sum(((x>>i)&1)<<x for x in range(1<<n)) for i in range(n)]
def truth(term,patterns,mask):
    stack=[]
    for c in term:
        if c==NAND:
            b=stack.pop(); a=stack.pop(); stack.append(mask^(a&b))
        else: stack.append(patterns[c])
    assert len(stack)==1
    return stack[0]
def support(y,n):
    return sum(any(((y>>x)^(y>>(x^(1<<i))))&1 for x in range(1<<n) if not x&(1<<i))<<i for i in range(n))
def food(n):
    return [bytes([i]) for i in range(n)]+[bytes([i,j,NAND]) for i in range(n) for j in range(i,n)]
def target_suite():
    rng=random.Random(772010); pat=inputs(5); mask=(1<<32)-1
    def tree(g):
        if not g:return bytes([rng.randrange(5)])
        a=rng.randrange(g);return tree(a)+tree(g-1-a)+bytes([NAND])
    targets={};attempts=0
    while len(targets)<512:
        t=tree(rng.randint(2,12)); y=truth(t,pat,mask); s=support(y,5);attempts+=1
        if s&16 and s.bit_count()>=4: targets.setdefault(y,t.hex())
    parity=sum((x.bit_count()%2)<<x for x in range(32));majority=sum((x.bit_count()>=3)<<x for x in range(32))
    return targets,{'parity5':parity,'majority5':majority},attempts
def subtree_range(a,rng):
    end=rng.randrange(len(a))+1; i=end; needed=1
    while needed:
        i-=1; needed+=1 if a[i]==NAND else -1
    return i,end
def proposal(a,b,law,n,rng):
    if law=='nand' or rng.random()<.5:return a+b+bytes([NAND])
    if law=='template':return a.replace(bytes([rng.randrange(n)]),b)
    i,j=subtree_range(a,rng);return a[:i]+b+a[j:]
def initial(n,ret,rng):
    f=food(n);pat=inputs(n);mask=(1<<(1<<n))-1
    if ret=='random':return [rng.choice(f) for _ in range(POOL)]
    unique={}
    for t in f:unique.setdefault(truth(t,pat,mask),t)
    return list(unique.values())
def run(n,law,ret,seed,targets,named,starting=None,budget=BUDGET):
    start=time.perf_counter();rng=random.Random(seed);f=food(n);pat=inputs(n);mask=(1<<(1<<n))-1
    pool=list(starting) if starting is not None else initial(n,ret,rng)
    if ret=='semantic':
        unique={truth(t,pat,mask):t for t in pool};pool=list(unique.values());index={truth(t,pat,mask):i for i,t in enumerate(pool)}
    seen={}; initial_seen=set(); work=steps=oversize=0
    def record(t,y):
        cost=(len(t)-1)//2
        if y not in seen or cost<seen[y]:seen[y]=cost
    for t in pool+f:
        y=truth(t,pat,mask);record(t,y);initial_seen.add(y)
    while work<budget:
        a=rng.choice(f if rng.random()<.2 else pool);b=rng.choice(f if rng.random()<.2 else pool)
        prod=proposal(a,b,law,n,rng);charge=len(a)+len(b)+1+(2*len(prod) if len(prod)<=CAP else 0)
        if work+charge>budget:break
        work+=charge;steps+=1
        if len(prod)>CAP:oversize+=1;continue
        y=truth(prod,pat,mask);record(prod,y)
        if ret=='random':pool[rng.randrange(POOL)]=prod
        elif y in index:
            i=index[y]
            if len(prod)<len(pool[i]):pool[i]=prod
        elif len(pool)<POOL:index[y]=len(pool);pool.append(prod)
        else:
            i=rng.randrange(POOL);del index[truth(pool[i],pat,mask)];pool[i]=prod;index[y]=i
    elapsed=time.perf_counter()-start
    resident={truth(t,pat,mask) for t in pool}
    full=new=0
    for y in seen:
        s=support(y,n);full+=s==(1<<n)-1;new+=bool(s&(1<<(n-1)))
    hits=seen.keys()&targets.keys();hcosts=[seen[y] for y in hits]
    return pool,{'unique':len(seen),'new_unique':len(seen.keys()-initial_seen),'full_support':full,'new_input_functions':new,'hits':len(hits),'initial_hits':len(initial_seen&targets.keys()),'resident_hits':len(resident&targets.keys()),'named_hits':{k:v in seen for k,v in named.items()},'hit_gate_sum':sum(hcosts),'resident_unique':len(resident),'resident_slots':len(pool),'resident_tokens':sum(map(len,pool)),'resident_max_gates':max((len(t)-1)//2 for t in pool),'work':work,'reactions':steps,'oversize':oversize,'seconds':elapsed}
def paired_ci(a,b):
    d=np.array(a,dtype=float)-np.array(b,dtype=float);r=np.random.default_rng(8244);means=d[r.integers(0,len(d),size=(10000,len(d)))].mean(axis=1)
    return {'difference':float(d.mean()),'lo':float(np.quantile(means,.025)),'hi':float(np.quantile(means,.975))}
def summarize(rows):
    fields=['unique','new_unique','full_support','new_input_functions','hits','initial_hits','resident_hits','resident_unique','resident_slots','resident_tokens','resident_max_gates','work','reactions','oversize','seconds']
    return {**{k:statistics.mean(r[k] for r in rows) for k in fields},'named_hits':{k:sum(r['named_hits'][k] for r in rows) for k in rows[0]['named_hits']},'mean_gate_per_hit':sum(r['hit_gate_sum'] for r in rows)/max(1,sum(r['hits'] for r in rows))}
def main():
    p=argparse.ArgumentParser();p.add_argument('--seeds',type=int,default=SEEDS);p.add_argument('--budget',type=int,default=BUDGET);p.add_argument('--output',type=Path,default=Path(__file__).with_name('results.json'));args=p.parse_args()
    targets,named,attempts=target_suite();results={};summaries={}
    for law,ret in MODES:
        mode=f'{law}_{ret}';rows=[]
        for seed in range(args.seeds):
            pool,first=run(4,law,ret,10000+seed,{}, {},budget=args.budget)
            _,warm=run(5,law,ret,20000+seed,targets,named,starting=pool,budget=args.budget)
            _,cold=run(5,law,ret,20000+seed,targets,named,budget=args.budget)
            _,cold2=run(5,law,ret,20000+seed,targets,named,budget=2*args.budget)
            rows.append({'seed':seed,'phase1':first,'warm':warm,'cold':cold,'cold2':cold2})
        results[mode]=rows;summaries[mode]={k:summarize([r[k] for r in rows]) for k in ('phase1','warm','cold','cold2')}
        summaries[mode]['warm_minus_cold_hits']=paired_ci([r['warm']['hits'] for r in rows],[r['cold']['hits'] for r in rows])
        summaries[mode]['warm_minus_cold2_hits']=paired_ci([r['warm']['hits'] for r in rows],[r['cold2']['hits'] for r in rows])
        s=summaries[mode];print(mode,'P1 unique',round(s['phase1']['unique'],1),'warm hits',round(s['warm']['hits'],2),'cold',round(s['cold']['hits'],2),'cold2',round(s['cold2']['hits'],2),'delta',s['warm_minus_cold_hits'],flush=True)
        args.output.write_text(json.dumps({'config':{'seeds':args.seeds,'budget':args.budget,'pool':POOL,'token_cap':CAP,'target_count':len(targets),'target_generation_attempts':attempts},'target_terms':{str(y):t for y,t in targets.items()},'named_targets':named,'summary':summaries,'runs':results},indent=2)+'\n')
if __name__=='__main__':main()
