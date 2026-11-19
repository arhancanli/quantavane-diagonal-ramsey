import json, sys
from fractions import Fraction as F
for path in sys.argv[1:]:
    c = json.load(open(path))
    m_eps = min(F(s['eps']) for s in c['sources']); m_eta = min(F(s['eta']) for s in c['sources'])
    grounded_eta = [F(s['eta']) for s in c['sources'] if any(x['kind'] == 'grounded' for x in s['cells'])]
    print(path.split('/')[-1], 'sources', len(c['sources']), 'min eps', m_eps, float(m_eps), 'min eta', m_eta, float(m_eta),
          'min eta over sources with a grounded cell', float(min(grounded_eta)) if grounded_eta else None)
    del c
