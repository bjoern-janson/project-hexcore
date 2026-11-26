import random, math, statistics
N=2000; T=96; SEED=20261124; E=.1; H=.04
NAMES=('fixed','last observation','causal model','generic predictor','oracle')
def episode(modes,errors,goals,k,h):
    p=.5; q=.5; last=0; correct=0; loss=0; post=[]
    for t,(m,e,g) in enumerate(zip(modes,errors,goals)):
        # p: probability of inverted actuator; q: probability that output for action 0 is 1.
        p=h+(1-2*h)*p; q=h+(1-2*h)*q
        if k==0: a=g; pred=.5
        elif k==1: a=g^last; pred=.5 if t==0 else .1+.8*last
        elif k==2: a=g^int(p>.5); pred=E+(1-2*E)*p
        elif k==3:
            prob1=[E+(1-2*E)*q,1-(E+(1-2*E)*q)]
            a=max((g,1-g),key=lambda a: prob1[a] if g else 1-prob1[a]); pred=E+(1-2*E)*q
        else: a=g^m; pred=E+(1-2*E)*m
        z=a^m^e; d=z^a; correct+=z==g; post.append(int(z==g)); loss-=math.log2(pred if d else 1-pred)
        last=d
        l1=1-E if d else E; l0=E if d else 1-E
        p=p*l1/(p*l1+(1-p)*l0)
        # Generic output likelihood update, using observed action and output directly.
        r0= E+(1-2*E)*a; r1=1-r0
        lq1=r1 if z else 1-r1; lq0=r0 if z else 1-r0
        q=q*lq1/(q*lq1+(1-q)*lq0)
        assert abs(p-q)<1e-12
    return correct/T,loss/T,tuple(post)
def run():
 rng=random.Random(SEED)
 print('Exploratory C0f; paired histories, iid fair goals; z=a XOR m XOR e; e~Bernoulli(.1); initial m fair. Filter hazard .04 for every scenario. N=2000 per scenario, T=96. Causal and generic filters mathematically equivalent. CI paired episode normal approximation; no tuning.')
 for scenario in ('stable','single switch','Markov switching'):
    rows=[[] for _ in NAMES]; matches=0; switch_scores=[[] for _ in NAMES]
    for _ in range(N):
      m=rng.randrange(2); modes=[]; s=rng.randrange(32,65)
      for t in range(T):
        if t and ((scenario=='single switch' and t==s) or (scenario=='Markov switching' and rng.random()<H)):m^=1
        modes.append(m)
      errors=[int(rng.random()<E) for _ in modes]; goals=[rng.randrange(2) for _ in modes]
      out=[episode(modes,errors,goals,k,H) for k in range(len(NAMES))]
      matches+=out[2][2]==out[3][2]
      for k,r in enumerate(out):
        rows[k].append(r)
        if scenario=='single switch':switch_scores[k].append(sum(r[2][s:s+12])/12)
    print('\n'+scenario, 'matched causal/generic reward traces',matches,'/',N)
    for k,name in enumerate(NAMES):
      r=rows[k]; dif=[a[0]-b[0] for a,b in zip(r,rows[1])]; avg=statistics.mean(dif); ci=1.96*statistics.stdev(dif)/math.sqrt(N)
      print(f'{name:18s} reward={statistics.mean(x[0] for x in r):.6f} loss={statistics.mean(x[1] for x in r):.6f} delta_vs_last={avg:+.6f} CI=[{avg-ci:+.6f},{avg+ci:+.6f}]',f'post12={statistics.mean(switch_scores[k]):.6f}' if switch_scores[k] else '')
if __name__=='__main__':run()
