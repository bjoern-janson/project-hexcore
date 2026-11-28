"""Diagnostic controls after initial experiment; see followup_protocol.md."""
import json, random, time
from pathlib import Path
from chemistry import *

def random_tree(g,rng):
    if not g:return bytes([rng.randrange(5)])
    a=rng.randrange(g);return random_tree(a,rng)+random_tree(g-1-a,rng)+bytes([NAND])
def port(t,rng):
    mapping=list(range(256));mapping[:4]=rng.sample(range(5),4)
    return t.translate(bytes(mapping))
def fragment(t,rng):
    starts=[];choices=[]
    for i,c in enumerate(t):
        if c==NAND:
            starts.pop();start=starts.pop()
        else:start=i
        starts.append(start)
        if i+1-start<=15:choices.append((start,i+1))
    a,b=rng.choice(choices);return t[a:b]
def prepare(pool,mode,seed,frags):
    start=time.perf_counter();rng=random.Random(seed);old=list(pool)
    if mode=='inherited':new=old;charge=0
    elif mode=='portable':new=[port(t,rng) for t in old]
    elif mode=='leaf_scramble':new=[bytes(c if c==NAND else rng.randrange(5) for c in t) for t in old]
    elif mode=='random_shape':new=[random_tree((len(t)-1)//2,rng) for t in old]
    elif mode=='turnover':
        new=old.copy();f=food(5)
        for i in rng.sample(range(len(old)),len(old)//2):new[i]=rng.choice(f)
    elif mode=='small_fragments':new=[port(t,rng) for t in frags]
    elif mode=='matched_small':new=[random_tree((len(t)-1)//2,rng) for t in frags]
    else:raise ValueError(mode)
    if mode!='inherited':charge=2*(sum(map(len,old))+sum(map(len,new)))
    return new,charge,time.perf_counter()-start

def main():
    targets,named,_=target_suite();out={};summary={};modes=['inherited','portable','leaf_scramble','random_shape','turnover','small_fragments','matched_small','cold','cold2']
    for law in ('template','subtree'):
        rows=[]
        for seed in range(SEEDS):
            pool,first=run(4,law,'random',10000+seed,{},{});rng=random.Random(3190+seed);frags=[fragment(t,rng) for t in pool]
            row={'seed':seed}
            for mode in modes:
                if mode in ('cold','cold2'):
                    start=None;charge=0;pt=0;budget=BUDGET*(1+(mode=='cold2'))
                else:
                    start,charge,pt=prepare(pool,mode,30000+seed,frags);budget=BUDGET-charge
                _,s=run(5,law,'random',20000+seed,targets,named,starting=start,budget=budget)
                s['prep_work']=charge;s['prep_seconds']=pt;s['start_tokens']=sum(map(len,start)) if start else 0
                s['lifetime_work']=s['work']+charge+(first['work'] if start else 0);row[mode]=s
            rows.append(row)
        out[law]=rows;summary[law]={mode:{**summarize([r[mode] for r in rows]),'prep_work':statistics.mean(r[mode]['prep_work'] for r in rows),'lifetime_work':statistics.mean(r[mode]['lifetime_work'] for r in rows),'start_tokens':statistics.mean(r[mode]['start_tokens'] for r in rows)} for mode in modes}
        pairs=[('portable','inherited'),('portable','leaf_scramble'),('portable','random_shape'),('small_fragments','matched_small'),('small_fragments','cold'),('small_fragments','cold2'),('turnover','cold2'),('portable','cold2')]
        summary[law]['contrasts']={a+' - '+b:paired_ci([r[a]['hits'] for r in rows],[r[b]['hits'] for r in rows]) for a,b in pairs}
        print(law,{m:round(summary[law][m]['hits'],2) for m in modes},summary[law]['contrasts'])
    Path(__file__).with_name('followup_results.json').write_text(json.dumps({'summary':summary,'runs':out},indent=2)+'\n')
if __name__=='__main__':main()
