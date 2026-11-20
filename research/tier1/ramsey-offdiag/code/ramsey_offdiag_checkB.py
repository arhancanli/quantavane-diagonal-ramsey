#!/usr/bin/env python3
"""Checker B: independent exact checker for the off-diagonal certificate.

usage: ramsey_offdiag_checkB.py BANK.json CERT.json [OUT.json]

Written from the specification only.  All accept/refuse decisions use exact
rationals (python-flint 0.9.0 fmpq); no floats.  On acceptance it prints a JSON
summary with "ok": true and exits 0; on any failed check or malformed input it
prints a line starting "REFUSED:" and exits 2.

What is checked
---------------
Tiling: cells[0].lo == g_lo > 0, lo < hi <= 1 in each cell, each next lo equals
the previous hi, the last hi == 1, v_lo > 0 and v_hi > 0.  Per cell
Phi(g) = v_lo + (v_hi - v_lo) (g - lo) / (hi - lo) on [lo, hi], and for EVERY
real g in [lo, hi]:
  src  AB : A_h + g B_h <= Phi(g)          src  BA : B_h + g A_h <= Phi(g)
  pair    : p_R + p_S <= 1, [lo, hi] inside I_R, [1/hi, 1/lo] inside I_S,
            L_R(g) <= Phi(g) and g L_S(1/g) <= Phi(g).

Reduction of "for every real g" to finitely many exact checks
--------------------------------------------------------------
Let D(g) = Phi(g) - bound(g).  In every case below D is continuous on [lo, hi]
and affine on each piece of an explicit finite partition of [lo, hi]; an affine
function is >= 0 on a closed interval iff it is >= 0 at both ends, so D >= 0 on
[lo, hi] iff D >= 0 at every partition point.  We evaluate D exactly there.

1. src: A + gB (or B + gA) is affine, Phi is affine, so D is affine on [lo, hi].
   Points: lo, hi.

2. pair, R side: L_R is continuous and affine between consecutive knots.  The
   knots of R strictly inside (lo, hi) cut [lo, hi] into pieces with no knot in
   their interior, so L_R, hence D, is affine on each piece.
   Points: lo, hi, and every knot x of R with lo < x < hi.

3. pair, S side: F(g) = g L_S(1/g).  t = 1/g maps [lo, hi] decreasingly and
   bijectively onto [1/hi, 1/lo] (lo >= g_lo > 0).  On a piece [x_j, x_{j+1}] of
   S, L_S(t) = c + d t with d the slope and c = y_j - d x_j, so for t = 1/g,
   F(g) = g (c + d/g) = c g + d, which is affine in g.  Breakpoints of F in g are
   therefore exactly g = 1/t for knots t of S, and the knots t strictly inside
   (1/hi, 1/lo) give breakpoints 1/t strictly inside (lo, hi).  F is continuous
   (L_S is continuous and 1/g is continuous for g > 0), so D is continuous and
   affine between consecutive breakpoints.
   Points: lo, hi, and g = 1/t for every knot t of S with 1/hi < t < 1/lo.

Profile values are computed exactly by linear interpolation on the segment that
contains the point (exact knot value at a knot).  The containment checks are
done before any evaluation, so every evaluation point lies in the profile's
interval [xs[0], xs[-1]].  Every cell is checked; the count of checked cells is
compared with the number of cells before acceptance.

The e^Phi column in the summary is reporting only: an exact rational upper bound
from the Taylor series with Lagrange remainder, rounded up to 7 decimals.
"""

import sys

EXIT_REFUSED = 2

PINNED_BANKS = {
    "32bcafd3fccbf094c83cc942669b3b843f09a3b10f87a6bd6a465d112bb07af8": "certCD3-full",
    "38091eed691b3ffa954d81e9658885cb68fb30e4e46ae76ddc376444f69ee468": "certK3-full",
    # added 20 Nov 2026 by the lane (pin only; no other change): the extended-range bank
    "d3c8cd100f97d7cfcf4ac354d8bd71d5cf6e3c627782ef1049d56ff0177f6e86": "certX8-full",
}

TABLE_G = ["1/8", "3/20", "4/25", "17/100", "9/50", "19/100",  # first six added 20 Nov 2026 (reporting only)
           "1/5", "21/100", "1/4", "3/10", "1/3", "2/5", "1/2", "3/5", "2/3",
           "7/10", "3/4", "4/5", "17/20", "9/10", "19/20", "99/100", "1"]


class Refused(Exception):
    pass


def refuse(msg):
    raise Refused(msg)


# ---------------------------------------------------------------- environment

def _environment():
    if (not __debug__) or sys.flags.optimize:
        refuse("refusing to run under python -O")
    try:
        import flint
    except Exception as e:  # noqa: BLE001
        refuse("python-flint not importable: %r" % (e,))
    if getattr(flint, "__version__", None) != "0.9.0":
        refuse("python-flint version must be 0.9.0, found %r"
               % (getattr(flint, "__version__", None),))
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    return flint


flint = None
fmpq = None


def _bind():
    global flint, fmpq
    flint = _environment()
    fmpq = flint.fmpq


# ---------------------------------------------------------------- parsing

import re  # noqa: E402
import json  # noqa: E402
import hashlib  # noqa: E402
from bisect import bisect_left, bisect_right  # noqa: E402

_RAT_RE = re.compile(r"(-?)([0-9]+)(?:/([0-9]+))?")


def rat(s, what):
    """Strict rational from a string 'n', '-n', 'n/d' or '-n/d' (ASCII digits, d > 0)."""
    if type(s) is not str:
        refuse("%s: expected a rational string, got %s" % (what, type(s).__name__))
    m = _RAT_RE.fullmatch(s)
    if m is None:
        refuse("%s: malformed rational string %r" % (what, s[:80]))
    num = int(m.group(2))
    den = int(m.group(3)) if m.group(3) is not None else 1
    if den == 0:
        refuse("%s: zero denominator in %r" % (what, s[:80]))
    if m.group(1):
        num = -num
    return fmpq(num, den)


def index(x, n, what):
    if type(x) is not int:  # rejects bool, float, str, None
        refuse("%s: index must be a JSON integer, got %s %r"
               % (what, type(x).__name__, x))
    if not (0 <= x < n):
        refuse("%s: index %d out of range [0, %d)" % (what, x, n))
    return x


def _no_dup_pairs(pairs):
    d = dict(pairs)
    if len(d) != len(pairs):
        seen = set()
        for k, _ in pairs:
            if k in seen:
                refuse("duplicate JSON key %r" % (k,))
            seen.add(k)
    return d


def _bad_constant(name):
    refuse("non-finite JSON constant %s" % name)


def load_json_bytes(data, what):
    try:
        obj = json.loads(data, object_pairs_hook=_no_dup_pairs,
                         parse_constant=_bad_constant)
    except Refused as e:
        refuse("%s: %s" % (what, e))
    except (ValueError, UnicodeDecodeError, RecursionError) as e:
        refuse("%s: invalid JSON: %s" % (what, str(e)[:200]))
    if type(obj) is not dict:
        refuse("%s: top level must be a JSON object" % what)
    return obj


def read_file(path, what):
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as e:
        refuse("%s: cannot read %r: %s" % (what, path, e))
    return data, hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------- bank access

class Profile(object):
    __slots__ = ("name", "p", "xs", "ys")

    def __init__(self, name, p, xs, ys):
        self.name, self.p, self.xs, self.ys = name, p, xs, ys


class Bank(object):
    def __init__(self, obj):
        self.obj = obj
        self._prof = {}
        self._src = {}

    def _list(self, key):
        v = self.obj.get(key, None)
        if type(v) is not list:
            refuse("bank: key %r missing or not a list" % key)
        return v

    def profile(self, ref, what):
        if type(ref) is not list or len(ref) != 2:
            refuse("%s: profile reference must be a 2-element list" % what)
        name, i = ref
        if type(name) is not str or name not in ("raw", "closed"):
            refuse("%s: profile name must be 'raw' or 'closed', got %r" % (what, name))
        lst = self._list(name)
        index(i, len(lst), what + " index")
        key = (name, i)
        if key in self._prof:
            return self._prof[key]
        tag = "bank.%s[%d]" % key
        pr = lst[i]
        if type(pr) is not dict:
            refuse("%s: profile is not an object" % tag)
        for k in ("p", "xs", "ys"):
            if k not in pr:
                refuse("%s: missing key %r" % (tag, k))
        p = rat(pr["p"], tag + ".p")
        if not (fmpq(0) < p < fmpq(1)):
            refuse("%s: density p=%s not in (0, 1)" % (tag, p))
        xs_raw, ys_raw = pr["xs"], pr["ys"]
        if type(xs_raw) is not list or type(ys_raw) is not list:
            refuse("%s: xs and ys must be lists" % tag)
        if len(xs_raw) != len(ys_raw) or len(xs_raw) < 2:
            refuse("%s: need len(xs) == len(ys) >= 2 (got %d, %d)"
                   % (tag, len(xs_raw), len(ys_raw)))
        xs = [rat(x, "%s.xs[%d]" % (tag, j)) for j, x in enumerate(xs_raw)]
        ys = [rat(y, "%s.ys[%d]" % (tag, j)) for j, y in enumerate(ys_raw)]
        if not (xs[0] > 0):
            refuse("%s: xs[0] = %s must be > 0" % (tag, xs[0]))
        for j in range(len(xs) - 1):
            if not (xs[j] < xs[j + 1]):
                refuse("%s: xs not strictly increasing at %d" % (tag, j))
        prof = Profile(tag, p, xs, ys)
        self._prof[key] = prof
        return prof

    def source(self, h, what):
        lst = self._list("sources")
        index(h, len(lst), what)
        if h in self._src:
            return self._src[h]
        tag = "bank.sources[%d]" % h
        s = lst[h]
        if type(s) is not dict:
            refuse("%s: not an object" % tag)
        for k in ("A", "B"):
            if k not in s:
                refuse("%s: missing key %r" % (tag, k))
        A = rat(s["A"], tag + ".A")
        B = rat(s["B"], tag + ".B")
        if not (A > 0 and B > 0):
            refuse("%s: need A > 0 and B > 0" % tag)
        self._src[h] = (A, B)
        return A, B


def L(prof, x):
    """Exact value of the piecewise-linear profile at x (x must be in its interval)."""
    xs, ys = prof.xs, prof.ys
    if x < xs[0] or x > xs[-1]:
        refuse("internal: evaluation point %s outside %s interval" % (x, prof.name))
    j = bisect_right(xs, x) - 1
    if j >= len(xs) - 1:
        return ys[-1]
    if xs[j] == x:
        return ys[j]
    return ys[j] + (ys[j + 1] - ys[j]) * (x - xs[j]) / (xs[j + 1] - xs[j])


# ---------------------------------------------------------------- cell checks

def phi(c, g):
    return c["v_lo"] + (c["v_hi"] - c["v_lo"]) * (g - c["lo"]) / (c["hi"] - c["lo"])


def check_src(c, A, B, orient, where):
    """Returns (min slack, point).  Affine bound: endpoints suffice."""
    best = None
    for g in (c["lo"], c["hi"]):
        bound = (A + g * B) if orient == "AB" else (B + g * A)
        s = phi(c, g) - bound
        if s < 0:
            refuse("%s: src bound exceeds Phi at g=%s by %s" % (where, g, -s))
        if best is None or s < best[0]:
            best = (s, g)
    return best


def r_points(c, R):
    lo, hi = c["lo"], c["hi"]
    xs = R.xs
    a = bisect_right(xs, lo)
    b = bisect_left(xs, hi)
    return [lo, hi] + xs[a:b]


def s_points(c, S):
    lo, hi = c["lo"], c["hi"]
    tlo, thi = 1 / hi, 1 / lo
    xs = S.xs
    a = bisect_right(xs, tlo)
    b = bisect_left(xs, thi)
    return [lo, hi] + [1 / t for t in xs[a:b]]


def check_pair(c, R, S, where):
    """Returns ((min slack R side, g), (min slack S side, g))."""
    lo, hi = c["lo"], c["hi"]
    if R.p + S.p > 1:
        refuse("%s: p_R + p_S = %s + %s > 1" % (where, R.p, S.p))
    if not (R.xs[0] <= lo and hi <= R.xs[-1]):
        refuse("%s: [lo, hi] = [%s, %s] not inside I_R = [%s, %s] (%s)"
               % (where, lo, hi, R.xs[0], R.xs[-1], R.name))
    tlo, thi = 1 / hi, 1 / lo
    if not (S.xs[0] <= tlo and thi <= S.xs[-1]):
        refuse("%s: [1/hi, 1/lo] = [%s, %s] not inside I_S = [%s, %s] (%s)"
               % (where, tlo, thi, S.xs[0], S.xs[-1], S.name))
    bestR = None
    for g in r_points(c, R):
        s = phi(c, g) - L(R, g)
        if s < 0:
            refuse("%s: L_R(g) exceeds Phi at g=%s by %s" % (where, g, -s))
        if bestR is None or s < bestR[0]:
            bestR = (s, g)
    bestS = None
    for g in s_points(c, S):
        s = phi(c, g) - g * L(S, 1 / g)
        if s < 0:
            refuse("%s: g*L_S(1/g) exceeds Phi at g=%s by %s" % (where, g, -s))
        if bestS is None or s < bestS[0]:
            bestS = (s, g)
    return bestR, bestS


# ---------------------------------------------------------------- reporting helpers

def _ceil_div(n, d):
    return -((-n) // d)


def ceil_grid(q, D):
    return fmpq(_ceil_div(int(q.p) * D, int(q.q)), D)


def _taylor_exp_upper(x, N):
    """Upper bound for e^x, 0 <= x <= 1: sum_{n<=N} x^n/n! + 3 x^(N+1)/(N+1)!."""
    s = fmpq(0)
    term = fmpq(1)
    for n in range(N + 1):
        if n > 0:
            term = term * x / n
        s += term
    return s + 3 * term * x / (N + 1)


def exp_upper_7(v):
    """Decimal string, rounded up to 7 places, of an exact upper bound for e^v (v >= 0)."""
    if v < 0:
        refuse("internal: exp bound requested for negative value")
    D = 10 ** 60
    m = int(v.p) // int(v.q)
    r = v - m
    e_up = ceil_grid(_taylor_exp_upper(fmpq(1), 60), D)
    res = ceil_grid(_taylor_exp_upper(r, 60), D)
    for _ in range(m):
        res = ceil_grid(res * e_up, D)
    k = _ceil_div(int(res.p) * 10 ** 7, int(res.q))
    return "%d.%07d" % (k // 10 ** 7, k % 10 ** 7)


def dec(q, places=12):
    """Exact decimal rendering (truncated toward zero) for display only."""
    n, d = int(q.p), int(q.q)
    sign = "-" if n < 0 else ""
    n = abs(n)
    k = n * 10 ** places // d
    return "%s%d.%0*d" % (sign, k // 10 ** places, places, k % 10 ** places)


# ---------------------------------------------------------------- main

def parse_cert(cert, bank_sha):
    for k in ("bank_sha256", "g_lo", "cells"):
        if k not in cert:
            refuse("cert: missing key %r" % k)
    if type(cert["bank_sha256"]) is not str or cert["bank_sha256"] != bank_sha:
        refuse("cert: bank_sha256 %r does not match the bank file's SHA-256 %s"
               % (cert["bank_sha256"], bank_sha))
    g_lo = rat(cert["g_lo"], "cert.g_lo")
    if not (g_lo > 0):
        refuse("cert: g_lo must be > 0")
    raw_cells = cert["cells"]
    if type(raw_cells) is not list or len(raw_cells) == 0:
        refuse("cert: cells must be a non-empty list")
    cells = []
    one = fmpq(1)
    for i, rc in enumerate(raw_cells):
        w = "cell %d" % i
        if type(rc) is not dict:
            refuse("%s: not an object" % w)
        for k in ("kind", "lo", "hi", "v_lo", "v_hi"):
            if k not in rc:
                refuse("%s: missing key %r" % (w, k))
        c = {"i": i, "raw": rc}
        for k in ("lo", "hi", "v_lo", "v_hi"):
            c[k] = rat(rc[k], "%s.%s" % (w, k))
        kind = rc["kind"]
        if type(kind) is not str or kind not in ("src", "pair"):
            refuse("%s: unknown kind %r" % (w, kind))
        c["kind"] = kind
        if kind == "src":
            for k in ("h", "orient"):
                if k not in rc:
                    refuse("%s: missing key %r" % (w, k))
            if type(rc["h"]) is not int:
                refuse("%s: h must be a JSON integer, got %s %r"
                       % (w, type(rc["h"]).__name__, rc["h"]))
            if type(rc["orient"]) is not str or rc["orient"] not in ("AB", "BA"):
                refuse("%s: orient must be 'AB' or 'BA', got %r" % (w, rc["orient"]))
        else:
            for k in ("R", "S"):
                if k not in rc:
                    refuse("%s: missing key %r" % (w, k))
                ref = rc[k]
                if type(ref) is not list or len(ref) != 2:
                    refuse("%s.%s: must be a 2-element list" % (w, k))
                if type(ref[0]) is not str or ref[0] not in ("raw", "closed"):
                    refuse("%s.%s: name must be 'raw' or 'closed'" % (w, k))
                if type(ref[1]) is not int:
                    refuse("%s.%s: index must be a JSON integer, got %s %r"
                           % (w, k, type(ref[1]).__name__, ref[1]))
        # tiling
        if not (c["lo"] < c["hi"]):
            refuse("%s: need lo < hi" % w)
        if not (c["hi"] <= one):
            refuse("%s: need hi <= 1" % w)
        if not (c["v_lo"] > 0 and c["v_hi"] > 0):
            refuse("%s: need v_lo > 0 and v_hi > 0" % w)
        if i == 0:
            if c["lo"] != g_lo:
                refuse("cell 0: lo %s != g_lo %s" % (c["lo"], g_lo))
        elif c["lo"] != cells[-1]["hi"]:
            refuse("%s: lo %s != previous hi %s (tiling broken)"
                   % (w, c["lo"], cells[-1]["hi"]))
        cells.append(c)
    if cells[-1]["hi"] != one:
        refuse("cert: last hi %s != 1" % cells[-1]["hi"])
    return g_lo, cells


def run(argv):
    _bind()
    if len(argv) not in (3, 4):
        refuse("usage: %s BANK.json CERT.json [OUT.json]" % argv[0])
    bank_path, cert_path = argv[1], argv[2]
    out_path = argv[3] if len(argv) == 4 else None

    bank_bytes, bank_sha = read_file(bank_path, "bank")
    if bank_sha not in PINNED_BANKS:
        refuse("bank SHA-256 %s is not one of the pinned banks" % bank_sha)
    label = PINNED_BANKS[bank_sha]
    cert_bytes, cert_sha = read_file(cert_path, "cert")
    cert = load_json_bytes(cert_bytes, "cert")
    g_lo, cells = parse_cert(cert, bank_sha)

    bank = Bank(load_json_bytes(bank_bytes, "bank"))
    del bank_bytes

    counts = {"src": 0, "pair": 0}
    mins = {"src": None, "pair": None, "pair_R": None, "pair_S": None}
    points = {"src": 0, "pair_R": 0, "pair_S": 0}
    checked = 0

    def upd(key, s, i, g):
        if mins[key] is None or s < mins[key][0]:
            mins[key] = (s, i, g)

    for c in cells:
        i = c["i"]
        w = "cell %d" % i
        rc = c["raw"]
        if c["kind"] == "src":
            A, B = bank.source(rc["h"], w + ".h")
            s, g = check_src(c, A, B, rc["orient"], w)
            upd("src", s, i, g)
            points["src"] += 2
        else:
            R = bank.profile(rc["R"], w + ".R")
            S = bank.profile(rc["S"], w + ".S")
            (sr, gr), (ss, gs) = check_pair(c, R, S, w)
            points["pair_R"] += len(r_points(c, R))
            points["pair_S"] += len(s_points(c, S))
            upd("pair_R", sr, i, gr)
            upd("pair_S", ss, i, gs)
            upd("pair", sr, i, gr)
            upd("pair", ss, i, gs)
        counts[c["kind"]] += 1
        checked += 1
    if checked != len(cells) or counts["src"] + counts["pair"] != len(cells):
        refuse("internal: checked %d of %d cells" % (checked, len(cells)))

    # Phi table
    los = [c["lo"] for c in cells]
    table = []
    for gs in TABLE_G:
        g = rat(gs, "table g")
        if g == 1:
            c = cells[-1]
        else:
            j = bisect_right(los, g) - 1
            c = cells[j] if (j >= 0 and c_contains(cells[j], g)) else None
        if c is None:
            table.append({"g": gs, "cell": None, "phi": None,
                          "note": "g not covered by the certificate"})
            continue
        v = phi(c, g)
        table.append({"g": gs, "cell": c["i"], "phi": str(v), "phi_dec": dec(v, 10),
                      "exp_phi_upper_7dp": exp_upper_7(v)})

    def fmt_min(key):
        m = mins[key]
        if m is None:
            return None
        return {"slack": str(m[0]), "slack_dec": dec(m[0], 15),
                "cell": m[1], "g": str(m[2])}

    summary = {
        "checker": "B",
        "ok": True,
        "bank_label": label,
        "bank_sha256": bank_sha,
        "cert_sha256": cert_sha,
        "g_lo": str(g_lo),
        "n_cells": len(cells),
        "counts": counts,
        "points_checked": points,
        "min_slack": {"src": fmt_min("src"), "pair": fmt_min("pair")},
        "min_slack_pair_sides": {"R": fmt_min("pair_R"), "S": fmt_min("pair_S")},
        "phi_table": table,
    }
    return summary, out_path


def c_contains(c, g):
    return c["lo"] <= g < c["hi"]


def _write_out(path, obj):
    try:
        with open(path, "w") as f:
            json.dump(obj, f, indent=1)
            f.write("\n")
    except OSError as e:
        print("WARNING: could not write %s: %s" % (path, e), file=sys.stderr)


def main(argv):
    out_path = argv[3] if len(argv) == 4 else None
    try:
        summary, out_path = run(argv)
    except Refused as e:
        msg = str(e)
    except SystemExit:
        msg = "unexpected SystemExit"
    except BaseException as e:  # noqa: BLE001  any crash is a refusal
        msg = "internal error %s: %s" % (type(e).__name__, str(e)[:300])
    else:
        text = json.dumps(summary, indent=1)
        if out_path:
            _write_out(out_path, summary)
        print(text)
        return 0
    print("REFUSED: " + msg)
    if out_path:
        _write_out(out_path, {"checker": "B", "ok": False, "refused": msg})
    return EXIT_REFUSED


if __name__ == "__main__":
    sys.exit(main(sys.argv))
