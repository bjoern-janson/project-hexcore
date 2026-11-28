import random, time, json, statistics, math
from pathlib import Path
OUT=Path(__file__).resolve().parent
PRE=800; BUDGET=12000; CAP=512; K=12; SEEDS=range(14000,14032)

def inputs(n):
    return [sum(1<<x for x in range(1<<n) if (x>>i)&1) for i in range(n)]
def full_support(v,n):
    for i in range(n):
        shift=1<<i
        mask=sum(1<<x for x in range(1<<n) if not ((x>>i)&1))
        if not ((v^(v>>shift))&mask): return False
    return True

def support_count(v,n):
    return sum(bool((v^(v>>(1<<i))) & sum(1<<x for x in range(1<<n) if not ((x>>i)&1))) for i in range(n))

def cost(e): return 0 if isinstance(e,int) else 1+cost(e[0])+cost(e[1])
def compile_(e):
    ops=[]
    def rec(a):
        if isinstance(a,int): return a
        i=rec(a[0]); j=rec(a[1]); ops.append((i,j)); return len(ops)+2
    root=rec(e); assert root==len(ops)+2
    return ops

def eval_e(e, a, mask):
    if isinstance(e,int):return a[e]
    return mask ^ (eval_e(e[0],a,mask)&eval_e(e[1],a,mask))

def historical(seed,systematic=False):
    rng=random.Random(seed); x=inputs(3); archive={v:i for i,v in enumerate(x)}; vals=x[:]; mask=255
    start=time.perf_counter(); i=j=0
    for _ in range(PRE):
        if systematic:
            # enumerate unordered pairs in order of discovery; later pairs introduced when a new value enters
            if i>=len(vals): break
            a,b=vals[i],vals[j]; j+=1
            if j>i:i+=1;j=0
        else:a,b=rng.choice(vals),rng.choice(vals)
        v=mask^(a&b); e=(archive[a],archive[b]); c=cost(e)
        if c>12:continue
        if v not in archive: vals.append(v); archive[v]=e
        elif c<cost(archive[v]):archive[v]=e
    # identical blind sampling policy after both prehistories
    eligible=[(v,e) for v,e in archive.items() if 2<=cost(e)<=9 and support_count(v,3)>=2]
    rng2=random.Random(seed^0xAA55)
    chosen=rng2.sample(eligible,min(K,len(eligible)))
    return [compile_(e) for v,e in chosen], {'discovered':len(archive),'eligible':len(eligible),'chosen_truth_tables':[v for v,e in chosen], 'seconds':time.perf_counter()-start,'gates':_+1}

def standard():
    # Explicitly supplied standard constructions, used as a conventional comparator.
    N=lambda a,b:(a,b); NOT=lambda a:N(a,a); AND=lambda a,b:NOT(N(a,b)); OR=lambda a,b:N(NOT(a),NOT(b)); XOR=lambda a,b:N(N(a,N(a,b)),N(b,N(a,b)))
    # Formula expansion (no internal common-subexpression discounts).
    expr=[AND(0,1),OR(0,1),XOR(0,1),NOT(XOR(0,1)),N(0,NOT(1)),AND(0,NOT(1)),NOT(OR(0,1)),AND(AND(0,1),2),OR(AND(0,1),2),OR(0,AND(1,2)),OR(AND(0,1),AND(NOT(0),2)),N(AND(0,1),2)]
    return [compile_(e) for e in expr]

def make_targets(n):
    rng=random.Random(90210+n); base=inputs(n); mask=(1<<(1<<n))-1; out=set(); draws=0
    while len(out)<512:
        vals=base[:]; draws+=1
        for j in range(rng.randrange(5,21)):
            a,b,c=[rng.choice(vals) for _ in range(3)]; op=rng.randrange(6)
            v=[a&b,a|b,a^b,mask^a,(a&b)|(a&c)|(b&c),(a&b)|((mask^a)&c)][op]; vals.append(v)
        if full_support(vals[-1],n):out.add(vals[-1])
    return out,draws

def experiment(n,seed,targets,macros,limit,systematic=False):
    rng=random.Random(seed+100*n); base=inputs(n); mask=(1<<(1<<n))-1
    # Code is charged conservatively in logical words, not Python allocator bytes.
    code_words=sum(2*len(m)+3 for m in macros); cap=CAP-code_words; assert cap>n
    pool=[]; members=set(); seen=set(base); hit=0; checkpoints={}; primitive=0; calls=0; macro_calls=0; i=j=0; enum=[]; enums=set()
    start=time.perf_counter()
    def record(v):
        nonlocal primitive,hit
        primitive+=1
        if v not in seen:
            seen.add(v); hit+=int(v in targets)
        if v not in members and v not in base:
            if len(pool)==cap:
                if not systematic:
                    z=rng.randrange(cap); members.remove(pool[z]);pool[z]=v;members.add(v)
            else:pool.append(v);members.add(v)
        if primitive in (1000,4000,BUDGET,limit):checkpoints[primitive]={'unique':len(seen),'hits':hit}
        return v
    def operand():return rng.choice(base) if not pool or rng.random()<.4 else rng.choice(pool)
    if systematic:
        enum=base[:]; enums=set(enum)
        while primitive<limit:
            if i>=len(enum):break
            v=record(mask^(enum[i]&enum[j])); j+=1
            if j>i:i+=1;j=0
            if v not in enums and len(enum)<cap+n:enum.append(v);enums.add(v)
            calls+=1
    else:
        while primitive<limit:
            calls+=1
            if macros and rng.random()<.5:
                ops=rng.choice(macros)
                if len(ops)<=limit-primitive:
                    vals=[operand(),operand(),operand()]; macro_calls+=1
                    for a,b in ops:vals.append(record(mask^(vals[a]&vals[b])))
                    continue
            record(mask^(operand()&operand()))
    elapsed=time.perf_counter()-start
    # Exact full-support count using precomputed masks; external scoring not part of learner.
    tests=[(1<<i,sum(1<<x for x in range(1<<n) if not ((x>>i)&1))) for i in range(n)]
    full=sum(all((v^(v>>s))&m for s,m in tests) for v in seen)
    return {'unique':len(seen),'full_support':full,'hits':hit,'gates':primitive,'calls':calls,'macro_calls':macro_calls,'pool_cap':cap,'code_words':code_words,'seconds':elapsed,'checkpoints':checkpoints}

def paired(rows,a,b,key):
    d=[r[a][key]-r[b][key] for r in rows]; mean=statistics.mean(d); se=statistics.stdev(d)/math.sqrt(len(d)); return {'mean':mean,'se':se,'approx95':[mean-2.04*se,mean+2.04*se],'positive_seeds':sum(x>0 for x in d),'negative_seeds':sum(x<0 for x in d)}

def main():
    pre={s:historical(s) for s in SEEDS}; enum_pre={s:historical(s,True) for s in SEEDS}
    result={'protocol':{'seeds':list(SEEDS),'pre_gates':PRE,'test_gates':BUDGET,'capacity_words':CAP,'max_macros':K},'historical':{str(s):pre[s][1] for s in SEEDS},'historical_enumeration':{str(s):enum_pre[s][1] for s in SEEDS},'worlds':{}}
    for n in (4,5):
        targets,draws=make_targets(n); rows=[]
        for s in SEEDS:
            row={'seed':s}
            for name,macros,lim,sys in [('flat',[],BUDGET,False),('flat_lifetime',[],BUDGET+PRE,False),('inherited',pre[s][0],BUDGET,False),('standard',standard(),BUDGET,False),('enumerated_templates',enum_pre[s][0],BUDGET,False),('systematic_lifetime',[],BUDGET+PRE,True)]:
                row[name]=experiment(n,s,targets,macros,lim,sys)
            rows.append(row)
        arms=['flat','flat_lifetime','inherited','standard','enumerated_templates','systematic_lifetime']
        summary={a:{k:statistics.mean(r[a][k] for r in rows) for k in ('unique','full_support','hits','gates','macro_calls','pool_cap','code_words','seconds')} for a in arms}
        result['worlds'][str(n)]={'target_bank':sorted(targets),'target_draws':draws,'rows':rows,'summary':summary,'paired':{f'inherited_vs_{a}':{k:paired(rows,'inherited',a,k) for k in ('unique','full_support','hits')} for a in arms if a!='inherited'}}
        print(n, json.dumps(summary),flush=True)
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
