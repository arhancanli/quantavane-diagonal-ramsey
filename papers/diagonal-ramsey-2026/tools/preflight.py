"""Preflight for the bank checkers A and B (fix of referee 2's two GAPs and NIT 3, 19 Nov 2026).

Run it before code/checkA/runA.py and code/checkB/runB.py; acceptance of a certificate is: preflight OK AND checker A ok
AND checker B ok. It does not modify the frozen Lemma D checkers (their SHA-256 pins stay valid); it adds, at run time:
  (1) the pin of the frozen Lemma D code: research/tier2/ramsey-zbs/code/lemmaD/MANIFEST.sha256 must have the
      hard-coded SHA-256 below and list exactly 31 files, each with its listed SHA-256; checkD_A.py, checkD_B.py, ivA.py,
      genD.py and tamper_D.py must be listed with the hard-coded hashes below; and checkA/ivA.py (the module that
      checkD_A's `import ivA` resolves to inside checker A's process) must have the frozen ivA's hash;
  (2) for every control: exactly one of 'cert' (Lemma C) or 'lemmaD' (Lemma D), and no 'control' key inside 'lemmaD'
      (the bank control's own p, mu, w, beta, x are the ones checked);
  (4) Theorem 5.7's proviso: every source pair has eps_h and eta_h > 8/10^15 > 2 h(10^-16) (exact rationals);
  (3) for every Lemma D block, the parts of CERT_DESIGN 4c that checkD_A and checkD_B enforce only through unrelated
      exceptions: K4's N >= 2 (N = len(qgrid) - 1) and K6's 1 <= jA0 <= N - 1 with jA0 an integer; and the tree format
      of 4c: every node is "L" or a list [axis, child1, child2] with axis exactly "P" or "p" (checkD_A reads any axis
      other than "P" as "p"); trees deeper than 200 are refused (a conservative cap, not part of 4c).
The per-box conditions of 7.4 (for example jA = N) are computed inside the Lemma D checkers and are not preflight
checks. Recommended invocation of every checker: python3 -I -X pycache_prefix=<empty directory> (so that no stale
bytecode file next to a pinned .py can be loaded).
usage: python3 -I preflight.py <certificate.json> [more.json ...]
       A file with a top-level 'controls' list is a bank certificate; a file with 'qgrid' is a single Lemma D certificate.
Exit status 0 and "PREFLIGHT OK" iff every check passes. Standard library only; no floating point is used."""
import sys, os, json, hashlib
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
LANE = os.path.join(REPO, 'research', 'tier2', 'ramsey-zbs')
LEMMAD = os.path.join(LANE, 'code', 'lemmaD')

# Hard-coded pins (re-referee G1, 19 Nov): the manifest on disk is itself pinned, the five code files must be listed in
# it with these exact hashes, and checker A's ivA.py must have the frozen ivA's hash. This file is in turn pinned by
# papers/diagonal-ramsey-2026/MANIFEST.sha256 of the commit that carries it.
MANIFEST_SHA = '22742abbba6f6b6395ae18c0935f0285d3af557423db93d3d51f1d2d348ce46b'
CODE_PINS = {
    'checkD_A.py': '3600766b7c768a8047e34a02b7299515c6f1c5c6ddeaa994e10b84f1ef31b9bc',
    'checkD_B.py': '3a748ce26085caaa15a681b12585ae5601ad3f951a5884bb67e98494edf4723a',
    'ivA.py': 'f6fe4408e2899fcfb39eab8ec2a4cba6f05ef6c2ba6855b97644a252b4579ee8',
    'genD.py': 'aa7d6bc346c68372621ede22b2dbf1e2a63ded29f4b86b360f7bcd20fa179aee',
    'tamper_D.py': '388de79d0207091291d887a85783e118c8cff7ed30dd5df78f66f337bddcd642',
}
MANIFEST_LINES = 31
TREE_DEPTH_CAP = 200   # conservative: a deeper tree is refused although 7.5's format allows it


class Refused(Exception):
    pass


def need(ok, why):
    if not ok:
        raise Refused(why)


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


# (4) Theorem 5.7's proviso (SELF_CONTAINED Section 16, P3.3): min over sources of min(eps_h, eta_h) > 2 h(10^-16).
# Certified bound: h(a) <= a (1 + a) + a log(1/a) for 0 < a <= 1/e ((1+a) log(1+a) <= (1+a) a), log(10^16) = 16 log 10,
# and log 10 < 231/100 because sum_{k<=40} (231/100)^k/k! (a lower bound of e^{2.31}) exceeds 10 (checked exactly below).
# So 2 h(10^-16) < 2 * 10^-16 (1 + 10^-16 + 16 * 231/100) = 7.5121...e-15 + ... < 8/10^15 = PROVISO.
PROVISO = Fraction(8, 10 ** 15)


def proviso_bound_ok():
    x = Fraction(231, 100); term = Fraction(1); tot = Fraction(1)
    for k in range(1, 41):
        term = term * x / k; tot += term
    assert tot > 10, 'e^{2.31} > 10'
    a = Fraction(1, 10 ** 16)
    return 2 * (a * (1 + a) + a * 16 * x) < PROVISO


def check_sources(c):
    srcs = c.get('sources', [])
    for i, s in enumerate(srcs):
        e, t = Fraction(s['eps']), Fraction(s['eta'])
        need(e > PROVISO and t > PROVISO, 'source %d: eps = %s, eta = %s; Theorem 5.7 proviso needs both > 8/10^15' % (i, e, t))
    return len(srcs), (min(min(Fraction(s['eps']), Fraction(s['eta'])) for s in srcs) if srcs else None)


def check_pins():
    man = os.path.join(LEMMAD, 'MANIFEST.sha256')
    need(sha(man) == MANIFEST_SHA, 'code/lemmaD/MANIFEST.sha256 is not the pinned manifest')
    listed = {}
    with open(man) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            h, name = line.split(None, 1)
            name = name.lstrip('*')
            need(name not in listed, 'MANIFEST.sha256 lists %s twice' % name)
            need(sha(os.path.join(LEMMAD, name)) == h, 'frozen Lemma D file changed: %s' % name)
            listed[name] = h
    need(len(listed) == MANIFEST_LINES, 'MANIFEST.sha256 must list %d files' % MANIFEST_LINES)
    for name, h in CODE_PINS.items():
        need(listed.get(name) == h, 'pinned code file %s missing from the manifest or with another hash' % name)
    a = os.path.join(LANE, 'code', 'checkA', 'ivA.py')
    need(sha(a) == CODE_PINS['ivA.py'], 'checkA/ivA.py differs from the frozen lemmaD/ivA.py')
    return len(listed)


def check_tree(t, depth=0):
    need(depth <= TREE_DEPTH_CAP, 'tree deeper than %d (conservative cap)' % TREE_DEPTH_CAP)
    if t == 'L':
        return 1
    need(isinstance(t, list) and len(t) == 3, 'tree node is neither "L" nor [axis, child1, child2]')
    need(t[0] in ('P', 'p'), 'tree axis must be exactly "P" or "p", got %r' % (t[0],))
    return check_tree(t[1], depth + 1) + check_tree(t[2], depth + 1)


def check_lemmad(d, where):
    q = d.get('qgrid')
    need(isinstance(q, list), '%s: qgrid missing' % where)
    N = len(q) - 1
    need(N >= 2, '%s: K4 needs N >= 2, got N = %d' % (where, N))
    j = d.get('jA0')
    need(isinstance(j, int) and not isinstance(j, bool), '%s: jA0 must be an integer' % where)
    need(1 <= j <= N - 1, '%s: K6 needs 1 <= jA0 <= N - 1, got jA0 = %r, N = %d' % (where, j, N))
    need('tree' in d, '%s: tree missing' % where)
    return check_tree(d['tree'])


def check_file(path):
    with open(path) as f:
        c = json.load(f)
    if isinstance(c, dict) and 'controls' in c:
        nD = 0
        for i, k in enumerate(c['controls']):
            kinds = ('cert' in k) + ('lemmaD' in k)
            need(kinds == 1, 'control %d: exactly one of cert / lemmaD required' % i)
            if 'lemmaD' in k:
                need(isinstance(k['lemmaD'], dict) and 'control' not in k['lemmaD'],
                     'control %d: lemmaD must not carry its own control' % i)
                check_lemmad(k['lemmaD'], 'control %d' % i)
                nD += 1
        need(proviso_bound_ok(), '2 h(10^-16) < 8/10^15')
        ns, mn = check_sources(c)
        return ('bank certificate: %d controls, %d of kind Lemma D; %d sources, min(eps, eta) = %s > 8/10^15 '
                '(Theorem 5.7 proviso)' % (len(c['controls']), nD, ns, mn))
    need(isinstance(c, dict) and 'qgrid' in c, 'neither a bank certificate nor a Lemma D certificate')
    leaves = check_lemmad(c, os.path.basename(path))
    return 'Lemma D certificate: N = %d, jA0 = %d, %d leaves' % (len(c['qgrid']) - 1, c['jA0'], leaves)


def main(paths):
    try:
        n = check_pins()
        print('pins: %d frozen Lemma D files match MANIFEST.sha256; checkA/ivA.py == lemmaD/ivA.py' % n)
        for p in paths:
            print('%s: %s' % (p, check_file(p)))
    except Refused as e:
        print('PREFLIGHT REFUSED: %s' % e)
        return 1
    print('PREFLIGHT OK')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
