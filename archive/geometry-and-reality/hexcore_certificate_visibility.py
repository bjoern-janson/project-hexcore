"""Exact one-step witness-disclosure assay.
Mode i gives a nonempty set of actions that reach goal; all others self-loop.
A trusted encoder sees the current mode and sends one of k labels before the
controller chooses an action. Mode held fixed through action. Min labels via
exhaustive hitting sets and, independently, all canonical set partitions.
"""
from itertools import combinations, product
from pathlib import Path
import json, math, random

checks=0
def check(b):
    global checks
    checks+=1
    assert b

def hitting(rows,na):
    for k in range(1,na+1):
        for a in combinations(range(na),k):
            mask=sum(1<<x for x in a)
            if all(r&mask for r in rows):return k,a
    raise AssertionError

def partition_min(rows,na):
    # Each block is a label. Every mode in a block must share a good action.
    # Enumerate all set partitions using canonical block labels.
    best=len(rows)
    def rec(i,blocks):
        nonlocal best
        if i==len(rows):best=min(best,len(blocks));return
        if len(blocks)>=best:return
        for j,v in enumerate(blocks):
            common=v&rows[i]
            if common:rec(i+1,blocks[:j]+[common]+blocks[j+1:])
        rec(i+1,blocks+[rows[i]])
    rec(0,[])
    return best

def audit(rows,na):
    k,a=hitting(rows,na)
    check(k==partition_min(rows,na))
    # Construct code and verify all modes, including collision partitions.
    code=[next(j for j,x in enumerate(a) if row&(1<<x)) for row in rows]
    for i,c in enumerate(code):check(bool(rows[i]&(1<<a[c])))
    check((k==1)==bool(__import__('functools').reduce(int.__and__,rows)))
    return k

hist={}
for rows in product(range(1,8),repeat=3):
    k=audit(rows,3);hist[k]=hist.get(k,0)+1
rng=random.Random(8191); random_hist={}
for i in range(1000):
    nm=rng.randint(2,7);na=rng.randint(2,7);rows=tuple(rng.randrange(1,1<<na) for _ in range(nm));k=audit(rows,na);random_hist[k]=random_hist.get(k,0)+1
unique=[]
# For distinct unique correct actions, identity communication cost is exactly
# ceil(log2 m). Above m=7 use the elementary proof, not expensive enumeration.
for m in (2,3,4,5,6,7,8,16,32,64,128,256,1024):
    if m<=7:check(audit(tuple(1<<i for i in range(m)),m)==m)
    unique.append({'modes':m,'minimum_labels':m,'fixed_width_bits':(m-1).bit_length(),'rank':1})
# Atomicity counterexample: full mode report is exact when issued; it is not
# useful for sure reachability if adversary may choose a fresh mode after report.
stale={}
for m in range(2,9):
    # enumerate all disclosed old modes, then every available action. Every
    # action has at least one alternative current mode that makes it fail.
    check(all(any(a!=v for v in range(m)) for old in range(m) for a in range(m)))
    stale[m]={'held_through_action':True,'unrestricted_switch_after_report':False}
out={'exhaustive_3_modes_3_actions':343,'exhaustive_label_histogram':hist,'random_cases':1000,'random_label_histogram':random_hist,'unique_correct_actions':unique,'atomicity_cases':stale,'assertion_evaluations':checks,'failed_assertions':0}
Path(__file__).with_name('hexcore_certificate_visibility_results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
