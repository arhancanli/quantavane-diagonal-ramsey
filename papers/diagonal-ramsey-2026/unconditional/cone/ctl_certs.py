"""Lemma C certificates for ZBS controls (cone step, 19 Nov 2026).

For each requested ZBS control (p, mu, w, beta, x, lxU, l1mL, exactly as parsed by parse_zbs_full.py) this proposes a
Lemma C certificate with research/tier2/ramsey-zbs/search/build_ctl.py (uniform q-grid with N cells, secant choices,
heights; data only) and then verifies it with BOTH checkers' control code directly: ctlA.check_control (checker A,
Fractions + ivA intervals) and ctlB.check_control (checker B, python-flint Arb).  If either refuses, N is doubled
(512, 1024, ..., N_MAX).  A control that no N certifies is reported with the best hinge bound reached (exact upper end
from checker A when its other conditions pass, else the builder's float estimate).
Must run under the python-flint 0.9.0 interpreter (checker B); the builder uses only math and fractions.
usage: <flint-python> -I ctl_certs.py <zbs_full.json> <indices.json | all> <shard k> <shards m> <out.json>
indices.json: a JSON object with key 'controls' (list of ZBS control indices), e.g. the cone file of cone.py."""
import sys, os, json, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', 'research', 'tier2', 'ramsey-zbs'))
sys.path.insert(0, os.path.join(LANE, 'code', 'checkA'))
sys.path.insert(0, os.path.join(LANE, 'code', 'checkB'))
sys.path.insert(0, os.path.join(LANE, 'search'))
import ctlA, ctlB, build_ctl          # noqa: E402
import flint                           # noqa: E402

N_LIST = (512, 1024, 2048, 4096, 8192, 16384)
FIELDS = ('p', 'mu', 'w', 'beta', 'x', 'lxU', 'l1mL')


def certify(c):
    """c: control dict (strings). Returns (record, control-with-cert or None)."""
    p, mu, w, beta, x = (Fr(c[k]) for k in ('p', 'mu', 'w', 'beta', 'x'))
    tries = []
    for N in N_LIST:
        t0 = time.time()
        cert = build_ctl.build(p, mu, w, beta, x, N=N)
        if cert is None:
            tries.append({'N': N, 'built': False})
            continue
        fb = cert.pop('float_bound')
        cc = {k: c[k] for k in FIELDS}
        cc['cert'] = cert
        rec = {'N': N, 'float_bound': fb}
        try:
            okA, bA = ctlA.check_control(cc)
            rec['A'] = bool(okA); rec['boundA'] = '%d/%d' % (bA.numerator, bA.denominator); rec['boundA_float'] = float(bA)
        except (AssertionError, ArithmeticError) as e:
            rec['A'] = False; rec['A_refusal'] = str(e)[:200]
        try:
            okB, bB = ctlB.check_control(cc)
            rec['B'] = bool(okB); rec['boundB'] = str(bB)
        except (AssertionError, ArithmeticError) as e:
            rec['B'] = False; rec['B_refusal'] = str(e)[:200]
        rec['seconds'] = round(time.time() - t0, 2)
        tries.append(rec)
        if rec['A'] and rec['B']:
            return {'ok': True, 'N': N, 'tries': tries}, cc
    return {'ok': False, 'tries': tries}, None


def main(zp, idxp, k, m, outp):
    assert flint.__version__ == '0.9.0', flint.__version__
    k, m = int(k), int(m)
    z = json.load(open(zp))
    ctl = z['controls']
    idx = list(range(len(ctl))) if idxp == 'all' else sorted(json.load(open(idxp))['controls'])
    mine = idx[k::m]
    out = {'zbs_full': zp, 'shard': [k, m], 'records': {}, 'controls': {}}
    t0 = time.time()
    for n, i in enumerate(mine):
        rec, cc = certify(ctl[i])
        out['records'][str(i)] = rec
        if cc is not None:
            out['controls'][str(i)] = cc
        print('ctl %d: %s N=%s boundA=%s (%.0f s)' % (i, 'OK' if rec['ok'] else 'FAILED', rec.get('N'),
              rec['tries'][-1].get('boundA_float'), time.time() - t0), flush=True)
        if n % 25 == 0:
            with open(outp, 'w') as f: json.dump(out, f)
    out['seconds'] = round(time.time() - t0, 1)
    with open(outp, 'w') as f: json.dump(out, f)
    nok = sum(r['ok'] for r in out['records'].values())
    print('DONE shard %d/%d: %d of %d certified (%.0f s)' % (k, m, nok, len(mine), time.time() - t0), flush=True)


if __name__ == '__main__':
    main(*sys.argv[1:])
