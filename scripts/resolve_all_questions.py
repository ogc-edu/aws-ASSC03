import os
import sys
import re
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
            print("Error reading cache:", e)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def build_prompt_for_questions(q_list):
    questions_block = ""
    for q in q_list:
        correct_str = ", ".join(q["correctAnswers"])
        opts = "\n".join([f"{k}: {v}" for k, v in sorted(q["options"].items())])
        questions_block += f"""
---
QUESTION {q['id']}:
Prompt: {q['prompt']}
Options:
{opts}
Candidate Answer: Option {correct_str}
"""

    prompt = f"""You are an elite AWS Certified Solutions Architect Associate (SAA-C03) instructor.
Review each exam question below and provide a rigorous, independent technical evaluation for EACH option.

STRICT INSTRUCTIONS:
1. Review the question scenario and candidate answer. If the candidate answer is incorrect, identify the actual correct answer.
2. EVERY OPTION MUST BE VALUED INDEPENDENTLY WITH CONCRETE TECHNICAL REASONS.
3. NEVER USE GENERIC PHRASES LIKE "this answer is not effective", "does not meet requirements", or "introduces suboptimal trade-offs".
4. Explicitly explain the AWS architecture mechanisms: why the correct option works and why EVERY OTHER option is technically wrong (e.g. wrong protocol, lacks durability, excessive operational complexity, incompatible API, unsupported feature, high latency, missing requirement, etc.).

Questions to analyze:
{questions_block}

Format your output clearly separating each question with:
=== QUESTION <ID> ===
### ✅ Why Option <X> is Correct
...
### ❌ Why Other Options Are Incorrect
- **Option <A> is Incorrect**: ...
- **Option <B> is Incorrect**: ...
### 💡 SAA-C03 Exam Concept & AWS Best Practice
...
"""
    return prompt

def generate_single_question(q):
    qid = q["id"]
    correct_str = ", ".join(q["correctAnswers"])
    opts = "\n".join([f"{k}: {v}" for k, v in sorted(q["options"].items())])
    prompt = f"""You are an elite AWS Solutions Architect Associate (SAA-C03) instructor.
Review this exam question and provide a rigorous, independent technical evaluation for EACH option.
NEVER use generic boilerplate like "this answer is not effective" or "does not meet requirements". Explain the exact technical mechanism why the correct option works and why every other option is technically wrong.

Question {qid}:
{q['prompt']}

Options:
{opts}
Candidate Answer: Option {correct_str}

Format your output in clean Markdown:
### ✅ Why Option <X> is Correct
...
### ❌ Why Other Options Are Incorrect
(For EVERY single incorrect option, explain the specific technical reason why it is wrong)
...
### 💡 SAA-C03 Exam Concept & AWS Best Practice
...
"""
    try:
        res = subprocess.run([AGY_BIN, "--model", "gemini-3.8-flash-low", "-p", prompt], capture_output=True, text=True, timeout=45)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception as e:
        print(f"Error single Q{qid}: {e}")
    return None

def run_resolver():
    print("=" * 60)
    print("Starting Comprehensive AWS SAA-C03 Question Resolution Engine")
    print("=" * 60)

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    cache = load_cache()
    q_map = {q["id"]: q for q in questions}

    # Find unresolved questions
    unresolved = []
    for q in questions:
        qid_str = str(q["id"])
        # Check if already resolved with the high-rigor format
        if qid_str in cache and "Why Other Options Are Incorrect" in cache[qid_str]:
            continue
        unresolved.append(q)

    total_all = len(questions)
    resolved_count = total_all - len(unresolved)
    print(f"Total questions: {total_all}")
    print(f"Already resolved: {resolved_count}")
    print(f"Remaining to resolve: {len(unresolved)}")

    if not unresolved:
        print("All questions are already resolved!")
        return

    # Process in batches of 3
    batch_size = 3
    for i in range(0, len(unresolved), batch_size):
        batch = unresolved[i:i + batch_size]
        batch_ids = [q["id"] for q in batch]
        print(f"\nProcessing Batch: Questions {batch_ids} ({resolved_count}/{total_all} - {resolved_count/total_all*100:.1f}%)")

        batch_prompt = build_prompt_for_questions(batch)
        success = False

        try:
            res = subprocess.run([AGY_BIN, "--model", "gemini-3.8-flash-low", "-p", batch_prompt], capture_output=True, text=True, timeout=90)
            if res.returncode == 0 and res.stdout.strip():
                output = res.stdout.strip()
                # Split output by === QUESTION <ID> ===
                parts = re.split(r'===\s*QUESTION\s*(\d+)\s*===', output)
                if len(parts) > 1:
                    for p_idx in range(1, len(parts), 2):
                        qid = int(parts[p_idx])
                        content = parts[p_idx + 1].strip()
                        if "Why Other Options Are Incorrect" in content:
                            cache[str(qid)] = content
                            if qid in q_map:
                                q_map[qid]["explanation"] = content
                                # Extract corrected answer if explicitly mentioned
                                m_corr = re.search(r'Why\s+Option\s+([A-F](?:\s*,\s*[A-F])*)\s+is\s+Correct', content, re.I)
                                if m_corr:
                                    letters = [l.strip().upper() for l in m_corr.group(1).split(',')]
                                    q_map[qid]["correctAnswers"] = letters
                            resolved_count += 1
                            print(f"  ✓ Q#{qid} resolved and cached ({len(content)} chars)")
                    save_cache(cache)
                    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
                        json.dump(questions, f, indent=2, ensure_ascii=False)
                    success = True
        except Exception as e:
            print(f"Batch failed: {e}")

        # If batch failed, fallback to single question processing for this batch
        if not success:
            print("  Retrying questions in batch individually...")
            for q in batch:
                qid = q["id"]
                exp = generate_single_question(q)
                if exp and "Why Other Options Are Incorrect" in exp:
                    cache[str(qid)] = exp
                    q_map[qid]["explanation"] = exp
                    m_corr = re.search(r'Why\s+Option\s+([A-F](?:\s*,\s*[A-F])*)\s+is\s+Correct', exp, re.I)
                    if m_corr:
                        letters = [l.strip().upper() for l in m_corr.group(1).split(',')]
                        q_map[qid]["correctAnswers"] = letters
                    resolved_count += 1
                    save_cache(cache)
                    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
                        json.dump(questions, f, indent=2, ensure_ascii=False)
                    print(f"  ✓ Q#{qid} resolved individually ({len(exp)} chars)")
                else:
                    print(f"  ✗ Q#{qid} failed")
                time.sleep(1)

        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("ALL QUESTIONS RESOLUTION COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    run_resolver()
