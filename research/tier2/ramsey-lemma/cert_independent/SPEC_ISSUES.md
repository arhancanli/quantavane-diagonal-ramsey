# SPEC_ISSUES: points found while writing checkD_C from CERT_DESIGN.md (spec at ddb8c7a8e)

Written by the author of checkD_C from Sections 1-3, 4b and 4c only (checkD_A, checkD_B and genD
not opened). Each item says where the text is, what is unclear or wrong, whether it matters for
soundness, and what checkD_C does.

## Soundness: none found that breaks the bound

I re-derived D3-D7 line by line (S >= w + u_b p_b - Phi_b - D(p_b + w); the D4 linearisation; Lemma M
on both regions; the (B) integration by parts; the mid, high and cap bands; the switch-interval
difference formulas behind the slope of T). I found no step where U(B) as written in 4b fails to
bound V_A. The items below are gaps in the text, edge cases the text does not cover, and choices it
leaves open.

## 1. Commit reference

The brief named commit 18d7f5ac8, which does not exist in our working repository. The 4c text is at
ddb8c7a8e (corrected by the lab lead).

## 2. 4b step 3: "[u_b, u_b] if PK = g-" does not always enclose u1 (still sound, for another reason)

When PK = g- and pl > phi_s(u_b) (feasible: p_b ranges up to -w log u_b = phi_s(u_b) + w), the line
Phi_b - pl (u_b - u) crosses g well inside (0, u_b). Then u1 is interior, [u_b, u_b] does not
enclose it, and the term (u_b - ak)(pl - s0)_+ is dropped. The step is still sound. With bk = u_b,
Kint = int_0^{u_b} (phi_s - s0)_+. For every feasible pair, phi* has cumulative Phi* <= g with
Phi*(0) = g(0), and (. - s0)_+ is convex and nondecreasing, so by weak majorisation K <= Kint. The
justification is weak majorisation, not "enclosure plus dK/dPhi <= 1" as D7 suggests. The
"+ (g+ - g-)" term is then redundant. Suggested wording: "if PK = g-, use the bound
K <= int_0^{u_b} (phi_s - s0)_+ (weak majorisation)". checkD_C follows 4b exactly here.

## 3. 4b step 4 / 4c SWITCH POINTS: u2 at (P1, ph) need not exist

4c says f(u_b) < 0 <= f(1) for u2. At (P1, ph), f(1) = P1 + ph (1 - u_b) can be negative, because
step 0 only excludes Ph + ph (1 - u_b) < 0 and P1 can be below Ph. Then f < 0 on all of [u_b, 1]
and the rule "b2 = 1" applies. I checked that T(Phi') - T(P1) <= slope (Phi' - P1) still holds.
With u2 := 1 at P1, IR2(Phi') - IR2(P1) <= q_R (Phi' + ph (1 - u_b)) <= q_R (Phi' - P1), and the
4b formula with b2 = 1 is at least (1 - u_b) Hhat+(ph). So it is sound, but the text should say
that u2 is clipped to 1 when f(1) < 0. checkD_C bisects on [u_b, 1] and accepts b2 = 1.

## 4. Node ranges for jA and jB

Step 1 says "least node j >= 1" for j0. Steps 5 and 6 ("largest node with Ht'(q_j)- >= y") do not
say j >= 1. q_0 = a_cut need not lie in Q, so Ht'(q_0) is undefined. checkD_C uses j >= 1 for j0,
jA and jB.

## 5. Empty cell ranges: jA = N or jB = N

kappa2 = 1/max over cells i >= jA is undefined when jA = N (no cells), and likewise kappa2h when
jB = N. jA = N needs Ht'(mu) >= y_top, which only happens when ph <= y_c. Every such box is
infeasible by step 0, since p_b >= -Phi_b/(1 - u_b) >= -G_up/(1 - u_b), about -0.05, while y_c is
about -0.31. So the case does not arise in these certificates. checkD_C rejects a box with jA = N,
and sets kappa2h = 0 when jB = N, jB < jA0 or jB is undefined.

## 6. No node with H(q_j)- >= C0

Step 1 does not say what happens when no node j >= 1 has H(q_j)- >= C0. checkD_C rejects the box.
This is conservative: with G > 0 the constraint set can be non-empty.

## 7. Rounding direction of interval arguments of Psi+ and Hhat+

Steps 2 and 4 use Psi+(phi_s(b1)) and Hhat+(phi_s(b2)), but phi_s(b) is irrational. Both envelopes
are decreasing in y, so an upper bound needs the LOWER end of the phi_s enclosure. 4b does not say
which end to use. checkD_C uses the lower end.

## 8. Node values where the sign of A - B is uncertain

K6 says to use both branch formulas on a cell where A - B changes sign, but 4c is silent about
point values H(q_j) and Ht'(q_j) when the sign of A - B at the node is not certified. checkD_C takes
the union of both branch enclosures. Ht is C^1 there and H is continuous, so the true value lies in
the union.

## 9. "Certified in Q" (K6)

The method is not stated. checkD_C certifies G0(q)+ < 0 at both ends of each cell; G0 is convex, so
G0 < 0 on the whole cell. It also checks every node q_1..q_N directly, although K2 + K4 imply this.

## 10. D8 wording

D8 says "kappa E_grid is about 1e-7 near the saturated profile, the same size as the worst margin
of the c1722 certificate at -3.0e-4". 1e-7 and 3e-4 are not the same size. Presumably the
m300-mesh certificate's margin (about -1e-7) was meant.

## 11. tamper_D's two "semantic" tampers are margin probes, not hypothesis violations

tamper_D regenerates every data field at x' = x e^f (f = 2e-6 and 1e-5) with the same tree, and
expects a refusal ("some box must fail"). The regenerated data satisfy K1-K9, so the only possible
refusal is K10. Whether K10 fails depends on the certificate's margin. On all four certificates,
checkD_C finds that U shifts by about 0.5 f.
- c1722_m300 (margin -1.33e-7) and c1722_m280 (-7.6e-7): both semantic tampers are refused.
- c1701_m280 (-1.03e-6): f = 2e-6 is ACCEPTED (worst U -1.2e-8) and f = 1e-5 is refused.
- certUroot_m250 (-9.1e-6): both are ACCEPTED (worst U -8.0e-6 and -3.8e-6).
checkD_A and checkD_B give exactly the same verdicts. Run unmodified, tamper_D.py prints
"SOME TAMPER ACCEPTED" on c1701_m280 and certUroot_m250. This is not a soundness problem: the
regenerated certificate is a valid certificate for the nearby control. But the claim that every
tamper must be refused holds only for the thin-margin c1722 certificates. Suggest choosing f per
certificate from its own margin (about 10 |worst U| / 0.5), or labelling these as margin probes.

## 12. D8 confirmed numerically

The mesh terms matter at the m300 margin. With D multiplied by 2 or 4 (still dividing 1 - u_b),
c1722_m300 is still accepted (worst U -9.3e-8, -1.2e-8). With D x 8 or x 16 it is refused (+1.5e-7,
+4.7e-7).

## 13. K5 relies on Lemma C (iii), which no check verifies and which is not in this folder

The node heights are valid only because H is concave on Q (Lemma C (iii)). 4c cites it, but the
lemma is not in PROOF.md or CERT_DESIGN.md, and no K-check tests it. As a sanity check (not part of
acceptance), sanity_C.py certifies Ht'' < 0 by interval jets on every cell i >= 1 except cell 1,
which touches a(0), where the jets blow up. This covers 1316 of 1317 cells on c1722_m300 and 1348 of
1349 on certUroot_m250.

## 14. Cell 0 needs the right-end tangent in practice

"Any tangent of the concave H works" is true, but H' is unbounded as q -> a(0)+, and a(0) lies
within about 4e-15 of q_1 = a_hi. A tangent at any point of cell 0 other than q_1 (for example its
midpoint) gives valid but useless heights: U(B) about +1e3 on c1722_m280 and certUroot_m250 in my
first --heights mid run. A checker that takes "the better of the two end tangents" must use the
right end on cell 0, because q_0 = a_cut is not in Q. checkD_C uses the right-end tangent on cell 0
under every option.

## 15. Choices the text leaves open (checkD_C's choices)

- Node heights (K5): right-end tangents, the 4c example (more conservative than midpoint tangents).
  --heights mid is available for comparison only.
- |Ht''| on a cell (K6): min of the direct interval enclosure over the cell and
  |Ht''(mid)| + (h/2) sup|Ht'''|; on an uncertain-sign cell, the max over both branch formulas.
- q_min(Psi+) = q_j0. q_R = q of the full-hull line active at s = (log b2)+, taking the right piece
  at a breakpoint.
- theta = kappa * max|Ht''|+ is computed exactly (kappa = alpha K+/h1 exactly), so the same theta
  appears in (1 - theta) IR2 and theta (IRs - qB m_b). D6 needs theta >= kappa/kappa2; the same
  value must be used in both places.
- Switch points: bisection to width 2^-120 of the interval, or until the sign is uncertain.
