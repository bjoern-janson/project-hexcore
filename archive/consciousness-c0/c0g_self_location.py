import random, math, statistics
N=4000; T=8; SEED=20261124; E=.1
# Two sources routed to two outputs; opposing targets (g,1-g).
# Training logs both actions; other source is unknown and fair at test.
def out(a,b,m,e): return ((a,b) if m==0 else (b,a))[0]^e[0], ((a,b) if m==0 else (b,a))[1]^e[1]
def L(a,b,x,m): return math.prod(.9 if i==j else .1 for i,j in zip(x,(a,b) if m==0 else (b,a)))
def run():
 r=random.Random(SEED)
 print('C0g exploratory paired assay; 4000 independent histories per condition, 8 training steps; exact expected held-out reward per history, fair other action; noise .1; no test updates.')
 for scenario in ('synchronous','independent','opposed'):
  rows=[]; matches=0; ident=[]
  for _ in range(N):
   m=r.randrange(2); w=[1.,1.]; c=[[[1,1] for a in range(2)] for j in range(2)]
   for t in range(T):
    a=r.randrange(2); b=a if scenario=='synchronous' else 1-a if scenario=='opposed' else r.randrange(2)
    x=out(a,b,m,[int(r.random()<E) for j in range(2)])
    w=[w[h]*L(a,b,x,h) for h in range(2)]
    for j in range(2): c[j][a][x[j]]+=1
   p=w[1]/sum(w); route=int(p>.5+1e-12); ident.append(.5 if abs(p-.5)<1e-12 else int(route==m))
   rewards=[0.]*5; same=True
   for g in (0,1):
    targets=(g,1-g)
    def table(a): return sum(c[j][a][targets[j]]/sum(c[j][a]) for j in range(2))/2
    def generic(a):
     return sum(w[h]/sum(w)*sum(.5*L(a,b,x,h)*sum(x[j]==targets[j] for j in range(2))/2 for b in (0,1) for x in ((0,0),(0,1),(1,0),(1,1))) for h in (0,1))
    aa=[g,max((g,1-g),key=lambda a:round(table(a),12)),targets[route],max((g,1-g),key=lambda a:round(generic(a),12)),targets[m]]
    same &= aa[2]==aa[3]
    for k,a in enumerate(aa): rewards[k]+=(.5+(.9 if a==targets[m] else .1))/4
   matches+=same; rows.append(rewards)
  print(scenario,'identification',statistics.mean(ident),'matched policies',matches,'/',N)
  for k,name in enumerate(('fixed route','generic marginal table','explicit attribution','generic structured','oracle')):
   vals=[x[k] for x in rows]; ds=[x[k]-x[1] for x in rows]; d=statistics.mean(ds); ci=1.96*statistics.stdev(ds)/math.sqrt(N)
   print(f'{name}: reward={statistics.mean(vals):.6f}; delta vs table={d:.6f}; 95% CI [{d-ci:.6f},{d+ci:.6f}]')
 for a,b in ((0,0),(0,1)):
  kl=sum(L(a,b,x,0)*math.log2(L(a,b,x,0)/L(a,b,x,1)) for x in ((0,0),(0,1),(1,0),(1,1)))
  print('KL',a,b,kl)
if __name__=='__main__':run()
