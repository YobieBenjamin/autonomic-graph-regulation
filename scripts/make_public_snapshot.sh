#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# One command: build and publish the PUBLIC snapshot (YobieBenjamin/autonomic-graph-regulation) from the PRIVATE
# original (YobieBenjamin/safety). The private repository and its history are never modified. Self-validating: refuses
# to publish on uncommitted private changes, any book material, or any secret pattern.
# Usage: scripts/make_public_snapshot.sh
set -euo pipefail
export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
PRIV="$(cd "$(dirname "$0")/.." && pwd)"
PUB="${PUB_DIR:-$HOME/Desktop/agr-public}"
REPO=YobieBenjamin/autonomic-graph-regulation

cd "$PRIV"
[ -z "$(git status --porcelain)" ] || { echo 'ABORT: private repository has uncommitted changes; publish privately first.'; exit 1; }
if git ls-files | grep -q '^docs/book/'; then echo 'ABORT: book files are tracked in the private repository.'; exit 1; fi
SRC=$(git rev-parse HEAD)
SRC_DATE=$(git log -1 --format=%cI)
ORIGIN_SHA=$(git ls-remote origin -h refs/heads/main | cut -c1-40)
[ "$SRC" = "$ORIGIN_SHA" ] || { echo 'ABORT: private HEAD is not what GitHub has; push the private repository first.'; exit 1; }

mkdir -p "$PUB"
[ -d "$PUB/.git" ] || git -C "$PUB" init -q -b main
find "$PUB" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
git archive "$SRC" | tar -x -C "$PUB"
rm -rf "$PUB/docs/book" "$PUB/.github/workflows/mine.yml"
cd "$PUB"

# Guards: no book material, no oversized prose, no secrets or personal addresses.
[ ! -e docs/book ] || { echo 'ABORT: book directory present in snapshot'; exit 1; }
BIG=$(find . -path ./.git -prune -o -name '*.md' -size +300k -print)
[ -z "$BIG" ] || { echo "ABORT: unexpectedly large prose files: $BIG"; exit 1; }
# Every line of every file is checked; lines that are themselves scanner pattern definitions (they contain grep -rIlE /
# grep -rnIE) are ignored, and any real match is printed before aborting.
HITS=$(grep -rnIE 'ghp_[A-Za-z0-9]{20,}|github_pat_|sk-ant-|AKIA[0-9A-Z]{16}|PRIVATE KEY|OAUTH_TOKEN=[A-Za-z0-9]{8,}|gmail\.com|icloud\.com' --exclude-dir=.git . | grep -vE 'grep -r[nI]+[lI]*E' || true)
[ -z "$HITS" ] || { echo "ABORT: secret or personal-address pattern found:"; echo "$HITS"; exit 1; }

cat > PROVENANCE.md <<PROV
# Provenance of this public snapshot

This repository is a **public snapshot** of the private research repository YobieBenjamin/safety, which holds the
complete, unaltered history (every commit, pre-registration and correction) and remains the evidence of record.

- **Source commit (private):** ${SRC} (${SRC_DATE})
- **Excluded from this snapshot:** docs/book/ (an unpublished draft of the author's book) and
  .github/workflows/mine.yml (a disabled automation). Nothing else was removed or changed.
- **Verify the files:** run \`shasum -a 256 -c MANIFEST.sha256\` to check every file against its fingerprint.
- **Timeline evidence:** pre-registration commit hashes cited in the reports refer to the private history. GitHub's
  server-side timestamps for the decisive pre-registration are preserved in
  archive/audit/artifacts/c1_github_server_timestamps.json. Qualified reviewers may request read access to the
  private history: yobie@ieee.org.
- **Licensing and attribution:** see LICENSING.md, NOTICE and CITATION.cff. Authorship and AI assistance: see README.md.
PROV

find . -path ./.git -prune -o -type f -print | sed 's#^\./##' | grep -v '^MANIFEST.sha256$' | sort \
  | while read -r f; do shasum -a 256 "$f"; done > MANIFEST.sha256
shasum -a 256 -c MANIFEST.sha256 > /dev/null || { echo 'ABORT: manifest self-check failed'; exit 1; }

git add -A
if ! git -c user.name='Yobie Benjamin' -c user.email='yobie@ieee.org' commit -q -m "Public snapshot of AGR at private commit ${SRC:0:7}"; then
  echo 'nothing new to publish'; exit 0
fi
if ! gh repo view "$REPO" > /dev/null 2>&1; then
  gh repo create "$REPO" --public --source . --push \
    --description 'Autonomic Graph Regulation (AGR): an external, text-blind early-warning regulator for transformer language models. Source-available (PolyForm Noncommercial 1.0.0 / CC BY-NC 4.0).'
else
  git remote get-url origin > /dev/null 2>&1 || git remote add origin "https://github.com/$REPO.git"
  git push -q origin main
fi
echo "PUBLISHED public snapshot of $SRC to https://github.com/$REPO"
