"""Exploratory C0o. Two local tabular learners, no central trainable state.
Messages: silence or literal private bit; gate sees cue, not bit (no silence code).
Each learner receives same scalar team payoff. Fixed training exploration.
Exact held-out evaluation over all private bits and cues; 200 seeds.
"""
import random, itertools, statistics, math
N=200; TRAIN=4000; COST=.15; ALPHA=.05; EPS=.10

def pick(q,r,train=True):
    if train and r.random()<EPS: return r.randrange(2)
    if q[0]==q[1]: return r.randrange(2) if train else 0
    return int(q[1]>q[0])
class Agent:
    def __init__(self):
        self.g=[[0.,0.] for _ in range(2)]
        self.d=[[[[0.,0.] for _ in range(3)] for _ in range(2)] for _ in range(2)]
    def send(self,c,r,train):return pick(self.g[c],r,train)
    def read(self,c,b,m,r,train):return pick(self.d[c][b][m],r,train)
    def update(self,c,b,m,s,y,reward,mode):
        if mode=='learn': self.g[c][s]+=ALPHA*(reward-self.g[c][s])
        self.d[c][b][m][y]+=ALPHA*(reward-self.d[c][b][m][y])

def run_event(agents,c,b,rev,mode,r,train):
    s=[a.send(c,r,train) if mode=='learn' else int(mode=='always') for a in agents]
    m=[b[1-i]+1 if s[1-i] else 0 for i in range(2)]
    y=[a.read(c,b[i],m[i],r,train) for i,a in enumerate(agents)]
    joint=c^rev
    t=[b[0]^b[1]]*2 if joint else b
    acc=sum(y[i]==t[i] for i in range(2))/2
    reward=acc-COST*sum(s)
    if train:
        for i,a in enumerate(agents):a.update(c,b[i],m[i],s[i],y[i],reward,mode)
    return reward,acc,sum(s)

def evaluate(agents,rev,mode,r):
    rows=[run_event(agents,c,list(b),rev,mode,r,False) for c in range(2) for b in itertools.product(range(2),repeat=2)]
    return tuple(sum(x[i] for x in rows)/len(rows) for i in range(3))

def train(agents,rev,mode,r,n):
    for _ in range(n):run_event(agents,r.randrange(2),[r.randrange(2),r.randrange(2)],rev,mode,r,True)

def main():
    data={k:[] for k in ['learn','always','never','reversal0','reversal500','reversal2000']}
    gates=[]
    for seed in range(N):
        for mode in ['learn','always','never']:
            r=random.Random(seed); agents=[Agent(),Agent()];train(agents,0,mode,r,TRAIN)
            data[mode].append(evaluate(agents,0,mode,r))
            if mode=='learn':
                gates.append(tuple(a.send(c,r,False) for c in range(2) for a in agents))
                data['reversal0'].append(evaluate(agents,1,mode,r))
                train(agents,1,mode,r,500);data['reversal500'].append(evaluate(agents,1,mode,r))
                train(agents,1,mode,r,1500);data['reversal2000'].append(evaluate(agents,1,mode,r))
    print(f'{N} seeds, {TRAIN} training events per arm, cost {COST} per message; shared payoff; exact evaluation of 8 inputs per seed.')
    for k,rows in data.items():print(k,*(f'{statistics.mean(col):.6f}' for col in zip(*rows)))
    print('both send joint and neither local',sum(g==(0,0,1,1) for g in gates), '/',N)
    for k in ['always','never']:
        d=[a[0]-b[0] for a,b in zip(data['learn'],data[k])];m=statistics.mean(d); e=1.96*statistics.stdev(d)/math.sqrt(N);print('paired advantage vs',k,m,(m-e,m+e))
    print('oracle gate policies (local send count, joint send count):')
    for l,j in itertools.product(range(3),repeat=2):print(l,j, (1-COST*l + .5+(.25-COST)*j)/2)
    print('unrestricted silence coding oracle: local no messages, joint send iff bit=1; utility',1-COST/2)
if __name__=='__main__':main()
