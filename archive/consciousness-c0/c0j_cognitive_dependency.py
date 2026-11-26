"""C0j exploratory exact assay: locate a memory dependency via intervention.
Python standard library. Fixed controller and inference machinery are outside
mutable registers; no claim of endogenous selfhood or consciousness.
"""
from fractions import Fraction as F
from itertools import product
from functools import lru_cache
Q=F(1,10)

def execute(route, bit, reset, replacement, noise):
    registers=[bit,bit]  # observationally identical at write time
    if reset is not None:
        registers[reset]=replacement
    return registers[route]^noise  # actual read from mutable register

@lru_cache(None)
def kernel(route,reset):
    # distribution of correctness of the actual memory read
    out=[F(0),F(0)]
    for bit,replacement,noise in product(range(2),repeat=3):
        w=F(1,4)*(Q if noise else 1-Q)
        correct=int(execute(route,bit,reset,replacement,noise)==bit)
        out[correct]+=w
    assert sum(out)==1
    return tuple(out)

def update(p,reset,o):
    l0,l1=kernel(0,reset)[o],kernel(1,reset)[o]
    return p*l0/(p*l0+(1-p)*l1)

def generic_update(odds,reset,o):
    # generic two-response-law predictor, no ownership label
    return odds*kernel(0,reset)[o]/kernel(1,reset)[o]

def test_score(p,route):
    # protect likely read register; the other register is reset
    if p==F(1,2): return F(1,2)*(kernel(route,0)[1]+kernel(route,1)[1])
    protect=0 if p>F(1,2) else 1
    return kernel(route,1-protect)[1]

def run(schedule,flip=F(0),cue=F(0)):
    acc=loc=base=oracle=mass=F(0); ties=F(0); frozen=F(0)
    for route in range(2):
      for history in product(range(2),repeat=len(schedule)):
        p=F(1,2); odds=F(1); w=F(1,2)
        for reset,o in zip(schedule,history):
            w*=kernel(route,reset)[o]
            p=update(p,reset,o); odds=generic_update(odds,reset,o)
            assert p==odds/(1+odds)
        for change in range(2):
            r=route^change; weight=w*(flip if change else 1-flip)
            pp=(1-cue)*p+cue*(1-p)
            mass+=weight
            acc+=weight*test_score(pp,r)
            frozen+=weight*test_score(p,r)
            base+=weight*test_score(F(1,2),r)
            oracle+=weight*test_score(F(int(r==0)),r)
            loc+=weight*(F(1,2) if pp==F(1,2) else int((pp>F(1,2))==(r==0)))
            ties+=weight*(pp==F(1,2))
    assert mass==1
    return loc,acc,base,oracle,ties,frozen

def show(label,schedule,flip=F(0),cue=F(0)):
    vals=run(schedule,flip,cue)
    print(label, ' | '.join(f'{k}={float(v)*100:.6f}% ({v})' for k,v in zip(['location','task','blind','oracle','ties','frozen'],vals)))

if __name__=='__main__':
    print('C0j exact finite assay; output noise 10%, randomized reset; one final protected memory read.')
    for r in range(2):
        print('route',r,'P(correct) passive/reset0/reset1:',*[str(kernel(r,i)[1]) for i in [None,0,1]])
    for n in [0,2,4,8,12]:
        show(f'passive n={n}',[None]*n)
        show(f'active n={n}',[i%2 for i in range(n)])
    for flip,cue in [(F(1),F(0)),(F(1),F(1)),(F(4,5),F(4,5))]:
        show(f'transfer p={flip}, cue={cue}',[0,1]*4,flip,cue)
    print('Exact generic posterior equivalence checked on every history prefix.')
    # Negative control: two independent memory routes cannot be distinguished from passive reads.
    assert kernel(0,None)==kernel(1,None)
    for reset in [None,0,1]:
        assert kernel(0,reset)==kernel(1,None if reset is None else 1-reset)
    print('Passive observational equivalence and channel relabeling checks passed.')
