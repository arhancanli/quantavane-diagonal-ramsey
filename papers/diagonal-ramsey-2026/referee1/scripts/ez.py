import sys; sys.path.insert(0, '.')
from riv import exp_iv, ln_iv
from fractions import Fraction as F
z1 = F(1248056263241, 10**12); b1 = F(8708913097, 2500000000)
z2 = F(311946616731, 250000000000); b2 = F(278610041, 80000000)
for name, z, b, base in [("z1", z1, b1, F(34835653, 10**7)), ("z2", z2, b2, F(34826256, 10**7))]:
    lo, hi = exp_iv(z)
    print(name, float(z), "e^z in [%.15f, %.15f]" % (float(lo), float(hi)), "claimed ub", float(b), "ub>=hi:", b >= hi, "base>b:", base > b)
zep = F(625145177, 500000000)
print("EP z", float(zep), "z1 gap", float(zep - z1), "z2 gap", float(zep - z2))
print("z2 exact decimal", z2 == F(1247786466924, 10**12))
lo, hi = exp_iv(zep); print("e^zEP", float(lo), float(hi))
