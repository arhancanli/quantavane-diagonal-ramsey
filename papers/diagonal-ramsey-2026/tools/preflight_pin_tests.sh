#!/bin/bash
# Pin tests for tools/preflight.py in a sandbox copy of the pinned tree.
B=$1; R=.
rm -rf $B/repo; mkdir -p $B/repo/papers/diagonal-ramsey-2026/tools $B/repo/research/tier2/ramsey-zbs/code/checkA
cp -R $R/research/tier2/ramsey-zbs/code/lemmaD $B/repo/research/tier2/ramsey-zbs/code/
rm -rf $B/repo/research/tier2/ramsey-zbs/code/lemmaD/__pycache__
cp $R/research/tier2/ramsey-zbs/code/checkA/ivA.py $B/repo/research/tier2/ramsey-zbs/code/checkA/
cp $R/papers/diagonal-ramsey-2026/tools/preflight.py $B/repo/papers/diagonal-ramsey-2026/tools/
CERT=$R/research/tier2/ramsey-zbs/code/lemmaD/certs/root3_x337059333092731.json
L=$B/repo/research/tier2/ramsey-zbs/code/lemmaD
run() { echo "$1: $(python3 -I $B/repo/papers/diagonal-ramsey-2026/tools/preflight.py $CERT | tail -1)"; }
run "untouched"
cp $L/checkD_A.py $L/checkD_A.bak; echo '# edit' >> $L/checkD_A.py; run "edit checkD_A"
cp $L/MANIFEST.sha256 $L/MANIFEST.bak
NEW=$(shasum -a 256 $L/checkD_A.py | cut -d' ' -f1)
sed "s/^[0-9a-f]*  checkD_A.py$/$NEW  checkD_A.py/" $L/MANIFEST.bak > $L/MANIFEST.sha256; run "edit checkD_A + regenerate its manifest line"
grep -v 'checkD_A.py' $L/MANIFEST.bak > $L/MANIFEST.sha256; run "edit checkD_A + delete its manifest line"
head -5 $L/MANIFEST.bak > $L/MANIFEST.sha256; run "manifest truncated to 5 lines"
cp $L/MANIFEST.bak $L/MANIFEST.sha256; cp $L/checkD_A.bak $L/checkD_A.py; run "restored"
echo '# x' >> $B/repo/research/tier2/ramsey-zbs/code/checkA/ivA.py; run "edit checkA/ivA.py"
cp $R/research/tier2/ramsey-zbs/code/checkA/ivA.py $B/repo/research/tier2/ramsey-zbs/code/checkA/; run "restored ivA"
