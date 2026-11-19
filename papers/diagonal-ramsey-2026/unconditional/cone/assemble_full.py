"""Assemble a ZBS-free certificate (cone step, 19 Nov 2026).

Input: our certificate (certK3.json or certCD3.json), ZBS's bank as parsed by parse_zbs_full.py, the cone of the
certificate (cone.py) and the Lemma C certificates of ZBS's controls (ctl_certs.py shard files).
Output: the same certificate with
  - every ZBS object of the cone appended as a NEW object: cone raw profile i -> new raw index len(raw) + rank(i),
    cone closed profile j -> len(closed) + rank(j), cone source h -> len(sources) + rank(h), cone control c ->
    len(controls) + rank(c) (ranks in increasing ZBS index);
  - every reference replaced: ["zr", i] -> ["nr", new], ["zc", j] -> ["nc", new], ["z", h] -> ["n", new], and in the
    converted ZBS pieces the control index c -> its new index;
  - each converted ZBS control carrying OUR Lemma C certificate ('cert'), verified by ctl_certs.py;
  - everything else of our certificate (objects, their order and fields, root, meta) unchanged.
Converted objects carry a provenance string 'zbs' (e.g. "r123", "q45", "s678", "c12"); the checkers do not read it.
A map file <out>.map.json records the index maps.
usage: python3 -I assemble_full.py <zbs_full.json> <cert.json> <cone.json> <out.json> <ctl_shard.json> [...]"""
import sys, json, hashlib, time

# SHA-256 of zbs_full.json as written by parse_zbs_full.py from the c2875f33 tree (audit C-3)
ZBS_FULL_SHA256 = 'a2395f138b9ee24a2a5409debe44bb15443f544179fc75837d53c79b195903ca'

FIELDS = ('p', 'mu', 'w', 'beta', 'x', 'lxU', 'l1mL')


def main(zp, cp, conep, outp, *ctlps):
    t0 = time.time()
    cone = json.load(open(conep))
    csha = hashlib.sha256(open(cp, 'rb').read()).hexdigest()
    assert cone['cert_sha256'] == csha, 'cone file is for another certificate'
    cert = json.load(open(cp))
    assert hashlib.sha256(open(zp, 'rb').read()).hexdigest() == ZBS_FULL_SHA256, 'zbs_full.json is not the pinned parse'
    z = json.load(open(zp))
    ctlc = {}
    for p in ctlps:
        ctlc.update({int(k): v for k, v in json.load(open(p))['controls'].items()})
    missing = [c for c in cone['controls'] if c not in ctlc]
    assert not missing, 'controls without a Lemma C certificate: %r' % missing[:20]

    nR, nC, nS, nK = len(cert['raw']), len(cert['closed']), len(cert['sources']), len(cert['controls'])
    rmap = {i: nR + r for r, i in enumerate(cone['raw'])}
    cmap = {j: nC + r for r, j in enumerate(cone['closed'])}
    smap = {h: nS + r for r, h in enumerate(cone['sources'])}
    kmap = {c: nK + r for r, c in enumerate(cone['controls'])}
    count = {'zr': 0, 'zc': 0, 'z': 0, 'ctl': 0}

    def prof(ref):
        t, i = ref[0], int(ref[1])
        if t == 'zr': count['zr'] += 1; return ['nr', rmap[i]]
        if t == 'zc': count['zc'] += 1; return ['nc', cmap[i]]
        assert t in ('nr', 'nc'), ref
        return ref

    def src(ref):
        t, h = ref[0], int(ref[1])
        if t == 'z': count['z'] += 1; return ['n', smap[h]]
        assert t == 'n', ref
        return ref

    def raw_piece(pc, zbs):
        """in place: references of a raw piece; zbs=True also maps the control index (ZBS control -> new)."""
        T = pc if pc['kind'] == 'leaf' else pc['t']
        T['src'] = src(T['src'])
        if zbs:
            T['c'] = kmap[int(T['c'])]; count['ctl'] += 1
        if pc['kind'] == 'route':
            for cl in pc['calls']:
                cl['ch'] = prof(cl['ch'])
        else:
            assert pc['kind'] == 'leaf'

    def closed_piece(pc):
        pc['R'] = prof(pc['R'])
        if pc['kind'] == 'pair':
            pc['S'] = prof(pc['S'])
        else:
            assert pc['kind'] == 'density'
        assert pc['R'][0] == 'nr' and (pc['kind'] != 'pair' or pc['S'][0] == 'nr'), 'closed pieces use raw profiles'

    def source(s):
        for c in s['cells']:
            if c['kind'] == 'pair':
                c['PR'] = prof(c['PR']); c['PB'] = prof(c['PB'])
            else:
                assert c['kind'] == 'grounded'

    # 1. our objects: references only
    for P in cert['raw']:
        for pc in P['pieces']: raw_piece(pc, False)
    for Q in cert['closed']:
        for pc in Q['pieces']: closed_piece(pc)
    for s in cert['sources']: source(s)
    ours = dict(count)

    # 2. the cone's ZBS objects, converted and appended
    for i in cone['raw']:
        P = z['raw'][i]
        for pc in P['pieces']: raw_piece(pc, True)
        cert['raw'].append({'p': P['p'], 'xs': P['xs'], 'ys': P['ys'], 'min': P['min'], 'pieces': P['pieces'],
                            'zbs': 'r%d' % i})
    for j in cone['closed']:
        Q = z['closed'][j]
        for pc in Q['pieces']: closed_piece(pc)
        cert['closed'].append({'p': Q['p'], 'xs': Q['xs'], 'ys': Q['ys'], 'min': Q['min'], 'pieces': Q['pieces'],
                               'zbs': 'q%d' % j})
    for h in cone['sources']:
        s = z['sources'][h]
        source(s)
        cert['sources'].append({'A': s['A'], 'B': s['B'], 'Lo': s['Lo'], 'Hi': s['Hi'], 'eps': s['eps'], 'eta': s['eta'],
                                'kL': s['kL'], 'kR': s['kR'], 'cells': s['cells'], 'zbs': 's%d' % h})
    for c in cone['controls']:
        k = ctlc[c]
        assert all(k[f] == z['controls'][c][f] for f in FIELDS), 'control %d data differs from the parse' % c
        d = {f: k[f] for f in FIELDS}
        d['cert'] = k['cert']; d['zbs'] = 'c%d' % c
        cert['controls'].append(d)

    with open(outp, 'w') as f:
        json.dump(cert, f)
    osha = hashlib.sha256(open(outp, 'rb').read()).hexdigest()
    m = {'cert': cp, 'cert_sha256': csha, 'out': outp, 'out_sha256': osha, 'cone': conep,
         'ctl_shards': list(ctlps), 'ctl_shard_sha256': [hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in ctlps],
         'refs_replaced_in_our_objects': ours, 'refs_replaced_total': count,
         'base': {'raw': nR, 'closed': nC, 'sources': nS, 'controls': nK},
         'final': {'raw': len(cert['raw']), 'closed': len(cert['closed']), 'sources': len(cert['sources']),
                   'controls': len(cert['controls'])},
         'raw_map': rmap, 'closed_map': cmap, 'source_map': smap, 'control_map': kmap,
         'seconds': round(time.time() - t0, 1)}
    with open(outp[:-5] + '.map.json' if outp.endswith('.json') else outp + '.map.json', 'w') as f:
        json.dump(m, f)
    print(json.dumps({k: m[k] for k in ('out_sha256', 'refs_replaced_in_our_objects', 'refs_replaced_total', 'base',
                                         'final', 'seconds')}))


if __name__ == '__main__':
    main(*sys.argv[1:])
