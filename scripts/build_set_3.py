"""Build, balance, and validate Set 3, updating client/public/claude and client/dist/claude."""
import json
import random
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from sets_data.set_3_d1 import QUESTIONS as D1_QUESTIONS
from sets_data.set_3_d2 import QUESTIONS as D2_QUESTIONS
from sets_data.set_3_d3 import QUESTIONS as D3_QUESTIONS
from sets_data.set_3_d4 import QUESTIONS as D4_QUESTIONS

PUBLIC_CLAUDE = ROOT / "client" / "public" / "claude"
DIST_CLAUDE = ROOT / "client" / "dist" / "claude"

EXAM_FORMAT = {
    "examCode": "SAA-C03",
    "verifiedOn": "2026-10-21",
    "totalQuestions": 65,
    "scoredQuestions": 50,
    "unscoredQuestions": 15,
    "durationMinutes": 130,
    "passingScore": 720,
    "scoreRange": "100-1000",
    "approxPassingPercent": 72,
    "responseTypes": [
        "Multiple choice: one correct response and three distractors",
        "Multiple response: two or more correct responses out of five or more options",
    ],
    "domains": [
        {"id": 1, "name": "Design Secure Architectures", "weight": 30},
        {"id": 2, "name": "Design Resilient Architectures", "weight": 26},
        {"id": 3, "name": "Design High-Performing Architectures", "weight": 24},
        {"id": 4, "name": "Design Cost-Optimized Architectures", "weight": 20},
    ],
}

FIELDS = ("domain", "task", "topics", "prompt", "options", "isMulti", "requiredCount", "correctAnswers", "explanation")


def validate(q, where):
    errs = [f"missing {f}" for f in FIELDS if f not in q]
    if errs:
        return [f"{where}: {e}" for e in errs]
    letters = sorted(q["options"])
    n_opts, n_correct = len(letters), len(q["correctAnswers"])
    if letters != [chr(65 + i) for i in range(n_opts)]:
        errs.append(f"option letters not contiguous: {letters}")
    if not set(q["correctAnswers"]) <= set(letters):
        errs.append(f"correct answers {q['correctAnswers']} not in options")
    if len(set(q["correctAnswers"])) != n_correct:
        errs.append("duplicate correct answers")
    if q["requiredCount"] != n_correct or q["isMulti"] != (n_correct > 1):
        errs.append(f"isMulti/requiredCount inconsistent with correctAnswers: req={q['requiredCount']} n_corr={n_correct} isMulti={q['isMulti']}")
    if n_correct == 1 and n_opts != 4:
        errs.append(f"multiple choice must have 4 options, has {n_opts}")
    if n_correct > 1 and n_opts < 5:
        errs.append(f"multiple response must have >=5 options, has {n_opts}")
    if q["domain"] not in (1, 2, 3, 4):
        errs.append(f"bad domain {q['domain']}")
    return [f"{where}: {e}" for e in errs]


def remap_single(q, target_corr):
    old_corr = q["correctAnswers"][0]
    if old_corr == target_corr:
        return q

    # Swap old_corr and target_corr
    swap_a, swap_b = old_corr, target_corr
    letter_map = {l: l for l in "ABCD"}
    letter_map[swap_a] = swap_b
    letter_map[swap_b] = swap_a

    # New options
    new_options = {letter_map[l]: text for l, text in q["options"].items()}
    new_options = {l: new_options[l] for l in sorted(new_options)}

    # Parse explanation
    exp = q["explanation"]
    parts = exp.split("---")
    if len(parts) != 3:
        raise ValueError(f"Expected 3 parts in explanation, got {len(parts)}")

    correct_sec, incorrect_sec, tip_sec = parts[0], parts[1], parts[2]

    # In correct section: update header
    correct_sec = re.sub(r"### ✅ Why Option [A-D] is Correct", f"### ✅ Why Option {target_corr} is Correct", correct_sec)

    # In incorrect section: find bullets
    bullets = []
    lines = incorrect_sec.strip().split("\n")
    header_line = lines[0]
    current_bullet_letter = None
    current_bullet_lines = []

    for line in lines[1:]:
        m = re.match(r"^\* \*\*Option ([A-D]) is incorrect", line)
        if m:
            if current_bullet_letter:
                bullets.append((current_bullet_letter, "\n".join(current_bullet_lines)))
            current_bullet_letter = m.group(1)
            current_bullet_lines = [line]
        elif current_bullet_letter:
            current_bullet_lines.append(line)

    if current_bullet_letter:
        bullets.append((current_bullet_letter, "\n".join(current_bullet_lines)))

    if len(bullets) != 3:
        raise ValueError(f"Expected 3 distractor bullets, got {len(bullets)}: {[b[0] for b in bullets]}")

    new_bullets = []
    for old_l, b_text in bullets:
        new_l = letter_map[old_l]
        updated_text = re.sub(r"^\* \*\*Option " + old_l + r" is incorrect", f"* **Option {new_l} is incorrect", b_text)
        new_bullets.append((new_l, updated_text))

    # Sort bullets by new letter
    new_bullets.sort(key=lambda x: x[0])
    new_incorrect_sec = header_line + "\n\n" + "\n".join(b[1] for b in new_bullets) + "\n\n"

    new_exp = correct_sec.rstrip() + "\n\n---\n\n" + new_incorrect_sec + "---\n" + tip_sec

    return {
        **q,
        "options": new_options,
        "correctAnswers": [target_corr],
        "explanation": new_exp,
    }


def main():
    domain_groups = [D1_QUESTIONS, D2_QUESTIONS, D3_QUESTIONS, D4_QUESTIONS]
    expected_counts = [20, 17, 15, 13]

    # Check raw counts
    for d_idx, (group, exp) in enumerate(zip(domain_groups, expected_counts), start=1):
        if len(group) != exp:
            print(f"Domain {d_idx} count mismatch: got {len(group)}, expected {exp}")
            sys.exit(1)

    # Rebalance single choice questions across ABCD
    all_raw = []
    for g in domain_groups:
        all_raw.extend(g)

    single_qs = [q for q in all_raw if not q["isMulti"]]
    multi_qs = [q for q in all_raw if q["isMulti"]]

    # Target rotation: A, B, C, D cyclically
    targets = [["A", "B", "C", "D"][i % 4] for i in range(len(single_qs))]

    remapped_singles = []
    for q, target in zip(single_qs, targets):
        remapped_singles.append(remap_single(q, target))

    # Re-group by domain
    pool = []
    for q in remapped_singles + multi_qs:
        pool.append({k: q[k] for k in FIELDS})

    # Validate all pooled questions
    errors = []
    for i, q in enumerate(pool):
        errors.extend(validate(q, f"Pool Q{i+1} [D{q['domain']}]"))

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print("  - " + e)
        sys.exit(1)

    # Shuffle with seed 3093 (matching build_claude_sets.py metadata)
    random.Random(3093).shuffle(pool)
    questions = [{"id": i + 1, **q} for i, q in enumerate(pool)]

    domain_counts = [sum(q["domain"] == d for q in questions) for d in (1, 2, 3, 4)]
    multi_count = sum(q["isMulti"] for q in questions)
    singles = [q["correctAnswers"][0] for q in questions if not q["isMulti"]]
    dist = {l: singles.count(l) for l in "ABCD"}

    print("Set 3 successfully balanced and assembled:")
    print(f"  Total questions: {len(questions)}")
    print(f"  Domain counts: {domain_counts}")
    print(f"  Multiple response questions: {multi_count}")
    print(f"  Single answer distribution: {dist}")

    meta = {
        "id": "3",
        "title": "Claude & Gemini Mock Exam — Set 3",
        "description": "Identity-heavy security (permissions boundaries, ABAC, Cognito, WAF), messaging resilience and storage/compute performance tuning.",
        "examCode": "SAA-C03",
        "generatedBy": "Claude & Gemini (AI Collaboration)",
        "generatedAt": date.today().isoformat(),
        "format": EXAM_FORMAT,
        "questions": questions,
    }

    # Write set-3.json
    PUBLIC_CLAUDE.mkdir(parents=True, exist_ok=True)
    DIST_CLAUDE.mkdir(parents=True, exist_ok=True)

    set3_file = PUBLIC_CLAUDE / "set-3.json"
    set3_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {set3_file}")

    dist_set3_file = DIST_CLAUDE / "set-3.json"
    shutil.copyfile(set3_file, dist_set3_file)
    print(f"Copied to {dist_set3_file}")

    # Update sets.json in public and dist
    sets_index_file = PUBLIC_CLAUDE / "sets.json"
    sets_data = json.loads(sets_index_file.read_text())

    existing_ids = [s["id"] for s in sets_data["sets"]]
    set3_entry = {
        "id": "3",
        "title": meta["title"],
        "description": meta["description"],
        "questionCount": len(questions),
        "multiCount": multi_count,
        "domainCounts": domain_counts,
        "path": "/claude/3",
        "file": "claude/set-3.json",
    }

    if "3" in existing_ids:
        for idx, s in enumerate(sets_data["sets"]):
            if s["id"] == "3":
                sets_data["sets"][idx] = set3_entry
    else:
        sets_data["sets"].append(set3_entry)

    sets_index_file.write_text(json.dumps(sets_data, indent=2, ensure_ascii=False) + "\n")
    print(f"Updated {sets_index_file}")

    dist_sets_index = DIST_CLAUDE / "sets.json"
    shutil.copyfile(sets_index_file, dist_sets_index)
    print(f"Copied to {dist_sets_index}")


if __name__ == "__main__":
    main()
