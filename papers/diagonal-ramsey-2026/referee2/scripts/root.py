import json, sys
from fractions import Fraction as F
cert = json.load(open(sys.argv[1]))
q = cert['root']['closed']; Q = cert['closed'][q]
print('root closed', q, 'p', Q['p'], 'xs', Q['xs'], 'ys', Q['ys'], 'min', Q['min'], Q.get('gen'))
for pc in Q['pieces']: print(' piece', pc)
R = cert['raw'][Q['pieces'][0]['R'][1]] if Q['pieces'][0]['R'][0]=='nr' else None
if R:
    print('root raw p', R['p'], 'xs', R['xs'], 'ys', R['ys'], R.get('gen'))
    for pc in R['pieces']:
        print(' raw piece kind', pc['kind'], {k: v for k, v in pc.items() if k not in ('calls','us','ds','bp')})
        if pc['kind']=='route':
            print('  ncells', len(pc['ds']), 'us0', pc['us'][0], 'usN', pc['us'][-1], 'children', sorted(set((c['ch'][0], c['ch'][1]) for c in pc['calls']))[:10])
            ci = pc['t']['c']
        else: ci = pc['c']
        c = cert['controls'][ci]
        print('  control', ci, {k: v for k, v in c.items() if k not in ('cert','lemmaD')})
        if 'lemmaD' in c: print('  lemmaD keys', sorted(c['lemmaD'].keys()), 'control' in c['lemmaD'])
print('n lemmaD', sum('lemmaD' in c for c in cert['controls']))
for i, c in enumerate(cert['controls']):
    if 'lemmaD' in c:
        assert 'control' not in c['lemmaD'] and 'cert' not in c
print('ok no control key inside lemmaD')
