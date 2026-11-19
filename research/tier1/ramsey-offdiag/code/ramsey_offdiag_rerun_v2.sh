#!/bin/zsh
# Reruns after the 19 Nov referee (PASS WITH FIXES): checker A (exact ceilings, g_lo pin) on both certificates,
# red controls for both checkers (11 tampers), comparison v2 (fully generous baseline). Gate: load < 60 before each step.
cd research/tier1/ramsey-offdiag
setopt NO_BG_NICE
gate() { while true; do L=$(sysctl -n vm.loadavg | awk '{print int($2)}'); [[ $L -lt 60 ]] && break; echo "$(date +%T) waiting, load $L"; sleep 30; done; echo "$(date +%T) gate ok, load $L"; }
CD="<archive>/ramsey-unconditional/cone/certCD3-full.json"
K3="<archive>/ramsey-unconditional/cone/certK3-full.json"
FPY=<flint-python>
IN="<archive>/ramsey-offdiag/inputs"
ZB="<archive>/ramsey-zbs/zbs_bank.json"
LW="<archive>/ramsey-unconditional/lw_5ec98f47/source.json"
RD="<archive>/ramsey-offdiag/red_cd3_v2"
gate; nice -n 10 python3 -I code/ramsey_offdiag_checkA.py "$CD" cert/offdiag_cd3_v1.json runs/checkA_cd3_v2.json > runs/checkA_cd3_v2.log 2>&1; echo "checkA cd3 exit $?"
gate; nice -n 10 python3 -I code/ramsey_offdiag_checkA.py "$K3" cert/offdiag_k3_v1.json runs/checkA_k3_v2.json > runs/checkA_k3_v2.log 2>&1; echo "checkA k3 exit $?"
gate; nice -n 10 python3 -I code/ramsey_offdiag_red_make.py "$CD" cert/offdiag_cd3_v1.json "$RD"
gate; zsh code/ramsey_offdiag_red.sh "$CD" cert/offdiag_cd3_v1.json "$RD" nice -n 10 python3 -I $PWD/code/ramsey_offdiag_checkA.py > runs/red_checkA_cd3_v2.log 2>&1; tail -1 runs/red_checkA_cd3_v2.log
gate; zsh code/ramsey_offdiag_red.sh "$CD" cert/offdiag_cd3_v1.json "$RD" nice -n 10 $FPY -I $PWD/code/ramsey_offdiag_checkB.py > runs/red_checkB_cd3_v2.log 2>&1; tail -1 runs/red_checkB_cd3_v2.log
gate; nice -n 10 python3 -I code/ramsey_offdiag_vs_published2.py "$ZB" "$IN/ep_959f46b06e/ep_extra.json" "$LW" "$IN/nss_e53b8cf11d/pq_cert_final.json" cert/offdiag_cd3_v1.json runs/vs_published2_cd3_v1.tsv > runs/vs_published2_cd3_v1.log 2>&1; echo "vs2 cd3 exit $?"
gate; nice -n 10 python3 -I code/ramsey_offdiag_vs_published2.py "$ZB" "$IN/ep_959f46b06e/ep_extra.json" "$LW" "$IN/nss_e53b8cf11d/pq_cert_final.json" cert/offdiag_k3_v1.json runs/vs_published2_k3_v1.tsv > runs/vs_published2_k3_v1.log 2>&1; echo "vs2 k3 exit $?"
echo DONE
