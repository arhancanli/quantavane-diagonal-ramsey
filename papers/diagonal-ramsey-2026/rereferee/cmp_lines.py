import json, re, sys
from fractions import Fraction as F
bank = json.load(open(sys.argv[1]))
lean = open(sys.argv[2]).read()
print(type(bank), list(bank.keys()) if isinstance(bank, dict) else len(bank))
L = bank['lines']
print('bank lines', len(L), L[0])
body = lean[lean.index('theorem lu_wang_lines_P0r12'):]
body = body[:body.index(': List (ℚ × ℚ)')]
pairs = re.findall(r'\(\(\((-?\d+)/(\d+) : ℚ\), \((-?\d+)/(\d+) : ℚ\)\)', body)
if not pairs:
    pairs = re.findall(r'\(\((-?\d+)/(\d+) : ℚ\), \((-?\d+)/(\d+) : ℚ\)\)', body)
print('lean pairs', len(pairs))
def tofr(x):
    if isinstance(x, (list, tuple)) and len(x) == 2: return F(int(x[0]), int(x[1]))
    return F(x)
lp = [(F(int(a), int(b)), F(int(c), int(d))) for a, b, c, d in pairs]
bp = []
for e in L:
    if isinstance(e, dict): bp.append((tofr(e['c']), tofr(e['d'])))
    else: bp.append((tofr(e[0]), tofr(e[1])))
print('equal in order:', lp == bp)
print('equal as sets:', sorted(lp) == sorted(bp))
# also check per-file theorems match aggregate list
import glob, os
d = os.path.dirname(sys.argv[2])
thm = {}
for fn in glob.glob(os.path.join(d, 'P06LinesP0r12_*.lean')):
    s = open(fn).read()
    for m in re.finditer(r'theorem line_P0r12_(\d+) : ∀ s : ℝ, 0 < s →\s+symmetricProfile luWangSource 1 s ≤ \(\(\((-?\d+)/(\d+) : ℚ\)\) : ℝ\) \+ \(\(\((-?\d+)/(\d+) : ℚ\)\) : ℝ\) \* s', s):
        i = int(m.group(1)); thm[i] = (F(int(m.group(2)), int(m.group(3))), F(int(m.group(4)), int(m.group(5))))
print('per-file theorems parsed', len(thm))
print('per-file == aggregate in index order:', [thm[i] for i in range(len(thm))] == lp)
