"""Targeted one-object tampers on a real certificate (shared by harnessA / harnessB)."""
import copy
from fractions import Fraction as F

def fs(x): x = F(x); return '%d/%d' % (x.numerator, x.denominator)

def find(cert):
    raws = cert['raw']
    out = {}
    # a leaf piece with an interior bp that is a knot of P
    for i in range(len(raws) - 1, -1, -1):
        P = raws[i]; xs = set(F(t) for t in P['xs'])
        for pc in P['pieces']:
            if pc['kind'] == 'leaf' and any(F(t) in xs for t in pc['bp'][1:-1]):
                out['leaf'] = (i, P['pieces'].index(pc)); break
        if 'leaf' in out: break
    # a route piece with >= 2 cells, whose some child bp has an interior knot
    for i in range(len(raws) - 1, -1, -1):
        P = raws[i]
        for k, pc in enumerate(P['pieces']):
            if pc['kind'] == 'route' and len(pc['ds']) >= 2 and any(len(c['bp']) > 2 for c in pc['calls']):
                out['route'] = (i, k); break
        if 'route' in out: break
    out['rootQ'] = cert['root']['closed']
    for qi, Q in enumerate(cert['closed']):
        if Q.get('gen', {}).get('U') is not None:
            out['U'] = qi; break
    for h, S in enumerate(cert['sources']):
        kinds = set(c['kind'] for c in S['cells'])
        if 'grounded' in kinds and 'pair' in kinds:
            out['src'] = h; break
    return out

def tamper_list(cert):
    loc = find(cert)
    T = []
    raws = cert['raw']; ctls = cert['controls']
    # ---------- leaf ----------
    i, k = loc['leaf']; P = raws[i]; L = P['pieces'][k]; c = ctls[int(L['c'])]
    def leaf(name, fP=None, fL=None):
        P2 = copy.deepcopy(P); L2 = copy.deepcopy(L)
        if fP: fP(P2)
        if fL: fL(L2)
        T.append((name, 'leaf', (P2, L2)))
    leaf('leaf: control p > P.p', fP=lambda d: d.__setitem__('p', fs(F(c['p']) - F(1, 10**12))))
    def dropknot(L2):
        xs = set(F(t) for t in P['xs'])
        j = next(j for j in range(1, len(L2['bp']) - 1) if F(L2['bp'][j]) in xs); del L2['bp'][j]
    leaf('leaf: interior knot dropped from bp', fL=dropknot)
    leaf('leaf: margin 0', fL=lambda d: d.__setitem__('margin', '0'))
    leaf('leaf: xi = x', fL=lambda d: d.__setitem__('xi', c['x']))
    leaf('leaf: ys = 0', fL=lambda d: d.__setitem__('ys', '0'))
    leaf('leaf: nu = mu', fL=lambda d: d.__setitem__('nu', c['mu']))
    leaf('leaf: aU - 1e-30', fL=lambda d: d.__setitem__('aU', fs(F(d['aU']) - F(1, 10**30))))
    leaf('leaf: lo = 0 (bp[0]=0)', fL=lambda d: (d.__setitem__('lo', '0'), d['bp'].__setitem__(0, '0')))
    leaf('leaf: src -> ZBS source 0 (B_sigma changes)', fL=lambda d: d.__setitem__('src', ['z', 0]))
    leaf('leaf: control index -1', fL=lambda d: d.__setitem__('c', -1))
    # ---------- route ----------
    i, k = loc['route']; P = raws[i]; R = P['pieces'][k]; cR = ctls[int(R['t']['c'])]
    def route(name, fP=None, fR=None):
        P2 = copy.deepcopy(P); R2 = copy.deepcopy(R)
        if fP: fP(P2)
        if fR: fR(R2)
        T.append((name, 'route', (P2, R2)))
    route('route: P.p = control p (non-strict)', fP=lambda d: d.__setitem__('p', cR['p']))
    route('route: hm = 0', fR=lambda d: d.__setitem__('hm', '0'))
    route('route: g0 = 0', fR=lambda d: d.__setitem__('g0', '0'))
    route('route: one call removed', fR=lambda d: d['calls'].pop())
    route('route: one extra call', fR=lambda d: d['calls'].append(copy.deepcopy(d['calls'][-1])))
    route('route: hi beyond us[-1]', fR=lambda d: (d.__setitem__('hi', fs(F(d['us'][-1]) + F(1, 10**9))), d['bp'].__setitem__(-1, fs(F(d['us'][-1]) + F(1, 10**9)))))
    route('route: theta above lo', fR=lambda d: d['us'].__setitem__(0, fs(F(d['lo']) + F(1, 10**12))))
    def zbad(d):
        cl = d['calls'][0]
        # child density p_c: look it up by reference below in harness (store marker)
        cl['z'] = 'ONE_MINUS_PC'
    route('route: z = 1 - p_child', fR=zbad)
    route('route: child -> nr index -1', fR=lambda d: d['calls'][0].__setitem__('ch', [d['calls'][0]['ch'][0], -1]))
    route('route: child -> unknown kind', fR=lambda d: d['calls'][0].__setitem__('ch', ['xx', 0]))
    def dropchildknot(d):
        cl = next(c for c in d['calls'] if len(c['bp']) > 2); del cl['bp'][1]
    route('route: child bp interior point dropped', fR=dropchildknot)
    route('route: margin 0', fR=lambda d: d.__setitem__('margin', '0'))
    route('route: terminal ys = 0', fR=lambda d: d['t'].__setitem__('ys', '0'))
    route('route: terminal xi = x', fR=lambda d: d['t'].__setitem__('xi', cR['x']))
    route('route: ds[0] -> 0 (slope too small)', fR=lambda d: d['ds'].__setitem__(0, '0'))
    # ---------- closed ----------
    q = loc['rootQ']; Q = cert['closed'][q]; pc = Q['pieces'][0]
    def closed(name, fQ=None, fpc=None, fRprof=None):
        Q2 = copy.deepcopy(Q); pc2 = copy.deepcopy(pc)
        if fQ: fQ(Q2)
        if fpc: fpc(pc2)
        T.append((name, 'closed', (Q2, pc2, fRprof)))
    closed('closed root: R,S -> closed profile', fpc=lambda d: (d.__setitem__('R', ['nc', 0]), d.__setitem__('S', ['nc', 0])))
    closed('closed root: R p raised (p_R + p_S > 1)', fRprof=lambda Rd: Rd.__setitem__('p', fs(F(Rd['p']) + F(1, 10**12))))
    closed('closed root: Q value at 1 lowered by 1e-15', fQ=lambda d: d['ys'].__setitem__(1, fs(F(d['ys'][1]) - F(1, 10**15))))
    closed('closed root: Q value at 1+delta lowered (reflected fails)', fQ=lambda d: d['ys'].__setitem__(2, fs(F(d['ys'][2]) - F(1, 10**14))))
    closed('closed root: bp drops knot 1', fpc=lambda d: d['bp'].pop(1))
    closed('closed root: kind density with p_R <= p_Q (allowed, check R<=Q only)', fpc=lambda d: d.__setitem__('kind', 'density'))
    if 'U' in loc:
        U = cert['closed'][loc['U']]; upc = U['pieces'][len(U['pieces']) // 2]
        U2 = copy.deepcopy(U); upc2 = copy.deepcopy(upc); upc2['kind'] = 'density'
        T.append(('closed U: pair -> density copy (p_R > p_Q=1e-6)', 'closed', (U2, upc2, None)))
    # ---------- source ----------
    h = loc['src']; S = cert['sources'][h]
    def src(name, f):
        S2 = copy.deepcopy(S); f(S2); T.append((name, 'source', (h, S2)))
    src('source: eps = 0', lambda d: d.__setitem__('eps', '0'))
    src('source: kL = -1', lambda d: d.__setitem__('kL', -1))
    src('source: kL out of range', lambda d: d.__setitem__('kL', 10**6))
    src('source: last cell dropped (cover short of Hi)', lambda d: d['cells'].pop())
    def gap(d):
        c0 = d['cells'][0]; c0['hi'] = fs(F(c0['hi']) - F(1, 10**12))
        if 'bp' in c0: c0['bp'][-1] = c0['hi']
    src('source: gap between first two cells', gap)
    def gk(d):
        g = next(c for c in d['cells'] if c['kind'] == 'grounded'); g['k'] = -1
    src('source: grounded k = -1', gk)
    def pairp(d):
        p = next(c for c in d['cells'] if c['kind'] == 'pair'); p['PR'] = ['zr', 0]   # density 1/80, domain small
    src('source: pair PR -> ZBS raw 0', pairp)
    src('source: A lowered by 1e-6', lambda d: d.__setitem__('A', fs(F(d['A']) - F(1, 10**6))))
    src('source: Hi beyond right tail line validity (Hi lowered, chain kept?)', lambda d: d.__setitem__('Hi', fs(F(d['Hi']) - F(1, 10**12))))
    # ---------- root ----------
    T.append(('root: piece kind density', 'root', ('kind', 'density')))
    T.append(('root: z claimed 1e-15 lower', 'root', ('z', fs(F(cert['root']['z']) - F(1, 10**15)))))
    T.append(('root: closed index -1', 'root', ('closed', -1)))
    return T, loc

def control_tampers(c):
    """tampers of a Lemma C control (dict with 'cert')."""
    T = []
    def ctl(name, f):
        c2 = copy.deepcopy(c); f(c2); T.append((name, c2))
    cc = c['cert']; N = len(cc['q']) - 1
    ctl('ctl: secant through the cell itself (same side)', lambda d: d['cert']['sec'].__setitem__(N // 2, [N // 2, N // 2 + 1]))
    ctl('ctl: secant straddling the cell', lambda d: d['cert']['sec'].__setitem__(N // 2, [N // 2 - 1, N // 2 + 2]))
    ctl('ctl: secant through a_cut (q_0 not in D)', lambda d: d['cert']['sec'].__setitem__(N // 2, [0, 1]))
    ctl('ctl: k -> 0 (dominance fails?)', lambda d: d['cert'].__setitem__('k', 0))
    ctl('ctl: k -> N+1', lambda d: d['cert'].__setitem__('k', N + 1))
    ctl('ctl: k -> -1', lambda d: d['cert'].__setitem__('k', -1))
    ctl('ctl: h[k] lowered 1e-12', lambda d: d['cert']['h'].__setitem__(int(cc['k']), fs(F(cc['h'][int(cc['k'])]) - F(1, 10**12))))
    ctl('ctl: h[0] raised by 1 (hinge?)', lambda d: d['cert']['h'].__setitem__(0, fs(F(cc['h'][0]) + 1)))
    ctl('ctl: a_cut moved into D (q0 = q1 - 1e-12)', lambda d: (d['cert'].__setitem__('a_cut', fs(F(cc['q'][1]) - F(1, 10**12))), d['cert']['q'].__setitem__(0, fs(F(cc['q'][1]) - F(1, 10**12)))))
    ctl('ctl: q[0] != a_cut', lambda d: d['cert'].__setitem__('a_cut', fs(F(cc['a_cut']) / 2)))
    ctl('ctl: q[N] != mu', lambda d: d['cert']['q'].__setitem__(N, fs(F(cc['q'][N]) - F(1, 10**15))))
    ctl('ctl: two q swapped', lambda d: (d['cert']['q'].__setitem__(5, cc['q'][6]), d['cert']['q'].__setitem__(6, cc['q'][5])))
    ctl('ctl: beta = 1', lambda d: d.__setitem__('beta', '1'))
    ctl('ctl: x = p', lambda d: d.__setitem__('x', d['p']))
    ctl('ctl: lxU raised to w*l1mL', lambda d: d.__setitem__('lxU', fs(F(d['w']) * F(d['l1mL']))))
    ctl('ctl: x raised 2e-5 relative', lambda d: d.__setitem__('x', fs(F(d['x']) * (1 + F(2, 10**5)))))
    ctl('ctl: both cert and lemmaD', lambda d: d.__setitem__('lemmaD', {}))
    ctl('ctl: no cert at all', lambda d: d.pop('cert'))
    ctl('ctl: sec entry negative index', lambda d: d['cert']['sec'].__setitem__(N // 2, [-2, -1]))
    return T

def cd_tampers(c):
    """tampers of a Lemma D control (dict with 'lemmaD')."""
    T = []
    def ctl(name, f):
        c2 = copy.deepcopy(c); f(c2); T.append((name, c2))
    ctl('cd: lemmaD carries its own control with larger x', lambda d: d['lemmaD'].__setitem__('control', dict(p=d['p'], mu=d['mu'], w=d['w'], beta=d['beta'], x=fs(F(d['x']) * F(101, 100)))))
    ctl('cd: bank control mu + 1e-12 (qgrid end stale)', lambda d: d.__setitem__('mu', fs(F(d['mu']) + F(1, 10**12))))
    ctl('cd: bank control x + 1e-9 relative', lambda d: d.__setitem__('x', fs(F(d['x']) * (1 + F(1, 10**9)))))
    ctl('cd: jA0 = 0', lambda d: d['lemmaD'].__setitem__('jA0', 0))
    ctl('cd: jA0 = -1', lambda d: d['lemmaD'].__setitem__('jA0', -1))
    ctl('cd: tree axis "x" at root', lambda d: d['lemmaD'].__setitem__('tree', ['x'] + d['lemmaD']['tree'][1:]))
    ctl('cd: qgrid N = 1', lambda d: d['lemmaD'].__setitem__('qgrid', [d['lemmaD']['qgrid'][0], d['lemmaD']['qgrid'][-1]]))
    ctl('cd: P_up below -w log u_b', lambda d: d['lemmaD'].__setitem__('P_up', fs(F(d['lemmaD']['P_up']) * F(999, 1000))))
    ctl('cd: y_c > phi_s(u_b)', lambda d: d['lemmaD'].__setitem__('y_c', '2'))
    ctl('cd: Dplus doubled (still divides?)', lambda d: d['lemmaD'].__setitem__('Dplus', fs(F(d['lemmaD']['Dplus']) * 2)))
    ctl('cd: mu + 1e-12 with l1mL lowered (CtrlD.ok kept)', lambda d: (d.__setitem__('mu', fs(F(d['mu']) + F(1, 10**12))), d.__setitem__('l1mL', fs(F(d['l1mL']) - F(1, 10**9)))))
    ctl('cd: x * (1+1e-6) with lxU raised (CtrlD.ok kept)', lambda d: (d.__setitem__('x', fs(F(d['x']) * (1 + F(1, 10**6)))), d.__setitem__('lxU', fs(F(d['lxU']) + F(2, 10**6)))))
    ctl('cd: x * (1+2e-12) with lxU raised (CtrlD.ok kept)', lambda d: (d.__setitem__('x', fs(F(d['x']) * (1 + F(2, 10**12)))), d.__setitem__('lxU', fs(F(d['lxU']) + F(4, 10**12)))))
    ctl('cd: w * (1+1e-9)', lambda d: d.__setitem__('w', fs(F(d['w']) * (1 + F(1, 10**9)))))
    ctl('cd: beta -> 1 - 1e-6 (looser)', lambda d: d.__setitem__('beta', '999999/1000000'))
    def axis_swap(d):
        t = d['lemmaD']['tree']
        # find first internal node with axis 'p' and relabel it 'x' (A treats any non-'P' label as 'p')
        st = [t]
        while st:
            n = st.pop()
            if isinstance(n, list):
                if n[0] == 'p': n[0] = 'x'; return
                st += [n[1], n[2]]
    ctl('cd: a "p" axis relabelled "x" (format only)', axis_swap)
    return T
