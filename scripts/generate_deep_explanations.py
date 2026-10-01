import os
import sys
import json
import subprocess
import time

AGY_BIN = "/Users/ooiguancheng/.local/bin/agy"
QUESTIONS_FILE = "server/data/questions.json"
CACHE_FILE = "server/data/detailed_explanations.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Error loading cache:", e)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def generate_explanation_for_question(q):
    qid = q["id"]
    prompt = q["prompt"]
    options = q["options"]
    correct = q["correctAnswers"]
    correct_str = ", ".join(correct)
    
    options_text = "\n".join([f"{k}: {v}" for k, v in sorted(options.items())])

    user_prompt = f"""You are an elite AWS Solutions Architect Associate (SAA-C03) instructor.
Review this exact exam question and provide a rigorous, independent technical evaluation for EACH option.

STRICT INSTRUCTIONS:
- EVERY OPTION MUST BE VALUED AND EXPLAINED INDEPENDENTLY WITH CONCRETE TECHNICAL REASONS.
- NEVER USE GENERIC PHRASES LIKE "this answer is not effective", "does not meet requirements", or "introduces suboptimal trade-offs".
- Clearly explain the exact technical mechanism: why the correct option works and why EVERY OTHER option is technically wrong (e.g. wrong protocol, lacks durability, excessive operational complexity, incompatible API, unsupported feature, high latency, missing requirement, etc.).

Question:
{prompt}

Options:
{options_text}

Correct Answer: Option {correct_str}

Format your output in clean Markdown with these exact sections:
### ✅ Why Option {correct_str} is Correct
(Provide concrete technical explanation detailing the AWS service features, architecture pattern, and how it satisfies the scenario)

---

### ❌ Why Other Options Are Incorrect
(For EVERY single incorrect option letter, provide a dedicated bullet explaining the specific technical flaw)

---

### 💡 SAA-C03 Exam Concept & AWS Best Practice
(2-3 key takeaways and architecture rules of thumb tested by this question)
"""

    try:
        res = subprocess.run(
            [AGY_BIN, "--model", "gemini-3.8-flash-low", "-p", user_prompt],
            capture_output=True,
            text=True,
            timeout=40
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
        else:
            print(f"Error for Q{qid}: {res.stderr[:200]}")
            return None
    except Exception as e:
        print(f"Exception generating Q{qid}: {e}")
        return None

def process_batch(start_id=1, end_id=20):
    cache = load_cache()
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    q_map = {q["id"]: q for q in questions}

    print(f"Processing questions from {start_id} to {end_id}...")
    updated = 0

    for qid in range(start_id, end_id + 1):
        if str(qid) in cache and "Why Other Options Are Incorrect" in cache[str(qid)]:
            print(f"Q#{qid} already cached, skipping.")
            continue
        q = q_map.get(qid)
        if not q:
            continue
        print(f"Generating deep explanation for Question #{qid}...")
        exp = generate_explanation_for_question(q)
        if exp:
            cache[str(qid)] = exp
            save_cache(cache)
            # Update questions.json
            q["explanation"] = exp
            updated += 1
            print(f"Saved Q#{qid} deep explanation ({len(exp)} chars).")
        else:
            print(f"Failed to generate for Q#{qid}")
        time.sleep(0.5)

    if updated > 0:
        with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        print(f"Updated {QUESTIONS_FILE} with {updated} new explanations.")

if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    process_batch(start, end)
