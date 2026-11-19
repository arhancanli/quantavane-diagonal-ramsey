#!/bin/zsh
# Red controls: every tampered certificate must be REFUSED (exit 2) by the checker; the clean one accepted (exit 0).
# usage: zsh ramsey_offdiag_red.sh <bank_full.json> <clean cert> <red dir> <checker command...>
BANK=$1; CLEAN=$2; RD=$3; shift 3
fails=0
for f in $RD/r*.json; do
  out=$("$@" "$BANK" "$f" 2>&1); ec=$?
  if [[ $ec == 2 && "$out" == *REFUSED* ]]; then echo "refused OK  $(basename $f): $(echo $out | grep REFUSED | head -1)"; else echo "NOT REFUSED (exit $ec) $(basename $f)"; fails=$((fails+1)); fi
done
out=$("$@" "$BANK" "$CLEAN" 2>&1); ec=$?
if [[ $ec == 0 && "$out" == *'"ok": true'* ]]; then echo "green OK  clean certificate accepted"; else echo "GREEN FAILED (exit $ec)"; fails=$((fails+1)); fi
echo "red/green failures: $fails"
