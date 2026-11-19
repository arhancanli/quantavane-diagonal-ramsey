"""Full parser of ZBS's exported bank P0r12 (github.com/w2ll2am/diagonal-ramsey @ c2875f33), written for the cone step
of the unconditional plan (19 Nov 2026).  Written separately from research/tier2/ramsey-zbs/search/parse_zbs.py and from
code/zbs_pieces.py (no code shared): a tokenizer and recursive-descent parser for the Lean term syntax of the data
files, then a typed decoder for each structure of Lemmas/DiagRamsey_V5Fast.lean.

Lean syntax handled (the only syntax the data files use; anything else is refused):
  numerals, identifiers (.leaf, FQ.mk, nat_lit, .inl, rp0_0, ...), applications `f a b`, parentheses, tuples `(a, b)`,
  anonymous constructors `⟨a, b, ...⟩` and lists `[a, b, ...]`.
Semantics decoded (V5Fast.lean): FQ.mk n d = n/(d+1); `.ofNat (nat_lit n)` = n, `.negSucc (nat_lit n)` = -(n+1);
  a numeral of type Fin N must be < N (Lean would reduce it mod N; we refuse instead); `.inl i` = raw profile i,
  `.inr i` = closed profile i; structures by positional fields:
  CtrlF ⟨p, μ, w, β, x, lxU, l1mL⟩; ProfF ⟨p, xs, ys⟩;
  LeafF ⟨c, σ, ξ, ν, ys, aU, bU, margin, lo, hi, bp⟩; TermF ⟨c, σ, ξ, ν, ys, aU, bU⟩; CallF ⟨ch, z, bp⟩;
  RouteF ⟨t, us, ds, calls, g0, hm, margin, lo, hi, bp⟩; ClosedPF .rawDensity R lo hi bp | .complRaw R S lo hi bp;
  SrcCellF .grounded k lo hi | .pair PR PB lo hi bp; SourceF ⟨Lo, Hi, ε, η, kL, kR, cells⟩.
The index structure is read from the files, not assumed from names: T.lean (ctlL, rawL, rawMinL, clL, clMinL, AL, BL,
lines and the accessor defs A, B, ctl, raw, rawMin, closed, closedMin, pd, i0, whose exact text is checked) and Data.lean
(rawPL, clPL, srcL and the `bank` structure, whose exact text is checked).  The theorem files Raw*.lean, Closed*.lean,
Src*.lean and Bank.lean are read only to check that every piece and every profile/source carries ZBS's kernel theorem
for the index it is used at.

Every input file is checked against its git blob SHA-1 in filelist.txt (download listing, c2875f33 tree).
Output (JSON, every rational a reduced string "n/d"): controls, raw, closed, sources, lines in the certificate format of
papers/diagonal-ramsey-2026/SELF_CONTAINED.md Section 4, with references ["zr", i] / ["zc", i] / ["z", h] to ZBS objects
and control indices into ZBS's controls; plus counts.  With a third argument, cross-checks against zbs_bank.json.
usage: python3 -I parse_zbs_full.py <zbs_c2875f33 dir> <out.json> [zbs_bank.json]"""
import sys, os, re, json, hashlib, time
from fractions import Fraction as Fr

NR, NC, NCTL, NSRC, NLINES = 1902, 1003, 918, 2713, 1128
NS = 'DiagRamsey.V5.P06_P0r12'
SUBDIR = os.path.join('Solutions', 'P06', 'P0r12')


class ParseError(Exception):
    pass


def need(c, msg):
    if not c:
        raise ParseError(msg)


# ---------------------------------------------------------------- integrity
def blob_sha1(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def load_listing(root):
    lst = {}
    with open(os.path.join(root, 'filelist.txt')) as f:
        for line in f:
            line = line.strip()
            if line:
                path, h = line.rsplit(' ', 1)
                need(path not in lst, 'filelist.txt lists %s twice' % path)
                lst[path] = h
    return lst


def read_checked(root, rel, listing, seen):
    need(rel in listing, 'not in filelist.txt: %s' % rel)
    with open(os.path.join(root, rel), 'rb') as f:
        data = f.read()
    need(blob_sha1(data) == listing[rel], 'git blob SHA-1 mismatch: %s' % rel)
    seen[rel] = listing[rel]
    return data.decode('utf-8')


# ---------------------------------------------------------------- tokenizer and parser
TOKEN = re.compile(r"[⟨⟩()\[\],]|[0-9]+|[A-Za-z_.][A-Za-z0-9_.']*|\S")
STOP = frozenset([',', ')', ']', '⟩'])


class Parser:
    """recursive descent over the token list.  Nodes: int, ('id', s), ('app', head, [args]), ('tuple', [..]),
    ('anon', [..]) for ⟨..⟩, ('list', [..])."""

    def __init__(self, text):
        self.t = TOKEN.findall(text)
        self.n = len(self.t)
        self.i = 0

    def done(self):
        need(self.i == self.n, 'trailing tokens: %r' % self.t[self.i:self.i + 5])

    def expr(self):
        t = self.t
        items = []
        while self.i < self.n and t[self.i] not in STOP:
            items.append(self.primary())
        need(items, 'empty expression at token %d' % self.i)
        if len(items) == 1:
            return items[0]
        need(isinstance(items[0], tuple) and items[0][0] == 'id', 'application head is not an identifier')
        return ('app', items[0][1], items[1:])

    def seq(self, close):
        out = []
        t = self.t
        if t[self.i] == close:
            self.i += 1
            return out
        while True:
            out.append(self.expr())
            tok = t[self.i]
            self.i += 1
            if tok == close:
                return out
            need(tok == ',', 'expected , or %s, got %r' % (close, tok))

    def primary(self):
        tok = self.t[self.i]
        self.i += 1
        if tok == '(':
            e = self.expr()
            if self.t[self.i] == ',':
                items = [e]
                while self.t[self.i] == ',':
                    self.i += 1
                    items.append(self.expr())
                e = ('tuple', items)
            need(self.t[self.i] == ')', 'expected )')
            self.i += 1
            return e
        if tok == '⟨':
            return ('anon', self.seq('⟩'))
        if tok == '[':
            return ('list', self.seq(']'))
        if tok.isdigit():
            return int(tok)
        if tok[0].isalpha() or tok[0] in '_.':
            return ('id', tok)
        raise ParseError('unexpected token %r' % tok)


def parse_term(text):
    p = Parser(text)
    e = p.expr()
    p.done()
    return e


# ---------------------------------------------------------------- typed decoding
def S(x):
    return '%d/%d' % (x.numerator, x.denominator)


def natlit(e):
    need(isinstance(e, tuple) and e[0] == 'app' and e[1] == 'nat_lit' and len(e[2]) == 1 and isinstance(e[2][0], int),
         'nat_lit expected')
    return e[2][0]


def fq(e):
    """FQ.mk (.ofNat (nat_lit n) | .negSucc (nat_lit n)) (nat_lit d) -> Fraction n / (d + 1)."""
    need(isinstance(e, tuple) and e[0] == 'app' and e[1] == 'FQ.mk' and len(e[2]) == 2, 'FQ.mk expected')
    num, den = e[2]
    need(isinstance(num, tuple) and num[0] == 'app' and len(num[2]) == 1, 'FQ numerator')
    n = natlit(num[2][0])
    if num[1] in ('.ofNat', 'Int.ofNat'):
        v = n
    elif num[1] in ('.negSucc', 'Int.negSucc'):
        v = -(n + 1)
    else:
        raise ParseError('FQ numerator constructor %r' % (num[1],))
    return Fr(v, natlit(den) + 1)


def fqs(e):
    return S(fq(e))


def fqlist(e):
    need(isinstance(e, tuple) and e[0] == 'list', 'list of FQ expected')
    return [fqs(x) for x in e[1]]


def fin(e, bound, what):
    need(isinstance(e, int), '%s: numeral expected' % what)
    need(0 <= e < bound, '%s: numeral %d not below Fin bound %d' % (what, e, bound))
    return e


def nat(e, what):
    need(isinstance(e, int), '%s: numeral expected' % what)
    return e


def sumref(e, what):
    need(isinstance(e, tuple) and e[0] == 'app' and len(e[2]) == 1, '%s: .inl/.inr expected' % what)
    if e[1] in ('.inl', 'Sum.inl'):
        return ['zr', fin(e[2][0], NR, what)]
    if e[1] in ('.inr', 'Sum.inr'):
        return ['zc', fin(e[2][0], NC, what)]
    raise ParseError('%s: constructor %r' % (what, e[1]))


def anon(e, nfields, what):
    need(isinstance(e, tuple) and e[0] == 'anon' and len(e[1]) == nfields,
         '%s: anonymous constructor with %d fields expected' % (what, nfields))
    return e[1]


def ctor(e, names):
    need(isinstance(e, tuple) and e[0] == 'app' and e[1] in names, 'constructor %s expected' % '/'.join(names))
    return e[1], e[2]


def dec_ctrl(e):
    f = anon(e, 7, 'CtrlF')
    return dict(zip(('p', 'mu', 'w', 'beta', 'x', 'lxU', 'l1mL'), (fqs(x) for x in f)))


def dec_prof(e):
    p, xs, ys = anon(e, 3, 'ProfF')
    return {'p': fqs(p), 'xs': fqlist(xs), 'ys': fqlist(ys)}


def dec_term(f, what):
    c, sg, xi, nu, ys, aU, bU = f
    return {'c': fin(c, NCTL, what + '.c'), 'src': ['z', fin(sg, NSRC, what + '.sigma')], 'xi': fqs(xi), 'nu': fqs(nu),
            'ys': fqs(ys), 'aU': fqs(aU), 'bU': fqs(bU)}


def dec_raw_piece(e, what):
    k, args = ctor(e, ('.leaf', '.route', 'RawF.leaf', 'RawF.route'))
    need(len(args) == 1, what + ': one argument')
    if k.endswith('leaf'):
        f = anon(args[0], 11, what + ' LeafF')
        d = dec_term(f[:7], what)
        d.update(margin=fqs(f[7]), lo=fqs(f[8]), hi=fqs(f[9]), bp=fqlist(f[10]))
        d['kind'] = 'leaf'
        return d
    t, us, ds, calls, g0, hm, mg, lo, hi, bp = anon(args[0], 10, what + ' RouteF')
    need(isinstance(calls, tuple) and calls[0] == 'list', what + ': calls list')
    cl = []
    for j, c in enumerate(calls[1]):
        ch, z, cbp = anon(c, 3, what + ' CallF')
        cl.append({'ch': sumref(ch, '%s call %d' % (what, j)), 'z': fqs(z), 'bp': fqlist(cbp)})
    return {'kind': 'route', 't': dec_term(anon(t, 7, what + ' TermF'), what), 'us': fqlist(us), 'ds': fqlist(ds),
            'calls': cl, 'g0': fqs(g0), 'hm': fqs(hm), 'margin': fqs(mg), 'lo': fqs(lo), 'hi': fqs(hi), 'bp': fqlist(bp)}


def dec_closed_piece(e, what):
    k, a = ctor(e, ('.rawDensity', '.complRaw', 'ClosedPF.rawDensity', 'ClosedPF.complRaw'))
    if k.endswith('rawDensity'):
        need(len(a) == 4, what + ': rawDensity arity')
        return {'kind': 'density', 'R': ['zr', fin(a[0], NR, what + '.R')], 'lo': fqs(a[1]), 'hi': fqs(a[2]),
                'bp': fqlist(a[3])}
    need(len(a) == 5, what + ': complRaw arity')
    return {'kind': 'pair', 'R': ['zr', fin(a[0], NR, what + '.R')], 'S': ['zr', fin(a[1], NR, what + '.S')],
            'lo': fqs(a[2]), 'hi': fqs(a[3]), 'bp': fqlist(a[4])}


def dec_source(e, what):
    Lo, Hi, eps, eta, kL, kR, cells = anon(e, 7, what + ' SourceF')
    need(isinstance(cells, tuple) and cells[0] == 'list', what + ': cells list')
    out = []
    for j, c in enumerate(cells[1]):
        k, a = ctor(c, ('.grounded', '.pair', 'SrcCellF.grounded', 'SrcCellF.pair'))
        w = '%s cell %d' % (what, j)
        if k.endswith('grounded'):
            need(len(a) == 3, w + ': grounded arity')
            kk = nat(a[0], w)
            need(kk < NLINES, w + ': line index %d >= %d' % (kk, NLINES))
            out.append({'kind': 'grounded', 'k': kk, 'lo': fqs(a[1]), 'hi': fqs(a[2])})
        else:
            need(len(a) == 5, w + ': pair arity')
            out.append({'kind': 'pair', 'PR': sumref(a[0], w + '.PR'), 'PB': sumref(a[1], w + '.PB'), 'lo': fqs(a[2]),
                        'hi': fqs(a[3]), 'bp': fqlist(a[4])})
    kL, kR = nat(kL, what + '.kL'), nat(kR, what + '.kR')
    need(kL < NLINES and kR < NLINES, what + ': tail line index out of range')
    return {'Lo': fqs(Lo), 'Hi': fqs(Hi), 'eps': fqs(eps), 'eta': fqs(eta), 'kL': kL, 'kR': kR, 'cells': out}


def idlist(e, what):
    need(isinstance(e, tuple) and e[0] == 'list', what + ': list expected')
    out = []
    for x in e[1]:
        need(isinstance(x, tuple) and x[0] == 'id', what + ': identifier expected')
        out.append(x[1])
    return out


# ---------------------------------------------------------------- file layout
TY_RAWP = 'RawF (Fin 1902 ⊕ Fin 1003) 918 2713'
TY_RAWL = 'List (RawF (Fin 1902 ⊕ Fin 1003) 918 2713)'
TY_CLP = 'ClosedPF 1902'
TY_CLL = 'List (ClosedPF 1902)'
TY_SRC = 'SourceF (Fin 1902 ⊕ Fin 1003)'

# T.lean accessor definitions whose exact text fixes the index semantics (A h = AL[h], raw i = rawL[i], ...)
T_TEXT = {
    'A': 'def A : Fin 2713 → FQ := fun i => AL.getD i.val FQ.zero',
    'B': 'def B : Fin 2713 → FQ := fun i => BL.getD i.val FQ.zero',
    'ctl': 'def ctl : Fin 918 → CtrlF := fun i => ctlL.getD i.val CtrlF.dflt',
    'raw': 'def raw : Fin 1902 → ProfF := fun i => rawL.getD i.val ProfF.dflt',
    'rawMin': 'def rawMin : Fin 1902 → FQ := fun i => rawMinL.getD i.val FQ.zero',
    'closed': 'def closed : Fin 1003 → ProfF := fun i => clL.getD i.val ProfF.dflt',
    'closedMin': 'def closedMin : Fin 1003 → FQ := fun i => clMinL.getD i.val FQ.zero',
    'pd': 'def pd : Fin 1902 ⊕ Fin 1003 → ProfF := Sum.elim raw closed',
    'i0': 'def i0 : Fin 1902 ⊕ Fin 1003 := .inl 0',
}
BANK_TEXT = """def bank : BankF 918 2713 1902 1003 where
  A := A
  B := B
  ctl := ctl
  raw := raw
  rawMin := rawMin
  closed := closed
  closedMin := closedMin
  rawPieces := fun i => rawPL.getD i.val []
  closedPieces := fun i => clPL.getD i.val []
  src := fun i => srcL.getD i.val SourceF.dflt
  lines := lines
  i0 := i0"""
HEADER_OK = re.compile(r'^(import [A-Za-z0-9_.]+|set_option [A-Za-z.]+ [0-9]+|namespace %s|end %s|end|open [A-Za-z0-9_. ]+|'
                       r'noncomputable section)$' % (re.escape(NS), re.escape(NS)))


def split_defs(text, fname):
    """returns list of (name, type, body) for one-line `def` commands; refuses any other command except the header
    forms, comments and (Data.lean) the `bank` structure instance, which is returned with type 'BANK'."""
    out = []
    lines = text.split('\n')
    i = 0
    in_comment = False
    ns_open = False
    while i < len(lines):
        ln = lines[i]
        i += 1
        if in_comment:
            if '-/' in ln:
                need(ln.rstrip().endswith('-/'), '%s: text after comment end' % fname)
                in_comment = False
            continue
        s = ln.strip()
        if not s:
            continue
        if s.startswith('/-'):
            if not s.endswith('-/'):
                in_comment = True
            continue
        if ln.startswith('def bank : BankF'):
            blk = [ln]
            while i < len(lines) and lines[i].startswith('  '):
                blk.append(lines[i])
                i += 1
            need('\n'.join(blk) == BANK_TEXT, '%s: bank structure text differs' % fname)
            out.append(('bank', 'BANK', None))
            continue
        if ln.startswith('def '):
            m = re.match(r'^def ([A-Za-z_][A-Za-z0-9_]*) : (.*?) := (.*)$', ln)
            need(m is not None, '%s: unrecognised def line %r' % (fname, ln[:80]))
            out.append((m.group(1), m.group(2), m.group(3)))
            continue
        need(HEADER_OK.match(s) is not None, '%s: unrecognised command %r' % (fname, s[:80]))
        if s == 'namespace ' + NS:
            ns_open = True
    need(not in_comment, fname + ': unterminated comment')
    need(ns_open or not out, fname + ': defs outside namespace %s' % NS)
    return out


THM_RP = re.compile(r'^theorem rp(\d+)_(\d+)_ok : RawF\.check ctl A B pd i0 \(raw \(⟨(\d+), by decide⟩ : Fin 1902\)\) '
                    r'rp(\d+)_(\d+) = true := by decide \+kernel$')
THM_RAW = re.compile(r'^theorem raw(\d+)_h : \(\(raw \(⟨(\d+), by decide⟩ : Fin 1902\)\)\.ok \(rawMin \(⟨(\d+), by decide⟩ : '
                     r'Fin 1902\)\) && chainF \(\(raw \(⟨(\d+), by decide⟩ : Fin 1902\)\)\.xs\.headD FQ\.zero\) \(rp(\d+)\.map '
                     r'\(fun x => \(x\.lo, x\.hi\)\)\) \(\(raw \(⟨(\d+), by decide⟩ : Fin 1902\)\)\.xs\.getLastD FQ\.zero\)\) = '
                     r'true := by decide \+kernel$')
THM_QP = re.compile(r'^theorem qp(\d+)_(\d+)_ok : ClosedPF\.check raw \(closed \(⟨(\d+), by decide⟩ : Fin 1003\)\) '
                    r'qp(\d+)_(\d+) = true := by decide \+kernel$')
THM_CL = re.compile(r'^theorem cl(\d+)_h : \(\(closed \(⟨(\d+), by decide⟩ : Fin 1003\)\)\.ok \(closedMin \(⟨(\d+), by decide⟩ '
                    r': Fin 1003\)\) && chainF \(\(closed \(⟨(\d+), by decide⟩ : Fin 1003\)\)\.xs\.headD FQ\.zero\) \(qp(\d+)'
                    r'\.map \(fun x => \(x\.lo, x\.hi\)\)\) \(\(closed \(⟨(\d+), by decide⟩ : Fin 1003\)\)\.xs\.getLastD '
                    r'FQ\.zero\)\) = true := by decide \+kernel$')
THM_SRC = re.compile(r'^theorem src(\d+)_h : \(FQ\.lt FQ\.zero \(A \(⟨(\d+), by decide⟩ : Fin 2713\)\) && FQ\.lt FQ\.zero '
                     r'\(B \(⟨(\d+), by decide⟩ : Fin 2713\)\) && SourceF\.check pd lines \(A \(⟨(\d+), by decide⟩ : '
                     r'Fin 2713\)\) \(B \(⟨(\d+), by decide⟩ : Fin 2713\)\) s(\d+)\) = true := by decide \+kernel$')


def theorems(text, fname):
    """(kind, profile/source index, piece def name) for every theorem line of a Raw/Closed/Src file; refuses any other
    theorem form."""
    out = []
    for ln in text.split('\n'):
        if not ln.startswith('theorem '):
            continue
        m = THM_RP.match(ln)
        if m:
            a, b, i, a2, b2 = m.groups()
            need(a == a2 and b == b2, fname + ': theorem name / piece mismatch')
            out.append(('rp', int(i), 'rp%s_%s' % (a, b)))
            continue
        m = THM_RAW.match(ln)
        if m:
            g = m.groups()
            need(len(set([g[0], g[1], g[2], g[3], g[4], g[5]])) == 1, fname + ': raw_h indices differ')
            out.append(('raw', int(g[1]), 'rp%s' % g[4]))
            continue
        m = THM_QP.match(ln)
        if m:
            a, b, i, a2, b2 = m.groups()
            need(a == a2 and b == b2, fname + ': theorem name / piece mismatch')
            out.append(('qp', int(i), 'qp%s_%s' % (a, b)))
            continue
        m = THM_CL.match(ln)
        if m:
            g = m.groups()
            need(len(set(g)) == 1, fname + ': cl_h indices differ')
            out.append(('cl', int(g[1]), 'qp%s' % g[4]))
            continue
        m = THM_SRC.match(ln)
        if m:
            g = m.groups()
            need(len(set(g)) == 1, fname + ': src_h indices differ')
            out.append(('src', int(g[1]), 's%s' % g[5]))
            continue
        raise ParseError('%s: unrecognised theorem %r' % (fname, ln[:100]))
    return out


# ---------------------------------------------------------------- main
def main(root, outp, zbs_bank=None):
    t0 = time.time()
    listing = load_listing(root)
    seen = {}
    P = os.path.join(SUBDIR, '%s')
    defs = {}          # name -> (type, body text)

    def add_defs(rel):
        for name, ty, body in split_defs(read_checked(root, rel, listing, seen), rel):
            need(name not in defs, 'duplicate def %s (%s)' % (name, rel))
            defs[name] = (ty, body, rel)

    dfiles = sorted([k for k in listing if re.match(r'^Solutions/P06/P0r12/D[0-9]+\.lean$', k)],
                    key=lambda k: int(re.search(r'D([0-9]+)\.lean$', k).group(1)))
    need(len(dfiles) == 349 and dfiles[-1].endswith('D348.lean'), 'expected D0..D348.lean')
    for rel in ['Solutions/P06/P0r12/T.lean'] + ['Solutions/P06/P0r12/TD%d.lean' % k for k in range(4)] + dfiles + \
               ['Solutions/P06/P0r12/Data.lean']:
        add_defs(rel)
    print('read %d data files, %d defs (%.0f s)' % (len(seen), len(defs), time.time() - t0), flush=True)

    # accessor defs of T.lean: exact text
    for name, txt in T_TEXT.items():
        ty, body, rel = defs.pop(name)
        need('def %s : %s := %s' % (name, ty, body) == txt, 'T.lean accessor %s differs: %r' % (name, body))
    defs.pop('linesRat')        # the ℚ copy of `lines` (not used by BankF); `lines` below is the FQ list BankF uses
    need(defs.pop('bank')[0] == 'BANK', 'bank')

    def take(name, ty):
        t, body, rel = defs.pop(name)
        need(t == ty, '%s: type %r, expected %r' % (name, t, ty))
        return parse_term(body)

    ctl_names = idlist(take('ctlL', 'List CtrlF'), 'ctlL')
    raw_names = idlist(take('rawL', 'List ProfF'), 'rawL')
    cl_names = idlist(take('clL', 'List ProfF'), 'clL')
    need(len(ctl_names) == NCTL and len(raw_names) == NR and len(cl_names) == NC, 'table lengths')
    rawMin = fqlist(take('rawMinL', 'List FQ')); clMin = fqlist(take('clMinL', 'List FQ'))
    AL = fqlist(take('AL', 'List FQ')); BL = fqlist(take('BL', 'List FQ'))
    need(len(rawMin) == NR and len(clMin) == NC and len(AL) == NSRC and len(BL) == NSRC, 'min / A / B lengths')
    le = take('lines', 'List (FQ × FQ)')
    need(le[0] == 'list', 'lines')
    lines = []
    for x in le[1]:
        need(isinstance(x, tuple) and x[0] == 'tuple' and len(x[1]) == 2, 'line pair')
        lines.append([fqs(x[1][0]), fqs(x[1][1])])
    need(len(lines) == NLINES, 'lines length %d' % len(lines))
    controls = [dec_ctrl(take(n, 'CtrlF')) for n in ctl_names]
    rawprof = [dec_prof(take(n, 'ProfF')) for n in raw_names]
    clprof = [dec_prof(take(n, 'ProfF')) for n in cl_names]
    rawPL = idlist(take('rawPL', 'List (List (RawF (Fin 1902 ⊕ Fin 1003) 918 2713))'), 'rawPL')
    clPL = idlist(take('clPL', 'List (List (ClosedPF 1902))'), 'clPL')
    srcL = idlist(take('srcL', 'List (SourceF (Fin 1902 ⊕ Fin 1003))'), 'srcL')
    need(len(rawPL) == NR and len(clPL) == NC and len(srcL) == NSRC, 'rawPL / clPL / srcL lengths')
    print('tables decoded (%.0f s)' % (time.time() - t0), flush=True)

    raw = []
    used_piece = {}
    for i, ln in enumerate(rawPL):
        names = idlist(take(ln, TY_RAWL), ln)
        pcs = []
        for nm in names:
            need(nm not in used_piece, 'raw piece %s used twice' % nm); used_piece[nm] = ('raw', i)
            pcs.append(dec_raw_piece(take(nm, TY_RAWP), nm))
        d = dict(rawprof[i]); d['min'] = rawMin[i]; d['pieces'] = pcs
        raw.append(d)
        if i % 200 == 0:
            print('  raw %d (%.0f s)' % (i, time.time() - t0), flush=True)
    closed = []
    for i, ln in enumerate(clPL):
        names = idlist(take(ln, TY_CLL), ln)
        pcs = []
        for nm in names:
            need(nm not in used_piece, 'closed piece %s used twice' % nm); used_piece[nm] = ('cl', i)
            pcs.append(dec_closed_piece(take(nm, TY_CLP), nm))
        d = dict(clprof[i]); d['min'] = clMin[i]; d['pieces'] = pcs
        closed.append(d)
    sources = []
    for h, nm in enumerate(srcL):
        need(nm not in used_piece, 'source %s used twice' % nm); used_piece[nm] = ('src', h)
        d = dec_source(take(nm, TY_SRC), nm)
        d['A'] = AL[h]; d['B'] = BL[h]
        sources.append(d)
    need(not defs, 'unused defs: %r' % sorted(defs)[:10])
    print('pieces decoded (%.0f s)' % (time.time() - t0), flush=True)

    # kernel theorem files: every piece / profile / source has its theorem at the index it is used at
    thm = {'rp': {}, 'raw': {}, 'qp': {}, 'cl': {}, 'src': {}}
    for rel in sorted(listing):
        if re.match(r'^Solutions/P06/P0r12/(Raw|Closed|Src)[0-9]+\.lean$', rel):
            for kind, idx, nm in theorems(read_checked(root, rel, listing, seen), rel):
                need(nm not in thm[kind], 'theorem for %s twice' % nm)
                thm[kind][nm] = idx
    need(set(thm['raw']) == set(rawPL) and all(thm['raw'][rawPL[i]] == i for i in range(NR)), 'raw_h theorems')
    need(set(thm['cl']) == set(clPL) and all(thm['cl'][clPL[i]] == i for i in range(NC)), 'cl_h theorems')
    need(set(thm['src']) == set(srcL) and all(thm['src'][srcL[h]] == h for h in range(NSRC)), 'src_h theorems')
    rp_used = {nm: v[1] for nm, v in used_piece.items() if v[0] == 'raw'}
    qp_used = {nm: v[1] for nm, v in used_piece.items() if v[0] == 'cl'}
    need(thm['rp'] == rp_used, 'rp_ok theorems differ from the pieces of rawPL')
    need(thm['qp'] == qp_used, 'qp_ok theorems differ from the pieces of clPL')
    btxt = read_checked(root, 'Solutions/P06/P0r12/Bank.lean', listing, seen)
    bk = {k: len(set(re.findall(r'^theorem %s([0-9]+)' % k, btxt, re.M))) for k in ('raw', 'cl', 'src')}
    need(bk == {'raw': NR, 'cl': NC, 'src': NSRC}, 'Bank.lean theorem counts %r' % bk)
    print('kernel theorem files consistent (%.0f s)' % (time.time() - t0), flush=True)

    # counts
    pk = [p['kind'] for P in raw for p in P['pieces']]
    ck = [p['kind'] for Q in closed for p in Q['pieces']]
    calls = [c for P in raw for p in P['pieces'] if p['kind'] == 'route' for c in p['calls']]
    allgr = [all(c['kind'] == 'grounded' for c in s['cells']) for s in sources]
    single = [len(s['cells']) == 1 and s['cells'][0]['kind'] == 'grounded' for s in sources]
    counts = {'raw': len(raw), 'closed': len(closed), 'sources': len(sources), 'controls': len(controls),
              'lines': len(lines), 'leaf': pk.count('leaf'), 'route': pk.count('route'),
              'density': ck.count('density'), 'pair': ck.count('pair'), 'route_calls': len(calls),
              'route_calls_raw_child': sum(c['ch'][0] == 'zr' for c in calls),
              'route_calls_closed_child': sum(c['ch'][0] == 'zc' for c in calls),
              'sources_all_cells_grounded': sum(allgr), 'sources_with_pair_cell': len(sources) - sum(allgr),
              'sources_one_grounded_cell': sum(single),
              'sources_one_grounded_cell_same_line_as_tails': sum(
                  1 for s, f in zip(sources, single) if f and s['cells'][0]['k'] == s['kL'] == s['kR']),
              'source_cells': sum(len(s['cells']) for s in sources),
              'source_pair_cells': sum(c['kind'] == 'pair' for s in sources for c in s['cells']),
              'routes_calls_ne_cells': sum(1 for P in raw for p in P['pieces'] if p['kind'] == 'route'
                                           and len(p['calls']) != len(p['ds'])),
              'ctl_beta_values': sorted(set(c['beta'] for c in controls))}
    print(json.dumps(counts), flush=True)

    res = {'what': 'ZBS bank P0r12 at c2875f33, parsed by parse_zbs_full.py', 'files_git_blob_sha1': seen,
           'counts': counts, 'controls': controls, 'raw': raw, 'closed': closed, 'sources': sources, 'lines': lines}

    if zbs_bank:
        z = json.load(open(zbs_bank))
        F = lambda s: Fr(s)
        bad = []
        for i in range(NR):
            a, b = raw[i], z['raw'][i]
            if not (F(a['p']) == F(b['p']) and list(map(F, a['xs'])) == list(map(F, b['xs'])) and
                    list(map(F, a['ys'])) == list(map(F, b['ys']))):
                bad.append(('raw', i))
        for i in range(NC):
            a, b = closed[i], z['closed'][i]
            if not (F(a['p']) == F(b['p']) and list(map(F, a['xs'])) == list(map(F, b['xs'])) and
                    list(map(F, a['ys'])) == list(map(F, b['ys']))):
                bad.append(('closed', i))
        if list(map(F, rawMin)) != list(map(F, z['rawMin'])): bad.append(('rawMin',))
        if list(map(F, clMin)) != list(map(F, z['closedMin'])): bad.append(('closedMin',))
        if list(map(F, AL)) != list(map(F, z['A'])): bad.append(('A',))
        if list(map(F, BL)) != list(map(F, z['B'])): bad.append(('B',))
        if [tuple(map(F, l)) for l in lines] != [tuple(map(F, l)) for l in z['lines']]: bad.append(('lines',))
        for i in range(NCTL):
            if [F(controls[i][k]) for k in ('p', 'mu', 'w', 'beta', 'x', 'lxU', 'l1mL')] != list(map(F, z['ctl'][i])):
                bad.append(('ctl', i))
        res['crosscheck_zbs_bank'] = {'file_sha256': hashlib.sha256(open(zbs_bank, 'rb').read()).hexdigest(),
                                      'mismatches': bad[:50], 'n_mismatches': len(bad)}
        print('cross-check with zbs_bank.json: %d mismatches %r' % (len(bad), bad[:10]), flush=True)

    with open(outp, 'w') as f:
        json.dump(res, f)
    print('wrote %s (%.0f s)' % (outp, time.time() - t0), flush=True)
    return res


if __name__ == '__main__':
    main(*sys.argv[1:])
