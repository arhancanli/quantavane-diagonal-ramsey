# Code referee (ref6) of stages 2a, 2b and 2c: lines, source and cone programs (19 Nov 2026, 17:4x-18:2x +04)

A fresh, independent code referee. I read the programs against RESULT_2a.md, RESULT_2b.md, P4_SOURCE.md (P4.5, P4.6)
and RESULT_2c.md. I ran the programs, wrote separate models and verifiers of my own, and tried tampered inputs.
The audited programs and data were not modified: SHA-256 values match MANIFEST.sha256 and the RESULT files.
Scripts and logs are in the session scratchpad,
<scratch>/ref6/. That folder is not
durable, so the important outputs are quoted below.

## Verdicts

| Group | Programs | Verdict | Soundness |
| --- | --- | --- | --- |
| 2a lines | lines_A.py, lines_B.py | PASS | sound; NITs only |
| 2b source | source_A.py, source_B.py | PASS WITH FIXES | sound; the fixes are option handling and reporting only |
| 2c cone | parse_zbs_full.py, cone.py, ctl_certs.py, assemble_full.py, check_full.py, run_cone.sh | PASS | sound; NITs only |

No ERROR anywhere. No float enters a decision in any program (details at the end).

## Group 1: lines (2a). PASS

Answers:
- Small-t argument (lines_A.py:136-151, 167-170): correct. (1+t)log(1+t) <= t(1+t); t log(1/t) is increasing on
  (0, 1/e], and INV_E = 0.367879441171442321 < 1/e; t e^{-t} P(t) <= t max(0, sup P), with pplus[k] the maximum over
  cells 0..k-1, which cover [0, nodes[k]]. The bound must be strictly below alpha, and alpha <= alpha + beta t. The
  binary search keeps ok(lo) true as an invariant, so the k it returns is valid whether or not the computed bound is
  monotone.
- Taylor bound (lines_A.py:117-133): valid on every piece, including where f'' is large. It is the second-order
  Lagrange form on [t1, t2] inside one Hermite piece, where f is C^2. sup|f''| is an interval enclosure over the
  subinterval and includes the -1/T term, with T >= nodes[k] > 0. I re-derived f' and f''.
- Convex tangent bound in B (lines_B.py:132-156): nothing unproved is needed. f'' < 0 is certified on every piece,
  including (0, t1] through sup j'' < 1/(t1(1+t1)). C^1 holds across nodes by construction. f is continuous at 0. So
  g = L - f is convex on [0, 1], and the tangent at any m in (0, 1] (the one-sided derivative at m = 1) bounds g from
  below. The bisection only affects tightness, not soundness.
- Same 1,128 lines, and they are ZBS's: yes. zbs_bank.json lines (A), the theorem list of
  Bridge/P06LinesP0r12.lean (B, parsed with a tolerant parser of mine: 2,256 rationals), and T.lean's FQ `lines` are
  equal as rationals and in the same order. T.lean is checked against its git blob SHA-1.

Independent checks:
- Decimal model (Python `decimal`, 70 to 140 digits; no ivA, no Arb), maximising f - L over all 2,256 orientations:
  0 negative gaps. Smallest gap 1.119384e-25 (1019/O2), then 1014/O2, 224/O1, 1059/O2, 934/O2, matching both programs.
  In 1,128 orientations the maximum is at t = 1.
- I re-ran lines_B on all lines: ALL LINES CERTIFIED, smallest gap 1.1194e-25.
- Tight red/green tamper on 1019/O2. Lowered by 1.1195e-25 (true gap -6e-30): both FAIL. Lowered by 1.1193e-25 (true
  gap 8.4e-30): both pass, with gaps 8.6e-30 (A) and 8.4e-30 (B).

Findings (none touches soundness):
- NIT L-1, lines_A.py:16-17 against :156. The usage text says `[--lines i,j,...] [--tamper k:delta,...]`, but the
  code needs `--lines=...` and `--tamper=i:o:delta`. The space form crashes with int(''), so it fails safe.
- NIT L-2, lines_B.py:161. Arguments without '=' are silently dropped, so `--tamper 1019:2:x` would run untampered
  and print ALL LINES CERTIFIED. This only affects red controls.
- NIT L-3, lines_B.py:59. The statement-form check is a substring search over the whole file, not tied to the theorem.
  I checked that the only occurrence is the statement of lu_wang_lines_P0r12.
- NIT L-4, lines_B.py:69-70 and source_A.py:250-253. The Hermite C^1 checks are algebraic identities of the Hermite
  construction and cannot fail on any data. The statement is true, but P4.6 should not count it as a check of the data.
- NIT L-5. Bridge/P06LinesP0r12.lean is not in filelist.txt, so it has no git-blob provenance, only the lab's SHA-256
  pin. Its list equals the blob-verified T.lean `lines` exactly, so nothing in substance is missing.

## Group 2: source (2b). PASS WITH FIXES

Answers:
- Coverage of [1e-16, 1]: no gaps in either program. Each cell starts where the previous one ended (x = y), every
  cell lies inside one Hermite piece, and the first cell starts at max(a, alpha). The controls can be any positive
  values, so the choice of Lu-Wang cell cannot affect soundness. A: 73,302 cells; B: 73,302 of 73,302.
- Mean-value bound: valid. I re-derived Delta'(s) = (w+1) f' + l'(1 - s lambda*) - b + w log(rs) + w and l'. Every
  enclosure points the right way:
  - b at the midpoint is bounded above by b(lower end of A) (b is decreasing).
  - lambda* lies in [lambda*(A_hi), lambda*(A_lo)].
  - b over the cell lies in [b(A_hi), b(A_lo)].
  - A's upper bound for b is the concave tangent at l0 != 1, maximised over the bracket ends.
  - B's b comes from bracket ends ordered by monotonicity (psi increasing, f' decreasing).
- Uncertain brackets: both are valid. A's else-branch gives [1 - d, 1] or [1, 1/(1 - d)]; "straddles 1" is
  unreachable because the enclosures of f'(1) and f(1) - f'(1) are disjoint. B's undecided branch gives a valid but
  loose b (NIT S-4). Tested by importing the unmodified modules, at A = the midpoints of the f'(1) and f(1) - f'(1)
  enclosures, at +-1e-60 from them, at the corner, and at A = 1e-16, 5 and 30. Against a 140-digit Decimal model:
  0 violations in A, 0 in B.
- First-piece concavity test (source_A.py:256-262): right. On (0, hi], f'' <= -1/(hi(1+hi)) + sup j'' < 0, and the
  lo == 0 branch is kept under bisection.
- Floats: used only to propose bracket points in source_A. Every bracket is accepted only after exact interval sign
  checks.
- --require (margin probe): with '=' it behaves as documented (Delta(s) - TAU s > 0 in both Dm and Delta'). Near the
  threshold on the last cell, both programs fail at TAU = 7.7532e-7 and pass at 7.7531e-7. The Decimal model gives
  Delta(1) = 7.753163e-7. TAU = 7.76e-7 fails and 7.74e-7 passes in both. See GAP S-1 for the form without '='.

Independent checks:
- Decimal Delta at the reported argmin s = 0.994484636871508 with its controls: Delta/s = 7.837072e-7. The programs
  report 7.83707e-7. At s = 0.953, the cell where the RED probe stopped, Delta/s = 8.05e-7 < 1e-6, so that refusal is
  correct.
- Tampered controls: on three cells (s = 0.5, s = 0.1 in the right branch, s = 1e-12 in the geometric cells) I found
  by Decimal the w* where min Delta crosses 0. Called directly, both programs' cell certifiers CERTIFY at w* - 1e-5
  and REFUSE at w* + 1e-5; the true controls certify.
- Full re-run of source_B: ALL CELLS CERTIFIED, 0..73302 of 73302, 80,270 evaluations, min Delta/s 7.8371e-7. I did
  not repeat the full source_A run; my source_A runs were targeted.

Findings (none touches soundness of the recorded claim):
- GAP S-1, source_A.py:320, source_B.py:209 (same pattern as lines_B.py:161). Arguments without '=' and unknown keys
  are silently ignored.
  - Demonstrated: `--require 776/1000000000` (space) makes B print ALL CELLS CERTIFIED with require_tau "0", while
    `--require=776/1000000000` refuses. `--requre=...` (typo) makes A certify.
  - So a red margin probe can silently test nothing. The recorded probes used '=': the logs and JSON show require_tau
    and the expected refusals, so the recorded results stand.
  - Fix: refuse unknown or malformed options.
- GAP S-2, source_A.py:353-370 and source_B.py:251-270. An empty or partial range prints "ALL CELLS CERTIFIED" with
  exit 0.
  - Demonstrated: `--from=73302` gives 0 evaluations and "ALL CELLS CERTIFIED". A does not print the total cell count.
  - The recorded full runs cover 0..73302 of 73302.
  - Fix: print the covered range against the total, and use a separate headline (or a nonzero exit) unless the range
    is full.
- NIT S-3, source_A.py:24. The usage line omits --require; only the comment at :48 documents it.
- NIT S-4, source_B.py:160-165. In the undecided branch, lo_r defaults to 1, so the b enclosure also contains f'(1).
  Its width is about 0.21. This is valid (tested) but loose: if the branch were ever hit, the result would be a
  refusal, never a false certificate.
- NIT S-5, source_B.py:3. "Same claim as source_A.py", but B does not certify concavity itself; it relies on lines_B
  and source_A. P4.6 and RESULT_2b give the credit correctly.
- NIT S-6, source_A.py:287-288 and source_B.py:178-179. "b > 0" is checked at b(lower end of A_m), not at A(m). It is
  only a sanity check; P4.6 rightly derives b > 0 from P4.5(ii).

## Group 3: cone (2c). PASS

Answers:
- Closure complete: yes. It was recomputed from my own decode of the raw Lean files, covering children, closed R/S,
  source-cover PR/PB, terminal sources and controls, starting from the original certificates' references (478 direct:
  473 zr + 5 z). Result for both certificates: raw 1,902, closed 1,001, sources 2,713, controls 918, equal to the map
  keys.
- Remapping: nothing silently changed. My own regex decoder (no code shared with parse_zbs_full.py or zbs_pieces.py)
  read every D/TD/T/Data file and compared each appended object of BOTH full certificates against the Lean data, with
  references and control indices converted through the map. The comparison covered:
  - 1,902 raw profiles (p, xs, ys, min; 17,183 pieces; 304,695 route calls, child by child);
  - 1,001 closed profiles (11,592 pieces);
  - 2,713 sources (A, B, Lo, Hi, eps, eta, kL, kR; 1,493,877 cells);
  - 918 controls.

  0 mismatches. Each map is a bijection onto the appended index range.
- Original objects and root: kept. In each certificate every original object equals its counterpart after reference
  replacement (my own parallel walk; 24,777 references converted in K3 and 24,785 in CD3). The root, meta and the
  top-level key set ({raw, closed, sources, controls, root, meta}) are equal.
- Negative control of my verifier: swapping two raw and two source map entries gives 38 mismatches.
- check_full.py: it proves what it claims for these certificates. Under --zbs a wrong map entry, a wrong child or a
  wrong cover cell cannot pass, because each appended object must equal the remapped parse including its provenance
  tag. A consistent relabelling (swap two appended objects, their map entries and all their references) is correctly
  accepted: the meaning is unchanged. Synthetic tampers, run through the real cone.py, assemble_full.py and
  check_full.py:

  | Tamper | Result | Expected? |
  | --- | --- | --- |
  | ZBS route child changed | REFUSED | yes |
  | source cell lo changed | REFUSED | yes |
  | cover PB pointing at our closed profile | REFUSED | yes |
  | pair S changed | REFUSED | yes |
  | terminal source changed | REFUSED | yes |
  | piece control changed | REFUSED | yes |
  | our reference pointing at the wrong ZBS raw | REFUSED | yes |
  | our field changed | REFUSED | yes |
  | piece dropped | REFUSED | yes |
  | extra key in an appended source | REFUSED | yes |
  | control data changed | REFUSED | yes |
  | map entries swapped, file unchanged | REFUSED | yes |
  | root z changed | REFUSED | yes |
  | clean | OK | yes |
  | consistent relabelling | OK | yes |
  | other top-level key changed | OK | NIT C-1 |
  | garbage control cert | OK | yes, the checkers' job; see NIT C-2 |
- No ZBS dependence: I ran checker B's own driver logic (runB.main copied, unmodified bankB/ctlB) with a bank that
  keeps only ZBS's 1,128 lines (raw, closed, A, B and ctl emptied).
  - certK3-full: ok, z = 1248056263241/10^12, 2,641 controls verified.
  - certCD3-full: ok, z = 311946616731/250000000000, 2,747 controls verified (25 Lemma D).
  - So only the lines remain referenced, and every appended control's Lemma C certificate passes ctlB.
- ZBS files: all 1,523 files in filelist.txt match their git blob SHA-1 (0 mismatches).
- Hashes: certK3-full = 38091eed...; certCD3-full = 32bcafd3...; originals 76f9679a... and 896dc046...; all as
  recorded. zbs_full.json = a2395f138b9ee24a2a5409debe44bb15443f544179fc75837d53c79b195903ca (not recorded anywhere;
  see NIT C-3).

Findings (none touches soundness):
- NIT C-1 (latent), check_full.py:103-104. Top-level keys other than root/meta are compared by name only. Demonstrated
  on a synthetic certificate: changing a 'params' key passes. The real certificates have no such key.
- NIT C-2, check_full.py:128-131. For appended controls it checks only that 'cert' is present, and extra keys are
  allowed. Validity is left to the checkers, which verify every control; I confirmed this with checker B.
- NIT C-3. zbs_full.json is not pinned by hash (RESULT_2c, logs, assemble and check_full), so --zbs is relative to
  whatever file is passed. My direct Lean comparison covers this gap for the actual certificates. Record the hash.
- NIT C-4, check_full.py:88 and 119. A missing map entry raises an uncaught KeyError (traceback, exit 1) instead of
  "REFUSED". It fails safe.
- NIT C-5, run_cone.sh:27-28. The checkers still receive the full zbs_bank.json and would silently resolve any leftover
  zr/zc/z reference from it. check_full's no_zbs guards against this, and the lines-only-bank run above confirms it in
  practice. A lines-only bank would make this hold by construction.

## Floats

No float enters a decision. Float uses found:
- source_A: proposals only (Piece.kf, Src.tf, f/f1/f2_float, _float_root); every bracket is re-checked in exact
  intervals; display at :369.
- lines_A: display only (:197, :204).
- source_B: arb .mid() at :200, used only to pick the reported minimum.
- cone.py:119: reported min eps/eta only.
- source_margins.py: exact Fraction minimum, floats printed only.
- ctl_certs.py: the builder's float_bound is a record; acceptance is ctlA/ctlB.

lines_B, check_full, assemble_full and parse_zbs_full use no floats.

## Other

- Not repeated: the full runs of lines_A and source_A, and checker A on the full certificates. Their existing logs
  were read; my runs of these were targeted.
- At 18:13, .claude-flow/ and .swarm/ appeared in papers/diagonal-ramsey-2026. These are plugin-hook state, most
  likely written when this session's working directory changed to that folder. I did not create or remove them by
  command. Check `git ls-files` and .gitignore before committing.
- Nothing was written to the SSD; ref6_work stayed empty and was removed.
