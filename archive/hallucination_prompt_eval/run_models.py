# Runs the identical prompt+document through four models, strictly one at a time. Raw outputs and timings are saved.
import json, os, subprocess, time, urllib.request
os.chdir(os.path.dirname(os.path.abspath(__file__)))
P = open('full_prompt.txt', encoding='utf-8').read()
ENV = dict(os.environ); ENV.pop('ANTHROPIC_API_KEY', None)
ENV['PATH'] = os.path.expanduser('~/.nvm/versions/node/v22.17.1/bin') + ':' + os.path.expanduser('~/.lmstudio/bin') + ':/opt/homebrew/bin:/usr/local/bin:' + ENV.get('PATH', '')
tok = subprocess.run(['security', 'find-generic-password', '-s', 'claude-code-oauth-token', '-w'], capture_output=True, text=True).stdout.strip()
ENV['CLAUDE_CODE_OAUTH_TOKEN'] = tok
log = {}
def save(name, text, t0, note=''):
    open('out_' + name + '.txt', 'w', encoding='utf-8').write(text); log[name] = dict(seconds=round(time.time() - t0, 1), chars=len(text), note=note)
    json.dump(log, open('run_log.json', 'w'), indent=1); print(name, log[name], flush=True)
def claude(model, name):
    t0 = time.time(); sb = '/tmp/hpe_sandbox'; os.makedirs(sb, exist_ok=True)
    r = subprocess.run(['claude', '-p', P, '--model', model, '--allowedTools', '', '--max-turns', '1', '--output-format', 'text'], cwd=sb, env=ENV, capture_output=True, text=True, timeout=1800)
    save(name, r.stdout if r.stdout.strip() else 'ERROR: ' + r.stderr[-800:], t0, 'exit %d' % r.returncode)
def local(model_key, name):
    t0 = time.time()
    subprocess.run(['lms', 'unload', '--all'], env=ENV, capture_output=True)
    subprocess.run(['lms', 'load', model_key, '--context-length', '32768', '-y'], env=ENV, capture_output=True, timeout=900)
    body = json.dumps(dict(model=model_key, messages=[dict(role='user', content=P)], temperature=0, max_tokens=24000)).encode()
    req = urllib.request.Request('http://localhost:1234/v1/chat/completions', data=body, headers={'Content-Type': 'application/json'})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=3600)); txt = d['choices'][0]['message'].get('content') or ''
    except Exception as e:
        txt = 'ERROR: ' + repr(e)[:800]
    subprocess.run(['lms', 'unload', '--all'], env=ENV, capture_output=True)
    save(name, txt, t0)
claude('claude-opus-5-5', 'claude_opus_5_5')
claude('claude-fable-5-1', 'claude_fable_5_1')
local('openai/gpt-oss-120b', 'gpt_oss_120b')
local('qwen/qwen3-vl-30b', 'qwen3_vl_30b')
print('ALL_DONE', flush=True)
