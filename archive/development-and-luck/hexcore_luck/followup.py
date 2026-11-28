import random, time, json, statistics, math
from experiment import inputs, historical, full_support, CAP, PRE, BUDGET, OUT
SEEDS=range(14032,14064)

def targets(n,kind):
    rng=random.Random(77531+10*n+(kind=='mixed')); base=inputs(n); mask=(1<<(1<<n))-1; out=set(); draws=0
    while len(out)<1024:
        vals=base[:]; draws+=1
        for _ in range(rng.randrange(5,25)):
            a,b,c=[rng.choice(vals) for j in range(3)]
            if kind=='nand':v=mask^(a&b)
            else:v=[a&b,a|b,a^b,mask^a,(a&b)|(a&c)|(b&c),(a&b)|((mask^a)&c)][rng.randrange(6)]
            vals.append(v)
        if full_support(vals[-1],n):out.add(vals[-1])
    return out,draws

def search(n,s,macros,rate,budget,banks):
    rng=random.Random(s+100*n); base=inputs(n); mask=(1<<(1<<n))-1
    words=sum(2*len(m)+3 for m in macros); cap=CAP-words
    pool=[]; members=set(); seen=set(base); gate=0; mc=0; calls=0
    def record(v):
        nonlocal gate
        gate+=1; seen.add(v)
        if v not in members and v not in base:
            if len(pool)==cap:
                i=rng.randrange(cap);members.remove(pool[i]);pool[i]=v;members.add(v)
            else:pool.append(v);members.add(v)
        return v
    def operand():return rng.choice(base) if not pool or rng.random()<.4 else rng.choice(pool)
    start=time.perf_counter()
    while gate<budget:
        calls+=1
        if macros and rng.random()<rate:
            ops=rng.choice(macros)
            if len(ops)<=budget-gate:
                vals=[operand(),operand(),operand()];mc+=1
                for a,b in ops:vals.append(record(mask^(vals[a]&vals[b])))
                continue
        record(mask^(operand()&operand()))
    elapsed=time.perf_counter()-start
    tests=[(1<<i,sum(1<<x for x in range(1<<n) if not ((x>>i)&1))) for i in range(n)]
    full=sum(all((v^(v>>s))&m for s,m in tests) for v in seen)
    return {'full_support':full,'unique':len(seen),'nand_hits':len(seen&banks['nand']),'mixed_hits':len(seen&banks['mixed']),'code_words':words,'pool_cap':cap,'gates':gate,'macro_calls':mc,'calls':calls,'seconds':elapsed}

def pair(rows,arm,key):
    x=[r[arm][key]-r['flat_lifetime'][key] for r in rows]; mu=statistics.mean(x); se=statistics.stdev(x)/math.sqrt(len(x));return [mu,mu-2.04*se,mu+2.04*se,sum(i>0 for i in x),sum(i<0 for i in x)]

def main():
    pres={s:historical(s) for s in SEEDS}; epres={s:historical(s,True) for s in SEEDS}; out={}
    for n in (4,5):
        t={k:targets(n,k) for k in ('nand','mixed')}; banks={k:v[0] for k,v in t.items()}; rows=[]
        rates=[0,.1,.25,.5,.75,1]
        for s in SEEDS:
            arms=[('flat_lifetime',[],0,BUDGET+PRE),('flat_test',[],0,BUDGET),('enum_0.5',epres[s][0],.5,BUDGET)]+[(f'inherit_{rate}',pres[s][0],rate,BUDGET) for rate in rates]
            row={'seed':s}
            for arm,macros,rate,budget in arms:row[arm]=search(n,s,macros,rate,budget,banks)
            rows.append(row)
        fields=['full_support','unique','nand_hits','mixed_hits','seconds','pool_cap','gates','macro_calls','code_words']
        summary={arm:{k:statistics.mean(r[arm][k] for r in rows) for k in fields} for arm in rows[0] if arm!='seed'}
        full_space=sum((-1)**(n-j)*math.comb(n,j)*(2**(2**j)) for j in range(n+1));
        out[str(n)]={'target_banks':{k:sorted(v) for k,v in banks.items()},'draw_counts':{k:v[1] for k,v in t.items()},'full_support_function_count':full_space,'rows':rows,'summary':summary,'paired_vs_flat_lifetime':{a:{k:pair(rows,a,k) for k in fields[:4]} for a in summary if a!='flat_lifetime'}}
        print('n',n,'full space',full_space,flush=True)
        for a,v in summary.items():print(a, 'full',round(v['full_support'],2),'nand',round(v['nand_hits'],2),'mixed',round(v['mixed_hits'],2),flush=True)
    (OUT/'followup_results.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
