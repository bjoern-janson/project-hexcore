import itertools, json, time, ast
from pathlib import Path

def variables(n):
    return [(sum(((s>>i)&1)<<s for s in range(1<<n)),f'x{i}') for i in range(n)]
def apply(op,a,b,mask):
    # truth table of an arbitrary binary primitive, index 2*a+b
    return ((~a&~b if op&1 else 0)|(~a&b if op&2 else 0)|(a&~b if op&4 else 0)|(a&b if op&8 else 0))&mask
OPS={8:'AND',14:'OR',7:'NAND'}
def search(n,ops,target,budget):
    mask=(1<<(1<<n))-1
    known=dict(variables(n)); known.update({0:'0',mask:'1'})
    levels=[list(known)]; count=0
    if target in known:return dict(found=True,attempts=0,expression=known[target],depth=0,states=len(known))
    while levels[-1]:
        prev=levels[-1]; old=list(known); new=[]; depth=len(levels)
        # enumerate pairs with at least one operand from most recent layer
        for a in prev:
            for b in old:
                for op,name in ops.items():
                    for u,v in ((a,b),) if op in (0,1,6,7,8,9,14,15) else ((a,b),(b,a)):
                        if count>=budget:return dict(found=False,attempts=count,states=len(known),depth=depth)
                        count+=1; c=apply(op,u,v,mask)
                        if c in known:continue
                        known[c]=f'{name}({known[u]},{known[v]})';new.append(c)
                        if c==target:return dict(found=True,attempts=count,expression=known[c],depth=depth,states=len(known))
        levels.append(new)
    return dict(found=False,attempts=count,states=len(known),depth=len(levels)-1,closed=True)
def eval_expr(expr, inputs, ops):
    def ev(node):
        if isinstance(node,ast.Constant):return node.value
        if isinstance(node,ast.Name):return inputs[int(node.id[1:])]
        a,b=map(ev,node.args);return (ops[node.func.id]>>(2*a+b))&1
    return ev(ast.parse(expr,mode="eval").body)
def parity(n):return sum((s.bit_count()%2)<<s for s in range(1<<n))
def main():
    # Initial language exhaustive closure over two inputs.
    closure=search(2,{8:'AND',14:'OR'},parity(2),100000)
    # Generic substrate: enumerate all 16 two-input truth tables in numeric order;
    # select first extension enabling the example target, using a fixed budget per candidate.
    probes=[]
    for op in range(16):
        if op in (8,14):continue
        r=search(2,{8:'AND',14:'OR',op:f'P{op}'},parity(2),10000)
        probes.append({'primitive':op,**r})
        # choose first successful primitive, no target-specific ordering
        if r['found']:break
    chosen=probes[-1]['primitive']; base={8:'AND',14:'OR',chosen:f'P{chosen}'}
    train=probes[-1]; learned_op=0
    # Convert demonstrated two-variable semantic function into reusable macro.
    # x0 is low input bit, x1 high; parity symmetric.
    for a,b in itertools.product(range(2),repeat=2):
        learned_op|=eval_expr(train["expression"],[a,b],{v:k for k,v in base.items()})<<(2*a+b)
    assert learned_op==6
    traincost=sum(p['attempts'] for p in probes)
    budget=100000
    # baseline also receives the discovered substrate, and same total budget.
    tests=[]
    for n in range(3,7):
        r=search(n,base,parity(n),budget)
        m=search(n,{**base,learned_op:'M'},parity(n),max(0,budget-traincost))
        # arbitrary extra primitive control (not chosen by target), XNOR also parity-equivalent
        control=search(n,{**base,11:'P11'},parity(n),max(0,budget-traincost))
        for res, opmap in [(r,base),(m,{**base,learned_op:"M"}),(control,{**base,11:"P11"})]:
            if res["found"]:
                # Independent evaluator checks every input, with macro expanded through learned truth table.
                res["verified"]=all(eval_expr(res["expression"],bits,{v:k for k,v in opmap.items()})==sum(bits)%2 for bits in itertools.product(range(2),repeat=n))
                assert res["verified"]
        tests.append(dict(n=n,baseline=r,macro=m,control=control))
    result=dict(closure=closure,probes=probes,chosen=chosen,traincost=traincost,budget=budget,tests=tests)
    Path(__file__).with_name('sealed_world_results.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
