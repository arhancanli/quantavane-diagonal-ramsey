# RESULT_CD (19 Nov 2026): second claim, ASSUMING THEOREM A: R(k,k) <= (3.4826256 + o(1))^k

This is a SECOND claim. The conservative headline is unchanged: RESULT.md, certK3, R(k,k) <= (3.4835653 + o(1))^k,
which rests on ZBS's framework alone. The claim below also rests on our own Theorem A (ramsey-lemma lane). Theorem A
has been read by fresh-context referees inside Quantavane, but no outside reader has seen it.

## Current second claim: certCD3 (18-19 Nov)

Claim (assuming Theorem A). R(k,k) <= ceil(C e^{z k}) with
  z = 311946616731/250000000000 = 1.247786466924,   e^z <= 278610041/80000000 = 3.4826255125 (checkers A and B),
so R(k,k) <= (3.4826256 + o(1))^k, assuming Theorem A. Compared with the other bounds:
- 1.811e-4 below certCD (below);
- 2.698e-4 below the ZBS-only certK3;
- 2.5039e-3 below EvolvingPrograms (3.49135655^k).

Construction, and what changed against certCD:
- It starts from certK3's generator state (9 rounds). search/cd_rounds.py then runs 4 more rounds with the control
  table lowered:
  - the 24 depth-1 route controls of certK3's root are set to their certified a';
  - the p = 1/2 row is lowered by the designer's float shift map at 0.92 x (ramsey-lemma SHIFT_MAP_root.tsv, eadc4b15a).
  After the 4 rounds comes a root_only round.
- The root is the table control 48/80/16, of kind CD: p = 499999/10^6, mu = 400499607047/10^12,
  w = 428621991427/10^12, beta = 9999999/10^7, x = 337059333092731/10^15 (a lowered by 2.8507e-4). Its certificate is
  the designer's stored root3_x337059333092731.json (207f77a96, SHA-256 7fb3ea94...22522b).
- 25 CD controls in all: the root plus the 24 depth-1 controls (stored certificates c7e57e100 / 0f5332014). They are
  vendored in code/lemmaD/certs and listed in code/lemmaD/cdmap_cd3.json. materialise asserts that each bank control
  equals its stored certificate's control exactly. Lemma C controls at lowered table entries are backed off until
  Lemma C certifies them (25 such back-offs). The certified z equals the generator's model (1.247786467127) to 2e-10.
- Dependencies: the same as certCD (listed below), now with 25 Lemma D controls.

Checks:
- certCD3.json (SSD archive). SHA-256 896dc046c2ca401e3dca4a3d453e432078ceaabca15fcbf55ca862f1c7034f37. Contents:
  1,829 controls (25 of kind CD), 4,861 source lines, 2,197 raw profiles (34,462 pieces), 14 closed profiles.
- Checker A ok: e^z <= 278610041/80000000 = 3.4826255125 (1207 s).
- Checker B ok: e^z in [3.48262551243994... +/- 8e-96] (128 s).
- Red controls: 13 one-field tampers, all refused by both checkers. These are the 10 bank tampers plus the 3 Gate 4 CD
  tampers on the root's CD control; the merged worst leaf gives U = +2.13 > 0.
- checkD_C, the independent third Lemma D checker: ACCEPTS every stored certificate (26 files, including all 25 used).
  The thinnest margin is c1407, at -9.2e-10.
- Fresh sparse clone of 8efa1092b (reproduce.sh <work> <py> 9 2 "" cdmap_cd3.json 4; 19 Nov 00:26-04:38). Results:
  - every generator round matches the certK3 run, and the 4 lowered rounds match the gate run;
  - cert.json is BIT-IDENTICAL to certCD3.json (896dc046...7034f37);
  - checker A ok (1118 s) and checker B ok (126 s), both with z = 311946616731/250000000000.
- Prior art (19 Nov 04:39 +04). Results:
  - Base repositories unchanged: ZBS c2875f33, EvolvingPrograms 959f46b0, 0 forks each.
  - GitHub repository search finds nothing below 3.49135655^k.
  - GitHub code search: 311946616731 and 1248056263241 give 0 hits; 3.4826256 matches only unrelated data files.
  - arXiv math.CO /list/new (the 18 Nov listing, the latest posted) has no diagonal R(k,k) upper bound.

## Earlier second claim: certCD (18 Nov, 17:30), still valid


Claim (assuming Theorem A). For every k >= 1, R(k,k) <= ceil(C e^{z k}) with
  z = 1247967523563/1000000000000 = 1.247967523563,   e^z <= 1741628061/500000000 = 3.4832561220 (checkers A and B),
so R(k,k) <= (3.4832562 + o(1))^k, assuming Theorem A. Compared with the other bounds:
- 8.874e-5 below our ZBS-only headline (certK3, z = 1.248056263241);
- 2.3228e-3 below EvolvingPrograms' z = 1.250290354 (3.49135655^k).

## What changed against certK3

One control changed: the root control c1722. All other objects are built exactly as in certK3 (same generator state,
kp = 2, 9 rounds, root refinement):
- The root's control is now of kind CD. It has the same (p, mu, w, beta) as certK3's c1722, and
  x = 329303794434999/10^15 (a lowered by 3.00e-4). Its validity is proved by Lemma D, through Theorem A, instead of Lemma C.
- The certificate of that control is the STORED file ramsey-lemma cert/certs/c1722_m300.json, SHA-256
  f9312c39887e0ace39081c679ff2eec6d62a31f27b3fbac500ee434b37ebada3, vendored as code/lemmaD/certs/c1722_m300.json.
  materialise.py asserts that the bank's control equals that file's control exactly.
- The root route was re-optimised with that control (search/root_cd.py): 1.248056263 -> 1.247967524. Lowering a by
  2.8e-4 gives the same value, because from about there on the root is bound by its path term.

## Dependencies (all unrefereed outside Quantavane)

1. Everything certK3 rests on (RESULT.md):
   - ZBS (github.com/w2ll2am/diagonal-ramsey @ c2875f33): Theorem 5.7, Lemmas 5.8 and 5.9, Corollary 5.10, Theorems 3.4
     and 4.2, and their Lean-checked bank P0r12;
   - Lu-Wang's f-hat tangents;
   - Lemma C (PROOF.md, refereed in REFEREE_20261117.md) for the other 1,722 controls;
   - two separately written Python checkers for our new objects.
2. Theorem A, Theorem 4.2', (INF) and Definition 5.2', in ramsey-lemma PROOF.md at c6cc2808e. They replace the CERT < 0
   hypothesis of a control by Lemma D's finite test, and they keep ZBS's 5.7-5.10 verbatim for banks mixing both
   kinds of control. Review: three fresh-context referees on the analytic chain, then the final Gate 1 referee
   (ramsey-lemma NOTES.md, 13:0x FAIL on one point, 13:1x PASS). Gate 1 found no open point once x < (1-mu)^w was
   checked on the CD path.
3. Lemma D: ramsey-lemma CERT_DESIGN.md Sections 1-4 at 4c103f48. Review:
   - Gate 1's referee checked D0.1-D7;
   - a fresh-context review here (REFEREE_LEMMAD_20261118.md) found no ERROR. Its blocking fix F2 is in 4c103f48;
   - the Gate 4 review (ramsey-lemma NOTES.md 13:3x) passed.
4. Lemma D's checkers checkD_A.py (Fractions with its own dyadic intervals, ivA.py) and checkD_B.py (Arb,
   python-flint 0.9.0, pinned; other versions are refused). They are copied unchanged from 4c103f48; SHA-256s are in
   code/lemmaD/MANIFEST.sha256.
   SHARED U(B) FORMULA: the two CD checkers are independent in their arithmetic (H, H', H'' formulas, interval
   systems, hull) but NOT in how they assemble the box bound U(B). Lemma D Sections D3-D7 are written twice by
   the same author, so an error in that derivation would pass both. What covers that derivation is the Gate 1
   referee's reading of D0.1-D7, not the second checker. CERT_DESIGN Section 4b/4c is a self-contained specification for a
   third, independently written checker. That checker now exists: checkD_C (ramsey-lemma cert_independent/, commits
   0548347a0 and 9fe23c44f). Its author wrote it from CERT_DESIGN Sections 1-3, 4b and 4c only, without opening
   checkD_A, checkD_B or genD. It accepts c1722_m300, the exact data of our CD control, with worst U <= -1.33e-7. It
   also records "no soundness break" in SPEC_ISSUES.md after re-deriving D3-D7. checkD_C is not wired into our bank
   checkers A and B. It is a standalone third reading of the same certificate.
5. Lemma C (iii): H is concave on Q (PROOF.md Section 3, refereed in REFEREE_20261117.md item 3). Lemma D's node heights
   (K5) rest on it, and no K-check tests it. Its hypotheses are exactly Lemma D's K1. As a cross-check outside
   acceptance, checkD_C's sanity_C.py certifies Ht'' < 0 by interval jets on 1316 of the 1317 cells of c1722_m300. The
   exception is the cell touching a(0).

## Certificate and checks (18 Nov 2026)

- certCD.json (118 MB, SSD archive: <archive>/ramsey-zbs/certCD.json). SHA-256
  5a3af93b10deca7f9b5fe10161b3514da5f0a15eabd0b748cf32e1fbc82fb03f. Contents: 1,723 controls (1 of kind CD),
  4,021 source lines, 1,393 raw profiles (27,619 pieces), 10 closed profiles.
- Checker A ok: e^z <= 1741628061/500000000 = 3.4832561220 (990 s).
- Checker B ok: e^z in [3.48325612199641906758... +/- 1.6e-95] (58 s).
- Red controls (code/red_controls.py, 13:51-14:19): 13 one-field tampers, every one refused by both checkers. Ten are bank
  tampers: leaf aU, leaf value, route g0, route slope, control x, source, source line, root z, negative index, and a
  closed profile using a raw one. Three are CD tampers from Gate 4: alpha - 1e-12 refused at
  "alpha >= beta/|G0'(a_hi)|"; u_b - D refused at "P_up >= -w log u_b"; merging the worst leaf refused at a box with
  U = +9.17e-6. (The Lemma C tangent tamper ctl_h targets the route's control, which is now the CD control. The CD
  tampers take its place there.)
- Fresh sparse clone of b4ca59955 (reproduce.sh <work> <py> 9 2 329303794434999/1000000000000000; 14:21-17:30). Results:
  - ZBS tables re-fetched at c2875f33, zbs_bank.json identical (2946c656...);
  - the generator ran 9 rounds;
  - the root was refined, then re-optimised at the stored control (1.247967524);
  - cert.json is BIT-IDENTICAL to certCD.json (5a3af93b...82fb03f);
  - checker A ok (1003 s) and checker B ok (65 s), both with z = 1247967523563/10^12.
- Lean (separate from this claim): the B2 split module kernel-checks certK3's root control (the Lemma C control at
  a, not the CD control). See NOTES.md 17:16 and lean/split/RUN_20261118.log.
- B2 (EvolvingPrograms-format Lean check of certK3's root control) is separate and not part of this claim: it
  concerns the ZBS-only headline's Lemma C root control.

## Dated negatives and the gate (18 Nov)
- certCD2 kept the 24 depth-1 route controls as Lemma D controls and fully regenerated the bank. It gave
  z = 1.247974485504, 7.0e-6 above certCD, because the generator's root stays bound by its terminal term.
- Root gate, with the p = 1/2 row also lowered by the shift map:
  - root_only: no gain;
  - 1 lowered round: 1.247942655, a gain of 2.49e-5, below the 3e-5 needed;
  - 2, 3 and 4 rounds: 1.247931964, 1.247831557 and 1.247786467 (rounds 5 and 6 are unchanged).
  The gate passed, which led to certCD3 above.
- certCD4 model gate (19 Nov). The designer's float shift map (0.92 x float) lowered the 160 Lemma C controls in
  certCD3's route tree (depths 1-2) that admit a Lemma D shift. After 2 full rounds the root was 1.247786467, exactly
  certCD3, so the gain is 0. The root is bound by its own terminal term at its certified Lemma D limit. The CD route
  rests at certCD3.

## Prior art, re-run on the day (18 Nov 13:24 +04)

- Base repositories unchanged: ZBS head c2875f33 (8 Oct), EvolvingPrograms head 959f46b0 (1 Nov); 0 forks each.
- GitHub repository search ("diagonal Ramsey" bound, diagonal ramsey lean, ...): no bound below 3.49135655^k. The
  nearest results are sichen-wang/diagonal-ramsey-numbers (3.69507^k) and wamlat/RamseyLean-bootstrap (3.769^k).
- GitHub code search: 1248056263241 gives 0 hits. Searches for 3.4835653 and "R(k,k)" 3.48 return only unrelated data files.
- arXiv math.CO /list new (18 Nov) and recent (11-18 Nov): no paper on diagonal R(k,k) upper bounds.

Superseded: the unconditional route is in papers/diagonal-ramsey-2026/SELF_CONTAINED.md, Section 13.
