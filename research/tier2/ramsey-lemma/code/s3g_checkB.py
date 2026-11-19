"""S3G/S6 check B (sympy exact rationals; matrix/count formulas). Written separately from check A, 18 Nov 2026.

Differences from A: hosts from bit masks; nu, V by matrix products; psi_S from column COUNTS (not from e_i); tests in
the 'raised to beta' form Phi^beta = |S|^{w beta} M^beta E_Y(.)_+^s (A compares Phi itself); maximal pairs by an
alternating exact local search (one-sided maximal, A uses the global maximiser); H^T by direct numerical optimisation
of the convex program (*) (A uses the closed form), compared with the closed form of PROOF.md; and the limit
r S(m, U, L) -> M^T of Proposition S3.3 at growing r.  Run: <python with sympy, mpmath> -I s3g_checkB.py [n] [seed]
"""
import sys, random, itertools
import sympy as sp

R = sp.Rational


def tb(e):
    """sympy relational -> 0/1"""
    return int(bool(e))
PARAMS = [(R(1, 2), 3, 2), (R(1, 2), 4, 4), (R(1, 3), 3, 3)]      # (beta, s, w); r = s/beta


def nonempty_subsets(idx):
    for m in range(1, 1 << len(idx)):
        yield [idx[b] for b in range(len(idx)) if m >> b & 1]


class Instance:
    def __init__(self, red, blue, X, Y, c, beta, s, w):
        self.red, self.blue, self.X, self.Y = red, blue, list(X), list(Y)
        self.c, self.beta, self.s, self.w = c, beta, s, w
        self.r = s / beta
        self.Hm = sp.Matrix([[red[i][y] for y in self.Y] for i in self.X])          # N x M 0/1
        self.N, self.M = self.Hm.shape
        ones = sp.ones(1, self.N)
        self.gv = (ones * self.Hm) / self.N                                       # 1 x M
        self.uv = self.gv - c * sp.ones(1, self.M)
        self.Hs = sum(t ** s for t in self.uv) / self.M
        self.nu = sp.Matrix([[t ** s / (self.M * self.Hs) for t in self.uv]])
        wv = sp.Matrix([t ** (s - 1) for t in self.uv])                           # M x 1
        self.Vv = (self.Hm - c * sp.ones(self.N, self.M)) * wv / (self.M * self.Hs)   # N x 1
        self.phiv = self.r * (self.Vv - sp.ones(self.N, 1))

    def col_counts(self, rows):          # rows are positions 0..N-1
        return [sum(self.Hm[i, k] for i in rows) for k in range(self.M)]

    def psi(self, rows):
        cnt = self.col_counts(rows)
        return [self.r * (R(cnt[k], len(rows)) - self.gv[k]) / self.uv[k] for k in range(self.M)]

    def Enu(self, vals):
        return sum(self.nu[k] * vals[k] for k in range(self.M))

    def phi_beta(self, rows, cols, shift):
        """Phi_shift(rows, cols)^beta times M^{-beta}... we return |rows|^{w beta} |cols|^{beta-1} sum_{cols}(.)_+^s
        divided by nothing; comparisons use the same normalisation on both sides."""
        tot = 0
        for k in cols:
            gk = R(sum(self.Hm[i, k] for i in rows), len(rows))
            if gk > shift: tot += (gk - shift) ** self.s
        return len(rows), len(cols), tot


def phi_full(inst, rows, cols, shift):
    """Phi = |rows|^w |cols|^{1 - 1/beta} (sum)^{1/beta} (1/beta integer)."""
    n, mcols, tot = inst.phi_beta(rows, cols, shift)
    k = int(1 / inst.beta)
    return R(n) ** inst.w * R(mcols) ** (1 - k) * tot ** k


def make_host(rng, N0, M0, pr):
    bits = [rng.getrandbits(M0) for _ in range(N0)]
    red = [[(bits[i] >> y & 1) if pr == 0.5 else int(rng.random() < pr) for y in range(M0)] for i in range(N0)]
    blue = [[False] * N0 for _ in range(N0)]
    for i in range(N0):
        for j in range(i + 1, N0):
            blue[i][j] = blue[j][i] = bool(rng.getrandbits(1))
    return red, blue


def local_max_pair(red, N0, M0, c, beta, s, w):
    """alternating exact restriction until one-sided maximal; returns (X, Y) or None."""
    X, Y = list(range(N0)), list(range(M0))
    k = int(1 / beta)
    def Phi(Xs, Ys):
        tot = 0
        for y in Ys:
            g = R(sum(red[i][y] for i in Xs), len(Xs))
            if g > c: tot += (g - c) ** s
        return R(len(Xs)) ** w * R(len(Ys)) ** (1 - k) * tot ** k
    for _ in range(20):
        cur = Phi(X, Y)
        bestX = max(nonempty_subsets(X), key=lambda Xs: Phi(Xs, Y))
        if Phi(bestX, Y) > cur: X = bestX; continue
        bestY = max(nonempty_subsets(Y), key=lambda Ys: Phi(X, Ys))
        if Phi(X, bestY) > cur: Y = bestY; continue
        return (X, Y) if cur > 0 else None
    return None


def checks_identities(inst, rng, st, tamper=None):
    N, M, r, s, w, beta, c = inst.N, inst.M, inst.r, inst.s, inst.w, inst.beta, inst.c
    kb = int(w * beta); k = int(1 / beta)
    mu = R(rng.randint(25, 60), 100); x = R(rng.randint(10, 45), 100)
    allrows = list(range(N)); allcols = list(range(M))
    PXY = phi_full(inst, allrows, allcols, c)
    # S2 row by row: E_nu[(h_i - g)/u] = V_i - 1
    for i in allrows:
        val = inst.Enu([(inst.Hm[i, kk] - inst.gv[kk]) / inst.uv[kk] for kk in allcols])
        if tamper == 'S2_uniform': val = sum((inst.Hm[i, kk] - inst.gv[kk]) / inst.uv[kk] for kk in allcols) / M
        st['S2'] += 1; st['fail_S2'] += tb((val != inst.Vv[i] - 1))
    sets = list(nonempty_subsets(allrows)) if N <= 7 else [sorted(rng.sample(allrows, rng.randint(1, N))) for _ in range(50)]
    for T in sets:
        nT = len(T); v = R(nT, N); psiT = inst.psi(T)
        avgphi = sum(inst.phiv[i] for i in T) / nT
        st['ET'] += 1; st['fail_ET'] += tb((inst.Enu(psiT) != avgphi))
        for j in allrows:
            BT = [i for i in T if i != j and inst.blue[inst.X[i]][inst.X[j]]]
            RT = [i for i in T if i != j and not inst.blue[inst.X[i]][inst.X[j]]]
            q = R(len(BT), nT); sig = R(len(RT), nT)
            Yj = [kk for kk in allcols if inst.Hm[j, kk] == 1]
            m = sum(inst.nu[kk] for kk in Yj); pi = R(len(Yj), M)
            if BT:
                cb = inst.col_counts(BT)
                bT = [R(cb[kk], len(BT)) for kk in allcols]
                Z = [(bT[kk] - inst.gv[kk]) / inst.uv[kk] for kk in allcols]
            else:
                bT = None; Z = [0] * M
            if BT:
                lhs = r * inst.Enu(Z); rhs = sum(inst.phiv[i] for i in BT) / len(BT)
                if tamper == 'phi_shift': rhs = rhs + R(1, 1000)
                st['a'] += 1; st['fail_a'] += tb((lhs != rhs))
                # blue failure in 'raised to beta' form: (|B|/N)^{w beta} E_Y(b - c)_+^s < mu^{w beta} H^s
                EYb = sum(max(bT[kk] - c, 0) ** s for kk in allcols) / M
                fails = bool((q * v) ** kb * EYb < mu ** kb * inst.Hs)
                ineq = bool(inst.Enu([max(1 + Z[kk], 0) ** s for kk in allcols]) < (mu / (q * v)) ** kb)
                st['b'] += 1; st['fail_b'] += int(fails != ineq); st['b_fail_inst'] += int(fails)
            if not RT or not Yj or not (0 < m < 1): continue
            Delta = (1 - c) / (nT * sig) if j in T else R(1, 3)
            cprime = c - Delta
            cr = inst.col_counts(RT)
            for kk in Yj:
                rho = R(cr[kk], len(RT))
                gT = R(inst.col_counts(T)[kk], nT)
                # identity from the proof of S3.1(c): sigma'(rho - c') = (gT - c) - q (bT - c) + E_j
                Ej = sig * Delta - ((1 - c) / nT if j in T else 0)
                rhs = (gT - c) - q * ((bT[kk] if BT else 0) - c) + Ej
                if tamper == 'sign_shift': rhs = (gT - c) - q * ((bT[kk] if BT else 0) - c) - Ej - R(1, 97)
                st['c_id'] += 1; st['fail_c_id'] += tb((sig * (rho - cprime) != rhs))
                # and (gT - c) - q(bT - c) = u W  with W = (1-q) + psi_T/r - q Z
                W = (1 - q) + psiT[kk] / r - q * Z[kk]
                st['c_id2'] += 1; st['fail_c_id2'] += tb(((gT - c) - q * ((bT[kk] if BT else 0) - c) != inst.uv[kk] * W))
            fails_red = bool(phi_full(inst, RT, Yj, cprime) < x * PXY)
            EhW = inst.Enu([inst.Hm[j, kk] * max((1 - q) + psiT[kk] / r - q * Z[kk], 0) ** s for kk in allcols])
            if fails_red:
                st['c_inst'] += 1
                st['fail_c'] += 1 - tb((EhW ** k < (1 - q) ** (r - w) * x * v ** (-w) * pi ** (k - 1)))
            Psi = sum(inst.nu[kk] * psiT[kk] for kk in Yj) / m
            zin = sum(inst.nu[kk] * Z[kk] for kk in Yj) / m
            zout = sum(inst.nu[kk] * Z[kk] for kk in allcols if kk not in Yj) / (1 - m)
            st['d'] += 1
            st['fail_d1'] += tb((m * max((1 - q) + Psi / r - q * zin, 0) ** s > EhW))
            if BT:
                st['fail_d2'] += tb((m * max(1 + zin, 0) ** s + (1 - m) * max(1 + zout, 0) ** s)
                                  > inst.Enu([max(1 + Z[kk], 0) ** s for kk in allcols]))
            if not BT and fails_red:
                st['e'] += 1
                st['fail_e'] += 1 - tb(((m * max(1 + Psi / r, 0) ** s) ** k < x * v ** (-w) * pi ** (k - 1)))
    # S3.5 identity, both sides from matrices
    for _ in range(10):
        T = sorted(rng.sample(allrows, rng.randint(1, N))); C = sorted(rng.sample(allrows, rng.randint(1, N)))
        d0 = R(rng.randint(0, 50), 50)
        psiT = inst.psi(T); EpsiT = inst.Enu(psiT); D = [p - EpsiT for p in psiT]
        lhs = sum(inst.Enu([psiT[kk] * inst.Hm[j, kk] for kk in allcols]) - EpsiT * inst.Enu([inst.Hm[j, kk] for kk in allcols])
                  for j in C) / len(C)
        psiC = inst.psi(C)
        rhs = inst.Enu([D[kk] * (inst.gv[kk] - d0) for kk in allcols])
        if tamper != 'S35_drop':
            rhs += inst.Enu([D[kk] * inst.uv[kk] * psiC[kk] for kk in allcols]) / r
        st['S35'] += 1; st['fail_S35'] += tb((lhs != rhs))


def checks_maximal(inst, st):
    N, M, r, s, w, beta, c = inst.N, inst.M, inst.r, inst.s, inst.w, inst.beta, inst.c
    kb = int(w * beta)
    allrows, allcols = list(range(N)), list(range(M))
    for kk in allcols:
        st['fail_L31'] += 1 - tb((inst.uv[kk] > 0 and inst.uv[kk] ** s >= (1 - beta) * inst.Hs))
    for i in allrows:
        st['fail_L32'] += 1 - tb((inst.phiv[i] >= -w))
    for S in nonempty_subsets(allrows):
        sg = R(len(S), N); psiS = inst.psi(S)
        cnt = inst.col_counts(S)
        HSs = sum(max(R(cnt[kk], len(S)) - c, 0) ** s for kk in allcols) / M
        mom = inst.Enu([max(1 + p / r, 0) ** s for p in psiS])
        st['S34'] += 1
        st['fail_S34i'] += tb((mom != HSs / inst.Hs) or not (mom * sg ** kb <= 1))
        if sg == 1: continue
        E2 = inst.Enu([p ** 2 for p in psiS])
        bound = (sg ** (-kb) + (1 - sg) ** (2 - kb) * sg ** (-2)) * 2 * r ** 2 / ((s - 1) * (s - 2))
        st['fail_S34iii'] += 1 - tb((E2 <= bound))
        for t in [R(1, 3), R(1), R(3)]:
            up = sum(inst.nu[kk] for kk in allcols if psiS[kk] >= t)
            lo = sum(inst.nu[kk] for kk in allcols if psiS[kk] <= -t)
            st['fail_S34tail'] += 1 - tb((up <= sg ** (-kb) * (1 + t / r) ** (-s)))
            st['fail_S34tail'] += 1 - tb((lo <= (1 - sg) ** (-kb) * (1 + sg * t / ((1 - sg) * r)) ** (-s)))
    e = 1 - beta
    for A in nonempty_subsets(allcols):
        nA = sum(inst.nu[kk] for kk in A)
        st['fail_S34iv'] += 1 - tb((nA ** e.q <= R(len(A), M) ** e.p))


def limit_checks():
    """S3.2: H^T by direct optimisation of (*) vs the closed form; concavity of the optimised values;
    S3.3: r S(m, U, L) -> M^T as r grows (ZBS two-cell formula with the Psi term)."""
    import mpmath as mp
    mp.mp.dps = 40
    d, mu, w, beta, x = (mp.mpf('0.499999'), mp.mpf(80725349867) / 200000000000, mp.mpf(120299011257) / 250000000000,
                         1 - mp.mpf('1e-7'), mp.mpf(8107422360171) / 25000000000000)
    def avd(q, v): return (1 - q) * (mp.log(d * v ** w / x) + w * mp.log(1 - q))
    def H_opt(q, Psi, v):
        """sup d z1 + (1-d) z2, z1 >= A, d e^{b z1} + (1-d) e^{b z2} <= e^{b B}; times q. Golden search on z1."""
        A = (avd(q, v) + Psi) / q; B = w * mp.log(mu / (q * v))
        zmax = B - mp.log(d) / beta                    # largest z1 with the constraint feasible
        if A >= zmax: return -mp.inf
        def f(z1):
            rest = mp.exp(beta * B) - d * mp.exp(beta * z1)
            return d * z1 + (1 - d) / beta * mp.log(rest / (1 - d))
        lo, hi = A, zmax - mp.mpf('1e-30')
        gr = (mp.sqrt(5) - 1) / 2
        a1, b1 = hi - gr * (hi - lo), lo + gr * (hi - lo)
        for _ in range(160):
            if f(a1) < f(b1): lo = a1
            else: hi = b1
            a1, b1 = hi - gr * (hi - lo), lo + gr * (hi - lo)
        return q * f((lo + hi) / 2)
    def H_closed(q, Psi, v):          # PROOF.md "Limit functions"
        A = (avd(q, v) + Psi) / q; B = w * mp.log(mu / (q * v))
        if A <= B: return q * B
        z = mp.exp(beta * B) - d * mp.exp(beta * A)
        return -mp.inf if z <= 0 else q * (d * A + (1 - d) / beta * mp.log(z / (1 - d)))
    rng = random.Random(5)
    worst = mp.mpf(0); pts = []
    for _ in range(150):
        v = mp.mpf(rng.choice([0.05, 0.2, 0.5, 1.0])); q = mp.mpf(rng.uniform(0.15, 0.42))
        Psi = -w * mp.log(v) + mp.mpf(rng.uniform(-1.0, 0.3))
        ho, hc = H_opt(q, Psi, v), H_closed(q, Psi, v)
        if ho == -mp.inf or hc == -mp.inf:
            if not (ho == -mp.inf and hc == -mp.inf): worst = mp.inf
            continue
        worst = max(worst, abs(ho - hc)); pts.append((v, q, Psi, ho))
    bad = 0; nch = 0
    for v0 in [mp.mpf('0.05'), mp.mpf('0.2'), mp.mpf('0.5'), mp.mpf(1)]:
        P = [(q, Psi, h) for (v, q, Psi, h) in pts if v == v0]
        pairs = list(itertools.combinations(P, 2)); rng.shuffle(pairs)
        for (q1, P1, h1), (q2, P2, h2) in pairs[:60]:
            hm = H_opt((q1 + q2) / 2, (P1 + P2) / 2, v0)
            nch += 1; bad += (hm < (h1 + h2) / 2 - mp.mpf('1e-25'))
    # S3.3 convergence: r * S_r -> M^T with q' r L = (1-q) r (1 - e^{l/r}) + Psi, U = (mu/(q v))^{w beta}, m = pi = d
    conv = []
    for (v, q, Psi) in [(mp.mpf('0.2'), mp.mpf('0.33'), -w * mp.log(mp.mpf('0.2')) - mp.mpf('0.02')),
                        (mp.mpf('0.5'), mp.mpf('0.38'), -w * mp.log(mp.mpf('0.5')) + mp.mpf('0.05')),
                        (mp.mpf(1), mp.mpf('0.35'), mp.mpf(0))]:
        target = H_closed(q, Psi, v) / q
        errs = []
        for r in [mp.mpf(10) ** 3, mp.mpf(10) ** 5, mp.mpf(10) ** 7]:
            s = beta * r; m = d; pi = d
            l = mp.log(x) - w * mp.log(v) - w * mp.log(1 - q) + ((1 - beta) * mp.log(pi) - mp.log(m)) / beta
            L = ((1 - q) * r * (1 - mp.exp(l / r)) + Psi) / (q * r)
            U = (mu / (q * v)) ** (w * beta); tU = U ** (1 / s)
            if L <= tU - 1: S = tU - 1
            else:
                Q = (U - m * (1 + L) ** s) / (1 - m); S = m * L + (1 - m) * (Q ** (1 / s) - 1)
            errs.append(abs(r * S - target))
        conv.append(errs)
    return worst, nch, bad, conv


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 4242
    rng = random.Random(seed)
    ok = True
    keys = ['S2', 'fail_S2', 'ET', 'fail_ET', 'a', 'fail_a', 'b', 'fail_b', 'b_fail_inst', 'c_id', 'fail_c_id', 'c_id2',
            'fail_c_id2', 'c_inst', 'fail_c', 'd', 'fail_d1', 'fail_d2', 'e', 'fail_e', 'S35', 'fail_S35', 'L31',
            'fail_L31', 'fail_L32', 'S34', 'fail_S34i', 'fail_S34iii', 'fail_S34tail', 'fail_S34iv', 'maximal']
    for (beta, s, w) in PARAMS:
        st = dict.fromkeys(keys, 0)
        for _ in range(n):                                   # generic instances
            red, blue = make_host(rng, 6, 6, 0.5)
            g = [R(sum(red[i][y] for i in range(6)), 6) for y in range(6)]
            if min(g) == 0: continue
            inst = Instance(red, blue, range(6), range(6), min(g) / 3, beta, s, w)
            checks_identities(inst, rng, st)
        got = 0; tries = 0
        while got < n and tries < 40 * n:                      # one-sided maximal instances
            tries += 1
            red, blue = make_host(rng, 8, 6, 0.8)
            c = R(rng.randint(20, 40), 100)
            pr = local_max_pair(red, 8, 6, c, beta, s, w)
            if pr is None: continue
            X, Y = pr
            if len(set(tuple(red[i][y] for y in Y) for i in X)) < 3: continue
            inst = Instance(red, blue, X, Y, c, beta, s, w)
            checks_maximal(inst, st); checks_identities(inst, rng, st); got += 1
        st['maximal'] = got
        fails = {kk: vv for kk, vv in st.items() if kk.startswith('fail') and vv}
        print('beta=%s s=%d w=%d:' % (beta, s, w), st, flush=True)
        if fails or got < n or min(st[kk] for kk in ['a', 'b', 'b_fail_inst', 'c_inst', 'd', 'e', 'S35', 'S34']) == 0:
            ok = False; print('  PROBLEM', fails)
    for tname, key in [('S2_uniform', 'fail_S2'), ('phi_shift', 'fail_a'), ('sign_shift', 'fail_c_id'), ('S35_drop', 'fail_S35')]:
        st = dict.fromkeys(keys, 0); trng = random.Random(7)
        for _ in range(2):
            red, blue = make_host(trng, 6, 6, 0.5)
            g = [R(sum(red[i][y] for i in range(6)), 6) for y in range(6)]
            if min(g) == 0: continue
            checks_identities(Instance(red, blue, range(6), range(6), min(g) / 3, *PARAMS[0]), trng, st, tamper=tname)
        print('tamper %-11s -> %s (%s = %d)' % (tname, 'REFUSED' if st[key] else 'NOT REFUSED', key, st[key]))
        ok = ok and st[key] > 0
    worst, nch, bad, conv = limit_checks()
    import mpmath as mp
    print('S3.2: H by direct optimisation vs closed form, max |diff| = %s; concavity of optimised H on %d chords: %d violations'
          % (mp.nstr(worst, 5), nch, bad))
    print('S3.3: |r S_r - M^T| at r = 1e3, 1e5, 1e7:', [[mp.nstr(e, 3) for e in row] for row in conv])
    ok = ok and worst < mp.mpf('1e-20') and bad == 0 and all(row[2] < row[0] and row[2] < 1e-4 for row in conv)
    print('CHECK B:', 'OK' if ok else 'FAILED')


if __name__ == '__main__':
    main()
