"""Exploration (proves nothing): the extremal limiting configuration of ZBS's CERT relaxation at a control.

For a control (p, mu, w, beta, x) with CERT = int_0^1 sup_{q in Q} [H(q) + w q log t] dt, H = q M(q) + w q,
the relaxation is tight for the quantile function Q(t) = argmax_q [H(q) + w q log t] (nondecreasing in t), the
row drift phi(t) = -w (1 + log t) (rows sorted by blue degree) and row gains zeta(t) = M(Q(t)).
Identity used (exact at finite r, see NOTES.md): zeta_i = r E_nu Z_i = average of phi_j over j in B_i.
"""
import numpy as np
from fractions import Fraction as F

ROOT = dict(p=0.499999, mu=80725349867 / 200000000000, w=120299011257 / 250000000000, beta=1 - 1e-7,
            x=8107422360171 / 25000000000000)


def parts(q, p, mu, w, beta, x):
    with np.errstate(all='ignore'):
        A = (1 - q) / q * np.log(p * (1 - q) ** w / x)
        B = w * np.log(mu / q)
        U = np.exp(beta * B)
        arg = (U - p * np.exp(beta * A)) / (1 - p)
        M2 = p * A + (1 - p) / beta * np.log(arg)
        M = np.where(A <= B, B, M2)
        feas = (A <= B) | (arg > 0)
        # binding-branch outside cell value C: p A + (1-p) C = M
        C = np.where(A <= B, B, (1 - p) ** -1 * (M - p * np.where(A <= B, B, A)))
    return A, B, M, C, feas


def G0(q, p, mu, w, beta, x):
    return q * np.log(p) + beta * (1 - q) * np.log(p * (1 - q) ** w / x) - beta * w * q * np.log(mu / q)


def left_end(p, mu, w, beta, x):
    lo, hi = 1e-12, mu
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if G0(m, p, mu, w, beta, x) < 0: hi = m
        else: lo = m
    return hi


def envelope(c, nq=200001, ts=None):
    p, mu, w, beta, x = c['p'], c['mu'], c['w'], c['beta'], c['x']
    a = left_end(p, mu, w, beta, x)
    q = a + (mu - a) * np.linspace(0, 1, nq)[1:]
    A, B, M, C, feas = parts(q, p, mu, w, beta, x)
    q, M, A, B, C = q[feas], M[feas], A[feas], B[feas], C[feas]
    H = q * M + w * q
    if ts is None:
        s = np.concatenate([np.linspace(0, 12, 6001), np.linspace(12.002, 80, 3000)])
    else:
        s = -np.log(ts)
    # argmax for each s (t = e^{-s})
    idx = np.empty(len(s), int)
    for k0 in range(0, len(s), 500):
        ss = s[k0:k0 + 500]
        idx[k0:k0 + 500] = np.argmax(H[None, :] - w * q[None, :] * ss[:, None], axis=1)
    E = H[idx] - w * q[idx] * s
    certv = np.trapezoid(E * np.exp(-s), s)
    return dict(a=a, q=q, M=M, H=H, A=A, B=B, C=C, s=s, idx=idx, E=E, cert=certv)


if __name__ == '__main__':
    c = ROOT
    e = envelope(c)
    print('left end a = %.6f, mu = %.6f, CERT (float) = %.3e' % (e['a'], c['mu'], e['cert']))
    q, M, H, s, idx = e['q'], e['M'], e['H'], e['s'], e['idx']
    i1 = np.argmax(H)
    print('argmax H at q = %.6f, H = %.6f, M = %.6f' % (q[i1], H[i1], M[i1]))
    for t in [1, 0.9, 0.7, 0.5, 0.3, 0.2, 0.1, 0.05, 0.01, 1e-3, 1e-4, 1e-6, 1e-10, 1e-20]:
        k = np.argmin(abs(s + np.log(t)))
        j = idx[k]
        print('t=%-8g Q=%.6f  zeta=M(Q)=%+.5f  phi=%+.5f  A=%.4f B=%.4f C=%.4f  E=%+.5f' % (
            t, q[j], M[j], -c['w'] * (1 + np.log(t)), e['A'][j], e['B'][j], e['C'][j], e['E'][k]))
