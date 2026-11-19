import sys, json, inspect, textwrap
sys.path.insert(0, 'research/tier2/ramsey-zbs/code/lemmaD')
from fractions import Fraction as F
import checkD_A as DA, checkD_B as DB
path = sys.argv[1]; cert = json.load(open(path))
LA = DA.LemmaD(cert); LB = DB.LemmaD(cert)
def patch(mod, cls, retline):
    src = textwrap.dedent(inspect.getsource(cls.box))
    src = src.replace("return U, dict(", "return U, {k: v for k, v in locals().items() if k != 'self'}; dict(")
    ns = {}; exec(src, mod.__dict__, ns); return ns['box']
boxA = patch(DA, DA.LemmaD, "return U, dict(j0=j0, jA=jA, kEhigh=float(kap * Ehigh), th=round(float(th), 4), K=float(Kv), IL=float(IL), IR2=float(IR2),\n                       dvar=float(dvar), kEcap=float(kap * Ecap), slope=round(float(slope), 5))")
boxB = patch(DB, DB.LemmaD, "return U, dict(j0=j0, jA=jA)")
rect = (F(0), F(cert['G_up']), -LA.w, F(cert['P_up']))
best = None
for b in DA.walk(cert['tree'], rect):
    u, _ = LB.box(*(DB.Q('%d/%d' % (t.numerator, t.denominator)) for t in b))
    u = F(int(u.p), int(u.q))
    if best is None or u > best[0]: best = (u, b)
bx = best[1]; print('box', [str(t) for t in bx])
ua, la = boxA(LA, *bx); ub, lb = boxB(LB, *(DB.Q('%d/%d' % (t.numerator, t.denominator)) for t in bx))
def f(x):
    try: return float(F(int(x.p), int(x.q)))
    except Exception:
        try: return float(x)
        except Exception: return str(x)[:40]
keys = ['U','C0','j0','h1','s0','Dl0','P1','a1','b1','F0p','IL','PK','ak','bk','Kint','Kv','a2','b2','Fph','IR2','ytop','jA','kap2','jB','qB','kap','th','mb','qR','slope','dvar','Egrid','Ecap','kap2h','Ehigh']
for k in keys:
    print('%-6s A %-28s B %-28s' % (k, f(la.get(k)), f(lb.get(k))))
