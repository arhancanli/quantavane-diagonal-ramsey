# Off-diagonal Ramsey bounds R(k, l), l = gamma k, from the unconditional bank (Theorem O)

Lane `research/tier1/ramsey-offdiag`, opened 19 Nov 2026 21:0x +04. All logarithms natural. "SC" is
papers/diagonal-ramsey-2026/SELF_CONTAINED.md v5. Public copy (deposit of 19 Nov 2026); not yet peer reviewed.

## 0. Claim and what it rests on

**Theorem O (certCD3-full).** Let Phi be the function on [1/5, 1] given by the certificate
`cert/offdiag_cd3_v1.json` (SHA-256 7a390e477f49cc04a5edcc56d23cd6bd5f676ac38c813df298c985d52b68a8d1): 1,601 cells
[lo_i, hi_i] tiling [1/5, 1], each with an affine Phi_i(g) = v_lo + (v_hi - v_lo)(g - lo)/(hi - lo). Let C_* be the
constant of SC Theorem 5.7 (P3.3) for the bank certCD3-full (the bank of SC Theorem 2U). Then for all integers
k, l >= 1 and every cell i with l/k in [lo_i, hi_i]:

    R(k, l) <= ceil(C_* e^{k Phi_i(l/k)}),

and, for every fixed gamma in [1/5, 1], log R(k, floor(gamma k)) <= Phi(gamma) k + O(1) for k >= 5, where
Phi(gamma) = Phi_i(gamma) for the cell with lo_i <= gamma < hi_i (the last cell at gamma = 1). By R(k, l) = R(l, k) this
covers l/k in [1, 5] too. Since R(k, l) is nondecreasing in l, the monotone hull Phi*(gamma) = min_{gamma' in [gamma, 1]}
Phi(gamma') is also a valid exponent; it is lower than Phi on (0.99852, 1 - 1e-10), by up to 6.4e-4, where Phi(1) is
smaller. The stated Phi is therefore not the best exponent derivable from this bank, and all comparisons below use Phi
itself.

Values (exact rationals printed identically by both checkers; decimals rounded up):

| gamma | Phi(gamma) | e^Phi <= | best published exponent (source) | gain |
|---|---|---|---|---|
| 1/5 | 0.488743602 | 1.6302668 | 0.488733 (Lu-Wang f) | -0.000011 (no claim) |
| 21/100 | 0.501329821 | 1.6509153 | 0.504193 (ZBS/EP banks) | 0.002863 |
| 1/4 | 0.561026928 | 1.7524713 | 0.563955 (banks) | 0.002928 |
| 1/3 | 0.672264445 | 1.9586677 | 0.675098 (banks) | 0.002834 |
| 1/2 | 0.857469512 | 2.3571884 | 0.861784 (banks) | 0.004314 |
| 2/3 | 1.009761706 | 2.7449469 | 1.014477 (banks) | 0.004715 |
| 3/4 | 1.075811109 | 2.9323705 | 1.079859 (banks) | 0.004048 |
| 4/5 | 1.113747353 | 3.0457506 | 1.118088 (banks) | 0.004341 |
| 9/10 | 1.183712738 | 3.2664794 | 1.190165 (banks) | 0.006452 |
| 19/20 | 1.218244041 | 3.3812453 | 1.222929 (banks) | 0.004685 |
| 99/100 | 1.243103357 | 3.4663542 | 1.247424 (banks) | 0.004321 |
| 1 | 1.247786467 | 3.4826256 | 1.250290 (EP diagonal) | 0.002504 (Theorem 2U itself, not new here) |

(Full table: runs/table_cd3_v1.md. "Published" = the best bound derivable from any published object, read
generously; Section 4. Decimals of Phi and e^Phi are exact ceilings, checker A v2 / checker B.)

**Comparison (the record claim).** On every cell from gamma = 201/1000 to 1, Phi is strictly below every published
upper bound exponent, with the published side read as generously as possible: inf over a >= 1, b >= gamma of a E(b/a)
(monotone in both arguments, ratios above 1 by symmetry). Exact against everything derivable from ZBS's bank P0r12
and EvolvingPrograms' bank (959f46b0); floats (21 points per cell with a slope margin; a log grid below 1/5) for Lu-Wang's
f, GNNW (Theorem 1, Theorem 5 at its optimal p, Corollary 6), Neisler-Shin-Sukhatankar and Erdos-Szekeres (Section 4,
v2 after the referee). Pointwise gains 2.8e-3 to 6.5e-3 in the exponent on (0.2, 1) (2.5e-3 at gamma = 1 is Theorem
2U's own); cellwise conservative gains >= 1.7e-3.

**What it rests on.** Only the chain of SC Theorem 2U: Theorem 5.7 in our restated form (SC Section 16, P3.3, with
P1, P2, P4 and the extended controls of SC 6.10), applied to the bank certCD3-full (SHA-256 32bcafd3...07af8), which
checkers A and B accepted with the proviso min(eps_h, eta_h) = 5e-13 > 7.57e-15 (SC 18.3-18.4). New here: Corollary O
(Section 2; the off-diagonal form of SC Corollary 5.10, a few lines) and the finite certificate of Phi (Section 3).
Conservative variant without Lemma D (chain of Theorem 1U): `cert/offdiag_k3_v1.json` over certK3-full, at most
7.9e-4 above the CD3 values cellwise (e.g. 0.751603947 vs 0.750926046 at 2/5, 0.857571908 at 1/2, 1.183822672 at 9/10;
2e-6 below at 3/5, the banks being different), also below every published bound from 201/1000; checkers A and B
both accept it with identical Phi tables.

**Weight.** It is a corollary of the lab's diagonal machinery plus an exact
function certificate; the improvement is over AI-generated, unrefereed prior work (ZBS, EP) by 2.5e-3 to 6.5e-3 in
the exponent; over the best refereed-type bound (GNNW 2407.19026 Theorem 1) by 0.015 to 0.062. No new idea beyond
reading the bank at every ratio.

## 1. Transfer map (step 1): which parts carry over, and every use of symmetry

Read for this map: SC Sections 1.1-1.7, 2, 6.10, 13, 14 (P1), 15 (P2), 16 (P3), 17 (P4), 18; grep of SC for
"renam", "naming", "symmetr", "k, k", "1/2".

| Block | Object | Uses k = l or colour symmetry? | Transfers? |
|---|---|---|---|
| P1 (SC 14) | local step: CERT, Thm 3.4, Prop 3.5 | No. Red density p from X to Y; targets red K_k, blue K_t in X, blue K_l in Y are already asymmetric and ratio-free. The "symmetry" of Step 4 (SC line 1482) is the symmetry of the undirected blue graph BB, not of the colours. | Yes, unchanged |
| P2 (SC 15) | Thm 4.2 finite-host closure, Lemmas 4.3-4.5 | No. Arbitrary k, t, l; Stop(C, xhat, yhat, l) for every a. | Yes, unchanged |
| P3 (SC 16) | Lemma 5.8 (leaves, routes) | No. One naming fixed; any ratio b/k in J. | Yes |
| P3 | P_V(C) "under both namings" | Symmetric hypothesis, used for every pair (k, b). | Yes |
| P3 | Lemma 5.9, complementary pair | Uses renaming: (k, b) at ratio r becomes (b, k) at ratio 1/r. Already a statement at every r. | Yes; this IS the off-diagonal mechanism |
| P3 | Thm 5.7 Stage 3, source covers | Same renaming as Lemma 5.9; every source claim is for all (k, b). | Yes |
| P3 | **Cor 5.10 (diagonal bound)** | **The only use of k = l**: the root pair (R, R) at ratio 1, density 1/2 + 1/2 = 1. | **Replaced by Corollary O (Section 2)** |
| P4 (SC 17) | Thm 2.2' (Lu-Wang source), Lemma B.1' | Uses G_F(a, b) = G_F(b, a) ("rename the colours if needed", SC line 1999), true by the definition of G_F (P4.1: G_F(a, b) = max(a, b) F(min/max)); the renaming keeps N and the threshold, so a least counterexample stays least. Theorem 2.2' is stated for all integers a, b >= 1. | Yes, unchanged |
| Lemma C, Thm A, Lemma D (SC 3, 6, 7) | one control's CERT / finite test | No k, l at all. | Yes, unchanged |
| 2a lines (SC 18.1) | f-hat(lambda) <= c + d lambda for all lambda > 0 | No. | Yes |
| 2b source (SC 18.2) | Lu-Wang certificate on [1e-16, 1] | No. | Yes |
| 2c bank (SC 18.3) | 4,099 raw / 1,015 closed profiles, 7,574 sources, 2,747 controls | Profiles at densities j/80 (and j/160 near 1/2) on ratios in [1/5, 5]; only the root (raw 2196, closed 13) is diagonal-specific. | Yes, at ratios [1/5, 5] |

What changes for l = gamma k. Only Corollary 5.10. The two sides of the pair are no longer one profile: a red-side
profile R at ratio gamma with density p_R and a blue-side profile S at ratio 1/gamma with density p_S <= 1 - p_R. The
best split moves away from 1/2 as gamma falls (certificate: p_R = 0.50625 at 0.95-0.99, 0.51875 at 0.9, 0.5375 at
0.8, 0.5625 at 0.7, 0.5875 at 0.6; at gamma = 1/4, 3/10, 2/5, 1/2 the extreme split p_R = 0.0125, p_S = 0.95, i.e.
the red side is almost unconditional and the blue side is a dense-host profile).

Limits of the transfer (each a dated finding, 19 Nov):
1. Ratios below 1/5: the bank has no profile there (ZBS's design, kept by our generator); the sources there are
   Lu-Wang tangents. No gain for gamma < 0.2; at gamma = 1/5 Lu-Wang's f is better by 1.1e-5.
2. The bank was optimised for the diagonal root only. Off the diagonal Phi comes from generic profiles with 1/400
   knots. At gamma = 1 the dedicated root is 6.4e-4 below the best generic pair (1.247786 vs 1.248430), so dedicated
   roots at other ratios would give roughly that much more (float, measured at gamma = 1 only).
3. Multicolour R_r(k), r >= 3: nothing transfers. The local step, Theorem 4.2, the banks and complementary pairs are
   two-colour objects; the reduction R_r(k) <= R(k, R_{r-1}(k)) needs ratios l/k exponential in k, outside every
   profile interval. A multicolour version needs an r-colour local step: new mathematics, not a transfer. Dated
   negative for the cheap multicolour route (19 Nov 2026, 22:0x +04).

## 2. Corollary O (new; the off-diagonal form of SC Corollary 5.10)

Let B be a bank satisfying the hypotheses of SC Theorem 5.7 with its proviso, and C_* its constant.

(a) For every source pair h of B and all integers k, l >= 1:
    R(k, l) <= ceil(C_* e^{A_h k + B_h l})  and  R(k, l) <= ceil(C_* e^{B_h k + A_h l}).
(b) Let P, Q be profiles of B (direct or combined) with p_P + p_Q <= 1, and k, l >= 1 integers with r = l/k in I_P
    and 1/r in I_Q. Then R(k, l) <= ceil(C_* e^{k max(L_P(r), r L_Q(1/r))}).

Proof. (a) By Theorem 5.7, (SOURCE_h) with C = C_* holds for every host: |V| >= C_* e^{A_h k + B_h l} implies a red
K_k or a blue K_l. A red/blue colouring of K_N with N >= ceil(C_* e^{A_h k + B_h l}) is such a host, so R(k, l) is at
most that number. Swapping the colours shows R(k, l) = R(l, k), and (a) at (l, k) gives the second bound.
(b) Let M = max(L_P(r), r L_Q(1/r)) and N >= C_* e^{kM}. Profiles are positive (Definition 5.3), so N > 1 and the red
density d_R of a colouring of K_N is defined. If d_R >= p_P, (ASSERT_P) (Theorem 5.7) at the integer pair (k, l),
whose ratio r lies in I_P, applies since N >= C_* e^{k L_P(r)}: a red K_k or a blue K_l. Otherwise the blue density is
d_B = 1 - d_R > 1 - p_P >= p_Q. In the colouring with the colours swapped the red density is d_B >= p_Q, and
(ASSERT_Q) (Theorem 5.7 holds for every host, so for this one) at the pair (l, k), ratio k/l = 1/r in I_Q, applies
since its threshold is C_* e^{l L_Q(k/l)} = C_* e^{k r L_Q(1/r)} <= N: in the swapped colouring a red K_l or a blue
K_k, i.e. in the original a blue K_l or a red K_k. []

This is SC P3.4's proof with the pair (R, R) at ratio 1 replaced by (P, Q) at ratio r; Lemma 5.9's complementary case
is the same argument for a combined profile. Combined profiles may be used in (b) because Theorem 5.7 asserts
(ASSERT_Q) for them as well (Stage 2).

Premise on the bank (referee finding 3). The certificate's "raw" profiles are the bank's direct profiles (Definition
5.4) and its "closed" profiles the combined ones (Definition 5.5). The off-diagonal checkers accept ANY in-range index,
so Theorem O needs every object of certCD3-full to be validated, not only the root's reference cone. It is: the bank
checker validates all 7,574 sources, 4,099 raw and 1,015 closed profiles (research/tier2/ramsey-zbs/code/checkA/runA.py
lines 28-37; the counts are in certCD3-full_A.json), and SC 18.3 reports checker B on the same full certificate.

Proof of Theorem O from Corollary O and the checks. Take B = certCD3-full. Let l/k = r lie in cell i. If the cell is
'src' with source h and orientation AB, (a) gives R(k, l) <= ceil(C_* e^{k (A_h + r B_h)}) and the check gives
A_h + r B_h <= Phi_i(r) (BA: B_h + r A_h with the second bound of (a)). If the cell is 'pair' (R, S), the checks give
p_R + p_S <= 1, [lo_i, hi_i] in I_R, [1/hi_i, 1/lo_i] in I_S (so r in I_R and 1/r in I_S) and
max(L_R(r), r L_S(1/r)) <= Phi_i(r); apply (b) with P = R, Q = S. Monotonicity of ceil finishes.
Asymptotic form: for gamma in [1/5, 1) let i be the cell with lo_i <= gamma < hi_i. For k >= max(5, 1/(hi_i - gamma)) the
integer l = ceil(gamma k) has l/k in [gamma, gamma + 1/k], inside cell i, so
R(k, floor(gamma k)) <= R(k, ceil(gamma k)) <= ceil(C_* e^{k Phi_i(gamma) + s_i}), s_i = |slope of Phi_i|. At gamma = 1
the last cell is [1 - 1e-10, 1] with the root pair and Phi = 623893233463/500000000000 (z of Theorem 2U rounded up by
2e-12).

## 3. The certificate and the two checkers

Format (built by `code/ramsey_offdiag_build.py`, a float search that proves nothing): bank SHA-256, g_lo = 1/5, and
cells {lo, hi, v_lo, v_hi, kind, refs}: kind 'src' (h, orient AB/BA) or 'pair' (R, S as [raw|closed, index]). Cells:
step 1/2000 on [1/5, 1999/2000], then [1999/2000, 1 - 1e-10] and [1 - 1e-10, 1]. v_lo, v_hi are float needs rounded up
to 1e-12 plus 2e-12.

Finite reduction (written independently in both checkers): Phi_i is affine; A + rB is affine; L_R is affine between
its knots; on a piece of S where L_S(t) = c + d t, r L_S(1/r) = c r + d is affine in r, with breakpoints r = 1/y for
the knots y of S. So Phi_i minus each bound is continuous and piecewise affine on the cell, and it is >= 0 on the cell
iff it is >= 0 at lo, hi, the knots of R inside (lo, hi) and the points 1/y for knots y of S inside (1/hi, 1/lo).
Interval containment is checked before any evaluation.

Checks (19 Nov 2026, 21:2x-21:4x +04):
- Checker A (`code/ramsey_offdiag_checkA.py`, Python Fractions, written by this lane): ok, 1,601 cells, min slack
  2e-12 for both kinds, 17 s (runs/checkA_cd3_v1.json). certK3-full variant: ok (runs/checkA_k3_v1.json).
- Checker B (`code/ramsey_offdiag_checkB.py`, python-flint 0.9.0 fmpq, written by a separate agent from a written
  specification without opening checker A or the builder): ok, same certificate SHA-256, 1 src + 1,600 pair cells,
  2 + 3,200 + 4,782 points checked, min slack 2e-12 (runs/checkB_cd3_v1.json). The two Phi tables (17 exact rationals)
  are identical.
- Red controls (`code/ramsey_offdiag_red_make.py`, `code/ramsey_offdiag_red.sh`; tampered files on the SSD,
  quantavane-archive/ramsey-offdiag/red_cd3_v1): 10 tampers (pair v_hi - 1e-9, src v_lo - 1e-9, densities summing
  above 1, tiling gap, wrong bank hash, R interval missing the cell, string index, src orientation swapped, last cell
  missing, unknown kind), each refused by BOTH checkers with the expected reason; the clean file accepted by both
  (runs/red_checkA_cd3_v1.log, runs/red_checkB_cd3_v1.log). Checker B's author also ran 7 tampers of its own (all
  refused) and a synthetic unit test where the violation sits only at an interior R knot or only at an interior S
  breakpoint (refused).

## 4. Comparison with the literature, and prior art (step 4), 19 Nov 2026 21:2x-21:5x +04

Baseline, made as low as possible (code/ramsey_offdiag_vs_published.py, exact for the banks):
- ZBS P0r12 (github.com/w2ll2am/diagonal-ramsey @ c2875f33; zbs_bank.json SHA-256 2946c656...): all 2,713 sources in
  both orientations; every pair of its 1,902 raw and 1,003 closed profiles with p_R + p_S <= 1.
- EvolvingPrograms/DiagonalRamsey @ 959f46b06e (head unchanged, pushed 1 Nov, 0 forks): its 2,716 sources = ZBS's
  2,713 + the chosen source (A_s, B_s) (L1_Parameters.lean) + two auxiliary sources (Candidate6330Prefix,
  Candidate600Prefix control A, B); every profile literal of Append.lean, Source/Profiles.lean,
  Source/HullProfiles.lean and L4_Routes.lean (205, treated as valid claims, which only lowers the baseline); its
  diagonal 625145177/500000000, and monotonicity of R(k, l) in l.
- Cellwise test v2 (code/ramsey_offdiag_vs_published2.py, after referee finding 1). The generous published exponent at
  gamma is inf over a >= 1, b >= gamma of a E(b/a): a published claim at ratio y counts against gamma when y >= gamma
  (E(y) > Phi(gamma) needed) and when y < gamma (E(y)/y > Phi(gamma)/gamma needed; this also covers ratios above 1).
  Since Phi_i(g)/g = c_i/g + s_i is monotone on a cell, published claims on cell j are tested against
  T_j = max(W_j, hi_j max_{i >= j} max(v_lo_i/lo_i, v_hi_i/hi_i)), W_j = max_{i0 <= i <= j} max(v_lo_i, v_hi_i), i0 the
  first cell of the claim (lo = 201/1000); cells below i0 against hi_j max_{i >= i0}(...); ratios below 1/5: no
  published pair exists (every published profile ends at ratio <= 5, asserted), sources exactly at y = 1/5 (A/y + B is
  decreasing), curves on a log grid of [2e-5, 0.2] (float). Results (runs/vs_published2_cd3_v1.log): all 1,599 cells
  of the claim pass, the 2 cells below pass as ratios y < gamma, the diagonals pass, ratios below 1/5 pass (min f(y)/y
  = 2.443664 against max Phi(g)/g = 2.424145): ALL_OK. The certK3 variant: the same, ALL_OK
  (runs/vs_published2_k3_v1.log). (v1, runs/vs_published_cd3_v1.log,
  used only W_j and missed the y < gamma direction; the data were already fine.)
- Non-bank curves inside v2 (floats, 21 points per cell, slope margin 9 x spacing, against T_j): Lu-Wang f
  (source.json @ 5ec98f47), GNNW arXiv:2407.19026v2 Theorem 1 (H(l) + (-0.25 l + 0.03 l^2 + 0.08 l^3) e^{-l}, read on
  the arXiv HTML page), Theorem 5 at its optimal p in closed form, p* = (phi/2 + l/phi)/(phi (l + 1/2)), Corollary 6,
  NSS (wamlat/RamseyLean-bootstrap @ e53b8cf11d, pq_cert_final.json), Erdos-Szekeres. The earlier sampled check
  (runs/lit_curves2_cd3_v1.log: two points per cell, Theorem 5 on a p-grid) was exploratory only (referee finding 2);
  its smallest margins were 2.3e-3 (Lu-Wang f) and 2.8e-3 (NSS).
- CGMS arXiv:2303.09521v2 (Annals 2026): Theorem 1.2, R(k, l) <= e^{-delta l + o(k)} binom(k + l, l) for some delta > 0,
  unspecified: weaker than GNNW.
- Prior-art searches: arXiv math.CO /list/recent (13-19 Nov), arXiv search "off-diagonal Ramsey" and "Ramsey numbers
  upper bound" by announcement date: no new R(k, gamma k) or R(k, k) upper bound (2609.04596 is multicolour R_r(k));
  OpenAlex works citing CGMS (W4327811148; 16 since 15 Aug 2026) and GNNW (W4401201099; 11): the only new upper-bound
  work is E. A. Puerto, Zenodo 10.5281/zenodo.23885217 (2 Nov 2026), an eight-step GNNW iteration with diagonal
  3.76973, the same method and level as NSS (not evaluated numerically; NSS is above Lu-Wang's f at every point
  checked in [0.2, 1]);
  GitHub: no repository pushed since 1 Nov matches off-diagonal/diagonal Ramsey bound searches, and code searches for
  w2ll2am/diagonal-ramsey, EvolvingPrograms/DiagonalRamsey, 625145177 and luWangSource find only EP itself. ZBS
  (c2875f33, 8 Oct) and Lu-Wang (5ec98f47) unchanged. Nobody has stated the off-diagonal function of the ZBS or EP
  banks; the baseline above is our generous reading of them.

## 5. Not claimed

- Nothing for gamma < 201/1000.
- Phi is not optimised off the diagonal (Section 1, limit 2).
- No multicolour result (Section 1, limit 3).
- The record is against unrefereed, AI-generated work (ZBS, EP), as is the diagonal result it rests on.

## 6. Referee record

19 Nov 2026 21:4x-21:5x +04, one fresh-context referee (told to find errors; read Sections 0-4, SC 1.4 and 16-17, both
checkers, the comparison program; scope widened to the transfer map, Lemma 5.9 / Stage 3 at
reciprocal ratios and Lemma B.1'). Verdict: PASS WITH FIXES, no ERROR. Corollary O (a) and (b) follow from Theorem 5.7
as restated; both checkers check exactly what the deduction needs, with a sufficient finite reduction and exact
arithmetic; the transfer map items (i)-(iii) PASS (Corollary 5.10 is the only use of k = l). Findings and responses:
1. GAP, comparison baseline missed monotonicity in k and ratios above 1: fixed by vs_published2.py (Section 4), with
   one further correction found while running it (some cells of the certK3 variant have a negative intercept, so the
   maximum of Phi_i(g)/g is taken at either end).
2. GAP, sampled float check of NSS / GNNW Theorem 5 / Corollary 6: moved into the v2 test with a slope margin and the
   closed-form optimal p.
3. NIT, bank premise: stated (Section 2).
4. NIT, monotone hull lower than Phi near 1: stated (Section 0).
5. NIT, k >= 5: added.
6. NIT, the gamma = 1 gain is Theorem 2U's: stated in the table and the comparison paragraph.
7. NIT, decimals "rounded up" in checker A were float-rounded: now exact ceilings (checker A v2; reruns
   runs/checkA_*_v2.json give the same exact Phi values).
8. NIT, g_lo not pinned: checker A now requires g_lo = 1/5 (red control r11 refused by A at the pin and by B at the
   tiling); checker B reports g_lo and checks cells[0].lo = g_lo.
10. Wording of the P4 row: corrected (Section 1).
No re-referee of the fixes (they are the referee's own specifications and touch the comparison and reporting, not the
soundness of Theorem O).
