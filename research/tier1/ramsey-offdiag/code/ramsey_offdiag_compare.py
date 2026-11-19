"""Float comparison (exploration only; proves nothing) of off-diagonal exponents E(g), log R(k, g k) <= E(g) k + o(k).

Published baseline (made as LOW as possible, so that a gain against it is conservative):
  ZBS P0r12 (2,713 sources, 1,902 raw + 1,003 closed profiles)
  + EvolvingPrograms 959f46b0: chosen source (A_s, B_s), auxiliary sources (A606, B606), (A546, B546),
    every profile literal in Append.lean, Source/Profiles.lean, Source/HullProfiles.lean, L4_Routes.lean (205),
    diagonal z_EP = 625145177/500000000 (R(k, g k) <= R(k, k)).
Ours: zbs objects + certificate objects (certCD3 or certK3), i.e. the content of certCD3-full / certK3-full.
Bounds per bank: src(g) = min_h min(A_h + g B_h, B_h + g A_h); pair(g) = min over claims R, S with
p_R + p_S <= 1 of max(L_R(g), g L_S(1/g)); then the running minimum from the right (monotonicity in l).
usage: ramsey_offdiag_compare.py zbs_bank.json ep_extra.json cert.json label out.tsv [extra g list, e.g. 1/3,2/3]
"""
import sys, json, bisect
from fractions import Fraction as Fr

EP_SOURCES = [  # EvolvingPrograms/DiagonalRamsey @ 959f46b06e
    ('1086180879838687/1000000000000000',
     '11640399543290787172985714354555752537/36367644171000000000000000000000000000'),  # L1_Parameters sourceA/B
    ('523723367013/500000000000',
     '659232501933912836000511047884943/1949512210000000000000000000000000'),  # Candidate6330Prefix control A/B
    ('2956367223781/1000000000000', '53408694539/1000000000000'),  # Candidate600Prefix control A/B
]
Z_EP = 625145177 / 500000000


def fl(s):
    return float(Fr(s))


def profs(lst):
    # EP's rootDatum writes its heights as the symbol rawExponent = 625145177/500000000 (L1_Parameters.lean:32)
    lst = [dict(r, ys=['625145177/500000000' if y == 'rawExponent' else y for y in r['ys']]) for r in lst]
    return [(fl(r['p']), [fl(x) for x in r['xs']], [fl(y) for y in r['ys']]) for r in lst]


def Lv(xs, ys, t):
    if t < xs[0] - 1e-13 or t > xs[-1] + 1e-13:
        return None
    i = min(max(bisect.bisect_right(xs, t) - 1, 0), len(xs) - 2)
    a, b = xs[i], xs[i + 1]
    return ys[i] + (ys[i + 1] - ys[i]) * (t - a) / (b - a)


def src_bound(AB, g):
    return min(min(A + g * B, B + g * A) for A, B in AB)


def pair_bound(P, g):
    lr = sorted((p, v) for p, xs, ys in P for v in [Lv(xs, ys, g)] if v is not None)
    ls = sorted((p, g * v) for p, xs, ys in P for v in [Lv(xs, ys, 1.0 / g)] if v is not None)
    if not lr or not ls:
        return float('inf')
    ps, vs, m = [], [], float('inf')
    for p, v in ls:
        m = min(m, v); ps.append(p); vs.append(m)
    best, m = float('inf'), float('inf')
    for p, v in lr:
        m = min(m, v)
        j = bisect.bisect_right(ps, 1.0 - p + 1e-12) - 1
        if j >= 0:
            best = min(best, max(m, vs[j]))
    return best


def runmin_right(vals):
    out, m = [0.0] * len(vals), float('inf')
    for i in range(len(vals) - 1, -1, -1):
        m = min(m, vals[i]); out[i] = m
    return out


if __name__ == '__main__':
    zbs_path, ep_path, cert_path, label, out = sys.argv[1:6]
    zb = json.load(open(zbs_path))
    zAB = [(fl(a), fl(b)) for a, b in zip(zb['A'], zb['B'])]
    zP = profs(zb['raw']) + profs(zb['closed'])
    epP = profs(json.load(open(ep_path)))
    epAB = [(fl(a), fl(b)) for a, b in EP_SOURCES]
    cd = json.load(open(cert_path))
    nAB = [(fl(s['A']), fl(s['B'])) for s in cd['sources']]
    nP = profs(cd['raw']) + profs(cd['closed'])
    del cd
    gs = [round(0.01 * i, 4) for i in range(5, 101)]
    if len(sys.argv) > 6:
        gs = sorted(set(gs + [float(Fr(x)) for x in sys.argv[6].split(',')]))
    pub, ours, rows = [], [], []
    for g in gs:
        pub_src = src_bound(zAB + epAB, g); pub_pair = pair_bound(zP + epP, g)
        our_src = src_bound(zAB + nAB, g); our_pair = pair_bound(zP + nP, g)
        pub.append(min(pub_src, pub_pair, Z_EP)); ours.append(min(our_src, our_pair))
        rows.append((g, pub_src, pub_pair, our_src, our_pair))
    pubm, oursm = runmin_right(pub), runmin_right(ours)
    hdr = 'g\tpub_src\tpub_pair\tpub_best\tours_src\tours_pair\tours_best\tgain'
    lines = [hdr]
    for (g, a, b, c, d), P, O in zip(rows, pubm, oursm):
        lines.append('%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%.6f\t%+.6f' % (g, a, b, P, c, d, O, P - O))
    open(out, 'w').write('\n'.join(lines) + '\n')
    print(label); print('\n'.join(lines))
