import json, sys
from fractions import Fraction as F
P = "<archive>/ramsey-zbs/zbs_bank.json"
b = json.load(open(P))
print(type(b), list(b.keys()) if isinstance(b, dict) else len(b))
for k, v in b.items():
    if isinstance(v, list):
        print(k, len(v), json.dumps(v[0])[:400])
    else:
        print(k, json.dumps(v)[:300])
