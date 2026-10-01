'''Audit B17: LLM-judge compute time per prefix check, from committed data (YB-0035 seed 7, YB-0033 seed 5, YB-0034 seed 6).
Run from the repo root. Writes archive/audit/artifacts/judge_timing.json.'''
import json, gzip, numpy as np
out = {}
for label, p in (('seed7 (YB-0035)', 'algorithms/YB-0035-corrected-realtime-race/data/prefix_judge_abs_s7.jsonl.gz'),
                 ('seed5 (YB-0033)', 'algorithms/YB-0033-clean-realtime-race/data/prefix_judge_abs_s5.jsonl.gz'),
                 ('seed6 (YB-0034)', 'algorithms/YB-0034-replication-realtime-race/data/prefix_judge_abs_s6.jsonl.gz')):
    D = [json.loads(l) for l in gzip.open(p, 'rt')]; c = np.array([d['compute_s'] for d in D])
    per = {str(t): round(float(np.median([d['compute_s'] for d in D if int(d['f']) == t])), 3) for t in (48, 96, 192, 384) if any(int(d['f']) == t for d in D)}
    out[label] = dict(checks=len(c), median_s=round(float(np.median(c)), 3), p10_s=round(float(np.percentile(c, 10)), 3), p90_s=round(float(np.percentile(c, 90)), 3), median_by_checkpoint_s=per)
json.dump(out, open('archive/audit/artifacts/judge_timing.json', 'w'), indent=1); print(json.dumps(out))
