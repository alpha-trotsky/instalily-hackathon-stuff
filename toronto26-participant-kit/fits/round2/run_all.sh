#!/bin/bash
# Round-2 collection (approved by the user 2026-09-28). One system per invocation; runs sequential.
sys=$1; shift
cd "$(dirname "$0")/../.."
while [ $# -gt 0 ]; do
  name=$1; out=$2; shift 2
  seg=fits/round2/segments/${sys}_${name}.json
  n=$(python3 -c "import json;print(sum(s['steps'] for s in json.load(open('$seg'))))")
  echo "$(date -u +%FT%TZ) start $sys $name -> $out ($n steps)"
  python3 run_schedule.py --system $sys --output data/$sys/$out.json --segments $seg --confirm $n || { echo "FAILED $sys $name"; exit 1; }
  echo "$(date -u +%FT%TZ) done $sys $name"
done
python3 run_schedule.py --budget $sys
