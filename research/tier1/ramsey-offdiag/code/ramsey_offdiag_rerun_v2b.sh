#!/bin/zsh
# Comparison v2 rerun after the intercept fix (Phi_i(g)/g maximum taken at either end). Gate: load < 60.
cd research/tier1/ramsey-offdiag
setopt NO_BG_NICE
gate() { while true; do L=$(sysctl -n vm.loadavg | awk '{print int($2)}'); [[ $L -lt 60 ]] && break; echo "$(date +%T) waiting, load $L"; sleep 30; done; echo "$(date +%T) gate ok, load $L"; }
IN="<archive>/ramsey-offdiag/inputs"
ZB="<archive>/ramsey-zbs/zbs_bank.json"
LW="<archive>/ramsey-unconditional/lw_5ec98f47/source.json"
for v in cd3 k3; do
  gate; nice -n 10 python3 -I code/ramsey_offdiag_vs_published2.py "$ZB" "$IN/ep_959f46b06e/ep_extra.json" "$LW" "$IN/nss_e53b8cf11d/pq_cert_final.json" cert/offdiag_${v}_v1.json runs/vs_published2_${v}_v1.tsv > runs/vs_published2_${v}_v1.log 2>&1; echo "vs2 $v exit $?"
done
echo DONE
