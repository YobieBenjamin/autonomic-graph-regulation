# Provenance of this public snapshot

This repository is a **public snapshot** of the private research repository YobieBenjamin/safety, which holds the
complete, unaltered history (every commit, pre-registration and correction) and remains the evidence of record.

- **Source commit (private):** 5534bf1a347e8b3fc10df7533b74e7f660f7f1a2 (2026-10-07T01:56:04-07:00), with additions synced from 6b67b23986c9350b28c5cb945f5fa745bfc3d657 (see below)
- **Excluded from this snapshot:** docs/book/ (an unpublished draft of the author's book) and
  .github/workflows/mine.yml (a disabled automation). Nothing else was removed or changed.
- **Verify the files:** run `shasum -a 256 -c MANIFEST.sha256` to check every file against its fingerprint.
- **Timeline evidence:** pre-registration commit hashes cited in the reports refer to the private history. GitHub's
  server-side timestamps for the decisive pre-registration are preserved in
  archive/audit/artifacts/c1_github_server_timestamps.json. Qualified reviewers may request read access to the
  private history: yobie@ieee.org.
- **Licensing and attribution:** see LICENSING.md, NOTICE and CITATION.cff. Authorship and AI assistance: see README.md.

## Later additions

Added to this public snapshot after 5534bf1, copied unchanged from the private repository at 6b67b23986c9350b28c5cb945f5fa745bfc3d657:

- `observer/`: the Layer 3 safety observer (scoring of risk signal families and signed observer assertions, with tests). Its wire format follows `docs/LANES.md` in `hardware-and-silicon`.
- `algorithms/YB-0051-low-false-alarm-precision/`: the YB-0051 study folder.

Still excluded: `docs/book/` and `.github/workflows/mine.yml`. Nothing else was removed or changed.
`MANIFEST.sha256` lists the added files with their SHA-256 values.
