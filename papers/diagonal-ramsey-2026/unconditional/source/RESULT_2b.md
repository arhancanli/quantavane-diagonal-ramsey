# Stage 2b (item L4): Lu-Wang's source certificate, re-proved by two programs (19 Nov 2026, 15:1x +04)

Claim (the hypotheses of Lemma B.1' in P4_SOURCE.md for Lu-Wang's f on [10^-16, 1]):
 (S0) f'(1) > 0 and 2 f'(1) > f(1);
 (S1) for every s in [10^-16, 1], with (r, w) Lu-Wang's rational controls of the cell of data/source_cells.json
      containing the midpoint of our cell (SHA-256 055d8695...4bff; used only as data), mu = r s,
      p0 = 1 - e^{-f'(s)}, X = (1 - mu)^w p0^{1/(1 - mu)}, A = -log X, b(A) = sup_l (f-hat(l) - A l) and Y = e^{-b(A)}:
      0 < mu < 1, 0 < p0 < 1, b(A) > 0 and Delta(s) = (w + 1) f(s) + log X + s log Y + w s log mu > 0.
Together with the concavity and C^1 property of f certified by lines_B.py (stage 2a), this gives Theorem 2.2' (P4.6)
for every eps > 2 h(10^-16) = 7.57e-15. Written from Lu-Wang's Appendix B text, not their code; our certificate
design differs from theirs (we use the conjugate b(A) with Danskin's derivative b' = -lambda*, a mean-value bound per
cell, and no t -> 0 normalisation, which a fixed eps makes unnecessary).

Programs (final versions, re-run 19 Nov 15:3x-15:5x after the P4 referee; SHA-256 prefixes 6c7b1df64add08b3... and c579ee486dc1b4a6...,
full values in the folder MANIFEST.sha256):
- source_A.py: exact Fractions + ivA dyadic intervals (256 bits, pinned); first certifies (S0') f C^1 on (0, 1] (exact
  Hermite identities) and f'' < 0 on every Hermite piece (independently of lines_B.py; so concavity is certified by two
  programs); lambda* bracketed by exact interval sign checks around float proposals; b bounded above by a concave
  tangent bound over the bracket and below by its definition (the branch "bracket straddles 1" refuses; it is
  unreachable); cells: Hermite pieces, geometric with ratio 1 + 2^-11 below 1/8, bisection up to depth 60.
- source_B.py: Arb at 300 bits (python-flint 0.9.0, pinned); b through the tangency parameter (b = psi(t) on the left
  branch, f'(u) on the right, f(1) - A at the corner); brackets by rational bisection with both ends at CERTIFIED signs
  (no floating point); its own cell list.
Results:
- Program A: f C^1 and f'' < 0 on all 2,279 pieces; ALL CELLS CERTIFIED, 73,302 cells, 80,328 evaluations.
- Program B: ALL CELLS CERTIFIED, 73,302 cells, 80,270 evaluations.
- Both report the smallest value of Delta(m)/m over cell MIDPOINTS m: 7.8371e-7 (near s = 0.99448). The certified
  statement is Delta > 0 on every whole cell (mean-value bound); the true minimum of Delta(s)/s is smaller, about
  7.75e-7 at s = 1 (referee P4, independent 80-digit evaluation), and Delta(s)/s is not uniform: about 1.1e-6 near 0,
  about 1.0e-5 near s = 0.01.
- Margin probes on the last 102 cells (source_probes_20261119.log): RED, require Delta(s) > 1e-6 s: REFUSED by both
  programs (same cell, near s = 0.953). GREEN, require Delta(s) > 5e-7 s: CERTIFIED by both (midpoint residual
  2.8371e-7 s).
Logs: sourceA_full_20261119.log, sourceB_full_20261119.log, source_probes_20261119.log; outputs runs/*.json.

## After the code audit (19 Nov 2026, 18:2x-18:3x +04)

Code referee ref6 (../REFEREE_CODE_AUDIT_20261119.md): 2b PASS WITH FIXES, sound; the fixes are option handling and
reporting only. The recorded probes used '=', so the results above stand. Applied:
- S-1: both programs refuse an option without '=', an unknown key and a repeated key (before, '--require 776/...' with a
  space and the typo '--requre=...' were silently ignored, so a red probe could test nothing).
- S-2: both refuse an empty or out-of-range cell range; a part range runs only with --partial=yes and is then reported as
  "ALL CELLS OF THE PARTIAL RANGE CERTIFIED (not a full certificate)"; source_A now prints and records the total cell
  count ("cells i..j of 73302"; JSON keys cells_total and full_range in both).
- S-3: the usage line of both programs documents --require (and --partial).
Recorded as known limitations: S-4 (source_B's undecided bracket branch gives a valid but loose b; it would refuse, never
certify falsely), S-5 (source_B's header says "same claim" though it relies on lines_B and source_A for concavity; P4.6
credits this correctly), S-6 ("b > 0" is checked at b(lower end of A_m), a sanity check; P4.6 derives b > 0 from P4.5(ii)).
New versions (full values in ../../MANIFEST.sha256): source_A.py b3faa939f5755f26..., source_B.py 4ca80de62278bd4b...;
run_2b.sh takes TAG (logs and outputs named by it) and passes --partial=yes to the probes.
Re-run in full (TAG=rerun_20261119, from ../rerun_after_audit_20261119.sh):
- Program B: ALL CELLS CERTIFIED; cells 0..73302 of 73302; 80,270 evaluations; min Delta/s 7.8371e-7.
  sourceB_full_rerun_20261119.log.
- Program A: f C^1 and f'' < 0 on all 2,279 pieces; ALL CELLS CERTIFIED; cells 0..73302 of 73302; 80,328 evaluations;
  min Delta/s 7.8371e-07. sourceA_full_rerun_20261119.log.
- Probes on cells 73200..73302 with --partial=yes (source_probes_rerun_20261119.log): RED, require Delta(s) > 1e-6 s:
  NOT CERTIFIED by A and REFUSED by B, at the same cell [0.95300000000000007, 0.953...]; GREEN, require Delta(s) >
  5e-7 s: both "ALL CELLS OF THE PARTIAL RANGE CERTIFIED", 288 evaluations, min Delta/s 2.8371e-7.
- Every output equals the first run's apart from 'seconds' and the new keys (runs/*_rerun_20261119.json).
- Option and range controls (source_option_controls_followup_rerun_20261119.log): for each program, '--require 776/...'
  (space), '--requre=...', '--from=73302' (empty), '--from=73200 --to=73302' without --partial=yes and '--require'
  given twice: all 10 REFUSED (exit 1). The driver's first pass (source_option_controls_rerun_20261119.log) printed
  CONTROL FAILED for four of them only because its message pattern matched "refus" and not the programs' wording ("is
  only part of", "given twice"); the programs had exited 1 with those messages. ../rerun_after_audit_followup_20261119.sh
  widened the pattern and re-ran all 10.
