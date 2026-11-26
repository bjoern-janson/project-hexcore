"""BL09 exploratory: generic symbolic certificate synthesis and decoder transfer.
No Newton recurrence or explicit inverse formula supplied to the search. It
uses a generic GF(2) polynomial-span solver over monomials in S=x+y and
T=h(x)+h(y). The sufficient proof target S^a (xy)^(2^r) and root-decoding
schema are supplied by the researcher. Accepted identities are checked
independently in the polynomial ring. Field construction uses Rabin's test.
Large-field trials use a sparse index representation, NOT a materialized array.
This is known finite-field algebra; no novelty or new computational primitive.
"""
import itertools, math, json, random, pathlib, statistics, time
import numpy as np
from bl08 import powers, POLY
D=32; STRIDE=D+1

def mul_s(f):return (f<<STRIDE)^(f<<1)
def mul_t(f,exps):
    o=0
    for e in exps:o^=(f<<(STRIDE*e))^(f<<e)
    return o

def expand(i,j,exps):
    # Separate direct expansion routine, not reuse of the elimination basis.
    p={(0,0)}
    for factors in [[(1,0),(0,1)]]*i + [[(e,0) for e in exps]+[(0,e) for e in exps]]*j:
        new=set()
        for a,b in p:
            for c,d in factors:
                v=(a+c,b+d)
                if v in new:new.remove(v)
                else:new.add(v)
        p=new
    return p

def certificate(exps):
    start=time.perf_counter_ns();degree=max(exps,default=0)
    if not degree:return None,dict(columns=0,xors=0,targets=0,ns=time.perf_counter_ns()-start)
    piv={};cols=[];tp=1;ops=0
    for j in range(D//degree+1):
        v=tp
        for i in range(D-j*degree+1):
            col=v;mask=1<<len(cols);cols.append((i,j))
            while col:
                k=col.bit_length()-1
                if k in piv:col^=piv[k][0];mask^=piv[k][1];ops+=2
                else:piv[k]=(col,mask);break
            v=mul_s(v)
        tp=mul_t(tp,exps)
    # Candidate identities: S^a (xy)^(2^r) in span of all allowed S^i T^j.
    ts=[]
    for r in range(5):
        power=1<<r
        if 2*power>D:continue
        v=1<<(STRIDE*power+power)
        for a in range(D-2*power+1):
            ts.append((a+2*power,a,r,v));v=mul_s(v)
    tested=0
    for total,a,r,v in sorted(ts):
        tested+=1;rem=v;mask=0
        while rem:
            k=rem.bit_length()-1
            if k not in piv:break
            rem^=piv[k][0];mask^=piv[k][1];ops+=2
        if rem:continue
        terms=[ij for k,ij in enumerate(cols) if mask>>k&1]
        actual=set()
        for i,j in terms:actual^=expand(i,j,exps)
        expected={(i+(1<<r),j+(1<<r)) for i,j in expand(a,0,exps)}
        assert actual==expected and actual
        cert=dict(a=a,r=r,terms=terms,degree=total)
        return cert,dict(columns=len(cols),xors=ops,targets=tested,ns=time.perf_counter_ns()-start)
    return None,dict(columns=len(cols),xors=ops,targets=tested,ns=time.perf_counter_ns()-start)

def cases():
    rng=random.Random(928193);data={}
    def add(e,k):data.setdefault(tuple(sorted(set(e))),k)
    for k in range(1,17):add([k],'monomial')
    # Positive-control families, deliberately constructed to contain solutions.
    for b in (3,6,12):
        for mask in range(1,32):
            add([b]+[1<<i for i in range(5) if mask>>i&1],'additive_perturbation')
    for mask in range(1,32):add([1<<i for i in range(5) if mask>>i&1],'additive_null')
    while sum(v=='random' for v in data.values())<128:
        add([i for i in range(1,17) if rng.random()<.28],'random')
    return data

def poly_mod(a,b):
    while a.bit_length()>=b.bit_length():a^=b<<(a.bit_length()-b.bit_length())
    return a

def poly_gcd(a,b):
    while b:a,b=b,poly_mod(a,b)
    return a

def poly_square(a):
    out=0
    while a:
        l=a&-a;out|=1<<(2*(l.bit_length()-1));a^=l
    return out

def prime_divisors(m):return [p for p in range(2,m+1) if m%p==0 and all(p%d for d in range(2,int(math.sqrt(p))+1))]

def irreducible(f,m):
    if f.bit_length()!=m+1 or not f&1:return False
    checks={m//p for p in prime_divisors(m)};x=2;v=x
    for i in range(1,m+1):
        v=poly_mod(poly_square(v),f)
        if i in checks and poly_gcd(v^x,f)!=1:return False
    return v==x

def choose_modulus(m,seed):
    rng=random.Random(seed);attempts=0
    while True:
        attempts+=1;f=(1<<m)|(rng.randrange(1<<(m-1))<<1)|1
        if irreducible(f,m):return f,attempts

def gf_mul(a,b,m,f):
    z=0
    while b:
        if b&1:z^=a
        b>>=1;a<<=1
        if a>>m:a^=f
    return z

def gf_pow(a,n,m,f):
    z=1
    while n:
        if n&1:z=gf_mul(z,a,m,f)
        a=gf_mul(a,a,m,f);n>>=1
    return z

def eval_h(x,exps,m,f):
    y=0
    for e in exps:y^=gf_pow(x,e,m,f)
    return y

def solve_quadratic(c,m,f):
    # Solve u^2+u=c by a generic GF(2) linear solve. The two solutions
    # differ by 1. Only one solution is necessary to recover unordered roots.
    piv={}
    for i in range(m):
        b=1<<i;v=gf_mul(b,b,m,f)^b;mask=b
        while v:
            k=v.bit_length()-1
            if k in piv:v^=piv[k][0];mask^=piv[k][1]
            else:piv[k]=(v,mask);break
    assert len(piv)==m-1
    v=c;u=0
    while v:
        k=v.bit_length()-1
        if k not in piv:return None
        v^=piv[k][0];u^=piv[k][1]
    assert gf_mul(u,u,m,f)^u==c
    return u

def decode(s,t,cert,m,f):
    assert s
    z=0
    for i,j in cert['terms']:
        z^=gf_mul(gf_pow(s,i,m,f),gf_pow(t,j,m,f),m,f)
    inv=gf_pow(s,(1<<m)-2,m,f);z=gf_mul(z,gf_pow(inv,cert['a'],m,f),m,f)
    r=cert['r']%m
    for _ in range((m-r)%m):z=gf_mul(z,z,m,f)
    c=gf_mul(z,gf_mul(inv,inv,m,f),m,f);u=solve_quadratic(c,m,f)
    if u is None:return None
    x=gf_mul(s,u,m,f);return sorted((x,x^s))

def main():
    root=pathlib.Path(__file__).parent;data=[];P={m:powers(m) for m in (4,5,6,7,8)};ij={m:np.triu_indices(1<<m,1) for m in P}
    for exps,kind in cases().items():
        cert,work=certificate(exps);valid={}
        for m,p in P.items():
            h=np.zeros(1<<m,dtype=np.int32)
            for e in exps:h^=p[e]
            i,j=ij[m];syndrome=((i^j)<<m)|(h[i]^h[j]);valid[m]=len(np.unique(syndrome))==len(i)
        assert not cert or all(valid.values()),(exps,cert,valid)
        data.append(dict(exps=exps,kind=kind,certificate=cert,work=work,valid=valid))
    print('families')
    for kind in sorted({r['kind'] for r in data}):
        rows=[r for r in data if r['kind']==kind];print(kind,len(rows),'certified',sum(r['certificate'] is not None for r in rows),'calibration m5',sum(r['valid'][5] for r in rows),'all m4..8',sum(all(r['valid'].values()) for r in rows),flush=True)
    initial=[r for r in data if r['valid'][5]];print('empirical calibration failures',len(initial),sum(not all(r['valid'].values()) for r in initial));certified=[r for r in data if r['certificate']];print('certificate',len(certified),'max degree',max(r['certificate']['degree'] for r in certified),'mean xors',statistics.mean(r['work']['xors'] for r in certified))
    # Test transferred certificate-derived decoders, not just predicted validity.
    rng=random.Random(180133);sample=rng.sample(certified,min(24,len(certified)));large=[]
    for m in (16,32,64):
        f,attempts=choose_modulus(m,701+m);assert irreducible(f,m)
        # Independent sanity check for random nonzero elements.
        for _ in range(16):
            x=rng.randrange(1,1<<m);assert gf_mul(x,gf_pow(x,(1<<m)-2,m,f),m,f)==1
        ntests=0;elapsed=time.perf_counter_ns()
        for row in sample:
            for _ in range(8):
                x,y=rng.sample(range(1<<m),2) if m<64 else (rng.getrandbits(m),rng.getrandbits(m))
                while x==y:y=rng.getrandbits(m)
                s=x^y;t=eval_h(x,row['exps'],m,f)^eval_h(y,row['exps'],m,f)
                recovered=decode(s,t,row['certificate'],m,f)
                assert recovered==sorted((x,y)),(m,row,x,y,recovered)
                ntests+=1
        out=dict(m=m,locations=str(1<<m),modulus=hex(f),irreducible_attempts=attempts,tests=ntests,syndrome_bits=2*m+1,wall_ns=time.perf_counter_ns()-elapsed);large.append(out);print('large',out,flush=True)
    (root/'bl09_results.json').write_text(json.dumps(dict(cases=data,large_fields=large),indent=2))
    print('All accepted polynomial identities independently expanded and checked; all large-field decoder tests passed.')
if __name__=='__main__':main()
