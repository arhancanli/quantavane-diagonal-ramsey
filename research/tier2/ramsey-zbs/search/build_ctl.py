"""Build an exact-data certificate for one control (proposes data only; the checkers decide).

Certificate of CERT(p, mu, w, beta, x) < 0 in ZBS's form (ZBS Sec. 3.2; feasible set Q = D cap (0, mu],
D = {q : G0(q) < 0}, G0(q) = q log p + beta(1-q) log(p (1-q)^w / x) - beta w q log(mu/q), convex):
  a_cut with G0(a_cut) >= 0 and G0(mu) < 0         => Q is inside (a_cut, mu] and mu in Q;
  grid a_cut = q_0 < q_1 < ... < q_N = mu; for each cell a secant of H = qM + wq through two grid points on one side
  of the cell (H is concave on D), extended over the cell; heights h_i above those extensions at the cell ends;
  k = argmax_i h_i (then h_j <= h_k for j > k, so those lines are dominated for v = log u <= 0);
  hinge bound  h_k - w q_k + sum_{i<k} w (q_{i+1} - q_i) exp(r_i) < 0,  r_i = (h_i - h_{i+1}) / (w (q_{i+1} - q_i)).
Output: dict of rationals as strings.
"""
from fractions import Fraction as Fr
import math


def G0f(q, p, mu, w, beta, x):
    return q * math.log(p) + beta * (1 - q) * math.log(p * (1 - q) ** w / x) - beta * w * q * math.log(mu / q)


def Hf(q, p, mu, w, beta, x):
    A = (1 - q) / q * math.log(p * (1 - q) ** w / x); B = w * math.log(mu / q)
    if A <= B: M = B
    else:
        arg = (math.exp(beta * B) - p * math.exp(beta * A)) / (1 - p)
        if arg <= 0: return -math.inf
        M = p * A + (1 - p) / beta * math.log(arg)
    return q * M + w * q


def rat(v, den=10 ** 15, up=True):
    n = math.ceil(v * den) if up else math.floor(v * den)
    return Fr(n, den)


def build(p, mu, w, beta, x, N=256, pad=1e-7):
    """p, mu, w, beta, x: Fractions. Returns certificate dict or None."""
    pf, muf, wf, bf, xf = map(float, (p, mu, w, beta, x))
    if not G0f(muf, pf, muf, wf, bf, xf) < -1e-12: return None
    lo, hi = 1e-9, muf
    for _ in range(80):
        m = 0.5 * (lo + hi)
        if G0f(m, pf, muf, wf, bf, xf) < 0: hi = m
        else: lo = m
    a = rat(lo * (1 - 1e-12), 10 ** 12, up=False)                  # G0(a) >= 0 (checked exactly later)
    qs = [a + (mu - a) * Fr(i, N) for i in range(N + 1)]
    qf = [float(q) for q in qs]
    H = [Hf(q, pf, muf, wf, bf, xf) if i > 0 else -math.inf for i, q in enumerate(qf)]
    # majorant per cell: cell i = [q_i, q_{i+1}]; use the secant through (q_{i+2}, q_{i+3}) extended left for
    # the first two cells, else the secant through (q_{i-1}, q_i) extended right.
    def secant_val(u, v, q):
        return H[u] + (H[v] - H[u]) * (qf[q] - qf[u]) / (qf[v] - qf[u])
    sec = []
    hs = [-math.inf] * (N + 1)
    for i in range(N):
        uv = (i + 2, i + 3) if i < 2 else (i - 1, i)
        sec.append(uv)
        for q in (i, i + 1):
            hs[q] = max(hs[q], secant_val(uv[0], uv[1], q))
    hs = [rat(h + pad * 1e-3 + 1e-12) for h in hs]
    # lines past the largest height are dominated on v <= 0 (larger slope, no larger height): truncate at k
    k = max(range(N + 1), key=lambda i: hs[i])
    tot = float(hs[k]) - wf * qf[k]
    for i in range(k):
        d = wf * (qf[i + 1] - qf[i]); r = (float(hs[i]) - float(hs[i + 1])) / d
        tot += d * math.exp(r)
    return {'a_cut': str(a), 'q': [str(q) for q in qs], 'h': [str(h) for h in hs], 'sec': sec, 'k': k, 'float_bound': tot}
