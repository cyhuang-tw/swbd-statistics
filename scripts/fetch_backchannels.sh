#!/usr/bin/env bash
# Fetch the VAP / Ekstedt Switchboard backchannel list used by
# per_conversation_swbd.py. A copy is already committed at the repo root; run this
# only to refresh it from source.
#
# Source: https://github.com/ErikEkstedt/VoiceActivityProjection
#         (dataset_swb/backchannels.csv)
set -euo pipefail

URL="https://raw.githubusercontent.com/ErikEkstedt/VoiceActivityProjection/main/dataset_swb/backchannels.csv"
out="${1:-backchannels.csv}"

echo "Downloading backchannels.csv -> ${out}"
if command -v wget >/dev/null 2>&1; then
    wget -O "${out}" "${URL}"
else
    curl -fsSL "${URL}" -o "${out}"
fi
echo "Done."
