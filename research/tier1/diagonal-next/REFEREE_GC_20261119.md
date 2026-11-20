# Referee report on PROOF_GC.md (Proposition GC, limit form): 19 Nov 2026, 22:3x-23:0x +04

Fresh-context referee. Read: PROOF_GC.md; SELF_CONTAINED.md Section 14 (P1.1-P1.4); PROOF_QR.md; code/ramsey_gauss_cap.py,
code/ramsey_gc_montecarlo.py (and ramsey_agc_table.py, dp.py, ramsey_levers2.py for the table and bank numbers). New
referee programs (all FLOAT, all in code/, nothing else edited):
- `ramsey_ref_capexact.py`: the EXACT continuum cap functional at finite dimension R (exact sphere laws, no Gaussian
  approximation, no linearisation), in the exp form of PROOF_GC (d) or (option H) in the exact finite-r form (1 + D/H)_+^r.
- `ramsey_ref_gc_search.py`: search for sub-pairs beating ratio 1 on the Monte Carlo host (same seed as the MC).
- `ramsey_ref_agc_fix.py`, `ramsey_ref_bank_gcfix.py`: the a_GC table and the bank model under an alternative constraint
  (see item 2; both turned out not to change the drafted numbers).

## Verdict: SOUND WITH FIXES

The limit construction, the gain field, the limit forms of both tests (including the beta-dependence) and the numbers are
right. The maximality argument of Section 3(d) is not: its ASSERTED inequality is false (even for caps), and its exp-form
ratio formula is not a (1 + o(1)) approximation where it matters. Both have fixes that I checked, and with them maximality
holds for every lambda <= w at every p (strict margin at lambda/w = 0.27), so the numbers in Sections 1 and 4 stand. The
finite-host passage (Section 5 item 1) is a real gap but a routine one; a proof route is given, with a size condition
(N, M at least exp(c sqrt R)) that the Monte Carlo host does not meet.

## Items

**1. ERROR (Section 3(d), the bracketed ASSERTED claim). It is false, even for caps. Maximality still holds (Fix A).**

(a) Hemisphere, p = 1/2. S = {<f, e> > 0}. Write rho = <u/sqrt R, e>. Two halfspaces through the origin give, exactly and in
every dimension, Pr_{f in S}(<f, u> > 0) = 1/2 + arcsin(rho)/pi, so D(u) = arcsin(rho)/pi. The linear term is
phi(0) <m_S, u> = c_R rho with c_R = sqrt(R) E|s| / sqrt(2 pi), which is 0.318509 at R = 400 and 0.318318 at R = 10^4
(-> 1/pi = 0.318310). So D(u) > phi(0) <m_S, u> > 0 whenever rho > 0.0612 (R = 400) or rho > 0.0122 (R = 10^4), i.e.
Z = rho sqrt R > 1.22. That is 11.0% of all columns at every R. At rho = 1, D = 1/2 against 0.318.
(b) Thin slabs S = {0 < <f, e> < delta}. At u = sqrt(R) e, D = 1/2, while phi(0) <m_S, u> is about phi(0) sqrt(R) delta/2,
which tends to 0. The violation is unbounded.
(c) Why the stated reason fails. At tau_p = 0, D(u) = E_S[sign <f, u>]/2, and sign(x)/2 <= phi(0) x is false. The linear
term comes from averaging over the transverse Gaussian part of <f, u>, not from a pointwise inequality in <f, u>. Also, a
bound valid only where <m_S, u> >= 0 ("bounds the upper tail") gives tau^w (e^{sigma^2/2} Phi(sigma) + 1/2), and this
exceeds 1 for complements of small caps (removed-cap threshold above w/(phi(0) sqrt(lambda)), about 3.3 at
lambda/w = 0.27). The argument would need oddness as well:
at p = 1/2, D(-u) = -D(u), so E e^{D/eps} = E cosh(D/eps).
(d) The macroscopic-cap paragraph uses exp(lambda R t^2/2), which comes from the same false bound. That step is not needed:
D <= 1 - p_R gives ratio <= tau^w e^{(1-p)/eps}, and this tends to 0 whenever log(1/tau) >> sqrt R.

**Fix A (replaces linearisation plus rearrangement; works for every p, every finite R, every S, and fractional X').**
(i) Columns. For beta <= 1 and any Y' in Y (theta = |Y'|/|Y|, Z = (1 + D/H)_+), Hoelder gives
theta^{1 - r/s} (E[1_{Y'} Z^s])^{r/s} <= E Z^r <= E e^{D/eps}. So sup over Y' and beta of the ratio is at most
tau^w E_nu (1 + D_S/H)_+^r <= tau^w E_nu e^{D_S/eps}.
(ii) Rows. D_S(u) + p_R = tau^{-1} int 1_S(f) K(<f, u/sqrt R>) dsigma(f), with K(t) = 1[t > tau_p/sqrt R] nondecreasing.
Baernstein-Taylor (Duke Math. J. 43 (1976), spherical Riesz inequality: for K bounded and nondecreasing on [-1, 1] and
f, g >= 0, int int f(x) g(y) K(x.y) <= int int f*(x) g*(y) K(x.y)) with g = 1_E gives int_E (1_S * K) <= int_{E*} (1_{S*} * K)
for every E, with equal totals. The Hardy-Littlewood-Polya (Karamata) majorisation then gives
int Phi(1_S * K) <= int Phi(1_{S*} * K) for every convex Phi. Take Phi(z) = exp((z/tau - p_R)/eps) or
(1 + (z/tau - p_R)/H)_+^r. So the cap of the same measure is EXACTLY extremal, with no linearisation. The same holds for
densities 0 <= z <= 1 (bathtub after rearranging z), which the finite-host step needs. This closes Section 5 item 3.
(iii) Caps. This is a one-parameter problem, computed exactly by ramsey_ref_capexact.py. Asymptotically (theta the cap
threshold in sqrt(R) units):
- Gaussian regime (theta = O(1)): ratio -> tau^w e^{lambda m^2/2}. This is <= 1 iff lambda <= w g(theta), and g >= 1. Checked:
  g decreases on [0, 12], g(0) = 2.1776, g(12) = 1.0332, and g >= 2.18 for theta < 0.
- Intermediate regime (theta^2 = kappa sqrt R): the exponent is sqrt(R) G(kappa). In the exact potential (item 2),
  G <= sup_y [sqrt(lambda) phi(tau_p)^{-1} H log(1 + D(y)/H) - y^2/(2 kappa)] - w kappa/2 <= (lambda - w) kappa/2.
- theta^2 >> sqrt R (including macroscopic caps): the trivial bound.
- Near-full sets (complements of small caps): D has mean 0 under nu, so this is a second-order check, < 1.
Exact check of every cap theta in [-3, 100], R in {400, 10^4, 10^6}, p = 1/2, exp form:
- lambda/w in {0.27, 0.95, 1.0}: no cap has ratio >= 1. The supremum is approached only as S -> X (log ratio -0.0006 at
  theta = -3).
- lambda/w = 1.05: no cap at R = 400 or 10^4; at R = 10^6, log ratio 1.16 at theta = 18.
- lambda/w = 1.3: log ratio 0.016 (theta = 3, R = 400), 2.20 (theta = 8, R = 10^4), 30.6 (theta = 27, R = 10^6).
So at p = 1/2 the threshold is lambda = w, as the draft says. At the optimum used (lambda/w = 0.27) maximality holds in the
limit with a wide margin: the largest non-trivial cap ratio is tau^w e^{lambda m^2/2}, which is 0.755 at theta = 0 and
-> 1 only as tau -> 1.

**2. ERROR (Section 3(d), first display: "Phi(X', Y')/Phi(X, Y) = tau^w E_nu[1_{Y'} e^{D(u)/eps}] (1 + o(1))").
Fixable; numbers unchanged.**
The exp form is the r -> infinity limit at FIXED D/eps. It is exact in the Gaussian regime. For sets with D = O(1) (cap
thresholds theta^2 >~ sqrt R) it is only an upper bound: the true ratio is (1 + D/H)^r = exp((H/eps) log(1 + D/H)). It is
also not a safe proxy. In the exp form, maximality FAILS at p < 1/2 for lambda > w/L(p)^2, where
L(p) = sup_{y > 0} (Phibar(tau_p - y) - p)/(phi(tau_p) y) > 1 (Phibar(tau_p - y) is convex on [0, tau_p]):

| p | 0.40 | 0.30 | 0.20 | 0.10 | 0.05 | 0.0125 |
|---|---|---|---|---|---|---|
| L(p) | 1.024 | 1.109 | 1.310 | 1.895 | 2.929 | 7.91 |
| exp-form lambda/w cap | 0.953 | 0.812 | 0.583 | 0.278 | 0.117 | 0.016 |

Exact exp-form cap check at p = 0.1, lambda/w = 0.5: log ratio 7.8 (theta = 8, R = 400), 45.9 (theta = 18, R = 10^4),
477 (theta = 58, R = 10^6). The asymptotic prediction is sqrt(R) max_y [sqrt(lambda) D(y)/phi(tau_p) - sqrt(w) y], about
0.48 sqrt R. At lambda/w = 0.27 (below 0.278) there is no violation at any R.

Taken at face value, the exp form would therefore cut a_GC on 1,353 of the 19,522 certified cells. All of these have
p <= 0.275 (every cell at p = 0.0125). The cut is up to 0.319, mean 0.033 (ramsey_ref_agc_fix.py; it reproduces
logs/agc_m4w4.npz exactly before the cut).

The fix: use the exact finite-r ratio (Fix A(i) bounds every Y' and every beta by tau^w E(1 + D/H)_+^r). In the intermediate
regime the condition becomes sqrt(lambda) H log(1 + D(y)/H) <= sqrt(w) phi(tau_p) y for all y > 0. This holds at every p and
for every admissible H (0 < H < min(p, 1 - p)):
- F(y) := H log(1 + D(y)/H) has F'(y) = phi(tau_p - y)/(1 + D(y)/H).
- F' <= phi(tau_p) is equivalent to phi(t) - phi(tau_p) <= (phi(tau_p)/H) int_t^{tau_p} phi for t = tau_p - y.
- For tau_p > 0: the left side is int_t^{tau_p} s phi(s) ds <= tau_p int_t^{tau_p} phi, and tau_p < phi(tau_p)/Phibar(tau_p)
  <= phi(tau_p)/H, since H < p (Mills ratio).
- For tau_p <= 0: phi(tau_p - y) <= phi(tau_p) directly.
So lambda <= w suffices for every p; numerically, sup over y and H of the finite-H L is 0.99999. Exact finite-r cap check at
p = 0.1: see the table in "Numerical results" (B). The drafted a_GC table and bank therefore stand. Even under the exp-form
cut the bank model would be unchanged: 'gc' z = 1.2042023 (drafted 1.2042023), 'gcc' z = 1.2040417 (drafted 1.2040415),
because the affected low-p cells do not bind. The text of (d) must switch to the exact form. The Monte Carlo and code may
keep the exp form, which is a valid upper bound for maximality.

**3. GAP (Section 5 item 1, finite-host passage). Real but routine at fixed R; it needs N, M >= exp(c sqrt R).**
Proof route, with the order of limits as stated (N, M -> infinity at fixed R, then R -> infinity):
(i) Rows. Take an equal-area partition of S^{R-1} into N cells of diameter delta_N -> 0 (for example Leopardi's recursive
zonal partition, diameter O(N^{-1/(R-1)})) with one row per cell, or i.i.d. rows with W_infinity(mu_N, sigma) -> 0. Replace
each row of X' by the uniform measure on its cell. X' then becomes the set U = union of its cells, with sigma(U) = tau
exactly, and every D(u) changes by at most tau^{-1} sigma(slab of width 2 delta_N) <= C sqrt(R) delta_N/tau.
(ii) Columns. The functions u -> mu(H_u), over all row measures mu, form the convex hull of a VC class (halfspaces, VC
dimension R + 1, fixed R). That hull has finite uniform entropy, and so do its images under a Lipschitz Phi, so the class
is Glivenko-Cantelli. Hence column averages of Phi(D_{X'}(u_y)) equal E_nu uniformly over all X' as M -> infinity. The
growth of the VC dimension with R does not matter in this order of limits, and the union bound of QR is not needed.
(iii) Small sets. D <= 1 - p_R + o(1) gives ratio <= tau^w (1 + (1-p)/H)^r < 1 for tau < tau_R := (1 + (1-p)/H)^{-r/w}
= exp(-Theta(sqrt R)). This needs N >> 1/tau_R. Larger sets go through (i), (ii) and Fix A.
(iv) Strict margin. The continuum sup over sets of measure <= 1 - delta0 is <= 1 - c(delta0) at each large fixed R (caps;
item 1). For Y' in Y use Hoelder with exponent r(1 + eta): ratio <= theta^{eta/(1+eta)} times a continuum ratio at
(lambda(1+eta)^2, w(1+eta)), which is fine for small eta since lambda/w = 0.27. So the GLOBAL maximiser (X*, Y*) of Phi_c
over sub-pairs of the finite host has |X \ X*| = o(N) and |Y \ Y*| = o(M), and it is maximal.
(v) Tests. q_v, pi_v, m_v and b_v(y) at every v in X* move by O(delta/q0). Divided by the fixed eps this is o(1). VC
uniformity covers caps intersected with halfspaces, so the bounds hold for EVERY row, as (iii)-(iv) of Theorem 3.4 need.
Finite r only helps: (1 + psi/r)^s <= e^{beta psi} and (1 - k psi/r)_+^s <= e^{-beta k psi}. |c - p| = H <= eta is free,
and r = H sqrt(lambda R)/phi(tau_p) -> infinity.
The size condition is real. The Monte Carlo host (R = 400, N = 2e4, M = 4e3) is NOT maximal in the exp-form potential:
- random sets of up to about 9 rows beat ratio 1 on average (n = 1: 35.9; n = 8: 1.69; n = 10: 1.02 in-sample, 0.93
  held-out);
- X' = the red rows of one column has ratio 2.15 (column overfit; 0.76 on held-out columns).
At R = 400 the exp form needs N >> e^{(1-p)/(w eps)} = 2.1e8 and M >> e^{(1-p)/eps} = 7.1e3. In the exact potential with
H = 0.25 (r = 4.43) these artefacts are below 1 (single row 0.66, column-aligned 0.77). With H = 0.45 (r = 8), a single row
is already about 2.

**4. GAP (Section 5 item 2, p != 1/2 and the intermediate regime).** As posed in the draft (linear bound plus
second-order terms), this is not closable: the linear bound is false (item 1) and the exp form fails at p < 1/2 (item 2).
With Fix A and the exact form of item 2 it is closed for every p, all three regimes included. The second-order
phi'(tau_p) terms only contribute O(theta^2/sqrt R) to D/eps in the Gaussian regime.

**5. NIT (3(d)).** "Y' = all columns maximises it" is true only at beta = 1. At beta < 1 a proper Y' (an exponential tilt)
gets within o(1) of the beta = 1 value. The conclusion stands by Fix A(i) (Hoelder).

**6. NIT (3(c)).** The beta claim is right; add the proof. Blue is monotone in beta. For red, the log of the left side,
beta -> beta^2 kR^2/2 + log Phibar(tau_p + beta kR), is convex: its second derivative is kR^2 (1 - h(h - x)) > 0, with h the
inverse Mills ratio. It equals log p at beta = 0, and the log of the right side is linear in beta. So failure at beta = 1
implies failure on all of (0, 1].

**7. NIT (3(a)).** u_y = H + (p_R - p) with p_R = p + O(1/R); this is exactly H only at p = 1/2. Harmless.

**8. NIT (3(b)).** Uniformity on |G'| <= R^{1/8} alone does not control exponential moments, since psi can be O(sqrt R)
elsewhere. Add |psi| <= C kappa_B |G'| for |G'| <= sqrt(R)/2 (Lipschitz) and |psi| <= 1/eps beyond (probability e^{-R/8}).

**9. NIT (3(e)).** The "expected sampling noise ~0.107" ignores that b_v and g_y share rows. The right value is
sqrt(p(1-p)(1/|B_v| - 1/N))/eps = 0.087, which matches the observed 0.0867 exactly. E e^psi = 1.0778 against 1.0747 is
the noise factor e^{0.087^2/2} = 1.0038 (1.0747 x 1.0038 = 1.0788). The cap ratios at t >= 2.5 are noise-dominated: at
t = 3 there are about 20 rows and a noise factor of about 7, so the MC gives 0.568 where the exact continuum value is
0.0897. The MC cap check is informative only for t <= 2.

**10. NIT (Section 1).** "45-63%" is the range over the 8 printed controls. Over the 19,522 cells the GC share lies in
[0.000, 0.707], median 0.603. Also, the garbled clause "D(u) = E_S[Phi(<f,u> ...) ...]" in 3(d) should be removed with the
ASSERTED step.

## Numerical results

(A) Search for sub-pairs on the MC host (code/ramsey_ref_gc_search.py 400 20000 4000 4000 0.27 1 0.25; same F, U as
the MC; 4,000 extra held-out columns; ratio = tau^w mean_y exp(D_y/eps) as in (d)).

Columns of the table:
- in-sample: the ratio on the host's own columns;
- held-out: the same set evaluated on the held-out columns (removes column overfitting);
- held-out minus noise: held-out divided by the row-noise factor e^{s^2/2}, s^2 = mean g(1-g)(1/n - 1/N)/eps^2;
- exact r: the exact finite-r beta = 1 potential with c = p - 0.25, r = 4.43.

| family | best in-sample | held-out | held-out minus noise | exact r | set |
|---|---|---|---|---|---|
| caps, random directions | 0.972 | 0.972 | 0.972 | 0.972 | t = -1.5, n = 18,697 |
| caps aligned with one column | 2.150 | 0.764 | 0.763 | 0.773 | t = 0, n = 9,899 (column overfit) |
| 2-cap intersections | 0.864 | 0.865 | 0.865 | 0.862 | t = -1, n = 14,154 |
| 3-cap intersections | 26.0 | 26.0 | 0.803 | 0.799 | n = 2 (finite-N artefact) |
| 2-cap unions | 0.991 | 0.990 | 0.990 | 0.991 | t = -1, n = 19,574 |
| slabs | 0.840 | 0.840 | 0.840 | 0.840 | (-1, 1), n = 13,664 |
| red degree into k random columns (k = 1..500) | 2.17 | <= 1.000 | <= 1.000 | <= 1.000 | k = 5, top 1% (overfit); best held-out = whole X |
| spectral (top singular vector) sets | 0.785 | 0.767 | 0.765 | 0.771 | top/bottom half |
| greedy 1-flip local search (from whole X, random half, caps t = -1, 0, 1) | 1.00002 | 0.9998 | 0.9998 | 1.0000 | all converge to X minus 9 low-red-degree rows (n = 19,991) |
| greedy local search from a column-aligned cap | 2.041 | 0.756 | 0.755 | 0.776 | n = 9,998 (stuck at the overfit set) |
| random sets of n rows | n = 1: 35.9; 5: 5.6; 8: 1.69; 10: 1.02; 15: 0.43 | same | | n = 1: 0.66 | finite-N artefact |

Largest ratio found: 35.9 (single rows; exp form; finite N). Among sets with n >= 1000 it is 2.15 in-sample (a
column-aligned cap; finite M). On held-out columns with noise removed, nothing beats 1. The best non-trivial sets are
near-full: a union of two caps at 0.990, a cap at t = -1.5 at 0.972. No non-cap family beats the cap of the same measure,
as Fix A(ii) predicts. Every ratio above 1 is a finite-size artefact of the kind item 3 quantifies.

(B) Exact cap functional (code/ramsey_ref_capexact.py; theta grid [-3, 100] (p = 1/2) or [-3, 120] (p = 0.1)):

Each entry is the largest log ratio over the theta grid. "none" means no cap reaches ratio 1: the supremum is approached
only as S -> X, with log ratio -0.0006 to -0.0008 at theta = -3.

| p | potential | lambda/w | R = 400 | R = 10^4 | R = 10^6 |
|---|---|---|---|---|---|
| 1/2 | exp form | 0.27, 0.95, 1.0 | none | none | none |
| 1/2 | exp form | 1.05 | none | none | +1.16 (theta 18) |
| 1/2 | exp form | 1.3 | +0.016 (theta 3) | +2.20 (theta 8) | +30.6 (theta 27) |
| 1/2 | exact, H = 0.25 | 1.0 | | none (r = 42.6) | |
| 0.1 | exp form | 0.25, 0.27 | none | none | none (0.27) |
| 0.1 | exp form | 0.29 | none | +0.45 (theta 17) | +23.9 (theta 53) |
| 0.1 | exp form | 0.35 | +1.41 (theta 7) | +14.1 (theta 17) | |
| 0.1 | exp form | 0.5 | +7.8 (theta 8) | +45.9 (theta 18) | +477 (theta 58) (first-pass quadrature, 4,001 a-nodes) |
| 0.1 | exact, H = 0.02 / 0.05 / 0.09 | 0.5 and 1.0 | none (H = 0.02, 0.05; 0.09) | none (all three H) | none (H = 0.05; r = 137 and 194) |

Reading:
- The exp-form threshold at p = 0.1 is sharp at 1/L(0.1)^2 = 0.2785: none at 0.27; positive at 0.29 and growing like sqrt R
  (prediction 0.026 sqrt R minus O(1)).
- The exact finite-r potential has no violation at p = 0.1 even at lambda/w = 1.0, for every H tried.
- The exp-form violations at R = 1e6 for p = 0.1 sit at theta of about 53-58, where the cap has measure about e^{-1500}.
  They are continuum effects that matter only in the N -> infinity-first order of limits; they are not finite-sample
  effects.

(C) Reruns (Section 1 and 3(e) numbers).
- ramsey_gauss_cap.py reproduces every line. Root (1/2, 0.4005, 0.4629): a_rand 0.9300, a_GC 1.0384 (q0 0.342,
  lambda/w 0.27), a_sym 1.0903, a_cert 1.1098, share 0.60. The other seven controls: shares 0.60, 0.58, 0.54, 0.45, 0.63,
  0.63, 0.57.
- ramsey_gc_montecarlo.py 400 20000 4000 0.27 1 reproduces 3(e) to the printed digits: sd/eps 0.061; slope 0.3794 against
  0.3796; residual 0.0867; E e^psi 1.0778 against 1.0747; red 0.4298 against 0.4301; cap ratios 0.764 (t = 0), 0.643, 0.501,
  0.376, 0.273, 0.224, 0.568 (t = 3, noise-dominated, item 9).
- Table: 19,522 cells, median share 0.603. The bank logs say z = 1.2042023 ('gc') and 1.2040415 ('gcc').
- The exact cap functional agrees with the Gaussian-limit formula at theta = O(1): R = 400, theta = 0 gives 0.7550 against
  0.7549.
