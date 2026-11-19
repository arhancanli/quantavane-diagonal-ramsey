"""Report table (floats, for reading only): certified Phi (checker A output) vs the best published exponent at g.
Published = min(bank-derived ZBS+EP, pointwise, from compare_*.tsv; Lu-Wang f; GNNW Thm 1; NSS; EP diagonal).
usage: ramsey_offdiag_table.py checkA_out.json compare.tsv lw_source.json nss_cert.json"""
import sys, json, math, bisect
from fractions import Fraction as Fr
A = json.load(open(sys.argv[1]))
pub = {round(float(l.split('\t')[0]), 6): float(l.split('\t')[3]) for l in open(sys.argv[2]).read().split('\n')[1:] if l}
d = json.load(open(sys.argv[3]))
X = [float(Fr(a)) for a in d['nodes']]; V = [float(Fr(a)) for a in d['values']]; DV = [float(Fr(a)) for a in d['derivatives']]
def P(t):
    i = min(max(bisect.bisect_right(X, t) - 1, 0), len(X) - 2); a, b = X[i], X[i + 1]; dl = b - a; u = t - a; D = V[i + 1] - V[i]
    return V[i] + DV[i]*u + (3*D/dl - 2*DV[i] - DV[i+1])/dl*u*u + (DV[i] + DV[i+1] - 2*D/dl)/dl**2*u**3
H = lambda s: (1+s)*math.log1p(s) - s*math.log(s)
lwf = lambda s: H(s) + s*math.exp(-s)*P(s)
gn = lambda s: H(s) + (-0.25*s + 0.03*s*s + 0.08*s**3)*math.exp(-s)
nd = json.load(open(sys.argv[4])); SC = nd['meta']['SC']; FS = nd['meta']['FS']
lam = [int(n[0]) / SC for n in nd['nodes']]; Fv = [int(n[1]) / FS for n in nd['nodes']]; Dv = [int(n[2]) / SC for n in nd['nodes']]
def nss(s):
    i = min(max(bisect.bisect_right(lam, s) - 1, 0), len(lam) - 2); a, b = lam[i], lam[i + 1]; u = s - a
    return Fv[i] + Dv[i]*u + 0.5*(Dv[i+1] - Dv[i])/(b - a)*u*u
print('| gamma | best published (source) | ours, certified | gain | published base | our base |')
print('|---|---|---|---|---|---|')
for r in A['phi']:
    g = float(Fr(r['g'])); ours = float(r['phi_dec_up'])
    cands = {'LW f': lwf(g), 'GNNW': gn(g), 'NSS': nss(g), 'EP diag': 625145177/500000000}
    gr = round(g, 6)
    if gr in pub:
        cands['ZBS/EP banks'] = pub[gr]
    k = min(cands, key=cands.get); b = cands[k]
    print('| %s | %.6f (%s) | %.9f | %.6f | %.5f | %.7f |' % (r['g'], b, k, ours, b - ours, math.exp(b), float(r['exp_phi_upper'])))
