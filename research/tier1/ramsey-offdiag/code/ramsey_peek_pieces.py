"""Print the keys of a control and of one leaf and one route piece of the bank (format exploration)."""
import sys, json
d = json.load(open(sys.argv[1]))
c = d['controls'][0]
print('control keys', sorted(k for k in c if k != 'cert'), {k: c[k] for k in c if k != 'cert'})
r = d['raw'][0]
print('raw keys', sorted(r.keys()))
pcs = r.get('pieces') or r.get('cells') or []
print('piece example', json.dumps(pcs[0])[:600] if pcs else None)
for r in d['raw']:
    for pc in (r.get('pieces') or []):
        if pc.get('kind') not in (None, 'leaf') or 'route' in json.dumps(pc)[:50]:
            print('route-like piece', json.dumps(pc)[:700]); break
    else:
        continue
    break
print('closed keys', sorted(d['closed'][0].keys()), json.dumps(d['closed'][0].get('pieces', d['closed'][0].get('cells', [None]))[0])[:300])
