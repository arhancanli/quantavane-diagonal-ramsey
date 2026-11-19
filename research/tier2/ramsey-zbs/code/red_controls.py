"""Red controls for a certificate: each tamper must be REFUSED by both checkers.
usage: python3 red_controls.py zbs_bank.json cert.json <flint-python> outdir
Each tamper edits ONE field of the certificate in place, writes the tampered file, runs checkers A and B, and restores
the field (one copy of the certificate in memory).  Tampers:
  leaf     : a leaf piece's aU lowered by 1e-6 (terminal no longer certified: e^{-aU} > xi)
  leafval  : a profile value at a leaf piece's left end lowered by 1e-6
  route_g0 : the root route's start value g0 lowered by 1e-7 (a child pokes above the path)
  route_ds : the root route's first slope multiplied by 0.999 (slope below -log(1 - p_child))
  control  : the root control's x raised by 2e-5 relative
  ctl_h    : one secant height of the root control lowered by 1e-6
  source   : the first source line's B lowered by 1e-5 (cover fails)
  srcline  : a grounded source cell's tangent line replaced by the line farthest above the source line
  rootz    : the claimed z lowered by 1e-12
  negidx   : a route child index replaced by -1
  closed_raw_only : a complementary-pair piece of a closed U object pointing at a CLOSED profile
"""
import sys, json, subprocess, os
from fractions import Fraction as Fr


def fs(x): return '%d/%d' % (x.numerator, x.denominator)


def worst_leaf_parent(tree, rect, L):
    """path to the parent of the leaf with the largest box bound U (checker A); same as ramsey-lemma tamper_D.py
    (copied here because tamper_D imports the Arb checker, which this script's interpreter may lack)."""
    best = [None, None]
    def rec(t, r, path):
        Pl, Ph, pl, ph = r
        if t == 'L':
            U, _ = L.box(*r)
            if U is not None and (best[0] is None or U > best[0]): best[0], best[1] = U, path[:-1]
            return
        ax, a, b = t
        if ax == 'P':
            m = (Pl + Ph) / 2; rec(a, (Pl, m, pl, ph), path + [1]); rec(b, (m, Ph, pl, ph), path + [2])
        else:
            m = (pl + ph) / 2; rec(a, (Pl, Ph, pl, m), path + [1]); rec(b, (Pl, Ph, m, ph), path + [2])
    rec(tree, rect, [])
    return best[1]


def tamper_list(cert, lines):
    """yields (name, container, key, new value) for in-place edits."""
    raws = cert['raw']
    for P in reversed(raws):
        lf = [p for p in P['pieces'] if p['kind'] == 'leaf']
        if lf:
            yield 'leaf', lf[0], 'aU', fs(Fr(lf[0]['aU']) - Fr(1, 10 ** 6))
            i = [Fr(x) for x in P['xs']].index(Fr(lf[0]['lo']))
            yield 'leafval', P['ys'], i, fs(Fr(P['ys'][i]) - Fr(1, 10 ** 6))
            break
    root_raw = next(i for i, P in enumerate(raws) if P.get('gen', {}).get('root'))
    rp = raws[root_raw]['pieces'][0]
    if rp['kind'] == 'route':
        yield 'route_g0', rp, 'g0', fs(Fr(rp['g0']) - Fr(1, 10 ** 7))
        yield 'route_ds', rp['ds'], 0, fs(Fr(rp['ds'][0]) * Fr(999, 1000))
        ci = int(rp['t']['c'])
    else:
        ci = int(rp['c'])
    k = cert['controls'][ci]
    yield 'control', k, 'x', fs(Fr(k['x']) * (1 + Fr(2, 10 ** 5)))
    if 'lemmaD' in k:      # Lemma D control (second claim): the three gate-4 CD tampers (ramsey-lemma, 18 Nov)
        lem = k['lemmaD']
        yield 'cd_alpha_minus_1e-12', lem, 'alpha', fs(Fr(lem['alpha']) - Fr(1, 10 ** 12))
        yield 'cd_u_b_minus_D', lem, 'u_b', fs(Fr(lem['u_b']) - Fr(lem['Dplus']))
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lemmaD'))
        import checkD_A
        cd = dict(control={kk: k[kk] for kk in ('p', 'mu', 'w', 'beta', 'x')}, **lem)
        L = checkD_A.LemmaD(cd)
        pth = worst_leaf_parent(lem['tree'], (Fr(0), Fr(lem['G_up']), -L.w, Fr(lem['P_up'])), L)
        if pth:
            node = lem['tree']
            for i in pth[:-1]: node = node[i]
            yield 'cd_merge_worst_leaf', node, pth[-1], 'L'
        else:
            yield 'cd_merge_worst_leaf', lem, 'tree', 'L'
    else:
        m = len(k['cert']['h']) // 2
        yield 'ctl_h', k['cert']['h'], m, fs(Fr(k['cert']['h'][m]) - Fr(1, 10 ** 6))
    if cert['sources']:
        s = cert['sources'][0]
        yield 'source', s, 'B', fs(Fr(s['B']) - Fr(1, 10 ** 5))
        for s in cert['sources']:
            g = [x for x in s['cells'] if x['kind'] == 'grounded']
            if g:
                cell = g[len(g) // 2]; mid = (Fr(cell['lo']) + Fr(cell['hi'])) / 2
                A, B = Fr(s['A']), Fr(s['B'])
                yield 'srcline', cell, 'k', max(range(len(lines)), key=lambda kk: lines[kk][0] + lines[kk][1] * mid - A - B * mid)
                break
    yield 'rootz', cert['root'], 'z', fs(Fr(cert['root']['z']) - Fr(1, 10 ** 12))
    for P in reversed(raws):
        rt = [p for p in P['pieces'] if p['kind'] == 'route']
        if rt:
            yield 'negidx', rt[0]['calls'][0], 'ch', [rt[0]['calls'][0]['ch'][0], -1]
            break
    for Q in cert['closed']:
        if Q.get('gen', {}).get('U') is not None:
            yield 'closed_raw_only', Q['pieces'][len(Q['pieces']) // 2], 'R', ['nc', 0]
            break


if __name__ == '__main__':
    zp, cp, flintpy, od = sys.argv[1:5]
    os.makedirs(od, exist_ok=True)
    cert = json.load(open(cp))
    lines = [(Fr(a), Fr(b)) for a, b in json.load(open(zp))['lines']]
    here = os.path.dirname(os.path.abspath(__file__))
    allok = True
    for name, cont, key, val in tamper_list(cert, lines):
        old = cont[key]; cont[key] = val
        fn = os.path.join(od, 'red_%s.json' % name)
        with open(fn, 'w') as f: json.dump(cert, f)
        cont[key] = old
        ra = subprocess.run([sys.executable, '-I', os.path.join(here, 'checkA', 'runA.py'), zp, fn], capture_output=True, text=True)
        rb = subprocess.run([flintpy, '-I', os.path.join(here, 'checkB', 'runB.py'), zp, fn], capture_output=True, text=True)
        refA = ra.returncode != 0; refB = rb.returncode != 0
        why = lambda r: (r.stderr.strip().splitlines() or ['?'])[-1][:120]
        print('%-15s A %s  B %s   | A: %s | B: %s' % (name, 'REFUSED' if refA else 'ACCEPTED', 'REFUSED' if refB else 'ACCEPTED',
                                                      why(ra) if refA else '', why(rb) if refB else ''), flush=True)
        allok &= refA and refB
        os.remove(fn)
    print('ALL RED CONTROLS REFUSED BY BOTH' if allok else 'SOME RED CONTROL ACCEPTED', flush=True)
