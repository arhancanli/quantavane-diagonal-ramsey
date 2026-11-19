"""Certify Lemma D for bank controls (route tree), one at a time: genD branch and bound at a lowered a, then
checkD_A, checkD_B, checkD_C (cert_independent/) and tamper_D on the stored certificate. On a generator failure the
shift is lowered by 10% (at most 4 tries).
Usage: python3 tree_cert.py controls.tsv plan.txt   (plan lines: name da_float u_b;  da > 0 lowers a: x' = x e^{da})
Writes certs/<name>.json (bare control) and certs/<name>_m<da in 1e-6>.json; prints one RESULT line per control."""
import json
import math
import os
import subprocess
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def run(args, log):
    t = time.time()
    r = subprocess.run([PY] + args, cwd=HERE, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip().splitlines()
    log.write('$ %s  (rc %d, %.0fs)\n%s\n' % (' '.join(args), r.returncode, time.time() - t, '\n'.join(out[-12:])))
    log.flush()
    return r.returncode, out


def main(tsv, plan):
    rows = {}
    for line in open(tsv):
        f = line.rstrip('\n').split('\t')
        if f[0] == 'control': hdr = f; continue
        rows[f[0]] = dict(zip(hdr, f))
    log = open(os.path.join(HERE, '..', 'cert', 'runs_tree.log'), 'a')
    for line in open(plan):
        if not line.strip() or line.startswith('#'): continue
        name, da, ub = line.split(); da = float(da); ub = float(ub)
        r = rows[name]
        bare = dict(p=r['p'], mu=r['mu'], w=r['w'], beta='9999999/10000000', x=r['x'])
        bpath = os.path.join(HERE, 'certs', name + '.json')
        json.dump(bare, open(bpath, 'w'))
        ok = False
        for _ in range(4):
            tag = '%s_m%d' % (name, round(da * 1e6))
            out = os.path.join('certs', tag + '.json')
            log.write('\n#### %s da %.2e u_b %.3f  %s\n' % (name, da, ub, time.strftime('%H:%M:%S', time.gmtime())))
            # genD convention: x' = x exp(-da_arg), so pass -da
            rc, o = run(['genD.py', 'certs/%s.json' % name, str(Fr(-da).limit_denominator(10**9)), str(ub), out, '48'], log)
            if rc != 0 or not os.path.exists(os.path.join(HERE, out)):
                da = math.floor(da * 0.9 * 1e6) / 1e6
                continue
            rA, oA = run(['checkD_A.py', out], log)
            rB, oB = run(['checkD_B.py', out], log)
            rC, oC = run([os.path.join('..', 'cert_independent', 'checkD_C.py'), out], log)
            rT, oT = run(['tamper_D.py', out], log)
            wC = [s for s in oC if 'worst U(B) <=' in s]
            print('RESULT %s da %.2e u_b %.3f: genD ok; A rc %d, B rc %d, C rc %d (%s), tamper rc %d (%s)  -> %s'
                  % (name, da, ub, rA, rB, rC, wC[0].strip() if wC else '?', rT, oT[-1] if oT else '?', out), flush=True)
            ok = True
            break
        if not ok:
            print('RESULT %s: generator could not close down to da %.2e' % (name, da), flush=True)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
