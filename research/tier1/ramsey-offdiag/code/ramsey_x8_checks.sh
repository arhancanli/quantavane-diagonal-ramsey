#!/bin/zsh
# Checks of the extended off-diagonal certificate (bank certX8-full): checkers A, B, red controls (both), comparison v2.
cd research/tier1/ramsey-offdiag
setopt NO_BG_NICE
gate() { while true; do L=$(sysctl -n vm.loadavg | awk '{print int($2)}'); [[ $L -lt 60 ]] && break; sleep 30; done; echo "$(date +%T) gate ok, load $L: $1"; }
X="<archive>/ramsey-offdiag/genext/certX8-full.json"
FPY=<flint-python>
IN="<archive>/ramsey-offdiag/inputs"
ZB="<archive>/ramsey-zbs/zbs_bank.json"
LW="<archive>/ramsey-unconditional/lw_5ec98f47/source.json"
RD="<archive>/ramsey-offdiag/red_x8_v1"
C=cert/offdiag_x8_v1.json
gate checkA; nice -n 10 python3 -I code/ramsey_offdiag_checkA.py "$X" $C runs/checkA_x8_v1.json > runs/checkA_x8_v1.log 2>&1; echo "A exit $?"
gate checkB; nice -n 10 $FPY -I code/ramsey_offdiag_checkB.py "$X" $C runs/checkB_x8_v1.json > runs/checkB_x8_v1.log 2>&1; echo "B exit $?"
gate red_make; nice -n 10 python3 -I code/ramsey_offdiag_red_make.py "$X" $C "$RD"
gate redA; zsh code/ramsey_offdiag_red.sh "$X" $C "$RD" nice -n 10 python3 -I $PWD/code/ramsey_offdiag_checkA.py > runs/red_checkA_x8_v1.log 2>&1; tail -1 runs/red_checkA_x8_v1.log
gate redB; zsh code/ramsey_offdiag_red.sh "$X" $C "$RD" nice -n 10 $FPY -I $PWD/code/ramsey_offdiag_checkB.py > runs/red_checkB_x8_v1.log 2>&1; tail -1 runs/red_checkB_x8_v1.log
for gc in 3/20 4/25 17/100; do gate "vs2 $gc"; nice -n 10 python3 -I code/ramsey_offdiag_vs_published2.py "$ZB" "$IN/ep_959f46b06e/ep_extra.json" "$LW" "$IN/nss_e53b8cf11d/pq_cert_final.json" $C runs/vs_published2_x8_${gc:s#/#_#}.tsv $gc > runs/vs_published2_x8_${gc:s#/#_#}.log 2>&1; echo "vs2 $gc exit $?"; done
echo X8 CHECKS DONE
