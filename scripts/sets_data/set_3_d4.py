"""Domain 4: Design Cost-Optimized Architectures (13 Questions for Set 3)
Tasks:
- 4.1: Design cost-optimized storage solutions (4 questions, 1 multi)
- 4.2: Design cost-optimized compute solutions (3 questions, 1 multi)
- 4.3: Design cost-optimized database solutions (3 questions)
- 4.4: Design cost-optimized network architectures (3 questions)
"""

QUESTIONS = [
    # Task 4.1 - Question 1 (Multi 2 of 5)
    {
        "domain": 4,
        "task": "4.1",
        "topics": ["Amazon S3", "S3 Lifecycle", "S3 Glacier tiers", "Cost optimization"],
        "prompt": "An enterprise generates 10 TB of compliance audit documents monthly and uploads them to Amazon S3 Standard. Regulations require the enterprise to retain these documents for 10 years. The access pattern is as follows: documents are accessed frequently during the first 30 days, accessed rarely (once or twice a year) between days 31 and 365 where retrieval within 3 to 5 hours is acceptable, and virtually never accessed after year 1 (retrieval within 12 hours is acceptable). Deleting noncurrent object versions after 90 days is required to avoid orphaned version storage costs. Which combination of S3 Lifecycle actions should a solutions architect configure? (Select TWO.)",
        "options": {
            "A": "Transition current versions from S3 Standard to S3 Glacier Flexible Retrieval after 30 days, and transition to S3 Glacier Deep Archive after 365 days.",
            "B": "Configure noncurrent version expiration to permanently delete noncurrent versions 90 days after becoming noncurrent.",
            "C": "Transition objects to S3 One Zone-IA after 1 day and immediately delete after 30 days.",
            "D": "Transition current versions directly to S3 Glacier Deep Archive on day 1 with instant retrieval.",
            "E": "Enable S3 Versioning and keep all historical versions in S3 Standard permanently."
        },
        "isMulti": True,
        "requiredCount": 2,
        "correctAnswers": ["A", "B"],
        "explanation": "### ✅ Why Options A & B are Correct\n\n* **Lifecycle transitions across Glacier tiers (A):** S3 Glacier Flexible Retrieval provides low-cost archival with standard retrieval times of 3-5 hours (or expedited 1-5 minutes), matching the requirements for days 31-365. S3 Glacier Deep Archive is the lowest-cost storage in the cloud (~$0.00099/GB/mo), with 12-hour standard retrieval, matching requirements after year 1.\n* **Noncurrent version expiration (B):** Setting noncurrent version expiration to 90 days ensures older, superseded versions do not accumulate storage costs indefinitely in S3 Standard.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option C is incorrect:** S3 One Zone-IA lacks multi-AZ durability and deleting documents after 30 days violates the 10-year regulatory retention mandate.\n* **Option D is incorrect:** S3 Glacier Deep Archive does not support instant retrieval (retrieval takes 12-48 hours) and transitioning on day 1 prevents frequent access during the first 30 days.\n* **Option E is incorrect:** Keeping all versions in S3 Standard for 10 years results in astronomical storage costs.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Glacier Tiers comparison:**\n   - **Glacier Instant Retrieval:** Millisecond retrieval, lowest cost for rarely accessed data needing immediate access.\n   - **Glacier Flexible Retrieval:** 3-5 hours (bulk 5-12 hours, expedited 1-5 min).\n   - **Glacier Deep Archive:** Lowest cost (~$1/TB/month), 12-48 hours retrieval.\n2. **Noncurrent version management:** S3 Versioning continues to store previous versions until explicitly expired via lifecycle rules."
    },
    # Task 4.1 - Question 2 (Single)
    {
        "domain": 4,
        "task": "4.1",
        "topics": ["Amazon EFS", "Elastic Throughput", "Throughput modes"],
        "prompt": "A company uses Amazon Elastic File System (Amazon EFS) to share configuration templates across a fleet of containerized applications running on Amazon ECS. The file system contains only 20 GB of files, but the application experiences brief, unpredictable read spikes where throughput needs to surge to 150 MB/s for 2 minutes before dropping back to near zero. Previously, using the default Bursting Throughput mode, the small 20 GB file system quickly exhausted its burst credit balance, resulting in application timeouts. The company wants to support these high-throughput bursts without provisioning and paying for unneeded baseline throughput 24/7. Which throughput mode should a solutions architect select?",
        "options": {
            "A": "Elastic Throughput",
            "B": "Provisioned Throughput set to 150 MB/s",
            "C": "Bursting Throughput with a 10 TB dummy file added to increase burst credits",
            "D": "Cold Throughput mode"
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **EFS Elastic Throughput:** Designed specifically for spiky and unpredictable workloads. It automatically delivers the throughput performance applications need without requiring any throughput provisioning or credit management.\n* **Pay only for data read/written:** You pay strictly for the data read and written (per GB), making it significantly cheaper for spiky workloads than paying 24/7 for 150 MB/s Provisioned Throughput.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Setting Provisioned Throughput to 150 MB/s costs $6.00/MB/s-month (over $900/month) 24 hours a day, even when the system is idle for 98% of the day.\n* **Option C is incorrect:** Creating a 10 TB dummy file incurs $3,000/month in EFS storage charges just to inflate burst credits, which is absurdly wasteful.\n* **Option D is incorrect:** There is no 'Cold Throughput' mode in Amazon EFS.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **EFS Throughput Modes:**\n   - **Elastic Throughput:** Best for spiky, unpredictable workloads with low duty cycles. Pay per GB transferred.\n   - **Provisioned Throughput:** Best for applications with high, steady, predictable throughput requirements.\n   - **Bursting Throughput:** Baseline throughput is proportional to storage size (50 KB/s per GB)."
    },
    # Task 4.1 - Question 3 (Single)
    {
        "domain": 4,
        "task": "4.1",
        "topics": ["Amazon EBS", "EBS Snapshot Archive", "Lifecycle management"],
        "prompt": "An enterprise maintains thousands of Amazon EBS snapshots across its AWS accounts for long-term compliance retention. Snapshots must be kept for 3 years. The security and audit teams rarely access these snapshots (access is required less than once every 18 months), and when access is required, a recovery time of 24 to 72 hours to restore a volume is acceptable. The enterprise wants to reduce its EBS snapshot storage costs by up to 75% with automated policy-based management. Which solution should a solutions architect implement?",
        "options": {
            "A": "Configure Amazon Data Lifecycle Manager (Amazon DLM) policies to automatically move EBS snapshots to EBS Snapshot Archive after 90 days.",
            "B": "Write an AWS Lambda function to download EBS snapshots as RAW files to an EC2 instance store volume.",
            "C": "Convert all EBS snapshots into Amazon S3 Standard objects using custom scripts.",
            "D": "Delete snapshots after 30 days and take daily RDS backups instead."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **EBS Snapshot Archive:** A low-cost storage tier for EBS snapshots that are rarely accessed and retained for 90 days or longer. It lowers snapshot storage costs by up to 75% compared to standard EBS snapshot storage.\n* **Automated management via DLM:** Amazon Data Lifecycle Manager (Amazon DLM) supports automated rules to transition standard snapshots to the archive tier based on age or schedules with zero script maintenance.\n* **Restoration:** Archived snapshots can be restored back to standard snapshot tier in 24 to 72 hours, perfectly matching the company's requirement.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** EC2 instance store is ephemeral; storing compliance snapshots on instance store risks permanent data loss when instances stop.\n* **Option C is incorrect:** EBS snapshots already reside in Amazon S3 internally managed by AWS; manually copying raw blocks requires complex custom code and higher storage costs.\n* **Option D is incorrect:** RDS backups only protect relational databases, not EC2 operating system disks and custom block storage volumes.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Long-term, rarely accessed EBS snapshots (retention > 90 days):** **EBS Snapshot Archive**.\n2. **Automation:** Use **Amazon Data Lifecycle Manager (DLM)** to automate snapshot creation, retention, and archiving."
    },
    # Task 4.1 - Question 4 (Single)
    {
        "domain": 4,
        "task": "4.1",
        "topics": ["Amazon S3", "S3 Intelligent-Tiering", "Automated cost optimization"],
        "prompt": "A digital asset management company hosts 5 PB of video, audio, and raw media files in Amazon S3. The access patterns are completely unpredictable: some files are downloaded hundreds of times within days, others remain untouched for months, and some are suddenly accessed again after a year. The company wants to minimize storage costs automatically without paying retrieval fees, without monitoring access patterns manually, and without risking performance penalties when objects are retrieved. Which storage class should a solutions architect recommend?",
        "options": {
            "A": "Amazon S3 Intelligent-Tiering",
            "B": "Amazon S3 Standard-Infrequent Access (S3 Standard-IA)",
            "C": "Amazon S3 Glacier Flexible Retrieval",
            "D": "Amazon S3 One Zone-IA"
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **S3 Intelligent-Tiering:** The only cloud storage class that delivers automatic cost savings by moving objects between access tiers based on changing access patterns, with **zero retrieval fees** and no operational monitoring.\n* **Access tiers:** Moves objects between Frequent Access, Infrequent Access (30 days untouched), Archive Instant Access (90 days untouched), and optional asynchronous archive tiers (Archive Access 90-730+ days, Deep Archive Access 180-730+ days).\n* **No performance impact:** Millisecond access latency across Frequent, Infrequent, and Archive Instant Access tiers.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** S3 Standard-IA incurs per-GB retrieval fees; if unpredictable traffic spikes cause frequent downloads, retrieval fees will outweigh storage savings.\n* **Option C is incorrect:** S3 Glacier Flexible Retrieval takes minutes to hours to restore data and charges retrieval fees, violating real-time download requirements.\n* **Option D is incorrect:** S3 One Zone-IA stores data in a single AZ (risk of data loss) and charges retrieval fees.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Unpredictable / unknown access patterns with NO retrieval fees:** **Amazon S3 Intelligent-Tiering**.\n2. **Small objects in Intelligent-Tiering:** Objects smaller than 128 KB are not monitored or tiered and remain charged at S3 Standard rates."
    },
    # Task 4.2 - Question 5 (Multi 2 of 5)
    {
        "domain": 4,
        "task": "4.2",
        "topics": ["Amazon EC2 Auto Scaling", "Spot Instances", "Mixed Instances Policies"],
        "prompt": "A software development company runs a stateless containerized web testing workload on Amazon EC2 instances managed by an Auto Scaling group. The workload requires a steady baseline capacity of 10 instances 24/7 to support background developer suites, but scales up to 50 instances during active working hours. The company wants to minimize compute costs as aggressively as possible while protecting baseline workloads from sudden Spot interruption terminations. Which combination of actions should a solutions architect recommend? (Select TWO.)",
        "options": {
            "A": "Configure an Auto Scaling group with a Mixed Instances Policy setting 'On-Demand Base Capacity' to 10 instances.",
            "B": "Configure the Mixed Instances Policy to satisfy the remaining capacity above the base using Spot Instances with the 'capacity-optimized' allocation strategy across multiple instance types.",
            "C": "Purchase 50 On-Demand instances with dedicated host tenancy.",
            "D": "Configure all 50 instances as Spot Instances with no On-Demand base.",
            "E": "Use EC2 Scheduled Instances for all instances across all hours."
        },
        "isMulti": True,
        "requiredCount": 2,
        "correctAnswers": ["A", "B"],
        "explanation": "### ✅ Why Options A & B are Correct\n\n* **Mixed Instances Policy with On-Demand Base (A):** Setting `On-Demand Base Capacity` to 10 guarantees that the baseline capacity is always fulfilled by reliable On-Demand instances that are never interrupted by AWS.\n* **Capacity-optimized Spot allocation (B):** For the remaining 40 burst instances, Spot instances offer up to 90% savings. The `capacity-optimized` allocation strategy launches Spot instances into the deepest available capacity pools across multiple instance types, minimizing the likelihood of Spot interruptions.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option C is incorrect:** Dedicated Hosts are the most expensive EC2 purchasing option and are only used for strict per-socket software licensing compliance.\n* **Option D is incorrect:** Running 100% Spot with zero On-Demand base leaves the baseline background testing suite vulnerable to fleet-wide termination if Spot capacity is reclaimed.\n* **Option E is incorrect:** Scheduled Instances are deprecated and do not support dynamic horizontal auto-scaling.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Mixed Instances Policy in ASG:** Combine On-Demand (for steady baseline) with Spot Instances (for bursty scale-out).\n2. **Spot Allocation Strategy:**\n   - **Capacity-optimized:** Best for minimizing interruption risk.\n   - **Lowest-price:** Lowest cost, but higher interruption risk."
    },
    # Task 4.2 - Question 6 (Single)
    {
        "domain": 4,
        "task": "4.2",
        "topics": ["Savings Plans", "AWS Cost Explorer", "Commitment discounts"],
        "prompt": "A enterprise runs a diverse compute environment consisting of Amazon EC2 instances (mix of Linux and Windows across m6i, c6i, and r6i instance families), AWS Fargate serverless containers, and AWS Lambda functions across three AWS Regions (us-east-1, us-west-2, and eu-west-1). The enterprise plans to modernize several EC2 workloads to AWS Graviton (c7g, m7g) and migrate more services to AWS Fargate over the next 12 to 24 months. The enterprise wants to commit to a 3-year term to achieve maximum cost savings. Which purchasing model provides the HIGHEST discount while maintaining complete flexibility across instance types, operating systems, compute services, and AWS Regions?",
        "options": {
            "A": "Compute Savings Plans",
            "B": "EC2 Instance Savings Plans",
            "C": "Standard Reserved Instances",
            "D": "Convertible Reserved Instances"
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Compute Savings Plans:** Provide up to 66% discount on compute spend. They automatically apply to EC2 instance usage regardless of instance family, size, operating system, tenancy, or AWS Region.\n* **Cross-service flexibility:** Crucially, Compute Savings Plans also apply to AWS Fargate and AWS Lambda spend, allowing seamless modernization from EC2 to Fargate or from x86 to Graviton without stranding discounts.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** EC2 Instance Savings Plans provide up to 72% savings, but are locked to an individual instance family in a specific AWS Region (e.g. m6i in us-east-1), and do NOT apply to Fargate or Lambda.\n* **Option C is incorrect:** Standard RIs apply only to EC2, are tied to specific regions and families, and do not cover Fargate or Lambda.\n* **Option D is incorrect:** Convertible RIs cover only EC2 and require manual exchange processes, whereas Compute Savings Plans apply automatically without management.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Compute Savings Plans vs EC2 Instance Savings Plans:**\n   - **Compute Savings Plans:** Maximum flexibility (EC2, Fargate, Lambda across any family/Region/OS).\n   - **EC2 Instance Savings Plans:** Higher discount, but locked to 1 family in 1 Region (EC2 only)."
    },
    # Task 4.2 - Question 7 (Single)
    {
        "domain": 4,
        "task": "4.2",
        "topics": ["AWS Lambda", "AWS Lambda Power Tuning", "Serverless cost optimization"],
        "prompt": "A company operates thousands of event-driven AWS Lambda functions. The engineering director noticed that some memory-bound functions run for 45 seconds at 512 MB memory, costing more than expected, while other CPU-bound functions are over-provisioned at 3,008 MB memory and finish in 100 milliseconds. The engineering team wants an automated data-driven tool to test functions with different memory allocations, measure execution duration and cost, and identify the exact optimal configuration for cost or performance. Which solution should the company implement?",
        "options": {
            "A": "Deploy the open-source AWS Lambda Power Tuning state machine to benchmark functions across multiple memory configurations and visualize the cost vs execution time curve.",
            "B": "Configure Amazon CloudWatch Alarms to trigger AWS Systems Manager to double Lambda memory every hour.",
            "C": "Convert all Lambda functions to run on Amazon EC2 m5.metal bare metal instances.",
            "D": "Increase the timeout of all Lambda functions to 15 minutes."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **AWS Lambda Power Tuning:** An open-source, AWS-recommended tool powered by AWS Step Functions that runs multiple concurrent versions of a Lambda function with different memory settings (from 128 MB to 10,240 MB) against sample inputs.\n* **Visual optimization curve:** Generates a visual graph showing the trade-off between execution speed and cost, allowing teams to pick the configuration optimized for lowest cost, best performance, or balanced.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Arbitrarily doubling memory increases costs exponentially without benchmarking.\n* **Option C is incorrect:** Bare metal EC2 instances are extremely expensive and destroy the serverless operational model.\n* **Option D is incorrect:** Function timeout does not alter execution speed or memory allocation; it only caps maximum runtime before killing the invocation.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Lambda CPU allocation:** Lambda allocates CPU power linearly in proportion to configured memory (at 1,769 MB, a function has 1 full vCPU).\n2. **Lambda cost formula:** Cost is calculated based on number of requests and duration (GB-seconds)."
    },
    # Task 4.3 - Question 8 (Single)
    {
        "domain": 4,
        "task": "4.3",
        "topics": ["Amazon Aurora Serverless v2", "Development environments", "Database cost"],
        "prompt": "A software development firm maintains 80 development and testing databases for feature branch testing on Amazon RDS for PostgreSQL. Developers work on these environments during normal business hours (9 AM to 6 PM, Monday through Friday). Outside of business hours and on weekends, the databases receive zero queries. Despite having no active queries, the provisioned RDS db.m5.large instances incur substantial ongoing costs. The firm wants a relational database solution that automatically scales down compute to minimal capacity (0.5 ACU) during periods of inactivity and scales up instantly in fractions of a second when developers run tests. Which solution meets these requirements with the LOWEST operational effort?",
        "options": {
            "A": "Migrate the development databases to Amazon Aurora Serverless v2, configuring the minimum capacity to 0.5 Aurora Capacity Units (ACUs) and maximum capacity to 8 ACUs.",
            "B": "Write an Amazon EventBridge Scheduler rule and Lambda function to stop and start all 80 RDS instances every morning and evening.",
            "C": "Keep RDS provisioned instances and downgrade all development databases to single-AZ t4g.nano instances.",
            "D": "Migrate all relational databases to Amazon S3 CSV files queried by Athena."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Amazon Aurora Serverless v2:** Automatically adjusts database compute capacity in fine-grained increments (Aurora Capacity Units or ACUs) in fractions of a second based on application demand.\n* **Why a 0.5 ACU minimum:** With a minimum of 0.5 ACU, each instance stays warm at very low cost during nights and weekends, so the first query of the morning is served immediately without connection drops.\n* **Why not 0 ACUs:** Aurora Serverless v2 can also scale to 0 ACUs and auto-pause, which stops compute charges while idle (storage is still billed). Resuming typically takes about 15 seconds, and 30 seconds or more after a pause longer than 24 hours, which breaks the requirement to scale up instantly. For dev databases that can tolerate that delay, 0 ACUs is the cheaper setting.\n* **Zero operational effort:** No need to manage stop/start scripts, handle failed restarts, or reconfigure connection strings.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** While stopping RDS instances saves money, RDS instances automatically start after 7 days if stopped, a stopped instance takes minutes to start, connection pooling breaks, and developers cannot work late without manual intervention.\n* **Option C is incorrect:** A t4g.nano has only 0.5 GB RAM, which cannot support PostgreSQL performance tests or developer schema migrations.\n* **Option D is incorrect:** S3 CSV files and Athena cannot replace transactional relational databases with ACID requirements.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Aurora Serverless v2:** Scales instantly in ACUs (1 ACU = approx 2 GB RAM + CPU).\n2. **Min/Max ACUs:** A minimum of 0 ACUs (auto-pause, on supported engine versions) costs nothing for compute while idle but takes about 15 seconds to resume. A minimum of 0.5 ACU stays warm for instant response. The maximum ACU caps spend at peak load."
    },
    # Task 4.3 - Question 9 (Single)
    {
        "domain": 4,
        "task": "4.3",
        "topics": ["Amazon DynamoDB", "Table classes", "Standard-IA table class"],
        "prompt": "An industrial IoT company stores sensor telemetry history in an Amazon DynamoDB table. The table stores over 50 TB of data. New data is written continuously, but historical data is queried rarely (primarily for annual regulatory compliance audits and warranty dispute checks). Storage costs currently account for over 85% of the total monthly DynamoDB bill. Which configuration change will reduce DynamoDB storage costs by up to 60% with NO application code changes or performance degradation on reads?",
        "options": {
            "A": "Change the DynamoDB table class from DynamoDB Standard to DynamoDB Standard-Infrequent Access (DynamoDB Standard-IA).",
            "B": "Enable DynamoDB Streams and replicate all items to an unencrypted MySQL database on EC2.",
            "C": "Change the table billing mode from On-Demand to Provisioned with 1 WCU.",
            "D": "Enable DynamoDB Global Tables across three AWS Regions."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **DynamoDB Standard-IA:** Designed for tables that store large amounts of data that are accessed infrequently (where storage exceeds 50% of monthly DynamoDB costs).\n* **60% lower storage costs:** Offers 60% lower storage costs than DynamoDB Standard, with slightly higher pricing for reads and writes.\n* **Zero application changes:** Has identical DynamoDB APIs, identical performance, identical single-digit millisecond latency, and identical durability.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Managing custom MySQL EC2 instances adds maintenance, security risks, and hardware costs.\n* **Option C is incorrect:** Changing provisioned WCU affects write throughput capacity; it does not reduce the per-GB storage fee for the 50 TB of data.\n* **Option D is incorrect:** DynamoDB Global Tables replicates storage to multiple Regions, tripling storage and write costs rather than reducing them.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **DynamoDB storage cost optimization:** When storage is the primary cost driver and data is accessed infrequently, switch table class to **DynamoDB Standard-IA**.\n2. **DynamoDB Table Classes:**\n   - **Standard:** Default for active workloads.\n   - **Standard-IA:** Best when storage costs dominate read/write costs."
    },
    # Task 4.3 - Question 10 (Single)
    {
        "domain": 4,
        "task": "4.3",
        "topics": ["Amazon Redshift Serverless", "Usage limits", "Cost control"],
        "prompt": "A marketing agency uses Amazon Redshift Serverless to analyze ad performance data. Business analysts run ad-hoc queries irregularly throughout the day. Management is concerned that a poorly optimized query running in parallel could spawn high Redshift Processing Units (RPUs) and trigger massive billing spikes. The agency wants to enforce a strict maximum daily spend cap on Amazon Redshift Serverless, automatically halting query execution or alerting administrators when the threshold is approached. Which feature should a solutions architect configure?",
        "options": {
            "A": "Configure Redshift Serverless Usage Limits, specifying maximum RPU-hours per day and setting the action to log to CloudWatch or turn off query processing.",
            "B": "Create a billing alarm in AWS Cost Explorer that deletes the Redshift namespace when budget exceeds $50.",
            "C": "Migrate the data warehouse to Amazon RDS Single-AZ with manual query killing scripts.",
            "D": "Switch from Redshift Serverless to a provisioned dc2.8xlarge cluster running 24/7."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Redshift Serverless Usage Limits:** Amazon Redshift Serverless allows administrators to define explicit **usage limits** in terms of RPU-hours consumed on a daily, weekly, or monthly basis.\n* **Automated cost controls:** When limits are reached, Redshift can automatically take action: emit an alert to Amazon CloudWatch, write to system logs, or automatically toggle off query processing to prevent further charges.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Cost Explorer updates billing data several times per day (not real-time), and deleting a database namespace is destructive and loses data.\n* **Option C is incorrect:** RDS is an OLTP database, not an analytical data warehouse, and manual query killing is error-prone.\n* **Option D is incorrect:** Running a 24/7 dc2.8xlarge cluster incurs high fixed costs even during long idle periods, increasing total spend.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Cost control in Redshift Serverless:** Configure **Usage Limits** (RPU-hours per day/week/month) with automated actions (Alert or Deactivate).\n2. **RPU (Redshift Processing Unit):** Redshift Serverless scales in RPUs (base capacity + max capacity settings)."
    },
    # Task 4.4 - Question 11 (Single)
    {
        "domain": 4,
        "task": "4.4",
        "topics": ["Amazon VPC", "Public IPv4 charges", "IPv6", "Egress-only internet gateway"],
        "prompt": "A company operates 500 Amazon EC2 instances in private subnets across multiple VPCs. The instances only need outbound internet access to download software package patches from public repositories; they do not require any inbound internet connectivity. Previously, instances each had an auto-assigned public IPv4 address and routed through an Internet Gateway. AWS charges for public IPv4 addresses have increased monthly cloud costs significantly. The company wants to eliminate public IPv4 address charges entirely while allowing instances to initiate outbound connections to the internet. Which architecture achieves this with the LOWEST ongoing cost?",
        "options": {
            "A": "Transition the VPC and EC2 instances to dual-stack IPv6, assign IPv6 addresses to the instances, and deploy an Egress-Only Internet Gateway in the VPC for outbound internet communication.",
            "B": "Deploy two NAT Gateways in every public subnet and assign an Elastic IP address to each.",
            "C": "Create an AWS Direct Connect dedicated connection to route all outbound traffic through an on-premises proxy.",
            "D": "Purchase EC2 Instance Savings Plans to cover the cost of public IPv4 addresses."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Eliminate IPv4 charges with IPv6:** AWS assigns public IPv6 addresses free of charge (there are no hourly fees for IPv6 addresses unlike public IPv4 addresses).\n* **Egress-Only Internet Gateway (EIGW):** An Egress-Only Internet Gateway provides stateful outbound internet communication for IPv6-enabled EC2 instances while preventing anyone on the public internet from initiating inbound connections to the instances.\n* **Zero hourly NAT fees:** Egress-Only Internet Gateways are completely free to deploy (no hourly charge, no data processing charge, unlike NAT Gateways).\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** NAT Gateways incur hourly fees ($0.045/hour each) plus data processing fees ($0.045/GB), which is significantly more expensive than an Egress-Only Internet Gateway.\n* **Option C is incorrect:** Direct Connect requires expensive monthly port fees ($0.30-$2.25/hour) and dedicated telecommunication provider circuit costs.\n* **Option D is incorrect:** Savings Plans apply to compute spend (EC2, Fargate, Lambda); they do not cover public IPv4 address charges.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Outbound-only internet for IPv6:** **Egress-Only Internet Gateway** (free, no hourly/processing fees).\n2. **Outbound-only internet for IPv4:** **NAT Gateway** (incurs hourly + per-GB data processing fees)."
    },
    # Task 4.4 - Question 12 (Single)
    {
        "domain": 4,
        "task": "4.4",
        "topics": ["Amazon VPC", "Data transfer cost", "Cross-AZ traffic"],
        "prompt": "A microservices application running on Amazon EC2 processes 100 TB of inter-service RPC data monthly. The application is deployed across three Availability Zones. Architecture review shows that Service A in AZ-a frequently calls Service B in AZ-b and AZ-c through an internal Application Load Balancer with cross-zone load balancing enabled. The monthly AWS bill shows high 'DataTransfer-Regional-Bytes' (inter-AZ data transfer) charges. Which architectural change will reduce inter-AZ data transfer costs while preserving high availability?",
        "options": {
            "A": "Deploy instances of Service A and Service B co-located in each of the three Availability Zones, and configure DNS routing or service discovery to route traffic to local instances within the same Availability Zone whenever healthy.",
            "B": "Move all EC2 instances into a single Availability Zone and disable backups.",
            "C": "Route all inter-service traffic over an AWS Site-to-Site VPN across the public internet.",
            "D": "Attach an Elastic IP address to every EC2 instance and communicate using public IPs."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Inter-AZ Data Transfer Charges:** Traffic that traverses across different Availability Zones within the same Region incurs standard inter-AZ data transfer charges ($0.01/GB in each direction, total $0.02/GB).\n* **AZ-Affinity routing:** Deploying balanced instances of both services in all three AZs and routing requests to the local AZ instance (intra-AZ) incurs **$0.00 data transfer charges** (data transfer within the same AZ using private IPs is completely free), while maintaining multi-AZ failover resilience.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Collapsing to a single AZ creates an immediate single point of failure and violates high availability.\n* **Option C is incorrect:** Routing over VPN increases latency, adds VPN hourly and data transfer out costs, and degrades throughput.\n* **Option D is incorrect:** Public IP communication between EC2 instances in the same Region incurs data transfer charges and introduces security risks.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **AWS Data Transfer Pricing:**\n   - Same AZ, private IP: **Free ($0.00)**.\n   - Cross-AZ, same Region: **Charged ($0.01/GB in + $0.01/GB out)**.\n   - Inter-Region: **Charged standard regional egress rates**.\n   - Inbound from Internet: **Free**."
    },
    # Task 4.4 - Question 13 (Single)
    {
        "domain": 4,
        "task": "4.4",
        "topics": ["AWS Direct Connect", "AWS Site-to-Site VPN", "Hybrid network cost"],
        "prompt": "A corporation connects its on-premises corporate headquarters to an AWS VPC. Currently, they use an AWS Site-to-Site VPN over the public internet, transferring 80 TB of database backup data to AWS each month. The corporation is experiencing internet packet drops and high internet data transfer out costs on return queries. They want a dedicated, consistent network connection with lower AWS Data Transfer Out (DTO) pricing compared to standard internet egress, without paying for expensive multi-gigabit hardware if current throughput needs do not exceed 500 Mbps. Which hybrid networking solution is MOST cost-effective?",
        "options": {
            "A": "Order a 500 Mbps AWS Direct Connect hosted connection from an AWS Direct Connect Delivery Partner.",
            "B": "Deploy 10 parallel AWS Site-to-Site VPN connections using ECMP over the public internet.",
            "C": "Establish an AWS Storage Gateway Tape Gateway over public internet with maximum retry settings.",
            "D": "Use Amazon S3 Transfer Acceleration over the public internet for all VPC traffic."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **AWS Direct Connect hosted connection:** An AWS Direct Connect Delivery Partner creates the connection for the company at a chosen speed (50 Mbps up to 25 Gbps, depending on the partner), so the company can buy exactly 500 Mbps. Dedicated connections start at 1 Gbps and are a whole port ordered from AWS.\n* **Lower Data Transfer Out pricing:** Data transferred out of AWS over Direct Connect is billed at Direct Connect data transfer rates, which are lower than internet data transfer out rates.\n* **Consistent performance:** Dedicated private circuit bypasses public internet congestion and packet drops.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Running 10 parallel VPNs across the public internet multiplies the per-connection hourly VPN charge and still incurs full standard internet data transfer out rates without resolving internet packet jitter.\n* **Option C is incorrect:** Tape Gateway is for tape backup archival, not general VPC-to-on-premises bidirectional hybrid application traffic.\n* **Option D is incorrect:** S3 Transfer Acceleration only speeds up S3 bucket uploads over the internet; it does not connect on-premises corporate infrastructure to VPC private workloads.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Direct Connect benefits:** Consistent network throughput, private security, and lower Data Transfer Out (DTO) pricing.\n2. **Sub-1 Gbps Direct Connect:** Choose a **hosted connection** from an AWS Direct Connect Partner.\n3. **Dedicated vs hosted:** Dedicated = 1, 10, 100 or 400 Gbps ports ordered from AWS. Hosted = 50 Mbps to 25 Gbps, created by a partner."
    }
]
