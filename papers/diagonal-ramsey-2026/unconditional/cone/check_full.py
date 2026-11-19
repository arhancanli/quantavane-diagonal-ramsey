"""Structural check of a ZBS-free certificate (cone step, 19 Nov 2026).  Exit status 0 and "FULL CHECK OK" iff:
 (1) NO reference to a ZBS object remains: no list [t, i] with t in {"zr", "zc", "z"} anywhere in the JSON, and no
     string value equal to "zr", "zc" or "z" anywhere (a generic walk over every value);
 (2) every profile / source reference in the fields the checkers read is ["nr", i] / ["nc", i] / ["n", h] with i, h in
     range, every closed piece uses raw profiles, and every control index is in range;
and, in the optional modes,
 --orig <cert.json> <map.json>: every object of the original certificate equals the full certificate's object at the
     same index after replacing its ZBS references through the map; root and meta are equal; the appended objects are
     exactly the map's cone objects (counts);
 --zbs <zbs_full.json> <map.json>: every appended object equals the parsed ZBS object it came from after replacing
     references and control indices through the map (plus its provenance tag), and every appended control has the
     parsed ZBS control's (p, mu, w, beta, x, lxU, l1mL) and a Lemma C 'cert' (no 'lemmaD').
usage: python3 -I check_full.py <full.json> [--orig <cert.json> <map.json>] [--zbs <zbs_full.json> <map.json>]"""
import sys, json, copy, hashlib

# SHA-256 of zbs_full.json as written by parse_zbs_full.py from the c2875f33 tree (audit C-3)
ZBS_FULL_SHA256 = 'a2395f138b9ee24a2a5409debe44bb15443f544179fc75837d53c79b195903ca'

ZT = ('zr', 'zc', 'z')


class Refused(Exception):
    pass


def need(c, msg):
    if not c:
        raise Refused(msg)


def no_zbs(o, path='$'):
    if isinstance(o, list):
        need(not (len(o) == 2 and isinstance(o[0], str) and o[0] in ZT), 'ZBS reference %r at %s' % (o, path))
        for x in o:
            no_zbs(x, path)
    elif isinstance(o, dict):
        for k, x in o.items():
            no_zbs(x, path + '.' + k)
    elif isinstance(o, str):
        need(o not in ZT, 'string %r at %s' % (o, path))


def fields(c):
    nR, nC, nS, nK = len(c['raw']), len(c['closed']), len(c['sources']), len(c['controls'])
    n = {'refs': 0, 'ctl_refs': 0}

    def prof(r, raw_only=False):
        need(isinstance(r, list) and len(r) == 2 and isinstance(r[1], int), 'profile reference %r' % (r,))
        need(r[0] in (('nr',) if raw_only else ('nr', 'nc')), 'profile reference kind %r' % (r,))
        need(0 <= r[1] < (nR if r[0] == 'nr' else nC), 'profile reference out of range %r' % (r,))
        n['refs'] += 1

    def term(T):
        need(T['src'][0] == 'n' and isinstance(T['src'][1], int) and 0 <= T['src'][1] < nS, 'source ref %r' % (T['src'],))
        need(isinstance(T['c'], int) and 0 <= T['c'] < nK, 'control index %r' % (T['c'],))
        n['refs'] += 1; n['ctl_refs'] += 1

    for P in c['raw']:
        for pc in P['pieces']:
            if pc['kind'] == 'leaf':
                term(pc)
            else:
                need(pc['kind'] == 'route', 'piece kind')
                term(pc['t'])
                for cl in pc['calls']: prof(cl['ch'])
    for Q in c['closed']:
        for pc in Q['pieces']:
            prof(pc['R'], True)
            if pc['kind'] == 'pair': prof(pc['S'], True)
            else: need(pc['kind'] == 'density', 'closed piece kind')
    for s in c['sources']:
        for cell in s['cells']:
            if cell['kind'] == 'pair':
                prof(cell['PR']); prof(cell['PB'])
            else:
                need(cell['kind'] == 'grounded', 'cell kind')
    need(isinstance(c['root']['closed'], int) and 0 <= c['root']['closed'] < nC, 'root index')
    return n


def maps(mp):
    m = json.load(open(mp))
    return ({int(k): v for k, v in m['raw_map'].items()}, {int(k): v for k, v in m['closed_map'].items()},
            {int(k): v for k, v in m['source_map'].items()}, {int(k): v for k, v in m['control_map'].items()}, m)


def remap(o, rm, cm, sm):
    """deep copy with ZBS references replaced (control indices untouched)."""
    if isinstance(o, list):
        if len(o) == 2 and isinstance(o[0], str) and o[0] in ZT:
            return ['nr', rm[o[1]]] if o[0] == 'zr' else ['nc', cm[o[1]]] if o[0] == 'zc' else ['n', sm[o[1]]]
        return [remap(x, rm, cm, sm) for x in o]
    if isinstance(o, dict):
        return {k: remap(x, rm, cm, sm) for k, x in o.items()}
    return o


def check_orig(full, origp, mp):
    rm, cm, sm, km, m = maps(mp)
    orig = json.load(open(origp))
    for key, n0 in (('raw', len(orig['raw'])), ('closed', len(orig['closed'])), ('sources', len(orig['sources'])),
                    ('controls', len(orig['controls']))):
        need(m['base'][key] == n0, 'map base %s' % key)
        for i in range(n0):
            need(remap(orig[key][i], rm, cm, sm) == full[key][i], '%s %d changed beyond its references' % (key, i))
    need(orig['root'] == full['root'] and orig.get('meta') == full.get('meta'), 'root / meta changed')
    need(set(full) == set(orig), 'top-level keys changed')
    need(len(full['raw']) == len(orig['raw']) + len(rm) and len(full['closed']) == len(orig['closed']) + len(cm) and
         len(full['sources']) == len(orig['sources']) + len(sm) and
         len(full['controls']) == len(orig['controls']) + len(km), 'appended object counts')
    return 'original objects unchanged except references (%d raw, %d closed, %d sources, %d controls)' % (
        len(orig['raw']), len(orig['closed']), len(orig['sources']), len(orig['controls']))


def check_zbs(full, zp, mp):
    rm, cm, sm, km, m = maps(mp)
    need(hashlib.sha256(open(zp, 'rb').read()).hexdigest() == ZBS_FULL_SHA256, 'zbs_full.json is not the pinned parse')
    z = json.load(open(zp))
    for i, ni in rm.items():
        P = copy.deepcopy(z['raw'][i])
        for pc in P['pieces']:
            T = pc if pc['kind'] == 'leaf' else pc['t']
            T['c'] = km[T['c']]
        P = remap(P, rm, cm, sm); P['zbs'] = 'r%d' % i
        need(full['raw'][ni] == P, 'raw %d (ZBS %d) differs from the parse' % (ni, i))
    for j, nj in cm.items():
        Q = remap(z['closed'][j], rm, cm, sm); Q['zbs'] = 'q%d' % j
        need(full['closed'][nj] == Q, 'closed %d (ZBS %d) differs from the parse' % (nj, j))
    for h, nh in sm.items():
        s = remap(z['sources'][h], rm, cm, sm); s['zbs'] = 's%d' % h
        need(full['sources'][nh] == s, 'source %d (ZBS %d) differs from the parse' % (nh, h))
    for c, nc in km.items():
        k = full['controls'][nc]
        need(all(k[f] == z['controls'][c][f] for f in ('p', 'mu', 'w', 'beta', 'x', 'lxU', 'l1mL')), 'control %d data' % c)
        need('cert' in k and 'lemmaD' not in k and k['zbs'] == 'c%d' % c, 'control %d kind' % c)
    return 'appended objects equal the parsed ZBS objects (%d raw, %d closed, %d sources, %d controls)' % (
        len(rm), len(cm), len(sm), len(km))


def main(argv):
    fp = argv[0]
    try:
        full = json.load(open(fp))
        no_zbs(full)
        print('no ZBS reference ("zr", "zc", "z") anywhere in %s' % fp)
        n = fields(full)
        print('%d profile/source references and %d control references in range; counts: raw %d, closed %d, sources %d, '
              'controls %d' % (n['refs'], n['ctl_refs'], len(full['raw']), len(full['closed']), len(full['sources']),
                               len(full['controls'])))
        rest = argv[1:]
        while rest:
            if rest[0] == '--orig':
                print(check_orig(full, rest[1], rest[2])); rest = rest[3:]
            elif rest[0] == '--zbs':
                print(check_zbs(full, rest[1], rest[2])); rest = rest[3:]
            else:
                raise SystemExit('unknown option %r' % rest[0])
    except Refused as e:
        print('FULL CHECK REFUSED: %s' % e)
        return 1
    print('FULL CHECK OK')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
