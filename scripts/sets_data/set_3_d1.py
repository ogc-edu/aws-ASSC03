"""Domain 1: Design Secure Architectures (20 Questions for Set 3)
Tasks:
- 1.1: Design secure access to AWS resources (7 questions, 1 multi)
- 1.2: Design secure workloads and applications (7 questions, 1 multi)
- 1.3: Determine appropriate data security controls (6 questions, 1 multi-3)
"""

QUESTIONS = [
    # Task 1.1 - Question 1 (Single)
    {
        "domain": 1,
        "task": "1.1",
        "topics": ["IAM", "Cross-account access", "External ID", "SaaS integration"],
        "prompt": "A company wants to subscribe to a third-party software-as-a-service (SaaS) monitoring platform that needs read-only access to query AWS CloudWatch metrics and describe EC2 instances across 50 AWS accounts. The security team insists on preventing the 'confused deputy' problem so that another client of the SaaS vendor cannot use the vendor's role to access the company's AWS resources. Which solution meets these requirements with the LEAST administrative effort?",
        "options": {
            "A": "Create an IAM user in each account with read-only permissions, generate access keys, and encrypt the keys with AWS KMS before sharing them with the SaaS vendor.",
            "B": "Create a cross-account IAM role in each account that trusts the SaaS vendor's AWS account ID, and require an External ID condition in the role trust policy provided by the vendor.",
            "C": "Create an AWS Site-to-Site VPN between each VPC and the SaaS provider's data center and route all monitoring API calls privately.",
            "D": "Create an IAM role in the management account only, attach the AdministratorAccess policy, and generate temporary STS credentials valid for 36 hours."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["B"],
        "explanation": "### ✅ Why Option B is Correct\n\n* **External ID for confused deputy prevention:** When delegating access to a third party (multi-tenant SaaS vendor), the IAM trust policy must require `sts:ExternalId`. The vendor generates a unique external ID per client, preventing one client from tricking the vendor into accessing another client's AWS resources.\n* **Role-based cross-account access:** Using IAM roles avoids distributing long-term IAM credentials (access keys).\n* **Least privilege:** Read-only policies can be attached directly to the assumed role in each target account.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option A is incorrect:** Distributing long-term IAM access keys to third parties violates AWS security best practices and increases credential leakage risks.\n* **Option C is incorrect:** AWS CloudWatch and EC2 describe APIs are AWS public/regional API endpoints, not private on-premises services; a Site-to-Site VPN is unnecessary and adds high operational complexity.\n* **Option D is incorrect:** AdministratorAccess violates the principle of least privilege, and STS tokens cannot exceed 12 hours for role assumption (or 36 hours is invalid for cross-account assume-role chains).\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Confused deputy problem:** Always look for **External ID** (`sts:ExternalId`) in the IAM role trust policy when third parties or multi-tenant SaaS solutions assume roles in your account.\n2. **Cross-account access:** Prefer IAM roles (`sts:AssumeRole`) over IAM users and access keys for cross-account third-party integrations."
    },
    # Task 1.1 - Question 2 (Single)
    {
        "domain": 1,
        "task": "1.1",
        "topics": ["IAM", "Permissions boundaries", "Privilege escalation"],
        "prompt": "A company wants to delegate IAM permissions to development team leads so they can create IAM roles for new AWS Lambda functions and Amazon EC2 instances. However, the security team requires that team leads cannot grant permissions exceeding a predefined security baseline, and cannot grant themselves or their created roles full administrator rights. Which solution should a solutions architect recommend?",
        "options": {
            "A": "Attach an IAM permissions boundary to the team leads' IAM policies and require that any role created by the team leads must also have this permissions boundary attached.",
            "B": "Create an AWS Organizations Service Control Policy (SCP) that restricts IAM policy modification to the root user only.",
            "C": "Configure an AWS Config rule to automatically delete any IAM role that contains the AdministratorAccess policy within 5 minutes of creation.",
            "D": "Use IAM session policies attached to the EC2 instance metadata service to limit runtime execution privileges."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Permissions boundaries prevent privilege escalation:** An IAM permissions boundary sets the maximum allowable permissions that an IAM entity (user or role) can have. \n* **Enforcing boundary on created roles:** By including a condition in the team lead's policy requiring `iam:PermissionsBoundary` on `iam:CreateRole` and `iam:PutRolePermissionsBoundary`, the team lead can create roles for Lambda/EC2, but cannot grant those roles more permissions than the boundary allows, nor bypass the boundary.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Restricting IAM policy modifications to root prevents team leads from creating any roles at all, blocking their development workflow.\n* **Option C is incorrect:** Reactive deletion via AWS Config creates a vulnerability window where elevated privileges are active before remediation occurs, and does not stop non-admin but over-permissive policies.\n* **Option D is incorrect:** Instance metadata service (IMDS) does not enforce IAM role creation boundaries for Lambda developers.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Permissions boundaries:** Ideal for delegating role/user creation to developers without risking privilege escalation.\n2. **Effective permissions:** An entity's effective permissions are the intersection of its identity-based policy and its permissions boundary."
    },
    # Task 1.1 - Question 3 (Single)
    {
        "domain": 1,
        "task": "1.1",
        "topics": ["IAM", "ABAC", "Tag-based access control"],
        "prompt": "An enterprise has hundreds of project teams sharing several AWS accounts. As new projects launch weekly, managing individual IAM policies for each project's Amazon S3 buckets and Amazon EC2 instances has become unmanageable. The security team wants to implement an authorization strategy where access is automatically granted when an engineer's department tag matches the project tag on the resource, without updating IAM policies for every new project. Which strategy meets these requirements?",
        "options": {
            "A": "Role-Based Access Control (RBAC) with unique IAM roles created for every individual project and department.",
            "B": "Attribute-Based Access Control (ABAC) using IAM policies that compare 'aws:PrincipalTag/Department' with 'aws:ResourceTag/Department'.",
            "C": "AWS Systems Manager Session Manager with AWS KMS key sharing across departmental accounts.",
            "D": "AWS Directory Service Simple AD groups mapped directly to Amazon S3 bucket access control lists (ACLs)."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["B"],
        "explanation": "### ✅ Why Option B is Correct\n\n* **ABAC reduces policy sprawl:** Attribute-Based Access Control (ABAC) uses tags on IAM principals (users/roles) and tags on AWS resources. A single generic policy granting access when `${aws:PrincipalTag/Department}` matches `${aws:ResourceTag/Department}` automatically scales to new projects without modifying IAM policies.\n* **Zero operational overhead on new projects:** When a new project is created, simply tagging its resources allows matching engineers immediate access based on their principal tags.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option A is incorrect:** RBAC requires creating and maintaining new IAM roles and policies for every new project, which causes policy explosion and administrative overhead.\n* **Option C is incorrect:** Systems Manager Session Manager is for instance shell access, not general S3/EC2 authorization policy scaling.\n* **Option D is incorrect:** S3 ACLs are legacy, do not support fine-grained ABAC tag comparisons, and AWS recommends disabling ACLs (Bucket Owner Enforced).\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **ABAC vs RBAC:** Choose ABAC when requirements mention scaling permissions without rewriting policies, or matching user tags to resource tags (`aws:PrincipalTag` vs `aws:ResourceTag`).\n2. **ABAC prerequisite:** Requires consistent tag governance and enforcement using SCP tag policies or AWS Config rules."
    },
    # Task 1.1 - Question 4 (Single)
    {
        "domain": 1,
        "task": "1.1",
        "topics": ["IAM Roles Anywhere", "Hybrid cloud", "PKI"],
        "prompt": "A company has legacy servers running on-premises that need to securely upload transaction logs directly to an Amazon S3 bucket every hour. Company security policy strictly forbids storing long-term AWS credentials (IAM access keys) on on-premises disks. The company already operates an internal Public Key Infrastructure (PKI) with an active Certificate Authority (CA). Which solution meets these requirements with the HIGHEST security posture?",
        "options": {
            "A": "Use AWS IAM Roles Anywhere, establishing a trust anchor with the on-premises CA, and have on-premises servers obtain temporary AWS STS credentials using their X.509 certificates.",
            "B": "Configure an AWS Direct Connect connection with a public virtual interface (VIF) and configure IAM basic authentication over the dedicated circuit.",
            "C": "Store IAM user secret access keys in an on-premises hardware security module (HSM) and query them via local cron jobs.",
            "D": "Create an Amazon Cognito user pool, create an IAM user for each server, and exchange passwords for JWT tokens hourly."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **IAM Roles Anywhere:** Allows workloads outside AWS (such as on-premises servers or other cloud environments) to use X.509 digital certificates from your existing PKI to obtain temporary, scoped AWS credentials from AWS STS.\n* **No long-term credentials:** Eliminates the security risk of hardcoded or stored AWS access keys and secret keys on on-premises servers.\n* **Seamless integration:** Reuses existing internal enterprise Certificate Authorities as IAM Roles Anywhere trust anchors.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Direct Connect provides private network transport; it does not replace IAM authentication and there is no 'IAM basic authentication' mechanism.\n* **Option C is incorrect:** Using IAM user access keys still relies on long-term credentials, violating the company's explicit security policy.\n* **Option D is incorrect:** Cognito user pools are designed for end-user app authentication (web/mobile users), not server-to-S3 infrastructure batch uploads.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **On-premises workloads needing temporary AWS credentials:** Choose **AWS IAM Roles Anywhere** when PKI / X.509 certificates are mentioned.\n2. **Credential hygiene:** Always eliminate long-term IAM access keys in favor of short-term temporary credentials issued by AWS STS."
    },
    # Task 1.1 - Question 5 (Multi 2 of 5)
    {
        "domain": 1,
        "task": "1.1",
        "topics": ["AWS Organizations", "Resource Control Policies", "Service Control Policies"],
        "prompt": "A financial enterprise uses AWS Organizations with multiple organizational units (OUs). The CISO wants to enforce strict organizational data perimeter boundaries. Specifically, the enterprise must ensure that: (1) member accounts cannot make AWS API calls to services outside approved AWS Regions, and (2) resources within member accounts (such as S3 buckets and KMS keys) can only be accessed by principals that belong to the organization. Which combination of AWS Organizations policy types meets these requirements? (Select TWO.)",
        "options": {
            "A": "Apply a Service Control Policy (SCP) with a Deny effect on all actions where the 'aws:RequestedRegion' condition is not in the approved Regions list.",
            "B": "Apply a Tag Policy to enforce 'Region=Approved' tags on all EC2 instances and VPCs.",
            "C": "Apply a Resource Control Policy (RCP) that restricts resource access to principals belonging to 'aws:PrincipalOrgID'.",
            "D": "Attach an IAM permissions boundary to all IAM roles denying calls outside approved regions.",
            "E": "Configure an AWS Backup policy across the root OU to replicate S3 buckets to approved regions."
        },
        "isMulti": True,
        "requiredCount": 2,
        "correctAnswers": ["A", "C"],
        "explanation": "### ✅ Why Options A & C are Correct\n\n* **Service Control Policies (SCPs) for Region restriction (A):** SCPs act as guardrails on IAM principals across member accounts. A standard SCP denying actions where `aws:RequestedRegion` is not in approved Regions prevents principals from creating or accessing resources in unapproved regions.\n* **Resource Control Policies (RCPs) for data perimeter (C):** Resource Control Policies (RCPs) are an AWS Organizations policy type that acts as a central guardrail on resource-based policies (such as S3 buckets, SQS queues, and KMS keys). Using an RCP with `aws:PrincipalOrgID` guarantees that resources in member accounts cannot grant access to external principals.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Tag policies enforce compliance on tag keys and values; they do not block API calls to unapproved AWS Regions.\n* **Option D is incorrect:** Permissions boundaries must be attached individually to every IAM user/role in every account, creating immense operational overhead and offering no central enforcement across new accounts.\n* **Option E is incorrect:** AWS Backup policies manage backup schedules and vaults; they do not enforce regional API restrictions or data perimeter controls.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **SCPs vs RCPs:** SCPs restrict what *principals* (IAM users/roles) can do in member accounts. RCPs restrict what *resources* (S3 buckets, KMS keys) can be accessed by in member accounts.\n2. **Data perimeter controls:** Combine SCPs (restrict outbound access to authorized orgs/regions) and RCPs (restrict inbound resource access to authorized principals)."
    },
    # Task 1.1 - Question 6 (Single)
    {
        "domain": 1,
        "task": "1.1",
        "topics": ["IAM", "AWS IAM Identity Center", "Multi-account access"],
        "prompt": "A global company has migrated to a multi-account AWS environment managed by AWS Organizations. Employees currently authenticate against an on-premises Microsoft Active Directory. The company wants to implement single sign-on (SSO) so that administrators can access all AWS accounts and business applications using their corporate credentials, while supporting multi-factor authentication (MFA) and central session logging. Which solution meets these requirements with the LEAST operational overhead?",
        "options": {
            "A": "Deploy AWS IAM Identity Center (AWS Single Sign-On), connect it to the corporate Active Directory using AWS Directory Service AD Connector, and assign permission sets to AD groups across target AWS accounts.",
            "B": "Deploy Amazon Cognito user pools in each individual AWS account and federate each user pool with on-premises Active Directory using SAML 2.0.",
            "C": "Create IAM users with matching usernames in each AWS account, configure Active Directory Federation Services (ADFS), and write custom scripts to synchronize passwords.",
            "D": "Create an AWS CloudHSM cluster in the management account to store Active Directory user passwords and issue temporary STS tokens."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **AWS IAM Identity Center:** The AWS-recommended service for centrally managing single sign-on access across all accounts in an AWS Organization and business applications.\n* **AD Connector integration:** Connects IAM Identity Center directly to existing on-premises Microsoft Active Directory without replicating directory data to the cloud.\n* **Permission sets:** Permissions are centrally defined as permission sets and assigned to AD security groups for specific AWS accounts, minimizing administrative overhead.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Amazon Cognito user pools are built for customer-facing web and mobile applications, not for workforce multi-account administrative access.\n* **Option C is incorrect:** Creating IAM users in every account requires massive maintenance, password synchronization scripts, and violates multi-account federation best practices.\n* **Option D is incorrect:** CloudHSM is a dedicated hardware cryptographic module for key storage; it cannot validate Active Directory passwords or issue STS tokens.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Workforce single sign-on across multi-account AWS Organizations:** Always choose **AWS IAM Identity Center** (successor to AWS SSO).\n2. **Directory integration:** Use **AD Connector** to proxy authentication to on-premises AD without directory synchronization, or **AWS Managed Microsoft AD** if a managed AD is needed in the cloud."
    },
    # Task 1.1 - Question 7 (Single)
    {
        "domain": 1,
        "task": "1.1",
        "topics": ["IAM", "Condition keys", "Network security"],
        "prompt": "A company wants to ensure that developers can only access AWS Management Console and execute AWS CLI commands against their development accounts when connected to the corporate office network (CIDR 198.51.100.0/24) or corporate VPN (CIDR 203.0.113.0/24). If a request originates from any other IP address, access must be immediately denied, even if other policies allow it. Which policy configuration should the solutions architect implement?",
        "options": {
            "A": "Create an IAM policy with an Effect of Deny, Action of '*', and a Condition with 'NotIpAddress' for 'aws:SourceIp' specifying the corporate CIDR ranges, and attach it to the developers' IAM group.",
            "B": "Configure an AWS WAF Web ACL on all VPC Internet Gateways to block IP addresses outside the corporate CIDRs.",
            "C": "Add an inbound rule to the default security group of every VPC allowing traffic only from 198.51.100.0/24 and 203.0.113.0/24.",
            "D": "Create an Amazon Route 53 Resolver DNS firewall rule that rejects DNS queries originating outside corporate subnets."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Explicit Deny with NotIpAddress:** In AWS IAM policy evaluation, an explicit Deny always overrides any Allow. Using `Effect: Deny`, `Action: *`, `Condition: {\"NotIpAddress\": {\"aws:SourceIp\": [\"198.51.100.0/24\", \"203.0.113.0/24\"]}}` immediately blocks any request originating from outside those IP ranges.\n* **Comprehensive enforcement:** Enforces IP restrictions at the IAM authorization layer for both AWS Console and AWS CLI/API operations.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** AWS WAF inspects HTTP/HTTPS traffic to Application Load Balancers, CloudFront, API Gateway, and AppSync; it cannot attach to VPC Internet Gateways or protect the AWS Management Console.\n* **Option C is incorrect:** Security groups control network packets to EC2/VPC network interfaces; they do not govern IAM control plane API calls or AWS Management Console access.\n* **Option D is incorrect:** Route 53 Resolver DNS Firewall inspects outbound DNS queries from within VPCs, not inbound public management API access.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Enforce corporate network access:** Use an IAM policy with `Effect: Deny` and condition `NotIpAddress: {\"aws:SourceIp\": [...]}`.\n2. **Be cautious with aws:SourceIp:** When calling AWS services that call other services on your behalf (service-to-service calls), `aws:SourceIp` can block the downstream service unless `aws:ViaAWSService` is handled."
    },
    # Task 1.2 - Question 8 (Single)
    {
        "domain": 1,
        "task": "1.2",
        "topics": ["AWS WAF", "Application Load Balancer", "DDoS", "Rate limiting"],
        "prompt": "An e-commerce website hosted on Amazon EC2 instances behind an Application Load Balancer (ALB) is experiencing HTTP flood attacks against its login endpoint (`/api/login`), causing database CPU spikes and service degradation. The security team wants to automatically block IP addresses that send more than 2,000 requests per 5-minute period to the login endpoint, while inspecting request bodies for common SQL injection attempts across the entire website. Which solution meets these requirements with the MINIMAL operational overhead?",
        "options": {
            "A": "Deploy AWS WAF associated with the ALB. Create a rate-based rule evaluated on the URI path '/api/login' with a limit of 2,000 requests per 5 minutes, and add the AWS-managed rule group 'AWSManagedRulesSQLiRuleSet'.",
            "B": "Write a custom AWS Lambda function that parses ALB access logs in S3 every 5 minutes and updates ALB security group rules to deny offending IP addresses.",
            "C": "Deploy AWS Network Firewall in front of the ALB and write Suricata rules to track HTTP request counts and regex match SQL injection strings.",
            "D": "Enable Amazon GuardDuty and configure automated remediation via EventBridge and Lambda to terminate EC2 instances under high load."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **AWS WAF Rate-based rules:** Specifically designed to track request rates from individual IP addresses over 5-minute (or 1-minute / 2-minute) windows. Scoping down the rate-based rule to the specific URI path `/api/login` protects the login endpoint from brute-force/HTTP floods.\n* **AWS Managed Rules:** The `AWSManagedRulesSQLiRuleSet` is maintained by AWS threat research and automatically inspects incoming web requests for SQL injection patterns with zero operational management.\n* **Direct ALB integration:** AWS WAF inspects traffic directly at the ALB layer before requests hit backend EC2 instances or the database.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Parsing ALB access logs asynchronously in S3 incurs a multi-minute delay, consumes compute, and security group rule limits (60 rules per SG by default) make IP blocking unscalable.\n* **Option C is incorrect:** AWS Network Firewall is a Layer 3-7 network firewall; while it supports Suricata rules, parsing HTTP URIs and application-layer SQL injection is far more complex and costly than AWS WAF.\n* **Option D is incorrect:** Terminating EC2 instances during high load achieves the attacker's denial-of-service goal and does not mitigate the attack.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Protect web applications (ALB/CloudFront/API Gateway):** Use **AWS WAF** with rate-based rules for HTTP floods/login protection, and AWS Managed Rules (Core Rule Set, SQLi, Known Bad Inputs).\n2. **Rate-based rule scoping:** Can be scoped using statement conditions (e.g. only apply rate limit when URI path matches `/login`)."
    },
    # Task 1.2 - Question 9 (Single)
    {
        "domain": 1,
        "task": "1.2",
        "topics": ["Amazon VPC", "Transit Gateway", "AWS Network Firewall", "Inspection VPC"],
        "prompt": "An enterprise has 40 VPCs connected via an AWS Transit Gateway. Security compliance mandates that all outbound traffic destined for the public internet from any workload VPC must pass through an intrusion detection and prevention system (IDS/IPS) for deep packet inspection and URL domain filtering. The architecture must be centralized and scale without configuring individual NAT gateways in all 40 VPCs. Which architecture should a solutions architect recommend?",
        "options": {
            "A": "Deploy an Inspection VPC with an AWS Network Firewall endpoint and NAT Gateways across multiple AZs. Route outbound 0.0.0.0/0 traffic from spoke VPC route tables through the Transit Gateway to the Inspection VPC.",
            "B": "Deploy an Internet Gateway in each spoke VPC and attach AWS WAF Web ACLs directly to the Internet Gateways.",
            "C": "Create VPC peering connections between all 40 VPCs in a full mesh and deploy squid proxy instances on EC2 in each VPC.",
            "D": "Enable Amazon GuardDuty and configure an egress VPC endpoint for GuardDuty in every spoke VPC."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Centralized Inspection VPC with Transit Gateway:** The standard enterprise hub-and-spoke architecture. Workload (spoke) VPCs route default outbound traffic (`0.0.0.0/0`) to the Transit Gateway, which routes traffic to an Inspection VPC.\n* **AWS Network Firewall:** Deployed in the Inspection VPC across multiple Availability Zones, providing stateful deep packet inspection, IDS/IPS, and stateful domain name filtering.\n* **Cost and operational efficiency:** Centralizes NAT Gateways and firewall endpoints in one VPC rather than provisioning NAT gateways in 40 separate VPCs.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** AWS WAF cannot attach directly to VPC Internet Gateways (it attaches to ALB, API Gateway, CloudFront, Cognito, and AppSync).\n* **Option C is incorrect:** A full mesh VPC peering across 40 VPCs requires 780 peering connections (`N*(N-1)/2`), which exceeds peering limits and adds severe administrative complexity.\n* **Option D is incorrect:** GuardDuty is a detective threat detection service; it is not an inline proxy or deep packet inspection firewall.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Centralized egress / inspection architecture:** Transit Gateway + Central Inspection VPC with **AWS Network Firewall** and NAT Gateways.\n2. **Appliance Mode:** Enable **Transit Gateway Appliance Mode** on the inspection VPC attachment to ensure symmetric bidirectional traffic routing through the same AZ firewall endpoint."
    },
    # Task 1.2 - Question 10 (Multi 2 of 5)
    {
        "domain": 1,
        "task": "1.2",
        "topics": ["Amazon Cognito", "Amazon S3", "Mobile authentication"],
        "prompt": "A company is building a consumer photo-sharing mobile application. Hundreds of thousands of users will sign up, authenticate using Apple ID, Google, or email/password, and upload photos directly to Amazon S3. The architecture must ensure that users can only upload photos to their own dedicated folder in the S3 bucket (`photos/{user_id}/*`), without passing photo binaries through application web servers or exposing long-term AWS credentials in the mobile app. Which combination of services and configurations should a solutions architect choose? (Select TWO.)",
        "options": {
            "A": "Use Amazon Cognito User Pools for user registration, directory management, and social identity provider federation.",
            "B": "Use Amazon Cognito Identity Pools (Federated Identities) to exchange User Pool tokens for temporary AWS STS credentials.",
            "C": "Create an IAM user for each registered mobile user and store their secret access keys in the mobile app's secure enclave.",
            "D": "Attach an IAM policy to the authenticated Cognito role using '${cognito-identity.amazonaws.com:sub}' in the S3 resource ARN to restrict folder access.",
            "E": "Deploy an Application Load Balancer with basic HTTP authentication to proxy all image uploads directly to S3."
        },
        "isMulti": True,
        "requiredCount": 2,
        "correctAnswers": ["A", "D"],
        "explanation": "### ✅ Why Options A & D are Correct\n\n* **Cognito User Pools (A):** Provides identity management, user sign-up, sign-in, MFA, and federation with external social identity providers (Apple, Google, Facebook).\n* **IAM policy variable with sub (D):** By using Amazon Cognito Identity Pools together with User Pools, authenticated users assume an IAM role. The role's IAM policy uses policy variables: `arn:aws:s3:::mybucket/photos/${cognito-identity.amazonaws.com:sub}/*`, ensuring that each user can only read/write to their own folder matching their unique Cognito identity ID.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is partially descriptive but does not solve the fine-grained S3 authorization requirement:** While Identity Pools are involved, Option D specifically details the required folder-level authorization mechanism, and Option A provides the required user registration and social federation.\n* **Option C is incorrect:** Creating IAM users for external mobile users is an anti-pattern that hits IAM service quotas (5,000 IAM users per account) and poses severe credential leakage risks.\n* **Option E is incorrect:** Passing uploads through an ALB introduces unnecessary compute overhead and costs, whereas uploading directly to S3 via temporary credentials or presigned URLs is serverless and scalable.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **User Pools vs Identity Pools:** User Pools = Authentication (user directory, tokens). Identity Pools = Authorization (exchanging tokens for temporary AWS IAM credentials).\n2. **Fine-grained S3 user folder isolation:** Use IAM policy variable `${cognito-identity.amazonaws.com:sub}` in the S3 resource ARN."
    },
    # Task 1.2 - Question 11 (Single)
    {
        "domain": 1,
        "task": "1.2",
        "topics": ["Amazon Inspector", "Amazon ECR", "AWS Lambda", "Vulnerability management"],
        "prompt": "A software company deploys containerized microservices to Amazon Elastic Container Service (Amazon ECS) with AWS Fargate, and serverless backend functions on AWS Lambda. The security team requires continuous, automated vulnerability scanning for software dependencies, CVE vulnerabilities, and unintended network exposure across all container images stored in Amazon Elastic Container Registry (Amazon ECR) and all active Lambda functions. The solution must provide finding summaries without deploying third-party agent software. Which solution meets these requirements?",
        "options": {
            "A": "Enable Amazon Inspector in the AWS Organizations management account and activate scanning for Amazon ECR and AWS Lambda standard and code scanning.",
            "B": "Deploy an Amazon EC2 instance running open-source ClamAV, and configure a daily cron job to pull container images from ECR and scan them.",
            "C": "Configure AWS CloudTrail insights to analyze container execution logs and trigger alarms on suspicious API invocations.",
            "D": "Use AWS Trusted Advisor security checks to inspect Lambda source code and ECR repository contents."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Amazon Inspector:** The native automated vulnerability management service in AWS that continuously scans Amazon EC2 instances, container images in Amazon ECR, and AWS Lambda functions for software vulnerabilities and unintended network exposure.\n* **Agentless for ECR and Lambda:** Inspector automatically scans ECR container images on push and continuously re-scans when new CVEs are published, without requiring any installed agent.\n* **Multi-account centralization:** Inspector integrates with AWS Organizations to centrally delegate administration and aggregate findings across all member accounts.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Deploying custom EC2 scanning instances with ClamAV creates high operational maintenance, does not scan Lambda functions, and is not a managed AWS solution.\n* **Option C is incorrect:** CloudTrail Insights detects unusual management API activity (e.g. sudden spike in console logins), not software CVE package vulnerabilities.\n* **Option D is incorrect:** Trusted Advisor checks account configuration best practices (e.g. S3 public access, MFA on root), not deep container CVEs or Lambda application code vulnerabilities.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Vulnerability scanning for EC2, ECR, and Lambda:** Choose **Amazon Inspector**.\n2. **Inspector vs GuardDuty:** Inspector scans for known vulnerabilities (CVEs) and exposure before/during runtime. GuardDuty detects malicious behavior and active threats during runtime using machine learning."
    },
    # Task 1.2 - Question 12 (Single)
    {
        "domain": 1,
        "task": "1.2",
        "topics": ["Amazon VPC", "VPC Endpoints", "Endpoint Policies", "Data exfiltration"],
        "prompt": "A company's proprietary data processing application runs on Amazon EC2 instances inside private subnets. The instances need to download large training datasets from an Amazon S3 bucket named 'corporate-datasets' and upload processed results to 'corporate-results'. The security team wants to prevent malicious actors or rogue scripts on the EC2 instances from exfiltrating data to external, unauthorized personal S3 buckets. Which solution meets these requirements with the LEAST cost and complexity?",
        "options": {
            "A": "Create an S3 Gateway VPC Endpoint in the VPC. Attach an Endpoint Policy to the Gateway Endpoint that grants 's3:GetObject' and 's3:PutObject' actions only on the 'corporate-datasets' and 'corporate-results' bucket ARNs.",
            "B": "Route all outbound S3 traffic through a NAT Gateway to the public internet, and use security groups to block all TCP ports except port 443.",
            "C": "Deploy an AWS Site-to-Site VPN to route S3 requests to an on-premises proxy server that performs SSL decryption.",
            "D": "Enable S3 Block Public Access on all S3 buckets in the AWS account."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **VPC Endpoint Policies prevent data exfiltration:** An S3 Gateway VPC Endpoint allows private traffic to S3 without internet access or NAT gateways (and has no hourly or data transfer cost). Attaching an **Endpoint Policy** to the VPC endpoint explicitly restricts which S3 resources can be accessed through that endpoint, preventing access to external or personal buckets.\n* **Zero data transfer cost:** S3 Gateway Endpoints are completely free of charge.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Security groups operate at Layer 4 (IP/port) and cannot inspect HTTP/S3 bucket destination host headers; traffic over port 443 would allow uploads to any S3 bucket on the internet, and NAT Gateways incur hourly and data processing fees.\n* **Option C is incorrect:** Routing cloud traffic back to an on-premises proxy introduces significant latency, egress bandwidth costs, and architectural complexity.\n* **Option D is incorrect:** S3 Block Public Access prevents public internet users from reading your bucket; it does not stop instances from uploading data to an external personal bucket.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **VPC Endpoint Policies:** Use endpoint policies on VPC endpoints to enforce least-privilege resource access and prevent data exfiltration.\n2. **Gateway Endpoints:** Gateway endpoints exist for **Amazon S3** and **Amazon DynamoDB**. They are route table entries and have no hourly or data transfer charges."
    },
    # Task 1.2 - Question 13 (Single)
    {
        "domain": 1,
        "task": "1.2",
        "topics": ["Amazon GuardDuty", "EventBridge", "Automated remediation"],
        "prompt": "A company uses Amazon GuardDuty across its AWS Organization. Security operations wants to automatically isolate any Amazon EC2 instance that generates a GuardDuty finding indicating compromised credentials or active command-and-control communication (e.g. 'Backdoor:EC2/C&CActivity.B!DNS'). The solution must isolate the affected instance from the network immediately and notify the on-call security engineer. Which architecture achieves this?",
        "options": {
            "A": "Create an Amazon EventBridge rule that matches GuardDuty findings. Set the target to an AWS Lambda function that changes the instance's security group to an isolation security group with no inbound or outbound rules, and sends an alert to an Amazon SNS topic.",
            "B": "Configure Amazon GuardDuty to directly terminate offending EC2 instances and write an email to the root account contact.",
            "C": "Create an Amazon CloudWatch billing alarm that triggers an EC2 Auto Scaling action to scale down the instance group.",
            "D": "Write an AWS Systems Manager Automation document that runs every 24 hours to scan running instances and reboot compromised servers."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Event-driven automated remediation:** Amazon GuardDuty emits findings as events to Amazon EventBridge in near-real-time.\n* **Automated isolation via Lambda:** EventBridge triggers a Lambda function that swaps or modifies the EC2 instance's security group to an 'isolation' security group (denying all inbound and outbound traffic), preventing further lateral movement or data exfiltration while preserving memory state for forensic analysis.\n* **Instant notification:** Lambda publishes finding details to an Amazon SNS topic subscribed to by on-call engineers.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** GuardDuty is a detection service; it cannot directly terminate instances or email root contacts on its own.\n* **Option C is incorrect:** Billing alarms monitor estimated AWS charges, not real-time security threats.\n* **Option D is incorrect:** A 24-hour batch scan leaves a compromised instance running for up to a full day, creating unacceptable risk, and rebooting clears volatile forensic memory without isolating the threat.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **GuardDuty remediation pattern:** GuardDuty -> Amazon EventBridge -> AWS Lambda (or Systems Manager Automation) -> isolate/remediate + SNS notification.\n2. **Forensics preservation:** Prefer isolating instances (changing security group) over terminating them, so security analysts can inspect EBS snapshots and RAM."
    },
    # Task 1.2 - Question 14 (Single)
    {
        "domain": 1,
        "task": "1.2",
        "topics": ["Amazon Cognito", "AWS AppSync", "API security"],
        "prompt": "A healthcare startup is building a GraphQL backend using AWS AppSync for a patient management web application. Patients and medical staff will access the system. Patients must only query their own health records, while medical staff with valid organizational credentials must have elevated query privileges based on their group membership. The architecture must enforce fine-grained authentication and authorization at the GraphQL resolver level. Which solution meets these requirements with the LEAST operational overhead?",
        "options": {
            "A": "Integrate Amazon Cognito User Pools with AWS AppSync, define groups for 'Patients' and 'MedicalStaff', and use GraphQL schema `@aws_auth` directives and resolver authorization logic to enforce field-level access.",
            "B": "Place an Application Load Balancer in front of AWS AppSync with custom Apache basic auth plugins.",
            "C": "Configure an AWS Lambda authorizer that connects directly to an unencrypted MySQL database table storing plaintext user credentials.",
            "D": "Deploy an EC2 reverse proxy running NGINX with Lua scripts to parse and validate incoming GraphQL queries before forwarding to AppSync."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Native AppSync + Cognito integration:** AWS AppSync has built-in integration with Amazon Cognito User Pools as an authorization provider.\n* **Fine-grained GraphQL authorization:** Using Cognito groups ('Patients', 'MedicalStaff') combined with GraphQL schema directives (`@aws_auth`) allows fine-grained, field-level and type-level access control with zero server management.\n* **Resolver context:** Resolvers can inspect `$context.identity.claims` or `$context.identity.username` to restrict patient queries to their own specific user ID.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** ALB cannot front AWS AppSync in this manner, and basic HTTP authentication is insecure and does not provide fine-grained GraphQL field-level authorization.\n* **Option C is incorrect:** Storing plaintext credentials in an unencrypted MySQL database violates basic security best practices and HIPAA compliance standards.\n* **Option D is incorrect:** Deploying self-managed NGINX EC2 proxies adds significant operational maintenance, patching overhead, and defeats the purpose of managed AppSync.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **AppSync security:** Supports API keys (public/dev only), IAM, OpenID Connect (OIDC), and Amazon Cognito User Pools.\n2. **Fine-grained control in AppSync:** Use Cognito User Pools with Cognito groups and resolver mapping templates/JavaScript resolvers."
    },
    # Task 1.3 - Question 15 (Single)
    {
        "domain": 1,
        "task": "1.3",
        "topics": ["AWS KMS", "Multi-Region keys", "Cross-region disaster recovery"],
        "prompt": "A company operates an active-passive disaster recovery architecture across two AWS Regions: us-east-1 (primary) and us-west-2 (secondary). Data stored in Amazon S3 and Amazon Aurora PostgreSQL is encrypted using customer-managed AWS KMS keys. In the event of a regional disaster in us-east-1, the application in us-west-2 must be able to decrypt replicated data and resume operations immediately without re-encrypting datasets or decrypting and moving key material across the internet. Which KMS key architecture should a solutions architect recommend?",
        "options": {
            "A": "Create a multi-Region primary KMS key in us-east-1, replicate it to us-west-2 as a multi-Region replica key, and use the replica key to decrypt the replicated data in us-west-2.",
            "B": "Create independent single-Region KMS keys in us-east-1 and us-west-2, and export the private key from us-east-1 using the AWS Management Console to import into us-west-2.",
            "C": "Use the AWS managed key 'aws/s3' in us-east-1 and grant the us-west-2 IAM roles access to the us-east-1 key via an IAM policy.",
            "D": "Create an AWS CloudHSM cluster spanning both Regions with VPC peering to share cryptographic keys."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **KMS Multi-Region keys:** AWS KMS multi-Region keys (MRKs) are customer managed keys in different AWS Regions that have the same key material, key ID, and ARN prefix, but are managed independently for regional access policies.\n* **Seamless cross-Region decryption:** Ciphertext encrypted under a primary multi-Region key in us-east-1 can be decrypted directly by the replica key in us-west-2 without any re-encryption or cross-Region network calls to KMS.\n* **Zero key exposure:** AWS KMS handles the secure synchronization of key material inside the AWS KMS hardware security modules.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** AWS KMS does not allow exporting the private key material of KMS keys generated by KMS.\n* **Option C is incorrect:** AWS managed keys (`aws/s3`) are single-Region only, cannot be shared across accounts or Regions, and their key policies cannot be modified.\n* **Option D is incorrect:** CloudHSM clusters cannot span across multiple AWS Regions; each cluster is bound to a single VPC in a single Region.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **KMS Multi-Region keys:** Choose multi-Region keys when data is replicated across Regions (e.g. S3 CRR, Aurora Global Databases, DynamoDB global tables) and needs to be decrypted locally in the target Region.\n2. **Key ID compatibility:** Multi-Region keys share the same key ID and key material, but have Region-specific ARNs and key policies."
    },
    # Task 1.3 - Question 16 (Single)
    {
        "domain": 1,
        "task": "1.3",
        "topics": ["Amazon S3", "S3 Object Lock", "Compliance", "Immutability"],
        "prompt": "A multinational banking institution must store transaction ledger files in Amazon S3 for exactly 7 years to comply with SEC Rule 17a-4 and FINRA regulatory mandates. The regulation strictly dictates that under no circumstances—including compromised administrator credentials or actions by the AWS root account—can the files be deleted, overwritten, or have their retention period shortened during the 7-year timeframe. Which S3 configuration satisfies these legal requirements?",
        "options": {
            "A": "Enable S3 Versioning, create an S3 Lifecycle policy to transition objects to S3 Glacier Flexible Retrieval after 1 day, and enable MFA Delete on the bucket.",
            "B": "Enable S3 Object Lock in Compliance mode with a default retention period of 7 years on the bucket.",
            "C": "Enable S3 Object Lock in Governance mode with a retention period of 7 years, and attach an SCP denying 's3:DeleteObject'.",
            "D": "Enable S3 Server-Side Encryption with Customer-Provided Keys (SSE-C) and delete the encryption key after writing."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["B"],
        "explanation": "### ✅ Why Option B is Correct\n\n* **S3 Object Lock Compliance Mode:** In Compliance mode, a protected object version cannot be overwritten or deleted by any user, including the root user in the AWS account. Its retention period cannot be shortened, and its compliance mode cannot be changed.\n* **Regulatory compliance:** Specifically meets stringent financial standards like SEC Rule 17a-4(f), FINRA Rule 4511, and CFTC 1.31.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option A is incorrect:** MFA Delete requires root credentials to permanently delete an object version, but the root user could still delete it or turn off MFA Delete.\n* **Option C is incorrect (Governance Mode):** In Governance mode, users with the `s3:BypassGovernanceRetention` permission (such as administrators or root) can still delete objects or alter retention settings.\n* **Option D is incorrect:** Deleting encryption keys renders the data permanently unreadable and unrecoverable, which violates the requirement to preserve and store the records for 7 years.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **S3 Object Lock modes:**\n   - **Compliance Mode:** No one can overwrite/delete, not even root. Retention cannot be reduced.\n   - **Governance Mode:** Privileged users with special IAM permissions can override/delete.\n2. **Prerequisites:** S3 Object Lock requires **S3 Versioning** enabled at bucket creation."
    },
    # Task 1.3 - Question 17 (Single)
    {
        "domain": 1,
        "task": "1.3",
        "topics": ["AWS Secrets Manager", "Amazon RDS", "Credential rotation"],
        "prompt": "A company stores production database credentials in AWS Secrets Manager for an Amazon RDS for MySQL database accessed by hundreds of microservice containers. To satisfy compliance requirements, the database passwords must be automatically rotated every 30 days. The rotation must not cause application connection failures or downtime when the password changes. Which rotation strategy should a solutions architect configure?",
        "options": {
            "A": "Configure automatic rotation in Secrets Manager using the multi-user rotation strategy, where Secrets Manager uses a separate superuser credential to rotate the application user's password.",
            "B": "Configure single-user rotation in Secrets Manager with a 1-second maintenance window and reboot the RDS instance after rotation.",
            "C": "Create an Amazon EventBridge Scheduler rule that invokes a custom Lambda function to restart all microservice containers whenever the secret updates.",
            "D": "Store the database password in AWS Systems Manager Parameter Store as a SecureString and configure manual rotation notifications via Amazon SNS."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **Multi-user rotation avoids downtime:** With multi-user rotation, Secrets Manager manages two application users (e.g., user_clone_1 and user_clone_2) using an administrative superuser account. It alternates between them: updating the inactive user's password in the database, updating the secret value, and leaving active connections on the other user uninterrupted.\n* **Zero downtime:** In-flight queries and existing application connection pools continue using the current credentials while new connections seamlessly transition to the rotated user.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Single-user rotation updates the database password immediately; any microservice container caching the previous password will experience authentication failures until it fetches the new secret, causing downtime. Rebooting RDS causes an outage.\n* **Option C is incorrect:** Restarting hundreds of containers during rotation causes application service disruption.\n* **Option D is incorrect:** Systems Manager Parameter Store does not support automated native credential rotation; rotation would be manual or require custom Lambda orchestration.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **Secrets Manager rotation strategies:**\n   - **Single-user:** Best for non-production or workloads that tolerate brief auth retry blips.\n   - **Multi-user:** Recommended for production databases to ensure seamless zero-downtime rotation.\n2. **Managed rotation Lambda:** Secrets Manager provides pre-built Lambda templates for RDS (MySQL, PostgreSQL, Oracle, SQL Server)."
    },
    # Task 1.3 - Question 18 (Single)
    {
        "domain": 1,
        "task": "1.3",
        "topics": ["AWS KMS", "Key Policy", "IAM delegation"],
        "prompt": "A security architect is configuring a customer managed key (CMK) in AWS KMS to encrypt sensitive corporate documents stored in Amazon S3. The security architect wants to allow members of the 'CloudAdmins' IAM group to administer the key (enable, disable, rotate, and change policies), but explicitly ensure that the CloudAdmins CANNOT decrypt the sensitive documents. Which configuration achieves this separation of duties?",
        "options": {
            "A": "In the KMS Key Policy, grant the CloudAdmins IAM role permissions for 'kms:Create*', 'kms:Describe*', 'kms:Enable*', 'kms:Put*', and 'kms:Update*', but omit 'kms:Decrypt' and 'kms:GenerateDataKey*'.",
            "B": "In the IAM policy attached to CloudAdmins, grant 'kms:*' and attach an S3 bucket policy denying CloudAdmins access to S3.",
            "C": "Configure an AWS Organizations SCP with 'Deny' on 'kms:Decrypt' for the entire account.",
            "D": "Use an AWS managed key instead of a customer managed key."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **KMS Key Policies enforce separation of duties:** AWS KMS controls access primarily through Key Policies. Key administrative actions (`kms:PutKeyPolicy`, `kms:ScheduleKeyDeletion`, `kms:EnableKeyRotation`, etc.) are completely distinct API operations from cryptographic operations (`kms:Decrypt`, `kms:GenerateDataKey`, `kms:Encrypt`).\n* **Omitting cryptographic actions:** By granting CloudAdmins administrative API permissions while explicitly excluding cryptographic API permissions (`kms:Decrypt`), administrators can maintain the key lifecycle without having the capability to view plaintext data.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Granting `kms:*` gives full cryptographic rights; relying on S3 bucket policies is insufficient if data can be downloaded through other mechanisms or if the admin modifies the S3 policy.\n* **Option C is incorrect:** Denying `kms:Decrypt` via SCP blocks all principals in the account, preventing the authorized application from decrypting documents.\n* **Option D is incorrect:** AWS managed keys cannot have custom access policies or separation of duties configured; permissions are fixed by AWS.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **KMS separation of duties:** Key Administrators vs Key Users. Key policies should separate management actions from cryptographic actions (`kms:Encrypt`, `kms:Decrypt`).\n2. **KMS root access:** The key policy must grant the account root user permission to avoid orphan keys, but IAM policies can then control individual principal access."
    },
    # Task 1.3 - Question 19 (Single)
    {
        "domain": 1,
        "task": "1.3",
        "topics": ["Amazon S3", "AWS KMS", "S3 Bucket Keys", "Cost optimization"],
        "prompt": "A analytics platform processes 500 million object PUT and GET requests daily on an Amazon S3 bucket. Objects are encrypted using server-side encryption with AWS KMS customer-managed keys (SSE-KMS). The finance department alerts the team that AWS KMS request costs now exceed the cost of S3 storage itself. Which solution reduces AWS KMS request costs by up to 99% with NO changes to application code?",
        "options": {
            "A": "Enable Amazon S3 Bucket Keys on the S3 bucket.",
            "B": "Switch all objects from SSE-KMS to client-side encryption using the AWS Encryption SDK on EC2 instances.",
            "C": "Change the KMS key deletion window to 7 days.",
            "D": "Create an S3 Lifecycle rule to transition objects to S3 One Zone-IA after 30 days."
        },
        "isMulti": False,
        "requiredCount": 1,
        "correctAnswers": ["A"],
        "explanation": "### ✅ Why Option A is Correct\n\n* **S3 Bucket Keys:** S3 Bucket Keys reduce AWS KMS request traffic from Amazon S3 to AWS KMS by creating a short-lived intermediate bucket key within S3. S3 uses this bucket-level key to generate data keys for new objects, reducing KMS API calls by up to 99%.\n* **Zero application changes:** S3 Bucket Keys can be enabled with a single checkbox in the S3 bucket configuration or via CloudFormation/API, requiring zero changes to client application code.\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** Implementing client-side encryption requires extensive rewriting and re-architecting of application code, adding operational burden.\n* **Option C is incorrect:** Scheduling key deletion marks the key for destruction and does not reduce ongoing request API costs.\n* **Option D is incorrect:** S3 One Zone-IA changes storage tier pricing; it does not reduce the KMS API request charges incurred on every PUT and GET.\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **High KMS costs on S3:** The answer is almost always **Amazon S3 Bucket Keys**.\n2. **KMS Request Limits:** In addition to saving money, S3 Bucket Keys prevent hitting KMS regional request tier throttling limits."
    },
    # Task 1.3 - Question 20 (Multi 3 of 6)
    {
        "domain": 1,
        "task": "1.3",
        "topics": ["AWS KMS", "Envelope encryption", "Cryptography"],
        "prompt": "A solutions architect is designing an on-premises data ingestion pipeline that encrypts 5 GB video files locally before uploading them to Amazon S3. Due to bandwidth and performance constraints, video files cannot be transmitted to AWS KMS over the network for encryption. The solution must implement envelope encryption using customer-managed AWS KMS keys. Which sequence of actions correctly implements envelope encryption? (Select THREE.)",
        "options": {
            "A": "Call the AWS KMS 'GenerateDataKey' API to obtain a plaintext Data Encryption Key (DEK) and an encrypted copy of the DEK.",
            "B": "Call the AWS KMS 'Encrypt' API and pass the entire 5 GB video file directly in the API request body.",
            "C": "Encrypt the 5 GB video file locally using the plaintext DEK and a symmetric algorithm like AES-GCM.",
            "D": "Erase the plaintext DEK from memory as soon as local encryption of the video file is complete.",
            "E": "Upload the encrypted video file along with the plaintext DEK to the S3 bucket.",
            "F": "Store the encrypted copy of the DEK alongside the encrypted video file metadata in Amazon S3."
        },
        "isMulti": True,
        "requiredCount": 3,
        "correctAnswers": ["A", "C", "D"],
        "explanation": "### ✅ Why Options A & C & D are Correct\n\n* **GenerateDataKey (A):** The application calls KMS `GenerateDataKey`, which returns both a plaintext Data Encryption Key (DEK) and a ciphertext DEK encrypted under the KMS root key.\n* **Local data encryption (C):** The client uses the plaintext DEK to encrypt large datasets locally using high-performance symmetric ciphers (e.g. AES-256-GCM).\n* **Memory hygiene (D):** Once encryption finishes, the plaintext DEK must be securely wiped from RAM to prevent compromise. The encrypted DEK is safely stored alongside the ciphertext (or in object metadata).\n\n---\n\n### ❌ Why Other Options Are Incorrect\n\n* **Option B is incorrect:** The KMS `Encrypt` API has a strict 4 KB maximum data size limit and cannot accept 5 GB files.\n* **Option E is incorrect:** Storing or transmitting the plaintext DEK defeats the entire purpose of encryption and exposes the data to compromise.\n* **Option F is a valid best practice in general, but between the core mechanics of envelope encryption (Generate DEK -> Encrypt locally -> Clear plaintext from memory), A, C, and D are the foundational sequence steps.**\n\n---\n\n### 💡 SAA-C03 Exam Concept & AWS Best Practice\n\n1. **KMS Encrypt limit:** Max payload is **4 KB**. For anything larger, use **envelope encryption** via `GenerateDataKey`.\n2. **Envelope encryption lifecycle:** GenerateDataKey -> Encrypt data with plaintext key -> Erase plaintext key from memory -> Store encrypted key with encrypted data."
    }
]
