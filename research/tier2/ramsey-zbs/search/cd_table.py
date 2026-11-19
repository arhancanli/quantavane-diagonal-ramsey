"""Second claim (assuming Theorem A), bank form: lower the control table's a at the controls certified by Lemma D.
usage: python3 cd_table.py ctltable2.npz cdmap.json out.npz
cdmap.json: list of {"j": generator j, "imu": .., "iw": .., "x": "n/d" (x_D of the stored certificate), "cert": path}.
The generator's j is the table index + 1 (gen2 prepends an empty density row).  The new entry is -log(x_D) + 1e-12,
which is >= the certificate's a, so the materialised bank is never worse than the generator's model."""
import sys, json, math
import numpy as np
from fractions import Fraction as Fr

t = dict(np.load(sys.argv[1])); m = json.load(open(sys.argv[2]))
a = t['a'].copy()
for e in m:
    i = (int(e['j']) - 1, int(e['imu']), int(e['iw']))
    new = -math.log(float(Fr(e['x']))) + 1e-12
    assert new < a[i], ('not a gain', e, a[i], new)
    print('j %d imu %d iw %d: a %.12f -> %.12f (%.3e)' % (e['j'], e['imu'], e['iw'], a[i], new, new - a[i]))
    a[i] = new
t['a'] = a
np.savez(sys.argv[3], **t)
