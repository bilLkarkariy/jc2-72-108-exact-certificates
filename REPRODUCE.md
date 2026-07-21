# Reproduction guide

## Preferred clean-room replay

Requirements:

- Docker with Linux `amd64` support;
- network access to Zenodo;
- about 500 MB of free disk space.

Run:

```bash
docker build --pull -t jc2-exact-audit .
docker run --rm jc2-exact-audit
```

The Docker base image is pinned to Python `3.14.6` by manifest digest. Python
packages and their Linux-wheel hashes are pinned in `requirements-lock.txt`.
The container does not copy the frozen replay from the Git checkout. It:

1. downloads the `v1.0.1` source snapshot from Zenodo;
2. verifies SHA-256
   `f7f0876de12d35badbed2be6a773d4a9dada50aff778c080126aab541deefcde`;
3. extracts and verifies the nested replay bundle SHA-256
   `232204bdb598cc2ea0368e154c8573e18bbfdc69fa631c8878de4b884b38bb18`;
4. runs the frozen `verify_all.sh`;
5. runs the local transcription-bridge audit;
6. runs five negative controls.

Success requires both markers:

```text
JC2_72_108_EXACT_REPLAY_PASS
JC2_72_108_CLEAN_ROOM_PASS
```

## Direct replay without Docker

On Python `3.14.6`, create a fresh virtual environment and install the locked
dependencies. On Linux x86-64:

```bash
python3.14 -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes -r requirements-lock.txt
AUDIT_PYTHON="$PWD/.venv/bin/python" ./scripts/clean_room_replay.sh
```

The lock file contains hashes for CPython 3.14 Linux x86-64 wheels. Other
platforms should use Docker or create and publish a platform-specific lock.

## Run only the bridge audit

After extracting the frozen replay archive:

```bash
python scripts/verify_transcription_bridge.py /path/to/exact_replay
```

Expected final marker:

```text
TRANSCRIPTION_BRIDGE_LOCAL_PASS
```

## Run only the negative controls

```bash
python tests/negative_controls.py /path/to/exact_replay
```

The test works on temporary copies and does not modify the frozen artifacts.
It must finish with:

```text
ALL_NEGATIVE_CONTROLS_PASS
```

## Trust boundary

The clean-room workflow demonstrates deterministic replay and active checking
of the data. It does not by itself validate the upstream proof of Proposition
4.3. See `TRANSCRIPTION_AUDIT.md` for the remaining mathematical review tasks.
