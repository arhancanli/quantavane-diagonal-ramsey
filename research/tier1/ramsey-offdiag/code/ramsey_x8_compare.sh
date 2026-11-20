#!/bin/zsh
# Comparison v3 for the extended certificate at several claim starts, and for certCD3 (regression: must stay ALL_OK).
cd research/tier1/ramsey-offdiag
setopt NO_BG_NICE
gate() { while true; do L=$(sysctl -n vm.loadavg | awk '{print int($2)}'); [[ $L -lt 60 ]] && break; sleep 30; done; echo "$(date +%T) gate ok, load $L: $1"; }
IN="<archive>/ramsey-offdiag/inputs"
ZB="<archive>/ramsey-zbs/zbs_bank.json"
LW="<archive>/ramsey-unconditional/lw_5ec98f47/source.json"
run() { gate "$1 $2"; nice -n 10 python3 -I code/ramsey_offdiag_vs_published3.py "$ZB" "$IN/ep_959f46b06e/ep_extra.json" "$LW" "$IN/nss_e53b8cf11d/pq_cert_final.json" cert/offdiag_$1_v1.json runs/vs_published3_$1_${2:s#/#_#}.tsv $2 > runs/vs_published3_$1_${2:s#/#_#}.log 2>&1; echo "$1 $2 exit $?: $(grep ALL_OK runs/vs_published3_$1_${2:s#/#_#}.log)"; }
run cd3 201/1000
for gc in 31/200 4/25 33/200 17/100 7/40; do run x8 $gc; done
echo DONE
