#!/usr/bin/env python3
"""tamper_C: minimal tampers of a Lemma D certificate, designed from CERT_DESIGN 4c (K1-K10) only.

Each tamper moves ONE hypothesis across its boundary by (close to) the smallest amount that breaks
it, writes the tampered JSON to OUTDIR and runs checkD_C on it.  Every tamper must be refused.
Usage: tamper_C.py CERT.json OUTDIR
"""
import os
import sys
import json
import copy
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checkD_C as C  # noqa: E402

TINY = Fr(1, 10 ** 30)


def S(F):
    return str(Fr(F))


def bracket_a0(M, lo, hi, steps=110):
    """[l, h] with G0(l) >= 0 certified (or l = lo) and G0(h) < 0 certified: around a(0)."""
    for _ in range(steps):
        m = (lo + hi) / 2
        g = M.G0(m)
        if g.lo >= 0:
            lo = m
        elif g.hi < 0:
            hi = m
        else:
            break
    return lo, hi


def find_worst_path(rows):
    best = None
    for r in rows:
        if r[6] is not None and (best is None or r[6] > best[6]):
            best = r
    return best


def merge_parent(tree, path):
    """Replace the parent of the leaf at `path` (string of P1/P2/p1/p2 tokens) by a leaf."""
    toks = [path[i:i + 2] for i in range(0, len(path), 2)]
    if not toks:
        return 'L'
    t = copy.deepcopy(tree)
    node = t
    for tok in toks[:-2]:
        node = node[1] if tok[1] == '1' else node[2]
    if len(toks) == 1:
        return 'L'
    k = 1 if toks[-2][1] == '1' else 2
    node[k] = 'L'
    return t


def main():
    src, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    raw = json.load(open(src))
    cert = C.load_cert(src)
    quiet = []
    base = C.Checker(cert, log=quiet.append)
    acc, worst, nleaf = base.run()
    print('base %s: %s, worst U <= %s' % (os.path.basename(src), 'ACCEPT' if acc else 'REJECT', C.dec(worst)))
    M = base.M
    p, mu, w, beta, x = cert['p'], cert['mu'], cert['w'], cert['beta'], cert['x']
    a_cut, a_hi, u_b = cert['a_cut'], cert['a_hi'], cert['u_b']
    N = len(cert['qgrid']) - 1
    tampers = []

    def T(name, why, f):
        d = copy.deepcopy(raw)
        f(d)
        tampers.append((name, why, d))

    # K1
    T('x_eq_p', 'K1: x < p broken (x = p)', lambda d: d['control'].__setitem__('x', S(p)))
    # K2: move a_cut just past a(0) (and q_0 with it), a_hi just before a(0), alpha just below its bound
    l, h = bracket_a0(M, a_cut, a_hi)

    def acut_in(d):
        d['a_cut'] = S(h)
        d['qgrid'][0] = S(h)
    T('a_cut_past_a0', 'K2: G0(a_cut) >= 0 broken (a_cut = a(0) + <%s)' % C.dec(h - l), acut_in)
    T('a_hi_before_a0', 'K2: G0(a_hi) < 0 broken (a_hi = a(0) - <%s)' % C.dec(h - l), lambda d: d.__setitem__('a_hi', S(l)))
    gp = M.G0p(a_hi)
    bound_lo = beta / (-gp.lof())          # <= beta/|G0'(a_hi)|
    T('alpha_below', "K2: alpha >= beta/|G0'(a_hi)| broken by 1e-30", lambda d: d.__setitem__('alpha', S(bound_lo - TINY)))
    g_cut = M.G0(a_cut)
    dx = 2 * g_cut.hif() * x / (beta * (1 - a_cut))
    T('x_up', 'K2: control x raised by %s (G0(a_cut) turns negative)' % C.dec(dx),
      lambda d: d['control'].__setitem__('x', S(x + dx)))
    dp = 2 * g_cut.hif() * p / (a_cut + beta * (1 - a_cut))
    T('p_down', 'K2: control p lowered by %s (G0(a_cut) turns negative)' % C.dec(dp),
      lambda d: d['control'].__setitem__('p', S(p - dp)))
    AmB = M.branches(C.IV.of(a_hi), 0)[0]
    dbeta = 2 * (-M.G0(a_hi).lof()) / (a_hi * AmB.lof())
    T('beta_up', 'K2: control beta raised by %s (G0(a_hi) turns >= 0)' % C.dec(dbeta),
      lambda d: d['control'].__setitem__('beta', S(beta + dbeta)))
    # K3
    T('Dplus_nonint', 'K3: (1-u_b)/Dplus not an integer (Dplus + 1e-30)', lambda d: d.__setitem__('Dplus', S(cert['Dplus'] + TINY)))
    T('u_b_shift', 'K3: (1-u_b)/Dplus not an integer (u_b + 1e-30)', lambda d: d.__setitem__('u_b', S(u_b + TINY)))
    # K4
    T('q1_below_a_hi', 'K4: q_1 >= a_hi broken by 1e-30', lambda d: d['qgrid'].__setitem__(1, S(a_hi - TINY)))
    T('qN_ne_mu', 'K4: q_N = mu broken by 1e-30', lambda d: d['qgrid'].__setitem__(N, S(mu - TINY)))

    def swap(d):
        d['qgrid'][5], d['qgrid'][6] = d['qgrid'][6], d['qgrid'][5]
    T('q_unsorted', 'K4: q not increasing (q_5, q_6 swapped)', swap)
    # K6
    T('jA0_zero', 'K6: jA0 = 0', lambda d: d.__setitem__('jA0', 0))
    T('jA0_N', 'K6: jA0 = N', lambda d: d.__setitem__('jA0', N))
    jAs = [r[7].get('jA') for r in base.rows if r[7] and r[7].get('jA') is not None]
    if jAs:
        T('jA0_above_minjA', 'K10 step 5: jA0 = (least jA over boxes) + 1 = %d' % (min(jAs) + 1),
          lambda d: d.__setitem__('jA0', min(jAs) + 1))
    # K7 / K8
    Htp_mu = base.Htpn[N]
    T('y_c_below_Htp_mu', "K7: y_c >= Ht'(mu) broken by 1e-30", lambda d: d.__setitem__('y_c', S(Htp_mu.lof() - TINY)))
    T('y_c_eq_minus_w', 'K7: y_c > -w broken (y_c = -w)', lambda d: d.__setitem__('y_c', S(-w)))
    T('y_c_above_phis', 'K8: phi_s(u_b) >= y_c broken by 1e-30', lambda d: d.__setitem__('y_c', S(base.phis_ub.hif() + TINY)))
    # K9
    T('G_up_below_g', 'K9: G_up >= g(u_b) broken by 1e-30', lambda d: d.__setitem__('G_up', S(base.g_ub.lof() - TINY)))
    mwl = -w * C.ilog(u_b)
    T('P_up_below', 'K9: P_up >= -w log u_b broken by 1e-30', lambda d: d.__setitem__('P_up', S(mwl.lof() - TINY)))
    dw = 2 * (cert['G_up'] - base.g_ub.lof()) / (-u_b * C.ilog(u_b).hif())
    T('w_up', 'K9 (and others): control w raised by %s so g(u_b) > G_up' % C.dec(dw),
      lambda d: d['control'].__setitem__('w', S(w + dw)))
    # K10
    T('tree_root_leaf', 'K10: whole rectangle as one leaf', lambda d: d.__setitem__('tree', 'L'))
    wr = find_worst_path(base.rows)
    if wr is not None and wr[0]:
        T('tree_merge_worst', 'K10: worst leaf %s merged with its sibling' % wr[0],
          lambda d: d.__setitem__('tree', merge_parent(raw['tree'], wr[0])))
    # format
    T('fmt_float', 'format: a rational given as a JSON number', lambda d: d.__setitem__('alpha', 0.8))

    def badaxis(d):
        d['tree'] = ['X', 'L', 'L']
    T('fmt_axis', 'format: tree axis "X"', badaxis)
    T('fmt_zero_den', 'format: denominator 0', lambda d: d.__setitem__('y_c', '1/0'))
    T('fmt_missing', 'format: field tree missing', lambda d: d.pop('tree'))

    refused = 0
    for name, why, d in tampers:
        path = os.path.join(outdir, 'tC_%s.json' % name)
        with open(path, 'w') as f:
            json.dump(d, f)
        lines = []
        try:
            ct = C.load_cert(path)
            ch = C.Checker(ct, log=lines.append, stop_on_data_fail=True)
            acc_t, worst_t, _ = ch.run()
            first = ch.fails[0] if ch.fails else '(no data failure; worst U <= %s)' % C.dec(worst_t) if worst_t is not None else ''
        except C.CertError as e:
            acc_t, first = False, 'format: %s' % e
        except Exception as e:  # any crash counts as refusal but is reported
            acc_t, first = False, 'EXCEPTION %s: %s' % (type(e).__name__, e)
        refused += (not acc_t)
        print('%-20s %-7s %s\n%22s first failure: %s' % (name, 'REFUSED' if not acc_t else 'ACCEPTED', why, '', first[:160]))
    print('tamper_C: %d / %d refused' % (refused, len(tampers)))

    # positive controls: legitimate variants that must still be ACCEPTED
    def split_leaves(t):
        if t == 'L':
            return ['P', 'L', 'L']
        return [t[0], split_leaves(t[1]), split_leaves(t[2])]
    controls = []

    def CT(name, f):
        d = copy.deepcopy(raw)
        f(d)
        controls.append((name, d))
    CT('ctrl_split_all_leaves', lambda d: d.__setitem__('tree', split_leaves(raw['tree'])))
    CT('ctrl_D_half', lambda d: d.__setitem__('Dplus', S(cert['Dplus'] / 2)))

    def acut_low(d):
        d['a_cut'] = S(a_cut - TINY)
        d['qgrid'][0] = d['a_cut']
    CT('ctrl_a_cut_lower', acut_low)
    accepted = 0
    for name, d in controls:
        path = os.path.join(outdir, 'tC_%s.json' % name)
        with open(path, 'w') as f:
            json.dump(d, f)
        ch = C.Checker(C.load_cert(path), log=[].append)
        acc_t, worst_t, nl = ch.run()
        accepted += acc_t
        print('%-20s %-8s leaves=%d worst U <= %s' % (name, 'ACCEPTED' if acc_t else 'REFUSED', nl, C.dec(worst_t) if worst_t is not None else 'n/a'))
    print('controls: %d / %d accepted' % (accepted, len(controls)))

    # informational: coarser mesh, (1 - u_b)/D still an integer; the mesh terms of U(B) grow with D
    n0 = (1 - u_b) / cert['Dplus']
    for k in (2, 4, 8, 16):
        if (n0 / k).denominator != 1:
            continue
        d = copy.deepcopy(raw)
        d['Dplus'] = S(cert['Dplus'] * k)
        path = os.path.join(outdir, 'tC_D_times_%d.json' % k)
        with open(path, 'w') as f:
            json.dump(d, f)
        ch = C.Checker(C.load_cert(path), log=[].append)
        acc_t, worst_t, nl = ch.run()
        print('sweep D x %-3d %-8s worst U <= %s' % (k, 'ACCEPTED' if acc_t else 'REFUSED', C.dec(worst_t) if worst_t is not None else 'n/a'))
    return 0 if (refused == len(tampers) and accepted == len(controls)) else 1


if __name__ == '__main__':
    sys.exit(main())
