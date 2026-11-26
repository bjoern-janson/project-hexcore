"""Exploratory finite closure audit, not a consciousness assay.
Boolean formula trees, constants and variables free; binary gates cost one.
Enumerates minimum formula size by dynamic programming over semantic tables.
All sixteen possible two-input truth tables serve as fully observed histories.
"""
from itertools import product
from collections import Counter

def table(n,f):
    return sum(int(f(*x))<<i for i,x in enumerate(product((0,1),repeat=n)))

def closure(n, gates, maxcost):
    mask=(1<<(1<<n))-1
    leaves={0,mask}|{table(n,lambda *x,i=i:x[i]) for i in range(n)}
    levels=[leaves]; dist={v:0 for v in leaves}
    def apply(g,a,b):
        parts=(~a&~b,~a&b,a&~b,a&b)
        return mask & sum(parts[i]&mask for i in range(4) if (g>>i)&1)
    for k in range(1,maxcost+1):
        new=set()
        for g,w in gates:
            for i in range(k-w+1):
                j=k-w-i
                for a in levels[i]:
                    for b in levels[j]:new.add(apply(g,a,b))
        new-=dist.keys();levels.append(new);dist.update({v:k for v in new})
    return dist

def main():
    nand=7; B=2
    old2=closure(2,[(nand,1)],20)
    old3=closure(3,[(nand,1)],20)
    assert len(old2)==16 and len(old3)==256
    old={t for t,c in old3.items() if c<=B}
    print('Budget:',B,'gate invocations; old NAND-only closure:',len(old),'of 256')
    print('history truth table | NAND formula cost | staged size | apparent gain | expanded-cost gain | replay-shadow gain')
    gains=[]
    for h in range(16):
        # Exact history is four labelled examples, fitting all truth tables.
        history=[(x,y,(h>>i)&1) for i,(x,y) in enumerate(product((0,1),repeat=2))]
        fits=[g for g in range(16) if all((g>>(2*x+y))&1==z for x,y,z in history)]
        assert fits==[h]
        g=fits[0]; w=old2[g]
        # Zero-cost functions are constants/projections, already available.
        staged=set(closure(3,[(nand,1),(g,1)],B))
        # At B=2 a gate with NAND cost >=2 can only be applied to leaves
        # if charged its full cost; hence duplication of non-leaf arguments
        # cannot affect this particular equality. Do not generalize weighted
        # gate costs to arbitrary nested formula inlining.
        expanded=set(closure(3,[(nand,1)]+([(g,w)] if w else []),B))
        # Shadow is permitted the same generic compiler and history; no persistent install needed.
        replay=set(closure(3,[(nand,1),(fits[0],1)],B))
        assert expanded==old and replay==staged
        gains.append(len(staged-old))
        print(f'{g:04b} {w:2} {len(staged):3} {len(staged-old):3} {len(expanded-old):3} {len(staged-replay):3}')
    print('Histories with apparent gain:',sum(x>0 for x in gains),'/16; total gain across histories:',sum(gains))
    xor=6; parity=table(3,lambda x,y,z:x^y^z)
    d=closure(3,[(nand,1),(xor,1)],2)
    print('Three-bit parity: old minimum formula cost',old3[parity],'; installed XOR cost',d[parity],'; exact inlining cost of XOR(XOR(x,y),z)',20)
    print('All budget-2 expanded-cost and same-evidence replay-shadow equality checks passed.')
if __name__=='__main__':main()
