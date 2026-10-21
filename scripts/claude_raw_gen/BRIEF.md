# Brief: write original AWS SAA-C03 practice questions

Official exam guide text (dated Oct 2026, still SAA-C03): ../guide.txt — read the task statements
for your domain AND the in-scope / out-of-scope service appendix before writing.

## Exam format to mirror
- Scenario-based ("A company ... Which solution meets these requirements?" / "...with the LEAST operational overhead?" /
  "MOST cost-effectively?" / "Which combination of steps ... (Select TWO.)").
- Multiple choice: exactly 4 options A-D, exactly 1 correct.
- Multiple response: 5 options A-E with 2 correct (prompt ends "(Select TWO.)"), or 6 options A-F with 3 correct ("(Select THREE.)").
- Distractors must be plausible to someone with partial knowledge — real services, real features, subtly wrong for the stated constraint.
- Prompts are 2-6 sentences, realistic, with the deciding constraint(s) clearly stated.
- Spread single-choice correct letters roughly evenly across A/B/C/D. Do not make the correct answer consistently the longest.

## Currency (this is the point of the exercise — the old bank is outdated)
Reflect AWS as of 2025-2026: e.g. gp3 over gp2, Graviton, S3 default SSE-S3 encryption & Block Public Access/ACLs-disabled defaults,
S3 Express One Zone, IAM Identity Center (not "AWS SSO"), Control Tower/Organizations SCPs & RCPs, CloudFront OAC (not OAI),
Aurora Serverless v2 / Aurora I/O-Optimized / Aurora Global Database, RDS Proxy, DynamoDB on-demand, ElastiCache Serverless,
Savings Plans, Compute Optimizer, EventBridge Pipes/Scheduler, Step Functions, Lambda SnapStart/function URLs, ECS/Fargate, EKS,
Verified Access, VPC Lattice, Transit Gateway, PrivateLink, Gateway Load Balancer, Network Firewall, GuardDuty, Security Hub,
Secrets Manager rotation, KMS multi-Region keys, AWS Backup (vault lock, cross-account), Elastic Disaster Recovery, DataSync,
Transfer Family, Kinesis Data Streams/Firehose, MSK, Glue, Athena, Lake Formation, Redshift Serverless, OpenSearch, etc.
Use only services that are in scope per the guide's appendix. Avoid deprecated/closed products as the CORRECT answer
(e.g. Snowmobile, CodeCommit for new customers, Cloud9, OAI, gp2 as the optimal choice, EC2-Classic, AWS SSO naming).
Use correct current service names.

## Accuracy
Every correct answer must be unambiguously correct per AWS documentation, and every distractor unambiguously worse/wrong
for the stated requirement. Re-check each one before finishing. If unsure about a fact, rewrite the question around something you are sure of.
No two questions in your output may test the same concept with the same answer — Set 1 and Set 2 must cover different scenarios.

## Output
Write ONE JSON file (path given in your task) — a JSON object: {"set1": [...], "set2": [...]}. Each question:
{
  "domain": 1,                     // 1-4
  "task": "1.2",                   // task statement from the guide
  "topics": ["Amazon S3", "AWS KMS"],
  "prompt": "...",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
  "isMulti": false,
  "requiredCount": 1,
  "correctAnswers": ["C"],
  "explanation": "markdown, see format"
}
Explanation markdown format (match exactly these headings; this is what the app renders):

### ✅ Why Option C is Correct            (or "Why Options B & D are Correct")

* **Key point:** ...  (2-4 bullets, concrete technical reasons)

---

### ❌ Why Other Options Are Incorrect

* **Option A is incorrect:** ...   (one bullet per wrong option)

---

### 💡 SAA-C03 Exam Concept & AWS Best Practice

1. **...:** keyword-to-service pattern / exam tip (2-3 items)

Validate the file parses with `python3 -c "import json;json.load(open('PATH'))"` and check counts/requiredCount/correctAnswers consistency before you finish.
Reply with only a short summary: counts, answer-letter distribution, and the list of topics per set.
