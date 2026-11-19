import json, sys, time
from fractions import Fraction as F
P = sys.argv[1]
t=time.time(); c = json.load(open(P)); print("loaded", time.time()-t)
print("keys", list(c.keys()))
for k,v in c.items():
    if isinstance(v, list): print(k, len(v))
    else: print(k, json.dumps(v)[:300])
root = c["root"]; Qi = root["closed"]; Q = c["closed"][Qi]
print("Q p", Q["p"], "xs", Q["xs"], "ys", Q["ys"], "min", Q["min"])
print("Q pieces", json.dumps(Q["pieces"])[:2000])
ctl0 = c["controls"][0]; print("ctl0 keys", list(ctl0.keys()))
src0 = c["sources"][0]; print("src0", json.dumps(src0)[:800])
