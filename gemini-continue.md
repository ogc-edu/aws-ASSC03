# Gemini Handoff & Progress Report: SAA-C03 Question Sets Generation

**Date:** October 21, 2026  
**Status:** Set 1, Set 2, and Set 3 Complete (195 questions total)  
**Target:** 10 Complete Mock Exam Sets (650 questions total)  
**Next Up for Claude:** Set 4 (and onwards through Set 10)

---

## 1. Executive Summary & Current Status

The user requested 10 full-length practice question sets for the AWS Certified Solutions Architect - Associate (SAA-C03) exam.

1. **Claude completed:**
   - Base UI routes (`/claude` and `/claude/:id`) in [client/src/pages/ClaudeSetsIndex.jsx](file:///Users/ooiguancheng/Documents/SAA-PY/AWS-Certified-Solutions-Architect-Associate-SAA-C03-Exam-Dump-With-Solution/client/src/pages/ClaudeSetsIndex.jsx) and [ClaudeSetPage.jsx](file:///Users/ooiguancheng/Documents/SAA-PY/AWS-Certified-Solutions-Architect-Associate-SAA-C03-Exam-Dump-With-Solution/client/src/pages/ClaudeSetPage.jsx).
   - Set progress service with `localStorage` isolation in [client/src/services/claudeSetService.js](file:///Users/ooiguancheng/Documents/SAA-PY/AWS-Certified-Solutions-Architect-Associate-SAA-C03-Exam-Dump-With-Solution/client/src/services/claudeSetService.js).
   - **Set 1** (`client/public/claude/set-1.json`, 65 questions).
   - **Set 2** (`client/public/claude/set-2.json`, 65 questions).
   - Core assembly script [scripts/build_claude_sets.py](file:///Users/ooiguancheng/Documents/SAA-PY/AWS-Certified-Solutions-Architect-Associate-SAA-C03-Exam-Dump-With-Solution/scripts/build_claude_sets.py).

2. **Gemini completed:**
   - **Investigated & verified current SAA-C03 Exam Guide & blueprint** (re-confirmed for 2025–2026 updates).
   - **Authored, validated, balanced, and published Set 3** (`client/public/claude/set-3.json` and `client/dist/claude/set-3.json`, 65 questions).
   - **Modularized domain question definitions** in `scripts/sets_data/`:
     - [set_3_d1.py](file:///Users/ooiguancheng/Documents/SAA-PY/AWS-Certified-Solutions-Architect-Associate-SAA-C03-Exam-Dump-With-Solution/scripts/sets_data/set_3_d1.py) (20 questions, Domain 1: Secure)
     - [set_3_d2.py](file:///Users/ooiguancheng/Documents/SAA-PY/AWS-Certified-Solutions-Architect-Associate-SAA-C03-Exam-Dump-With-Solution/scripts/sets_data/set_3_d2.py) (17 questions, Domain 2: Resilient)
     - [set_3_d3.py](file:///Users/ooiguancheng/Documents/SAA-PY/AWS-Certified-Solutions-Architect-Associate-SAA-C03-Exam-Dump-With-Solution/scripts/sets_data/set_3_d3.py) (15 questions, Domain 3: High-Performing)
     - [set_3_d4.py](file:///Users/ooiguancheng/Documents/SAA-PY/AWS-Certified-Solutions-Architect-Associate-SAA-C03-Exam-Dump-With-Solution/scripts/sets_data/set_3_d4.py) (13 questions, Domain 4: Cost-Optimized)
   - Built [scripts/build_set_3.py](file:///Users/ooiguancheng/Documents/SAA-PY/AWS-Certified-Solutions-Architect-Associate-SAA-C03-Exam-Dump-With-Solution/scripts/build_set_3.py) to validate question schemas, rebalance single-choice options across `{'A': 14, 'B': 14, 'C': 14, 'D': 13}`, shuffle deterministically (seed `3093`), and update both `client/public/claude/sets.json` and `client/dist/claude/sets.json`.
   - Updated the index in `sets.json` so Set 3 renders immediately at `/claude` and `/claude/3`.

---

## 2. Official SAA-C03 Blueprint & Mathematical Constraints

Every 65-question set must adhere strictly to these exact specifications:

| Parameter | Specification |
|---|---|
| **Total Questions** | Exactly 65 questions (50 scored, 15 unscored pilot questions) |
| **Duration** | 130 minutes |
| **Passing Score** | 720 / 1000 scaled |
| **Domain 1: Design Secure Architectures** | **30% (20 questions)**: Tasks 1.1 (7 Qs), 1.2 (7 Qs), 1.3 (6 Qs) |
| **Domain 2: Design Resilient Architectures** | **26% (17 questions)**: Tasks 2.1 (8-9 Qs), 2.2 (8-9 Qs) |
| **Domain 3: Design High-Performing Architectures** | **24% (15 questions)**: Tasks 3.1 (3 Qs), 3.2 (3 Qs), 3.3 (3 Qs), 3.4 (3 Qs), 3.5 (3 Qs) |
| **Domain 4: Design Cost-Optimized Architectures** | **20% (13 questions)**: Tasks 4.1 (4 Qs), 4.2 (3 Qs), 4.3 (3 Qs), 4.4 (3 Qs) |
| **Question Types** | **55 Single-Choice** (1 of 4: A-D) + **10 Multiple-Response** (8 of 2-from-5, 2 of 3-from-6) |
| **Option Balance** | Single-choice answers must be distributed evenly across A, B, C, D (approx 13-14 each). |

---

## 3. JSON Question Schema & Explanation Standard

Each question object inside `questions` must follow this schema:

```json
{
  "id": 1,
  "domain": 1,
  "task": "1.1",
  "topics": [
    "AWS Organizations",
    "Resource Control Policies",
    "Service Control Policies"
  ],
  "prompt": "Scenario description ending in a clear business/technical question... (Select TWO.)",
  "options": {
    "A": "Option text...",
    "B": "Option text...",
    "C": "Option text...",
    "D": "Option text...",
    "E": "Option text..."
  },
  "isMulti": true,
  "requiredCount": 2,
  "correctAnswers": ["A", "C"],
  "explanation": "### ✅ Why Options A & C are Correct\n\n* **Reason 1:** ...\n* **Reason 2:** ...\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** ...\n* **Option D is incorrect:** ...\n* **Option E is incorrect:** ...\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Concept:** ...\n2. **Best Practice:** ..."
}
```

### Explanation Formatting Requirements:
1. `### ✅ Why Option ... is Correct` with technical justification.
2. `### ❌ Why Other Options Are Incorrect` with explicit `* **Option X is incorrect:**` bullets for each distractor.
3. `### 💡 SAA-C03 Exam Concept & AWS Best Practice` with 2-3 numbered exam tips and distinctions.

---

## 4. Current Sets Summary

| Set ID | Title | Questions | Domains (D1 / D2 / D3 / D4) | Multi-Response | Seed | Status |
|---|---|---|---|---|---|---|
| **Set 1** | Claude Mock Exam — Set 1 | 65 | 20 / 17 / 15 / 13 | 10 (8 x 2-of-5, 2 x 3-of-6) | 1031 | ✅ Complete |
| **Set 2** | Claude Mock Exam — Set 2 | 65 | 20 / 17 / 15 / 13 | 10 (8 x 2-of-5, 2 x 3-of-6) | 2062 | ✅ Complete |
| **Set 3** | Claude & Gemini Mock Exam — Set 3 | 65 | 20 / 17 / 15 / 13 | 10 (8 x 2-of-5, 2 x 3-of-6) | 3093 | ✅ Complete |
| **Set 4** | Mock Exam — Set 4 | 65 | 20 / 17 / 15 / 13 | 10 | 4124 | ⏳ Planned |
| **Set 5** | Mock Exam — Set 5 | 65 | 20 / 17 / 15 / 13 | 10 | 5155 | ⏳ Planned |
| **Set 6** | Mock Exam — Set 6 | 65 | 20 / 17 / 15 / 13 | 10 | 6186 | ⏳ Planned |
| **Set 7** | Mock Exam — Set 7 | 65 | 20 / 17 / 15 / 13 | 10 | 7217 | ⏳ Planned |
| **Set 8** | Mock Exam — Set 8 | 65 | 20 / 17 / 15 / 13 | 10 | 8248 | ⏳ Planned |
| **Set 9** | Mock Exam — Set 9 | 65 | 20 / 17 / 15 / 13 | 10 | 9279 | ⏳ Planned |
| **Set 10** | Mock Exam — Set 10 | 65 | 20 / 17 / 15 / 13 | 10 | 10310 | ⏳ Planned |

---

## 5. Topics Covered in Set 3 (Avoid Redundant Duplicate Questions in Set 4)

In Set 3, we specifically covered:
- **Domain 1**: IAM External ID (confused deputy), Permissions boundaries for delegated role creation, ABAC (`aws:PrincipalTag` vs `aws:ResourceTag`), IAM Roles Anywhere with X.509 PKI, Organizations Resource Control Policies (RCPs) vs SCPs, IAM Identity Center with AD Connector, explicit Deny on `aws:SourceIp`, AWS WAF rate-based rules + SQLi managed rules on ALB, Centralized Inspection VPC with AWS Network Firewall + Transit Gateway, Cognito User Pools + Identity Pools folder policies (`sub`), Amazon Inspector continuous scanning for ECR and Lambda, S3 Gateway Endpoint Policies, GuardDuty automated isolation via EventBridge + Lambda, AppSync + Cognito GraphQL field auth, KMS Multi-Region replica keys, S3 Object Lock Compliance vs Governance, Secrets Manager multi-user rotation for RDS, KMS Key Policy separation of duties, S3 Bucket Keys, KMS envelope encryption (`GenerateDataKey`).
- **Domain 2**: SQS FIFO `MessageGroupId` and deduplication, EventBridge Pipes with filtering/transformation, API Gateway WebSocket API with connection IDs, SNS fanout to SQS with subscription filters, SQS DLQ native Redrive (`StartMessageMoveTask`), Step Functions Distributed Map for massive S3 batches, ECS Service Discovery with AWS Cloud Map + Route 53 private hosted zone, Kinesis Data Streams On-Demand mode vs Provisioned, S3 Event Notifications to SQS with Target Tracking on `BacklogPerInstance`, DR strategies RPO/RTO spectrum (Warm Standby), Route 53 Application Recovery Controller (ARC) routing controls, RDS Multi-AZ DB Cluster (2 readable standbys, sub-35s failover), S3 Cross-Region Replication with Replication Time Control (RTC) & delete marker settings, Aurora Global Database sub-second replication, Static stability across AZs, AWS Fault Injection Service (FIS), EC2 Auto Scaling ELB health checks + grace periods.
- **Domain 3**: S3 Express One Zone directory buckets for single-digit ms AI/ML, FSx for NetApp ONTAP dual NFS/SMB + Multi-AZ failover, EBS io2 Block Express vs gp3 for sub-ms 256k IOPS, Lambda SnapStart for Java cold starts, EC2 Cluster Placement Group + Elastic Fabric Adapter (EFA) for MPI HPC, AWS AppRunner for zero-infra container web apps, ElastiCache Serverless for Redis/Valkey, Amazon MemoryDB for Redis Multi-AZ durable log, DynamoDB hot partitions and Write Sharding, AWS Global Accelerator Anycast IPs for UDP/TCP, Amazon VPC Lattice application-layer cross-VPC networking, CloudFront Functions vs Lambda@Edge, Amazon Data Firehose Dynamic Partitioning + Glue Data Catalog Parquet conversion, Amazon MSK for Apache Kafka migration, AWS Glue Job Bookmarks for incremental ETL.
- **Domain 4**: S3 Lifecycle across Glacier Flexible and Deep Archive + noncurrent version expiration, EFS Elastic Throughput for spiky file storage, EBS Snapshot Archive with DLM policies, S3 Intelligent-Tiering automatic archive tiers with no retrieval fees, EC2 Auto Scaling Mixed Instances Policy with On-Demand base + Spot capacity-optimized, Compute Savings Plans vs EC2 Instance Savings Plans flexibility, AWS Lambda Power Tuning, Aurora Serverless v2 scaling to 0.5 ACU, DynamoDB Standard-IA table class for high-storage/low-access tables, Amazon Redshift Serverless daily RPU-hour usage limits, eliminating public IPv4 charges with IPv6 dual-stack + Egress-Only Internet Gateway, reducing cross-AZ data transfer fees via intra-AZ co-location, AWS Direct Connect hosted connections for discounted Data Transfer Out.

---

## 6. Recommended Blueprint & Topics for Set 4 (for Claude to generate)

Claude should focus on these fresh, high-yield SAA-C03 topics for **Set 4** (seed `4124`):

### Domain 1 (20 Qs):
- AWS KMS asymmetric keys (signing/verification vs encryption).
- Amazon Bedrock guardrails and VPC interface endpoint access.
- Amazon Macie automated sensitive data discovery (PII / PCI) with custom data identifiers.
- AWS Security Hub automated security standard checks (CIS AWS Foundations / AWS Foundational Security Best Practices).
- AWS WAF Fraud Control (Account Takeover Prevention / Account Creation Fraud).
- IAM session policies and role chaining restrictions.
- VPC Flow Logs filtering (REJECT vs ACCEPT) to S3 / CloudWatch Logs / Athena analysis.
- Secrets Manager cross-account replica secrets.
- AWS Signer code signing for AWS Lambda functions.
- IAM policy evaluation logic: Explicit Deny > SCP > RCP > Permissions Boundary > Identity/Resource Policy.
- Amazon Cognito hosted UI and OAuth 2.0 PKCE flow.
- Transit Gateway Network Manager and route table isolation per tenant/environment.
- S3 Cross-account access with bucket owner condition (`s3:ExpectedBucketOwner`) and Object Ownership (BucketOwnerEnforced).

### Domain 2 (17 Qs):
- Amazon Aurora connection management with Amazon RDS Proxy (connection pooling and read replica pin avoid).
- AWS Step Functions Standard vs Express Workflows (at-least-once vs at-most-once, rate, execution history).
- Amazon SQS visibility timeout vs message retention vs dead-letter queue max receive count.
- Amazon EventBridge Scheduler with flexible time windows and retry configurations.
- Route 53 Geolocation routing vs Geoproximity routing (using routing controls and biases).
- AWS Backup logically air-gapped vaults.
- Multi-region disaster recovery: Aurora Global Database write forwarding.
- DynamoDB global tables conflict resolution (last writer wins) and replication metrics.
- Amazon ECS rolling update vs blue/green deployment with AWS CodeDeploy.
- EC2 Auto Scaling predictive scaling vs step scaling vs target tracking.

### Domain 3 (15 Qs):
- Amazon EFS Provisioned Throughput vs Elastic Throughput for continuous read-heavy web farm.
- Amazon FSx for OpenZFS for high-performance Linux shared storage.
- Amazon Redshift Serverless data sharing across multiple AWS accounts without copying data.
- DynamoDB Accelerator (DAX) microsecond caching for read-heavy tables.
- Amazon Athena partition projection for high-volume logs in S3.
- AWS Lambda provisioned concurrency vs reserved concurrency.
- VPC Peering MTU (9001 jumbo frames) vs Transit Gateway MTU (8500).
- Amazon CloudFront origin request policies vs cache policies.
- Amazon OpenSearch Serverless collections (vector search vs search vs time-series).

### Domain 4 (13 Qs):
- S3 Storage Lens metrics and recommendations for identifying uncompressed or orphan data.
- AWS Cost Anomaly Detection with SNS alerts.
- AWS Graviton4 instance cost-performance migration.
- VPC Endpoints vs NAT Gateway cost comparison (data processing charges vs interface endpoint hourly fee).
- Amazon Aurora I/O-Optimized storage configuration for read/write heavy workloads.
- EBS gp3 performance tuning (baseline 3,000 IOPS / 125 MB/s free with volume).
- Consolidated billing and blended vs unblended rates in AWS Organizations.
- AWS Compute Optimizer recommendations for rightsizing underutilized EC2 and EBS volumes.

---

## 7. How Claude Can Pick Up & Generate Set 4

Claude can use the established modular architecture:

1. **Create domain files in `scripts/sets_data/`:**
   - `scripts/sets_data/set_4_d1.py` (20 questions)
   - `scripts/sets_data/set_4_d2.py` (17 questions)
   - `scripts/sets_data/set_4_d3.py` (15 questions)
   - `scripts/sets_data/set_4_d4.py` (13 questions)

2. **Create build script `scripts/build_set_4.py`:**
   - Import questions from `set_4_d1..d4`.
   - Run `validate()` on every question.
   - Use the remapping helper to balance single-choice options across `{'A': 14, 'B': 14, 'C': 14, 'D': 13}`.
   - Shuffle with seed `4124`.
   - Write to `client/public/claude/set-4.json` and `client/dist/claude/set-4.json`.
   - Add Set 4 entry to `client/public/claude/sets.json` and `client/dist/claude/sets.json`.

3. **Verify:**
   ```bash
   python3 scripts/build_set_4.py
   python3 -c "
   import json
   d = json.load(open('client/public/claude/set-4.json'))
   print('Set 4 questions:', len(d['questions']))
   "
   ```

4. **Update `gemini-continue.md`** with the updated status, topics covered, and the handoff instructions for Set 5.
