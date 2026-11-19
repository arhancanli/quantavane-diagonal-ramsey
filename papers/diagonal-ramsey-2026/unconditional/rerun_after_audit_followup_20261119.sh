#!/bin/zsh
# Follow-up to rerun_after_audit_20261119.sh (19 Nov 2026), two record fixes found when reading its logs:
# (1) Its refusal check matched only "refus", "not the pinned" or "not a full". source_A/B refuse a part range without
#     --partial=yes with "cells i..j is only part of the N cells; ..." and a repeated option with "option --k given twice":
#     both exited 1, but the check printed CONTROL FAILED. Here every source control is re-run with the pattern widened.
# (2) It compared the re-assembled *.map.json byte for byte, but the map records its own output path ("out") and the run
#     time ("seconds"). Here both full certificates are re-assembled again and the maps compared without those two keys.
set -u
U=${0:A:h}
FPY=${QV_FLINT_PY:-<flint-python>}
A="<archive>/ramsey-unconditional"
S="$A/lw_5ec98f47"; CR="$A/cone"; CERTS="<archive>/ramsey-zbs"
T=rerun_20261119
gate() { while (( $(sysctl -n vm.loadavg | awk '{print $2}') >= 60 )) || \
               (( $(memory_pressure | awk '/free percentage/ {gsub("%", "", $NF); print $NF}') < 35 )); do sleep 20; done; }
refuse() { local name=$1; shift; local out rc; out=$("$@" 2>&1); rc=$?
  if (( rc != 0 )) && print -r -- "$out" | grep -qiE 'refus|not the pinned|only part of|given twice'; then print -r -- "REFUSED as required ($name): $(print -r -- "$out" | tail -1)"
  else print -r -- "CONTROL FAILED ($name): exit $rc: $(print -r -- "$out" | tail -2)"; fi; }

gate; ( date
  echo '== OPTION AND RANGE CONTROLS (audit S-1, S-2), refusal pattern widened: each must be refused'
  for prog in A B; do
    if [ $prog = A ]; then PY=python3; else PY=$FPY; fi
    cd $U/source
    refuse "source_$prog --require without =" nice -n 10 $PY -I source_$prog.py "$S/source.json" "$S/source_cells.json" "$A/source_runs/x.json" --from=73200 --to=73302 --partial=yes --require 776/1000000000
    refuse "source_$prog misspelt key --requre" nice -n 10 $PY -I source_$prog.py "$S/source.json" "$S/source_cells.json" "$A/source_runs/x.json" --from=73200 --to=73302 --partial=yes --requre=776/1000000000
    refuse "source_$prog empty range --from=73302" nice -n 10 $PY -I source_$prog.py "$S/source.json" "$S/source_cells.json" "$A/source_runs/x.json" --from=73302
    refuse "source_$prog part range without --partial=yes" nice -n 10 $PY -I source_$prog.py "$S/source.json" "$S/source_cells.json" "$A/source_runs/x.json" --from=73200 --to=73302
    refuse "source_$prog option given twice" nice -n 10 $PY -I source_$prog.py "$S/source.json" "$S/source_cells.json" "$A/source_runs/x.json" --require=0 --require=1/1000000
  done
  date ) > $U/source/source_option_controls_followup_$T.log 2>&1

gate; ( date
  echo '== assemble_full.py (with the pin) re-run to a scratch path; certificate byte for byte, map equal apart from "out" and "seconds"'
  mkdir -p "$CR/rerun_tmp2"; cd $U/cone
  for c in certK3 certCD3; do
    nice -n 10 python3 -I assemble_full.py "$CR/zbs_full.json" "$CERTS/$c.json" "$CR/cone_$c.json" "$CR/rerun_tmp2/$c-full.json" "$CR/ctl_certs_0.json" "$CR/ctl_certs_1.json" > /dev/null; echo "EXIT $?"
    cmp -s "$CR/rerun_tmp2/$c-full.json" "$CR/$c-full.json" && echo "$c-full.json identical to the recorded certificate" || echo "MISMATCH $c-full.json"
    python3 -I -c '
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
rest = [k for k in diff if k not in ("out", "seconds")]
print("%s map: %d keys; differing keys %s; %s" % (sys.argv[3], len(a), diff, "EQUAL apart from out and seconds" if not rest else "MISMATCH in %s" % rest))
' "$CR/rerun_tmp2/$c-full.map.json" "$CR/$c-full.map.json" $c
  done
  rm -f "$CR/rerun_tmp2"/*.json; rmdir "$CR/rerun_tmp2"
  date ) > $U/cone/assemble_pin_followup_$T.log 2>&1
echo FOLLOWUP_DONE
