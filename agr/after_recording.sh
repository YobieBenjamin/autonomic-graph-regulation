#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Waits for the recorder to finish, snapshots the dataset into each algorithm, runs both experiments in the sandbox.
# Names: the folders, scripts, data files, /tmp logs and done markers used here carry the experiments' descriptive names
# (2026-10 rename, which retired the YB numbers). Each log or marker was renamed in its writer and its reader together.
cd "$(dirname "$0")/.."
while pgrep -f 'agr/recorder.py' >/dev/null; do sleep 20; done
gzip -9 -c data/agr/episodes.jsonl > /tmp/episodes.jsonl.gz
# EXPERIMENT-CONTAMINATION-TEST, EXPERIMENT-HPA-AXIS-ORGANISM and EXPERIMENT-PHYSIOLOGICAL-COUPLING-GRAPH: the paths below use their descriptive folder names (2026-10 rename, which retired the YB numbers)
for a in contamination-test hpa-axis-organism physiological-coupling-graph; do
  cp /tmp/episodes.jsonl.gz algorithms/$a/data/episodes.jsonl.gz
  sandbox/run.sh algorithms/$a all > /tmp/$a.log 2>&1; echo "$a EXIT=$?" >> /tmp/agr_pipeline.log
done
echo PIPELINE_DONE >> /tmp/agr_pipeline.log
# publish data snapshots + results (interpretation is written separately, by reading the numbers)
export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
./publish.sh "AGR data (480 episodes) + raw experiment results for EXPERIMENT-CONTAMINATION-TEST and EXPERIMENT-HPA-AXIS-ORGANISM (interpretation pending)" >> /tmp/agr_pipeline.log 2>&1
echo "PUBLISH EXIT=$?" >> /tmp/agr_pipeline.log
git -C ~/safety pull -q >> /tmp/agr_pipeline.log 2>&1
echo ALL_DONE >> /tmp/agr_pipeline.log
