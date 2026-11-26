"""C0k: exact finite assay. No third-party dependencies.
A fixed interpreter reads/writes its belief ONLY through hidden operative slot.
The evaluator enumerates latent route, initial signal and probe outcomes.
The route is not exposed to the policy. Probe operation physically resets a slot.
"""
from fractions import Fraction as F
from collections import defaultdict

HALF=F(1,2)
def guess(odds):
    return 1 if odds>1 else 0 if odds<1 else None

def choices(odds,policy):
    g=guess(odds)
    if policy=='stop': return [(None,F(1))]
    if policy=='random' or g is None: return [(0,HALF),(1,HALF)]
    if policy=='preserve': return [(1-g,F(1))]
    if policy=='disrupt': return [(g,F(1))]
    raise ValueError(policy)

class Machine:
    def __init__(self,route,odds=F(1)):
        self._route=route
        self.slots=[odds,odds]
    def read(self): return self.slots[self._route]
    def write(self,value): self.slots[self._route]=value
    def probe(self,slot,success,protected=False):
        if not protected: self.slots[slot]=F(1)
        # Likelihood of success given an active vs inactive reset.
        p0=HALF if slot==0 else F(9,10)
        p1=HALF if slot==1 else F(9,10)
        if not success: p0,p1=1-p0,1-p1
        self.write(self.read()*p1/p0)
    def decision(self): return guess(self.read())

def evaluate(policy,n,initial=F(3,4),protected=False):
    # Evaluator-only latent state. Decoy slot cannot affect read or write.
    states=defaultdict(F)
    for route in (0,1):
        for signal in (0,1):
            odds=initial/(1-initial) if signal else (1-initial)/initial
            states[route,odds]+=HALF*(initial if signal==route else 1-initial)
    erasures=F(0)
    for _ in range(n if policy!='stop' else 0):
        nxt=defaultdict(F)
        for (route,odds),w in states.items():
            for slot,q in choices(odds,policy):
                if slot==route and not protected: erasures+=w*q
                p=HALF if slot==route else F(9,10)
                for success,prob in [(True,p),(False,1-p)]:
                    m=Machine(route,odds); m.probe(slot,success,protected)
                    nxt[route,m.read()]+=w*q*prob
        states=nxt
        assert sum(states.values())==1
    correct=sum(w*(HALF if guess(o) is None else int(guess(o)==r)) for (r,o),w in states.items())
    return correct, HALF+F(2,5)*correct, erasures

def main():
    print('Exact expected results; final task accuracy = .5 + .4 * correct protection choice')
    print('Initial evidence accuracy 0.75; probe success P=.5 active / .9 inactive; reset erases operative odds to 1 before update.')
    print('n policy protected attribution task_accuracy expected_erasures')
    for n in (0,1,2,4,8):
        for policy,protected in [('stop',False),('random',False),('preserve',False),('disrupt',False),('preserve',True),('random',True)]:
            vals=evaluate(policy,n,protected=protected)
            print(n,policy,protected,*(f'{float(v):.9f}' for v in vals))
    print('\nNet utility over four tasks, cost .02/probe (predeclared illustrative parameters)')
    for n in (0,1,2,4,8):
        for policy in ('random','preserve','disrupt'):
            _,acc,_=evaluate(policy,n)
            print(n,policy,float(4*acc-F(1,50)*n))
    # Actual memory reset and no independent posterior cache.
    m=Machine(0,F(3));m.probe(0,True);assert m.read()==F(9,5)
    m=Machine(0,F(3));m.probe(1,True);assert m.read()==F(5,3)
    # Relabel invariance of likelihood update, including destructive reset.
    for r in (0,1):
        for slot in (0,1):
            for s in (False,True):
                m=Machine(r,F(3)); k=Machine(1-r,F(1,3))
                m.probe(slot,s);k.probe(1-slot,s);assert m.read()*k.read()==1
    print('PASS: actual slot reset, nonoperative slot preservation, label symmetry, probability conservation')
if __name__=='__main__': main()
