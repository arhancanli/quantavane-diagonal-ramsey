"""ramsey_materialise_ext.py: copy of research/tier2/ramsey-zbs/search/materialise.py (19 Nov 2026) for the
extended-range generator (ramsey_gen2_ext.py, QV_RMAX): the source-cover range [1/5, 5] becomes [1/R, R], R = RMAX.
Run it through ramsey_ext_pipeline.py (which maps the module name gen2 to ramsey_gen2_ext).

Materialise the gen2 root's dependency cone as an exact-rational certificate (proposes data; the checkers decide).

History (DAG) version: objects of round q are realised against round q's pool, so everything is built in round order
and every number is computed exactly from data already fixed:
  * a route's start value g0 = max over its cells and breakpoints of (child(t) - gL(t)) + hm  (exact; the float path
    only supplies the structure: theta, cells, children, slopes);
  * every profile value = (exact maximum requirement of the pieces sharing that knot) rounded UP to 1e-12, plus a
    margin; leaf/route requirements use the certificate's own aU, bU, B + ys;
  * U_q (closed, complRaw pairs of raw objects) values = exact max(R(t), t S(1/t)) at its knots, rounded up;
  * own source lines: A = a' rounded up, B rounded up; cover cells grounded (one ZBS tangent line, exact) or pairs of
    raw objects (exact); a line whose cover fails is bumped (B += 1e-9) and rebuilt (count reported);
  * controls: x below the tabulated certifiable value; Lemma C certificate from build_ctl.py (N = 512), with x
    backed off until the float hinge bound is negative (exact check by the checkers).
Output: certificate JSON in the format of code/checkA/runA.py and code/checkB/runB.py.
usage: python3 materialise.py state.pkl zbs_bank.json out.json"""
import sys, os, json, math, pickle, collections, time      # pickle: our own local model state, never downloaded data
from fractions import Fraction as Fr
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import Gen, H, NS, RMAX
RR = Fr(int(RMAX)) if RMAX == int(RMAX) else Fr(RMAX).limit_denominator(1000)
import cone as conemod
import build_ctl
from gen_common import up, down, neg_log_up

DEN = 10 ** 12
HM = Fr(1, 10 ** 12)          # route child margin
MG = Fr(1, 10 ** 13)          # piece margin
ETA = Fr(1, 10 ** 12)         # source cover reserve (eta) and tail reserve (eps)
DELTA_ROOT = Fr(1, 10 ** 10)


def Srat(i): return Fr(5 + i, 400)


def fs(x): return '%d/%d' % (x.numerator, x.denominator)


class PL:
    """exact piecewise-linear profile (sorted rational knots)."""
    def __init__(self, p, xs, ys):
        self.p, self.xs, self.ys = p, xs, ys
    def __call__(self, t):
        from bisect import bisect_left
        xs = self.xs; k = bisect_left(xs, t)
        if k < len(xs) and xs[k] == t: return self.ys[k]
        assert 0 < k < len(xs), 'evaluation outside domain'
        x0, x1, y0, y1 = xs[k - 1], xs[k], self.ys[k - 1], self.ys[k]
        return y0 + (y1 - y0) * (t - x0) / (x1 - x0)
    def knots_in(self, lo, hi):
        from bisect import bisect_right, bisect_left
        return self.xs[bisect_right(self.xs, lo):bisect_left(self.xs, hi)]


class Mat:
    def __init__(self, g, zbs):
        self.g, self.zbs = g, zbs
        self.zraw = [PL(Fr(d['p']), [Fr(x) for x in d['xs']], [Fr(y) for y in d['ys']]) for d in zbs['raw']]
        self.zlines = [(Fr(c), Fr(d)) for c, d in zbs['lines']]
        self.zA = [Fr(a) for a in zbs['A']]; self.zB = [Fr(b) for b in zbs['B']]
        self.zlines_f = np.array([[float(c), float(d)] for c, d in self.zlines])
        self.PPr = [Fr(1, 10 ** 6)] + [Fr(p).limit_denominator(160) for p in g.PP[1:]]
        for j in range(1, len(g.PP)): assert abs(float(self.PPr[j]) - g.PP[j]) < 1e-12
        self.TUr = self.exact_TU()
        self.cert = {'raw': [], 'closed': [], 'sources': [], 'controls': [], 'root': None, 'meta': {}}
        self.rawPL = []           # PL objects of new raw profiles (index = position in cert['raw'])
        self.ctl_index = {}; self.src_index = {}; self.objmap = {}  # (pool o, step) -> ('nr', idx)
        self.Umap = {}            # (round, cell k) -> ('nc', idx)
        self.closedPL = []
        self.stats = collections.Counter()
        # table-keyed Lemma D controls (second claim): QV_CD_MAP = cdmap.json of cd_table.py (generator j, imu, iw)
        self.cdmap = {}
        if os.environ.get('QV_CD_MAP'):
            base = os.path.dirname(os.path.abspath(os.environ['QV_CD_MAP']))
            for e in json.load(open(os.environ['QV_CD_MAP'])):
                self.cdmap[(int(e['j']), int(e['imu']), int(e['iw']))] = dict(x=e['x'], cert=os.path.join(base, e['cert']))

    def exact_TU(self):
        g = self.g
        pts = set()
        for i in range(NS):
            s = Srat(i)
            if 1 / RR <= s <= RR: pts.add(s); pts.add(1 / s)
        T = sorted(t for t in pts if 1 / RR <= t <= RR)
        assert len(T) == len(g.TU) and all(abs(float(a) - b) < 1e-11 for a, b in zip(T, g.TU))
        return T

    # ---------- references ----------
    def ref_obj(self, o, i_step):
        """reference of pool object o for grid step i (covering [S_{i-1}, S_i])."""
        tag = self.g.pool_tag[o]
        if tag[0] == 'zr': return ('zr', tag[1]), self.zraw[tag[1]]
        r = self.objmap[(o, i_step)]
        return r, self.rawPL[r[1]]

    def ref_prof(self, ref):
        k, i = ref
        if k == 'zr': return self.zraw[i]
        if k == 'nr': return self.rawPL[i]
        if k == 'nc': return self.closedPL[i]
        raise KeyError(ref)

    # ---------- controls ----------
    def control(self, j, imu, iw, custom=None, cd_x=None):
        key = (j, imu, iw) if custom is None else (j, 'custom') + tuple(custom)
        if cd_x is not None: key = key + ('cd', cd_x)
        if key in self.ctl_index: return self.ctl_index[key]
        if cd_x is not None: return self.control_cd(j, custom, cd_x, key)
        if custom is None and self.cdmap and (int(j), int(imu), int(iw)) in self.cdmap:
            e = self.cdmap[(int(j), int(imu), int(iw))]
            return self.control_cd(j, None, e['x'], key, imu=imu, iw=iw, stored=e['cert'])
        g = self.g
        p = self.PPr[j] - Fr(1, 10 ** 6)
        if custom is None:
            mu = Fr(round(g.MU[imu] * 1e12), 10 ** 12); w = Fr(round(g.W[iw] * 1e12), 10 ** 12); a_tab = g.acl[j, imu, iw]
        else:
            mu = Fr(round(custom[0] * 1e12), 10 ** 12); w = Fr(round(custom[1] * 1e12), 10 ** 12); a_tab = custom[2]
        beta = 1 - Fr(1, 10 ** 7)
        xf = math.exp(-a_tab) * (1 - 1e-10)
        cert = None
        for k in range(40):
            x = down(xf, 10 ** 15)
            cap = min(float(p), (1 - float(mu)) ** float(w))
            if float(x) < cap * (1 - 1e-12):
                cert = build_ctl.build(p, mu, w, beta, x, N=512)
                if cert is not None and cert['float_bound'] < -1e-12: break
            xf *= (1 - 2e-7 * (2 ** min(k, 20)))
            cert = None
        assert cert is not None, ('control not certifiable', key)
        if k: self.stats['control_backoffs'] += 1
        lxU = up(math.log(float(x)) + 1e-13)
        while not math.exp(float(lxU)) >= float(x): lxU += Fr(1, DEN)
        l1mL = down(math.log(1 - float(mu)) - 1e-13)
        c = {'p': fs(p), 'mu': fs(mu), 'w': fs(w), 'beta': fs(beta), 'x': fs(x), 'lxU': fs(lxU), 'l1mL': fs(l1mL),
             'cert': {'a_cut': cert['a_cut'], 'q': cert['q'], 'h': cert['h'], 'sec': cert['sec'], 'k': cert['k']},
             'gen': {'j': int(j), 'imu': int(imu), 'iw': int(iw), 'a_table': float(a_tab), 'custom': custom is not None}}
        self.cert['controls'].append(c)
        idx = len(self.cert['controls']) - 1
        self.ctl_index[key] = (idx, p, mu, w, x)
        return self.ctl_index[key]

    def control_cd(self, j, custom, cd_x, key, imu=None, iw=None, stored=None):
        """control kind CD (second claim, assuming Theorem A): x = cd_x exactly, certified by Lemma D (frozen generator
        code/lemmaD/genD.py run in the python-flint interpreter named by QV_FLINT_PY).  Raises if Lemma D fails (the
        caller then has no CD claim; the ZBS-only certificate is unaffected)."""
        import subprocess, tempfile
        p = self.PPr[j] - Fr(1, 10 ** 6)
        if custom is not None:
            mu = Fr(round(custom[0] * 1e12), 10 ** 12); w = Fr(round(custom[1] * 1e12), 10 ** 12)
        else:      # table control (same rounding as control())
            mu = Fr(round(self.g.MU[imu] * 1e12), 10 ** 12); w = Fr(round(self.g.W[iw] * 1e12), 10 ** 12)
        beta = 1 - Fr(1, 10 ** 7); x = Fr(cd_x)
        here = os.path.dirname(os.path.abspath(__file__))
        stored = stored or os.environ.get('QV_CD_CERT')
        if stored:
            # a STORED, checker-accepted Lemma D certificate (ramsey-lemma certs/, pinned in code/lemmaD/MANIFEST.sha256):
            # the bank control must equal its control exactly
            sc = json.load(open(stored))
            mine = {'p': fs(p), 'mu': fs(mu), 'w': fs(w), 'beta': fs(beta), 'x': fs(x)}
            assert all(Fr(sc['control'][k]) == Fr(v) for k, v in mine.items()), ('stored CD certificate control differs', sc['control'], mine)
            lem = {k: v for k, v in sc.items() if k != 'control'}
        else:
            out = tempfile.mktemp(suffix='.json')
            r = subprocess.run([os.environ['QV_FLINT_PY'], '-I', os.path.join(here, '..', 'code', 'lemmaD', 'gen_cd.py'),
                                fs(p), fs(mu), fs(w), fs(beta), fs(x), out], capture_output=True, text=True)
            assert r.returncode == 0, ('Lemma D generator failed', key, r.stderr[-500:])
            lem = json.load(open(out)); os.remove(out)
        lxU = up(math.log(float(x)) + 1e-13)
        while not math.exp(float(lxU)) >= float(x): lxU += Fr(1, DEN)
        l1mL = down(math.log(1 - float(mu)) - 1e-13)
        c = {'p': fs(p), 'mu': fs(mu), 'w': fs(w), 'beta': fs(beta), 'x': fs(x), 'lxU': fs(lxU), 'l1mL': fs(l1mL),
             'lemmaD': lem, 'gen': {'j': int(j), 'custom': custom is not None, 'cd_x': cd_x,
                                    'imu': None if imu is None else int(imu), 'iw': None if iw is None else int(iw),
                                    'scales': 'Lambda = {u_b + k Dplus : k = 0, ..., (1 - u_b)/Dplus} (lemmaD u_b, Dplus)'}}
        self.cert['controls'].append(c)
        idx = len(self.cert['controls']) - 1
        self.ctl_index[key] = (idx, p, mu, w, x)
        self.stats['controls_lemmaD'] += 1
        return self.ctl_index[key]

    def terminal(self, ctl, src):
        """terminal data for control ctl = (idx, p, mu, w, x) and source (kind, h, A, B)."""
        idx, p, mu, w, x = ctl
        A = src[2]
        import ivA
        eA = ivA.exp(-A).lof()
        xi = down(min(x, eA) * (1 - Fr(1, 10 ** 11)), 10 ** 15)
        nu = down(mu * (1 - Fr(1, 10 ** 11)), 10 ** 15)
        ysl = Fr(1, 10 ** 12)
        aU = neg_log_up(xi); bU = neg_log_up(nu)
        T = {'c': idx, 'src': [src[0], src[1]], 'xi': fs(xi), 'nu': fs(nu), 'ys': fs(ysl), 'aU': fs(aU), 'bU': fs(bU)}
        return T, aU, bU, src[3] + ysl, w

    # ---------- sources ----------
    def source(self, q, a, b):
        """own line of round q at intercept a (slope >= b), covered with round q's pool; returns ('n', idx, A, B)."""
        key = (q, round(a, 12))
        if key in self.src_index: return self.src_index[key]
        A = up(a + 1e-12, DEN); B = up(b + 2e-12, DEN)
        B0 = B
        for bump in range(40):
            cov = self.cover(q, A, B)
            if cov is not None: break
            B = B0 + Fr(2 ** bump, 10 ** 10); self.stats['source_bumps'] += 1
        if B > B0: self.stats['source_bump_max_1e-10'] = max(self.stats['source_bump_max_1e-10'], int((B - B0) * 10 ** 10))
        assert cov is not None, ('source cover failed', q, a, b)
        cov.update({'A': fs(A), 'B': fs(B)})
        self.cert['sources'].append(cov)
        r = ('n', len(self.cert['sources']) - 1, A, B)
        self.src_index[key] = r
        return r

    def zsource(self, a):
        """ZBS's best line with A <= a (exact)."""
        if not hasattr(self, '_zc'): self._zc = {}
        if a in self._zc: return self._zc[a]
        best = None
        for h, (A, B) in enumerate(zip(self.zA, self.zB)):
            if float(A) <= a + 1e-15 and (best is None or B < best[3]): best = ('z', h, A, B)
        self._zc[a] = best
        return best

    def line_ok(self, k, A, B, e, t):
        c, d = self.zlines[k]
        return c + d * t <= A + B * t - e * (1 + t)

    def best_line(self, A, B, e, t0, t1):
        """a ZBS tangent line below A + B t - e(1+t) at t0 and t1 (exact), or None."""
        tm = float(t0 + t1) / 2
        vals = self.zlines_f[:, 0] + self.zlines_f[:, 1] * tm
        for k in np.argsort(vals)[:6]:
            k = int(k)
            if self.line_ok(k, A, B, e, t0) and self.line_ok(k, A, B, e, t1): return k
        return None

    def cover(self, q, A, B):
        r = self._cover(q, A, B)
        return r

    def _why(self, msg):
        if os.environ.get('QV_DEBUG_COVER'): self.stats['why_' + msg] += 1
        return None

    def _cover(self, q, A, B):
        g = self.g; T = self.TUr
        Q, bR, bS, QK = g.Uhist[q]
        cells = []
        # tails
        Af, Bf = float(A), float(B)
        LF = self.zlines_f
        cand = [k for k in range(len(LF)) if LF[k, 0] <= Af - 2e-12]
        if not cand: return self._why('no_left_line')
        # left tail: Lo as large as possible
        bestL = None
        for k in cand:
            c, d = LF[k]
            Lo = (Af - 1e-9 - c) / (d - Bf) if d > Bf else 1e9
            if bestL is None or Lo > bestL[0]: bestL = (Lo, k)
        Lo = min(down(bestL[0] * (1 - 1e-9), 10 ** 9), 1 / RR); kL = bestL[1]
        if Lo <= 0: return self._why('Lo')
        while not (self.line_ok(kL, A, B, ETA, Fr(0)) and self.line_ok(kL, A, B, ETA, Lo)):
            Lo = Lo * Fr(999, 1000)
            if Lo < Fr(1, 10 ** 6): return self._why('Lo_small')
        bestR = None
        for k in range(len(LF)):
            c, d = LF[k]
            if d <= Bf - 2e-12:
                Hi = (c - Af + 1e-9) / (Bf - d)
                if bestR is None or Hi < bestR[0]: bestR = (Hi, k)
        if bestR is None: return self._why('no_right_line')
        Hi = max(up(max(bestR[0], 0) * (1 + 1e-9) + 1e-9, 10 ** 9), RR); kR = bestR[1]
        while not (self.line_ok(kR, A, B, ETA, Hi) and self.zlines[kR][1] <= B - ETA):
            Hi = Hi * Fr(1001, 1000)
            if Hi > 10 ** 6: return self._why('Hi_big')
        # grounded cells on [Lo, 1/R] and [R, Hi]: greedy
        def grounded_run(t0, t1):
            out = []; cur = t0
            while cur < t1:
                k = None; span = float(t1 - cur)
                for h in range(24):
                    tn = t1 if h == 0 else min(t1, up(float(cur) + span / 2 ** h, 10 ** 9))
                    if tn <= cur: break
                    kk = self.best_line(A, B, ETA, cur, tn)
                    if kk is not None: k = kk; break
                if k is None: return None
                out.append({'kind': 'grounded', 'k': k, 'lo': fs(cur), 'hi': fs(tn)}); cur = tn
            return out
        left = grounded_run(Lo, 1 / RR) if Lo < 1 / RR else []
        if left is None: return self._why('left_grounded')
        cells += left
        Ki = list(g.Kidx)
        for m in range(len(Ki) - 1):
            fine = [(T[k], T[k + 1]) for k in range(Ki[m], Ki[m + 1])]
            # grounded if every fine cell has a tangent line below the source line; keep extending the open grounded cell
            # with its own line while that line stays below at the new end (both affine: the whole cell is covered)
            tent = []
            last = cells[-1] if (cells and cells[-1]['kind'] == 'grounded') else None
            ok = True
            for t0, t1 in fine:
                cur = tent[-1] if tent else last
                if cur is not None and Fr(cur['hi']) == t0 and self.line_ok(int(cur['k']), A, B, ETA, t1):
                    if tent: tent[-1] = dict(tent[-1], hi=fs(t1))
                    else: tent.append(dict(last, hi=fs(t1), _ext=True))
                    continue
                kk = self.best_line(A, B, ETA, t0, t1)
                if kk is None: ok = False; break
                tent.append({'kind': 'grounded', 'k': kk, 'lo': fs(t0), 'hi': fs(t1)})
            if ok:
                for c in tent:
                    if c.pop('_ext', False): cells[-1] = c
                    else: cells.append(c)
                continue
            a0, a1 = T[Ki[m]], T[Ki[m + 1]]
            try:
                rU, PU = self.U_ref(q, a0, a1); rV, PV = self.U_ref(q, 1 / a1, 1 / a0)
            except (KeyError, AssertionError):
                self.stats['source_missing_U'] += 1; return None
            lineA, lineB = A - ETA, B - ETA
            if not all(PU(t) <= lineA + lineB * t and t * PV(1 / t) <= lineA + lineB * t for t in (a0, a1)):
                if os.environ.get('QV_DEBUG_COVER'):
                    ex = max(max(PU(t), t * PV(1 / t)) - (lineA + lineB * t) for t in (a0, a1))
                    self.stats['why_pair_round%d' % q] += 1
                    if os.environ.get('QV_DEBUG_STOP') and ex > Fr(1, 10 ** 7):
                        Uf, bRf, bSf, QKf = g.Uhist[q]
                        Kf = g.K; m0 = int(np.searchsorted(Kf, float(a0) - 1e-9))
                        print('FIRST_BIG_FAIL round', q, 'A', float(A), 'B', float(B), 'interval', float(a0), float(a1), 'excess', float(ex))
                        for t, mm in ((a0, m0), (a1, m0 + 1)):
                            print('  t %.6f exact U %.9f float QK %.9f | exact refl %.9f float refl %.9f | line %.9f' % (
                                float(t), float(PU(t)), QKf[mm], float(t * PV(1 / t)), Kf[mm] * QKf[g.Krec[mm]], float(lineA + lineB * t)))
                        T = self.TUr; Ki = list(g.Kidx)
                        mr = int(g.Krec[m0 + 1])
                        print('  PV run knots near 1/a1:', [(round(float(x), 6), float(PV(x))) for x in PV.xs if abs(float(x) - float(1 / a1)) < 0.005])
                        dbg = getattr(self, '_Udbg', {}).get((q, PV.xs[0]))
                        if dbg:
                            yv, exv = dbg
                            print('  exact y near:', [(round(float(t), 6), float(v)) for t, v in sorted(yv.items()) if abs(float(t) - float(1 / a1)) < 0.004])
                            print('  exact chord excess per interval near:', [(m, float(e)) for m, e in sorted(exv.items()) if abs(float(T[Ki[m]]) - float(1 / a1)) < 0.006])
                        print('  float QK near:', [(Kf[i], QKf[i]) for i in range(max(mr - 2, 0), mr + 3)])
                        for k in list(range(Ki[mr] - 2, Ki[mr] + 2)) + list(range(Ki[m0] - 1, Ki[m0 + 1] + 1)):
                            if k < 0 or k >= len(T) - 1: continue
                            t0, t1 = T[k], T[k + 1]
                            try:
                                rR, PR = self.pair_ref(int(bRf[k]), t0, t1); rS, PS = self.pair_ref(int(bSf[k]), 1 / t1, 1 / t0)
                            except Exception as e_:
                                print('   cell', k, 'pair lookup failed', e_); continue
                            V = g.pool_v
                            fR = np.interp(float(t0), g.S, V[int(bRf[k])]); fS = float(t0) * np.interp(1 / float(t0), g.S, V[int(bSf[k])])
                            print('   cell %d [%.5f,%.5f] R %s S %s exact R(t0) %.9f float %.9f | exact refl %.9f float %.9f' % (
                                k, float(t0), float(t1), g.pool_tag[int(bRf[k])], g.pool_tag[int(bSf[k])], float(PR(t0)), fR, float(t0 * PS(1 / t0)), fS))
                        raise SystemExit('stopped at first big pair failure')
                    self.stats['why_pair'] += 1; self.stats['why_pair_max_excess_1e-12'] = max(self.stats['why_pair_max_excess_1e-12'], int(ex * 10 ** 12))
                    self.stats['why_pair_at_%.2f' % float(a0)] += 1
                return None
            if (cells and cells[-1]['kind'] == 'pair' and Fr(cells[-1]['hi']) == a0 and cells[-1]['PR'] == list(rU)
                    and cells[-1]['PB'] == list(rV)):
                cells[-1]['hi'] = fs(a1); cells[-1]['bp'].append(fs(a1))
            else:
                cells.append({'kind': 'pair', 'PR': list(rU), 'PB': list(rV), 'lo': fs(a0), 'hi': fs(a1), 'bp': [fs(a0), fs(a1)]})
            self.stats['source_pair_intervals'] += 1
        right = grounded_run(RR, Hi) if Hi > RR else []
        if right is None: return self._why('right_grounded')
        cells += right
        return {'Lo': fs(Lo), 'Hi': fs(Hi), 'eps': fs(ETA), 'eta': fs(ETA), 'kL': kL, 'kR': kR, 'cells': cells}

    def Rmap(self, q): return None

    def pair_ref(self, o, t0, t1):
        """reference to raw object o (pool index) covering [t0, t1] (exact)."""
        tag = self.g.pool_tag[o]
        if tag[0] == 'zr': return ('zr', tag[1]), self.zraw[tag[1]]
        i0 = int(math.floor((float(t0) - 0.0125) * 400 + 1e-9)); i1 = int(math.ceil((float(t1) - 0.0125) * 400 - 1e-9))
        r = self.objmap[(o, max(i0 + 1, 1))]
        P = self.rawPL[r[1]]
        assert P.xs[0] <= t0 and t1 <= P.xs[-1], 'pair object domain'
        return r, P

    # ---------- U ----------
    def build_U(self, q, cells):
        """closed complementary-pair objects of round q: pieces = fine T_U cells (pair of RAW objects), knots = the coarse
        set K (multiples of 1/80 and reciprocals); knot values rounded up so that every chord lies above every fine
        requirement (exact).  One object per run of consecutive defined coarse intervals."""
        g = self.g; T = self.TUr
        U, bR, bS, QK = g.Uhist[q]
        Ki = list(g.Kidx)
        cells = set(cells)
        intervals = [m for m in range(len(Ki) - 1) if all(k in cells for k in range(Ki[m], Ki[m + 1]))]
        runs = []
        for m in intervals:
            if runs and runs[-1][-1] == m - 1: runs[-1].append(m)
            else: runs.append([m])
        for run in runs:
            k0, k1 = Ki[run[0]], Ki[run[-1] + 1]            # fine cells k0 .. k1-1
            y = {}; pieces = []
            for k in range(k0, k1):
                t0, t1 = T[k], T[k + 1]
                rR, PR = self.pair_ref(int(bR[k]), t0, t1); rS, PS = self.pair_ref(int(bS[k]), 1 / t1, 1 / t0)
                for t in (t0, t1):
                    v = max(PR(t), t * PS(1 / t)); y[t] = max(y.get(t, v), v)
                pieces.append({'kind': 'pair', 'R': list(rR), 'S': list(rS), 'lo': fs(t0), 'hi': fs(t1), 'bp': [fs(t0), fs(t1)]})
            # knot values: the generator's own coarse values (QK, rounded up by 1e-9), so that the exact U equals the U
            # that the generator's source lines were computed against; then verify exactly that every chord lies above
            # every fine requirement and raise an interval's ends only where it does not (17 Nov fix: trimmed raw
            # objects are lower at run ends, which created kinks that the old chord raise turned into higher knots)
            knots = run + [run[-1] + 1]
            val = {m: up(Fr(float(QK[m])) + Fr(1, 10 ** 9), DEN) for m in knots}
            ex = {}
            for m in run:
                a0, a1 = T[Ki[m]], T[Ki[m + 1]]
                for _ in range(3):
                    v0, v1 = val[m], val[m + 1]
                    need = max(y[T[f]] - (v0 + (v1 - v0) * (T[f] - a0) / (a1 - a0)) for f in range(Ki[m], Ki[m + 1] + 1))
                    if need <= 0: break
                    val[m] = up(v0 + need + Fr(1, 10 ** 13), DEN); val[m + 1] = up(v1 + need + Fr(1, 10 ** 13), DEN)
                    self.stats['U_raised_intervals'] += 1
                ex[m] = need
            xs = [T[Ki[m]] for m in knots]
            ys = [val[m] for m in knots]
            idx = len(self.cert['closed'])
            self.cert['closed'].append({'p': fs(self.PPr[0]), 'xs': [fs(x) for x in xs], 'ys': [fs(v) for v in ys],
                                        'min': fs(down(min(ys) / 2, DEN)), 'pieces': pieces, 'gen': {'U': q}})
            P = PL(self.PPr[0], xs, ys)
            if os.environ.get('QV_DEBUG_COVER'):
                self._Udbg = getattr(self, '_Udbg', {}); self._Udbg[(q, xs[0])] = (y, ex)
            # sanity (exact): every fine requirement under the chord
            assert all(P(t) >= v for t, v in y.items())
            self.closedPL.append(P)
            for k in range(k0, k1): self.Umap[(q, k)] = ('nc', idx)

    def U_ref(self, q, t0, t1):
        T = self.TUr
        from bisect import bisect_right
        k = bisect_right(T, t0) - 1
        r = self.Umap[(q, k)]
        P = self.closedPL[r[1]]
        assert P.xs[0] <= t0 and t1 <= P.xs[-1], 'U domain'
        return r, P

    # ---------- raw pieces ----------
    def piece_requirements(self, rec, q, lo_i, hi_i, extra_last=None):
        """exact piece data and requirement per knot for a leaf/route record of round q on grid nodes lo_i..hi_i."""
        g = self.g
        j = rec['j']
        ctl = self.control(j, rec['imu'], rec['iw'], rec.get('custom'), rec.get('cd_x'))
        sk = conemod.source_kind(g, q, rec['a'], rec['b'])
        src = self.zsource(rec['a']) if sk[0] == 'z' else self.source(sk[1], sk[2], sk[3])
        T, aU, bU, Bys, w = self.terminal(ctl, src)
        nodes = [Srat(i) for i in range(lo_i, hi_i + 1)]
        if extra_last is not None: nodes.append(extra_last)
        if rec['kind'] == 0:
            req = {t: MG * (1 + t) + (aU + t * (Bys + w * bU)) / (1 + w) for t in nodes}
            piece = dict(T); piece.update({'kind': 'leaf', 'margin': fs(MG)})
            return piece, req
        steps, _ = conemod.route_steps(g, rec, q)
        th = rec['th']
        # cells: merge consecutive steps with the same child object and bucket
        cells = []
        for (i, jj, o) in steps:
            if jj == 0: key = ('U', q)
            else: key = ('o', o)
            if cells and cells[-1]['key'] == key and cells[-1]['j'] == jj: cells[-1]['i1'] = i
            else: cells.append({'key': key, 'j': jj, 'i0': i - 1, 'i1': i})
        us = [Srat(cells[0]['i0'])] + [Srat(c['i1']) for c in cells]
        if extra_last is not None:
            us[-1] = extra_last          # last cell extended past S_r (root): same child, same slope
        ds, calls = [], []
        for c in cells:
            t0, t1 = Srat(c['i0']), (Srat(c['i1']) if not (extra_last is not None and c is cells[-1]) else extra_last)
            if c['key'][0] == 'U':
                ref, P = self.U_ref(c['key'][1], t0, t1)
            else:
                ref, P = self.ref_obj(c['key'][1], c['i1'] if extra_last is None or c is not cells[-1] else c['i1'])
                if not (P.xs[0] <= t0 and t1 <= P.xs[-1]):
                    raise AssertionError(('child domain', ref, float(t0), float(t1)))
            z = 1 - P.p - Fr(1, 10 ** 12)
            d = neg_log_up(z)
            ds.append(d)
            cbp = [t0] + [x for x in P.knots_in(t0, t1)] + [t1]
            calls.append({'ch': list(ref), 'z': fs(z), 'bp': cbp, 'P': P})
        # gL and exact g0
        pre = [Fr(0)]
        for k, d in enumerate(ds): pre.append(pre[-1] + d * (us[k + 1] - us[k]))
        def gL(t):
            from bisect import bisect_left
            if t <= us[0]: return Fr(0)
            if t >= us[-1]: return pre[-1]
            k = bisect_left(us, t) - 1
            return pre[k] + ds[k] * (t - us[k])
        g0 = max(cl['P'](t) - gL(t) for cl in calls for t in cl['bp']) + HM + Fr(1, 10 ** 13)
        g0 = up(g0, 10 ** 13)
        thr = us[0]
        req = {}
        for t in nodes:
            G = gL(t)
            req[t] = max(MG + g0 + G, MG + (aU + w * thr * bU) / (1 + w) + t * Bys / (1 + w) + w / (1 + w) * G)
        for cl in calls:
            cl['bp'] = [fs(x) for x in cl['bp']]; del cl['P']
        piece = {'kind': 'route', 't': T, 'us': [fs(u) for u in us], 'ds': [fs(d) for d in ds], 'calls': calls,
                 'g0': fs(g0), 'hm': fs(HM), 'margin': fs(MG)}
        self.stats['route_cells'] += len(calls)
        return piece, req

    def build_raw(self, o, q, j, rs):
        """new raw object o (round q, bucket j) on the needed pieces rs (right ends), one profile per contiguous run."""
        g = self.g; kp = g.kp
        rs = sorted(rs); runs = []
        for r in rs:
            if runs and runs[-1][-1] == r - kp: runs[-1].append(r)
            else: runs.append([r])
        for run in runs:
            reqs = {}; pieces = []
            for r in run:
                rec = self.recs[(q, j, r)]
                piece, req = self.piece_requirements(rec, q, r - kp, r)
                piece['lo'] = fs(Srat(r - kp)); piece['hi'] = fs(Srat(r))
                piece['bp'] = [fs(Srat(i)) for i in range(r - kp, r + 1)]
                pieces.append(piece)
                for t, v in req.items(): reqs[t] = max(reqs.get(t, v), v)
            xs = [Srat(i) for i in range(run[0] - kp, run[-1] + 1)]
            ys = [up(reqs[t] + Fr(1, 10 ** 13), DEN) for t in xs]
            idx = len(self.cert['raw'])
            self.cert['raw'].append({'p': fs(self.PPr[j]), 'xs': [fs(x) for x in xs], 'ys': [fs(y) for y in ys],
                                     'min': fs(down(min(ys) / 2, DEN)), 'pieces': pieces, 'gen': {'round': q, 'j': int(j)}})
            self.rawPL.append(PL(self.PPr[j], xs, ys))
            for i in range(run[0] - kp + 1, run[-1] + 1): self.objmap[(o, i)] = ('nr', idx)

    def build_root(self, root):
        q = root['round']; r = root['r']
        hi = Fr(1) + 2 * DELTA_ROOT; lo = Fr(1) - 2 * DELTA_ROOT
        piece, req = self.piece_requirements(root, q, r, r, extra_last=hi) if root['kind'] == 1 else \
            self.piece_requirements(root, q, r, r, extra_last=hi)
        z = up(max(req.values()) + Fr(1, 10 ** 13), DEN)
        piece['lo'] = fs(lo); piece['hi'] = fs(hi); piece['bp'] = [fs(lo), fs(Fr(1)), fs(hi)]
        idx = len(self.cert['raw'])
        self.cert['raw'].append({'p': fs(self.PPr[root['j']]), 'xs': [fs(lo), fs(hi)], 'ys': [fs(z), fs(z)],
                                 'min': fs(down(z / 2, DEN)), 'pieces': [piece], 'gen': {'root': True, 'round': q}})
        self.rawPL.append(PL(self.PPr[root['j']], [lo, hi], [z, z]))
        d = DELTA_ROOT
        Qxs = [1 - d, Fr(1), 1 + d]; Qys = [z, z, up(z * (1 + d), DEN)]
        cidx = len(self.cert['closed'])
        self.cert['closed'].append({'p': '1/2', 'xs': [fs(x) for x in Qxs], 'ys': [fs(y) for y in Qys],
                                    'min': fs(down(z / 2, DEN)),
                                    'pieces': [{'kind': 'pair', 'R': ['nr', idx], 'S': ['nr', idx], 'lo': fs(1 - d),
                                                'hi': fs(1 + d), 'bp': [fs(1 - d), '1/1', fs(1 + d)]}], 'gen': {'Q': True}})
        self.closedPL.append(PL(Fr(1, 2), Qxs, Qys))
        self.cert['root'] = {'closed': cidx, 'z': fs(z), 'z_float': float(z)}
        return z

    def run(self):
        g = self.g; t0 = time.time()
        root = g.last_root
        npcs, nU, srcs, nsteps = conemod.cone(g, root, root_extra=True)
        self.recs = {}
        for q, rs in enumerate(g.recs_hist):
            for rec in rs: self.recs[(q, rec['j'], rec['r'])] = rec
        R = root['round']
        for q in range(R + 1):
            if nU.get(q): self.build_U(q, nU[q])
            for o, rs in sorted(npcs.items()):
                tag = g.pool_tag[o]
                if tag[1] == q: self.build_raw(o, q, tag[2], rs)
            print('round %d materialised: raw %d closed %d sources %d controls %d  %.0fs' % (
                q, len(self.cert['raw']), len(self.cert['closed']), len(self.cert['sources']), len(self.cert['controls']),
                time.time() - t0), flush=True)
        z = self.build_root(root)
        self.cert['meta'] = {'float_root': float(root['vals'][-1]), 'z': float(z), 'stats': dict(self.stats),
                             'rounds': R + 1, 'kp': g.kp}
        return z


if __name__ == '__main__':
    g = pickle.load(open(sys.argv[1], 'rb'))
    zbs = json.load(open(sys.argv[2]))
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'code', 'checkA'))
    m = Mat(g, zbs)
    z = m.run()
    json.dump(m.cert, open(sys.argv[3], 'w'))
    print('certificate written: z = %s = %.12f (float model %.12f); stats %s' % (fs(z), float(z), g.last_root['vals'][-1], dict(m.stats)))
