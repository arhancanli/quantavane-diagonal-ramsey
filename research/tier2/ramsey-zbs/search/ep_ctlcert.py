"""Write a control certificate in EvolvingPrograms' Lean format (Support/Controls/ControlCertificate.lean at 959f46b0:
Data = (p, x, mu, beta, w, cutoff, margin, precision, tangents, degrees, cells); `ControlCertificate.sound` turns
`Checks data` (decided by the kernel) into CERT < -margin, and `PublishedControlBridge.certOK_of_parameters` into ZBS's
`CtrlD.CertOK`).  A tangent (q, m, c, k) claims sharpH(t) <= m t + c on sharpDomain; Lean checks it at q with interval
arithmetic plus mu * |sharpH'(q) - m| (concavity, EP's sharpH_tangent_of_error_bound).
This script only PROPOSES tangents (float model of EP's checks, same construction of degree and integral cells);
the Lean kernel decides.  usage: python3 ep_ctlcert.py p mu w beta x n_tangents name [lxU l1mL] > Module.lean
(all of p mu w beta x as exact rationals 'n/d')."""
import os, sys, math
from fractions import Fraction as Fr


def sharp(p, x, mu, beta, w, q):
    """EP's ParametricTangents.formula in floats: (H, H') with H = q M(q) (binding branch), plus delta and z."""
    lpx = math.log(p / x); l1q = math.log(1 - q); lmq = math.log(mu / q)
    v = beta * ((1 - q) * lpx + w * (1 - q) * l1q - w * q * lmq)
    vp = beta * (-lpx - w * l1q - w * lmq)
    delta = v / q
    z = p * math.exp(delta)
    g = p * delta + (1 - p) * (math.log(1 - z) - math.log(1 - p))
    gp = (p - z) / (1 - z)
    H = -w * q * math.log(q / mu) + q * g / beta
    D = -w * (math.log(q / mu) + 1) + (g + gp * (vp - delta)) / beta
    return H, D, delta, z


def sharp_hp(p, x, mu, beta, w, q):
    """the same (H, H', delta, z) in 90-digit decimal arithmetic from the exact rationals: near the left edge 1 - z is
    ~1e-3 and the float version loses ~1e-10 in H' (18 Nov: row 0 of the first Kaggle module failed EP's rowCheck by
    4e-11 for that reason).  Tangent data are now built from these values."""
    import decimal
    from decimal import Decimal as Dd
    with decimal.localcontext() as cx:
        cx.prec = 90
        p, x, mu, beta, w, q = (Dd(Fr(v).numerator) / Dd(Fr(v).denominator) for v in (p, x, mu, beta, w, q))
        lpx = (p / x).ln(); l1q = (1 - q).ln(); lmq = (mu / q).ln()
        v = beta * ((1 - q) * lpx + w * (1 - q) * l1q - w * q * lmq)
        vp = beta * (-lpx - w * l1q - w * lmq)
        delta = v / q
        z = p * delta.exp()
        g = p * delta + (1 - p) * ((1 - z).ln() - (1 - p).ln())
        gp = (p - z) / (1 - z)
        H = -w * q * (q / mu).ln() + q * g / beta
        D = -w * ((q / mu).ln() + 1) + (g + gp * (vp - delta)) / beta
        return Fr(H), Fr(D), float(delta), float(z)


def left_edge(p, x, mu, beta, w):
    """smallest q of the binding domain: delta(q) < -log p  (delta decreases in q near the edge)."""
    lo, hi = 1e-9, mu
    for _ in range(200):
        m = 0.5 * (lo + hi)
        _, _, d, z = (None, None, None, None)
        try:
            H, D, d, z = sharp(p, x, mu, beta, w, m)
            ok = 0 < d < -math.log(p)
        except ValueError:
            ok = False
        if ok: hi = m
        else: lo = m
    return hi


def rat(v, den=10 ** 12, up=False):
    return Fr(math.ceil(v * den) if up else round(v * den), den)


def rat_up(v, den=10 ** 12):
    """exact rational ceiling of the rational v on the grid 1/den"""
    v = Fr(v)
    return Fr(-((-v.numerator * den) // v.denominator), den)


def degree_cells(mu, tangents):
    out = []; lo = Fr(0)
    for i, (q, m, c, k) in enumerate(tangents):
        hi = mu if i + 1 == len(tangents) else (tangents[i + 1][2] - c) / (m - tangents[i + 1][1])
        out.append((lo, hi, m, c)); lo = hi
    return out


def integral_cells(w, cutoff, degrees):
    out = []; lo = Fr(0)
    for (dl, dr, m, c) in reversed(degrees):
        hi = min(cutoff, (m + w) / w)
        if lo < hi:
            out.append((lo, hi, -w * dr, (m + w) * dr + c)); lo = hi
    return out


def total(cells):
    s = 0.0
    for lo, hi, a, b in cells:
        F = lambda u: -(float(a) * (u + 1) + float(b)) * math.exp(-u)
        s += F(float(hi)) - F(float(lo))
    return s


def build(p, mu, w, beta, x, n, slack=Fr(1, 10 ** 11), edge_frac=1e-3):
    pf, muf, wf, bf, xf = map(float, (p, mu, w, beta, x))
    a = left_edge(pf, xf, muf, bf, wf)
    # tangent points: geometric near the steep left edge, uniform elsewhere
    qs = sorted(set([a + (muf - a) * t for t in [edge_frac * 4 ** i for i in range(12) if edge_frac * 4 ** i < 0.05]]
                    + [a + (muf - a) * (0.05 + 0.95 * i / (n - 1)) for i in range(n)]))
    tangents = []
    for q in qs:
        qr = rat(q, 10 ** 15)
        if not (float(qr) <= muf): qr = mu
        H, D, d, z = sharp_hp(p, x, mu, beta, w, qr)
        m = rat(float(D))
        c = rat_up(H - m * qr + mu * abs(D - m)) + slack
        k = max(2, int(math.ceil(-math.log2(1 - z))))      # EP's data: k = ceil(-log2(1 - z)), at least 2
        tangents.append((qr, m, c, k))
    degs = degree_cells(mu, tangents)
    ok_chain = all(d[0] < d[1] for d in degs) and degs[-1][1] == mu
    cutoff = Fr(32)
    cells = integral_cells(w, cutoff, degs)
    tail = all((m + w - w * cutoff) * l + c <= 0 and (m + w - w * cutoff) * r + c <= 0 for (l, r, m, c) in degs)
    return tangents, degs, cells, total(cells), ok_chain, tail, a


def lean_module(name, p, mu, w, beta, x, tangents, margin=Fr(1, 10 ** 10), precision=24, ctl=None, zline='', chunk=25):
    def q(v): return '(%d/%d : ℚ)' % (v.numerator, v.denominator)
    fmt = lambda T: ',\n    '.join('⟨%s, %s, %s, %d⟩' % (q(a), q(m), q(c), k) for (a, m, c, k) in T)
    chunks = [tangents[i:i + chunk] for i in range(0, len(tangents), chunk)]
    rowdefs = '\n\n'.join('def rows%d : List ControlCertificate.Tangent := [\n    %s]' % (i, fmt(T)) for i, T in enumerate(chunks))
    rowsum = ' ++ '.join('rows%d' % i for i in range(len(chunks)))
    rowthms = '\n'.join('theorem rows%d_checked : rows%d.all (ControlCertificate.rowCheck data) = true := by decide +kernel' % (i, i) for i in range(len(chunks)))
    rowsimp = ', '.join('rows%d_checked' % i for i in range(len(chunks)))
    s = f'''import Support.Controls.ControlCertificate
import Support.Controls.EnvelopeData
import Support.Controls.PublishedControlBridge

/-! Quantavane ramsey-zbs lane: the {name} control of our diagonal-Ramsey certificate{zline},
certified in EvolvingPrograms' format.  `checked` is decided by the kernel; `sound` and `cert_ok` reuse EvolvingPrograms'
generic theorems ControlCertificate.sound and PublishedControlBridge.certOK_of_parameters (no new axioms). -/

set_option autoImplicit false
set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace QV.RamseyZBS.{name}
open RamseyAnalytic RamseyAnalytic.ControlGeometry

{rowdefs}

def tangents : List ControlCertificate.Tangent := {rowsum}

def degrees : List Cell := EnvelopeData.degreeCells {q(mu)} tangents
def cells : List Cell := EnvelopeData.integralCells {q(w)} 32 degrees

def data : ControlCertificate.Data where
  p := {q(p)}
  x := {q(x)}
  μ := {q(mu)}
  β := {q(beta)}
  w := {q(w)}
  cutoff := 32
  margin := {q(margin)}
  precision := {precision}
  tangents := tangents
  degrees := degrees
  cells := cells

-- diagnostics (compiled evaluation, not part of the proof)
#eval (decide (ControlCertificate.parameters data), tangents.length,
  (tangents.map (ControlCertificate.rowCheck data)).count false,
  decide (ControlCertificate.GeometryChecks data),
  ((ControlCertificate.totalExpr data).safe (AnalyticBounds.FixedPointInterval.point 0)),
  ControlPower.check data.μ data.w data.x)
#eval (tangents.map (ControlCertificate.rowCheck data)).zipIdx.filter (fun t => !t.1) |>.map (·.2)

-- the kernel check, split as in EvolvingPrograms' Candidate467Certificate (one declaration per piece keeps the
-- kernel's memory per declaration small)
{rowthms}
theorem geometry_checked : ControlCertificate.GeometryChecks data := by decide +kernel
theorem linkage_checked : data.degrees.all (fun d => data.tangents.any
    (fun t => decide (d.slope=t.m ∧ d.intercept=t.c))) = true := by decide +kernel
theorem integral_checked :
    ((ControlCertificate.totalExpr data).safe (AnalyticBounds.FixedPointInterval.point 0) &&
      decide (RamseyAnalytic.TangentExpressions.boundHi
        ((ControlCertificate.totalExpr data).bound (AnalyticBounds.FixedPointInterval.point 0)) < -data.margin)) = true := by
  decide +kernel
theorem power_checked : ControlPower.check data.μ data.w data.x = true := by decide +kernel
theorem checked : ControlCertificate.Checks data := by
  refine ⟨by decide +kernel, by decide +kernel, ?_, geometry_checked, linkage_checked, integral_checked, power_checked⟩
  change ({rowsum}).all (ControlCertificate.rowCheck data) = true
  simp only [List.all_append, {rowsimp}, Bool.and_self, Bool.true_and]
theorem sound : ControlCertificate.Sound data := ControlCertificate.sound data checked
#print axioms sound
{{ctl_block}}end QV.RamseyZBS.{name}
'''
    ctl_block = ''
    if ctl is not None:
        ctl_block = f'''
/-- the control exactly as it appears in our certificate (ZBS's CtrlD) -/
def ctl : DiagRamsey.V5.CtrlD where
  p := {q(p)}
  μ := {q(mu)}
  w := {q(w)}
  β := {q(beta)}
  x := {q(x)}
  lxU := {q(ctl[0])}
  l1mL := {q(ctl[1])}

theorem ctl_ok : ctl.ok = true := by decide +kernel
theorem cert_ok : ctl.CertOK := by
  apply PublishedControlBridge.certOK_of_parameters data ctl sound
  all_goals decide +kernel
#print axioms cert_ok
'''
    return s.replace('{ctl_block}', ctl_block)


if __name__ == '__main__':
    p, mu, w, beta, x = (Fr(a) for a in sys.argv[1:6]); n = int(sys.argv[6]); name = sys.argv[7]
    t, degs, cells, tot, okc, tail, a = build(p, mu, w, beta, x, n)
    sys.stderr.write('left edge %.12f; tangents %d; chain %s; tail %s; float total (bound on CERT) %.6e\n' % (a, len(t), okc, tail, tot))
    ctl = (Fr(sys.argv[8]), Fr(sys.argv[9])) if len(sys.argv) > 9 else None
    zline = ' (z = %s)' % sys.argv[10] if len(sys.argv) > 10 else ''
    print(lean_module(name, p, mu, w, beta, x, t, ctl=ctl, zline=zline))
    if os.environ.get('QV_RED'):
        # red control: the middle tangent as is (must pass) and with its intercept lowered by 1e-6 (must be refused)
        a_, m_, c_, k_ = t[len(t) // 2]
        def q(v): return '(%d/%d : ℚ)' % (v.numerator, v.denominator)
        row = lambda cc: '⟨%s, %s, %s, %d⟩' % (q(a_), q(m_), q(cc), k_)
        open(os.environ['QV_RED'], 'w').write(f'''import Support.Controls.ControlCertificate

/-! Red control for QVRoot.lean: the middle tangent unchanged must pass `rowCheck`; the same tangent with its intercept
lowered by 1e-6 must be REFUSED by the kernel (this file is expected to fail at `red_bad`). -/
set_option maxRecDepth 100000
set_option maxHeartbeats 0
namespace QV.RamseyZBS.RootRed
open RamseyAnalytic RamseyAnalytic.ControlGeometry
def data : ControlCertificate.Data where
  p := {q(p)}
  x := {q(x)}
  μ := {q(mu)}
  β := {q(beta)}
  w := {q(w)}
  cutoff := 32
  margin := (1/10000000000 : ℚ)
  precision := 24
  tangents := []
  degrees := []
  cells := []
theorem red_good : ControlCertificate.rowCheck data {row(c_)} = true := by decide +kernel
theorem red_bad : ControlCertificate.rowCheck data {row(c_ - Fr(1, 10 ** 6))} = true := by decide +kernel
end QV.RamseyZBS.RootRed
''')
