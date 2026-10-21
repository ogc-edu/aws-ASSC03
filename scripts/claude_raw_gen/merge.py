import json, sys
from pathlib import Path
QUOTA = {1: (20, 3), 2: (17, 3), 3: (15, 2), 4: (13, 2)}
ok = True
for d in (1, 2, 3, 4):
    data = json.load(open(f"d{d}.json"))
    for n in range(3, 8):
        f = Path(f"new/d{d}_set{n}.json")
        if not f.exists():
            print("MISSING", f); ok = False; continue
        qs = json.load(open(f))
        multi = sum(q["isMulti"] for q in qs)
        if (len(qs), multi) != QUOTA[d] or any(q["domain"] != d for q in qs):
            print("QUOTA", f, len(qs), multi); ok = False
        data[f"set{n}"] = qs
    json.dump(data, open(f"d{d}.json", "w"), indent=2, ensure_ascii=False)
print("ok" if ok else "problems")
