# tf-starter

**Enterprise-grade Terraform Infrastructure-as-Code project generator.**

Generate production-ready Terraform projects for AWS, GCP, or Azure in seconds. `tf-starter` scaffolds a complete, modular IaC project with best practices baked in — multi-environment support, remote state, CI/CD pipelines, and more.

```
  _    __             _              _
 | |  / _|       ___| |_ __ _ _ __| |_ ___ _ __
 | __| |_ _____ / __| __/ _` | '__| __/ _ \ '__|
 | |_|  _|_____|\__ \ || (_| | |  | ||  __/ |
  \__|_|        |___/\__\__,_|_|   \__\___|_|

  Enterprise Terraform Project Generator v1.0.0
```

---

## Table of Contents

- [Features](#features)
- [Supported Providers](#supported-providers)
- [Available Modules](#available-modules)
- [Installation](#installation)
- [Usage](#usage)
- [Interactive Prompts](#interactive-prompts)
- [Generated Project Structure](#generated-project-structure)
- [What Gets Generated](#what-gets-generated)
- [Module Details](#module-details)
- [Environment-Aware Configuration](#environment-aware-configuration)
- [Dependencies & Smart Defaults](#dependencies--smart-defaults)
- [Requirements](#requirements)
- [License](#license)

---

## Features

- **Multi-cloud support** — AWS, GCP, and Azure with provider-specific best practices
- **Interactive CLI** — Guided prompts for environments, services, region, and backend configuration
- **Modular architecture** — Pick only the services you need; each generates an isolated Terraform module
- **9 service modules** — Network, Compute, Serverless Functions, API Gateway, Database, Kubernetes, Monitoring, Messaging, Storage
- **Multi-environment** — Generate separate configurations for dev, staging, prod, or custom environments
- **Environment-aware defaults** — Production gets HA, multi-AZ, higher resources; dev gets cost-optimized settings
- **Remote state backend** — Optional S3+DynamoDB (AWS), GCS (GCP), or Azure Storage backend
- **CI/CD pipeline** — GitHub Actions workflow for Terraform plan/apply with environment-based triggers
- **Makefile** — Pre-configured `make init`, `make plan`, `make apply`, `make destroy` commands
- **Pre-commit hooks** — terraform fmt, validate, tflint, and tfsec checks
- **Auto-generated README** — Project documentation with architecture diagram tailored to selected services
- **Dependency enforcement** — Kubernetes auto-enables Compute; API Gateway auto-enables serverless functions
- **Jinja2 template engine** — Dynamic rendering with conditional blocks based on selected services
- **Dual installation** — Install via pip (Python) or npm (Node.js)

---

## Supported Providers

| Provider | Network | Compute | Serverless | Database | Kubernetes | Monitoring | Messaging | Storage |
|----------|---------|---------|------------|----------|------------|------------|-----------|---------|
| **AWS** | VPC, Subnets, IGW, NAT | EC2, ALB, ASG | Lambda, API Gateway | RDS PostgreSQL | EKS | CloudWatch, SNS | SQS | S3 |
| **GCP** | VPC, Subnets, Firewall | GCE, Load Balancer | Cloud Functions, API Gateway | Cloud SQL | GKE | Cloud Monitoring | Pub/Sub | GCS |
| **Azure** | VNet, Subnets, NSG | VM Scale Sets, LB | Azure Functions, API Management | Azure Database for PostgreSQL | AKS | Azure Monitor | Service Bus | Blob Storage |

---

## Available Modules

| Module | Description | Always Included |
|--------|-------------|:---------------:|
| **network** | VPC/VNet, subnets (public + private), internet gateway, NAT, route tables | Yes |
| **compute** | Virtual machines, load balancer, auto-scaling group, launch templates | No |
| **lambda** / **cloud_functions** / **functions** | Serverless functions (Lambda on AWS, Cloud Functions on GCP, Azure Functions on Azure) | No |
| **apigateway** | REST API with proxy integration to Lambda, throttling, CORS, access logging | No |
| **database** | Managed PostgreSQL with encryption, multi-AZ (prod), automated backups | No |
| **kubernetes** | Managed Kubernetes cluster with node groups, IAM/RBAC, cluster logging | No |
| **monitoring** | Alarms, dashboards, log groups, notification topics | No |
| **messaging** | Message queues with dead-letter queues, encryption, access policies | No |
| **storage** | Object storage with versioning, encryption, lifecycle rules, public access block | No |

---

## Installation

### Option 1: pip (Python)

```bash
# Clone the repository
git clone https://github.com/your-org/tf-starter.git
cd tf-starter

# Create a virtual environment and install
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Run
tf-starter init
```

### Option 2: npm (Node.js)

```bash
# Clone the repository
git clone https://github.com/your-org/tf-starter.git
cd tf-starter

# Install (automatically sets up Python venv via postinstall)
npm install

# Run
npx tf-starter init
```

### Option 3: npm global install

```bash
npm install -g tf-starter
tf-starter init
```

---

## Usage

### Basic Command

```bash
tf-starter init [--output-dir <path>]
```

The interactive wizard will guide you through selecting provider, project name, environments, services, region, and backend configuration.

### Arguments

| Argument | Required | Description |
|----------|:--------:|-------------|
| `init` | Yes | Start the interactive project generator |
| `--output-dir` | No | Output directory (default: current directory) |

### Examples

```bash
# Create a new project (interactive)
tf-starter init

# Create a new project in a specific directory
tf-starter init --output-dir ./projects
```

---

## Interactive Prompts

After running `tf-starter init`, the wizard guides you through six interactive prompts:

### 1. Cloud Provider

```
? Select cloud provider:
  aws
  gcp
  azure
```

### 2. Project Name

```
? Enter project name: my-platform
```

### 3. Environments

```
? Select environments to create:
  [x] dev
  [ ] staging
  [ ] prod
  [ ] custom
```

Select one or more environments. Each gets its own `terraform.tfvars` with environment-specific values. Choose "custom" to enter a custom environment name.

### 4. Services

```
? Select service categories to enable:
  [x] Compute     (EC2, ALB, Auto Scaling)
  [ ] Lambda      (Serverless Functions)
  [ ] API Gateway (REST API + Lambda Integration)
  [ ] Database    (RDS PostgreSQL)
  [ ] Kubernetes  (EKS)
  [ ] Monitoring  (CloudWatch, SNS)
  [ ] Messaging   (SQS)
  [ ] Storage     (S3)
```

Select the infrastructure modules you need. The **Network** module is always included automatically.

### 5. Region

```
? Select AWS region:
  us-east-1
  us-east-2
  us-west-1
  ...
  Other (type manually)
```

Choose from common regions or type a custom one.

### 6. Remote Backend

```
? Enable remote backend (recommended for teams)? (Y/n)
```

Enables provider-specific remote state storage (S3+DynamoDB for AWS, GCS for GCP, Azure Storage for Azure).

---

## Generated Project Structure

After generation, you get a complete, ready-to-use Terraform project:

```
my-platform/
├── main.tf                    # Root module — wires all service modules together
├── variables.tf               # Root-level variable declarations
├── outputs.tf                 # Root-level outputs
├── providers.tf               # Provider configuration
├── versions.tf                # Terraform & provider version constraints
├── backend.tf                 # Remote state backend (if enabled)
├── Makefile                   # make init / plan / apply / destroy
├── README.md                  # Auto-generated docs with architecture diagram
├── .pre-commit-config.yaml    # Pre-commit hooks (fmt, validate, tflint, tfsec)
├── scripts/
│   └── init.sh                # Backend initialization script
├── .github/
│   └── workflows/
│       └── terraform.yml      # CI/CD pipeline (plan on PR, apply on merge)
├── modules/
│   ├── network/               # VPC, subnets, gateways, route tables
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── compute/               # EC2, ALB, ASG (if selected)
│   ├── lambda|cloud_functions|functions/  # Serverless functions (if selected)
│   ├── apigateway/            # API Gateway (if selected)
│   ├── database/              # RDS PostgreSQL (if selected)
│   ├── kubernetes/            # EKS cluster (if selected)
│   ├── monitoring/            # CloudWatch alarms (if selected)
│   ├── messaging/             # SQS queues (if selected)
│   └── storage/               # S3 buckets (if selected)
└── environments/
    ├── dev/
    │   ├── main.tf            # References root module
    │   ├── variables.tf       # Environment variable declarations
    │   ├── terraform.tfvars   # Dev-specific values (smaller instances, no HA)
    │   └── backend.tf         # Environment-specific backend config
    ├── staging/
    │   └── ...
    └── prod/
        └── ...                # Prod gets HA, multi-AZ, larger instances
```

---

## What Gets Generated

### Root Module (`main.tf`)

Wires all selected service modules together with proper dependency references. For example, the compute module receives VPC and subnet IDs from the network module.

### Environment Configurations

Each environment gets its own directory with `terraform.tfvars` containing environment-appropriate values. This allows you to run `terraform apply` per environment independently.

### CI/CD Pipeline (`.github/workflows/terraform.yml`)

A GitHub Actions workflow that:
- Runs `terraform fmt -check` and `terraform validate` on every pull request
- Runs `terraform plan` on PRs targeting the main branch
- Runs `terraform apply` on merge to main
- Supports environment-based deployment strategy

### Makefile

Pre-configured targets for common operations:

```bash
make init          # Initialize Terraform and backend
make plan          # Run terraform plan
make apply         # Apply changes
make destroy       # Destroy all resources
make fmt           # Format Terraform files
make validate      # Validate configuration
make lint          # Run tflint
```

### Pre-commit Hooks

Configured checks that run before every git commit:
- `terraform fmt` — Consistent formatting
- `terraform validate` — Configuration validation
- `tflint` — Terraform linter
- `tfsec` — Security scanner

### Auto-generated README

Each generated project includes a README with:
- Architecture diagram (dynamically generated based on selected services)
- Quick-start instructions
- Module documentation
- Scaling and operational guidance

---

## Module Details

### AWS Modules

| Module | Resources Created |
|--------|-------------------|
| **network** | VPC, 2 public subnets, 2 private subnets, Internet Gateway, NAT Gateway, route tables, elastic IP |
| **compute** | Application Load Balancer, security groups, launch template (Amazon Linux 2023, IMDSv2), Auto Scaling Group, scaling policies |
| **lambda** | IAM execution role, Lambda function, CloudWatch log group, optional VPC deployment, conditional SQS/RDS access policies |
| **apigateway** | REST API, `{proxy+}` catch-all resource, Lambda proxy integration, deployment, stage with throttling/logging, CORS support |
| **database** | RDS PostgreSQL 16.2, DB subnet group, security group, multi-AZ (prod), encryption at rest, SSM parameter for password, auto-scaling storage |
| **kubernetes** | EKS cluster, managed node group, IAM roles (cluster + node), cluster logging, security group |
| **monitoring** | SNS topic, CloudWatch alarms (CPU, storage, connections — conditional on compute/database), log groups with retention |
| **messaging** | SQS queue, dead-letter queue, redrive policy, server-side encryption, IAM access policy |
| **storage** | S3 bucket, versioning, AES-256 encryption, public access block, lifecycle rules (Intelligent Tiering, Glacier archival) |

### GCP Modules

| Module | Resources Created |
|--------|-------------------|
| **network** | VPC, subnets, firewall rules, Cloud NAT, Cloud Router |
| **compute** | GCE instances, instance groups, load balancer, health checks |
| **lambda** | Cloud Functions (2nd Gen), service account, GCS source bucket, Cloud Run IAM |
| **apigateway** | API Gateway, API config (OpenAPI spec), gateway deployment |
| **database** | Cloud SQL PostgreSQL, private networking, automated backups |
| **kubernetes** | GKE cluster, node pools, workload identity |
| **monitoring** | Cloud Monitoring alert policies, notification channels, log sinks |
| **messaging** | Pub/Sub topics and subscriptions, dead-letter topics |
| **storage** | GCS buckets, versioning, lifecycle rules, IAM |

### Azure Modules

| Module | Resources Created |
|--------|-------------------|
| **network** | VNet, subnets, NSG, NAT Gateway, public IP |
| **compute** | VM Scale Sets, load balancer, availability sets |
| **lambda** | Azure Function App (Linux), App Service Plan, Storage Account, Application Insights, managed identity |
| **apigateway** | API Management service, API definition, proxy operations, backend configuration, CORS policy |
| **database** | Azure Database for PostgreSQL Flexible Server, private DNS |
| **kubernetes** | AKS cluster, node pools, managed identity, Azure CNI |
| **monitoring** | Azure Monitor, alert rules, action groups, Log Analytics workspace |
| **messaging** | Service Bus namespace, queues, topics, subscriptions |
| **storage** | Storage Account, blob containers, lifecycle management |

---

## Environment-Aware Configuration

Generated `terraform.tfvars` files are automatically tuned per environment:

| Setting | Dev | Staging | Prod |
|---------|-----|---------|------|
| Instance type | `t3.micro` | `t3.small` | `t3.medium` |
| Min instances | 1 | 1 | 2 |
| Max instances | 2 | 3 | 6 |
| Multi-AZ (DB) | No | No | Yes |
| DB instance class | `db.t3.micro` | `db.t3.small` | `db.r6g.large` |
| Lambda memory | 128 MB | 256 MB | 512 MB |
| Lambda timeout | 30s | 60s | 120s |
| API throttle rate | 100 rps | 500 rps | 2000 rps |
| Deploy Lambda in VPC | No | No | Yes |
| Monitoring retention | 7 days | 14 days | 30 days |

---

## Dependencies & Smart Defaults

`tf-starter` enforces module dependencies automatically:

- **Kubernetes** requires **Compute** — EKS needs VPC networking and node instances. If you select Kubernetes without Compute, Compute is auto-enabled.
- **API Gateway** requires **Serverless Functions** — The API Gateway module integrates with Lambda (AWS), Cloud Functions (GCP), or Azure Functions (Azure). Selecting API Gateway without the serverless module auto-enables it.
- **Network** is always included — All modules depend on VPC/subnet infrastructure.

Conditional cross-module integrations:
- **Lambda** automatically gets IAM policies for **SQS** access if Messaging is selected
- **Lambda** automatically gets IAM policies for **RDS** access if Database is selected
- **Monitoring** generates alarms for **Compute** metrics (CPU) and **Database** metrics (storage, connections) only when those modules are selected

---

## Requirements

- **Python** 3.9 or higher
- **Node.js** 16+ (only if installing via npm)
- **Terraform** 1.0+ (to use the generated projects)

### Optional (for generated projects)

- [pre-commit](https://pre-commit.com/) — For pre-commit hooks
- [tflint](https://github.com/terraform-linters/tflint) — Terraform linter
- [tfsec](https://github.com/aquasecurity/tfsec) — Security scanner

---

## Quick Start

```bash
# 1. Install
git clone https://github.com/your-org/tf-starter.git && cd tf-starter
npm install

# 2. Generate a project
npx tf-starter init

# 3. Use the generated project
cd my-platform
make init
make plan
make apply
```

---

## License

MIT
