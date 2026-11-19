"""The certK3 root control in EvolvingPrograms' ControlCertificate format, as separately compiled modules so that no
single lean process holds the whole kernel check (the one-file version needs > 6 GB and is killed by the lab
governor; on Kaggle it is the same check).  Data are the same as lean/kaggle_root/QVRoot.lean (tangent rows identical,
checked below); degrees and cells are written as literal lists (EP's EnvelopeData builders are only generators: the
checks `Checks data` verify every property, and `ControlCertificate.sound` holds for any Data).
Each piece is decided by the kernel (`decide +kernel`); Main assembles `Checks data` from the pieces with List.all_append
and applies EP's ControlCertificate.sound and PublishedControlBridge.certOK_of_parameters.  No native_decide, no sorry.
usage: python3 gen_split.py outdir"""
import os, re, sys
from fractions import Fraction as Fr
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'search'))
import ep_ctlcert as E

import json
# default: certK3's root control; or a control dict (p, mu, w, beta, x, lxU, l1mL as exact strings) and a module name
#   python3 gen_split.py outdir [control.json Name]
if len(sys.argv) > 3:
    cj = json.load(open(sys.argv[2])); NAME = sys.argv[3]
    P = {k: Fr(cj[k]) for k in ('p', 'mu', 'w', 'beta', 'x')}; CTL = (Fr(cj['lxU']), Fr(cj['l1mL']))
else:
    NAME = 'Root'
    P = dict(p=Fr(499999, 10 ** 6), mu=Fr(201365398437, 5 * 10 ** 11), w=Fr(3592666967, 7812500000), beta=Fr(9999999, 10 ** 7),
             x=Fr(164602509056929, 5 * 10 ** 14))
    CTL = (Fr(-138884320867, 125000000000), Fr(-5153873407173, 10 ** 13))
MOD = 'QVRootSplit' if NAME == 'Root' else 'QV%sSplit' % NAME
CH = 25
T, degs, cells, tot, okc, tail, a = E.build(P['p'], P['mu'], P['w'], P['beta'], P['x'], 200)
cells = [(l, r, s, i) for (l, r, s, i) in cells]
q = lambda v: '(%d/%d : ℚ)' % (v.numerator, v.denominator)
mine = ['⟨%s, %s, %s, %d⟩' % (q(a_), q(m), q(c), k) for (a_, m, c, k) in T]
if NAME == 'Root':      # identical rows to the one-file module
    one = open(os.path.join(HERE, '..', 'kaggle_root', 'QVRoot.lean')).read()
    pat = r'⟨\([-0-9/]+ : ℚ\), \([-0-9/]+ : ℚ\), \([-0-9/]+ : ℚ\), \d+⟩'
    assert re.findall(pat, one) == mine, 'tangent rows differ from QVRoot.lean'
assert okc and tail and tot < -1e-9, ('float model fails', okc, tail, tot)

out = os.path.join(sys.argv[1], MOD); os.makedirs(out, exist_ok=True)
HEAD = ['set_option autoImplicit false', 'set_option maxRecDepth 100000', 'set_option maxHeartbeats 0',
        'set_option linter.unusedSimpArgs false', '', 'namespace QV.RamseyZBS.' + NAME,
        'open RamseyAnalytic RamseyAnalytic.ControlGeometry', '']
def write(name, imports, lines):
    open(os.path.join(out, name + '.lean'), 'w').write('\n'.join(imports + [''] + HEAD + lines + ['', 'end QV.RamseyZBS.' + NAME, '']))
chunks = lambda L: [L[i:i + CH] for i in range(0, len(L), CH)]
cell = lambda c: '⟨%s, %s, %s, %s⟩' % tuple(q(v) for v in c)

D = ['/-! Quantavane ramsey-zbs lane: data of %s (z = 1248056263241/10^12, the ZBS-only headline). -/' % ('the certK3 root control' if NAME == 'Root' else 'certK3 control ' + NAME), '']
rowids = []
for k, ch in enumerate(chunks(mine)):
    ids = ['rows%d_%d' % (k, i) for i in range(len(ch))]
    D += ['def %s : ControlCertificate.Tangent := %s' % (i, t) for i, t in zip(ids, ch)]
    D.append('def rows%d : List ControlCertificate.Tangent := [%s]' % (k, ', '.join(ids))); rowids.append(ids)
NR = len(rowids)
D.append('def tangents : List ControlCertificate.Tangent := ' + ' ++ '.join('rows%d' % k for k in range(NR)))
dgc = chunks([(l, r, m, c) for (l, r, m, c) in degs]); clc = chunks(cells)
for k, ch in enumerate(dgc): D.append('def dg%d : List Cell := [\n    %s]' % (k, ',\n    '.join(cell(c) for c in ch)))
for k, ch in enumerate(clc): D.append('def cl%d : List Cell := [\n    %s]' % (k, ',\n    '.join(cell(c) for c in ch)))
DG = ' ++ '.join('dg%d' % k for k in range(len(dgc))); CL = ' ++ '.join('cl%d' % k for k in range(len(clc)))
D += ['def degrees : List Cell := ' + DG, 'def cells : List Cell := ' + CL, '',
      'def data : ControlCertificate.Data where',
      '  p := %s' % q(P['p']), '  x := %s' % q(P['x']), '  μ := %s' % q(P['mu']), '  β := %s' % q(P['beta']),
      '  w := %s' % q(P['w']), '  cutoff := 32', '  margin := (1/10000000000 : ℚ)', '  precision := 24',
      '  tangents := tangents', '  degrees := degrees', '  cells := cells', '',
      '/-- the control exactly as it appears in our certificate (ZBS\'s CtrlD) -/',
      'def ctl : DiagRamsey.V5.CtrlD where',
      '  p := %s' % q(P['p']), '  μ := %s' % q(P['mu']), '  w := %s' % q(P['w']), '  β := %s' % q(P['beta']),
      '  x := %s' % q(P['x']), '  lxU := %s' % q(CTL[0]), '  l1mL := %s' % q(CTL[1])]
IMP = ['import Support.Controls.ControlCertificate', 'import Support.Controls.PublishedControlBridge']
write('Data', IMP, D)
order = ['Data']
for k, ids in enumerate(rowids):
    L = ['theorem %s_ok : ControlCertificate.rowCheck data %s = true := by decide +kernel' % (i, i) for i in ids]
    L += ['theorem rows%d_checked : rows%d.all (ControlCertificate.rowCheck data) = true := by' % (k, k),
          '  simp only [rows%d, List.all_cons, List.all_nil, %s, Bool.and_self, Bool.true_and, Bool.and_true]' % (k, ', '.join(i + '_ok' for i in ids))]
    write('Rows%d' % k, ['import %s.Data' % MOD], L); order.append('Rows%d' % k)
CORNER = '(fun i => data.degrees.all (fun d => ParametricEnvelope.cornerCheck data.w d i))'
LINK = '(fun d => data.tangents.any (fun t => decide (d.slope=t.m ∧ d.intercept=t.c)))'
for k in range(len(clc)):
    write('Corner%d' % k, ['import %s.Data' % MOD], ['theorem corner%d : cl%d.all %s = true := by decide +kernel' % (k, k, CORNER)]); order.append('Corner%d' % k)
write('Link', ['import %s.Data' % MOD], ['theorem link%d : dg%d.all %s = true := by decide +kernel' % (k, k, LINK) for k in range(len(dgc))]); order.append('Link')
write('Geo', ['import %s.Data' % MOD], [
    'theorem geo_chain_deg : chain 0 data.degrees data.μ = true := by decide +kernel',
    'theorem geo_chain_cells : chain 0 data.cells data.cutoff = true := by decide +kernel',
    'theorem geo_deg_nonneg : data.degrees.all (fun d => decide (0 ≤ d.left ∧ 0 ≤ d.right)) = true := by decide +kernel',
    'theorem geo_cells_ok : data.cells.all (fun i => decide (0 ≤ i.left ∧ i.left ≤ i.right)) = true := by decide +kernel',
    'theorem geo_tail : data.degrees.all (fun d => decide (',
    '    (d.slope+data.w-data.w*data.cutoff)*d.left+d.intercept ≤ 0 ∧',
    '    (d.slope+data.w-data.w*data.cutoff)*d.right+d.intercept ≤ 0)) = true := by decide +kernel']); order.append('Geo')
write('Integral', ['import %s.Data' % MOD], [
    'theorem integral_checked :',
    '    ((ControlCertificate.totalExpr data).safe (AnalyticBounds.FixedPointInterval.point 0) &&',
    '      decide (RamseyAnalytic.TangentExpressions.boundHi',
    '        ((ControlCertificate.totalExpr data).bound (AnalyticBounds.FixedPointInterval.point 0)) < -data.margin)) = true := by',
    '  decide +kernel']); order.append('Integral')
write('Power', ['import %s.Data' % MOD], ['theorem power_checked : ControlPower.check data.μ data.w data.x = true := by decide +kernel',
                                             'theorem ctl_ok : ctl.ok = true := by decide +kernel']); order.append('Power')
M = ['theorem geometry_checked : ControlCertificate.GeometryChecks data := by',
     '  refine ⟨by decide +kernel, by decide +kernel, geo_chain_deg, geo_chain_cells, geo_deg_nonneg, geo_cells_ok, ?_, geo_tail⟩',
     '  change (%s).all %s = true' % (CL, CORNER),
     '  simp only [List.all_append, %s, Bool.and_self]' % ', '.join('corner%d' % k for k in range(len(clc))),
     'theorem linkage_checked : data.degrees.all %s = true := by' % LINK,
     '  change (%s).all %s = true' % (DG, LINK),
     '  simp only [List.all_append, %s, Bool.and_self]' % ', '.join('link%d' % k for k in range(len(dgc))),
     'theorem checked : ControlCertificate.Checks data := by',
     '  refine ⟨by decide +kernel, by decide +kernel, ?_, geometry_checked, linkage_checked, integral_checked, power_checked⟩',
     '  change (%s).all (ControlCertificate.rowCheck data) = true' % ' ++ '.join('rows%d' % k for k in range(NR)),
     '  simp only [List.all_append, %s, Bool.and_self]' % ', '.join('rows%d_checked' % k for k in range(NR)),
     'theorem sound : ControlCertificate.Sound data := ControlCertificate.sound data checked',
     '#print axioms sound',
     'theorem cert_ok : ctl.CertOK := by',
     '  apply PublishedControlBridge.certOK_of_parameters data ctl sound',
     '  all_goals decide +kernel',
     '#print axioms cert_ok']
write('Main', ['import %s.' % MOD + m for m in order[1:]], M); order.append('Main')
open(os.path.join(sys.argv[1], 'order%s.txt' % ('' if NAME == 'Root' else '_' + NAME)), 'w').write('\n'.join(order) + '\n')
print('tangents %d, degree cells %d, integral cells %d, float total %.6e; modules %s' % (len(T), len(degs), len(cells), tot, ' '.join(order)))
