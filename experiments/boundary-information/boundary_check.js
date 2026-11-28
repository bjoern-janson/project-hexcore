"use strict";
function verifyBoundary(){
 const out=[];
 for(let m=3;m<=12;m++){
  const N=2**m;
  const transform=x=>{
    const last=(x>>(m-1))&1;
    let y=0;
    for(let i=0;i<m-1;i++)y|=(((x>>i)&1)^last)<<i;
    y|=(((x&1)^((x>>1)&1))^last)<<(m-1);
    return y;
  };
  const ys=Array.from({length:N},(_,i)=>transform(i));
  if(new Set(ys).size!==N)throw Error("not bijective");
  const counts=Array.from({length:2*m},()=>Array.from({length:2*m},()=>[0,0,0,0]));
  for(let x=0;x<N;x++){
   const v=x|(ys[x]<<m);
   for(let i=0;i<2*m;i++)for(let j=i+1;j<2*m;j++){
    counts[i][j][2*((v>>i)&1)+((v>>j)&1)]++;
   }
  }
  for(let i=0;i<2*m;i++)for(let j=i+1;j<2*m;j++)if(counts[i][j].some(c=>c!==N/4))throw Error("pairwise test failed");
  const cases=[];
  for(let b=0;b<=m;b++){
   const K=2**b,g=N/K;let good=0,total=0;
   const left=Array(N).fill(0),right=Array(N).fill(0);
   for(let z=0;z<K;z++)for(let i=z*g;i<(z+1)*g;i++)for(let j=z*g;j<(z+1)*g;j++){
    total++;left[i]++;right[ys[j]]++;if(ys[i]===ys[j])good++;
   }
   if(good!==N || total!==N*g || left.some(c=>c!==g)||right.some(c=>c!==g))throw Error("factorization check failed");
   cases.push({boundary_bits:b,boundary_states:K,match_probability:good/total,total_variation:1-good/total});
  }
  out.push({m,worlds:N,pairwise_checks:(2*m)*(2*m-1)/2,exact_joint_rank:N,independent_joint_rank:1,cases});
 }
 return out;
}
console.log(JSON.stringify(verifyBoundary(), null, 2));
