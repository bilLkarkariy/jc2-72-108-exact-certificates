#!/usr/bin/env bash
set -euo pipefail

readonly OUTER_URL="https://zenodo.org/records/21479814/files/bilLkarkariy/jc2-72-108-exact-certificates-v1.0.1.zip?download=1"
readonly OUTER_SHA256="f7f0876de12d35badbed2be6a773d4a9dada50aff778c080126aab541deefcde"
readonly INNER_SHA256="232204bdb598cc2ea0368e154c8573e18bbfdc69fa631c8878de4b884b38bb18"
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
readonly SCRIPT_DIR
AUDIT_PYTHON=${AUDIT_PYTHON:-$(command -v python)}
readonly AUDIT_PYTHON

AUDIT_TMP=$(mktemp -d /tmp/jc2-clean-room.XXXXXX)
readonly AUDIT_TMP
cleanup() {
    if [[ -n "${AUDIT_TMP:-}" && -d "$AUDIT_TMP" && "$AUDIT_TMP" == /tmp/jc2-clean-room.* ]]; then
        find "$AUDIT_TMP" -depth -delete
    fi
}
trap cleanup EXIT

readonly OUTER_ZIP="$AUDIT_TMP/v1.0.1-zenodo.zip"
curl --fail --location --retry 4 --show-error --silent "$OUTER_URL" --output "$OUTER_ZIP"
printf '%s  %s\n' "$OUTER_SHA256" "$OUTER_ZIP" | sha256sum -c -

mkdir "$AUDIT_TMP/outer"
unzip -q "$OUTER_ZIP" -d "$AUDIT_TMP/outer"
INNER_ZIP=$(find "$AUDIT_TMP/outer" -type f -name 'jc2_72_108_exact_replay_v1.0.1.zip' -print -quit)
if [[ -z "$INNER_ZIP" || "$INNER_ZIP" != "$AUDIT_TMP"/* ]]; then
    echo "Frozen replay bundle was not found inside the Zenodo snapshot" >&2
    exit 2
fi
readonly INNER_ZIP
printf '%s  %s\n' "$INNER_SHA256" "$INNER_ZIP" | sha256sum -c -

mkdir "$AUDIT_TMP/replay"
unzip -q "$INNER_ZIP" -d "$AUDIT_TMP/replay"
EXACT_ROOT=$(find "$AUDIT_TMP/replay" -type f -name verify_all.sh -print -quit)
if [[ -z "$EXACT_ROOT" ]]; then
    echo "verify_all.sh was not found in the frozen replay bundle" >&2
    exit 2
fi
EXACT_ROOT=$(dirname "$EXACT_ROOT")
readonly EXACT_ROOT

PYTHON="$AUDIT_PYTHON" "$EXACT_ROOT/verify_all.sh" | tee "$AUDIT_TMP/exact-replay.log"
grep -Fxq 'JC2_72_108_EXACT_REPLAY_PASS' "$AUDIT_TMP/exact-replay.log"

"$AUDIT_PYTHON" "$SCRIPT_DIR/verify_transcription_bridge.py" "$EXACT_ROOT"

if [[ "${RUN_NEGATIVE_CONTROLS:-1}" == "1" ]]; then
    "$AUDIT_PYTHON" "$SCRIPT_DIR/../tests/negative_controls.py" "$EXACT_ROOT"
fi

echo "JC2_72_108_CLEAN_ROOM_PASS"
