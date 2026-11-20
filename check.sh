#!/bin/sh
# One command:
#   sh check.sh          standard check, about 30-40 minutes on one core
#   sh check.sh full     everything, about 2.5-3.5 hours on one core
# Needs: python3 (3.10 or later, standard library only) and a second Python with python-flint 0.9.0 exactly
# (python3 -m venv flintenv && flintenv/bin/pip install python-flint==0.9.0; then FLINT_PYTHON=flintenv/bin/python),
# curl, and about 1.5 GB of free disk in $WORK (default ./work) for the unpacked certificates.
#
# standard: fetch the public inputs (ZBS's bank tables and lines at c2875f33, Lu-Wang's source at 5ec98f47) and check
#           their SHA-256; parse ZBS's tables (pinned output hash); unpack the three full bank certificates and check
#           their SHA-256; preflight; checker B on the three banks; Theorem O by checkers A and B (both variants) and its
#           11 red controls; Theorem O-X8 (bank on ratios [1/8, 8]) by checkers A and B and its 12 red controls.
# full:     standard, plus checker A on both banks (about 30 minutes each), the 1,128 lines by two programs, Lu-Wang's
#           source criterion on 73,302 cells by two programs, and the third Lemma D checker on the 25 embedded
#           Lemma D certificates; checker A on the third bank (certX8-full).
set -eu
cd "$(dirname "$0")"
MODE=${1:-standard}
ROOT=$(pwd)
PY=${PYTHON:-python3}
FPY=${FLINT_PYTHON:-}
WORK=${WORK:-$ROOT/work}
fail() { echo "CHECK FAILED: $*"; exit 1; }
[ -n "$FPY" ] || fail "set FLINT_PYTHON to a Python with python-flint 0.9.0 (see the top of this file)"
"$FPY" -c 'import flint, sys; sys.exit(0 if flint.__version__ == "0.9.0" else 1)' || fail "FLINT_PYTHON must have python-flint 0.9.0"
mkdir -p "$WORK/inputs" "$WORK/out"
PYC=$(mktemp -d)          # empty bytecode cache: no stale .pyc next to a pinned .py can be loaded
IN=$WORK/inputs; OUT=$WORK/out
sha() { "$PY" -c 'import hashlib,sys; h=hashlib.sha256(); f=open(sys.argv[1],"rb"); [h.update(c) for c in iter(lambda: f.read(1<<22), b"")]; print(h.hexdigest())' "$1"; }
pin() { [ "$(sha "$1")" = "$2" ] || fail "SHA-256 of $1 is not $2"; }

echo "1. Public inputs (fetched from GitHub at fixed commits, SHA-256 checked)"
ZBS=https://raw.githubusercontent.com/w2ll2am/diagonal-ramsey/c2875f33a9d5c89f71c68f51b5767550570b5603
LW=https://raw.githubusercontent.com/sichen-wang/diagonal-ramsey-numbers/5ec98f470c43be747ea638f796d1494f9b4c0177
mkdir -p "$IN/zbs"
for f in T TD0 TD1 TD2 TD3; do
  [ -s "$IN/zbs/$f.lean" ] || curl -sSfL -A research-client -o "$IN/zbs/$f.lean" "$ZBS/Solutions/P06/P0r12/$f.lean"
done
[ -s "$IN/P06LinesP0r12.lean" ] || curl -sSfL -A research-client -o "$IN/P06LinesP0r12.lean" "$ZBS/Bridge/P06LinesP0r12.lean"
[ -s "$IN/source.json" ] || curl -sSfL -A research-client -o "$IN/source.json" "$LW/data/source.json"
[ -s "$IN/source_cells.json" ] || curl -sSfL -A research-client -o "$IN/source_cells.json" "$LW/data/source_cells.json"
pin "$IN/P06LinesP0r12.lean" aeac27eba632215b908461f7ee42c886ff4d14bd5b5b6ad5cd5b5a0d9d4556ba
pin "$IN/source.json" f3e4a4eaf3f778ae125466eb6d47647a38fd38430fdcdffe8c5f774f9718c08c
pin "$IN/source_cells.json" 055d86954ba7bc4e636ded1c0bb603a142ca738174e79a997f17b0c51c524bff
"$PY" -I research/tier2/ramsey-zbs/search/parse_zbs.py "$IN/zbs/T.lean" "$IN/zbs_bank.json" > "$OUT/parse.log"
pin "$IN/zbs_bank.json" 2946c6561f562ea01a5f9b60ac0812c689af71985c60378e11c89e8cdc003bf0
echo "   ok (the parser checks the SHA-256 of each ZBS table; zbs_bank.json has the pinned hash)"

echo "2. The three full bank certificates"
for c in certK3-full certCD3-full certX8-full; do
  [ -s "$WORK/$c.json" ] || "$PY" -c 'import gzip,shutil,sys; shutil.copyfileobj(gzip.open(sys.argv[1]), open(sys.argv[2],"wb"), 1<<22)' "certs/$c.json.gz" "$WORK/$c.json"
done
pin "$WORK/certK3-full.json" 38091eed691b3ffa954d81e9658885cb68fb30e4e46ae76ddc376444f69ee468
pin "$WORK/certCD3-full.json" 32bcafd3fccbf094c83cc942669b3b843f09a3b10f87a6bd6a465d112bb07af8
pin "$WORK/certX8-full.json" d3c8cd100f97d7cfcf4ac354d8bd71d5cf6e3c627782ef1049d56ff0177f6e86
echo "   ok"

echo "3. Preflight (pins of the frozen Lemma D code; structure; Theorem 5.7's proviso)"
"$PY" -I -X pycache_prefix="$PYC" papers/diagonal-ramsey-2026/tools/preflight.py "$WORK/certK3-full.json" "$WORK/certCD3-full.json" "$WORK/certX8-full.json" | tee "$OUT/preflight.log"
grep -q "PREFLIGHT OK" "$OUT/preflight.log" || fail preflight

zcheck() {  # file, expected z
  grep -q '"ok": true' "$1" && grep -q "\"z\": \"$2\"" "$1" || fail "$1 does not accept z = $2"
}
echo "4. Checker B (Arb balls, python-flint) on the three banks"
"$FPY" -I -X pycache_prefix="$PYC" research/tier2/ramsey-zbs/code/checkB/runB.py "$IN/zbs_bank.json" "$WORK/certK3-full.json" "$OUT/K3_B.json" > "$OUT/K3_B.log" 2>&1 || { tail -5 "$OUT/K3_B.log"; fail "checker B, certK3-full"; }
zcheck "$OUT/K3_B.json" 1248056263241/1000000000000
"$FPY" -I -X pycache_prefix="$PYC" research/tier2/ramsey-zbs/code/checkB/runB.py "$IN/zbs_bank.json" "$WORK/certCD3-full.json" "$OUT/CD3_B.json" > "$OUT/CD3_B.log" 2>&1 || { tail -5 "$OUT/CD3_B.log"; fail "checker B, certCD3-full"; }
zcheck "$OUT/CD3_B.json" 311946616731/250000000000
"$FPY" -I -X pycache_prefix="$PYC" research/tier2/ramsey-zbs/code/checkB/runB.py "$IN/zbs_bank.json" "$WORK/certX8-full.json" "$OUT/X8_B.json" > "$OUT/X8_B.log" 2>&1 || { tail -5 "$OUT/X8_B.log"; fail "checker B, certX8-full"; }
zcheck "$OUT/X8_B.json" 1248049473997/1000000000000
echo "   certK3-full: z = 1248056263241/10^12; certCD3-full: z = 311946616731/250000000000; certX8-full: z = 1248049473997/10^12"

echo "5. Theorem O (off-diagonal) by checkers A and B, and its red controls"
O=research/tier1/ramsey-offdiag
"$PY" -I $O/code/ramsey_offdiag_checkA.py "$WORK/certCD3-full.json" $O/cert/offdiag_cd3_v1.json "$OUT/O_cd3_A.json" > "$OUT/O_cd3_A.log" 2>&1 || fail "Theorem O, checker A"
"$FPY" -I $O/code/ramsey_offdiag_checkB.py "$WORK/certCD3-full.json" $O/cert/offdiag_cd3_v1.json "$OUT/O_cd3_B.json" > "$OUT/O_cd3_B.log" 2>&1 || fail "Theorem O, checker B"
"$PY" -I $O/code/ramsey_offdiag_checkA.py "$WORK/certK3-full.json" $O/cert/offdiag_k3_v1.json "$OUT/O_k3_A.json" > "$OUT/O_k3_A.log" 2>&1 || fail "Theorem O (K3 variant), checker A"
for f in O_cd3_A O_cd3_B O_k3_A; do grep -q '"ok": true' "$OUT/$f.json" || fail "$f"; done
RD="$WORK/red"; rm -rf "$RD"; mkdir -p "$RD"
"$PY" -I $O/code/ramsey_offdiag_red_make.py "$WORK/certCD3-full.json" $O/cert/offdiag_cd3_v1.json "$RD" > "$OUT/O_red_make.log" 2>&1
n=0
for f in "$RD"/r*.json; do
  set +e; "$PY" -I $O/code/ramsey_offdiag_checkA.py "$WORK/certCD3-full.json" "$f" > "$OUT/red_one.log" 2>&1; ec=$?; set -e
  [ $ec = 2 ] && grep -q REFUSED "$OUT/red_one.log" || fail "red control $(basename "$f") was not refused"
  n=$((n+1))
done
[ $n -ge 11 ] || fail "expected at least 11 red controls, found $n"
echo "   Theorem O accepted by A and B; $n red controls refused"
echo "5b. Theorem O-X8 (bank on ratios [1/8, 8]) by checkers A and B, and its red controls"
"$PY" -I $O/code/ramsey_offdiag_checkA.py "$WORK/certX8-full.json" $O/cert/offdiag_x8_v1.json "$OUT/O_x8_A.json" > "$OUT/O_x8_A.log" 2>&1 || fail "Theorem O-X8, checker A"
"$FPY" -I $O/code/ramsey_offdiag_checkB.py "$WORK/certX8-full.json" $O/cert/offdiag_x8_v1.json "$OUT/O_x8_B.json" > "$OUT/O_x8_B.log" 2>&1 || fail "Theorem O-X8, checker B"
for f in O_x8_A O_x8_B; do grep -q '"ok": true' "$OUT/$f.json" || fail "$f"; done
RD="$WORK/red_x8"; rm -rf "$RD"; mkdir -p "$RD"
"$PY" -I $O/code/ramsey_offdiag_red_make.py "$WORK/certX8-full.json" $O/cert/offdiag_x8_v1.json "$RD" > "$OUT/O_x8_red_make.log" 2>&1
n=0
for f in "$RD"/r*.json; do
  set +e; "$PY" -I $O/code/ramsey_offdiag_checkA.py "$WORK/certX8-full.json" "$f" > "$OUT/red_one.log" 2>&1; ec=$?; set -e
  [ $ec = 2 ] && grep -q REFUSED "$OUT/red_one.log" || fail "red control (X8) $(basename "$f") was not refused"
  n=$((n+1))
done
[ $n -ge 12 ] || fail "expected at least 12 red controls for Theorem O-X8, found $n"
echo "   Theorem O-X8 accepted by A and B; $n red controls refused"

if [ "$MODE" = full ]; then
  echo "6. Checker A (exact rationals and dyadic intervals) on the three banks (about 30 minutes each)"
  "$PY" -I -X pycache_prefix="$PYC" research/tier2/ramsey-zbs/code/checkA/runA.py "$IN/zbs_bank.json" "$WORK/certK3-full.json" "$OUT/K3_A.json" > "$OUT/K3_A.log" 2>&1 || fail "checker A, certK3-full"
  zcheck "$OUT/K3_A.json" 1248056263241/1000000000000
  "$PY" -I -X pycache_prefix="$PYC" research/tier2/ramsey-zbs/code/checkA/runA.py "$IN/zbs_bank.json" "$WORK/certCD3-full.json" "$OUT/CD3_A.json" > "$OUT/CD3_A.log" 2>&1 || fail "checker A, certCD3-full"
  zcheck "$OUT/CD3_A.json" 311946616731/250000000000
  "$PY" -I -X pycache_prefix="$PYC" research/tier2/ramsey-zbs/code/checkA/runA.py "$IN/zbs_bank.json" "$WORK/certX8-full.json" "$OUT/X8_A.json" > "$OUT/X8_A.log" 2>&1 || fail "checker A, certX8-full"
  zcheck "$OUT/X8_A.json" 1248049473997/1000000000000
  echo "7. The 1,128 lines of ZBS's list, valid for all lambda > 0 (two programs)"
  U=papers/diagonal-ramsey-2026/unconditional
  "$PY" -I $U/lines/lines_A.py "$IN/source.json" "$IN/zbs_bank.json" "$OUT/linesA.json" > "$OUT/linesA.log" 2>&1 || fail lines_A
  "$FPY" -I $U/lines/lines_B.py "$IN/source.json" "$IN/P06LinesP0r12.lean" "$OUT/linesB.json" > "$OUT/linesB.log" 2>&1 || fail lines_B
  echo "8. Lu-Wang's source criterion on [10^-16, 1] (two programs, 73,302 cells each)"
  "$PY" -I $U/source/source_A.py "$IN/source.json" "$IN/source_cells.json" "$OUT/sourceA.json" > "$OUT/sourceA.log" 2>&1 || fail source_A
  "$FPY" -I $U/source/source_B.py "$IN/source.json" "$IN/source_cells.json" "$OUT/sourceB.json" > "$OUT/sourceB.log" 2>&1 || fail source_B
  grep -q "ALL CELLS CERTIFIED" "$OUT/sourceA.log" && grep -q "ALL CELLS CERTIFIED" "$OUT/sourceB.log" || fail "source criterion"
  echo "9. Third Lemma D checker on the 25 Lemma D certificates embedded in certCD3-full"
  mkdir -p "$WORK/lemmaD"
  "$PY" -I papers/diagonal-ramsey-2026/evidence/extract_cd3_lemmaD.py "$WORK/certCD3-full.json" research/tier2/ramsey-zbs/code/lemmaD/cdmap_cd3.json research/tier2/ramsey-zbs/code/lemmaD "$WORK/lemmaD" > "$OUT/lemmaD_extract.log"
  "$PY" -I research/tier2/ramsey-lemma/cert_independent/checkD_C.py "$WORK"/lemmaD/*.json > "$OUT/checkD_C.log" 2>&1 || fail "checkD_C"
fi
echo "ALL CHECKS PASSED ($MODE): R(k,k) <= ceil(C e^{z k}) with z = 311946616731/250000000000 (e^z <= 3.4826255125),"
echo "and with z = 1248056263241/10^12 (e^z <= 3.4835652388) without Lemma D; Theorem O on [1/5, 1]; Theorem O-X8 on [1/8, 1]. Logs in $OUT."
