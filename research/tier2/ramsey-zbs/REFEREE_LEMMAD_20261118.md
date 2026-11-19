# Referee report: Lemma D (CERT_DESIGN.md) and its two checkers

Fresh-context referee, 18 Nov 2026. Material frozen at c3a828dee; re-checked against 3683ff5e9 at the ramsey-zbs
agent's request (diff: one line each in checkD_A.py / checkD_B.py adding x < (1-mu)^w, one tamper in tamper_D.py,
text edits to CERT_DESIGN.md D1/D5/D8/Section 2/Section 6/Section 7, PROOF.md edits). The working copies of
research/tier2/ramsey-lemma/cert and CERT_DESIGN.md equal 3683ff5e9; the copies in ramsey-zbs/code/lemmaD match its
MANIFEST.sha256. Theorem A itself (PROOF.md) was NOT refereed; I read only its statement.

## Summary of verdicts

| item | verdict |
|---|---|
| (1) Lemma D proof, D0-D8, U(B) | OK (no wrong inequality found). Four GAPs in the written proof (G1-G4), none changes U(B) or the checkers |
| (2) covering rectangle | OK |
| (3) checker faithfulness | OK at 3683ff5e9. At c3a828dee: GAP (x < (1-mu)^w not checked, now fixed). Process GAP: the U(B) formula is shared line for line by A and B |
| (4) interface to the ZBS bank | OK given Theorem A and S7 as stated; Lambda should be made explicit |

No ERROR found.

## Runs (python-flint 0.9.0 venv, nice -n 10, single thread, cwd ramsey-lemma/cert)

- checkD_A.py certs/c1722_m300.json: `checker A: 97 boxes, all U < 0; worst U = -8.892874e-08 at Phi in [0.0393054,
  0.0408172], p in [1.35348, 1.41824] {j0 637, jA 509, th 0.4784, K 0.01607, IL -0.012668, IR2 0.012637, dvar 0,
  kEcap 1.14e-05, kEhigh 4.57e-06}` / `checker A ok` (14 s). Same output under /usr/bin/python3 3.9.6.
  `python3 -O checkD_A.py ...` prints `checker A uses assert statements; refusing to run under python -O`, exit 1.
- checkD_B.py certs/c1722_m300.json: `checker B: 97 boxes, all U < 0; worst U = [-1.7448186e-8 +/- 4.85e-16]` /
  `checker B ok` (3 s).
- tamper_D.py certs/c1722_m300.json: at c3a828dee `ALL 12 TAMPERS REFUSED BY BOTH`; at 3683ff5e9 `ALL 13 TAMPERS
  REFUSED BY BOTH`, the new one (`w -> 3`) refused by A with `x < (1 - mu)^w` and by B with `x < (1-mu)^w`. (The
  13:1x note in CERT_DESIGN.md Section 7 calls it "a 14th tamper"; the script has 13.) Same outputs at both commits
  for the other 12. Reasons: 10 of the 13 are refused by data assertions before any box is bounded; only `tree ->
  single leaf` (U = +2.46e-3) and `merge the worst leaf` (U = +9.17e-7) exercise U(B), plus `jA0 -> last node`.
- Extra (not asked): c1701_m280.json, A: 72 boxes, worst -1.029008e-06; B: worst -1.0353553e-6. This does NOT match
  CERT_DESIGN Section 7, whose c1701 row says "-6.2e-7 / -5.3e-7" (box count 72 matches). See fix F7.
- Referee's semantic red/green controls (scratch script tamper2.py: regenerate the data with genD.skeleton for
  x' = x e^s, keep the certificate's tree): s = 0 accepted by both (-8.89e-8 / -1.74e-8); s = +2e-6 (a lower by
  2e-6) REFUSED by both (A: leaf U = +9.36e-7); s = +2e-5 REFUSED by both (U = +2.65e-6); s = -2e-5 accepted by both
  (worst -1.039e-5). The bound is live and the certified point sits within about 2e-7 in a of this tree's limit.
- Referee's float brute force of V_A itself (scratch bruteVA.py; proves nothing): explicit admissible profiles with
  the adversary's largest gaps eta_k = m(v_k)/v_k on the exact grid u_b + kD (10^6 cells), phi(1-) = -w, nine
  right-region shapes (phi**, exponential desaturation lambda = 0.5..25, flat gaps) and three left-region shapes,
  at five points of the three worst leaves. Every V_A is below checker A's point-box U: margins 2.2e-5 to 1.0e-4
  (e.g. (0.040817, 1.3534): max V_A -9.66e-5, U(point) -1.20e-5). No contradiction; the test cannot see errors below
  about 1e-5.

## (1) Lemma D, step by step

D0. OK. Ht is C^1 across A = B (the computation Ht'_bind = pA + (1-p)B + qB' = (qB)' at A = B is right). G0 for the
shifted pair (x e^eta, mu e^{eta/w}) is G0 - beta eta exactly, so a(eta) is the left root of G0 = beta eta; a' =
beta/G0'(a), a'' = -beta^2 G0''/G0'^3 > 0 (G0'' = beta w (1/q + 1/(1-q)) > 0, G0'(a) < 0 strictly because the
level set is crossed). Convexity also holds across the regime x e^eta >= p where a = 0 (max of a convex decreasing
function and 0), so (D0.1) a(eta) >= a(0) + a'(0) eta >= a_cut - alpha eta holds for ALL eta >= 0. The role of
alpha: G0' increasing and a(0) < a_hi give |G0'(a(0))| >= |G0'(a_hi)|, which needs G0'(a_hi) < 0; both checkers
assert that sign. Say in the text that (D0.1) also covers eta >= log(p/x) (a = 0).

D1. Conclusion OK, justification GAP (G1). With Theorem A's phi(1) = phi(1-) (PROOF.md: "phi(1) means the left
limit"; 3683ff5e9's new header says the same), "lowering phi(1) to -w changes phi at one point only" is false: a
one-point change does not move a left limit. The correct argument: treat f1 := phi(1-) as a parameter that enters
V_A only through the restriction q M(q) >= q f1 + c(u; f1); its f1-derivative is q - a(eta_{m-1}) v_{m-1} > 0 for
u <= v_{m-1} and q > 0 for u > v_{m-1}, so V_A is nonincreasing in f1 and f1 >= -w gives V_A(f1) <= V_A(-w). From
then on Delta_{m-1} := phi(v_{m-1}) + w (this is what D3, D6 and both checkers use).

D2. OK (c nonincreasing; c(u) >= C for u <= u_b because u_b is a scale; scales below u_b only add nonnegative terms).

D3. OK. eta_k v_k <= m(v_k) from admissibility; a0 = a_cut > 0 (asserted) is needed for a0 S >= a0 (lower bound of
S); weight v_k >= s - D on cell k; int_{[u_b,1]} s d(-phi) = w + u_b p_b - Phi_b uses Phi(1) = 0 and phi(1) = -w.
The box minimum C0 = a0 (w + u_b pl - Ph - D(ph + w)) has every corner in the right direction.

D4. OK. Superlevel bound q0 - q <= (H(q0) - C0 + G)/H'(q0) <= Delta0 + G/h1 for q < q0 (concavity, H(q0) >= C0,
H'(q0) >= h1 > 0); Ht concave gives the linearisation with s0 <= Ht'(q0); Ht(q0) - q0 y <= h_j0 - q_j0(w+y). j0 >= 1
is enforced (both checkers search from j = 1), so q0 >= a_hi is in Q. Lemma M is correct (the integration by parts
needs only bounded slopes; phi may be unbounded near 0). Phi <= Phi* with equal ends on [0, u_b] is right
(Phi* concave as a min of concave functions).

D5. OK. (A): Phi <= Phi** with Phi**(1) = 0 because Phi_b + p_b(1 - u_b) >= 0 for feasible pairs. (B): subgradient
-qhat(phi(u)) of Hhat; integration by parts against the absolutely continuous m with m(1) = 0; the 3683ff5e9 note on
the jump of Q at u_b+ is right.

D6. OK as computed by the checkers; the text has two gaps.
- slope: y = Ht'(qhat(y)) for y in [y_c, y_top] needs y_c >= Ht'(mu) (asserted) and qhat(y_top) >= q_A (certified by
  the largest node with Ht'(q_j) >= y_top). Per cell, int_cell m dQ >= (min_cell m) Delta Q_k and
  m(v_k) <= min_cell m + D Lip, Lip = max(phi_s(u_b), ph) + w >= |phi_s - phi|. OK.
- high band: m(v_k) <= m_b for cells whose drop passes a level >= y_sp >= phi_s(u_b) (concavity of g). OK.
- cap: m(v_k) <= g(v_k) + (1 - v_k) y + D(ph - y), beta_max(y) = y + w e^{-1-y/w} (maximiser e^{-1-y/w} <= 1 since
  y >= -w), E_cap integral correct. OK.
- G2 (text): the leftover per high-band cell is kappa(1-r) m(v_k) Delta + kappa r (m(v_k) - min_cell m) Delta,
  r = kappa2h/kappa2, so besides "(1 - kappa2h/kappa2) kappa m_b (ph - y_sp)_+" there is a grid term
  kappa r D Lip (ph - y_sp)_+, and E_grid is never defined in the text. Both checkers use E_grid = Lip D (ph - y_c)_+,
  which covers the middle and the high band's grid terms when y_sp >= y_c. Define E_grid that way in D6.
- G3 (text): the band split assumes y_c <= y_sp (and the high-band slope bound needs y_sp >= Ht'(mu)); neither
  checker asserts it. The checkers' U(B) stays valid in every order: assign the levels [y_sp, y_c) to the cap band
  (full bound, no charging); the high band [y_c, ph] then has m <= m_b and the slope bound, and the code's
  (ph - y_sp)_+ and (ph - y_c)_+ terms over-cover it; if y_c > ph everything is in the cap band and
  kappa sum m Delta - theta int m dQ <= kappa E_cap. Say so in D6 (or assert y_sp >= y_c; it holds with a wide margin,
  y_sp = 1.15 vs y_c = -0.31 for c1722).
- theta <= 1 checked; kappa2h <= kappa2 clamp is valid (a smaller kappa2h is a weaker true bound).

D7. OK, verified by differentiating the switch-point formulas:
- dIL/dPhi = (F(phi_s(u1)) - F(p))/(phi_s(u1) - p) <= -q_j0 (F = Psi_j0+, slopes in [-q_N, -q_j0]); IL
  nonincreasing in p by Lemma M; needs Phi >= p u_b, which P1 >= pl u_b guarantees (else the box is refused).
- dK/dPhi in [0, 1] (difference quotient of the 1-Lipschitz (. - s0)_+), which is what justifies "+ (g+ - g-)" and
  evaluating K at min(Ph, g-); K nonincreasing in p. The text should state dK/dPhi <= 1 (G4).
- dIR2/dPhi = minus the average slope of Hhat+ on [phi_s(u2), p] <= active q at drift phi_s(u2); as Phi grows u2
  falls, so the maximum over the box is at the LARGEST u2, i.e. the upper end b2 of u2's enclosure at (P1, ph). The
  checkers take exactly that; the text's "q_R = active slope ... at drift phi_s(u2)" should name b2 (G4).
- G4 also: when P1 + ph(1 - u_b) < 0 (possible for boxes with ph < 0), switch_right's stated precondition fails and
  the bisection returns u2 in [1 - 2^-70(1 - u_b), 1], i.e. IR2 = (1 - u_b) Hhat+(ph). That is the correct continuous
  extension of IR2(., ph) below Phi = -ph(1 - u_b) (constant, derivative 0 <= q_R, and q_R is then taken at b2 = 1),
  and every feasible Phi_b of the box is >= -ph(1 - u_b). Valid, but the docstrings of switch_right (both checkers)
  claim a precondition box() does not enforce; state the extension in D7.
- T(Phi) uses max(0, g- - Phi) <= m_b and qB <= qhat(ph) <= qhat(p_b) (qB = a_cut when no node qualifies: valid).
  E_high uses m_b <= g+ - P1, valid because every feasible Phi_b of the box is >= P1.
- Assembly: V_A <= IL + (Delta0 + G/h1) K + int_{u_b}^1 Hhat(phi) <= T(Phi_b) + Delta0 Kv + kappa(E_grid + E_cap +
  E_high) <= U(B), with Delta0 >= 0, Kv >= K, kappa = alpha Kv/h1. Every term enters with the right sign and
  rounding.

D8. OK. The proof works for ANY grid that contains u_b and has mesh <= D on [u_b, 1] (scales below u_b arbitrary);
the integrality of (1 - u_b)/D only makes 1 a grid point of the uniform grid. 3683ff5e9's correction of "< 1e-9" is
right in substance (the mesh terms are in U(B) explicitly).

Edges of the rectangle: Phi_b = g(u_b) (m_b = 0), Phi_b = 0, p_b = -w and the corner (g(u_b), -w log u_b) (feasible:
phi = -w log u_b on [0, u_b]) are all inside boxes the formula handles; boxes with pl u_b > g- are refused (box
returns None), which fails safe; infeasible boxes (Pl > g+, pl u_b > min(Ph, g+), ph(1 - u_b) < -Ph, ph < -w) are
correctly discarded. Conclusion: U(B) < 0 on every leaf of a cover gives V_A <= U(B) < 0 for every admissible
(phi, eta).

## (2) Covering rectangle: OK

Phi is concave with Phi(0) = Phi(1) = 0 (phi nonincreasing, int phi = 0), so Phi_b >= 0; Phi_b <= g(u_b) by the
support bound. p_b = phi(u_b) >= -w; u_b p_b <= Phi_b <= g(u_b) gives p_b <= -w log u_b. The checkers use
[0, G_up] x [-w, P_up] with G_up >= g(u_b) and P_up >= -w log u_b asserted (outward rounded).

## (3) Checker faithfulness

Hypotheses verified by both, by recomputation (nothing taken from the certificate except a_cut, a_hi, alpha, u_b,
D, the q-grid, y_c, jA0, G_up, P_up, tree):
- ranges 0 < p, mu, beta < 1, w > 0, 0 < x < p; x < (1-mu)^w only at 3683ff5e9 (A: x < lo(exp(w log(1-mu))), B: Arb
  strict <; both outward-correct);
- G0(a_cut) >= 0 > G0(a_hi), G0'(a_hi) < 0, alpha >= beta/|G0'(a_hi)| (upper end of the enclosure);
- (1 - u_b)/D a positive integer; q_0 = a_cut, q_N = mu, strictly increasing, q_1 >= a_hi;
- every node q_1..q_N certified in D: B explicitly (G0 < 0 in jet); A only implicitly (jet raises ArithmeticError if
  Z <= 0 is possible on the binding branch; A <= B certified implies G0 < 0). So mu in Q is certified by both, but A
  has no explicit `G0(mu) < 0` assertion (F2);
- y_c >= Ht'(mu); |Ht''| enclosures on every cell from jA0 (interval / Arb ball over the closed cell, both branches
  when the cell straddles A = B);
- node heights computed by the checker: A right-end tangent, B the better end tangent (left tangent only for i >= 1,
  so never at a_cut, which may lie outside D); values rounded up (A: cup to 2^-90; B: ub_q); H(q_j) <= h_j holds;
- coverage: both walk the bisection tree from the fixed rectangle, so leaves tile it with only boundary overlap; A
  treats any non-'P' tag as a p-split (still a valid cover), B raises on unknown tags;
- U(B) < 0 on every leaf, every term an upper bound (checked term by term above).
Floats: none in any decision (only in messages/info dicts; genD's floats only propose data). Asserts: A has 17 and
ivA has some; both refuse python -O at import (verified). B uses explicit raises only.

Independence. The arithmetic layer is genuinely independent (A: hand-derived two-branch H, H', H'' with own dyadic
intervals; B: Lemma C(iii) representation with arb_series derivatives; stack hull vs gift-wrapping successor map;
different node heights, so different U values). The bound layer is NOT: checkD_B.box is a line-by-line
transliteration of checkD_A.box (same P1/PK clamps, same "+ (gh - gl)", same qB fallback, same qR rule, same E terms,
same variable names). A shared error in U(B) would pass both; only this referee pass (and the float brute force)
guards it. Docstring inaccuracies in B: "bisection in log u" (it is linear bisection) and "tangent at the LEFT end"
(it takes the better of the two).

Interface side effects (ramsey-zbs, not soundness): importing checkD_B inside ctlB sets the global
flint.ctx.prec from 320 to 300 for every later Arb computation of checker B; checkD_A's `import ivA` resolves to
ramsey-zbs/code/checkA/ivA.py already in sys.modules (byte-identical today, f6fe4408..., but fragile); ctlA's comment
still cites c3a828dee.

## (4) Interface: OK, given Theorem A and S7

A control {p, mu, w, beta, x, lxU, l1mL, lemmaD} passes iff CtrlD.ok and checkD_X.check(...) pass. Then:
- 0 < x < min(p, (1-mu)^w): x < p by both; x < (1-mu)^w by CtrlD.ok already at c3a828dee (x <= e^lxU, lxU < w l1mL,
  e^l1mL <= 1 - mu, all outward-rounded), and at 3683ff5e9 also inside checkD_A/checkD_B. So the gate-1 point was a
  gap for standalone Lemma D runs (Section 7's table), not for the bank path; the new check closes it for both.
- Q nonempty: mu in Q is certified (B explicitly, A via jet at q_N = mu); a_hi in Q as well. Definition 5.2' does
  not need it ((INF) replaces "F nonempty and CERT < 0"), but it holds.
- V_A < 0 strictly for every admissible (phi, eta) on Lambda = {u_b + kD}, i.e. (INF-b), hence (INF) by Theorem A,
  hence Lemma 4.5', Theorem 4.2' and Definition 5.2' as stated in PROOF.md S7.
- Lambda is implicit in the control (it is {u_b + k Dplus : 0 <= k <= (1 - u_b)/Dplus}); L_0 of Theorem 4.2' depends
  on it (v_1 = u_b = 3/100, 10^6 + 1 scales). Record it explicitly (F6).
- This rests on Theorem A and S7, which I did not referee; at 3683ff5e9 PROOF.md calls Theorem A proved by S6 + S7.

## Required fixes

F1 (D1, G1). Replace "Lowering phi(1) to -w changes phi at one point only" by the monotonicity-in-f1 argument above
    and define Delta_{m-1} = phi(v_{m-1}) + w explicitly. Still needed at 3683ff5e9 (only the header changed).
F2 (checker A). Add an explicit `assert C.G0(mu).hi < 0` (or check in build_lines) instead of relying on jet's
    exception, so "Q nonempty" is an assertion in both checkers.
F3 (D6, G2/G3). Define E_grid := Lip D (ph - y_c)_+ and say it covers the middle and the high band's grid terms;
    state the band assignment when y_sp < y_c or y_c > ph (or assert y_sp >= y_c in both checkers).
F4 (D7, G4). State dK/dPhi in [0,1] (justifies + (g+ - g-)), that q_R is taken at the upper end b2 of u2's
    enclosure at (P1, ph), and the extension of IR2 when P1 + ph(1 - u_b) < 0; fix the switch_right docstrings.
F5 (independence). Record in CERT_DESIGN Section 4 that checker B shares checker A's U(B) formula verbatim, so the
    two checkers are independent only below the box bound; fix B's two docstring inaccuracies.
F6 (interface). Put Lambda (or u_b and D with "Lambda = {u_b + kD}") in the CD control's recorded data and in the
    Definition 5.2' statement used by the bank; update ctlA's c3a828dee comment; restore flint.ctx.prec after
    importing checkD_B, or set it per call.
F7 (records). Section 7: the c1701 row says worst U -6.2e-7 / -5.3e-7 but both checkers print -1.029e-6 /
    -1.035e-6 for certs/c1701_m280.json; the 13:1x note says "14th tamper" but tamper_D.py has 13. Fill both from
    checker output.
Recommended (not required): add one or two semantic red controls to tamper_D.py of the kind above (regenerate the
data at x e^{+2e-6} with the same tree; both checkers refuse), because 10 of the 13 current tampers stop at data
assertions before any box is bounded.
