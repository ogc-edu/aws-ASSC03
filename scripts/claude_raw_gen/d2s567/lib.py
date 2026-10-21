import json, sys
L = "ABCDEF"
def build(items, out):
    res = []
    for it in items:
        opts = {L[i]: o for i, o in enumerate(it["o"])}
        corr = list(it["c"])
        n = len(corr)
        assert all(c in opts for c in corr)
        if n == 1:
            assert len(opts) == 4
            head = f"### ✅ Why Option {corr[0]} is Correct"
        else:
            assert (n == 2 and len(opts) == 5) or (n == 3 and len(opts) == 6), it["p"][:60]
            names = ", ".join(corr[:-1]) + " & " + corr[-1]
            head = f"### ✅ Why Options {names} are Correct"
            suffix = "(Select TWO.)" if n == 2 else "(Select THREE.)"
            assert it["p"].endswith(suffix), it["p"][-40:]
        wrong = [k for k in opts if k not in corr]
        assert sorted(it["x"].keys()) == wrong, (it["p"][:60], sorted(it["x"].keys()), wrong)
        ex = head + "\n\n" + "\n".join(f"* **{k}:** {v}" for k, v in it["w"])
        ex += "\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n"
        ex += "\n".join(f"* **Option {k} is incorrect:** {it['x'][k]}" for k in wrong)
        ex += "\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n"
        ex += "\n".join(f"{i+1}. **{k}:** {v}" for i, (k, v) in enumerate(it["e"]))
        res.append({"domain": 2, "task": it["t"], "topics": it["tp"], "prompt": it["p"], "options": opts,
                    "isMulti": n > 1, "requiredCount": n, "correctAnswers": corr, "explanation": ex})
    json.dump(res, open(out, "w"), indent=2, ensure_ascii=False)
    from collections import Counter
    print(len(res), "multi", sum(q["isMulti"] for q in res),
          Counter(q["correctAnswers"][0] for q in res if not q["isMulti"]),
          Counter(q["task"] for q in res))
