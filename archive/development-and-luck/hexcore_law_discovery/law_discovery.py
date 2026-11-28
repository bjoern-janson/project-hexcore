import collections, json, math, random, time, operator
from pathlib import Path
import numpy as np
D=tuple(range(2,65)); N=len(D); TRAIN=tuple(range(6,17)); TEST=tuple(range(17,65)); MAX=4096
OPS={'+':operator.add,'-':operator.sub,'*':operator.mul,'//':operator.floordiv,'%':operator.mod,'min':min,'max':max}
COMM={'+','*','min','max'}
def clip(n,k):return max(1,min(n//2,k))
def fmt(op,a,b):return f'{op}({a},{b})' if op in ('min','max') else f'({a}{op}{b})'
def enumerate_laws():
    start=time.perf_counter(); sizes={1:{(c,)*N:str(c) for c in range(1,5)}};sizes[1][D]='n';known=dict(sizes[1]);attempts=collections.Counter();invalid=collections.Counter()
    for size in (3,5,7):
        new={}
        for a in range(1,size-1,2):
            b=size-1-a
            for av,ae in sizes[a].items():
                for bv,be in sizes[b].items():
                    for op,func in OPS.items():
                        if op in COMM and (a>b or a==b and ae>be):continue
                        attempts[size]+=1
                        if op in ('//','%') and 0 in bv:invalid[size]+=1;continue
                        val=tuple(map(func,av,bv))
                        if max(val)>MAX or min(val)<-MAX:invalid[size]+=1;continue
                        if val in known:continue
                        e=fmt(op,ae,be)
                        if val not in new or e<new[val]:new[val]=e
        sizes[size]=new;known.update(new)
    profiles={}
    for cost,vals in sizes.items():
        for v,e in vals.items():
            p=tuple(clip(n,k) for n,k in zip(D,v));cand=(cost,e)
            if p not in profiles or cand<profiles[p]:profiles[p]=cand
    items=sorted(profiles.items(),key=lambda kv:kv[1]);arr=np.array([p for p,e in items],np.int16);desc=[e for p,e in items];weights=np.exp2(-np.array([a for a,b in desc],float));meta={'raw_by_nodes':{k:len(v) for k,v in sizes.items()},'attempts_by_nodes':dict(attempts),'invalid_by_nodes':dict(invalid),'profile_count':len(items),'profile_array_bytes':arr.nbytes,'descriptions_utf8_bytes':sum(len(e.encode()) for c,e in desc),'seconds':time.perf_counter()-start,'scalar_eval_upper_proxy':sum(attempts.values())*N}
    return arr,desc,weights,meta

def worlds():
    f={'thirds':lambda n:n//3,'quarters':lambda n:n//4,'two_fifths':lambda n:2*n//5,'alternating':lambda n:n//(2+n%2),'capped_thirds':lambda n:min(n//3,3),'modular':lambda n:n//(1+n%3),'sqrt':math.isqrt,'log2':lambda n:n.bit_length()-1,'alias_halves':lambda n:n//3 if n<=16 else n//2,'alias_quarters':lambda n:n//3 if n<=16 else n//4}
    return {k:tuple(clip(n,g(n)) for n in D) for k,g in f.items()}

def lookup(p,n):return p[n-2]
def tree(p,n):
    if n==1:return None
    k=lookup(p,n);return (tree(p,k),tree(p,n-k))
def nearest(obs):return tuple(clip(n,obs[min(obs,key=lambda z:(abs(n-z),z))]) for n in D)
def frac_fit(obs):
    candidates=sorted(set((a,b) for b in range(2,17) for a in range(1,b//2+1) if math.gcd(a,b)==1))
    def key(ab):
        a,b=ab;return (sum(abs(clip(n,n*a//b)-k) for n,k in obs.items()),b,a)
    a,b=min(candidates,key=key);return tuple(clip(n,n*a//b) for n in D),f'{a}/{b}'
def score(p,t):
    roots=sum(lookup(p,n)==lookup(t,n) for n in TEST);trees=sum(tree(p,n)==tree(t,n) for n in TEST)
    return {'roots':roots,'trees':trees,'test_count':len(TEST)}
def induce(arr,desc,weights,t,mode,seed=0):
    r=random.Random(seed);start=time.perf_counter();obs={};idx=np.arange(len(arr));steps=[];comparisons=visits=0
    for step in range(5):
        if step<2:n=(4,5)[step]
        elif mode=='active' and len(idx):
            rem=[n for n in TRAIN if n not in obs];ent=[]
            for n0 in rem:
                h=np.bincount(arr[idx,n0-2],weights=weights[idx]);v=h[h>0]/h.sum();ent.append(float(-np.dot(v,np.log2(v))));visits+=len(idx)
            n=rem[int(np.argmax(ent))]
        elif mode=='sequential':n=next(n for n in TRAIN if n not in obs)
        else:n=r.choice([n for n in TRAIN if n not in obs])
        k=lookup(t,n);obs[n]=k;comparisons+=len(idx);idx=idx[arr[idx,n-2]==k];steps.append({'n':n,'split':k,'remaining':len(idx)})
    if len(idx):p=tuple(map(int,arr[idx[0]]));model=desc[idx[0]]
    else:p=nearest(obs);model=None
    if len(idx):
        a=arr[idx,15:];ambig=int(np.sum(np.min(a,axis=0)!=np.max(a,axis=0)));test_profiles=len(np.unique(a,axis=0))
    else:ambig=None;test_profiles=0
    return {'mode':mode,'seed':seed,'queries':steps,'model':model,'comparisons':comparisons,'entropy_visits':visits,'ambiguous_test_sizes':ambig,'compatible_test_profiles':test_profiles,'seconds':time.perf_counter()-start,'prediction':p,**score(p,t)},obs

def truth(p,n):
    x=np.arange(1<<n,dtype=np.uint32);i=iter(range(n))
    def f(t):
        if t is None:return ((x>>next(i))&1).astype(bool)
        return np.logical_not(np.logical_and(f(t[0]),f(t[1])))
    return f(tree(p,n))
def main():
    arr,desc,weights,meta=enumerate_laws();print('library',meta,flush=True);rows={};cache={}
    def gettruth(p):
        p=tuple(p)
        if p not in cache:cache[p]=truth(p,17)
        return cache[p]
    for name,t in worlds().items():
        match=np.flatnonzero(np.all(arr==np.array(t),axis=1));a,obs=induce(arr,desc,weights,t,'active');s,_=induce(arr,desc,weights,t,'sequential');pas=[induce(arr,desc,weights,t,'passive',i)[0] for i in range(32)]
        fp,fr=frac_fit(obs);npred=nearest(obs)
        alternatives={'fraction':{'formula':fr,'prediction':fp,**score(fp,t)},'nearest':{'prediction':npred,**score(npred,t)},'chain':{'prediction':tuple(1 for n in D),**score(tuple(1 for n in D),t)},'balanced':{'prediction':tuple(n//2 for n in D),**score(tuple(n//2 for n in D),t)}}
        ref=gettruth(t)
        for row in [a,s,*pas,*alternatives.values()]:
            predicted=gettruth(row['prediction']);row['function_equal_n17']=bool(np.array_equal(ref,predicted));row['function_accuracy_n17']=float(np.mean(ref==predicted))
            if tree(row['prediction'],17)==tree(t,17):assert row['function_equal_n17']
        rows[name]={'target':t,'in_library':bool(len(match)),'target_min_model':desc[match[0]] if len(match) else None,'active':a,'sequential':s,'passive':pas,'alternatives':alternatives}
        print(name,'in',bool(len(match)),'active',a['roots'],a['trees'],a['model'],'passive',round(np.mean([q['roots'] for q in pas]),2),round(np.mean([q['trees'] for q in pas]),2),'ambiguity',a['ambiguous_test_sizes'],'fraction',alternatives['fraction']['roots'],flush=True)
    for k in ('alias_halves','alias_quarters'):
        assert rows[k]['active']['queries']==rows['thirds']['active']['queries'];assert rows[k]['active']['prediction']==rows['thirds']['active']['prediction']
    Path(__file__).with_name('results.json').write_text(json.dumps({'config':{'domain':D,'train_options':TRAIN,'test':TEST,'passive_seeds':32},'library':meta,'worlds':rows},indent=2)+'\n')
if __name__=='__main__':main()
