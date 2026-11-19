# Fresh re-referee of the P1-P4 changes (8817ebaee..28823e532), 19 Nov 2026, 15:3x-15:5x +04

Given the diffs, the four referee reports and the v2 files. Report as returned (verbatim content, lightly reflowed).
Its NITs were applied at commit 2d016a9ac: P1 (Step 3 vector wording; Step 6(b) R_j/Rd and U_j, s_j defined; Step 7
omega_j, the feasibility/atom remark, omega_j = H0 where S is undefined; Claim P1.6 cites (5)); P3 (G_f(k, b) in
grounding (b); P3.6 C_tail remark); P4 (K1 removed from Steps 3 and 6; "P consists of finitely many cubic pieces");
records (RESULT_2b.md corrected; final 2b logs and outputs committed). The beta R0 > 2 (SELF_CONTAINED 6.10, Theorem A)
versus beta R0 > 1 (Lemma 4.5, Theorem 3.4) difference is intended: Lemma 4.5' needs s > 2 for Theorem A; ZBS's chain
needs only s > 1; enlarging R0 is free.

---

**Verdict: PASS WITH FIXES.** Every requested mathematical fix is made correctly, and none of the changes introduces an
ERROR or a GAP. What is left is wording, notation and records.

Checks run: P3's new identity re-derived by hand and checked exactly in rational arithmetic on 279,072 cases (random
knots, slopes and k, including 767 with t exactly on a knot): 0 mismatches, worst |difference|/V_d = 0.987
(scratchpad/ref5/r2.py). Everything else by hand. Nothing under our working repository was modified.

P1 (full v2 read). GAP-1 fixed correctly (Step 6(a) gets d_* < 1 without S; then q_i >= delta, m_i >= p/2,
m_i <= d_j + eta_j < 1). GAP-2 fixed correctly (all three cases of the limsup lemma checked; e^y - 1 <= y e^y for y <= 0
handles bounded y_j, the limit -1 handles y_j -> -infinity; F_d defined; usc now only for Borel measurability). GAP-3
fixed with one NIT (Borel w_j, iota = 1 eventually a.s., q(omega) in [delta, mu], fixed d_* with later subsequences
inside, Fatou direction all right; NIT: say why each two-cell problem is feasible a.s. (atoms are actual rows) or that
infeasible terms are -infinity; define w_j = H0 where S is undefined). GAP-4 fixed correctly (split; left-continuous
quantile convention matches the identity). GAP-5 fixed correctly. Step 5 constants correct (-log(1-q) <= 2q for
q <= 1/2; r(1 - e^{-kappa/(2r)}) >= kappa/4 for r >= kappa/2; C0 = (2/p) max{w, beta^{-1} log(2/p)}; delta <= 1/e
needed and sufficient; the q = 0 argument now right). Claim P1.6 correct (uses only x < p, x < (1-mu)^w, Steps 2, 5 and
6(a)); NIT: also cite (5). Other first-referee NITs all fixed. Notation mostly fixed (BB, Fq, Ys, Xt, e_A, y_z, vec,
|Y| consistent; P2 says "BB the blue graph"); remaining NITs: (a) Step 3 "z_v = 1[q_v <= z]" uses z as vector and
threshold; (b) new: Step 6(b) Q_j clashes with Step 7's quantile Q_j; (c) w_j clashes with w; (d) U_j and s_j undefined.

P3. GAP-1 (R2) fixed correctly (identity re-derived: d(s) = d_1 + sum (d_{j+1} - d_j) 1[s > u_j]; the integral gives
(t - k u_j)_+, the count t - floor(k u_j) since k u_j > k theta >= n0). NIT-1 fixed (c = c(j) and d(s) = d_j from the same
cell, matching delta0 and eta0). NITs 2-3 fixed (both namings). NIT-4 fixed (K >= 2). NITs 5-9 fixed; NIT-10 deferred to
SELF_CONTAINED as stated. P3.6 correct as remarks; NIT: in the second bullet add "(with eps in C_tail redefined as that
minimum)". Cross-block NIT: P3's grounding (b) still writes f-hat(k, b), P4.6 renamed it G_f(a, b).

P4. E1 fixed correctly (|X| > C(xhat/x)^{k/w}(yhat/y)^{l/w} mu^{-t} >= C e^{c1(k+l+t)}; no other uses of c1). E2 fixed
correctly (b > 0 since phi' = f' - A > 0 near 0+ and phi(0+) = 0; attained and unique; exchange argument; Danskin
localisation on [lambda*(A2), lambda*(A1)]; lambda* continuous; (iii) both coordinates in (0, 1); counterexample right).
N1 fixed (L1 independent of C, k, host). N2 partly fixed (multiset justification and "each lower bound on |X|" in; K1 in
"c1(n + l) >= K0 (log n)^3 + K1" still undefined: drop it or define it). N3, N4, N5 fixed. P4.6 certified facts correct
(f'(0+) = +infinity as stated; say P, P' bounded because P is finitely many cubic pieces); the second concavity
certificate in source_A.py is sound (exact C^1 identities; first-piece test j'' < 1/(t1(1+t1)), j'' re-derived). "Use in
Theorem 5.7" correct; the certified stage-2c minimum is still owed. Records: the full source_A re-run with the
concavity check was still running when looked at; commit the new log and JSON before "certified twice" counts; N6 not
yet applied in RESULT_2b.md (minimum over midpoints; "between 7.8e-7 and 1e-6 on all cells" false; concavity credited
to lines_B only).

P2. All nine NITs fixed correctly (local-case reason, n - b >= k + 1 >= 3, delta b/(n(n-b)) >= delta/n^2, the cap
hypothesis, the reordering of mu, citations of P1's (2), (3)). Carry-over: SELF_CONTAINED 6.10 asks beta R0 > 2 while
Lemma 4.5 and Theorem 3.4 state beta R0 > 1; enlarging R0 is free, but the documents should agree.
