# Fresh referee of the merged SELF_CONTAINED.md v4 draft (commit 660b06732), 19 Nov 2026, 17:4x-18:0x +04

Given the merged document and the block referee reports; asked to check the chain of Section 13 and every remaining
use of a ZBS or Lu-Wang result. Report as returned (verbatim content, lightly reflowed). GAP-1 was fixed by adding the
proviso check to tools/preflight.py (a second program, part of acceptance; evidence/preflight_proviso_tests_20261119.log,
preflight_certs_20261119.log); NITs 1-17 were applied in SELF_CONTAINED v4 (and the standalone files where they recur);
NIT-18 is recorded as a note in Section 18.3.

---

**Verdict: PASS WITH FIXES.** The chain in 13.2 holds. No ERROR, one GAP (in the record, not the maths) and a set of
NITs, mostly stale v1-v3 wording and cross-references.

**Explicit answer** to "rests only on Erdos-Szekeres, standard analysis, this document's proofs and the Section 18
computations": in substance YES (every ZBS-numbered result used in Sections 3, 5, 6 and 7 on the route is proved again
in Sections 14-17; Lu-Wang's Theorem 2.2 is replaced by Theorem 2.2' plus the proviso in P3.3; no ZBS or Lu-Wang result
is assumed anywhere). As 13.1 is written, not exactly: it says "the exact two-program computations of 13.3", while the
proviso check is one program and not in 13.3 (GAP-1); its list "Sections 3, 6, 7 and 14-17" leaves out Sections 2 and 5
(NIT-12); and by Section 13's own STATUS line the code audit must pass before "unconditional" is used.

1. The chain (13.2). Step 1: the full certificates checked directly with a regex over the raw text (a different method
from json.load): no "zr", "zc" or ["z", ...] references; certK3-full has 2,641 Lemma C controls, certCD3-full 2,722
Lemma C plus 25 Lemma D (2,747); counts reconcile (6,734 = 4,021 + 2,713 sources; 7,574 = 4,861 + 2,713; 3,295 =
1,393 + 1,902 raw). Since every reference is resolved inside the certificate and checked by A and B, the bank's validity
does not depend on the parser being faithful or the cone being complete (settles REFEREE_P3's "NOT CHECKED" item).
Step 2, Lemma C controls: Lemma C's setting plus the control check (0 < x < p, x < (1-mu)^w through lxU and l1mL) gives
"F nonempty and CERT < 0", integrability proved in Lemma C (iv); these are exactly P2.4's hypotheses; F and CERT are
defined identically in Section 3/1.2 and P1.2. Step 2, Lemma D controls: Lemma D gives V_A < 0 on the grid of 7.1;
Theorem A gives (INF); Theorem 4.2' applies with the same terminal hypotheses. ZBS items inside Theorem A and 4.2' are
covered: Lemma 4.5' meets (INF) exactly (R_0 = max{j, w+1, 3/beta}, N_0 = j, cap = mu + 1/j, zeta = 1/j, the Delta bound
a hypothesis); d_* < 1 in A.9 Step 2 follows from Claim P1.6, the failing sequence at v = 1 satisfying (i)-(iv) of
Proposition 3.5 ((i) Lemma 3.1; (iii) the derivation of (2) in P2.3(iii); (iv) for X_g = {q_i <= cap_n} using P2.3's
identity, with Delta_n >= (1-c_n)/(N(1-cap_n)-1) because v_1 <= 1, sigma_i > 0 and Y_i nonempty for large n). Even read
literally, citing "Step 6" is harmless. Step 3: P3.3's proviso is met (min eps_h = min eta_h = 1/2000000000000 = 5e-13 in
both full certificates, none <= 0, against 2h(1e-16) = 7.56827e-15; ZBS's 2,713 sources: 749 have 5e-13, the rest 5e-11).
P3.5 consistent with P3.1; P3.6 not needed for the full certificates. Theorem 2.2': each hypothesis met (continuity and
f(0) = 0 analytic; C^1 (18.1 lines_B, 18.2 source_A); f'' < 0 on all 2,279 pieces (both programs); f'(0+) = +infinity
(analytic, P4.6); (S0); (S1)/(B.1) on [1e-16, 1]; B_f membership and b > 0 from P4.5 (ii)-(iii)). Step 4: Corollary 5.10
used correctly, with the proviso.

2. Uses of ZBS results in Sections 0-12 on the route: all covered; numbering lines up (ZBS's (1)-(11) = P1's (1)-(11)).
6.1 Lemma 3.1/3.2 -> P1.1; 6.2(d) two-cell supremum -> P1.3 Step 1 (4); Lemma A.4 "Step 8" -> P1.3 Step 8; 6.4 (4) and
Step 5 -> P1.3; 6.5(iv) Step 2, Lemma 3.1 -> P1.3, P1.1; 6.7 (6), (7), (1), Step 6 -> P1.3, P1.1, Claim P1.6; 6.9 and
6.10 Theorem 4.2 proof, Lemmas 4.3/4.4, two L_0 conditions -> P2.4, P2.1, P2.2; 6.10 Theorem 3.4 from Proposition 3.5 ->
P1.2; 6.10 bank validity with extended controls and Section 2's root paragraph -> P3.1, P3.3-P3.5; Section 5's source
check citing lu_wang_lines_P0r12 -> 18.1; Lemma 2.1 -> P4.3; Lemma 2.3 -> P4.5 + 18.1/18.2; (13) -> P3.3 grounding (b) +
18.1. Not on the route: 6.10 "every ZBS control is an extended control"; 8.4 (Lean check).

3. Constants (60 digits): e^{z1} = 3.4835652387383... <= 3.4835652388; e^{z2} = 3.4826255124399... <= 3.4826255125 (match
checker B's balls and the full-certificate logs); z2 = 1.247786466924; gaps to EP 2.234090759e-3 and 2.503887076e-3;
2h(1e-16) = 7.568e-15; minimum 5e-13 confirmed. All 123 entries of MANIFEST.sha256 verify; the RESULT_2a/2b/2c and
program hashes cited in Section 18 match, apart from NIT-8.

4. Statements in 13.1: justified. ceil(C_* e^{zk}) <= C_* e^{zk} + 1, log(3.4835653/e^{z1}) = 1.76e-8 > 0 and
log(3.4826256/e^{z2}) = 2.51e-8 > 0, so R(k,k) <= 3.4835653^k (<= 3.4826256^k for 2U) for all large k; the
(3.4836 + o(1))^k and (3.4827 + o(1))^k forms follow.

Findings.
GAP-1 (13.1, 13.3, 18.3 item 7, Section 5 "ACCEPTANCE"): the P3.3 proviso (new in v4) is checked only by the six-line
source_margins.py; preflight, A and B check only eps, eta > 0, and 13.3 has no row for it. Fix: have the checkers assert
min eps_h and min eta_h > 8/10^15 (a rational above 2h(1e-16)) or add a second program, and add a row to 13.3. The value
itself is right; my independent check agrees.
NITs: (1) line 1 "(v3)" -> "(v4)". (2) Lines 15-16 "It re-proves nothing that ZBS prove ... proves in full what is new"
contradicts v4. (3) 0.3 "proves every item of (A) and (B) in Sections 14-17": Theorem 2.2 is replaced by the weaker
Theorem 2.2' and Theorem 5.7 gains a proviso; say "proves, or replaces by a sufficient weaker statement". (4) Sections
6.1-6.10 still say "ZBS ..." for results proved here: add a reading convention in 13; in 6.7 Step 2 cite Claim P1.6
(v_1 <= 1 for the Delta bound). (5) Heading "P1.4 Claim (used by Theorem A.9 of SELF_CONTAINED)" labels the claim P1.6;
rename and write "Section 6.7". (6) File names left from the separate drafts: P4.6 "(P3_BANKS.md, P3.3)"; 18.2 "Lemma
B.1' in P4_SOURCE.md" (P3 intro's "SELF_CONTAINED 6.10" already became "Section 6.10"). (7) "(31)" in 13.2 step 3 and
13.3 -> "(B.1) (P4.4) = (S1) (18.2), Lu-Wang's (31)". (8) 18.1 (and RESULT_2a.md), "lines_B.py (SHA-256
a9820baf...68d0...)": the real hash is a9820baf...22efa83. (9) Section 5 (Source), 1.6 and 1.7 still cite the Lean theorem;
add "(v4: 18.1)". (10) 8.3 "ZBS's bank P0r12 is not re-verified by us" -> "(v1-v3; re-verified in 18.3)". (11) P4.6
"(ZBS report 10^-12 as their smallest source margin)": the stored minimum is 5e-13; state 5e-13. (12) 13.1: add Sections 2
and 5; the analysis list omits results used (Tomic-Weyl, entropy bound for binomials, Bernoulli, power mean, layer-cake,
Stieltjes integration by parts); add them or write "e.g.". (13) 13's STATUS line conflicts with 13.4's "code audit
PENDING"; reword. (14) 2U: state "R(k,k) <= 3.4826256^k for all sufficiently large k". (15) 0.1's note on C_* cites ZBS;
for 1U/2U it comes from P3.3 through the compactness steps in P1.2, Theorem A and Lemma B.1'. (16) 13.2 "7.57e-15" ->
"about 7.568e-15"; optionally note P3.6 is not needed. (17) Notation: P2 and 6.1 use M = |Y|, which P1 reserves for
M(q); Lemma A.4 uses E, z where P1 Step 8 uses e_A, y_z; harmonise. (18) Evidence only: the full-certificate checker
outputs print the fixed labels "ZBS-only" and "assuming Theorem A (ramsey-lemma ...)", which now describe the route wrongly.

Nothing under our working repository was modified; scratch script ref7/minmargin.py.
