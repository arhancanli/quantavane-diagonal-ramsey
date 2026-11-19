"""Print the top-level structure of a bank certificate (exploration only)."""
import sys, json
d = json.load(open(sys.argv[1]))
print('keys', list(d.keys()))
for k, v in d.items():
    if isinstance(v, list):
        print(k, len(v), json.dumps(v[0])[:600] if v else '')
    else:
        print(k, json.dumps(v)[:600])
