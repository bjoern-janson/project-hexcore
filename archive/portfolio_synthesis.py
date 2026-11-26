import itertools,random,time,json,statistics
from functools import lru_cache
from pathlib import Path
from scoped_synthesis import solve

# All backends emit the same hash-consed Boolean DAG; primitives AND OR NOR XOR.
class DAG:
 def __init__(self,n): self.n=n; self.nodes=[('input',i) for i in range(n)]+[('const',0),('const',1)]; self.cache={x:i for i,x in enumerate(self.nodes)}
 def op(self,o,a,b):
  if o=='AND':
   if a==self.n or b==self.n:return self.n
   if a==self.n+1:return b
   if b==self.n+1:return a
   if a==b:return a
  if o=='OR':
   if a==self.n+1 or b==self.n+1:return self.n+1
   if a==self.n:return b
   if b==self.n:return a
   if a==b:return a
  if o=='XOR' and a==b:return self.n
  k=(o,*sorted((a,b)))
  if k not in self.cache:self.cache[k]=len(self.nodes);self.nodes.append(k)
  return self.cache[k]
 def neg(self,a):return self.op('NOR',a,a)
 def mux(self,x,a,b):
  if a==b:return a
  if a==self.n and b==self.n+1:return x
  if b==self.n and a==self.n+1:return self.neg(x)
  return self.op('OR',self.op('AND',self.neg(x),a),self.op('AND',x,b))
 def bdd(self,vs,t):
  @lru_cache(None)
  def rec(v,t):
   k=len(v); half=1<<(k-1) if k else 0
   if not t:return self.n
   if t==(1<<(1<<k))-1:return self.n+1
   return self.mux(v[-1],rec(v[:-1],t&((1<<half)-1)),rec(v[:-1],t>>half))
  return rec(tuple(vs),t)
 def expr(self,s):
  import ast
  def rec(x):
   if isinstance(x,ast.Constant):return self.n+x.value
   if isinstance(x,ast.Name):return int(x.id[1:])
   return self.op({'M':'XOR'}.get(x.func.id,x.func.id),*(rec(a) for a in x.args))
  return rec(ast.parse(s,mode='eval').body)
 def finish(self,root,target):
  mask=(1<<(1<<self.n))-1; seen=set()
  @lru_cache(None)
  def val(i):
   k=self.nodes[i];seen.add(i)
   if k[0]=='input':return sum(((s>>k[1])&1)<<s for s in range(1<<self.n))
   if k[0]=='const':return mask*k[1]
   a,b=map(val,k[1:]);return {'AND':a&b,'OR':a|b,'XOR':a^b,'NOR':mask^(a|b)}[k[0]]
  assert val(root)==target
  return sum(i>=self.n+2 for i in seen)

def multi(d,n,t):
 # Balanced cut, encode distinct residual functions with binary class IDs.
 k=n//2; w=1<<k; rows=[sum(((t>>(a+(b<<k)))&1)<<b for b in range(1<<(n-k))) for a in range(w)]
 classes=list(dict.fromkeys(rows)); ids=[classes.index(r) for r in rows]; bits=(len(classes)-1).bit_length()
 codes=[d.bdd(range(k),sum(((c>>j)&1)<<a for a,c in enumerate(ids))) for j in range(bits)]
 residual=[d.bdd(range(k,n),r) for r in classes]; residual += [d.n]*(2**bits-len(residual))
 for code in codes:residual=[d.mux(code,a,b) for a,b in zip(residual[::2],residual[1::2])]
 return residual[0],len(classes)

def run(method,n,t):
 start=time.perf_counter_ns();d=DAG(n);extra={}
 if method=='scoped':
  r=solve(n,t,budget=12000);extra['checks']=r['checks'];root=d.expr(r['expression']) if r['expression'] else None
 elif method=='multi':root,c=multi(d,n,t);extra['classes']=c
 else:root=d.bdd(range(n),t)
 gates=d.finish(root,t) if root is not None else None
 return dict(gates=gates,us=(time.perf_counter_ns()-start)/1000,**extra)

def main():
 rng=random.Random(1729); records=[]
 for n in (4,6,8):
  for family in ('parity','majority','mixed','random'):
   for trial in range(4):
    perm=list(range(n));rng.shuffle(perm)
    def f(s):
     x=[(s>>i)&1 for i in perm]
     if family=='parity':return sum(x)%2
     if family=='majority':return sum(x)>=n//2+1
     if family=='mixed':return (sum(x[:n//2])%2) ^ int(all(x[n//2:]))
     return rng.randrange(2)
    t=sum(int(f(s))<<s for s in range(1<<n));results={m:run(m,n,t) for m in ('bdd','scoped','multi')};records.append(dict(n=n,family=family,trial=trial,target=hex(t),results=results))
 # Online selector: prior completed tasks only, no family labels. Cost objective gates + latency (1 gate per 100 us).
 # Select by n and observed row count, charge feature extraction, update from full shadow runs (charged separately).
 hist={}; totals={m:0 for m in ('bdd','scoped_fallback','multi','portfolio','oracle')}; time_tot={m:0 for m in totals}; choices={}
 rng.shuffle(records)
 for r in records:
  n=r['n'];t=int(r['target'],16);start=time.perf_counter_ns();k=n//2; rows={sum(((t>>(a+(b<<k)))&1)<<b for b in range(1<<(n-k))) for a in range(1<<k)};key=(n,len(rows));feature=(time.perf_counter_ns()-start)/1000
  v=r['results'];cost={m:(z['gates'] if z['gates'] is not None else v['bdd']['gates']) for m,z in v.items()};lat={m:z['us']+(v['bdd']['us'] if z['gates'] is None else 0) for m,z in v.items()}
  h=hist.setdefault(key,{m:[] for m in v}); choice=min(v,key=lambda m:statistics.mean(h[m]) if h[m] else (0 if m=='bdd' else 1));choices[choice]=choices.get(choice,0)+1
  best=min(v,key=lambda m:cost[m]+lat[m]/100)
  for label,m in [('bdd','bdd'),('scoped_fallback','scoped'),('multi','multi'),('portfolio',choice),('oracle',best)]:totals[label]+=cost[m];time_tot[label]+=lat[m]+(feature if label=='portfolio' else 0)
  # Full information shadow evaluation costs: already measured; charge both unchosen methods.
  time_tot['portfolio']+=sum(z['us'] for m,z in v.items() if m!=choice)
  for m in v:h[m].append(cost[m]+lat[m]/100)
  r['choice']=choice
 out=dict(records=records,totals=totals,time_us=time_tot,choices=choices)
 Path(__file__).with_name('portfolio_synthesis_results.json').write_text(json.dumps(out,indent=2));print(totals,time_tot,choices)
 for f in ('parity','majority','mixed','random'):
  rr=[r for r in records if r['family']==f];print(f,{m:(sum(z['results'][m]['gates'] is not None for z in rr),sum(z['results'][m]['gates'] or 0 for z in rr),round(sum(z['results'][m]['us'] for z in rr))) for m in ('bdd','scoped','multi')})
if __name__=='__main__':main()
