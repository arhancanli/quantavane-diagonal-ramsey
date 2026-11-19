"""Extract every ProfD/ProfF literal (p, xs, ys) from EP Lean files (exploration input). usage: files... -> stdout json"""
import re, sys, json
def dec(s):
    s = re.sub(r'\(FQ\.mk \(\.ofNat \(nat_lit (\d+)\)\) \(nat_lit (\d+)\)\)', lambda m: '%s/%d' % (m.group(1), int(m.group(2)) + 1), s)
    s = re.sub(r'⟨(\d+), (\d+)⟩', lambda m: '%s/%d' % (m.group(1), int(m.group(2)) + 1), s)   # FQ anonymous ⟨n, d⟩
    return s
out = []
for fn in sys.argv[1:]:
    s = dec(open(fn).read())
    for m in re.finditer(r'def (\S+) : Prof[DF] :=\s*⟨([^⟩]*)⟩', s):
        body = m.group(2)
        parts = re.match(r'\s*([^,\[]+),\s*\[([^\]]*)\],\s*\[([^\]]*)\]', body)
        if not parts: continue
        p = parts.group(1).strip(); xs = [t.strip() for t in parts.group(2).split(',')]; ys = [t.strip() for t in parts.group(3).split(',')]
        if len(xs) == len(ys) and len(xs) >= 2 and re.match(r'^-?\d+(/\d+)?$', p):
            out.append({'name': fn.split('/')[-1] + ':' + m.group(1), 'p': p, 'xs': xs, 'ys': ys})
json.dump(out, sys.stdout)
