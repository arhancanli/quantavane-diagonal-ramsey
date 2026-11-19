"""Float model (exploration only, proves nothing) of the two local certificates.
ZBS (zbs_main.tex Sec 3.2):  CERT = int_0^1 sup_{q in Q} [q M(q) + w q (1+log t)] dt,
   Q = {q in (0,mu]: A<=B or p e^{beta A} < U}.
EP (Paper/sections/03, 05): same objective, q restricted to F_p = {q in (0,mu]: Fc(q) <= 0},
   Fc(q) = q log Z_theta(q) + beta w [(1-q)log(1-q) + q log(q/mu)], theta = p (x/p)^beta.
E(u) = sup_q [H(q) + w q log u], H = qM + wq; returns int_0^1 E(u) du (negative = certificate exists)."""
import numpy as np
def M(q, p, mu, w, beta, x):
    A = (1-q)/q*np.log(p*(1-q)**w/x); B = w*np.log(mu/q); U = np.exp(beta*B)
    with np.errstate(all='ignore'):
        arg = (U - p*np.exp(beta*A))/(1-p)
        M2 = p*A + (1-p)/beta*np.log(arg)
    out = np.where(A <= B, B, M2)
    feas = (A <= B) | (arg > 0)
    return out, feas
def Fc(q, p, mu, w, beta, x):
    th = p*(x/p)**beta
    lZ = np.logaddexp(np.log(th) + np.log(p/th)/q, np.log1p(-th) + np.log((1-p)/(1-th))/q)
    return q*lZ + beta*w*((1-q)*np.log1p(-q) + q*np.log(q/mu))
def cert(p, mu, w, beta, x, comp=True, nq=20000, nu=4000):
    q = np.linspace(1e-6, mu, nq)
    m, feas = M(q, p, mu, w, beta, x)
    if comp: feas = feas & (Fc(q, p, mu, w, beta, x) <= 0)
    if not feas.any(): return np.inf, None
    q = q[feas]; H = q*m[feas] + w*q
    # integral over u in (0,1]: substitute u = e^{-s}, s in [0, inf): int E(e^{-s}) e^{-s} ds
    s = np.concatenate([np.linspace(0, 12, nu), np.linspace(12.01, 60, 400)])
    E = np.max(H[None, :] - w*q[None, :]*s[:, None], axis=1)
    f = E*np.exp(-s)
    return np.trapz(f, s), q.min()
def xmax(p, mu, w, beta, comp=True, lo=None, hi=None, ngrid=60):
    cap = min(p, (1-mu)**w)*(1-1e-9)
    xs = np.linspace(cap*0.3, cap, ngrid)
    cs = [cert(p, mu, w, beta, xx, comp)[0] for xx in xs]
    neg = [i for i, c in enumerate(cs) if c < 0]
    if not neg: return None
    i = max(neg)
    if i == len(xs)-1: return cap
    lo, hi = xs[i], xs[i+1]
    for _ in range(50):
        mid = 0.5*(lo+hi)
        c, _ = cert(p, mu, w, beta, mid, comp)
        if c < 0: lo = mid
        else: hi = mid
    return lo
if __name__ == '__main__':
    import sys
    child = (0.513412585543, 0.404343086429, 101922637213/250000000000, 0.9999999)
    root = (0.499999999, 0.405108059767, 104160447497/250000000000, 0.9999999)
    for nm, (p, mu, w, b) in [('child', child), ('root', root)]:
        xz = xmax(p, mu, w, b, comp=False); xc = xmax(p, mu, w, b, comp=True)
        print(nm, 'ZBS x_max %.6f  comp x_max %.6f  -log: %.6f %.6f' % (xz, xc, -np.log(xz), -np.log(xc)))
    print('EP published: child x 0.350832374917 (ZBS-form), root x 0.337503 (comp)')
    print('cert at published root x (comp):', cert(*root, 0.337503, True))
    print('cert at published child x (zbs):', cert(*child, 0.350832374917, False))
