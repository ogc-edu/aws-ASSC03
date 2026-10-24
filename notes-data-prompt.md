# Prompt: generate the SAA-C03 study notes data

Copy everything below the line into a new agent session opened at the root of this repository.

---

You are writing the study-notes data for an AWS Certified Solutions Architect – Associate (SAA-C03) study site in this repository. The web pages are already built (`client/src/pages/NotesIndex.jsx`, `NoteTopicPage.jsx`, `NotesCheatSheet.jsx`, `client/src/services/notesService.js`). Your job is **data only**: JSON files under `client/public/notes/`. They are served as static files (locally by Vite, in production from S3 behind CloudFront). Do not change anything under `client/src/`.

## What to read first

1. `client/public/notes/index.json` and `client/public/notes/topics/kms-cloudhsm.json`. These are the one finished example. Match their shape, depth and tone exactly.
2. `scripts/validate_notes.py`. It enforces the format below. Run it with `python3 scripts/validate_notes.py`; it also prints which question tags no note covers yet.
3. `client/public/claude/set-*.json`. Each question there has `domain`, `task` and `topics` (tag strings such as `"AWS KMS"` or `"S3 Bucket Keys"`). The site links notes and questions by matching these tags exactly, so read the tags before you decide your topics.
4. The official exam guide's task statements and in-scope services: https://docs.aws.amazon.com/aws-certification/latest/examguides/solutions-architect-associate-03.html

## Files to produce

```
client/public/notes/index.json            one index for the whole site
client/public/notes/topics/<slug>.json    one file per topic note
```

### `index.json`

```json
{
  "version": 1,
  "examCode": "SAA-C03",
  "generatedOn": "YYYY-MM-DD",
  "domains": [
    {
      "id": 1, "name": "Design Secure Architectures", "weight": 30,
      "tasks": [
        { "id": "1.1", "name": "Design secure access to AWS resources", "topics": ["iam-policies", "..."] }
      ]
    }
  ],
  "topics": {
    "<slug>": {
      "title": "AWS KMS & CloudHSM",
      "domain": 1,
      "task": "1.3",
      "summary": "One sentence, shown on cards and in search results.",
      "keywords": ["search terms", "exam phrases", "acronyms"],
      "questionTopics": ["AWS KMS", "AWS CloudHSM"]
    }
  }
}
```

- Keep `domains` and the 14 task ids and names exactly as in the current file. Only fill in each task's `topics` array, which lists slugs in reading order.
- Every slug in `topics` must appear under **exactly one** task, the one where the exam tests it most. Its `domain` and `task` fields must match that task.
- `questionTopics` copies tag strings **verbatim** from the question sets: same case, same spelling. These strings decide which questions appear under "Related questions" and which notes appear in the "Study this topic" links after a question is answered. A tag may belong to more than one note when it truly spans both (for example `"Amazon S3"`), but prefer specific tags.
- `keywords` feed the search box. Include acronyms and exam phrasing ("lowest operational overhead", "single-tenant HSM").

### `topics/<slug>.json`

```json
{
  "slug": "kms-cloudhsm",
  "title": "…",  "domain": 1,  "task": "1.3",  "summary": "…",
  "services": ["AWS KMS", "AWS CloudHSM"],
  "tldr": ["2–4 markdown bullets: what it is, when the exam wants it"],
  "keyFacts": [{ "value": "4 KB", "text": "Markdown sentence explaining the number or fact." }],
  "comparisons": [{
    "title": "Compare: …",
    "columns": ["Option", "…", "Pick it when…"],
    "rows": [["Row label", "cell", "cell"]],
    "highlightRow": 2
  }],
  "keywords": [{ "cue": "phrase as it appears in a question", "answer": "Service or pattern that answers it" }],
  "traps": ["Markdown sentence describing a distractor the exam uses"],
  "sections": [{ "heading": "Optional deep dive", "body": "Markdown, may use lists" }],
  "relatedNotes": ["other-slug"],
  "sources": [{ "title": "AWS doc page title", "url": "https://docs.aws.amazon.com/…" }]
}
```

- `slug`, `title`, `domain`, `task` and `summary` must equal the note's entry in `index.json`.
- Required and non-empty: `services`, `tldr` (2–4 items), `keyFacts`, `keywords`, `traps`. Optional: `comparisons` (most notes should have one; every row has one cell per column, and the first cell is the row label), `sections`, `relatedNotes` (slugs of other notes), `sources` (https only, prefer docs.aws.amazon.com).
- Strings in `tldr`, `keyFacts[].text`, `traps`, table cells and `sections[].body` are rendered as Markdown: `**bold**`, `*italic*`, `` `code` ``. Keep `keywords[].cue` and `keywords[].answer` plain text, because the cheat sheet prints them unformatted.
- Slugs are lower-case words joined by hyphens, such as `s3-storage-classes` or `vpc-endpoints-privatelink`.

## Content rules

- **Scope:** aim for 50–70 notes that cover all 14 tasks, with at least two notes per task. Size the notes by exam weight (D1 30%, D2 26%, D3 24%, D4 20%) and by how many questions carry each tag. Use the validator's "Uncovered tags used by 2+ questions" list as your checklist. Group related tags into one note (for example "SQS & SNS", or "Multi-AZ vs read replicas") rather than writing one note per tag.
- **Accuracy matters more than volume.** These notes are for passing a real exam in late 2026. Check limits, numbers and feature behaviour against current AWS documentation, and add the page you used to `sources`. If you can't confirm a number, leave it out rather than guess. Watch for facts that have changed in recent years (for example S3 strong consistency, gp3 baselines, KMS rotation periods, Lambda limits).
- **Exam focus:** every note should help someone answer a scenario question. Prefer "when the question says X, pick Y" over general description. Keyword pairs and traps should reflect the distractors that actually appear in the practice sets. Read the explanations of the tagged questions for that.
- Write original text. Don't copy passages from AWS docs, the practice-set explanations, or the PDF/TXT exam dump in the repo root.
- Keep it scannable: TL;DR bullets of one or two sentences, key facts of about 25 words, and traps of one sentence each.

## How to work

1. Read the tags across all sets and draft the topic list (slug → task → questionTopics) in `index.json` first. Run the validator; at this stage expect errors only for the topic files that don't exist yet.
2. Write the topic files domain by domain. Run the validator after each domain and fix every error before moving on.
3. Keep `kms-cloudhsm` (you may improve it). Set `generatedOn` to today.
4. Finish with a run that reports `0 error(s)` and no `WARN` lines about misspelled `questionTopics`.
5. Check the pages in the browser: `.claude/launch.json` has a `client` dev server on port 3000. Open `/notes`, a few `/notes/<slug>` pages, and `/notes/cheatsheet`, and confirm that topic pages list related questions.
6. Don't edit `client/src/`, `client/dist/` or the question sets. Don't commit unless the user asks.

## Definition of done

- `python3 scripts/validate_notes.py` exits 0.
- Every task on `/notes` shows at least two notes.
- Most tags used by two or more questions are covered, and the validator's uncovered list holds only tags you deliberately left out. List those, with the reason, in your final message.
- Your final message lists the note count per domain and any facts you weren't sure about.
