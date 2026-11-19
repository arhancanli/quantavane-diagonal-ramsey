#!/bin/bash
# Red/green controls for the preflight's Theorem 5.7 proviso check: margins 5e-13 must pass; eps = 7e-15 and
# eta = 7.9e-15 (both below 8/10^15) must be refused.   usage: bash preflight_proviso_tests.sh <scratch dir>
D=$1; mkdir -p $D; HERE=$(cd "$(dirname "$0")" && pwd)
echo '{"controls": [], "sources": [{"eps": "1/2000000000000", "eta": "1/2000000000000"}]}' > $D/ok.json
echo '{"controls": [], "sources": [{"eps": "7/1000000000000000", "eta": "1/2000000000000"}]}' > $D/bad_eps.json
echo '{"controls": [], "sources": [{"eps": "1/2000000000000", "eta": "79/10000000000000000"}]}' > $D/bad_eta.json
for f in ok bad_eps bad_eta; do echo "$f: $(python3 -I $HERE/preflight.py $D/$f.json | tail -1)"; done
