# Changes made for the public copy

The files here are copies of our working repository, made on 19-20 November 2026. Two kinds of edits were made, and
nothing else changed:

1. Status sentences about release ("nothing here is public" and similar) were replaced in
   `papers/diagonal-ramsey-2026/SELF_CONTAINED.md`, `research/tier1/ramsey-offdiag/PROOF.md`,
   `research/tier2/ramsey-zbs/RESULT.md` and `RESULT_CD.md`; tier labels were removed from the last three.
2. Local absolute paths were made relative to the repository root (or written as `<archive>/`, `<scratch>/`,
   `<python>`, `<flint-python>` for the lab's disk, scratch folders and interpreters), and the working repository's
   name was replaced by "our working repository"; in four comments, "coordinator" and "owner's" became "lab lead" and
   "lab". Program logic is unchanged.

So the SHA-256 values recorded in `papers/diagonal-ramsey-2026/MANIFEST.sha256`, in the run logs and in the proof
documents refer to the lab versions. The files whose bytes differ because of edit 2 are listed below. In
`research/tier1/ramsey-offdiag/cert/offdiag_cd3_v1.json` and `offdiag_k3_v1.json` only the informational "bank"
path field changed; the 1,601 cells are byte-identical, and the checkers identify the bank by its SHA-256, not by this
field. None of the files that the acceptance checks pin (the frozen Lemma D code and certificates, `ivA.py`, the
checkers, the certificates in `certs/`) changed.

| file | SHA-256 as first copied (the lab version, except for the files named in the status-line edits above) | SHA-256 here |
|---|---|---|
| `papers/diagonal-ramsey-2026/REFEREE1_CHAIN_20261119.md` | af868c779db32a04bd73f5abef9541cf9b9a0d7df1d7f1dd58c8d897f1a62387 | a878bb4bce5e8373926dcba454811ec20bcce37b9a992702861fac39c9f46006 |
| `papers/diagonal-ramsey-2026/REFEREE2_CODE_20261119.md` | e5a85e318f10828f80801b9b070c774667e1d452a8448b84a814c62b198c6509 | b23c132389bb0b87ab3070992162a0efc84fd4ac6d1330e9f757d66c2732a6ec |
| `papers/diagonal-ramsey-2026/REREFEREE_20261119.md` | f2ac89b198a5682758061556a2440f311db79ecdf997782762d8626e04fc15b8 | 86b14510e12562bb88c1a8a1e05dba7e7128f895e9b712ed36e8799fc9aafda5 |
| `papers/diagonal-ramsey-2026/SELF_CONTAINED.md` | 402bb15859e4d7dd80edb20ffc99e1b184fbc17467e2cf5da6e1e9f6d1194010 | 628ff1db74935af7a25f4f17875b3a3f38c70e470e373eb48ed1cae24ecf8f78 |
| `papers/diagonal-ramsey-2026/evidence/preflight_certs_20261119.log` | f1dbc676d2e309e730d51b2e5767daed6f33a2600dd43f62517dc653498095b8 | fec79ef511e2ca0675f98c1454b179822bba2fd810e860b6255807979b55c001 |
| `papers/diagonal-ramsey-2026/referee1/scripts/cdroot.py` | 2e28f0e77b7fb29c28c49e8893092cc6afb8487417df862931f24d26f244001f | 4508c41bef258da0841467d58b364df06682c2e6280b7e63457bda238c356431 |
| `papers/diagonal-ramsey-2026/referee1/scripts/globalcheck.py` | 1538b0610838896052be79b4b9a3d4e37bff0fd93d5af111f279ed504ce27b2c | 8f74c58502f046ae9a7b10f8ada66f20f2da3c2c9051d9b2d97135d40825c1bc |
| `papers/diagonal-ramsey-2026/referee1/scripts/k7.py` | 92e45f0adaf49469837b460a8db9024a6176b9391133d80f2801f76b64bf890d | ed290c8945b3c0b0a205a2a0d1d82b52ac9ab9d151d1a2040cc3fb57a6722e76 |
| `papers/diagonal-ramsey-2026/referee1/scripts/rootchain.py` | d114c6438d68fb13d450cad8fb7dab05bcded0c48ed9e82c79d589929b10ca72 | 280b78a0f00c4e0aba66739359568cf8abac95912876775d90410363bdbc0b37 |
| `papers/diagonal-ramsey-2026/referee1/scripts/zbank.py` | 0ef83a9eca367b81bc28935649930226d459ddb9a6a506c027bbe874910a4486 | ff7af0ddd714eeddbce6cbf7e84ae12099c7a26c8d09a5f904f4f796f7736489 |
| `papers/diagonal-ramsey-2026/referee2/runC_all.log` | fbad125ad10da4f2a3158ddf4826e8970ad733fffb0f147c42432f40165b64a0 | 97e9416d7fb7cdb1dddb848803a9f697aa8960ab848b60c9931afeb4b34081fa |
| `papers/diagonal-ramsey-2026/referee2/scripts/arith_test.py` | 733e6cd1832dc281b0c2443344058675b0ebbd5027851d2e926974a94d61b4c1 | a68a67d94b5f7d7d1db43091be53f3d0f9a262690de0f47ee7ac1b237b318fb4 |
| `papers/diagonal-ramsey-2026/referee2/scripts/ctl_margin.py` | 881b69a16819707768a154a21af9059a179e907fed52e9e059e039415c97b9af | 8a8907e53e003e433e8bc3ac545676d6d64a39c3c842d54ed9aaf17654712155 |
| `papers/diagonal-ramsey-2026/referee2/scripts/d2check.py` | 23e29f1d25688a4abdbaa97ee8629f8b099ac6a84c1d8067553a1756aee8da77 | f46c72c6c6244fba5db144934d847fc18e3d6478de32d9e6af6cab9ae6fd88c8 |
| `papers/diagonal-ramsey-2026/referee2/scripts/harnessA.py` | f5a783d76f12e898e00d923a562707f295f4ef2bd665628ce9417350594007cd | e755d4f4cfa47244e6f98c1b4dd11163bacd742afd451c0a8fdbcc4ca5b7f9bf |
| `papers/diagonal-ramsey-2026/referee2/scripts/harnessB.py` | f2469a43e8a8b02ad05828695a4b719acdc52bab4827704bf2b63d57571006b3 | 6874aeacdf61cc5401a434d2b3b50727f765eade0d6e3cfd9f518dfc6c8a41c5 |
| `papers/diagonal-ramsey-2026/referee2/scripts/jet_cross.py` | 6530ef37e7a1e8897e675ac9def7488a9c9b3a67310abb2fe9db5f278bd8d981 | 19af6ec059d6e1e78d9994dbad7ffed100b3cfbb39f32a2dd0fddae0d67adc32 |
| `papers/diagonal-ramsey-2026/referee2/scripts/leafcmp.py` | 6da6f86e583eb584b5dec49e38fbc7425b73c683695123f1ebadee480b20151a | 81d47f14b1bb9053cc60aaa021bacf3b1ad7d6a00f5449ba51f917b27105becf |
| `papers/diagonal-ramsey-2026/referee2/scripts/leafdiag.py` | 90b0529324a87ae36cc8767406834f30428b350b75d8c1212d008860cb871043 | f2d72877ccc6307c0b85590be70640413b768aa128c1a3efab355c3aae49bebf |
| `papers/diagonal-ramsey-2026/referee2/scripts/leafdiag2.py` | 003ff0041d2c50eeb2dbdebf1dae4baee2a1a6e4743532ab9980d5d65f1964bc | ed2b05df11da523a60b1ba89a1038ea734639fff771278f29913f3f908812186 |
| `papers/diagonal-ramsey-2026/referee2/scripts/run_tamperD.py` | c9185f0f16e2673e324e9475a4d1b8bad4ddb5860d57ee2cba8bb350bb213f42 | b76cbd5eb94cd17594f63ba71b9860a73ad1a0159d3b866435c4e6c08b344fe7 |
| `papers/diagonal-ramsey-2026/rereferee/pf_tests.py` | 16234497e7452d845cf1b70e737097453fcd0e200e6cbcd4598a007f8beb735b | e1b7d5eca29c17f62ddb0ac13806a57dd2f27d7523c14f01394e311bd231b484 |
| `papers/diagonal-ramsey-2026/rereferee/preflight_real.log` | 725a23eec1a62f850a7403fe8ac991406ff7003b6417630b8f3a7e891c22e293 | 42402bf2a3ce0c04e587a35c8e9f0f0f2f3320237bd06ccba2811305a50ea770 |
| `papers/diagonal-ramsey-2026/tools/preflight_pin_tests.sh` | bb24d8b2daad8905fad0f2271d2416ae962d71511775c6da07323ba87c2c15bf | 96613614e7d2cae4cafef7ee040c74918549d36355338b3390169f98f3a53ed2 |
| `papers/diagonal-ramsey-2026/unconditional/REFEREE_CODE_AUDIT_20261119.md` | 08fa5fd3686ea1f5605123234bf79a65a2584624823119740af38e8745ee24e7 | 57c891b6e2712ca2b432dd2d44791fb739354954110e93c90c26d80c1a64f559 |
| `papers/diagonal-ramsey-2026/unconditional/REFEREE_MERGE_20261119.md` | 3b541ec453ea4950227f02692c9b77150925e99acdf005058c9e673b714b6f1e | 160217ba7a26e8a413962d73728ede093fd33f60c0c9bd06cbdf9a2ddb736cb1 |
| `papers/diagonal-ramsey-2026/unconditional/REFEREE_P1_20261119.md` | 2ce1b72a2dc3008f8415f10cee46309d818d1ef3578a3d340ecf2b0804bd552a | 935cd2c060ebf0dca8034609e46439da85e7a655f4491faf435784ba6ca6b272 |
| `papers/diagonal-ramsey-2026/unconditional/REFEREE_P2_20261119.md` | ebba161904ddb011a26e449cc7940437aa6beb81ca3addfef65a922b44e1f53b | 60085dccb8fbe4f8de982efe17b58f14157034d34d0b993d438f526014a006a5 |
| `papers/diagonal-ramsey-2026/unconditional/REFEREE_P3_20261119.md` | 1fe83ea9ace12b1eb6ea38dddf5d05fb5eb34dc30c1822a0dcd7786f78f2d389 | 0ebcaa9a84403f5bf73cc84c1f2be5d6043b67f1a563542005a865a2165b6e27 |
| `papers/diagonal-ramsey-2026/unconditional/REFEREE_P4_20261119.md` | aa6be16a06941c4ee73f62a52d661b1c2295a51faf3095f4a5e5014f5ee524cc | 0c342c5f60237490cb0921f49fa48f671bc88b2ce28961c265a66e99c967ad0d |
| `papers/diagonal-ramsey-2026/unconditional/REREFEREE_BLOCKS_20261119.md` | c23b7e2717122c865f0b102c9be86be1ff621bb033f1061a946c5c1701a56530 | 7f437fec5bfe61133ab6c0d4c2ce53dffcf553cf075e3ddb9312a11d84444fa4 |
| `papers/diagonal-ramsey-2026/unconditional/cone/parse_20261119.log` | b72313e3eb6c64688fa0ad9416072209d7ce4b2db9fcaa5e85b8ee3b33cbf4ea | 615f52aac7e39a390d8a8cf4ab917684fd2e6e8d34e0431ae0b6ac880af9001a |
| `papers/diagonal-ramsey-2026/unconditional/cone/preflight_full_20261119.log` | 305d4665fbb4abbedd6648a4e2d4f5f1cd46235914a3b593d8877a17caac9250 | dbf62757eff52b92a5ce2fd59fba9a48fabd40417d32012f63e77a1aa870a4db |
| `papers/diagonal-ramsey-2026/unconditional/cone/run_cone.sh` | b638ddeef63f5a336416018f605c78f2fcb423b30f520617bf8c4c22add16b7f | cd40d143f2309c333ae1740858d18955b3c248c45458354c5fbbaa2ce1caf6dc |
| `papers/diagonal-ramsey-2026/unconditional/cone/structure_full_20261119.log` | 46c7c322a1009a60daab5485a4f39e285f5752d03151bccd8aa0381e0d9c2484 | dd639497402ffcfdf3793b7fd69aa4de79d14de5c7c8a73188a0320fe3bc3bbe |
| `papers/diagonal-ramsey-2026/unconditional/cone/structure_full_rerun_20261119.log` | a616a68aef9177e9143700548540024e6fca4e94363408818683a906e36f9b85 | 0429d54d3e606f7d056c5ca6e1866a9412277ac8d69f1fd81147c9d748e94843 |
| `papers/diagonal-ramsey-2026/unconditional/cone/xcheck_zbs_pieces.py` | faf12b6b11602ded9891696a695e38e0bbb99ab48712ab0f9ab9b6f9a004c683 | 17ea3edf42802bf0a97f1e6c87370803c40b6dfc3572776aa8a19d9147c02ba6 |
| `papers/diagonal-ramsey-2026/unconditional/rerun_after_audit_20261119.sh` | 84b458a7ea4d275bd49eb8472379c7b13aca61c0280cf828acb6e91ecc302734 | e7cc9e886bd571d931b91d2b39842a6fee68db410ce78fc772b7517a13828f15 |
| `papers/diagonal-ramsey-2026/unconditional/rerun_after_audit_followup_20261119.sh` | 52e2cb47dbe1456440ae7921022fa4bf8fba1f02d1c86c654453e70752042e54 | d8bc1f32a614f8c102f10fd313012076b1bb50094ca0db4e2b4db4165bf80154 |
| `papers/diagonal-ramsey-2026/unconditional/source/run_2b.sh` | d11d13f13e93e2746b2d5fe9705235bd6909b637d646189a4c1a7f44a3a1e639 | f350f5a7a0d892fc6ba1a9c0cdd38919ff311cb36187e1c8a9161f0f918e78c7 |
| `research/tier1/ramsey-offdiag/cert/offdiag_cd3_v1.json` | 7a390e477f49cc04a5edcc56d23cd6bd5f676ac38c813df298c985d52b68a8d1 | 2b10735de40beed054315e823f15962e71624849a9f4fea8bd3ba3b6abeb7a7b |
| `research/tier1/ramsey-offdiag/cert/offdiag_k3_v1.json` | d4191f4d8d7be4792d223df7c2668d0b79a100724707f77811eb89c3313e6a64 | a30dac7d77c6e0e426376b4d826af97cafc628b9021735d6cf680d9bfc9a90e1 |
| `research/tier1/ramsey-offdiag/code/ramsey_genext_launch.sh` | e1b6ab6e31d062eb9c4c6770dc66ae7bc749017267469e65598a9cf7bf6974c3 | 6cf9910756df938e8d8595531b8f43c73494b84abc6d3a356ca91554930ed4de |
| `research/tier1/ramsey-offdiag/code/ramsey_offdiag_rerun_v2.sh` | 11e10e3e827d4f5aa52352794e77b68f1d9dc73f618c6aa989046c16a5b8873e | aef6697716d9677d34b7c54b89f1c57debe12a44d67d540980c61d42f9837e25 |
| `research/tier1/ramsey-offdiag/code/ramsey_offdiag_rerun_v2b.sh` | ac1216accafd9700c9f49dc1ef2d1cc1a705cf2b5a21a8e8116e913aa5c4d9d6 | b4d7dd0d4f085c7e5340949323cd5c8ff6aa9d5e54fb2a38c4a9fe186f039346 |
| `research/tier1/ramsey-offdiag/code/ramsey_rootgate.py` | 1c6096828c364398317b6caa592effbb46d844413938ffe015101bb100ffd089 | cd283b8e2f7c5d49dae8b797fd0f0a59169f6262c5222e6eac561de53af5eed5 |
| `research/tier1/ramsey-offdiag/code/ramsey_rootgate.sh` | 1f4f0566236c50877611af8aac2346d96d069242167c257f42ca5c1a9f510096 | 56161dc7b4ded72059d83a2da9517614acdd06b8f002b3224e1ff2716b6382b8 |
| `research/tier2/ramsey-lemma/CERT_DESIGN.md` | a78897074bb543dfec38178bd84a938c16299db948a192f0f00b15702930dcfe | 6b4df4ecd7b5c3d7a37c2f8dee869c4f739fa0859427f0dca40cb29b78d9aba7 |
| `research/tier2/ramsey-lemma/cert/explore1.py` | 70d34400ee5a017ad0641ad3c0ebba21d5919ae919617c7e605aa6cfb4916ce2 | aeb77138cbd4bf1633c40d2c1e64c8e96cc8e55802867bc59b30aaa23a718c45 |
| `research/tier2/ramsey-lemma/cert_independent/RUNS_C.log` | ec7aadb1d6423fcb27029369750d5724cd0a6e5bc33a3f8033771fbd15e07e46 | 5adb06c013e0603ed95a9be153fe30798a546ee106c95921be849b3322e6823d |
| `research/tier2/ramsey-lemma/cert_independent/SPEC_ISSUES.md` | 471b5209159f7be1ddaad3dc67064222e2e52f1c99d3fb7ca7e63f888c36236d | 91b3115afc623bd44ac80dabc45a42f69ee6e7c0287f5a0fce396937a23894d2 |
| `research/tier2/ramsey-lemma/cert_independent/leaves_C_right.tsv` | dc6de98bf8cde65b7dbe0bbf7a8d607c2613794c6303d2ec36fb7dda7691978b | 31d57c3bd6eb2ea7d1676c4a51ec68687d16e58a28ad48fb59640528f3b16aaf |
| `research/tier2/ramsey-zbs/RESULT.md` | d6d57730f2964095d882c18e8dda5f9988040ad0886b1947de7897dc0fe11498 | 9cbfb4442f68f0f7fc3e0d4a5b5ba84c1a16c282ebac76d690c560a04ecfa418 |
| `research/tier2/ramsey-zbs/RESULT_CD.md` | 30f7ad6f4a5dede43d1e434a610c31a58dbbba1a4d72c491caef13da6f0b97c2 | 4ee902625728ab83e1a021796d802ef76d004e69cd87628489990cc0a0dbcbd4 |
| `research/tier2/ramsey-zbs/code/lemmaD/FROZEN.txt` | 99cffc4d738fb5723376b77175f257919116e0998d675e5a37e1ba4e702ceca3 | 5463e922e660ee9204a2eb14e17b23d5664880f757d3f3aa7ca082ed82d9c724 |
