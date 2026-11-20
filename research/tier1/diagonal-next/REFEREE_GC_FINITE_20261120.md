# Referee report on PROOF_GC_FINITE.md (Theorem GC, finite hosts): 20 Nov 2026 +04

Fresh-context referee. Read: PROOF_GC_FINITE.md; PROOF_GC.md (v2.1); REFEREE_GC_20261119.md; SELF_CONTAINED.md
Section 14 (P1.1-P1.4) and Section 15 P2.3 (Lemma 4.5), plus 6.10 (Lemma 4.5') for scope; our lab notes (not public) for 20 Nov 04:2x-04:3x;
code/ramsey_agc_proved_all.py (the float behind the Consequence). No new computation was run. The exact-sphere cap runs
in REFEREE_GC_20261119.md (B) were enough for the consistency checks below.

## Verdict: PROVED WITH FIXES

No step fails. Two local gaps need writing out. Item 1 affects only the Lemma 4.5 half of the Consequence; the
refutation of Theorem 3.4 does not use it. Item 2 is a true assertion that the draft does not prove; this report
supplies the proof. The rest are NITs. With the fixes, Theorem GC holds as stated under (L), and (L) is more than the
proof needs (item 8).

## Checked and correct (as asked)

- (F1) Even moments are prod_{i<j}(2i+1)R/(R+2i) <= (2j-1)!!, so E e^{s Xi_R} <= e^{s^2/2}, and the Chernoff tail bound
  follows. (F2) holds: Kolmogorov distance O(1/R). (F3) Three facts. Mean residual life is nonincreasing (log-concave),
  so a_theta <= theta + E|Xi| <= theta + 1. Var <= 1 by Heckman-Honore (log-concave truncation). Because Xi >= 0 on a
  cap with theta >= 0, E[Xi^3 | cap] <= 6 a^3 (nonnegative log-concave). (F4) The decomposition and sigma^2 are
  exact. (F5) h' = m(1 - m') > 0 and h(-inf) = 0.
- Lemma 2.1: the Hoelder exponent (1+eta')/beta >= 1; the powers of theta combine to theta^{eta'/(1+eta')}.
- Lemma 2.2 is valid for row densities 0 <= z <= 1 and for columns on sqrt(R) S^{R-1}. Under u -> u/|u|, nu becomes
  sigma and K is a nondecreasing function of <f, u/|u|>. The majorisation needs no monotonicity of D_C, because
  int_E tau(D_z + p) <= int_{E*} tau(D_C + p) <= sup_{|E'| = m} int_{E'} tau(D_C + p). HLP then applies on a
  non-atomic space. The one unproved step is item 2.
- Lemma 2.3 holds. When Xi >= 0 and Y <= 0, a' >= s_R/sigma, so the first bracket is <= 0. On |Xi|, |Y| <= sqrt(R)/2
  we have sigma >= 3/4 and |1/sigma - 1| <= C(Xi^2 + Y^2 + 1)/R. The cap part with Xi > sqrt(R)/2 has conditional mass
  <= e^{-R/16}. The E[Xi^3] cross term is <= C a(a+1)^2, since a >= E|Xi_R| is bounded below. Every constant comes
  from (F2) or (F3) and from sup|s_R|, so none depends on R.
- Lemma 2.4, regimes (a) and (b'): the arithmetic is right.
- Lemma 2.4 (b): the bound E e^{bY_+} <= Pr(Y <= 0) + E e^{bY} = 1/2 + e^{b^2/2} holds (Y continuous and
  symmetric). The cross terms are as stated. From (L): lambda_R <= 0.95(1+eta') w (g_{R-1}(0)/phi(0))^2, which is
  <= 0.96(1+eta') w for large R. With gamma chosen as stated, the exponent is (1+eta')(w/2)(-theta^2 + 0.97(theta+1)^2)
  + log 2 + C(theta^2+1)/sqrt R + o(1). See item 4 for how the C theta^2/sqrt R term is absorbed.
- Lemma 2.4 (c): D_{C(tau)} = -(delta/tau) D_{C'} and E_nu X = 0 both hold exactly, because s_R = Gbar_R^{-1}(p). The
  bound e^x <= 1 + x + x^2 e^{|x|}/2 holds. (E X^4)^{1/2} <= C delta^2 log(1/delta), using
  (theta'+1)^2 <= C log(1/delta) and log(1/delta) <= R/16. In the tiny-delta case, e^x <= 1 + x + x^2 for |x| <= 1, and
  delta R <= R e^{-R/16}. Item 3 adds two details.
- Lemma 2.4 (d): the limit [Phibar^w e^{(1+eta') lambda m^2/2}]^{1+eta'} is right. Since (1+eta')lambda <= 0.95 w and
  h > 0, it is <= Phibar^{0.05 w}. The regimes cover (0, 1], and c_1 works. See item 5 on uniformity.
- Corollary 2.5 (both tangent-line inequalities and the product step) and Lemma 2.6 (the Gaussian shift identity, and
  s_R -> tau_p) are correct.
- Choices: blue is monotone in beta. G(beta) = beta w log(1-q0) + beta^2 k^2 kappa^2/2 + log Phibar(tau_p + beta k kappa)
  has G'' = k^2 kappa^2 (1 - m') > 0 (m = inverse Mills ratio) and G(0) = log p. So for beta <= 1,
  G(beta) <= (1-beta) log p + beta log rho_R, which is the displayed bound.
- Section 3, order of quantifiers. eta and R_0 come first, then H. Then eta', gamma, K, Theta, delta*, then R_2 (none of
  these depend on H). Then R is fixed, then N, then M. Neither tau_* nor c_2 depends on N or M, and t_M may depend on N.
- Section 3 (a): band-counting gives at most N e_N cut cells for every u at once.
- Section 3 (b): Hoeffding plus a union bound over 2^N + O(N) functions at fixed N and R, with M -> infinity.
- Section 3 (c): the small-set bound holds once e_N < H/2. Large sets go through Lemma 2.1 on the empirical measure,
  then (b), Lemma 2.2 and Lemma 2.4. The additive t_M becomes a factor because int F_{X'} dnu >= 1 (Jensen,
  E_nu D = 0).
- Section 3 (d): ratio >= 1 gives c_2 max(1-tau, 1-theta) <= vartheta/(1+vartheta). A global maximiser is one-sided
  maximal, and Lemma 3.1 gives (i) when beta < 1.
- Section 3 (e), the test transfer: the error |rZ_v - psi_{f_v}| <= C(vartheta + e_N)/(q0 eps) holds deterministically
  for every v and y. Factors (u_y/H)^s and e^{beta|k_v - k| C sqrt R} tend to 1 because s and R are fixed. Both tests
  hold at EVERY row with margin e^{-2 beta kappa_0}, and q_v -> q0 in (0, mu).
- Consistency with the paper: Theorem 3.4 is proved under CERT < 0, so it needs a_cert >= a_GC* on every certified
  cell. The earlier table has GC share <= 0.707 < 1, so there is no contradiction. (L) is also consistent with the
  exp-form threshold: L(p)^2 <= e^{tau_p^2} (for example p = 0.1: (L) allows lambda/w <= 0.174 < 1/L^2 = 0.2785).

## Items

**1. GAP (statement (iv) and Section 3(f): Lemma 4.5's RED alternative is not "(3) with c replaced by c'").**
Failing (RED) at v, raised to beta and multiplied by sigma_v^s (the computation in P2.3), is exactly
    sum_{y in Y_v} ( (1-q_v) u_y - q_v (b_v(y) - g_y) + E_v )_+^s < x^beta sigma_v^{s - w beta} pi_v^{1-beta} sum_Y u_y^s,
with sigma_v = 1 - 1/N - q_v and E_v = sigma_v Delta - (1-c)/N in [0, Delta]. This differs from P1's (3) in two ways:
(a) sigma_v^{s - w beta} < (1-q_v)^{s - w beta} on the right, and the draft omits this;
(b) the shift E_v on the left. (f) bounds it "by a factor (1 + Delta/(H/2))^s" term by term. That is false where
    A_y := (1-q_v)u_y - q_v(b_v - g_y) <= 0 or A_y is small. Such red columns have positive nu-mass whenever
    H < k(1-p): there psi_{f_v} reaches (1-p)/eps, and A_y <= 0 once D >= H/k.

Fix: in (e), use (1 - k'Z + e')_+^s <= e^{s e'} e^{-beta k' r Z} with e' = E_v/((1-q_v)u_y) <= 2 Delta/((1-mu)H).
Also note (sigma_v/(1-q_v))^{s - w beta} >= (1 - 2/(N(1-mu)))^s. Both factors tend to 1 as N -> infinity at fixed s,
and the e^{beta kappa_0} margin absorbs them. Restate (iv) as: "for every cap < 1 and N_0, once N >= N_0, with
Delta = (1-c)/(N(1-cap)-1), every v fails (RED) of Lemma 4.5". Delta_min depends on Lemma 4.5's cap, which the
theorem must quantify. The refutation of Theorem 3.4 does not use this item.

**2. GAP, closed here (Lemma 2.2, bathtub step).** The draft asserts "f -> int_{E*} K(f,u) dnu(u) is nondecreasing in
<f, e>" without proof. Proof by two-point symmetrisation. Write F(f) for this function; a cap E* about e makes it
depend only on <f, e>. Take <x, e> > <x', e> with |x| = |x'| = 1. Let sigma be the reflection in the hyperplane through 0
normal to n = (x - x')/|x - x'|, so sigma x = x' and <e, n> > 0. Let H+ = {<y, n> >= 0}. Then
F(x) - F(x') = int_{H+} [1_{E*}(y) - 1_{E*}(sigma y)] [k(<x, y>) - k(<x, sigma y>)] dy >= 0. For y in H+ both brackets
are >= 0: <sigma y, e> <= <y, e>, and <x, y> - <x, sigma y> = 2<x, n><y, n> >= 0. The bathtub step is then
int z* F <= int 1_{C(tau)} F, because 1_C - z* is >= 0 on C and <= 0 off C, F is monotone, and the masses are
equal. (The step via z* can be skipped; Baernstein-Taylor followed by the bathtub step is enough.) Insert this
paragraph or cite Baernstein, Symmetrization in Analysis (2019), Ch. 7.

**3. NIT (Lemma 2.4 (c)).** Lemma 2.3 covers only |Y| <= sqrt(R)/2. Split off the rest: there
|X| <= 2(1+eta')delta/eps, so its share of the second-order term is <= C delta^2 R e^{C delta sqrt R - R/8}, which is
negligible. Also, the cross term of Lemma 2.3 is C R^{-1/2}(theta'+1)Y^2, not C R^{-1/2}Y^2. Because
(theta'+1)/sqrt R <= C when delta >= e^{-R/16}, this puts C delta Y^2 into |X|, which is harmless for small delta*
(E e^{C delta Y^2} <= 2). The bounds do not change.

**4. NIT (Lemma 2.4 (b)).** The term C theta^2/sqrt R is O(K^2) at theta ~ K R^{1/4}, so it is not small. It is
absorbed into the -0.03 theta^2 coefficient once C/sqrt R <= 0.0075 w. Then
(1+eta')(w/2)(-0.015 theta^2 + 1.94 theta + 0.97) + log 2 + o(1) <= -1 for theta >= Theta(w, eta'). Say this. Also say
that tau >= e^{-R/16} (needed for Lemma 2.3) holds automatically on theta <= K R^{1/4} for large R.

**5. NIT (Lemma 2.4 (d), Lemma 2.6).** The law of Y depends on R. Run dominated convergence in density form:
g_R(t) <= c_R e^{-t^2/4} for R >= 6, so e^{C(1+|t|)} g_R(t) has an R-free integrable majorant. Uniformity in theta
follows from local-uniform convergence in (theta, t) plus this tail bound, on a fixed compact that contains
[theta_lo(R), Theta] for all large R. For theta < 0, Lemma 2.3's proof gives only the |.| form, with E[|Xi| | cap]
<= 1/(1-delta*), and that is all (d) uses. State this.

**6. NIT (Section 3 (a), (e)).** Two corrections. First, q_v excludes v itself, so |q_v - q0| <= e_N + 1/N. Second,
pi_v (the red degree into Y0) is an empirical column average. It is controlled by (b), not by (a): add the N
functions 1[Y_{f_v} > s_R] to the Hoeffding family. (e) lists m_v, but no test uses it, so delete it.

**7. NIT (beta = 1).** P1 (Lemma 3.1, Theorem 3.4) assumes 0 < beta < 1. At beta = 1, Lemma 3.1 gives only
u_y >= 0, because deleting a column with u_y <= 0 leaves Phi unchanged when s = r. So (i) then needs the tie-break to
take a maximiser with |Y| minimal. Alternatively, state Theorem GC for beta in (0, 1), which is all that refuting
Theorem 3.4 and Lemma 4.5 needs.

**8. NIT ((L) is sufficient, and stronger than the proof needs).** The factor e^{tau_p^2} enters only in (b), through
lambda_R (sup g in place of phi(tau_p)). The 0.9 is only slack for eta' and gamma. Regime (d) needs only
(1+eta')lambda < w. Any lambda e^{tau_p^2} < w works: choose eta' and gamma from the slack, and (b) still gives
-theta^2 + (1 - c)(theta+1)^2. By continuity this defines the same infimum as lambda e^{tau_p^2} <= w, so x_GC* can be
stated with that constraint. In exp form nothing beats lambda L(p)^2 < w (REFEREE_GC_20261119 item 2), so e^{tau_p^2}
is lossy: by e^{tau_p^2} itself when p >= 1/2 (L = 1 there), and by e^{tau_p^2}/L(p)^2 when p < 1/2. The (b)
envelope gives the slope bound D(y) <= phi(0) y, which is where the e^{tau_p^2} comes from. A sharper version would
recover part of that loss. This is optional; the draft's (L) is valid as written.

**9. NIT (Consequence).** Theorem GC is stated for x < min{p, (1-mu)^w}. "At any x > x_GC*" follows because (3) and
(RED) are monotone in x, or because Theorem 3.4 and Lemma 4.5 assume x < min{...}. The statement is not vacuous:
lambda -> 0 gives x_GC* <= p(1-mu)^w = e^{-a_rand}. Floats: code/ramsey_agc_proved_all.py implements (L) exactly
(lmax = 0.9 w e^{-tau_p^2}) together with the blue constraint. A grid minimum over-estimates x_GC*, so the printed
a_GC* is a lower bound, which is the safe direction for a barrier. (Not re-run. The z = 1.20409, 3.334^k rounds
the lab notes' 3.3337^k.) Scope: the Consequence does not cover the sub-pair Lemma 4.5' (SELF_CONTAINED 6.10, used for the
extended controls through Theorem 4.2'). The draft says so ("Not claimed"). Keep that sentence next to the claim
"every control certified through such a statement".

**10. NIT (notation).** h names the function in (F5), but in Choices "h'" means the derivative of the inverse Mills
ratio. Use m' there. vartheta is both the column density (Section 2) and the error vartheta_{N,M} (Section 3); rename
one. Lemma 2.4 (a) writes e^{-wR/16} for tau^{w(1+eta')}, which is fine but say "<=". (F3): cite Heckman-Honore
(1990) for the truncated variance, and Barlow-Marshall-Proschan for E Y^3 <= 6 (E Y)^3 when Y >= 0 is log-concave.

## Answers to the draft's Section 4 checklist
1. Baernstein-Taylor applies once u is identified with u/|u|. Majorisation holds for every m, as shown above; the one
   missing proof is supplied in item 2.
2. The sign claim is correct. The constants are R-free.
3. E e^{bY_+} <= 1/2 + e^{b^2/2} is correct, and the (b) arithmetic is correct, with item 4 added. In (c), E_nu X = 0
   holds exactly and the fourth-moment bound is correct, with item 3 added. Uniform convergence in (d) holds, with
   item 5 added.
4. The order of quantifiers is correct (R depends on H, eta and R_0 as well).
5. (L) suffices and is more than needed (item 8).

## Re-referee of v2 (20 Nov 2026, +04)

**Verdict: PASS WITH FIXES.** The three fixes are one-line wording changes; none changes the mathematics. GAP 1 and
GAP 2 are closed correctly, and NITs 3-10 are applied correctly. I found no new mathematical error.

Checked:
1. GAP 1 is closed. The display in 3(f) is exactly Lemma 4.5's (RED) after raising to beta and multiplying by sigma_v^s.
   E_v lies in [0, Delta] because sigma_v |X| >= |X|(1 - cap) - 1 when q_v <= cap. The bracket factors as
   (1-q_v) u_y (1 - k'Z + e'), so (1 + a)_+^s <= e^{s a} gives the e^{s e'} bound. The bound e' <= 2 Delta/((1-mu)H)
   uses u_y >= H/2 and q_v < mu. Since 0 < s - w beta <= s and the base is <= 1, the sigma_v factor is
   >= (1 - 2/(|X|(1-mu)))^s. Both factors tend to 1 at fixed s, and the e^{-2 beta kappa_0} margin absorbs them.
2. GAP 2 is closed. The two-point proof in Lemma 2.2 is correct: <x, n> > 0, and both brackets are >= 0 on H+. The
   bathtub step is correct.
3. NITs 3-10 are applied correctly:
   - (b): the -0.015 theta^2 absorption is right; the "+1" part of C(theta^2+1)/sqrt R goes into o(1).
   - (c): the |Y| split and the (theta'+1) Y^2 cross term are both added.
   - (d): the density-form majorant is in (F3); it holds because c_R is bounded.
   - (a) and (b): the 1/N self-term and pi_v's Hoeffding function are added.
   - beta is now in (0,1) in the Statement.
   - The (L) remark is correct.
   - The Consequence scope sentence is next to the claim.
   - Notation: m' replaces h', err replaces vartheta, and the (F3) citations are added. The E Z^3 <= 6 (E Z)^3 bound
     holds because a log-concave law on [0, infinity) has an increasing failure rate (Barlow-Marshall-Proschan).

Remaining (NIT, wording only):
R1. Statement (iv), quantifier order. As written, one configuration is fixed and then "for every cap and N_0, once the
    host is large enough" follows. No single host works for every cap, because Delta blows up as cap -> 1. The proof
    picks N after cap, so the statement should read: "For every eta > 0, R_0, cap in (mu, 1) and N_0 there are r >= R_0
    and a configuration with |X| >= N_0 such that (i)-(iii), P1's (3) at every row, and, with
    Delta := (1-c)/(|X|(1-cap)-1), (RED) of Lemma 4.5 fails at every v." This is also the order a refutation of
    Lemma 4.5 needs.
R2. 3(e): m_v was removed but its continuum value was not. The list "(q0, p, H, p + D_{C(f_v)}, p, p)" now has one p
    too many; drop the last p. Also, "(by (a))" should read "(by (a); (b) for pi_v)".
R3. "Choices" (line 161) still says "beta in (0, 1]"; change it to (0, 1) to match the Statement. The Section 4
    checklist is stale; drop it or mark it as v1.
