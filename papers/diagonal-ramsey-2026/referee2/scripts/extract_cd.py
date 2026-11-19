import json, sys, os, glob
from fractions import Fraction as F
cert = json.load(open(sys.argv[1])); certdir = sys.argv[2]; out = sys.argv[3]
files = {}
for fn in glob.glob(os.path.join(certdir, '*.json')):
    files[os.path.basename(fn)] = json.load(open(fn))
n = 0
for i, c in enumerate(cert['controls']):
    if 'lemmaD' not in c: continue
    d = dict(control={k: c[k] for k in ('p', 'mu', 'w', 'beta', 'x')}, **c['lemmaD'])
    match = [fn for fn, f in files.items() if f == d]
    match2 = [fn for fn, f in files.items() if {k: v for k, v in f.items() if k != 'control'} == c['lemmaD']]
    # also compare control values numerically
    m3 = [fn for fn in match2 if all(F(files[fn]['control'][k]) == F(c[k]) for k in ('p','mu','w','beta','x'))]
    json.dump(d, open(os.path.join(out, 'ctl%d.json' % i), 'w'))
    print(i, 'exact-match', match, 'data-match', match2, 'numeric-control-match', m3, 'x', c['x'])
    n += 1
print('n', n)
