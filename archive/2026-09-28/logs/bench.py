import json, time, urllib.request, re, subprocess, os, sys
PROMPT = ('Write a C function `double laplacian_quadform(const double *A, int n, const double *x)` returning x^T L x '
          'where L = D - A is the combinatorial graph Laplacian of symmetric weighted adjacency A (row-major). '
          'Then a main() that tests it on the 3-node path graph with x = (1,0,-1) (answer: 2.0) and prints PASS or FAIL. '
          'Reply with ONLY one ```c code block.')
def run(model):
    body = json.dumps({'model': model, 'messages': [{'role': 'user', 'content': PROMPT}], 'max_tokens': 4000,
                       'temperature': 0.2}).encode()
    t = time.time()
    d = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:1234/v1/chat/completions', body,
                                          {'content-type': 'application/json'}), timeout=600))
    dt = time.time() - t; u = d['usage']; txt = d['choices'][0]['message']['content']
    m = re.search(r'```c\n(.*?)```', txt, re.S); verdict = 'NO CODE'
    if m:
        open('/tmp/b.c', 'w').write(m.group(1))
        env = {**os.environ, 'SDKROOT': '/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk'}
        c = subprocess.run(['gcc', '-O2', '-Wall', '-Werror', '-o', '/tmp/b', '/tmp/b.c', '-lm'], capture_output=True, env=env)
        verdict = subprocess.run(['/tmp/b'], capture_output=True, text=True).stdout.strip()[-20:] if c.returncode == 0 else 'COMPILE FAIL'
    print(f'{model}: {u["completion_tokens"]} tok in {dt:.1f}s = {u["completion_tokens"]/dt:.0f} tok/s | compiled+ran: {verdict}', flush=True)
for mdl in sys.argv[1:]: run(mdl)
