"""Checker A, controls: verifies that a control (p, mu, w, beta, x, lxU, l1mL) satisfies ZBS's CtrlD.ok and that
CERT(p, mu, w, beta, x) < 0 with Q nonempty (ZBS Theorem 3.4 hypotheses, printed numbering), from the certificate data
(a_cut, q-grid, secant choices, heights h, index k).  Exact rationals + ivA outward intervals; no floats.

Mathematics (PROOF.md, Lemma C):
  G0(q) = q log p + beta (1-q) (log p + w log(1-q) - log x) - beta w q (log mu - log q) is convex on (0,1);
  Q = {q in (0,mu] : G0(q) < 0}; G0(a_cut) >= 0 > G0(mu) gives mu in Q and Q inside (a_cut, mu].
  H(q) = q M(q) + w q is concave on {G0 < 0}; a secant through grid points u < v of that set bounds H above at every
  point of the set outside (u, v).  If on each cell [q_i, q_{i+1}] such a secant is <= h_i, h_{i+1} at the cell ends,
  then sup_{q in Q} [H(q) + w q log t] <= max_i (h_i + w q_i log t); if moreover h_j <= h_k for j > k, the lines j > k
  are dominated for log t <= 0, and int_0^1 max_{i<=k}(h_i + w q_i log t) dt <= h_k - w q_k + sum_{i<k} D_i e^{r_i},
  D_i = w (q_{i+1} - q_i) > 0, r_i = (h_i - h_{i+1}) / D_i (EP Sec. 5 hinge bound)."""
if not __debug__:
    raise SystemExit('checker A is written with assert statements; refusing to run under python -O')
from fractions import Fraction as Fr
import ivA
from ivA import Iv


def _lt0(iv): return iv.hi < 0
def _ge0(iv): return iv.lo >= 0


def logs(p, mu, w, beta, x):
    return {'lp': ivA.log(p), 'lmu': ivA.log(mu), 'lx': ivA.log(x)}


def G0(q, P, L):
    p, mu, w, beta, x = P
    q = Fr(q)
    l1q = ivA.log(1 - q); lq = ivA.log(q)
    return (Iv.q(q) * L['lp'] + Iv.q(beta * (1 - q)) * (L['lp'] + Iv.q(w) * l1q - L['lx'])
            - Iv.q(beta * w * q) * (L['lmu'] - lq))


def H(q, P, L):
    """enclosure of H(q) = q M(q) + w q for q with G0(q) < 0; raises if q is not certified inside D."""
    p, mu, w, beta, x = P
    q = Fr(q)
    l1q = ivA.log(1 - q); lq = ivA.log(q)
    Aq = Iv.q((1 - q) / q) * (L['lp'] + Iv.q(w) * l1q - L['lx'])
    Bq = Iv.q(w) * (L['lmu'] - lq)
    def M2():
        arg = (ivA.exp(Iv.q(beta) * Bq) - Iv.q(p) * ivA.exp(Iv.q(beta) * Aq)) / Iv.q(1 - p)
        if arg.lo <= 0: raise ArithmeticError('q not certified in D')
        return Iv.q(p) * Aq + Iv.q((1 - p) / beta) * ivA.log(arg)
    if Aq.hi <= Bq.lo: M = Bq
    elif Aq.lo > Bq.hi: M = M2()
    else:
        m2 = M2(); M = Iv(min(Bq.lo, m2.lo), max(Bq.hi, m2.hi))
    return Iv.q(q) * M + Iv.q(w * q)


def check_control(c, verbose=False):
    """c: dict with rationals as strings. Returns (True, bound) or raises AssertionError."""
    p, mu, w, beta, x, lxU, l1mL = (Fr(c[k]) for k in ('p', 'mu', 'w', 'beta', 'x', 'lxU', 'l1mL'))
    # ZBS CtrlD.ok
    assert 0 < p < 1 and 0 < mu < 1 and 0 < w and 0 < beta < 1 and 0 < x < p, 'ranges'
    assert x <= ivA.exp(lxU).lof(), 'x <= exp(lxU)'
    assert ivA.exp(l1mL).hif() <= 1 - mu, 'exp(l1mL) <= 1 - mu'
    assert lxU < w * l1mL, 'lxU < w l1mL'
    if 'lemmaD' in c:
        # control kind CD: x is valid by Theorem A (ramsey-lemma PROOF.md) through Lemma D (CERT_DESIGN.md), checked by
        # the frozen checker A of that lane (code/lemmaD, frozen commit and SHA-256s in code/lemmaD/MANIFEST.sha256); used only for the second claim
        # "assuming Theorem A"
        assert 'cert' not in c, 'one certificate kind per control'
        import os, sys
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lemmaD'))
        import checkD_A
        worst = checkD_A.check(dict(control={k: c[k] for k in ('p', 'mu', 'w', 'beta', 'x')}, **c['lemmaD']), verbose=False)
        return True, worst
    P = (p, mu, w, beta, x); L = logs(*P)
    cert = c['cert']
    q = [Fr(t) for t in cert['q']]; h = [Fr(t) for t in cert['h']]; sec = cert['sec']; k = int(cert['k'])
    N = len(q) - 1
    assert len(h) == N + 1 and len(sec) == N and 0 <= k <= N and N >= 2
    assert Fr(cert['a_cut']) == q[0] and q[-1] == mu
    assert all(q[i] < q[i + 1] for i in range(N)) and q[0] > 0
    assert _ge0(G0(q[0], P, L)), 'G0(a_cut) >= 0'
    assert _lt0(G0(mu, P, L)), 'G0(mu) < 0'
    Hc = {}
    def Hat(i):
        if i not in Hc: Hc[i] = H(q[i], P, L)
        return Hc[i]
    for i in range(N):
        u, v = int(sec[i][0]), int(sec[i][1])
        assert 0 <= u < v <= N and (v <= i or u >= i + 1), 'secant on one side of cell %d' % i
        Hu, Hv = Hat(u), Hat(v)
        for node in (i, i + 1):
            t = (q[node] - q[u]) / (q[v] - q[u])
            if t >= 1: up = Iv.q(1 - t) * Iv(Hu.lo) + Iv.q(t) * Iv(Hv.hi)     # (1-t) <= 0: lower H(u)
            else:
                assert t <= 0
                up = Iv.q(1 - t) * Iv(Hu.hi) + Iv.q(t) * Iv(Hv.lo)          # t <= 0: lower H(v)
            assert up.hif() <= h[node], 'height at node %d, cell %d' % (node, i)
    assert all(h[j] <= h[k] for j in range(k + 1, N + 1)), 'lines past k dominated'
    tot = Iv.q(h[k] - w * q[k])
    for i in range(k):
        D = w * (q[i + 1] - q[i])
        tot = tot + Iv.q(D) * ivA.exp(Fr(h[i] - h[i + 1]) / D)
    assert tot.hif() < 0, 'hinge bound negative'
    return True, tot.hif()
