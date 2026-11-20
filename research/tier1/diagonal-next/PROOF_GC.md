# Proposition GC (limit form): Gaussian-cap configurations and the ceiling they put on the local step

Draft 19 Nov 2026, 22:2x +04 (research/tier1/diagonal-next). Status v2.1 (20 Nov 04:2x): fresh referee SOUND WITH FIXES (REFEREE_GC_20261119.md); v2 applied Fix A (exact rearrangement
to caps) and NITs 5-10; v2.1 states item 2 in full (3(d)(iv): exp form false where D = O(1), fails at p < 1/2 above
1/L(p)^2, exact form with the Mills-ratio proof). Section 5 (finite-host passage) is being written as a full proof (SECTION 5
below is still the route). Notation as in PROOF_QR.md and SELF_CONTAINED.md Section 14 (P1). All logs natural.
Phi(t) is the standard normal distribution function, Phibar = 1 - Phi, phi its density.

## 1. What is claimed

Fix a control (p, mu, w) and beta in (0, 1]. For q0 in (0, mu) and kappa_B >= 0 put theta_q = Phibar^{-1}(q0),
tau_p = Phibar^{-1}(p), k = q0/(1 - q0), kR = k kappa_B and
    blue retention   rho_B = q0^w e^{kappa_B^2/2},
    red retention    rho_R = (1 - q0)^w e^{kR^2/2} Phibar(tau_p + kR),
subject to kappa_B <= sqrt(w) phi(theta_q)/q0 (maximality). Define x_GC(p, mu, w) = inf rho_R over (q0, kappa_B) with
rho_B < mu^w, and a_GC = -log x_GC.

Claim (limit). For every x > x_GC (and x < min{p, (1 - mu)^w}) there are continuum configurations, i.e. limits r -> infinity
of the objects of Proposition 3.5 (P1.3), in which: all rows have blue degree q0 < mu, red degree p into Y and nu-red
degree p; every row fails blue (P1's (2)) and shifted-red (P1's (3)) in the limit form; and every sub-pair (X', Y') has
potential ratio Phi(X', Y')/Phi(X, Y) <= 1 + o(1) (so the pair is maximal in the limit). Hence no statement with the
conclusion of Theorem 3.4 can hold at such x IF the continuum configurations are realised by finite maximal pairs
(Section 5), and then every envelope of that kind has a >= a_GC.

Float consequences (code/ramsey_gauss_cap.py, ramsey_agc_table.py, our lab notes, not public, 19 Nov 22:0x-22:2x): a_GC recovers 45-63% of the gap
(range over 8 printed controls; over all 19,522 cells the share lies in [0, 0.707], median 0.603)
between a_rand and the certified a (median 0.60 over 19,522 cells; root-like control (1/2, 0.4005, 0.4629): a_rand 0.930,
a_GC 1.038, a_cert 1.110); the realisable bank model with every control at a_GC reaches z = 1.2042 (3.334^k).

## 2. The construction (dimension R -> infinity)

Rows: N points f_v, i.i.d. uniform on the unit sphere S^{R-1}. Columns: M points u_y, i.i.d. uniform on the sphere of radius
sqrt(R). Red X-Y edge vy iff <f_v, u_y> > tau_p. Blue graph on X (the graph BB): j ~ v iff c_{jv} := sqrt(R) <f_j, f_v> > theta_q.
Shift c = p - H for any fixed H in (0, min(p, 1 - p)), and r chosen with
    eps := H/r = phi(tau_p)/sqrt(lambda R),   lambda in (0, w)  (so r -> infinity with R).                       (2.1)
Order of limits: N, M -> infinity first (empirical averages over rows and columns equal their expectations up to o(eps)),
then R -> infinity (r grows like sqrt(R)).

## 3. Derivation

(a) Columns are homogeneous. For fixed u with |u| = sqrt(R), <f, u> for uniform f has a law depending only on |u|, so
g_y = Pr_f(<f, u_y> > tau_p) =: p_R is the same for every column (p_R = p + O(1/R)). Hence u_y = H + (p_R - p) for every y, nu is uniform,
and by symmetry every row has red degree pi_v = m_v = p_R. Every row has blue degree q_v = Pr(c > theta_q) -> q0.

(b) Gain field. For row v write f_j = alpha f_v + sqrt(1 - alpha^2) g_j with g_j uniform on the sphere orthogonal to f_v;
on B_v, alpha = c/sqrt(R) with c ~ N(0,1) conditioned on c > theta_q (as R -> infinity). With G'(y) := <f_v, u_y>
(-> N(0,1) under nu) and <g_j, u_y> -> N(0, 1) independent of G':
    b_v(y) = E_{j in B_v} Phibar((tau_p - alpha G')/sqrt(1 - alpha^2)) = p + phi(tau_p) E[alpha | B] G' + O(1/R),
    E[alpha | B] = phi(theta_q)/(q0 sqrt(R)).
So psi_v(y) := r (b_v(y) - g_y)/H = (b_v - g)/eps = kappa_B G' + O(1/sqrt(R)), kappa_B = sqrt(lambda) phi(theta_q)/q0,
uniformly on |G'| <= R^{1/8}; for exponential moments add |psi| <= C kappa_B |G'| for |G'| <= sqrt(R)/2 (Lipschitz) and
|psi| <= 1/eps beyond (probability e^{-R/8}). kappa_B <= sqrt(w) phi(theta_q)/q0 is lambda <= w.

(c) Tests in the limit (P1.3 Step 1 notation; (1 + psi/r)^s -> e^{beta psi}, s = beta r):
    blue (2) at v:  E_nu e^{beta psi_v} = e^{beta^2 kappa_B^2/2} < (mu/q0)^{w beta}  <=>  e^{beta kappa_B^2/2} < (mu/q0)^w;
    red (3) at v:   E_nu[h_v e^{-beta k psi_v}] < (1 - q0)^{-w beta} x^beta p^{1 - beta}, and with s-free normalisation,
                    E_nu[h_v e^{-beta k psi_v}] = e^{beta^2 kR^2/2} Phibar(tau_p + beta kR)   (h_v = 1[G' > tau_p]).
At beta = 1 these are rho_B < mu^w and rho_R < x. (beta < 1 only makes both easier for the construction: blue is monotone
in beta; for red, beta -> beta^2 kR^2/2 + log Phibar(tau_p + beta kR) is convex (second derivative kR^2 (1 - h(h - x)) > 0,
h the inverse Mills ratio), equals log p at beta = 0, and the right side is linear in log, so failure at beta = 1 gives
failure on (0, 1]. The certified controls use beta = 1 - 1e-7.)

(d) Maximality (v2, after the referee's Fix A; REFEREE_GC_20261119.md items 1, 2, 4, 5). Let X' have row measure tau
(a set S of the sphere, or a density 0 <= z <= 1 for fractional sets) and D_S(u) := Pr_{f in S}(<f, u> > tau_p) - p_R.
(i) Columns: for beta <= 1 and any Y' (proportion theta), Hoelder gives theta^{1 - r/s} (E[1_{Y'} Z^s])^{r/s} <= E Z^r with
    Z = (1 + D_S/H)_+, so the potential ratio over every Y' and every beta is at most tau^w E_nu (1 + D_S/H)_+^r (EXACT
    finite-r form) <= tau^w E_nu e^{D_S/eps} (exp form, a valid upper bound but not a (1 + o(1)) approximation for large D).
(ii) Rows: 1_S * K with K(t) = 1[t > tau_p/sqrt(R)] nondecreasing; the Baernstein-Taylor spherical rearrangement inequality
    (Duke Math. J. 43 (1976)) gives int_E (1_S * K) <= int_{E*} (1_{S*} * K) for all E with equal totals, so by
    Hardy-Littlewood-Polya majorisation int Phi(1_S * K) <= int Phi(1_{S*} * K) for every convex Phi: the cap S* of the same
    measure is EXACTLY extremal (no linearisation; also for densities z after the bathtub step).
(iii) Caps, exact one-parameter problem (referee's code/ramsey_ref_capexact.py, exact sphere laws): Gaussian regime
    (threshold theta = O(1) in sqrt(R) units): ratio -> tau^w e^{lambda m^2/2} <= 1 iff lambda <= w g(theta), g decreasing
    from 2.178 to its infimum 1; intermediate regime (theta^2 ~ sqrt R): see (iv) (exact form,
    lambda <= w at EVERY p); large caps: D <= 1 - p_R and tau^w (1 + (1-p)/H)^r -> 0. Exact checks at p = 1/2, R in {400, 1e4, 1e6}: no cap reaches ratio 1 for lambda/w in
    {0.27, 0.95, 1.0}; violations appear at lambda/w = 1.05 (R = 1e6) and 1.3. So lambda <= w is the threshold; the optimum
    used (lambda/w = 0.27) has a wide margin (largest non-trivial cap ratio 0.755 at theta = 0, -> 1 only as tau -> 1).
    WITHDRAWN from v1: the bracketed claim D(u) <= phi(0) <m_S, u> (false even for hemispheres: D = arcsin(rho)/pi).
(iv) Exact form, not exp form (referee item 2; v2.1, 20 Nov). Three facts.
    1. The v1 display "ratio = tau^w E_nu[1_{Y'} e^{D/eps}] (1 + o(1))" is FALSE where D = O(1) (caps with theta^2 >~ sqrt R):
       the exact ratio there is tau^w E_nu (1 + D/H)_+^r = tau^w E_nu exp((H/eps) log(1 + D/H)), and log(1 + D/H) < D/H.
       The exp form is only an upper bound.
    2. The exp form is not a safe proxy: in exp form maximality FAILS at p < 1/2 once lambda/w > 1/L(p)^2, where
       L(p) = sup_{y > 0} (Phibar(tau_p - y) - p)/(phi(tau_p) y) > 1. Values: p = 0.4: 1/L^2 = 0.953; 0.3: 0.812; 0.2: 0.583;
       0.1: 0.2785; 0.05: 0.117; 0.0125: 0.016. Exact exp-form cap checks at p = 0.1: no violation at lambda/w = 0.27; positive
       log ratio at 0.29 (+0.45 at R = 1e4, theta 17), growing like sqrt(R) (referee's (B); rerun 20 Nov, logs/ref/).
    3. So the proof uses the EXACT finite-r potential. In the intermediate regime (theta^2 = kappa sqrt R) the log ratio is
       sqrt(R) G(kappa) + o(sqrt R) with
         G(kappa) <= sup_{y > 0} [ sqrt(lambda) F(y)/phi(tau_p) - y^2/(2 kappa) ] - w kappa/2,   F(y) := H log(1 + D(y)/H),
       D(y) = Phibar(tau_p - y) - p. CLAIM: F(y) <= phi(tau_p) y for all y >= 0, every p, and every admissible H
       (0 < H < min(p, 1 - p)). Then G(kappa) <= sup_y [sqrt(lambda) y - y^2/(2 kappa)] - w kappa/2 = (lambda - w) kappa/2 <= 0
       for lambda <= w.
       Proof of the CLAIM (Mills ratio; referee). F(0) = 0 and F'(y) = phi(tau_p - y)/(1 + D(y)/H); show F' <= phi(tau_p).
       If tau_p <= 0: |tau_p - y| >= |tau_p| gives phi(tau_p - y) <= phi(tau_p), and D(y) >= 0 makes the denominator >= 1.
       If tau_p > 0: with t = tau_p - y < tau_p, F' <= phi(tau_p) is phi(t) - phi(tau_p) <= (phi(tau_p)/H) D(y), and
       D(y) = int_t^{tau_p} phi. Now phi(t) - phi(tau_p) = int_t^{tau_p} s phi(s) ds <= tau_p int_t^{tau_p} phi(s) ds (s <= tau_p on
       the range; s phi(s) <= 0 <= tau_p phi(s) for s < 0), and tau_p < phi(tau_p)/Phibar(tau_p) = phi(tau_p)/p < phi(tau_p)/H
       (Mills: Phibar(x) < phi(x)/x for x > 0; H < p). []
       Numerically sup over y and H of F(y)/(phi(tau_p) y) is 0.99999; exact finite-r cap checks at p = 0.1 with
       H in {0.02, 0.05, 0.09} show no violation even at lambda/w = 1.0 (referee's (B); rerun logs/ref/).
    The a_GC table and the bank numbers do not depend on this (gc 1.2042023, gcc 1.2040417): the cells an exp-form cut would
    touch (1,353 cells, all with p <= 0.275) do not bind.
(e) Monte Carlo check, a separate program (code/ramsey_gc_montecarlo.py; R = 400, N = 20,000, M = 4,000, lambda/w = 0.27,
p = 1/2, q0 = 0.342, w = 0.4629; seed 1): column density sd/eps = 0.061 (homogeneous); fitted gain slope on <f_v,u_y>
0.3794 against kappa_B = 0.3796; residual sd 0.0867 against the correct sampling noise sqrt(p(1-p)(1/|B_v| - 1/N))/eps =
0.087; E e^psi 1.0778 against e^{kappa_B^2/2} x (noise factor 1.0038) = 1.0788; E[1_red e^{-k psi}] 0.4298 against 0.4301;
cap sub-pairs: largest ratio 0.764 (t = 0); values at t >= 2.5 are noise-dominated (about 20 rows at t = 3).
Referee's search on the same host (code/ramsey_ref_gc_search.py, 4,000 held-out columns): caps, cap intersections and
unions, slabs, red-degree sets, spectral sets, greedy local search: nothing beats ratio 1 on held-out columns once row
noise is removed (best near-full sets 0.990, 0.972); in-sample values above 1 are finite-N/finite-M artefacts (single rows,
column-aligned caps), quantified in Section 5.

## 4. Optimisation (float)

x_GC: grid over q0 in (0, mu) and lambda in [0, w] (code/ramsey_gauss_cap.py; vectorised table ramsey_agc_table.py).
At the optimum the blue constraint binds and lambda < w. Values in Section 1.

## 5. Finite-host passage (v2: the referee's route; written as a route, not yet as a full proof)

Order of limits: N, M -> infinity at fixed R, then R -> infinity. (i) Rows: equal-area partition of S^{R-1} into N cells of
diameter delta_N -> 0 (one row per cell); any X' with |X'| = tau N moves, by at most delta_N per row, to a density
0 <= z <= 1/tau, changing every D(u) by at most C sqrt(R) delta_N/tau. (ii) Columns: {u -> mu(H_u)} over row measures mu is the
convex hull of a VC class (halfspaces, dimension R + 1, fixed in this order of limits), hence Glivenko-Cantelli: column
averages equal E_nu uniformly over all X' as M -> infinity. (iii) Small sets: D <= 1 - p_R + o(1) gives ratio <=
tau^w (1 + (1-p)/H)^r < 1 for tau < tau_R := (1 + (1-p)/H)^{-r/w} = exp(-Theta(sqrt R)); this needs N >> 1/tau_R. (iv) Strict
margin: the continuum supremum over sets of measure <= 1 - delta0 is <= 1 - c(delta0) at each large R (caps, Section 3(d));
for Y' use Hoelder with exponent r(1 + eta), giving a continuum ratio at (lambda (1+eta)^2, w (1+eta)), fine since
lambda/w = 0.27; so the global maximiser (X*, Y*) of Phi_c over sub-pairs has |X \ X*| = o(N), |Y \ Y*| = o(M), and is
maximal. (v) Tests: q_v, pi_v, m_v, b_v(y) at every v in X* move by O(delta/q0) = o(eps), uniformly by VC (caps intersected
with halfspaces), so (iii)-(iv) of Theorem 3.4 hold at EVERY row; finite r only helps ((1 + psi/r)^s <= e^{beta psi},
(1 - k psi/r)_+^s <= e^{-beta k psi}). Size condition: N, M >= exp(c sqrt R); the Monte Carlo host (R = 400, N = 2e4,
M = 4e3) does not meet it (in exp form single rows reach 35.9; in the exact potential with H = 0.25, r = 4.43, the
artefacts are below 1).
Status: with Fix A and this route the claim is "sound with fixes" (referee); a full written proof of (i)-(v) is the remaining
step before GC counts as a theorem.
## 6. Why this matters (scope)

QR shows a >= a_rand for every envelope of the potential method. GC, if Section 5 is closed, shows a >= a_GC, a much higher
wall (60% of the gap). Together with the symmetric-split analysis (our lab notes, 19 Nov 22:0x: two-valued gains would put the wall at
a_sym, 90% of the gap, and the bank at 3.469^k) the picture is: the true threshold of the potential method lies in
[a_GC, a_cert]; whether it is near a_cert (CERT nearly sharp) depends on whether per-row two-valued gain splits are
realisable, which the near-twin obstruction (our lab notes, 19 Nov 22:0x (c)) argues against. GC hosts contain linear-size blue cliques,
so like QR this is a barrier only for local lemmas about arbitrary maximal pairs.
