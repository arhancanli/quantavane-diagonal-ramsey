"""Parse ZBS raw pieces (D*.lean at c2875f33) into checker JSON (used only for green controls of the checkers)."""
import re, sys, json
def decode(s):
    s = re.sub(r'\(FQ\.mk \(\.ofNat \(nat_lit (\d+)\)\) \(nat_lit (\d+)\)\)', lambda m: '%s/%d' % (m.group(1), int(m.group(2)) + 1), s)
    return re.sub(r'\(FQ\.mk \(\.negSucc \(nat_lit (\d+)\)\) \(nat_lit (\d+)\)\)', lambda m: '-%d/%d' % (int(m.group(1)) + 1, int(m.group(2)) + 1), s)
def tok(s):
    return re.findall(r'\.inl \d+|\.inr \d+|-?\d+/\d+|-?\d+|\[|\]|⟨|⟩', s)
def parse_term(ts, i):
    """returns (value, i): lists [..], tuples ⟨..⟩, numbers/refs."""
    t = ts[i]
    if t in ('[', '⟨'):
        close = ']' if t == '[' else '⟩'; out = []; i += 1
        while ts[i] != close:
            v, i = parse_term(ts, i); out.append(v)
        return out, i + 1
    if t.startswith('.inl'): return ('zr', int(t.split()[1])), i + 1
    if t.startswith('.inr'): return ('zc', int(t.split()[1])), i + 1
    return t, i + 1
def pieces(path):
    s = decode(open(path).read()); out = {}
    for m in re.finditer(r'^def (rp\d+_\d+) : RawF [^:]*:= \.(leaf|route) (.*)$', s, re.M):
        ts = tok(m.group(3)); v, _ = parse_term(ts, 0)
        if m.group(2) == 'leaf':
            c, sg, xi, nu, ys, aU, bU, mg, lo, hi, bp = v
            d = {'kind': 'leaf', 'c': int(c), 'src': ('z', int(sg)), 'xi': xi, 'nu': nu, 'ys': ys, 'aU': aU, 'bU': bU,
                 'margin': mg, 'lo': lo, 'hi': hi, 'bp': bp}
        else:
            (c, sg, xi, nu, ys, aU, bU), us, ds, calls, g0, hm, mg, lo, hi, bp = v
            d = {'kind': 'route', 't': {'c': int(c), 'src': ('z', int(sg)), 'xi': xi, 'nu': nu, 'ys': ys, 'aU': aU, 'bU': bU},
                 'us': us, 'ds': ds, 'calls': [{'ch': ch, 'z': z, 'bp': cbp} for ch, z, cbp in calls], 'g0': g0, 'hm': hm,
                 'margin': mg, 'lo': lo, 'hi': hi, 'bp': bp}
        out[m.group(1)] = d
    return out
