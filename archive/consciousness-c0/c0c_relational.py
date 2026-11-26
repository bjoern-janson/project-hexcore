"""Exact finite calibration: discovery of a Boolean feature predictive of an intervention.
Balanced actions, six observations each; enumerate multinomial count histories.
Generic candidate language: all nonconstant 2-input Boolean truth tables modulo complement.
No parity-specific operation or label in learner. This is selection in a fixed universe.
"""
from math import factorial, log2
from itertools import product
from fractions import Fraction as F
M=6
# canonical masks: bit 0 off; nonconstant; all 7 complement classes
MASKS=tuple(range(2,16,2))
X,Y,PARITY=12,10,6
# training evidence threshold: BF>=70 for 7 candidates; trigger joint BF>=10 and both marginal BFs<10

def compositions(n,k):
    if k==1: yield (n,); return
    for i in range(n+1):
        for c in compositions(n-i,k-1): yield (i,)+c

def beta(a,b): return F(factorial(a)*factorial(b),factorial(a+b+1))
def bf(groups):
    a=sum(x for x,y in groups); b=sum(y for x,y in groups)
    v=F(1)
    for x,y in groups: v*=beta(x,y)
    return v/beta(a,b)
def groups(c,d,mask):
    return tuple((sum(c[i] for i in range(4) if (mask>>i)&1==z),sum(d[i] for i in range(4) if (mask>>i)&1==z)) for z in (0,1))
def histories(p):
    for c in compositions(M,4):
        w=F(factorial(M))
        for n,q in zip(c,p): w*=q**n/factorial(n)
        if w: yield c,w

def pred(gs, idx):
    a,b=gs[idx]; return float(F(b+1,a+b+2))
def loss(p0,p1,ps):
    return -sum(float(p)*log2((1-q) if a==0 else q)/2 for a,pp in enumerate((p0,p1)) for p,q in zip(pp,ps) if p)

def run(p0,p1,target):
    out={k:0. for k in ('trigger','gated_any','gated_target','always_any','always_target','marginal_loss','joint_loss','gated_loss','always_loss')}; mass=F(0)
    for (c,w0),(d,w1) in product(histories(p0),histories(p1)):
        w=w0*w1; mass+=w; w=float(w)
        scores={m:bf(groups(c,d,m)) for m in MASKS}; best=max(MASKS,key=lambda m:scores[m]); mb=max((X,Y),key=lambda m:scores[m]); j=list(zip(c,d)); trig=bf(j)>=10 and scores[mb]<10
        # retain the best supported marginal by default, otherwise pooled prediction
        base=mb if scores[mb]>=10 else None
        chosen=best if scores[best]>=70 else base
        gated=chosen if trig else base
        def predict(m):
            return [pred(groups(c,d,m),(m>>i)&1) for i in range(4)] if m is not None else [.5]*4
        for k,v in [('trigger',trig),('gated_any',gated is not None and gated not in (X,Y)),('gated_target',gated==target if target else False),('always_any',chosen is not None and chosen not in (X,Y)),('always_target',chosen==target if target else False),('marginal_loss',loss(p0,p1,predict(base))),('joint_loss',loss(p0,p1,[pred(j,i) for i in range(4)])),('gated_loss',loss(p0,p1,predict(gated))),('always_loss',loss(p0,p1,predict(chosen)))]: out[k]+=w*v
    assert mass==1
    return out
if __name__=='__main__':
    h=F(1,2); q=F(1,4); z=F(0)
    cases={'XOR':((h,z,z,h),(z,h,h,z),PARITY),'XNOR':((z,h,h,z),(h,z,z,h),PARITY),'independent null':((q,)*4,(q,)*4,None),'correlated null':((h,z,z,h),(h,z,z,h),None),'direct X':((h,h,z,z),(z,z,h,h),X),'noisy XOR 10%':((F(9,20),F(1,20),F(1,20),F(9,20)),(F(1,20),F(9,20),F(9,20),F(1,20)),PARITY)}
    print('M=6 per action; exact count-history distribution; held-out inverse log loss bits/action')
    for name,args in cases.items():
        print(name, {k:round(v,6) for k,v in run(*args).items()})
