# Stage 2c (item Z13): ZBS's bank re-verified by our own programs; full certificates without ZBS references (19 Nov 2026)

Done by a subagent from 15:0x to 17:3x +04 under the lab's gates; scripts and logs in this folder; large outputs on the
SSD (quantavane-archive/ramsey-unconditional/cone/).

1. New parser (parse_zbs_full.py, written apart from parse_zbs.py): reads ZBS's P0r12 files at c2875f33 (1,517 files,
   each checked against its git blob SHA-1 from GitHub's tree listing), including the piece data, closed pieces, source
   covers and controls. Counts equal ZBS's: 1,902 raw / 1,003 closed profiles, 2,713 sources, 918 controls (all
   beta = 999/1000), 1,128 lines; 9,899 leaf / 7,284 route pieces; 9,908 density-copy / 1,686 complementary-pair pieces;
   304,695 route calls. Cross-checks with 0 mismatches against zbs_bank.json and against code/zbs_pieces.py (all 17,183
   raw pieces). parse_20261119.log, xcheck_zbs_pieces_20261119.log.
2. Reference cone (cone.py): from each certificate's direct references (473 raw profiles, 5 sources) the closure is
   essentially all of P0r12: 1,902 raw, 1,001 of 1,003 closed profiles, all 2,713 sources, 918 controls, 1,128 lines.
   cone_20261119.log.
3. Lemma C (ctl_certs.py; proposals by build_ctl.build, each verified by ctlA.check_control and ctlB.check_control):
   918 of 918 ZBS controls certified at N = 512, hinge bounds from -1.2984e-5 (control 51) to -2.0547e-3.
   ctl_certs_20261119.log.
4. Assembly (assemble_full.py) and structural check (check_full.py; refused all 7 of its own tampers, accepted the clean
   case): certK3-full.json (SHA-256 38091eed691b3ffa954d81e9658885cb68fb30e4e46ae76ddc376444f69ee468, 363 MB) and
   certCD3-full.json (32bcafd3fccbf094c83cc942669b3b843f09a3b10f87a6bd6a465d112bb07af8, 382 MB): every ZBS object of
   the cone appended as a new object, every reference remapped, no "zr", "zc" or "z" reference left; original objects
   equal their counterparts after remapping; root unchanged. Only ZBS's 1,128 lines remain referenced, proved in 2a.
5. Acceptance (preflight, checker A, checker B), same z and e^z bounds as the originals:
   certK3-full: PREFLIGHT OK (2,641 controls); A ok, z = 1248056263241/10^12, e^z <= 3.4835652388 (1,629 s); B ok (167 s).
   certCD3-full: PREFLIGHT OK (2,747 controls, 25 Lemma D); A ok, z = 311946616731/250000000000, e^z <= 3.4826255125
   (2,098 s); B ok (242 s).
6. Red controls on certK3-full (code/red_controls.py): all 11 refused by both checkers.
7. The proviso of Theorem 5.7 (P3.3): over all sources of each full certificate (ours and ZBS's), min eps_h = min eta_h =
   1/2000000000000 = 5e-13 > 8/10^15 > 2 h(10^-16) (about 7.568e-15); two programs: source_margins.py
   (source_margins_20261119.log) and the preflight (evidence/preflight_certs_20261119.log, preflight_proviso_tests_20261119.log).
Consequence: the validity of ZBS's bank P0r12 is no longer an assumption. Theorem 5.7 (P3) applied to the bank of
certK3-full (resp. certCD3-full), whose every object is verified by our two checkers and whose every control carries our
own Lemma C certificate (or Lemma D for the 25 CD controls), gives the bounds with the lines of 2a and the source of 2b.

## After the code audit (19 Nov 2026, 18:2x-19:2x +04)

Code referee ref6 (../REFEREE_CODE_AUDIT_20261119.md): 2c PASS, sound, NITs only. It decoded ZBS's Lean data with its own
regex decoder and compared every appended object of both full certificates (1,902 raw, 1,001 closed, 2,713 sources,
918 controls): 0 mismatches. Of 17 synthetic cases run through cone/assemble/check_full, the 13 tampers were refused, the
clean case and a consistent relabelling accepted, and two latent cases accepted (an extra top-level key, C-1; a garbage
control certificate, left to the checkers, C-2). Checker B's driver on a bank holding only the 1,128 lines accepted both
full certificates.
Applied: C-3. assemble_full.py and check_full.py now require zbs_full.json to have SHA-256
a2395f138b9ee24a2a5409debe44bb15443f544179fc75837d53c79b195903ca (new versions: assemble_full.py ba56e0a118eeb4bf...,
check_full.py 84615172456a1c7c...). Recorded as known limitations: C-1, C-2, C-4, C-5 (see ../../RESPONSES_20261119.md).
Re-runs (../rerun_after_audit_20261119.sh, ../rerun_after_audit_followup_20261119.sh):
- assemble_full.py with the pin, to a scratch path: certK3-full.json and certCD3-full.json reproduced byte for byte;
  maps equal apart from their own output path and run time (assemble_pin_rerun_20261119.log,
  assemble_pin_followup_rerun_20261119.log; the first log's "MISMATCH ... map.json" lines compared the maps byte for byte,
  which cannot hold since a map records its output path and run time).
- zbs_bank.json passed as zbs_full.json: refused by assemble_full.py and by check_full.py.
- check_full.py with the pin on both full certificates: FULL CHECK OK (structure_full_rerun_20261119.log).
- Checker A on both full certificates:
  certK3-full: ok, 2,641 controls, z = 1248056263241/10^12, e^z <= 3.4835652388 (1,515 s;
  checkA_certK3-full_rerun_20261119.log);
  certCD3-full: ok, 2,747 controls (25 Lemma D), z = 311946616731/250000000000, e^z <= 3.4826255125 (1,954 s;
  checkA_certCD3-full_rerun_20261119.log). Same z and e^z bounds as the first runs.
