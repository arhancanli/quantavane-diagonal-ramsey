"""Dependency cone of the gen2 root (exploration): which pieces of which new objects, which U cells and which source
lines a certificate must contain.  History version: an object of round q is realised against round q's pool (E_hist[q],
Uhist[q], Bown_hist[q]); nothing is rewired, so the bank is a DAG.  usage: python3 cone.py state.pkl"""
import sys, pickle, collections   # pickle: our own local model state, never downloaded data
import numpy as np
from gen2 import Gen, H, NS


def route_steps(g, rec, q):
    """rebuild the path of a route record against round q's children: list of (step i, bucket, object or ('U', q))."""
    E, Earg = g.E_hist[q]
    saveE, saveA, saveN = g.E, g.Earg, g.negm
    g.E, g.Earg, g.negm = E, Earg, -np.minimum.accumulate(E, axis=0)
    gp, jst, sl = g.descent(rec['r'], np.array([rec['G']]))
    g.E, g.Earg, g.negm = saveE, saveA, saveN
    out = []
    for i in range(rec['th'] + 1, rec['r'] + 1):
        j = int(jst[0, i]); assert j >= 0
        out.append((i, j, ('U', int(Earg[0, i])) if j == 0 else int(Earg[j, i])))
    return out, gp[0]


def source_kind(g, q, a, b):
    """the line used at round q for intercept a: ZBS's best line with A <= a, or the own line of the round q' <= q
    (whose pool covers it) with the least slope."""
    owns = [float(np.interp(a, g.Ag, g.Bown_hist[qq], left=np.inf, right=g.Bown_hist[qq][-1])) for qq in range(q + 1)]
    qq = int(np.argmin(owns)); own = owns[qq]
    k = np.searchsorted(g.zA, a, 'right') - 1
    z = g.zB[k] if k >= 0 else np.inf
    return ('z', a, z) if z <= own else ('own', qq, a, own)


def cone(g, root, root_extra=True, src_margin=1e-6):
    """BFS.  Returns the needed pieces per object, U cells per round and own source lines."""
    obj_round = {}
    for o, tag in enumerate(g.pool_tag):
        if tag[0] == 'nr': obj_round[o] = (tag[1], tag[2])
    recs = {}
    for q, rs in enumerate(g.recs_hist):
        for rec in rs: recs[(q, rec['j'], rec['r'])] = rec
    need_pieces = collections.defaultdict(set)       # object -> set of piece right ends r
    need_U = {}                                      # round -> set of fine T_U cell indices
    srcs = set()
    todo = collections.deque()

    def req_obj(o, i0, i1):
        if o not in obj_round: return                # ZBS object
        q, j = obj_round[o]
        kp = g.kp
        i1 = max(i1, i0 + 1)
        for r in range((i0 // kp + 1) * kp, -(-i1 // kp) * kp + 1, kp):     # pieces (r - kp, r] meeting (i0, i1]
            if r > NS - 1: continue
            if r not in need_pieces[o]:
                need_pieces[o].add(r); todo.append(('piece', o, q, j, r))

    def req_U(q, t0=None, t1=None):
        """U_q is materialised whole (all fine cells of its defined coarse intervals)."""
        if q in need_U: return
        U, bR, bS, QK = g.Uhist[q]
        K, Ki = g.K, g.Kidx
        cells = set()
        for m in range(len(K) - 1):
            if np.isfinite(QK[m]) and np.isfinite(QK[m + 1]) and np.all(np.isfinite(U[Ki[m]:Ki[m + 1] + 1])):
                cells.update(range(Ki[m], Ki[m + 1]))
        need_U[q] = cells
        for k in sorted(cells): todo.append(('U', q, k))

    def req_src(q, a, b):
        s = source_kind(g, q, a, b)
        if s[0] == 'z' or s in srcs: return
        srcs.add(s); todo.append(('src',) + s)

    def do_rec(rec, q):
        if rec['kind'] == 1:
            steps, _ = route_steps(g, rec, q)
            for i, j, o in steps:
                if isinstance(o, tuple): req_U(o[1], g.S[i - 1], g.S[i])
                else: req_obj(o, i - 1, i)
        req_src(q, rec['a'], rec['b'])

    do_rec(root, root['round'])
    if root_extra and root['kind'] == 1:
        # the root's last path cell is extended past S_r (to 1 + 2e-10): its child must also cover step r + 1
        steps, _ = route_steps(g, root, root['round'])
        i, j, o = steps[-1]
        if isinstance(o, tuple): req_U(o[1], g.S[i - 1], g.S[i + 1])
        else: req_obj(o, i - 1, i + 1)
    nsteps = 0
    while todo:
        it = todo.popleft()
        if it[0] == 'piece':
            _, o, q, j, r = it
            rec = recs.get((q, j, r))
            if rec is None: raise KeyError((q, j, r))
            if rec['kind'] == 1: nsteps += rec['r'] - rec['th']
            do_rec(rec, q)
        elif it[0] == 'U':
            _, q, k = it
            Q, bR, bS, QK = g.Uhist[q]
            T = g.TU
            req_obj(int(bR[k]), int(np.floor((T[k] - g.S[0]) / H + 1e-9)), int(np.ceil((T[k + 1] - g.S[0]) / H - 1e-9)))
            req_obj(int(bS[k]), int(np.floor((1 / T[k + 1] - g.S[0]) / H + 1e-9)), int(np.ceil((1 / T[k] - g.S[0]) / H - 1e-9)))
        elif it[0] == 'src':
            _, _, q, a, b = it
            # the cover uses U_q on coarse intervals where one LW tangent line does not suffice
            T = g.TU
            mid = 0.5 * (T[:-1] + T[1:]); kk = g.lw_line_at(mid)
            g0 = g.lc[kk] + g.ld[kk] * T[:-1]; g1 = g.lc[kk] + g.ld[kk] * T[1:]
            bad = (g0 > a + b * T[:-1] - src_margin * (1 + T[:-1])) | (g1 > a + b * T[1:] - src_margin * (1 + T[1:]))
            if bad.any(): req_U(q)
    return need_pieces, need_U, srcs, nsteps


if __name__ == '__main__':
    g = pickle.load(open(sys.argv[1], 'rb'))
    root = g.last_root
    npcs, nU, srcs, nsteps = cone(g, root)
    byround = collections.Counter()
    for o, rs in npcs.items(): byround[g.pool_tag[o][1]] += len(rs)
    print('root %.9f round %d' % (root['vals'][-1], root['round']))
    print('objects', len(npcs), 'pieces', sum(len(v) for v in npcs.values()), 'by round', dict(sorted(byround.items())))
    print('route steps in cone', nsteps, 'U cells', {q: len(v) for q, v in nU.items()}, 'own source lines', len(srcs))
