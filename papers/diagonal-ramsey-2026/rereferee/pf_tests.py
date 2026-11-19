import json, copy, os, subprocess, sys
PF = 'papers/diagonal-ramsey-2026/tools/preflight.py'
SRC = 'research/tier2/ramsey-zbs/code/lemmaD/certs/root3_x337059333092731.json'
OUT = sys.argv[1]
base = json.load(open(SRC))
N = len(base['qgrid']) - 1
print('root3: N =', N, 'jA0 =', base['jA0'], 'keys', sorted(base.keys()))
def run(name, obj, raw=None):
    fn = os.path.join(OUT, name.replace(' ', '_').replace('/', '_') + '.json')
    with open(fn, 'w') as f:
        f.write(raw if raw is not None else json.dumps(obj))
    r = subprocess.run([sys.executable, '-I', PF, fn], capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or ['?'])[-1]
    if r.returncode not in (0, 1): last = 'CRASH rc=%d %s' % (r.returncode, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else '')
    print('%-40s rc=%d | %s' % (name, r.returncode, last[:150]))
    os.remove(fn)
def T(name, f):
    d = copy.deepcopy(base); f(d); run(name, d)
run('original', base)
T('jA0=1 (valid range end)', lambda d: d.__setitem__('jA0', 1))
T('jA0=N-1 (valid range end)', lambda d: d.__setitem__('jA0', N - 1))
T('jA0=0', lambda d: d.__setitem__('jA0', 0))
T('jA0=N', lambda d: d.__setitem__('jA0', N))
T('jA0=5.0 float', lambda d: d.__setitem__('jA0', 5.0))
T('jA0=true', lambda d: d.__setitem__('jA0', True))
T('jA0 missing', lambda d: d.pop('jA0'))
T('qgrid len 2 (N=1)', lambda d: (d.__setitem__('qgrid', d['qgrid'][:1] + d['qgrid'][-1:]), d.__setitem__('jA0', 1)))
T('qgrid len 3 (N=2), jA0=1', lambda d: (d.__setitem__('qgrid', d['qgrid'][:2] + d['qgrid'][-1:]), d.__setitem__('jA0', 1)))
T('qgrid as dict', lambda d: d.__setitem__('qgrid', {'a': 1}))
T('tree missing', lambda d: d.pop('tree'))
T('tree = "L" (single box)', lambda d: d.__setitem__('tree', 'L'))
T('root axis "x"', lambda d: d['tree'].__setitem__(0, 'x'))
T('root axis "P " (trailing space)', lambda d: d['tree'].__setitem__(0, 'P '))
T('root node 4 items', lambda d: d['tree'].append('L'))
T('leaf "l" lower case', lambda d: d.__setitem__('tree', ['P', 'l', 'L']))
T('leaf as ["L"]', lambda d: d.__setitem__('tree', ['P', ['L'], 'L']))
def deep(d, n):
    t = 'L'
    for _ in range(n): t = ['P', t, 'L']
    d['tree'] = t
T('valid-format tree depth 200', lambda d: deep(d, 200))
T('valid-format tree depth 201', lambda d: deep(d, 201))
# duplicate key: json keeps the last one
s = json.dumps(base)
s2 = s[:-1] + ', "jA0": 0}'
run('duplicate key jA0 (last=0)', None, raw=s2)
s3 = '{"jA0": 0, ' + s[1:]
run('duplicate key jA0 (first=0, last=orig)', None, raw=s3)
# bank-level synthetic certificates
lem = {k: v for k, v in base.items() if k != 'control'}
ok_ctl = {'p': '1/2', 'cert': {'q': []}}
run('bank: 1 Lemma C + 1 Lemma D', {'controls': [ok_ctl, {'p': '1/2', 'lemmaD': lem}]})
run('bank: both kinds', {'controls': [{'cert': {}, 'lemmaD': lem}]})
run('bank: neither kind', {'controls': [{'p': '1/2'}]})
run('bank: control key in lemmaD', {'controls': [{'lemmaD': dict(lem, control=base['control'])}]})
run('bank: lemmaD null', {'controls': [{'lemmaD': None}]})
run('bank: lemmaD jA0=0', {'controls': [{'lemmaD': dict(lem, jA0=0)}]})
run('bank: controls is a dict {"cert":1}', {'controls': {'cert': 1}})
run('bank: controls is a string "cert"', {'controls': 'certcert'})
run('neither bank nor lemmaD', {'foo': 1})
