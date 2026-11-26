"""Exploratory BL03: exact discovery of translation symmetries via Walsh support.
Fixed design: n=6,8,10,12; 16 seeds; nested random full-rank linear maps of
ranks n-2,n-4,n-5; fresh independent Boolean truth tables conditioned on full
Walsh-support rank. Compare fresh full-domain Walsh inference, persistent
quotient inference, and a generic memoized quotient baseline (same algorithm).
Costs: oracle queries, Walsh butterflies, and parity tests separately. Full
external verification not charged to learner; report its size. Shift control
uses independently sampled rank n-5 map. No claim of novel mathematical tools.
"""
import random, json, statistics, itertools
from pathlib import Path

def basis(vs):
 b={}
 for v in vs:
  while v:
   i=v.bit_length()-1
   if i in b:v^=b[i]
   else:b[i]=v;break
 return list(b.values())
def span(b):
 a=[0]
 for v in b:a += [x^v for x in a]
 return a
def independent(n,r,rng):
 b=[]
 while len(b)<r:
  v=rng.randrange(1,1<<n)
  if len(basis(b+[v]))>len(b):b.append(v)
 return b
def fwht(a):
 a=a[:];h=1
 while h<len(a):
  for i in range(0,len(a),2*h):
   for j in range(i,i+h):x,y=a[j],a[j+h];a[j],a[j+h]=x+y,x-y
  h*=2
 return a
def support(f):return basis(i for i,v in enumerate(fwht([1-2*x for x in f])) if v)
def table(r,rng):
 while True:
  f=[rng.randrange(2) for _ in range(1<<r)]
  if len(support(f))==r:return f
def encode(x,b):return sum(((x&v).bit_count()%2)<<i for i,v in enumerate(b))
def reps(n,b):
 # Construct representatives by elimination on columns of the linear map.
 # Count parity operations used to form its columns; enumerate only 2^rank reps.
 cols=[encode(1<<i,b) for i in range(n)]; piv={}
 for i,c in enumerate(cols):
  v=c;w=1<<i
  while v:
   k=v.bit_length()-1
   if k in piv:v^=piv[k][0];w^=piv[k][1]
   else:piv[k]=(v,w);break
 out=[];xor=0
 for y in range(1<<len(b)):
  v=y;w=0
  while v:
   k=v.bit_length()-1;a,z=piv[k];v^=a;w^=z;xor+=2
  out.append(w)
 return out,n*len(b),xor

def discover(n,b,oracle):
 xs,par,xor=reps(n,b);f=[oracle(x) for x in xs];s=support(f)
 new=[]
 for v in s:
  z=0
  for i,w in enumerate(b):
   if v>>i&1:z^=w
  new.append(z)
 return new,dict(queries=len(xs),butterflies=len(xs)*len(b)//2,representative_parities=par,representative_solve_xors=xor),f

def run():
 rows=[]
 for n in (6,8,10,12):
  for seed in range(16):
   rng=random.Random(8300*n+seed);ranks=[n-2,n-4,n-5];hidden=independent(n,ranks[0],rng);learned=[1<<i for i in range(n)]
   for stage,r in enumerate(ranks):
    h=hidden[:r];f=table(r,rng);oracle=lambda x:f[encode(x,h)]
    old=learned[:];learned,cost,observed=discover(n,old,oracle)
    fresh,fc,_=discover(n,[1<<i for i in range(n)],oracle)
    assert set(span(learned))==set(span(fresh))==set(span(h))
    assert all(oracle(x)==observed[encode(x,old)] for x in range(1<<n))
    # On each task the generic persistent Walsh baseline uses the same prior
    # support and same quotient, so its results/costs are exactly identical.
    rows.append(dict(n=n,seed=seed,stage=stage+1,rank=r,adaptive=cost,fresh=fc))
   # Test the invalidity of blindly inheriting the learned quotient on shift.
   h=independent(n,ranks[-1],rng);f=table(len(h),rng);oracle=lambda x:f[encode(x,h)]
   xs,_,_=reps(n,learned);pred=[oracle(x) for x in xs]
   errors=sum(oracle(x)!=pred[encode(x,learned)] for x in range(1<<n))
   rows[-1]['shift_error']=errors/(1<<n)
   # One random held-out check has exact miss probability 1-error; independent
   # draws with replacement have (1-error)^k. Audit cost includes 16 queries.
   rows[-1]['shift_miss16']=(1-errors/(1<<n))**16
 return rows
if __name__=='__main__':
 rows=run();Path(__file__).with_name('bl03_quotient_results.json').write_text(json.dumps(rows,indent=2))
 for n in (6,8,10,12):
  a=[x for x in rows if x['n']==n]
  print('n',n,'queries',[(x['adaptive']['queries'],x['fresh']['queries']) for x in a[:3]],'lifetime butterflies',sum(x['adaptive']['butterflies'] for x in a[:3]),sum(x['fresh']['butterflies'] for x in a[:3]),'mean shift error',statistics.mean(x['shift_error'] for x in a if x['stage']==3),'mean miss16',statistics.mean(x['shift_miss16'] for x in a if x['stage']==3))
 print('verified',len(rows),'paired exact support spaces; external full-domain checks',sum(1<<x['n'] for x in rows))
