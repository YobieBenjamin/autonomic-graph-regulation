import json, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
def one(i):
    body = json.dumps({'model': 'local-strong', 'messages': [{'role': 'user', 'content': f'Write 300 words on graph Laplacians, variant {i}.'}],
                       'max_tokens': 500, 'temperature': 0.7}).encode()
    d = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:1234/v1/chat/completions', body, {'content-type': 'application/json'}), timeout=600))
    return d['usage']['completion_tokens']
for n in (1, 4):
    t = time.time()
    with ThreadPoolExecutor(n) as ex: toks = sum(ex.map(one, range(n)))
    print(f'{n} concurrent: {toks} tok in {time.time()-t:.1f}s = {toks/(time.time()-t):.0f} tok/s aggregate', flush=True)
