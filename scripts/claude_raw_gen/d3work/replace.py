import json, sys
sys.argv=['x','/dev/null']
src=open('d3work/build.py').read().split('out = sys.argv[1]')[0]
ns={}; exec(src, ns); q=ns['q']
new4=q("3.2", ["Amazon EC2", "Cluster placement groups", "Elastic Fabric Adapter (EFA)"],
 "A research institute runs a tightly coupled computational fluid dynamics simulation that uses MPI across 64 Amazon EC2 instances. Nodes exchange data constantly, and job runtime is dominated by inter-node network latency. The simulation can be rerun if it fails, so high availability across Availability Zones is not required. Which deployment will provide the BEST network performance between the nodes?",
 {"A": "Launch the instances in a spread placement group across multiple Availability Zones.",
  "B": "Launch the instances in a partition placement group with each partition on separate racks.",
  "C": "Launch HPC-optimized instances that support Elastic Fabric Adapter (EFA) into a cluster placement group in a single Availability Zone, with EFA enabled.",
  "D": "Launch the instances in an Auto Scaling group across three Availability Zones behind a Network Load Balancer."},
 ["C"],
 [("Cluster placement group", "Packs instances close together inside one Availability Zone, giving the low-latency, high-bandwidth node-to-node networking that tightly coupled workloads need."),
  ("Elastic Fabric Adapter", "EFA is a network interface for EC2 that lets MPI and NCCL applications bypass the operating system kernel (OS-bypass) for lower and more consistent latency than TCP. Its enhanced networking builds on ENA."),
  ("Trade-off accepted", "A single-AZ placement reduces fault isolation, which is acceptable because the job can be rerun.")],
 {"A": "Spread placement groups put each instance on distinct hardware to reduce correlated failures. They allow at most 7 running instances per AZ per group and do not optimize inter-node latency. Spanning AZs also adds latency.",
  "B": "Partition placement groups isolate groups of instances on separate racks for large distributed workloads such as HDFS, HBase, and Cassandra. They are built for fault isolation, not the lowest latency between all nodes.",
  "D": "Spreading nodes across AZs increases inter-node latency. A load balancer distributes client requests and plays no part in MPI node-to-node communication."},
 [("Tightly coupled HPC / MPI / low latency between nodes", "Cluster placement group + EFA (+ ENA enhanced networking)."),
  ("Placement group types", "Cluster = performance (single AZ); partition = rack-level fault isolation for distributed data stores; spread = maximum isolation for a small number of critical instances.")])
new8=q("3.3", ["Amazon Redshift", "Amazon RDS for PostgreSQL"],
 "A retail company runs its order-processing application on Amazon RDS for PostgreSQL. Analysts also run complex SQL aggregations and joins over 5 years of historical sales data, which is now 40 TB and growing quickly. These analytical queries take hours, slow down the transactional workload, and use BI tools that connect through standard SQL drivers. The company wants fast analytical queries that scale with data growth without managing database infrastructure. Which solution meets these requirements?",
 {"A": "Migrate the historical sales data to Amazon DynamoDB and create global secondary indexes for each analytical query.",
  "B": "Move the RDS DB instance to the largest available instance class with io2 Provisioned IOPS storage.",
  "C": "Load the historical sales data into Amazon Redshift Serverless and point the BI tools at the Redshift endpoint.",
  "D": "Migrate the historical sales data to Amazon Neptune and run the analytical queries as graph traversals."},
 ["C"],
 [("Purpose-built data warehouse", "Amazon Redshift uses columnar storage, data compression, and massively parallel processing (MPP), so complex aggregations and joins over terabytes to petabytes of data run far faster than on a row-oriented OLTP database."),
  ("Workload isolation", "Moving analytics to Redshift removes the heavy queries from the RDS instance, so order processing is no longer slowed down."),
  ("Serverless and SQL-compatible", "Redshift Serverless provisions and scales capacity automatically, and BI tools connect through standard JDBC/ODBC drivers.")],
 {"A": "DynamoDB is a key-value and document database optimized for known access patterns. It does not support ad hoc SQL joins and aggregations, and a GSI per query is impractical.",
  "B": "A bigger OLTP instance is a temporary fix that has a hard ceiling. A row-store database still scans entire rows for analytical queries, and analytics would still compete with transactions on the same instance.",
  "D": "Neptune is a graph database for highly connected data such as social networks or fraud rings. It is not designed for SQL-based aggregations over large sales datasets."},
 [("OLTP vs. OLAP", "RDS/Aurora for transactions; Amazon Redshift for complex analytical SQL over large historical datasets."),
  ("Columnar + MPP + BI tools", "Amazon Redshift (Serverless for no capacity management)."),
  ("Ad hoc SQL on data already in S3", "Amazon Athena or Redshift Spectrum.")])
d=json.load(open('d3.json'))
assert 'backlog per instance' in d['set1'][3]['prompt'] or 'SQS' in d['set1'][3]['prompt']
assert 'RDS Proxy' in d['set1'][7]['options']['C']
d['set1'][3]=new4; d['set1'][7]=new8
json.dump(d,open('d3.json','w'),indent=2,ensure_ascii=False)
