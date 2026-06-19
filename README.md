# Cloud Native Microservices

A production-grade containerized microservices platform built with Python (FastAPI), Docker, and AWS ECS Fargate. Three loosely-coupled services communicate via AWS Cloud Map (DNS-based service discovery) and Redis pub/sub, fronted by an Application Load Balancer.

## Architecture

```
                        ┌──────────────────────────────────────────────┐
                        │                   AWS VPC                    │
                        │                                              │
Internet ──► Route 53 ──►  ALB (public subnets)                       │
                        │   │                                          │
                        │   ├──/auth/*──────► Auth Service (Fargate)   │
                        │   │                      │                   │
                        │   ├──/orders/*─────► Orders Service (Fargate)│
                        │   │                      │                   │
                        │   └──/notifications/*──► Notifications       │
                        │                      │   Service (Fargate)   │
                        │                      │                       │
                        │              ElastiCache Redis               │
                        │          (session store + pub/sub)           │
                        │                                              │
                        │      All services in private subnets         │
                        │      NAT Gateway for outbound traffic        │
                        └──────────────────────────────────────────────┘
```

### AWS Services Used

| Service | Purpose |
|---------|---------|
| ECS Fargate | Serverless container runtime — no EC2 management |
| ECR | Private Docker registry with vulnerability scanning |
| ALB | Layer 7 load balancing with path-based routing rules |
| AWS Cloud Map | DNS-based service discovery (`auth.cloud-native-ms.local`) |
| ElastiCache Redis | Shared session store + pub/sub for event-driven notifications |
| Secrets Manager | JWT secret injected at runtime — never in environment config |
| CloudWatch | Centralized logs + CPU alarms per service |
| VPC | Public/private subnet isolation, NAT Gateway, Security Groups |
| CodeDeploy / GitHub Actions | Blue/green deployments with automatic rollback |

## Services

### Auth Service (`/auth/*`)
Handles user registration, login, and JWT token verification. All other services validate tokens by calling `/auth/verify` via Cloud Map.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/auth/register` | POST | No | Register a new user |
| `/auth/login` | POST | No | Returns a JWT token |
| `/auth/verify` | GET | Bearer | Validates a token (used internally) |
| `/health` | GET | No | Health check |

### Orders Service (`/orders/*`)
Full CRUD for orders. Publishes `order_created` and `order_updated` events to Redis on every write.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/orders` | GET | Bearer | List all orders for current user |
| `/orders` | POST | Bearer | Create an order |
| `/orders/{id}` | GET | Bearer | Get a specific order |
| `/orders/{id}` | PUT | Bearer | Update an order |
| `/orders/{id}` | DELETE | Bearer | Delete an order |
| `/health` | GET | No | Health check |

### Notifications Service (`/notifications/*`)
Runs a background worker that subscribes to Redis pub/sub. Every order event becomes a notification delivered to the owning user.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/notifications` | GET | Bearer | List notifications for current user |
| `/notifications/{id}/read` | PATCH | Bearer | Mark a notification as read |
| `/health` | GET | No | Health check |

## Local Setup

**Prerequisites:** Docker, Docker Compose, `make`

```bash
git clone https://github.com/AmiraBahaa/cloud-native-microservices.git
cd cloud-native-microservices

cp .env.example .env

make up
```

Services will be available at:

| Service | URL | Swagger Docs |
|---------|-----|-------------|
| API Gateway (nginx) | http://localhost | — |
| Auth | http://localhost:8001 | http://localhost:8001/docs |
| Orders | http://localhost:8002 | http://localhost:8002/docs |
| Notifications | http://localhost:8003 | http://localhost:8003/docs |
| Jaeger UI | http://localhost:16686 | — |

### Quick API test

```bash
# Register
curl -X POST http://localhost/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"amira","password":"secret123","email":"amira@example.com"}'

# Login → get token
TOKEN=$(curl -s -X POST http://localhost/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"amira","password":"secret123"}' | jq -r '.access_token')

# Create an order
curl -X POST http://localhost/orders/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product":"MacBook Pro","quantity":1,"price":2499.99}'

# Check notifications (auto-created by the event)
curl http://localhost/notifications/ \
  -H "Authorization: Bearer $TOKEN"
```

### Makefile commands

```bash
make up        # start all services (builds images)
make down      # stop all services
make logs      # tail all logs
make ps        # service status
make clean     # stop + remove volumes + prune Docker
```

## AWS Deployment

### Prerequisites

- AWS CLI configured
- Terraform >= 1.6
- An S3 bucket for Terraform state

### Deploy infrastructure

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars

terraform init
terraform plan
terraform apply
```

### Push images and deploy

On push to `main`, GitHub Actions automatically:
1. Builds all three Docker images
2. Pushes to ECR with the commit SHA tag
3. Forces a new ECS deployment on each service
4. Waits for `services-stable` before marking the workflow green

Configure these GitHub secrets before the first deploy:

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user with ECS + ECR permissions |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret |
| `AWS_ACCOUNT_ID` | Your 12-digit AWS account ID |

## Project Structure

```
cloud-native-microservices/
├── services/
│   ├── auth/               # Auth microservice
│   ├── orders/             # Orders microservice
│   └── notifications/      # Notifications microservice
├── nginx/                  # ALB simulation (local)
├── terraform/              # Full AWS IaC
│   ├── vpc.tf              # VPC, subnets, NAT Gateway
│   ├── ecs.tf              # ECS cluster, task defs, services
│   ├── ecr.tf              # Container registries
│   ├── alb.tf              # Load balancer + routing rules
│   ├── elasticache.tf      # Redis cluster
│   ├── secrets.tf          # Secrets Manager
│   ├── iam.tf              # Execution + task roles
│   ├── cloudmap.tf         # Service discovery
│   └── cloudwatch.tf       # Logs + alarms
├── .github/workflows/
│   ├── ci.yml              # Build + integration tests on every push
│   └── deploy.yml          # Push to ECR + deploy to ECS on main
├── docker-compose.yml
├── Makefile
└── README.md
```

## Security

- All compute runs in **private subnets** — no direct internet access
- **Security Groups** restrict: ALB → ECS (port 8000), ECS → Redis (port 6379)
- JWT secret is stored in **AWS Secrets Manager**, injected at task startup
- ECR repositories have **image vulnerability scanning** on every push
- Redis in-transit and at-rest **encryption enabled**
- IAM roles follow **least privilege** — task roles only have X-Ray write access
