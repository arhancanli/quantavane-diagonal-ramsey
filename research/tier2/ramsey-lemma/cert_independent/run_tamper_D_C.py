#!/usr/bin/env python3
"""Run cert/tamper_D.py's tampered certificates through checkD_C only.

tamper_D builds its tampers in memory (some with genD.skeleton, the merge tamper with checkD_A's
box bound to choose the leaf) and hands each to refuse().  Here refuse() is replaced by one that
writes the tampered certificate to OUTDIR and runs checkD_C on it.  checkD_B is stubbed out (never
run); checkD_A and genD run only as tamper_D's tamper generators, unread.
Usage: run_tamper_D_C.py CERT.json OUTDIR
"""
import os
import sys
import json
import types

HERE = os.path.dirname(os.path.abspath(__file__))
CERT_DIR = os.path.join(os.path.dirname(HERE), 'cert')
sys.path.insert(0, HERE)
import checkD_C as C  # noqa: E402

sys.path.insert(1, CERT_DIR)
sys.modules['checkD_B'] = types.ModuleType('checkD_B')   # stub: tamper_D imports it but we never call it
import tamper_D  # noqa: E402

COUNT = {'n': 0, 'refused': 0}


def refuse_C(cert):
    COUNT['n'] += 1
    path = os.path.join(sys.argv[2], 'tD_%02d.json' % COUNT['n'])
    try:
        txt = json.dumps(cert)
    except TypeError as e:
        COUNT['refused'] += 1
        return [('C', True, 'not JSON-serialisable: %s' % e)]
    with open(path, 'w') as f:
        f.write(txt)
    lines = []
    try:
        ct = C.load_cert(path)
        ch = C.Checker(ct, log=lines.append, stop_on_data_fail=True)
        acc, worst, nleaf = ch.run()
        if acc:
            msg = 'ACCEPTED, worst U <= %s' % C.dec(worst)
        else:
            msg = ch.fails[0] if ch.fails else 'rejected'
            if worst is not None:
                msg += ' [worst U <= %s]' % C.dec(worst)
    except C.CertError as e:
        acc, msg = False, 'format: %s' % e
    except Exception as e:
        acc, msg = False, 'EXCEPTION %s: %s' % (type(e).__name__, e)
    COUNT['refused'] += (not acc)
    return [('C', not acc, '%s  (%s)' % (msg[:200], os.path.basename(path)))]


tamper_D.refuse = refuse_C

if __name__ == '__main__':
    os.makedirs(sys.argv[2], exist_ok=True)
    tamper_D.main(sys.argv[1])
    print('checkD_C on tamper_D: %d / %d refused' % (COUNT['refused'], COUNT['n']))
    sys.exit(0 if COUNT['refused'] == COUNT['n'] else 1)
