import json, sys, collections
from fractions import Fraction as F
cp = sys.argv[1]
nf = [0]; nint = [0]
def hook_float(s):
    nf[0] += 1; return s
cert = json.load(open(cp), parse_float=hook_float)
print('top keys', list(cert.keys()), 'json floats:', nf[0])
for k, v in cert.items():
    print(k, type(v).__name__, len(v) if hasattr(v, '__len__') else v)
print('root', cert['root'])
# key sets
def keysets(objs, name):
    c = collections.Counter(tuple(sorted(o.keys())) for o in objs)
    for ks, n in c.items(): print(name, n, ks)
keysets(cert['controls'], 'control')
keysets(cert['raw'], 'raw')
keysets(cert['closed'], 'closed')
keysets(cert['sources'], 'source')
pk = collections.Counter(); refs = collections.Counter(); cellk = collections.Counter(); srcrefs = collections.Counter()
for P in cert['raw']:
    for pc in P['pieces']:
        pk[('raw', pc['kind'], tuple(sorted(pc.keys())))] += 1
        T = pc if pc['kind'] == 'leaf' else pc['t']
        srcrefs[T['src'][0]] += 1
        if pc['kind'] != 'leaf':
            for cl in pc['calls']: refs[('child', cl['ch'][0])] += 1
for Q in cert['closed']:
    for pc in Q['pieces']:
        pk[('closed', pc['kind'])] += 1
        refs[('closedR', pc['R'][0])] += 1
        if 'S' in pc: refs[('closedS', pc['S'][0])] += 1
for S in cert['sources']:
    for c in S['cells']:
        cellk[c['kind']] += 1
        if c['kind'] != 'grounded': refs[('srcPR', c['PR'][0])] += 1; refs[('srcPB', c['PB'][0])] += 1
for k, v in sorted(pk.items(), key=str): print(k, v)
print(refs); print(cellk); print('terminal sources', srcrefs)
ck = collections.Counter(('lemmaD' in c, 'cert' in c) for c in cert['controls']); print('control kinds (lemmaD, cert)', ck)
for c in cert['controls']:
    if 'lemmaD' in c:
        print('lemmaD keys', sorted(c['lemmaD'].keys())); break
for c in cert['controls']:
    if 'cert' in c:
        print('cert keys', sorted(c['cert'].keys()), 'len q', len(c['cert']['q'])); break
# types of scalar fields: any ints / non-strings?
types = collections.Counter()
def walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items(): walk(v, k)
    elif isinstance(o, list):
        for v in o: walk(v, path)
    else:
        types[(path, type(o).__name__)] += 1
walk(cert)
for k, v in sorted(types.items()): print('type', k, v)
