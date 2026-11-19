# CERT_DESIGN: a robust certificate for the level (i) self-similar step (Lemma D), and the plan for the chain

Status (18 Nov 2026, 12:2x +04): DESIGN + PROTOTYPE. Lemma D below is proved here in full (to be refereed). Its
numerical part is checked by two separately written programs (cert/checkD_A.py, cert/checkD_B.py). Nothing here is a
claim about R(k,k) until Lemma D is refereed, Theorem A (PROOF.md) is refereed, and the bank is regenerated and
recertified (Section 6). Notation: ZBS Section 3 and PROOF.md (Theorem A). All logs natural.

## 0. What is certified and why the earlier robust LP failed

Theorem A (PROOF.md) says: the local step at (p, mu, w, beta, x) holds if V_A(phi, eta) < 0 for EVERY admissible
desaturation profile (phi, eta), where V_A integrates, over rows u in drift order, the ZBS per-row gain restricted by
the level (i) bound c(u) = sum_{k: v_k >= u} a(eta_k) v_k (phi(v_k) - phi(v_{k+1})). The adversary's profile is a
nonincreasing FUNCTION phi (not a cell average) plus gaps eta_k. A box over eta per scale decouples the cell drifts and
kills the effect. Lemma D avoids boxes over the drift altogether:
- the drift enters through convex functionals of a nonincreasing function on two intervals, so Hardy-Littlewood-Polya
  majorisation gives the worst profile on each interval in closed form, given only two numbers (Phi_b, p_b);
- the desaturation gain (a(eta) < a(0)) is linearised by convexity of a and charged EXACTLY against the first-order
  majorisation loss of the ZBS part, through a lower bound on the response slope of ZBS's argmax q-hat;
- the remaining adversary freedom is the pair (Phi_b, p_b) = (Phi(u_b), phi(u_b)), covered by a 2-D branch and bound
  whose every box is bounded rigorously.
The within-cell drift shape is an adversary variable by construction (phi is a general nonincreasing function; the
scale grid enters only through its mesh D, and D = (1 - u_b)/10^6 is used).

## 1. Notation

Q = F_p(x, mu) (ZBS feasible set) = (a(0), mu] (Lemma C (i)); Ht(q) = q M(q); H = Ht + w q, concave (Lemma C (iii)).
Lemma C is research/tier2/ramsey-zbs/PROOF.md Section 3, refereed in research/tier2/ramsey-zbs/REFEREE_20261117.md
(item 3, "H = qM + wq concave on D ... OK"). Its hypotheses are p, mu, beta in (0,1), w > 0, 0 < x < min{p, (1-mu)^w},
exactly K1 of 4c. Proof of (iii) in one line: with z = G0(q)/q, f(z) = p z + (1-p) log(1 - e^z), fbar(z) = f(max{z,
log p}), H(q) = q B(q) + w q + (q/beta)[fbar(G0(q)/q) - f(log p)]; q B(q) = w q log(mu/q) is concave; fbar is concave
and nonincreasing on z < 0, so its perspective (q, y) -> q fbar(y/q) is jointly concave and nonincreasing in y, and G0
is convex (Lemma C (ii)), so q -> q fbar(G0(q)/q) is concave; the rest is linear. D = {G0 < 0} is an interval (G0
convex), so Q = D cap (0, mu] is an interval and every tangent of H at a point of Q bounds H on all of Q (used in K5).
No K-check tests concavity: it is a proved property of the formula, not of the data. Cross-check (not part of
acceptance): checkD_C's sanity_C.py certifies Ht'' < 0 by interval jets on every cell except the one touching a(0)
(1316 of 1317 cells on c1722_m300, 1348 of 1349 on certUroot_m250; SPEC_ISSUES item 13).
Hhat(y) = sup_{q in Q} [Ht(q) - q y] (convex, nonincreasing); qhat(y) an argmax.
g(u) = -w u log u, phi_s(u) = g'(u) = -w (1 + log u) (saturated cumulative and drift).
a(eta) = left root of G0(q) = beta eta (PROOF.md, Theorem A).  Grid: u_b, and v_k = u_b + k D (k = 0..(1-u_b)/D) are
among Theorem A's scales (scales below u_b may be present; they are not used).
For a profile: Phi(u) = int_0^u phi, m(u) = g(u) - Phi(u) >= 0, Phi_b = Phi(u_b), p_b = phi(u_b), m_b = m(u_b),
Delta_k = phi(v_k) - phi(v_{k+1}) >= 0.

## 2. Lemma D (statement)

Data (all rational): the control with 0 < p, mu, beta < 1, w > 0 and 0 < x < min{p, (1 - mu)^w} (the second bound
is checked with outward rounding by both checkers; Theorem A, (INF), Theorem 4.2' and Definition 5.2' assume it: it
gives d* < 1 in ZBS Step 6, and G0(mu) < 0 does not imply it; referee of gate 1, 18 Nov 13:1x); a_cut < a_hi with
G0(a_cut) >= 0 > G0(a_hi); alpha >= beta / |G0'(a_hi)| (with G0'(a_hi) < 0);
u_b, D as above; q-grid a_cut = q_0 < q_1 < ... < q_N = mu with q_1 >= a_hi; y_c >= Ht'(mu); index jA0.
Node heights h_j: any rationals with H(q) <= affine_i(q) on each cell [q_i, q_{i+1}] and affine_i(q_i) <= h_i,
affine_i(q_{i+1}) <= h_{i+1} (checker A: tangent at the right end; checker B: the better of the two end tangents;
on cell 0 every checker uses the tangent at q_1, see K5).
Then for all y: Hhat(y) <= Hhat+(y) := max_j (h_j - q_j (w + y)) and, for j0 >= 1,
sup_{q in Q, q >= q_j0} [Ht(q) - q y] <= Psi_j0+(y) := max_{j >= j0} (h_j - q_j (w + y)).

LEMMA D. For every admissible (phi, eta) of Theorem A, with (Phi_b, p_b) its pair at u_b, and for every rational box
B = [Pl, Ph] x [pl, ph] containing (Phi_b, p_b): V_A(phi, eta) <= U(B), where U(B) is the explicit number of Section 4
(computed from the data above with exact rationals and outward-rounded exp/log). Hence, if a finite family of boxes
covers [0, g(u_b)] x [-w, -w log u_b] (which contains every feasible (Phi_b, p_b)) and U(B) < 0 for all of them,
Theorem A's hypothesis holds and the local alternative with sub-pair moves holds at (p, mu, w, beta, x).

## 3. Proof

D0 (facts about H). On the binding branch (A > B), Ht = p (1-q) l + ((1-p)/beta) q log Z with
l = log(p (1-q)^w / x), Z = (U - p e^{beta A})/(1-p), U = e^{beta B}; on A <= B, Ht = q B. At A = B: Z = e^{beta B},
Z' = beta e^{beta B}(B' - p A')/(1-p), so Ht'_bind = p(A + qA') + ((1-p)/beta)(beta B + q beta (B' - pA')/(1-p))
= B + q B' = (qB)'. Hence Ht is C^1 on (a(0), mu], C^2 on each branch, and |Ht'(q) - Ht'(q')| <= sup|Ht''| |q - q'|.
a(eta) is convex and decreasing: a'(eta) = beta / G0'(a), a'' = -beta^2 G0''/G0'^3 > 0 (G0 convex, G0'(a) < 0). Since
a(0) in (a_cut, a_hi) and G0' is increasing, |a'(0)| = beta/|G0'(a(0))| <= beta/|G0'(a_hi)| <= alpha, hence
  a(eta) >= a0 - alpha eta  for all eta >= 0,  a0 := a_cut.                                               (D0.1)

D1 (phi(1-) = -w; Theorem A's phi(1) is the value at the last rank, phi(1-) in the limit). V_A depends on phi(1) only through the row restriction q M(q) >= q phi(1) + c(u), and c(u) contains
a(eta_{m-1}) v_{m-1} (phi(v_{m-1}) - phi(1)). The derivative of q phi(1) + c(u) in phi(1) is q - a(eta_{m-1}) v_{m-1} > 0
(q > a(0) >= a(eta)). So for fixed phi on (0, 1) the integrand of V_A is nonincreasing in f1 := phi(1) on [-w, phi(1-)]
(the constraint sets grow as f1 decreases, and no other term of V_A involves f1; ranks are measure zero points), and the
bound we prove for f1 = -w bounds V_A for every admissible f1 (monotonicity in f1, referee F1). With phi(1) = -w the
restriction reads H(q) >= c(u).

D2 (two regions). c is nonincreasing in u and, for u <= u_b, c(u) >= C := sum_{k >= k_b} a(eta_k) v_k Delta_k. Drop the
restriction for u > u_b:  V_A <= int_0^{u_b} psi_C(phi(u)) du + int_{u_b}^1 Hhat(phi(u)) du,
psi_C(y) = sup{Ht(q) - q y : q in Q, H(q) >= C}  (-infinity if empty).

D3 (linearising the gaps). By (D0.1) and eta_k <= m(v_k)/v_k (admissibility),
  C >= a0 S - G,  S := sum_{k >= k_b} v_k Delta_k,  G := alpha sum_{k >= k_b} m(v_k) Delta_k >= 0.
Each drop located at s in [v_k, v_{k+1}] has weight v_k >= s - D, and int_{[u_b,1]} s d(-phi) = w + u_b p_b - Phi_b, so
S >= w + u_b p_b - Phi_b - D (p_b + w). For the box: C >= C0 - G, C0 := a0 (w + u_b pl - Ph - D (ph + w)).

D4 (left region, exact in G). Let j0 be the first node with H(q_j0) >= C0 certified, q0 = q_j0, h1 <= H'(q0) (h1 > 0),
s0 <= Ht'(q0), Delta0 := (H(q0)+ - C0)/h1. Since H is concave, {q in Q: H(q) >= C0 - G} is contained in [q1, mu] with
H(q1) = C0 - G, and q0 - q1 <= (H(q0) - H(q1))/H'(q0) <= Delta0 + G/h1. For q in [q1, q0), concavity of Ht gives
Ht(q) - q y <= Ht(q0) - q0 y + (q0 - q)(y - s0). Hence for all y
  psi_C(y) <= psi_{C0 - G}(y) <= Psi_j0+(y) + (Delta0 + G/h1) (y - s0)_+.
LEMMA M (majorisation on an interval). If phi, phibar are nonincreasing on [a, b], their cumulatives satisfy
Phi <= Phibar on [a, b] with equality at a and b, and f is convex with bounded slopes on the range, then
int_a^b f(phi) <= int_a^b f(phibar). Proof: with sigma(u) in the subdifferential of f at phi(u), chosen nondecreasing
in phi (so nonincreasing in u), f(phibar) - f(phi) >= sigma (phibar - phi); integrate by parts against
d(Phibar - Phi): the boundary terms vanish and -int (Phibar - Phi) d sigma >= 0.
On [0, u_b] every admissible phi with (Phi_b, p_b) has phi >= p_b and Phi <= g, so Phi <= Phi* := min(g,
Phi_b - p_b (u_b - .)), a concave function with the same end values; Psi_j0+ and (. - s0)_+ are convex. So
  int_0^{u_b} psi_C(phi) <= IL + (Delta0 + G/h1) K,   IL = int_0^{u_b} Psi_j0+(phi*),  K = int_0^{u_b} (phi* - s0)_+.

D5 (right region, two inequalities). On [u_b, 1], phi <= p_b and Phi <= g, so Phi <= Phi** := min(g, Phi_b + p_b (. - u_b))
with equal end values. (A) Lemma M: int_{u_b}^1 Hhat(phi) <= IR2 := int_{u_b}^1 Hhat+(phi**). (B) Convexity of Hhat at
phi(u) (subgradient -qhat(phi(u))) against the saturated profile, integrated by parts with m(1) = 0, m(u_b) = m_b:
  int_{u_b}^1 Hhat(phi) <= int_{u_b}^1 Hhat(phi_s) - qhat(p_b) m_b - int_{(u_b,1]} m dQ,   Q := qhat o phi (nondecreasing),
  where the Stieltjes integral over (u_b, 1] includes the jump of Q at u_b+ (Q(u_b) = qhat(p_b) is the value AT u_b).

D6 (charging the gain to the loss). Both checkers assert y_sp >= y_c (here y_sp = phi_s(u_b) is about 1.2 and y_c about
-0.32), so the cap band (levels < y_c) and the high band (levels >= y_sp) are disjoint. Split each Delta_k by drift level
into the parts below y_c, in [y_c, y_top], and
above y_sp >= phi_s(u_b) (y_top = min(ph, y_sp)).
 (slope) If |Ht''| <= 1/kappa2 on [q_A, mu] with qhat(y_top) >= q_A, then for y_c <= y1 < y2 <= y_top, qhat(y1) - qhat(y2)
 >= kappa2 (y2 - y1) (D0: y = Ht'(qhat(y)) for y > Ht'(mu)). So on each cell the increment of Q is at least kappa2 times
 the middle part of Delta_k, and m(v_k) <= min_cell m + D Lip (Lip = max(phi_s(u_b), ph) + w >= |m'|):
   sum_k m(v_k) Delta_k^mid <= (1/kappa2) int m dQ + Lip D (y_top - y_c)_+.
 (high band) If the drop of cell k passes a level >= y_sp >= phi_s(u_b), then phi >= y_sp on [u_b, v_k], so
 m(v_k) <= m_b + g(v_k) - g(u_b) - phi_s(u_b)(v_k - u_b) <= m_b (g concave). The slope bound also holds on [y_sp, ph]
 with kappa2h = 1/sup{|Ht''| on [q_jB, mu]}, qhat(ph) >= q_jB, so the Q-increment of the cell is at least
 kappa2 Delta^mid + kappa2h Delta^high; after charging, only (1 - kappa2h/kappa2) kappa m_b (ph - y_sp)_+ is left.
 (cap) If the drop of cell k passes level y < y_c, then m(v_k) <= g(v_k) + (1 - v_k) y + D (ph - y) <=
 beta_max(y) + D (ph + w), beta_max(y) = max_r [g(r) + (1-r) y] = y + w e^{-1 - y/w}; each level is passed once:
   sum m Delta^cap <= E_cap := int_{-w}^{y_c} beta_max + D (ph + w)(y_c + w)
   = (y_c^2 - w^2)/2 + w^2 (1 - e^{-1 - y_c/w}) + D (ph + w)(y_c + w).
 E_grid := Lip D (ph - y_c)_+ (the mesh term above, over the middle and high bands), Lip = max(phi_s(u_b)+, ph) + w.
 With kappa := alpha K / h1 and theta := kappa / kappa2 <= 1 (checked), (B) gives theta int m dQ <= theta (int Hhat(phi_s)
 - qhat(p_b) m_b - int Hhat(phi)), and so
   int_{u_b}^1 Hhat(phi) + (K/h1) G <= (1-theta) IR2 + theta (IRs - qB m_b) + kappa (E_grid + E_cap + (1 - kappa2h/kappa2) m_b (ph - y_sp)_+),
 IRs = int_{u_b}^1 Hhat+(phi_s), qB <= qhat(ph) <= qhat(p_b).

D7 (the box). (Referee F4.) K = int_0^{u_b} (phi* - s0)_+ has dK/dPhi_b in [0, 1] (exact difference formula on the
switch interval, (y - s0)_+ has slopes in [0, 1]), so K at min(Ph, g-) plus (g+ - g-) bounds it. When min(Ph, g-) = g-
(4b step 3 with PK = g-) the bound used is different: phi* is nonincreasing with Phi* <= g = int phi_s and Phi*(0) = 0,
so phi* is weakly submajorised by phi_s on [0, u_b], and (. - s0)_+ is convex and nondecreasing, hence K <=
int_0^{u_b} (phi_s - s0)_+ for EVERY feasible Phi_b (weak majorisation, Tomic-Weyl; the switch point u1 may then be
interior, e.g. when pl > phi_s(u_b), and is not needed). The added (g+ - g-) is then redundant (SPEC_ISSUES item 2). q_R is the active
slope of Hhat+ at the drift phi_s(b2) with b2 the UPPER end of the u2-enclosure at P1 (u2 decreases in Phi_b, so
phi_s(u2) >= phi_s(b2) for every Phi_b >= P1). IR2 uses Phi** = min(g, Phi_b + p_b(. - u_b)) also for Phi_b above
g(u_b) (P1 is clipped to g- so this does not occur in T(P1)). IL is nonincreasing in Phi_b and in p_b; K nondecreasing in Phi_b and nonincreasing in p_b; IR2
nondecreasing in both (Lemma M and the switch-point argument: raising Phi_b moves drift mass across the switch point
where F(phi_s) and F(p_b) are compared with the right sign). So, with P1 = min(max(Pl, pl u_b), g(u_b)-),
T(Phi) := IL(Phi, pl) + (1-theta) IR2(Phi, ph) + theta (IRs - qB max(0, g- - Phi)) bounds every configuration of
the box with Phi_b = Phi, and T(Phi') - T(Phi) <= (-q_min + (1-theta) q_R + theta qB)(Phi' - Phi) (exact difference
formulas on the switch intervals; q_min = least slope of Psi_j0+, q_R = active slope of Hhat+ at drift phi_s(u2)).
  U(B) = T(P1) + max(0, slope)(Ph - P1) + Delta0 K + kappa (E_grid + E_cap + E_high),  K at (min(Ph, g-), pl) + (g+ - g-).
Switch points u1, u2 are enclosed by certified-sign bisection; on the enclosure the integrand is bounded by its
monotone end value. All integrals of max-of-lines along phi_s are exact: with s = log t, h_j - q_j(w + phi_s(t)) =
h_j + w q_j log t, the upper hull has rational breakpoints, and int (c + d log t) dt = t (c + d (log t - 1)).

D8 (all scales) Theorem A's grid needs only u_b and the mesh D, and the mesh terms are added explicitly in U(B)
(C0's D(ph + w), kappa E_grid, the D terms of E_cap). With D = (1 - u_b)/10^6 they are small but NOT negligible
against the tightest margins: kappa E_grid is about 1e-7 near the saturated profile, the same size as the worst leaf
U of the c1722 certificate at a - 3.0e-4 (c1722_m300, worst U -1.33e-7; gate-1 referee; the a-shift 3.0e-4 itself is
not a margin); soundness is unaffected because every checker adds them. Confirmed by checkD_C (SPEC_ISSUES item 12):
with D multiplied by 2 or 4 (still dividing 1 - u_b) c1722_m300 is still accepted (worst U -9.3e-8, -1.2e-8); with
D x 8 or x 16 it is refused (+1.5e-7, +4.7e-7).

## 4. The two checkers and the generator (cert/)

INDEPENDENCE (gate-4 review, F5): checkD_A and checkD_B are independent in ARITHMETIC only: separate interval
libraries (own dyadic intervals vs Arb), separate evaluation of H, Ht', Ht'' (hand-derived two-branch formulas vs
Lemma C (iii)'s representation with Arb power series), separate hull algorithms and switch-point code. The ASSEMBLY of
the box bound U(B) (D3-D7, spec in Section 4b) is shared: both files were written by the same author and implement
the same formula line by line. That formula is covered by the gate-1 referee's reading of Lemma D, not by a second
independent implementation. A fully independent second checker needs a fresh author writing U(B) from Section 4b alone.
THIRD CHECKER (18 Nov): checkD_C (research/tier2/ramsey-lemma/cert_independent/, code 0548347a0, results 9fe23c44f)
was written by a fresh author from Sections 1-3, 4b and 4c alone (spec at ddb8c7a8e; checkD_A, checkD_B and genD not
opened). It ACCEPTS all four certificates (worst U: c1722_m300 -1.33e-7, c1722_m280 -7.63e-7, c1701_m280 -1.03e-6,
certUroot_m250 -9.12e-6), refuses its 27 own tampers and every one-field tamper of tamper_D, and found no soundness
gap (SPEC_ISSUES.md, 15 text points). The text fixes for all 15 points are in this file (Sections 1, 2, 3 D7/D8,
4b, 4c); they change no number that checkD_A or checkD_B computes.

### 4b. Specification of U(B) (what both checkers compute; every quantity is an outward-rounded upper/lower bound;
### the data checks, formats and definitions it relies on are in 4c)
Input box B = [Pl, Ph] x [pl, ph]; g-, g+ enclose g(u_b) = -w u_b log u_b.
0. Infeasible (U = -1): Pl > g+; pl u_b > Ph or pl u_b > g+; ph (1 - u_b) < -Ph; ph < -w.
All node indices j in steps 1, 5, 6, 7 range over j >= 1 (q_0 = a_cut need not lie in Q; Ht'(q_0) is undefined).
Where a box "fails", the checker rejects the certificate (conservative; the box need not be infeasible).
1. C0 = a0 (w + u_b pl - Ph - D (ph + w)). j0 = least node j >= 1 with H(q_j)- >= C0 (fail if there is none);
   h1 = Ht'(q_j0)- + w (> 0); s0 = Ht'(q_j0)-; Delta0 = (H(q_j0)+ - C0)/h1. Psi+ = max over nodes j >= j0 of
   (h_j - q_j (w + y)).
2. P1 = min(max(Pl, pl u_b), g-) (fail if P1 < pl u_b). [a1, b1] encloses u1 for (P1, pl) (bisection, f = g - line).
   IL = int_0^{a1} Psi+(phi_s) + (b1 - a1) max(Psi+(pl), Psi+(phi_s(b1)-)) + (u_b - b1) Psi+(pl)  (exact hull integral).
   Psi+ and Hhat+ are nonincreasing in y, so at an irrational argument such as phi_s(b1) the LOWER end of its
   enclosure is used (likewise phi_s(b2)- in step 4).
3. PK = max(min(Ph, g-), pl u_b). If PK < g-: [ak, bk] encloses u1 for (PK, pl). If PK = g-: [ak, bk] = [u_b, u_b],
   which gives K = int_0^{u_b} (phi_s - s0)_+ + (g+ - g-), valid for every feasible Phi_b by weak majorisation (D7;
   u1 need not lie in [u_b, u_b]). t0 = e^{-1 - s0/w};
   Kint = -bk s0 - w bk log bk if bk <= t0 (certified), else w t0; K = Kint + (u_b - ak)(pl - s0)_+ + (g+ - g-).
4. [a2, b2] encloses u2 for (P1, ph) (f = line - g on [u_b, 1]; if f(1)+ < 0, which step 0 does not exclude at P1 < Ph,
   take a2 = b2 = 1, see SWITCH POINTS). IR2 = (a2 - u_b) Hhat+(ph) + (b2 - a2) max(Hhat+(ph),
   Hhat+(phi_s(b2)-)) + int_{b2}^1 Hhat+(phi_s). IRs = int_{u_b}^1 Hhat+(phi_s).
5. y_sp = phi_s(u_b)+, y_top = min(ph, y_sp). jA = largest node j >= 1 with Ht'(q_j)- >= y_top (fail if none, if
   jA < jA0, or if jA = N: then there is no cell i >= jA; such boxes are infeasible by step 0 in practice, since
   ph >= -Ph/(1 - u_b) is about -0.05 while y_c is about -0.31); kappa2 = 1/max of |Ht''|+ over cells i >= jA;
   jB = largest node j >= 1 with Ht'(q_j)- >= ph, qB = q_jB (qB = a0 if there is none);
   kappa = alpha K / h1; theta = kappa/kappa2 (fail if > 1); m_b = (g- - P1)_+. theta is ONE number (any upper bound
   of kappa/kappa2 that is <= 1) used in both (1 - theta) IR2 and theta (IRs - qB m_b) of step 8: D6 needs only
   theta >= kappa/kappa2 and the same value in both places.
6. q_R = (slope of the hull piece of Hhat+ at s = log(b2)+)/w; slope = -q_min(Psi+) + (1 - theta) q_R + theta qB;
   dvar = slope_+ (Ph - P1).
7. Lip = max(phi_s(u_b)+, ph) + w; E_grid = Lip D (ph - y_c)_+; E_cap = (y_c^2 - w^2)/2 + w^2 (1 - e^{-1 - y_c/w})
   + D (ph + w)(y_c + w); kappa2h = 1/max of |Ht''|+ over cells i >= jB (0 if jB is undefined, jB < jA0 or jB = N),
   capped at kappa2;
   E_high = (1 - kappa2h/kappa2)(g+ - P1)(ph - y_sp)_+.
8. U(B) = IL + Delta0 K + (1 - theta) IR2 + theta (IRs - qB m_b) + dvar + kappa (E_grid + E_cap + E_high).

- genD.py: float data (a_cut, a_hi, alpha, q-grid, y_c, jA0) + branch and bound over (Phi_b, p_b) boxes using
  checker A's box bound; writes the JSON with the bisection tree (coverage of the rectangle is by construction).
- checkD_A.py: Fractions + own dyadic intervals (ivA.py copied from ramsey-zbs checker A, unchanged); H, Ht', Ht'' by
  hand-derived formulas on both branches; stack hull; recomputes every box.
- checkD_B.py: python-flint Arb/fmpq; H through Lemma C (iii)'s representation with fbar; Ht', Ht'' by arb_series;
  node heights by the better end tangent; gift-wrapping hull with successor map; recomputes every box.
- tamper_D.py: red controls. Thirteen tampers break a hypothesis (K1-K9) or the tree (control x, mu, w, alpha, a_cut,
  y_c, u_b, D, G_up, jA0, a q-node, single leaf, merge of the worst leaf) and are refused whatever the margin. The two
  MARGIN PROBES regenerate all data at x e^f with the same tree; they satisfy K1-K9 and are refused only through K10,
  i.e. only if f exceeds the certificate's margin. Until 18 Nov they used fixed f = 2e-6 and 1e-5, which all three
  checkers ACCEPTED on c1701_m280 (f = 2e-6) and certUroot_m250 (both): correct behaviour, but the suite then printed
  "SOME TAMPER ACCEPTED" (SPEC_ISSUES item 11). Now f is chosen per certificate from checker A's worst leaf U0 (U moves
  by about 0.5 f): f1 = max(2e-6, 8 |U0|), f2 = max(1e-5, 40 |U0|). ramsey-zbs's CD red controls draw on this file.

### 4c. Self-contained specification for an independent checker (read with Sections 1-3 and 4b only)

FORMAT. A certificate is a JSON object. Rationals are strings "n/d" or "n" (exact). Fields:
  control: {p, mu, w, beta, x}  (rationals);  a_cut, a_hi, alpha, u_b, Dplus, y_c, G_up, P_up  (rationals);
  qgrid: list of rationals q_0 < ... < q_N;  jA0: integer;  tree: the box tree.
TREE. A node is the string "L" (leaf) or a list [axis, child1, child2] with axis "P" or "p". The root rectangle is
[0, G_up] x [-w, P_up] in (Phi_b, p_b). Axis "P" splits the node's [Pl, Ph] at m = (Pl + Ph)/2 into child1 = [Pl, m]
and child2 = [m, Ph] (same p-range); axis "p" splits [pl, ph] the same way. The leaves cover the root rectangle.
FUNCTIONS (ZBS Section 3; logs natural). For q in (0, 1):
  A(q) = ((1-q)/q) (log p + w log(1-q) - log x),  B(q) = w (log mu - log q),  U = e^{beta B},
  M(q) = B if A <= B, else p A + ((1-p)/beta) log((U - p e^{beta A})/(1-p))  (defined iff U > p e^{beta A});
  Q = {q in (0, mu]: M(q) defined} (Lemma C (i): Q = {G0 < 0} cap (0, mu]),
  G0(q) = q log p + beta (1-q)(log p + w log(1-q) - log x) - beta w q (log mu - log q),
  G0'(q) = log p - beta (log p + w log(1-q) - log x) - beta w (log mu - log q),
  Ht(q) = q M(q), H(q) = Ht(q) + w q (concave on Q; Ht is C^1 on Q and C^2 on each branch, Section 3 D0),
  phi_s(u) = -w (1 + log u), g(u) = -w u log u.
For the shifted parameters needed nowhere else: none (Lemma D uses only the base control).
CHECKS, all with exact rationals and outward-rounded exp/log (every "<" or ">=" must hold for the whole enclosure):
 K1 0 < p < 1, 0 < mu < 1, w > 0, 0 < beta < 1, 0 < x < p, and x < (1 - mu)^w.
 K2 0 < a_cut < a_hi < mu; G0(a_cut) >= 0; G0(a_hi) < 0; G0(mu) < 0; G0'(a_hi) < 0; alpha >= beta / |G0'(a_hi)|.
    (Then a0 := a_cut <= a(0) and a(eta) >= a0 - alpha eta for eta >= 0.)
 K3 0 < u_b < 1, Dplus > 0, (1 - u_b)/Dplus is a positive integer. (D := Dplus in 4b.)
 K4 N >= 2, q_0 = a_cut, q_N = mu, strictly increasing, q_1 >= a_hi (so q_1, ..., q_N are in Q).
 K5 Node heights (computed by the checker, not read from the file): rationals h_0, ..., h_N such that on every cell
    [q_i, q_{i+1}] some affine A_i satisfies H <= A_i on Q cap [q_i, q_{i+1}], A_i(q_i) <= h_i and A_i(q_{i+1}) <= h_{i+1}.
    Any tangent of the concave H at a point of Q works (Lemma C (iii), cited in Section 1), e.g. at the right end:
    A_i(q) = H(q_{i+1}) + H'(q_{i+1})(q - q_{i+1}), so h_{i+1} >= H(q_{i+1})+ and h_i >= H(q_{i+1})+ - H'(q_{i+1})-
    (q_{i+1} - q_i); a node's height is the max over its (at most two) cells. CELL 0 MUST USE THE RIGHT-END TANGENT
    (at q_1): q_0 = a_cut is not in Q, and H' is unbounded as q -> a(0)+ with a(0) within about 4e-15 of q_1 = a_hi, so
    a tangent at any other point of cell 0 gives valid but useless heights (U(B) about +1e3; SPEC_ISSUES item 14). A
    checker that takes the better of two end tangents does so only on cells i >= 1. Then Hhat+(y) := max_j (h_j - q_j (w + y)) >= sup_{q in Q} [Ht(q) - q y] for all y, and
    Psi+_{j0}(y) := max_{j >= j0} (h_j - q_j (w + y)) >= sup_{q in Q, q >= q_j0} [Ht(q) - q y].
 K6 1 <= jA0 <= N - 1; for every cell i >= jA0 an upper bound d2_i >= |Ht''| on
    [q_i, q_{i+1}] (use both branch formulas where A - B changes sign on the cell, i.e. the max of the two bounds; the
    cell must be certified in Q: G0(q_i)+ < 0 and G0(q_{i+1})+ < 0 suffice, G0 being convex). At a NODE where the sign
    of A - B is not certified, enclose H(q_j) and Ht'(q_j) by the union of the two branch enclosures (Ht is C^1 and H
    continuous across A = B, Section 3 D0), and use the lower end of that union for "X-" and the upper end for "X+".
 K7 y_c > -w and y_c >= Ht'(mu) (the derivative at mu of the branch formula valid there).
 K8 phi_s(u_b) >= y_c (lower end of the enclosure).
 K9 G_up >= g(u_b) and P_up >= -w log u_b.
 K10 every leaf box B of the tree has U(B) < 0, with U(B) computed by Section 4b (steps 0-8), or is infeasible by
    step 0. Enclosure conventions in 4b: "X+" is an upper bound, "X-" a lower bound; Ht'(q_j)- is a lower bound of
    the derivative at the node; "largest node with Ht'(q_j)- >= y" uses that Ht' is decreasing (a prefix of nodes).
SWITCH POINTS (4b steps 2-4). u1 for (Phi, p) on [0, u_b]: f(u) = g(u) - (Phi - p (u_b - u)) is concave with
f(0+) <= 0 (Phi >= p u_b) and f(u_b) > 0 (Phi < g(u_b)); u1 = inf{u: f > 0 on (u, u_b]}. Any [a1, b1] with a1 = 0 or
f(a1)+ <= 0, and b1 = u_b or f(b1)- > 0, encloses u1 (a1 <= u1 <= b1). u2 for (Phi, p) on [u_b, 1]: f(u) = Phi + p (u -
u_b) - g(u) is convex with f(u_b) < 0; [a2, b2] with f(a2)+ <= 0 (or a2 = u_b) and f(b2)- > 0 (or b2 = 1). At the
evaluation point (P1, ph) f(1) = P1 + ph (1 - u_b) can be negative (step 0 excludes only Ph + ph (1 - u_b) < 0): then
f < 0 on all of [u_b, 1], u2 is clipped to 1 and a2 = b2 = 1, IR2(P1) = (1 - u_b) Hhat+(ph). This is sound: for any
feasible Phi' > P1, IR2(Phi') - IR2(P1) = int_{u2'}^1 [Hhat+(phi_s) - Hhat+(ph)] <= q_R int_{u2'}^1 (ph - phi_s)
= q_R (Phi' + ph (1 - u_b)) <= q_R (Phi' - P1), so T(Phi') - T(P1) <= slope (Phi' - P1) still holds (SPEC_ISSUES 3).
INTEGRALS. Along phi_s, h_j - q_j (w + phi_s(t)) = h_j + w q_j log t, so int_{ta}^{tb} Hhat+(phi_s(t)) dt is the
integral of the upper envelope of the lines c_j + d_j s (c_j = h_j, d_j = w q_j, s = log t). Any rigorous UPPER bound
is acceptable. Exact method: the hull of the lines has rational breakpoints s_k; on each piece
int (c + d log t) dt = [t (c + d (log t - 1))], with t = e^{s_k} at breakpoints and t = ta, tb at the ends (ta = 0
contributes 0). Psi+ integrals use the lines j >= j0 only.
OTHER QUANTITIES IN 4b. q_R (step 6) may be any upper bound of the slope magnitudes of Hhat+ on [phi_s(b2), ph]; the
largest q_j among lines attaining Hhat+ at some y >= phi_s(b2)- is enough. q_min(Psi+) may be any lower bound of the
slope magnitudes of Psi+, e.g. q_j0. Any choice that is more conservative than 4b's is sound.
|Ht''| on a cell (K6) may be bounded by any rigorous method: a direct interval enclosure over the cell, or
|Ht''(mid)| + (h/2) sup |Ht'''| (checkD_C takes the min of the two). Switch-point bisection may stop at any width, or
when the sign is uncertain; a coarser enclosure only raises U.
OUTPUT. Accept iff K1-K10 all hold; report the number of leaves and the largest U(B).

## 5. Prototype results (filled from checker output only)

See Section 7 (dated).

## 6. Plan and estimate: integration into the bank and recertification of z

1. Referee Lemma D (this file) and Theorem A (PROOF.md) in a fresh context. (Half a day.)
2. New control kind 'CD' in the ZBS pipeline: a control (p, mu, w, beta, x) is valid if 0 < x < min{p, (1 - mu)^w}
   (outward rounded), Q is nonempty (G0(a_hi) < 0 with a_hi < mu) and Lemma D's data shows U(B) < 0 on a covering box tree. Changes (owned by the ramsey-zbs agent, to be agreed):
   checkers A and B each gain a 'CD' branch that imports checkD_A / checkD_B respectively; materialise.py emits the
   Lemma D data for controls flagged CD; red controls gain three tampers (box U, a tree leaf, alpha). (One day.)
3. Generator: ctltable2 gets, per grid control, the level (i) certified a-shift Delta(p, mu, w) (float map from a
   fast version of Section 4's bound, then certified per used control by genD's branch and bound, about 20 s to a few
   minutes per control). Only controls whose dz/da is first order need it (ramsey-zbs agent, 18 Nov: the root
   control, dz/da 0.685, and control 1113, dz/da 0.369; the routes 519 and 1297 are path-bound). Rerun gen2 rounds.
4. Recertify: materialise, checkers A and B, 11 + 3 tampers, fresh sparse clone (as in RESULT.md). Wall time about
   one day of compute at kp = 2 (the 17 Nov run was 3 h per reproduce).
Expected z gain. ramsey-zbs agent (18 Nov 12:2x, traced in certK3): at the root the terminal term binds
(T = 1.248056263) with dz/da_root = 1/(1+w) = 0.685, but the path term (g0 + gL = 1.247988276) has only 6.8e-5 of
slack, and the source line's tightest point leads to control 1113 (dz/da about 0.369). So the root control alone can
lower z by at most about 6.8e-5; beyond that the route children (c1701, c1407, c1509, ...) and the source chain
(c1113) must improve too, i.e. Lemma D must be applied bank-wide and the generator rerun. Lemma D does NOT help at
c1113 (Section 7: there the gap gain is not dominated, kappa/kappa2 = 8 at useful u_b), so the source side stays as is
unless the chain (below) is certified. Rough expectation from the lane's bank-wide float test (every control
a - 0.003 gave z lower by 1.2e-3 to 1.6e-3, ratio about 0.4-0.5): a bank-wide robust shift of about 2.8e-4 on the
controls near the root regime gives z lower by about 1e-4, capped by c1113-type controls. To be measured by rerunning.

The full chain (G, L, symmetry; NOTES 10:4x-12:0x) needs the same two ingredients plus one more: per-row profiles
F_u across scales. Lemma D's tools carry over (majorisation per interval for the drift; the gap gain charged to the
first-order ZBS loss), but the per-row chain makes the drift-dependent part bilinear in (profile, drift). The route
I recommend: certify the chain with drift taken as a step function on a FINE scale grid, the within-cell shape
handled by the convex lower bound c_k(dF) = Phi(s_k) - Phi(s_k - dF) (lane, chain_safe.py), and the cell drift values
as LP variables (not boxes), with the bilinear term F x drift-drop relaxed by McCormick on a branch and bound over a
FEW aggregate drift parameters (Phi at 4-6 knots), each box's LP dual checked in exact rationals. Not started.

## 7. Dated results

18 Nov 12:4x +04 (checker output; certificates in cert/certs/, scratch logs in scratchpad cd/runs/).
Lemma D at u_b = 3/100, D = (1 - u_b)/10^6, q-grids of 1,319-1,351 nodes, branch and bound with both checkers' bounds:
| certificate (cert/certs/) | bank a | certified a' (Lemma D) | shift | boxes | worst U (A / B) | tampers |
|---|---|---|---|---|---|---|
| c1722_m300.json (root c1722; dz/da 0.685) | 1.111074566936 | 1.110774566936 (x' = 329303794434999/10^15) | -3.00e-4 | 97 | -8.89e-8 / -1.74e-8 | 15/15 refused by both (13 data/closability + 2 semantic) |
| c1722_m280.json (ramsey-zbs's z = 1.247967524 is at this x) | 1.111074566936 | 1.110794566936 (x' = 329297208424971/10^15) | -2.80e-4 | 97 | -7.50e-7 / -7.29e-7 | - |
| c1701_m280.json (route child) | 1.107325086 | 1.107045086 | -2.80e-4 | 72 | -1.03e-6 / -1.04e-6 | - |
| certUroot_m250.json (17 Nov root) | 1.12610 | | -2.50e-4 | 53 | -9.12e-6 / -9.12e-6 | - |
(Regenerated 13:4x from the frozen checkers' output; earlier entries were from before the kappa2h refinement.)
c1722.json, c1701.json, c1113.json, c52.json in cert/certs/ are BARE CONTROLS (bank data), not certificates.
18 Nov 11:1x UTC (route tree, for ramsey-zbs's certCD2; checker output only): Lemma D for ALL 24 depth-1 controls of the
root's route tree (ramsey-zbs scratch rz/root_tree_controls_certCD.tsv; beta = 1 - 10^-7). Float screen
(cert/screenD.py): u_b = 0.03 is best for every control (0.02, 0.045 and 0.07 are worse); thresholds 2.68e-4 to
4.21e-4. Generated at 0.88 x the float threshold by genD (cert/tree_cert.py), then: checkD_A ACCEPT, checkD_B ACCEPT,
checkD_C ACCEPT (independent), tamper_D 15/15 refused by both, for all 23 new certificates (c1701 reuses
c1701_m280). Shifts of a: c1219 -3.70e-4, c1607 -3.38e-4, c1708 -3.24e-4, c885 -3.14e-4, c1702 -3.09e-4, c1707 -2.99e-4,
c1710 -2.92e-4, c1700 -2.90e-4, c1606 -2.89e-4, c1701 -2.80e-4, c899 -2.79e-4, c1705 -2.78e-4, c1615 -2.72e-4,
c882 -2.67e-4, c1500 -2.67e-4, c1721 -2.63e-4, c1609 -2.62e-4, c1509 -2.57e-4, c1407 -2.52e-4, c1720 -2.52e-4,
c1512 -2.48e-4, c1499 -2.46e-4, c1415 -2.41e-4, c1518 -2.35e-4. Index with SHA-256: cert/certs/TREE_INDEX.tsv; checker
transcripts: cert/runs_tree.log. Thinnest margin: c1407 (checkD_C worst U -9.2e-10, still accepted by all three).
x' = floor(x e^{|shift|} 10^15)/10^15, so the certified a' = -log x' lies slightly ABOVE bank a - |shift| (by < 1e-14;
conservative); TREE_INDEX.tsv lists a' computed from the exact x'.
c1722 at -3.2e-4: a point box at U = +5.8e-12 (the design's limit is between -3.0e-4 and -3.2e-4).
c1113 (source chain, dz/da 0.369): NO useful gain. Float: robust two-region threshold about 4e-6 in a (u_b 0.16-0.25);
for u_b <= 0.1, theta = kappa/kappa2 = 8.5 > 1 (alpha = 1.63, |Ht''| up to 500: the desaturation gain beats ZBS's
first-order loss). Even non-robust full level (i) at c1113 is about 1.2e-4 in a (CERT slope 1.9 per unit a).
z (ramsey-zbs measurement, kp = 2 state, root re-optimised with source and path re-chosen, root control shifted only):
-1.0e-4 -> z 1.248016841 (gain 3.9e-5); -2.8e-4 -> z 1.247967524 (gain 8.9e-5; e^z about 3.48325). The path-term
slack does not cap the gain (the route re-balances). Not a certified z: needs the gates in Section 6.
Gates agreed with ramsey-zbs (12:4x): (1) final fresh-context referee of Theorem A / Theorem 4.2' with no open point,
and a fresh-context review of checkD_A/checkD_B against Lemma D; (2) the lab lead's agreement that a record may rest on
it; (3) the ZBS-only certK3 stays the conservative headline, a CD certificate is a second claim "assuming Theorem A".
Integration: CD list (root c1722, c1701, maybe c1407/c1509) + genD.certify(ctl, da) as the entry point inside
materialise.Mat.control() (halve on failure, Lemma C after 3 tries); ctlA/ctlB branch importing checkD_A/checkD_B;
three CD tampers in red_controls.py; then kp = 2 chain and fresh clone. Lean kernel check (B2) does not cover CD.

18 Nov 12:5x +04. CHAIN CERTIFICATE: the route proposed at the end of Section 6 is withdrawn (decisive obstacle).
- What the chain needs: the gain comes from (G) at MANY scales (40-100; with 1, 3 or 5 scales it is only the eta cost),
  and each (G_i) depends at first order on the drift shape near and below v_i: in kappa-form (dkappa = -t dphi) it reads
  int_0^{v_i} (g_i - g(t)) dkappa(t) >= v_i R_i(g_i, eta~_i), so the adversary gains by putting drift drops where each
  row's profile g(t) is small, and also through eta~_i and the spread Gamma_i = kappa(v_i)/v_i.
- Why McCormick over 4-6 knots fails: with Phi pinned only at knots, a cell drift between decade-spaced knots ranges
  over about w log 10 = 1.1; the McCormick gap of each product dF_k x phi_k (or F_k x drop_k after summation by parts)
  is about (F range)(drift range)/4, i.e. about 0.06 v_i per row and scale, while the slack that the chain must keep is
  about v_i (H(g) - w gbar) = 0.01 v_i. The relaxed adversary satisfies every (G_i) and the gain vanishes. Tight
  enough boxes need the drift pinned at every cell, i.e. branching in 40-100 dimensions. This is the same decoupling
  that killed the first robust LP, moved from eta to the drift.
- What Lemma D's tools give and what is missing: majorisation handles the convex ZBS part between knots exactly, and
  the a(eta) gain was charged at first order to the ZBS majorisation loss. For the chain, the per-row feasibility
  margin is a CONCAVE function of the drift (a minimum over profiles of terms linear in kappa), so its adversarial
  minimum sits at extreme drift profiles (saturated on a set, flat on gaps, with kinks at grid points), and it is not
  first-order controlled by the ZBS loss. A certificate needs a new analytic comparison lemma along the chain (an ODE
  inequality for gbar in kappa-time with an explicit cost for every flat gap), not more computation.
- Recommendation: treat the chain as research (a comparison lemma first, float-tested against the lane's 8-knot
  adversary), and keep the certified line at Lemma D (level (i)).

18 Nov 13:1x +04. Gate-1 referee (via the lane): ONE blocking point, x < (1 - mu)^w never certified on the CD path. Fixed:
both checkers now check it with outward rounding (checker A: x < lower end of exp(w log(1 - mu)); checker B: Arb), a
13th tamper (w -> 3, so (1-mu)^w < x < p; the count was 13, not 14, referee F7) is refused by both with exactly that message, and the condition is in Lemma D's
data and in the CD validity rule. It holds with a wide margin on the three certificates (c1722_m300: x 0.3293 against
(1-mu)^w 0.7890; c1701_m280; certUroot_m250), which both checkers re-accept. Non-blocking: D1 now says phi(1-), D5(B)
says the integral includes the jump of Q at u_b, D8's "< 1e-9" claim is corrected (mesh terms are added explicitly).

## 8. The chain in comparison form (Lemma CF; 18 Nov 13:xx, statement + float test)

Setting: Theorem S, version A (rows of T_v only), constraints (B) and (G) at the scales v_1 < ... < v_m = 1, ZBS's
aggregate at v = 1. A drift phi (nonincreasing, admissible) with drop measure nu = -d phi; for a row with profile F
(nondecreasing, 1-Lipschitz, F(0) = 0), at a scale v > u:
  S(v) = int_{(0,v)} F dnu,  kappa(v) = int_{(0,v]} t dnu(t) = Phi(v) - v phi(v-),  Gamma(v) = kappa(v)/v,
  rho(v) = S(v)/F(v),  D(v) = Gamma(v) - rho(v),  g(v) = F(v)/v,  ghat(v) = (1/kappa(v)) int_0^v g dkappa.
LEMMA CF. (a) (G) at v holds iff D(v) >= -M'_v(g(v)) (M'_v = M at (x e^{eta~_v}, mu e^{eta~_v/w})); equivalently
kappa(v) (g(v) - ghat(v)) >= v R_v(g(v)), R_v(g) = -g M'_v(g).
(b) Between scales: S(v') - S(v) = int_{[v, v')} F dnu >= F(v) nu([v, v')), and the row minimises S by keeping F as low
as monotonicity and the Lipschitz bound allow: F(t) = max(F(v), F(v') - (v' - t)) on [v, v'] (exact minimiser).
(c) Continuum form: dD = -D dlog t + rho dlog g. Drift drops cancel: a drop raises Gamma and rho equally; the chain
advances only through the row's growth of g, and D decays like 1/t otherwise.
(d) kappa-time form: dghat = (g - ghat) dkappa/kappa. On a flat gap [t_a, t_b] (no drop) ghat and kappa are frozen and
(a) reads g(t) >= ghat(t_a) + (t/kappa(t_a)) R_t(g(t)): with g <= mu, R_t(g) <= (mu - ghat) kappa(t_a)/t, so a flat gap
of ratio t_b/t_a forces the desaturation eta~_t up to the level where M'_t >= -(mu - ghat) kappa(t_a)/(t g), i.e. the
gap is paid inside the chain (constraint tightening), not only in ZBS's aggregate.
Proof: (a) is S4 (summation by parts) applied to (G'); (b) monotone F; (c), (d) differentiate. Exact; no new hypothesis.

Float test (cert/chain_float.py, Chain2: drift piecewise linear on a FINE grid, (G), (B) only at every 8th point, so the
within-cell drift shape is the adversary's; greedy least profile per row; c1722; V >= 0 = adversary survives):
- grid: 100 scales, family A log(1/v): V(A=.01) = -2.6e-4 at a - 1e-3, -1.6e-4 at - 1.2e-3, +2.5e-7 at - 1.5e-3;
  fine-grid convergence at 100 scales: 400/800/1600 drift points -> -2.70e-4/-2.62e-4/-2.58e-4 at - 1e-3.
- 200 scales: best of the family at - 1e-3: -5.2e-4; at - 2e-3: +1.4e-5 (A = .01); at - 3e-3: +5.5e-4. 400 scales at - 1e-3:
  -7.0e-4. The chain strengthens with the number of scales (Theorem S allows any finite grid fixed first).
- Named adversaries at 200 scales (- 1e-3 and - 1.5e-3): the lane's 8-knot optima, top-flattening (eta~ = w log(v1/v) on
  v < v1, v1 = 1e-6 ... 0.1, alone or with A log(1/v)) and flat gaps on saturated or desaturated profiles (ratio 3 and 10
  at v = 1e-4 ... 0.2) are all WORSE for the adversary than A = .01 log(1/v). Saturated drift is infeasible (rows near
  the top cannot exist) at 200 and 400 scales.
- So against these drifts the comparison form keeps about 1.5e-3 (100 scales) to 2e-3 (200 scales) in a at c1722, far
  above 5e-4. This is the MODEL's gain: Lemma CF is an exact reformulation, not yet a bound over all drifts.
Robust status: Lemma CF localises the drift (through eta~, Gamma = w + d eta~/dlog v and the drop measure between
scales) and shows that flat gaps are paid. It does not by itself bound the adversary's best drift: all rows share one
drift and each row's chain depends on it over [u, 1], so the sup over drifts is a control problem whose state is the
family of row value functions. Routes: (i) a two-region chain (rows u <= u_b need q >= q_chain(u_b)), certified with
Lemma D's majorisation and a first-order charge of the chain's drift sensitivity (per-row LP multipliers) to the ZBS
loss; (ii) a backward dynamic programme in log v with a finite parametrisation of the row value function.
Float test, richer adversary (13:2x; eta~ piecewise linear in log v on 11-12 knots, Nelder-Mead, c1722, 100 scales,
800-point drift grid):
- full chain (version A, bounds + G at every scale): the adversary SURVIVES at a - 1.2e-3 (V = +3.0e-5; eta~ 0.39 at
  1e-10, 0.14 at 1e-6..1e-4, 0.08 at 1e-3..1e-2, 0.04 at 0.1, 0 above 0.4). So against rich drifts the 100-scale full
  chain keeps less than 1.2e-3 (family: 1.5e-3); 200 scales not yet searched.
- TWO-REGION CHAIN (rows u <= u_b = 0.03 need q >= q_chain(u_b), the least final q of the u_b-cell row's chain over
  [u_b, 1]; rows above unrestricted): the adversary still FAILS at a - 1.0e-3 (V = -1.3e-5); family threshold about
  - 1.55e-3. This route keeps about 1e-3 in a, about 3x Lemma D, and has Lemma D's structure (one row's chain + two
  majorised regions), so it is the certifiable target ('Lemma D'').

## 9. Lemma D' (two-region chain): exact statement (18 Nov 13:4x; for a fresh referee before any long job)

Setting. A control (p, mu, w, beta, x) with 0 < p, mu, beta < 1, w > 0, 0 < x < min{p, (1 - mu)^w}; a scale grid
Lambda = (0 < v_1 < ... < v_m = 1), fixed first, and an index b with u_b := v_b < 1. "Admissible drift": phi
nonincreasing on (0, 1], phi >= -w, int_0^1 phi = 0, Phi(v) := int_0^v phi <= -w v log v; eta~_i := -w log v_i -
Phi(v_i)/v_i (in [0, w log(1/v_i)]); M'_i := ZBS's M at (x e^{eta~_i}, mu e^{eta~_i/w}) (and M'_m = M).
Chain set. For an admissible phi, call a function F: [0, 1] -> [0, 1] a CHAIN PROFILE if F(0) = 0, F is nondecreasing
and 1-Lipschitz, and for every i with v_i > u_b, with g_i := F(v_i)/v_i:
  (B'_i) G0(g_i) <= beta eta~_i and g_i <= mu, i.e. g_i lies in the q-section of D_{v_i,p} at Phibar_i (the closure
         of the shifted feasible set; G0 at the base control); F(v_i) = 0 is the q = 0 case of the same inequality,
         possible only when eta~_i >= log(p/x) (redundant but consistent);
  (G'_i) int_0^{v_i} phi dF - (Phi(v_i)/v_i) F(v_i) <= F(v_i) M'_i(g_i)   (both sides 0 if F(v_i) = 0);
and let Q_min(phi) := inf { F(1) : F a chain profile }  (+infinity if there is none).
The functional:
  V_D'(phi) := int_0^{u_b} sup{ q M(q) - q phi(u) : q in F_p(x, mu), q >= Q_min(phi) } du
             + int_{u_b}^1 sup{ q M(q) - q phi(u) : q in F_p(x, mu) } du        (sup of the empty set = -infinity).
LEMMA D'. If V_D'(phi) < 0 for every admissible drift phi, then (INF) of PROOF.md S7 holds for (p, mu, w, beta, x; Lambda),
so the control meets Definition 5.2''s (INF) requirement and Theorem 4.2' applies (the source index, xi, y0 and nu
are separate data of the control).
V_D' is well defined: both integrands have the form h(phi(u)) with h convex and nonincreasing (a supremum of affine
functions of y = phi(u) with slopes -q <= 0), hence monotone in u and Borel; both are bounded above by w mu/e + w mu
(on F_p, q M(q) <= q B(q) = w q log(mu/q) <= w mu/e, and -q phi(u) <= w q <= w mu since phi >= -w), so V_D' is in
[-infinity, infinity).
Proof (from refereed statements only). Suppose a failing sequence exists. Theorem S3.6 (with d_* relaxed to p, S3.2(iii)) gives
a limit drift phi (admissible, with eta~_i as above) and limit rows omega with uniform rank U and profiles F_omega such
that, for a.e. omega and every i with v_i > U(omega), (B') and (G') hold PER ROW (S3.6 Step 5, first sentence). For a row
with U(omega) <= u_b this holds in particular for every i with v_i > u_b, so F_omega is a chain profile and
q_omega := F_omega(1) >= Q_min(phi). By (G') at v_m = 1 (eta~_m = 0), int_0^1 phi dF_omega <= q_omega M_{d_*}(q_omega) <=
q_omega M(q_omega), and q_omega is in F_p(x, mu) (PROOF.md S6, "Level (i)": closure plus finiteness of (G') at 1, and
F_{d_*} contained in F_p). The limit of ZBS's Step 4 identity (PROOF.md S6) gives E[int phi dF_omega] = E[q_omega phi(U)].
Hence 0 <= E[q_omega M(q_omega) - q_omega phi(U)] <= V_D'(phi): rows with U > u_b are bounded by the second sup, rows with
U <= u_b by the first (q_omega is feasible for it). This contradicts V_D'(phi) < 0. []
Remarks. (1) Only S3.6's per-row (B'), (G') (Step 5), S3.2(iii) (d_* relaxed to p), S6's Level (i) facts (q in F_p),
the v = 1 row bound and the Step 4 limit are used: no (Sym) (per-row (G') does not need (Sym'), PROOF.md as clarified
by the lane), no (L), no version B, no flatness. (2) Every row of rank <= u_b is a chain profile for the SAME set of constraints (scales > u_b),
which is what makes Q_min a single number per drift; rows above u_b are restricted only by q in F_p(x, mu). (3) For the saturated drift
on a 100-scale grid at c1722, Q_min about 0.312 (u_b = 0.03), against 0.293 for level (i)'s two-region restriction.
(4) Lemma D' and Theorem A are different relaxations of S3.6's limit object; neither hypothesis implies the other in
general (V_A restricts rows above u_b through c(u) and uses scales in [u, u_b]; Lemma D' puts no upper end on q, while
{H >= C} can stop below mu). (Referee N1, 14:0x.)
Certification route (NOT part of the statement; open). One must show V_D'(phi) < 0 for all admissible phi. Lemma D's
majorisation handles both regions given (Phi_b, p_b); the new ingredient is a robust LOWER bound on Q_min(phi). A first-
order charge as in D6 meets one bilinear term: with m = g - Phi (deficit) and the row's neighbour density f = F',
the drift enters (G'_i) at first order through -g_i m(v_i) + int_0^{v_i} m'(t) f(t) dt + v_i kappa_eta(g_i) eta~_i, and
the middle term couples the row's neighbour placement with the derivative of the deficit; it is not bounded by ZBS's
majorisation loss alone. Candidate: a branch and bound over Phi at 6-10 knots on [u_b, 1], with Lemma CF's
comparison form (drops cancel; the drift enters through eta~ and Gamma = w + d eta~/dlog v) bounding the chain
between knots. To be designed after the referee has read the statement.


18 Nov 13:5x. Reconciliation with the lane's chain_safe (66 scales: 16 geometric on [1e-6, 0.05], 50 linear on
[0.05, 1]). On the lane's own drifts and grid, Chain2 (drift sampled 16 times per cell) gives V about 1.2e-4 BELOW
chain_safe (-3.3e-4 vs -2.1e-4 at a - 1.2e-3), consistent with chain_safe's extra adversary-favourable relaxations
(tangent bounds, right-end sub-cell drift). My 100-scale "adversary survives at - 1.2e-3" used log-uniform scales from
1e-10 (only about 13 above 0.05, against the lane's 50) and an NM drift admissible only as an 800-point interpolant; it
is a property of that grid, not a stronger adversary. Thresholds should be quoted from LP-based evaluators on grids
dense at large v. Two cautions for Lemma D': the greedy least profile can only overstate Q_min (through the Lipschitz
cap and q-grid rounding, estimated < 1e-4 in q here), so the certificate must compute Q_min's lower bound by an exact LP
with a rational dual; and a grid dense at large v should make the two-region chain STRONGER than the 1e-3 estimate.
18 Nov 14:0x (lane, chain_safe LP as the threshold reference; my 800-point NM drift run through it, scales fixed first):
66 scales: V = -1.48e-4 at a - 1.2e-3, -9.5e-5 at - 1.3e-3, +6.6e-5 at - 1.6e-3 (linear crossing about a - 1.48e-3);
74 scales: -1.27e-4, -7.3e-5, +8.8e-5; 120 scales (40 geometric + 80 linear): -3.80e-4 at - 1.2e-3, -3.25e-4 at - 1.3e-3.
This drift is the strongest adversary so far and is still beaten at a - 1.3e-3; scales dense above 0.05 bind it.
Lemma D' statement (Section 9) is with a fresh referee (arranged by the lane); no long job until its verdict.

18 Nov 14:1x. Lemma D' statement: fresh referee PASS, no blocking point (lane NOTES 14:0x, commit 3925220d5); text fixes
N1-N6 applied above. Certification job may start (one long job at a time, machine gates).

18 Nov 14:2x. New adversary for the chain: STEP DRIFTS aligned with the scale grid. Phi = chords of a desaturated
base curve between breakpoints placed at a fraction theta of every scale cell (drift flat across each scale, drops
between scales). On the lane's 66-scale grid (Chain2, 16 drift points per cell), base = lane's shape-carry eta~:
theta = 0.75 gives V = -1.21e-4 at a - 1.2e-3 and -6.7e-5 at a - 1.3e-3, against -3.27e-4 and -2.72e-4 for the smooth
base; theta = 0.5: -1.72e-4, -1.20e-4; theta = 0.25: -3.9e-4, -3.3e-4; theta = 1 (drops at the scales): -8.0e-4.
Mechanism: a flat stretch across a scale v_i lowers Phi(v_i) (eta~_i > 0 relaxes M'_i at first order) and puts the drift
just below v_i lower (the row's neighbours there count less), while ZBS's majorisation loss is only second order.
The depth of such a dent is at most a chord deficit, about w W^2/(8 v) for width W <= the scale spacing, so the effect
shrinks as the grid is refined; it is a mesh effect, but a first-order one, and it is NOT charged by D5(B) (no drops
where m > 0). Consequences for certifying Lemma D': (1) use a scale grid dense above 0.05 (200+ scales there);
(2) split any drift into its grid data (Phi and the drift at the scales) and its within-cell shape; bound the
within-cell part explicitly through the mesh (as the lane's one-sided c_k bound does), and charge only the
grid-level deviation to ZBS's loss; (3) adversary searches must include step drifts, not only smooth eta~ families.

## 10. Decomposition lemma for certifying Lemma D' (Lemma DL; 18 Nov 14:3x; for a fresh referee)

Setting: Lemma D' (Section 9). Scales v_1 < ... < v_m = 1 of Lambda, u_b = v_b; cells C_k = (v_{k-1}, v_k], v_0 = 0,
Delta_k = v_k - v_{k-1}. For an admissible drift phi: grid values Phi_k = Phi(v_k), chord slopes
sigma_k = (Phi_k - Phi_{k-1})/Delta_k (k = 1..m), sigma_{m+1} := -w; deficits m_k = g(v_k) - Phi_k >= 0 (g(v) = -w v log v),
eta~_k = m_k / v_k, Phibar_k = Phi_k / v_k. For a chain profile F: F_k = F(v_k), DF_k = F_k - F_{k-1}, g_k = F_k / v_k.

(a) WITHIN-CELL PART (exact, one-sided). For every admissible phi and every nondecreasing F,
      int_0^{v_i} phi dF >= sum_{k <= i} DF_k sigma_{k+1}.
    Proof: phi is nonincreasing, so on C_k, phi >= phi(v_k) >= (1/Delta_{k+1}) int_{C_{k+1}} phi = sigma_{k+1} (and
    phi >= -w on C_m); integrate against dF >= 0. []
    Consequently every chain profile under phi satisfies the GRID CHAIN (G~_i), i > b:
      sum_{k <= i} DF_k sigma_{k+1} <= F_i (Phibar_i + M'_i(g_i)),   with (B'_i) as in Section 9,
    and Q_min(phi) >= Q~(Phi_1, ..., Phi_m) := inf{F(1): F nondecreasing, 1-Lipschitz, F(0) = 0, (B'_i), (G~_i) for i > b}.
    The drift enters Q~ only through its grid values. The price is the one-cell lag: the true drift on C_k is replaced by
    the next chord slope, a loss of at most DF_k (sigma_k - sigma_{k+1}) per cell (about w DF_k Delta/v on saturated
    drifts). This is exactly what step drifts (Section 8 note 14:2x) exploit, so a grid geometric with ratio close to 1
    (several hundred scales on [u_b, 1]) makes it small.
(b) GRID-LEVEL LINEARISATION (exact, one-sided). Fix multipliers lambda_i >= 0 (i > b) and write
      L(F; Phi) = sum_{i > b} lambda_i [ F_i (Phibar_i + M'_i(g_i)) - sum_{k <= i} DF_k sigma_{k+1} ].
    Every chain profile under phi has L(F; Phi) >= 0 (each bracket >= 0). For fixed F, L is concave in the grid vector:
    Phibar_i and sigma_k are affine in it, and eta -> g M_eta(g) = K(g, eta) + g eta - w g is concave (K jointly concave,
    Section 3 / Lemma C (iii) with the shift) and eta~_i is affine. Hence, at the saturated grid g_k = g(v_k), wherever
    L(F; g) is finite:
      L(F; Phi) <= L(F; g) + sum_k gamma_k(F) m_k,
      gamma_k(F) = lambda_k dK(g_k) + Lam_{k-1} DF_{k-1}/Delta_k - Lam_k DF_k/Delta_{k+1}   (Lam_k = sum_{i >= k, i > b} lambda_i,
    dK = d_eta K(g, 0) >= 0, zero on the non-binding branch; terms with indices outside the chain read 0).
    Summing by parts, sum_k gamma_k m_k = sum_k lambda_k dK(g_k) m_k + sum_k Lam_k (DF_k/Delta_{k+1}) (m_{k+1} - m_k):
    the desaturation term (as in Lemma D's D6) plus a BILINEAR term (row density times deficit increments).
    Rows with g_i below the base feasible set but above a(eta~_i) are handled by a(eta) >= a0 - alpha eta (D0.1): the
    sup over F below runs over F_i >= a0 v_i - alpha m_i, with M'_i bounded above by its value at the left end.
(c) ZBS CHARGE (exact, one-sided). On [u_b, 1] (D5(B) with strong convexity): if kappa2 <= -qhat' on the drift range
    [y_c, y_top] (Lemma D's slope bound), then
      int_{u_b}^1 Hhat(phi_s) - int_{u_b}^1 Hhat(phi) >= qhat(p_b) m_b + int m dQ + (kappa2/2) int_U (phi_s - phi)^2,
    U = {t: phi(t), phi_s(t) in [y_c, y_top]}, Q = qhat o phi. (Ĥ(phi_s) >= Ĥ(phi) + Ĥ'(phi)(phi_s - phi) + (kappa2/2)
    (phi_s - phi)^2 when both lie in the strongly convex range; integrate by parts as in D5(B).) In grid terms:
      int_U (m')^2 >= sum_{cells C_k in U} (m_k - m_{k-1})^2 / Delta_k     (Cauchy-Schwarz on each cell),
      int m dnu >= sum_k (min over C_k cup C_{k+1} of m) (sigma_k - sigma_{k+2})/... >= explicit grid lower bound
    (m >= linear interpolation - w Delta^2/(8 v) on a cell, since m'' >= -w/t; drops over two cells are >= the chord-slope
    difference), so the whole charge is bounded below by an explicit function Z(m_grid) of the grid deficits.
(d) CLOSING CONDITION (what the certificate verifies, per box of (Phi_b, p_b) and per target Q_t). With lambda from the
    saturated reference LP at Q_t, margin(Q_t) := -sup_{F(1) <= Q_t} L(F; g) > 0, and Lemma D's theta-combination,
    Lemma D' holds on the box if for every admissible grid deficit vector m (m_k >= 0, discrete m'' >= -w/v, m_m = 0,
    m_b in the box): either sup_F sum_k gamma_k(F) m_k < margin(Q_t) (then Q_min >= Q_t), or the ZBS charge
    theta Z(m) pays for lowering Q_min to the next target level. This is a finite-dimensional condition on the grid
    vector m; its verification (a QP-type bound, the bilinear term handled by the bounds on F) is the computational
    part, and the open question is whether the constants leave a material gain. The mesh enters only through (a)'s lag
    and the cell terms of (c).
Status: REFEREE FAILED (18 Nov, fresh referee via the lane agent): part (a) is correct; (b), (c) and (d) have
blocking gaps B1-B3 (rows below a(0) not covered by the saturated tangent; the grid lower bound for the ZBS charge is
wrong in three places; the closing condition is not a precise inequality). The earlier line "(a)-(c) are proved" was
false. Revision in progress; nothing in Section 10 may be used until a fresh referee passes it.

18 Nov 14:0x. Lemma D' float sweep (cert/dprime_float.py: Q_min by the exact grid-chain LP of Lemma DL (a), tangents of
g M'_i as upper bounds; c1722; u_b = 0.03; 29 scales below u_b, chain scales geometric on [0.03, 1]; 6 drift points
per cell). Named drifts (5 bases x step theta in {none, .5, .75, .9}): best V at a - 1.2e-3 = -2.09e-4 (200 chain
scales), -2.76e-4 (400); thresholds about a - 1.6e-3 and a - 1.7e-3. Step drifts add nothing under the grid relaxation
(it already takes the worst within-cell shape). Nelder-Mead adversary (12 eta~ knots + step theta, 3 starts, 200 chain
scales): a - 1.2e-3 -> V = -1.39e-4 (fails); a - 1.5e-3 -> V = +1.6e-5 (survives); threshold about a - 1.47e-3.
So the drift-by-drift value of Lemma D' keeps about 1.45e-3 in a at the root against the searched adversary; the robust
certificate (Lemma DL (d)) will lose part of it. Realistic certified target: 0.9e-3 to 1.2e-3 (guess, to be measured).

Note (18 Nov, independent checker and spec fixes). checkD_C (cert_independent/, fresh author from 4b/4c only) accepts all
four Lemma D certificates and found no soundness gap; its 15 SPEC_ISSUES points are fixed in the text (Section 1:
Lemma C (iii) cited with source, referee and proof; Section 2 and K5: cell 0 uses the right-end tangent; D7: the
PK = g- case of K rests on weak majorisation; D8: wording and the D-scaling test; 4b: node ranges j >= 1, empty and
missing node cases, rounding direction of phi_s arguments, u2 clipped to 1, one theta; 4c: certified-in-Q method and
node values at uncertain branch sign; Section 4: the third checker and tamper_D's margin probes). The only code change
is tamper_D.py: the two margin probes now take f from the certificate's own worst leaf U0 (f1 = max(2e-6, 8|U0|),
f2 = max(1e-5, 40|U0|)). Rerun at 10:16-10:19 UTC on all four certificates (checkD_A and checkD_B, python-flint 0.9.0):
ALL 15 TAMPERS REFUSED BY BOTH on each. Worst leaf U by checker A: c1722_m300 -8.89e-8, c1722_m280 -7.50e-7,
c1701_m280 -1.03e-6, certUroot_m250 -9.12e-6 (checkD_C: -1.33e-7, -7.63e-7, -1.03e-6, -9.12e-6; the checkers differ
only in enclosure choices, all negative). Margin probes refused through K10 (a box with U > 0) in every case.
checkD_A, checkD_B, genD, ivA and the certificates are unchanged from the frozen commit 4c103f488.

Note (18 Nov, 10:3x UTC; DATED NEGATIVE for the linearised Lemma D' certificate; float, proves nothing). Before revising
Lemma DL (b)-(d) I measured what a linearised robust bound keeps at the saturated box at c1722 (cert/dl_robust_float.py,
cert/dl_scale.py; 100 chain scales, u_b = 0.03). Design L1, the simplest bound valid for every row profile F: the
reference chain LP at m = 0 (B1's fix: supporting planes of the jointly concave K(g, eta), plus F_i >= a0 v_i), its
optimal duals y, and the partial Lagrangian with 0 <= DF_k <= Delta_k kept inside, giving for every deficit vector m
  Q_min(m) >= Q_ref - S(m),  S(m) = sum_k Delta_k Y_k ((m_{k+1} - m_k)/Delta_{k+1})_+ + sum_i (E_i)_+ m_i,
with IL concave in Q (IL(Q_ref - S) <= IL(Q_ref) + |IL'(Q_ref)| S). Q_ref agrees with dprime_float's LP (0.31146 vs
0.31135 at a - 4e-4). Results (bump-family search plus SLSQP refinement over m, constraints: m >= 0, m_b = m(1) = 0,
drift nonincreasing and >= -w, m(v) <= g(v) + (1 - v) phi(v)):
- Right region by Lemma D's (B): sup over m of the bound's excess is about 2.5e-2 at a - 4e-4 and a - 1.2e-3, against
  margins 6.1e-4 and 1.9e-4. The adversary flattens the drift where m is large, so int m dQ is about 0: (B) drops the
  Bregman term, which is the whole charge for such profiles.
- Right region exact on the grid (sum Delta_k Hhat(sig_k(m)), keeps the Bregman term): excess still about 1.8e-2.
- Scale test (dl_scale.py, a - 4e-4, saturated V = -6.16e-4). For the bumps best for the bound, the L1 bound's change
  of V against the TRUE change (exact chain LP on the same grid drift):

  | peak m | L1 bound dV | true dV  | bound on Q drop | true Q drop |
  |--------|-------------|----------|-----------------|-------------|
  | 1.7e-4 | +3.8e-5     | +2.0e-5  | 1.1e-3          | 6.1e-4      |
  | 5.0e-4 | +8.1e-5     | +2.7e-5  | 2.7e-3          | 1.2e-3      |
  | 1.7e-3 | +2.6e-4     | +4.4e-5  | 7.7e-3          | 1.9e-3      |
  | 5.0e-3 | +7.8e-4     | +5.8e-5  | 2.3e-2          | 3.5e-3      |
  | 1.7e-2 | +2.3e-3     | -1.1e-4  | 6.9e-2          | 5.0e-3      |
  | 5.0e-2 | +6.7e-3     | -2.1e-3  | 2.6e-1          | 2.3e-2      |

  The TRUE response is fine: dV is at most about +6e-5 and turns negative for large deficits, consistent with the
  Nelder-Mead threshold a - 1.47e-3. But the true Q drop grows like sqrt(m) (x10 in m gives about x3.2), while any
  bound linear in m grows like m. The linear bound is 2x the truth at peak 1.7e-4, 7x at 5e-3 and 11x at 5e-2, and
  passes the 6.1e-4 margin at a peak of about 4e-3.
CONCLUSION: a linearised (single reference dual) certificate of Lemma D' keeps NOTHING in a: it fails at every shift
tested, including a - 4e-4, below the 4e-4 bar. By the rule set on 18 Nov, the Lemma D' certificate is STOPPED, and
the B1-B3 revision of Lemma DL is not pursued. The obstacle is structural, not a referee detail. A valid certificate
must bound Q_min by a concave (about sqrt) function of a deficit vector with about 100 free coordinates. The only route
I see:
- a trust region (peak deficit up to about 3e-3, where L1 keeps the margin);
- outside it, a nonlinear bound: several reference duals (multi-cut outer approximation) plus the right region's
  Bregman charge, over a deficit space with no low-dimensional sufficient statistic, while the cap band (v > 0.72)
  charges nothing.
That is a new project, not a refinement of Lemma DL. Lemma D (level (i), certified at c1722 a - 3.0e-4 and
a - 2.8e-4) is unaffected.

Note (18 Nov, 11:1x UTC; FLOAT GATE FAILED for the multi-cut Lemma D' certificate; float, proves nothing). The lab lead's
gate: trust region plus multi-cut outer approximation of Q_min must keep >= 4e-4 in a at c1722. Code:
cert/cutq_float.py (cuts) and cert/dp_gate.py (exact sup of the convexified form).
- CUTS. For a reference deficit m^(j), the chain LP's optimal duals are kept with the DF box inside the Lagrangian.
  Minimising over the box and over the gaps then gives cut_j(m), a valid lower bound of Q_min(m) for EVERY m, exact at
  m^(j) (checked: cut equals LP value to 1e-16). The planes of K are B1's fix; F_i >= (a0 - alpha eta_i) v_i.
- Form 1 (non-convex): Vb(m) = IL(max_j cut_j(m)) + exact grid right region. Its sup can only be SEARCHED (bumps,
  Nelder-Mead on 12 log-knots, 6000-step full-dimensional random search), with cuts added at the true adversary's
  worst deficit and at each searched maximiser.
  - 100 scales, a - 4e-4 (saturated V -6.16e-4, true searched sup -4.86e-4): sup Vb with 12 cuts is -2.5e-5. It
    fluctuates between -2.8e-5 and +8e-5 across 2-12 cuts.
  - 100 scales, a - 6e-4: +3.2e-5 with 12 cuts (fails).
  - 200 scales, a - 4e-4 (saturated -7.99e-4, true -6.25e-4): it fluctuates around 0 (+1.2e-5 with 12 cuts, -6.9e-5
    with 11).
  - Marginal at best, and no exact sup method exists for this form.
- Form 2 (convex, exact sup):
  - For each cut, IL is replaced by its tangent at Q_j. Then f_j(m) is a SEPARABLE CONVEX function of the right-cell
    drifts.
  - The admissible set is {s nonincreasing, Phi <= g, Phi(u_b) = g(u_b), Phi(1) = 0}. Its vertices are the
    grid-chord profiles: at an extreme point every kink lies on g (tent perturbation), so Phi is g or a chord of g.
  - So max over m of sum_j lambda_j f_j(m), and of f(m; averaged duals), is a longest-path DP over touching points,
    O(n^3), and EXACT.
  - Results, min over lambda of the exact max (100 scales, a - 4e-4):
    - convex combination of bounds: +1.78e-2 (1 cut), +3.1e-3 (2), +2.5e-3 (5), +2.12e-3 (12);
    - averaged multipliers (never worse, by Jensen): +2.8e-3 (2), +2.2e-3 (3), +2.0e-3 (5).
  - The maximisers are multi-chord profiles with 4 to 36 touching points, where the true V is -0.7e-3 to -1.9e-3.
- VERDICT: the gate fails. The searched form is marginal at a - 4e-4 and fails at a - 6e-4. The exactly bounded form
  fails by about 2e-3, because global multipliers cannot serve all chord profiles. In any case the searched form would
  add under 1e-4 to Lemma D's certified 3.0e-4 at c1722. The multi-cut lane is STOPPED.
- What remains for level (ii) is the lane agent's per-row Lagrangian with multipliers per row cell, fitted at the worst
  drift. Its test drifts (8 named, single chords) stay at W < 0 at a - 1e-3 with 66 scales. Two things are still open:
  - multi-chord drifts, which were the maximisers here;
  - region-dependent multipliers: branch and bound over anchor values of Phi, with the anchors as DP nodes and a
    concavity check at each anchor.
  Same rule: no rigorous work before an exact (DP) or exhaustive float sup keeps >= 4e-4.

Note (18 Nov, 11:3x UTC; domain of the shifted control, after the lane agent's chain_safe fix 28851ef20). At a scale
with eta~ >= about 0.418 at c1722, the shifted control leaves the domain: x e^eta >= p (from eta = 0.4179) or
mu e^{eta/w} >= 1 (from 0.4182). Lemma D' then gives no (B') or (G') constraint at that scale.
- cert/dprime_float.py kept FINITE but unjustified tangents there; it did not drop them. This is the opposite artefact to
  the lane's -inf.
- It now drops both constraints at such scales and keeps only F_i <= v_i, which favours the adversary.
- Recheck at a - 4e-4 (100 scales): the single chord u_b -> 1 has max eta~ 0.61, and its true V is unchanged at
  -7.185e-3. Two- and three-chord profiles (max eta~ about 0.28) are inside the domain.
- The planes in cutq_float.py and dl_robust_float.py are also applied beyond the domain. That can only make those
  bounds smaller than a correct bound, so their negatives stand.
- Lemma D and its certificates use no shifted control and are unaffected.

Note (18 Nov, 11:4x UTC; REGION-DEPENDENT multipliers also fail; float, proves nothing; cert/region_bb.py). This was the
lane agent's request: a branch and bound over anchor values lo_a <= Phi(v_a) <= hi_a at v_a = 0.06, 0.12, 0.25, 0.50,
with ONE cut per box fitted at the box's worst vertex and the EXACT max over the box's vertices.
- How the max is computed: an anchor DP. Kinks are allowed at grid points on g and at anchor nodes. Chords that pass
  an anchor are checked against [lo_a, hi_a], and anchor nodes below g are checked for concavity. On the unrestricted
  box it reproduces the plain DP to 1e-17.
- Results at a - 4e-4, 100 scales:
  - The depth-first run reached depth 19 after 20 boxes (each anchor about 1/32 of its range) and still had a max of
    +2.9e-3.
  - Diagnosis: a TINY box (all four anchors within 1% of their range of g) still has an exact max of +1.3e-3 to +2.5e-3.
    The refits cycle between two vertices: deficit 2.0e-2 peaked at v 0.73 (true V -8.3e-4) and deficit 4.9e-3 peaked
    at v 0.87 (true V -5.4e-4). The cut fitted at one gives the other.
- Cause: a cut is linear in the deficits away from its reference, while Q's true response is about sqrt-like. Every
  scale whose deficit an anchor does not pin is a direction where the cut overstates the drop. The cap band
  (v > 0.72) gives no right-region charge to offset it. Anchors would be needed at essentially every scale, which makes
  the search exponential.
- VERDICT: region-dependent multipliers with a few anchors do not close even near saturation. Level (ii) through
  Lagrangian or cut bounds is exhausted in both the two-region and the per-row form (the lane agent: global lambda
  fails, and averaged lambda is worse). Any further level-(ii) attempt needs a bound that is NONLINEAR in the deficit
  at every scale, i.e. a new idea, not more cuts or regions.

Note (18 Nov, 11:5x UTC; the two-region form's TRUE threshold over chord profiles; float; cert/chord_search.py). True V
here means the exact chain LP on the grid drift, with the domain fix d5e9faf6c. It is maximised over grid-chord profiles
by local search on the touching set: 6 starts, 250 toggle or block moves each. Results at 100 chain scales:

| shift in a | saturated V | worst chord V | grid points off g |
|---|---|---|---|
| 4e-4   | -6.16e-4 | -4.12e-4 | 64 of 100 |
| 1.0e-3 | -2.94e-4 | -0.90e-4 | 62 |
| 1.4e-3 | -0.79e-4 | +1.18e-4 | 59 |

- Chord profiles beat the smooth bump and Nelder-Mead families: -4.86e-4 at a - 4e-4.
- The worst ones leave the cells next to u_b and many others off g.
- The two-region threshold over chord profiles at 100 scales is about a - 1.17e-3 (interpolated). The saturated
  threshold is about a - 1.5e-3.
- This corrects my earlier "about 1.4e-3 to 1.5e-3", which came from the 200-scale Nelder-Mead family. Chord profiles
  were not searched there.
- The chord gain is about 2.0e-4 in V at every shift, i.e. about 3.5e-4 in a.
