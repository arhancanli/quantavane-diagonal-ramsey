# Responses to the referees of SELF_CONTAINED.md v1 (commit 1ce268ad9), 19 Nov 2026

Every finding, the change made in v2, and where. "Accepted" means the text was changed as asked. No finding was rejected.

## Referee 1 (chain), REFEREE1_CHAIN_20261119.md: PASS WITH FIXES for both theorems, no ERROR

GAP-1 (source of the global line inequality). Accepted, and checked by the lab before writing:
- fetched Bridge/P06LinesP0r12_0.lean, Bridge/P06LinesP0r12.lean and Bridge/TangentLines.lean of ZBS at c2875f33;
  each line is a theorem `line_P0r12_<i> : ∀ s : ℝ, 0 < s → symmetricProfile luWangSource 1 s ≤ c + d * s` proved by
  `line_atS`, in 29 files Bridge/P06LinesP0r12_<i>.lean, collected as `lu_wang_lines_P0r12`;
- the 1,128 pairs in `lu_wang_lines_P0r12` equal zbs_bank.json's line list exactly (all compared as rationals);
- ZBS's paper names `DiagRamsey.lu_wang_lines_P0r12` in its Section 7 (final axiom checks) and says the tangent lines
  are taken from Lu-Wang's Lean development.
Changes: 0.3 (A) gets a separate item for the lines (Lean theorem names, the assumption that
`symmetricProfile luWangSource 1` is f-hat, not audited by us); the closing paragraph of 0.3 now lists ZBS's exact
non-Lean checker run (their Section 6.2) next to the kernel check; 1.6, 1.7 and Section 5 (Source) cite the Lean theorem.

GAP-2 (0.3 (B) incomplete). Accepted. 0.3 (B) now lists: Lemmas 3.1, 3.2; Proposition 3.5's hypotheses and Steps 1,
2, 5, 6, 8 (3, 4, 7 not used); the deduction of Theorem 3.4 from Proposition 3.5 (reused in Lemma 4.5'); Lemma 4.5's
identity; Lemmas 4.3, 4.4; the proof of Theorem 4.2; the proofs of Lemma 5.8 and Theorem 5.7 (re-read in 6.10).
Theorem A.9 Step 2 now says "Steps 1, 2, 5 and 6" and states why Proposition 3.5's hypotheses (i)-(iv) hold at v = 1.

GAP-3 (breakpoint end points). Accepted. Section 5 (Route, route calls, Source pair cells) now states that bp starts
at the left end and ends at the right end (checked), and a sentence names the checks in both checkers (bankA.bp_ok,
bankB.increasing_from_to; the lab confirmed both are applied to leaf, route piece, route call, closed piece and source
pair cell). Referee 2 was also asked to confirm.

NIT-1 (gL formula). Accepted: gL(s) = sum_j d_j (clamp(s, u_{j-1}, u_j) - u_{j-1}), which is what bankA.GL computes.
NIT-2 (Lemma 2.3 misplaced; Definition 4.1 and Erdos-Szekeres missing). Accepted (0.3 (A)).
NIT-3 (title). Accepted: "R(k,k) <= 3.4836^k (and <= 3.4827^k with Theorem A), below the previous 3.4914^k".
NIT-4 (finite v in Proposition 6.5). Accepted: v_n = n_T/N is used for every finite-r quantity in Proposition A.5.
NIT-5 (numbering). Accepted: the results of Section 6 are renamed A.1-A.10 (subsections stay 6.0-6.10, so "6.10" is
always a subsection); the internal label "S3.7" is removed; "(6.9)" in the constants becomes "(Lemma A.10)".
NIT-6 (grid indexing). Accepted: 7.1 now defines Lambda in Theorem A's notation, v_k = u_b + (k - 1) D,
k = 1, ..., m, v_1 = u_b, k_b = 1, and says it is the grid fixed before r in Theorem A, Lemma 4.5', Theorem 4.2'.
NIT-7 (failing boxes in 7.2). Accepted: Lemma D's statement is restricted to boxes on which 7.4 does not fail.
NIT-8 (D7 one-liners). Accepted: D7 now gives u1, u2, du1/dPhi_b, du2/dPhi_b and the three difference formulas, and
the p_b-monotonicity through Lemma M with the direction of each comparison. One sign differs from the report: the
report writes dIL/dPhi_b = -[Psi(phi_s(u1)) - Psi(p_b)]/[phi_s(u1) - p_b]; differentiating IL = int_0^{u1}
Psi(phi_s) + (u_b - u1) Psi(p_b) with du1/dPhi_b = 1/(phi_s(u1) - p_b) gives the quotient WITHOUT the leading minus,
which (Psi nonincreasing with slopes -q_j, phi_s(u1) >= p_b) lies in [-q_max, -q_min]; that is the bound D7 uses and
the conclusion the report states. v2 writes the version without the minus.

Evidence kept: the referee's scripts and logs are in referee1/ (globalcheck.py re-checks every Section 5 condition
over all new objects of both certificates: 0 failures; lemmaC_*.py re-verifies Lemma C for 49 + 49 controls).

## Referee 2 (code audit), REFEREE2_CODE_20261119.md: PASS for all five checkers and parse_zbs.py, no ERROR

Constraint on the fixes: the Lemma D checkers are frozen copies pinned by code/lemmaD/MANIFEST.sha256 (and used by
reproduce.sh), and this task may commit only papers/diagonal-ramsey-2026/. So no frozen file was edited; the fixes are
a run-time preflight in this folder, made part of the acceptance rule. Recommendation for the lane's next freeze:
add the same explicit checks inside checkD_A and checkD_B and the MANIFEST check inside runA/runB.

Finding 1 (GAP: K4's N >= 2 and K6's 1 <= jA0 <= N - 1 not tested explicitly in checkD_A, checkD_B). Fixed:
tools/preflight.py tests both (and that jA0 is an integer) for every Lemma D block. Red controls
(tools/preflight_tampers.py on certCD3's root block): jA0 = 0, -1, N, N + 1, jA0 as a string, N = 1, root axis "x",
a node with one child: all 8 REFUSED, the original ACCEPTED (evidence/preflight_tampers_root873_20261119.log).
Finding 2 (GAP: frozen Lemma D code not pinned at run time; checkD_A's `import ivA` resolves to checkA/ivA.py inside
checker A). Fixed: the preflight verifies all 31 files of MANIFEST.sha256 and the byte-identity of checkA/ivA.py with
lemmaD/ivA.py. Preflight on certK3 and certCD3: OK (evidence/preflight_certs_20261119.log).
Finding 3 (NIT: checkD_A reads any axis other than "P" as "p"). The preflight refuses any axis other than "P"/"p".
Finding 4 (NIT: checkD_B precision 300 bits at first import, 320 afterwards). Documented in SELF_CONTAINED 7.6; rigour
unaffected; no change.
Finding 5 (NIT: tamper suites count any nonzero exit as a refusal; some conditions have no tamper). Documented in 8.3:
the 19 Nov logs show the assertion text of each refusal, and the referee's 125 further tampers cover the missing
conditions. No change to the suites (they are lane files).
Finding 6 (NIT: parse_zbs.py style: unused regex, layout assumptions). Documented; the referee's independent re-parse
matches every object, so the output is right; no change (lane file).
Count note: the report says "certCD3: 14/14 refused"; referee2/red_CD3.log lists 13 tampers, all refused by both,
which is the count in RESULT_CD.md and in SELF_CONTAINED 8.2.
Additional evidence produced by the lab after the report: checker A re-run on certCD3 (evidence/runA_certCD3_20261119.log).

## Re-referee of v1 -> v2 (REREFEREE_20261119.md): PASS WITH FIXES, no mathematical error; all fixes applied in v3

E1 (folder MANIFEST.sha256 named but not committed). Fixed: MANIFEST.sha256 of this folder is committed with v3 and with
every later version; Section 10 says how to verify a version and that the lane files are unchanged since aeaa8f1cc
(checked: git log aeaa8f1cc..HEAD on both lanes is empty).
G1 (the preflight trusted the manifest on disk). Fixed: preflight.py now hard-codes the SHA-256 of
code/lemmaD/MANIFEST.sha256 (22742abb...ce46b), requires exactly 31 listed files, requires checkD_A, checkD_B, ivA,
genD and tamper_D with hard-coded hashes, and checks checkA/ivA.py against the frozen ivA hash; preflight.py itself is
pinned by this folder's MANIFEST.sha256. Pin tests in a sandbox copy (tools/preflight_pin_tests.sh,
evidence/preflight_pin_tests_20261119.log): an edited checkD_A.py, the same with its manifest line regenerated, the
same with its line deleted, a manifest truncated to 5 lines and an edited checkA/ivA.py are all REFUSED; the untouched
and restored trees are OK. Preflight on certK3 and certCD3 and its 8 tampers re-run with the hardened version (OK /
all refused).
G2 (checker A on certCD3 listed before it finished). Resolved: the run finished at 13:44 (ok, z = 311946616731/
250000000000, e^z <= 3.4826255125, 1207 s; evidence/runA_certCD3_20261119.log), recorded in 8.2 and 12.
N1 (ZBS section and splice). Fixed: Section 7.2 and the full sentence quoted; lu_wang_lines_P0r12 in Section 7.4.
N2 (what line_atS states; index letters). Fixed: line_atS's statement as given by the re-referee; files indexed
f = 0..28, theorems i = 0..1127.
N3 (jB = N in 7.6). Fixed: 7.4 step 7 sets kappa2h = 0 for jB = N; the frozen checkers refuse there (completeness,
not soundness; never reached by the 26 accepted certificates); the preflight covers K4/K6 only, not per-box conditions.
N4 (6.10 grid). Fixed: "Lambda the grid of 7.1".
N5 (title). Fixed: "for large k".
N6 (depth cap). Documented in Section 5 and in preflight.py (conservative; kept).
N7 (tamper wording; where the 8 preflight tampers apply). Fixed in 8.1 and 8.2.
N8 (stale bytecode). Section 9 now recommends -X pycache_prefix=<empty directory> for every python3 call.
The re-referee confirmed the lab's sign for dIL/dPhi_b (referee 1's leading minus was a slip) and GAP-3's checks in
both checkers (bankA.bp_ok at five call sites, bankB.increasing_from_to at five).

## Code audit of stages 2a, 2b, 2c (unconditional/REFEREE_CODE_AUDIT_20261119.md): no ERROR, nothing touching soundness; fixes applied in v5

Verdicts: 2a lines PASS (NITs only); 2b source PASS WITH FIXES (option handling and reporting only); 2c cone PASS (NITs
only). No float enters a decision in any program. Every changed program was re-run in full with its red and green
controls (unconditional/rerun_after_audit_20261119.sh and _followup_; results in SELF_CONTAINED 18.4 and the RESULT files).
S-1 with L-2 (options without '=' and unknown keys silently ignored in source_A, source_B, lines_B). Fixed in all four
programs (lines_A too): one strict parser refuses an argument that is not --key=value, an unknown key and a repeated
key. Controls: 14 malformed, misspelt, repeated or out-of-range invocations, all refused.
S-2 (an empty or partial range printed ALL CELLS CERTIFIED; A did not print the total). Fixed: an empty or out-of-range
range is refused; a part range runs only with --partial=yes and has its own headline ("ALL CELLS OF THE PARTIAL RANGE
CERTIFIED (not a full certificate)"); both programs print and record "cells i..j of N" (cells_total, full_range).
S-3, L-1 (usage text). Fixed: the usage lines give the forms the code accepts and document --require and --partial.
L-3 (statement check over the whole file). Fixed: lines_B checks the statement of lu_wang_lines_P0r12 itself.
C-3 (zbs_full.json not pinned). Fixed: assemble_full.py and check_full.py require SHA-256
a2395f138b9ee24a2a5409debe44bb15443f544179fc75837d53c79b195903ca; both refuse zbs_bank.json passed in its place. With the
pin, assemble_full.py reproduces both full certificates byte for byte (maps equal apart from their own output path and
run time) and check_full.py accepts both (FULL CHECK OK).
Known limitations, recorded and not changed (none affects a recorded result): L-4 (the Hermite C^1 checks are identities
of the construction and cannot fail on data; P4.6 does not count them as a data check), L-5 (P06LinesP0r12.lean pinned by
SHA-256 only, no git-blob provenance; equal to the blob-verified T.lean list), S-4 (source_B's undecided branch gives a
loose but valid b; it can only refuse), S-5 (source_B's header wording; concavity is credited to lines_B and source_A),
S-6 ("b > 0" checked at the lower end of A_m, a sanity check only), C-1 (check_full compares top-level keys other than
root/meta by name only; the real certificates have none), C-2 (appended controls checked for presence of 'cert' only;
validity is the checkers' job, and both checkers verify every control), C-4 (a missing map entry raises KeyError, exit
1, rather than REFUSED; fails safe), C-5 (the checkers still receive the full zbs_bank.json; check_full's no-ZBS-reference
check and the auditor's lines-only bank run show nothing else is used).
Record fix found while reading the rerun logs: the driver's refusal pattern missed two of the programs' refusal wordings
and printed CONTROL FAILED for four refused controls; the follow-up script widened the pattern and re-ran all 10 source
controls (all refused). It also compared the re-assembled maps without "out" and "seconds", which the driver had
compared byte for byte.
