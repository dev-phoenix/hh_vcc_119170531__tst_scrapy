# proxy.py
"""collect proxies from json and put to txt"""

import json

cou = 0
with open("proxy_filtered_3.json", "r") as f:
    with open("proxy.txt", "w") as w:
        rows = json.load(f)
        for r in rows:
            # print(r)
            p = r['proxy']
            # print(p)
            w.write(p+"\n")
            cou += 1
print(f"put {cou} proxies")