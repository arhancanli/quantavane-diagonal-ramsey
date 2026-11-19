"""FLOAT check (exploration; not a proof) of the non-bank published off-diagonal exponents against our certified Phi.
Curves (log R(k, g k) / k, g = l/k <= 1): Erdos-Szekeres H; GNNW arXiv:2407.19026v2 Thm 1 (H + G e^{-g}), Thm 5
(minimised over p on a grid of 4000) and Cor 6; Lu-Wang f (source.json @ 5ec98f47); NSS spline F
(wamlat/RamseyLean-bootstrap @ e53b8cf11d code2/pq_cert_final.json). Our Phi: cell values from the certificate.
usage: ramsey_lit_curves2.py lw_source.json nss_cert.json offdiag_cert.json"""
import sys, json, math, bisect
from fractions import Fraction as Fr
d = json.load(open(sys.argv[1]))
X = [float(Fr(a)) for a in d['nodes']]; V = [float(Fr(a)) for a in d['values']]; DV = [float(Fr(a)) for a in d['derivatives']]
def P(t):
    i = min(max(bisect.bisect_right(X, t) - 1, 0), len(X) - 2)
    a, b = X[i], X[i + 1]; dl = b - a; u = t - a; D = V[i + 1] - V[i]
    return V[i] + DV[i]*u + (3*D/dl - 2*DV[i] - DV[i+1])/dl*u*u + (DV[i] + DV[i+1] - 2*D/dl)/dl**2*u**3
H = lambda s: (1+s)*math.log1p(s) - s*math.log(s)
phi = (1 + 5 ** 0.5) / 2
def thm5(s):
    lo = (5 ** 0.5 - 1) / (5 ** 0.5 + 1)
    return min(-0.5 * math.log(phi * p + (1 - 5 ** 0.5) / 2) - s * math.log(1 - p)
               for p in [lo + (1 - lo) * (i + 0.5) / 4000 for i in range(4000)])
nd = json.load(open(sys.argv[2])); SC = nd['meta']['SC']; FS = nd['meta']['FS']
lam = [int(n[0]) / SC for n in nd['nodes']]; Fv = [int(n[1]) / FS for n in nd['nodes']]; Dv = [int(n[2]) / SC for n in nd['nodes']]
def nss(s):
    i = min(max(bisect.bisect_right(lam, s) - 1, 0), len(lam) - 2); a, b = lam[i], lam[i + 1]; u = s - a
    return Fv[i] + Dv[i] * u + 0.5 * (Dv[i + 1] - Dv[i]) / (b - a) * u * u
curves = {'ES': H, 'GNNW1': lambda s: H(s) + (-0.25*s + 0.03*s*s + 0.08*s**3)*math.exp(-s),
          'GNNW5': thm5, 'GNNWc6': lambda s: s*math.log((5**0.5+1)*(1+2*s)/(4*s)) + 0.5*math.log(1+2*s),
          'LWf': lambda s: H(s) + s*math.exp(-s)*P(s), 'NSS': nss}
print('NSS F(1) = %.6f (paper 1.32680); NSS range [%.3f, %.3f]' % (nss(1.0), lam[0], lam[-1]))
cert = json.load(open(sys.argv[3]))
cells = [(float(Fr(c['lo'])), float(Fr(c['hi'])), max(float(Fr(c['v_lo'])), float(Fr(c['v_hi'])))) for c in cert['cells']]
print('g\t' + '\t'.join(curves) + '\tPhi\tmin(lit)-Phi')
worst = {}
for lo, hi, U in cells:
    if hi - lo < 1e-6:
        continue
    for t in (lo, (lo + hi) / 2):
        vals = {k: f(t) for k, f in curves.items() if not (k == 'NSS' and not lam[0] <= t <= lam[-1])}
        m = min(vals.values())
        if lo >= 0.201:
            for k, v in vals.items():
                worst[k] = min(worst.get(k, 9), v - U)
        if abs(t * 20 - round(t * 20)) < 1e-9:
            print('%.2f\t' % t + '\t'.join('%.6f' % vals.get(k, float('nan')) for k in curves) + '\t%.6f\t%+.6f' % (U, m - U))
print('min over cells with lo >= 0.201 of (curve - Phi_cell_max):', {k: round(v, 6) for k, v in worst.items()})
