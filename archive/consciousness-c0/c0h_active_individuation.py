"""C0h: exact finite-horizon value of independently controlled probes.
Calibration, not preregistered confirmation. No feedback in terminal deployment batch.
"""
from functools import lru_cache
from fractions import Fraction as F
from itertools import product
E=F(1,10)
# During diagnostics B=0, A either synchronizes (0) or opposes (1).
# Both output bits are observed with independent flip noise.
def likelihood(a,x,m):
    expected=(a,0) if m==0 else (0,a)
    return (1-E if x[0]==expected[0] else E)*(1-E if x[1]==expected[1] else E)
def outcomes(p,a):
    for x in product(range(2),repeat=2):
        l0,l1=likelihood(a,x,0),likelihood(a,x,1)
        w=(1-p)*l0+p*l1
        yield w,p*l1/w
# At deployment, B is independent fair and hidden. Opposing goals.
# No observations returned until all H choices are committed.
def terminal(p,H): return H*(F(1,2)+F(2,5)*(max(p,1-p)-F(1,2)))
def solve(H,c,T=3,allow=True):
    @lru_cache(None)
    def V(p,t):
        if not t: return terminal(p,H),F(0),F(0)
        options=[]
        for a in range(2 if allow else 1):
            branches=[(w,V(q,t-1)) for w,q in outcomes(p,a)]
            options.append((sum(w*v[0] for w,v in branches)-c*a, a+sum(w*v[1] for w,v in branches),F(a)))
        return max(options,key=lambda v:(v[0],-v[1]))
    return V(F(1,2),T)
def fixed(H,c,k):
    @lru_cache(None)
    def V(p,t):
        if not t:return terminal(p,H)
        return sum(w*V(q,t-1) for w,q in outcomes(p,1))-c
    return V(F(1,2),k)
def main():
    print('Exact rational enumeration, 3 diagnostic slots, 10% independent bit noise, equal prior.')
    print('H cost optimal_net expected_probes first_probe never best_fixed_k best_fixed_net always3_net')
    for H in (1,2,4,8,16):
        for c in map(F,('0.05','0.15','0.30','0.60')):
            v,n,a=solve(H,c); vals=[fixed(H,c,k) for k in range(4)]; k=max(range(4),key=lambda k:vals[k]);
            assert v>=max(vals)
            print(f'{H:2} {float(c):.2f} {float(v):.6f} {float(n):.6f} {int(a)} {H/2:.6f} {k} {float(vals[k]):.6f} {float(vals[3]):.6f}')
    H,c=4,F('0.15');v,n,a=solve(H,c)
    print('Illustrative H=4,c=.15: gross reward',float(v+c*n),'net',float(v),'expected probes',float(n))
    for x in product(range(2),repeat=2):
        l0,l1=likelihood(1,x,0),likelihood(1,x,1);print('first outcome',x,'prob',float((l0+l1)/2),'posterior m=1',float(l1/(l0+l1)))
    print('Locked synchronization: all posterior updates remain at prior; net',float(solve(4,F('.15'),allow=False)[0]))
    print('Generic Bayes control is the same Bellman problem under route relabeling; equality by construction, not independent empirical replication.')
if __name__=='__main__':main()
