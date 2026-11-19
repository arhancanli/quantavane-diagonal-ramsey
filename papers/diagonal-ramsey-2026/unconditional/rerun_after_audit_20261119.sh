#!/bin/zsh
# Reruns after the code audit (REFEREE_CODE_AUDIT_20261119.md), 19 Nov 2026 evening.
# The fixes changed source_A.py, source_B.py, lines_A.py, lines_B.py (strict options: S-1, L-1, L-2; explicit part range
# and cell totals: S-2; usage text: S-3, L-1; statement check tied to the theorem: L-3) and check_full.py, assemble_full.py
# (zbs_full.json pinned by SHA-256: C-3). Every changed program is re-run in full here with its red and green controls,
# and checker A is re-run on both full certificates.
# Three streams at most (lab gate: at most 4 cores); each heavy step waits for load < 60 and >= 35% memory free, nice 10.
# Logs: next to each program, named *_rerun_20261119.log; outputs on the archive SSD.
set -u
U=${0:A:h}
REPO=${U:h:h:h}
LANE=$REPO/research/tier2/ramsey-zbs
FPY=${QV_FLINT_PY:-<flint-python>}
A="<archive>/ramsey-unconditional"
S="$A/lw_5ec98f47"; LR="$A/lines_runs"; CR="$A/cone"; CERTS="<archive>/ramsey-zbs"
LEAN="$A/zbs_c2875f33/Bridge/P06LinesP0r12.lean"
T=rerun_20261119
gate() { while (( $(sysctl -n vm.loadavg | awk '{print $2}') >= 60 )) || \
               (( $(memory_pressure | awk '/free percentage/ {gsub("%", "", $NF); print $NF}') < 35 )); do sleep 20; done; }
# a refusal control: the command must exit nonzero and print a refusal; the run is counted only if both hold
refuse() { local name=$1; shift; local out rc; out=$("$@" 2>&1); rc=$?
  if (( rc != 0 )) && print -r -- "$out" | grep -qiE 'refus|not the pinned|not a full'; then print -r -- "REFUSED as required ($name): $(print -r -- "$out" | tail -1)"
  else print -r -- "CONTROL FAILED ($name): exit $rc: $(print -r -- "$out" | tail -2)"; fi; }
L25=3/10000000000000000000000000      # 3e-25
G26=5/100000000000000000000000000     # 5e-26

lines_stream() { cd $U/lines
  gate; ( date; uptime; nice -n 10 $FPY -I lines_B.py "$S/source.json" "$LEAN" "$LR/linesB_full_$T.json"; echo "EXIT $?"; date ) > linesB_full_$T.log 2>&1
  gate; ( date; uptime; nice -n 10 python3 -I lines_A.py "$S/source.json" "$CERTS/zbs_bank.json" "$LR/linesA_full_$T.json"; echo "EXIT $?"; date ) > linesA_full_$T.log 2>&1
  gate; ( date
    RED="--tamper=1019:2:$L25,1014:2:$L25,224:1:$L25,1059:2:$L25,934:2:$L25"
    echo '== RED (5 thinnest line-orientations lowered by 3e-25 > twice their gap): exactly these 5 must FAIL'
    echo '-- program A'; nice -n 10 python3 -I lines_A.py "$S/source.json" "$CERTS/zbs_bank.json" "$LR/linesA_red_$T.json" --lines=1019,1014,224,1059,934 $RED; echo "EXIT $?"
    echo '-- program B'; nice -n 10 $FPY -I lines_B.py "$S/source.json" "$LEAN" "$LR/linesB_red_$T.json" --lines=1019,1014,224,1059,934 $RED; echo "EXIT $?"
    echo '== GREEN (line 1019 orientation 2 lowered by 5e-26 < its gap 1.12e-25): must PASS'
    echo '-- program A'; nice -n 10 python3 -I lines_A.py "$S/source.json" "$CERTS/zbs_bank.json" "$LR/linesA_green_$T.json" --lines=1019 --tamper=1019:2:$G26; echo "EXIT $?"
    echo '-- program B'; nice -n 10 $FPY -I lines_B.py "$S/source.json" "$LEAN" "$LR/linesB_green_$T.json" --lines=1019 --tamper=1019:2:$G26; echo "EXIT $?"
    echo '== OPTION CONTROLS (audit L-1, L-2): malformed or unknown options must be refused'
    refuse 'lines_B tamper without =' nice -n 10 $FPY -I lines_B.py "$S/source.json" "$LEAN" "$LR/x.json" --lines=1019 --tamper 1019:2:$L25
    refuse 'lines_B unknown key' nice -n 10 $FPY -I lines_B.py "$S/source.json" "$LEAN" "$LR/x.json" --line=1019
    refuse 'lines_A tamper without =' nice -n 10 python3 -I lines_A.py "$S/source.json" "$CERTS/zbs_bank.json" "$LR/x.json" --lines=1019 --tamper 1019:2:$L25
    refuse 'lines_A unknown key' nice -n 10 python3 -I lines_A.py "$S/source.json" "$CERTS/zbs_bank.json" "$LR/x.json" --tamperr=1019:2:$L25
    date ) > lines_red_green_$T.log 2>&1
  echo LINES_STREAM_DONE; }

source_stream() { cd $U/source
  gate; ( date
    echo '== OPTION AND RANGE CONTROLS (audit S-1, S-2): each must be refused'
    for prog in A B; do
      if [ $prog = A ]; then PY=python3; else PY=$FPY; fi
      refuse "source_$prog --require without =" nice -n 10 $PY -I source_$prog.py "$S/source.json" "$S/source_cells.json" "$A/source_runs/x.json" --from=73200 --to=73302 --partial=yes --require 776/1000000000
      refuse "source_$prog misspelt key --requre" nice -n 10 $PY -I source_$prog.py "$S/source.json" "$S/source_cells.json" "$A/source_runs/x.json" --from=73200 --to=73302 --partial=yes --requre=776/1000000000
      refuse "source_$prog empty range --from=73302" nice -n 10 $PY -I source_$prog.py "$S/source.json" "$S/source_cells.json" "$A/source_runs/x.json" --from=73302
      refuse "source_$prog part range without --partial=yes" nice -n 10 $PY -I source_$prog.py "$S/source.json" "$S/source_cells.json" "$A/source_runs/x.json" --from=73200 --to=73302
      refuse "source_$prog option given twice" nice -n 10 $PY -I source_$prog.py "$S/source.json" "$S/source_cells.json" "$A/source_runs/x.json" --require=0 --require=1/1000000
    done
    date ) > source_option_controls_$T.log 2>&1
  TAG=$T zsh $U/source/run_2b.sh
  echo SOURCE_STREAM_DONE; }

cone_stream() { cd $U/cone
  gate; ( date
    echo '== assemble_full.py (pin added) re-run to a scratch path: each output must equal the recorded full certificate byte for byte'
    mkdir -p "$CR/rerun_tmp"
    for c in certK3 certCD3; do
      nice -n 10 python3 -I assemble_full.py "$CR/zbs_full.json" "$CERTS/$c.json" "$CR/cone_$c.json" "$CR/rerun_tmp/$c-full.json" "$CR/ctl_certs_0.json" "$CR/ctl_certs_1.json" > /dev/null; echo "EXIT $?"
      n=$(shasum -a 256 "$CR/rerun_tmp/$c-full.json" | cut -c1-64); o=$(shasum -a 256 "$CR/$c-full.json" | cut -c1-64)
      if [ "$n" = "$o" ]; then echo "$c-full.json reproduced byte for byte: $n"; else echo "MISMATCH $c-full.json: new $n, recorded $o"; fi
      cmp -s "$CR/rerun_tmp/$c-full.map.json" "$CR/$c-full.map.json" && echo "$c-full.map.json identical" || echo "MISMATCH $c-full.map.json"
    done
    rm -f "$CR/rerun_tmp"/*.json; rmdir "$CR/rerun_tmp"
    echo '== C-3 controls: a zbs file other than the pinned parse must be refused'
    refuse 'assemble_full with zbs_bank.json as zbs_full' nice -n 10 python3 -I assemble_full.py "$CERTS/zbs_bank.json" "$CERTS/certK3.json" "$CR/cone_certK3.json" "$CR/x.json" "$CR/ctl_certs_0.json"
    refuse 'check_full --zbs with zbs_bank.json' nice -n 10 python3 -I check_full.py "$CR/certK3-full.json" --zbs "$CERTS/zbs_bank.json" "$CR/certK3-full.map.json"
    date ) > assemble_pin_$T.log 2>&1
  gate; ( date; echo '== structure (check_full.py with the pin) on both full certificates'; zsh run_cone.sh structure; echo "EXIT $?"; date ) > structure_full_$T.log 2>&1
  gate; ( date; uptime; zsh run_cone.sh checkA certK3; echo "EXIT $?"; date ) > checkA_certK3-full_$T.log 2>&1
  gate; ( date; uptime; zsh run_cone.sh checkA certCD3; echo "EXIT $?"; date ) > checkA_certCD3-full_$T.log 2>&1
  echo CONE_STREAM_DONE; }

date; uptime
lines_stream & source_stream & cone_stream &
wait
date; echo ALL_RERUNS_DONE
