'''Descriptive counts for seed 7 (third audit m5, m13, m20): episodes and errors per checkpoint, errors by question type,
never-answered episodes by type. Same population as the primary analysis. Writes docs/seed7_counts.json.'''
import json, gzip, collections
T = (48, 96, 192, 384)
R = [json.loads(l) for l in gzip.open('data/seed7_L.jsonl.gz', 'rt')]
PJ = {(d['idx'], int(d['f'])) for d in (json.loads(l) for l in gzip.open('data/prefix_judge_abs_s7.jsonl.gz', 'rt'))}
A = [r for r in R if r['answered'] and all((r['idx'], t) in PJ for t in T if t < r['final_start'])]
res = dict(recorded=len(R), answered_in_primary=len(A), wrong=sum(1 for r in A if not r['correct']),
           per_checkpoint={str(t): dict(episodes=sum(1 for r in A if t < r['final_start']), wrong=sum(1 for r in A if t < r['final_start'] and not r['correct'])) for t in T},
           errors_by_type=dict(collections.Counter(r['cat'] for r in A if not r['correct'])),
           never_answered=sum(1 for r in R if not r['answered']), never_answered_by_type=dict(collections.Counter(r['cat'] for r in R if not r['answered'])))
json.dump(res, open('docs/seed7_counts.json', 'w'), indent=1); print(json.dumps(res))
