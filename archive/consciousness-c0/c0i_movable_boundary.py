"""C0i exploratory exact assay. No external dependencies.
Two output channels: one responds to command, other is fair noise.
Three initial probes, optional cue about transfer, one new probe, then control.
Physical host label is independent and unobserved (negative control).
"""
from fractions import Fraction as F
from itertools import product
Q=F(1,10)
OBS=list(product(range(2),repeat=2))
def like(m,o,a=1):
    return (1-Q if o[m]==a else Q)*F(1,2)
def update(p,o):
    w=[p*like(0,o),(1-p)*like(1,o)]
    return w[0]/sum(w)
def histories(n,m):
    for h in product(OBS,repeat=n):
        w=F(1); p=F(1,2)
        for o in h:
            w*=like(m,o); p=update(p,o)
        yield h,w,p

def score(p,m):
    # target (1,0); action 1 if channel 0 believed controlled, else 0.
    correct=(p>F(1,2) and m==0) or (p<F(1,2) and m==1)
    return F(1,2) if p==F(1,2) else F(7,10) if correct else F(3,10)
def generic_update(r,o):
    # r = predicted P(x=1 | command 1), not a designated self variable.
    # same two endpoint response laws; Bayes over the endpoints.
    w=(r-F(1,2))/(F(9,10)-F(1,2))
    return F(1,2)+F(2,5)*update(w,o)
def generic_to_p(r): return (r-F(1,2))/F(2,5)

def run(flip, cue):
    names=['fixed','frozen','reset','adaptive_uncued','cue_model','generic','oracle']
    sums={k:F(0) for k in names}; mass=F(0); disagreement=F(0)
    for m in range(2):
      for h,w,p in histories(3,m):
       for change in range(2):
        m2=m^change; wt=F(1,2)*w*(flip if change else 1-flip)
        for o in OBS:
          weight=wt*like(m2,o); mass+=weight
          predicted=(1-cue)*p+cue*(1-p)
          post=update(predicted,o)
          r=F(1,2)+F(2,5)*predicted
          gen=generic_to_p(generic_update(r,o))
          assert gen==post
          # relabel channels: probability complements; score is invariant if target and action relabeled.
          assert update(1-predicted,o[::-1])==1-post
          ps=[F(1,2),p,update(F(1,2),o),update(F(4,5)*p+F(1,5)*(1-p),o),post,gen,F(int(m2==0))]
          for k,v in zip(names,ps): sums[k]+=weight*score(v,m2)
    assert mass==1
    return sums
if __name__=='__main__':
    print('C0i exact enumeration; 3 initial diagnostic probes + 1 post-transfer probe')
    print('Expected fraction of two target bits matched; oracle = 0.7; ties random.')
    for label,flip,cue in [('stable',F(0),F(0)),('transfer 80%, calibrated cue',F(4,5),F(4,5)),('transfer 80%, misleading cue',F(4,5),F(0)),('certain transfer',F(1),F(1))]:
        print('\n'+label)
        for k,v in run(flip,cue).items(): print(f'{k:20s} {float(v)*100:9.5f}%  exact={v}')
    print('\nExact posterior equivalence and channel-permutation checks passed for every enumerated case.')
    print('Physical-host label independent of all dynamics: likelihood ratio 1, posterior 1/2, MI=0 by construction.')
