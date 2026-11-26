"""C0m exploratory exact finite-state assay. No learning or consciousness claim."""
from fractions import Fraction as F
from itertools import product, combinations
from collections import defaultdict
from math import comb

STATES=list(product((0,1),repeat=6))
MESSAGES=list(product((0,1),repeat=2))
def majority(xs): return int(sum(xs)*2>len(xs))
def encode(m): return (m[0],)*3+(m[1],)*3
def decode(s): return (majority(s[:3]),majority(s[3:]))
def repair(s): return encode(decode(s))
def hold(s): return s
def code(m): return (m[0],)*2+(m[1],)*2+(m[0]^m[1],)*2
CODE={m:code(m) for m in MESSAGES}
def nearest(s):
    d={m:sum(a!=b for a,b in zip(s,c)) for m,c in CODE.items()}
    best=min(d.values()); return [m for m in MESSAGES if d[m]==best]
def masks(kind):
    if kind=='single': return [(tuple(int(i==j) for i in range(6)),F(1,6)) for j in range(6)]
    if kind=='double': return [(tuple(int(i in js) for i in range(6)),F(1,15)) for js in combinations(range(6),2)]
    p=F(1,10)
    return [(s,p**sum(s)*(1-p)**(6-sum(s))) for s in STATES]
def flip(s,b): return tuple(x^y for x,y in zip(s,b))
# FSM uses identical six-bit state and transition lookup, not a new mechanism.
LUT={s:repair(s) for s in STATES}
# Compare exact memory and mean accuracy for three equally likely queries x,y,xor.
def scores(m,guess):
    return (F(m==guess),F((m[0]==guess[0])+(m[1]==guess[1])+((m[0]^m[1])==(guess[0]^guess[1])),3))
def evaluate(kind,steps,mode):
    enc=code if mode.startswith('code') else encode
    noise=masks(kind); totals=[F(0),F(0)]
    for m in MESSAGES:
        dist={enc(m):F(1)}
        for _ in range(steps):
            nd=defaultdict(F)
            for s,p in dist.items():
                for b,q in noise:
                    t=flip(s,b)
                    if mode=='recurrent': outcomes=[repair(t)]
                    elif mode=='fsm': outcomes=[LUT[t]]
                    elif mode=='code_repair': outcomes=[code(g) for g in nearest(t)]
                    else: outcomes=[t]
                    for o in outcomes: nd[o]+=p*q/len(outcomes)
            assert sum(nd.values())==1
            dist=nd
        for s,p in dist.items():
            guesses=nearest(s) if mode.startswith('code') else [decode(s)]
            for g in guesses:
                for i,v in enumerate(scores(m,g)): totals[i]+=p*v/(4*len(guesses))
    return totals

def main():
    assert all(repair(s)==LUT[s] for s in STATES)
    assert all(decode(repair(s))==decode(s) for s in STATES)
    assert all(repair(repair(s))==repair(s) for s in STATES)
    assert all(repair(flip(encode(m),b))==encode(m) for m in MESSAGES for b,_ in masks('single'))
    print('C0m exact enumeration; 64 states, 4 messages, no learned weights; uniform tie breaking for code baseline.')
    print('kind,steps,model,exact_message_pct,mean_query_pct')
    for kind in ('single','double','iid10'):
        for n in (1,2,4,8):
            vals={mode:evaluate(kind,n,mode) for mode in ('recurrent','hold','fsm','code_repair','code_hold')}
            assert vals['recurrent']==vals['fsm']
            for mode,(a,b) in vals.items(): print(f'{kind},{n},{mode},{float(a)*100:.6f},{float(b)*100:.6f}')
    print('All probability conservation, single-fault recovery, idempotence, and FSM equivalence checks passed.')
if __name__=='__main__': main()
