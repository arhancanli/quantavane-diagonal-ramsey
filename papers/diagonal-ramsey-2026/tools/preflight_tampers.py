"""Red and green controls for tools/preflight.py on one Lemma D certificate.
usage: python3 -I preflight_tampers.py <lemmaD certificate.json> <scratch dir>
The untouched certificate must be ACCEPTED; each tamper (referee 2, findings 1 and 3) must be REFUSED by the preflight."""
import sys, os, json, copy, subprocess

src, out = sys.argv[1:3]
os.makedirs(out, exist_ok=True)
base = json.load(open(src))
here = os.path.dirname(os.path.abspath(__file__))


def tampers():
    yield 'original', base, True
    N = len(base['qgrid']) - 1
    for j in (0, -1, N, N + 1):
        d = copy.deepcopy(base); d['jA0'] = j
        yield 'jA0=%d' % j, d, False
    d = copy.deepcopy(base); d['jA0'] = str(base['jA0'])
    yield 'jA0 as string', d, False
    d = copy.deepcopy(base); d['qgrid'] = [base['qgrid'][0], base['qgrid'][-1]]; d['jA0'] = 1
    yield 'N=1', d, False
    if base['tree'] != 'L':
        d = copy.deepcopy(base); d['tree'][0] = 'x'
        yield 'root axis x', d, False
        d = copy.deepcopy(base); d['tree'] = d['tree'][:2]
        yield 'root node with one child', d, False


ok = True
for name, d, want in tampers():
    fn = os.path.join(out, 'pf_%s.json' % name.replace(' ', '_').replace('=', ''))
    json.dump(d, open(fn, 'w'))
    r = subprocess.run([sys.executable, '-I', os.path.join(here, 'preflight.py'), fn], capture_output=True, text=True)
    got = r.returncode == 0
    last = (r.stdout.strip().splitlines() or ['?'])[-1]
    print('%-26s %s  (expected %s)  | %s' % (name, 'ACCEPTED' if got else 'REFUSED', 'ACCEPT' if want else 'REFUSE', last))
    ok &= (got == want)
    os.remove(fn)
print('ALL PREFLIGHT CONTROLS AS EXPECTED' if ok else 'SOME PREFLIGHT CONTROL NOT AS EXPECTED')
sys.exit(0 if ok else 1)
