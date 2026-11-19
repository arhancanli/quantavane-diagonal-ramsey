import json, sys, math, time
from fractions import Fraction as Fr
src = open("vafloat.py").read().split("# exact c on the grid")[0]
exec(src)
# a(eta) table: left root of G0 = beta*eta (0 if none)
lp0 = math.log(p/x)
def a_of(eta):
    if beta*eta >= beta*lp0: return 0.0
    lo, hi = 1e-15, a0
    for _ in range(80):
        m = 0.5*(lo+hi)
        if G0(m) > beta*eta: lo = m
        else: hi = m
    return hi
ET = [i*0.002 for i in range(0, 2001)]; AT = [a_of(e) for e in ET]
def a_interp(eta):
    if eta >= ET[-1]: return a_of(eta)
    i = int(eta/0.002); t = (eta - ET[i])/0.002
    return min(AT[i], AT[i] + t*(AT[i+1]-AT[i]))   # min with left value: a decreasing, chord above convex a -> use lower-ish
g = lambda u: -w*u*math.log(u)
def simpson(f, a, b, N):
    h = (b-a)/N; s = f(a) + f(b)
    for i in range(1, N): s += (4 if i % 2 else 2)*f(a + i*h)
    return s*h/3
def VA(phi, Phi, f1, label):
    n = round((1 - u_b)/D)
    vs = [u_b + j*D for j in range(n)] + [1.0]
    ph = [phi(vv) for vv in vs[:-1]] + [f1]
    S = [0.0]*(n+1); acc = 0.0
    for j in range(n-1, -1, -1):
        dj = ph[j] - ph[j+1]
        if dj < -1e-12: raise ValueError("not nonincreasing")
        if dj > 0:
            vj = vs[j]; eta = min(w*math.log(1/vj), max(0.0, (g(vj) - Phi(vj))/vj))
            acc += a_interp(eta)*vj*dj
        S[j] = acc
    def cfun(u):
        if u <= u_b: return S[0]
        k = math.ceil((u - u_b)/D - 1e-12); return S[k] if k <= n-1 else 0.0
    qf = qhat(f1)
    Hmax = Ht(qf) - f1*qf
    def integ(u):
        c = cfun(u); y = phi(u)
        if Hmax < c: return -math.inf
        lo_, hi_ = a0*(1+1e-15), qf
        for _ in range(60):
            m = 0.5*(lo_+hi_)
            if Ht(m) - f1*m >= c: hi_ = m
            else: lo_ = m
        qlo = hi_
        if Ht(mu) - f1*mu >= c: qhi = mu
        else:
            lo_, hi_ = qf, mu
            for _ in range(60):
                m = 0.5*(lo_+hi_)
                if Ht(m) - f1*m >= c: lo_ = m
                else: hi_ = m
            qhi = lo_
        q = min(max(qhat(y), qlo), qhi)
        return Ht(q) - q*y
    Lp = simpson(lambda s: integ(u_b*math.exp(-s))*u_b*math.exp(-s), 0.0, 60.0, 4000)
    Rp = simpson(integ, u_b, 1.0, 8000)
    print("%-28s V_A ~ %.4e" % (label, Lp + Rp), flush=True)
for s0 in (0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 0.9, 0.98):
    lam = w*s0*math.log(s0)/(1 - s0)
    phi = (lambda s0, lam: (lambda u: -w*(1+math.log(u)) if u <= s0 else lam))(s0, lam)
    Phi = (lambda s0, lam: (lambda u: g(u) if u <= s0 else g(s0) + lam*(u - s0)))(s0, lam)
    VA(phi, Phi, lam, "sat-then-flat s0=%.2f" % s0)
# two-level step: phi = A on (0,t], B on (t,1], A t + B (1-t) = 0, A <= -w log t (Phi<=g at t suffices by concavity? check at grid)
for t, A in ((0.1, 1.0), (0.3, 0.6), (0.5, 0.4), (0.03, 2.0), (0.6, 0.25)):
    B = -A*t/(1-t)
    if A*t > g(t) or B < -w: print("skip", t, A); continue
    phi = (lambda t, A, B: (lambda u: A if u <= t else B))(t, A, B)
    Phi = (lambda t, A, B: (lambda u: A*u if u <= t else A*t + B*(u - t)))(t, A, B)
    # admissibility Phi<=g needs A <= -w log u on (0,t]: A <= -w log t
    if A > -w*math.log(t): print("skip (Phi>g)", t, A); continue
    VA(phi, Phi, B, "step t=%.2f A=%.2f" % (t, A))
