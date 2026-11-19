"""Checker A driver: verifies every new object of a certificate (controls, raw profiles with leaf/route pieces, closed
profiles with density/pair pieces, source covers) against ZBS's Boolean checks (bankA.py) and Lemma C (ctlA.py), then
reads the claimed diagonal exponent from the final closed profile Q (Corollary 5.10 of ZBS, printed numbering: the piece of Q containing 1
must be a complementary pair).  usage: python3 -I runA.py zbs_bank.json cert.json [out.json]"""
if not __debug__:
    raise SystemExit('checker A is written with assert statements; refusing to run under python -O')
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as Fr
import bankA, ctlA, ivA
ZBS_SHA = '2946c6561f562ea01a5f9b60ac0812c689af71985c60378e11c89e8cdc003bf0'


def main(zp, cp, outp=None):
    t0 = time.time()
    import hashlib
    assert hashlib.sha256(open(zp, 'rb').read()).hexdigest() == ZBS_SHA, 'zbs_bank.json is not the pinned parse of c2875f33'
    zbs = json.load(open(zp)); cert = json.load(open(cp))
    res = {'checker': 'A', 'ok': False}
    bank = bankA.Bank(zbs, cert, lambda c: ctlA.check_control(c)[0])
    # every object is checked; the order (claimed root first, then sources, raw profiles from the last, closed
    # profiles, any control not yet reached) only makes refusals of tampered certificates arrive sooner
    q = int(cert['root']['closed']); Q = bank.nc[q]
    pc = [pc for pc in cert['closed'][q]['pieces'] if Fr(pc['lo']) <= 1 <= Fr(pc['hi'])]
    assert pc and all(p['kind'] == 'pair' for p in pc), 'piece of Q containing 1 is a complementary pair'
    z = Q.at(Fr(1))
    assert z == Fr(cert['root']['z']), 'claimed z = L_Q(1)'
    for h in range(len(cert['sources'])): bank.source_ok(h)
    res['sources'] = len(cert['sources'])
    for i in reversed(range(len(cert['raw']))):
        P = cert['raw'][i]
        bank.profile_ok(bank.nr[i], P['pieces'], Fr(P['min']), 'raw')
    res['raw'] = len(cert['raw']); res['raw_pieces'] = sum(len(P['pieces']) for P in cert['raw'])
    for i, Qd in enumerate(cert['closed']):
        bank.profile_ok(bank.nc[i], Qd['pieces'], Fr(Qd['min']), 'closed')
    res['closed'] = len(cert['closed'])
    for i in range(len(cert['controls'])): bank.control(i)
    res['controls'] = len(cert['controls'])
    eu = ivA.exp(z).hif()                    # certified: e^z <= eu
    eu10 = Fr(-((-eu.numerator * 10 ** 10) // eu.denominator), 10 ** 10)
    nD = sum('lemmaD' in k for k in cert['controls'])
    res.update(controls_lemmaD=nD, claim='ZBS-only' if nD == 0 else 'assuming Theorem A (ramsey-lemma; %d Lemma D controls)' % nD)
    res.update(ok=True, z=str(z), z_float=float(z), base_upper=str(eu10), base_upper_dec='%.10f' % float(eu10), seconds=round(time.time() - t0, 1))
    print(json.dumps(res))
    if outp: json.dump(res, open(outp, 'w'))
    return res


if __name__ == '__main__':
    main(*sys.argv[1:])
