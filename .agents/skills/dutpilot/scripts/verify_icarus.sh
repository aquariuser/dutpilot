#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <dutpilot.yaml>" >&2
  exit 2
fi

config="$1"
python -m dutpilot.cli verify "$config"
