"""Index of the route-tree Lemma D certificates: for every certs/<name>_m<k>.json whose bare control certs/<name>.json
exists, print control, bank a = -log x, certified a' = -log x', shift, leaves, SHA-256 (TSV).
Usage: python3 tree_index.py name1,name2,...  (a, a' in float from the exact rationals; the checkers prove x' only)"""
import glob
import hashlib
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))


def leaves(t):
    return 1 if t == 'L' else leaves(t[1]) + leaves(t[2])


if __name__ == '__main__':
    print('control\tcertificate\tbank_a\tcertified_a\tshift\tu_b\tleaves\tsha256')
    for nm in sys.argv[1].split(','):
        bare = json.load(open(os.path.join(HERE, 'certs', nm + '.json')))
        for p in sorted(glob.glob(os.path.join(HERE, 'certs', nm + '_m*.json'))):
            c = json.load(open(p))
            a = -math.log(Fr(bare['x'])); a2 = -math.log(Fr(c['control']['x']))
            assert all(Fr(c['control'][k]) == Fr(bare[k]) for k in ('p', 'mu', 'w', 'beta'))
            h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
            print('%s\t%s\t%.12f\t%.12f\t%.3e\t%s\t%d\t%s' % (nm, os.path.relpath(p, HERE), a, a2, a2 - a, c['u_b'],
                                                          leaves(c['tree']), h))
