# Re-referee (fresh context) of the v1 -> v2 changes (1ce268ad9 -> a4400241e)

19 Nov 2026, 13:3x-13:4x +04. Given the diff, both referee reports, the lab's responses, the preflight tool and its
logs; asked to check only the changes. Report as returned, verbatim; scripts in rereferee/; the lab's responses (v3)
are in RESPONSES_20261119.md.

---

## Re-referee of SELF_CONTAINED.md v1 → v2 (1ce268ad9 → a4400241e)

**Verdict: PASS WITH FIXES.** None of the v2 changes introduces a mathematical error. The fixes for Theorems 1 and 2 are correct. Three fixes are still needed:
- one false statement in the record (E1);
- a weakness in the preflight's code pin (G1);
- an evidence entry listed before its run finished (G2).

There are also some NITs. I modified nothing in our working repository or on the SSD. certCD3's SHA-256 is unchanged (896dc046…).

### Referee 1 findings
- **GAP-1: fixed correctly**, with NITs N1 and N2 below. I fetched ZBS's Lean files at c2875f33 and checked:
  - There are 29 files, Bridge/P06LinesP0r12_0..28.lean, holding 1,128 theorems `line_P0r12_0`…`_1127`.
  - Each has the form `∀ s, 0 < s → symmetricProfile luWangSource 1 s ≤ c + d*s`, and all 1,128 are proved by `line_atS`.
  - `DiagRamsey.lu_wang_lines_P0r12` collects them.
  - With my own script, its list equals zbs_bank.json's `lines` as rationals and in order, and each per-file theorem matches it.
  - ZBS's paper names `lu_wang_lines_P0r12` in §7.4 ("Final statements and axiom checks", three axioms).
  - The (C4) quote and the 224-bit exact checker of §6.2 are accurate.
- **GAP-2: fixed correctly.** I checked it against zbs_main.tex:
  - The deduction of Thm 3.4 from Prop 3.5 has |c| ≤ 1+p, H ≤ 2 and d > c ≥ p−1/j, as stated.
  - Step 6 uses only Steps 1, 2 and 5.
  - The (i)–(iii) of 6.10 are present.
- **GAP-3: fixed correctly.** Referee 2's report does not contain the confirmation that was requested, so I checked the code myself:
  - `bankA.bp_ok` is applied at bankA.py lines 118, 136, 139, 148 and 178 (leaf, call, route, closed, source pair).
  - `bankB.increasing_from_to` is applied at bankB.py lines 105, 125, 127, 139 and 169.
  - Both check first = lo, last = hi and strict increase.
- **NIT-1: fixed correctly.** The formula equals bankA.gL / GL.
- **NIT-2: fixed correctly.**
- **NIT-3: fixed**, see N5.
- **NIT-4: fixed correctly.** v_n = n_T/N is used in the statement and in both cases. I re-derived the A.2(e) limit and the q=0 bound.
- **NIT-5: fixed correctly.** I listed every "6.x" and "A.x" reference:
  - Every remaining "6.x" names a subsection.
  - A.1–A.10 map one-to-one onto the old 6.1–6.10.
  - "S3.7" survives only in the source-file line, and "(Lemma A.10)" is used in the constants.
  - No reference dangles.
- **NIT-6: fixed with a leftover**, see N4. 7.1's indexing v_k = u_b+(k−1)D, k_b = 1, matches Theorem A (c(u), Δ_k), D2–D3 (Σ_{k≥k_b}), Lemma 4.5' and Theorem 4.2' (v_1 = u_b).
- **NIT-7: fixed correctly.**
- **NIT-8: fixed correctly. The lab is right about the sign** (derivation below).

### Referee 2 findings
- **F1: fixed correctly** by the preflight (tests below).
- **F2: fixed with a problem**, see G1.
- **F3: fixed correctly.**
- **F4 and F5: documented correctly** in 7.6 and 8.3.
- **F6: no change.** It is "documented" only through 8.3's re-parse sentence. That is acceptable.
- **The lab's count correction is right:** red_CD3.log has 13 tampers, not the 14 the report says.

### New ERROR
**E1, §10:** "This folder (papers/diagonal-ramsey-2026): the SHA-256 of every file, including this document, are in MANIFEST.sha256 of the same commit".
- No such file exists in a4400241e (checked with git ls-tree).
- Fix: commit that manifest, or delete the sentence.
- Also say which commit "same commit" means; the §10 header says aeaa8f1cc, where these files did not exist.

### New GAPs
**G1. The preflight trusts the MANIFEST.sha256 it finds on disk.** In a sandbox copy of the pinned tree:
- editing checkD_A.py → REFUSED (correct);
- editing checkD_A.py and regenerating its manifest line → PREFLIGHT OK;
- editing it and deleting its line → OK;
- truncating the manifest to 5 lines → OK;
- editing checkA/ivA.py → REFUSED (correct).

reproduce.sh's `shasum -c` has the same weakness, so referee 2's request is met literally. But Section 5's "pins at run time the frozen Lemma D code" is overstated.

Fix: hard-code in preflight.py the SHA-256 of MANIFEST.sha256 (22742abb…ce46b, already in §10), or the three code hashes (checkD_A 3600766b…, checkD_B 3a748ce2…, ivA f6fe4408…). Require those names to be present. Then pin preflight.py itself through E1's manifest. Soundness today is unaffected: all 31 files match.

**G2. §8.2 lists "checker A on certCD3 (evidence/runA_certCD3_20261119.log…)" among the 19 Nov persisted re-runs, but the run has not finished.**
- The committed log contains only the start timestamp, 13:24:17.
- At 13:43 the process (PID 23876) was still running (19 min).
- Fix: mark it pending in 8.2 until the log shows ok. §12 already says "result recorded below when done".
- The earlier fresh-clone acceptance (1118 s) remains the evidence in the meantime.

### NITs
- **N1.** ZBS's "tangent lines … taken from Lu and Wang's Lean development" is in their **§7.2**, not 7.1. It is also spliced from "The off-diagonal input, Theorem 2.2, and the tangent lines of f-hat are taken from…". Mark the cut or paraphrase.
- **N2.** `line_atS` does not bound F̂ "by the tangent lines". Its statement is: given kernel enclosures F'(u) ≤ pa/qa and F(u)−uF'(u) ≤ pb/qb at a rational u in a knot piece, F̂(s) ≤ pa/qa + (pb/qb)s and ≤ pb/qb + (pa/qa)s for all s > 0. The exact tangent bound is `symm_le_lines`. Also, `<i>` is used both for the file index (0–28) and the line index (0–1127).
- **N3. 7.6:** "(and jA = N or jB = N ends in max() of an empty sequence where 7.4 says "fail")" is wrong for jB.
  - 7.4 step 7 sets κ2h = 0 when jB = N; it does not say fail.
  - checkD_A.py:352 and checkD_B's κ2h line take max over an empty range, so the frozen checkers refuse where the spec computes U(B). That is a completeness issue, not a soundness one, and it is never reached by the 26 accepted certificates.
  - "tools/preflight.py now tests them explicitly" can be read as covering jA/jB = N. The preflight cannot test those: they are computed per box.
- **N4. 6.10 "Consequence for Theorem 2"** still writes Λ = {u_b + kD : k = 0,…}. It is the same set; write "the grid Λ of 7.1".
- **N5.** The title omits "for large k". C_* is non-effective, so the bound is not proved for every k.
- **N6.** The preflight's tree-depth cap of 200 is not in 7.5's format: a format-valid depth-201 tree is refused. This is conservative. Either document the cap or drop it.
- **N7.** In 8.1/8.2, "each with the assertion text" overstates slightly: checker A refuses closed_raw_only with a bare AssertionError that has no text. Also, 8.2's "its 8 tampers" were applied to the root's Lemma D block (root3), not to certCD3.
- **N8 (optional hardening).** The pin covers .py bytes only. Python will load a lemmaD/__pycache__ .pyc whose recorded mtime and size match. Running with `-X pycache_prefix=<empty dir>` closes this.

### The sign of dIL/dΦ_b
On [0, u_b], φ* = φ_s on [0, u1) and p_b on (u1, u_b]. u1 solves G := g(u1) − Φ_b + p_b(u_b − u1) = 0, with φ_s(u1) ≥ p_b.

- ∂G/∂u1 = φ_s(u1) − p_b and ∂G/∂Φ_b = −1, so du1/dΦ_b = 1/(φ_s(u1) − p_b) > 0.
- IL = ∫_0^{u1} Ψ(φ_s) + (u_b − u1)Ψ(p_b), so dIL/dΦ_b = [Ψ(φ_s(u1)) − Ψ(p_b)]·du1/dΦ_b = [Ψ(φ_s(u1)) − Ψ(p_b)]/(φ_s(u1) − p_b).
- Ψ is convex and nonincreasing with slopes −q_j, j ≥ j0. So this difference quotient lies in [−μ, −q_j0], and dIL/dΦ_b ≤ −q_min.

Referee 1's leading minus would make it ≥ +q_min, which contradicts its own "≤ −q_min". **The lab's version is right.** A float finite difference agrees: −0.0500 versus −0.0500 for the lab's formula and +0.0500 for referee 1's.

The other formulas:
- dK/dΦ_b = [(φ_s(u1)−s0)_+ − (p_b−s0)_+]/(φ_s(u1)−p_b), which lies in [0,1].
- On the right, du2/dΦ_b = −1/(p_b − φ_s(u2)), so dIR2/dΦ_b = [Ĥ+(φ_s(u2)) − Ĥ+(p_b)]/(p_b − φ_s(u2)) ≥ 0. This is at most q_R, because u2 decreases in Φ_b, so φ_s(u2) ≥ φ_s(b2) and the slope magnitudes of a convex Ĥ+ are largest at the left.

Both match v2 and the finite differences. The p_b paragraph is also correct:
- Raising p_b lowers Φ* with ends 0 and Φ_b, which needs Φ_b ≥ p_b u_b and holds at pl. So IL and K do not increase.
- It raises Φ** with ends Φ_b and 0, which needs Φ_b + p_b(1−u_b) ≥ 0 and holds at ph. So IR2 does not decrease.
- This is consistent with evaluating at (·, pl) and (·, ph).

### What I ran on the preflight
- **Real preflight on certCD3 (SSD, read-only) and root3_x337059333092731.json:** PREFLIGHT OK in 3 s. It reported 31 pins, 1,829 controls (25 Lemma D), and root3 with N = 1318, jA0 = 394, 67 leaves.
- **On all 26 vendored Lemma D certificates:** all OK (N = 1318; jA0 from 369 to 446).
- **Refused, correctly:** jA0 = 0, N, 5.0, true, or missing; N = 1; qgrid given as a dict; tree missing; axis "x" or "P "; a 4-item node; leaf "l"; leaf ["L"]; a bank control with both kinds or neither; a 'control' key in lemmaD; lemmaD null; a bank lemmaD block with jA0 = 0; a file of neither format.
- **Accepted, correctly (valid format):** jA0 = 1 and jA0 = N−1; N = 2 with jA0 = 1; tree "L"; a depth-200 tree; a bank with one Lemma C and one Lemma D control.
- **Edge cases:** depth 201 is refused (N6); `controls` given as the dict {"cert":1} passes the preflight, which is harmless because the checkers refuse it; duplicate JSON keys follow last-wins, the same as the checkers' json.load.
- **Pin tests:** as reported under G1.

Files (copied to rereferee/): pf_tests.py, cmp_lines.py (Lean list vs zbs_bank.json), d7check.py, preflight_real.log.
