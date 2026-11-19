#!/bin/zsh
# Reproduce the ramsey-zbs certificate from a fresh clone: fetch ZBS's tables (SHA-256 checked), build the certifiable
# control table, run the generator, refine the root control, materialise the certificate, run checkers A and B.
# usage: zsh reproduce.sh <workdir> <python-with-python-flint-0.9.0> [rounds (7)] [piece steps kp (5)] [x_D: second claim]
#        [cdmap.json: table controls certified by Lemma D (code/lemmaD/cdmap_*.json), second claim] [N: CD rounds]
# With cdmap and N (certCD3): the generator runs with the original table; then search/cd_rounds.py continues the refined
# state for N rounds with the table lowered (cdmap entries; root row by the designer's shift map) and a root_only round.
# With x_D, the root's control is replaced by the Lemma D control at x = x_D (second claim, assuming Theorem A), using
# the stored certificate code/lemmaD/certs/c1722_m300.json when x_D is its x (else genD builds one).
# Everything is single-threaded (nice 10).  Expected outputs are in RESULT.md (z and SHA-256 of cert.json).
set -e
W=$1; FPY=$2; R=${3:-7}; KP=${4:-5}; XD=${5:-}; CDMAP=${6:-}; CDR=${7:-}
HERE=${0:A:h}
mkdir -p $W/zbsdata
ZBS=https://raw.githubusercontent.com/w2ll2am/diagonal-ramsey/c2875f33a9d5c89f71c68f51b5767550570b5603/Solutions/P06/P0r12
for f in T TD0 TD1 TD2 TD3; do
  [ -s $W/zbsdata/$f.lean ] || curl -sSfL -A 'research-client' -o $W/zbsdata/$f.lean $ZBS/$f.lean
done
echo "[1/7] $(date) parse ZBS tables (parse_zbs.py checks SHA-256 of every file)"
python3 -I $HERE/search/parse_zbs.py $W/zbsdata/T.lean $W/zbsdata/zbs_bank.json
shasum -a 256 $W/zbsdata/zbs_bank.json
echo "[2/7] $(date) certifiable control table"
(cd $HERE/search && nice -n 10 python3 ctltable2.py $W/ctltable2.npz 1 > $W/ctltable2.log 2>&1)
TAB=$W/ctltable2.npz
if [ -n "$CDMAP" ] && [ -z "$CDR" ]; then
  echo "[2b/7] $(date) table lowered at the Lemma D controls of $CDMAP"
  (cd $HERE/code/lemmaD && shasum -a 256 -c MANIFEST.sha256 > /dev/null) || exit 1
  (cd $HERE/search && python3 cd_table.py $W/ctltable2.npz ${CDMAP:A} $W/ctltable2_cd.npz | tail -2)
  TAB=$W/ctltable2_cd.npz; export QV_CD_MAP=${CDMAP:A}
fi
echo "[3/7] $(date) generator, $R rounds, kp = $KP"
(cd $HERE/search && nice -n 10 python3 run_gen2.py $W/zbsdata/zbs_bank.json $TAB $R $W/gen.pkl $KP > $W/gen.log 2>&1)
grep ROOT $W/gen.log | tail -2
echo "[4/7] $(date) root control refinement"
(cd $HERE/search && nice -n 10 python3 root_refine.py $W/gen.pkl $W/gen_ref.pkl)
if [ -n "$CDMAP" ] && [ -n "$CDR" ]; then
  echo "[4c/7] $(date) $CDR rounds with the table lowered at the Lemma D controls of $CDMAP (root row: shift map)"
  (cd $HERE/code/lemmaD && shasum -a 256 -c MANIFEST.sha256 > /dev/null) || exit 1
  $FPY -I -c "import flint; assert flint.__version__ == '0.9.0', flint.__version__" || exit 1
  (cd $HERE/search && nice -n 10 python3 cd_rounds.py $W/gen_ref.pkl ${CDMAP:A} $CDR $W/gen_cd.pkl | grep ROOT) && mv $W/gen_cd.pkl $W/gen_ref.pkl
  export QV_CD_MAP=${CDMAP:A}
fi
if [ -n "$XD" ]; then
  echo "[4b/7] $(date) root re-optimised at the Lemma D control x = $XD"
  (cd $HERE/code/lemmaD && shasum -a 256 -c MANIFEST.sha256) || exit 1
  $FPY -I -c "import flint; assert flint.__version__ == '0.9.0', flint.__version__; print('python-flint', flint.__version__)" || exit 1
  if [ "$XD" = "329303794434999/1000000000000000" ]; then export QV_CD_CERT=$HERE/code/lemmaD/certs/c1722_m300.json; fi
  (cd $HERE/search && nice -n 10 python3 root_cd.py $W/gen_ref.pkl $W/gen_cd.pkl $XD ${CDMAP:+$QV_CD_CERT}) && mv $W/gen_cd.pkl $W/gen_ref.pkl
fi
echo "[5/7] $(date) materialise"
(cd $HERE/search && QV_FLINT_PY=$FPY nice -n 10 python3 materialise.py $W/gen_ref.pkl $W/zbsdata/zbs_bank.json $W/cert.json | tail -3)
shasum -a 256 $W/cert.json
echo "[6/7] $(date) checker A"
nice -n 10 python3 -I $HERE/code/checkA/runA.py $W/zbsdata/zbs_bank.json $W/cert.json $W/checkA.json
echo "[7/7] $(date) checker B"
nice -n 10 $FPY -I $HERE/code/checkB/runB.py $W/zbsdata/zbs_bank.json $W/cert.json $W/checkB.json
echo "END $(date)"
