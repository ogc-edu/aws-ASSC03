"""Domain 2: Design Resilient Architectures (17 Questions for Set 3)
Tasks:
- 2.1: Design scalable and loosely coupled architectures (9 questions, 1 multi)
- 2.2: Design highly available and/or fault-tolerant architectures (8 questions, 1 multi-2, 1 multi-3)
"""

QUESTIONS = [
    # Task 2.1 - Question 1 (Single)
    {
        "domain": 2,
        "task": "2.1",
        "topics": ["Amazon SQS FIFO", "Message deduplication", "Ordering"],
        "prompt": "A fintech startup processes retail stock trade orders. The backend processing service must execute orders in the exact chronological sequence they are placed by each individual trader. Additionally, the system must guarantee that network retries or transient connection failures do not produce duplicate trade executions within any 5-minute interval. Which architecture meets these requirements?",
        "options": {
            "A": "Send trade orders to an Amazon SQS FIFO queue, setting the MessageGroupId to the trader's account ID and using content-based deduplication or a unique transaction MessageDeduplicationId.",
            "B": "Send trade orders to an Amazon SQS Standard queue and configure the visibility timeout to 300 seconds.",
            "C": "Publish orders to an Amazon SNS Standard topic with Amazon Kinesis Data Firehose as the subscription endpoint.",
            "D": "Store incoming orders in an Amazon DynamoDB table with strong consistency and run an hourly cron job on EC2 to process rows in order."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **FIFO ordering with MessageGroupId:** Amazon SQS FIFO queues preserve the strict order of messages within a message group. Setting `MessageGroupId` to the trader's account ID guarantees sequential processing per trader while allowing parallel processing across different traders.\n* **Exactly-once processing:** SQS FIFO provides exactly-once processing by deduplicating messages within a 5-minute deduplication window using `MessageDeduplicationId` or content-based SHA-256 hash deduplication.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** SQS Standard queues provide at-least-once delivery (duplicates can occur) and best-effort ordering (no strict chronological guarantee). A visibility timeout only hides messages while in flight.\n* **Option C is incorrect:** Standard SNS and Data Firehose do not guarantee strict per-trader chronological order or deduplication.\n* **Option D is incorrect:** Running batch cron jobs every hour introduces huge latency and does not provide real-time event-driven processing.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Strict ordering + No duplicates:** Use **Amazon SQS FIFO**.\n2. **MessageGroupId:** Determines the ordering partition. Messages with the same group ID are processed one by one in order.\n3. **MessageDeduplicationId:** SQS FIFO automatically rejects duplicate messages with the same deduplication ID within a 5-minute window."
    },
    # Task 2.1 - Question 2 (Single)
    {
        "domain": 2,
        "task": "2.1",
        "topics": ["Amazon EventBridge Pipes", "DynamoDB Streams", "Decoupling"],
        "prompt": "An application writes order updates to an Amazon DynamoDB table with DynamoDB Streams enabled. A downstream analytics team wants to ingest only orders with a status of 'COMPLETED' and an order value greater than $500 into an Amazon SQS queue. The team requires a serverless integration with built-in filtering and transformation without writing or managing AWS Lambda functions. Which AWS solution meets these requirements with the LOWEST operational overhead?",
        "options": {
            "A": "Create an Amazon EventBridge Pipe with the DynamoDB Stream as the source, configure a filter pattern for status and order value, and set the Amazon SQS queue as the target.",
            "B": "Write an AWS Lambda function triggered by DynamoDB Streams that filters records in code and calls 'sqs:SendMessage'.",
            "C": "Deploy an Amazon Kinesis Client Library (KCL) consumer application on an Amazon EC2 Auto Scaling group.",
            "D": "Use AWS Glue Streaming ETL to read the DynamoDB stream every 15 minutes and write to SQS."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Amazon EventBridge Pipes:** Provides point-to-point integrations between event producers (such as DynamoDB Streams, Kinesis, SQS, MSK) and consumers (SQS, SNS, Step Functions, EventBridge event bus, etc.).\n* **Built-in filtering and enrichment:** EventBridge Pipes includes native declarative JSON filtering and payload transformation without needing custom AWS Lambda code.\n* **Lowest operational overhead:** Serverless, managed polling, automatic scaling, and zero code maintenance.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** While AWS Lambda works, it requires authoring, testing, deploying, and maintaining custom code and monitoring execution errors, increasing operational overhead compared to EventBridge Pipes.\n* **Option C is incorrect:** Deploying self-managed EC2 instances with KCL introduces infrastructure management, OS patching, and unnecessary server costs.\n* **Option D is incorrect:** AWS Glue Streaming ETL is designed for continuous data lake ingestion and transformation into S3/Redshift; using it for simple DynamoDB-to-SQS filtering is expensive and over-engineered.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **EventBridge Pipes:** Point-to-point integration with optional filtering, enrichment (via Lambda/API Destinations), and transformation.\n2. **DynamoDB Streams filtering:** EventBridge Pipes and Lambda event source mappings both support event filtering, but Pipes requires zero code for simple target routing."
    },
    # Task 2.1 - Question 3 (Single)
    {
        "domain": 2,
        "task": "2.1",
        "topics": ["Amazon API Gateway", "WebSocket API", "Real-time notifications"],
        "prompt": "A logistics company wants to build a live parcel tracking dashboard for warehouse dispatchers. Dispatchers should receive real-time location and status push updates on their browser screens whenever a courier scans a package. The architecture must support persistent bidirectional connections for up to 50,000 concurrent browser sessions without requiring clients to poll REST endpoints continuously. Which architecture is MOST scalable and cost-effective?",
        "options": {
            "A": "Amazon API Gateway WebSocket API with AWS Lambda integration, storing active connection IDs in Amazon DynamoDB and using the '@connections' API to push updates.",
            "B": "Amazon API Gateway REST API with short polling configured on browser clients every 500 milliseconds.",
            "C": "An Application Load Balancer with long polling HTTP requests directed to an EC2 instance running in a single Availability Zone.",
            "D": "AWS App Runner service hosting an unmanaged PHP server that writes updates directly to browser local storage."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **API Gateway WebSocket APIs:** WebSocket APIs maintain persistent, bidirectional connections between browser clients and API Gateway.\n* **Connection ID management:** API Gateway assigns a unique `$connectionId` when a client connects. Lambda stores these in DynamoDB. When a courier scans a package, a backend process retrieves relevant connection IDs and invokes the API Gateway `@connections` endpoint to push data in real time to connected clients.\n* **Scalability:** Serverless, scales to hundreds of thousands of concurrent connections, and charges only for connection minutes and messages transferred.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Polling REST endpoints every 500 ms creates immense request volume, high API Gateway and Lambda costs, and unnecessary database load.\n* **Option C is incorrect:** Long polling on a single EC2 instance is a single point of failure and cannot scale to 50,000 persistent HTTP connections.\n* **Option D is incorrect:** Servers cannot write directly to a remote browser's local storage over the internet without an active protocol connection.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Bidirectional real-time web communication:** Choose **API Gateway WebSocket API**.\n2. **WebSocket connection lifecycle:** `$connect` (store connection ID), `$disconnect` (delete connection ID), `$default` (custom routes)."
    },
    # Task 2.1 - Question 4 (Multi 2 of 5)
    {
        "domain": 2,
        "task": "2.1",
        "topics": ["Amazon SNS", "Amazon SQS", "Fanout pattern", "Message filtering"],
        "prompt": "An online retail platform receives order placement events. When an order is placed: (1) the order inventory service must process all orders, (2) the express fulfillment service must process only orders flagged with 'Priority=High', and (3) the analytics pipeline must receive all orders for daily aggregations. The system must decouple the producer from consumers, ensure independent scaling of each consumer tier, and prevent unneeded messages from reaching the express fulfillment service. Which combination of actions should a solutions architect take? (Select TWO.)",
        "options": {
            "A": "Publish order placement events to a central Amazon SNS topic.",
            "B": "Create three separate Amazon SQS queues subscribed to the SNS topic, applying an SNS subscription filter policy on the express fulfillment queue for 'Priority=High'.",
            "C": "Have the frontend application call three separate AWS Lambda functions sequentially using synchronous invocations.",
            "D": "Create a single Amazon SQS FIFO queue with three message groups and have all services poll the same queue.",
            "E": "Write events to an Amazon S3 bucket and have Amazon Athena run queries every second."
        },
        "isMulti": True,
        "requiredCount": 2,
        "correctAnswers": ["A", "B"],
        "explanation": "### ✅ Why Options A & B are Correct\n\n* **SNS to SQS Fanout pattern (A & B):** Publishing a single message to an Amazon SNS topic that fans out to multiple Amazon SQS queues allows each consumer service to process messages at its own pace asynchronously and scale independently.\n* **SNS Subscription Filter Policies (B):** SNS subscription filter policies inspect message attributes (such as `Priority: High`). SNS delivers only matching messages to that specific SQS queue, eliminating waste and keeping unwanted messages away from the express fulfillment consumer.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option C is incorrect:** Synchronous Lambda calls couple the frontend tightly to downstream services, multiplying latency and risking transaction failure if any downstream service is unavailable.\n* **Option D is incorrect:** Multiple consumer services polling a single queue compete for messages (each message is consumed by only one service), breaking the requirement that inventory and analytics both process all orders.\n* **Option E is incorrect:** Athena is an interactive analytical query engine; polling it every second is not real-time, expensive, and impractical for transactional processing.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Fanout architecture:** Publish once to **Amazon SNS**, fan out to multiple **Amazon SQS** queues.\n2. **Message Filtering:** Apply **Subscription Filter Policies** on SNS subscriptions to avoid having downstream consumers discard irrelevant messages."
    },
    # Task 2.1 - Question 5 (Single)
    {
        "domain": 2,
        "task": "2.1",
        "topics": ["Amazon SQS", "Dead-Letter Queue", "Redrive Allow Policy"],
        "prompt": "A backend microservice processes invoices from an Amazon SQS queue. Due to a bug in a newly deployed application version, messages containing international currency codes failed validation repeatedly and were automatically sent to a Dead-Letter Queue (DLQ). The engineering team has deployed a code patch that fixes the bug. What is the MOST operationally efficient way to reprocess the failed messages from the DLQ?",
        "options": {
            "A": "Use the Amazon SQS DLQ redrive feature in the AWS Management Console or AWS CLI to move messages from the DLQ back to the source queue for reprocessing.",
            "B": "Write a custom Python script running on an EC2 instance to read each message from the DLQ, parse the body, and make 'sqs:SendMessage' calls to the source queue.",
            "C": "Delete the DLQ and recreate it with the same name, which automatically pushes messages into the source queue.",
            "D": "Increase the visibility timeout of the DLQ to 14 days and let consumers read directly from both queues simultaneously."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Native SQS DLQ Redrive:** Amazon SQS provides a built-in DLQ Redrive feature (both in the console and via the `StartMessageMoveTask` API). It allows administrators to move messages from a dead-letter queue back to the original source queue (or another specified queue) without writing, hosting, or running custom code.\n* **Zero operational overhead:** Handles batching, throttling, and verification automatically.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Writing and maintaining custom scripts requires extra operational overhead, compute resources, and error handling.\n* **Option C is incorrect:** Deleting a queue permanently destroys all messages inside it, resulting in catastrophic data loss.\n* **Option D is incorrect:** SQS consumers should poll designated workload queues; polling a DLQ directly creates race conditions and does not clean up the dead-letter state.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Reprocessing DLQ messages:** Always use the native **Amazon SQS DLQ Redrive** (`StartMessageMoveTask`).\n2. **Redrive Allow Policy:** Controls which source queues are permitted to route failed messages to a given DLQ."
    },
    # Task 2.1 - Question 6 (Single)
    {
        "domain": 2,
        "task": "2.1",
        "topics": ["AWS Step Functions", "Distributed Map", "Large-scale data processing"],
        "prompt": "A media research organization processes daily batch archives containing 500,000 JSON survey files stored in an Amazon S3 bucket. The processing requires parsing each file, applying normalization logic, and writing summary outputs. The entire 500,000-file dataset must be processed within 1 hour each morning. The solution must handle transient file errors gracefully, scale compute dynamically, and provide visual execution monitoring with the LEAST code maintenance. Which solution should a solutions architect recommend?",
        "options": {
            "A": "Use an AWS Step Functions state machine with a Distributed Map state configured to iterate over S3 objects concurrently, invoking child AWS Lambda executions with built-in retry and catch error handling.",
            "B": "Deploy an Amazon EMR cluster with Hadoop MapReduce and write custom Java map jobs that run every morning.",
            "C": "Create an Amazon EC2 Auto Scaling group with 100 t3.micro instances and have them poll S3 bucket listings in a while loop.",
            "D": "Use Amazon SQS with a single consumer Lambda function configured with a reserved concurrency of 1."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Step Functions Distributed Map:** Designed specifically for large-scale parallel data processing. It can iterate over millions of objects directly in an S3 bucket or JSON files, coordinating up to 10,000 concurrent child workflow or Lambda executions.\n* **Resilience and error handling:** Provides native visual state tracking, automated retries with exponential backoff, catch handlers for failed items, and execution summaries.\n* **Serverless & cost-effective:** No clusters to provision, manage, or keep running when idle.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Managing an EMR Hadoop cluster adds infrastructure overhead, cluster spin-up delays, and custom code complexity.\n* **Option C is incorrect:** Self-managed EC2 instances in an infinite loop polling S3 listings cause race conditions, S3 ListObjects API throttling, and high compute waste.\n* **Option D is incorrect:** A concurrency of 1 processes files sequentially one by one; 500,000 files cannot finish within 1 hour.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Parallel processing of massive datasets in S3:** **AWS Step Functions Distributed Map** state.\n2. **Concurrency:** Distributed Map supports thousands of concurrent child executions, ideal for S3 batch processing."
    },
    # Task 2.1 - Question 7 (Single)
    {
        "domain": 2,
        "task": "2.1",
        "topics": ["AWS Cloud Map", "Amazon ECS", "Service discovery"],
        "prompt": "A company has converted a monolithic application into 25 microservices running in Amazon Elastic Container Service (Amazon ECS) across private subnets. Microservices scale up and down dynamically and need to discover and communicate with each other using internal domain names (e.g., 'orders.production.local') without routing traffic through public networks or provisioning dedicated load balancers for every individual microservice. Which architecture provides reliable, dynamic service discovery with the LOWEST infrastructure cost?",
        "options": {
            "A": "Integrate Amazon ECS with AWS Cloud Map and configure Service Discovery with an Amazon Route 53 private hosted zone.",
            "B": "Deploy an Application Load Balancer in front of each of the 25 microservices.",
            "C": "Hardcode the private IP addresses of the ECS container instances in an Amazon S3 configuration file.",
            "D": "Use an Amazon API Gateway Public HTTP API and route all microservice traffic over the public internet."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **ECS Service Discovery with AWS Cloud Map:** Native ECS integration with AWS Cloud Map automatically registers and deregisters container task IP addresses and ports in an Amazon Route 53 private hosted zone as tasks scale in and out or become unhealthy.\n* **Internal DNS resolution:** Microservices simply call domain names like `orders.production.local` to resolve private IPs directly.\n* **Lowest cost:** Eliminates the significant monthly cost of running 25 separate Application Load Balancers.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Deploying 25 ALBs incurs unnecessary baseline hourly costs ($0.0225/hour x 25 = ~$405/month just for idle load balancers) plus LCU charges.\n* **Option C is incorrect:** Container IP addresses in ECS are dynamic; hardcoded IPs fail immediately whenever containers restart or scale.\n* **Option D is incorrect:** Routing private internal microservice traffic over the public internet compromises security and incurs avoidable data transfer out charges.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Microservice discovery in ECS/EKS without ALBs:** **AWS Cloud Map** with **Route 53 Private Hosted Zone**.\n2. **Health checking:** Cloud Map checks task health before returning IPs in DNS queries."
    },
    # Task 2.1 - Question 8 (Single)
    {
        "domain": 2,
        "task": "2.1",
        "topics": ["Amazon Kinesis Data Streams", "Capacity modes", "Partition keys"],
        "prompt": "An IoT telematics platform ingests real-time GPS coordinates from 100,000 delivery vehicles into Amazon Kinesis Data Streams. During normal operations, vehicles emit steady telemetry, but during sudden morning rush-hour shifts, ingestion volume spikes unpredictably by 500% within two minutes. Previously, provisioned shards became throttled ('ProvisionedThroughputExceededException'). The company wants an ingestion architecture that automatically scales up and down to accommodate sudden traffic bursts without manual shard management. Which solution should a solutions architect recommend?",
        "options": {
            "A": "Configure the Amazon Kinesis Data Stream in On-Demand capacity mode, using the vehicle's unique device ID as the partition key.",
            "B": "Keep the stream in Provisioned capacity mode and use an EC2 cron job running a bash script to call 'kinesis:UpdateShardCount' every 2 minutes.",
            "C": "Switch from Kinesis to an Amazon RDS MySQL database with Auto Scaling storage.",
            "D": "Write GPS coordinates directly to an Amazon S3 Standard bucket using single-part PUT operations."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Kinesis On-Demand Mode:** Automatically accommodates throughput increases up to double your previous peak within minutes without throttling or manual capacity planning. Charges are based strictly on per-GB data ingested and hourly stream pricing.\n* **High-cardinality partition key:** Using the unique `device ID` distributes records evenly across internal shards, avoiding hot shards and maximizing throughput.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Manual or scripted shard splitting (`UpdateShardCount`) can take several minutes to complete, has API rate limits, and requires continuous maintenance and monitoring.\n* **Option C is incorrect:** Relational databases (RDS) are not designed to ingest 100,000 rapid concurrent streaming IoT writes and will suffer severe connection and locking bottlenecks.\n* **Option D is incorrect:** Performing individual direct S3 PUTs for continuous high-frequency GPS pings generates massive S3 PUT request costs and creates billions of tiny files that ruin analytical query performance.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Kinesis Capacity Modes:**\n   - **On-Demand:** Spiky, unpredictable workloads with unknown peak traffic.\n   - **Provisioned:** Predictable, steady-state workloads where costs can be forecasted and optimized.\n2. **Partition Keys:** Always choose high-cardinality keys (e.g. Device ID, User ID) to distribute writes evenly across shards."
    },
    # Task 2.1 - Question 9 (Single)
    {
        "domain": 2,
        "task": "2.1",
        "topics": ["Amazon S3", "Amazon SQS", "EC2 Auto Scaling", "Decoupled architecture"],
        "prompt": "A tax preparation software platform allows users to upload scanned tax documents (PDFs up to 25 MB) for optical character recognition (OCR) parsing. OCR processing is compute-intensive and takes between 30 and 90 seconds per document. During peak tax season, upload volume spikes 100-fold. The company wants to decouple document upload from document processing so that users receive an immediate confirmation, while worker EC2 instances scale dynamically based on the volume of documents waiting to be processed. Which architecture meets these requirements?",
        "options": {
            "A": "Have users upload files directly to Amazon S3. Configure an S3 Event Notification to send an event to an Amazon SQS queue when an object is created. Configure an Amazon EC2 Auto Scaling group of OCR workers that scales based on a target tracking policy tracking the 'BacklogPerInstance' metric.",
            "B": "Have users upload files directly to an Application Load Balancer that routes HTTP POST requests to synchronous Lambda functions.",
            "C": "Store the PDF files directly in Amazon DynamoDB as binary attributes and trigger DynamoDB Streams to invoke an EC2 instance.",
            "D": "Attach an Amazon EBS Multi-Attach volume to all EC2 instances and write files directly to the shared EBS block device."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Decoupled upload & immediate confirmation:** Uploading to S3 gives users high durability and immediate upload acknowledgment.\n* **S3 Event Notifications to SQS:** S3 automatically queues a message in SQS whenever a new file lands, providing a durable buffer.\n* **Target Tracking on BacklogPerInstance:** AWS best practice for scaling worker fleets behind an SQS queue is tracking the backlog per instance (`ApproximateNumberOfMessagesVisible` divided by the fleet capacity). The Auto Scaling group scales out when the queue builds up and scales in when the queue is drained.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Lambda functions running synchronous 90-second OCR computations behind an ALB risk ALB 60-second default timeouts, high concurrency limits, and poor cost efficiency for long-running CPU workloads.\n* **Option C is incorrect:** DynamoDB maximum item size is 400 KB; 25 MB PDF files exceed DynamoDB limits.\n* **Option D is incorrect:** EBS Multi-Attach requires a cluster-aware file system (like GFS2) to prevent data corruption and is limited to instances in a single AZ, not a general scalable multi-tier web architecture.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Asynchronous file processing pattern:** Client -> S3 -> S3 Event Notification -> SQS -> EC2 Auto Scaling worker tier.\n2. **Scaling metric for SQS worker fleets:** Use custom metric **Backlog Per Instance** (`ApproximateNumberOfMessagesVisible / ASG Fleet Size`) rather than standard CPU utilization."
    },
    # Task 2.2 - Question 10 (Single)
    {
        "domain": 2,
        "task": "2.2",
        "topics": ["Disaster recovery", "RPO", "RTO", "Multi-Region DR"],
        "prompt": "An enterprise is defining a disaster recovery (DR) strategy for its core banking application across two AWS Regions: us-east-1 (active) and us-west-2 (standby). The business requires a Recovery Point Objective (RPO) of less than 15 minutes and a Recovery Time Objective (RTO) of less than 10 minutes. The standby Region should run minimal, scaled-down core infrastructure (such as a small database replica and essential base services) that can rapidly scale up to handle full production load upon failover. Which disaster recovery strategy matches these requirements?",
        "options": {
            "A": "Backup and Restore",
            "B": "Pilot Light",
            "C": "Warm Standby",
            "D": "Multi-Site Active-Active"
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["C"],
        "explanation": "### ✅ Why Option C is Correct\n\n* **Warm Standby:** In a Warm Standby DR strategy, a scaled-down but *fully functional* version of the core system is continuously running in the secondary Region. It actively syncs data (meeting low RPO < 15 min) and can immediately take initial traffic and scale up horizontally in minutes (meeting low RTO < 10 min).\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option A is incorrect (Backup and Restore):** Backups are restored only after disaster strikes; RTO is hours to days.\n* **Option B is incorrect (Pilot Light):** In Pilot Light, data is replicated and core infrastructure like databases may be running, but application compute/web servers are NOT running (AMIs/templates are maintained, but instances must be launched). Scaling up from zero compute typically takes 15-30+ minutes, exceeding the strict 10-minute RTO.\n* **Option D is incorrect (Multi-Site Active-Active):** Multi-Site Active-Active serves production traffic from both regions simultaneously with near-zero RTO/RPO; it does not run a 'minimal, scaled-down standby'.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **AWS DR Strategies spectrum:**\n   - **Backup & Restore:** Highest RPO/RTO, lowest cost.\n   - **Pilot Light:** Data live, core services off; moderate RTO.\n   - **Warm Standby:** Scaled-down core always running; minutes RTO/RPO.\n   - **Active-Active:** Full capacity multi-site, zero downtime, highest cost."
    },
    # Task 2.2 - Question 11 (Single)
    {
        "domain": 2,
        "task": "2.2",
        "topics": ["Amazon Route 53", "Application Recovery Controller", "Failover"],
        "prompt": "A critical payment processor hosts its API across two AWS Regions in an active-active configuration. The engineering team needs a mechanism to shift 100% of incoming production traffic away from one Region to the other within seconds during an incident. The mechanism must not rely on DNS TTL expiration caches in internet client resolvers and must allow engineers to trigger failover safely with a simple, highly reliable control plane switch. Which service feature should the solutions architect implement?",
        "options": {
            "A": "Amazon Route 53 Application Recovery Controller (ARC) routing controls.",
            "B": "Manually update the Route 53 latency records in the public hosted zone and wait for TTL expiration.",
            "C": "Update the AWS WAF Web ACL to return HTTP 500 errors in the degraded Region.",
            "D": "Delete the Application Load Balancer in the degraded Region so DNS queries fail over."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Route 53 Application Recovery Controller (ARC):** Route 53 ARC provides **routing controls** (on/off switches) that let you safely shift traffic across Availability Zones or AWS Regions. Routing controls use a cluster of five regional endpoints with quorum-based consensus, remaining fully operational even if an entire AWS Region is down.\n* **Immediate traffic shifting:** ARC routing controls integrate with Route 53 health checks to instantly redirect traffic without waiting for client DNS TTL re-queries or complex record edits.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Public DNS resolvers frequently ignore or extend DNS TTLs, causing client caching delays of 15-60 minutes, which violates rapid failover requirements.\n* **Option C is incorrect:** Returning HTTP 500 errors breaks end-user payment transactions rather than rerouting them to the healthy Region.\n* **Option D is incorrect:** Deleting infrastructure is destructive, irreversible in seconds, and takes minutes to propagate.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Route 53 ARC:** Use **Route 53 Application Recovery Controller** for mission-critical automated readiness checks and instantaneous cross-Region/cross-AZ routing controls.\n2. **High availability of ARC:** ARC runs across 5 AWS Regions to ensure routing controls can be toggled even when the workload Region is completely offline."
    },
    # Task 2.2 - Question 12 (Single)
    {
        "domain": 2,
        "task": "2.2",
        "topics": ["Amazon RDS", "Multi-AZ DB Cluster", "Failover time"],
        "prompt": "A company runs an enterprise e-commerce transaction database on Amazon RDS for PostgreSQL with a standard Multi-AZ DB instance deployment (one primary and one synchronous standby). During an unexpected primary instance hardware failure, the automatic failover took 85 seconds, causing transaction timeouts. The business requires a database solution that lowers failover downtime to under 35 seconds, provides two readable standby instances across Availability Zones, and supports faster transaction commit latencies. Which solution meets these requirements?",
        "options": {
            "A": "Migrate the database to an Amazon RDS Multi-AZ DB Cluster deployment with two readable standby instances across three Availability Zones.",
            "B": "Deploy an Amazon RDS Single-AZ instance and create an asynchronous read replica in a different Region.",
            "C": "Increase the storage volume size of the existing Multi-AZ DB instance to 64 TB.",
            "D": "Deploy an Amazon EC2 instance running self-managed PostgreSQL with custom rsync scripts."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **RDS Multi-AZ DB Cluster:** Amazon RDS offers a Multi-AZ DB Cluster deployment option with one primary writer and **two readable standby instances** across three Availability Zones.\n* **Sub-35 second failovers:** Uses NVMe-based solid-state storage and optimized transaction commit protocols, reducing failover time from ~60-120 seconds down to typically under 35 seconds.\n* **Read scalability:** Unlike traditional Multi-AZ (where the standby is passive and cannot serve reads), both standbys in a Multi-AZ DB cluster serve read traffic without needing extra read replicas.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Single-AZ has zero high availability; failure requires manual intervention and long downtime.\n* **Option C is incorrect:** Increasing disk capacity does not change failover architecture or add readable standbys.\n* **Option D is incorrect:** Self-managed EC2 databases drastically increase operational maintenance, manual patching, and failover engineering complexity.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **RDS Multi-AZ Instance vs Multi-AZ Cluster:**\n   - **Multi-AZ DB Instance:** 1 primary + 1 non-readable standby. Failover ~60-120 seconds.\n   - **Multi-AZ DB Cluster:** 1 primary + 2 readable standbys across 3 AZs. Failover typically < 35 seconds."
    },
    # Task 2.2 - Question 13 (Multi 2 of 5)
    {
        "domain": 2,
        "task": "2.2",
        "topics": ["Amazon S3", "S3 Cross-Region Replication", "Replication Time Control"],
        "prompt": "A healthcare provider stores medical diagnostic scans in an Amazon S3 bucket in us-east-1. Due to compliance and disaster recovery requirements: (1) all new scans and updates to existing scans must be automatically replicated to a secondary bucket in us-west-2, (2) new objects must replicate within 15 minutes, with that replication time backed by a Service Level Agreement (SLA), and (3) deletions of object versions must not replicate to the destination bucket to prevent accidental data destruction. Which combination of configurations meets these requirements? (Select TWO.)",
        "options": {
            "A": "Enable Amazon S3 Replication Time Control (S3 RTC) on the cross-region replication rule.",
            "B": "Enable S3 Cross-Region Replication (CRR) and enable Delete Marker Replication in the replication rule.",
            "C": "Enable S3 Cross-Region Replication (CRR) and disable Delete Marker Replication in the replication rule.",
            "D": "Use AWS DataSync to execute scheduled hourly transfers between the two S3 buckets.",
            "E": "Enable S3 Cross-Account Transfer Acceleration with automatic object shredding."
        },
        "isMulti": True,
        "requiredCount": 2,
        "correctAnswers": ["A", "C"],
        "explanation": "### ✅ Why Options A & C are Correct\n\n* **S3 Replication Time Control (RTC) (A):** S3 RTC is designed to replicate 99.99% of new objects within 15 minutes, and it is the only S3 replication option backed by an SLA (the SLA commits to 99.9% of objects within 15 minutes in a billing month). It also turns on S3 Replication metrics in CloudWatch for replication latency and pending bytes and operations.\n* **Disable Delete Marker Replication (C):** By disabling delete marker replication, if a user or script deletes an object in the source bucket (creating a delete marker), the delete marker is not copied to the destination bucket, protecting the secondary bucket from accidental deletions. Deletes that name a specific object version ID are never replicated, so permanently removing a version in the source never removes it from the destination.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Enabling delete marker replication would cause deletions in the primary bucket to propagate to the DR bucket, violating requirement (3).\n* **Option D is incorrect:** DataSync scheduled hourly cannot provide the continuous 15-minute SLA replication required by compliance.\n* **Option E is incorrect:** S3 Transfer Acceleration speeds up internet client uploads to S3; there is no 'Cross-Account Transfer Acceleration with automatic object shredding'.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Replication within 15 minutes backed by SLA:** Choose **S3 Replication Time Control (S3 RTC)**. Design target: 99.99% of objects in 15 minutes; SLA commitment: 99.9%.\n2. **Protect against accidental deletion across replication:** Ensure **Delete Marker Replication** is disabled in the replication rule."
    },
    # Task 2.2 - Question 14 (Single)
    {
        "domain": 2,
        "task": "2.2",
        "topics": ["Amazon Aurora", "Aurora Global Database", "Disaster recovery"],
        "prompt": "An international retail enterprise runs its core transactional ordering database on Amazon Aurora PostgreSQL. The enterprise wants to implement a disaster recovery strategy across a secondary AWS Region 2,000 miles away. The solution must provide cross-region physical storage-level replication with typical latency under 1 second, have zero impact on database write throughput in the primary Region, and enable fast promotion of the secondary cluster with RTO under 1 minute in the event of a regional disaster. Which database architecture meets these requirements?",
        "options": {
            "A": "Deploy an Amazon Aurora Global Database with the primary DB cluster in the main Region and a secondary DB cluster in the disaster recovery Region.",
            "B": "Deploy an Aurora DB cluster in the primary Region and set up AWS Database Migration Service (AWS DMS) continuous change data capture (CDC) to an EC2 PostgreSQL instance in the secondary Region.",
            "C": "Create an automated snapshot of the Aurora cluster every hour and copy the snapshot to the secondary Region using AWS Lambda.",
            "D": "Set up PostgreSQL logical replication over an AWS Site-to-Site VPN to an on-premises physical database server."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Amazon Aurora Global Database:** Designed for globally distributed applications and fast disaster recovery. Aurora's dedicated storage infrastructure handles replication across Regions with typical replication latency of under 1 second.\n* **Zero performance impact on primary:** Replication occurs at the storage layer; primary database compute instances do not spend CPU or memory replicating data.\n* **Sub-minute RTO:** Secondary clusters can be promoted to a standalone read-write cluster in under 1 minute using managed unplanned failover.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** AWS DMS CDC introduces compute overhead, replication lag during high write spikes, and requires managing replication instances.\n* **Option C is incorrect:** Hourly snapshots yield an RPO of up to 60 minutes, and restoring an Aurora cluster from a snapshot takes 15-30+ minutes, violating both RPO and RTO goals.\n* **Option D is incorrect:** Logical replication over VPN is constrained by network bandwidth, introduces write latency, and does not provide managed sub-minute failover.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Aurora Cross-Region DR with < 1s latency & sub-minute failover:** **Amazon Aurora Global Database**.\n2. **Storage-level replication:** Aurora Global Database replicates at the storage layer, completely freeing database compute engines from replication overhead."
    },
    # Task 2.2 - Question 15 (Single)
    {
        "domain": 2,
        "task": "2.2",
        "topics": ["Static stability", "Availability Zones", "Resilient architecture"],
        "prompt": "A solutions architect is reviewing an enterprise banking application deployed across three Availability Zones behind an Application Load Balancer. The system consists of an Amazon EC2 Auto Scaling group and an Amazon Aurora database. During a past Availability Zone outage, the Auto Scaling group attempted to launch replacement EC2 instances in the remaining two AZs, but faced severe delays because control plane API rate limits were saturated during the regional event. Which architectural pattern should the solutions architect implement to achieve 'static stability'?",
        "options": {
            "A": "Pre-provision sufficient EC2 capacity across the Availability Zones so that if any single AZ fails, the remaining AZs already have 100% of the compute capacity needed to handle full production load without waiting for Auto Scaling to launch new instances.",
            "B": "Configure the Auto Scaling group to launch instances in all AWS Regions worldwide on an hourly schedule.",
            "C": "Replace the EC2 instances with a single large bare-metal EC2 instance in a single Availability Zone.",
            "D": "Write a Lambda function to call 'ec2:RunInstances' every 10 seconds during an outage."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Static Stability Pattern:** AWS Well-Architected Framework emphasizes static stability: the workload should continue operating normally without needing to make control plane calls (such as launching new instances, provisioning disks, or modifying route tables) during an active failure.\n* **Pre-provisioning across AZs:** For example, provisioning 50% capacity in each of 3 AZs (total 150%) guarantees that if one AZ fails completely, the remaining two AZs immediately provide 100% capacity with zero dependency on the EC2 control plane during the incident.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Launching instances globally adds extreme cost and does not solve local regional availability.\n* **Option C is incorrect:** Single AZ bare-metal creates an immediate single point of failure.\n* **Option D is incorrect:** Aggressively calling `RunInstances` every 10 seconds exacerbates API rate limiting and throttling errors.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Static Stability:** Workloads are resilient to impairment when they do not rely on dynamic control plane changes during failure.\n2. **Sizing for AZ loss:** For 3 AZs, run at least 50% capacity per AZ (total 150%) so that losing 1 AZ leaves 100% capacity."
    },
    # Task 2.2 - Question 16 (Single)
    {
        "domain": 2,
        "task": "2.2",
        "topics": ["AWS Fault Injection Service", "Resilience testing", "Chaos engineering"],
        "prompt": "An insurance enterprise wants to validate that its multi-tier application can smoothly survive the sudden failure of an Amazon EC2 instance, an Availability Zone network disruption, and an Amazon Aurora database failover. The company wants to run controlled, automated chaos engineering experiments in a staging environment to observe system recovery metrics without writing custom scripts to terminate resources manually. Which AWS service should the enterprise use?",
        "options": {
            "A": "AWS Fault Injection Service (AWS FIS)",
            "B": "AWS Trusted Advisor",
            "C": "AWS Shield Advanced",
            "D": "Amazon CloudWatch Synthetics"
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **AWS Fault Injection Service (AWS FIS):** A fully managed service for running controlled fault injection and chaos engineering experiments on AWS workloads.\n* **Pre-built actions:** Provides built-in actions to simulate real-world impairments, such as draining container tasks, stopping EC2 instances, injecting CPU stress, simulating network latency/blackholes, and triggering RDS/Aurora failovers.\n* **Safety guardrails:** FIS includes stop conditions that automatically roll back experiments if CloudWatch alarms breach safety thresholds.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Trusted Advisor inspects account configurations for cost, performance, and security recommendations; it cannot inject faults.\n* **Option C is incorrect:** Shield Advanced protects applications against distributed denial of service (DDoS) attacks; it does not simulate internal infrastructure failure.\n* **Option D is incorrect:** CloudWatch Synthetics runs canaries to monitor user endpoints and APIs; it does not inject underlying infrastructure faults.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Chaos engineering / fault injection on AWS:** **AWS Fault Injection Service (AWS FIS)**.\n2. **Stop conditions:** FIS integrates with Amazon CloudWatch alarms to halt experiments if unexpected production disruption occurs."
    },
    # Task 2.2 - Question 17 (Multi 3 of 6)
    {
        "domain": 2,
        "task": "2.2",
        "topics": ["Amazon EC2 Auto Scaling", "Application Load Balancer", "High availability"],
        "prompt": "A media company is hosting a high-traffic web application on Amazon EC2 instances across three Availability Zones behind an Application Load Balancer (ALB). The instances are managed by an Auto Scaling group (ASG). During a recent load spike, several newly launched EC2 instances received traffic before their local web server software finished initializing, returning HTTP 502 Bad Gateway errors to users. Additionally, unhealthy instances were not being replaced promptly. Which combination of configurations resolves these issues and improves fleet resilience? (Select THREE.)",
        "options": {
            "A": "Configure the Auto Scaling group health check type to use ELB health checks in addition to EC2 status checks.",
            "B": "Configure an appropriate health check grace period on the Auto Scaling group to give instances time to complete initialization scripts.",
            "C": "Configure ALB target group health checks with an appropriate success threshold, interval, and path matching the application health endpoint.",
            "D": "Change the ALB to a Classic Load Balancer with TCP pass-through.",
            "E": "Disable cross-zone load balancing on the ALB.",
            "F": "Set the minimum capacity of the Auto Scaling group to 0."
        },
        "isMulti": True,
        "requiredCount": 3,
        "correctAnswers": ["A", "B", "C"],
        "explanation": "### ✅ Why Options A & B & C are Correct\n\n* **ELB Health Checks on ASG (A):** By default, ASG only uses EC2 hardware/OS status checks. If the web server process crashes, EC2 still looks healthy. Enabling ELB health checks ensures the ASG replaces instances if the ALB health check marks them unhealthy.\n* **Health Check Grace Period (B):** The grace period prevents the ASG from prematurely terminating newly launched instances while user-data scripts or application runtimes are still bootstrapping.\n* **Target Group Health Checks (C):** Setting an explicit health check path (e.g. `/healthz`) with reasonable intervals and thresholds ensures the ALB directs traffic only to instances that are fully ready to serve traffic.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option D is incorrect:** Classic Load Balancers are legacy, lack modern ALB routing and performance features, and do not resolve initialization race conditions.\n* **Option E is incorrect:** Disabling cross-zone load balancing can lead to uneven request distribution across backend instances.\n* **Option F is incorrect:** Setting minimum capacity to 0 allows the fleet to scale down completely to zero, causing downtime.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Premature traffic / 502 during ASG scale out:** Increase the **Health Check Grace Period**.\n2. **Unhealthy web server not replaced:** Switch ASG health check type from **EC2** to **ELB**."
    }
]
