"""Reference cone of a certificate inside ZBS's bank P0r12 (cone step, 19 Nov 2026).

Starting from every reference of the certificate to a ZBS object (["zr", i] raw profile, ["zc", j] closed profile,
["z", h] source pair; found by a generic walk over the whole JSON, and cross-checked against the fields the checkers
read), the closure adds, for a ZBS object:
  raw profile i   -> for each piece: its control c, its terminal source sigma, and (route) the child of every call;
  closed profile j -> for each piece: R (and S for a pair) (raw profiles);
  source pair h   -> for each pair cell: PR and PB (raw or closed profiles).
Controls and ZBS's 1,128 lines (kL, kR, grounded k) refer to nothing further; the lines used are listed.
usage: python3 -I cone.py <zbs_full.json> <cert.json> <out_cone.json>"""
import sys, json, hashlib, time

ZTAGS = ('zr', 'zc', 'z')


def walk_refs(o, found, path='$'):
    """every [tag, int] with tag in zr/zc/z anywhere in the JSON, with its path (generic, field-agnostic)."""
    if isinstance(o, list):
        if len(o) == 2 and isinstance(o[0], str) and o[0] in ZTAGS:
            found.append((o[0], o[1], path))
            return
        for i, x in enumerate(o):
            walk_refs(x, found, path)
    elif isinstance(o, dict):
        for k, x in o.items():
            walk_refs(x, found, path + '.' + k)


def field_refs(cert):
    """the ZBS references in the fields the checkers read (bankA/bankB)."""
    out = []
    for P in cert['raw']:
        for pc in P['pieces']:
            if pc['kind'] == 'leaf':
                out.append(tuple(pc['src']))
            else:
                out.append(tuple(pc['t']['src']))
                out.extend(tuple(cl['ch']) for cl in pc['calls'])
    for Q in cert['closed']:
        for pc in Q['pieces']:
            out.append(tuple(pc['R']))
            if pc['kind'] == 'pair':
                out.append(tuple(pc['S']))
    for s in cert['sources']:
        for c in s['cells']:
            if c['kind'] == 'pair':
                out.extend([tuple(c['PR']), tuple(c['PB'])])
    return [r for r in out if r[0] in ZTAGS]


def closure(z, direct):
    raw, cl, src, ctl = set(), set(), set(), set()
    todo = list(direct)
    while todo:
        t, i = todo.pop()
        if t == 'zr':
            if i in raw: continue
            raw.add(i)
            for pc in z['raw'][i]['pieces']:
                T = pc if pc['kind'] == 'leaf' else pc['t']
                ctl.add(int(T['c']))
                assert T['src'][0] == 'z'
                todo.append(('z', int(T['src'][1])))
                if pc['kind'] == 'route':
                    todo.extend((cl_['ch'][0], int(cl_['ch'][1])) for cl_ in pc['calls'])
        elif t == 'zc':
            if i in cl: continue
            cl.add(i)
            for pc in z['closed'][i]['pieces']:
                todo.append(('zr', int(pc['R'][1])))
                if pc['kind'] == 'pair':
                    todo.append(('zr', int(pc['S'][1])))
        elif t == 'z':
            if i in src: continue
            src.add(i)
            for c in z['sources'][i]['cells']:
                if c['kind'] == 'pair':
                    todo.extend([(c['PR'][0], int(c['PR'][1])), (c['PB'][0], int(c['PB'][1]))])
        else:
            raise ValueError(t)
    return sorted(raw), sorted(cl), sorted(src), sorted(ctl)


def stats(z, raw, cl, src, ctl):
    pk = [pc for i in raw for pc in z['raw'][i]['pieces']]
    ck = [pc for j in cl for pc in z['closed'][j]['pieces']]
    cells = [c for h in src for c in z['sources'][h]['cells']]
    lines = set()
    for h in src:
        s = z['sources'][h]
        lines.update([s['kL'], s['kR']])
        lines.update(c['k'] for c in s['cells'] if c['kind'] == 'grounded')
    return {'raw_profiles': len(raw), 'closed_profiles': len(cl), 'sources': len(src), 'controls': len(ctl),
            'leaf_pieces': sum(p['kind'] == 'leaf' for p in pk), 'route_pieces': sum(p['kind'] == 'route' for p in pk),
            'route_calls': sum(len(p['calls']) for p in pk if p['kind'] == 'route'),
            'density_pieces': sum(p['kind'] == 'density' for p in ck), 'pair_pieces': sum(p['kind'] == 'pair' for p in ck),
            'source_cells': len(cells), 'source_grounded_cells': sum(c['kind'] == 'grounded' for c in cells),
            'source_pair_cells': sum(c['kind'] == 'pair' for c in cells), 'zbs_lines_used': len(lines)}


def main(zp, cp, outp):
    t0 = time.time()
    z = json.load(open(zp))
    csha = hashlib.sha256(open(cp, 'rb').read()).hexdigest()
    cert = json.load(open(cp))
    found = []
    walk_refs(cert, found)
    fr = field_refs(cert)
    assert sorted((t, i) for t, i, _ in found) == sorted(fr), 'generic walk and checker fields disagree'
    paths = sorted(set(p for _, _, p in found))
    direct = sorted(set((t, int(i)) for t, i, _ in found))
    dstat = {t: len([1 for tt, _ in direct if tt == t]) for t in ZTAGS}
    raw, cl, src, ctl = closure(z, direct)
    st = stats(z, raw, cl, src, ctl)
    res = {'cert': cp, 'cert_sha256': csha, 'zbs_full': zp,
           'direct': {t: [i for tt, i in direct if tt == t] for t in ZTAGS}, 'direct_counts': dstat,
           'direct_ref_occurrences': len(found), 'direct_ref_paths': paths,
           'raw': raw, 'closed': cl, 'sources': src, 'controls': ctl, 'stats': st,
           'min_source_eps_eta': min(min(float(eval_fr(z['sources'][h]['eps'])), float(eval_fr(z['sources'][h]['eta'])))
                                     for h in src) if src else None,
           'seconds': round(time.time() - t0, 1)}
    with open(outp, 'w') as f:
        json.dump(res, f)
    print(json.dumps({k: res[k] for k in ('cert_sha256', 'direct_counts', 'direct_ref_occurrences', 'direct_ref_paths',
                                          'stats', 'min_source_eps_eta', 'seconds')}))
    return res


def eval_fr(s):
    from fractions import Fraction
    return Fraction(s)


if __name__ == '__main__':
    main(*sys.argv[1:])
