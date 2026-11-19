# P2. The finite-host closure: Lemmas 4.3-4.5 and Theorem 4.2 with full proofs

Draft 19 Nov 2026 (+04); v2 after its fresh referee (PASS, nine wording NITs applied; REFEREE_P2_20261119.md). Block P2
of UNCONDITIONAL_PLAN.md: ZBS Section 4 (preprint @ c2875f33) restated in our words with every step checked. Inputs:
Theorem 3.4 and Lemmas 3.1-3.2 (block P1; equations (2), (3) below are P1's (2), (3)), Erdos-Szekeres (ES), and the
notation of SELF_CONTAINED 6.1 with s = beta r > 1 as in P1 (6.1's s > 2 is needed only for Theorem A, not here) (hosts, Phi_c(X, Y) = |X|^w |Y| H_c(X, Y)^r, maximal pairs in the one-sided
sense, N = |X|, M = |Y|, u_y = g_y - c, H = H_c(X, Y), pi_v the red density of row v to Y, B_v, R_v the blue and red
neighbourhoods of v in X, q_v = |B_v|/N, Y_v the red neighbourhood of v in Y, b_v(y) the red density from B_v to y
(any value, e.g. 0, if B_v is empty; it is then always multiplied by q_v = 0). Standing hypotheses: w > 0,
0 < beta < 1, r > w, s = beta r > 1.
Stop(C, xhat, yhat, l) is as in P4.1. An outcome for a pair (X, Y) with targets (k, t) and l is a red K_k in X ∪ Y, a
blue K_t in X or a blue K_l in Y.

## P2.1 Lemma 4.3 (good pages)

Lemma 4.3. Let w > 0, 0 < beta < 1, r > w, s = beta r > 1, let (X, Y) be maximal with H > 0 and put D_r = w/(r - w) + 1 - (1 - beta)^{1/(beta r)} and
G = {v in X : pi_v >= c}. Then 1 - |G|/|X| <= D_r.
Proof. For t > 1 let A_t be the set of rows with pi_v >= c + H t (if A_t is empty there is nothing to prove). The column densities of A_t average to the average of
pi over A_t, which is at least c + H t, so H_c(A_t, Y) >= E_Y (g^{A_t} - c)_+ >= H t (power mean, s >= 1). Maximality
(Phi_c(A_t, Y) <= Phi_c(X, Y)) gives (|A_t|/N)^w t^r <= 1, i.e. Pr_X(pi_v >= c + H t) <= t^{-r/w}. By the layer-cake
formula, E_X (pi - c - H)_+ = H int_0^infinity Pr(pi > c + H(1 + tau)) dtau <= H int_0^infinity (1 + tau)^{-r/w} dtau =
H w/(r - w). Since E_X pi_v = c + alpha with alpha = E_Y u_y >= (1 - beta)^{1/s} H (Lemma 3.1),
E_X (c + H - pi)_+ = E_X (pi - c - H)_+ - (alpha - H) <= D_r H. A row outside G has (c + H - pi_v)_+ > H; Markov. []

## P2.2 Lemma 4.4 (blue book with good pages)

Lemma 4.4. Let X be a nonempty vertex set, N = |X|, G in X. Let 0 < theta < tau < 1, D real, and b <= m positive
integers with 1 - |G|/N <= D <= 1/4, m/N <= 1/4 and D + m/N + b/m <= tau - theta. Let W be the set of v in X with at
least tau N blue neighbours in X, and let k >= 1 be an integer. If |W| >= R(k, m), then X contains a red K_k, or there are disjoint S, T in X with S a
blue clique of exactly b vertices, all S-T edges blue, T in G and |T| >= theta^b N/2.
Proof. If W has no red K_k it contains a blue clique U with |U| = m. Let P = G \ U; |P| >= (1 - D) N - m >= N/2. Each
u in U has at least (tau - D) N - m blue neighbours in P (at least tau N in X, at most D N outside G, at most m in U), so
the blue density sigma between U and P is at least ((tau - D) N - m)/|P| >= tau - D - m/N >= theta + b/m (the
numerator (tau - D) N - m is positive by the hypothesis, and |P| <= N). Choose a uniformly random b-subset S of
U and let T be the set of z in P blue to all of S. If z has j_z blue neighbours in U, Pr(z in T) = binom(j_z, b)/binom(m, b);
the piecewise-linear extension of j -> binom(j, b) is convex and nondecreasing, and j_z averages sigma m over P, so
E|T| >= |P| binom(floor(sigma m), b)/binom(m, b) >= |P| (sigma - b/m)^b >= (N/2) theta^b (each factor
(floor(sigma m) - i)/(m - i), 0 <= i < b, is at least sigma - b/m > 0). Some S attains |T| >= E|T|. []

## P2.3 Lemma 4.5 (local alternative)

Lemma 4.5. Let p, mu, w, beta, x satisfy the hypotheses of Theorem 3.4 (0 < x < min{p, (1 - mu)^w}, F nonempty,
CERT < 0), and fix an integer N0 with N0 (1 - mu) > 1. There are eta, tau, zeta > 0 and R0 with eta < min{p, 1 - p},
cap := mu + tau < 1 - 1/N0, R0 > w and beta R0 > 1 such that for every r >= R0: if (X, Y) is maximal for Phi_c with
|c - p| <= eta, N >= N0, H > 0, and at most zeta N rows have q_v > cap, then for every Delta >= (1 - c)/(N(1 - cap) - 1)
and c' = c - Delta,
 (RED) some v with q_v <= cap has Phi_{c'}(R_v, Y_v) >= x Phi_c(X, Y), or
 (BLUE) some v has Phi_c(B_v, Y) >= mu^w Phi_c(X, Y).
Proof. Take eta, tau, zeta, R0 from Theorem 3.4 and shrink eta, tau to meet the side conditions; shrinking keeps Theorem
3.4 true (its conclusion excludes configurations, and smaller eta, tau allow fewer). Suppose both alternatives fail and
apply Theorem 3.4 with BB the blue graph (P1's notation). (i): Lemma 3.1. (ii): given. (iii): failure of (BLUE) at v with q_v > 0 reads
(q_v N)^w M H_c(B_v, Y)^r < mu^w N^w M H^r; raising to beta and using H_c(B_v, Y)^s = (1/M) sum_y (b_v(y) - c)_+^s and
H^s = (1/M) sum_y (u_y)_+^s gives P1's (2). (iv): let X_g = {v : q_v <= cap}; |X \ X_g| <= zeta N. Fix v in X_g; then
sigma_v := |R_v|/N = 1 - 1/N - q_v > 0. For y in Y_v let rho_y be the red density from R_v to y. The red neighbours of y
in X = {v} ∪ B_v ∪ R_v number N g_y = 1 + q_v N b_v(y) + sigma_v N rho_y, so
    sigma_v (rho_y - c') = (1 - q_v) u_y - q_v (b_v(y) - g_y) + [sigma_v Delta - (1 - c)/N],
and the bracket is >= 0 because N sigma_v = N - 1 - q_v N >= N(1 - cap) - 1 and Delta >= (1 - c)/(N(1 - cap) - 1).
Y_v is nonempty: with a = u/H and J = E_Y a^{s-1} > 0, E_Y[h_{vy} a_y^{s-1}] = H V_v + c J > 0 (V_v >= 1 - w/r > 0 by
Lemma 3.2, c >= p - eta > 0). Failure of (RED) at v, raised to beta, is
|R_v|^{w beta} |Y_v|^{beta} (1/|Y_v|) sum_{Y_v} (rho - c')_+^s < x^beta N^{w beta} M^{beta} (1/M) sum_Y u^s, i.e.
sum_{Y_v} (rho_y - c')_+^s < x^beta sigma_v^{-w beta} pi_v^{1 - beta} sum_Y u_y^s. Multiplying by sigma_v^s, using the
identity (the bracket is >= 0, so sigma_v (rho - c') >= (1 - q_v) u - q_v (b_v - g)), sigma_v <= 1 - q_v and
s - w beta > 0, we get P1's (3) at v. So (i)-(iv) of Theorem 3.4 hold, a contradiction. []

## P2.4 Theorem 4.2 (finite-host closure)

Theorem 4.2. Let 0 < p, mu, beta < 1, w > 0, 0 < x < min{p, (1 - mu)^w}, F nonempty and CERT(p, mu, w, beta, x) < 0.
Let xi, y0, nu, xhat, yhat in (0, 1) with xi < min{x, xhat}, y0 < yhat, nu < mu. There is an integer L0, depending only
on these ten numbers, such that: for C >= 1, l >= L0, a host on V satisfying Stop(C, xhat, yhat, l), integers k, t >= 1
and disjoint nonempty X, Y in V with d_R(X, Y) >= p and |X|^w |Y| >= C^{w+1} xi^{-k} y0^{-l} nu^{-w t}, the pair (X, Y)
has an outcome with targets (k, t) and l.

Proof. Parameters (chosen before C, the host, k, l, t). Choose lambda, y with xi < lambda < min{x, xhat} and
y0 < y < yhat. Fix N0 with N0 (1 - mu) > 1 and take eta, tau, zeta, R0, cap from Lemma 4.5; choose theta with
mu < theta < cap; fix r >= R0 with D_r < min{1/4, (cap - theta)/2} (D_r -> 0 as r -> infinity); fix
0 < delta < min{p/2, eta}; for n >= 2 let c_n = p - delta/n and Phi_n = Phi_{c_n}. Put script-A = min{lambda/xi,
(mu/nu)^w} > 1, h = cap - theta - D_r > 0, a0 = min{(1/w) log(xhat/lambda), (1/w) log(yhat/y), log(1/mu)} > 0, and for
n >= 4
    b_n = max{1, ceil((r log(n^2/delta) + w log 2)/(w log(theta/mu)))},   m_n = ceil(2 b_n/h)
(both O(log n); b_n <= m_n). Let kappa0 = inf_{n >= 2} script-A^n/n^r > 0. For 2 <= k <= n, R(k, m) <= n^{m-1} (ES:
binom(k + m - 2, m - 1) is the number of multisets of size m - 1 from k types, at most k^{m-1}), and n^{m_n - 1} =
e^{O((log n)^2)}, so
    K1 = sup_{n >= 4} e^{-a0 n} max{N0, 4 m_n, 2 m_n/h, n^{m_n - 1}/zeta, (1 + n(n-1)/delta)/(1 - cap)} < infinity.
Let L0 >= 1 be an integer with (y/y0)^{L0} delta^r kappa0 >= 1 and e^{a0 L0} >= K1.
Induction. Fix C >= 1, l >= L0 and a host satisfying Stop(C, xhat, yhat, l). By strong induction on n = k + t:
  (I_n) for all integers k, t >= 1 with k + t = n, every disjoint nonempty pair X, Y with
        Phi_n(X, Y) >= C^{w+1} lambda^{-k} y^{-l} mu^{-w t} has an outcome.
If k = 1 or t = 1, any vertex of X is an outcome.
The theorem follows from (I_n): H_{c_n}(X, Y) >= E_Y (g_y - c_n)_+ >= d_R(X, Y) - c_n >= delta/n (power mean), so
Phi_n(X, Y)/(C^{w+1} lambda^{-k} y^{-l} mu^{-wt}) >= (delta/n)^r (lambda/xi)^k (y/y0)^l (mu/nu)^{wt} >=
(y/y0)^l delta^r script-A^n/n^r >= 1.
Inductive step (k, t >= 2, n >= 4). Among all pairs of nonempty subsets of X and of Y choose one maximising Phi_n; it is
maximal (one-sided), its potential is at least Phi_n(X, Y), and an outcome for it is one for (X, Y); rename it (X, Y).
N = |X|, M = |Y|, H = H_{c_n}(X, Y) in (0, 1], so Phi_n <= N^w M.
If M >= C xhat^{-k} yhat^{-l}: Y is a proper subset of V (X is nonempty and disjoint from it), and the stopping rule
gives a red K_k or a blue K_l in Y. Otherwise N^w M >= Phi_n >= C^{w+1} lambda^{-k} y^{-l} mu^{-wt} and
M < C xhat^{-k} yhat^{-l} give N > C (xhat/lambda)^{k/w} (yhat/y)^{l/w} mu^{-t} >= e^{a0 (n + l)} >= e^{a0 n} K1. So
N >= N0, N >= 4 m_n, N >= 2 m_n/h, R(k, m_n) <= n^{m_n - 1} <= zeta N and N (1 - cap) - 1 >= n(n-1)/delta.
Book case: at least R(k, m_n) rows have q_v >= cap. Lemma 4.3 gives 1 - |G|/N <= D_r for G = {v : pi_v >= c_n}. Lemma
4.4 applies with tau = cap, D = D_r, b = b_n, m = m_n: D_r <= 1/4, m_n/N <= 1/4, m_n/N <= h/2, b_n/m_n <= h/2, so
D_r + m_n/N + b_n/m_n <= D_r + h = cap - theta; W = {v : q_v >= cap} has |W| >= R(k, m_n). It gives a red K_k, or a blue
b_n-clique S and T in G with |T| >= theta^{b_n} N/2, all S-T edges blue. If b_n >= t, S contains a blue K_t. If
b := b_n < t: then n - b >= k + 1 >= 3, so c_{n-b} is defined; the columns of T have average red density
d_R(T, Y) = avg_{v in T} pi_v >= c_n, so H_{c_{n-b}}(T, Y) >= c_n - c_{n-b} = delta b/(n(n - b)) >= delta/n^2, and
    Phi_{n-b}(T, Y)/Phi_n(X, Y) >= (|T|/N)^w (delta/n^2)^r >= 2^{-w} theta^{wb} (delta/n^2)^r >= mu^{wb}
by the choice of b_n. So (I_{n-b}) applies to (T, Y) with targets (k, t - b); a blue K_{t-b} in T together with S is a
blue K_t in X, and the other outcomes are outcomes.
Local case: fewer than R(k, m_n) <= zeta N rows have q_v >= cap. Apply Lemma 4.5 with c = c_n (|c_n - p| = delta/n <=
eta) and Delta = c_n - c_{n-1} = delta/(n(n-1)) >= (1 - c_n)/(N (1 - cap) - 1) (because N(1 - cap) - 1 >= n(n-1)/delta > 0
and 0 < 1 - c_n < 1). The cap hypothesis of Lemma 4.5 holds: #{q_v > cap} <= #{q_v >= cap} < R(k, m_n) <= zeta N. In
case (RED),
Phi_{n-1}(R_v, Y_v) = Phi_{c'}(R_v, Y_v) >= x Phi_n(X, Y) >= C^{w+1} lambda^{-(k-1)} y^{-l} mu^{-wt} (x > lambda); by
(I_{n-1}) with targets (k - 1, t), a red K_{k-1} in R_v ∪ Y_v together with v is a red K_k; the other outcomes are
outcomes. In case (BLUE), lowering the shift to c_{n-1} can only increase H, so Phi_{n-1}(B_v, Y) >= mu^w Phi_n(X, Y)
>= C^{w+1} lambda^{-k} y^{-l} mu^{-w(t-1)}; by (I_{n-1}) with targets (k, t - 1), a blue K_{t-1} in B_v together with v is
a blue K_t in X. []
