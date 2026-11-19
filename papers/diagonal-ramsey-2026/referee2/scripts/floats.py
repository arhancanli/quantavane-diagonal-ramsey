import json, sys, collections
class FL(float): pass
cert = json.load(open(sys.argv[1]), parse_float=lambda s: FL(s))
c = collections.Counter()
def walk(o, path):
    if isinstance(o, dict):
        for k, v in o.items(): walk(v, path + '.' + k)
    elif isinstance(o, list):
        for v in o: walk(v, path + '[]')
    elif isinstance(o, FL): c[path] += 1
walk(cert, '')
print(c)
print('meta', cert['meta'])
print('gen sample control', cert['controls'][0]['gen'])
print('gen sample raw', cert['raw'][0]['gen'], cert['closed'][0]['gen'])
