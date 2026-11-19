# RESULT (18 Nov 2026, 05:25 +04): R(k,k) <= (3.4835653 + o(1))^k, certified over ZBS's bank

Current headline (supersedes the 17 Nov results below, which remain valid):
  z = 1248056263241/1000000000000 = 1.248056263241,   e^z <= 8708913097/2500000000 = 3.4835652388 (checkers A and B),
so R(k,k) <= (3.4835653 + o(1))^k. 2.234e-3 below EvolvingPrograms' z = 1.250290354 (3.49135655^k).
The same kp = 2 generator state as the 17 Nov 22:55 result, rematerialised with the U-knot fix (NOTES.md 18 Nov 00:2x).
This removed the 3.6e-5 materialisation loss: the certificate now equals the generator's 1.248056263388 to 1.5e-10.
- certK3.json (118 MB, SSD archive) SHA-256 76f9679ad5c7214a7f840816b16c19dd37aa2ff47959e8511b5163ce0406e1ae; new
  objects as before: 1,723 controls, 4,021 source lines, 1,393 raw profiles (27,619 pieces), 10 closed.
- checker A ok, checker B ok; 11/11 one-field tampers refused by both (18 Nov 01:07).
- Fresh sparse clone of 024c64a85 (reproduce.sh <work> <py> 9 2, 02:29-05:25): every generator round identical,
  cert.json bit-identical, checker A and B ok with the same z.
Same dependencies and caveats as below. Honest tier: 5.

## 17 Nov 22:55 result: z = 1.248092176788 (kp = 2, before the U-knot fix)

Superseded headline (still valid):
  z = 312023044197/250000000000 = 1.248092176788,   e^z <= 3.4836903482 (certified by checkers A and B),
so R(k,k) <= (3.4836904 + o(1))^k. 2.198e-3 below EvolvingPrograms' z = 1.250290354 (3.49135655^k).
Built with pieces of 1/200 (kp = 2), 9 rounds (search/run_gen2.py ... 9 out.pkl 2), root control refined.
- certK2.json (118 MB, SSD archive) SHA-256 57d7edc55ca7f3d0a5eaf012f6149784e89d38008698989b1115d880b861919a; new
  objects: 1,723 controls, 4,021 source lines, 1,393 raw profiles (27,619 pieces, 106,126 route cells), 10 closed.
- checker A ok, checker B ok (e^z <= 17418451741/5*10^9 = 3.4836903482); 11/11 one-field tampers refused by both;
  fresh sparse clone of d06a6a79d (reproduce.sh <work> <py> 9 2, 18:56-22:55): ctltable2.npz identical, every
  generator round identical, cert.json bit-identical, checker A and B ok with the same z.
- Known loss: the certified z is 3.6e-5 above the generator's 1.248056263 (20,935 source lines were bumped in
  materialisation, the largest by 8.4e-4); the cause is being traced (materialise.py records it with QV_DEBUG_COVER=1).
Same dependencies and caveats as below (ZBS Theorem 5.7 / Corollary 5.10 and their Lean-checked bank, Lu-Wang;
new objects checked by two Python checkers, not a kernel). Honest tier: 5.

## Earlier result (17 Nov 15:30): z = 1.248570727515 (kp = 5)


Claim. For every k >= 1, R(k,k) <= ceil(C e^{z k}) with
  z = 249714145503/200000000000 = 1.248570727515,   e^z <= 3.4853578697 (certified by checkers A and B),
so R(k,k) <= (3.4853579 + o(1))^k. Previous best: EvolvingPrograms/DiagonalRamsey (1 Nov 2026), z = 1.250290354
(3.49135655^k); improvement in z: 1.7196e-3.

What it rests on (all unrefereed): Zhao, Booth-Clibborn, Schwahn (github.com/w2ll2am/diagonal-ramsey @ c2875f33):
Theorem 5.7 (bank validity, generic in the bank), Lemmas 5.8-5.9, Corollary 5.10 (printed numbering), Theorems 3.4
and 4.2 (local step), the validity of their bank P0r12 (kernel-checked in Lean by ZBS) and their 1,128 tangent lines
of Lu-Wang's f-hat (Lu-Wang arXiv:2609.14525v1, formalised by Lu-Wang). Our new objects (controls, profiles, source
lines) are checked by two separately written Python checkers, NOT by a proof kernel; Lemma C (PROOF.md, refereed in
REFEREE_20261117.md) turns each control's finite certificate into CERT < 0. EvolvingPrograms' objects are not used.

Certificate (archive: <archive>/ramsey-zbs/; not committed, 204 MB):
- certU.json  SHA-256 74ed7cfdf4e1547aba8650213c92ff1e900f42fe87e7830ce7e6c1d59eea40df
- input zbs_bank.json (parse_zbs.py of T, TD0-TD3.lean at c2875f33)  SHA-256 2946c6561f562ea01a5f9b60ac0812c689af71985c60378e11c89e8cdc003bf0
- ctltable2.npz (generator input)  SHA-256 5dde387aafb285e2a3908ee6521590aea936d9e674735bc30c6c260a02d05509
- new objects: 1,263 controls (Lemma C certificates, N = 512, beta = 1 - 10^-7), 2,550 source lines, 771 raw
  profiles (9,057 leaf/route pieces, 34,038 route cells), 8 closed profiles (7 complementary-pair objects U_q at
  density 10^-6 and the root's Q).
- root: raw profile at density 1/2 on [1 - 2e-10, 1 + 2e-10], one retained route (theta = 0.725, 22 cells), control
  p = 0.499999, mu = 80725349867/200000000000, w = 120299011257/250000000000, x = 8107422360171/25000000000000,
  terminal source A = 1.126095841913, B = 0.301656966084; Q = complementary pair (R, R) on [1 - 1e-10, 1 + 1e-10].

Checks (17 Nov 2026):
- checker A (own dyadic intervals, Fractions): ok, z as above, e^z <= 34853578697/10^10, 732 s.
- checker B (python-flint 0.9.0 Arb + fmpq): ok, z as above, e^z in [3.48535786968256307816... +/- 1e-95], 48 s.
- red controls on the full certificate (code/red_controls.py): 11 one-field tampers (leaf aU, leaf value, root route
  g0, root route slope, root control x, root control secant height, source B, grounded line, root z, negative child
  index, closed pair pointing at a closed profile), all refused by both checkers (17 Nov 13:56).
- fresh shallow clone (sparse file:// clone of commit 2a3811d33, reproduce.sh, 13:57-15:30): ZBS tables re-fetched at
  c2875f33 (SHA-256 match), zbs_bank.json and ctltable2.npz bit-identical, generator roots identical round by round,
  cert.json bit-identical (SHA-256 74ed7cfd...ea40df), checker A ok (610 s), checker B ok, same z and e^z bound.
- referee (fresh context): REFEREE_20261117.md (no mathematical error; checker A's assert gap fixed).
- prior art re-run 17 Nov 12:05: nothing below 3.49135655 (NOTES.md).

Weight: a computational improvement on an unrefereed, AI-generated prior result, by the same method with a
better-converged bank.
