"""BL08 exploratory: a reusable mathematical certificate for sparse-fault
measurement instruments. Search a predeclared monomial family in GF(2^m),
compare finite calibration, transfer, and a supplied generic symbolic proof
schema. This is known coding theory, not invention of the underlying algebra.
All pair collisions are checked exactly. Query counts distinguish pooled parity
observations from the cost of constructing them with individual bit reads.
"""
import numpy as np, random, itertools, json, pathlib, statistics, math, csv
POLY={4:0x13,5:0x25,6:0x43,7:0x83,8:0x11B,10:0x409}
EXPS=list(range(1,32)); SIZES=tuple(POLY); HOLD=(6,7,8,10); TRIALS=128

def mul(a,b,m):
    c=0
    while b:
        if b&1:c^=a
        b>>=1;a<<=1
        if a>>m:a^=POLY[m]
    return c

def powf(a,k,m):
    z=1
    while k:
        if k&1:z=mul(z,a,m)
        a=mul(a,a,m);k>>=1
    return z

def powers(m):
    N=1<<m
    # A finite ring in which every nonzero element has inverse is a field.
    assert all(powf(x,N-1,m)==1 for x in range(1,N)),m
    P=np.zeros((32,N),dtype=np.int32);P[0]=1;P[1]=np.arange(N)
    for k in range(2,32):P[k]=[mul(int(v),x,m) for x,v in enumerate(P[k-1])]
    return P

def unique_pairs(h,m,ij):
    i,j=ij
    code=((i^j)<<m) | (h[i]^h[j]);return len(np.unique(code))

def codebook(h,m):
    return (1<<(2*m))|(np.arange(1<<m,dtype=np.int32)<<m)|h

def certificate(k):
    # Newton recurrence in characteristic 2: P_k(s,p)=sP_(k-1)+pP_(k-2).
    # A set of (s-degree,p-degree) monomials uses symmetric difference as GF2 add.
    p0=set();p1={(1,0)};ops=0
    if k==1:p=p1
    else:
        for _ in range(2,k+1):
            a={(i+1,j) for i,j in p1};b={(i,j+1) for i,j in p0};ops+=len(a)+len(b)
            p=a^b;p0,p1=p1,p
    dependent=[(i,j) for i,j in p if j]
    good=len(dependent)==1 and dependent[0][1]&(dependent[0][1]-1)==0
    return bool(good),sorted(p),ops

def main():
    root=pathlib.Path(__file__).parent;data={};mat={};powcache={}
    for m in SIZES:
        N=1<<m;P=powers(m);powcache[m]=P;ij=np.triu_indices(N,1);pairs=len(ij[0]);mat[m]={}
        for k in EXPS:
            z=unique_pairs(P[k],m,ij);mat[m][k]=z==pairs
        c=codebook(P[3],m);syndromes=set(map(int,c));pair_syn=c[ij[0]]^c[ij[1]]
        assert len(syndromes)==N and 0 not in syndromes
        assert len(np.unique(pair_syn))==pairs and not any(int(x) in syndromes or x==0 for x in pair_syn)
        decoder={0:()};decoder.update({int(v):(i,) for i,v in enumerate(c)})
        decoder.update({int(v):(int(i),int(j)) for i,j,v in zip(ij[0],ij[1],pair_syn)})
        assert len(decoder)==1+N+pairs
        rng=random.Random(700+m);triple=0;quad=0
        for _ in range(2000):
            a=rng.sample(range(N),3);s=0
            for x in a:s^=int(c[x])
            triple+=s in decoder
            a=rng.sample(range(N),4);s=0
            for x in a:s^=int(c[x])
            quad+=s in decoder
        # Raw scan under promise <=2, unknown count: cannot stop before N
        # unless two defects found. Uniform over valid patterns (not counts).
        raw_mean=(N*(1+N)+pairs*2*(N+1)/3)/(1+N+pairs)
        reads=sum(int(x).bit_count() for x in c)
        data[m]=dict(N=N,pairs=pairs,valid_exponents=[k for k,v in mat[m].items() if v],lower_bound=math.ceil(math.log2(1+N+pairs)),parity_queries=2*m+1,raw_mean=raw_mean,raw_worst=N,emulated_parity_reads=reads,triple_alias=triple,quad_alias=quad,alias_trials=2000)
        if m<=8:
            rr=[];rng=np.random.default_rng(3901+m)
            for _ in range(64):
                h=rng.choice(1<<(2*m),N,replace=False);z=len(np.unique(h[ij[0]]^h[ij[1]]));rr.append((z+N+1)/(pairs+N+1))
            data[m]['random_code_mean']=statistics.mean(rr);data[m]['random_code_best']=max(rr)
        print(m,data[m],flush=True)
    cert={k:certificate(k) for k in EXPS};proved=[k for k,(g,_,_) in cert.items() if g]
    assert all(mat[m][k] for m in SIZES for k in proved)
    # Exact simulated cumulative pair-check cost for different policies using
    # independently randomized candidate orders; each attempted candidate is
    # charged a full exhaustive pair verification. No hidden test outcomes are
    # exposed before a candidate is evaluated. Precomputed matrix is evaluator.
    trials=[]
    for seed in range(TRIALS):
        order=random.Random(21999+seed).sample(EXPS,len(EXPS))
        def first(m,seq):
            for i,k in enumerate(seq,1):
                if mat[m][k]:return k,i*data[m]['pairs']
            raise AssertionError('no solution')
        k,cost=first(5,order);train_one=k;fresh=0;reuse=cost;first_reuse=k;fail=0;fresh_rows=[];reuse_rows=[]
        for m in HOLD:
            kk,cc=first(m,order);fresh+=cc;fresh_rows.append(cc)
            seq=[k]+[x for x in order if x!=k]
            if not mat[m][k]:fail+=1
            k,cc=first(m,seq);reuse+=cc;reuse_rows.append(cc)
        surviving=[x for x in order if mat[4][x] and mat[5][x]];vcost=len(EXPS)*(data[4]['pairs']+data[5]['pairs']);vrows=[];vfails=0
        for m in HOLD:
            while not mat[m][surviving[0]]:
                surviving.pop(0);vcost+=data[m]['pairs'];vfails+=1
            vcost+=data[m]['pairs'];vrows.append(surviving[0])
        # Generic symbolic proof verifier searches same candidate ordering.
        # Number of set-monomial ops is a DIFFERENT resource, not directly
        # equated to pair checks. No field enumeration needed after certificate.
        sym=0
        for z in order:
            good,_,ops=cert[z];sym+=ops
            if good:break
        trials.append(dict(seed=seed,train_one=train_one,first_transfer=first_reuse,fail=fail,version_fail=vfails,fresh=fresh,reuse=reuse,version=vcost,first_symbolic=z,symbolic_ops=sym,fresh_rows=fresh_rows,reuse_rows=reuse_rows,version_choices=vrows))
    out=dict(sizes=data,certificates=cert,proved=proved,trials=trials)
    (root/'bl08_results.json').write_text(json.dumps(out,indent=2))
    print('Universal sufficient proof schema accepts',proved)
    for label in ['fresh','reuse','version','symbolic_ops','fail','version_fail']:
        print(label,statistics.mean(r[label] for r in trials))
    print('valid on m5 but fail on at least one heldout', [k for k in EXPS if mat[5][k] and not all(mat[m][k] for m in HOLD)])
    print('valid on m4 and m5 but fail later', [k for k in EXPS if mat[4][k] and mat[5][k] and not all(mat[m][k] for m in HOLD)])
    print('Verified exact decoding of every error set of size <=2 at each dimension.')
if __name__=='__main__':main()
