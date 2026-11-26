import itertools,json,time
from pathlib import Path
from sealed_world import search,parity,eval_expr
from functools import lru_cache
OPS={8:'AND',14:'OR',1:'NOR',6:'M'}
# Generic disjoint decomposition: each operand conveys at most one bit.
def solve(n,target,ops=OPS,budget=100000):
    checks=0
    @lru_cache(None)
    def rec(vs,t):
        nonlocal checks
        k=len(vs); mask=(1<<(1<<k))-1
        if t==0:return '0'
        if t==mask:return '1'
        for i,v in enumerate(vs):
            a=sum(((s>>i)&1)<<s for s in range(1<<k))
            if t==a:return f'x{v}'
            if t==mask^a and 1 in ops:return f'NOR(x{v},x{v})'
        for size in range(1,k//2+1):
            for left in itertools.combinations(range(k),size):
                right=tuple(i for i in range(k) if i not in left)
                def embed(s,ix):return sum(((s>>j)&1)<<i for j,i in enumerate(ix))
                rows=[]
                for a in range(1<<len(left)):
                    row=0
                    for b in range(1<<len(right)):
                        checks+=1
                        if checks>budget:raise TimeoutError
                        row|=((t>>(embed(a,left)|embed(b,right)))&1)<<b
                    rows.append(row)
                    if len(set(rows))>2:break
                if len(rows)!=1<<len(left) or len(set(rows))>2:continue
                cols=[sum(((r>>b)&1)<<a for a,r in enumerate(rows)) for b in range(1<<len(right))]
                if len(set(cols))>2:continue
                for ar in (0,1):
                    for br in (0,1):
                        aa=[int(r!=rows[0])^ar for r in rows];bb=[int(c!=cols[0])^br for c in cols]
                        for op,name in ops.items():
                            checks+=1
                            if checks>budget:raise TimeoutError
                            if not all(((op>>(2*aa[a]+bb[b]))&1)==((rows[a]>>b)&1) for a in range(len(aa)) for b in range(len(bb))):continue
                            l=rec(tuple(vs[i] for i in left),sum(x<<i for i,x in enumerate(aa)))
                            if l is None:continue
                            r=rec(tuple(vs[i] for i in right),sum(x<<i for i,x in enumerate(bb)))
                            if r is not None:return f'{name}({l},{r})'
        return None
    try:e=rec(tuple(range(n)),target)
    except TimeoutError:e=None
    verified=bool(e) and all(eval_expr(e,[(s>>i)&1 for i in range(n)],{v:k for k,v in ops.items()})==((target>>s)&1) for s in range(1<<n))
    assert not e or verified
    return dict(expression=e,verified=verified,checks=checks)
def main():
    out=[]
    for n in range(3,13):
        t=parity(n); r=solve(n,t);out.append(dict(task='parity',n=n,**r))
    for name,n,fn in [('mixed',6,lambda s: (((s&3).bit_count()%2) & (((s>>2)&3)!=0)) ^ (((s>>4)&3)==3)),('majority',3,lambda s:s.bit_count()>=2),('majority',5,lambda s:s.bit_count()>=3)]:
        t=sum(int(fn(s))<<s for s in range(1<<n));out.append(dict(task=name,n=n,**solve(n,t)))
    Path(__file__).with_name('scoped_synthesis_results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
