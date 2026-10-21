# Addendum for Sets 3-7 (overrides the "Output" section of BRIEF.md)

Read BRIEF.md (format, currency, accuracy, explanation markdown) — all of it still applies — then this file.

## Avoid repeats
existing_index.txt lists the 130 questions already written for Sets 1-2 (set, domain, task, topics, prompt start).
Do NOT re-test a concept/scenario already there with the same answer. Other agents are writing the other domains and
other sets in parallel; each agent has a service emphasis list (in its task) to keep coverage spread out. Draw mainly from
your emphasis list, but any in-scope service is allowed when a scenario needs it. Within your own output, no two questions
may test the same concept.

## Per-set quotas (per domain, per set)
- Domain 1: 20 questions, 3 of them multiple response
- Domain 2: 17 questions, 3 multiple response
- Domain 3: 15 questions, 2 multiple response
- Domain 4: 13 questions, 2 multiple response
Cover every task statement of the domain in each set (roughly in proportion). Multiple response: mostly "Select TWO." (5 options),
at most one "Select THREE." (6 options) per set per domain. Balance single-choice correct letters A/B/C/D within each set.
Vary the question stems: MOST cost-effective, LEAST operational overhead, MOST secure, highest availability, lowest latency, etc.

## Output
Write ONE JSON array file per set: new/d{DOMAIN}_set{N}.json (relative to this gen directory), e.g. new/d2_set5.json.
Write and validate one set file at a time. Validate each with:
python3 -c "import json;q=json.load(open('PATH'));print(len(q));[print(i,x['task'],x['correctAnswers']) for i,x in enumerate(q)]"
Then re-read every question and re-verify the facts and the answer key before finishing.
Reply with only a short summary: per set, count, multi count, answer-letter distribution, and the topics covered.
