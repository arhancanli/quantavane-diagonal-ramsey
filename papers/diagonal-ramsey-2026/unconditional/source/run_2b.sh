#!/bin/zsh
# Stage 2b runs: both programs on all cells of [1e-16, 1], then margin probes (red: tau = 1e-6, above the true minimum of Delta(s)/s (about 7.75e-7, at s = 1), must FAIL; green:
# tau = 5e-7 must PASS) on the last cells (around the worst point s ~ 0.9945). nice 10, one process at a time.
S="<archive>/ramsey-unconditional/lw_5ec98f47"
R="<archive>/ramsey-unconditional/source_runs"
# TAG names the logs and outputs: 20261119 = first runs; rerun_20261119 = after the code audit fixes (strict options, explicit
# --partial=yes for a part range). Since the audit fixes, a part range without --partial=yes is refused.
TAG=${TAG:-20261119}
P=""; [ "$TAG" != 20261119 ] && P="--partial=yes"
FPY=<flint-python>
gate() { while [ "$(uptime | sed 's/.*load averages*: //' | awk '{print int($1)}')" -ge 60 ]; do sleep 30; done; }
gate; (date; uptime; nice -n 10 $FPY -I source_B.py "$S/source.json" "$S/source_cells.json" "$R/sourceB_full_$TAG.json"; echo "EXIT $?"; date) > sourceB_full_$TAG.log 2>&1
gate; (date; uptime; nice -n 10 python3 -I source_A.py "$S/source.json" "$S/source_cells.json" "$R/sourceA_full_$TAG.json"; echo "EXIT $?"; date) > sourceA_full_$TAG.log 2>&1
gate; ( date
  echo '== RED margin probe: require Delta(s) > 1e-6 s on cells 73200..73302 (the minimum of Delta(s)/s there is about 7.75e-7, at s = 1): must FAIL'
  nice -n 10 python3 -I source_A.py "$S/source.json" "$S/source_cells.json" "$R/probeA_red_$TAG.json" --from=73200 --to=73302 $P --require=1/1000000; echo "EXIT $?"
  nice -n 10 $FPY -I source_B.py "$S/source.json" "$S/source_cells.json" "$R/probeB_red_$TAG.json" --from=73200 --to=73302 $P --require=1/1000000; echo "EXIT $?"
  echo '== GREEN margin probe: require Delta(s) > 5e-7 s on the same cells: must PASS'
  nice -n 10 python3 -I source_A.py "$S/source.json" "$S/source_cells.json" "$R/probeA_green_$TAG.json" --from=73200 --to=73302 $P --require=1/2000000; echo "EXIT $?"
  nice -n 10 $FPY -I source_B.py "$S/source.json" "$S/source_cells.json" "$R/probeB_green_$TAG.json" --from=73200 --to=73302 $P --require=1/2000000; echo "EXIT $?"
  date ) > source_probes_$TAG.log 2>&1
echo ALL_2B_RUNS_DONE
