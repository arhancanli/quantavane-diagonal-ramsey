# P4. The source bound (Lu-Wang's Theorem 2.2) for one fixed epsilon: statements and full proofs

Draft 19 Nov 2026 (+04); v2 after its fresh referee (PASS WITH FIXES: two local errors corrected (a constant in
(A.4), a missing hypothesis in P4.5), concavity now certified by two programs, NITs applied; REFEREE_P4_20261119.md).
Block P4 of UNCONDITIONAL_PLAN.md. It replaces the assumption of
"ZBS Theorem 2.2 = Lu-Wang (32)" (Lu, Wang, "Retained-Set Descent for Diagonal Ramsey Numbers", arXiv:2609.14525 v1,
paper.pdf of github.com/sichen-wang/diagonal-ramsey-numbers @ 5ec98f47, SHA-256 cd03ef58...dc968c) by proofs written
here and two certified computations of our own. The arguments of P4.2-P4.4 are Lu and Wang's (their Lemma A.1,
Corollary A.2, Lemma B.1), which in turn adapt the candidate induction of Gupta, Ndiaye, Norin and Wei; we restate
them in our words with every step checked, and modify Lemma B.1 to a fixed epsilon (all that ZBS's Theorem 5.7 uses).
All logarithms are natural. The only external result used is the Erdos-Szekeres bound
    R(a, b) <= binom(a + b - 2, a - 1)                                                              (ES)
(refereed, 1935), with the entropy form log binom(k + l, l) <= k h(l/k) for 1 <= l <= k, where
    h(s) = (1 + s) log(1 + s) - s log s,  h(0) = 0
((k + l) H(l/(k + l)) = k h(l/k) for the binary entropy H, and binom(n, m) <= e^{n H(m/n)}); h is increasing on [0, 1].

## P4.1 Notation

A host is a red/blue colouring of the edges of a complete graph on a finite vertex set V. For disjoint nonempty X, Y,
d_R(X, Y) = e_R(X, Y)/(|X||Y|). N_R(v), N_B(v) are the red and blue neighbourhoods of v; deg_chi(v, Z) = |N_chi(v) ∩ Z|.
A candidate is an ordered pair (X, Y) of disjoint nonempty vertex sets; it is (k, l, t)-good if X ∪ Y contains a red
K_k, or X contains a blue K_t, or Y contains a blue K_l. For reals C >= 1, xhat, yhat in (0, 1) and an integer l >= 1,
a host satisfies Stop(C, xhat, yhat, l) if for every integer a >= 1 every proper subset Z of V with
|Z| >= C xhat^{-a} yhat^{-l} contains a red K_a or a blue K_l (ZBS's Definition 4.1).
For a continuous F on [0, 1] with F(0) = 0 put G_F(a, b) = max(a, b) F(min(a, b)/max(a, b)) for a, b > 0, and
    B_F = {(X, Y) in (0, 1)^2 : G_F(a, b) <= -a log X - b log Y for all a, b > 0}.
With F-hat(lambda) = F(lambda) on (0, 1] and lambda F(1/lambda) on [1, infinity) one has G_F(a, b) = b F-hat(a/b), so
(X, Y) is in B_F iff F-hat(lambda) <= A lambda + B for all lambda > 0, where A = -log X, B = -log Y. B_F is closed
downward: (X, Y) in B_F and X' <= X, Y' <= Y give (X', Y') in B_F.

## P4.2 Lemma A.1 (finite-host weighted candidate bound)

Lemma A.1. Fix w > 0 and x0, y0, xhat, yhat, mu0, p in (0, 1) with x0 < xhat, y0 < yhat and
    x0 < (1 - mu0)^w p^{1/(1 - mu0)}.
There is L0, depending only on these numbers, such that: for every C >= 1, every host, and every integer l >= L0 such
that the host satisfies Stop(C, xhat, yhat, l), every candidate (X, Y) with
    d_R(X, Y) >= p   and   |X|^w |Y| >= C^{w+1} x0^{-k} y0^{-l} mu0^{-w t}                               (A.1)
is (k, l, t)-good, for all integers k, t >= 1.

Proof. Step 0 (parameters, fixed before C, the host, k, l, t). Choose an integer r > max{1, w} with p^{1/r} > mu0 and
    x0 < (p^{1/r} - mu0)^r (1 - mu0)^{w - r}.                                                       (A.2)
This is possible: p^{1/r} - mu0 = (1 - mu0) + (log p)/r + O(r^{-2}), so the logarithm of the right side of (A.2) is
r log(1 - mu0) + (log p)/(1 - mu0) + O(1/r) + (w - r) log(1 - mu0), which tends to log((1 - mu0)^w p^{1/(1 - mu0)}),
strictly above log x0. For x, mu in (0, 1) put phi_{x,mu}(q) = x^{1/r} (1 - q)^{1 - w/r} + mu^{w/r} q^{1 - w/r} on
[0, 1]. (A.2) raised to the power 1/r says phi_{x0,mu0}(mu0) = x0^{1/r}(1 - mu0)^{1 - w/r} + mu0 < p^{1/r}. Since
1 - w/r > 0, phi_{x0,mu0}'(q) has the sign of mu0^{w/r} q^{-w/r} - x0^{1/r}(1 - q)^{-w/r}, which is >= 0 iff
q <= mu0/(mu0 + x0^{1/w}); this threshold exceeds mu0 because x0 < (1 - mu0)^w. So phi_{x0,mu0} is increasing on
[0, mu0] and max_{[0, mu0]} phi_{x0,mu0} < p^{1/r}. The map (x, mu, beta) -> max_{[0, beta]} phi_{x,mu} is continuous,
so we can choose x0 < x < xhat, y0 < y < yhat, mu0 < mu < beta < 1, 0 < delta < p/2 and gamma > 0 with
    max_{0 <= q <= beta} phi_{x,mu}(q) <= (1 - gamma) pbar^{1/r},   pbar := p - delta.                      (A.3)
Put kappa0 = inf_{n >= 2} c^n/n^r > 0 with c = min{x/x0, (mu/mu0)^w} > 1, and a constant c1 > 0 with
xhat/x >= e^{w c1}, yhat/y >= e^{w c1} and 1/mu >= e^{c1} (possible since all three exceed 1).

Step 1 (a stronger statement). For n = k + t put delta_n = delta/n. We prove by induction on n, for fixed l >= L0 (L0
chosen at the end), the statement
  (I_n) every candidate (X, Y) with d_R(X, Y) >= p - delta_n and
        Q_n(X, Y) := (d_R(X, Y) - p + delta_n)^r |X|^w |Y| >= C^{w+1} x^{-k} y^{-l} mu^{-w t}
        is (k, l, t)-good.
(A.1) implies the hypothesis of (I_n): d_R >= p gives d_R - p + delta_n >= delta/n, so Q_n >= (delta/n)^r |X|^w |Y| >=
C^{w+1} x^{-k} y^{-l} mu^{-wt} times (delta/n)^r (x/x0)^k (y/y0)^l (mu/mu0)^{wt} >= delta^r kappa0 (y/y0)^l, which is
>= 1 once (y/y0)^l delta^r kappa0 >= 1 (a condition on L0). If k = 1 or t = 1, any vertex of X is a red K_1 or a blue
K_1, so the candidate is good. Let k, t >= 2 (so n >= 4) and assume (I_{n'}) for n' < n.

Step 2 (regularise; stop if Y is large). Delete from X, one at a time, vertices with fewer than (p - delta_n)|Y| red
neighbours in Y. With E = e_R(X, Y) - (p - delta_n)|X||Y| we have Q_n = E^r |X|^{w - r} |Y|^{1 - r}; a deletion
increases E and decreases |X|, and w - r < 0, so Q_n does not decrease. Q_n > 0 gives E > 0, so some vertex has more
than (p - delta_n)|Y| red neighbours and is never deleted: X stays nonempty. Goodness of the new pair implies goodness
of the old one. Now every nonempty T in X has d_R(T, Y) >= p - delta_n. If |Y| >= C xhat^{-k} yhat^{-l}: Y is a proper
subset of V (X is nonempty and disjoint from Y), and Stop with a = k gives a red K_k or a blue K_l in Y. Otherwise,
since Q_n <= |X|^w |Y|,
    |X|^w > C^w (xhat/x)^k (yhat/y)^l mu^{-w t},  hence  |X| >= C e^{c1 (k + l + t)} >= e^{c1 (n + l)}.          (A.4)

Step 3 (constants of the book step). Put
    b = ceil((2 r log n + r log(1/delta) + w log 2)/(w log(beta/mu))),  m = ceil(10 b^2/beta),  xi_n = delta/(2 n^2),
W = {v in X : deg_B(v, X) >= beta |X|}. We need
    |X| >= 5 m^2,   R(k, m) < pbar xi_n |X|,   2 n^2/(delta |X|) < gamma.                                    (A.5)
b = O(log n), m = O((log n)^2) and R(k, m) <= binom(k + m - 2, m - 1) <= n^{m - 1} = e^{O((log n)^3)} (ES; the binomial
counts multisets of size m - 1 from k symbols, at most k^{m-1} <= n^{m-1}), so each lower bound on |X| required by
(A.5) is at most e^{K0 (log n)^3} for a constant K0 (n >= 4, so log n > 1 and K0 absorbs additive constants); by (A.4) it suffices that
c1 (n + l) >= K0 (log n)^3 for all n >= 4, which holds for all l >= L0 with L0 large. So (A.5) holds.

Step 4 (many high blue degrees: a blue book). Suppose |W| >= R(k, m). Then W contains a red K_k (done) or a blue
clique U with |U| = m. Each u in U has at least beta |X| - m blue neighbours in X \ U, so the blue density sigma between
U and X \ U satisfies sigma >= (beta |X| - m)/(|X| - m) = beta - (1 - beta) m/(|X| - m) >= beta - 1/(4m) (as
|X| - m >= 4 m^2 by (A.5)). Pick a uniformly random b-subset S of U and let T be the set of vertices of X \ U joined in
blue to all of S. If z in X \ U has j_z blue neighbours in U, then Pr(z in T) = binom(j_z, b)/binom(m, b); the
piecewise-linear extension of j -> binom(j, b) is convex and nondecreasing, and the average of j_z is sigma m, so
E|T| >= (|X| - m) binom(floor(sigma m), b)/binom(m, b) >= (|X| - m)(sigma - b/m)^b (each factor
(floor(sigma m) - i)/(m - i), 0 <= i < b, is at least sigma - b/m > 0). Since m >= 10 b^2/beta,
sigma - b/m >= beta - beta/(40 b^2) - beta/(10 b) >= beta (1 - 1/(8b)), so by Bernoulli (sigma - b/m)^b >= (7/8) beta^b,
and |X| - m >= (4/5)|X|; hence E|T| >= (7/10) beta^b |X|. Fix S with |T| >= beta^b |X|/2; S is a blue b-clique, all
S-T edges are blue, S ∩ T is empty. If b >= t, S contains a blue K_t in X. If b < t: delta_{n-b} - delta_n >= delta/n^2,
and d_R(T, Y) >= p - delta_n (Step 2), so d_R(T, Y) - p + delta_{n-b} >= delta/n^2 and
    Q_{n-b}(T, Y) >= (delta/n^2)^r 2^{-w} beta^{w b} |X|^w |Y| >= (delta/n^2)^r 2^{-w} beta^{wb} Q_n >= mu^{wb} Q_n
                 >= C^{w+1} x^{-k} y^{-l} mu^{-w(t - b)},
using Q_n <= |X|^w |Y| and (beta/mu)^{wb} >= 2^w (n^2/delta)^r (the choice of b). By (I_{n-b}), (T, Y) is
(k, l, t - b)-good; a blue K_{t-b} in T together with S is a blue K_t in X, and the other outcomes are outcomes.

Step 5 (few high blue degrees: one vertex). Suppose |W| < R(k, m) < pbar xi_n |X|. Let Y_v = N_R(v) ∩ Y,
d = d_R(X, Y) and E0 = e_R(X, Y) >= pbar |X||Y| (Step 2: every row has at least (p - delta_n)|Y| >= pbar |Y| red
neighbours). Counting through Y and Cauchy-Schwarz:
    sum_{v in X} d_R(X, Y_v) |Y_v| = (1/|X|) sum_{y in Y} deg_R(y, X)^2 >= E0^2/(|X||Y|) = d E0.
The terms with v in W total at most |W||Y| < pbar xi_n |X||Y| <= xi_n E0, so
sum_{v not in W} d_R(X, Y_v)|Y_v| > (d - xi_n) E0 >= (d - xi_n) sum_{v not in W} |Y_v|, and some v not in W has
d_R(X, Y_v) >= d - xi_n (with |Y_v| >= pbar |Y| > 0). Put Y' = Y_v, X_R = N_R(v) ∩ X, X_B = N_B(v) ∩ X,
a = |X_R|/|X|, q = |X_B|/|X|, so a + q = 1 - 1/|X| and q < beta (v not in W). Put
alpha = d_R(X, Y') - p + delta_{n-1} >= (d - p + delta_n) + (delta_{n-1} - delta_n - xi_n) >= d - p + delta_n + delta/(2n^2)
> 0, and for chi in {R, B}: alpha_chi = d_R(X_chi, Y') - p + delta_{n-1} if X_chi is nonempty, alpha_chi = 0 otherwise;
Q_chi = (alpha_chi)_+^r |X_chi|^w |Y'|. Counting the red edges between X = {v} ∪ X_R ∪ X_B and Y' (v is red to all of
Y') gives d_R(X, Y') = a d_R(X_R, Y') + q d_R(X_B, Y') + 1/|X|; subtracting (p - delta_{n-1})(a + q + 1/|X|),
    alpha = a alpha_R + q alpha_B + (1 - p + delta_{n-1})/|X|,  so  1 <= a (alpha_R)_+/alpha + q (alpha_B)_+/alpha + 1/(alpha |X|)
(1 - p + delta_{n-1} <= 1 as delta < p/2). Claim: Q_R >= x Q_n or Q_B >= mu^w Q_n. If both fail, use
Q_n <= alpha^r |X|^w |Y| (alpha >= d - p + delta_n) and |Y'| >= pbar |Y|: (alpha_R)_+/alpha < (x/pbar)^{1/r} a^{-w/r}
(if a > 0) and (alpha_B)_+/alpha < (mu^w/pbar)^{1/r} q^{-w/r} (if q > 0); terms with a = 0 or q = 0 vanish. Then
    1 < pbar^{-1/r} {x^{1/r} a^{1 - w/r} + mu^{w/r} q^{1 - w/r}} + 1/(alpha |X|)
      <= pbar^{-1/r} phi_{x,mu}(q) + 2n^2/(delta |X|) <= (1 - gamma) + 2n^2/(delta |X|) < 1
(a <= 1 - q and 1 - w/r > 0; (A.3) with q < beta; alpha >= delta/(2n^2); (A.5)), a contradiction. If Q_R >= x Q_n, then
Q_R > 0 so alpha_R > 0, i.e. d_R(X_R, Y') > p - delta_{n-1}, and Q_{n-1}(X_R, Y') = Q_R >= x C^{w+1} x^{-k} y^{-l}
mu^{-wt} = C^{w+1} x^{-(k-1)} y^{-l} mu^{-wt}: by (I_{n-1}) with targets (k - 1, t), (X_R, Y') is (k - 1, l, t)-good,
and a red K_{k-1} in X_R ∪ Y' together with v (red to all of X_R and Y') is a red K_k in X ∪ Y; the other outcomes
are outcomes. If Q_B >= mu^w Q_n, then likewise Q_{n-1}(X_B, Y') >= C^{w+1} x^{-k} y^{-l} mu^{-w(t-1)}: by (I_{n-1})
with targets (k, t - 1), a blue K_{t-1} in X_B together with v (blue to all of X_B) is a blue K_t in X.

Step 6 (L0). L0 is any integer with (y/y0)^{L0} delta^r kappa0 >= 1 and c1 (n + L0) >= K0 (log n)^3 for all
n >= 4; it depends only on the fixed parameters. []

## P4.3 Corollary A.2 (local density bound)

Corollary A.2. Fix w > 0 and mu, p, x, y, xhat, yhat in (0, 1) with x < xhat, y < yhat and
x < (1 - mu)^w p^{1/(1 - mu)}. There is L1 = L1(w, mu, p, x, y, xhat, yhat) such that for every C >= 1, every integer
l >= L1, every integer k >= 1 and every host satisfying Stop(C, xhat, yhat, l) with red density at least p and order
    N >= C x^{-k/(w+1)} (y mu^w)^{-l/(w+1)},                                                        (A.6)
the host contains a red K_k or a blue K_l.
Proof. Choose y < y1 < yhat (depending only on y, yhat). A uniformly random subset of floor(N/2) vertices separates
every pair of vertices with the same probability, so the expected number of red edges across the cut is the same
multiple of e_R(V) as the expected number of all pairs across is of binom(N, 2): some cut V = X ⊔ Y with
|X|, |Y| >= floor(N/2) >= N/3 (N >= 3) has d_R(X, Y) >= d_R(V) >= p (ZBS Lemma 2.1, reproved by this sentence). Then
|X|^w |Y| >= (N/3)^{w+1} >= 3^{-(w+1)} C^{w+1} x^{-k} y^{-l} mu^{-wl} >= C^{w+1} x^{-k} y1^{-l} mu^{-wl} once
(y1/y)^l >= 3^{w+1}. Lemma A.1 with (x0, y0, mu0) = (x, y1, mu), t = l, applies for l >= L0(x, y1, xhat, yhat, mu, p, w),
so (X, Y) is (k, l, l)-good: a red K_k in X ∪ Y or a blue K_l in X or in Y. (N >= 3 holds for l large by (A.6).) []

## P4.4 Lemma B.1' (source criterion for one fixed epsilon)

Lemma B.1'. Let F: [0, 1] -> R be continuous with F(0) = 0, C^1 and concave on (0, 1], with F' > 0 on (0, 1]. Let
eps > 0 and alpha in (0, 1) with h(alpha) < eps/2. Suppose that for every s in [alpha, 1] there are w > 0 and
mu, Y in (0, 1) such that, with p0(s) = 1 - e^{-F'(s)} and X = (1 - mu)^w p0(s)^{1/(1 - mu)}, the pair (X, Y) is in B_F and
    (w + 1) F(s) + log X + s log Y + w s log mu > 0.                                                (B.1)
Then there is C_eps >= 1 such that for all integers a, b >= 1 and N >= C_eps exp(G_F(a, b) + eps(a + b)), every host
of order N contains a red K_a or a blue K_b.
(Lu and Wang assume (B.1) for all s in (0, 1] and conclude for every eps; their proof uses, for a given eps, only
s >= alpha with h(alpha) < eps/2, which is what is stated here.)

Proof. F >= 0 on [0, 1] (F(0) = 0, F' > 0). For x, y in (0, 1), mu in (0, 1), w > 0 put
H_{x,y}(t) = (-log x + t(-log y - w log mu))/(w + 1); (B.1) says H_{X,Y}(s) < F(s).
Local bounds. Fix s0 in [alpha, 1] with its w, mu, X, Y from the hypothesis, and put xbar = e^{-eps} X,
ybar = e^{-eps} Y. Then H_{xbar,ybar}(s0) = H_{X,Y}(s0) + eps(1 + s0)/(w + 1) < F(s0) + eps(1 + s0). Choose
x < xhat < xbar, y < yhat < ybar and p < p0(s0), so close to (xbar, ybar, p0(s0)) that x < (1 - mu)^w p^{1/(1 - mu)} (the
right side tends to X > xbar as p -> p0(s0)) and H_{x,y}(s0) < F(s0) + eps(1 + s0). F, F' are continuous at s0 > 0, so
there are an open neighbourhood O(s0) and eta(s0) > 0 with H_{x,y}(s) < F(s) + eps(1 + s) and p0(s) > p + 2 eta(s0) for
s in O(s0) ∩ [alpha, 1]. Every selected pair satisfies
    -a log xhat - b log yhat >= G_F(a, b) + eps(a + b)   (a, b > 0),                                     (B.2)
because -log xhat > -log X + eps, -log yhat > -log Y + eps and G_F(a, b) <= -a log X - b log Y ((X, Y) in B_F).
[alpha, 1] is compact: finitely many O(s0) cover it; let eta > 0 be the least eta(s0) and L >= 2 the largest of the
thresholds L1 of Corollary A.2 for the finitely many local bounds (independent of C).
Constants. Choose an integer K with alpha K >= L, and C_eps = C >= max{3, 2/eta, 4^K}.
Smallest counterexample. Suppose some host of order N >= C exp(G_F(a, b) + eps(a + b)) has no red K_a and no blue K_b;
take one of least order N over all pairs (a, b) and all such hosts. Rename the colours if needed (G_F is symmetric) so
that the targets are (k, l) with k >= l; then G_F(k, l) = k F(l/k).
- If k < K: by (ES), R(k, l) <= binom(k + l - 2, k - 1) <= 2^{k + l} <= 4^K <= C <= N, a contradiction.
- If s := l/k <= alpha: log R(k, l) <= log binom(k + l, l) <= k h(s) <= k h(alpha) < eps k/2 <=
  k F(s) + eps(k + l) + log C (F >= 0), so R(k, l) <= N, a contradiction.
- So s in [alpha, 1] and l = sk >= alpha K >= L. Take the local bound (w, mu, x, y, xhat, yhat, p) selected at a point
  whose neighbourhood contains s. Stop(C, xhat, yhat, l) holds: a proper subset Z with |Z| >= C xhat^{-a} yhat^{-l}
  has |Z| >= C exp(G_F(a, l) + eps(a + l)) by (B.2), and has smaller order, so by minimality it contains a red K_a or
  a blue K_l.
  - If the host's red density is at least p0(s) - eta (> p + eta > p): N >= C exp(k F(s) + eps(k + l)) >
    C exp(k H_{x,y}(s)) = C x^{-k/(w+1)} (y mu^w)^{-l/(w+1)}, and Corollary A.2 (l >= L) gives a red K_k or a blue K_l,
    a contradiction.
  - Otherwise the blue density exceeds q := e^{-F'(s)} + eta (< 1). Some vertex v has blue degree at least
    q (N - 1) = N e^{-F'(s)} + (eta N - q) > N e^{-F'(s)} (eta N >= 2 > q). Let Z be its blue neighbourhood.
    Concavity gives F(s - 1/k) <= F(s) - F'(s)/k, so
        |Z| > N e^{-F'(s)} >= C exp(k F(s) - F'(s) + eps(k + l)) >= C exp(k F((l - 1)/k) + eps(k + l - 1))
          = C exp(G_F(k, l - 1) + eps(k + l - 1))
    (l - 1 <= k). If l = 1 the host itself contains a blue K_1; otherwise Z, of smaller order, contains a red K_k or a
    blue K_{l-1} by minimality, and a blue K_{l-1} in Z together with v is a blue K_l. A contradiction.
Hence there is no counterexample. []

## P4.5 Lemma (concavity of f-hat and its conjugate)

Lemma P4.5. Let f be continuous on [0, 1], f(0) = 0, C^1 on (0, 1] and piecewise C^2 with f'' < 0 on every piece,
f'(t) -> +infinity as t -> 0+, and 2 f'(1) > f(1), f'(1) > 0. Then:
 (i) f-hat is strictly concave on (0, infinity) and increasing (its one-sided derivatives are positive everywhere);
 (ii) for A > 0, b(A) := sup_{lambda > 0} (f-hat(lambda) - A lambda) is finite, positive, and attained at a unique
      lambda*(A); lambda*(A) is nonincreasing and continuous in A, and b is convex, decreasing and C^1 with
      b'(A) = -lambda*(A);
 (iii) (e^{-A}, e^{-b(A)}) is in B_f for every A > 0 (both coordinates in (0, 1) because A > 0 and b(A) > 0);
 (iv) on the three branches: if A >= f'(1) then lambda* = t solves f'(t) = A and b = f(t) - t f'(t); if
      A <= f(1) - f'(1) then lambda* = 1/u where psi(u) := f(u) - u f'(u) = A, and b = f'(u); if
      f(1) - f'(1) <= A <= f'(1) then lambda* = 1 and b = f(1) - A.
(Without the hypothesis f'(0+) = +infinity the lemma can fail: for f(t) = 4t - t^2 and A = 5 the supremum is 0 and not
attained.)
Proof. (i) f is concave on [0, 1] (C^1 with nonincreasing derivative, continuous at 0) and strictly so (f'' < 0 on
pieces). On [1, infinity), d^2/dlambda^2 [lambda f(1/lambda)] = f''(1/lambda)/lambda^3 < 0 on pieces, and the derivative
f(1/lambda) - f'(1/lambda)/lambda is continuous; so f-hat is strictly concave on [1, infinity). At lambda = 1 the left
derivative f'(1) exceeds the right derivative f(1) - f'(1) (since 2 f'(1) > f(1)), so f-hat is strictly concave on
(0, infinity). f' >= f'(1) > 0 on (0, 1]; on (1, infinity) the derivative is psi(1/lambda) with psi(u) = f(u) - u f'(u)
(u = 1/lambda in (0, 1)), and psi(u) > 0: the tangent line of the strictly concave f at u lies strictly above f at 0,
i.e. f(0) = 0 < f(u) - u f'(u); at 1 both one-sided derivatives, f'(1) and f(1) - f'(1) = psi(1) > 0, are positive.
(ii) phi(lambda) = f-hat(lambda) - A lambda is continuous and strictly concave on (0, infinity), phi(lambda) -> f(0) = 0
as lambda -> 0+, phi(lambda) -> -infinity as lambda -> infinity (f-hat(lambda)/lambda = f(1/lambda) -> 0), and
phi > 0 on some (0, lambda0) because phi'(lambda) = f'(lambda) - A > 0 for small lambda (f'(0+) = +infinity). So
sup phi > 0 is attained in (0, infinity), at a unique point lambda*(A) by strict concavity; b(A) = phi(lambda*) > 0.
b is a supremum of affine functions of A, hence convex. Monotonicity (exchange argument): for A1 < A2, optimality of
lambda*(A1) at A1 and of lambda*(A2) at A2 gives, after adding the two inequalities,
(A2 - A1)(lambda*(A1) - lambda*(A2)) >= 0, so lambda* is nonincreasing. Danskin: for A in a compact [A1, A2] the
maximisers lie in the compact [lambda*(A2), lambda*(A1)], the function (A, lambda) -> f-hat(lambda) - A lambda is
continuous with A-derivative -lambda, and the maximiser is unique, so b is differentiable with b'(A) = -lambda*(A). A
differentiable convex function is C^1, so lambda* = -b' is continuous. (iii) f-hat(lambda) <= A lambda + b(A) for all
lambda > 0 by the definition of b; this is (e^{-A}, e^{-b(A)}) in B_f (P4.1). (iv) The maximiser satisfies 0 in the
superdifferential of phi at lambda*: on (0, 1) this is f'(lambda*) = A, on (1, infinity) it is psi(1/lambda*) = A, and
lambda* = 1 iff f(1) - f'(1) <= A <= f'(1). The values of b follow by substitution (on the right branch,
b = lambda* f(u) - A lambda* = (f(u) - psi(u))/u = f'(u)). []

## P4.6 Theorem 2.2' for Lu-Wang's source, and its use in ZBS's Theorem 5.7

Theorem 2.2'. Let f be Lu-Wang's source (f(t) = (1+t) log(1+t) - t log t + t e^{-t} P(t), P the cubic Hermite
interpolant of data/source.json, SHA-256 f3e4a4ea...c08c). For every eps > 2 h(10^-16) (= 7.57e-15 to three digits)
there is C_eps >= 1 such that for all integers a, b >= 1 and N >= C_eps exp(G_f(a, b) + eps(a + b)), every host of
order N contains a red K_a or a blue K_b, where G_f(a, b) = a f-hat(b/a) (written f-hat(a, b) in ZBS).
Proof. Lemma B.1' with F = f, alpha = 10^-16 (h(alpha) < eps/2), applied with the following certified facts:
 - f is continuous on [0, 1] with f(0) = 0 (the formula; t log t -> 0), C^1 on (0, 1] (the Hermite data match
   values and derivatives at every node: exact checks in lines_B.py and source_A.py), and f'' < 0 on every Hermite
   piece (certified twice: lines_B.py, Arb, and source_A.py, ivA intervals; 2,279 pieces), hence f is concave on (0, 1];
 - f'(t) -> +infinity as t -> 0+: f'(t) = log((1 + t)/t) + e^{-t}((1 - t) P(t) + t P'(t)) with P and P' bounded on [0, 1] (P consists of finitely many cubic pieces);
 - f'(1) > 0 and 2 f'(1) > f(1) (source_A.py and source_B.py, check S0), so f' >= f'(1) > 0 on (0, 1];
 - for every s in [10^-16, 1], with w > 0 and r > 0 the rational controls of the Lu-Wang cell containing the midpoint
   of the program's own work cell containing s (any positive values are allowed; they are constant on a work cell) and
   mu = r s: 0 < mu < 1, 0 < p0(s) < 1, and (B.1) with Y = e^{-b(A(s))}, A(s) = -log X(s) (source_A.py and source_B.py,
   stage 2b); b(A(s)) > 0 holds for every A > 0 by P4.5 (ii) (the programs also check it at one A per cell). The pair (X(s), Y) is in
   B_f by P4.5 (iii). The mean-value bound used by the programs, Delta(s) >= Delta(m) - sup|Delta'| (s2 - s1)/2 on each
   cell [s1, s2] inside one Hermite piece, rests on P4.5 (ii): Delta(s) = (w + 1) f(s) + log X(s) - s b(A(s)) +
   w s log(r s) is C^1 on the cell with
       Delta'(s) = (w + 1) f'(s) + l'(s) (1 - s lambda*(A(s))) - b(A(s)) + w log(r s) + w,
   where l = log X, A = -l, l'(s) = -w r/(1 - mu) + (e^{-f'} f''/p0)/(1 - mu) + r log(p0)/(1 - mu)^2, and
   d/ds[-s b(A(s))] = -b(A) - s b'(A) A'(s) = -b(A) - s lambda* l'(s).  []
Use in Theorem 5.7. Our restated Theorem 5.7 (P3_BANKS.md, P3.3) uses the source bound exactly once, in grounding (b)
(tails and grounded cells of source pairs), with eps = min_h min(eps_h, eta_h) and in exactly the form proved here
(N >= C_eps exp(G_f(k, b) + eps (k + b)) implies a red K_k or a blue K_b); its proviso is that this minimum exceeds
2 h(10^-16) = 7.57e-15. The minimum over our certificates' new sources and over the ZBS sources of the reference cone
is computed exactly from the data in stage 2c: 5e-13 (cone/RESULT_2c.md).
