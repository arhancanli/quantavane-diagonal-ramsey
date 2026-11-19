# Stage 2a (item Z14): the 1,128 global line inequalities, proved by two programs (19 Nov 2026, 14:3x +04)

Claim. For every line (c, d) in ZBS's list (theorem lu_wang_lines_P0r12 of ZBS's Bridge/P06LinesP0r12.lean @ c2875f33,
equal as rationals and in order to zbs_bank.json's lines):  f-hat(lambda) <= c + d lambda  for ALL lambda > 0,
where f is Lu-Wang's source (f(t) = (1+t) log(1+t) - t log t + t e^{-t} P(t), P the cubic Hermite interpolant of their
data/source.json, SHA-256 f3e4a4ea...c08c) and f-hat(lambda) = f(lambda) on (0, 1], lambda f(1/lambda) on [1, inf).
Equivalent form checked: for t in (0, 1], (O1) f(t) <= c + d t and (O2) f(t) <= d + c t (t = 1/lambda on lambda >= 1).
This replaces ZBS's Lean-only theorem and also makes ZBS's Lemma 2.3 unnecessary for the lines.

Programs (written separately; different arithmetic, different method, different source of the line list):
- lines_A.py (SHA-256 49ffc856...b3d6ff): exact Fractions + the lab's own dyadic intervals (ivA.py, 256 bits, pinned);
  NO concavity used: an explicit bound on (0, t0] (t0 <= 1/e a node chosen per line) and, on every Hermite piece,
  the second-order Taylor form at midpoints with bisection (depth <= 90). Lines from zbs_bank.json (pinned).
- lines_B.py (SHA-256 a9820baf...22efa83): python-flint 0.9.0 Arb at 400 bits + fmpq; checks the Hermite
  C^1 identities exactly, certifies f'' < 0 on all 2,279 pieces (so g = line - f is convex on [0, 1]), then the convex
  tangent bound at a point m located by bisection of f' - slope. Lines read from ZBS's Lean file (pinned, SHA-256
  aeac27eb...56ba).

Results (logs in this folder; full per-line outputs in runs/*.json.gz):
- Program A: 2,256 line-orientations (1,128 x 2), 0 failed, ALL LINES CERTIFIED; smallest midpoint gap 1.131e-25
  (line 1014, O2). linesA_full_20261119.log.
- Program B: 2,256 line-orientations, 0 failed, ALL LINES CERTIFIED; concavity certified on every piece; smallest
  certified gap lower bound 1.119e-25 (line 1019, O2). linesB_full_20261119.log.
- Red controls (lines_red_green_20261119.log): the 5 thinnest line-orientations (1019/O2, 1014/O2, 224/O1, 1059/O2,
  934/O2; gaps 1.12e-25 to 1.24e-25) with the intercept lowered by 3e-25: exactly these 5 FAIL in both programs (the
  untouched other orientations of the same lines pass). Green control: 1019/O2 lowered by 5e-26 (< its gap) passes in
  both (gaps 6.96e-26 in A, 6.19e-26 in B).
Observation: ZBS's lines are tangents of f-hat rounded up by about 1e-25; both programs resolve this.

## After the code audit (19 Nov 2026, 18:2x +04)

Code referee ref6 (../REFEREE_CODE_AUDIT_20261119.md): 2a PASS, sound, NITs only. Applied: L-1 (lines_A's usage text now
gives the forms the code accepts, --lines=i,j,... and --tamper=i:o:delta,...), L-2 / S-1 (both programs refuse an option
without '=', an unknown key and a repeated key, so a red control can no longer run untampered by a typo), L-3
(lines_B's statement-form check now searches the statement of lu_wang_lines_P0r12 itself, from the theorem name to its
':=', not the whole file). Recorded as known limitations: L-4 (the Hermite C^1 checks are identities of the construction
and cannot fail on any data) and L-5 (Bridge/P06LinesP0r12.lean has the lab's SHA-256 pin but no git-blob provenance;
its list equals the blob-verified T.lean list).
New versions (full values in ../../MANIFEST.sha256): lines_A.py e4821d1e1148dc65..., lines_B.py f0c50bc6b13ba4ff...
Re-run in full by ../rerun_after_audit_20261119.sh:
- Program A: 2,256 line-orientations, 0 failed, ALL LINES CERTIFIED; smallest midpoint gap 1.131e-25 (line 1014, O2).
  linesA_full_rerun_20261119.log.
- Program B: 2,256, 0 failed, ALL LINES CERTIFIED; concavity on all 2,279 pieces; smallest certified gap 1.1194e-25
  (line 1019, O2). linesB_full_rerun_20261119.log.
- Both outputs equal the first runs' line by line (only 'seconds' differs): runs/lines{A,B}_full_rerun_20261119.json.gz.
- Red and green (lines_red_green_rerun_20261119.log): exactly 1019/O2, 1014/O2, 224/O1, 1059/O2, 934/O2 FAIL in both
  programs when lowered by 3e-25; 1019/O2 lowered by 5e-26 passes in both (gaps 6.956e-26 A, 6.1938e-26 B). Option
  controls: '--tamper 1019:2:...' (space) and an unknown key are REFUSED by both programs.
