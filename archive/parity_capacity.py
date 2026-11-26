import numpy as np
from itertools import combinations
# For uniform independent bits, a linear memory of rank <=4 identifies a pair parity iff its vector lies in row span.
# Exhaustively enumerate set partitions with sum(block_size-1)<=4, since identifiable pair parities form equivalence classes.
def partitions(n, blocks=()):
 if n==0:
  yield blocks;return
 for s in range(min(n,5),1,-1):
  if not blocks or s<=blocks[-1]:
   if sum(x-1 for x in blocks)+s-1<=4: yield from partitions(n-s,blocks+(s,))
 yield blocks
valid=set(partitions(12)); best=max(valid,key=lambda b:sum(x*(x-1)//2 for x in b))
print('best',best,'covered',sum(x*(x-1)//2 for x in best),'total',66)
# Explicit encoding for five channels: store parity with anchor, reconstruct any of ten pairs.
r=np.random.default_rng(42); bits=r.integers(0,2,(100000,12)); q=np.array(list(combinations(range(12),2))); requests=q[r.integers(len(q),size=len(bits))]; mask=(requests<5).all(1); mem=bits[:,1:5]^bits[:,[0]]; decoded=np.column_stack([np.zeros(len(bits),dtype=int),mem]); rows=np.where(mask)[0]; pred=decoded[rows,requests[rows,0]]^decoded[rows,requests[rows,1]]; truth=bits[rows,requests[rows,0]]^bits[rows,requests[rows,1]]; print('coverage',mask.mean(),'conditional exact',np.mean(pred==truth))
