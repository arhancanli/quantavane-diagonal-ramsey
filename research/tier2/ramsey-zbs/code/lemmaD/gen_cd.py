"""ramsey-zbs wrapper (not part of the frozen set): build a Lemma D certificate for one TARGET control and write the
'lemmaD' dict as JSON.  usage: <flint-python> gen_cd.py p mu w beta x out.json   (exit 1 if the branch and bound fails)"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genD
p, mu, w, beta, x, out = sys.argv[1:7]
lem = genD.build(p, mu, w, beta, x)
if lem is None: sys.exit(1)
json.dump(lem, open(out, 'w'))
