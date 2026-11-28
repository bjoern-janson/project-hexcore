import json,collections,itertools,statistics
from pathlib import Path
from law_discovery import enumerate_laws,worlds,lookup,D,TEST
ROOT=Path(__file__).parent
arr,desc,w,meta=enumerate_laws()
classes=collections.defaultdict(list)
for i,p in enumerate(arr):classes[tuple(map(int,p[2:15]))].append(i)
counts=collections.Counter(map(len,classes.values()))
max_key,max_group=max(classes.items(),key=lambda kv:len(kv[1]))
assert sum(k*v for k,v in counts.items())==len(arr)
assert sum(counts.values())==len(classes)
# One full-profile identifier per transcript class is optimal under the uniform prior.
assert all(len({tuple(map(int,arr[i,15:])) for i in g})==len(g) for g in classes.values())
worlds_=worlds();runs=json.loads((ROOT/'results.json').read_text())['worlds'];audit={}
for name,t in worlds_.items():
 g=classes.get(tuple(t[2:15]),[])
 a=runs[name]['active'];p=runs[name]['passive'];audit[name]={'complete_transcript_class_size':len(g),'complete_transcript_compatible_laws':[desc[i] for i in g],'active_observations_class_size':a['compatible_test_profiles'],'active_query_sizes':[q['n'] for q in a['queries']],'active_comparisons':a['comparisons'],'active_entropy_visits':a['entropy_visits'],'passive_mean_comparisons':statistics.mean(q['comparisons'] for q in p),'active_fit_seconds':a['seconds'],'passive_mean_fit_seconds':statistics.mean(q['seconds'] for q in p),'active_full_tree_success':a['trees'],'passive_mean_tree_success':statistics.mean(q['trees'] for q in p),'fraction_full_tree_success':runs[name]['alternatives']['fraction']['trees'],'active_truth_equal_n17':a['function_equal_n17']}
ali=['thirds','alias_halves','alias_quarters'];pairs=[]
for a,b in itertools.combinations(ali,2):
 x,y=worlds_[a],worlds_[b];equal_train=all(lookup(x,n)==lookup(y,n) for n in range(2,17));different_test=sum(lookup(x,n)!=lookup(y,n) for n in TEST);assert equal_train and different_test==len(TEST);pairs.append({'pair':[a,b],'equal_all_training':equal_train,'different_heldout_sizes':different_test})
result={'library_profiles':len(arr),'transcript_classes':len(classes),'class_size_distribution':dict(sorted(counts.items())),'singleton_classes':counts[1],'ambiguous_profiles':len(arr)-counts[1],'largest_class_size':len(max_group),'largest_class_transcript':max_key,'largest_class_example_formulas':[desc[i] for i in max_group[:12]],'uniform_prior_optimal_exact_profile_accuracy':len(classes)/len(arr),'world_audit':audit,'alias_pair_checks':pairs,'alias_uniform_prior_root_accuracy_upper_bound':1/3}
(ROOT/'ambiguity_results.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:v for k,v in result.items() if k not in ('world_audit','class_size_distribution','largest_class_transcript','largest_class_example_formulas')})
for k,v in audit.items():print(k,'all',v['complete_transcript_class_size'],'active',v['active_observations_class_size'],'queries',v['active_query_sizes'],'fit work',v['active_comparisons']+v['active_entropy_visits'],'passive',round(v['passive_mean_comparisons']),'frac trees',v['fraction_full_tree_success'],'n17',v['active_truth_equal_n17'])
