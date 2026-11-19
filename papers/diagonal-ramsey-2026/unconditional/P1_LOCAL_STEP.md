# P1. The local step: Lemmas 3.1-3.2, Theorem 3.4 and Proposition 3.5 with full proofs

Draft 19 Nov 2026 (+04); v2 after its fresh referee (PASS WITH FIXES: five GAPs supplied below, NITs applied, notation
de-clashed; REFEREE_P1_20261119.md). Block P1 of UNCONDITIONAL_PLAN.md: ZBS Section 3 (preprint @ c2875f33) restated
in our words with every step checked. Notation (only the notation, not 6.1's restrictions s > 2 and c in (0, 1)) as in
SELF_CONTAINED 6.1: a host; disjoint nonempty X, Y; N = |X|; |Y| is written |Y| (the letter M is reserved for the
functions M(q), M_d(q)); h_{iy} = 1 if iy is red; g_y = (1/N) sum_i h_{iy}; pi_i = (1/|Y|) sum_y h_{iy}; d = d_R(X, Y);
w > 0, 0 < beta < 1, r > w, s = beta r > 1, c real; H_c(X, Y) = (E_Y (g_y - c)_+^s)^{1/s}; Phi_c(X, Y) = |X|^w |Y|
H_c(X, Y)^r; (X, Y) maximal: Phi_c(X', Y) <= Phi_c(X, Y) and Phi_c(X, Y') <= Phi_c(X, Y) for nonempty X' in X, Y' in Y;
u_y = g_y - c, H = H_c(X, Y), alpha = E_Y u_y.

## P1.1 Lemmas 3.1 and 3.2

Lemma 3.1 (columns). If (X, Y) is maximal and H > 0, then u_y >= (1 - beta)^{1/s} H > 0 for all y; hence
alpha >= (1 - beta)^{1/s} H.
Proof. For nonempty Y' in Y, Phi_c(X, Y') = N^w |Y'|^{1 - r/s} (sum_{y in Y'} (u_y)_+^s)^{r/s} with 1 - r/s < 0. If some
u_{y0} <= 0 and |Y| >= 2, deleting y0 keeps the sum (positive, as H > 0) and lowers |Y'|, strictly increasing Phi_c:
impossible. If |Y| = 1, u_y = H > 0. Let |Y| >= 2, fix y, a = u_y/H, so u_y^s/sum u^s = a^s/|Y|. Maximality at
Y \ {y}, raised to s/r: 1 - a^s/|Y| <= (1 - 1/|Y|)^{1 - s/r} <= 1 - (1 - beta)/|Y| (Bernoulli for the exponent
1 - s/r = 1 - beta in (0, 1)). So a^s >= 1 - beta. []

Lemma 3.2 (rows). If (X, Y) is maximal and H > 0, put V_v = E_Y[u_y^{s-1}(h_{vy} - c)]/H^s. Then E_X V_v = 1 and for every
z in [0, 1]^X with t = E_X z > 0,
    E_X[z_v V_v] <= t^{1 - w/r};                                                                    (1)
in particular V_v >= 1 - w/r for every v.
Proof. Averaging h_{vy} - c over v gives u_y, so E_X V = E_Y u^s/H^s = 1. For z in [0, 1]^X let b_y = E_X[z_v (h_{vy} - c)],
||vec||_s = (E_Y |vec_y|^s)^{1/s} for vectors vec indexed by Y, and Lambda(z) = t (||(b/t)_+||_s/H)^{r/w}, Lambda(0) = 0.
The map vec -> (||vec_+||_s/H)^{r/w} is convex (||vec_+||_s is convex and nonnegative, r/w > 1), so Lambda (its
perspective composed with a linear map) is convex on {t > 0}; b/t is a convex combination of the vectors (h_{v.} - c),
so Lambda(z) = O(t) and Lambda extends continuously by 0 to a convex function on [0, 1]^X. At a vertex z = 1_{X'}
(X' nonempty), b/t is the column density of X' minus c, so Lambda(1_{X'}) = (Phi_c(X', Y)/Phi_c(X, Y))^{1/w} <= 1. A
convex function on the cube is at most its largest vertex value, so ||b_+||_s <= H t^{1 - w/r}. By Hoelder and u > 0
(Lemma 3.1), H^s E_X[z_v V_v] = E_Y[u^{s-1} b] <= ||u^{s-1}||_{s/(s-1)} ||b_+||_s = H^{s-1} ||b_+||_s, which is (1). With
z = 1 - eps e_v: 1 - eps V_v/N <= (1 - eps/N)^{1 - w/r}; let eps -> 0. []

## P1.2 CERT and Theorem 3.4

For 0 < p, mu, beta < 1, w > 0, x > 0 and q in (0, mu]: A(q) = ((1 - q)/q) log(p (1 - q)^w/x), B(q) = w log(mu/q),
U(q) = e^{beta B(q)}; M(q) = B(q) if A(q) <= B(q), else M(q) = p A(q) + ((1 - p)/beta) log((U(q) - p e^{beta A(q)})/(1 - p))
(defined iff U(q) > p e^{beta A(q)}). F = F(p, mu, w, beta, x) = {q in (0, mu] : A <= B, or A > B and p e^{beta A} < U}.
Since A <= B implies p e^{beta A} <= p U < U, F = {q in (0, mu] : p e^{beta A(q)} < U(q)}. For d in (0, 1) write A_d, M_d,
F_d for the same with p replaced by d. If F is nonempty,
    CERT(p, mu, w, beta, x) = int_0^1 sup_{q in F} [q M(q) + w q (1 + log t)] dt,
where "CERT < 0" includes integrability (on F, M <= B by concavity of log, so the integrand is bounded above).
Let BB be any simple graph on V; for i in X: B_i = {j in X : ij in BB}, q_i = |B_i|/N, b_i(y) the red density from B_i to
y (any value, e.g. 0, if B_i is empty; it is then multiplied by q_i = 0). Row i with q_i > 0 FAILS BLUE if
    sum_{y in Y} (b_i(y) - c)_+^s < (mu/q_i)^{w beta} sum_{y in Y} (u_y)_+^s,                                      (2)
and FAILS SHIFTED-RED if
    sum_{y : h_{iy} = 1} ((1 - q_i) u_y - q_i (b_i(y) - g_y))_+^s < (1 - q_i)^{s - w beta} x^beta pi_i^{1 - beta} sum_y (u_y)_+^s.   (3)

Theorem 3.4 (sharp envelope). Let 0 < p, mu, beta < 1, w > 0, 0 < x < min{p, (1 - mu)^w}, F nonempty and CERT < 0. There
are eta, tau, zeta > 0 and R0 > w with beta R0 > 1 such that for no r >= R0 is there a configuration (a host on V, a
simple graph BB on V, disjoint nonempty X, Y in V, a real c with |c - p| <= eta) with: (i) g_y > c for all y in Y;
(ii) (X, Y) maximal for Phi_c with parameters w, r, s = beta r; (iii) every i in X with q_i > 0 fails blue; (iv) some
X_g in X with |X \ X_g| <= zeta |X| has q_i <= mu + tau and fails shifted-red for every i in X_g.

Proposition 3.5 (limit form). Fix p, mu, w, beta, x as in Theorem 3.4. Suppose that for each j there is a configuration
with parameter r_j satisfying (i)-(iv) with tau = tau_j, zeta = zeta_j, where r_j -> infinity, r_j > w, beta r_j > 1,
tau_j, zeta_j -> 0, the shifts c_j and moments H_j are bounded, and liminf d_j >= p (d_j = d_R(X_j, Y_j)). Then, if F is
nonempty and the integrand of CERT is integrable, CERT >= 0.

Theorem 3.4 from Proposition 3.5. If the conclusion fails, then for every j >= 1 the choice eta = tau = zeta = 1/j,
R0 = max{j, w + 1, 2/beta} admits r_j >= R0 and a configuration with |c_j - p| <= 1/j satisfying (i)-(iv). Then
|c_j| <= 1 + p, H_j <= max_y u_y <= 1 - c_j <= 2, and d_j = c_j + E_Y u_y > c_j >= p - 1/j, so Proposition 3.5 gives
CERT >= 0, a contradiction. []

## P1.3 Proof of Proposition 3.5

Fix one configuration (index j suppressed). By (i), all u_y > 0, so H > 0; put a_y = u_y/H (E_Y a^s = 1), the probability
measure nu_y = a_y^s/|Y| on Y, m_i = E_nu h_{iy}, and for q_i > 0, Z_i(y) = (b_i(y) - g_y)/u_y. Since
u_y + (b_i(y) - g_y) = b_i(y) - c, (2) reads E_nu (1 + Z_i)_+^s < U_i := (mu/q_i)^{w beta}, and (3) reads
E_nu[h_{iy} ((1 - q_i) - q_i Z_i)_+^s] < (1 - q_i)^{s - w beta} x^beta pi_i^{1 - beta} (for q_i = 0 its left side is m_i).

Step 1 (two cells). For 0 < m < 1, s > 1, U > 0, t_U = U^{1/s} and real L, let S(m, U, L) be the supremum of
m z1 + (1 - m) z2 over z1 >= L with m (1 + z1)_+^s + (1 - m)(1 + z2)_+^s < U (-infinity if there is no such pair).
Raising a coordinate below -1 to -1 keeps the constraint and raises the objective, so put A1 = 1 + z1 >= 0,
C1 = 1 + z2 >= 0; by the power mean, m A1 + (1 - m) C1 < t_U. If L < t_U - 1 the supremum is t_U - 1 (approached at
A1 = C1 increasing to t_U); if L = t_U - 1 it is again t_U - 1 (take A1 = t_U and C1 increasing to its boundary
value, or use (4) below). If L > t_U - 1, then on the boundary C1 = ((U - m A1^s)/(1 - m))^{1/s} we have C1 < t_U < A1,
and the objective has A1-derivative m (1 - (A1/C1)^{s-1}) < 0; so the supremum is approached at A1 = 1 + L with C1
increasing to its boundary value, and equals
    m L + (1 - m)[((U - m (1 + L)^s)/(1 - m))^{1/s} - 1],                                                  (4)
the strict problem being feasible exactly when U > m (1 + L)^s. For a row i in X_g with q_i > 0 and 0 < m_i, Jensen on
the red cell {h_{iy} = 1} (nu-mass m_i) applied to (3) gives m_i ((1 - q_i) - q_i z_in)_+^s < (1 - q_i)^{s - w beta}
x^beta pi_i^{1 - beta}, z_in = E_nu[Z_i | h_{iy} = 1]; taking s-th roots ((s - w beta)/s = 1 - w/r, beta/s = 1/r),
    z_in > L_i,   q_i r L_i = (1 - q_i) r (1 - e^{l_i/r}),   l_i = log x - w log(1 - q_i) + beta^{-1}[(1 - beta) log pi_i - log m_i].   (5)
If pi_i, m_i -> d and q_i -> q, then l_i -> log x - w log(1 - q) - log d and r L_i -> A_d(q). If moreover m_i < 1, Jensen
on both cells, applied to (2), gives the constraint of the two-cell problem with m = m_i, U = U_i, z1 = z_in and
z2 = z_out = E_nu[Z_i | h_{iy} = 0]; the objective is E_nu Z_i, so E_nu Z_i <= S(m_i, U_i, L_i).

Step 2 (rows and columns concentrate). Lemma 3.1 gives a^s >= 1 - beta, so with K_beta = -log(1 - beta)/beta,
e^{-K_beta/r} <= alpha/H <= 1 (upper bound: power mean). Column maximality for a set Ys in Y of proportion theta gives
E_Y[a^s 1_{Ys}] <= theta^{1 - s/r}; with Ys = {a >= t} (t >= 1) this gives Pr_Y(a >= t) <= t^{-r}. Let J = E_Y a^{s-1} <= 1 and
P+ = E_Y[(a - 1)_+ a^{s-1}]. By the layer-cake formula and the tail bound,
P+ <= int_1^infinity (s t^{s-1} - (s - 1) t^{s-2}) t^{-r} dt = r/((r - s)(r - s + 1)) = O(1/r), and
1 - J = E_Y[a^{s-1}(a - 1)] <= P+. Let f_i = E_Y[a^{s-1} h_{iy}] = H V_i + c J; E_X f = H + c J. By Lemma 3.2,
f_i - E f >= -H w/r; f - E f has mean zero, so E_X |f_i - E f| <= 2 H w/r. Also m_i = E_Y[a^s h_{iy}], so
|m_i - f_i| <= E_Y[a^{s-1}|a - 1|] = 2 P+ - (1 - J) <= 2 P+, and E f - d = (H - alpha) - c (1 - J). Together
    E_X |m_i - d| = O(1/r).                                                                         (6)
Rows: the rows with pi_i >= c + H t (t > 1) form a set Xt with H_c(Xt, Y) >= H t (power mean), so (|Xt|/N)^w t^r <= 1 and
Pr_X(pi_i >= c + H t) <= t^{-r/w}; integrating, E (pi - c - H)_+ <= H w/(r - w), and since E pi = c + alpha = d,
    E_X |pi_i - d| <= 2 H w/(r - w) + 2 (H - alpha) = O(1/r).                                                (7)
(Constants in O(.) depend only on beta, w and the bounds on |c| and H.)

Step 3 (row maximality, averaged). Let gamma = 1 - w/r, Fq(z) = Pr_X(q <= z) (z real) and Q(t) = inf{z : Fq(z) >= t}
(t in (0, 1)) the quantile function of q. Since q = int_0^1 1[q > z] dz and E V = 1,
E[q V] = 1 - int_0^1 E[V 1[q <= z]] dz >= 1 - int_0^1 Fq(z)^gamma dz by (1) applied to the 0/1 vector (1[q_v <= z])_v in place of Lemma 3.2's vector (when Fq(z) = 0 the
inequality reads 0 <= 0); and 1 - int_0^1 Fq^gamma = int_0^1 Q(t) gamma t^{gamma - 1} dt (if T has density
gamma t^{gamma - 1} on (0, 1), then Pr(Q(T) > z) = Pr(T > Fq(z)) = 1 - Fq(z)^gamma with this convention for Q).
Subtracting E q = int_0^1 Q,
    r E[q (V - 1)] >= int_0^1 Q(t) k_r(t) dt,   k_r(t) = r[(1 - w/r) t^{-w/r} - 1] -> -w (1 + log t)           (8)
in L1(0, 1) (|k_r(t)| <= w t^{-1/2}(1 + |log t|) for r >= 2w).

Step 4 (symmetry). BB is undirected, so for each y, E_i[q_i b_i(y)] = N^{-2} sum_i sum_{j in B_i} h_{jy} = E_j[q_j h_{jy}].
With sum_y nu_y (h_{iy} - g_y)/u_y = V_i - 1 (expand nu_y = u_y^s/(|Y| H^s)) this gives
    E_X[q_i E_nu Z_i] = E_X[q_i (V_i - 1)].                                                           (9)
(8) and (9) hold over all rows, including exceptional ones.

Step 5 (small blue degrees do not occur). Put kappa = log(p/x) > 0 and choose, depending only on (p, mu, w, beta, x):
delta0 in (0, 1/2] with 2 w delta0 <= kappa/4, and delta in (0, min{delta0, 1/e}] with C0 sqrt(delta)(1 + log(1/delta))
< kappa/8, where C0 is the constant of the bound below. Call a row regular if |pi_i - d_j|, |m_i - d_j| <= eta_j with
eta_j = r_j^{-1/2}; by (6), (7) and Markov the proportion of non-regular rows tends to 0. For a regular row in X_g with
0 < q <= delta0 and j large (so that r_j >= max{2w, kappa/2} and d_j >= p - o(1)): l <= -kappa + 2 w delta0 + o(1) <=
-kappa/2 and m >= p/2, so (5) gives q r L >= (1/2) r (1 - e^{-kappa/(2r)}) >= kappa/8. On the other hand the blue
constraint on the red cell alone gives m (1 + z_in)_+^s < U, so q r z_in < q r (e^{b/r} - 1) <= q b e^{b/r} with
b = w log(mu/q) - beta^{-1} log m (e^y - 1 <= y e^y for y >= 0; if b <= 0 the bound is <= 0; if 1 + z_in < 0 the
conclusion is trivial), which is at most C0 sqrt(q)(1 + log(1/q)) for r >= 2w, m >= p/2, q <= mu. With z_in > L,
regular rows of X_g with 0 < q < delta do not occur for j large. At q = 0, (3) reads m < x^beta pi^{1 - beta}; for a
regular row m and pi are within o(1) of d_j >= p - o(1) > x, so m - x^beta pi^{1 - beta} is within o(1) of
d_j^{1 - beta}(d_j^beta - x^beta), which is bounded away from 0; this is impossible for j large. Hence for j large every regular row in X_g has q_i in [delta, mu + tau_j],
and every weak limit of the laws of q_i (laws on [0, 1], so subsequential limits exist) is supported on [delta, mu]
(the exceptional rows have vanishing proportion).

Step 6 (the limiting envelope). Pass to a subsequence with d_j -> d_* in [p, 1]; d_* is fixed from now on (later
subsequences are taken inside this one). By Step 2, pi_i and m_i converge in probability to d_*.
(a) d_* < 1. For j large, regular rows of X_g form a proportion tending to 1, and by Step 5 their q lie in
[delta, mu + tau_j]; choose one row per j and pass to a subsequence along which its q converges to some q in [delta, mu].
Combining z_in > L with the blue constraint on the red cell gives m (1 + L)_+^s < U, and r L -> A_{d_*}(q),
(1 + L)^s -> e^{beta A_{d_*}(q)}, so
    d_* e^{beta A_{d_*}(q)} <= U(q).                                                                    (10)
In logarithms, (10) says T_{d_*}(q) <= log x with T_d(q) = (1 + q/(beta(1 - q))) log d + w log(1 - q) + (w q/(1 - q)) log(q/mu);
T_d'(q) = [beta^{-1} log d + w log(q/mu)]/(1 - q)^2 <= 0 for d <= 1, q <= mu, so T_{d_*}(mu) <= log x, i.e.
    d_* <= [x/(1 - mu)^w]^{1/(1 + mu/(beta(1 - mu)))} < 1   (x < (1 - mu)^w).                                  (10')
Consequently, for j large every regular row in X_g has q_i >= delta > 0, m_i >= p/2 and m_i <= d_j + eta_j < 1, so Step 1
applies to it: E_nu Z_i <= S(m_i, U_i, L_i).
(b) Limsup lemma. If r_j -> infinity and (q_j, m_j, pi_j) -> (q, d, d) with q in [delta, mu] and d in (0, 1), and each
two-cell problem (m_j, U_j, L_j), U_j = U(q_j) = (mu/q_j)^{w beta}, s_j = beta r_j, with L_j = L(q_j, m_j, pi_j, r_j) from (5) is feasible, then
    limsup_j q_j r_j S(m_j, U(q_j), L_j) <= q M_d(q),   M_d := -infinity off F_d,
where F_d = {q : d e^{beta A_d(q)} < U(q)} (as for F). Proof: r_j L_j -> A_d(q), r_j (t_{U_j} - 1) -> w log(mu/q) = B(q), and
(1 + L_j)^{s_j} -> e^{beta A_d(q)}. If A_d(q) < B(q), eventually L_j < t_{U_j} - 1 and r S = r (t_U - 1) -> B = M_d. If
A_d(q) > B(q), eventually S is given by (4); R_j := (U_j - m_j (1 + L_j)^{s_j})/(1 - m_j) -> Rd := (U(q) - d e^{beta A_d})/(1 - d).
If Rd > 0, r_j (R_j^{1/s_j} - 1) -> beta^{-1} log Rd and r S -> d A_d + (1 - d) beta^{-1} log Rd = M_d(q). If Rd <= 0 (q not
in F_d), feasibility gives R_j > 0 and R_j -> 0+, and r (R_j^{1/s_j} - 1) -> -infinity (for y <= 0, e^y - 1 <= y e^y, and
e^y - 1 -> -1 as y -> -infinity), so q_j r_j S -> -infinity = q M_d(q). If A_d(q) = B(q), both expressions tend to B(q) =
M_d(q) (on any subsequence either case applies). []

Step 7 (passage to the limit). Jensen on (2) gives (1 + E_nu Z)_+^s < U, so for q > 0, q r E_nu Z <= q r[(mu/q)^{w/r} - 1]
<= w mu^{w/r} q^{1 - w/r} log(mu/q) for q <= mu (at most H0 := 2 w sqrt(mu)/e for r >= 2w), and <= 0 for q > mu; rows with
q = 0 contribute 0. So q r E_nu Z <= H0 for all rows. Let iota_i be the indicator of "regular and in X_g" and define the
Borel function omega_j(q, m, pi, iota) = H0 if iota = 0, and min{H0, q r_j S(m, (mu/q)^{w beta}, L(q, m, pi, r_j))} if
iota = 1 (with S = -infinity when infeasible, and omega_j = H0 where S is undefined, i.e. q = 0 or m not in (0, 1);
such points carry no mass for j large); put W_j = omega_j(q_i, m_i, pi_i, iota_i). For j large, q_i r E_nu Z_i <= W_j
on every row (Step 6 (a) and the H0 bound), so E_X[q r E_nu Z] <= E_X W_j. Inside the subsequence of Step 6 take a
further one along which the joint laws of (q_i, m_i, pi_i, iota_i) (i uniform in X_j) converge; Skorokhod represents
them on one probability space with a.s. convergence and the same laws, so E_X W_j = E omega_j(xi_j) there. In the limit,
m = pi = d_*, and iota^{(j)} -> 1 a.s.; iota is {0, 1}-valued, so a.s. iota^{(j)} = 1 for all large j, and q(omega) is in
[delta, mu] (Step 5). Almost surely each xi_j(omega) is an atom of the law of xi_j, i.e. an actual row, for which (z_in, z_out) is a feasible
pair of its two-cell problem (and in any case an infeasible term equals -infinity and only lowers the limsup). The
limsup lemma (Step 6 (b)) then gives limsup_j omega_j(xi_j) <= q M_{d_*}(q) a.s. (q M_{d_*}(q) is
Borel: the formula is continuous on the open set F_{d_*} and equals -infinity off it). Fatou applied to H0 - omega_j(xi_j) >= 0
gives limsup_j E_X[q r E_nu Z] <= int_0^1 Q(t) M_{d_*}(Q(t)) dt, Q the quantile of the limit law of q. For the lower bound,
(9) and (8) give E_X[q r E_nu Z] = r E[q (V - 1)] >= int_0^1 Q_j k_{r_j}, and
int Q_j k_{r_j} - int Q k_infinity = int Q_j (k_{r_j} - k_infinity) + int (Q_j - Q) k_infinity, k_infinity = -w (1 + log t):
the first term is at most ||k_{r_j} - k_infinity||_1 -> 0 (|Q_j| <= 1); the second tends to 0 by dominated convergence
(Q_j -> Q at the continuity points of the monotone Q, all but countably many; bound 2 |k_infinity|). Together
    int_0^1 [Q(t) M_{d_*}(Q(t)) + w Q(t)(1 + log t)] dt >= 0,                                               (11)
and the integral is finite.

Step 8 (from the limit to CERT). Fix q in (0, mu]. On the binding branch put e_A = e^{beta A}, y_z = (U - d e_A)/(1 - d);
there e_A > U > y_z > 0. With M = d A + ((1 - d)/beta) log y_z and U - e_A = (1 - d)(y_z - e_A):
beta dM/dd (A fixed) = log(e_A/y_z) + 1 - e_A/y_z <= 0 and dM/dA = d (1 - e_A/y_z) < 0, while dA_d/dd = (1 - q)/(q d) > 0.
So M_d(q) decreases in d; on the non-binding branch M_d = B, and the branches meet continuously. F_d = {d e^{beta A_d} < U}
shrinks as d grows, because d e^{beta A_d(q)} increases in d (both factors increase). Since d_* >= p: F_{d_*} in F and
M_{d_*} <= M on F_{d_*}. (11) is finite, so Q(t) in F_{d_*} for almost every t, and for such t
Q(t) M_{d_*}(Q(t)) + w Q(t)(1 + log t) <= sup_{q in F} [q M(q) + w q (1 + log t)]. Integrating, CERT >= 0. []

## P1.4 Claim P1.6 (used by Theorem A.9, SELF_CONTAINED Section 6.7)

Claim P1.6. Under the hypotheses of Proposition 3.5 other than "F nonempty and the integrand integrable" (that is, for
any sequence of configurations satisfying (i)-(iv) with r_j -> infinity, tau_j, zeta_j -> 0, c_j and H_j bounded and
liminf d_j >= p), every limit point d_* of d_j satisfies (10'), d_* <= [x/(1 - mu)^w]^{1/(1 + mu/(beta(1 - mu)))} < 1, and every
weak limit of the laws of q_i is supported on [delta, mu]. Proof: Steps 2, 5 and 6 (a), which use neither F nonempty nor
the integrability of CERT's integrand; Step 5 uses (5) of Step 1. []
