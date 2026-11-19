"""Float (proves nothing): Lemma D shift per control for a ramsey-zbs request list (JSON list of dicts with control, depth,
uses, p, mu, w, beta, x, j, imu, iw). Writes a TSV with the float threshold in a at u_b = 0.03 and 0.92 x it.
Usage: python3 shift_list.py request.json out.tsv [depth]"""
import json
import sys
from fractions import Fraction as Fr

import numpy as np

sys.path.insert(0, __file__.rsplit('/', 1)[0])
import screenD   # noqa: E402

if __name__ == '__main__':
    req = json.load(open(sys.argv[1])); out = sys.argv[2]
    dep = int(sys.argv[3]) if len(sys.argv) > 3 else None
    rows = [r for r in req if dep is None or r['depth'] == dep]
    rows.sort(key=lambda r: (r['depth'], -r['uses']))
    with open(out, 'w') as f:
        f.write('control\tj\timu\tiw\tdepth\tuses\ta_bank\tlemmaD_float_threshold\tshift_0.92\n')
        for r in rows:
            ctl = {k: float(Fr(r[k])) for k in ('p', 'mu', 'w', 'beta', 'x')}
            t = screenD.threshold(ctl, 0.03, nq=50001, it=7)
            f.write('%s\t%d\t%d\t%d\t%d\t%d\t%.12f\t%.3e\t%.3e\n' % (r['control'], r['j'], r['imu'], r['iw'], r['depth'],
                                                                   r['uses'], -np.log(ctl['x']), t, 0.92 * t))
            f.flush()
            print(r['control'], r['depth'], '%.3e' % t, flush=True)
