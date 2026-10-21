# Dedup fix round

All 9 agents wrote in parallel, so Sets 3-7 contain repeated concepts. new_index.txt (this dir) now lists ALL 325 new
questions ("setN DD #k" = 1-based position k in new/dD_setN.json). existing_index.txt lists Sets 1-2.

Rewrite ONLY the questions listed for you, in place (same position in the same file). For each replacement:
- Same domain; same task statement unless noted; same isMulti, same requiredCount and same number of options;
  keep the same correct letter(s) so the set's answer-letter balance is unchanged.
- The new concept must not appear anywhere in existing_index.txt or new_index.txt (other than the question you are replacing).
- Pick from YOUR topic pool below first — pools are disjoint across agents so replacements don't collide.
  Any other in-scope concept is allowed only if it is clearly absent from both index files.
- Same quality bar as BRIEF.md (current services, unambiguous key, plausible distractors, explanation format).
- If you regenerate files from your generator scripts, make sure the rewrite is in the script too, and never
  regenerate a file you were told is owned by another agent.
Validate the file(s) afterwards (BRIEF2.md command). Reply with only: per replaced question, old topic -> new topic + key.
