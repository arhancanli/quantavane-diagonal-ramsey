# independent re-parse of ZBS tables; compare with zbs_bank.json
import sys, re, json
from fractions import Fraction as F
d = sys.argv[1]; bankp = sys.argv[2]
bank = json.load(open(bankp))
files = {fn: open(d + '/' + fn).read() for fn in ['T.lean','TD0.lean','TD1.lean','TD2.lean','TD3.lean']}
# every FQ.mk occurrence anywhere must be in one of the two known forms
allsrc = '\n'.join(files.values())
n_any = allsrc.count('FQ.mk')
pat = re.compile(r'\(FQ\.mk \((\.ofNat|\.negSucc) \(nat_lit (\d+)\)\) \(nat_lit (\d+)\)\)')
n_pat = len(pat.findall(allsrc))
print('FQ.mk total', n_any, 'matched by pattern', n_pat)
# other numeric-looking literal forms that could hide values
print('Int.negSucc', allsrc.count('Int.negSucc'), 'Int.ofNat', allsrc.count('Int.ofNat'), 'qq ', allsrc.count('qq '), ' : ℚ)', allsrc.count(': ℚ)'))
def fq(m):
    n = int(m.group(2)); den = int(m.group(3)) + 1
    if m.group(1) == '.negSucc': n = -(n + 1)
    return F(n, den)
defs = {}
for fn, t in files.items():
    for line in t.split('\n'):
        m = re.match(r'def (\S+) : (.*?) := (.*)$', line)
        if m:
            assert m.group(1) not in defs, m.group(1)
            defs[m.group(1)] = (m.group(2), m.group(3))
print('defs', len(defs))
# controls: structure literal with 7 FQ
bad = 0
for k in range(918):
    ty, body = defs['c%d' % k]; assert ty == 'CtrlF'
    v = [fq(m) for m in pat.finditer(body)]
    assert body.startswith('⟨') and body.endswith('⟩') and len(v) == 7
    if [F(s) for s in bank['ctl'][k]] != v: bad += 1
print('ctl mismatches', bad)
# profiles: parse structure ⟨p, [xs], [ys]⟩ explicitly by brackets
def prof(body):
    assert body.startswith('⟨') and body.endswith('⟩')
    inner = body[1:-1]
    i1 = inner.index('['); j1 = inner.index(']', i1)
    i2 = inner.index('[', j1); j2 = inner.index(']', i2)
    assert inner[j2+1:].strip() == ''
    p = [fq(m) for m in pat.finditer(inner[:i1])]; assert len(p) == 1
    xs = [fq(m) for m in pat.finditer(inner[i1:j1])]; ys = [fq(m) for m in pat.finditer(inner[i2:j2])]
    assert inner[i1:j1].count('FQ.mk') == len(xs) and inner[i2:j2].count('FQ.mk') == len(ys)
    return p[0], xs, ys
for key, pre, n in [('raw','r',1902),('closed','q',1003)]:
    bad = 0; badlen = 0
    for k in range(n):
        ty, body = defs['%s%d' % (pre, k)]; assert ty == 'ProfF'
        p, xs, ys = prof(body)
        if len(xs) != len(ys): badlen += 1
        b = bank[key][k]
        if F(b['p']) != p or [F(s) for s in b['xs']] != xs or [F(s) for s in b['ys']] != ys: bad += 1
    print(key, 'mismatches', bad, 'len mismatches', badlen)
for key, name in [('A','AL'),('B','BL'),('rawMin','rawMinL'),('closedMin','clMinL')]:
    ty, body = defs[name]
    v = [fq(m) for m in pat.finditer(body)]
    assert body.count('FQ.mk') == len(v)
    print(key, len(v), [F(s) for s in bank[key]] == v)
ty, body = defs['lines']
assert ty == 'List (FQ × FQ)'
pairs = re.findall(r'\(\((FQ\.mk[^)]*\)\)[^)]*\))\), \((FQ\.mk[^)]*\)\)[^)]*\))\)\)', body)
v = [fq(m) for m in pat.finditer(body)]
L = list(zip(v[0::2], v[1::2]))
print('lines', len(L), [(F(c), F(dd)) for c, dd in bank['lines']] == L)
# linesRat in T.lean
ty, body = defs['linesRat']
R = re.findall(r'\(\((-?\d+)/(\d+) : ℚ\), \((-?\d+)/(\d+) : ℚ\)\)', body)
LR = [(F(int(a), int(b)), F(int(c), int(e))) for a, b, c, e in R]
print('linesRat', len(LR), LR == L)
# Bridge theorem list
br = open(d + '/P06LinesP0r12.lean').read()
i = br.index('theorem lu_wang_lines_P0r12'); j = br.index(']', i)
seg = br[i:j]
RB = re.findall(r'\(\((-?\d+)/(\d+) : ℚ\), \((-?\d+)/(\d+) : ℚ\)\)', seg)
LB = [(F(int(a), int(b)), F(int(c), int(e))) for a, b, c, e in RB]
print('bridge lines', len(LB), LB == L)
print(br[j:j+400])
