"""Make the red-control (tampered) certificates. usage: ramsey_offdiag_red_make.py bank_full.json cert.json outdir"""
import sys, json, os, copy
from fractions import Fraction as F
bank = json.load(open(sys.argv[1])); cert = json.load(open(sys.argv[2])); od = sys.argv[3]
os.makedirs(od, exist_ok=True)
cells = cert['cells']
def find(g):
    return next(i for i, c in enumerate(cells) if F(c['lo']) <= F(g) < F(c['hi']))
def save(name, c):
    json.dump(c, open(os.path.join(od, name + '.json'), 'w'))
i9 = find('9/10'); i6 = find('3/5'); i0 = 0
c = copy.deepcopy(cert); c['cells'][i9]['v_hi'] = str(F(c['cells'][i9]['v_hi']) - F(1, 10**9)); save('r1_pair_vhi_minus_1e-9', c)
c = copy.deepcopy(cert); c['cells'][i0]['v_lo'] = str(F(c['cells'][i0]['v_lo']) - F(1, 10**9)); save('r2_src_vlo_minus_1e-9', c)
# r3: S replaced by a claim whose density makes p_R + p_S > 1 but whose interval still contains [1/hi, 1/lo]
c = copy.deepcopy(cert); cc = c['cells'][i6]; pR = F(bank[cc['R'][0]][cc['R'][1]]['p']); lo, hi = F(cc['lo']), F(cc['hi'])
cand = [j for j, r in enumerate(bank['raw']) if F(r['p']) + pR > 1 and F(r['xs'][0]) <= 1 / hi and 1 / lo <= F(r['xs'][-1])]
cc['S'] = ['raw', cand[0]]; save('r3_density_sum_above_1', c)
c = copy.deepcopy(cert); c['cells'][100]['lo'] = str(F(c['cells'][100]['lo']) + F(1, 10**12)); save('r4_tiling_gap', c)
c = copy.deepcopy(cert); c['bank_sha256'] = '0' * 64; save('r5_wrong_bank_sha', c)
# r6: R replaced by a claim of the same or lower density whose interval misses [lo, hi]
c = copy.deepcopy(cert); cc = c['cells'][i9]; lo, hi = F(cc['lo']), F(cc['hi']); pR = F(bank[cc['R'][0]][cc['R'][1]]['p'])
cand = [j for j, r in enumerate(bank['raw']) if F(r['p']) <= pR and not (F(r['xs'][0]) <= lo and hi <= F(r['xs'][-1]))]
cc['R'] = ['raw', cand[0]]; save('r6_R_interval_misses_cell', c)
c = copy.deepcopy(cert); c['cells'][i9]['R'] = [c['cells'][i9]['R'][0], str(c['cells'][i9]['R'][1])]; save('r7_string_index', c)
c = copy.deepcopy(cert); c['cells'][i0]['orient'] = 'AB' if c['cells'][i0]['orient'] == 'BA' else 'BA'; save('r8_src_orientation_swapped', c)
c = copy.deepcopy(cert); del c['cells'][-1]; save('r9_last_cell_missing', c)
c = copy.deepcopy(cert); c['cells'][i9]['kind'] = 'leaf'; save('r10_unknown_kind', c)
c = copy.deepcopy(cert); c['g_lo'] = '1/4'; save('r11_g_lo_changed', c)
# r12 (referee 20 Nov, finding 8): a pair cell below 1/5 whose S no longer covers [1/hi, 1/lo] (inside [5, 8])
low = [i for i, x in enumerate(cells) if x['kind'] == 'pair' and F(x['hi']) < F(1, 5)]
if low:
    c = copy.deepcopy(cert); cc = c['cells'][low[len(low) // 2]]; lo, hi = F(cc['lo']), F(cc['hi'])
    pS = F(bank[cc['S'][0]][cc['S'][1]]['p'])
    cand = [j for j, r in enumerate(bank['raw']) if F(r['p']) <= pS and F(r['xs'][0]) <= 1 / hi and F(r['xs'][-1]) < 1 / lo]
    cc['S'] = ['raw', cand[0]]; save('r12_S_interval_short_below_1_5', c)
print('made', sorted(os.listdir(od)))
