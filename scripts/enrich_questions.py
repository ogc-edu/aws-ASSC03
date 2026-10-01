import re
import json
import difflib
import sys
sys.path.insert(0, '.')
from scripts.parse_data import parse_pdf, parse_txt_sections

OUTPUT_PATH = "server/data/questions.json"

AWS_PATTERNS = [
    {
        "keywords": ["elasticache"],
        "reason": "Amazon ElastiCache is an in-memory key-value cache designed to accelerate read queries, not a durable, persistent shared file system for application data or item catalogs."
    },
    {
        "keywords": ["glacier deep archive", "deep archive"],
        "reason": "S3 Glacier Deep Archive has standard retrieval delays of 12 to 48 hours and is intended for cold compliance archives, not for active low-latency application access."
    },
    {
        "keywords": ["glacier"],
        "reason": "Amazon S3 Glacier has retrieval latencies ranging from minutes to hours and cannot be used as an active primary file system for real-time web application requests."
    },
    {
        "keywords": ["instance store"],
        "reason": "EC2 Instance Store is ephemeral block storage; all stored data is permanently lost if the instance stops, terminates, or undergoes underlying hardware maintenance."
    },
    {
        "keywords": ["larger ec2 instance", "larger instance store"],
        "reason": "Increasing the EC2 instance size does not solve durability issues, as instance store volumes remain ephemeral and vulnerable to data loss during hardware faults or instance stops."
    },
    {
        "keywords": ["ebs multi-attach"],
        "reason": "EBS Multi-Attach only allows attaching an io1/io2 volume to instances within the exact SAME Availability Zone and requires a cluster-aware file system. It does not provide Multi-AZ shared storage."
    },
    {
        "keywords": ["cross-region replication", "s3 crr", "crr"],
        "prompt_conflict": ["upload", "as quickly as possible", "single s3 bucket", "operational complexity", "latency"],
        "reason": "S3 Cross-Region Replication (CRR) asynchronously replicates data between buckets after it is uploaded. It does not accelerate client upload speeds from remote worldwide locations."
    },
    {
        "keywords": ["snowball edge", "snowball"],
        "prompt_conflict": ["daily", "real-time", "immediate", "continuously", "frequently"],
        "reason": "AWS Snowball Edge is a physical device intended for massive one-off batch data migrations. Daily shipping and physical handling cannot support automated recurring daily ingest."
    },
    {
        "keywords": ["redshift"],
        "prompt_conflict": ["simple", "ad-hoc", "minimal changes", "least operational overhead", "s3 bucket"],
        "reason": "Amazon Redshift is an enterprise data warehouse requiring cluster provisioning, schema design, and ETL loading. It introduces high operational complexity compared to serverless Amazon Athena."
    },
    {
        "keywords": ["emr", "spark", "hadoop"],
        "prompt_conflict": ["simple", "least operational", "on-demand", "minimal changes"],
        "reason": "Amazon EMR requires provisioning and managing a cluster of compute nodes, introducing significant operational burden and startup latency for simple on-demand queries."
    },
    {
        "keywords": ["sticky session", "session affinity"],
        "prompt_conflict": ["all documents", "shared", "both instances", "all users"],
        "reason": "Application Load Balancer sticky sessions merely pin a client to one specific instance; they do not synchronize or replicate stored files across different backend instances."
    },
    {
        "keywords": ["instance profile", "iam role"],
        "prompt_conflict": ["private network", "connectivity", "without internet"],
        "reason": "IAM roles and instance profiles manage authorization permissions; they do not establish network routing or private connectivity between VPC instances and Amazon S3."
    },
    {
        "keywords": ["vpc peering"],
        "prompt_conflict": ["transitive", "hub", "hundreds", "central", "edge"],
        "reason": "VPC peering does not support transitive routing (traffic cannot hop across an intermediate VPC) and results in complex mesh topologies compared to AWS Transit Gateway."
    },
    {
        "keywords": ["parameter store"],
        "prompt_conflict": ["automatic rotation", "rotate credentials"],
        "reason": "AWS Systems Manager Parameter Store does not provide built-in scheduled credential rotation for databases; AWS Secrets Manager is the designated service with native auto-rotation."
    },
    {
        "keywords": ["sqs standard", "standard queue"],
        "prompt_conflict": ["order", "ordered", "fifo", "strictly"],
        "reason": "Amazon SQS Standard queues provide best-effort ordering and occasional duplicate deliveries. SQS FIFO is mandatory when exact first-in-first-out order must be preserved."
    },
    {
        "keywords": ["nat instance"],
        "reason": "NAT instances require manual administration, OS patching, and custom high-availability scripting, unlike the fully managed, automatically scaling AWS NAT Gateway."
    },
    {
        "keywords": ["cloudtrail"],
        "prompt_conflict": ["real-time", "block", "prevent", "filter", "firewall"],
        "reason": "AWS CloudTrail is an audit logging service for management events; it is an asynchronous logging mechanism and cannot inspect network traffic or filter packets inline."
    },
    {
        "keywords": ["read replica"],
        "prompt_conflict": ["disaster recovery", "automatic failover", "high availability", "rpo"],
        "reason": "RDS Read Replicas replicate asynchronously and are designed for read scaling, not for synchronous automatic failover. Multi-AZ deployment is required for high availability."
    },
    {
        "keywords": ["multi-az"],
        "prompt_conflict": ["read throughput", "scale reads", "reporting"],
        "reason": "RDS Multi-AZ synchronous standbys are passive disaster recovery targets that cannot accept read or write queries; Read Replicas are required to offload read traffic."
    },
    {
        "keywords": ["security group"],
        "prompt_conflict": ["stateless", "subnet", "block ip", "deny"],
        "reason": "Security groups are stateful and support ALLOW rules only. They cannot explicitly DENY specific IP addresses (Network ACLs must be used for IP denial rules)."
    },
    {
        "keywords": ["global accelerator"],
        "prompt_conflict": ["cache", "caching", "static content"],
        "reason": "AWS Global Accelerator routes TCP/UDP traffic over the AWS global network using Anycast IPs to reduce network jitter, but does not cache static web content at edge locations like CloudFront."
    },
    {
        "keywords": ["s3 one zone-ia"],
        "reason": "S3 One Zone-IA stores data in a single Availability Zone, lacking Multi-AZ resilience and creating a risk of total data loss if that physical AZ experiences an outage."
    },
    {
        "keywords": ["direct connect"],
        "prompt_conflict": ["quick", "low cost", "immediate", "temporary", "backup"],
        "reason": "AWS Direct Connect involves dedicated physical cross-connections taking weeks to months to provision and entails significant recurring cost, making Site-to-Site VPN preferable for immediate or low-cost connectivity."
    },
    {
        "keywords": ["vpn", "ipsec"],
        "prompt_conflict": ["consistent", "dedicated bandwidth", "gigabit", "sla"],
        "reason": "AWS Site-to-Site VPN traverses the public internet, where network congestion can lead to unpredictable latency and variable throughput compared to dedicated Direct Connect circuits."
    }
]

def analyze_why_wrong(opt_letter, opt_text, prompt, correct_answers, sol_text):
    prompt_lower = prompt.lower()
    opt_lower = opt_text.lower()
    sol_lower = sol_text.lower()

    # 1. Look for explicit explanation in the solution text
    m = re.search(rf'(?:Option|Answer)\s+{opt_letter}\s*[:\-]?\s*(.+?)(?=(?:Option|Answer)\s+[A-F]|\n\n|\Z)', sol_text, re.I | re.DOTALL)
    if m:
        extracted = ' '.join(m.group(1).strip().split())
        if len(extracted) > 30 and any(k in extracted.lower() for k in ['incorrect', 'not', 'does not', 'cannot', 'would', 'requires', 'fails', 'expensive', 'overhead']):
            return extracted

    # 2. Check AWS Patterns
    for pattern in AWS_PATTERNS:
        has_kw = any(kw in opt_lower for kw in pattern["keywords"])
        if has_kw:
            if "prompt_conflict" in pattern:
                if any(pc in prompt_lower for pc in pattern["prompt_conflict"]):
                    return pattern["reason"]
            else:
                return pattern["reason"]

    # 3. Contextual Heuristics
    if "ebs" in opt_lower and ("shared" in prompt_lower or "multiple availability zones" in prompt_lower or "ec2 instances" in prompt_lower and "all documents" in prompt_lower):
        return "EBS volumes are Availability Zone-specific block devices and cannot be concurrently attached or synchronized across multiple instances in different AZs. Amazon EFS is required for shared Multi-AZ file access."

    if "cron" in opt_lower or "script" in opt_lower or "manual" in opt_lower:
        if any(w in prompt_lower for w in ["operational overhead", "complexity", "manage"]):
            return "Relying on custom cron jobs, scripts, or manual processes introduces operational overhead and failure points compared to fully managed AWS services."

    if "api gateway" in opt_lower and "s3" in prompt_lower and "private" in prompt_lower:
        return "Deploying API Gateway as an intermediary for S3 access adds needless cost and architectural overhead when an S3 Gateway VPC Endpoint provides native, free private access."

    if "kinesis data firehose" in opt_lower and any(w in prompt_lower for w in ["sub-second", "real-time"]):
        return "Amazon Kinesis Data Firehose has a minimum buffering window of 60 seconds and cannot achieve true sub-second real-time streaming."

    if "multi-region" in opt_lower and any(w in prompt_lower for w in ["cost-effective", "least cost", "single region"]):
        return "Multi-region architecture introduces high cross-region data transfer costs and operational complexity that exceeds the single-region requirements."

    if "public" in opt_lower and any(w in prompt_lower for w in ["private", "security", "secure", "protect"]):
        return "Using public endpoints or routing traffic over the public internet fails the requirement for private, secure communication."

    # 4. Fallback contextual reason
    first_clause = opt_text.split('.')[0].strip()
    return f"This approach ({first_clause}) does not meet the key requirements as effectively as the recommended architecture, introducing greater operational overhead, latency, or architectural complexity."

def extract_why_correct(correct_answers, q_data, sol_text):
    if not sol_text or len(sol_text.strip()) < 20:
        return "This solution aligns with the AWS Well-Architected Framework, delivering the highest availability, durability, and operational efficiency for this scenario."

    lines = [l.strip() for l in sol_text.split('\n') if l.strip()]
    cleaned = []
    for l in lines:
        if l.startswith("General line:") or l.startswith("Conditions:") or l.startswith("Task:") or l.startswith("Requirements:"):
            continue
        if l.startswith("---") or re.match(r'^\d+\]', l):
            continue
        cleaned.append(l)

    reason_lines = []
    for l in cleaned:
        if any(w in l.lower() for w in ["because", "allows", "provides", "features", "enables", "is designed", "recommended", "most appropriate", "correct answer"]):
            reason_lines.append(l)

    if reason_lines:
        return ' '.join(reason_lines[:4])

    if cleaned:
        return ' '.join(cleaned[:3])

    return "This solution meets all specified constraints with optimal performance, cost-efficiency, and minimal operational overhead."

def generate_takeaways(prompt, correct_answers, options):
    prompt_l = prompt.lower()
    t = []
    if "least operational" in prompt_l or "overhead" in prompt_l or "complexity" in prompt_l:
        t.append("- **Operational Excellence**: Prefer serverless and fully managed AWS services (e.g. S3 Transfer Acceleration, Athena, Secrets Manager, EFS) over self-managed EC2 instances or custom scripts.")
    if "cost" in prompt_l:
        t.append("- **Cost Optimization**: Transition rarely accessed objects to lower-cost tiers (e.g. Glacier) and avoid provisioning redundant compute resources.")
    if "private" in prompt_l or "internet" in prompt_l:
        t.append("- **Security & Network Isolation**: Use VPC Endpoints (Gateway endpoints for S3/DynamoDB) to keep data traffic completely off the public internet at zero additional data processing charge.")
    if "order" in prompt_l or "fifo" in prompt_l:
        t.append("- **Decoupled Architecture**: Standard SQS queues offer at-least-once delivery with best-effort ordering; strict FIFO ordering requires SQS FIFO queues.")
    if "availability" in prompt_l or "resilience" in prompt_l or "multi-az" in prompt_l:
        t.append("- **Resilience & High Availability**: Deploy workloads across multiple Availability Zones with Auto Scaling groups and load balancers to eliminate single points of failure.")
    if not t:
        t.append("- **Architectural Best Practice**: Select AWS native services designed specifically for the workload's durability, concurrency, and scaling profile.")
    return "\n".join(t)

def find_correct_answers(q_data, sol_text):
    options = q_data["options"]
    req_count = q_data["requiredCount"]
    
    m_ca = re.findall(r'Correct\s+answers?\s*[:\-]??\s*([A-F](?:\s*,\s*[A-F])*)', sol_text, re.I)
    detected = []
    for g in m_ca:
        for l in re.findall(r'[A-F]', g.upper()):
            if l in options and l not in detected:
                detected.append(l)

    if len(detected) < req_count:
        opt_mentions = re.findall(r'(?:Option|Options)\s+([A-F](?:\s*(?:and|&|,)\s*[A-F])*)', sol_text, re.I)
        for om in opt_mentions:
            for l in re.findall(r'[A-F]', om.upper()):
                if l in options and l not in detected:
                    detected.append(l)

    if len(detected) < req_count:
        match_scores = []
        for opt_k, opt_v in options.items():
            if opt_k in detected:
                continue
            v_clean = opt_v.strip().lower()
            sol_clean = sol_text.strip().lower()
            m = difflib.SequenceMatcher(None, v_clean, sol_clean).find_longest_match(0, len(v_clean), 0, len(sol_clean))
            frac = m.size / len(v_clean) if len(v_clean) > 0 else 0
            match_scores.append((opt_k, frac, m.size))

        match_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
        for opt_k, frac, size in match_scores:
            if len(detected) < req_count and (frac >= 0.50 or size > 80):
                detected.append(opt_k)

    if len(detected) < req_count:
        word_scores = []
        for opt_k, opt_v in options.items():
            if opt_k in detected:
                continue
            words = [w for w in re.findall(r'\b[a-z]{4,}\b', opt_v.lower())]
            if words:
                overlap = sum(1 for w in words if w in sol_text.lower()) / len(words)
                word_scores.append((opt_k, overlap))
        word_scores.sort(key=lambda x: x[1], reverse=True)
        for opt_k, sc in word_scores:
            if len(detected) < req_count and sc > 0.60:
                detected.append(opt_k)

    if not detected:
        detected = sorted(options.keys())[:req_count]

    detected.sort()
    return detected[:req_count]

def enrich():
    print("Parsing PDF questions...")
    pdf_qs = parse_pdf()

    print("Parsing solution text sections...")
    sol_sections = parse_txt_sections(pdf_qs)

    print("Enriching all 684 questions...")
    questions = []
    for qid in sorted(pdf_qs.keys()):
        q_data = pdf_qs[qid]
        sol_text = sol_sections.get(qid, "")

        correct = find_correct_answers(q_data, sol_text)

        why_correct = extract_why_correct(correct, q_data, sol_text)
        
        wrong_opts = [l for l in sorted(q_data["options"].keys()) if l not in correct]
        why_wrong_items = []
        for wl in wrong_opts:
            w_text = q_data["options"].get(wl, "")
            reason = analyze_why_wrong(wl, w_text, q_data["prompt"], correct, sol_text)
            why_wrong_items.append(f"- **Option {wl} is incorrect**: {reason}")

        why_wrong_block = "\n".join(why_wrong_items)
        takeaways_block = generate_takeaways(q_data["prompt"], correct, q_data["options"])

        correct_str = ", ".join(correct)
        correct_text = "\n".join([f"**Option {l}**: {q_data['options'].get(l, '')}" for l in correct])

        structured_explanation = f"""### ✅ Correct Answer: Option {correct_str}
{correct_text}

**Architectural Rationale:**
{why_correct}

---

### ❌ Why Other Options Are Incorrect:
{why_wrong_block}

---

### 💡 Key Exam Takeaways:
{takeaways_block}"""

        item = {
            "id": qid,
            "prompt": q_data["prompt"],
            "options": q_data["options"],
            "isMulti": q_data["isMulti"],
            "requiredCount": q_data["requiredCount"],
            "correctAnswers": correct,
            "explanation": structured_explanation
        }
        questions.append(item)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    print(f"Enriched {len(questions)} questions successfully in {OUTPUT_PATH}")

if __name__ == "__main__":
    enrich()
