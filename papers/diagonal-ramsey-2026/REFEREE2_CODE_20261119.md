# Referee 2 (fresh context): code audit of the five checkers and parse_zbs.py

19 Nov 2026, 12:0x-13:2x +04. Given the code, the specifications (ZBS Sections 3, 5, 6 and their Lean Booleans at
c2875f33; ramsey-zbs PROOF.md Section 3; ramsey-lemma CERT_DESIGN.md Sections 1-4) and the certificate files; asked to
try to break the checkers. Report as returned, verbatim; scripts and logs in referee2/; the lab's responses are in
RESPONSES_20261119.md.

---

## Referee report: the five checkers and parse_zbs.py for certK3 and certCD3

**I could not get any of the checkers to accept a false certificate, and I found no soundness error.** I read all the code against ZBS Sec. 3, 5 and 6 and their Lean Booleans (fetched at c2875f33), against PROOF.md Sec. 3 (Lemma C) and against CERT_DESIGN Sec. 1-4 (Lemma D). I then ran 147 tampers. Every false one was refused. The only "accepts" were modifications that are still valid, and for each I measured the slack that keeps it valid.

### What was verified
- **Data:** all three SHA-256 hashes match, before and after my runs. MANIFEST.sha256 checks OK. The 25 `lemmaD` dicts in certCD3 are byte-equal to the hashed `certs/*.json` files, and their control fields match the bank controls.
- **Reproduced acceptance:**
  - checker A on certK3: ok, z = 1248056263241/10^12, e^z ≤ 3.4835652388 (830 s).
  - checker B on certK3 and certCD3: ok, with the recorded z values.
  - checkD_C on all 26 stored Lemma D certificates: all ACCEPT, smallest margin about −1.15e-7.

### Verdicts
| Checked item | Verdict | Basis |
|---|---|---|
| Bank checker A (runA, bankA, ctlA, ivA) | **PASS** | Line-by-line port of ProfF.ok, chainF, TermF, LeafF, RouteF with cellCheck, ClosedPF, SourceF and CtrlD.ok. Equal or stricter everywhere (its chain also needs lo < hi). Lemma C re-derived in full ((i)-(v), the hinge integral and the telescoping) and implemented correctly. |
| Bank checker B (runB, bankB, ctlB) | **PASS** | Same contract. It also refuses evaluation outside a profile's domain. |
| Lemma D checker A (checkD_A) | **PASS** (one GAP, NITs) | Matches Sec. 4b steps 0-8 and 4c K1-K10, apart from the GAP below. |
| Lemma D checker B (checkD_B) | **PASS** (same GAP) | As for checkD_A. |
| Lemma D checker C (checkD_C) | **PASS** | Checks K1-K10 explicitly, including N ≥ 2 and the jA0 range. |
| parse_zbs.py | **PASS** | Confirmed against the raw Lean text (details below). |

**parse_zbs.py checks:**
- I wrote my own bracket-based re-parse of T.lean and TD0-3.lean: `ref2/scripts/parse_check.py`.
- All 83,282 `FQ.mk` literals are in the two parsed forms; `FQ.mk n d = n/(d+1)` and `.negSucc n = −(n+1)` were checked against `FQ.toQ`.
- The 918 controls, 1902 raw and 1003 closed profiles, 2713 A/B values, rawMin and clMin all match zbs_bank.json exactly. `ctlL`, `rawL` and `clL` are in index order.
- The 1128 `lines` equal T.lean's `linesRat` and the list in Bridge/P06LinesP0r12.lean, theorem `lu_wang_lines_P0r12`. That theorem states ∀ s > 0, `symmetricProfile luWangSource 1 s ≤ c + d·s`, so the meaning "f-hat(λ) ≤ c + dλ" is confirmed.
- ZBS's Bank.lean `bank_check` covers all 2713 sources, 1902 raw and 1003 closed objects. `final` uses `bank_diagonal certs lu_wang_lines_P0r12`.

### Findings (no ERROR found)
1. **GAP: checkD_A and checkD_B never test K4's N ≥ 2 or K6's 1 ≤ jA0 ≤ N−1.**
   - Where: checkD_A.py:239-249 and checkD_B.py:163-194. checkD_A indexes `qs` with a negative jA0 at line 248.
   - Such certificates are still always refused, but through unrelated exceptions. jA = N or jB = N ends in `max()` of an empty sequence (checkD_A.py:332, 352; checkD_B.py:290, 309), where Sec. 4b says "fail".
   - Demonstrated with `scripts/harnessA.py` / `scripts/harnessB.py … certCD3.json ctl 873`:

     | Tamper | checkD_A | checkD_B |
     |---|---|---|
     | jA0 = 0 | ArithmeticError "q not certified in D" | same |
     | jA0 = −1 | ArithmeticError "empty interval" | ArithmeticError |
     | N = 1 | "q_A below jA0" | "jA" |

   - Never accepted, so soundness is not affected. Fix: check K4/K6 explicitly, as checkD_C does.
2. **GAP: the frozen Lemma D code is not pinned at run time.**
   - runA and runB never verify MANIFEST.sha256; only reproduce.sh does (ctlA.py:67-70, ctlB.py:62-71).
   - In checker A's process, checkD_A.py:19 `import ivA` resolves to checkA/ivA.py, not the frozen lemmaD/ivA.py. The two are byte-identical today (I diffed them), so there is no effect.
3. **NIT: checkD_A.py:368-374 treats any axis label other than 'P' as 'p'.** A certificate with one 'p' relabelled 'x' is ACCEPTED by A and refused by B ("bad tree node") and C. It is still a valid bisection, so this is not a soundness issue.
4. **NIT: precision.** checkD_B.py:23 sets 300 bits only at first import. ctlB restores 320 bits afterwards, so later CD controls run at 320. Rigour is unaffected.
5. **NIT: the official tamper suites count any crash or nonzero exit as a refusal** (red_controls.py:118, tamper_D.py:18).
   - The `control` tamper (red_controls.py:62) is refused by CtrlD.ok ("x <= exp(lxU)") before Lemma C or Lemma D is reached.
   - The suite has no tamper for the hinge sum, dominance, secant side, a_cut inside D, density strictness, the pair density sum or the root piece kind. I ran all of these; all were refused.
6. **NIT: parse_zbs.py.**
   - The `FQ` regex at line 12 is unused.
   - `defbody` relies on one-def-per-line layout.
   - The profile split at lines 39-41 is by count. It is correct here: my bracket parse agrees.

### Tampers run and results
- **Official red_controls.py, full runA and runB pipeline:**
  - certK3: 11/11 refused by both, each for the right reason. Examples: leaf→"aU, bU"; leafval→"leaf inequality"; route_g0→"child below route"; route_ds→"child slope"; ctl_h→"height at node 256"; source→"right tail"; srcline→"grounded"; rootz→"claimed z"; negidx→negative index; closed_raw_only→raw-only assert; control→"x <= exp(lxU)".
  - certCD3: 14/14 refused by both. This includes cd_alpha (K2), cd_u_b_minus_D (refused by K9, "P_up >= -w log u_b") and cd_merge_worst_leaf (box U ≥ 0).
- **Frozen tamper_D.py on root3_x337059333092731.json:** 15/15 refused by both. The two semantic regenerations at x·e^{2e-6} and x·e^{1e-5} are refused through K10.
- **My own tamper harness: 125 tampers through the checkers' own functions.**
  - Bank level, 45 tampers × A and B × both certificates. Refused:
    - control p > P.p, and route p_γ = P.p (strictness)
    - a knot dropped from a leaf, child or closed bp
    - margin 0, hm 0, g0 0
    - xi = x; xi ≥ e^{-A_σ} (via swapping in another source); ys 0; nu = mu
    - a call added or removed; θ above lo; hi beyond us[−1]
    - z = 1 − p_child, ds = 0
    - negative or unknown child references
    - closed pieces using closed profiles; p_R + p_S > 1; U-pair turned into a density copy
    - Q lowered at 1
    - sources: eps 0, kL = −1 or out of range, chain gap or short chain, grounded k = −1, bad pair domain, A lowered
    - root piece kind 'density', root z 1e-15 too low, root index −1
  - Accepted only where the change is still valid:
    - aU − 1e-30: measured slack 1.8e-14.
    - Q(1+δ) − 1e-14: slack 1.9e-13 (certK3) and 2.2e-13 (certCD3).
    - Root piece relabelled 'density' with p_R ≤ p_Q: a valid copy, and the root check then refuses it.
  - Lemma C, control 1722 of certK3, 19 tampers × A and B. Refused: secant on the same side or straddling the cell; secant through a_cut (ArithmeticError); k = 0 (dominance); k = N+1 or −1; h[0] + 1 (hinge); a_cut moved into D; q0 ≠ a_cut; q_N ≠ mu; q not increasing; beta = 1; x = p; lxU = w·l1mL; x + 2e-5; both 'cert' and 'lemmaD'; no cert; negative secant index.
    - Accepted: h[k] − 1e-12, which is valid (node slack 1.0e-10).
    - The hinge check bites at its margin: h[k] + 1e-8 is refused, + 2e-9 accepted. The hinge bound is −1.05e-9.
  - Lemma D, control 873 of certCD3, 16 tampers × A and B. Refused: a `control` key inside `lemmaD` (TypeError, so the bank's own control fields are always the ones used); mu shifted with CtrlD.ok kept ("q grid"); x shifted by 1e-6 or 2e-12, w shifted, beta loosened (all by K2); jA0 = 0 or −1; N = 1; P_up and y_c tampers.
    - Accepted: Dplus doubled, which is a valid coarser grid ((1 − u_b)/D = 500000); and the 'x' axis label in A only (finding 3).

### Other cross-checks
- **ivA and checkD_C exp/log** against 2000-bit Arb on 4,510 adversarial points: 0 containment failures (`scripts/arith_test.py`).
- **Arb semantics in python-flint 0.9.0:** `<`, `<=` and `>=` are true only when certain; `upper()`/`lower()` are converted exactly via `man_exp` and rounded outward; `fmpz //` is floor.
- **H, H' and H'' enclosures:** A (hand formulas), B (Arb series) and C (jets) overlap at 9 nodes of the root3 certificate.
- **|Ht''| cell bounds:** for all 924 cells, the bounds of A, B and C each dominate pointwise lower bounds.
- **Thin margins (an observation, not a fault):** on the certCD3 root Lemma D certificate the worst leaf is U = −1.08e-7 in A, −3.42e-8 in B and −1.51e-7 in C. The difference comes only from how widely each checker encloses |Ht''| (cell 517: 42.598, 42.810 and 42.475).

### Float use
**There is no float use anywhere exactness is claimed, in any of the five checkers or parse_zbs.py.**
- Floats appear only in display output: runA.py:43, runB.py:29-30, and checkD_A.py:356-357 and 388-393.
- The A-family `Fraction` would convert a JSON float exactly, but none is read. certK3 has 1,726 JSON floats, all in unread metadata: `controls[].gen.a_table`, `root.z_float`, `meta`.
- checker A refuses to run under `python -O` (shown: exit 1). B and C use explicit raises, not `assert`.

### Scope
- I did not referee Theorem A or the full proof of Lemma D. I re-derived only parts of D3, D4 and D7: the a(η) bound, the switch-point monotonicity, the K bound and the q_R slope.
- I did not check ZBS's individual Lean line proofs (`line_P0r12_i`).

Nothing in our working repository was modified. The full-size tampered copies were deleted, and `ref2_work/` on the SSD is empty.

Files (copied to referee2/): scripts/parse_check.py, tampers.py, harnessA.py, harnessB.py, arith_test.py, jet_cross.py,
d2check.py, leafdiag2.py (and the other helper scripts); logs harnessA/B_bank_K3.log, harnessA/B_ctl_K3.log,
harnessA/B_bank_CD3.log, harnessA/B_cd_873.log, red_K3.log, red_CD3.log, tamperD_root3.log, runC_all.log, runA_K3.log,
runB_K3.json, runB_CD3.json.
