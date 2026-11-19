"""Parse ZBS bank tables (Solutions/P06/P0r12/T.lean + TD0-3.lean at c2875f33) into JSON with exact
rationals as strings 'n/d'.  FQ.mk n d means n/(d+1).  usage: python3 -I parse_zbs.py T.lean out.json"""
import re, sys, json, hashlib
import os
d = os.path.dirname(sys.argv[1]) or '.'
SHA = {'T.lean': '93843f28073606fd15055794b68c7237423bbce6dcdb33b75565b326ca9f158f',
       'TD0.lean': 'b98a2a097f9197ff5054ee0476864be80f3163379a036111188ae0de8fcd8f08',
       'TD1.lean': 'e18213b9a319a8e0a1185b8e5a68e5e9a5671a9dbd556c93d0500124b8d43098',
       'TD2.lean': '47e910a45dfb7b3425d9ed0a79a70b3fa162e69a073913c41e7c6e7aac527150',
       'TD3.lean': '02e8768154777b25ba35c955c79686f01921a4d717fc2f95d8f16cdb30652bb7'}
src = ''
for fn, h in SHA.items():
    t = open(os.path.join(d, fn)).read(); assert hashlib.sha256(t.encode()).hexdigest() == h, fn
    src += '\n' + t
FQ = r'\(FQ\.mk \((?:\.ofNat|Int\.negSucc) \(nat_lit (\d+)\)\) \(nat_lit (\d+)\)\)'
def fq_all(s):
    out = []
    for m in re.finditer(r'\(FQ\.mk \((\.ofNat|\.negSucc) \(nat_lit (\d+)\)\) \(nat_lit (\d+)\)\)', s):
        n = int(m.group(2)); d = int(m.group(3)) + 1
        if m.group(1) == '.negSucc': n = -(n + 1)
        out.append('%d/%d' % (n, d))
    return out
def defbody(name):
    i = src.index('\ndef ' + name + ' '); j = src.find('\ndef ', i + 5)
    return src[i:j if j > 0 else len(src)]
res = {}
res['A'] = fq_all(defbody('AL')); res['B'] = fq_all(defbody('BL'))
lb = defbody('lines'); res['lines'] = [x for x in fq_all(lb)]
res['lines'] = list(zip(res['lines'][0::2], res['lines'][1::2]))
# controls c0.. : CtrlF fields p mu w beta x lxU l1mL
ctl = []
for k in range(918):
    b = defbody('c%d' % k); v = fq_all(b); assert len(v) == 7, (k, len(v)); ctl.append(v)
res['ctl'] = ctl
def prof(name):
    b = defbody(name); v = fq_all(b)
    # ProfF p xs ys : p then xs list then ys list (equal length)
    n = (len(v) - 1) // 2; assert 2 * n + 1 == len(v), name
    return {'p': v[0], 'xs': v[1:1 + n], 'ys': v[1 + n:]}
res['raw'] = [prof('r%d' % k) for k in range(1902)]
res['closed'] = [prof('q%d' % k) for k in range(1003)]
res['rawMin'] = fq_all(defbody('rawMinL')); res['closedMin'] = fq_all(defbody('clMinL'))
print({k: len(v) for k, v in res.items()})
json.dump(res, open(sys.argv[2], 'w'))
