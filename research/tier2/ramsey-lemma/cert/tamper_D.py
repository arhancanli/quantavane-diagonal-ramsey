"""Red controls for Lemma D certificates: each tamper must be refused by BOTH checkers.
Usage: python3 tamper_D.py cert.json

Thirteen tampers break a hypothesis or the closability of the tree (K1-K10 of CERT_DESIGN 4c) and are refused
whatever the margin. The two MARGIN PROBES regenerate every data field at x' = x e^f with the same tree: the result
satisfies K1-K9 and is refused only through K10, i.e. only if f exceeds the certificate's own margin. U moves by about
0.5 f (checkD_C, SPEC_ISSUES item 11), so f is chosen per certificate from the worst leaf U0 < 0 found by checker A:
f1 = max(2e-6, 8 |U0|) (expected worst U about +3 |U0|) and f2 = max(1e-5, 40 |U0|) (about +19 |U0|)."""
import copy
import json
import sys
from fractions import Fraction as Fr

import checkD_A
import checkD_B


def refuse(cert):
    out = []
    for name, mod in (('A', checkD_A), ('B', checkD_B)):
        try:
            mod.check(cert, verbose=False)
            out.append((name, False, 'ACCEPTED'))
        except Exception as e:                      # AssertionError, ArithmeticError, KeyError, ...
            out.append((name, True, '%s: %s' % (type(e).__name__, str(e)[:90])))
    return out


def worst_leaf_parent(tree, rect, L):
    """path to the parent of the leaf with the largest U (checker A), and that U, for the merge tamper and the
    margin probes."""
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
    return best[1], best[0]


def main(path):
    cert = json.load(open(path))
    L = checkD_A.LemmaD(cert)
    tampers = []
    def T(name, f):
        c = copy.deepcopy(cert); f(c); tampers.append((name, c))
    T('control x * 1.01', lambda c: c['control'].__setitem__('x', str(Fr(c['control']['x']) * Fr(101, 100))))
    T('control mu + 1e-9', lambda c: c['control'].__setitem__('mu', str(Fr(c['control']['mu']) + Fr(1, 10**9))))
    T('alpha / 2', lambda c: c.__setitem__('alpha', str(Fr(c['alpha']) / 2)))
    T('w -> 3 (so (1-mu)^w < x < p)', lambda c: c['control'].__setitem__('w', '3'))
    def acut(c):
        c['a_cut'] = str(Fr(c['a_hi']) - Fr(1, 10**13)); c['qgrid'][0] = c['a_cut']
    T('a_cut above a(0) (inside D)', acut)
    T('y_c - 1e-3', lambda c: c.__setitem__('y_c', str(Fr(c['y_c']) - Fr(1, 1000))))
    T('u_b -> u_b * 2/3', lambda c: c.__setitem__('u_b', str(Fr(c['u_b']) * Fr(2, 3))))
    T('D not dividing 1-u_b', lambda c: c.__setitem__('Dplus', str(Fr(c['Dplus']) * Fr(3, 2))))
    T('G_up below g(u_b)', lambda c: c.__setitem__('G_up', str(Fr(c['G_up']) * Fr(999, 1000))))
    T('jA0 -> last node (no slope data)', lambda c: c.__setitem__('jA0', len(c['qgrid']) - 1))
    T('tree -> single leaf', lambda c: c.__setitem__('tree', 'L'))
    T('q_1 below a_hi', lambda c: c['qgrid'].__setitem__(1, str(Fr(c['a_cut']) + (Fr(c['a_hi']) - Fr(c['a_cut'])) / 2)))
    rect = (Fr(0), Fr(cert['G_up']), -L.w, Fr(cert['P_up']))
    pth, U0 = worst_leaf_parent(cert['tree'], rect, L)
    assert U0 is not None and U0 < 0, 'checker A finds no feasible leaf with U < 0'
    f1 = max(2e-6, 8 * abs(float(U0))); f2 = max(1e-5, 40 * abs(float(U0)))
    def semantic(c, f):
        # margin probe: regenerate every data field at x' = x e^{f} with the generator's skeleton, keep the tree;
        # f exceeds the margin |U0| by the factors above, so some box must fail K10
        import math, genD
        ctl = dict(c['control']); xf = float(Fr(ctl['x'])) * math.exp(f)
        ctl['x'] = str(Fr(math.ceil(xf * 10**15), 10**15))
        new = genD.skeleton(ctl, float(Fr(c['u_b'])))
        new['tree'] = c['tree']
        c.clear(); c.update(new)
    T('margin probe: data at x e^{+%.2e}, same tree' % f1, lambda c: semantic(c, f1))
    T('margin probe: data at x e^{+%.2e}, same tree' % f2, lambda c: semantic(c, f2))
    def merge(c):
        node = c['tree']
        for i in pth[:-1] if pth else []:
            node = node[i]
        if pth:
            node[pth[-1]] = 'L'
        else:
            c['tree'] = 'L'
    T('merge the worst leaf with its sibling', merge)
    print('worst leaf U (checker A) = %.3e; margin probes at f1 = %.3e, f2 = %.3e' % (float(U0), f1, f2))
    ok = True
    for name, c in tampers:
        res = refuse(c)
        both = all(r[1] for r in res)
        ok &= both
        print('%-44s %s' % (name, '  '.join('%s %s' % (r[0], 'refused' if r[1] else 'ACCEPTED') for r in res)))
        for r in res:
            print('    %s: %s' % (r[0], r[2]))
    print('ALL %d TAMPERS REFUSED BY BOTH' % len(tampers) if ok else 'SOME TAMPER ACCEPTED')
    return ok


if __name__ == '__main__':
    sys.exit(0 if main(sys.argv[1]) else 1)
