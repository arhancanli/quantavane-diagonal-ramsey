#!/bin/zsh
# Gate: load < 60 before the run (lab rule); one process, nice 10.
setopt NO_BG_NICE
while true; do L=$(sysctl -n vm.loadavg | awk '{print int($2)}'); [[ $L -lt 60 ]] && break; echo "$(date +%T) waiting, load $L"; sleep 30; done
echo "$(date +%T) gate ok, load $L; memory $(memory_pressure | tail -1)"
PY=<python>
nice -n 10 $PY -I research/tier1/ramsey-offdiag/code/ramsey_rootgate.py "$@"
echo "EXIT $? $(date +%T)"
