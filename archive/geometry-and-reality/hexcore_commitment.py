"""Finite commitment/repair counterexample. Python 3.10+, stdlib only.
All costs in ideal action/query units, not machine time. No training or claimed AI.
"""
from functools import lru_cache
from math import inf, isinf
from pathlib import Path
import json


def ceil_log2(n):
    return (n-1).bit_length() if n>1 else 0


def oracle(n, pair, repair=inf):
    """Exact policy evaluation after mode selection. World labels never change.
    A locked mode maps the second member of pair to the first for every readout.
    The only changing action, repair, costs r and unlocks all thresholds forever.
    Return worst cost and SUM of costs over a uniform compatible world set.
    These are separately optimized objectives.
    """
    mapped=[pair[0] if pair and x==pair[1] else x for x in range(n)]
    masks=tuple(set(sum(1<<x for x in range(n) if mapped[x]<t)
                    for t in range(1,n)))
    # Identity thresholds achieve optimal prefix depth on any ordered subset;
    # uniform expected binary-query total for h leaves in an optimal tree.
    def unlocked(h):
        k=ceil_log2(h)
        return k, h*(k+1)-(1<<k) if h else 0
    @lru_cache(None)
    def solve(s):
        h=s.bit_count()
        if h<=1: return 0,0
        u,v=unlocked(h)
        worst=repair+u; total=repair*h+v
        for q in masks:
            a,b=s&q,s&~q
            if not a or not b: continue
            wa,ea=solve(a); wb,eb=solve(b)
            worst=min(worst,1+max(wa,wb))
            total=min(total,h+ea+eb)
        return worst,total
    return solve


def mode_oracles(n, good=False, repair=inf):
    assert n%2==0 and n>=4
    return [oracle(n,None if good and i==0 else (i,i+1),repair)
            for i in range(0,n,2)]


def initial(s, modes):
    h=s.bit_count()
    if h<=1:return 0,0
    rows=[f(s) for f in modes]
    return 1+min(x[0] for x in rows), h+min(x[1] for x in rows)


def proper_subset_audit(n, repair):
    good,bad=mode_oracles(n,True,repair),mode_oracles(n,False,repair)
    full=(1<<n)-1
    for s in range(1,full):
        h=s.bit_count()
        k=ceil_log2(h)
        target=(1+k,h*(k+2)-(1<<k)) if h>1 else (0,0)
        a,b=initial(s,good),initial(s,bad)
        assert a==b==target,(n,repair,s,a,b,target)
    return full-1


def verify_policies(n,r):
    """Test explicit optimal expected and minimax policies, one run per world.
    We commit to pair (0,1), then threshold-query. The mean-optimal policy
    performs a balanced search, unlocking only when the candidate set is {0,1}.
    The worst-optimal policy isolates that pair immediately, or for free repair
    unlocks immediately. This is independent of the DP recurrence.
    """
    k=ceil_log2(n)
    def balanced(x):
        lo,hi=0,n; cost=1; repaired=False
        while hi-lo>1:
            if lo==0 and hi==2 and not repaired:
                cost+=r; repaired=True
            t=(lo+hi)//2
            observed=x if repaired or x!=1 else 0
            cost+=1
            if observed<t:hi=t
            else:lo=t
        assert lo==x
        return cost
    def minimax(x):
        cost=1
        if r==0:
            lo,hi=0,n
        else:
            # First threshold at 2. Collapsed pair is wholly on left.
            cost+=1
            if x<2:lo,hi=0,2;cost+=r
            else:lo,hi=2,n
        while hi-lo>1:
            t=(lo+hi)//2;cost+=1
            if x<t:hi=t
            else:lo=t
        assert lo==x
        return cost
    a=[balanced(x) for x in range(n)]
    b=[minimax(x) for x in range(n)]
    assert sum(a)==n*(k+1)+2*r
    assert max(b)==(1+k if r==0 else 1+max(k+1,r+2))
    return n


def run():
    audits=[];full_rows=[];policies=0
    for n in [4,8,12]:
        # No repair in audit of all proper subsets, plus two finite repair
        # settings for the smaller sizes. All tests optimize over every mode.
        for r in ([inf,0,1,5] if n<=8 else [inf]):
            count=proper_subset_audit(n,r)
            audits.append(dict(n=n,repair=None if isinf(r) else r,proper_subsets=count))
    for k in range(2,6):
        n=1<<k;s=(1<<n)-1
        for r in [inf,*range(0,2*k+3)]:
            a=initial(s,mode_oracles(n,True,r)); b=initial(s,mode_oracles(n,False,r))
            assert a==(k+1,n*(k+1)),(n,r,a)
            expected=(inf,inf) if isinf(r) else (1+k if r==0 else 1+max(k+1,r+2),n*(k+1)+2*r)
            assert b==expected,(n,r,b,expected)
            full_rows.append(dict(n=n,r=None if isinf(r) else r,good_worst=a[0],bad_worst=None if isinf(b[0]) else b[0],good_mean=a[1]/n,bad_mean=None if isinf(b[1]) else b[1]/n))
    for k in range(2,17):
        n=1<<k
        for r in [0,1,k-1,k,2*k,1<<(k//2)]:
            policies+=verify_policies(n,r)
    # No-repair accuracy: complete quotient readout, deterministic guess for
    # the one doubleton. Count exact distinguishable equivalence classes.
    for n in [4,8,32,128,1024,65536]:
        codes={0 if x==1 else x for x in range(n)}
        assert len(codes)==n-1
    result=dict(scope='deterministic finite world; known candidate subset; initial silent unit-cost commitment; ordered threshold queries cost one; optional repair cost r; null means impossible/unavailable',proper_subset_audits=audits,proper_subset_checks=sum(a['proper_subsets'] for a in audits),full_exact_dp=full_rows,full_cases=len(full_rows),explicit_policy_worlds_per_policy=policies)
    Path(__file__).with_name('hexcore_commitment_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print('proper subset comparisons',result['proper_subset_checks'],'full cases',len(full_rows),'world runs per explicit policy',policies)
    print('all assertions passed')

if __name__=='__main__':run()
