"""C0b: exact finite-distribution assay of generic binary dependency learning.
No control/self labels are given to the learner. Balanced randomized interventions.
The learner compares generic pooled vs action-conditioned Bernoulli predictors.
Uniform Beta(1,1) priors and equal prior model odds; BF>=10 is evidence threshold.
All binomial count histories are enumerated with exact integer probability weights.
"""
from fractions import Fraction as F
from math import comb, log2

def marginal(k,n):
    return F(1,(n+1)*comb(n,k))

def assay(m, controlled):
    detection=F(0); loss=0.; pooled_loss=0.; conditional_loss=0.; mass=F(0)
    for k0 in range(m+1):
      for k1 in range(m+1):
        w = F(int(k0==0 and k1==m)) if controlled else F(comb(m,k0)*comb(m,k1),2**(2*m))
        if not w: continue
        mass+=w
        bf=marginal(k0,m)*marginal(k1,m)/marginal(k0+k1,2*m)
        posterior=bf/(1+bf)
        detection+=w*(bf>=10)
        pooled=F(k0+k1+1,2*m+2)
        for a,k in enumerate((k0,k1)):
          conditional=F(k+1,m+2)
          pred=posterior*conditional+(1-posterior)*pooled
          truth=F(a) if controlled else F(1,2)
          def ce(p): return -float(truth)*log2(float(p))-float(1-truth)*log2(float(1-p))
          loss+=float(w)/2*ce(pred)
          pooled_loss+=float(w)/2*ce(pooled)
          conditional_loss+=float(w)/2*ce(conditional)
    assert mass==1
    return float(detection),loss,pooled_loss,conditional_loss

def run():
    print('n  TPR      FPR      exact map: none / one / both     avg logloss: mix / pooled / conditional (bits per output)')
    for m in (1,2,3,4,6,8,16,32):
      t,l1,p1,c1=assay(m,True); f,l0,p0,c0=assay(m,False)
      print(f'{2*m:2} {t:8.5f} {f:8.5f}   {(1-f)**2:8.5f} {t*(1-f):8.5f} {t*t:8.5f}     {(l0+l1)/2:.6f} {(p0+p1)/2:.6f} {(c0+c1)/2:.6f}')
    # Causal alias: without randomized action, a common cause U with A=U, X=U
    # gives exactly the same observational (A,X) law as A fair, X=A.
    # Under do(A=a), the former has X fair; the latter X=a.
    # Joint-only dependence: X=U, Y=U xor A; each marginal is fair,
    # while the joint output determines A exactly. This learner cannot detect it.
    for a in (0,1):
      states=[(u,u^a) for u in (0,1)]
      assert sum(x for x,y in states)==sum(y for x,y in states)==1
      assert all(x^y==a for x,y in states)
    print('Joint-only XOR control: marginal true dependency=0 bits each; joint dependency=1 bit.')
if __name__=='__main__': run()
