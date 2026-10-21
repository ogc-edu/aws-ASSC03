"""Assemble Sets 4, 5, 6, 7, and 8 from validated raw domain files."""
import json
import random
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_claude_sets import validate, FIELDS, EXAM_FORMAT

SRC = ROOT / "scripts" / "claude_raw_gen"
PUBLIC_CLAUDE = ROOT / "client" / "public" / "claude"
DIST_CLAUDE = ROOT / "client" / "dist" / "claude"

domain_files = [json.loads((SRC / f"d{d}.json").read_text()) for d in (1, 2, 3, 4)]

MAPPING = {
    "4": ("4", 4124, "Claude Mock Exam — Set 4", "Fresh scenarios on KMS and network controls, event-driven fault tolerance, database performance and compute pricing models."),
    "5": ("5", 5155, "Claude Mock Exam — Set 5", "Multi-account governance (Organizations, Control Tower, Identity Center), disaster recovery strategies and storage cost tiers."),
    "6": ("6", 6186, "Claude Mock Exam — Set 6", "Detective controls and compliance, cross-Region recovery, networking and analytics performance, database and network cost."),
    "7": ("7", 7217, "Claude Mock Exam — Set 7", "A final mixed mock: data-level access controls, static stability and recovery automation, streaming analytics and cost governance."),
    "8": ("3", 8248, "Claude Mock Exam — Set 8", "Comprehensive scenarios on IAM trust policies, cross-Region Aurora and DynamoDB replication, event-driven microservices, and compute optimization."),
}

def main():
    PUBLIC_CLAUDE.mkdir(parents=True, exist_ok=True)
    DIST_CLAUDE.mkdir(parents=True, exist_ok=True)

    sets_index_file = PUBLIC_CLAUDE / "sets.json"
    sets_data = json.loads(sets_index_file.read_text())
    existing_sets = {s["id"]: s for s in sets_data["sets"]}

    for out_id, (src_id, seed, title, desc) in MAPPING.items():
        pool = []
        errors = []
        for d, data in enumerate(domain_files, start=1):
            for i, q in enumerate(data[f"set{src_id}"]):
                errs = validate(q, f"Set {out_id} d{d}#{i+1}")
                errors.extend(errs)
                pool.append({k: q[k] for k in FIELDS})

        if errors:
            print(f"Validation errors in Set {out_id}:")
            for e in errors[:5]:
                print("  - " + e)
            sys.exit(1)

        random.Random(seed).shuffle(pool)
        questions = [{"id": i + 1, **q} for i, q in enumerate(pool)]
        d_counts = [sum(q["domain"] == d for q in questions) for d in (1, 2, 3, 4)]
        multi_count = sum(q["isMulti"] for q in questions)
        singles = [q["correctAnswers"][0] for q in questions if not q["isMulti"]]
        dist = {l: singles.count(l) for l in "ABCD"}

        payload = {
            "id": out_id,
            "title": title,
            "description": desc,
            "examCode": EXAM_FORMAT["examCode"],
            "generatedBy": "Claude (Anthropic)",
            "generatedAt": date.today().isoformat(),
            "format": EXAM_FORMAT,
            "questions": questions,
        }

        # Write set file
        pub_file = PUBLIC_CLAUDE / f"set-{out_id}.json"
        pub_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        dist_file = DIST_CLAUDE / f"set-{out_id}.json"
        shutil.copyfile(pub_file, dist_file)

        entry = {
            "id": out_id,
            "title": title,
            "description": desc,
            "questionCount": len(questions),
            "multiCount": multi_count,
            "domainCounts": d_counts,
            "path": f"/claude/{out_id}",
            "file": f"claude/set-{out_id}.json",
        }
        existing_sets[out_id] = entry
        print(f"Set {out_id} assembled: 65 Qs, domains {d_counts}, multi {multi_count}, singles {dist}")

    # Reorder sets by numeric ID
    ordered_ids = sorted(existing_sets.keys(), key=lambda x: int(x))
    sets_data["sets"] = [existing_sets[sid] for sid in ordered_ids]

    sets_index_file.write_text(json.dumps(sets_data, indent=2, ensure_ascii=False) + "\n")
    dist_index = DIST_CLAUDE / "sets.json"
    shutil.copyfile(sets_index_file, dist_index)
    print("Updated sets.json in public/ and dist/")

if __name__ == "__main__":
    main()
