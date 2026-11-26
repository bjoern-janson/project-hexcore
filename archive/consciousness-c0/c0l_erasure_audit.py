"""Exact audit of C0k; standard library only. No consciousness claim."""
from fractions import Fraction as F
from collections import defaultdict
from c0k_embedded_belief import evaluate, choices, guess
H=F(1,2)
# Full-history oracle: sees the same probe outcomes, but retains history.
# Matched random reset uses the mutable arm's unconditional reset rate at each step.
def run(n, mode, rates=None):
    d=defaultdict(F)
    for r in (0,1):
        for s in (0,1):
            d[r,F(3) if s else F(1,3)]+=H*(F(3,4) if r==s else F(1,4))
    resets=[]; records=[]
    for t in range(n+1):
        acc=sum(w*(H if guess(o) is None else int(guess(o)==r)) for (r,o),w in d.items())
        # Bayes-optimal readout of the retained scalar, with no hidden trial history.
        groups=defaultdict(lambda:[F(0),F(0)])
        for (r,o),w in d.items(): groups[o][r]+=w
        calibrated=sum(max(v) for v in groups.values())
        records.append((acc,calibrated))
        if t==n: break
        nxt=defaultdict(F); er=F(0)
        for (r,o),w in d.items():
            for slot,q in choices(o,'preserve'):
                reset=F(int(slot==r)) if mode=='physical' else rates[t] if mode=='random' else F(0)
                er+=w*q*reset
                p=H if slot==r else F(9,10)
                p0=H if slot==0 else F(9,10); p1=H if slot==1 else F(9,10)
                for success,prob in ((True,p),(False,1-p)):
                    lr=p1/p0 if success else (1-p1)/(1-p0)
                    for erased,e in ((True,reset),(False,1-reset)):
                        if e: nxt[r,(F(1) if erased else o)*lr]+=w*q*prob*e
        assert sum(nxt.values())==1
        d=nxt; resets.append(er)
    return records,resets

def main():
    n=8
    phys,rates=run(n,'physical'); rand,rr=run(n,'random',rates); prot,_=run(n,'protected')
    for t in range(n+1):
        assert phys[t][0]==evaluate('preserve',t)[0]
        assert prot[t][0]==evaluate('preserve',t,protected=True)[0]
        assert prot[t][0]==prot[t][1]
    assert rates==rr
    print('Exact enumeration; rates matched per step, not conditional on hidden state.')
    print('n physical random protected physical_calibrated random_calibrated')
    for t in range(n+1): print(t,*(f'{float(v):.9f}' for v in (phys[t][0],rand[t][0],prot[t][0],phys[t][1],rand[t][1])))
    print('expected resets',float(sum(rates)))
    print('reset rates',*[round(float(x),8) for x in rates])
    # An observable erasure is a perfect route signal in the supplied architecture.
    print('If reset event is observable, route is identified exactly after one probe: reset iff slot == route.')
    print('A protected observer given the same reset flag has the same information; no need to erase.')
    print('PASS: reproduced prior exact results; mass conservation; matched reset rates; protected posterior calibration.')
if __name__=='__main__': main()
