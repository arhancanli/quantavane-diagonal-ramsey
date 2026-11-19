"""Float (exploration; proves nothing): the two-region Lemma D' form's TRUE V (exact chain LP of dprime_float on the
grid drift) maximised over grid-CHORD profiles by local search on the touching set T (toggle moves and block
removals, several starts). Answers: how far below the saturated value does the worst chord profile reach, and at
which a-shift does it cross 0. Usage: python3 chord_search.py control.json nchain da1,da2,... [evals_per_start]"""
import sys
import numpy as np

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from cutq_float import Gate   # noqa: E402
from dp_gate import DPGate     # noqa: E402


def search(G, evals=300, starts=6, seed=0):
    D = DPGate(G); rng = np.random.default_rng(seed); b, n = G.b, G.n
    interior = np.arange(b + 1, n - 1)
    def V(Tmask):
        T = [b] + list(interior[Tmask]) + [n - 1]
        return G.Vtrue(D.m_of(T))
    best = (-np.inf, None)
    inits = [np.ones(len(interior), bool)]
    for s in range(starts - 1):
        p = rng.uniform(0.05, 0.9); inits.append(rng.random(len(interior)) < p)
    for T0 in inits:
        T = T0.copy(); fT = V(T)
        for e in range(evals):
            Tn = T.copy()
            if rng.random() < 0.7:
                Tn[rng.integers(len(T))] ^= True
            else:
                i = rng.integers(len(T)); L = rng.integers(2, 12)
                Tn[i:i + L] = rng.random() < 0.3
            fn = V(Tn)
            if np.isfinite(fn) and fn > fT: T, fT = Tn, fn
        if fT > best[0]: best = (fT, T.copy())
    fT, T = best
    pts = [round(G.v[k], 4) for k in interior[~T]]
    return fT, int((~T).sum()), pts[:12]


if __name__ == '__main__':
    import json
    from fractions import Fraction as Fr
    ctl = {k: float(Fr(s)) for k, s in json.load(open(sys.argv[1])).items()}
    nchain = int(sys.argv[2]); das = [float(s) for s in sys.argv[3].split(',')]
    ev = int(sys.argv[4]) if len(sys.argv) > 4 else 300
    for da in das:
        c = dict(ctl); c['x'] = ctl['x'] * np.exp(da)
        G = Gate(c, nchain)
        V0 = G.Vtrue(np.zeros(G.n))
        fT, nrem, pts = search(G, ev)
        print('da %.2e chain %d: saturated V %.3e; worst chord profile V %.3e (%d grid points off g, first: %s)'
              % (da, nchain, V0, fT, nrem, pts), flush=True)
