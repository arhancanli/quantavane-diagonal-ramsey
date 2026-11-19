"""Exploration (float): level (i) at the root, saturated drift. Per-row multipliers, cost vs gain densities."""
import numpy as np
P = dict(p=0.499999, mu=80725349867/200000000000, w=120299011257/250000000000, beta=1-1e-7,
         x=8107422360171/25000000000000)

def parts(q, p, mu, w, beta, x):
    with np.errstate(all='ignore'):
        A = (1-q)/q*np.log(p*(1-q)**w/x); B = w*np.log(mu/q)
        arg = (np.exp(beta*B) - p*np.exp(beta*A))/(1-p)
        M2 = p*A + (1-p)/beta*np.log(arg)
        M = np.where(A <= B, B, M2); feas = (A <= B) | (arg > 0)
    return np.where(feas, M, -np.inf)

def G0(q, p, mu, w, beta, x):
    return q*np.log(p) + beta*(1-q)*np.log(p*(1-q)**w/x) - beta*w*q*np.log(mu/q)

def a_of(eta, c=P):
    p, mu, w, beta, x = c['p'], c['mu'], c['w'], c['beta'], c['x']
    lo, hi = 1e-12, mu
    for _ in range(200):
        m = 0.5*(lo+hi)
        if G0(m, p, mu, w, beta, x) < beta*eta: hi = m
        else: lo = m
    return hi

def setup(c=P, nq=40001):
    p, mu, w, beta, x = c['p'], c['mu'], c['w'], c['beta'], c['x']
    a0 = a_of(0, c)
    q = a0 + (mu-a0)*np.linspace(0, 1, nq)[1:]
    M = parts(q, p, mu, w, beta, x)
    ok = np.isfinite(M)
    return q[ok], M[ok], a0

if __name__ == '__main__':
    c = P; w = c['w']
    q, M, a0 = setup(c)
    qM = q*M
    print('a0', a0, 'mu', c['mu'])
    for e in [0, 1e-4, 1e-3, 1e-2, 0.05, 0.1, 0.2]:
        print('  a(%g) = %.6f' % (e, a_of(e)), end='')
    print()
    al = (a_of(0) - a_of(1e-6))/1e-6
    print('alpha = -a\'(0) =', al)
    # saturated drift: phi(u) = -w(1+log u), phi(1) = -w. c(u) = int_u^1 a0 v (w/v) dv = a0 w (1-u)
    # per row: max q(M - phi(u)) s.t. qM - q phi(1) >= c(u)  i.e. qM + w q >= a0 w (1-u)
    u = np.concatenate([np.geomspace(1e-30, 1e-2, 3000), np.linspace(1e-2, 1, 5000)[1:]])
    du = np.diff(np.concatenate([[0], u]))
    phi = -w*(1+np.log(u))
    H = qM + w*q
    V0 = 0; V1 = 0; lam = np.zeros_like(u); qs = np.zeros_like(u); q0s = np.zeros_like(u)
    for i in range(len(u)):
        obj = qM - q*phi[i]
        j0 = np.argmax(obj); V0 += obj[j0]*du[i]; q0s[i] = q[j0]
        cu = a0*w*(1-u[i])
        okc = H >= cu
        j = np.argmax(np.where(okc, obj, -np.inf)); V1 += obj[j]*du[i]; qs[i] = q[j]
        if j != j0:
            # multiplier: d obj/dq = lam * (-dH/dq) at the binding point -> lam = -(obj'(q))/(H'(q))
            jj = min(j+1, len(q)-1)
            dobj = (obj[jj]-obj[j-1])/(q[jj]-q[j-1]); dH = (H[jj]-H[j-1])/(q[jj]-q[j-1])
            lam[i] = -dobj/dH
    print('V ZBS (sat) %.4e   V level(i) (sat, eta=0) %.4e' % (V0, V1))
    Lam = np.cumsum(lam*du)
    for t in [1e-20, 1e-10, 1e-5, 1e-3, 1e-2, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0]:
        i = np.argmin(abs(u-t))
        # q* slope in log u
        i2 = min(i+5, len(u)-1); i1 = max(i-5, 0)
        dqdlog = (qs[i2]-qs[i1])/(np.log(u[i2])-np.log(u[i1]))
        print('u=%-8g q0=%.4f q=%.4f lam=%.4f Lam=%.5f  dq/dlogu=%.4f  gain dens alpha*w*Lam=%.5f' % (
            t, q0s[i], qs[i], lam[i], Lam[i], dqdlog, al*w*Lam[i]))
    np.savez('<scratch>/cd/explore1.npz', u=u, lam=lam, qs=qs, q0s=q0s)
