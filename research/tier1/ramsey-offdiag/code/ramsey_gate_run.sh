#!/bin/zsh
# usage: zsh ramsey_gate_run.sh <command...>   (waits for load < 60, then runs the command at nice 10)
setopt NO_BG_NICE
while true; do L=$(sysctl -n vm.loadavg | awk '{print int($2)}'); [[ $L -lt 60 ]] && break; echo "$(date +%T) waiting, load $L"; sleep 30; done
echo "$(date +%T) gate ok, load $L"
nice -n 10 "$@"; echo "EXIT $? $(date +%T)"
