# Django Async Payment Notification Service

**🟢 Live on AWS Free Tier** — `http://3.235.76.131:8000`

A robust, production-ready Django application engineered to handle asynchronous payment processing and notifications. This project leverages an event-driven architecture to ingest payment events via an API and asynchronously process them using Celery workers backed by AWS Simple Queue Service (SQS) as the message broker.

---

## ✅ Live Deployment Evidence

| Resource          | Detail                                                                          |
| ----------------- | ------------------------------------------------------------------------------- |
| **EC2 Public IP** | [`3.235.76.131`](http://3.235.76.131:8000) · `t3.micro` · `us-east-1f`          |
| **Admin Panel**   | [http://3.235.76.131:8000/admin/](http://3.235.76.131:8000/admin/) (live 🟢)    |
| **API Base URL**  | `http://3.235.76.131:8000/api/v1/`                                              |
| **RDS Endpoint**  | `terraform-20260305162706385000000001.cqfemok6y1ta.us-east-1.rds.amazonaws.com` |
| **SQS Queue**     | `https://sqs.us-east-1.amazonaws.com/630596767200/django-payment-service`       |
| **Instance ID**   | `i-05c960f038d28cd28`                                                           |

> The infrastructure was provisioned with Terraform. The screenshot below was taken directly from the running production server.

![Django Admin panel live on AWS EC2 at 3.235.76.131:8000](docs/deployment_screenshot.png)

---

## ⚡ Performance Benchmarks

Load-tested with **autocannon** against the production EC2 instance. Full results in [BENCHMARKS.md](BENCHMARKS.md).

| Endpoint                     | Req/s   | p50 lat | p99 lat | Errors |
| ---------------------------- | ------- | ------- | ------- | ------ |
| `POST /api/v1/payments/`     | **214** | 38 ms   | 142 ms  | 0      |
| `GET  /api/v1/payments/{id}` | **389** | 21 ms   | 89 ms   | 0      |

> ✅ SRS success criteria met: >200 req/s sustained · p99 <150 ms

---

## 🏛️ Architecture Diagram

```mermaid
flowchart LR
    Client(["🌐 Client\nAPI Consumer"])

    subgraph PROD["  PRODUCTION  "]
        direction TB
        subgraph EC2["☁️ AWS EC2 — t2.micro (Free Tier)"]
            direction TB
            Web["🐍 Web Container\nDjango + Gunicorn · :8000"]
            Worker["⚙️ Worker Container\nCelery"]
        end

        subgraph MANAGED["☁️ AWS Managed Services"]
            direction TB
            SQS[("📨 AWS SQS\nMain Queue + DLQ")]
            RDS[("🗄️ AWS RDS\nPostgres 15")]
        end
    end

    subgraph DEV["  LOCAL DEVELOPMENT ONLY  "]
        direction TB
        LocalStack["🧪 LocalStack\nSQS Emulator"]
        LocalDB[("🐘 Postgres\nDocker Container")]
    end

    Client -->|"JWT Auth\nHTTP"| Web
    Web -->|"Enqueue task"| SQS
    Web <-->|"Read / Write"| RDS
    SQS -->|"Poll & consume"| Worker
    Worker -->|"Write results"| RDS

graph LR
    Client[Client] -->|POST /payments/| Web[Django Web API]
    Web -->|Write| RDS[(AWS RDS Postgres)]
    Web -->|Enqueue| SQS[[AWS SQS Queue]]
    SQS -->|Consume| Worker[Celery Worker]
    Worker -->|Update Status| RDS
    Worker -->|Log| Notifications[Notification Logs]
```

---

## 📂 Project Structure

Organized for clarity and maintainability:

- `core/`: Project configuration and settings for LocalStack and AWS.
- `payments/`: Core API for payment intake, models, and idempotency logic.
- `notifications/`: Celery tasks and logging for payment notifications.
- `docs/`: Comprehensive [documentation](docs/usage_scenario.md), [benchmarks](docs/BENCHMARKS.md), and [guides](docs/DEPLOYMENT_GUIDE.md).
- `scripts/`: Diagnostic and performance testing [scripts](scripts/benchmarks/README.md).
- `terraform/`: Infrastructure as Code for AWS deployment.

---

## � Reviewer Access

For recruiters and reviewers who wish to explore the live system without setting up the environment:

- **Admin URL**: `http://3.235.76.131:8000/admin`
- **Username**: `admin`
- **Password**: `adminpass`

> [!IMPORTANT]
> These credentials are for review purposes only. The system is deployed on a dedicated AWS instance for verification.

---

## �🚥 Quick Start (Local Development)

1. **Environment Setup**:

   ```bash
   cp .env.example .env
   # Ensure LocalStack and Postgres are configured
   ```

2. **Launch with Docker**:

   ```bash
   docker-compose up --build
   ```

3. **Access Documentation**:
   - Detailed Walkthrough: [Usage Scenario](docs/usage_scenario.md)
   - Performance Report: [Benchmarks](docs/BENCHMARKS.md)

---

## ✅ Performance Validation

Validating the system against production-grade requirements:

| Endpoint                     | Baseline Latency | Actual Throughput |
| :--------------------------- | :--------------- | :---------------- |
| `POST /api/v1/payments/`     | ~48ms            | ~208 req/s        |
| `GET /api/v1/payments/{id}/` | ~32ms            | ~312 req/s        |

See full results in [BENCHMARKS.md](docs/BENCHMARKS.md).

---

## 🛠️ Maintenance & Diagnostics

Utility scripts are available in the `scripts/` directory:

- `diagnose_sqs.py`: Verify connectivity and depth of SQS queues.
- `benchmarks/`: Autocannon configuration for load testing.

---

## 📄 License

Professional implementation by Krishna Pendyala. All rights reserved.

```env
DEBUG=True
SECRET_KEY=django-insecure-dev-key
DATABASE_URL=postgres://django_admin:change-me@db:5432/payment_db
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_REGION=us-east-1
SQS_ENDPOINT_URL=http://localstack:4566
SQS_QUEUE_NAME=django-payment-service
```

### 3. Start the Development Stack

Run the following command from the project root:

```bash
docker-compose up --build
```

This spins up:

1. `db`: Local PostgreSQL database.
2. `localstack`: Local AWS SQS mock.
3. `web`: Django application running on `http://localhost:8000`.
4. `worker`: Celery worker reading from LocalStack.

---

## ☁️ AWS Cloud Deployment (Production)

The production environment maps directly to managed AWS services rather than local containers. See `DEPLOYMENT_GUIDE.md` for extended details.

### 1. Provision Infrastructure via Terraform

```bash
cd terraform
terraform init
terraform apply
```

This provisions:

- **EC2 Instance (t2.micro)** — free-tier eligible (12-month) — for Docker hosts.
- **AWS RDS (Postgres 15)** inside a locked-down security group.
- **AWS SQS Queues** (Main queue and Dead-Letter Queue).
- **IAM User** with strict permissions for SQS access.

### 2. Production Environment Values

Update your `.env` with the Terraform outputs:

```env
DEBUG=False
DATABASE_URL=postgres://django_admin:password@<rds-endpoint>:5432/payment_db
AWS_ACCESS_KEY_ID=<iam-key>
AWS_SECRET_ACCESS_KEY=<iam-secret>
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/<account-id>/django-payment-service
```

### 3. Run Production Services on EC2

Deploy using the production compose file which omits `db` and `localstack`.

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🧪 Running Tests

To run the automated test suite through Docker:

```bash
docker-compose run web pytest
```

## 📖 Related Documents

- [⚡ Performance Benchmarks (autocannon)](BENCHMARKS.md)
- [Implementation Journey (Engineering Decisions)](IMPLEMENTATION_JOURNEY.md)
- [EC2 Deployment Guide](DEPLOYMENT_GUIDE.md)
