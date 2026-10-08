"""Command line: keygen, and assess a request file.

    python -m safety_observer keygen > observer.key
    python -m safety_observer assess request.json --key observer.key --id obs-main
"""

import argparse
import json
import sys

from .envelope import SigningKey
from .observer import SafetyObserver


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="safety_observer")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("keygen", help="print a fresh 32-byte Ed25519 seed (hex)")
    a = sub.add_parser("assess", help="score a request JSON file")
    a.add_argument("request")
    a.add_argument("--key", required=True, help="file containing the seed hex")
    a.add_argument("--id", default="obs-main")
    args = ap.parse_args(argv)

    if args.cmd == "keygen":
        print(_seed_hex())
        return 0
    with open(args.key) as f:
        key = SigningKey(bytes.fromhex(f.read().strip()))
    with open(args.request) as f:
        req = json.load(f)
    json.dump(SafetyObserver(args.id, key).assess(req), sys.stdout, indent=2, sort_keys=True)
    print()
    return 0


def _seed_hex() -> str:
    import os
    return os.urandom(32).hex()


if __name__ == "__main__":
    raise SystemExit(main())
