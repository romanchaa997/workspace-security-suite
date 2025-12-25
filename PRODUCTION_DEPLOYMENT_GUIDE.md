# Production Deployment Guide

## Overview

This comprehensive guide provides step-by-step instructions for deploying Workspace Security Suite to production environments on AWS, GCP, and Azure.

---

## Table of Contents

1. [AWS Deployment](#aws-deployment)
2. [GCP Deployment](#gcp-deployment)
3. [Azure Deployment](#azure-deployment)
4. [Multi-Cloud Setup](#multi-cloud-setup)
5. [Post-Deployment Validation](#post-deployment-validation)

---

## AWS Deployment

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- ECR repository created
- RDS PostgreSQL database
- ElastiCache Redis cluster

### Step 1: Prepare Infrastructure

```bash
# Create IAM roles for ECS
aws iam create-role --role-name workspace-security-ecs-role \
  --assume-role-policy-document file://trust-policy.json

# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Create subnets
aws ec2 create-subnet --vpc-id vpc-xxxxx --cidr-block 10.0.1.0/24 --availability-zone us-east-1a
aws ec2 create-subnet --vpc-id vpc-xxxxx --cidr-block 10.0.2.0/24 --availability-zone us-east-1b
```

### Step 2: Create RDS Instance

```bash
aws rds create-db-instance \
  --db-instance-identifier workspace-security-prod \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 14.5 \
  --allocated-storage 100 \
  --storage-type gp2 \
  --master-username admin \
  --master-user-password <STRONG_PASSWORD> \
  --backup-retention-period 30 \
  --multi-az \
  --publicly-accessible false
```

### Step 3: Create ElastiCache Redis

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id workspace-security-redis \
  --cache-node-type cache.t3.medium \
  --engine redis \
  --engine-version 7.0 \
  --num-cache-nodes 3 \
  --automatic-failover-enabled \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled
```

### Step 4: Push Docker Image to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Build and push image
docker build -t workspace-security:latest .
docker tag workspace-security:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/workspace-security:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/workspace-security:latest
```

### Step 5: Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name workspace-security-prod

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster workspace-security-prod \
  --service-name workspace-security-api \
  --task-definition workspace-security:1 \
  --desired-count 3 \
  --launch-type FARGATE
```

### Step 6: Configure Load Balancer

```bash
aws elbv2 create-load-balancer \
  --name workspace-security-lb \
  --subnets subnet-xxxxx subnet-yyyyy \
  --security-groups sg-xxxxx \
  --type application

# Create target group
aws elbv2 create-target-group \
  --name workspace-security-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxx
```

---

## GCP Deployment

### Prerequisites

- Google Cloud Project with billing enabled
- gcloud CLI installed and configured
- Cloud SQL PostgreSQL instance
- Cloud Memorystore Redis instance

### Step 1: Create GKE Cluster

```bash
gcloud container clusters create workspace-security \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n2-standard-4 \
  --enable-stackdriver-kubernetes \
  --enable-ip-alias \
  --network workspace-security-network \
  --cluster-secondary-range-name pods \
  --services-secondary-range-name services
```

### Step 2: Create Cloud SQL Instance

```bash
gcloud sql instances create workspace-security-db \
  --database-version POSTGRES_14 \
  --tier db-custom-4-16384 \
  --region us-central1 \
  --backup \
  --retained-backups-count 30 \
  --retained-backup-days 30

# Create database
gcloud sql databases create workspace_security \
  --instance=workspace-security-db

# Set password
gcloud sql users set-password postgres \
  --instance=workspace-security-db \
  --password
```

### Step 3: Create Memorystore Redis

```bash
gcloud redis instances create workspace-security-cache \
  --size=5 \
  --region=us-central1 \
  --redis-version=7.0 \
  --persistence-mode=RDB
```

### Step 4: Deploy Application

```bash
# Push image to GCR
docker tag workspace-security:latest gcr.io/PROJECT_ID/workspace-security:latest
docker push gcr.io/PROJECT_ID/workspace-security:latest

# Create deployment
kubectl create deployment workspace-security \
  --image=gcr.io/PROJECT_ID/workspace-security:latest \
  --replicas=3

# Create service
kubectl expose deployment workspace-security \
  --port=80 \
  --target-port=8000 \
  --type=LoadBalancer
```

---

## Azure Deployment

### Prerequisites

- Azure subscription
- Azure CLI installed
- Azure Container Registry
- Azure Database for PostgreSQL
- Azure Cache for Redis

### Step 1: Create Resource Group

```bash
az group create \
  --name workspace-security-prod \
  --location eastus
```

### Step 2: Create Azure Database

```bash
az postgres server create \
  --resource-group workspace-security-prod \
  --name workspace-security-db \
  --location eastus \
  --admin-user dbadmin \
  --admin-password <STRONG_PASSWORD> \
  --sku-name B_Gen5_2 \
  --storage-size 51200 \
  --backup-retention 30 \
  --geo-redundant-backup Enabled
```

### Step 3: Create Azure Cache for Redis

```bash
az redis create \
  --resource-group workspace-security-prod \
  --name workspace-security-cache \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

### Step 4: Create AKS Cluster

```bash
az aks create \
  --resource-group workspace-security-prod \
  --name workspace-security-aks \
  --node-count 3 \
  --vm-set-type VirtualMachineScaleSets \
  --load-balancer-sku standard \
  --enable-managed-identity \
  --enable-addons monitoring,http_application_routing
```

### Step 5: Deploy Application

```bash
# Get credentials
az aks get-credentials \
  --resource-group workspace-security-prod \
  --name workspace-security-aks

# Deploy
kubectl apply -f deployment.yaml
```

---

## Multi-Cloud Setup

### Cross-Cloud Load Balancing

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: multi-cloud-config
data:
  aws-endpoint: "https://aws.workspace-security.prod"
  gcp-endpoint: "https://gcp.workspace-security.prod"
  azure-endpoint: "https://azure.workspace-security.prod"
```

### Global DNS

```bash
# Using Route53 for multi-region failover
aws route53 create-hosted-zone \
  --name workspace-security.prod \
  --caller-reference $(date +%s)

# Create health checks for each region
aws route53 create-health-check \
  --health-check-config \
    IPAddress=AWS_LB_IP,Port=443,Type=HTTPS
```

---

## Post-Deployment Validation

### Health Checks

```bash
# Check API health
curl https://api.workspace-security.prod/health

# Check database connectivity
psql -h <DB_HOST> -U admin -d workspace_security -c "SELECT 1"

# Check Redis connectivity
redis-cli -h <REDIS_HOST> PING
```

### Monitoring Setup

```bash
# Deploy Prometheus
kubectl apply -f prometheus-config.yaml

# Deploy Grafana
kubectl apply -f grafana-config.yaml

# Create dashboards
kubectl apply -f grafana-dashboards.yaml
```

### Security Validation

```bash
# Run security scan
docker run --rm -v $(pwd):/src aquasec/trivy image workspace-security:latest

# Validate SSL certificates
sslscan api.workspace-security.prod

# Check OWASP compliance
zap-cli quick-scan --self-contained api.workspace-security.prod
```

---

## Rollback Procedures

### AWS ECS Rollback

```bash
aws ecs update-service \
  --cluster workspace-security-prod \
  --service workspace-security-api \
  --task-definition workspace-security:PREVIOUS_REVISION
```

### GCP GKE Rollback

```bash
kubectl rollout undo deployment/workspace-security
kubectl rollout history deployment/workspace-security
```

### Azure AKS Rollback

```bash
kubectl rollout undo deployment workspace-security
kubectl get rollouts -o wide
```

---

## Troubleshooting

### Common Issues

**1. Database Connection Failures**
```bash
# Check security groups/network policies
aws ec2 describe-security-groups --group-ids sg-xxxxx

# Verify RDS endpoint is accessible
nc -zv workspace-security-db.xxxxx.us-east-1.rds.amazonaws.com 5432
```

**2. Redis Connection Issues**
```bash
# Check ElastiCache cluster status
aws elasticache describe-cache-clusters

# Verify subnet routing
aws ec2 describe-route-tables
```

**3. Container Startup Failures**
```bash
# View container logs
aws logs get-log-events --log-group-name /ecs/workspace-security

# Check task definition
aws ecs describe-task-definition --task-definition workspace-security
```

---

## Support

For deployment support: deploy-support@workspace-security.dev
