"""Run targeted tampers through checker A's own functions (bankA / ctlA / runA root logic)."""
import sys, os, json, copy, time
CHK = 'research/tier2/ramsey-zbs/code/checkA'
sys.path.insert(0, CHK); sys.path.insert(1, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as Fr
import bankA, ctlA, ivA
import tampers
zp, cp = sys.argv[1], sys.argv[2]
mode = sys.argv[3] if len(sys.argv) > 3 else 'bank'
t0 = time.time()
zbs = json.load(open(zp)); cert = json.load(open(cp))
bank = bankA.Bank(zbs, cert, lambda c: ctlA.check_control(c)[0])
print('loaded', round(time.time() - t0), 's', flush=True)

def run(name, f):
    try:
        f(); print('%-62s ACCEPTED' % name, flush=True)
    except Exception as e:
        print('%-62s refused  %s: %s' % (name, type(e).__name__, str(e)[:110]), flush=True)

if mode == 'bank':
    T, loc = tampers.tamper_list(cert)
    print('locations', loc, flush=True)
    # sanity: the untampered objects pass
    i, k = loc['leaf']; P = cert['raw'][i]
    run('UNTAMPERED leaf', lambda: bank.leaf_ok(bankA.Prof(P), P['pieces'][k]))
    i, k = loc['route']; P = cert['raw'][i]
    run('UNTAMPERED route', lambda: bank.route_ok(bankA.Prof(P), P['pieces'][k]))
    Q = cert['closed'][loc['rootQ']]
    run('UNTAMPERED closed root piece', lambda: bank.closed_piece_ok(bankA.Prof(Q), Q['pieces'][0]))
    run('UNTAMPERED source', lambda: bank.source_ok(loc['src']))
    for name, kind, args in T:
        if kind == 'leaf':
            P2, L2 = args; run(name, lambda: bank.leaf_ok(bankA.Prof(P2), L2))
        elif kind == 'route':
            P2, R2 = args
            for cl in R2['calls']:
                if cl['z'] == 'ONE_MINUS_PC':
                    pc = bank.prof(cl['ch']).p; cl['z'] = '%d/%d' % ((1 - pc).numerator, (1 - pc).denominator)
            run(name, lambda: bank.route_ok(bankA.Prof(P2), R2))
        elif kind == 'closed':
            Q2, pc2, fR = args
            if fR is not None:
                ref = pc2['R']; Rd = copy.deepcopy(cert['raw'][int(ref[1])]); fR(Rd)
                old = bank.nr[int(ref[1])]; bank.nr[int(ref[1])] = bankA.Prof(Rd)
                run(name, lambda: bank.closed_piece_ok(bankA.Prof(Q2), pc2))
                bank.nr[int(ref[1])] = old
            else:
                run(name, lambda: bank.closed_piece_ok(bankA.Prof(Q2), pc2))
        elif kind == 'source':
            h, S2 = args
            old = (bank.newsrc[h], bank.nA[h], bank.nB[h])
            bank.newsrc[h] = S2; bank.nA[h] = Fr(S2['A']); bank.nB[h] = Fr(S2['B'])
            run(name, lambda: bank.source_ok(h))
            bank.newsrc[h], bank.nA[h], bank.nB[h] = old
        elif kind == 'root':
            key, val = args
            def root():
                c2 = copy.deepcopy(cert['root']); c2[key] = val
                q = int(c2['closed']); Q = bank.nc[q]
                pcs = copy.deepcopy(cert['closed'][q]['pieces'])
                if key == 'kind':
                    for p in pcs: p['kind'] = val
                pc = [p for p in pcs if Fr(p['lo']) <= 1 <= Fr(p['hi'])]
                assert pc and all(p['kind'] == 'pair' for p in pc), 'piece of Q containing 1 is a complementary pair'
                z = Q.at(Fr(1)); assert z == Fr(c2['z']), 'claimed z = L_Q(1)'
            run(name, root)
elif mode == 'ctl':
    ci = int(sys.argv[4])
    c = cert['controls'][ci]
    run('UNTAMPERED control %d' % ci, lambda: ctlA.check_control(c))
    TT = tampers.control_tampers(c) if 'cert' in c else tampers.cd_tampers(c)
    for name, c2 in TT:
        run(name, lambda: ctlA.check_control(c2))
print('done', round(time.time() - t0), 's')
