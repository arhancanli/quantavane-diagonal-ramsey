# Proposition QR: a quasi-random ceiling for the local step of the ZBS potential method (v2)

v1: 19 Nov 2026, 21:5x +04. Fresh referee (REFEREE_QR_20261119.md): PASS WITH FIXES, two GAPs (tolerances; red failure
needed at EVERY row for Lemma 4.5 / 4.5'), ten NITs. v2 (22:2x) applies every fix: kappa <= 1 and the (B1) tolerance
eps; a new Step D' giving red failure at every row (so (M) and the zeta-dependence of r are gone); (B2) restated; the
Step D factor corrected; N reserved for |X0|; Step A tie-break and dependencies; the c' remark at the minimal Delta;
scope of the Consequence narrowed; Remarks corrected; the sanity remark added. Status: v2 re-refereed 19 Nov 22:1x: PASS (six NITs, applied in v2.1).

Notation as in papers/diagonal-ramsey-2026/SELF_CONTAINED.md Section 14 (block P1): a host; disjoint nonempty X, Y;
h_{iy} = 1 if iy is red; g_y = (1/|X|) sum_i h_{iy}; pi_i = (1/|Y|) sum_y h_{iy}; d = d_R(X, Y); w > 0, 0 < beta < 1,
r > w, s = beta r > 1; H_c(X, Y) = (E_Y (g_y - c)_+^s)^{1/s}; Phi_c(X, Y) = |X|^w |Y| H_c(X, Y)^r; maximal = one-sided
maximal; u_y = g_y - c, H = H_c(X, Y); BB a simple graph on V, B_i = {j in X : ij in BB}, q_i = |B_i|/|X|, R_i, Y_i the
red neighbourhoods of i in X and in Y, b_i(y) the red density from B_i to y; tests (2) (fails blue) and (3) (fails
shifted-red) as in P1.2; m_i = sum_{y in Y_i} u_y^s / sum_{y in Y} u_y^s; a_y = u_y/H.

## Statement

**Proposition QR.** Let 0 < p, mu, beta < 1, w > 0 and x > p (1 - mu)^w. For every eta, tau > 0 and every r > w with
s = beta r > 1 and (1 - beta)^{1/s} >= 1/2, there is a configuration (a host, BB = its blue graph, disjoint nonempty X,
Y, a real c with |c - p| <= eta) such that: (i) g_y > c on Y; (ii) (X, Y) is maximal for Phi_c; (iii) every v in X has
q_v in (0, mu) and fails blue; (iv) every v in X fails shifted-red. Moreover, for some kappa > 0 depending only on
(p, mu, w, x): for every v in X and all nonempty T in B_v, Y'' in Y, Phi_c(T, Y'') <= e^{-kappa} mu^w Phi_c(X, Y); and
for every v in X and all nonempty T in R_v, Y'' in Y_v, Phi_c(T, Y'') <= e^{-kappa} x Phi_c(X, Y).

**Consequence (scope).** Every local-step statement about ARBITRARY maximal pairs of the form of Theorem 3.4, Lemma 4.5
or Lemma 4.5' (Section 6.10), with these two moves, any of their sub-pairs (Observation 2 of ramsey-lemma) and this
potential, is false at every x > p (1 - mu)^w. So a control certified through any such statement (Lemma C, Lemma D,
level (ii), Conjecture S, or any future sharpening of the same kind) has a = -log x >= a_rand := -log(p (1 - mu)^w).
The host built below is not outcome-free (it has red cliques of size about log N), so the barrier says nothing about
arguments that use outcome-freeness, the stopping rule, other moves or iterated moves.

**Sanity remark (referee item 12).** CERT(p, mu, w, beta, x) >= 0 whenever x >= p (1 - mu)^w: mu lies in F
(A(mu) <= 0 < -log p), M(mu) = B(mu) = 0, and the constant choice q = mu gives CERT >= int_0^1 w mu (1 + log t) dt = 0.
So QR is consistent with Theorem 3.4, and a > a_rand on every certified cell (min gap 0.0006, median 0.073; root-like
control p = 1/2, mu = 0.4005, w = 0.4629: a = 1.1098, a_rand = 0.9300) is forced by CERT itself (every cell of ctltable2.npz is a Lemma C / CERT cell; for a cell certified
through Lemma D instead, phi = 0, eta = 0 and q = mu give V_A >= 0 when x >= p (1 - mu)^w), not independent
evidence. What QR adds is that no sharpening of the envelope, of any kind covered by the scope above, can cross a_rand.

## Proof

Choices. Fix q0 in (0, mu) with p (1 - q0)^w < x, then kappa in (0, 1] with
    p (1 - q0)^w <= x e^{-4 kappa}   and   q0^w <= mu^w e^{-4 kappa}                                              (K)
(decreasing kappa keeps (K)). Put h = min{eta, p/2, (1 - p)/2}, c = p - h, C := max{1/2, mu/(2 (1 - mu))}, and fix
theta1 in (0, min{kappa/(8 C), kappa beta p/100}] and theta = theta1/r. Put eps := min{theta1 kappa/8, kappa (1 - mu)/(8 w)}.
The sizes are N = |X0| = M = |Y0| -> infinity; "w.h.p." is as N -> infinity with everything else fixed.

The random host. V = X0 ⊔ Y0. Each X0-Y0 edge is red with probability p; each X0-internal edge is blue with probability
q0; the Y0-internal edges are coloured at random (any rule independent of the rest); all independently. BB = the blue
graph.

Step A (the maximal pair; the X0-Y0 colouring only). Let (X, Y) maximise Phi_c over nonempty X in X0, Y in Y0, ties broken
by a fixed order of the pairs (so (X, Y) is a function of the X0-Y0 colouring). It is maximal. W.h.p.:
 (A1) |X| >= alpha N and |Y| >= gamma M, for alpha, gamma > 0 depending only on (r, h, theta1, w, p);
 (A2) h (1 - theta) <= H <= h (1 + 3 theta) and c < d <= p + 3 theta h;
 (A3) H_c(X', Y') <= h (1 + 3 theta) for all X' in X0, Y' in Y0 with |X'| >= alpha' N, |Y'| >= gamma' M (alpha' <= alpha,
      gamma' <= gamma fixed below);
 (A4) all but K columns y of Y0 have g^{X}_y < p + theta h, where K = ceil(2/(theta^2 h^2 min(alpha, alpha'))) is fixed.
Proof. (a) Every column of Y0 has density from X0 at least p - theta h (Hoeffding, union over M columns, log M = o(N)), so
Phi_0 := Phi_c(X0, Y0) >= N^w M (h (1 - theta))^r. (b) Let t = theta h and a = min(alpha, alpha'). For a fixed X' with
|X'| >= a N the column densities g^{X'}_y are independent with Pr(g^{X'}_y >= p + t) <= e^{-2 t^2 a N}; the probability
that some such X' has at least K columns with g^{X'}_y >= p + t is at most exp(N log 2 + K log M - 2 t^2 a N K) <=
exp(N log 2 + K log N - 4 N) -> 0. So w.h.p. every such X' (in particular X, once (A1) holds) has at most K such columns,
which is (A4), and for |Y'| >= gamma' M: H_c(X', Y')^s <= (h + t)^s + (K/(gamma' M))(1 - c)^s, whence
H_c(X', Y') <= h (1 + 3 theta) for N large: (A3). (c) A sub-pair with |X'| < alpha N has Phi_c <= (alpha N)^w M (1 - c)^r <
Phi_0 when alpha^w ((1 - c)/(h (1 - theta)))^r < 1, and one with |Y'| < gamma M has Phi_c <= N^w gamma M (1 - c)^r < Phi_0
when gamma ((1 - c)/(h (1 - theta)))^r < 1; fix such alpha, gamma. Since Phi_c(X, Y) >= Phi_0: (A1), H^r >= Phi_0/(|X|^w |Y|)
>= (h (1 - theta))^r, and H <= h (1 + 3 theta) by (A3). By Lemma 3.1 every u_y >= (1 - beta)^{1/s} H > 0, so d > c and
(i) holds; E_Y u_y <= H gives d <= c + H <= p + 3 theta h. (ii) holds by construction. []

Step B (the blue graph, conditionally on the X0-Y0 colouring). (X, Y) is a function of the X0-Y0 colouring, which is
independent of BB; conditionally, BB on X is G(|X|, q0) and the h_{jy} (j in X, y in Y) are fixed. W.h.p.:
 (B1) |q_v - q0| <= eps q0 for every v in X (Chernoff, union over |X| <= N rows);
 (B2) |b_v(y) - g_y| <= theta h/8 for every v in X and y in Y.
Proof of (B2). With xi_j = 1[j in B_v] independent Bernoulli(q0) (j != v), sum_{j in B_v}(h_{jy} - g_y) = sum_{j != v}
(xi_j - q0)(h_{jy} - g_y) - q0 (h_{vy} - g_y); Hoeffding bounds the first sum by t'|X| with probability >= 1 - 2 e^{-2 t'^2 |X|};
take t' = theta h q0/32 and a union over |X||Y| <= N M pairs. Dividing by |B_v| >= q0 |X|/2: |b_v(y) - g_y| <=
2 (t' + 1/|X|)/q0 = theta h/16 + o(1) <= theta h/8. []
By (B1) and (K), q_v <= q0 e^{eps} <= q0 e^{kappa/(8 w)} <= mu e^{-4 kappa/w + kappa/(8 w)} < mu for every v; so no row has
q_v > mu + tau, and q_v > 0.

Step C ((iii): every row fails blue). u_y >= H/2 >= h (1 - theta)/2 >= h/4, so by (B2) b_v(y) - c <= u_y + theta h/8 <=
u_y (1 + theta/2), and sum_y (b_v(y) - c)_+^s <= (1 + theta1/(2 r))^{beta r} sum_y u_y^s <= e^{theta1 beta/2} sum_y u_y^s.
By (B1) and (K), (mu/q_v)^{w beta} >= (mu/q0)^{w beta} e^{-w beta eps} >= e^{beta (4 kappa - kappa/8)} > e^{theta1 beta/2}.
So (2) holds at every v in X. []

Step D' (uniform row statistics; replaces the Markov step of v1). W.h.p.:
 (U1) every v in X0 has |deg_R(v, Y0)/M - p| <= N^{-1/3} (Hoeffding, union over N rows);
 (U2) (|X|/N)^w (|Y|/M) >= Phi_0/(N^w M H^r) >= ((1 - theta)/(1 + 3 theta))^r >= e^{-5 theta1}, so |Y0 \ Y| <= 5 theta1 M and,
      by (U1), |pi_v - p| <= 6 theta1 + o(1) for EVERY v in X;
 (U3) by (A4) all but K columns of Y have u_y < h (1 + theta), hence a_y^s <= ((1 + theta)/(1 - theta))^s <= e^{3 theta1};
      the K exceptional columns carry total weight at most (K/|Y|)((1 - c)/(h (1 - theta)))^s = o(1) relative to
      sum_y u_y^s (which is >= |Y| (H/2)^s). As E_Y a^s = 1 by definition of H,
      m_v = E_Y[a_y^s h_{vy}] <= pi_v + E_Y (a_y^s - 1)_+ <= pi_v + 4 theta1 + o(1) for EVERY v in X.
So every v in X has m_v <= p + 10 theta1 + o(1) and pi_v >= p - 6 theta1 - o(1).

Step D ((iv): every row fails shifted-red). For y in Y_v, (1 - q_v) u_y - q_v (b_v(y) - g_y) <= (1 - q_v) u_y
(1 + theta q_v/(2 (1 - q_v))) <= (1 - q_v) u_y (1 + C theta) (u_y >= h/4, (B2), q_v < mu). So the left side of (3) is at most
(1 - q_v)^s e^{theta1 beta C} m_v sum_y u_y^s, and (3) at v follows from
    (1 - q_v)^{w beta} m_v e^{theta1 beta C} < x^beta pi_v^{1 - beta}.
By (B1), (1 - q_v)^w <= (1 - q0)^w e^{w eps q0/(1 - q0)} <= (1 - q0)^w e^{kappa mu/8} (q0/(1 - q0) <= mu/(1 - mu)). With
Step D', the left side over the right side is at most
    [(1 - q0)^w e^{kappa mu/8} p/x]^beta (1 + 10 theta1/p + o(1)) (1 - 6 theta1/p - o(1))^{-(1 - beta)} e^{theta1 beta C}
    <= e^{-beta (4 kappa - kappa/8)} e^{17 theta1/p + o(1)} e^{kappa beta/8}
and theta1 <= kappa beta p/100, theta1 C <= kappa/8 make this at most e^{-beta (4 kappa - kappa/2) + 0.16 kappa beta} < 1. []

The sub-pair strengthening. Choose alpha' <= alpha, gamma' <= gamma with alpha'^w ((1 - c)/(h (1 - theta)))^r <= e^{-kappa}
min(x, mu^w) and gamma' ((1 - c)/(h (1 - theta)))^r <= e^{-kappa} min(x, mu^w). Let v in X and T in B_v, Y'' in Y nonempty. If
|T| < alpha' N or |Y''| < gamma' M, Phi_c(T, Y'')/Phi_c(X, Y) <= Phi_c(T, Y'')/Phi_0 <= e^{-kappa} mu^w directly. Otherwise
(A3): Phi_c(T, Y'')/Phi_c(X, Y) <= (|T|/|X|)^w ((1 + 3 theta)/(1 - theta))^r <= q_v^w e^{5 theta1}
<= mu^w e^{-4 kappa + kappa/8 + 5 kappa/8} <= e^{-kappa} mu^w. For T in R_v, Y'' in Y_v: the small case as before; otherwise
Phi_c(T, Y'')/Phi_c(X, Y) <= (|T|/|X|)^w (|Y''|/|Y|) e^{5 theta1} <= (1 - q_v)^w pi_v e^{5 theta1}
<= x e^{-4 kappa + kappa/8} (1 + 7 theta1/p) e^{5 theta1} <= e^{-kappa} x. []

The shift c'. Lemma 4.5 / 4.5' test RED at c' = c - Delta for every Delta above an explicit minimum
Delta_min = O(1/|X|); a counterexample needs only Delta = Delta_min, and H_{c'} <= H_c + Delta (Minkowski) changes every
ratio above by (1 + O(1/(N h)))^r = 1 + o(1). For Lemma 4.5' also its blue-degree hypothesis on the sets T_v must hold:
T_v is ranked by V, a function of the X0-Y0 colouring (fixed tie-break), so |B_i ∩ T_v| ~ Bin(|T_v| - 1, q0) given that
colouring and concentrates below cap |T_v| for the finitely many v in its grid. (ZBS's own induction (P2.4) uses
Delta = delta/(n(n - 1)), which stays fixed as N grows; for that step run the construction with red probability
p1 = c_n + h, where p1 (1 - q0)^w <= x e^{-4 kappa}, and require r Delta/h <= kappa/2.)

Steps A-D give (i)-(iv) at every row, for this r and |c - p| <= eta, for all large N; the margins are e^{-kappa}. []

Optional hardenings (free; the tests do not see them): red probability p + h/2 with c = p - h/2, theta1 <= h/12 and h small
enough that (p + h/2)(1 - q0)^w <= x e^{-4 kappa} gives d >= p + h/2 - 6 theta1 >= p (by (U2)), covering
variants that assume d_R(X, Y) >= p; with theta = theta_N -> 0 the construction works for every fixed r > w with s > 1.

## Remarks

1. The configurations are quasi-random: the red step keeps the column excess H and loses only the sizes (|X| by 1 - q0,
   |Y| by p). So the gap a - a_rand (0.18 at the root control) is AT MOST the room any sharper envelope of the scoped kind
   can use.
2. Beating a_rand needs a different potential, other moves, iterated moves, or arguments that use outcome-freeness or
   the stopping rule (the exclusions of the scope sentence).
3. Between a_rand and the certified a (p (1 - mu)^w > x > x_cert) the question is open; see NOTES.md (22:xx) for the
   symmetric-split adversary (90% of the gap, realisability open) and the Gaussian-cap construction (about 60% of the gap,
   a limit construction, not yet refereed).
4. Float (not part of the proposition): banks whose controls all sit at a_rand reach z ~ 1.0869 (e^z ~ 2.965) in the
   realisable model with ratio range [1/20, 20] (1.0901 with [1/5, 5]); NOTES.md 21:4x.
