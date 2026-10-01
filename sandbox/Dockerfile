# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Sandbox for building/testing untrusted (model-written) algorithm code.
# No secrets, no network at run time (enforced by run.sh), non-root user.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev make coreutils \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir numpy==2.5.3 scipy==1.18.1 scikit-learn==1.9.1
RUN python -c "from sklearn.datasets import load_digits; load_digits()"
RUN useradd -m -u 10001 miner
USER miner
ENV PYTHONDONTWRITEBYTECODE=1 HOME=/tmp
WORKDIR /work
