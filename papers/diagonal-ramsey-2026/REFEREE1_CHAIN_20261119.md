# Referee 1 (fresh context): the chain "certificate + checker => bound", on SELF_CONTAINED.md v1 (commit 1ce268ad9)

19 Nov 2026, 12:1x-12:5x +04. Given only SELF_CONTAINED.md v1, ZBS's preprint (zbs_main.tex/pdf) and the certificate
files; told not to open the lab's other files or the checker code. Report as returned, verbatim; the lab's responses
are in RESPONSES_20261119.md.

---

## Referee 1 report: does "certificate + checker ⇒ bound" hold in SELF_CONTAINED.md (v1)?

### Verdicts
- **Theorem 1 (certK3, z1 = 1.248056263241): PASS WITH FIXES.** I found no false step. The fixes concern how the dependency is stated and how Section 5 is worded. The bound is conditional on ZBS's preprint, which is unrefereed and AI-generated (its README says so), on Lu–Wang (arXiv v1), and on ZBS's Lean development for the lines and for the validity of their bank P0r12. The document says this openly.
- **Theorem 2 (certCD3, z2 = 1.247786466924): PASS WITH FIXES.** I worked through Theorem A (6.1–6.10) and Lemma D (D0–D8, Lemma M, the 7.4 assembly) step by step and found no error. Two kinds of fix are needed: the ZBS dependency list in 0.3(B) is incomplete, and several steps in Lemma D's D7 are only sketched. I re-derived all of the sketched steps and they are correct.

| Section | Verdict |
|---|---|
| 0–2 | PASS WITH FIXES (GAP-1, GAP-2, NITs) |
| 3 (Lemma C) | PASS. Every step re-derived: (i)–(v), concavity via the f̄ perspective representation, the secant majorant, the hinge integral, the telescoping identity, integrability. |
| 5 | PASS WITH FIXES (GAP-3, NIT-1) |
| 6 (Theorem A) | PASS (NITs) |
| 7 (Lemma D) | PASS WITH FIXES (NIT-7, NIT-8) |
| Spot checks | PASS (all below) |

### Is 0.3 exact and complete?
**No.**
- **(A)** is substantively complete for Theorem 1, but it attributes the global line inequality to the wrong source (GAP-1).
- **(B)** is incomplete for Theorem 2 (GAP-2).

Theorem 5.7 and Corollary 5.10 are quoted verbatim. Claim 2.1 applies Theorem 5.7 correctly to the union bank: the hypothesis is a conjunction over objects, ZBS's objects refer only to ZBS objects, and the bank is finite.

The quotations of Definitions 5.1–5.6, Lemmas 5.8–5.9, Theorems 3.4 and 4.2 and the CERT definition match zbs_main.tex. The printed numbering matches too: (1)=support, (2)=B, (3)=R, (4)=twocell, (6),(7)=C1,C2, (12)=route, (13)=tail.

The step from Corollary 5.10 to "R(k,k) ≤ 3.4835653^k for large k" is valid: ceil(C_* e^{zk}) ≤ (C_*+1)e^{zk}, and e^{z1} < 3.4835653.

### Findings (no ERROR found)

**GAP-1 (0.3(A) last item; 1.6; 1.7; 5 "Source").**
- Text: "the 1,128 lines (c, d) with f-hat(lambda) <= c + d lambda for all lambda > 0 that ZBS certify (C4)".
- ZBS's paper does not say this. Its (C4) only speaks of "tangent lines of f-hat … by Lemma 2.3" and gives no count.
- The stored slopes are rational with about 25 digits, so they are not exact tangent slopes. "Tangent + Lemma 2.3" therefore does not by itself give an inequality valid for all λ.
- Global validity really is needed, because new sources use these lines on tails and cells of their own choosing.
- The global statement does exist, but only in ZBS's Lean. I fetched Bridge/P06LinesP0r12_0.lean from GitHub: `theorem line_P0r12_0 : ∀ s : ℝ, 0 < s → symmetricProfile luWangSource 1 s ≤ c + d * s`. The aggregate is `lu_wang_lines_P0r12` in Bridge/P06LinesP0r12.lean.
- **Fix required:**
  - Cite these Lean theorems by name as the dependency.
  - State as an assumption that `symmetricProfile luWangSource 1` is f̂.
  - Correct "their kernel check is the only evidence": ZBS §6.2/§7.1 also report an exact non-Lean checker run of (C1)–(C5).

**GAP-2 (0.3(B)).**
- "Bank validity with extended controls" (6.10) works by re-reading the *proofs* of ZBS Lemma 5.8 and Theorem 5.7, not only their statements. (B) lists only "the proof of Theorem 4.2".
- Lemma 4.5' reuses ZBS's deduction of Theorem 3.4 from Proposition 3.5, including its bounds on |c|, H and d.
- 6.7 Step 2 also relies on Proposition 3.5's hypotheses (i)–(iv) holding at v = 1. That holds, via Lemma 4.5's identity and the Δ bound.
- 6.7 Step 2 says "ZBS Steps 1-6 apply", while (B) lists Steps 1, 2, 5, 6, 8. Steps 3–4 are not needed for d_* < 1.
- **Fix required:**
  - Add the proofs of Lemma 5.8 and Theorem 5.7 (controls enter only via (i)–(iii) of 6.10).
  - Add the deduction of Theorem 3.4 from Proposition 3.5, and Proposition 3.5's hypotheses.
  - Change "Steps 1-6" to "Steps 1, 2, 5, 6".

**GAP-3 (Section 5, Route and Source).**
- Texts: "at every point of bp (which contains every knot of L_P and of us inside (lo, hi))" and "bp containing the knots of P_R and the reciprocals of the knots of P_B".
- Neither text requires bp to begin at lo and end at hi. The "affine between consecutive points" argument needs that. The Leaf and Closed checks do say "from lo to hi". For route calls the cell endpoints are covered, because they are knots of us.
- In the data it holds: every route piece, every call and every source-pair cell in both certificates has bp running from the left endpoint to the right one (checked below).
- **Fix required:** state the endpoint condition as a checked condition, and have the code referee confirm that both checkers assert it.

**NITs**
1. **§5 Route, gL:** "gL(s) = sum_j d_j * clamp(s, u_{j-1}, u_j)" should read "d_j (clamp(s, u_{j-1}, u_j) − u_{j-1})". As written, gL(θ) ≠ 0.
2. **0.3(A), Lemma 2.3:** "Lemma 2.3 … used inside the proof of Theorem 5.7" is wrong; it justifies ZBS's lines. Definition 4.1 and Erdős–Szekeres are used but not listed (harmless).
3. **Title:** "below 3.4914^k" does not state the result; say 3.4836^k / 3.4827^k, or "below the previous 3.4914^k".
4. **6.4, lower bound:** "≥ −w v q'_j" should be "−w (n_T/N) q'_j".
5. **Numbering:** "Lemma 6.10" sits in subsection 6.9, and "6.10" also names the next subsection. Theorem A's "(With 6.10…)", Lemma 6.10's "constants of 6.10 (S3.7)" and the Constants' "(6.9)" are ambiguous. Also drop the internal label "S3.7".
6. **Grid indexing:** Theorem A indexes v_1<…<v_m=1, while 7.1 indexes v_k = u_b + kD from k = 0 with v_{k_b} = u_b. It is the same set; unify the notation.
7. **7.2:** "for every rational box B … V_A ≤ U(B)" should say "for every box on which 7.4 does not fail".
8. **7.3 D7 / 7.4 steps 2–6:** the monotonicity claims ("IL nonincreasing in Φ_b and p_b; K nondecreasing in Φ_b, nonincreasing in p_b; IR2 nondecreasing in both") and the slope bounds rest on one-liners ("exact difference formulas on the switch intervals").
   - I verified them. With u1 the left switch point and u2 the right one:
     - dIL/dΦ_b = −[Ψ(φ_s(u1)) − Ψ(p_b)]/[φ_s(u1) − p_b] ≤ −q_min
     - dK/dΦ_b = [(φ_s(u1) − s0)_+ − (p_b − s0)_+]/[φ_s(u1) − p_b] ∈ [0, 1]
     - dIR2/dΦ_b = [Ĥ+(φ_s(u2)) − Ĥ+(p_b)]/[p_b − φ_s(u2)] ≤ q_R
   - The p_b-monotonicity follows from Lemma M, and the u2 = 1 clipping argument is correct.
   - Write these formulas into the text.

### What I re-derived and found correct
- **Section 3 (Lemma C):** confirmed. G0 is convex, F = D∩(0,μ] ⊂ (a_cut,μ], and the f̄ identity holds exactly.
- **Proposition 6.2 (a)–(e):** I redid the algebra: the E_j identity, including the c[j∈T]/n_T cancellation; the root exponents (s−wβ)/s = 1−w/r and (1−β)/s; the Jensen steps.
- **Lemmas 6.3, 6.4 and Proposition 6.5, both cases:** the Q = 0 → −∞ argument, using e^t−1 ≤ te^t; all branch limits; the q'→0 membership.
- **Lemmas 6.6–6.7 and Corollary 6.8:** K2(σ) and the Beta integral are right.
- **Theorem 6.9, Steps 1–6:** uniform integrability, Helly, Skorokhod, the cell-oscillation bound, portmanteau, Corollary 6.8 pinning, the regularity/bracket condition, and the symmetry identity.
- **Theorem A:** the Fubini form of integration by parts with left-continuous φ, mass Δ_k on [v_k, v_{k+1}), the null set u = v_k, measurability, and the expectation argument (the integrand is bounded below by an integrable function).
- **Lemma 6.10:** RED', BLUE' and BOOK_S, including the b_n page ratio.
- **Lemma 4.5':** gives a failing sequence.
- **Theorem 4.2':** the three changes leave ZBS's proof valid. The v=1 book case still works because D_r ≤ D_r/v_1, and the new K_1 is finite. Λ is fixed before r.
- **Lemma D:** D0 (C¹ matching at A=B, convexity of a(η), (D0.1)), D1–D3 (including ∫s d(−φ) = w + u_b p_b − Φ_b with f1 = −w), D4; Lemma M, and the endpoint values of Φ* and Φ** (which use Φ_b ≥ p_b u_b and Φ_b + p_b(1−u_b) ≥ 0); D5(B) by parts, the D6 band charging (θ can be any upper bound of κ/κ2 that is ≤ 1), E_cap's closed form, D7, and the 7.4 steps against D7; K9 plus the tree covering the root rectangle gives V_A < 0 for every admissible pair; the Lemma D grid {u_b + kD} is the same object as Theorem A's Λ, with v_1 = u_b.

### Spot checks (my own scripts; Fractions plus decimal-based enclosures)
**Hashes and counts**
- e^{z1} = 3.4835652387383… ≤ 8708913097/2.5e9 and < 3.4835653.
- e^{z2} = 3.4826255124399… ≤ 278610041/8e7 and < 3.4826256.
- All 7 hashes match Section 10: zbs_bank.json, certK3/certCD3, and the four checker outputs.
- zbs_bank.json counts are 918 controls / 2713 sources / 1902 raw / 1003 closed, matching ZBS's Table 1, plus 1,128 lines.

**Roots**
- Both roots: every piece containing 1 is a pair (R,R), p_R = 1/2, L_Q(1) = z exactly, and the pair inequalities hold at bp.
- certK3 root route (control 1722, source n4020): every check passes; tightest slacks are about 1e-13.
- certCD3 root route (control 873, CD, parameters exactly as in 8.2): every check passes.

**Lemma C, independently re-verified with ZBS's two-branch H**
- certK3 root control 1722 (N = 512): G0(q0) = +1.0e-12, hinge sum −1.05e-9, minimum secant slack 1.0e-10.
- 48 more certK3 controls and 49 certCD3 controls (all terminal controls of the roots' children plus a seeded random sample) all pass. Hinge sums lie in [−1.71e-9, −1.01e-9].

**Full exact re-check of every Section 5 condition except the Lemma C/D internals, over ALL new objects: 0 failures in both certificates**

| | certK3 | certCD3 |
|---|---|---|
| Route pieces | 14,500 | 18,496 |
| Leaves | 13,119 | 15,966 |
| Route calls | 106,126 | 145,004 |
| Pair pieces | 34,399 | 49,687 |
| Source pairs | 4,021 | 4,861 |
| Grounded cells | 21,539 | 25,898 |
| Source-pair cells | 3,931 | 4,771 |

The minimum slacks are about 1e-13; source-pair cells reach 0, which is allowed because the inequality is non-strict with η included.

**CD controls**
- There are 25. Each embedded lemmaD block is identical to a vendored certs/*.json, and the five fields match (c1722_m300.json is unused).
- K1–K4 and K7–K9 hold under my enclosures: u_b = 3/100, D = 97/10^8, (1−u_b)/D = 10^6.

**Float sanity checks for the CD root (not rigorous)**
- CERT ≈ +1.39e-4, so Lemma C cannot certify this control and Theorem A is genuinely needed.
- V_A at the saturated profile ≈ −5.60e-5.
- The truncated-saturated family gives V_A from −8.0e-3 to −6.0e-5.
- max Ht on F ≈ −8.9e-3, so V_A(φ≡0) = −∞.
- All of this is consistent with Lemma D; the worst U(B) of about −1e-7 is valid but loose.

### What I could not check
- ZBS's own proofs: I read 3.4/3.5, 4.2 and 5.7–5.10 for consistency but did not referee them.
- The validity of P0r12, and whether zbs_bank.json faithfully parses T/TD*.lean (only the counts and hash were checked).
- ZBS's Lean statements: I read line_P0r12_0 but not the other 1,127; the aggregate theorem's predicate was truncated, and I could not see the definition of symmetricProfile.
- Lu–Wang's Theorem 2.2.
- Lemma C for the remaining ~1,675 / ~1,755 controls.
- Lemma D's U(B) < 0 on the leaf boxes (I did not reimplement 7.4), nor the K5 node heights or K6 |Ht''| bounds.
- The checker code (that is referee 2's audit).

Scripts are in the session scratchpad ref1/scripts (riv.py, liv.py, lemmaC_root.py, lemmaC_multi.py, rootchain.py, globalcheck.py, cdroot.py, k7.py, vafloat.py, vafam.py, flat.py); logs globalK3.log, globalCD3.log, lemmaC_K3.log, lemmaC_CD3.log. Nothing under our working repository or on the SSD was modified.
