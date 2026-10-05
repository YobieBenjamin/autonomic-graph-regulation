#!/usr/bin/env bash
# Twelfth audit: publish the v4 drafts, then run three auditors in parallel. Logs to /tmp/audit12.log.
export PATH=$HOME/.nvm/versions/node/v22.17.1/bin:/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH
cd ~/Desktop/SAFETY; L=/tmp/audit12.log; say() { echo "[$(date -u +%H:%M:%S)] $*" >> $L; }
: > $L; say START
SANDBOX_MEM=28g ./publish.sh 'Series v4 (four results, YB-0046 to YB-0049) for the twelfth audit; YB-0049 records; resume and battery scripts' > /tmp/pub_a12.log 2>&1 || { say STOP publish failed; exit 1; }; say COMMITTED $(git log --oneline -1 | cut -c1-7)
scripts/make_public_snapshot.sh >> /tmp/pub_a12.log 2>&1 && say SNAPSHOT_OK || { say STOP snapshot failed; exit 1; }
P=$(cat archive/audit/series_audit3_prompt.txt); TOK=$(security find-generic-password -s claude-code-oauth-token -w 2>/dev/null)
( env -u ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN=$TOK claude -p "$P" --model claude-fable-5-1 --permission-mode plan --allowedTools 'Read,Grep,Glob' --add-dir $HOME/Desktop/agr-public --max-turns 300 --output-format text > /tmp/a12_fable.md 2> /tmp/a12_fable.err; say FABLE_EXIT=$? ) &
( codex exec -m gpt-5.5 -c model_reasoning_effort=high -s read-only -C $HOME/Desktop/SAFETY --skip-git-repo-check -o /tmp/a12_gpt55.md "$P" > /tmp/a12_gpt55.log 2>&1; say GPT55_EXIT=$? ) &
( sed -e 's#series_final_2026-10-04/#series_v4_2026-10-05/#g' -e 's#series_audit2_%s_#series_audit3_%s_#g' -e 's#multi_audit_prompt_series.txt#multi_audit_prompt_series_v4.txt#' -e "s/reasoning_effort='high'/reasoning_effort='low'/" archive/audit/multi_audit_series.py > archive/audit/multi_audit_series_v4.py; .venv/bin/python archive/audit/multi_audit_series_v4.py zai > /tmp/a12_glm.log 2>&1; say GLM_EXIT=$? ) &
wait; say ALL_DONE
