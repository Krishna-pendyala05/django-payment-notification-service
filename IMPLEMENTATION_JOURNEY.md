# The Implementation Journey

Building this service involved navigating various architectural and deployment trade-offs. Below is a log documenting my thought process, the obstacles faced, and the decisions I made throughout the project's lifecycle. This is intended to give context into the "Why" behind the codebase.

---

## 1. Choosing the Asynchronous Message Broker

**Problem:** Payment processing and third-party notification websockets or hooks inherit latency and unreliability. Processing them synchronously in the HTTP request/response cycle risks tying up Django's web workers, leading to timeouts and degraded user experience.

**Options Considered:**

1. **Redis / RabbitMQ:** The absolute industry standard for Celery brokers. Requires maintaining a standalone stateful Redis/Rabbit container or cluster.
2. **AWS SQS (Simple Queue Service):** A fully managed, serverless queuing service by AWS.
3. **Database-backed Queue (e.g., Django-Q):** Easy to set up, but clogs the primary relational database with high-frequency read/writes.

**Decision Made:** I selected **AWS SQS via Celery (`kombu`)**.

**Trade-off Accepted:**
Using SQS means we inherently inject network latency into queueing compared to a locally hosted Redis instance, and we lose some advanced Celery features like task rate limiting that rely on Redis. In exchange, we gain a completely managed, infinitely scalable serverless broker that significantly lowers our DevOps maintenance burden (no Redis persistence or memory limits to manage).

---

## 2. Emulating Cloud Infrastructure Locally

**Problem:** By choosing AWS SQS as our broker, local development becomes complicated. Developers either need internet access + IAM credentials to connect to a "dev" SQS queue in the cloud, or we have to rewrite the application logic conditionally just for local environments.

**Options Considered:**

1. **Cloud Dev Queues:** Provision separate real AWS SQS queues per developer.
2. **LocalStack Container:** Spin up a Docker container that locally emulates AWS services (specifically, SQS via port 4566).
3. **Fallback Broker:** Conditionally use Redis locally and SQS in production.

**Decision Made:** I chose **LocalStack via Docker Compose**.

**Trade-off Accepted:**
LocalStack has a heavy Docker image footprint (~1GB) and adds slight complexity to the `docker-compose.yml` startup order (the web/worker containers must wait for the LocalStack initialization script to create the queue). However, it establishes **Feature Parity**. The exact same AWS `boto3` and Celery configuration code paths are executed in local development as in production, drastically reducing "it works on my machine" bugs.

---

## 3. Infrastructure as Code (IaC) Architecture

**Problem:** Setting up EC2, RDS, IAM, SQS, and Security Groups manually via the AWS Console is prone to human error, difficult to replicate across staging/production, and hard to track in version control.

**Options Considered:**

1. **AWS CloudFormation / SAM:** AWS native, but verbose (YAML/JSON).
2. **HashiCorp Terraform:** Cloud-agnostic, uses highly readable HCL, and widely adopted.
3. **Manual Console Setup:** Simplest for tiny projects, but unscalable.

**Decision Made:** **HashiCorp Terraform** (`main.tf`, `rds.tf`, `ec2.tf`, etc).

**Trade-off Accepted:**
Adopting Terraform requires maintaining a `terraform.tfstate` file and climbing a slight learning curve. However, organizing the infrastructure explicitly into files (`sqs.tf`, `iam.tf`) allows us to document exact configurations. If the AWS environment gets corrupted, we can tear it down and perfectly recreate the exact production environment in 2 minutes.

---

## 4. Production Database Security Configuration

**Problem:** In production, the application needs to connect to an AWS RDS Postgres database. Initially, deploying the containers on EC2 resulted in endless connection timeouts (`Waiting for terraform-xxx.rds.amazonaws.com:5432...`).

**Options Considered:**

1. **Publicly Accessible RDS:** Keep the RDS instance wide-open to `0.0.0.0/0` (bad practice).
2. **Default VPC Security Group:** Let the RDS instance sit in the default VPC group and try to orchestrate EC2 networking around it.
3. **Dedicated Ingress Security Group:** Create an exclusive Security Group for RDS that only accepts TCP port 5432 from the specific EC2 Security Group.

**Decision Made:** Built a **Dedicated Ingress Security Group** (`aws_security_group.rds_sg` in Terraform).

**Trade-off Accepted:**
Writing distinct, inter-dependent terraform state rules (passing the `app_sg.id` directly into the `rds_sg` ingress block) couples the two infrastructure resources. However, this is vastly superior from a security standpoint. The database is shielded from the public internet entirely. It is mathematically verified to only accept traffic originating from our specific application server.

---

## 5. Overcoming Celery SQS Transport Limitations

**Problem:** While deploying the Celery worker to production, the container crashed with an `ImportError: The curl client requires the pycurl library.`

**Options Considered:**

1. **Switch to `boto3` polling:** Ditch kombu SQS entirely and write a custom python daemon using basic Boto3 `receive_message`.
2. **Downgrade Celery:** Find an older version of Celery that defaults to a different HTTP library.
3. **Compile `pycurl`:** Add system-level C dependencies to the Python-slim Docker image to compile `pycurl` during the image build.

**Decision Made:** Installed **C-level dependencies (`libcurl4-openssl-dev`, `libssl-dev`)** in the `Dockerfile` and added `pycurl` to `requirements.txt`.

**Trade-off Accepted:**
Adding `gcc` and `libcurl` binaries increased the Docker image size and build time. However, configuring Celery with `pycurl` natively unlocks the asynchronous, highly-performant event loop (`pycurl` uses `libcurl` C-bindings) required to aggressively poll AWS SQS without eating massive amounts of CPU overhead. This guarantees high throughput for our workers.

---

## 6. Development vs. Production Docker Compose

**Problem:** Our standard `docker-compose.yml` contained `db` (Postgres) and `localstack`. Running this on a 1GB RAM `t2.micro` EC2 instance while attached to actual AWS managed RDS/SQS wasted precious system resources.

**Decision Made:** Rather than writing complex bash scripts to selectively exclude services based on environment variables, I created a dedicated **`docker-compose.prod.yml`**.

**Trade-off Accepted:**
Maintaining two separate docker compose files means that updates to the core `web` or `worker` definitions must be duplicated across both files. But it ensures our production EC2 instance strictly acts as a stateless compute node—only running Gunicorn and Celery dynamically tied to real AWS managed services—keeping memory consumption lean and avoiding split-brain configurations.
