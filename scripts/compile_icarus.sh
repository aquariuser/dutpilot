#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: $0 <top> <dut_file_in_src> <tb_file_in_tb>" >&2
  exit 2
fi

top="$1"
dut_file="$2"
tb_file="$3"

iverilog -g2012 -s "$top" -o build/sim.out "src/$dut_file" "tb/$tb_file"
