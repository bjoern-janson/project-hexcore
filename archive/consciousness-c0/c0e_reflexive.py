import math,random,statistics
N=1000;T=96;SEED=20261124;noise=.1;hazard=.06
names=['greedy','random probe','generic MI','current-control MI']
def h(p):return -p*math.log2(p)-(1-p)*math.log2(1-p) if 0<p<1 else 0

def episode(k,b,c,s,prev,goals,errors,null,coins):
 p=[1/3]*3;r=l=acc=over=0
 for t,g in enumerate(goals):
  p=[(1-hazard)*v+hazard/3 for v in p]; q=[[.1+.8*a,.1+.8*prev,.5] for a in (0,1)]; pred=[sum(v*w for v,w in zip(p,u)) for u in q]; util=[v if g else 1-v for v in pred]; greedy=g;a=greedy
  if t%6==0:
   if k==1:a=coins[t]
   elif k>=2:
    scores=[]
    for i,u in enumerate(q):
     cond=sum(v*h(w) for v,w in zip(p,u)) if k==2 else p[0]*h(u[0])+(p[1]+p[2])*h((p[1]*u[1]+p[2]*u[2])/(p[1]+p[2]))
     scores.append(util[i]+h(pred[i])-cond)
    a=int(scores[1]>scores[0]) if abs(scores[1]-scores[0])>1e-12 else greedy
   over+=a!=greedy
  mode=b if t<s else c;z=((a if mode==0 else prev)^errors[t]) if mode!=2 else null[t]
  r+=z==g;l-=math.log2(pred[a] if z else 1-pred[a]);p=[v*(w if z else 1-w) for v,w in zip(p,q[a])];total=sum(p);p=[v/total for v in p];acc+=max(range(3),key=p.__getitem__)==mode;prev=a
 return r/T,l/T,acc/T,over

def run():
 rng=random.Random(SEED)
 print('Exploratory paired simulation; 1000 histories/case, 96 steps, 16 diagnostic opportunities, 10% noise, hazard .06, switch uniform 32..64; reward + 1 bit-weight MI. Modes: current, lag, independent. All policies share filter and observation/action budget. Goals iid fair bits. Intervals paired episode normal Monte Carlo. Columns reward, logloss, mode accuracy, overrides, reward delta vs greedy [95% CI].')
 for b,c in [(0,1),(1,2),(2,0),(0,0),(1,1),(2,2)]:
  rows=[[] for _ in names]
  for _ in range(N):
   s=rng.randint(32,64);prev=rng.randrange(2);goals=[rng.randrange(2) for _ in range(T)];errors=[int(rng.random()<noise) for _ in range(T)];null=[rng.randrange(2) for _ in range(T)];coins=[rng.randrange(2) for _ in range(T)]
   for k in range(4):rows[k].append(episode(k,b,c,s,prev,goals,errors,null,coins))
  print(f'\n{b}->{c}')
  for name,row in zip(names,rows):
   v=[statistics.mean(x) for x in zip(*row)];d=[a[0]-b[0] for a,b in zip(row,rows[0])];m=statistics.mean(d);se=statistics.stdev(d)/math.sqrt(N);print(name,*(f'{x:.5f}' for x in v),f'{m:+.5f} [{m-1.96*se:+.5f},{m+1.96*se:+.5f}]')
if __name__=='__main__':run()
