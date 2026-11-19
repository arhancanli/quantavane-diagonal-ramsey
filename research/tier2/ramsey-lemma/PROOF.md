# Self-similar local step: statements and proofs (DRAFT, 18 Nov 2026, started 10:3x +04)

Status: DRAFT. Nothing here is claimed until a full proof is written, every numeric part is certified by two
programs with tampers refused, and a fresh-context referee has read it. Numbering below is ours; ZBS = Zhao,
Booth-Clibborn, Schwahn (preprint/main.tex @ c2875f33, printed numbering: Lemma 3.1 columns, Lemma 3.2 rows,
Theorem 3.4 sharp envelope, Proposition 3.5 limit form with Steps 1-8, Theorem 4.2 finite-host closure, Lemma 4.5
local alternative, Lemma 4.3 pages, Lemma 4.4 books). Notation as in ZBS Section 3: N = |X|, u_y = g_y - c,
H = H_c(X,Y), a_y = u_y/H, nu_y = a_y^s / M, V_v, B_v (blue neighbourhood of v in X), q_v = |B_v|/N.

## S1. Sub-pair alternatives (exact)

Lemma S1. Fix sigma in (0, 1]. In the induction (I_n) of the proof of ZBS Theorem 4.2 (shifts c_n = p - delta/n,
Phi_n = Phi_{c_n}, threshold C^{w+1} lambda^{-k} y^{-l} mu^{-w t}), the inductive step at a maximal pair (X, Y) also
succeeds (produces an outcome) in each of the following cases:
 (RED')  some v in X and some nonempty T in R_v, Y'' in Y_v with Phi_{c_{n-1}}(T, Y'') >= x Phi_n(X, Y);
 (BLUE') some v in X and some nonempty T in B_v, Y'' in Y with Phi_{c_n}(T, Y'') >= mu^w Phi_n(X, Y);
 (BOOK_S) some S in X with |S| >= sigma |X| in which at least R(k, m_n(sigma)) vertices have at least cap |S| blue
          neighbours in S, with the constants of S3.7 (referee 3, 12:3x: the version first written here was short of
          Lemma 4.4's hypotheses): sigma >= v_1 with the scale grid fixed first, r chosen so that D_r/v_1 <
          min{1/4, (cap - theta)/2}, h_1 = cap - theta - D_r/v_1, b_n = max{1, ceil((r log(n^2/delta) + w log(2/v_1))
          / (w log(theta/mu)))}, m_n = ceil(2 b_n/h_1), and N >= v_1^{-1} max{4 m_n, 2 m_n/h_1} so that Lemma 4.4's
          D <= 1/4, m/|S| <= 1/4 and D + m/|S| + b/m <= cap - theta all hold for |S| >= v_1 N.
Proof. (RED'): Phi_{n-1}(T, Y'') >= x Phi_n(X, Y) >=
C^{w+1} lambda^{-(k-1)} y^{-l} mu^{-wt} because x > lambda. (I_{n-1}) is a statement about EVERY disjoint nonempty pair
whose potential clears the threshold, so it applies to (T, Y'') with targets (k-1, t): a red K_{k-1} in T cup Y''
together with v is a red K_k in X cup Y, since v is red to every vertex of R_v and of Y_v; a blue K_t in T is in X; a
blue K_l in Y'' is in Y. (No condition q_v <= cap is needed: in ZBS that condition only serves the identity behind
the shift adjustment of Lemma 4.5, which a direct potential comparison does not use.)
(BLUE'): Phi_{n-1}(T, Y'') >= Phi_n(T, Y'') >= mu^w Phi_n(X, Y) >= C^{w+1} lambda^{-k} y^{-l} mu^{-w(t-1)}; (I_{n-1})
with targets (k, t-1); a blue K_{t-1} in T together with v (blue to all of B_v) is a blue K_t in X; the other outcomes
are outcomes.
(BOOK_S): ZBS Lemma 4.4 is stated for an arbitrary vertex set; apply it to S with page set G cap S, where
G = {v : pi_v >= c_n}. By ZBS Lemma 4.3, |X \ G| <= D_r |X|, so 1 - |G cap S|/|S| <= D_r/sigma. It gives (or a red K_k
in S) a blue clique S_b of b = b_n vertices and pages P in G cap S, all S_b-P edges blue, |P| >= theta^b |S|/2.
If b >= t, S_b contains a blue K_t. Otherwise H_{c_{n-b}}(P, Y) >= c_n - c_{n-b} >= delta/n^2 (the columns of P have
average red density >= c_n), so
  Phi_{n-b}(P, Y) / Phi_n(X, Y) >= (|P|/|X|)^w (delta/n^2)^r >= (sigma/2)^w theta^{wb} (delta/n^2)^r >= mu^{wb}
by the choice of b_n (sigma >= v_1), using Phi_n(X, Y) <= |X|^w |Y|. (I_{n-b}) with targets (k, t-b) applies to (P, Y); a blue
K_{t-b} in P together with S_b is a blue K_t in X. b_n, m_n (independent of sigma) are still O(log n), so ZBS's constant K_1
stays finite and the rest of the proof of Theorem 4.2 is unchanged. []
Consequence used below: in the limit argument (ZBS Proposition 3.5) we may assume that every sub-pair test fails and
that, for the sets S = T_v of the fixed scale grid (the only sets Theorem 4.2' tests with BOOK_S), all but o(|S|)
rows of S have fewer than (mu + o(1))|S| blue neighbours in S.

## S2. Blue-neighbourhood identity (exact, any r)

With e_j(y) = (h_{jy} - g_y)/u_y: V_j - 1 = E_nu e_j and E_nu Z_i = avg_{j in B_i} (V_j - 1).
Proof. nu_y = u_y^s / (M H^s), so V_j - 1 = E_Y[u_y^{s-1}(h_{jy} - g_y)]/H^s = sum_y nu_y e_j(y); and
b_i(y) = avg_{j in B_i} h_{jy}. []
The same identity holds for any pair (T, Y) with its own column measure nu_T, column densities g^T, and
B_i cap T in place of B_i.

## S3. Near-maximal subsets inherit the local step (limit form) -- SUPERSEDED by S3G (global coordinates); kept as history

NOTE (12:5x): nothing in Theorem A, Theorem S, S6 or S7 depends on this section; they use S3G. The text below is the
first, local-coordinate version, kept for the record of how the flatness question arose and was closed.

Setting. A sequence of configurations as in ZBS Proposition 3.5 (maximal pairs (X, Y) for Phi_c, r -> infinity,
c -> p, H bounded, d_R(X, Y) >= p - o(1)) in which every test of S1 fails: (RED') at every v (shift c' = c - Delta as
in ZBS Lemma 4.5), (BLUE') at every v with q_v > 0, and (BOOK_S) for the finitely many proportions used. Fix v in
(0, 1], let T = T_v be the ceil(vN) rows with the largest V_j, and suppose eta := log Phi_c(X,Y) - log Phi_c(T,Y)
stays below some eta_bar < log(p/x). Put x' = x e^eta, mu' = mu e^{eta/w}.

Claim. For all but o(|T|) rows i of T, with q'_i = |B_i cap T|/|T| and zeta'_i = r E_{nu_T} Z^T_i
(Z^T_i(y) = (b^T_i(y) - g^T_y)/u^T_y, b^T_i = red density from B_i cap T to y):
 (i)  q'_i <= mu + o(1), and q'_i lies within o(1) of F_p(x', mu') (ZBS's feasible set at x', mu'); in particular
      q'_i >= a(x', mu') - o(1);
 (ii) zeta'_i <= M'(q'_i) + o(1), M' = ZBS's M at (p, mu', w, beta, x');
 (iii) sum_{i in T} q'_i zeta'_i = sum_{s in T} q'_s phi'_s exactly, phi'_s = r (V^T_s - 1) (S2 inside T).
Proof. (iii) is S2 for the pair (T, Y) and symmetry of the blue graph inside T. For (i)-(ii):
(a) The tests are ZBS's tests for the pair (T, Y) at (x', mu'). Blue: Phi(B_i cap T, Y) < mu^w Phi(X, Y) =
    mu'^w Phi(T, Y), i.e. q'^w H_c(B_i cap T, Y)^r < mu'^w H_c(T, Y)^r, which raised to the power beta is ZBS (eq:B) for
    (T, Y) with mu'. Red: Phi_{c'}(R_i cap T, Y_i) < x e^eta Phi_c(T, Y); counting red neighbours of y in Y_i inside
    T = {i} cup (B_i cap T) cup (R_i cap T) gives ZBS's identity of Lemma 4.5 with (X, q_v, b_v) replaced by
    (T, q'_i, b^T_i), and the bracket sigma Delta - (1-c)/|T| is >= 0 once |T| (1 - cap) - 1 >= n(n-1)/delta; this
    yields ZBS (eq:R) for (T, Y) at x'.
(b) ZBS Steps 1 and 6 for one row use only these two failures, Jensen on the two cells of nu_T, and the limits
    m^T_i = nu_T(Y_i) -> d', pi_i -> d' with d' >= p. These limits are the concentration step below.
(c) Step 5 inside T: at q' = 0 the red failure reads m^T_i < x'^beta pi_i^{1-beta}, impossible when d' > x'
    (eta < log(p/x)); small q' > 0 is excluded as in ZBS. Step 6 then gives q'_i in F_{d'}(x', mu') and (ii) with
    M'_{d'}; Step 8's monotonicity in d (d' >= p) replaces d' by p.
(d) The upper bound q'_i <= mu + o(1) is (BOOK_S) with S = T.

Concentration inside T (the step that makes (i)-(ii) hold for rows of T without any flatness assumption).
Let T = T_v, delta = |D|/|T| for D in T. With W_D(y) = (g^T_y - g^D_y)/u^T_y one has
  g^{T\D}_y - c = u^T_y (1 + (delta/(1-delta)) W_D(y)),  E_{nu_T} W_D = avg_{i in D} (1 - V^T_i),
so by Jensen (H_{T\D}/H_T)^r >= (1 + (delta/(1-delta)) E_{nu_T} W_D)^r (exponent r; referee). If every i in D has
V^T_i <= 1 - theta/r, then Phi(T\D, Y)/Phi(T, Y) >= (1-delta)^w (1 + delta theta/((1-delta) r))^r, while
Phi(T\D, Y) <= Phi(X, Y) = e^eta Phi(T, Y). Hence delta theta/(1-delta) <= eta - w log(1-delta) + o(1): for theta = theta_r -> infinity
slowly, all but o(|T|) rows of T have V^T_i >= 1 - theta_r/r. Column side: Phi(T, Y') <= e^eta Phi(T, Y) for every
Y' in Y gives P_Y(a^T >= t) <= e^eta t^{-r}, so ZBS Step 2's estimates P_+ = O(1/r), |m^T_i - f^T_i| <= 2 P_+ hold for
(T, Y) with an extra factor e^eta; with f^T_i = H_T V^T_i + c J_T and avg_{i in T} f^T_i = H_T + c J_T this gives
m^T_i -> lim (c + H_T) for all but o(|T|) rows of T. ZBS (C2) gives pi_i -> d for all but o(N) rows. And H_T/H -> 1
because (H_T/H)^r = v^{-w} e^{-eta} exactly; moreover eta lies in [0, w log(1/v)] automatically (avg_T V >= 1 gives
H_T >= H). Columns with u^T_y <= 0 carry no nu_T-mass; restricting the sums in (eq:B), (eq:R) to supp nu_T only makes
the failure inequalities easier, so nothing is lost (referee). So the
red density of row i on Y_i, measured by nu_T and by counting, has the same limit d >= p for almost all i in T,
which is what ZBS Steps 1, 5, 6 need for one row relative to (T, Y). Rows OUTSIDE T are not covered by this argument
(their nu_T-densities may differ from d by O(1)); the model therefore imposes the within-T conditions only on rows
of T ("version A").

Flatness (HISTORICAL; CLOSED by S3G and S6: working in global coordinates, no conversion from inside-T drifts is ever
made, and Corollary S3.5' pins Psi_j(T) -> avg_T phi row by row, which defeats the escape described here; three
referees, NOTES 11:5x and 12:3x). The original paragraph: (i)-(iii) are statements about drifts INSIDE T,
phi'_s = r (V^T_s - 1). Using them with GLOBAL drifts (the model's (G), (L) and block symmetry) needs Hoelder equality
for T (psi_T constant nu-a.e.). Without it: the exact row formula is phi'_s = phi_s - E_nu[rho~_T psi_T] + r E_nu[(rho~_T - 1) e_s] with the tilt
rho~_T = (1 + psi_T/r)^{s-1} / E_nu(1 + psi_T/r)^s (referee; checked to 3e-14 by scratch chk_chi.py; my earlier
formula with rho_T = d nu_T/d nu errs by up to 8 per row, though it averages to 0 over T);
only KL(nu || nu_T) = beta J_v is controlled (Pinsker: ||rho_T - 1||_1 <= sqrt(2 beta J_v)); the L2 bound I sketched is
not available; the averaged sign (+ beta Var psi_T) does not reach the per-row (G) or the q'-weighted (L). The
adversary has a first-order escape: make T sparser on the binding rows' red neighbourhoods; since such a row's blue
neighbourhood profile is two-valued (A on Y_j, C off it; A - C = 1.8 to 3.2 at the root's binding q), the inside-T drift
of its neighbourhood drops by about (A - C) beta epsilon Cov(X, h_j) (psi_T = m + epsilon X), first order in epsilon,
at drift cost O(epsilon^2). So the conversion to global drifts must carry J_v and these row corrections as adversary
variables with valid bounds. Level (i) (S3(i) + S4 in GLOBAL drift order + ZBS's per-row bound) does not use the
conversion and is unaffected.

## S3G. Sub-pair tests inside any row set, in GLOBAL coordinates (rigorous; S3/flatness helper, 18 Nov 11:2x-)

Everything here is measured with the GLOBAL column measure nu and stated in GLOBAL drifts phi_i. No near-maximality of
T, no measure nu_T, no concentration inside T, no joint maximality and no flatness are used. This replaces the lane's
S3 (local coordinates) for every use in Theorem S; S6 below explains why the flatness hypothesis (F) is then not needed.

Setting. One configuration: a host, disjoint nonempty X, Y, (X, Y) maximal for Phi_c in ZBS's (one-sided) sense with
H > 0; w > 0, 0 < beta < 1, r > w, s = beta r > 2, 0 < c < 1. By ZBS Lemma 3.1 every u_y > 0. As in ZBS:
a_y = u_y/H, nu_y = a_y^s/M, V_i, and phi_i = r(V_i - 1); ZBS Lemma 3.2 gives phi_i >= -w for every i.
For i in X put e_i(y) = (h_iy - g_y)/u_y. For nonempty S in X put g^S_y = avg_{i in S} h_iy and
  psi_S = r (g^S - g)/u = r avg_{i in S} e_i.
By S2, E_nu e_i = V_i - 1, so E_nu psi_S = avg_S phi; |S| psi_S is additive over disjoint S; psi_X = 0.
Fix nonempty T in X, n_T = |T|, v = n_T/N. For j in X (inside or outside T): B^T_j = B_j cap T, R^T_j = R_j cap T,
q'_j = |B^T_j|/n_T, sigma'_j = |R^T_j|/n_T (= 1 - q'_j - 1/n_T if j in T, = 1 - q'_j if j not in T), b^T_j(y) and
rho^T_j(y) the red densities from B^T_j and from R^T_j to y, Z^T_j = (b^T_j - g)/u (Z^T_j := 0 if B^T_j is empty);
Y_j = red neighbourhood of j in Y, pi_j = |Y_j|/M, m_j = nu(Y_j) = E_nu h_j, and
  P_j(T) = E_nu[psi_T h_j],   Psi_j(T) = P_j(T)/m_j  (the nu-average of psi_T over the red cell of j).
Tests (instances of S1's (BLUE') and (RED'), shift c' = c - Delta, Delta > 0):
  BLUE_T(j): Phi_c(B^T_j, Y) >= mu^w Phi_c(X, Y);    RED_T(j): Phi_{c'}(R^T_j, Y_j) >= x Phi_c(X, Y).
T = X gives ZBS's tests.

### Proposition S3.1 (exact, finite r)
Let j in X with m_j > 0 and sigma'_j > 0, and if j in T assume Delta n_T sigma'_j >= 1 - c.
 (a) [identity] If q'_j > 0: r E_nu Z^T_j = avg_{i in B^T_j} phi_i.
 (b) [blue] If q'_j > 0 and BLUE_T(j) fails: E_nu (1 + Z^T_j)_+^s < U^T_j := (mu/(q'_j v))^{w beta}.
 (c) [red] If RED_T(j) fails: with W_j = (1 - q'_j) + psi_T/r - q'_j Z^T_j,
       E_nu[h_j (W_j)_+^s] < (1 - q'_j)^{s - w beta} x^beta v^{-w beta} pi_j^{1 - beta}.
 (d) [two cells] If q'_j > 0, m_j < 1 and both tests fail: with z_in = E_nu[Z^T_j | Y_j], z_out = E_nu[Z^T_j | Y \ Y_j],
       z_in > L^T_j,   q'_j r L^T_j = (1 - q'_j) r (1 - e^{l^T_j/r}) + Psi_j(T),
       l^T_j = log x - w log v - w log(1 - q'_j) + beta^{-1}[(1 - beta) log pi_j - log m_j],
       m_j (1 + z_in)_+^s + (1 - m_j)(1 + z_out)_+^s < U^T_j,
     hence avg_{i in B^T_j} phi_i <= r S(m_j, U^T_j, L^T_j), where S(m, U, L) = sup{m z1 + (1-m) z2 : z1 >= L,
     m (1+z1)_+^s + (1-m)(1+z2)_+^s < U} is ZBS's two-cell supremum (Step 1, eq. (twocell)).
 (e) [no blue neighbours in T] If q'_j = 0 and RED_T(j) fails: m_j (1 + Psi_j/r)_+^s < x^beta v^{-w beta} pi_j^{1-beta}.
Proof. (a) b^T_j - g = avg_{i in B^T_j}(h_i - g), so Z^T_j = avg_{i in B^T_j} e_i; apply S2.
(b) For any nonempty B in X, Phi_c(B, Y)^beta = |B|^{w beta} M^beta E_Y (b - c)_+^s (H_c^r raised to beta is H_c^s), and
Phi_c(X, Y)^beta = N^{w beta} M^beta H^s. So failure reads (q'_j v)^{w beta} E_Y (b^T_j - c)_+^s < mu^{w beta} H^s. Since
b^T_j - c = u (1 + Z^T_j) with u > 0 and nu_y = u_y^s/(M H^s), E_Y (b^T_j - c)_+^s = H^s E_nu (1 + Z^T_j)_+^s.
(c) For y in Y_j, count the red neighbours of y in T, the disjoint union of B^T_j, R^T_j and (if j in T) {j}:
n_T g^T_y = |B^T_j| b^T_j(y) + |R^T_j| rho^T_j(y) + [j in T]. Solving for rho and using c' = c - Delta,
  sigma'(rho^T_j(y) - c') = (g^T_y - c) - q'(b^T_j(y) - c) + E_j,   E_j = sigma' Delta - [j in T](1 - c)/n_T >= 0.
(For j in T: sigma' rho = g^T - q' b^T - 1/n_T and sigma' = 1 - q' - 1/n_T; expand.) Since g^T - c = u (1 + psi_T/r) and
b^T_j - c = u (1 + Z^T_j), the first two terms equal u W_j, so (sigma'(rho - c'))_+ >= u (W_j)_+ on Y_j. Failure of
RED_T(j) raised to beta: |R^T_j|^{w beta} |Y_j|^{beta - 1} sum_{Y_j} (rho - c')_+^s < x^beta N^{w beta} M^{beta - 1} sum_Y u^s,
i.e. sum_{Y_j} (rho - c')_+^s < x^beta (sigma' v)^{-w beta} pi_j^{1-beta} sum_Y u^s. Multiply by sigma'^s, use the
previous line, divide by sum_Y u^s = M H^s: E_nu[h_j (W_j)_+^s] < x^beta sigma'^{s - w beta} v^{-w beta} pi_j^{1-beta};
finally sigma' <= 1 - q' and s - w beta > 0.
(d) t -> t_+^s is convex, so Jensen on the red cell (nu-mass m_j) gives m_j ((1 - q') + Psi_j/r - q' z_in)_+^s <=
E_nu[h_j (W_j)_+^s]. With (c), (s - w beta)/s = 1 - w/r and beta/s = 1/r:
(1 - q') + Psi_j/r - q' z_in < (1 - q') e^{l^T_j/r}, which rearranges to z_in > L^T_j. Jensen on both cells applied to
(b) gives the second inequality. E_nu Z^T_j = m_j z_in + (1 - m_j) z_out, so (a) gives the last claim.
(e) As (c) with q' = 0, W_j = 1 + psi_T/r, then Jensen on the red cell. []

### Limit functions
For v in (0, 1], d in (0, 1), q in [0, 1) and Psi real put (q log q := 0 at q = 0)
  a_{v,d}(q) = (1 - q)[log(d v^w / x) + w log(1 - q)],
  G_{v,d}(q, Psi) = q log d + beta (a_{v,d}(q) + Psi) - beta w q log(mu/(q v)),
  D_{v,d} = {(q, Psi) : 0 <= q < 1, G_{v,d}(q, Psi) <= 0}.
For q > 0 put A = (a_{v,d}(q) + Psi)/q, B = w log(mu/(q v)) (so G = q (log d + beta A - beta B)), and
  M^T_{v,d}(q, Psi) = B if A <= B;  d A + ((1-d)/beta) log((e^{beta B} - d e^{beta A})/(1 - d)) if A > B and
  d e^{beta A} < e^{beta B};  -infinity otherwise;   H^T_{v,d}(q, Psi) = q M^T_{v,d}(q, Psi);
and H^T_{v,d}(0, Psi) = 0 on D_{v,d}. For v = 1, Psi = 0 these are ZBS's A_d, B, M_d and (G <= 0) the closure of F_d.
Relation to the flat model (direct substitution): for Psi = -w log v - eta,
  A = A_d(q; x e^eta) - w log v - eta,   B = B(q; mu e^{eta/w}) - w log v - eta,
  M^T_{v,d}(q, -w log v - eta) = M_d(q; x e^eta, mu e^{eta/w}) - w log v - eta,
  G_{v,d}(q, -w log v - eta) = G0_d(q) - beta eta,  G0_d(q) = q log d + beta (1-q) log(d (1-q)^w/x) - beta w q log(mu/q),
G0 being the lane's left-end function (code/extremal.py, with p -> d). So the q-section of D_{v,d} at
Psi = -w log v - eta is {q in [0,1) : G0_d(q) <= beta eta}, whatever v is. This set has no cap q <= mu e^{eta/w}, and
it can be nonempty when {G0_d < beta eta} is empty (tangency). The cap g <= mu is imposed separately (book case).
On {G0_d < beta eta} cap (0, mu] it is F_d(x e^eta, mu e^{eta/w}) cap (0, mu] (referee 12:xx).

### Lemma S3.2 (convexity and concavity)
 (i) G_{v,d} is jointly convex on [0, 1) x R, so D_{v,d} is closed and convex.
 (ii) H^T_{v,d} is jointly concave and upper semicontinuous on D_{v,d} (values in [-infinity, infinity)); for q > 0,
   H^T_{v,d}(q, Psi) = sup{d P + (1 - d) O : P >= a_{v,d}(q) + Psi,
                          q log(d e^{beta P/q} + (1 - d) e^{beta O/q}) <= beta w q log(mu/(q v))}   (*).
 (iii) At fixed (v, q, Psi), D_{v,d} shrinks and M^T_{v,d} decreases as d increases.
Proof. (i) q log d and Psi are linear; (1 - q) log(d v^w/x) is linear; w (1-q) log(1-q) has second derivative
w/(1-q) > 0; -beta w q log(mu/(qv)) = beta w q log q - beta w q log(mu/v) is convex.
(ii) Let K be the set of (P, O, q, Psi) with 0 < q < 1, P - Psi - a_{v,d}(q) >= 0 and
q log(d e^{beta P/q} + (1-d) e^{beta O/q}) - beta w q log(mu/(qv)) <= 0. The first function is concave (a convex).
(P, O, q) -> q log(d e^{beta P/q} + (1-d) e^{beta O/q}) is the perspective of the convex function
(P, O) -> log(d e^{beta P} + (1-d) e^{beta O}), hence jointly convex on q > 0, and the subtracted term is concave as in
(i). So K is convex, and (q, Psi) -> sup{d P + (1-d) O : (P, O, q, Psi) in K} is concave. It equals q M^T: with
P = q z1, O = q z2 the problem is q sup{d z1 + (1-d) z2 : z1 >= A, d e^{beta z1} + (1-d) e^{beta z2} <= e^{beta B}}. If
A <= B, (B, B) is feasible and optimal by Jensen (d e^{beta z1} + (1-d) e^{beta z2} >= e^{beta (d z1 + (1-d) z2)}). If
A > B, on the boundary z2 = beta^{-1} log((e^{beta B} - d e^{beta z1})/(1-d)) the objective has derivative
d (1 - e^{beta (z1 - z2)}) < 0 in z1 (there z1 > B > z2), so z1 = A is optimal when d e^{beta A} < e^{beta B}; when
d e^{beta A} >= e^{beta B} nothing with z1 >= A and z2 real is feasible. Upper semicontinuity on {q > 0}: the formula is
continuous where finite, and on {G = 0, q > 0} one has A > B (G = 0 and A <= B would force d >= 1) and M^T -> -infinity.
At q = 0: H^T <= q B = w q log(mu/(qv)) -> 0; conversely, every (0, Psi) in D is a limit of points (q, Psi - C q) of D
(C large) with A <= B, where H^T = w q log(mu/(qv)) -> 0. So H^T(0, .) = 0 on D is the upper semicontinuous hull, and
the closure of a concave function is concave. Closedness and upper semicontinuity are RELATIVE TO q < 1: extended by
-infinity, H^T is not usc at q = 1. Every use below restricts to D^mu_{v,d} = D_{v,d} cap {q <= mu}, which is closed
and convex, and on which H^T is usc, concave and bounded above by w mu/(e v) (referee 12:xx).
(iii) dG/dd = (q + beta (1-q))/d > 0. dA/dd = (1-q)/(q d) > 0; then ZBS Step 8's computation (dM/dd at fixed A <= 0,
dM/dA < 0 on the binding branch, continuity across the branches) applies verbatim. []

### Proposition S3.3 (one row in the limit)
Take a sequence of configurations as in the Setting with r -> infinity (beta, w, mu, x fixed), sets T with
n_T/N -> v in (0, 1], and rows j (inside or outside T) satisfying the hypotheses of S3.1, with both tests failing,
pi_j -> d and m_j -> d for some d in (0, 1), q'_j -> q in [0, 1) and Psi_j(T) -> Psi real. Then (q, Psi) is in D_{v,d}
(with G < 0 if q > 0), and
  limsup (1/N) sum_{i in B^T_j} phi_i <= v H^T_{v,d}(q, Psi),   while   (1/N) sum_{i in B^T_j} phi_i >= -w v q'_j.
Proof. Lower bound: phi_i >= -w. Write LHS_j = (1/N) sum_{B^T_j} phi_i = v q'_j avg_{B^T_j} phi_i.
Case q > 0 (so q'_j > 0 eventually). Here q'_j r L^T_j -> a_{v,d}(q) + Psi (because r(1 - e^{l/r}) -> -l, and
l^T_j -> log x - w log v - w log(1-q) - log d), so r L^T_j -> A, and U^T_j -> e^{beta B}. By (d), LHS_j <= v q'_j r S.
ZBS's formula (eq. (twocell)), t_U = U^{1/s}: if L <= t_U - 1 then S = t_U - 1 and r (t_U - 1) -> B. Otherwise the
strict two-cell problem is feasible only if Q_r := (U - m (1+L)^s)/(1-m) > 0, and S = m L + (1-m)(Q_r^{1/s} - 1).
Since (1 + L)^s = (1 + rL/r)^{beta r} -> e^{beta A}, Q_r -> Q := (e^{beta B} - d e^{beta A})/(1-d). If Q > 0,
r (Q_r^{1/s} - 1) -> beta^{-1} log Q and r S -> M^T. If Q = 0 then r (Q_r^{1/s} - 1) -> -infinity (for t <= 0,
e^t - 1 <= t e^t, and e^t - 1 -> -1 if t -> -infinity), so r S -> -infinity, contradicting LHS_j >= -w v q'_j: hence
Q > 0. If A < B the first branch holds eventually, if A > B the second, if A = B both limits equal B = M^T. So
limsup LHS_j <= v q M^T(q, Psi) = v H^T(q, Psi), and G < 0.
Case q = 0. If q'_j > 0: Jensen on (b) gives r E_nu Z^T_j < r(U^{1/s} - 1) <= b e^{b/r} with b = w log(mu/(q'_j v))
(e^t - 1 <= t e^t for t >= 0; if b <= 0 the bound is <= 0), so for r >= 2w,
LHS_j <= v w q'_j log(mu/(q'_j v)) (mu/(q'_j v))^{1/2} -> 0. For membership: the blue inequality on the red cell,
m (1 + z_in)^s < U, gives q' r z_in < q' b' e^{b'/r} with b' = w log(mu/(q'v)) - beta^{-1} log m_j, which -> 0 as
q' -> 0 (r >= 2w; ZBS Step 5's estimate C sqrt(q)(1 + log(1/q))); with z_in > L^T_j this gives a_{v,d}(0) + Psi <= 0,
i.e. (0, Psi) in D. If q'_j = 0: LHS_j = 0 and (e) gives s log(1 + Psi_j/r) < beta log(x v^{-w}) + (1-beta) log pi_j
- log m_j, whose limit is beta Psi <= beta log(x/(d v^w)) = -beta a_{v,d}(0). In both sub-cases the bound is
0 = v H^T(0, Psi). []

### Lemma S3.4 (L2 bounds; explicit; uses only ZBS's one-sided maximality)
 (i) For S in X with |S| = sigma N: E_nu (1 + psi_S/r)_+^s = (H_c(S,Y)/H)^s <= sigma^{-w beta}; hence
     nu(psi_S >= t) <= sigma^{-w beta} (1 + t/r)^{-s} for t > 0.
 (ii) If 0 < sigma < 1: psi_{X\S} = -sigma psi_S/(1 - sigma), and nu(psi_S <= -t) <= (1-sigma)^{-w beta}
     (1 + sigma t/((1-sigma) r))^{-s} for t > 0.
 (iii) E_nu psi_S^2 <= K2(sigma) 2 r^2/((s-1)(s-2)), K2(sigma) = sigma^{-w beta} + (1-sigma)^{2 - w beta} sigma^{-2}
     for 0 < sigma < 1 (for sigma = 1, psi_X = 0). K2 is bounded on [eps, 1/2] for every eps > 0, but if
     w beta > 2 it blows up as sigma -> 1 (referee 12:xx: K2(1) is NOT 0). As r -> infinity the factor
     2r^2/((s-1)(s-2)) -> 2/beta^2.
 (iv) With rho_beta = (1 - beta) r > 2 and K_beta = -log(1-beta)/beta: nu(a >= 1 + t) <= (1 + t)^{-rho_beta} (t > 0),
     a >= e^{-K_beta/r}, and E_nu (a - 1)^2 <= 2/((rho_beta - 1)(rho_beta - 2)) + K_beta^2/r^2 -> 0.
Proof. (i) H_c(S,Y)^s = E_Y (g^S - c)_+^s = E_Y[u^s (1 + psi_S/r)_+^s] = H^s E_nu (1 + psi_S/r)_+^s, and row maximality
Phi_c(S,Y) <= Phi_c(X,Y) reads sigma^w (H_c(S,Y)/H)^r <= 1; raise to beta; Markov on {psi_S >= t}.
(ii) sigma g^S + (1-sigma) g^{X\S} = g; apply (i) to X \ S. (iii) E psi^2 = int_0^inf 2t [nu(psi >= t) + nu(psi <= -t)] dt
and int_0^inf 2t (1 + k t/r)^{-s} dt = (2 r^2/k^2) int_0^inf y (1+y)^{-s} dy = 2 r^2/(k^2 (s-1)(s-2)).
(iv) ZBS Step 2: P_Y(a >= t) <= t^{-r}; column maximality for A in Y gives nu(A) = E_Y[a^s 1_A] <= P_Y(A)^{1-beta};
together nu(a >= t) <= t^{-r(1-beta)}. ZBS Lemma 3.1: a^s >= 1 - beta, so a >= e^{-K_beta/r} >= 1 - K_beta/r. Then
E (a-1)_+^2 <= int_0^inf 2t (1+t)^{-rho} dt = 2/((rho-1)(rho-2)) and (a-1)_-^2 <= K_beta^2/r^2. []
Consequence: |P_j(T)| <= E_nu |psi_T| <= ||psi_T||_2. This is bounded uniformly in r, and uniformly over all T with
|T|/N in [eps, 1 - eps], by (iii); T = X gives psi_X = 0. Only fixed v_k < 1 and v_m = 1 are used below.

### Lemma S3.5 (zero average over any balanced row set; exact identity)
For nonempty T, C in X and every constant d0, with D_T = psi_T - E_nu psi_T,
  avg_{j in C} [P_j(T) - m_j avg_T phi] = E_nu[D_T (g - d0)] + (1/r) E_nu[D_T u psi_C].
Hence |avg_{j in C} (P_j(T) - m_j avg_T phi)| <= ||psi_T||_2 (H ||a - 1||_2 + ||psi_C||_2 / r)   (norms in L2(nu)).
Proof. P_j - m_j E_nu psi_T = E_nu[D_T h_j]; average over C: E_nu[D_T g^C] with g^C = g + u psi_C/r; E_nu D_T = 0 lets
one subtract d0; take d0 = c + H (g - d0 = H(a - 1)), Cauchy-Schwarz, ||D_T||_2 <= ||psi_T||_2 and 0 < u < 1. []
Meaning: the red neighbourhoods of the rows of C have column density g^C = g + u psi_C/r. This is uniform over Y up
to O(1/r) in L2(nu), because psi_C is L2-bounded for EVERY C with |C|/N in [eps, 1/2] (S3.4(iii); row maximality
holds for every subset). So T cannot be made sparser on the red neighbourhoods of any set of rows of positive
proportion.

Corollary S3.5' (row-by-row pinning; strengthening suggested by the referee, 12:xx). Fix T with |T|/N in [eps, 1 - eps]
or T = X. Put kappa_j = P_j(T) - m_j avg_T phi. For every delta > 0,
  |{j in X : |kappa_j| > delta}| / N -> 0 as r -> infinity (beta, w, eps fixed; uniformly over such T).
Proof. Let 0 < e <= 1/2 and suppose |{j : kappa_j < -delta}| >= e N. Choose C in that set with |C| = ceil(e N)
(e N >= 1 for large N). Then sigma_C = |C|/N lies in [e, 1/2 + 1/N], and S3.5 with S3.4(iii) for T and for C gives
  delta < |avg_C kappa_j| <= ||psi_T||_2 (H ||a - 1||_2 + sqrt(K2*(e) 2 r^2/((s-1)(s-2)))/r),
where K2*(e) = sup of K2 over [e, 2/3] < infinity. The right side tends to 0 as r -> infinity (S3.4(iv): rho_beta =
(1-beta) r -> infinity), so for r large the assumption fails: |{kappa < -delta}| < e N. The set {kappa > delta} is
handled the same way, and e is arbitrary. []
Hence Psi_j(T) = P_j(T)/m_j -> avg_T phi in probability over the rows j with m_j bounded below (in particular over
the regular rows of S3.6). In the limit, Psi_omega(k) = Phibar_k for almost every row. Non-flatness of psi_T is
allowed (only correlations of psi_T with single rows' red cells are pinned).

### Theorem S3.6 (inside-T envelope, per row and rank-averaged; no flatness, no joint maximality)
Setting: a sequence of configurations as in ZBS Proposition 3.5 (r -> infinity, c -> p, H bounded, d_R(X,Y) >= p - o(1);
s > 2), with N = |X| -> infinity (used in Steps 2-4; supplied by N_0 = j in the contradiction of S7, Lemma 4.5'),
with cap_n = mu + tau_n, tau_n -> 0 (ZBS's limit-form convention), in which every test of S1 fails:
RED_T(j) and BLUE_T(j) for all j and every T = T_k below, and (BOOK_S) for S = T_k at cap_n, so that all but
zeta_n N rows of T_k (zeta_n -> 0) have q'_j(k) <= cap_n. Delta satisfies Delta (v_1 N (1 - cap) - 1) >= 1 - c, as in
ZBS Lemma 4.5 with N replaced by v_1 N. In the induction, Delta = delta/(n(n-1)), and this holds for every n >= 4 once
the last entry of ZBS's K_1 is replaced by (1 + n(n-1)/delta)/(v_1 (1 - cap)). The scales 0 < v_1 < ... < v_m = 1 are
fixed before r. Rank the rows by V decreasing (ties by a fixed order), the i-th row having rank i/N;
T_k = the ceil(v_k N) rows of rank <= ceil(v_k N)/N; for j in X let F_j(t) = |B_j cap {rank <= t}|/N.
Conclusion: along a subsequence there are d_* in [p, 1), a nonincreasing phi in L1(0,1] with phi >= -w, int phi = 0,
Phi(v) = int_0^v phi <= -w v log v, a probability space of limit rows omega with uniform rank U(omega) and
nondecreasing 1-Lipschitz profiles F_omega (F_omega(0) = 0), and the rank averages Fbar_u = E[F | U = u] (measurable in
u), such that (B') and (G') below hold for F_omega with u = U(omega) for almost every omega (PER ROW), and hence also
for Fbar_u for almost every u (RANK-AVERAGED). Here, with
  eta~_k = -w log v_k - Phi(v_k)/v_k in [0, w log(1/v_k)],   g_{u,k} = Fbar_u(v_k)/v_k,
for every k with v_k > u:
 (B') G0_{d_*}(g_{u,k}) <= beta eta~_k and g_{u,k} <= mu; i.e. g_{u,k} is in the closure of
      F_{d_*}(x e^{eta~_k}, mu e^{eta~_k/w}) cap (0, mu]; in particular g_{u,k} >= a_{d_*}(eta~_k) (left end) when
      eta~_k < log(d_*/x);
 (G') int_0^{v_k} phi dFbar_u <= v_k H^T_{v_k,d_*}(g_{u,k}, Phibar_k) = Fbar_u(v_k) [M_{d_*}(g_{u,k}; x e^{eta~_k},
      mu e^{eta~_k/w}) + Phibar_k],   Phibar_k = Phi(v_k)/v_k;
and (Sym') int_I Fbar_u(I') du = int_{I'} Fbar_u(I) du for all intervals I, I' (Fbar_u(I') = Fbar_u-mass of I').
By S3.2(iii) and d_* >= p, (B') and (G') remain true with d_* replaced by p (each is relaxed).
(L) at every scale follows from (G') and (Sym'): integrate (G') over u in (0, v_k), and by (Sym')
int_0^{v_k} int_0^{v_k} phi(t) dFbar_u(t) du = int_0^{v_k} phi(u) Fbar_u(v_k) du, which gives
int_0^{v_k} g_{u,k} [M_{d_*}(g_{u,k}; .) - (phi(u) - Phibar_k)] du >= 0 (only the inside-T_k part of (Sym') is used).
Proof.
Step 1 (regular rows). By ZBS (C1), (C2), E_X |m_i - d| + E_X |pi_i - d| = O(1/r) (d = d_R(X,Y)). By S3.4(iii) applied
to T_k and X \ T_k, sup_k ||psi_{T_k}||_2 <= C for large r, so |P_j(T_k)| <= C. By S1's (BOOK_S) consequence, all but
o(N) rows j of T_k have q'_j(k) <= mu + o(1) <= cap, so sigma'_j(k) >= 1 - cap - 1/(v_1 N) and the bracket condition of
S3.1 holds for every row with q'_j(k) <= cap_n (and only those are guaranteed it). Choose eps_n -> 0 slowly with
eps_n r_n -> infinity (Markov with (C1), (C2)). Call j regular if |m_j - d|, |pi_j - d| <= eps_n and q'_j(k) <= cap_n
for every k with j in T_k (Gate 1 referee: the degree condition is q' <= cap_n, NOT q' <= mu + eps_n, because the
bracket is guaranteed only for q' <= cap_n). The proportion of non-regular rows is at most O(1/(eps_n r_n)) + m zeta_n
-> 0, and cap_n -> mu gives g <= mu in the limit.
Step 2 (features, limit). Row features xi_j = (rank_j, F_j, m_j, pi_j, (P_j(T_k))_k, 1[j regular]) take values in a
compact metric space (F_j in the nondecreasing functions [0,1] -> [0,1] with the L1 metric, compact by Helly;
P in [-C, C]). Let phi_n(t) be the drift of the row of rank t (nonincreasing step function). phi_n >= -w,
int_0^1 phi_n = 0 and int_0^t phi_n <= r t (t^{-w/r} - 1) (ZBS (eq:support) with z = 1_{rank <= t}) make (phi_n)
uniformly integrable, so by Helly a subsequence converges in L1(0,1) to a nonincreasing phi with the stated
properties (Phi(v) <= -w v log v as the limit of r v (v^{-w/r} - 1)). Pass to a further subsequence along which
d_R(X,Y) -> d_* (d_* < 1 by ZBS Step 6) and the laws of xi_J (J uniform in X) converge; Skorokhod represents them on
([0,1], Leb) with xi^n(omega) -> xi(omega) a.s. In the limit the rank U is uniform, m = pi = d_*, the indicator is 1
for all large n a.s., F_omega is 1-Lipschitz (F_j(t') - F_j(t) <= t' - t + 1/N), and P_omega(k) is in [-C, C].
Step 3 (per row). Fix omega outside a null set and k with U(omega) < v_k; then the row j_n(omega) is in T_k and regular
for large n. Its q'_{j_n}(k) = F_{j_n}(|T_k|/N) N/|T_k| -> F_omega(v_k)/v_k = g_omega, Psi_{j_n} = P/m -> P_omega(k)/d_*.
Proposition S3.3 gives (g_omega, P_omega(k)/d_*) in D_{v_k,d_*}, g_omega <= mu, and
int_0^{v_k} phi dF_omega <= v_k H^T_{v_k,d_*}(g_omega, P_omega(k)/d_*), once the left side is identified as the limit
of (1/N) sum_{i in B^T_j} phi_i = sum_{i/N <= |T_k|/N} phi_n(i/N) (F_{j_n}(i/N) - F_{j_n}((i-1)/N)). (Corrected after the
referee, 12:xx: dF_{j_n} is purely atomic, so a density argument does not apply.) Take the left-continuous version of
phi. (a) (1/N) sum_{i <= N} |phi_n(i/N) - phi(i/N)| <= ||phi_n - phi||_1 + 2(phi(1/N) + w)/N + int_0^{1/N} |phi| -> 0,
because phi_n is constant on each cell ((i-1)/N, i/N] and phi is nonincreasing (so the cell oscillations of phi
telescope, the first cell taken separately), and phi(1/N) <= N int_0^{1/N} phi <= w log N.
Since each atom of dF_{j_n} has mass <= 1/N, |int phi_n dF_{j_n} - int phi dF_{j_n}| -> 0. (b) Fix t0 in (0, v_k). On
[t0, v_k], phi is bounded, and continuous except on a countable set, which is dF_omega-null because F_omega is
Lipschitz. The measures dF_{j_n} restricted to [t0, v_k] converge weakly to dF_omega (F_{j_n} -> F_omega uniformly,
since they are monotone, equi-Lipschitz up to 1/N, and converge in L1). The portmanteau theorem gives
int_{[t0,v_k]} phi dF_{j_n} -> int_{[t0,v_k]} phi dF_omega. (c) On [0, t0], |int phi dF_{j_n}| <= int_0^{t0} |phi| + o(1)
by (a)'s cell comparison, and the same holds for F_omega; let t0 -> 0.
Step 4 (row-by-row pinning in the limit). Corollary S3.5', applied to T_k (|T_k|/N -> v_k in (0,1)) or with psi_X = 0
for v_m = 1, gives P_j(T_k) - m_j avg_{T_k} phi_n -> 0 in probability over rows; avg_{T_k} phi_n -> Phibar_k; m -> d_*.
So P_omega(k) = d_* Phibar_k, i.e. Psi_omega(k) = Phibar_k, for almost every omega.
Step 5 (per row, then rank-averaged). By Steps 3-4, for a.e. omega and each k with U(omega) < v_k:
(g_omega, Phibar_k) is in D^mu_{v_k,d_*} and int_0^{v_k} phi dF_omega <= v_k H^T_{v_k,d_*}(g_omega, Phibar_k). By the
relation to the flat model this is (B') and (G') for F_omega: the per-row statement. For the rank averages, take a
regular version of Fbar_u = E[F | U = u] (averages of nondecreasing 1-Lipschitz functions are such). By Fubini
(dF_omega has density in [0,1]), E[int_0^v phi dF | U] = int_0^v phi dFbar_U. Now q -> H^T_{v_k,d_*}(q, Phibar_k) is
concave, usc and bounded above on the closed interval section of D^mu at Phibar_k (S3.2 at fixed Psi), so it is the
infimum of countably many affine majorants. Conditional Jensen in q alone then gives (B') and (G') for Fbar_u.
Neither the Psi-direction of S3.2(ii) nor any averaging of Psi is needed any more. (Steps 4-5 of the first version
averaged Psi over a rank instead. That is still valid, but superseded.)
(Sym'): sum_{j in C} |B_j cap C'| = sum_{j in C'} |B_j cap C| for drift intervals C, C' (the blue graph is undirected);
pass to the limit with (a)-(c) for indicator integrands, and condition. eta~_k >= 0 by Phi(v) <= -w v log v;
eta~_k <= w log(1/v_k) because avg_{T_k} phi_n >= avg_X phi_n = 0 (top set). []

Proposition S3.6B (rows OUTSIDE T_k, "version B"; both referees' q = 1 gap closed, 12:xx). In the setting of S3.6, for
a.e. limit row omega and every k with U(omega) > v_k, put g = F_omega(v_k)/v_k in [0, 1] and let Hhat_k be the
extension of q -> H^T_{v_k,d_*}(q, Phibar_k) from [0, 1) to [0, 1] by its limit at q -> 1 (value in [-infinity, inf)).
Then
 (B'_out) g = 1, or (g, Phibar_k) is in D_{v_k,d_*} (NO cap g <= mu for these rows);
 (G'_out) int_0^{v_k} phi dF_omega <= v_k Hhat_k(g);
 (Q1) if g = 1 then eta~_k >= w log(1/mu) (about 0.44 at the root control). So when eta~_k < w log(1/mu), no outside
      row has g = 1, and (B'_out), (G'_out) are the inside-row constraints without the cap.
The same holds for the rank averages Fbar_u (u > v_k), because Hhat_k is concave and usc on its domain, and that
domain is convex. If eta~_k >= w log(1/mu), then G_{v_k,d_*}(q, Phibar_k) -> log d_* + beta (w log(1/mu) - eta~_k)
< 0 as q -> 1, so the section of D at Phibar_k is an interval [a, 1) and the domain of Hhat_k is [a, 1]. If
eta~_k < w log(1/mu), no outside row has g = 1 (Q1), and the domain is the interval section of D.
Proof. Rows j outside T_k need no bracket condition (E_j = sigma' Delta >= 0). Corollary S3.5' covers every row of X,
so Psi_omega(k) = Phibar_k a.s. also for outside rows (Step 4 needs no restriction to ranks below v_k). If g < 1,
then q'_{j_n} -> g < 1 and Proposition S3.3 applies as in Step 3. If g = 1: F_omega is 1-Lipschitz with
F_omega(v_k) = v_k, so dF_omega = dt on [0, v_k] and int_0^{v_k} phi dF_omega = Phi(v_k) = v_k Phibar_k. The blue
failure alone (S3.1(b), Jensen) gives q' r E_nu Z^T_j < q' r (U^{1/s} - 1) -> q B = w q log(mu/(q v_k)); at q = 1 this
gives v_k Phibar_k <= v_k w log(mu/v_k), i.e. eta~_k >= w log(1/mu): this is (Q1). In that case A -> Phibar_k <=
w log(mu/v_k) = B(1) as q -> 1, so H^T(q, Phibar_k) = q B(q) near q = 1 (or the branches meet at A = B), and
Hhat_k(1) = B(1) = w log(mu/v_k): this is (G'_out) at g = 1. If eta~_k < w log(1/mu), rows with g = 1 do not exist,
by (Q1). Concavity: Hhat_k is the usc extension of a concave usc function on [0, 1) (S3.2), hence concave on [0, 1],
and the rank averaging is Step 5 verbatim. []
Not used in Theorem S as stated (which is version A). It is available to the certificate as extra constraints.

Remarks. (1) Rows OUTSIDE T: see Proposition S3.6B.
(2) What the global normalisation changes. In the lane's local S3 the objective of the two-cell problem is an
inside-T drift phi'_j = r(V^T_j - 1) and the bound is converted to global drifts afterwards, which needs flatness.
Here the objective is the global drift average directly (S3.1(a)); the only trace of T in the constraints is Psi_j(T)
(red-cell average of psi_T), plus v.
(3) The POTENTIAL gap eta = log Phi(X,Y) - log Phi(T,Y) never appears. Only the DRIFT desaturation eta~ does, through
Phibar_k. In the limit eta~ = eta + J with J = beta^{-1} log E(1 + psi/r)_+^s - E psi -> Jensen gap >= 0. At finite r,
J can be slightly negative (e.g. psi constant), so 'eta~ >= eta' is a limit statement (referee 12:xx). This is exactly the lane's model's eta (selfsim2.py: Phi(s_i) =
-w s_i log s_i - s_i eta_i, with H' and a' at (x e^{eta_i}, mu e^{eta_i/w}); the book cap stays mu).
(4) The lane's local per-row S3(i) (q'_i >= a(eta) per row, with the potential gap) is a different, also valid route
to level (i); it needs joint maximality of (X,Y) (available in the induction) and the concentration inside T.
S3G needs neither and gives level (i) PER ROW with eta~ (S3.6 Step 5), and for rank-averaged rows.

### S3.7 Constants for the finite-host closure (scales fixed FIRST; both referees, 12:xx)
Order of choices. (0) The control (p, mu, w, beta, x) and the scale grid 0 < v_1 < ... < v_m = 1 are fixed first.
(1) Then xi, y_0, nu, xhat, yhat and lambda, y are as in ZBS's proof of Theorem 4.2. N_0, eta, tau, zeta, R_0 and
cap = mu + tau come from Lemma 4.5' (S7) under the control's (INF) hypothesis: (INF-b) for level-(i) (CD) controls,
(INF-c) for full-chain controls, (INF-a) for ZBS's own controls. Lemma 4.5' is obtained from the limit form by
contradiction, as ZBS's Theorem 3.4 is obtained from Proposition 3.5, with all T_k-tests included. Take theta with mu < theta < cap. (2) Then r >= R_0 so large that
  D_r / v_1 < min{1/4, (cap - theta)/2}     (D_r as in ZBS Lemma 4.3; D_r -> 0, so this fixes r AFTER v_1).
(3) Put h_1 = cap - theta - D_r/v_1 > 0 and, for n >= 4,
  b_n = max{1, ceil((r log(n^2/delta) + w log(2/v_1)) / (w log(theta/mu)))},   m_n = ceil(2 b_n / h_1),
  K_1 = sup_{n >= 4} e^{-a_0 n} max{ N_0/v_1, 4 m_n/v_1, 2 m_n/(h_1 v_1), n^{m_n - 1}/(zeta v_1),
                                     (1 + n(n-1)/delta)/(v_1 (1 - cap)) }  < infinity
(each entry is e^{O((log n)^2)}), and choose L_0 by ZBS's two conditions with this K_1.
What these give when N >= e^{a_0 n} K_1 (which the induction provides, as in ZBS), for every S in
{T_1, ..., T_m, X} (|S| >= v_1 N) and every n >= 4:
 - Lemma 4.4 applies to S with page set G cap S: 1 - |G cap S|/|S| <= D_r/v_1 <= 1/4 (Lemma 4.3);
   m_n/|S| <= m_n/(v_1 N) <= min{1/4, h_1/2}; b_n/m_n <= h_1/2; so D + m_n/|S| + b_n/m_n <= cap - theta;
 - R(k, m_n) <= n^{m_n - 1} <= zeta v_1 N <= zeta |S|: in the local case at most zeta |S| rows of S have q'_j(S) >= cap;
 - the page ratio is Phi_{n-b}(P, Y)/Phi_n(X, Y) >= (theta^b v_1/2)^w (delta/n^2)^r >= mu^{w b}, by the choice of b_n;
 - the bracket of S3.1 for j in S with q'_j <= cap: Delta n_S sigma'_j >= Delta (v_1 N (1 - cap) - 1) >= 1 - c, with
   Delta = delta/(n(n-1)), because N >= (1 + n(n-1)/delta)/(v_1 (1 - cap));
 - |S| >= v_1 N >= N_0.
S1's (BOOK_S) with sigma = v_1 is this choice (one pair (b_n, m_n) serves every S, including S = X).

## S4. Summation by parts in drift order (exact)

Order rows by V_j decreasing: phi_(1) >= phi_(2) >= ... For any row u and any set B,
  sum_{j in B} phi_j = phi_(N) |B| + sum_{i<N} (phi_(i) - phi_(i+1)) |B cap T_{i/N}|,
so lower bounds |B_u cap T_v| >= f(v) N give  q_u zeta_u >= q_u phi_min + int f(v) (-dphi(v)).

## Theorem S (target, limit form). Self-similar envelope

Fix 0 < p, mu, beta < 1, w > 0 and 0 < x < min{p, (1 - mu)^w} (NOT "as in ZBS Theorem 3.4": that theorem assumes
CERT < 0, which fails above ZBS's x_max; referee 3, 12:3x) and a finite grid of scales 0 < v_1 < ... < v_m = 1, fixed
before r. Call a LIMIT CONFIGURATION the following data: a nonincreasing drift phi on (0, 1] with phi >= -w and
int phi = 0; desaturations eta~_i = -w log v_i - Phi(v_i)/v_i in [0, w log(1/v_i)] (Phi = cumulative of phi; the general
support bound int_S phi <= -w |S| log |S|); a measurable family of nondecreasing blue profiles F_u (Lipschitz with
constant 1) with g_{u,i} = F_u(v_i)/v_i, such that (continuous form of S6):
  (B)  for v_i > u: g_{u,i} in the CLOSURE of F_p(x e^{eta~_i}, mu e^{eta~_i/w}) (g = 0 allowed when
       x e^{eta~_i} >= p) and g_{u,i} <= mu (rows of T_{v_i}); for rows OUTSIDE T_{v_i} (version B, S3.6B):
       g_{u,i} = 1 or G0_p(g_{u,i}) <= beta eta~_i (the D-section, NO cap at mu or mu'; referee 3 re-check);
  (G)  for v_i > u: int_0^{v_i} phi dF_u - Phibar_i F_u(v_i) <= F_u(v_i) M'_i(g_{u,i}), Phibar_i = Phi(v_i)/v_i,
       M'_i = ZBS's M at (x e^{eta~_i}, mu e^{eta~_i/w}); on a grid of cells the left side may only be bounded below
       one-sidedly, by sum_k [Phi(s_k) - Phi(s_k - dF_k)] - Phibar_i F_u(v_i) (S6), never with cell averages;
       for rows outside T_{v_i} (version B) the same inequality with M'_i replaced by the usc extension of S3.6B
       (Hhat at g = 1: B(1) = w log(mu/v_i));
  (L)  int_0^{v_i} g_{u,i} [M'_i(g_{u,i}) - (phi(u) - Phibar_i)] du >= 0 (derived from (G) and (Sym), S3.6);
  (Sym) the blue measure dF_u(t) du is symmetric in (u, t);
  (Z)  ZBS's own conditions (the case v_m = 1).
CLAIM (final form after referee 3): for every failing sequence as in Definition (INF) of S7 (r -> infinity,
N -> infinity, the Delta lower bound, cap_j and zeta_j as stated there; all tests RED', BLUE', BOOK_{T_k} fail at
maximal pairs with shift c -> p), a limit configuration exists (Theorem S3.6, S3.6B, Corollary S3.5', S6; no flatness hypothesis).
CONSEQUENCE: by S7 (S3G helper, after referee 3): (INF) = "no failing sequence" holds when this system is infeasible
for every admissible drift (INF-c), or when V_A < 0 for all admissible drifts (INF-b, Theorem A), or when CERT < 0
(INF-a, ZBS); Lemma 4.5' and Theorem 4.2' (ZBS's closure with Lemma 4.5' in place of Lemma 4.5, BOOK_S at every T_k,
S3.7's constants; L_0 depends on the control and the grid) give the finite-host closure, and Definition 5.2' (grid and
(INF) in place of F nonempty and CERT < 0) makes ZBS's Lemmas 5.8, 5.9, Theorem 5.7 and Corollary 5.10 hold verbatim,
also for banks mixing old and new controls. S7 checked by referee 3's statement re-check (NOTES 12:4x) and by the
Gate 1 referee (NOTES 13:xx).
Status: analytic chain checked by three fresh-context referees (NOTES 11:2x, 11:5x, 12:3x), no wrong step found;
statement-level fixes above. OPEN: the certificate (infeasibility for every admissible drift, including every
within-cell drift shape, on a fine scale grid). Float evaluations for a drift family (code/chain_safe.py) are
measurements, not certificates, and a one-parameter family A log(1/v) overstates the gain (an 8-knot adversary already
survives at a_root - 0.0012 at 40 scales, NOTES 12:3x).
Update 18 Nov 15:xx. The two-region form of the chain is Lemma D' (CERT_DESIGN Section 9; fresh referee PASS, NOTES
14:0x): V_D'(phi) < 0 for every admissible phi implies (INF). Its first certification design (Lemma DL, Section 10)
FAILED a fresh referee (NOTES 14:2x) and, independently, cannot close in principle (linear bounds against a sqrt-type
Q drop; Section 10, 782e1f67d). Float threshold at c1722 (chain_safe, nsub 1000, 66 scales): about a_root - 0.0013
against step drifts (the strongest found), about - 0.00166 against smooth drifts (NOTES 14:3x). Certification of
level (ii) is OPEN; level (i) (Theorem A) is certified through Lemma D (certCD, ramsey-zbs).

## S5. The per-row scale chain (the mechanism; in global coordinates by S6, no flatness needed)

Let the drift have cumulative Phi(v) = -w v log v - v eta(v) (eta = eta~, the drift desaturation; S6), so
phi(v) = Phi'(v) and phibar_v - phi(v) = w + v eta'(v). For a row u and v >= u write F(v) = |B_u cap T_v|/N,
g(v) = F(v)/v. (G') of Theorem S3.6 (global drifts) and S4 (summation by parts in global drift order) give
  int_0^v F(s) |dphi(s)|  <=  F(v) (M'_v(g(v)) + phibar_v - phi(v))  =  v H'_v(g(v)) + F(v) v eta'(v),
with H'_v(q) = q M'_v(q) + w q (ZBS's H at x e^{eta_v}, mu e^{eta_v/w}). For eta = 0 this is
  w gbar(v) <= H(g(v)),  gbar(v) = (1/v) int_0^v g,
i.e. d gbar / d log v = g - gbar >= h^{-1}(w gbar) - gbar > 0 (h = H on its increasing branch; H(q) < w q because
M < 0 on the whole feasible set at ZBS's extremal). So along the scales above a row, the average relative blue density
of the row must keep increasing at a rate bounded below, which is incompatible with g <= mu for rows of small u unless
eta_v is large on a long range of scales (large enough that M'_v >= 0 near the relevant q, i.e. eta_v >= about 0.14
at q = 0.3 for the root control). Large eta costs drift (Phi lower by v eta_v), which ZBS's own aggregate penalises.
This "either desaturate on many scales or break the chain" dichotomy is the mechanism behind the model gain, and is
the natural backbone of a rigorous certificate (count the scales on which eta is large).

## Theorem A (level (i), the part the referee accepts; limit form) -- statement and certificate route

Fix 0 < p, mu, beta < 1, w > 0, 0 < x < min{p, (1 - mu)^w} (needed in ZBS Steps 5 and 6; referee 3) and scales
0 < v_1 < ... < v_m = 1 chosen before r. For eta >= 0 let a(eta) be the left end of
F_p(x e^eta, mu e^{eta/w}) (a(eta) = 0 if x e^eta >= p). Call (phi, eta) ADMISSIBLE if phi: (0,1] -> [-w, infinity) is
nonincreasing, int_0^1 phi = 0, int_S phi <= -w |S| log |S| for all S, and for each k: 0 <= eta_k <= w log(1/v_k) and
Phi(v_k) <= -w v_k log v_k - v_k eta_k (Phi = cumulative of phi). Put, for u in (0,1],
  c(u) = sum_{k < m, v_k >= u} a(eta_k) v_k (phi(v_k) - phi(v_{k+1})),
  V_A(phi, eta) = int_0^1 sup{ q (M(q) - phi(u)) : q in F_p(x, mu), q M(q) >= q phi(1) + c(u) } du
(sup of the empty set = -infinity). THEOREM A: if V_A(phi, eta) < 0 for every admissible
(phi, eta), the local alternative with the sub-pair moves of S1 holds at (p, mu, w, beta, x).
Proof. The complete proof is S6's paragraph "Level (i) (Theorem A) and what it relies on" together with S7 (closure);
what follows is an outline (cite the S6 route, "Level (i) (Theorem A) and what it relies on"; the older S3(i) is superseded).
In a failing sequence (r, N -> infinity): (B') at each v_k (all but o(N) rows of T_{v_k} have |B_u cap T_{v_k}| >=
(a(eta_k) - o(1)) |T_{v_k}|); S4 in global drift order turns these counts into q_u zeta_u >= q_u phi(1) + c(u) - o(1);
ZBS's per-row bound gives zeta_u <= M(q_u) + o(1); ZBS's exact identity sum q_u zeta_u = sum q_u phi_u and the
Step 7 passage to the limit (Fatou with the dominating H_0) give int q (M(q) - phi) >= 0 for the limit law, i.e.
V_A >= 0 for the limit drift. No flatness, no symmetry, no within-T aggregate is used. phi(1) means the left limit
phi(1-) >= -w. As for Theorem S, using the conclusion in the bank needs Theorem 4.2' (V_A < 0 in place of CERT < 0).
Certificate route (suggested to the certificate helper, 11:4x). For any multiplier lambda(u) >= 0,
  V_A <= int Gamma_lambda(phi(u), phi(1)) du - sum_k a(eta_k) v_k Lambda_k (phi(v_k) - phi(v_{k+1})),
  Gamma_lambda(f, f1) = sup_q [(1 + lambda) q M(q) - q f - lambda q f1],  Lambda_k = int_0^{v_k} lambda.
Gamma_lambda is a supremum of functions LINEAR in phi, so (as in ZBS) one swaps the sups: for each fixed choice q(u),
the phi-dependence is a linear functional int psi phi with psi = q(u) + (point masses at the v_k), minimised over the
drift polytope by summation by parts (the cumulative bounds Phi <= G_eta where d psi >= 0; concavity of Phi and
phi >= -w where d psi < 0). What remains is a finite-dimensional maximisation over (eta_k) and the q-profile, which
can be bounded on boxes of eta with the monotonicity of a(eta) (decreasing) and of G_eta (decreasing in eta).

## S6. Open 1 (flatness) closed: hypothesis (F) is not needed (S3/flatness helper; revised after two referees)

Theorem S6. In Theorem S's CLAIM, hypothesis (F) can be deleted, provided eta_i is read as the DRIFT desaturation
eta~_i = -w log v_i - Phi(v_i)/v_i and (B), (G), (L) are read in their continuous form below. Theorem S3.6 supplies:
(B) and (G) as (B') and (G') with d_* relaxed to p, for almost every limit row (per row) and for the rank averages;
(L) at every scale, derived from (G') and (Sym'); (Sym) as (Sym'); (Z) as the case v_m = 1 (T = X, psi_X = 0,
eta~_m = 0, BOOK_X = ZBS's book case); and the drift: phi nonincreasing, phi >= -w, int phi = 0,
int_S phi <= -w|S| log|S|, Phi(v_i) = -w v_i log v_i - v_i eta~_i with eta~_i in [0, w log(1/v_i)].
Continuous form: (G) reads int_0^{v_i} phi dF_u - Phibar_i F_u(v_i) <= F_u(v_i) M'_i(g_{u,i}), and (L) reads
int_0^{v_i} g_{u,i} [M'_i(g_{u,i}) - (phi(u) - Phibar_i)] du >= 0, with M'_i = M at (x e^{eta~_i}, mu e^{eta~_i/w}).

Grid form and the numerical models (CORRECTION of my 11:3x sentence; both referees). A model on scale cells can only
be a relaxation if its cell coefficients are adversary-favourable bounds. For a row's blue mass dF_k in cell
(s_{k-1}, s_k], int_cell phi dF >= Phi(s_k) - Phi(s_k - dF_k), because dF <= dt and phi is nonincreasing. If only
the grid values Phi(s_i) are known, the bound is >= phicell_{k+1} dF_k, with -w for the last cell. In (L) and in
ZBS's aggregate, a row's own drift must be replaced by the smallest drift of its cell. The cell-AVERAGE drift
(selfsim2.py and chain_rows.py with drift = 'avg') is NOT adversary-favourable. My 11:3x claim that "the lane's
model is a relaxation" is withdrawn for those codes. The lane's code/chain_safe.py uses the one-sided bound
Phi(s_k) - Phi(s_k - dF_k) for an exactly known Phi, and sub-cell rows with their smallest drift. That is the right
form for an eta-family evaluation. A certificate over ALL admissible drifts must use bounds valid for every phi
consistent with its data (certificate helper).

How the referee's first-order escape is defeated.
- In global coordinates, the escape ("make T sparser on the binding rows' red neighbourhoods") is an attempt to lower
  Psi_j(T), the red-cell average of psi_T, for the binding rows j. By S3.1(d) and S3.3 a lower Psi_j would relax
  row j's bound at first order.
- Corollary S3.5' rules it out ROW BY ROW: for every T of proportion in [eps, 1 - eps], all but o(N) rows j (inside
  or outside T) have Psi_j(T) -> avg_T phi. Reason: for ANY set C of rows of positive proportion, the red
  neighbourhoods of C have column density g^C = g + u psi_C/r, uniform over Y to O(1/r), because row maximality
  bounds psi_C in L2 (S3.4). So no positive proportion of rows can have red cells where T is sparse.
- psi_T itself may be far from constant (non-flat). Only its correlation with single rows' red cells is pinned. The
  Jensen gap J of psi_T costs drift exactly as desaturation does and relaxes the inside-T tests exactly as
  desaturation does, both only through eta~ (eta~ = potential gap + J in the limit). It is not a separate variable.
- So every failing configuration yields, row by row up to o(N) rows, a point of the FLAT system with eta = eta~. The
  escape gives no gain at any order. The first version of this argument (rank-averaging Psi with joint concavity,
  S3.2(ii)) is also valid, but is superseded.
- The lane's quadratic-form question (11:3x) and its q'-weighted (L) question (12:0x) are moot. No conversion from
  inside-T drifts is ever made, and (L) is derived after the fact from (G') and (Sym').
- Why the local analysis saw an escape: there the two-cell objective is an inside-T drift phi'_j, converted to global
  drifts afterwards, and the conversion error is not sign-controlled. Normalising both sub-pair failures by sum_Y u^s
  instead of by Phi(T, Y) makes the objective a global drift average (S3.1(a)), so there is no conversion.

Level (i) (Theorem A) and what it relies on. Theorem A holds with eta_k := eta~_k, both per row and for rank-averaged
rows. For a.e. limit row omega (u = U(omega)), with q_omega = F_omega(1):
 - q_omega is in F_{d_*} cap (0, mu]: the closure from (B') at v = 1, then F_{d_*} itself because (G') at v = 1 is
   finite;
 - int_0^1 phi dF_omega <= q_omega M_{d_*}(q_omega), by (G') at v = 1;
 - S4 for the Stieltjes integral, with F_omega(v_k) >= a_{d_*}(eta~_k) v_k for v_k > u (B') and a_{d_*} >= a_p (since
   F_{d_*} is in F_p), gives int_0^1 phi dF_omega >= q_omega phi(1) + c(u);
 - M_{d_*} <= M_p.
 The aggregate uses the LIMIT OF ZBS's STEP 4 IDENTITY (corrected wording, referee 12:xx). At finite r,
 (1/N) sum_j sum_{i in B_j} phi_i = (1/N) sum_i q_i phi_i exactly (the blue graph is undirected); in features this is
 E[int phi_n dF_J] = E[F_J(1) phi_n(U_J)]. The left side converges to E[int phi dF] by S3.6 Step 3 (a)-(c), with
 domination: -w <= int phi_n dF_j <= sup_t int_0^t phi_n <= w/e + o(1). The right side converges to E[F(1) phi(U)]
 because (1/N) sum_i |phi_n(i/N) - phi(i/N)| -> 0 (Step 3 (a)), F(1) is bounded, and E|phi(U^n) - phi(U)| -> 0
 (phi is in L1 and continuous a.e., and U^n -> U a.s. with uniformly integrable phi(U^n)). Hence
 E[int phi dF - q phi(U)] = 0, and so int_0^1 [qbar_u (M_p(qbar_u) - phi(u))] du >= 0 for the rank averages, with
 qbar_u satisfying the same restrictions by concavity of q M_p(q) (or row by row with the sup over q). So
 V_A(phi, eta~) >= 0, and (phi, eta~) is admissible (equality in the Phi bound).
 Relies on: S1 ((RED'), (BLUE'), (BOOK_S) for S = T_k and X); S2; S3.1, S3.3, S3.4, S3.5 and Corollary S3.5'
 (row-by-row pinning); S3.6 (B') and the v = 1 case of (G'); S3.7 (constants); S4; the Step 4 identity limit above;
 ZBS Lemmas 3.1 and 3.2 and Steps 2 and 5-8.
 Does NOT rely on: flatness; block symmetry between cells; (G') or (L) at scales v < 1; joint maximality; the
 Psi-direction of S3.2(ii).
 Alternative route: the lane's local S3(i), per row with the potential gap eta <= eta~. It needs joint maximality and
 the concentration inside T, but not S3.4-S3.5'. Either route gives the same certificate target (all admissible
 (phi, eta)).
Levels beyond (i) (G' at v < 1, (L), block symmetry, version B via S3.6B) rely in addition on S3.6's per-row (G')
(Steps 3-4, which do NOT use (Sym')) and, for (L), symmetry and version B only, on (Sym'). No flatness. (Lemma D',
CERT_DESIGN Section 9, uses per-row (B'), (G') and the v = 1 bound only, so no (Sym'); referee 18 Nov 14:xx.)

Still open in Theorem S, beyond (F), which is closed:
 (a) certification over every admissible (phi, eta~) (certificate helper), with valid grid bounds as above;
 (b) the finite-form wrapper: from the limit statement to a local alternative at fixed r, tau and zeta with the
     scale grid, by contradiction as in ZBS's Theorem 3.4. This is routine; its constants are recorded in S3.7.
 (c) CONJECTURE S (open question for level (ii); 18 Nov 18:xx; evidence in NOTES 18:0x and 18:2x).
     Setting: Lemma D' (CERT_DESIGN Section 9, refereed) in its grid relaxation. On a scale grid with u_b = v_b, a drift
     is described by its grid deficits m_i = g(v_i) - Phi(v_i) >= 0 (g = -w v log v). Q_LP(m) is the least final value
     of the grid-relaxed chain LP (Lemma DL (a) within-cell relaxation, supporting planes of K, adversary gap
     eta_i = m_i / v_i; CERT_DESIGN Sections 9-10, code cert/cutq_float.py). Q_ref = Q_LP(0). For each scale i,
     c_i := sup over single-scale deficits 0 < m <= m_i^max of (Q_ref - Q_LP(m e_i)) / sqrt(m).
     Conjecture S: there is a constant kappa (about 1.25 x the worst sampled ratio, i.e. about 5 at c1722) such that
       Q_LP(m) >= Q_ref - kappa sum_i c_i sqrt(m_i)   for every admissible deficit vector m.
     Consequence, if Conjecture S holds AND the sup below is certified: V_D'(phi) <= IL(Q_ref - kappa S(m)) + R(m), with
     S(m) = sum_i c_i sqrt(m_i); float sup at c1722 is < 0 up to about a_root - 7.5e-4 (100 scales) and about
     a_root - 8.5e-4 (120 scales), about 2.5x Lemma D's certified 3.0e-4 at the root.
     Two open lemmas:
       (S1) Validity: Conjecture S itself. kappa is empirical (the single-scale constants c_i alone fail: drop/S reaches
            4.0 at 100 scales and 4.5 at 120 on long chords starting at u_b, v .031 to about .08). A proof is a global
            bound on a bilinear LP value over the deficit polytope; no route yet.
       (S2) The sup of IL(Q_ref - kappa S(m)) + R(m) over admissible m. Obstruction: IL(Q_ref - kappa S) is
            nondecreasing in S and S is concave in m, so the adversary's gain is concave while R is convex; neither the
            chord-vertex reduction (convex objective) nor a concave-maximisation argument applies, and a Lagrangian on
            S >= s adds +lambda S, the wrong curvature. The float numbers above come from searches, not from an exact sup.

Checks (numeric parts; runs in NOTES_S3.md). Two separately written programs: code/s3g_checkA.py (Fractions; global
maximisers) and code/s3g_checkB.py (sympy; one-sided maximal pairs by local search; H^T by direct optimisation; the
S3.3 limit at r = 1e3, 1e5, 1e7). Both check exactly S2, S3.1(a)-(e), the identity in the proof of S3.1(c),
S3.4(i)-(iv) and the S3.5 identity. Both pass, and each refuses all 4 of its tampers. Lemma S3.2 has an analytic
proof; mpmath checks agree (2,000 + 120 chords, 0 violations; the second referee found 240,000 chords, 0
violations).
Referees: two fresh-context referees (12:xx, mine; 11:5x, the lane's): main claims CORRECT, with the fixable gaps now
fixed above. These are the Step 3 convergence, K2(1), cap_n, the 1/v_1 factors (S3.7), relative closedness, the
q-section sentence, J >= 0 only in the limit, the q = 1 case of version B (S3.6B), and the model-relaxation sentence
(withdrawn).

## S7. Finite-host closure for the new controls: (INF), Lemma 4.5', Theorem 4.2', Definition 5.2' (S3G helper, 12:4x)

ZBS (printed numbering) use CERT < 0 only in Lemma 4.5 (via Theorem 3.4), and their bank uses a control only through
the conclusion of Theorem 4.2 (proof of Lemma 5.8: "the hypotheses of Theorem 4.2 on (xi, y0, nu, xhat, yhat) hold by the
definition of a control, so it gives a threshold L_0(gamma)"). So it is enough to replace those two links (referee 3).

Definition (INF). Let 0 < p, mu, beta < 1, w > 0, 0 < x < min{p, (1 - mu)^w}, and let Lambda = (0 < v_1 < ... < v_m = 1) be a
scale grid. Say (INF) holds for (p, mu, w, beta, x; Lambda) if there is NO sequence (index j) of configurations such that:
r_j -> infinity with r_j > w and beta r_j > 2; N_j = |X_j| -> infinity; (X_j, Y_j) is maximal for Phi_{c_j} (ZBS's
one-sided sense) with H_j > 0, c_j -> p, H_j bounded, and liminf d_R(X_j, Y_j) >= p; with cap_j = mu + tau_j and
tau_j, zeta_j -> 0, for every v in Lambda at most zeta_j |T_v| rows i of T_v have |B_i cap T_v| > cap_j |T_v| (T_v = the
ceil(v N_j) rows of largest V_i for ONE fixed ranking by V (fixed tie-break), so the T_v are nested initial segments
of that ranking and T_v = X_j for v = 1); Delta_j >= (1 - c_j)/(v_1 N_j (1 - cap_j) - 1) > 0; and every test
RED_{T_v}(i), BLUE_{T_v}(i) (all v in Lambda, all rows i of X_j, whenever the sets involved are nonempty) fails, with c' = c_j - Delta_j.
(This is exactly the Setting of Theorem S3.6.) Sufficient conditions:
 (INF-a) F(p, mu, w, beta, x) nonempty and CERT(p, mu, w, beta, x) < 0, with ANY grid. The v = 1 tests are ZBS's. RED_X(i)
         failing gives the shifted-red failure (eq:R) through ZBS Lemma 4.5's identity. So such a sequence satisfies
         the hypotheses of ZBS Proposition 3.5, which gives CERT >= 0.
 (INF-b) V_A(phi, eta) < 0 for every admissible (phi, eta) (Theorem A; by S3.6 and S6, a failing sequence gives an
         admissible (phi, eta~) with V_A(phi, eta~) >= 0). If F is empty, (INF) holds trivially.
 (INF-c) Theorem S's limit system has no limit configuration (Theorem S's CLAIM).
How to certify (INF-b) or (INF-c) (the analogue of Lemma C for CERT < 0) is the certificate helper's open task.

Lemma 4.5' (local alternative with sub-pair moves). Assume (INF) for (p, mu, w, beta, x; Lambda). Then there are
eta, tau, zeta > 0, R_0 and N_0 with eta < min{p, 1 - p}, cap := mu + tau < 1, R_0 > w and beta R_0 > 2 such that
for every r >= R_0 the following holds. Let (X, Y) be maximal for Phi_c with |c - p| <= eta, H > 0 and N = |X| >= N_0.
For v in Lambda let T_v be the ceil(v N) rows of largest V_i for one fixed ranking by V (fixed tie-break), so the
T_v are nested initial segments of that ranking (T_v = X for v = 1). Suppose that for every v in Lambda
at most zeta |T_v| rows i of T_v have |B_i cap T_v| > cap |T_v|, and that Delta >= (1 - c)/(v_1 N (1 - cap) - 1) > 0, c' = c - Delta. Then for some v in Lambda
and some row i of X:
 (RED_T)  R_i cap T_v and Y_i are nonempty and Phi_{c'}(R_i cap T_v, Y_i) >= x Phi_c(X, Y), or
 (BLUE_T) B_i cap T_v is nonempty and Phi_c(B_i cap T_v, Y) >= mu^w Phi_c(X, Y).
(v = 1 gives ZBS's (RED) and (BLUE), but with no condition q_i <= cap; S1 shows none is needed.)
Proof. Fix j_0 with 1/j_0 < min{p, 1 - p, 1 - mu}. Suppose the statement fails for every admissible choice of
(eta, tau, zeta, R_0, N_0). Then for every j >= j_0 (so that eta = 1/j < min{p, 1 - p} and cap = mu + 1/j < 1, which
are the side conditions) the choice eta = tau = zeta = 1/j, R_0 = max{j, w + 1, 3/beta}, N_0 = j admits r_j >= R_0 and a configuration satisfying the
hypotheses in which every test fails. As in ZBS's proof of Theorem 3.4 from Proposition 3.5: |c_j| <= 1 + p,
H_j <= max_y u_y <= 1 - c_j <= 2, and d_j = c_j + E_Y u_y > c_j >= p - 1/j. With N_j >= j, cap_j = mu + 1/j and
zeta_j = 1/j, this is a sequence as in the definition of (INF), a contradiction. []

Theorem 4.2' (finite-host closure for the new controls). Let 0 < p, mu, beta < 1, w > 0, 0 < x < min{p, (1 - mu)^w},
let Lambda be a scale grid with (INF), and let xi, y0, nu, xhat, yhat in (0, 1) satisfy xi < min{x, xhat}, y0 < yhat,
nu < mu. Then there is an integer L_0, depending only on these numbers and on Lambda, with exactly the property in ZBS's
Theorem 4.2: for C >= 1, l >= L_0, a host satisfying Stop(C, xhat, yhat, l), integers k, t >= 1, and disjoint
nonempty X, Y with d_R(X, Y) >= p and |X|^w |Y| >= C^{w+1} xi^{-k} y0^{-l} nu^{-w t}, the set X cup Y contains a red K_k,
or X contains a blue K_t, or Y contains a blue K_l.
Proof. This is ZBS's proof of Theorem 4.2 with three changes.
 (1) Parameters. lambda and y are as in ZBS. N_0, eta, tau, zeta, R_0 and cap come from Lemma 4.5' instead of
     Lemma 4.5. Take theta with mu < theta < cap, and r >= R_0 with D_r/v_1 < min{1/4, (cap - theta)/2}. delta, c_n,
     Phi_n, script-A and a_0 are as in ZBS. b_n, m_n, h_1 and K_1 are as in S3.7: its entry N_0/v_1 is Lemma 4.5''s
     N_0, and it has the 1/v_1 factors. L_0 is chosen by ZBS's two conditions with this K_1.
 (2) The inductive step at the maximal pair (X, Y), chosen as in ZBS (it maximises Phi_n over all pairs of nonempty
     subsets). The stopping-rule case is unchanged. Otherwise N > e^{a_0 n} K_1 as in ZBS, which gives every
     consequence listed in S3.7 for each S = T_v (v in Lambda), and N >= N_0.
     BOOK CASE: for some v in Lambda, at least R(k, m_n) rows of S = T_v have at least cap |S| blue neighbours in S. Apply
     ZBS Lemma 4.4 to S, as in S1 (BOOK_S) with sigma = v_1 and the S3.7 constants. The result is a red K_k, or a
     blue b_n-clique S_b with pages P in G cap S, |P| >= theta^{b_n} |S|/2. If b_n >= t, S_b contains a blue K_t.
     Otherwise Phi_{n-b}(P, Y) >= mu^{w b} Phi_n(X, Y) (S3.7), so (I_{n-b}) applies to (P, Y), and a blue K_{t-b} in
     P together with S_b is a blue K_t. (v = 1 is ZBS's book case.)
     LOCAL CASE: for every v in Lambda, fewer than R(k, m_n) <= zeta v_1 N <= zeta |T_v| rows of T_v have at least
     cap |T_v| blue neighbours in T_v. Also |c_n - p| = delta/n <= eta, H in (0, 1], N >= N_0, and Delta = c_n - c_{n-1} =
     delta/(n(n-1)) >= (1 - c_n)/(v_1 N (1 - cap) - 1) (S3.7). Lemma 4.5' gives (RED_T) or (BLUE_T) for some v in Lambda and some row i.
     These are S1's (RED') with T = R_i cap T_v in R_i, Y'' = Y_i, and (BLUE') with T = B_i cap T_v in B_i, Y'' = Y.
     S1 turns either into an outcome through (I_{n-1}).
 (3) "The theorem follows from (I_n)" and the base cases are as in ZBS. []

Definition 5.2' (control, extended). A control is a tuple gamma = (p, mu, w, beta, x; Lambda; sigma; xi, y0, nu) with
0 < p, mu, beta < 1, w > 0, 0 < x < min{p, (1 - mu)^w}, a scale grid Lambda with (INF) for (p, mu, w, beta, x; Lambda), a source
index sigma, and 0 < xi < min{x, e^{-A_sigma}}, 0 < y0 < e^{-B_sigma}, 0 < nu < mu. p_gamma, w_gamma, A_gamma, B_gamma
and b_gamma are as in ZBS's Definition 5.2. Every ZBS control is a control in this sense (any grid; (INF-a)).
Bank validity with extended controls. ZBS's Lemma 5.8, Lemma 5.9, Theorem 5.7 and Corollary 5.10 hold verbatim for
banks whose controls are extended controls. In Lemma 5.8 the control is used only as follows:
 - the stopping rule from (SOURCE_sigma);
 - the hypotheses on (xi, y0, nu, xhat = e^{-A_sigma}, yhat = e^{-B_sigma}), which give L_0(gamma);
 - the conclusion of Theorem 4.2 at a pair with d_R >= p_gamma, under the leaf or route inequalities (in A_gamma,
   B_gamma, b_gamma and w_gamma).
Theorem 4.2' has the same hypotheses on those numbers and the same conclusion, so take L_0(gamma) from Theorem 4.2'
(it now also depends on Lambda). Lemma 5.9, the constants in the proof of Theorem 5.7 (K >= K_J and so on) and
Corollary 5.10 do not touch controls. Mixed banks (some ZBS controls, some new ones) are therefore allowed.
What a certificate must add for a new control: an exact certificate of (INF-b) or (INF-c) at that control and grid,
checked like Lemma C (two programs, tampers refused). That certificate is open.
