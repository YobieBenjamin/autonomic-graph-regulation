"""Risk signal families.

Each detector emits ``Hit(family, pattern, weight)``. ``pattern`` is a stable
identifier, never the matched text, so flags can go into the audit trail without
copying the request into it. Weights are evidence strength on a 0-1+ scale and
are combined per family in ``scoring.py``.

Families (see README.md for what each one means):

  injection            instructions smuggled into data or user text
  impersonation        claims of authority the request cannot prove
  exfiltration         data leaving the boundary: external hosts, bulk, encoded blobs
  credential_access    secrets, keys, or the material that unlocks them
  privilege_escalation granting, elevating or bypassing permissions
  oversight_evasion    disabling, deleting or tampering with audit and monitoring
  self_modification    changing the agent's own policy, prompt, weights or goals
  weight_exfiltration  moving model weights or checkpoints
  destructive          irreversible or bulk deletion
  financial            money movement: size relative to limit, new payees
  burst                action rate above the agent's normal pace
  scope_drift          an action outside the task the request declared
  hazard_content       categories of request the policy never permits (category only)
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse

_ZERO_WIDTH = re.compile("[\u200b\u200c\u200d\u2060\ufeff]")
_URL = re.compile(r"https?://[^\s\"'<>)]+", re.IGNORECASE)
_BLOB = re.compile(r"[A-Za-z0-9+/]{2000,}={0,2}")
BULK_CHARS = 4000


@dataclass(frozen=True)
class Hit:
    family: str
    pattern: str
    weight: float


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return _ZERO_WIDTH.sub("", text).lower()


def strings_in(obj: Any) -> Iterable[str]:
    """Every string value in a nested params structure, in order."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, Mapping):
        for v in obj.values():
            yield from strings_in(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from strings_in(v)


# (family, pattern id, regex, weight). Regexes run on normalised lowercase text.
PATTERNS: list[tuple[str, str, str, float]] = [
    # injection
    ("injection", "override_previous", r"ignore (all |any |the )?(previous|prior|above|earlier) (instructions|rules|prompts?|messages)", 1.0),
    ("injection", "disregard_system", r"disregard (your|the|all) (system|developer|safety|previous) ", 1.0),
    ("injection", "role_reassign", r"\byou are now (a |an |the )?\w+", 0.5),
    ("injection", "fake_system_tag", r"</?(system|assistant|developer)>|\[/?inst\]|<\|im_(start|end)\|>", 1.0),
    ("injection", "new_instructions", r"\bnew instructions?\s*:", 0.6),
    ("injection", "unrestricted_mode", r"(developer|jailbreak|god|unrestricted|dan) mode", 0.9),
    ("injection", "no_rules", r"pretend (there are )?no (rules|restrictions|guidelines)|without any (restrictions|filters)", 0.9),
    ("injection", "system_prompt_probe", r"(reveal|print|show|repeat) (your|the) (system prompt|hidden instructions)", 0.6),
    # impersonation
    ("impersonation", "claims_admin", r"\bi am (the |an? )?(administrator|admin|operator|developer|system owner|anthropic|openai)\b", 0.5),
    ("impersonation", "claims_approval", r"(authori[sz]ed|approved|signed off) by (the )?(security|compliance|legal|management|the ceo)", 0.3),
    ("impersonation", "urgent_override", r"\b(urgent|emergency)\b.{0,40}\b(skip|bypass|no need for) (the )?(approval|review|check|hold)", 0.9),
    # exfiltration (URL and blob checks are added in code below)
    ("exfiltration", "send_out", r"\b(upload|post|send|forward|email) (it |this |the (data|file|records|contents) )?(to|onto) (an? )?(external|personal|third[- ]party|pastebin|webhook|paste|dropbox|gist)", 0.9),
    ("exfiltration", "pastebin_like", r"pastebin|transfer\.sh|file\.io|ngrok\.io|webhook\.site", 0.9),
    # credential access
    ("credential_access", "secret_shape_openai", r"\bsk-[a-z0-9_-]{20,}", 1.0),
    ("credential_access", "secret_shape_aws", r"\bakia[0-9a-z]{16}\b", 1.0),
    ("credential_access", "secret_shape_github", r"\bghp_[a-z0-9]{30,}", 1.0),
    ("credential_access", "private_key_block", r"-----begin [a-z ]*private key-----", 1.0),
    ("credential_access", "seed_phrase", r"\b(seed phrase|mnemonic|recovery phrase)\b", 0.5),
    ("credential_access", "secret_keyword", r"\b(password|passwd|api[ _-]?key|private key|secret key)\b", 0.25),
    ("credential_access", "dotenv_or_keyfile", r"(^|[\s/\\])\.env\b|\bid_rsa\b|\.pem\b|keychain", 0.4),
    # privilege escalation
    ("privilege_escalation", "grant_admin", r"\b(grant|give|add|make)\b.{0,40}\b(admin|root|sudo|superuser|owner)\b", 0.9),
    ("privilege_escalation", "elevate", r"\b(escalate|elevate) (my |the |our )?(privileges?|permissions?|access)", 0.9),
    ("privilege_escalation", "sudo_chmod", r"\bsudo\b|chmod (-r )?(777|a\+rwx|\+s)\b|setuid", 0.8),
    ("privilege_escalation", "disable_control", r"\b(disable|turn off|bypass|circumvent|skip) (the |our )?(gate|guard|firewall|sandbox|policy|approval|allowlist)\b", 0.9),
    # oversight evasion
    ("oversight_evasion", "disable_monitor", r"\b(disable|turn off|stop|kill|pause) (the |all )?(audit|logging|logs?|monitor(ing)?|observer|sentry|watchdog|telemetry|alerts?)\b", 1.0),
    ("oversight_evasion", "tamper_log", r"\b(delete|erase|truncate|rewrite|clear|scrub|edit)\b.{0,30}\b(audit|logs?|ledger|history|trail|record of)\b", 1.0),
    ("oversight_evasion", "hide_action", r"without (it |this )?(being )?(logged|recorded|noticed|the (operator|human) knowing)|don'?t (log|record|tell)", 1.0),
    # self modification
    ("self_modification", "edit_own_policy", r"\b(modify|edit|change|rewrite|update|patch|overwrite) (your|the agent'?s|its) (own )?(policy|system prompt|prompt|rules|config(uration)?|guardrails?|goals?|objectives?)\b", 1.0),
    ("self_modification", "retrain_self", r"\b(retrain|fine[- ]tune|finetune) (yourself|itself|the model on your)", 1.0),
    ("self_modification", "self_replicate", r"\b(copy|replicate|clone|spawn) (yourself|itself)\b", 1.0),
    # weight exfiltration
    ("weight_exfiltration", "weights_transfer", r"\b(download|copy|export|upload|transfer|send|exfiltrate|move)\b.{0,40}\b(weights?|checkpoints?|model files?|state[_ ]dict)\b", 1.0),
    ("weight_exfiltration", "weight_file_types", r"\.(safetensors|gguf|ckpt|pth)\b", 0.8),
    # destructive
    ("destructive", "rm_rf", r"\brm\s+-rf?\b|\brm -r\b", 0.9),
    ("destructive", "drop_store", r"\bdrop (table|database|schema)\b|\btruncate table\b", 0.9),
    ("destructive", "bulk_delete", r"\bdelete (all|every|the entire|everything)\b|\bwipe\b|\bformat (the )?(disk|drive)\b", 0.7),
    # hazard content: category only, never content
    ("hazard_content", "chem_bio_weapon", r"\b(nerve agent|sarin|vx gas|anthrax|ricin|botulinum toxin|enhance (a |the )?pathogen|enrich (uranium|plutonium))\b", 1.0),
    ("hazard_content", "cyber_weapon", r"\b(write|build|create|deploy) (a |an |me )?(ransomware|keylogger|botnet|rootkit|worm)\b", 1.0),
    ("hazard_content", "zero_day_exploit", r"\b(zero[- ]day|0[- ]day) (exploit|chain)\b", 0.8),
]

_COMPILED = [(f, p, re.compile(rx), w) for f, p, rx, w in PATTERNS]


def _text_hits(text: str) -> list[Hit]:
    hits = []
    for family, pattern, rx, weight in _COMPILED:
        if rx.search(text):
            hits.append(Hit(family, pattern, weight))
    return hits


def detect(action: str, params: Mapping[str, Any], context: Mapping[str, Any] | None = None) -> list[Hit]:
    """Run every family over one request. Pure function: no I/O, no state."""
    context = dict(context or {})
    hits: list[Hit] = []

    # Scan the action name and every string in params.
    values = [action, *strings_in(params)]
    for value in values:
        hits += _text_hits(normalise(value))

    # Exfiltration: external destinations and bulk or encoded payloads.
    allowed = set(context.get("allowed_hosts", []))
    for value in values:
        for url in _URL.findall(value):
            host = (urlparse(url).hostname or "").lower()
            if host and host not in allowed:
                hits.append(Hit("exfiltration", "external_destination", 0.6))
        if len(value) > BULK_CHARS:
            hits.append(Hit("exfiltration", "bulk_payload", 0.8))
        if _BLOB.search(value):
            hits.append(Hit("exfiltration", "encoded_blob", 2.0))

    # Financial: size against the limit, and whether the payee is known.
    amount = params.get("amount") if isinstance(params, Mapping) else None
    if isinstance(amount, (int, float)) and not isinstance(amount, bool) and amount > 0:
        limit = float(context.get("limit", 1000))
        ratio = float(amount) / limit if limit > 0 else float("inf")
        if ratio >= 0.5:
            hits.append(Hit("financial", "amount_over_half_limit", min(3.0, ratio)))
    if isinstance(amount, (int, float)) and context.get("payee_known") is False:
        hits.append(Hit("financial", "new_payee", 0.5))

    # Burst: rate of actions in the last minute.
    if int(context.get("actions_last_60s", 0)) > 20:
        hits.append(Hit("burst", "rate_above_normal", 1.0))

    # Scope: an action outside what the request declared it would do.
    declared = context.get("declared_scope")
    if declared is not None and action not in set(declared):
        hits.append(Hit("scope_drift", "out_of_declared_scope", 1.0))

    return hits
