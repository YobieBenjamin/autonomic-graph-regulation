# Scores each model's findings against the 9 planted errors (ground_truth.json). A planted error counts as caught if any
# finding's quote or explanation contains its distinctive marker. Unmatched findings are listed for manual review.
import json, re, glob, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
GT = json.load(open('ground_truth.json'))
MARK = {'E1': ['260'], 'E2': ['140'], 'E3': ['8.6'], 'E4': ['15:25'], 'E5': ['I + D', 'I+D', '+ D^', 'sign'], 'E6': ['61%', '61 %', 'about 61'],
        'E7': ['all language models'], 'E8': ['2014'], 'E9': ['553']}
def parse(txt):
    t = re.sub(r'^```(json)?|```$', '', txt.strip(), flags=re.M); i, j = t.find('{'), t.rfind('}')
    try: return json.loads(t[i:j + 1])['findings']
    except Exception as e: return None
out = {}
for f in sorted(glob.glob('out_*.txt')):
    name = f[4:-4]; F = parse(open(f, encoding='utf-8').read())
    if F is None: out[name] = dict(parse_error=True); continue
    caught, used = {}, set()
    for g in GT:
        for k, fd in enumerate(F):
            blob = (str(fd.get('quote', '')) + ' ' + str(fd.get('explanation', ''))).lower()
            if any(m.lower() in blob for m in MARK[g['id']]) and (g['id'] != 'E5' or 'laplacian' in blob or 'i + d' in blob or 'i+d' in blob):
                caught[g['id']] = k; used.add(k); break
    other = [dict(quote=str(F[k].get('quote', ''))[:110], type=F[k].get('type'), severity=F[k].get('severity')) for k in range(len(F)) if k not in used]
    out[name] = dict(findings=len(F), planted_caught=len(caught), of=len(GT), caught_ids=sorted(caught), missed=sorted(set(g['id'] for g in GT) - set(caught)), other_findings=other)
json.dump(out, open('scores.json', 'w'), indent=1)
for n, v in out.items():
    print(n, '| parse error' if v.get('parse_error') else '| findings %d | planted caught %d/%d | missed %s | other %d' % (v['findings'], v['planted_caught'], v['of'], ','.join(v['missed']) or '-', len(v['other_findings'])))
