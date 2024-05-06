import os
import json

with open('ReVeal_vulnerables.json', 'r') as f:
    jdata = json.load(f)

for idx, d in enumerate(jdata):
    with open(os.path.join('tmp', str(idx)+".c"), 'w') as f:
        f.write(d['code'])
