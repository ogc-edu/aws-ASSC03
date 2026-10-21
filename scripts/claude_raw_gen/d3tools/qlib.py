import json
def Q(task, topics, prompt, options, correct, why, wrong, tips):
    correct = sorted(correct)
    multi = len(correct) > 1
    if multi:
        n = len(correct)
        word = {2: "TWO", 3: "THREE"}[n]
        assert prompt.endswith(f"(Select {word}.)"), prompt
        assert len(options) == {2: 5, 3: 6}[n]
        head = "### ✅ Why Options " + " & ".join(correct) + " are Correct"
    else:
        assert len(options) == 4
        head = f"### ✅ Why Option {correct[0]} is Correct"
    assert set(wrong) == set(options) - set(correct), (prompt[:40], wrong.keys())
    exp = head + "\n\n" + "\n".join(f"* **{k}:** {v}" for k, v in why) + "\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n"
    exp += "\n".join(f"* **Option {k} is incorrect:** {wrong[k]}" for k in sorted(wrong))
    exp += "\n\n---\n\n### \U0001F4A1 SAA-C03 Exam Concept & AWS Best Practice\n\n"
    exp += "\n".join(f"{i+1}. **{k}:** {v}" for i, (k, v) in enumerate(tips))
    return {"domain": 3, "task": task, "topics": topics, "prompt": prompt, "options": options,
            "isMulti": multi, "requiredCount": len(correct), "correctAnswers": correct, "explanation": exp}
def dump(qs, path):
    assert len(qs) == 15
    json.dump(qs, open(path, "w"), indent=2, ensure_ascii=False)
