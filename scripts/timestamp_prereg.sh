#!/usr/bin/env bash
# Copyright (c) 2026 Yobie Benjamin. Autonomic Graph Regulation (AGR). All rights reserved except as licensed.
# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0  (see LICENSE.md, NOTICE)
# Provenance canary: AGR-CANARY-7f3c2a9e-5b14-4d6e-9a1f-2c8e0b6d4a71
# Protocol rule 13: timestamp a pre-registration record two independent ways, verifying each.
#  (1) OpenTimestamps: the file's SHA-256 is anchored in the Bitcoin blockchain via public calendars (complete after a
#      few hours; upgrade with: .venv/bin/ots upgrade <file>.ots). Only the fingerprint leaves this machine.
#  (2) RFC 3161: signed timestamp tokens from two independent timestamp authorities (FreeTSA, DigiCert), each verified
#      against the authority's certificate chain. Only the fingerprint leaves this machine.
# Usage: scripts/timestamp_prereg.sh <record-file>
set -euo pipefail
cd "$(dirname "$0")/.."; F="$1"; [ -s "$F" ] || { echo "usage: $0 <record-file>"; exit 1; }
OSSL=/opt/homebrew/opt/openssl@3/bin/openssl; C=archive/timestamps/certs; mkdir -p "$C"
if [ -s "$F.ots" ]; then .venv/bin/ots upgrade "$F.ots" > /dev/null 2>&1 || true; else .venv/bin/ots stamp "$F" > /dev/null 2>&1; fi
if .venv/bin/ots info "$F.ots" 2>/dev/null | grep -q BitcoinBlockHeaderAttestation; then echo "OpenTimestamps: complete (Bitcoin-anchored)"; else echo "OpenTimestamps: pending (upgrade later)"; fi
[ -s "$C/freetsa_cacert.pem" ] || curl -sf -o "$C/freetsa_cacert.pem" https://freetsa.org/files/cacert.pem
[ -s "$C/freetsa_tsa.crt" ] || curl -sf -o "$C/freetsa_tsa.crt" https://freetsa.org/files/tsa.crt
$OSSL ts -query -data "$F" -no_nonce -sha256 -cert -out "$F.tsq" 2>/dev/null
for TSA in freetsa=https://freetsa.org/tsr digicert=http://timestamp.digicert.com; do
  N=${TSA%%=*}; U=${TSA#*=}
  curl -sf -H 'Content-Type: application/timestamp-query' --data-binary @"$F.tsq" "$U" -o "$F.$N.tsr" || { echo "RFC 3161 $N: request failed"; continue; }
  T=$($OSSL ts -reply -in "$F.$N.tsr" -text 2>/dev/null | grep 'Time stamp:' | sed 's/Time stamp: //')
  if [ "$N" = freetsa ]; then V=$($OSSL ts -verify -in "$F.$N.tsr" -queryfile "$F.tsq" -CAfile "$C/freetsa_cacert.pem" -untrusted "$C/freetsa_tsa.crt" 2>&1 | tail -1)
  else V=$($OSSL ts -verify -in "$F.$N.tsr" -queryfile "$F.tsq" -CAfile /etc/ssl/cert.pem 2>&1 | tail -1); fi
  echo "RFC 3161 $N: $T | verification: $V"
done
