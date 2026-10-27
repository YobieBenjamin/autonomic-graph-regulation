# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
"""Descriptive names for hypotheses, shared by the miner (miner/mine.py) and the orchestrator (orchestrator/orchestrate.py).

Why this file exists: until 2026-10 every hypothesis got a letter-number code (two letters and four digits) and its
folder was named "<code>-<title words>". The project retired those codes. Every hypothesis now has a descriptive name:

  EXPERIMENT-<2 to 5 plain English words in capitals, joined by hyphens>    e.g. EXPERIMENT-CORTISOL-INTEGRATOR
  (the chip-program wave issues use WAVE-... the same way, e.g. WAVE-CHIP-VISIBLE-VITALS)

and its folder is algorithms/<the same words in lowercase>, e.g. algorithms/cortisol-integrator.

The catalog is HYPOTHESES.md (one "## <NAME>: <title>" heading per hypothesis) and LEDGER.md (one "| <NAME> | ..." row
per attempt). A name the miner writes here is a proposal until the orchestrator registers it in the project's registry
(LABELS.md, outside this repository); the orchestrator copies new catalog names into LABELS.md (kit/sync_catalog.py)
and the naming checks refuse any name LABELS.md does not hold.

Rules for a NEW name (new_name below):
  - the words come from the hypothesis title, in title order; small linking words (of, the, for, ...) and any word that
    contains a digit (version tags such as v1, counts such as 768) are left out, so the name never holds a number;
  - the shortest candidate is the first three title words (two if the title has only two);
  - the name must be unique: not a heading in HYPOTHESES.md, not a row in LEDGER.md, and its folder must not exist
    under algorithms/ (optionally also not in LABELS.md, when the environment variable LABELS_MD points to it);
  - if it is taken, a more specific wording from the same title is tried (one more title word at a time, up to five,
    then other in-order choices of three to five title words). A number is NEVER appended. If every wording is taken
    the function returns None and the caller leaves the hypothesis out, so a person can give it a clearer title.
"""
import itertools
import os
import re

# A catalog name: EXPERIMENT or WAVE, then one or more capitalised words joined by hyphens. Digits are accepted when
# READING (older names elsewhere in the registry may have them); new_name below never produces one.
NAME = r'(?:EXPERIMENT|WAVE)(?:-[A-Z][A-Z0-9]*)+'
# A hypothesis heading in HYPOTHESES.md: "## NAME: title" or "## NAME (extension): title". Group 1 is the name, group 2 the rest.
HEADING_RE = re.compile(r'^## (' + NAME + r')(?=[\s:(]|$)(.*)$', re.M)
# A ledger row in LEDGER.md: "| NAME | ...". Group 1 is the name.
LEDGER_ROW_RE = re.compile(r'^\| (' + NAME + r') \|', re.M)
# An old-style letter-number code at the start of a heading that a person may still type (letters, digits, then a
# separator): removed before naming, so only the title words remain.
OLD_CODE_RE = re.compile(r'^[A-Za-z]{1,4}-?\d+\s*(?:\(extension\))?\s*[:\u2014\u2013-]?\s*')

# Small linking words that carry no meaning in a name.
STOPWORDS = set('''a an and as at be by for from in into is it its of on or over per the their this to under via with
                   within without using toward towards than that what which who whose when where how do does are can'''.split())
PREFIXES = ('EXPERIMENT', 'WAVE')
MIN_WORDS, MAX_WORDS = 2, 5
MAX_TITLE_WORDS = 12          # only the first 12 usable title words are combined (keeps the search small)


def folder_for(name):
    """The folder name for a catalog name: the words after the prefix, lowercase. EXPERIMENT-CORTISOL-INTEGRATOR -> cortisol-integrator."""
    return name.split('-', 1)[1].lower()


def title_words(title):
    """The usable words of a title, in order, in capitals: no linking words, no word containing a digit, no prefix word."""
    out = []
    for w in re.findall(r'[A-Za-z0-9]+', title):
        if len(w) < 2 or any(ch.isdigit() for ch in w) or w.lower() in STOPWORDS or w.upper() in PREFIXES:
            continue
        out.append(w.upper())
    return out[:MAX_TITLE_WORDS]


def candidates(words):
    """Name word lists to try, least specific first: the first 3 words, then 4 and 5, then other in-order choices of 3 to 5."""
    if len(words) < MIN_WORDS:
        return []
    seen, out = set(), []
    def add(ws):
        if tuple(ws) not in seen:
            seen.add(tuple(ws)); out.append(list(ws))
    for k in range(min(3, len(words)), min(MAX_WORDS, len(words)) + 1):
        add(words[:k])                                   # first k title words
    for k in range(3, min(MAX_WORDS, len(words)) + 1):
        for idx in itertools.combinations(range(len(words)), k):
            add([words[i] for i in idx])                 # other in-order choices, same title words only
    return out


def taken(root):
    """Names and folders already in use: HYPOTHESES.md headings, LEDGER.md rows, folders under algorithms/ (and LABELS_MD if set)."""
    names = set()
    for fname, rx in (('HYPOTHESES.md', HEADING_RE), ('LEDGER.md', LEDGER_ROW_RE)):
        p = os.path.join(root, fname)
        if os.path.exists(p):
            names.update(m.group(1) for m in rx.finditer(open(p, encoding='utf-8').read()))
    labels = os.environ.get('LABELS_MD')
    if labels and os.path.exists(labels):
        names.update(re.findall(r'\b' + NAME + r'\b', open(labels, encoding='utf-8').read()))
    alg = os.path.join(root, 'algorithms')
    folders = set(os.listdir(alg)) if os.path.isdir(alg) else set()
    return names, folders


def new_name(title, root, prefix='EXPERIMENT'):
    """A unique descriptive name for a hypothesis with this title, or None if no wording from the title is free."""
    names, folders = taken(root)
    for ws in candidates(title_words(title)):
        name = prefix + '-' + '-'.join(ws)
        if name not in names and folder_for(name) not in folders:
            return name
    return None


def parse_heading(block):
    """(name, title) of a HYPOTHESES.md block, or (None, None) when its heading carries no catalog name."""
    m = HEADING_RE.match(block.splitlines()[0]) if block.strip() else None
    if not m:
        return None, None
    rest = m.group(2)
    title = rest.split(':', 1)[1] if ':' in rest else rest
    return m.group(1), title.strip()


def ensure_named(text, root):
    """Give every OPEN hypothesis whose heading has no catalog name a new descriptive name, written into its heading.

    This is how a hypothesis that a person adds by hand ("## Somatic marker replay", or a heading that still starts with an old letter-number code)
    enters the catalog under a registered-style name before it is mined. Returns (new text, list of names given).
    A block whose title gives no free name is left as it is (and is not mined, because it has no name)."""
    given = []
    for block in re.split(r'(?m)^(?=## )', text):
        if not block.startswith('## ') or 'status: open' not in block or parse_heading(block)[0]:
            continue
        head = block.splitlines()[0]
        title = OLD_CODE_RE.sub('', head[3:]).strip()
        name = new_name(title, root) if title else None
        if name and name not in given:
            # write the heading in the catalog format "## NAME: title" (no dashes as separators)
            new_head = '## ' + name + ': ' + title
            text = text.replace(block, block.replace(head, new_head, 1), 1)
            given.append(name)
            open(os.path.join(root, 'HYPOTHESES.md'), 'w', encoding='utf-8').write(text)   # so the next name sees this one
    return text, given
