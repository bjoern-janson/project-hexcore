"""Exact finite C0 assay. No training or stochastic sampling required.
Hypotheses: which output bit is controlled by action; the other is fair noise.
All action histories and observation histories enumerated with exact probabilities.
"""
from fractions import Fraction as F
from itertools import product
from math import log2

STATES=list(product((0,1),repeat=2))
def likelihood(s,a,h):
    return F(1,2) if s[h]==a else F(0)
def history_likelihood(obs,acts,h):
    p=F(1)
    for s,a in zip(obs,acts): p*=likelihood(s,a,h)
    return p

def assay(n):
    acc=F(0); identified=F(0); score=0.; null_score=0.
    for acts in product((0,1),repeat=n):
      for obs in product(STATES,repeat=n):
        l=[history_likelihood(obs,acts,h) for h in (0,1)]
        mass=sum(l)*F(1,2**(n+1))
        if not mass: continue
        p=[v/sum(l) for v in l]
        acc+=mass*max(p); identified+=mass*(max(p)==1)
        for a in (0,1):
          for s in STATES:
            prob=sum(p[h]*likelihood(s,a,h) for h in (0,1))
            null=F(1,2)*sum(likelihood(s,a,h) for h in (0,1))
            if prob:
              score-=float(mass*prob/2)*log2(float(prob))
              null_score-=float(mass*prob/2)*log2(float(null))
    assert identified==1-F(1,2**n)
    assert acc==1-F(1,2**(n+1))
    return float(identified),float(acc),score,null_score

if __name__=='__main__':
    print('n  identified  MAP accuracy  predictive loss(bits)  no-history loss(bits)')
    for n in range(7):
        i,a,s,b=assay(n); print(f'{n}  {i:10.6f}  {a:12.6f}  {s:21.6f}  {b:21.6f}')
    # Observational aliasing: if both bits are copied from a, the two causal labels
    # induce identical distributions. No amount of this evidence identifies ownership.
    print('Matched observational alias: posterior=(1/2,1/2) at every horizon')
