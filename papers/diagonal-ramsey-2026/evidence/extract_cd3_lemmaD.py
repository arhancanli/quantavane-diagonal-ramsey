"""Extract the Lemma D blocks embedded in certCD3.json, write each as a stand-alone Lemma D certificate (control = the
bank control's own p, mu, w, beta, x), and compare with the vendored files listed in cdmap_cd3.json."""
import json, sys, os, hashlib
from fractions import Fraction as Fr
cert_path, cdmap_path, lemmad_dir, outdir = sys.argv[1:5]
cert = json.load(open(cert_path))
cdmap = json.load(open(cdmap_path))
vend = {}
for e in cdmap:
    p = os.path.join(lemmad_dir, e['cert'])
    assert hashlib.sha256(open(p, 'rb').read()).hexdigest() == e['sha256'], p
    vend[e['cert']] = json.load(open(p))
def canon(d):
    return json.dumps(d, sort_keys=True)
n = 0
for i, c in enumerate(cert['controls']):
    if 'lemmaD' not in c: continue
    n += 1
    ctl = {k: c[k] for k in ('p', 'mu', 'w', 'beta', 'x')}
    out = dict(control=ctl, **c['lemmaD'])
    fn = os.path.join(outdir, 'cd3_ctl%04d.json' % i)
    json.dump(out, open(fn, 'w'))
    match = [k for k, v in vend.items() if canon(v) == canon(out)]
    vmatch = [k for k, v in vend.items() if all(Fr(v['control'][kk]) == Fr(ctl[kk]) for kk in ctl)]
    print('control %4d  x=%s  identical_to=%s  same_control_as=%s' % (i, ctl['x'], match, vmatch))
print('embedded Lemma D controls:', n)
