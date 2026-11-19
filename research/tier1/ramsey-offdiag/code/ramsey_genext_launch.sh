#!/bin/zsh
# Float gate: extended-range generator (RMAX = 8), 6 rounds, kp = 5; detached; load gate < 60; <= 4 BLAS threads.
setopt NO_BG_NICE
D="<archive>/ramsey-offdiag/genext"
while true; do L=$(sysctl -n vm.loadavg | awk '{print int($2)}'); [[ $L -lt 60 ]] && break; echo "$(date +%T) waiting, load $L"; sleep 30; done
echo "$(date +%T) gate ok, load $L; $(memory_pressure | tail -1); disk $(df -g / | tail -1 | awk '{print $4}') GB"
export QV_RMAX=8 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 VECLIB_MAXIMUM_THREADS=4 MKL_NUM_THREADS=4
PY=<python>
nice -n 10 $PY -I research/tier1/ramsey-offdiag/code/ramsey_gen2_ext_run.py \
  "<archive>/ramsey-zbs/zbs_bank.json" "<archive>/ramsey-zbs/ctltable2.npz" \
  6 "$D/genext_r8_kp5.pkl" 5
echo "EXIT $? $(date +%T)"
