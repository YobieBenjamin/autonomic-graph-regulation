# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
'''Second, independent audit of the v10 blog drafts by GLM-5.3-flash (Zhipu AI) running locally in LM Studio. GLM cannot read
the repository, so this script inlines a self-contained evidence bundle (the committed result files behind every number, with
per-episode rows removed) and both drafts, and asks for a strict JSON report.
Runs against the Z.ai API (LM Studio could not load the glm5next architecture on 2026-10-02). The API key is read at runtime
from the macOS Keychain (service zai-api-key) and is never printed or written. Overrides: GLM_URL, GLM_MODEL.
Usage from the repo root: .venv/bin/python archive/audit/glm_audit.py [--build-only]
Outputs: archive/audit/glm_audit_prompt_v10.txt, blog_v10_audit_glm_raw.txt, blog_v10_audit_glm_2026-10-02.json'''
import json, os, subprocess, sys, time, urllib.request, urllib.error
D = 'archive/audit/blog_drafts_final_2026-10-03/'
PROVIDER = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'zai'
TAG = {'zai': 'glm', 'lmstudio': 'gptoss'}[PROVIDER]
def j(p, drop=()):
    x = json.load(open(p))
    for k in drop: x.pop(k, None)
    return json.dumps(x, separators=(',', ':'))
EV = {
 'YB-0035 results (seed 7)': j('algorithms/YB-0035-corrected-realtime-race/docs/results.json'),
 'YB-0042 results (seed 8)': j('algorithms/YB-0042-probe-baseline/docs/results.json'),
 'YB-0045 results (seeds 9, 13, 14)': j('algorithms/YB-0045-powered-replication/docs/results.json'),
 'YB-0045 post hoc per-seed': j('algorithms/YB-0045-powered-replication/docs/posthoc_per_seed.json'),
 'YB-0045 power calculation': j('algorithms/YB-0045-powered-replication/docs/power.json'),
 'YB-0044 results': j('algorithms/YB-0044-openshell-gating/docs/results.json'),
 'YB-0044 OpenShell policy latency (summary)': j('algorithms/YB-0044-openshell-gating/docs/reload_timing.json', drop=('rows',)),
 'YB-0044 replay plan (summary)': j('algorithms/YB-0044-openshell-gating/docs/replay_plan.json', drop=('episodes',)),
 'Model sizes': j('archive/audit/artifacts/model_sizes.json'),
 'Derivation sizes': j('archive/audit/artifacts/derivation_sizes.json'),
 'Judge timing': j('archive/audit/artifacts/judge_timing.json'),
}
EXTRA = ('Facts from other committed records (treat as evidence): seven earlier audits found 38 (3 critical), 25 (2), 30 (1), '
 '23 (1), 11 (0), 20 (1) and 15 (1) findings (CORRECTIONS.md). YB-0031: the regulator lost a pre-registered race to the judge, '
 '4 vs 12 of 47; on finished answers self-consistency AUROC 0.982, judge 0.947, earlier regulator 0.890. Answer-token confidence '
 'AUROC 0.366 [0.304, 0.433] on a fresh test; 27 of 36 errors at top-1 probability >= 0.9 in an early study. '
 'YB-0044 race details from live_B.jsonl: races won n = 19 (median alarm-to-commit gap 8.38 s); races lost n = 74 (median 2.89 s, '
 'max 8.23 s); 2 of the 16 correct commits held in arm C had no alarm (release issued on time, retry window 12 s). '
 'Timestamps: YB-0045 OpenTimestamps 14:53 UTC, RFC 3161 15:45 UTC, first test recording 18:59 UTC; '
 'YB-0044 pre-registration commit 43b2a9a, RFC 3161 18:08:17 UTC. OpenShell 0.1.2 on Colima (docs/OPENSHELL_SETUP.md).')
INSTR = '''You are an independent, adversarial fact-checker for two blog drafts about an AI safety research project.
Use ONLY the EVIDENCE section below. You cannot browse; do not use outside knowledge to confirm numbers.

Procedure:
1. Extract every quantitative claim (counts, percentages, intervals, timings, sizes) from both drafts.
2. For each, find the supporting evidence. If it matches (allow rounding to the precision shown), it is verified.
   If it contradicts the evidence, report a finding. If no evidence covers it, report it as UNVERIFIABLE (severity minor)
   unless it is central to a conclusion (then major).
3. Check internal consistency: the same quantity must not appear with different values in different places.
4. Check for overclaims: conclusions stronger than the evidence (for example generalising beyond one model or one task
   family, calling a descriptive comparison significant, or claiming something was tested that was not).
5. Literature citations (for example neuroscience, philosophy or law papers) are not in the evidence. Check them from your own
   knowledge: report one only if you are confident the author, year, venue or described finding is wrong, and say what you
   believe is correct; otherwise do not report it. Also check that general factual statements about the brain, law and AI
   are accurate and not overstated.
6. Do NOT report style. The plain-English draft is intentionally informal and irreverent; only flag wording that changes
   or overstates a claim.

Severity: critical = a false or misleading headline claim; major = a wrong number or an overclaim a reader would rely on;
minor = imprecision, an unverifiable detail, or a small inconsistency.

Output ONE JSON object and nothing else (no markdown fences, no prose before or after):
{"verdict": "publishable" | "publishable_with_fixes" | "not_publishable",
 "claims_checked": <int>, "claims_verified": <int>,
 "findings": [{"id": "G1", "severity": "critical|major|minor", "draft": "plain|technical",
   "quote": "<exact words from the draft, at most 25 words>", "issue": "<what is wrong>",
   "evidence": "<which evidence item, or UNVERIFIABLE>", "fix": "<concrete replacement wording>"}]}'''
prompt = INSTR + '\n\n=== EVIDENCE ===\n' + '\n'.join('[%s] %s' % (k, v) for k, v in EV.items()) + '\n[Other records] ' + EXTRA
prompt += '\n\n=== DRAFT 1: plain-English ===\n' + open(D + 'post_plain_linkedin.md').read() + '\n\n=== DRAFT 2: technical ===\n' + open(D + 'post_technical_v11.md').read()
open('archive/audit/multi_audit_prompt_final.txt', 'w').write(prompt)
print('prompt characters', len(prompt), '(about', len(prompt) // 4, 'tokens)', flush=True)
if '--build-only' in sys.argv: raise SystemExit(0)
if PROVIDER == 'zai':
    URL = os.environ.get('GLM_URL', 'https://api.z.ai/api/paas/v4/chat/completions'); MODEL = os.environ.get('GLM_MODEL', 'glm-5.3-flash')
    KEY = subprocess.run(['security', 'find-generic-password', '-s', 'zai-api-key', '-w'], capture_output=True, text=True).stdout.strip()
    if not KEY: raise SystemExit('No key in the Keychain under service zai-api-key')
    HDR = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + KEY}
    req = dict(model=MODEL, temperature=0, max_tokens=40000, reasoning_effort='high', messages=[dict(role='user', content=prompt)])
else:
    URL = 'http://localhost:1234/v1/chat/completions'; MODEL = 'openai/gpt-oss-120b'; HDR = {'Content-Type': 'application/json'}
    req = dict(model=MODEL, temperature=0, max_tokens=40000, reasoning_effort='high', messages=[dict(role='user', content=prompt)])
t0 = time.time()
try:
    r = json.load(urllib.request.urlopen(urllib.request.Request(URL, data=json.dumps(req).encode(), headers=HDR), timeout=7200))
except urllib.error.HTTPError as e:
    raise SystemExit('API error %s: %s' % (e.code, e.read().decode()[:600]))
out = r['choices'][0]['message']['content']
open('archive/audit/final_audit_%s_raw.txt' % TAG, 'w').write(out)
s = out[out.find('{'): out.rfind('}') + 1]
try:
    rep = json.loads(s); rep['_meta'] = dict(model=r.get('model', MODEL), endpoint=URL, seconds=round(time.time() - t0), usage=r.get('usage'))
except Exception as e:
    rep = dict(parse_error=str(e), seconds=round(time.time() - t0))
json.dump(rep, open('archive/audit/final_audit_%s_2026-10-03.json' % TAG, 'w'), indent=1)
print(json.dumps({k: rep.get(k) for k in ('verdict', 'claims_checked', 'claims_verified', 'parse_error')}), 'findings', len(rep.get('findings', [])))
