"""Domain 3: Design High-Performing Architectures (15 Questions for Set 3)
Tasks:
- 3.1: Determine high-performing and/or scalable storage solutions (3 questions, 1 multi)
- 3.2: Design high-performing and elastic compute solutions (3 questions)
- 3.3: Determine high-performing database solutions (3 questions)
- 3.4: Determine high-performing and/or scalable network architectures (3 questions)
- 3.5: Determine high-performing data ingestion and transformation solutions (3 questions, 1 multi)
"""

QUESTIONS = [
    # Task 3.1 - Question 1 (Single)
    {
        "domain": 3,
        "task": "3.1",
        "topics": ["Amazon S3 Express One Zone", "Machine learning", "Low latency storage"],
        "prompt": "An artificial intelligence research team is training large multimodal deep learning models on GPU-powered Amazon EC2 P5 instances located in a single Availability Zone. The training algorithm performs millions of small, read-heavy operations on image feature tensors per minute. The team requires object storage with consistent single-digit millisecond data access latencies (up to 10x faster than standard S3), high request throughput, and full compatibility with existing AWS SDK S3 APIs. Which storage solution should a solutions architect recommend?",
        "options": {
            "A": "Store training data in Amazon S3 Express One Zone directory buckets co-located in the same Availability Zone as the EC2 P5 instances.",
            "B": "Store training data in an Amazon S3 Standard general purpose bucket with S3 Transfer Acceleration enabled.",
            "C": "Mount an Amazon S3 Glacier Instant Retrieval bucket directly to the EC2 instances using NFS.",
            "D": "Attach an Amazon EBS cold HDD (sc1) volume to each EC2 instance and replicate files using rsync."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **S3 Express One Zone:** A high-performance, single-AZ S3 storage class designed specifically to deliver consistent single-digit millisecond data access latencies for latency-sensitive applications like AI/ML training and financial modeling.\n* **Directory buckets:** Uses specialized directory buckets co-located within the specific Availability Zone chosen by the customer, eliminating inter-AZ latency.\n* **10x faster & 50% lower request costs:** Delivers up to 10x lower latency than S3 Standard while reducing request processing costs by up to 50% for high-frequency access patterns.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** S3 Transfer Acceleration optimizes public internet uploads via CloudFront Edge Locations; it does not reduce intra-cloud read latencies between EC2 and S3 within an AZ.\n* **Option C is incorrect:** S3 Glacier Instant Retrieval has millisecond access but standard request latency (tens of milliseconds) and high per-GB retrieval fees, and S3 cannot be natively mounted via NFS.\n* **Option D is incorrect:** EBS sc1 volumes provide throughput-optimized magnetic storage for large sequential cold workloads, not ultra-fast low-latency random I/O for AI/ML training.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **S3 Express One Zone:** Choose when single-digit millisecond latency is needed on S3 object storage (e.g. AI/ML training, real-time analytics).\n2. **Directory Buckets:** S3 Express One Zone uses directory buckets rather than general purpose buckets."
    },
    # Task 3.1 - Question 2 (Single)
    {
        "domain": 3,
        "task": "3.1",
        "topics": ["Amazon FSx for NetApp ONTAP", "Enterprise storage", "Multi-AZ file systems"],
        "prompt": "A company is migrating an enterprise enterprise resource planning (ERP) application from an on-premises data center to AWS. The application requires a shared POSIX-compliant file system accessible over both NFS and SMB protocols concurrently. It also requires snapshot capabilities, deduplication, thin provisioning, and sub-millisecond file operation latency. The file system must span multiple Availability Zones with automatic failover. Which AWS storage service meets all these requirements?",
        "options": {
            "A": "Amazon FSx for NetApp ONTAP",
            "B": "Amazon Elastic File System (Amazon EFS)",
            "C": "Amazon FSx for Lustre",
            "D": "Amazon EBS Multi-Attach io2 volumes"
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Amazon FSx for NetApp ONTAP:** Provides full NetApp ONTAP features in a fully managed AWS service, supporting dual-protocol access (NFS v3/v4 and SMB v2/v3 simultaneously).\n* **Advanced storage features:** Features built-in hardware compression, deduplication, compaction, thin provisioning, and instant snapshots.\n* **Multi-AZ high availability:** Provides automated synchronous replication across Availability Zones with automatic failover in typically under 60 seconds.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Amazon EFS supports only NFS (Linux), not SMB (Windows), and does not support native deduplication or NetApp snapshot tooling.\n* **Option C is incorrect:** FSx for Lustre is a high-performance POSIX file system for HPC/compute-heavy workloads; it does not support SMB or enterprise multi-protocol storage management.\n* **Option D is incorrect:** EBS Multi-Attach io2 is a block storage volume confined to a single Availability Zone, not a multi-AZ managed file system.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **NFS + SMB dual protocol / NetApp ONTAP features:** Always choose **Amazon FSx for NetApp ONTAP**.\n2. **Tiering in FSx for ONTAP:** Offers primary NVMe/SSD storage and an automated capacity pool tier backed by S3 for cost optimization."
    },
    # Task 3.1 - Question 3 (Multi 2 of 5)
    {
        "domain": 3,
        "task": "3.1",
        "topics": ["Amazon EBS", "io2 Block Express", "High IOPS storage"],
        "prompt": "A global banking corporation runs a mission-critical transactional Oracle database on Amazon EC2 instances. The database demands 160,000 IOPS, 3,500 MB/s throughput, and sub-millisecond I/O latency with 99.999% volume durability. The storage volume must support dynamic online capacity resizing without taking the database offline. Which combination of Amazon EBS volume type and configuration should a solutions architect recommend? (Select TWO.)",
        "options": {
            "A": "Use Amazon EBS Provisioned IOPS SSD (io2 Block Express) volumes.",
            "B": "Use Amazon EBS General Purpose SSD (gp3) volumes striped in RAID 0.",
            "C": "Provision the required IOPS and storage capacity using Amazon EBS Elastic Volumes.",
            "D": "Use Amazon EBS Cold HDD (sc1) volumes with IOPS bursts.",
            "E": "Use Amazon EC2 instance store NVMe SSDs without EBS."
        },
        "isMulti": True,
        "requiredCount": 2,
        "correctAnswers": ["A", "C"],
        "explanation": "### ✅ Why Options A & C are Correct\n\n* **io2 Block Express (A):** Designed for mission-critical, high-throughput, low-latency databases. It delivers up to 256,000 IOPS, 4,000 MB/s throughput, sub-millisecond latencies, and 99.999% durability (100x higher durability than standard gp3/io1).\n* **EBS Elastic Volumes (C):** Allows you to dynamically increase volume size, adjust provisioned IOPS, or change volume types on live EBS volumes on-the-fly with zero downtime or performance detachment.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** A single gp3 volume maxes out at 16,000 IOPS and 1,000 MB/s. Striping gp3 volumes in RAID 0 increases risk (if any volume fails, the entire RAID array is lost) and does not achieve sub-millisecond enterprise durability.\n* **Option D is incorrect:** EBS sc1 is magnetic HDD designed for cold sequential workloads with low IOPS (max 250 IOPS).\n* **Option E is incorrect:** EC2 instance store is ephemeral; all data is permanently lost when the EC2 instance is stopped or hardware fails, which is unacceptable for a mission-critical banking database without external replication.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Highest EBS performance & 99.999% durability:** **io2 Block Express** (up to 256k IOPS, 4,000 MB/s).\n2. **Modify EBS without downtime:** **Amazon EBS Elastic Volumes**."
    },
    # Task 3.2 - Question 4 (Single)
    {
        "domain": 3,
        "task": "3.2",
        "topics": ["AWS Lambda", "Lambda SnapStart", "Cold start latency"],
        "prompt": "An online retail bank runs its loan approval microservice on AWS Lambda using Java 21 managed runtime. During morning traffic bursts, users experience response delays of over 4 seconds for initial requests due to JVM initialization and dependency injection (cold starts). Once initialized, subsequent requests execute in under 40 milliseconds. The engineering team wants to reduce cold start latency to under 250 milliseconds with the MINIMAL operational and development effort. Which feature should a solutions architect recommend?",
        "options": {
            "A": "Enable AWS Lambda SnapStart on the Lambda function.",
            "B": "Rewrite the entire loan approval microservice in Python or Node.js.",
            "C": "Increase the Lambda function timeout from 3 seconds to 15 minutes.",
            "D": "Deploy an Amazon CloudWatch Synthetics canary to ping the Lambda function every 5 minutes."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Lambda SnapStart:** Improves startup performance for Java functions by up to 90% (sub-second or sub-200ms cold starts). When you publish a function version, SnapStart initializes the function, takes a Firecracker microVM snapshot of the initialized memory and disk state, encrypts the snapshot, and caches it for multi-tier retrieval.\n* **Zero rewriting:** Requires simply turning on SnapStart on the function version without rewriting application code into another language.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Rewriting an entire enterprise loan microservice in another language requires enormous development effort, regression testing, and business risk.\n* **Option C is incorrect:** Function timeout specifies the maximum time a function is allowed to run before being killed; increasing it does nothing to shorten cold start initialization time.\n* **Option D is incorrect:** CloudWatch canary pings only keep one execution environment warm; during sudden concurrent traffic spikes, Lambda must spawn dozens of new execution environments which will all suffer the cold start delay.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Java Lambda cold start optimization:** Turn on **AWS Lambda SnapStart**.\n2. **SnapStart compatibility:** Supported on Java managed runtimes; initializes code at deployment time rather than invocation time."
    },
    # Task 3.2 - Question 5 (Single)
    {
        "domain": 3,
        "task": "3.2",
        "topics": ["Amazon EC2", "Cluster placement group", "Elastic Fabric Adapter", "HPC"],
        "prompt": "An aerospace engineering company runs computational fluid dynamics (CFD) simulation workloads on Amazon EC2 instances. The CFD simulation uses Message Passing Interface (MPI) for inter-node communication and requires high-throughput, low-latency inter-node networking (sub-15 microseconds) to achieve linear scaling across 64 instances. Which combination of AWS architecture choices will maximize network performance for this tightly coupled HPC workload?",
        "options": {
            "A": "Deploy compute-optimized EC2 instances equipped with Elastic Fabric Adapter (EFA) network interfaces inside a Cluster Placement Group within a single Availability Zone.",
            "B": "Deploy instances inside a Spread Placement Group distributed across three Availability Zones with Elastic Network Adapters (ENA).",
            "C": "Deploy instances inside a Partition Placement Group connected via AWS Transit Gateway.",
            "D": "Distribute instances across multiple AWS Regions connected by AWS Direct Connect Gateway."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Cluster Placement Group:** Packs instances close together inside a single Availability Zone to achieve the lowest possible network latency and highest network throughput.\n* **Elastic Fabric Adapter (EFA):** A specialized network interface designed specifically for HPC and ML workloads. It uses Libfabric and OS-bypass architecture to route MPI communication directly between application memory and the network hardware, bypassing the OS kernel for sub-15 microsecond latencies.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Spread placement groups place instances across distinct underlying hardware racks (max 7 instances per AZ) to reduce correlated failures, increasing physical distance and network latency.\n* **Option C is incorrect:** Partition placement groups are for distributed big data (HDFS, Cassandra, Kafka), not tightly coupled low-latency MPI simulations.\n* **Option D is incorrect:** Spanning multiple Regions introduces milliseconds of geographic latency, completely destroying tightly coupled MPI scaling.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Tightly coupled HPC / MPI workloads:** **Cluster Placement Group** + **Elastic Fabric Adapter (EFA)**.\n2. **Placement Groups summary:**\n   - **Cluster:** Low latency / high throughput in 1 AZ.\n   - **Spread:** Isolated hardware racks to reduce failure blast radius (max 7 per AZ).\n   - **Partition:** Large distributed workloads across partitions (Hadoop/Cassandra)."
    },
    # Task 3.2 - Question 6 (Single)
    {
        "domain": 3,
        "task": "3.2",
        "topics": ["AWS App Runner", "Container deployment", "PaaS"],
        "prompt": "A developer team that is new to AWS needs to deploy a containerized Node.js web application with an HTTPS endpoint. A GitHub Actions workflow already builds the container image and pushes it to Amazon Elastic Container Registry (Amazon ECR) on every commit, and each new image must be deployed automatically. The application will receive varying web traffic and must scale automatically from a few requests up to thousands of requests per second. The team has limited cloud operations experience and wants a managed AWS option that sets up the networking, load balancing, TLS and auto scaling for them, so they never have to design VPCs, subnets, route tables, Application Load Balancers, or ECS cluster settings themselves. Which option should they choose?",
        "options": {
            "A": "Amazon ECS Express Mode",
            "B": "Amazon Elastic Kubernetes Service (Amazon EKS)",
            "C": "Amazon EC2 with AWS Systems Manager",
            "D": "AWS CloudFormation with custom AMI provisioning"
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Amazon ECS Express Mode:** You supply a container image, a task execution role and an infrastructure role. Amazon ECS then creates a Fargate-based service with a unique HTTPS URL, an Application Load Balancer with TLS, auto scaling policies, monitoring and networking, all with production-ready defaults.\n* **No infrastructure design:** The team never designs the VPC, subnets, load balancer or cluster. The resources are created in the team's own account, so they can still be tuned later.\n* **Automated deployments:** The AWS-maintained GitHub Action for ECS Express Mode deploys each new image that the workflow pushes to Amazon ECR.\n* **Cost:** Express Mode itself has no extra charge; the team pays for the Fargate tasks, load balancer, logs and data transfer.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Amazon EKS requires significant Kubernetes operational expertise, VPC networking configuration, ingress controllers, and cluster management.\n* **Option C is incorrect:** Amazon EC2 requires managing virtual machines, OS patching, VPC subnets, and load balancers.\n* **Option D is incorrect:** Custom CloudFormation and AMI provisioning involves extensive DevOps overhead.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Deploy a containerized web app or API with no infrastructure design:** **Amazon ECS Express Mode**. Older exam questions give **AWS App Runner** as the answer for the same pattern.\n2. **Availability note:** AWS App Runner is no longer open to new customers. Existing customers can keep using it, and AWS recommends ECS Express Mode as the migration path.\n3. **Express Mode vs full ECS/EKS:** Choose Express Mode for simple HTTP apps and APIs; configure ECS or EKS directly when you need deep network customization or complex microservice orchestration."
    },
    # Task 3.3 - Question 7 (Single)
    {
        "domain": 3,
        "task": "3.3",
        "topics": ["Amazon ElastiCache Serverless", "In-memory caching", "Auto-scaling"],
        "prompt": "An online gaming platform uses an in-memory caching layer to store live leaderboard standings and player session states. Traffic is highly unpredictable: player surges occur during game release events, while traffic drops to near zero overnight. The platform previously suffered from out-of-memory errors during surges and over-provisioned cluster costs during quiet hours. The engineering team wants an in-memory cache that automatically scales compute and memory in seconds, eliminates cluster node provisioning, and charges strictly for stored data and compute capacity consumed. Which solution meets these requirements?",
        "options": {
            "A": "Deploy Amazon ElastiCache Serverless for Redis (or Valkey).",
            "B": "Deploy an Amazon ElastiCache node-based cluster with t4g.micro nodes and manually resize nodes during tournaments.",
            "C": "Deploy an Amazon DynamoDB table with standard read/write capacity units and no in-memory cache.",
            "D": "Deploy an Amazon RDS for MySQL database with maximum read replicas."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **ElastiCache Serverless:** Automatically scales memory and compute (measured in ElastiCache Processing Units or ECPUs) up or down in seconds to match application traffic demands.\n* **No cluster management:** Eliminates the need to select node types, configure shard counts, plan cluster capacity, or handle manual node resizings.\n* **Sub-millisecond latency:** Preserves the ultra-fast sub-millisecond read/write performance of Redis OSS / Valkey / Memcached with Multi-AZ redundancy.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Node-based ElastiCache requires manual capacity planning, node type selection, and vertical scaling can take 15-30 minutes, failing sudden spikes.\n* **Option C is incorrect:** DynamoDB provides single-digit millisecond latency, which is slower than sub-millisecond in-memory caching, and does not provide Redis data structures (like Sorted Sets for leaderboards).\n* **Option D is incorrect:** RDS for MySQL is a relational disk-based database, not an ultra-fast in-memory cache.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Serverless in-memory caching:** **Amazon ElastiCache Serverless**.\n2. **Billing:** In ElastiCache Serverless, you pay for data stored (GB-hours) and compute consumed (ECPUs), with zero charges for idle cluster instances."
    },
    # Task 3.3 - Question 8 (Single)
    {
        "domain": 3,
        "task": "3.3",
        "topics": ["Amazon MemoryDB for Redis", "Durability", "In-memory database"],
        "prompt": "A ride-sharing platform is building a real-time driver dispatch matching service. The service requires microsecond read latencies and single-digit millisecond write latencies using Redis data structures. Unlike a temporary cache, the data stored in this service represents critical active ride state; therefore, the database must guarantee zero data loss by persisting all writes synchronously to a Multi-AZ transactional log before acknowledging write requests. Which AWS service is designed for this use case?",
        "options": {
            "A": "Amazon MemoryDB for Redis",
            "B": "Amazon ElastiCache for Redis with replication groups",
            "C": "Amazon S3 One Zone-IA",
            "D": "Amazon Redshift with AQUA acceleration"
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Amazon MemoryDB for Redis:** A Redis-compatible, durable, in-memory database service designed for workloads that require an in-memory database as their primary data store.\n* **Multi-AZ Transaction Log:** Writes are synchronously written to a durable Multi-AZ distributed transaction log before write confirmation is returned, guaranteeing ACID transactions and zero data loss on node failure.\n* **Ultra-fast performance:** Delivers microsecond read latency and single-digit millisecond write latency.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Amazon ElastiCache for Redis is designed primarily as a cache; asynchronous replication to read replicas means failover can result in data loss, so it is not recommended as a durable primary database without a backing database.\n* **Option C is incorrect:** S3 One Zone-IA is object storage with tens of milliseconds latency; it cannot serve microsecond transactional state.\n* **Option D is incorrect:** Amazon Redshift is an analytical OLAP data warehouse for complex SQL queries, not an OLTP in-memory key-value engine.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **ElastiCache vs MemoryDB:**\n   - **ElastiCache:** In-memory *cache* (asynchronous replication; temporary data loss possible).\n   - **MemoryDB:** Primary *in-memory database* (durable Multi-AZ transaction log; zero data loss)."
    },
    # Task 3.3 - Question 9 (Single)
    {
        "domain": 3,
        "task": "3.3",
        "topics": ["Amazon DynamoDB", "Global Secondary Index", "Hot partitions"],
        "prompt": "An e-commerce marketplace stores customer orders in an Amazon DynamoDB table with 'CustomerID' as the partition key and 'OrderDate' as the sort key. During a flash sale, a single celebrity account receives 100,000 orders in 10 minutes, causing DynamoDB throttling exceptions ('ProvisionedThroughputExceededException') even though the overall provisioned write capacity for the table was only at 20% utilization. What is the root cause of this issue, and which design pattern should the solutions architect implement to resolve it?",
        "options": {
            "A": "The table experienced a hot partition because all writes targeted a single partition key value. Implement write sharding by appending a random suffix (e.g. 1 to 10) to the partition key for celebrity accounts.",
            "B": "The table reached the maximum storage size for a DynamoDB table. Delete old records using DynamoDB TTL.",
            "C": "DynamoDB does not support more than 1,000 items per table. Migrate to Amazon RDS MySQL.",
            "D": "The table was missing a Local Secondary Index. Create an LSI on the customer address attribute."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Hot Partition Problem:** DynamoDB allocates throughput across physical partitions based on the partition key hash. A single physical partition has a hard limit of 1,000 WCU or 3,000 RCU. If all 100,000 writes target the exact same `CustomerID`, they hit a single physical partition, resulting in throttling regardless of overall table capacity.\n* **Write Sharding Pattern:** Appending a randomized suffix (e.g. `CustomerID_1`, `CustomerID_2` ... `CustomerID_N`) or calculated hash suffix spreads the writes evenly across multiple partition keys and multiple physical partitions.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** DynamoDB tables have unlimited storage capacity; storage size does not cause instantaneous write throttling.\n* **Option C is incorrect:** DynamoDB scales horizontally to billions of items and petabytes of data.\n* **Option D is incorrect:** Creating an LSI consumes extra write capacity on the same partition and worsens the hot partition problem.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **DynamoDB hot partitions:** Occur when partition keys have low cardinality or traffic is concentrated on a single key.\n2. **Solution for hot write partitions:** **Write Sharding** (appending random or calculated suffixes to partition keys)."
    },
    # Task 3.4 - Question 10 (Single)
    {
        "domain": 3,
        "task": "3.4",
        "topics": ["AWS Global Accelerator", "Anycast IP", "TCP performance"],
        "prompt": "A multinational multiplayer gaming studio hosts game server fleets on Amazon EC2 instances across three AWS Regions: us-east-1, eu-west-1, and ap-southeast-1. Players connect over UDP/TCP game protocols. Players often experience packet loss and jitter because traffic traverses unpredictable public internet routing hops between their ISPs and the AWS Regions. The studio wants to provide players with two static IP addresses that route traffic into the nearest AWS edge location and then transport traffic over the dedicated, congestion-free AWS global network backbone. Which service meets these requirements?",
        "options": {
            "A": "AWS Global Accelerator",
            "B": "Amazon CloudFront with static IP origins",
            "C": "AWS Transit Gateway with inter-Region peering",
            "D": "Amazon Route 53 with latency-based routing"
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **AWS Global Accelerator:** Provides two static Anycast IPv4 addresses that serve as a single fixed entry point for applications globally.\n* **AWS Global Fiber Backbone:** Ingresses client traffic at the nearest AWS edge location and routes it over the high-speed, congestion-free AWS private global network backbone directly to application endpoints in any AWS Region.\n* **Protocol support:** Optimizes non-HTTP protocols (TCP and UDP) as well as HTTP, perfectly matching gaming, VoIP, and IoT workloads.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Amazon CloudFront is a content delivery network (CDN) built for HTTP/HTTPS caching; it does not provide static IP ingress or support raw UDP gaming packets.\n* **Option C is incorrect:** Transit Gateway connects VPCs and on-premises networks; it does not provide public Anycast IP entry points for internet gamers.\n* **Option D is incorrect:** Route 53 resolves DNS queries to regional IPs; once resolved, client packets still travel over the unreliable public internet.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Global Accelerator vs CloudFront:**\n   - **CloudFront:** HTTP/HTTPS web content caching, dynamic API acceleration.\n   - **Global Accelerator:** Static Anycast IPs, TCP/UDP traffic, non-HTTP workloads (gaming, VoIP), instant failover.\n2. **Network Performance:** Global Accelerator bypasses public internet routing issues by entering AWS's private network as close to the user as possible."
    },
    # Task 3.4 - Question 11 (Single)
    {
        "domain": 3,
        "task": "3.4",
        "topics": ["Amazon VPC Lattice", "Service-to-service networking", "Microservices"],
        "prompt": "An enterprise has 200 microservices deployed across 60 AWS accounts and multiple VPCs, using a mix of Amazon ECS, Amazon EKS, and AWS Lambda. Services need to discover and securely communicate with each other over HTTP/HTTPS and gRPC. The platform engineering team is struggling to manage complex Transit Gateway route tables, overlapping IP CIDR ranges, and VPC peering quotas. The team wants an application-layer networking service that enables seamless cross-VPC and cross-account service-to-service connectivity and access control without managing underlying network routes or IP CIDRs. Which service should they implement?",
        "options": {
            "A": "Amazon VPC Lattice",
            "B": "AWS Direct Connect with hosted virtual interfaces",
            "C": "AWS Site-to-Site VPN with BGP dynamic routing",
            "D": "Amazon Route 53 Resolver outbound endpoints in each VPC"
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Amazon VPC Lattice:** An application-layer networking service that connects, monitors, and secures communications between your services across different VPCs and AWS accounts without requiring complex network-layer routing or VPC peering.\n* **Eliminates IP overlapping issues:** Operates at the application layer (Layer 7 HTTP/HTTPS/gRPC), completely eliminating IP CIDR conflict issues.\n* **Built-in security and discovery:** Integrates with AWS IAM for fine-grained service-to-service authorization and provides centralized traffic management and telemetry.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Direct Connect connects on-premises data centers to AWS, not service-to-service networking between internal cloud VPCs.\n* **Option C is incorrect:** VPN connections add encryption overhead, bandwidth bottlenecks (1.25 Gbps per tunnel), and require complex route tables.\n* **Option D is incorrect:** Route 53 Resolver resolves DNS names across hybrid networks; it does not handle application-layer routing, authorization, or IP conflict resolution.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Cross-VPC / cross-account service-to-service communication without managing routes or CIDRs:** **Amazon VPC Lattice**.\n2. **VPC Lattice components:** Service Network, Service, Target Groups, and Auth Policies (IAM-based)."
    },
    # Task 3.4 - Question 12 (Single)
    {
        "domain": 3,
        "task": "3.4",
        "topics": ["Amazon CloudFront", "CloudFront Functions", "Edge computing"],
        "prompt": "A global media company uses Amazon CloudFront to deliver static assets and web content. The company needs to implement lightweight URL rewrites and HTTP header modifications (such as adding security headers like 'X-Frame-Options' and normalizing query strings for cache optimization) on all incoming requests at the edge. The operations must complete in less than 1 millisecond and process 200 million requests daily at the LOWEST possible cost. Which edge compute solution meets these requirements?",
        "options": {
            "A": "CloudFront Functions",
            "B": "Lambda@Edge",
            "C": "Origin Request AWS Lambda behind an Application Load Balancer",
            "D": "Amazon API Gateway HTTP API with mock integrations"
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **CloudFront Functions:** Designed specifically for lightweight, high-scale, latency-sensitive JavaScript functions running at 600+ CloudFront edge locations.\n* **Sub-millisecond execution:** Runs directly in the CloudFront process with sub-millisecond execution times.\n* **Cost effective:** Costs approximately 1/6th the price of Lambda@Edge, making it ideal for high-volume HTTP header modifications, URL redirects, and cache key normalization.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Lambda@Edge is designed for heavier compute (supports Node.js/Python, network calls, access to request bodies, long execution times up to 30 seconds), but has higher latency (tens of ms) and is significantly more expensive for simple header rewrites.\n* **Option C is incorrect:** Routing every request to an origin ALB and Lambda defeats edge execution and incurs high transit and compute costs.\n* **Option D is incorrect:** API Gateway is not an edge compute caching layer.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **CloudFront Functions vs Lambda@Edge:**\n   - **CloudFront Functions:** Lightweight, sub-ms latency, JavaScript only, viewer request/response only, no network access, lowest cost.\n   - **Lambda@Edge:** Complex logic, Node.js/Python, up to 30s execution, can access network/external APIs, body inspection, origin request/response."
    },
    # Task 3.5 - Question 13 (Multi 2 of 5)
    {
        "domain": 3,
        "task": "3.5",
        "topics": ["Amazon Data Firehose", "Dynamic Partitioning", "Data lake ingestion"],
        "prompt": "An analytics platform ingests 2 TB of streaming JSON clickstream data per day from mobile apps. The data must be delivered into an Amazon S3 data lake bucket. Downstream queries in Amazon Athena require data to be partitioned by both event date (`year=YYYY/month=MM/day=DD/`) and `customer_id`. Additionally, data must be converted from JSON to Apache Parquet format to optimize query speed and reduce Athena scan costs. Which combination of Amazon Data Firehose (formerly Kinesis Data Firehose) features should the solutions architect configure? (Select TWO.)",
        "options": {
            "A": "Enable Dynamic Partitioning in Amazon Data Firehose using JQ expressions to parse the partition keys from incoming JSON payloads.",
            "B": "Enable Record Format Conversion in Amazon Data Firehose referencing an AWS Glue Data Catalog table schema to convert JSON to Apache Parquet.",
            "C": "Deploy a custom Amazon EMR cluster to rewrite files in S3 every 5 minutes.",
            "D": "Configure Amazon S3 Lifecycle rules to compress JSON files into ZIP archives.",
            "E": "Use Amazon SQS with AWS Lambda to write individual Parquet files for each clickstream record."
        },
        "isMulti": True,
        "requiredCount": 2,
        "correctAnswers": ["A", "B"],
        "explanation": "### ✅ Why Options A & B are Correct\n\n* **Dynamic Partitioning (A):** Amazon Data Firehose can continuously parse attributes inside streaming data (such as `customer_id` and timestamp) using JQ expressions and write files directly into corresponding parameterized S3 prefix structures (`year=!{timestamp:yyyy}/customer_id=!{partitionKeyFromQuery:customer_id}/`).\n* **Record Format Conversion (B):** Firehose has native integration with AWS Glue Data Catalog to convert streaming JSON records into columnar Apache Parquet or ORC formats before writing objects to Amazon S3, drastically improving analytical query performance and lowering storage footprint.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option C is incorrect:** Running a 24/7 EMR cluster for continuous small rewrites is operationally complex and expensive compared to managed Firehose capabilities.\n* **Option D is incorrect:** S3 Lifecycle transitions storage classes; it does not convert JSON formats to Parquet.\n* **Option E is incorrect:** Writing individual files for every streaming record results in the 'small files problem', destroying S3 performance and inflating Athena query costs.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Streaming ingestion to S3 with Parquet conversion:** **Amazon Data Firehose** + **AWS Glue Data Catalog table schema**.\n2. **Custom S3 partitioning from JSON payload keys:** Use **Amazon Data Firehose Dynamic Partitioning**."
    },
    # Task 3.5 - Question 14 (Single)
    {
        "domain": 3,
        "task": "3.5",
        "topics": ["Amazon MSK", "Apache Kafka", "Streaming architecture"],
        "prompt": "A financial exchange uses Apache Kafka for its high-throughput real-time market data distribution. The exchange wants to migrate its on-premises Kafka cluster to AWS. The solution must support existing Apache Kafka client producer and consumer libraries with no code changes, support mutual TLS (mTLS) and IAM authentication, provide automated broker patching and multi-AZ storage replication, and eliminate manual server provisioning. Which AWS managed service meets these requirements?",
        "options": {
            "A": "Amazon Managed Streaming for Apache Kafka (Amazon MSK)",
            "B": "Amazon Kinesis Video Streams",
            "C": "Amazon Simple Queue Service (Amazon SQS)",
            "D": "Amazon Simple Notification Service (Amazon SNS)"
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Amazon MSK:** A fully managed, highly available service that makes it easy to build and run applications that use Apache Kafka.\n* **100% native Kafka compatibility:** Compatible with open-source Apache Kafka; applications and existing client code, tooling, and connectors work without changes.\n* **Enterprise security & management:** Supports IAM authentication, mTLS, VPC encryption, and automated patching and multi-AZ storage volume management.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Kinesis Video Streams is for ingesting live video and audio streams, not Kafka messaging topics.\n* **Option C is incorrect:** SQS is an AWS proprietary queue service with its own SDK and API, not compatible with Apache Kafka protocols or client libraries.\n* **Option D is incorrect:** SNS is a pub/sub push messaging service, not a persistent distributed commit log like Kafka.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Migrate Apache Kafka to AWS with zero code changes:** **Amazon MSK** (Managed Streaming for Apache Kafka).\n2. **MSK Serverless:** Amazon MSK Serverless automatically manages broker scaling and partitions if cluster capacity planning is not desired."
    },
    # Task 3.5 - Question 15 (Single)
    {
        "domain": 3,
        "task": "3.5",
        "topics": ["AWS Glue", "Job bookmarks", "Data lakehouse ETL"],
        "prompt": "A data engineering team maintains an hourly AWS Glue ETL job that reads raw log files from an Amazon S3 landing bucket, transforms the records, and writes output datasets to an S3 analytics bucket. The raw landing bucket receives thousands of new files every hour. Currently, every time the Glue job runs, it re-reads and re-processes all historical files in the landing bucket, leading to exponential increases in job execution time and cost. What feature should the data engineering team enable to ensure that each Glue job run processes ONLY newly arrived files?",
        "options": {
            "A": "Enable AWS Glue Job Bookmarks on the ETL job.",
            "B": "Delete the entire landing bucket after every run.",
            "C": "Change the Glue job worker type from G.1X to G.8X.",
            "D": "Configure S3 Object Lock on the destination bucket."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **AWS Glue Job Bookmarks:** Keeps track of data that has already been processed during previous runs of an ETL job. By persisting state information across runs, Glue automatically filters out previously processed objects and processes only new and changed files on subsequent scheduled runs.\n* **Prevents reprocessing:** Eliminates redundant data processing, reduces execution time, and lowers Glue DPU costs.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Deleting landing data destroys raw audit records and violates data lake immutability.\n* **Option C is incorrect:** Increasing worker size increases compute power but does not prevent the job from re-reading historical files, and drastically increases costs.\n* **Option D is incorrect:** S3 Object Lock prevents object deletion; it does not track ETL job processing state.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Glue re-processing existing files:** Enable **AWS Glue Job Bookmarks**.\n2. **Glue Job Bookmarks modes:** Enable (track new files), Disable (process all files), Pause (process new files without updating the bookmark state)."
    }
]
