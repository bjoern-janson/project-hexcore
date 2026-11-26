"""Exact universal-decodability frontier for 12 independent bits, four-bit memory.
An anchor node denotes constant zero. Edges (0,i) are single-bit queries.
Each connected component of size m requires m-1 independent parity bits.
The argument applies even to nonlinear deterministic encoders with <=16 states.
"""
from math import comb
from fractions import Fraction
import json

def partitions(n, ceiling=None):
    if not n:
        yield (); return
    for s in range(min(n, ceiling or n), 1, -1):
        for tail in partitions(n-s, s): yield (s,)+tail
    yield ()  # remaining vertices are singleton components

frontier={}
for s in range(5):
    scores=[]
    for other in partitions(12-s):
        if s+sum(m-1 for m in other)<=4:
            scores.append(comb(s,2)+sum(comb(m,2) for m in other))
    frontier[s]=max(scores)
assert frontier=={0:10,1:6,2:4,3:4,4:6}
# Uniform unknown query type, randomized encoder independent of observed bit values.
# Raw bits: (1/3, 1/11); relational bits: (0, 5/33).
t=Fraction(5,13)
single=t/3
pair=t*Fraction(1,11)+(1-t)*Fraction(5,33)
assert single==pair==Fraction(5,39)
print('frontier',frontier,'switch',Fraction(2,13),'minimax raw mixture',t,'worst-case',single,float(single))
# Monte Carlo test with random channel choices and independent uniform requests.
import numpy as np
r=np.random.default_rng(17); n=200000
raw=r.random(n)<float(t)
# By exchangeability can select first 4/5 indices, and uniformly sample requests.
q1=r.integers(12,size=n); q2=np.array([(i,j) for i in range(12) for j in range(i+1,12)])[r.integers(66,size=n)]
a=(raw & (q1<4)).mean(); b=np.where(raw,(q2<4).all(1),(q2<5).all(1)).mean()
print('Monte Carlo',a,b)
open('/mnt/data/representation_frontier_results.json','w').write(json.dumps({'frontier':frontier,'switch':str(Fraction(2,13)),'raw_probability':str(t),'worst_case':str(single),'simulation_single':a,'simulation_pair':b},indent=2))
