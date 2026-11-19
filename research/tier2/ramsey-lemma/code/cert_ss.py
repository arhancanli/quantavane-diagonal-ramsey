"""Exploration (float, proves nothing): the self-similar envelope CERT_SS in drift-rank coordinates.

Rows are ranked by drift phi (u = rank, phi nonincreasing).  For an admissible pair (phi, eta):
  phi(1) >= -w,  int_0^1 phi = 0,  Phi(v) = int_0^v phi <= -w v log v - v eta(v)   (eta(v) >= 0 = potential gap of T_v)
the self-similar per-row bound (sub-pair tests inside the top-v drift sets T_v, NOTES.md Idea 4) is
  q zeta >= q phi(1) + c(u),   c(u) = int_u^1 a(eta(v)) v |dphi(v)|,
and ZBS's per-row bound zeta <= M(q).  The adversary survives only if
  V(phi, eta) = int_0^1 sup{ q (M(q) - phi(u)) : q in F, q M(q) >= q phi(1) + c(u) } du  >= 0.
With a == 0 (no self-similarity) and phi saturated (eta = 0) this is exactly ZBS's CERT.
"""
import numpy as np
from extremal import ROOT, parts, left_end, G0


class Ctl:
    def __init__(self, c, nq=6001):
        self.c = c
        p, mu, w, beta, x = c['p'], c['mu'], c['w'], c['beta'], c['x']
        a0 = left_end(p, mu, w, beta, x)
        q = a0 + (mu - a0) * np.linspace(0, 1, nq)[1:]
        A, B, M, C, feas = parts(q, p, mu, w, beta, x)
        self.q, self.M = q[feas], M[feas]
        self.qM = self.q * self.M
        # a(eta) table: root of G0(q) = beta eta on the left branch
        self.etas = np.concatenate([[0], np.geomspace(1e-5, 3, 400)])
        self.aeta = np.array([self._a(e) for e in self.etas])

    def _a(self, eta):
        p, mu, w, beta, x = (self.c[k] for k in ('p', 'mu', 'w', 'beta', 'x'))
        if G0(mu, p, mu, w, beta, x) >= beta * eta: return mu
        lo, hi = 1e-12, mu
        for _ in range(100):
            m = 0.5 * (lo + hi)
            if G0(m, p, mu, w, beta, x) < beta * eta: hi = m
            else: lo = m
        return hi

    def a_of(self, eta):
        return np.interp(eta, self.etas, self.aeta)

    def V(self, u, phi, eta, selfsim=True, return_parts=False):
        """u: increasing grid in (0,1] with u[-1] = 1 (cell midpoints rule below); phi, eta on u.
        Integral by the rule: values at u_i weighted by cell widths du_i = u_i - u_{i-1} (u_{-1} = 0)."""
        du = np.diff(np.concatenate([[0], u]))
        if selfsim:
            dphi = np.maximum(-np.diff(phi), 0)                  # |dphi| on [u_i, u_{i+1}]
            av = self.a_of(eta) * u                                # a(eta(v)) v at grid points
            contrib = av[:-1] * dphi                               # left value (F(v) >= a v at v = u_i)
            c = np.concatenate([np.cumsum(contrib[::-1])[::-1], [0]])
        else:
            c = np.zeros_like(u)
        phi1 = phi[-1]
        # sup over q for each u
        obj = self.qM[None, :] - self.q[None, :] * phi[:, None]
        ok = self.qM[None, :] >= self.q[None, :] * phi1 + c[:, None]
        obj = np.where(ok, obj, -np.inf)
        best = obj.max(axis=1)
        if np.any(~np.isfinite(best)):
            return -np.inf if not return_parts else (-np.inf, best, c)
        val = np.sum(best * du)
        return val if not return_parts else (val, best, c)


def grid(n_log=300, n_lin=500, umin=1e-30):
    return np.unique(np.concatenate([np.geomspace(umin, 0.02, n_log), np.linspace(0.02, 1, n_lin)]))


def saturated(u, w, eta=None):
    """phi = derivative of G(v) = -w v log v - v eta(v) on the grid (cell averages); eta on grid (eta(1) = 0)."""
    uu = np.concatenate([[0], u])
    G = np.where(uu > 0, -w * uu * np.log(np.where(uu > 0, uu, 1)), 0)
    if eta is not None: G = G - uu * np.concatenate([[eta[0]], eta])
    return np.diff(G) / np.diff(uu)


if __name__ == '__main__':
    import sys
    c = dict(ROOT)
    for da in [0.0, -1e-3, -2e-3, -4e-3]:
        cc = dict(c); cc['x'] = c['x'] * np.exp(-da)
        k = Ctl(cc); u = grid(); w = cc['w']
        phi = saturated(u, w)
        v0 = k.V(u, phi, 0 * u, selfsim=False)
        v1 = k.V(u, phi, 0 * u, selfsim=True)
        print('a-a_root %+.4f: ZBS CERT (this grid) %+.4e   self-sim V(saturated, eta=0) %+.4e' % (da, v0, v1), flush=True)
