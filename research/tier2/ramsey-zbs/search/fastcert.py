"""Fast float certificate (exploration only). EP form: q in F_p = {q in (0,mu]: Fc(q) <= 0} (an interval (qa, mu]),
H(q) = q M(q) + w q concave there; E(v) = max_q [H(q) + w q v] (v = log u); returns int_{-inf}^0 E(v) e^v dv,
computed exactly for the max of the sampled lines (a lower estimate of the true integral; fine for search)."""
import numpy as np
def Mq(q, p, mu, w, beta, x):
    A = (1-q)/q*np.log(p*(1-q)**w/x); B = w*np.log(mu/q)
    with np.errstate(all='ignore'):
        arg = (np.exp(beta*B) - p*np.exp(beta*A))/(1-p)
        M2 = p*A + (1-p)/beta*np.log(arg)
    return np.where(A <= B, B, M2), (A <= B) | (arg > 0)
def Fc(q, p, mu, w, beta, x):
    th = p*(x/p)**beta
    lZ = np.logaddexp(np.log(th) + np.log(p/th)/q, np.log1p(-th) + np.log((1-p)/(1-th))/q)
    return q*lZ + beta*w*((1-q)*np.log1p(-q) + q*np.log(q/mu))
def left_end(p, mu, w, beta, x):
    """smallest feasible q: Fc convex with Fc(mu) < 0 required; bisection for the root left of mu."""
    if not Fc(np.array([mu]), p, mu, w, beta, x)[0] < 0: return None
    lo, hi = 1e-9, mu
    for _ in range(60):
        m = 0.5*(lo+hi)
        if Fc(np.array([m]), p, mu, w, beta, x)[0] <= 0: hi = m
        else: lo = m
    return hi
def env_integral(h, a):
    """int_{-inf}^0 max_i (h_i + a_i v) e^v dv, a_i strictly increasing (assumed)."""
    # upper envelope over v in (-inf, 0]: smallest slope dominates at -inf
    st = []  # indices
    def xint(i, j): return (h[i]-h[j])/(a[j]-a[i])   # where line j overtakes line i (a_j > a_i)
    for j in range(len(h)):
        while st:
            i = st[-1]
            if len(st) >= 2 and xint(st[-2], i) >= xint(i, j): st.pop(); continue
            break
        st.append(j)
    # remove lines whose overtaking point is > 0 (never on top in v <= 0)
    bps = [-np.inf]; L = [st[0]]
    for k in range(1, len(st)):
        v = xint(L[-1], st[k])
        if v >= 0: break
        if v <= bps[-1]: L[-1] = st[k]; continue
        bps.append(v); L.append(st[k])
    bps.append(0.0)
    tot = 0.0
    for k, i in enumerate(L):
        v0, v1 = bps[k], bps[k+1]
        F = lambda v: (h[i] + a[i]*(v-1))*np.exp(v) if v > -np.inf else 0.0
        tot += F(v1) - F(v0)
    return tot
def cert(p, mu, w, beta, x, n=600):
    qa = left_end(p, mu, w, beta, x)
    if qa is None: return np.inf
    t = np.linspace(0, 1, n); q = qa + (mu-qa)*t
    M, feas = Mq(q, p, mu, w, beta, x)
    if not feas.all():
        q = q[feas]; M = M[feas]
        if len(q) < 2: return np.inf
    return env_integral(q*M + w*q, w*q)
def xmax(p, mu, w, beta=1-1e-7, tol=1e-10, n=600):
    cap = min(p, (1-mu)**w)*(1-1e-12)
    if cert(p, mu, w, beta, cap, n) < 0: return cap
    lo = None
    for xx in np.linspace(cap*0.98, cap*0.2, 25):
        if cert(p, mu, w, beta, xx, n) < 0: lo = xx; break
        hi = xx
    if lo is None: return None
    hi = cap if 'hi' not in dir() else hi
    while hi - lo > tol:
        m = 0.5*(lo+hi)
        if cert(p, mu, w, beta, m, n) < 0: lo = m
        else: hi = m
    return lo
if __name__ == '__main__':
    import time
    import certfloat as cf
    root = (0.499999999, 0.405108059767, 104160447497/250000000000, 0.9999999)
    t = time.time(); print('fast cert root x=0.337503:', cert(*root, 0.337503), time.time()-t)
    t = time.time(); print('xmax root', xmax(*root[:3], beta=root[3]), time.time()-t)
    child = (0.513412585543, 0.404343086429, 101922637213/250000000000)
    print('xmax child', xmax(*child, beta=0.9999999))
