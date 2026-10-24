#!/usr/bin/env python3
"""Validate the study notes in client/public/notes against the format the /notes pages read.

Checks index.json and every topics/<slug>.json, and reports which question topic tags
in the Claude practice sets no note covers yet. Exits 1 if any error is found.

Usage: python3 scripts/validate_notes.py
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES = ROOT / "client" / "public" / "notes"
SETS = ROOT / "client" / "public" / "claude"

TASKS = {
    1: ["1.1", "1.2", "1.3"],
    2: ["2.1", "2.2"],
    3: ["3.1", "3.2", "3.3", "3.4", "3.5"],
    4: ["4.1", "4.2", "4.3", "4.4"],
}
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def is_str_list(v, allow_empty=False):
    return isinstance(v, list) and (allow_empty or v) and all(isinstance(x, str) and x.strip() for x in v)


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        err(f"{path.relative_to(ROOT)}: missing")
    except json.JSONDecodeError as e:
        err(f"{path.relative_to(ROOT)}: invalid JSON ({e})")
    return None


def question_tags():
    tags = Counter()
    for f in sorted(SETS.glob("set-*.json")):
        for q in json.loads(f.read_text(encoding="utf-8")).get("questions", []):
            tags.update(q.get("topics", []))
    return tags


def check_index(index):
    topics = index.get("topics")
    if not isinstance(topics, dict) or not topics:
        err("index.json: 'topics' must be a non-empty object keyed by slug")
        return {}

    placed = Counter()
    domains = index.get("domains")
    if not isinstance(domains, list) or [d.get("id") for d in domains] != [1, 2, 3, 4]:
        err("index.json: 'domains' must list domains 1-4 in order")
        domains = []
    for d in domains:
        ids = [t.get("id") for t in d.get("tasks", [])]
        if ids != TASKS[d["id"]]:
            err(f"index.json: domain {d['id']} tasks must be {TASKS[d['id']]}, got {ids}")
        for t in d.get("tasks", []):
            if not isinstance(t.get("topics"), list):
                err(f"index.json: task {t.get('id')} needs a 'topics' list")
                continue
            for slug in t["topics"]:
                placed[slug] += 1
                entry = topics.get(slug)
                if entry is None:
                    err(f"index.json: task {t['id']} lists '{slug}', which is not in 'topics'")
                elif entry.get("task") != t["id"]:
                    err(f"index.json: '{slug}' is listed under task {t['id']} but its entry says task {entry.get('task')}")

    for slug, entry in topics.items():
        where = f"index.json topics['{slug}']"
        if not SLUG.match(slug):
            err(f"{where}: slug must be lower-case words joined by '-'")
        if placed[slug] != 1:
            err(f"{where}: must be listed under exactly one task (found {placed[slug]})")
        for key in ("title", "summary"):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                err(f"{where}: '{key}' must be a non-empty string")
        if entry.get("domain") not in TASKS or entry.get("task") not in TASKS.get(entry.get("domain"), []):
            err(f"{where}: domain/task {entry.get('domain')}/{entry.get('task')} is not a valid pair")
        if not is_str_list(entry.get("keywords")):
            err(f"{where}: 'keywords' must be a non-empty list of strings")
        if not is_str_list(entry.get("questionTopics")):
            err(f"{where}: 'questionTopics' must be a non-empty list of strings")
    return topics


def check_topic(slug, entry, all_slugs):
    path = NOTES / "topics" / f"{slug}.json"
    note = load(path)
    if note is None:
        return
    where = f"topics/{slug}.json"
    if note.get("slug") != slug:
        err(f"{where}: 'slug' must be '{slug}'")
    for key in ("title", "domain", "task", "summary"):
        if note.get(key) != entry.get(key):
            err(f"{where}: '{key}' differs from index.json ({note.get(key)!r} vs {entry.get(key)!r})")
    if not is_str_list(note.get("services")):
        err(f"{where}: 'services' must be a non-empty list of strings")
    if not is_str_list(note.get("tldr")) or not 2 <= len(note["tldr"]) <= 4:
        err(f"{where}: 'tldr' must hold 2-4 strings")
    if not is_str_list(note.get("traps")):
        err(f"{where}: 'traps' must be a non-empty list of strings")

    facts = note.get("keyFacts")
    if not isinstance(facts, list) or not facts:
        err(f"{where}: 'keyFacts' must be a non-empty list")
    else:
        for i, f in enumerate(facts):
            if not (isinstance(f, dict) and str(f.get("value", "")).strip() and str(f.get("text", "")).strip()):
                err(f"{where}: keyFacts[{i}] needs non-empty 'value' and 'text'")

    kws = note.get("keywords")
    if not isinstance(kws, list) or not kws:
        err(f"{where}: 'keywords' must be a non-empty list")
    else:
        for i, k in enumerate(kws):
            if not (isinstance(k, dict) and str(k.get("cue", "")).strip() and str(k.get("answer", "")).strip()):
                err(f"{where}: keywords[{i}] needs non-empty 'cue' and 'answer'")

    for i, c in enumerate(note.get("comparisons", [])):
        cols = c.get("columns")
        if not c.get("title") or not is_str_list(cols) or len(cols) < 2:
            err(f"{where}: comparisons[{i}] needs a 'title' and 2+ 'columns'")
            continue
        rows = c.get("rows")
        if not isinstance(rows, list) or not rows:
            err(f"{where}: comparisons[{i}] needs 'rows'")
            continue
        for r, row in enumerate(rows):
            if not is_str_list(row) or len(row) != len(cols):
                err(f"{where}: comparisons[{i}].rows[{r}] must have {len(cols)} non-empty strings")
        hl = c.get("highlightRow")
        if hl is not None and not (isinstance(hl, int) and 0 <= hl < len(rows)):
            err(f"{where}: comparisons[{i}].highlightRow must be a row index or omitted")

    for i, s in enumerate(note.get("sections", [])):
        if not (isinstance(s, dict) and str(s.get("heading", "")).strip() and str(s.get("body", "")).strip()):
            err(f"{where}: sections[{i}] needs non-empty 'heading' and 'body'")

    for other in note.get("relatedNotes", []):
        if other not in all_slugs or other == slug:
            err(f"{where}: relatedNotes '{other}' is not another note in index.json")

    for i, s in enumerate(note.get("sources", [])):
        if not (isinstance(s, dict) and s.get("title") and str(s.get("url", "")).startswith("https://")):
            err(f"{where}: sources[{i}] needs a 'title' and an https 'url'")


def main():
    index = load(NOTES / "index.json")
    if index is None:
        return report(Counter(), set())
    topics = check_index(index)
    for slug, entry in topics.items():
        check_topic(slug, entry, set(topics))

    for f in (NOTES / "topics").glob("*.json"):
        if f.stem not in topics:
            warnings.append(f"topics/{f.name} is not listed in index.json, so the site never shows it")

    tags = question_tags()
    covered = set()
    for slug, entry in topics.items():
        for tag in entry.get("questionTopics", []):
            if tag not in tags:
                warnings.append(f"'{slug}' questionTopics: no question is tagged '{tag}' (check spelling and case)")
            covered.add(tag)
    return report(tags, covered)


def report(tags, covered):
    total = sum(tags.values())
    hit = sum(n for t, n in tags.items() if t in covered)
    uncovered = sorted(((n, t) for t, n in tags.items() if t not in covered), reverse=True)

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    if tags:
        print(f"\nTag coverage: {len(covered & set(tags))}/{len(tags)} distinct tags, {hit}/{total} tag uses")
        frequent = [(n, t) for n, t in uncovered if n >= 2]
        if frequent:
            print("Uncovered tags used by 2+ questions:")
            for n, t in frequent:
                print(f"  {n:3d}  {t}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
