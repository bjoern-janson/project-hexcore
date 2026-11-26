"""Exploratory assay: streaming GF(2) invariant discovery, not open-ended invention.
Protocol fixed in source: 32 seeds, four dimensions, four checkpoints; compare
rebuilding the dual space, incremental dual, and generic incremental primal RREF.
Cost = count of word parity tests and word XORs (not physical FLOPs). All methods
receive identical rows. Validation is outside learner cost and shared.
"""
import random,json,statistics,time
from pathlib import Path
N=(16,32,64,128); SEEDS=range(32)
class Count:
 def __init__(self):self.dot=0;self.xor=0;self.test=0
 def parity(self,a,b):self.dot+=1;return (a&b).bit_count()&1
 def add(self,a,b):self.xor+=1;return a^b
 def bit(self,a,i):self.test+=1;return (a>>i)&1
 def total(self):return self.dot+self.xor+self.test
class Dual:
 def __init__(self,n):self.b=[1<<i for i in range(n)];self.c=Count()
 def update(self,row):
  hits=[i for i,v in enumerate(self.b) if self.c.parity(v,row)]
  if hits:
   p=hits[0]; pivot=self.b[p]
   for j in hits[1:]:self.b[j]=self.c.add(self.b[j],pivot)
   self.b.pop(p)
 def basis(self):return self.b[:]
class Primal:
 def __init__(self,n):self.n=n;self.r={};self.c=Count()
 def update(self,row):
  for i,v in sorted(self.r.items(),reverse=True):
   if self.c.bit(row,i):row=self.c.add(row,v)
  if not row:return
  p=row.bit_length()-1
  for i,v in list(self.r.items()):
   if self.c.bit(v,p):self.r[i]=self.c.add(v,row)
  self.r[p]=row
 def basis(self):
  out=[]
  for j in range(self.n):
   if j in self.r:continue
   v=1<<j
   for i,r in self.r.items():
    if self.c.bit(r,j):v=self.c.add(v,1<<i)
   out.append(v)
  return out

def rank(rows):
 p={}
 for x in rows:
  while x:
   i=x.bit_length()-1
   if i in p:x^=p[i]
   else:p[i]=x;break
 return len(p)
def verify(b,rows,n):
 assert len(b)==rank(b)==n-rank(rows)
 assert all((v&r).bit_count()%2==0 for v in b for r in rows)

def run():
 out=[]
 for n in N:
  for seed in SEEDS:
   rng=random.Random(83177*n+seed)
   # Fresh random full-rank history, no hand-selected coordinate alignment.
   rows=[]
   while len(rows)<n:
    v=rng.getrandbits(n)
    if rank(rows+[v])>len(rows):rows.append(v)
   # Four milestones, each receives another independent batch plus redundant rows.
   hist=[]; dual=Dual(n); primal=Primal(n); rebuild_total=0
   for k in range(1,5):
    batch=rows[(k-1)*n//4:k*n//4]
    # One dependent example for each independent example; randomized within batch.
    redundant=[]
    for _ in batch:
     x=0
     for v in rows[:k*n//4]:
      if rng.getrandbits(1):x^=v
     redundant.append(x)
    batch=batch+redundant;rng.shuffle(batch);hist+=batch
    d0=dual.c.total();p0=primal.c.total()
    for v in batch:dual.update(v);primal.update(v)
    db=dual.basis();pb=primal.basis()
    fresh=Dual(n)
    for v in hist:fresh.update(v)
    fb=fresh.basis();rebuild_total+=fresh.c.total()
    for b in (db,pb,fb):verify(b,hist,n)
    # Held-out combinations of known generators and a new independent direction.
    for _ in range(16):
     x=0
     for v in rows[:k*n//4]:
      if rng.getrandbits(1):x^=v
     assert all((x&v).bit_count()%2==0 for v in db)
    if k<4:assert any((rows[k*n//4]&v).bit_count()%2 for v in db)
    out.append(dict(n=n,seed=seed,stage=k,dimension=len(db),history=len(hist),dual_delta=dual.c.total()-d0,dual_lifetime=dual.c.total(),primal_delta=primal.c.total()-p0,primal_lifetime=primal.c.total(),fresh_cost=fresh.c.total(),fresh_lifetime=rebuild_total))
 return out
if __name__=='__main__':
 t=time.perf_counter();rows=run();Path(__file__).with_name('bl02_invariants_results.json').write_text(json.dumps(rows,indent=2))
 print('n stage dimension dual_increment primal_increment fresh_at_stage dual_lifetime primal_lifetime fresh_lifetime')
 for n in N:
  for k in range(1,5):
   a=[r for r in rows if r['n']==n and r['stage']==k]
   print(n,k,a[0]['dimension'],*[round(statistics.mean(r[x] for r in a),2) for x in ('dual_delta','primal_delta','fresh_cost','dual_lifetime','primal_lifetime','fresh_lifetime')])
 print('verified',len(rows)*3,'bases;',len(rows)*16,'held-out span checks; seconds',round(time.perf_counter()-t,2))
