#!/bin/zsh
# Red controls for the X8 certificate including r12 (both checkers).
cd research/tier1/ramsey-offdiag
setopt NO_BG_NICE
gate() { while true; do L=$(sysctl -n vm.loadavg | awk '{print int($2)}'); [[ $L -lt 60 ]] && break; sleep 30; done; echo "$(date +%T) gate ok, load $L: $1"; }
X="<archive>/ramsey-offdiag/genext/certX8-full.json"
FPY=<flint-python>
RD="<archive>/ramsey-offdiag/red_x8_v2"; C=cert/offdiag_x8_v1.json
gate make; nice -n 10 python3 -I code/ramsey_offdiag_red_make.py "$X" $C "$RD"
gate redA; zsh code/ramsey_offdiag_red.sh "$X" $C "$RD" nice -n 10 python3 -I $PWD/code/ramsey_offdiag_checkA.py > runs/red_checkA_x8_v2.log 2>&1
gate redB; zsh code/ramsey_offdiag_red.sh "$X" $C "$RD" nice -n 10 $FPY -I $PWD/code/ramsey_offdiag_checkB.py > runs/red_checkB_x8_v2.log 2>&1
grep -h -E 'r12|failures' runs/red_checkA_x8_v2.log runs/red_checkB_x8_v2.log
