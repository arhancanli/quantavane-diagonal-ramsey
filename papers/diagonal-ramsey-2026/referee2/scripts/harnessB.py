"""Run targeted tampers through checker B's own functions (bankB / ctlB / runB root logic)."""
import sys, os, json, copy, time
CHK = 'research/tier2/ramsey-zbs/code/checkB'
sys.path.insert(0, CHK); sys.path.insert(1, os.path.dirname(os.path.abspath(__file__)))
import bankB, ctlB
from bankB import Q as rat
import tampers
zp, cp = sys.argv[1], sys.argv[2]
mode = sys.argv[3] if len(sys.argv) > 3 else 'bank'
t0 = time.time()
zbs = json.load(open(zp)); cert = json.load(open(cp))
B = bankB.BankB(zbs, cert, ctlB.check_control)
print('loaded', round(time.time() - t0), 's', flush=True)

def run(name, f):
    try:
        f(); print('%-62s ACCEPTED' % name, flush=True)
    except Exception as e:
        print('%-62s refused  %s: %s' % (name, type(e).__name__, str(e)[:110]), flush=True)

if mode == 'bank':
    T, loc = tampers.tamper_list(cert)
    print('locations', loc, flush=True)
    i, k = loc['leaf']; P = cert['raw'][i]
    run('UNTAMPERED leaf', lambda: B.leaf(bankB.PL(P), P['pieces'][k]))
    i, k = loc['route']; P = cert['raw'][i]
    run('UNTAMPERED route', lambda: B.route(bankB.PL(P), P['pieces'][k]))
    Qd = cert['closed'][loc['rootQ']]
    run('UNTAMPERED closed root piece', lambda: B.closed_piece(bankB.PL(Qd), Qd['pieces'][0]))
    run('UNTAMPERED source', lambda: B.source(loc['src']))
    for name, kind, args in T:
        if kind == 'leaf':
            P2, L2 = args; run(name, lambda: B.leaf(bankB.PL(P2), L2))
        elif kind == 'route':
            P2, R2 = args
            for cl in R2['calls']:
                if cl['z'] == 'ONE_MINUS_PC':
                    pc = B.P[cl['ch'][0]][int(cl['ch'][1])].p; v = 1 - pc; cl['z'] = '%s/%s' % (v.p, v.q)
            run(name, lambda: B.route(bankB.PL(P2), R2))
        elif kind == 'closed':
            Q2, pc2, fR = args
            if fR is not None:
                ref = pc2['R']; Rd = copy.deepcopy(cert['raw'][int(ref[1])]); fR(Rd)
                old = B.P['nr'][int(ref[1])]; B.P['nr'][int(ref[1])] = bankB.PL(Rd)
                run(name, lambda: B.closed_piece(bankB.PL(Q2), pc2))
                B.P['nr'][int(ref[1])] = old
            else:
                run(name, lambda: B.closed_piece(bankB.PL(Q2), pc2))
        elif kind == 'source':
            h, S2 = args
            old = (B.newsrc[h], B.srcAB['n'][h])
            B.newsrc[h] = S2; B.srcAB['n'][h] = (rat(S2['A']), rat(S2['B']))
            run(name, lambda: B.source(h))
            B.newsrc[h], B.srcAB['n'][h] = old
        elif kind == 'root':
            key, val = args
            def root():
                c2 = copy.deepcopy(cert['root']); c2[key] = val
                q = int(c2['closed']); Qobj = B.P['nc'][q]
                pcs = copy.deepcopy(cert['closed'][q]['pieces'])
                if key == 'kind':
                    for p in pcs: p['kind'] = val
                one = rat('1')
                hits = [c for c in pcs if rat(c['lo']) <= one <= rat(c['hi'])]
                bankB.need(len(hits) > 0 and all(c['kind'] == 'pair' for c in hits), 'root piece is a complementary pair')
                bankB.need(Qobj(one) == rat(c2['z']), 'claimed z')
            run(name, root)
elif mode == 'ctl':
    ci = int(sys.argv[4])
    c = cert['controls'][ci]
    run('UNTAMPERED control %d' % ci, lambda: ctlB.check_control(c))
    TT = tampers.control_tampers(c) if 'cert' in c else tampers.cd_tampers(c)
    for name, c2 in TT:
        run(name, lambda: ctlB.check_control(c2))
print('done', round(time.time() - t0), 's')
