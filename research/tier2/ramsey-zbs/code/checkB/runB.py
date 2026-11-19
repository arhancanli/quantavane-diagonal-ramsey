"""Checker B driver (separately written): same certificate format, python-flint checks (bankB.py, ctlB.py).
usage: python3 runB.py zbs_bank.json cert.json [out.json]"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bankB, ctlB, hashlib
from flint import arb, fmpq
ZBS_SHA = '2946c6561f562ea01a5f9b60ac0812c689af71985c60378e11c89e8cdc003bf0'
from bankB import Q as rat, need


def main(zp, cp, outp=None):
    t0 = time.time()
    need(hashlib.sha256(open(zp, 'rb').read()).hexdigest() == ZBS_SHA, 'pinned zbs_bank.json')
    zbs = json.load(open(zp)); cert = json.load(open(cp))
    B = bankB.BankB(zbs, cert, ctlB.check_control)
    # all objects are checked; order chosen so that tampered certificates are refused early
    q = int(cert['root']['closed']); Qobj = B.P['nc'][q]
    one = rat('1')
    hits = [c for c in cert['closed'][q]['pieces'] if rat(c['lo']) <= one <= rat(c['hi'])]
    need(len(hits) > 0 and all(c['kind'] == 'pair' for c in hits), 'root piece is a complementary pair')
    z = Qobj(one)
    need(z == rat(cert['root']['z']), 'claimed z')
    for h in range(len(cert['sources'])): B.source(h)
    for i in reversed(range(len(cert['raw']))): B.profile(B.P['nr'][i], cert['raw'][i]['pieces'], cert['raw'][i]['min'], True)
    for i, Qp in enumerate(cert['closed']): B.profile(B.P['nc'][i], Qp['pieces'], Qp['min'], False)
    for i in range(len(cert['controls'])): B.ctrl(i)
    nD = sum('lemmaD' in k for k in cert['controls'])
    res = {'checker': 'B', 'ok': True, 'controls_lemmaD': nD, 'claim': 'ZBS-only' if nD == 0 else 'assuming Theorem A (ramsey-lemma; %d Lemma D controls)' % nD, 'controls': len(cert['controls']), 'sources': len(cert['sources']),
           'raw': len(cert['raw']), 'closed': len(cert['closed']), 'z': str(z), 'z_float': float(z.p) / float(z.q),
           'base_upper': str(arb(z).exp().upper()), 'seconds': round(time.time() - t0, 1)}
    print(json.dumps(res))
    if outp: json.dump(res, open(outp, 'w'))
    return res


if __name__ == '__main__':
    main(*sys.argv[1:])
