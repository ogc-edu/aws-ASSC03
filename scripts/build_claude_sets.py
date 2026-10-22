"""Assemble Claude-generated SAA-C03 practice sets.

Usage: python3 scripts/build_claude_sets.py <dir containing d1.json..d4.json>

Each dN.json is {"set1": [...], "set2": [...], ...} of questions for one exam domain.
Questions are validated, mixed across domains (deterministic seed, like the real exam
which does not group by domain), numbered 1..N and written to client/public/claude/.

Only builds Sets 1-2. Set 3 comes from build_set_3.py and Sets 4-8 from
assemble_sets_4_to_8.py; their sets.json entries are left untouched here.
"""
import json
import random
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "client" / "public" / "claude"

EXAM_FORMAT = {
    "examCode": "SAA-C03",
    "verifiedOn": "2026-10-20",
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

SOURCES = [
    {
        "title": "AWS Certified Solutions Architect - Associate (SAA-C03) Exam Guide",
        "url": "https://docs.aws.amazon.com/aws-certification/latest/examguides/solutions-architect-associate-03.html",
    }
]

SETS = {
    "1": {
        "title": "Claude Mock Exam — Set 1",
        "description": "Full-length 65-question mock exam weighted to the current SAA-C03 domain blueprint, written for 2025-2026 AWS services and defaults.",
        "seed": 1031,
    },
    "2": {
        "title": "Claude Mock Exam — Set 2",
        "description": "A second, non-overlapping 65-question mock exam with different scenarios across all four domains.",
        "seed": 2062,
    },
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
        errs.append("isMulti/requiredCount inconsistent with correctAnswers")
    if n_correct == 1 and n_opts != 4:
        errs.append(f"multiple choice must have 4 options, has {n_opts}")
    if n_correct > 1 and n_opts < 5:
        errs.append(f"multiple response must have >=5 options, has {n_opts}")
    if q["domain"] not in (1, 2, 3, 4):
        errs.append(f"bad domain {q['domain']}")
    return [f"{where}: {e}" for e in errs]


def main(src_dir):
    src = Path(src_dir)
    domain_files = [json.loads((src / f"d{d}.json").read_text()) for d in (1, 2, 3, 4)]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    errors, index = [], []

    for set_id, meta in SETS.items():
        pool = []
        for d, data in enumerate(domain_files, start=1):
            for i, q in enumerate(data[f"set{set_id}"]):
                errors += validate(q, f"set{set_id} d{d}#{i + 1}")
                pool.append({k: q[k] for k in FIELDS})

        random.Random(meta["seed"]).shuffle(pool)
        questions = [{"id": i + 1, **q} for i, q in enumerate(pool)]
        domain_counts = [sum(q["domain"] == d for q in questions) for d in (1, 2, 3, 4)]
        multi_count = sum(q["isMulti"] for q in questions)

        payload = {
            "id": set_id,
            "title": meta["title"],
            "description": meta["description"],
            "examCode": EXAM_FORMAT["examCode"],
            "generatedBy": "Claude (Anthropic)",
            "generatedAt": date.today().isoformat(),
            "format": EXAM_FORMAT,
            "questions": questions,
        }
        (OUT_DIR / f"set-{set_id}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        index.append({
            "id": set_id,
            "title": meta["title"],
            "description": meta["description"],
            "questionCount": len(questions),
            "multiCount": multi_count,
            "domainCounts": domain_counts,
            "path": f"/claude/{set_id}",
            "file": f"claude/set-{set_id}.json",
        })
        singles = [q["correctAnswers"][0] for q in questions if not q["isMulti"]]
        dist = {l: singles.count(l) for l in "ABCD"}
        print(f"set {set_id}: {len(questions)} questions, domains {domain_counts}, multi {multi_count}, single-answer letters {dist}")

    index_file = OUT_DIR / "sets.json"
    existing = json.loads(index_file.read_text())["sets"] if index_file.exists() else []
    merged = [s for s in existing if s["id"] not in SETS] + index
    merged.sort(key=lambda s: int(s["id"]))
    index_file.write_text(json.dumps(
        {"examFormat": EXAM_FORMAT, "sources": SOURCES, "sets": merged}, indent=2, ensure_ascii=False) + "\n")

    if errors:
        print("\nVALIDATION ERRORS:\n" + "\n".join(errors))
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1])
