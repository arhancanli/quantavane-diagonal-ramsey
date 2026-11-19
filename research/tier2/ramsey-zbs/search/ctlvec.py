"""Vectorised float version of the Lemma C control certificate (ZBS form, PROOF.md Sec. 3), exactly as build_ctl.py
lays it out (uniform grid a_cut..mu with N cells, secants (i+2,i+3) for i<2 else (i-1,i), hinge bound).  Used to
tabulate the CERTIFIABLE x (largest x whose float hinge bound is below -tol), so the search model uses values a
certificate can realise.  Exploration only: every control actually used is re-certified exactly by checkers A and B."""
import numpy as np


def G0(q, p, mu, w, beta, x):
    return q * np.log(p) + beta * (1 - q) * np.log(p * (1 - q) ** w / x) - beta * w * q * np.log(mu / q)


def Hq(q, p, mu, w, beta, x):
    with np.errstate(all='ignore'):
        A = (1 - q) / q * np.log(p * (1 - q) ** w / x); B = w * np.log(mu / q)
        arg = (np.exp(beta * B) - p * np.exp(beta * A)) / (1 - p)
        M2 = p * A + (1 - p) / beta * np.log(arg)
        M = np.where(A <= B, B, M2)
        return np.where((A <= B) | (arg > 0), q * M + w * q, np.nan)


def bound(p, mu, w, beta, x, N=512):
    """arrays of shape (K,) -> float hinge bound (inf if Q empty / not certifiable)."""
    p, mu, w, beta, x = (np.asarray(v, float)[:, None] for v in (p, mu, w, beta, x))
    ok = (G0(mu, p, mu, w, beta, x) < -1e-12)[:, 0]
    lo = np.full_like(mu, 1e-12); hi = mu.copy()
    for _ in range(64):
        m = 0.5 * (lo + hi); neg = G0(m, p, mu, w, beta, x) < 0
        hi = np.where(neg, m, hi); lo = np.where(neg, lo, m)
    a = lo * (1 - 1e-12)
    t = np.arange(N + 1)[None, :] / N
    q = a + (mu - a) * t
    H = Hq(q, p, mu, w, beta, x); H[:, 0] = np.nan
    ok &= np.isfinite(H[:, 1:]).all(axis=1)
    # secant extension values at cell ends
    hs = np.full(q.shape, -np.inf)
    i = np.arange(N)
    u = np.where(i < 2, i + 2, i - 1); v = np.where(i < 2, i + 3, i)
    for node in (i, i + 1):
        val = H[:, u] + (H[:, v] - H[:, u]) * (q[:, node] - q[:, u]) / (q[:, v] - q[:, u])
        hs[:, node] = np.maximum(hs[:, node], val)
    hs = hs + 1e-10
    k = np.argmax(hs, axis=1)
    K = len(k); rows = np.arange(K)
    D = w * (q[:, 1:] - q[:, :-1]); r = (hs[:, :-1] - hs[:, 1:]) / D
    with np.errstate(over='ignore'):
        terms = D * np.exp(r)
    mask = np.arange(N)[None, :] < k[:, None]
    tot = hs[rows, k] - w[:, 0] * q[rows, k] + np.where(mask, terms, 0).sum(axis=1)
    return np.where(ok & np.isfinite(tot), tot, np.inf)


def xcert(p, mu, w, beta=1 - 1e-7, N=512, tol=1e-9, iters=48):
    """largest x (bisection, relative precision ~1e-12) with bound < -tol; nan if none.  Vectorised."""
    p, mu, w = (np.atleast_1d(np.asarray(v, float)) for v in (p, mu, w))
    p, mu, w = np.broadcast_arrays(p, mu, w)
    beta = np.full(p.shape, beta)
    cap = np.minimum(p, (1 - mu) ** w) * (1 - 1e-10)
    fr = np.linspace(1.0, 0.25, 31)
    lo = np.full(cap.shape, np.nan); hi = np.full(cap.shape, np.nan)
    for k, f in enumerate(fr):                       # largest feasible scan point (CERT < 0 holds on an x-window)
        b = bound(p, mu, w, beta, cap * f, N) < -tol
        new = b & np.isnan(lo)
        lo = np.where(new, cap * f, lo); hi = np.where(new, cap * fr[max(k - 1, 0)], hi)
    top = lo == cap
    for _ in range(iters):
        m = 0.5 * (lo + hi)
        b = bound(p, mu, w, beta, np.where(np.isfinite(m), m, cap * 0.5), N) < -tol
        lo = np.where(b & ~top, m, lo); hi = np.where(b | top, hi, m)
    return lo
