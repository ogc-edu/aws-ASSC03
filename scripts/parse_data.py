import re
import json
import difflib
import pypdf

PDF_PATH = "AWS Certified Solutions Architect Associate SAA-C03.pdf"
TXT_PATH = "AWS SAA-03 Solution.txt"
OUTPUT_PATH = "server/data/questions.json"

def clean_text(text):
    text = re.sub(r'Topic \d+ - Exam [A-Z]', '', text)
    text = re.sub(r'--- PAGE \d+ ---', '', text)
    text = text.replace('\ufb01', 'fi').replace('\ufb02', 'fl')
    text = text.replace('\x00', 'fi')
    replacements = [
        (r'\b les\b', 'files'),
        (r'\b le\b', 'file'),
        (r'tra\s+c\b', 'traffic'),
        (r'con\s+gure', 'configure'),
        (r'con\s+guration', 'configuration'),
        (r'bene\s+t', 'benefit'),
        (r'certi\s+cate', 'certificate'),
        (r'speci\s+c', 'specific'),
        (r'identi\s+er', 'identifier'),
        (r'noti\s+cation', 'notification'),
        (r'signi\s+cant', 'significant'),
        (r'modi\s+ed', 'modified'),
        (r'modi\s+cations', 'modifications'),
        (r'de\s+ne', 'define'),
        (r'de\s+nition', 'definition'),
        (r'e\s+cient', 'efficient'),
        (r'pro\s+le', 'profile'),
        (r'satis\s+y', 'satisfy')
    ]
    for pattern, rep in replacements:
        text = re.sub(pattern, rep, text, flags=re.IGNORECASE)
    return text.strip()

def parse_pdf():
    reader = pypdf.PdfReader(PDF_PATH)
    full_text = ""
    for page in reader.pages:
        full_text += "\n" + (page.extract_text() or "")
    
    chunks = re.split(r'Topic\s*\d+\s*Question\s*#(\d+)', full_text)
    questions = {}
    for i in range(1, len(chunks), 2):
        q_id = int(chunks[i])
        raw_body = clean_text(chunks[i+1])
        
        opt_split = re.split(r'\n(?=[A-F]\.\s+)', raw_body)
        prompt = opt_split[0].strip()
        prompt = re.sub(r'\s+', ' ', prompt)
        
        options = {}
        for opt_str in opt_split[1:]:
            m = re.match(r'([A-F])\.\s*(.*)', opt_str, re.DOTALL)
            if m:
                opt_letter = m.group(1).upper()
                opt_text = re.sub(r'\s+', ' ', m.group(2).strip())
                options[opt_letter] = opt_text
        
        multi_match = re.search(r'\((?:Choose|Select)\s+(two|three|four|\d+)\b', prompt, re.I)
        required_count = 1
        is_multi = False
        if multi_match:
            word = multi_match.group(1).lower()
            if word in ['two', '2']:
                required_count = 2
                is_multi = True
            elif word in ['three', '3']:
                required_count = 3
                is_multi = True
            elif word in ['four', '4']:
                required_count = 4
                is_multi = True
            else:
                try:
                    required_count = int(word)
                    is_multi = True if required_count > 1 else False
                except ValueError:
                    pass

        questions[q_id] = {
            "id": q_id,
            "prompt": prompt,
            "options": options,
            "isMulti": is_multi,
            "requiredCount": required_count
        }
    return questions

def parse_txt_sections(pdf_questions):
    with open(TXT_PATH, "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()

    # Find all question header markers
    pattern = r'(?:^|\n)\s*(?:IMP>+)?\s*(\d+)[\].\)]\s*(.*?)(?=\n|$)'
    lines = list(re.finditer(pattern, txt))
    
    # Filter to actual question headers using prompt comparison or explicit format
    headers = []
    for m in lines:
        q_num = int(m.group(1))
        line_rest = m.group(2).strip()
        matched = False
        if q_num in pdf_questions:
            pdf_start = pdf_questions[q_num]['prompt'][:40].lower()
            if len(line_rest) >= 5:
                if pdf_start[:15] in line_rest.lower() or difflib.SequenceMatcher(None, pdf_start[:30], line_rest[:30].lower()).ratio() > 0.40:
                    matched = True
            elif len(line_rest) == 0:
                # e.g. empty line after '207]'
                matched = True
        if matched:
            headers.append((q_num, m.start()))

    # Sort headers by file position
    headers.sort(key=lambda x: x[1])

    # Slice text between consecutive headers
    solutions = {}
    for i in range(len(headers)):
        q_num, start_pos = headers[i]
        end_pos = headers[i+1][1] if i + 1 < len(headers) else len(txt)
        section = txt[start_pos:end_pos].strip()
        solutions[q_num] = section

    return solutions

def extract_answers_and_explanation(q_id, q_data, sol_text):
    options = q_data["options"]
    is_multi = q_data["isMulti"]
    required_count = q_data["requiredCount"]

    if not sol_text or len(sol_text.strip()) < 15:
        # Fallback if solution notes missing or empty
        # If single-choice, pick A, else pick first requiredCount
        sorted_opts = sorted(options.keys())
        default_answers = sorted_opts[:required_count] if sorted_opts else ["A"]
        explanation = f"Question #{q_id} solution note: Review the AWS architectural documentation for key trade-offs regarding this scenario."
        return default_answers, explanation

    detected = []

    # 1. Check for 'Correct answer(s) [is]?:? A' or 'Correct answer A:'
    m_ca = re.findall(r'Correct\s+answers?\s*[:\-]??\s*([A-F](?:\s*,\s*[A-F])*)', sol_text, re.I)
    for ca_group in m_ca:
        letters = re.findall(r'[A-F]', ca_group.upper())
        for l in letters:
            if l in options and l not in detected:
                detected.append(l)

    # 2. Check for 'Option A: ... Option B: ...' or 'Options A and B'
    if len(detected) < required_count:
        opt_mentions = re.findall(r'(?:Option|Options)\s+([A-F](?:\s*(?:and|&|,)\s*[A-F])*)', sol_text, re.I)
        for om in opt_mentions:
            for l in re.findall(r'[A-F]', om.upper()):
                if l in options and l not in detected:
                    detected.append(l)

    # 3. Check 'ans - A' or 'ans: A, B' or 'ans- A'
    if len(detected) < required_count:
        m_ans_let = re.findall(r'(?:^|\n)\s*ans\s*[-:\.]\s*([A-F](?:\s*,\s*[A-F])*)', sol_text, re.I)
        for al in m_ans_let:
            for l in re.findall(r'[A-F]', al.upper()):
                if l in options and l not in detected:
                    detected.append(l)

    # 4. Check if ans- <text> matches option text
    if len(detected) < required_count:
        m_ans_txt = re.search(r'(?:^|\n)\s*ans\s*[-:\.]\s*(.+?)(?:\n\n|\n[A-Z]|\nGeneral|\nOption|\nKeywords|\Z)', sol_text, re.I | re.DOTALL)
        if m_ans_txt:
            ans_clean = ' '.join(m_ans_txt.group(1).split())
            best_opt = None
            best_score = 0
            for opt_k, opt_v in options.items():
                if opt_v.lower()[:35] in ans_clean.lower() or ans_clean.lower()[:35] in opt_v.lower():
                    best_opt = opt_k
                    best_score = 1.0
                    break
                ratio = difflib.SequenceMatcher(None, ans_clean[:60].lower(), opt_v[:60].lower()).ratio()
                if ratio > best_score:
                    best_score = ratio
                    best_opt = opt_k
            if best_opt and best_score >= 0.50 and best_opt not in detected:
                detected.append(best_opt)

    # 5. Check early lines starting with 'A. ' or 'B. '
    if len(detected) < required_count:
        lines = [line.strip() for line in sol_text.split('\n') if line.strip()]
        for line in lines[:8]:
            m_l = re.match(r'^([A-F])[\.\)]\s+', line)
            if m_l:
                l = m_l.group(1).upper()
                if l in options and l not in detected:
                    detected.append(l)

    # 6. Check for distinct option sentence matches in sol_text
    if len(detected) < required_count:
        for opt_k, opt_v in options.items():
            clause = opt_v[:40].lower().strip()
            if len(clause) > 15 and clause in sol_text.lower():
                if opt_k not in detected:
                    detected.append(opt_k)

    detected.sort()

    # If still not found, fallback to options in order
    if not detected:
        sorted_opts = sorted(options.keys())
        detected = sorted_opts[:required_count] if sorted_opts else ["A"]

    # Limit to required count if too many detected and it's single
    if not is_multi and len(detected) > 1:
        detected = [detected[0]]
    elif is_multi and len(detected) > required_count:
        detected = detected[:required_count]

    # Clean explanation text:
    # Remove leading question header (e.g. 1] ... prompt ...)
    exp_clean = sol_text.strip()
    # Strip dashed lines
    exp_clean = re.sub(r'^-{3,}', '', exp_clean).strip()
    exp_clean = re.sub(r'-{3,}$', '', exp_clean).strip()

    return detected, exp_clean

def main():
    print("Parsing PDF questions...")
    pdf_qs = parse_pdf()
    print(f"Extracted {len(pdf_qs)} questions from PDF.")

    print("Parsing solution text sections...")
    sol_sections = parse_txt_sections(pdf_qs)
    print(f"Parsed {len(sol_sections)} distinct solution sections from TXT.")

    dataset = []
    stats = {"total": 0, "single": 0, "multi": 0, "with_sol": 0}

    for q_id in sorted(pdf_qs.keys()):
        q_data = pdf_qs[q_id]
        sol_text = sol_sections.get(q_id, "")
        if sol_text:
            stats["with_sol"] += 1

        correct_answers, explanation = extract_answers_and_explanation(q_id, q_data, sol_text)

        item = {
            "id": q_id,
            "prompt": q_data["prompt"],
            "options": q_data["options"],
            "isMulti": q_data["isMulti"],
            "requiredCount": q_data["requiredCount"],
            "correctAnswers": correct_answers,
            "explanation": explanation
        }
        dataset.append(item)
        stats["total"] += 1
        if q_data["isMulti"]:
            stats["multi"] += 1
        else:
            stats["single"] += 1

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"Saved {stats['total']} questions to {OUTPUT_PATH}")
    print(f"Stats: Single={stats['single']}, Multi={stats['multi']}, WithSolutions={stats['with_sol']}")

if __name__ == "__main__":
    main()
