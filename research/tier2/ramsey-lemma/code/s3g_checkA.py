"""S3G/S6 check A (exact rationals, Fractions; loops). Written 18 Nov 2026 by the S3/flatness helper.

PROOF.md S3G statements checked exactly on finite configurations:
  generic pairs (any X, Y with all u_y > 0; S3.1 and S3.5 need nothing else):
    S2 (E_nu e_i = V_i - 1), E_nu psi_T = avg_T phi, S3.1(a) identity, S3.1(b) <=> (exact equivalence),
    S3.1(c) identity of its proof and the implication, S3.1(d) both Jensen steps, S3.1(e), S3.5 identity;
  maximal pairs (brute-force global maximiser of Phi_c, hence maximal in ZBS's one-sided sense):
    ZBS Lemma 3.1 (a^s >= 1 - beta), Lemma 3.2 (phi >= -w), support bound, S3.4(i)-(iv) (all subsets S, A).
Every power is rational: r/s = 1/beta integer, w beta integer, w/r and 1 - beta in {1/3, 1/2}.
Tampers (each must be REFUSED) at the end, then mpmath (60 digits) checks of S3.2 at the root control.
Run:  <python with mpmath> -I s3g_checkA.py [n_generic] [n_maximal]
"""
import sys, random, itertools
from fractions import Fraction as Fr

PARAMS = [dict(beta=Fr(1, 2), s=3, r=6, w=2), dict(beta=Fr(1, 2), s=4, r=8, w=4), dict(beta=Fr(1, 3), s=3, r=9, w=3)]
LOG_UP = {Fr(1, 2): Fr(6932, 10000), Fr(2, 3): Fr(4055, 10000)}   # upper bounds for -log(1-beta)


def powr(x, e):
    """x^e for rational e = a/b > 0 is not rational in general; callers only use integer e."""
    assert Fr(e).denominator == 1
    return x ** int(e)


def subsets(xs):
    for k in range(1, len(xs) + 1):
        yield from itertools.combinations(xs, k)


class Host:
    def __init__(self, rng, N0, M0, pr):
        self.N0, self.M0 = N0, M0
        self.H = [[1 if rng.random() < pr else 0 for _ in range(M0)] for _ in range(N0)]      # X0 x Y0 red
        self.Bl = [[False] * N0 for _ in range(N0)]                                            # blue inside X0
        for i in range(N0):
            for j in range(i + 1, N0):
                self.Bl[i][j] = self.Bl[j][i] = rng.random() < 0.5


def Phi(host, Xs, Ys, c, P):
    k = int(1 / P['beta'])
    tot = Fr(0)
    for y in Ys:
        g = Fr(sum(host.H[i][y] for i in Xs), len(Xs))
        if g > c: tot += (g - c) ** P['s']
    return Fr(len(Xs)) ** P['w'] * Fr(len(Ys)) ** (1 - k) * tot ** k


def maximal_pair(host, c, P):
    """global maximiser (float search over X and top-m column sets), then EXACT verification of one-sided maximality."""
    k = P['r'] / P['s']; best, arg = -1.0, None
    for Xs in subsets(range(host.N0)):
        g = [sum(host.H[i][y] for i in Xs) / len(Xs) for y in range(host.M0)]
        cols = sorted(range(host.M0), key=lambda y: -g[y]); tot = 0.0
        for m in range(1, host.M0 + 1):
            tot += max(g[cols[m - 1]] - float(c), 0) ** P['s']
            f = len(Xs) ** P['w'] * m ** (1 - k) * tot ** k
            if f > best: best, arg = f, (Xs, tuple(sorted(cols[:m])))
    X, Y = arg
    PXY = Phi(host, X, Y, c, P)
    for Xp in subsets(X):
        if Phi(host, Xp, Y, c, P) > PXY: return None
    for Yp in subsets(Y):
        if Phi(host, X, Yp, c, P) > PXY: return None
    return X, Y, PXY


class Conf:
    def __init__(self, host, X, Y, c, P):
        self.host, self.X, self.Y, self.c, self.P = host, list(X), list(Y), c, P
        s, r = P['s'], P['r']
        self.N, self.M = len(X), len(Y)
        self.g = {y: Fr(sum(host.H[i][y] for i in X), self.N) for y in Y}
        self.u = {y: self.g[y] - c for y in Y}
        assert all(self.u[y] > 0 for y in Y)
        self.Hs = sum(self.u[y] ** s for y in Y) / self.M
        self.nu = {y: self.u[y] ** s / (self.M * self.Hs) for y in Y}
        self.V = {i: sum(self.u[y] ** (s - 1) * (host.H[i][y] - c) for y in Y) / self.M / self.Hs for i in X}
        self.phi = {i: r * (self.V[i] - 1) for i in X}

    def E(self, f):
        return sum(self.nu[y] * f(y) for y in self.Y)

    def e(self, i, y):
        return (self.host.H[i][y] - self.g[y]) / self.u[y]

    def psi(self, S):
        return {y: self.P['r'] * sum(self.e(i, y) for i in S) / len(S) for y in self.Y}

    def gS(self, S, y):
        return Fr(sum(self.host.H[i][y] for i in S), len(S))


def new_stats():
    st = dict.fromkeys(['generic', 'maximal', 'fail_S2', 'a', 'fail_a', 'b', 'blue_fail_inst', 'fail_b', 'c_id',
                        'fail_c_id', 'red_fail_inst', 'fail_c', 'd', 'fail_d1', 'fail_d2', 'e', 'fail_e', 'nonflat',
                        'S35', 'fail_S35', 'S34_sets'], 0)
    st['L2_ratio_max'] = 0.0
    return st


def check_generic(C, rng, st, tamper=None):
    host, X, Y, c, P = C.host, C.X, C.Y, C.c, C.P
    s, r, w, beta = P['s'], P['r'], P['w'], P['beta']
    k = int(1 / beta); kb = int(w * beta)
    mu = Fr(rng.randint(25, 60), 100); x = Fr(rng.randint(10, 45), 100)
    PXY = Phi(host, X, Y, c, P)
    assert sum(C.V.values()) == C.N
    for i in X:
        lhs = C.E(lambda y: C.e(i, y))
        if tamper == 'uniform_nu': lhs = sum(C.e(i, y) for y in Y) / C.M
        if lhs != C.V[i] - 1: st['fail_S2'] += 1
    Ts = list(subsets(X)) if C.N <= 7 else [tuple(rng.sample(X, rng.randint(1, C.N))) for _ in range(60)]
    for T in Ts:
        T = list(T); nT = len(T); v = Fr(nT, C.N)
        psiT = C.psi(T); avgTphi = sum(C.phi[i] for i in T) / nT
        assert C.E(lambda y: psiT[y]) == avgTphi
        for j in X:
            BT = [i for i in T if i != j and host.Bl[i][j]]
            RT = [i for i in T if i != j and not host.Bl[i][j]]
            q = Fr(len(BT), nT); sig = Fr(len(RT), nT)
            assert sig == (1 - q - Fr(1, nT) if j in T else 1 - q)
            Yj = [y for y in Y if host.H[j][y]]
            m = sum(C.nu[y] for y in Yj); pi = Fr(len(Yj), C.M)
            Z = {y: (Fr(sum(host.H[i][y] for i in BT), len(BT)) - C.g[y]) / C.u[y] if BT else Fr(0) for y in Y}
            if BT:
                lhs = r * C.E(lambda y: Z[y]); rhs = sum(C.phi[i] for i in BT) / len(BT)
                if tamper == 'perturb_phi': rhs += Fr(1, 10 ** 6)
                st['a'] += 1
                if lhs != rhs: st['fail_a'] += 1
                fails_blue = Phi(host, BT, Y, c, P) < mu ** w * PXY
                ineq = C.E(lambda y: max(1 + Z[y], 0) ** s) < (mu / (q * v)) ** kb
                st['b'] += 1; st['blue_fail_inst'] += fails_blue
                if fails_blue != ineq: st['fail_b'] += 1
            if not RT or not Yj: continue
            for Delta in ([(1 - c) / (nT * sig), 1 - c] if j in T else [Fr(1, 7), 1 - c]):
                cp = c - Delta
                Ej = sig * Delta - ((1 - c) / nT if j in T else 0)
                assert Ej >= 0
                for y in Yj:
                    rho = Fr(sum(host.H[i][y] for i in RT), len(RT))
                    W = (1 - q) + psiT[y] / r - q * Z[y]
                    if tamper == 'drop_psi': W = (1 - q) - q * Z[y]
                    if sig * (rho - cp) != C.u[y] * W + Ej: st['fail_c_id'] += 1
                st['c_id'] += 1
                fails_red = Phi(host, RT, Yj, cp, P) < x * PXY
                EhW = C.E(lambda y: host.H[j][y] * max((1 - q) + psiT[y] / r - q * Z[y], 0) ** s)
                bound_k = (1 - q) ** (r - w) * x * v ** (-w) * pi ** (k - 1)      # (c) raised to 1/beta = k
                if fails_red:
                    st['red_fail_inst'] += 1
                    if not EhW ** k < bound_k: st['fail_c'] += 1
                if 0 < m < 1:
                    Psi = sum(C.nu[y] * psiT[y] for y in Yj) / m
                    zin = sum(C.nu[y] * Z[y] for y in Yj) / m
                    zout = sum(C.nu[y] * Z[y] for y in Y if y not in Yj) / (1 - m)
                    st['d'] += 1
                    if m * max((1 - q) + Psi / r - q * zin, 0) ** s > EhW: st['fail_d1'] += 1
                    if BT and m * max(1 + zin, 0) ** s + (1 - m) * max(1 + zout, 0) ** s > C.E(lambda y: max(1 + Z[y], 0) ** s):
                        st['fail_d2'] += 1
                    if not BT and fails_red:
                        st['e'] += 1
                        if not (m * max(1 + Psi / r, 0) ** s) ** k < x * v ** (-w) * pi ** (k - 1): st['fail_e'] += 1
                    if Psi != avgTphi: st['nonflat'] += 1
    for _ in range(12):
        T = rng.sample(X, rng.randint(1, C.N)); Cc = rng.sample(X, rng.randint(1, C.N))
        d0 = Fr(rng.randint(0, 100), 100)
        psiT, psiC = C.psi(T), C.psi(Cc); EpsiT = C.E(lambda y: psiT[y])
        lhs = sum(C.E(lambda y: psiT[y] * host.H[j][y]) - C.E(lambda y: host.H[j][y]) * EpsiT for j in Cc) / len(Cc)
        rhs = C.E(lambda y: (psiT[y] - EpsiT) * (C.g[y] - d0))
        if tamper != 'drop_psiC': rhs += C.E(lambda y: (psiT[y] - EpsiT) * C.u[y] * psiC[y]) / r
        st['S35'] += 1
        if lhs != rhs: st['fail_S35'] += 1


def check_maximal(C, st):
    X, Y, c, P = C.X, C.Y, C.c, C.P
    s, r, w, beta = P['s'], P['r'], P['w'], P['beta']
    kb = int(w * beta); wr = Fr(w, r)
    for y in Y:
        assert C.u[y] > 0 and C.u[y] ** s >= (1 - beta) * C.Hs, 'ZBS Lemma 3.1'
    for i in X:
        assert C.phi[i] >= -w, 'ZBS Lemma 3.2'
    for S in subsets(X):
        S = list(S); sig = Fr(len(S), C.N); psiS = C.psi(S)
        HSs = sum(max(C.gS(S, y) - c, 0) ** s for y in Y) / C.M
        lhs = C.E(lambda y: max(1 + psiS[y] / r, 0) ** s)
        assert lhs == HSs / C.Hs, 'S3.4(i) identity'
        assert lhs <= sig ** (-kb), 'S3.4(i) bound'
        sv = sig * sum(C.V[i] for i in S) / len(S)                 # support bound sv <= sig^{1 - w/r}
        b = wr.denominator; a = wr.numerator
        assert sv <= 0 or sv ** b <= sig ** (b - a), 'support bound'
        st['S34_sets'] += 1
        if sig == 1: continue
        comp = [i for i in X if i not in S]; psiC = C.psi(comp)
        assert all(psiC[y] == -sig * psiS[y] / (1 - sig) for y in Y), 'S3.4(ii) complement'
        for t in [Fr(1, 4), Fr(1, 2), Fr(1), Fr(2), Fr(5)]:
            up = sum(C.nu[y] for y in Y if psiS[y] >= t); lo = sum(C.nu[y] for y in Y if psiS[y] <= -t)
            assert up <= sig ** (-kb) * (1 + t / r) ** (-s), 'S3.4(i) tail'
            assert lo <= (1 - sig) ** (-kb) * (1 + sig * t / ((1 - sig) * r)) ** (-s), 'S3.4(ii) tail'
        K2 = sig ** (-kb) + (1 - sig) ** (2 - kb) * sig ** (-2)
        bound = K2 * 2 * r ** 2 / ((s - 1) * (s - 2))
        E2 = C.E(lambda y: psiS[y] ** 2)
        assert E2 <= bound, 'S3.4(iii)'
        st['L2_ratio_max'] = max(st['L2_ratio_max'], float(E2 / bound))
    for A in subsets(Y):
        nA = sum(C.nu[y] for y in A); pA = Fr(len(A), C.M)
        e = 1 - beta                                                   # nu(A) <= pA^e, e = a/b -> nu^b <= pA^a
        assert nA ** e.denominator <= pA ** e.numerator, 'S3.4(iv) nu(A)'
    rho = (1 - beta) * r; assert rho.denominator == 1 and rho > 2
    for t in [Fr(1, 10), Fr(1, 2), Fr(1)]:
        tail = sum(C.nu[y] for y in Y if C.u[y] ** s >= (1 + t) ** s * C.Hs)
        assert tail <= (1 + t) ** (-int(rho)), 'S3.4(iv) tail'
    lo, hi = Fr(0), Fr(1)
    for _ in range(80):
        mid = (lo + hi) / 2
        if mid ** s <= C.Hs: lo = mid
        else: hi = mid
    Kb = LOG_UP[1 - beta] / beta
    bound = Fr(2) / ((rho - 1) * (rho - 2)) + Kb ** 2 / r ** 2
    for Hb in (lo, hi):
        assert C.E(lambda y: (C.u[y] / Hb - 1) ** 2) <= bound, 'S3.4(iv) E(a-1)^2'


def concavity_checks(seed=7):
    import mpmath as mp
    mp.mp.dps = 60
    rng = random.Random(seed)
    p, mu, w, beta, x = (mp.mpf('0.499999'), mp.mpf(80725349867) / 200000000000, mp.mpf(120299011257) / 250000000000,
                         1 - mp.mpf('1e-7'), mp.mpf(8107422360171) / 25000000000000)
    d = p
    def a_fn(q, v): return (1 - q) * (mp.log(d * v ** w / x) + w * mp.log(1 - q))
    def G(q, Psi, v): return q * mp.log(d) + beta * (a_fn(q, v) + Psi) - (beta * w * q * mp.log(mu / (q * v)) if q > 0 else 0)
    def H(q, Psi, v):
        if G(q, Psi, v) > 0: return -mp.inf
        if q == 0: return mp.mpf(0)
        A = (a_fn(q, v) + Psi) / q; B = w * mp.log(mu / (q * v))
        if A <= B: return q * B
        z = mp.exp(beta * B) - d * mp.exp(beta * A)
        return -mp.inf if z <= 0 else q * (d * A + (1 - d) / beta * mp.log(z / (1 - d)))
    bad_H = bad_G = n = 0
    for v in [mp.mpf('0.02'), mp.mpf('0.1'), mp.mpf('0.3'), mp.mpf('0.7'), mp.mpf(1)]:
        P0 = -w * mp.log(v)
        for _ in range(400):
            pts = []
            while len(pts) < 2:
                q = mp.mpf(rng.choice([rng.uniform(0.0005, 0.42), rng.uniform(0.2, 0.42)])); Psi = P0 + mp.mpf(rng.uniform(-1.5, 0.6))
                if G(q, Psi, v) <= 0: pts.append((q, Psi))
            (q1, P1), (q2, P2) = pts
            lam = mp.mpf(rng.uniform(0.05, 0.95)); qm, Pm = lam * q1 + (1 - lam) * q2, lam * P1 + (1 - lam) * P2
            n += 1
            if G(qm, Pm, v) > lam * G(q1, P1, v) + (1 - lam) * G(q2, P2, v) + mp.mpf('1e-50'): bad_G += 1
            if H(qm, Pm, v) < lam * H(q1, P1, v) + (1 - lam) * H(q2, P2, v) - mp.mpf('1e-50'): bad_H += 1
    worst = mp.mpf(0)
    for _ in range(300):
        v = mp.mpf(rng.uniform(0.01, 1)); eta = mp.mpf(rng.uniform(0, 0.4)); q = mp.mpf(rng.uniform(0.2, 0.42))
        Psi = -w * mp.log(v) - eta
        if G(q, Psi, v) >= 0: continue
        x2, mu2 = x * mp.exp(eta), mu * mp.exp(eta / w)
        A2 = (1 - q) / q * mp.log(d * (1 - q) ** w / x2); B2 = w * mp.log(mu2 / q)
        M2 = B2 if A2 <= B2 else d * A2 + (1 - d) / beta * mp.log((mp.exp(beta * B2) - d * mp.exp(beta * A2)) / (1 - d))
        worst = max(worst, abs(H(q, Psi, v) / q - (M2 - w * mp.log(v) - eta)))
    return n, bad_G, bad_H, mp.nstr(worst, 5), worst < mp.mpf('1e-40')


def generic_conf(rng, P, N0=7, M0=7):
    host = Host(rng, N0, M0, 0.5)
    X, Y = list(range(N0)), list(range(M0))
    g = [Fr(sum(host.H[i][y] for i in X), N0) for y in Y]
    if min(g) == 0: return None
    c = min(g) / 2
    return Conf(host, X, Y, c, P)


def run(n_gen, n_max, P, st, rng, tamper=None):
    while st['generic'] < n_gen:
        C = generic_conf(rng, P)
        if C is None: continue
        check_generic(C, rng, st, tamper); st['generic'] += 1
    tries = 0
    while st['maximal'] < n_max and tries < 50 * max(n_max, 1):
        tries += 1
        host = Host(rng, 9, 7, 0.8); c = Fr(rng.randint(20, 40), 100)
        mp_ = maximal_pair(host, c, P)
        if mp_ is None: continue
        X, Y, _ = mp_
        if len(set(tuple(host.H[i][y] for y in Y) for i in X)) < 3: continue     # skip degenerate pairs
        C = Conf(host, X, Y, c, P)
        check_maximal(C, st); check_generic(C, rng, st, tamper); st['maximal'] += 1


def main():
    n_gen = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    n_max = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    ok = True
    for P in PARAMS:
        st = new_stats(); rng = random.Random(20261118 + 10 * P['r'] + P['w'])
        run(n_gen, n_max, P, st, rng)
        fails = {k: v for k, v in st.items() if k.startswith('fail') and v}
        print('beta=%s s=%d r=%d w=%d:' % (P['beta'], P['s'], P['r'], P['w']), st, flush=True)
        need = ['a', 'b', 'blue_fail_inst', 'c_id', 'red_fail_inst', 'd', 'e', 'nonflat', 'S35', 'S34_sets']
        empty = [k for k in need if st[k] == 0]
        if fails or empty or st['maximal'] < n_max:
            ok = False; print('  FAILURES', fails, 'EMPTY', empty, 'maximal', st['maximal'])
    for tname, key in {'uniform_nu': 'fail_S2', 'perturb_phi': 'fail_a', 'drop_psi': 'fail_c_id', 'drop_psiC': 'fail_S35'}.items():
        st = new_stats(); run(2, 0, PARAMS[0], st, random.Random(99), tamper=tname)
        refused = st[key] > 0
        print('tamper %-12s -> %s (%s = %d)' % (tname, 'REFUSED' if refused else 'NOT REFUSED', key, st[key]))
        ok = ok and refused
    n, bG, bH, ws, wok = concavity_checks()
    print('S3.2 at the root control (mpmath 60 digits): %d chords; G convexity violations %d; H concavity violations %d; '
          'flat-model relation max error %s' % (n, bG, bH, ws))
    ok = ok and bG == 0 and bH == 0 and wok
    print('CHECK A:', 'OK' if ok else 'FAILED')


if __name__ == '__main__':
    main()
