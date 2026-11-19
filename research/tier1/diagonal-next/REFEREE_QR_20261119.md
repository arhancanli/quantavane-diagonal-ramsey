# Referee report: Proposition QR (PROOF_QR.md, draft 19 Nov 2026 21:5x)

Fresh-context referee, 19 Nov 2026. Read: PROOF_QR.md; SELF_CONTAINED.md Section 14 (P1.1-P1.4), P2.3 (Lemma 4.5),
P2.4 (Theorem 4.2), 6.8-6.10 (Theorem A, Lemma A.10, Lemma 4.5'); ramsey-lemma NOTES Observation 2.

**VERDICT: PASS WITH FIXES.** Proposition QR as stated (conditions (i)-(iv) of Theorem 3.4, plus the sub-pair
strengthening, with red failure only on X_g) is true. The construction and the architecture of the proof are correct.
Two GAPs need fixing. GAP 1 is a missing smallness condition: as written, Steps C and D and the strengthening contain
inequalities that are false for some allowed choices of kappa and theta1. GAP 2 is in the Consequence paragraph. ZBS's
Lemma 4.5, which the bank actually uses, and our Lemma 4.5' (the Theorem A route behind Lemma D, level (ii) and
Conjecture S) both need RED to fail at EVERY row, not only on X_g. That step is true in this construction but is not
proved. No ERROR in the proposition itself.

## Items

1. **GAP (Choices; (B1); Step C; Step D; sub-pair strengthening): the tolerances are not small relative to w,
   mu/(1-mu) or 1/kappa.** (K) bounds kappa only from above in terms of the data, and theta1 is only <= kappa/8. So
   kappa can be large: p = mu = 1/2, w = 100, q0 = 0.4, x = 1e-10 admit kappa = 5 in (K). With theta1 = kappa/8:
   - (B1) then allows q_v up to 0.4(1 + 0.39) = 0.556 > mu. So "(B1) also gives q_v in (0, mu)" fails.
   - Step C's "e^{4 kappa beta}(1 - theta1 kappa/8)^{w beta} > e^{theta1 beta/2}" fails. In logs/beta it reads
     20 - 49.5 > 0.31.
   - Step D's bracket claim "(1 - q0 + theta1 kappa q0/8)^w (d/x) <= e^{-4 kappa}(1 + theta1 kappa + 3 theta1/r)"
     fails whenever w q0/(1 - q0) is large, even for small kappa. Example: w = 10, q0 = 0.5, kappa = 0.1,
     theta1 = kappa/8 gives a factor 1.00156 > 1.00125.
   - "(1 - kappa beta/4)^{-(1-beta)} <= e^{kappa beta/2}" needs kappa beta <= 2.

   The same w-factor enters q_v^w and (1 - q_v)^w in the strengthening.
   **Fix.** In Choices, add kappa <= 1; decreasing kappa preserves (K). In (B1), use the tolerance
   |q_v - q0| <= eps q0 with eps := min{theta1 kappa/8, kappa (1 - mu)/(8 w)}. Any fixed eps holds w.h.p., since q_v
   tends to q0 uniformly. Then:
   - q_v <= q0 e^{kappa/(8w)} < mu, by (K).
   - (mu/q_v)^w >= e^{4 kappa - kappa/8} > e^{theta1/2}, which closes Step C.
   - (1 - q_v)^w <= (1 - q0)^w e^{w eps q0/(1-q0)} <= (1 - q0)^w e^{kappa mu/8}. So the Step D bracket is at most
     e^{-4 kappa + kappa/8}(1 + 3 theta) <= e^{-3 kappa}.
   - In the strengthening, the exponents are -4 kappa + kappa/8 + 5 kappa/8 < 0 (blue) and
     -4 kappa + kappa/8 + kappa/2 + 5 kappa/8 < 0 (red).

2. **GAP (Consequence paragraph, and the claim "a >= a_rand for every bank / whatever improvement (CERT, Lemma D,
   level (ii), Conjecture S)"): red failure is shown only on X_g, but the lemmas the banks use quantify over all rows.**
   - ZBS Lemma 4.5 (P2.3): (RED) is "some v with q_v <= cap". Here every row has q_v <= cap, so the refutation needs
     RED to fail at every v in X.
   - Lemma 4.5' (6.10), through which Theorem A, and hence Lemma D, level (ii) and Conjecture S, reach the bank:
     (RED_T) is "some row i of X", with T = R_i ∩ T_v.

   Theorem 3.4's (iv) allows the zeta-exception, so refuting Theorem 3.4 does not refute these lemmas. Their
   contrapositive hypotheses are strictly stronger. As written, the proposition proves the Consequence only for
   statements of Theorem 3.4 form.
   **Fix** (true in this construction; it also simplifies the proof). Add a Step D' showing X_g = X w.h.p.:
   - (U1) Every v in X0 has |deg_R(v, Y0)/M - p| <= N^{-1/3} (Hoeffding plus a union over N rows).
   - (U2) Phi_c(X, Y) >= Phi_0 and H <= h(1 + 3 theta) give (|X|/N)^w |Y|/M >= ((1 - theta)/(1 + 3 theta))^r
     >= e^{-5 theta1}. So |Y0 \ Y| <= 5 theta1 M, and |pi_v - p| <= 6 theta1 + o(1) for EVERY v in X.
   - (U3) Apply (b) with X' = X. All but K columns of Y have u_y < h(1 + theta), so a_y^s <= e^{3 theta1}. The K
     exceptional columns contribute (K/|Y|)((1 - c)/(h(1 - theta)))^s = o(1). Hence
     m_v = E_Y[a^s h_vy] <= pi_v + E_Y(a^s - 1)_+ <= pi_v + 4 theta1 + o(1) for every v.
   - (U4) With theta1 <= kappa beta p/100 (and <= kappa/(8C)), Step D's ratio is < 1 for every v in X. The red
     sub-pair bound (1 - q_v)^w pi_v e^{5 theta1} < x also holds for every v.

   With D', (M) and the dependence of r on zeta can be dropped. For Lemma 4.5', also check its hypothesis. T_v is
   ranked by V, which is a function of the X0-Y0 colouring only (fix a tie-break). So |B_i ∩ T_v| ~ Bin(|T_v| - 1, q0)
   given that colouring, and it concentrates below cap |T_v| for the finitely many v in Lambda. Take Delta at its
   minimum (1 - c)/(v_1 N (1 - cap) - 1) = O(1/N). Then the c' remark applies.

3. **NIT ((B2) statement vs proof).** With t' = theta h q0/32, the derivation gives
   |b_v(y) - g_y| <= 2t'/q0 + 2/|X| = theta h/16 + o(1). That is not the stated theta h q0/8 when q0 < 1/2. Only
   theta h/8 is used (Steps C, D). **Fix:** state (B2) as <= theta h/8, or take t' = theta h q0^2/32.

4. **NIT (Step D, the parenthesis "q_v <= 1/2 is not needed ... shrink theta1 by that factor if needed").**
   - The displayed factor (1 + theta/2) is false when q_v > 1/2 and u_y is near h/4.
   - Shrinking theta1 cannot help, because both sides are linear in theta.
   - The correct factor is 1 + theta q_v/(2(1 - q_v)) <= 1 + theta mu/(2(1 - mu)).
   - The later constant C = 1/2 + mu q0/(2(1 - mu)) does dominate q_v/(2(1 - q_v)) (check:
     1 + mu q0/(1 - mu) >= q0/(1 - q0)), so the conclusion stands.

   **Fix:** write the factor as e^{theta1 beta C} in the display "(1 - q_v)^{w beta} m_v e^{theta1 beta/2} < ...". Delete
   the "shrink theta1" clause. Define C = max{1/2, mu/(2(1 - mu))}.

5. **NIT (notation clash N).** The header sets N = |X|, but the proof uses N = |X0|. Theorem 3.4 (iv) needs
   |X \ X_g| <= zeta |X|. (M) delivers this when read with N = |X|; Step D's "|X \ X_g| <= zeta N" with N = |X0| is
   weaker than needed. **Fix:** write zeta |X| in (M) and Step D, and reserve N = |X0|.

6. **NIT (Statement).** "with theta0 > 0 as small as we like fixed in advance" introduces theta0, which is never used.
   Delete it. Alternatively, state the strengthening with an explicit margin: the proof gives ratios
   <= e^{-kappa} mu^w and <= e^{-kappa} x.

7. **NIT (Step A).**
   - Fix a deterministic tie-break for the maximiser, so that (X, Y) is a function of the X0-Y0 colouring (Step B
     needs this).
   - alpha and gamma also depend on theta1 and on p (through c).
   - State r > w and s > 1 among the choices of r.
   - In (A3), choose alpha' <= alpha and gamma' <= gamma where they are chosen. Both constraints are upper bounds, so
     shrinking is free. Alternatively, run (b) with min{gamma', gamma} as well.
   - In (M), say that d > c >= p/2, so that the Markov threshold kappa beta d/4 >= kappa beta p/8 depends only on
     fixed parameters.

8. **NIT (c' remark).** "Delta = O(1/|X|)" holds for the minimal Delta allowed by Lemma 4.5 / 4.5'. That is all a
   counterexample to "for every Delta >= ..." needs; say so. ZBS's own induction (P2.4) uses Delta = delta/(n(n-1)),
   which is not O(1/|X|). If the barrier is wanted for that induction step itself, choose the construction's h with
   h >> r Delta. This is possible for large n, since x > p(1 - mu)^w is strict.

9. **NIT (scope of the Consequence).**
   - The barrier is for local-step statements about ARBITRARY maximal pairs (the form of Theorem 3.4, Lemma 4.5 and
     Lemma 4.5'), with these two moves, their sub-pairs and this potential.
   - The host is not outcome-free: Y0 is all red, and X0 ∪ Y0 has red cliques of size about log N. So the barrier
     says nothing about arguments that use outcome-freeness, the Stop condition, other moves or iterated moves.
     Reword "every control of a bank built on the potential" accordingly.
   - Optional hardening, all free because the tests do not see these features:
     - colour the Y0-internal edges at random;
     - use red probability p + h/2 and c = p - h/2, so that d >= p. This covers variants that assume d_R(X, Y) >= p,
       which the current construction (d possibly slightly < p) does not;
     - note that the construction works for every r >= R1 and every large N. With theta = theta_N -> 0 and D' it works
       for every fixed r > w with s > 1, which matters because a bank fixes one r.

10. **NIT (Remarks).**
    - Remark 1 "exactly the room any sharper envelope can use" should read "at most".
    - Remark 3 "Below a_rand nothing is known" contradicts the proposition, because a < a_rand is excluded. It
      should read "Between a_rand and the certified a (p(1 - mu)^w > x > x_cert)".

11. **NIT (Float line).** NOTES 21:4x supersedes z ~ 1.090 (2.97^k) with 1.08686 (2.965^k), using ratio range
    [1/20, 20]. Update it or cite both.

12. **NIT (missing sanity remark, recommended).** CERT >= 0 whenever x >= p(1 - mu)^w. The reason: mu is in F (A(mu)
    <= 0 < -log p), M(mu) = B(mu) = 0, and the constant choice q = mu gives CERT >= int_0^1 w mu (1 + log t) dt = 0.
    Consequences:
    - QR is consistent with Theorem 3.4.
    - "a > a_rand on every certified cell" is forced by CERT itself, so it is not independent evidence for QR.
    - The minimum gap of 0.0006 marks cells where CERT is nearly sharp.

    Say this in the Consequence paragraph.

## Checked and correct (no item)
- **Step A.**
  - (a) The Hoeffding/union bound and Phi_0 are correct.
  - (b) The union over 2^N sets X' with fixed K = ceil(2/(t^2 a)) is valid: the exponent is
    <= N log 2 + K log N - 4N, which tends to -infinity. The bound H_c(X', Y')^s <= (h + t)^s + (K/(gamma' M))(1 - c)^s
    and the step to h(1 + 3 theta) are correct.
  - (c) The size bounds, H >= h(1 - theta), d in (c, p + 3 theta h], (i) and (ii) are correct.
- **Step B.** Independence is correct: (X, Y) depends only on the X0-Y0 colouring, and BB restricted to X is
  G(|X|, q0) given that colouring. The decomposition in (B2) and the Hoeffding bound over |X||Y| pairs are correct.
- **Step C.** The argument is correct given item 1. u_y >= h/4 uses (1 - beta)^{1/s} >= 1/2 and theta <= 1/2.
- **Step D.** The reduction of (3) to (1 - q_v)^{w beta} m_v e^{theta1 beta C} < x^beta pi_v^{1-beta} is correct.
  (6), (7) and Markov give (M), with constants depending only on beta, w, |c| <= 1, H <= 1 and d >= p/2. beta is
  needed in the tolerance kappa beta d/4 because the gain e^{-3 kappa} enters raised to beta.
- **Quantifiers.** The order is: q0 and kappa (data); r (R0, beta, w, p, kappa, zeta); theta1 (kappa, mu, plus w via
  item 1's eps); alpha, gamma, alpha', gamma', K (r, h, theta1, x, mu, w); then N = M -> infinity. Nothing depends on
  N, and no constant blows up.
- **Sub-pair strengthening.** The small case and the (A3) case are correct given item 1, as is the e^{5 theta1} bound.
  The c' remark is correct via Minkowski (H_{c'} <= H_c + Delta), at the minimal Delta (item 8).
- **Numbers.** The table numbers were recomputed from code/dp.py load_table() (ctltable2.npz, 308,279 finite cells).
  a - a_rand lies in [0.000597, 1.2800], with median 0.07334 and no negative cell. The root-like cell has a = 1.10984
  and a_rand = 0.93001. Both match the text.

## Prior literature (secondary)
I do not know of a published quasi-random barrier for the local step of the CGMS book algorithm or for its successors
(GNNW 3.8^k; Balister et al.; ZBS). Two web queries found none. The nearest statement is different: CGMS and
Wigderson's Bourbaki exposé describe quasirandom colourings as the natural barrier for the Thomason/Conlon approach,
which the book algorithm was designed to get around. GNNW (arXiv 2407.19026) state no limit of their optimisation
(lane NOTES 21:4x). A grep of ZBS's TeX (lit/zbs_20261117/zbs_main.tex) for random/barrier/optimal shows no such
remark. Unpublished folklore of this kind cannot be excluded.

## Re-referee of v2

Same referee, 19 Nov 2026. Read PROOF_QR.md v2 in full.

**VERDICT: PASS.** All 12 items are fixed correctly. No new ERROR or GAP. Six NITs remain; none affects the proposition
or the Consequence.

**The 12 items.**
- Item 1. kappa <= 1 and eps = min{theta1 kappa/8, kappa(1 - mu)/(8w)} now close (B1), Step C, the Step D bracket and
  the strengthening. Checked: q_v <= q0 e^{kappa/(8w)} < mu; (mu/q_v)^w >= e^{4 kappa - kappa/8};
  (1 - q_v)^w <= (1 - q0)^w e^{kappa mu/8}.
- Item 2. Step D' is correct:
  - (U2): ((1 - theta)/(1 + 3 theta))^r >= e^{-5 theta1}, |Y0 \ Y| <= 5 theta1 M, and |pi_v - p| <= 6 theta1 + o(1)
    for every row.
  - (U3): (A4) is correctly derived from (b) with X' = X. a^s <= e^{2.1 theta1} <= e^{3 theta1} off the K columns;
    the K columns contribute o(1); so m_v <= pi_v + 4 theta1 + o(1).
  - Lemma 4.5' remarks are right: T_v depends only on the X0-Y0 colouring, so its blue degrees concentrate; minimal
    Delta = O(1/N); RED_T and BLUE_T are sub-pairs covered at every row.
- Items 3-7 and 10-12 are applied as proposed.
- Item 8 (c' at the minimal Delta) is correct; see NIT c for the ZBS-induction aside.
- Item 9 (scope) is correct.

**New margins checked.**
- Step D: the ratio is at most e^{-3.75 kappa beta + 0.17 kappa beta} < 1. The text's e^{-3.5 kappa beta + 0.16 kappa beta}
  is fine up to NIT a.
- Blue sub-pairs: exponent <= -4 kappa + kappa/8 + 5 kappa/8 <= -kappa.
- Red sub-pairs: exponent <= -4 kappa + kappa/8 + 0.07 kappa + 0.05 kappa <= -kappa.
- The small cases follow from the choice of alpha', gamma' with e^{-kappa} min(x, mu^w).
- The e^{-kappa} margins in the Statement hold.

**Scope sentence.** It is correct and now properly limited: it covers statements of Theorem 3.4 / 4.5 / 4.5' form about
arbitrary maximal pairs, with these moves, their sub-pairs and this potential. Its disclaimer covers outcome-freeness,
the stopping rule, other moves and iterated moves.

**Remaining items (all NIT).**
- a. Step D, line 102: (1 - 6 theta1/p)^{-(1 - beta)} <= e^{6.4 theta1/p}, so the display should read e^{17 theta1/p}
  (0.17 kappa beta), not e^{16 theta1/p}. The conclusion is unaffected.
- b. Optional hardening "red probability p + h/2 with c = p - h/2 gives d >= p". Lemma 3.1 alone gives only
  d >= p - theta h/2. Two conditions are needed: theta1 <= h/12, using (U2) to get d = E_X pi_v >= p + h/2 - 6 theta1
  - o(1); and h shrunk so that (p + h/2)(1 - q0)^w <= x e^{-4 kappa}.
- c. The ZBS-induction aside in "The shift c'". Run the proof with red probability p1 = c_n + h, not p, where
  p1 (1 - q0)^w <= x e^{-4 kappa}. Also require r Delta/h <= kappa/2. There Delta is fixed, so (1 + Delta/h)^r is not
  1 + o(1); the e^{-kappa} margin must absorb it.
- d. Sanity remark: if any certified cell rests on Lemma D (V_A < 0) rather than CERT, the same conclusion holds. The
  pair phi = 0, eta = 0 is admissible, and q = mu gives V_A >= 0 whenever x >= p(1 - mu)^w. Add this clause, or confirm
  that every cell of ctltable2 is CERT-certified.
- e. Line 77: "q_v <= ... < mu e^{-4 kappa/w + kappa/(8w)}": the first strict "<" should be "<=", since (K) gives
  q0 <= mu e^{-4 kappa/w}.
- f. Remark 2, "needs a different potential or different moves": align it with the scope sentence by adding "or
  arguments using outcome-freeness, the stopping rule or iterated moves".
