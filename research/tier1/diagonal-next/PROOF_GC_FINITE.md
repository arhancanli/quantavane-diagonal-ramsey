# Theorem GC (finite hosts): Gaussian-cap configurations refute every local-step lemma above x_GC

Draft 20 Nov 2026, 04:3x +04 (research/tier1/diagonal-next). Status v2.1 (05:0x): fresh referee PROVED WITH FIXES
(REFEREE_GC_FINITE_20261120.md; 2 GAPs, both closed in v2, 8 NITs applied); re-referee of v2 PASS WITH FIXES (three
wording items R1-R3, applied in v2.1). PROVED (lab bar for a proof: fresh referee + re-referee). Completes PROOF_GC.md
(the limit form, referee SOUND WITH FIXES) by the finite-host passage along the referee's route
(REFEREE_GC_20261119.md item 3), with one change: the near-full sub-pairs are handled by a second-order expansion, which
gives a LINEAR margin and so controls how much of the host the Phi-maximiser can drop. Notation as in PROOF_QR.md and
SELF_CONTAINED.md Section 14 (P1). All logs natural; Phi, Phibar = 1 - Phi, phi are the standard normal functions;
tau_p := Phibar^{-1}(p); C denotes constants depending only on the fixed data (p, mu, w, beta, x, q0, lambda, H), changing
from line to line, never on R, N, M.

## 0. Statement

Fix a control (p, mu, w) with 0 < p, mu < 1, w > 0, and beta in (0, 1) (as in P1's Theorem 3.4). GC data: q0 in (0, mu) and lambda > 0 with
    lambda e^{tau_p^2} <= 0.9 w;                                                                                      (L)
put theta_q := Phibar^{-1}(q0), kappa := sqrt(lambda) phi(theta_q)/q0, k := q0/(1 - q0),
    rho_B(q0, lambda) := q0^w e^{kappa^2/2},   rho_R(q0, lambda) := (1 - q0)^w e^{k^2 kappa^2/2} Phibar(tau_p + k kappa),
and x_GC*(p, mu, w) := inf{ rho_R : (q0, lambda) with (L) and rho_B < mu^w }.

**Theorem GC.** Let x_GC*(p, mu, w) < x < min{p, (1 - mu)^w}. For every eta > 0, R_0, cap in (mu, 1) and N_0 there are
r >= R_0 and a configuration (a host on V, BB its blue graph, disjoint nonempty X, Y in V with |X| >= N_0, c with
|c - p| <= eta) such that, with s = beta r: (i) g_y > c for every y in Y; (ii) (X, Y) is maximal for Phi_c; (iii) every v in X
has 0 < q_v < mu and fails blue (P1's (2)); (iv) every v in X fails shifted-red (P1's (3)), and, with
Delta := (1 - c)/(|X| (1 - cap) - 1), every v in X fails (RED) of Lemma 4.5 in its exact form (Section 3(f)).

(Remarks. "At any x > x_GC*" follows by monotonicity of (3) and (RED) in x, and is not vacuous: lambda -> 0 gives
x_GC* <= p (1 - mu)^w. (L) is stronger than needed: regime (d) needs only (1 + eta') lambda < w, and any lambda e^{tau_p^2} < w
works (choose eta', gamma from the slack), so x_GC* may be defined with lambda e^{tau_p^2} <= w (same infimum). The factor
e^{tau_p^2} comes from the sup-density envelope in regime (b) and is lossy (by e^{tau_p^2} for p >= 1/2, by e^{tau_p^2}/L(p)^2
for p < 1/2); a sharper envelope would recover part of it.)

**Consequence.** No statement with the conclusion of Theorem 3.4 or of Lemma 4.5 (arbitrary maximal pairs; the red move
(R_v, Y_v) and the blue move (B_v, Y); potential Phi_c) holds at any x > x_GC*. So every control certified through such a
statement has a >= a_GC* := -log x_GC*. Float (our lab notes, not public, 20 Nov 04:2x): (L) costs almost nothing at the optima (median share of the gap
a_cert - a_rand 0.599 against 0.603 without (L)), and a bank whose controls all sit at a_GC* reaches z = 1.20409, 3.334^k.
Scope, next to the claim: this does NOT cover sub-pair versions (Observation 2) or Lemma 4.5' (SELF_CONTAINED 6.10, used
for extended controls through Theorem 4.2'); the Gaussian-limit check (code/ramsey_gc_subpairs.py)
indicates they cost about 1e-3 in a. The host has huge blue cliques, so outcome-free arguments are not covered.

## 1. The sphere coordinate law

For R >= 4 let Xi_R be the law of sqrt(R) <f, e>, f uniform on S^{R-1}, e a unit vector; its density is
g_R(t) = c_R (1 - t^2/R)_+^{(R-3)/2}, and Gbar_R its tail.
(F1) Xi_R is symmetric and log-concave with E Xi^2 = 1, and E e^{s Xi_R} <= e^{s^2/2} for all real s, so
     Pr(Xi_R >= theta) <= e^{-theta^2/2} (theta >= 0). Proof: E Xi^{2j} = prod_{i<j} (2i + 1) R/(R + 2i) <= (2j - 1)!!, the
     Gaussian moments; odd moments vanish; sum the exponential series; Chernoff.
(F2) g_R -> phi uniformly, g_R(0) = sup g_R -> phi(0), sup_t |Gbar_{R-1}(t) - Gbar_R(t)| <= C/R, Gbar_R -> Phibar uniformly.
(F3) For theta >= 0: a_theta := E[Xi_R | Xi_R >= theta] <= theta + 1, Var(Xi_R | Xi_R >= theta) <= 1, and
     E[Xi_R^3 | Xi_R >= theta] <= 6 a_theta^3 (log-concave laws: nonincreasing mean residual life with
     E[Xi | Xi >= 0] = E|Xi| <= 1; truncation does not increase the variance (Heckman-Honore 1990); E Z^3 <= 6 (E Z)^3 for
     nonnegative log-concave Z (Barlow-Marshall-Proschan)). Also g_R(t) <= c_R e^{-t^2/4} for R >= 6 (an R-free majorant).
(F4) Decomposition. Let |u| = sqrt(R) and Y := <e, u>. If f is uniform on the cap C_theta := {sqrt(R) <f, e> >= theta}, then
     <f, u> = Xi Y/sqrt(R) + sigma(Xi, Y) Xi'' with Xi = sqrt(R) <f, e> ~ (Xi_R | Xi_R >= theta), Xi'' ~ Xi_{R-1} independent of
     Xi, and sigma(Xi, Y)^2 = (1 - Xi^2/R)(R - Y^2)/(R - 1). (Write f = (Xi/sqrt R) e + sqrt(1 - Xi^2/R) g with g uniform on the
     unit sphere of e-perp, independent of Xi; <g, u - Y e> = sqrt(R - Y^2) times a coordinate of g.)
(F5) The function h(theta) := log(1/Phibar(theta)) - m(theta)^2/2, m := phi/Phibar, is positive on R: h(-infinity) = 0 and
     h' = m (1 - m') > 0 because 0 < m' < 1 (the inverse Mills ratio has derivative in (0, 1)).

## 2. The continuum at dimension R

Rows: sigma = uniform on S^{R-1}. Columns: nu = uniform on sqrt(R) S^{R-1}. s_R := Gbar_R^{-1}(p), theta_R := Gbar_R^{-1}(q0).
Red iff <f, u> > s_R; K(f, u) := 1[<f, u> > s_R] - p has integral 0 in f for every u and in u for every f (<f, u> ~ Xi_R
either way). Shift: fix H in (0, min{eta, p/2, (1 - p)/2}); c := p - H. Scale: eps := phi(tau_p)/sqrt(lambda R), r := H/eps,
s := beta r. For a row density z (0 <= z <= 1, tau := int z dsigma > 0) and u: D_z(u) := tau^{-1} int z(f) K(f, u) dsigma(f), so
D_z in [-p, 1 - p] and int D_z dnu = 0. For a column density 0 <= vartheta <= 1 with theta := int vartheta dnu:
    Ratio(z, vartheta) := tau^w theta^{1 - r/s} ( int vartheta (1 + D_z/H)_+^s dnu )^{r/s},
which is Phi_c(X', Y')/Phi_c(X, Y) for the continuum host (all column densities equal p, so u_y = H). The cap of mass tau about
e is C(tau); D_theta(Y) denotes D_{1_{C_theta}}, a function of Y = <e, u> only.

Lemma 2.1 (columns; Hoelder). For eta' >= 0, Ratio(z, vartheta) <= theta^{eta'/(1+eta')} [ tau^{w(1+eta')} int e^{(1+eta') D_z/eps} dnu ]^{1/(1+eta')}.
Proof. Hoelder with exponent r(1 + eta')/s >= 1: int vartheta Z^s <= theta^{1 - s/(r(1+eta'))} (int vartheta Z^{r(1+eta')})^{s/(r(1+eta'))};
then vartheta <= 1 and (1 + a)_+^m <= e^{m a}; the powers of theta combine to theta^{eta'/(1+eta')}. []

Lemma 2.2 (rows; Baernstein-Taylor). For every convex Psi, int Psi(D_z) dnu <= int Psi(D_{C(tau)}) dnu.
Proof. K is a nondecreasing function of <f, u/|u|>. The spherical rearrangement inequality of Baernstein and Taylor (Duke
Math. J. 43 (1976) 245-268) gives, for every measurable E of nu-measure m, int_E (z * K) <= int_{E*} (z* * K), z* the symmetric
decreasing rearrangement and E* a cap; the bathtub principle then replaces z* by 1_{C(tau)}, because
F(f) := int_{E*} K(f, u) dnu(u) is a nondecreasing function of <f, e> (two-point symmetrisation, referee item 2: for
<x, e> > <x', e>, |x| = |x'| = 1, let rho be the reflection in the hyperplane through 0 normal to n = (x - x')/|x - x'|, so
rho x = x' and <e, n> > 0, and H+ := {<y, n> >= 0}; then F(x) - F(x') = int_{H+} [1_{E*}(y) - 1_{E*}(rho y)] [K(x, y) - K(x, rho y)] >= 0,
both brackets being >= 0 on H+ since <rho y, e> <= <y, e> and <x, y> - <x, rho y> = 2 <x, n><y, n> >= 0), so
int z* F <= int 1_{C(tau)} F (1_C - z* is >= 0 on C, <= 0 off C, equal masses); see also Baernstein, Symmetrization in
Analysis (2019), Ch. 7. (The intermediate z* can be skipped.) So the decreasing rearrangement of tau(D_z + p) is majorised by that of tau(D_{C(tau)} + p), with
equal integrals tau p; the Hardy-Littlewood-Polya inequality gives the claim for convex Psi of (D + p) and hence of D. []

Lemma 2.3 (envelope). There are C, R_1 such that for R >= R_1, theta >= 0 with Pr(Xi_R >= theta) >= e^{-R/16}, a := a_theta and
|Y| <= sqrt(R)/2:
    D_theta(Y) <= g_{R-1}(0) a Y_+ R^{-1/2} (1 + C ((a + 1)^2 + Y^2)/R) + C ((a + 1)^2 + Y^2 + 1)/R + e^{-R/16},
    |D_theta(Y)| <= g_{R-1}(0) a |Y| R^{-1/2} (1 + C ((a + 1)^2 + Y^2)/R) + C ((a + 1)^2 + Y^2 + 1)/R + e^{-R/16}.
Proof. By (F4), D_theta(Y) = E[Gbar_{R-1}((s_R - Xi Y/sqrt R)/sigma) | Xi >= theta] - Gbar_R(s_R). The part of the cap with
Xi > sqrt(R)/2 has conditional mass <= e^{-R/8}/e^{-R/16} (F1). For Xi, |Y| <= sqrt(R)/2: sigma >= 1/2 and
|1/sigma - 1| <= C (Xi^2 + Y^2 + 1)/R. Write the integrand minus Gbar_R(s_R) as
[Gbar_{R-1}(a') - Gbar_{R-1}(s_R/sigma)] + [Gbar_{R-1}(s_R/sigma) - Gbar_{R-1}(s_R)] + [Gbar_{R-1}(s_R) - Gbar_R(s_R)],
a' := (s_R - Xi Y/sqrt R)/sigma. The first bracket is at most g_{R-1}(0) |Xi Y|/(sqrt(R) sigma) in absolute value, and is
<= 0 when Xi Y <= 0 (Xi >= 0 on the cap); the second is at most g_{R-1}(0) |s_R| |1/sigma - 1|; the third is O(1/R) (F2).
Average over Xi with (F3). []

Lemma 2.4 (caps). For eta' > 0 small (fixed below) put Brk(tau) := tau^{w(1+eta')} int e^{(1+eta') D_{C(tau)}/eps} dnu. There
are c_1 > 0 and R_2 such that for R >= R_2 and every tau in (0, 1]:  Brk(tau) <= 1 - c_1 (1 - tau).
Proof. Fix eta' with (1 + eta') 0.9 <= 0.95; then lambda_R := lambda (1 + eta')^2 (g_{R-1}(0)/phi(tau_p))^2 satisfies
lambda_R <= 0.96 (1 + eta') w for large R, by (L) and (F2) ((phi(0)/phi(tau_p))^2 = e^{tau_p^2}). Write theta for the cap's
threshold (tau = Pr(Xi_R >= theta)). Four regimes; delta* > 0 and Theta are fixed in (c) and (b).
(a) Tiny caps, tau < e^{-R/16}: D <= 1 - p gives Brk <= e^{-w R/16 + (1 + eta')(1 - p) sqrt(lambda R)/phi(tau_p)} <= 1/2 for large R.
(b') Macroscopic caps, theta >= K R^{1/4} (and tau >= e^{-R/16}): D <= 1 - p and (F1) give
    Brk <= exp(-w (1+eta') K^2 sqrt(R)/2 + (1+eta')(1-p) sqrt(lambda R)/phi(tau_p)) <= 1/2 once K^2 > 2 (1-p) sqrt(lambda)/(w phi(tau_p)) + 1
    and R is large.
(b) Theta <= theta <= K R^{1/4}. By (F1) tau^{w(1+eta')} <= e^{-w(1+eta') theta^2/2}. By Lemma 2.3 (first form), with
    a <= theta + 1 <= 2 K R^{1/4}, the exponent (1 + eta') D_theta/eps is at most b Y_+ + E(Y) with b^2 = lambda_R a^2
    (lambda_R as above) and E(Y) <= C (theta^2 + 1)/sqrt(R) + C K^3 R^{-1/4} |Y| + C K R^{-1/4} Y^2 for |Y| <= sqrt(R)/2 (the
    cross term b |Y| ((a+1)^2 + Y^2)/R is at most C (a^3 |Y| + a Y^2 sqrt(R)/2)/R). Splitting off |Y| > sqrt(R)/2 (nu-mass
    <= 2 e^{-R/8}, integrand <= e^{C sqrt R}) and separating E(Y) by Hoelder with exponents (1 + gamma, (1 + gamma)/gamma):
        int e^{(1+eta') D_theta/eps} dnu <= (1/2 + e^{(1+gamma)^2 lambda_R (theta+1)^2/2})^{1/(1+gamma)} e^{C (theta^2 + 1)/sqrt(R) + o(1)},
    using E e^{b Y_+} <= 1/2 + e^{b^2/2} for symmetric 1-sub-Gaussian Y (F1) and E e^{c R^{-1/4} Y^2} -> 1. With gamma small
    ((1 + gamma) 0.96 <= 0.97) and 1/2 + e^{t} <= 2 e^{t}:
        log Brk <= (1+eta') (w/2) (-theta^2 + 0.97 (theta + 1)^2) + C theta^2/sqrt(R) + log 2 + o(1),
    and once C/sqrt(R) <= 0.0075 w the term C theta^2/sqrt(R) (which is O(K^2) at theta ~ K R^{1/4}, not small) is absorbed:
        log Brk <= (1+eta') (w/2) (-0.015 theta^2 + 1.94 theta + 0.97) + log 2 + o(1) <= -1 for theta >= Theta(w, eta').
    (tau >= e^{-R/16}, needed for Lemma 2.3, holds automatically for theta <= K R^{1/4} and R large.)
(c) Near-full caps, 1 - tau =: delta <= delta*. Let C' be the complementary cap (mass delta, direction -e, threshold
    theta' >= 0). Since int K dsigma = 0, D_{C(tau)} = -(delta/tau) D_{C'}. Put X := (1 + eta') D_{C(tau)}/eps; E_nu X = 0.
    By Lemma 2.3 (second form) applied to C', |X| <= 2 (1 + eta') delta (b' |Y| + C R^{-1/2}((theta'+1)^2 + Y^2 + 1)) with
    b' <= C (theta' + 1) and theta' <= sqrt(2 log(1/delta)) (F1). With e^X <= 1 + X + X^2 e^{|X|}/2,
        int e^X dnu <= 1 + (1/2) (E X^4)^{1/2} (E e^{2|X|})^{1/2} <= 1 + C delta^2 log(1/delta)   (delta <= delta*, R large),
    so Brk <= (1 - delta)^{w(1+eta')} (1 + C delta^2 log(1/delta)) <= 1 - (w/2) delta once delta* is small (fixed).
    (Lemma 2.3 covers |Y| <= sqrt(R)/2; on the rest |X| <= 2 (1+eta') delta/eps and its share of the second-order term is
    <= C delta^2 R e^{C delta sqrt(R) - R/8}, negligible. The cross term of Lemma 2.3 is C R^{-1/2} (theta'+1) Y^2, and
    (theta'+1)/sqrt(R) <= C when delta >= e^{-R/16}, so it adds C delta Y^2 to |X|, harmless since E e^{C delta Y^2} <= 2 for
    small delta*.)
    (Lemma 2.3 needs delta >= e^{-R/16}. If delta < e^{-R/16}, use |D_{C'}| <= 1: |X| <= 2 (1 + eta') delta/eps <= 1 for large R,
    so int e^X dnu <= 1 + E X^2 <= 1 + C delta^2 R, and Brk <= (1 - delta)^w (1 + C delta^2 R) <= 1 - (w/2) delta because
    delta R <= R e^{-R/16} is small.)
(d) Intermediate caps, theta in [theta_lo, Theta] with Pr(Xi_R >= theta_lo) = 1 - delta*. As R -> infinity, uniformly in theta on
    this compact range: tau -> Phibar(theta) (F2); for each Y, D_theta(Y)/eps -> sqrt(lambda) m(theta) Y (Taylor expansion of
    the tail in (F4) at shift Xi Y/sqrt R, with g_{R-1}(s_R) -> phi(tau_p), E[Xi | cap] -> m(theta) by uniform integrability),
    with the integrable envelope e^{C(1 + |Y|)} from Lemma 2.3 (for theta < 0 its proof gives the |.| form with
    E[|Xi| | cap] <= 1/(1 - delta*), which is all (d) uses). The law of Y depends on R, so run dominated convergence in
    density form: e^{C(1+|t|)} g_R(t) <= c_R e^{C(1+|t|) - t^2/4}, an R-free integrable majorant (F3); uniformity in theta
    follows from local-uniform convergence in (theta, t) on a fixed compact containing [theta_lo(R), Theta] for all large R.
    Dominated convergence gives Brk -> [Phibar(theta)^w e^{(1+eta') lambda m(theta)^2/2}]^{1+eta'}, and by (L), (F5),
        Phibar^w e^{(1+eta') lambda m^2/2} <= exp(-w (log(1/Phibar) - 0.475 m^2)) <= Phibar(theta)^{0.05 w}.
    So for R large, Brk <= (1 - delta*)^{0.04 w} on this range, while 1 - tau >= delta* there.
Together: Brk(tau) <= 1 - c_1 (1 - tau) with c_1 := min{1/2, w/2, (1 - (1 - delta*)^{0.04 w})} (the bounds 1/2 in (a), (b'),
(b) give 1/2 <= 1 - (1/2)(1 - tau)). Uniformity in (d): the Taylor remainders in (F4) are uniform for (theta, Y) in compacts and
the envelope is uniform in theta on [theta_lo, Theta], so the integrals converge uniformly. []

Corollary 2.5 (linear margin). For R >= R_2 and all (z, vartheta): Ratio(z, vartheta) <= 1 - c_2 max(1 - tau, 1 - theta),
c_2 := min{c_1, eta'}/(1 + eta').
Proof. Lemmas 2.1 and 2.2 (with Psi = exp((1 + eta') ./eps)) and 2.4: Ratio <= theta^{eta'/(1+eta')} (1 - c_1 (1 - tau))^{1/(1+eta')};
then theta^a <= 1 - a (1 - theta) (concavity, a < 1), (1 - y)^b <= 1 - b y (b <= 1) and (1 - A)(1 - B) <= 1 - max(A, B). []

Lemma 2.6 (the tests in the continuum). Every row f sees: blue neighbourhood C(f) := cap of mass q0 about f; gain
psi_f(u) := D_{C(f)}(u)/eps, a function of Y_f := <f, u>; red cell {Y_f > s_R}. Put
    Bl_R := int e^{beta psi_f} dnu,   Rd_R := int 1[Y_f > s_R] e^{-beta k psi_f} dnu   (independent of f).
As R -> infinity, Bl_R -> e^{beta^2 kappa^2/2} and Rd_R -> e^{beta^2 k^2 kappa^2/2} Phibar(tau_p + beta k kappa).
Proof. Lemma 2.4 (d) at the fixed threshold theta_q: psi_f -> kappa Y_f pointwise with the envelope of Lemma 2.3; dominated
convergence; Y_f -> N(0, 1); and the indicator 1[Y_f > s_R] converges in L^1 since s_R -> tau_p (F2). []

## 3. The finite host and the proof of Theorem GC

Choices. Since x > x_GC*, fix (q0, lambda) with (L), rho_B < mu^w and rho_R < x; then kappa_0 > 0 with
rho_B <= mu^w e^{-4 kappa_0}, rho_R <= x e^{-4 kappa_0}. With beta in (0, 1): e^{beta^2 kappa^2/2} <= e^{beta kappa^2/2}
< (mu/q0)^{w beta} e^{-4 beta kappa_0}; and by the convexity in beta of beta w log(1 - q0) + beta^2 k^2 kappa^2/2 +
log Phibar(tau_p + beta k kappa) (second derivative k^2 kappa^2 (1 - m'(.)) > 0, m the inverse Mills ratio, equal to log p at
beta = 0), (1 - q0)^{w beta} e^{beta^2 k^2 kappa^2/2} Phibar(tau_p + beta k kappa) <= x^beta p^{1 - beta} e^{-4 beta kappa_0}.
By Lemma 2.6 fix R (>= R_2, with r = H sqrt(lambda R)/phi(tau_p) >= R_0, r > w, s > 1) such that
    (1 - q0)^{w beta} Rd_R <= x^beta p^{1 - beta} e^{-3 beta kappa_0},   Bl_R <= (mu/q0)^{w beta} e^{-3 beta kappa_0}.
R is now fixed; everything below is at this R, and N, then M, tend to infinity.

The host. Rows: an equal-area partition {A_1, ..., A_N} of S^{R-1} into cells of diameter <= delta_N -> 0 (e.g. the recursive
zonal equal-area partition), and points f_i in A_i. Columns: u_1, ..., u_M i.i.d. nu. X0-Y0 edge f_i u_j red iff
<f_i, u_j> > s_R; X0-internal edge f_i f_j blue iff sqrt(R) <f_i, f_j> > theta_R; Y0-internal edges arbitrary. BB = blue graph.

(a) Discretisation. For X' in [N] with |X'| = tau N put z_{X'} := sum_{i in X'} 1_{A_i} (a row density of mass tau). A cell
    meets {<f, u> = s_R} only inside the band {|<f, u> - s_R| <= sqrt(R) delta_N}, of sigma-mass <= 2 sqrt(R) delta_N sup g_R
    <= 2 sqrt(R) delta_N. Hence for every u: |g^{X'}_u - p - D_{z_{X'}}(u)| <= e_N/tau with e_N := 2 sqrt(R) delta_N; likewise
    |q_v - q0| <= e_N + 1/N for every row (q_v excludes v) and |b_v(u) - p - D_{C(f_v)}(u)| <= 3 e_N/q0 for every row v and column u (cap boundary and
    hyperplane bands).
(b) Columns. The functions F_{X'}(u) := e^{(1+eta') D_{z_{X'}}(u)/eps} (X' in [N]) and the per-row functions
    e^{beta psi_{f_v}}, 1[Y_{f_v} > s_R] e^{-beta k psi_{f_v}} and 1[Y_{f_v} > s_R] (the last controls pi_v) are 2^N + O(N) functions bounded by
    e^{C sqrt R}; by Hoeffding and a union bound, with probability -> 1 as M -> infinity every empirical column average is within
    t_M -> 0 of its nu-integral. Fix such a realisation.
(c) Ratios. Let Phi_0 := Phi_c(X0, Y0). Column excesses of the full pair satisfy |u_j - H| <= e_N, so Phi_0 >= N^w M (H - e_N)^r.
    Small row sets: if tau < tau_* := (H/(2(1 - c)))^{r/w}, then Phi_c(X', Y')/Phi_0 <= tau^w ((1 - c)/(H - e_N))^r < 1. For
    tau >= tau_*: by (a) the finite column excesses of X' are at most H + D_{z_{X'}} + e_N/tau_*, and Lemma 2.1 on the empirical
    column measure, (b), Lemma 2.2 and Corollary 2.5 give
        Phi_c(X', Y')/Phi_0 <= (1 - c_2 max(1 - tau, 1 - theta)) (1 + err_{N,M}),
    theta := |Y'|/M, with err_{N,M} -> 0 as N -> infinity and then M -> infinity (it collects e_N/(tau_* eps),
    r e_N/H and t_M e^{C sqrt R}).
(d) The maximiser. Let (X, Y) maximise Phi_c over nonempty sub-pairs of (X0, Y0) (a fixed tie-break). It is maximal, so (ii)
    holds, and (i) holds by Lemma 3.1 of P1 (H_c(X, Y) > 0). Its ratio is >= 1, so by (c)
        |X0 \ X| <= (err/c_2) N,   |Y0 \ Y| <= (err/c_2) M,   err := err_{N,M}.
(e) The tests at every row. Fix v in X. Inside (X, Y): q_v, the blue neighbourhood B_v cap X, the column densities and
    excesses, b_v and pi_v differ from their values in (X0, Y0) by at most C err/q0, and those differ from the
    continuum values (q0, p, H, p + D_{C(f_v)}, p) by at most C e_N/q0 (by (a); (b) for pi_v). So the gain inside (X, Y) satisfies
    |r Z_v(u) - psi_{f_v}(u)| <= C (err + e_N)/(q0 eps) =: omega, uniformly in v and u, and omega -> 0. The column average over
    Y differs from the nu-integral by at most t_M + 2 (err/c_2) e^{C sqrt R}. With (1 + Z)_+^s <= e^{beta r Z} and
    (1 - k' Z)_+^s <= e^{-beta k' r Z} (k' = q_v/(1 - q_v) -> k), test (2) at v follows from Bl_R <= (mu/q0)^{w beta} e^{-3 beta kappa_0}
    and test (3) at v from (1 - q0)^{w beta} Rd_R <= x^beta p^{1-beta} e^{-3 beta kappa_0}, once N and M are large enough that
    the errors cost less than e^{beta kappa_0}. Also 0 < q_v < mu. (iii), (iv) hold at every row. (With beta < 1, (i)
    follows from P1's Lemma 3.1; at beta = 1 it would need a tie-break toward minimal |Y|.)
(f) Lemma 4.5's RED in its exact form (referee item 1). Fix cap in (mu, 1). Failing (RED) at v, raised to beta and
    multiplied by sigma_v^s (the computation in P2.3), is exactly
        sum_{y in Y_v} ((1 - q_v) u_y - q_v (b_v(y) - g_y) + E_v)_+^s < x^beta sigma_v^{s - w beta} pi_v^{1 - beta} sum_Y u_y^s,
    sigma_v := 1 - 1/|X| - q_v, E_v := sigma_v Delta - (1 - c)/|X| in [0, Delta], Delta = (1 - c)/(|X| (1 - cap) - 1). Use
    (1 - k' Z + e')_+^s <= e^{s e'} e^{-beta k' r Z} with e' := E_v/((1 - q_v) u_y) <= 2 Delta/((1 - mu) H) (u_y >= H/2), and
    (sigma_v/(1 - q_v))^{s - w beta} >= (1 - 2/(|X| (1 - mu)))^s. Both factors tend to 1 as N -> infinity at fixed s and R
    (|X| >= (1 - err/c_2) N), so the margin e^{-2 beta kappa_0} of (e) absorbs them for N large. (A term-by-term factor
    (1 + Delta/(H/2))^s, as in v1, is false where the bracket is <= 0 or small; red columns with that property have
    positive nu-mass when H < k (1 - p).) This step is not needed for the refutation of Theorem 3.4. []

## 4. (v1) What a referee should check first [stale; answered in REFEREE_GC_FINITE_20261120.md]
1. Lemma 2.2: that Baernstein-Taylor applies with rows on S^{R-1} and columns on sqrt(R) S^{R-1} (identify u with u/|u|), and
   that majorisation of the decreasing rearrangements follows for every m (the referee's Fix A(ii)).
2. Lemma 2.3: the sign claim (first bracket <= 0 when Y <= 0 on caps with theta >= 0) and the uniformity of the constants.
3. Lemma 2.4 (b): the bound E e^{b Y_+} <= 1/2 + e^{b^2/2} and the arithmetic -w(1+eta') theta^2/2 + 0.96(1+eta') w (theta+1)^2/2
   -> -infinity; (c): the claim E_nu X = 0 and the fourth-moment bound; (d): uniform convergence on the compact theta range.
4. Order of quantifiers: R is fixed in "Choices" (depending on kappa_0, eta', delta*, Theta, R_0), then N, then M.
5. Whether (L) (lambda e^{tau_p^2} <= 0.9 w) is really all the proof needs, given that sup g replaces phi(tau_p) in Lemma 2.3.
