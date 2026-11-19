# float sanity check of the D7 difference formulas (not rigorous)
import math
w, ub, pb = 0.43, 0.03, 1.2
qs = [0.05, 0.1, 0.2, 0.3, 0.4]; hs = [0.02, 0.05, 0.08, 0.1, 0.11]
Psi = lambda y: max(h - q*(w + y) for q, h in zip(qs, hs))       # convex, nonincreasing, slopes -q
s0 = 0.9
pos = lambda y: max(y - s0, 0.0)
g = lambda u: -w*u*math.log(u); phis = lambda u: -w*(1 + math.log(u))
def bisect(f, a, b):
    for _ in range(200):
        m = (a+b)/2
        if f(m) > 0: b = m
        else: a = m
    return (a+b)/2
def integ(f, a, b, n=200000):
    h = (b-a)/n; return sum(f(a+(i+0.5)*h) for i in range(n))*h
def u1(Pb): return bisect(lambda u: g(u) - (Pb - pb*(ub-u)), 1e-12, ub)
def IL(Pb): a = u1(Pb); return integ(lambda u: Psi(phis(u)), 1e-12, a) + (ub-a)*Psi(pb)
def K(Pb):  a = u1(Pb); return integ(lambda u: pos(phis(u)), 1e-12, a) + (ub-a)*pos(pb)
Pb = 0.5*(pb*ub + g(ub)); d = 1e-5
a = u1(Pb)
fdIL = (IL(Pb+d) - IL(Pb-d))/(2*d); fdK = (K(Pb+d) - K(Pb-d))/(2*d)
print('u1 =', a, 'phi_s(u1) =', phis(a), '>= p_b =', pb)
print('dIL/dPhi_b: finite diff %.6f   lab formula (no minus) %.6f   referee-1 formula (minus) %.6f' %
      (fdIL, (Psi(phis(a)) - Psi(pb))/(phis(a) - pb), -(Psi(phis(a)) - Psi(pb))/(phis(a) - pb)))
print('dK/dPhi_b: finite diff %.6f   formula %.6f' % (fdK, (pos(phis(a)) - pos(pb))/(phis(a) - pb)))
# right side
pr = 0.5; Hh = lambda y: max(h - q*(w + y) for q, h in zip(qs, hs))
def u2(Pb): return bisect(lambda u: Pb + pr*(u-ub) - g(u), ub, 1.0)
def IR2(Pb): b = u2(Pb); return (b-ub)*Hh(pr) + integ(lambda u: Hh(phis(u)), b, 1.0)
Pb2 = 0.02
b = u2(Pb2)
fd = (IR2(Pb2+d) - IR2(Pb2-d))/(2*d)
print('u2 =', b, 'phi_s(u2) =', phis(b), '<= p_b =', pr)
print('dIR2/dPhi_b: finite diff %.6f   formula %.6f' % (fd, (Hh(phis(b)) - Hh(pr))/(pr - phis(b))))
