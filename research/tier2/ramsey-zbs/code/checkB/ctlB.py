"""Checker B, controls (written separately from checker A): python-flint Arb balls + fmpq rationals.

H is evaluated through the identity (EP Sec. 5)  H(q) = q B_q + w q + (q/beta) [fbar(G0(q)/q) - f(log p)],
f(z) = p z + (1-p) log(1 - e^z), fbar(z) = f(max(z, log p)) (nonincreasing on z < 0), B_q = w log(mu/q), and
G0(q) = q log p + beta q (A_q - B_q), A_q = ((1-q)/q) log(p (1-q)^w / x).  (Checker A uses the two-branch formula.)
Checks: CtrlD.ok of ZBS; G0(a_cut) >= 0 > G0(mu); secant majorants at every cell end; dominance past k; hinge sum < 0.
"""
import flint
from flint import arb, fmpq
flint.ctx.prec = 320


def Q(s):
    s = str(s)
    if '/' in s:
        n, d = s.split('/'); return fmpq(int(n), int(d))
    return fmpq(int(s))


def A_(r): return arb(r)


class Ctl:
    def __init__(self, p, mu, w, beta, x):
        self.p, self.mu, self.w, self.beta, self.x = p, mu, w, beta, x
        self.lp = A_(p).log(); self.lmu = A_(mu).log(); self.lx = A_(x).log()
        self.flp = A_(p) * self.lp + A_(1 - p) * A_(1 - p).log()      # f(log p) = p log p + (1-p) log(1-p)

    def G0(self, q):
        qa = A_(q)
        Aq = A_((1 - q) / q) * (self.lp + A_(self.w) * A_(1 - q).log() - self.lx)
        Bq = A_(self.w) * (self.lmu - qa.log())
        return qa * self.lp + A_(self.beta) * qa * (Aq - Bq), Bq

    def f(self, z):
        return A_(self.p) * z + A_(1 - self.p) * (1 - z.exp()).log()

    def H(self, q):
        g0, Bq = self.G0(q)
        if not g0 < 0: raise ArithmeticError('q not certified in D')
        z = g0 / A_(q)
        zl, zh = arb(z.lower()), arb(z.upper())
        def fbar(t):
            if t <= self.lp: return self.flp
            if t > self.lp: return self.f(t)
            return self.flp.union(self.f(t))     # undecided comparison: either branch
        lo_v, hi_v = fbar(zh), fbar(zl)          # fbar nonincreasing: fbar(z) in [fbar(zh), fbar(zl)]
        fb = lo_v.union(hi_v)
        return A_(q) * Bq + A_(self.w * q) + A_(q) / A_(self.beta) * (fb - self.flp)


def check_control(c):
    p, mu, w, beta, x, lxU, l1mL = (Q(c[k]) for k in ('p', 'mu', 'w', 'beta', 'x', 'lxU', 'l1mL'))
    ok = (0 < p < 1) and (0 < mu < 1) and (w > 0) and (0 < beta < 1) and (0 < x < p)
    if not ok: raise AssertionError('ranges')
    if not A_(x) <= A_(lxU).exp(): raise AssertionError('x <= exp(lxU)')
    if not A_(l1mL).exp() <= A_(1 - mu): raise AssertionError('exp(l1mL) <= 1-mu')
    if not lxU < w * l1mL: raise AssertionError('lxU < w l1mL')
    if 'lemmaD' in c:
        # control kind CD (second claim, assuming Theorem A): the frozen Arb checker of ramsey-lemma (code/lemmaD)
        if 'cert' in c: raise AssertionError('one certificate kind per control')
        import os, sys
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lemmaD'))
        import flint
        if flint.__version__ != '0.9.0': raise AssertionError('Lemma D checker B is pinned to python-flint 0.9.0')
        prec0 = flint.ctx.prec
        try:
            import checkD_B                        # sets its own working precision (300 bits) ...
            worst = checkD_B.check(dict(control={k: c[k] for k in ('p', 'mu', 'w', 'beta', 'x')}, **c['lemmaD']), verbose=False)
        finally:
            flint.ctx.prec = prec0                 # ... which must not leak into the rest of checker B (referee F6)
        return True, worst
    C = Ctl(p, mu, w, beta, x)
    cert = c['cert']
    q = [Q(t) for t in cert['q']]; h = [Q(t) for t in cert['h']]; sec = cert['sec']; k = int(cert['k'])
    N = len(q) - 1
    if not (len(h) == N + 1 and len(sec) == N and 0 <= k <= N and Q(cert['a_cut']) == q[0] and q[N] == mu):
        raise AssertionError('shape')
    for i in range(N):
        if not q[i] < q[i + 1]: raise AssertionError('grid order')
    if not q[0] > 0: raise AssertionError('a_cut > 0')
    if not C.G0(q[0])[0] >= 0: raise AssertionError('G0(a_cut) >= 0')
    if not C.G0(mu)[0] < 0: raise AssertionError('G0(mu) < 0')
    cache = {}
    def Hat(i):
        if i not in cache: cache[i] = C.H(q[i])
        return cache[i]
    for i in range(N):
        u, v = int(sec[i][0]), int(sec[i][1])
        if not (0 <= u < v <= N and (v <= i or u >= i + 1)): raise AssertionError('secant side')
        for node in (i, i + 1):
            # extended secant at q[node]: H(u) + (H(v)-H(u)) * (q-q_u)/(q_v-q_u); evaluate as a ball (sound)
            t = (q[node] - q[u]) / (q[v] - q[u])
            val = Hat(u) + (Hat(v) - Hat(u)) * A_(t)
            if not val <= A_(h[node]): raise AssertionError('height node %d cell %d' % (node, i))
    for j in range(k + 1, N + 1):
        if not h[j] <= h[k]: raise AssertionError('dominance past k')
    tot = A_(h[k] - w * q[k])
    for i in range(k):
        D = w * (q[i + 1] - q[i])
        tot += A_(D) * A_((h[i] - h[i + 1]) / D).exp()
    if not tot < 0: raise AssertionError('hinge bound negative')
    return True, tot.upper()
