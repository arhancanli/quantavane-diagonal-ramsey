#!/bin/zsh
# Cone step (19 Nov 2026): the commands run, in order.  Large files live on the archive SSD ($D); logs here.
# usage: zsh run_cone.sh <step> ; steps: parse cone ctl assemble structure preflight checkA checkB red
# Machine gates (lab rules): each heavy step waits until the 1-minute load average is < 60 and runs under nice -n 10.
set -u
HERE=${0:A:h}
REPO=${HERE:h:h:h:h}
LANE=$REPO/research/tier2/ramsey-zbs
ZDIR="<archive>/ramsey-unconditional/zbs_c2875f33"
CERTS="<archive>/ramsey-zbs"
D="<archive>/ramsey-unconditional/cone"
FPY=${QV_FLINT_PY:-<flint-python>}
PYC=$(mktemp -d)        # empty pycache prefix: no stale bytecode next to a pinned .py is loaded
gate() { while (( $(sysctl -n vm.loadavg | awk '{print $2}') >= 60 )); do sleep 20; done; nice -n 10 "$@"; }
case $1 in
  parse) gate python3 -I $HERE/parse_zbs_full.py "$ZDIR" "$D/zbs_full.json" "$CERTS/zbs_bank.json" ;;
  cone) for c in certK3 certCD3; do gate python3 -I $HERE/cone.py "$D/zbs_full.json" "$CERTS/$c.json" "$D/cone_$c.json"; done ;;
  ctl) for k in 0 1; do gate $FPY -I $HERE/ctl_certs.py "$D/zbs_full.json" "$D/cone_certK3.json" $k 2 "$D/ctl_certs_$k.json" & done; wait ;;
  assemble) for c in certK3 certCD3; do
      gate python3 -I $HERE/assemble_full.py "$D/zbs_full.json" "$CERTS/$c.json" "$D/cone_$c.json" "$D/$c-full.json" \
        "$D/ctl_certs_0.json" "$D/ctl_certs_1.json"; done ;;
  structure) for c in certK3 certCD3; do
      gate python3 -I $HERE/check_full.py "$D/$c-full.json" --orig "$CERTS/$c.json" "$D/$c-full.map.json" \
        --zbs "$D/zbs_full.json" "$D/$c-full.map.json"; done ;;
  preflight) python3 -I -X pycache_prefix=$PYC $REPO/papers/diagonal-ramsey-2026/tools/preflight.py "$D/certK3-full.json" "$D/certCD3-full.json" ;;
  checkA) gate python3 -I -X pycache_prefix=$PYC $LANE/code/checkA/runA.py "$CERTS/zbs_bank.json" "$D/$2-full.json" "$D/$2-full_A.json" ;;
  checkB) gate $FPY -I -X pycache_prefix=$PYC $LANE/code/checkB/runB.py "$CERTS/zbs_bank.json" "$D/$2-full.json" "$D/$2-full_B.json" ;;
  red) gate python3 -I -X pycache_prefix=$PYC $LANE/code/red_controls.py "$CERTS/zbs_bank.json" "$D/certK3-full.json" $FPY "$D/red_K3full" ;;
  *) echo "unknown step $1"; exit 2 ;;
esac
