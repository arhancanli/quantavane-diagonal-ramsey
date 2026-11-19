# P3. Banks: Lemmas 5.8-5.9, Theorem 5.7 and Corollary 5.10 with full proofs

Draft 19 Nov 2026 (+04); v2 after its fresh referee (PASS WITH FIXES: one GAP, the proof of (R2), now replaced by an
exact identity; ten NITs applied; REFEREE_P3_20261119.md). Block P3 of UNCONDITIONAL_PLAN.md. The statements and arguments are
those of Zhao, Booth-Clibborn and Schwahn (ZBS, preprint @ c2875f33, Section 5); we restate them in our words with
every step checked, with two changes: (1) the off-diagonal input is our Theorem 2.2' (P4.6) at the one epsilon the
proof uses, instead of Lu-Wang's Theorem 2.2 for all epsilon; (2) a control may be an extended control (SELF_CONTAINED
6.10, Definition 5.2'), since the only property of a control used is the finite-host closure (Theorem 4.2 or 4.2').
Definitions 5.1-5.6 are as quoted in SELF_CONTAINED 1.4 (source pairs (A_h, B_h) with claims (SOURCE_h); controls;
profiles P = (p_P, I_P, L_P) with claims (ASSERT_P); direct realisations: leaves and retained routes with (12);
combined realisations: density copies and complementary pairs; source covers with (13)). A BANK is a finite set of
source pairs, controls, direct profiles and combined profiles in which every direct profile, combined profile and
source pair has a realisation or cover as in Definitions 5.4-5.6 whose references (controls, source indices, child
profiles, profiles of combined pieces and of cover cells) lie in the bank. Inputs used: Erdos-Szekeres (ES);
the balanced cut (P4.3, first sentences of its proof: a host of order N >= 3 and red density d has a partition
V = X ⊔ Y with |X|, |Y| >= N/3 and d_R(X, Y) >= d); Theorem 4.2 for ZBS-type controls (block P2) or Theorem 4.2' for
extended controls (SELF_CONTAINED 6.10); Theorem 2.2' (P4.6).

For C >= 1 and a host V, P_V(C) is the statement: every bank claim (ASSERT_P and SOURCE_h), with constant C, holds on
every proper subset Z of V, under both namings of the colours. (On sets with |Z| <= 1 every claim is vacuous: its
threshold C e^{(positive)} exceeds 1. Renaming the colours of V preserves P_V(C).)

## P3.1 Lemma 5.8 (leaves and routes)

Lemma 5.8. For each leaf or route piece J of a direct profile P there are K_J >= 1 and D_J >= 1, depending only on the
data of the piece (not on C), such that: if V satisfies P_V(C) for some C >= 1, a naming of the colours is fixed,
k >= K_J, b/k in J, d_R(V) >= p_P and |V| >= D_J C e^{k (L_P(b/k) - eps_J/2)}, then V contains a red K_k or a blue K_b.

Proof. Stopping rule. Let gamma be the control of the piece, sigma its source index, xhat = e^{-A_sigma},
yhat = e^{-B_sigma}. For every W in V and every l >= 1, W satisfies Stop(C, xhat, yhat, l): a proper subset Z of W is a
proper subset of V, and |Z| >= C xhat^{-a} yhat^{-l} = C e^{A_sigma a + B_sigma l} gives a red K_a or a blue K_l in Z by
(SOURCE_sigma) on Z (part of P_V(C)). gamma's numbers satisfy xi < min{x, xhat}, y0 < yhat, nu < mu (Definition 5.2 or
5.2'), so Theorem 4.2 (or 4.2') gives a threshold L_0(gamma). Write A = A_gamma = -log xi, B = B_gamma = -log y0,
b_g = b_gamma = -log nu, w = w_gamma, pi = p_gamma.

Leaves (D_J = 3). Let alpha = min J and choose K_J with floor(alpha k) >= max{1, L_0(gamma)} for k >= K_J. Let r = b/k,
L = L_P(r) - eps_J/2 (L > eps_J/2 > 0 by the leaf inequality, since A, B, b_g > 0). As |V| >= 3 C e^{kL} >= 3, the balanced cut gives V = X ⊔ Y with d_R(X, Y) >= d_R(V) >= p_P >= pi
and |X|, |Y| >= C e^{kL}. The leaf inequality (1 + w) L_P(r) >= (1 + w) eps_J + A + r (B + w b_g) gives
(1 + w) L > A + r (B + w b_g), so log(|X|^w |Y|) >= (1 + w) log C + (1 + w) k L >= (1 + w) log C + k A + b B + w b b_g,
i.e. |X|^w |Y| >= C^{w+1} xi^{-k} y0^{-b} nu^{-w b}. Theorem 4.2 with t = l = b (b = r k >= alpha k >= L_0(gamma)) gives
a red K_k in X ∪ Y or a blue K_b in X or in Y.

Routes. Let theta = u_0 < ... < u_M = omega, slopes d_j, children c(j), psi as in Definition 5.4(2); r = b/k in J, so
theta <= r <= omega. Put E(r) = max(psi(r), (A + r B + w (theta b_g + psi(r) - psi(theta)))/(1 + w)), eps = eps_J/2 and
z := E(r) + eps <= L_P(r) - eps_J/2. Let G = psi + E(r) - psi(r) + eps/2 on [theta, r] (a vertical shift of psi). Then
    z - G(r) = eps/2,   z + w G(theta) - (A + r B + w theta b_g) >= (1 + w/2) eps,                          (R1)
the second because (1 + w) E(r) >= A + r B + w (theta b_g + psi(r) - psi(theta)). Let V_d = |d_1| + sum_{j<M}
|d_{j+1} - d_j|, delta0 = min_j min_{s in J_j} (psi(s) - L_{c(j)}(s)) > 0, eta0 = min_j (1 - p_{c(j)} - e^{-d_j}) > 0, and
psi_min = min psi > 0 (psi > L_{c(j)} > 0 on each cell); all by (12) and compactness. Put D_J = 3(1 - pi)/(p_P - pi)
(>= 3) and choose K_J such that for k >= K_J: floor(theta k) >= max{1, L_0(gamma)}, k eps/2 > V_d, k delta0 > V_d and
eta0 e^{k psi_min - V_d} >= 1.
Suppose |V| >= D_J C e^{kz} (>= 3, since D_J >= 3 and z > 0). Take the balanced cut X0, Y (d_R(X0, Y) >= p_P, |X0|, |Y| >= |V|/3) and let X be the
vertices of X0 with at least pi |Y| red neighbours in Y. Since p_P |X0||Y| <= e_R(X0, Y) <= |X||Y| + pi (|X0| - |X|)|Y|,
|X| >= ((p_P - pi)/(1 - pi)) |X0| >= C e^{kz}; also |Y| >= |V|/3 >= C e^{kz}, and every nonempty Z in X has
d_R(Z, Y) >= pi. Let l = b and n0 = floor(theta k). For s in (theta, r] let d(s) be the slope of psi on the cell
containing s (the left cell at a knot). Define Gamma(t) = k G(theta) for t <= n0 and
Gamma(t) = k G(theta) + sum_{n0 < tau <= t} d(tau/k) for n0 < t <= l (integers).
(R2) |Gamma(t) - k G(t/k)| <= V_d for n0 < t <= l, and Gamma(t) >= k psi_min - V_d for all 1 <= t <= l.
Proof of (R2). For s in (theta, omega], d(s) = d_1 + sum_{j<M} (d_{j+1} - d_j) 1[s > u_j] (the left cell at a knot). Hence
k G(t/k) - k G(theta) = int_{k theta}^{t} d(sigma/k) dsigma = d_1 (t - k theta) + sum_j (d_{j+1} - d_j)(t - k u_j)_+, and
Gamma(t) - k G(theta) = sum_{tau = n0+1}^{t} d(tau/k) = d_1 (t - n0) + sum_j (d_{j+1} - d_j) #{integers tau in (k u_j, t]}
(using k u_j > k theta >= n0); the count is t - floor(k u_j) if k u_j < t and 0 otherwise. Subtracting (n0 = floor(k theta)),
    Gamma(t) - k G(t/k) = d_1 {k theta} + sum_{j : k u_j < t} (d_{j+1} - d_j) {k u_j},   {x} = x - floor(x) in [0, 1),
so |Gamma(t) - k G(t/k)| <= |d_1| + sum_j |d_{j+1} - d_j| = V_d. Also G >= psi + eps/2 >= psi_min (E(r) >= psi(r)), so k G(t/k) >= k psi_min and
Gamma(t) >= k psi_min - V_d; for t <= n0, Gamma(t) = k G(theta) >= k psi_min.
Claim: for t = 1, ..., l and every Z in X with |Z| >= C e^{Gamma(t)}, Z ∪ Y contains a red K_k, or Z a blue K_t, or Y a
blue K_l. Induction on t.
- t <= n0: by (R1), log(|Z|^w |Y|) >= (1 + w) log C + k (w G(theta) + z) >= (1 + w) log C + k A + l B + w k theta b_g
  + k (1 + w/2) eps > (1 + w) log C + k A + l B + w t b_g (t <= n0 <= k theta, l = k r), i.e.
  |Z|^w |Y| >= C^{w+1} xi^{-k} y0^{-l} nu^{-w t}, and d_R(Z, Y) >= pi; Theorem 4.2 (l >= n0 >= L_0(gamma)) gives the claim.
- n0 < t <= l: let s = t/k, let J_j be the cell that defines d(s) (the left cell at a knot) and c = c(j). By (R2), Gamma(t) >= k G(s) - V_d >=
  k psi(s) - V_d >= k (L_c(s) + delta0) - V_d > k L_c(s). If d_R(Z) >= p_c, (ASSERT_c) on the proper subset Z of V
  at the integer pair (k, t), t/k = s in J_j in I_c, gives a red K_k or a blue K_t in Z. Otherwise the average blue
  degree in Z exceeds (1 - p_c)(|Z| - 1), so some v in Z has more than (1 - p_c)(|Z| - 1) >= e^{-d(s)} |Z| blue neighbours
  in Z (the inequality is (1 - p_c - e^{-d(s)}) |Z| >= 1 - p_c, implied by eta0 |Z| >= 1, which holds as
  |Z| >= e^{Gamma(t)} >= e^{k psi_min - V_d} >= 1/eta0). Its blue neighbourhood Z' in Z has |Z'| > e^{-d(s)} |Z| >=
  C e^{Gamma(t) - d(s)} = C e^{Gamma(t-1)}. The claim for t - 1 on Z' gives a red K_k in Z' ∪ Y, a blue K_l in Y, or a
  blue K_{t-1} in Z', which with v is a blue K_t in Z.
Finally Gamma(l) <= k G(r) + V_d = k z - k eps/2 + V_d < k z (or Gamma(l) = k G(theta) = k G(r) if l <= n0), so
|X| >= C e^{kz} > C e^{Gamma(l)}, and the claim with Z = X, t = l = b gives a red K_k in X ∪ Y or a blue K_b in X or Y. []

## P3.2 Lemma 5.9 (combined profiles on the same host)

Lemma 5.9. Let C >= 1. If every direct claim with constant C holds on the host V under both namings of the colours,
then every combined claim with constant C holds on V, under both namings (apply the statement to V with the colours
renamed, which satisfies the same hypothesis). Proof. Let r = b/k lie in a piece J of a combined profile Q and |V| >= C e^{k L_Q(r)}. Density copy R:
d_R(V) >= p_Q >= p_R and L_R(r) <= L_Q(r), so (ASSERT_R) applies. Complementary pair (R, S): if d_R(V) >= p_R,
(ASSERT_R) applies at (k, b) (L_R(r) <= L_Q(r)); otherwise d_B(V) > 1 - p_R >= p_S, and (ASSERT_S) with the colours
renamed applies at the pair (b, k), whose threshold is C e^{b L_S(k/b)} = C e^{k r L_S(1/r)} <= C e^{k L_Q(r)}; in the
original names its outcome is a blue K_b or a red K_k. The complementary case never uses d_R(V) >= p_Q. []

## P3.3 Theorem 5.7 (bank validity)

Theorem 5.7. For every bank there is C_* >= 1 such that, with C = C_*, every claim (ASSERT_P) and (SOURCE_h) holds for
every host, provided min_h min(eps_h, eta_h) > 2 h(10^-16) (= 7.57e-15; this proviso comes from using Theorem 2.2'
instead of Lu-Wang's Theorem 2.2 for every epsilon).

Proof. Constants. Let K >= 2 be an integer with K >= K_J for every leaf and route piece J and K eps_J/2 >= log D_J for every
direct piece. Let M_I = max{1, the largest right end of all I_P}, c0 = min_h min(A_h, B_h) > 0, and
    C_prof = max{R(k, b) : 1 <= k < K, 1 <= b <= M_I (K - 1)},   C_small = max_{0 <= j <= K-2} j! (2/c0)^j,
and C_tail = C_eps of Theorem 2.2' with eps = min_h min(eps_h, eta_h) (> 2 h(10^-16) by the proviso). Let
C = max{1, C_prof, C_small, C_tail}.
Grounding. (a) For a profile P and k < K with b/k in I_P: b <= M_I (K - 1), so |V| >= C e^{k L_P(b/k)} >= C >= R(k, b),
whatever the density (L_P > 0). (b) For a source pair h and b/k not in (l_h, H_h): (13) gives (G_f(k, b) = k f-hat(b/k), P4.1)
G_f(k, b) + eps (k + b) <= k f-hat(b/k) + eps_h k (1 + b/k) <= k T_h(b/k) = A_h k + B_h b, so
|V| >= C e^{A_h k + B_h b} >= C_eps e^{G_f(k, b) + eps (k + b)} and Theorem 2.2' gives (SOURCE_h). The same on grounded
cells (with eta_h). (c) If min(k, b) < K, put j = min(k, b) - 1 and n = max(k, b); by (ES),
R(k, b) <= binom(n + j - 1, j) <= (2n)^j = j! (2/c0)^j (c0 n)^j/j! <= j! (2/c0)^j e^{c0 n} <= C e^{A_h k + B_h b}, which
proves (SOURCE_h) for such (k, b).
Induction. Suppose some claim fails. Let V be a host of least order on which some claim fails under some naming of the
colours; then P_V(C) holds.
Stage 1 (direct claims on V). Let P be direct, b/k in I_P, d_R(V) >= p_P, |V| >= C e^{k L_P(b/k)}. If k < K use (a).
Otherwise take the piece J containing b/k: k eps_J/2 >= log D_J gives |V| >= D_J C e^{k (L_P(b/k) - eps_J/2)}, and
Lemma 5.8 (k >= K >= K_J) gives a red K_k or a blue K_b. The same with the colours renamed.
Stage 2 (combined claims on V, under both namings): Stage 1 and Lemma 5.9.
Stage 3 (source claims on V, under both namings; we argue for one naming, the other being the same argument on V with
the colours renamed). By (b) and (c) we may assume k, b >= K and lambda = b/k in a cell J of [l_h, H_h] carrying
profiles P_R, P_B (grounded cells are covered by (b)). If d_R(V) >= p_{P_R}: (ASSERT_{P_R}) holds on V (Stages 1-2),
and k L_{P_R}(lambda) <= k T_h(lambda) = A_h k + B_h b. Otherwise d_B(V) > 1 - p_{P_R} >= p_{P_B}, and (ASSERT_{P_B})
with the colours renamed at (b, k) applies: b L_{P_B}(1/lambda) = k lambda L_{P_B}(1/lambda) <= A_h k + B_h b.
So every claim holds on V, a contradiction. Take C_* = C. []
Remark (cycles). References between profiles and sources may form cycles: every use of a claim in the proofs above is
on a proper subset of the current host (Lemma 5.8, Stage 3 uses Stages 1-2 on V itself only for direct and combined
claims, which Stage 1 proves on V from claims on proper subsets).

## P3.4 Corollary 5.10 (diagonal bound)

Corollary 5.10. If a combined profile Q of a bank has 1 in I_Q and the piece of Q containing 1 is a complementary pair,
then R(k, k) <= ceil(C_* e^{k L_Q(1)}) for every k >= 1 (under the proviso of Theorem 5.7). (It suffices that SOME
piece of Q containing 1 is a complementary pair; the checkers verify that every such piece is.)
Proof. By Theorem 5.7 every direct claim holds on every host under both namings. Let a host have order
N >= C_* e^{k L_Q(1)}. The proof of Lemma 5.9 for the complementary piece (R, S) containing 1, at the pair (k, k), gives
a red K_k or a blue K_k without using any density hypothesis on Q. []

## P3.5 Mixed banks

Every statement above holds verbatim for banks whose controls are extended controls (SELF_CONTAINED 6.10, Definition
5.2'): the only use of a control is in the proof of Lemma 5.8, through (i) the stopping rule from (SOURCE_sigma), (ii)
the inequalities xi < min{x, e^{-A_sigma}}, y0 < e^{-B_sigma}, nu < mu, which give L_0(gamma), and (iii) the conclusion of
Theorem 4.2 at a pair with d_R >= p_gamma; Theorem 4.2' provides (ii)-(iii) with the same hypotheses and conclusion; its threshold L_0 also depends on the
control's grid Lambda, which is part of the extended control's data, so K_J is still independent of C.

## P3.6 Remarks

- Sub-banks. The definition of a bank is intrinsic: any sub-collection of a bank that is closed under all references
  (controls, source indices, route children, profiles of combined pieces, profiles of source-cover cells) is a bank,
  and the proviso of Theorem 5.7 passes to it (a minimum over fewer sources is not smaller). This is what lets the
  certificates use only the reference-closed cone of ZBS's bank P0r12.
- The proviso is sufficient; eta_h reaches Theorem 2.2' only through grounded cells, so
  min(min_h eps_h, min over sources with a grounded cell of eta_h) > 2 h(10^-16) would also do (with eps in C_tail redefined as that minimum).
- Every citation of Theorem 5.7 or Corollary 5.10 for our certificates carries the proviso, checked on the data in
  stage 2c (P4.6).
