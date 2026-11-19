"""Extra cross-check (scratch): raw pieces of zbs_full.json vs the older regex parser code/zbs_pieces.py, and
degenerate intervals (lo >= hi) in pieces / source cells."""
import sys, json, re, os, glob
from fractions import Fraction as Fr
sys.path.insert(0, 'research/tier2/ramsey-zbs/code')
import zbs_pieces
z = json.load(open(sys.argv[1]))
root = sys.argv[2] + '/Solutions/P06/P0r12'
def norm(o):
    if isinstance(o, (list, tuple)):
        if len(o) == 2 and isinstance(o[0], str) and o[0] in ('zr', 'zc', 'z'):
            return (o[0], int(o[1]))
        return [norm(x) for x in o]
    if isinstance(o, dict):
        return {k: norm(v) for k, v in o.items()}
    if isinstance(o, str):
        return o if o in ('leaf', 'route') else Fr(o)
    return o
n = 0; bad = []
seen = set()
for f in sorted(glob.glob(root + '/D*.lean')):
    for name, d in zbs_pieces.pieces(f).items():
        i, j = map(int, re.match(r'rp(\d+)_(\d+)', name).groups())
        mine = z['raw'][i]['pieces'][j]
        a, b = norm(mine), norm(d)
        if a != b: bad.append(name)
        n += 1; seen.add((i, j))
tot = sum(len(P['pieces']) for P in z['raw'])
print('raw pieces compared with zbs_pieces.py:', n, 'of', tot, 'mismatches', len(bad), bad[:5], 'all covered', len(seen) == tot)
deg = []
for i, P in enumerate(z['raw']):
    for j, p in enumerate(P['pieces']):
        if not Fr(p['lo']) < Fr(p['hi']): deg.append(('raw', i, j))
for i, Q in enumerate(z['closed']):
    for j, p in enumerate(Q['pieces']):
        if not Fr(p['lo']) < Fr(p['hi']): deg.append(('closed', i, j))
for h, s in enumerate(z['sources']):
    for j, c in enumerate(s['cells']):
        if not Fr(c['lo']) < Fr(c['hi']): deg.append(('src', h, j))
print('degenerate intervals:', len(deg), deg[:10])
