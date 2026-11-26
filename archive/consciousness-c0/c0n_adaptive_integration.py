"""C0n exploratory local integration assay; standard library only.
Two independent triplets, local reward learning, no shared policy or self labels.
Feedback is exogenous task reward; local cue and late read address are supplied.
"""
import random, statistics, math
from itertools import product
from collections import defaultdict
N=2000
COST=.2
# initial triplet: majority bit b, minority at j. latent f=1 means minority is target.
def trial(b,j,f,hold):
    state=[b]*3; state[j]=1-b
    if not hold: state=[int(sum(state)>=2)]*3
    # Later query identifies which location is relevant; never gives its value.
    address=j if f else (j+1)%3
    target=b^f
    return int(state[address]==target)-COST*hold

def sample(r,quality):
    b=r.randrange(2); j=r.randrange(3); f=r.randrange(2)
    cue=f if r.random()<quality else 1-f
    return b,j,f,cue

def train(seed,quality,steps,initial=None):
    r=random.Random(seed)
    # Each triplet uses independent local tables, same generic bandit algorithm.
    tables=[defaultdict(lambda:[0.,0]) for _ in range(2)] if initial is None else initial
    for _ in range(steps):
        for tab in tables:
            b,j,f,c=sample(r,quality); a=r.randrange(2)
            reward=trial(b,j,f,a)
            cell=tab[c,a]; cell[0]+=reward; cell[1]+=1
    return tables

def policy(tab,c):
    def mean(a):
        s,n=tab[c,a]; return s/n if n else .5
    return int(mean(1)>mean(0))

def exact(policy_fn,q):
    util=acc=holdrate=0.
    for b,j,f,c in product(range(2),range(3),range(2),range(2)):
        p=(q if c==f else 1-q)/12
        a=policy_fn(c); reward=trial(b,j,f,a)
        util+=p*reward; acc+=p*(reward+COST*a); holdrate+=p*a
    return util,acc,holdrate

def summarize(vals):
    m=statistics.mean(vals); se=statistics.stdev(vals)/math.sqrt(len(vals))
    return f'{m:.6f} [{m-1.96*se:.6f}, {m+1.96*se:.6f}]'

def main():
    for b,j,f in product(range(2),range(3),range(2)):
        assert abs(trial(b,j,f,1)-.8)<1e-12
        assert trial(b,j,f,0)==1-f
    print('C0n exploratory; 2000 seeds; 2 local triplets per seed; 128 training events per triplet; exact held-out expectations. CI across seed means only.')
    for q in (.9,.5,.1):
        print(f'quality={q} trained/test matched')
        for name,pol in [('integrate',lambda c:0),('hold',lambda c:1),('oracle_cue',lambda c:int((q if c else 1-q)>.2))]:
            print(name,exact(pol,q))
        vals=[]
        for s in range(N):
            tabs=train(s,q,128)
            results=[exact(lambda c:policy(t,c),q) for t in tabs]
            vals.append([sum(x[i] for x in results)/2 for i in range(3)])
        print('learned utility, accuracy, hold rate:',*[summarize([x[i] for x in vals]) for i in range(3)])
    print('cue reversal: training quality=.9, testing quality=.1; additional training retains old counts')
    for k in (0,128,512):
        vals=[]
        for s in range(N):
            tabs=train(s,.9,128)
            if k: tabs=train(s+100000,.1,k,tabs)
            vals.append(sum(exact(lambda c:policy(t,c),.1)[0] for t in tabs)/2)
        print(k,summarize(vals))
    print('Matched generic contextual bandit is the exact same algorithm; no architectural advantage tested.')
if __name__=='__main__':main()
