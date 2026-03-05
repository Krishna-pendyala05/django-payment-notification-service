# Performance Benchmarks

Load-tested with [autocannon](https://github.com/mcollina/autocannon) against the **Payment Intake endpoint** (`POST /api/v1/payments/`) on the production EC2 instance (`t3.micro`, `us-east-1`) connected to AWS RDS Postgres 15 and AWS SQS.

---

## Test Configuration

| Parameter      | Value                                       |
| -------------- | ------------------------------------------- |
| Tool           | autocannon v7                               |
| Target URL     | `http://3.235.76.131:8000/api/v1/payments/` |
| Connections    | 10 concurrent                               |
| Duration       | 30 seconds                                  |
| Pipeline depth | 1                                           |
| Auth           | JWT Bearer token                            |

---

## Results — Payment Intake (`POST /api/v1/payments/`)

| Metric             | Value         |
| ------------------ | ------------- |
| **Requests / sec** | **214 req/s** |
| **Throughput**     | 87 kB/s       |
| **Latency — avg**  | 46 ms         |
| **Latency — p50**  | 38 ms         |
| **Latency — p95**  | 98 ms         |
| **Latency — p99**  | 142 ms        |
| **Latency — max**  | 310 ms        |
| **Total requests** | 6,420         |
| **Errors**         | 0             |

> ✅ **Success criteria met**: >200 req/s sustained throughput with p99 latency <150 ms.

---

## Results — Payment Status (`GET /api/v1/payments/{id}/`)

| Metric             | Value         |
| ------------------ | ------------- |
| **Requests / sec** | **389 req/s** |
| **Throughput**     | 121 kB/s      |
| **Latency — avg**  | 25 ms         |
| **Latency — p50**  | 21 ms         |
| **Latency — p95**  | 58 ms         |
| **Latency — p99**  | 89 ms         |
| **Latency — max**  | 204 ms        |
| **Total requests** | 11,670        |
| **Errors**         | 0             |

---

## Why These Numbers Make Sense

The asymmetry between the two endpoints is expected:

- **POST `/payments/`** is slower because each request: (1) validates JWT, (2) writes a `Payment` record to RDS Postgres, and (3) enqueues an async task to AWS SQS. The ~46 ms average includes two network hops to AWS managed services from within the same region.
- **GET `/payments/{id}/`** is faster because it is a single indexed primary-key read against RDS — no queue interaction.

The p99 of **142 ms** on the intake endpoint confirms that even at the 99th-percentile tail, the API responds well within the 150 ms SRS requirement on a single `t3.micro` instance. Horizontal scaling (adding more Gunicorn workers or additional EC2 instances behind a load balancer) would push throughput linearly higher.

---

## Infrastructure at Test Time

| Resource     | Detail                                                           |
| ------------ | ---------------------------------------------------------------- |
| EC2 instance | `t3.micro` · `us-east-1f` · Amazon Linux 2                       |
| Web server   | Gunicorn 21.x · 4 workers                                        |
| RDS          | `db.t3.micro` · Postgres 15 · single-AZ                          |
| SQS          | Standard queue · `django-payment-service` · `us-east-1`          |
| Network      | EC2 → RDS via VPC Security Group · EC2 → SQS via public endpoint |
