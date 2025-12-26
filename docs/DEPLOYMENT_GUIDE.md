# Workspace Security Suite - Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the Workspace Security Suite in various environments (development, staging, and production).

## Prerequisites

### Software Requirements
- Docker & Docker Compose
- Kubernetes 1.20+
- Node.js 16+ or Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Git

### Cloud Requirements
- AWS, GCP, or Azure account
- IAM permissions for resource creation
- DNS configuration access
- SSL/TLS certificates

### Google Workspace Requirements
- Admin account with API access
- Service account credentials (JSON file)
- Domain-wide delegation configured
- Required API scopes enabled

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/romanchaa997/workspace-security-suite.git
cd workspace-security-suite
```

### 2. Environment Variables
Create `.env` file in the root directory:

```env
# Application
NODE_ENV=production
PORT=3000
APP_SECRET=your-secret-key

# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=workspace_suite
DB_USER=postgres
DB_PASSWORD=secure_password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password

# Google Workspace
GWSPACE_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
GWSPACE_ADMIN_EMAIL=admin@yourdomain.com
GWSPACE_DOMAIN=yourdomain.com

# JWT
JWT_SECRET=jwt-secret-key
JWT_EXPIRY=24h

# SIEM Integration
SIEM_TYPE=splunk|elk|datadog
SIEM_ENDPOINT=https://your-siem-endpoint
SIEM_API_TOKEN=your-api-token

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=app-password
```

## Docker Deployment

### Quick Start with Docker Compose

```bash
# Copy service account file
cp /path/to/service-account.json ./config/

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Start services
docker-compose up -d

# Wait for services to be ready
sleep 30

# Run database migrations
docker-compose exec api npm run migrate

# Seed initial data (optional)
docker-compose exec api npm run seed
```

### Docker Compose Services

```yaml
services:
  api:
    build: ./api
    ports:
      - "3000:3000"
    depends_on:
      - postgres
      - redis
    environment:
      - NODE_ENV=production
      - DB_HOST=postgres
      - REDIS_HOST=redis

  frontend:
    build: ./frontend
    ports:
      - "80:3000"
    depends_on:
      - api

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
```

## Kubernetes Deployment

### 1. Create Namespace
```bash
kubectl create namespace workspace-security
```

### 2. Create Secrets
```bash
kubectl create secret generic workspace-suite-secrets \
  --from-file=service-account.json=./config/service-account.json \
  --from-env-file=.env \
  -n workspace-security
```

### 3. Create ConfigMap
```bash
kubectl create configmap workspace-suite-config \
  --from-file=nginx.conf=./config/nginx.conf \
  -n workspace-security
```

### 4. Deploy Using Helm
```bash
# Add Helm repository
helm repo add workspace-suite https://charts.example.com
helm repo update

# Install chart
helm install workspace-suite workspace-suite/workspace-suite \
  -n workspace-security \
  -f values.yaml

# Upgrade chart
helm upgrade workspace-suite workspace-suite/workspace-suite \
  -n workspace-security \
  -f values.yaml
```

### 5. Manual Kubernetes Deployment
```bash
# Apply manifests
kubectl apply -f k8s/

# Wait for deployments
kubectl wait --for=condition=available --timeout=300s \
  deployment/workspace-suite-api \
  -n workspace-security

# Check status
kubectl get deployments -n workspace-security
kubectl get pods -n workspace-security
```

## Database Setup

### PostgreSQL Initialization

```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d workspace_suite

# Run migrations
pg_restore -d workspace_suite < db/backup.sql

# Or using application migration tool
npm run migrate
```

### Database Backup
```bash
# Full backup
pg_dump -h localhost -U postgres workspace_suite > backup.sql

# Scheduled backup
0 2 * * * pg_dump -h localhost -U postgres workspace_suite | gzip > backup_$(date +\%Y-\%m-\%d).sql.gz
```

## SSL/TLS Configuration

### Using Let's Encrypt with Certbot
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Self-Signed Certificates (Development Only)
```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

## Health Checks and Monitoring

### Application Health
```bash
# Health check endpoint
curl http://localhost:3000/health

# Detailed metrics
curl http://localhost:3000/metrics
```

### Service Monitoring
```bash
# Check API status
kubectl logs -f deployment/workspace-suite-api -n workspace-security

# Monitor resource usage
kubectl top pods -n workspace-security
```

## Backup and Recovery

### Regular Backups
```bash
# Database backup
kubectl exec -it pod/postgres-0 -- pg_dump -U postgres workspace_suite > db_backup.sql

# Application data backup
kubectl cp workspace-security/workspace-suite-api:/app/data ./backup/
```

### Disaster Recovery
```bash
# Restore from backup
kubectl exec -it pod/postgres-0 -- psql -U postgres workspace_suite < db_backup.sql

# Verify restoration
kubectl logs deployment/workspace-suite-api
```

## Scaling

### Horizontal Scaling
```bash
# Scale API deployment
kubectl scale deployment workspace-suite-api --replicas=3 -n workspace-security

# Check scaling status
kubectl get pods -n workspace-security
```

### Load Balancing
- Use Ingress controller for external access
- Configure horizontal pod autoscaler (HPA)
- Set up metrics-based scaling policies

## Security Hardening

1. **Network Security**
   - Enable network policies
   - Restrict pod-to-pod communication
   - Use private subnets for databases

2. **Secret Management**
   - Use Kubernetes Secrets for sensitive data
   - Consider external secret management (Vault, AWS Secrets Manager)
   - Rotate credentials regularly

3. **Container Security**
   - Use non-root containers
   - Enable read-only root filesystem
   - Implement resource limits
   - Scan images for vulnerabilities

4. **Access Control**
   - Enable RBAC
   - Use service accounts with minimal permissions
   - Audit API access logs

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check PostgreSQL connectivity
kubectl run -it --rm debug --image=postgres:13 --restart=Never -- \
  psql -h postgres-service -U postgres -d workspace_suite
```

#### Memory Issues
```bash
# Increase memory limits
kubectl set resources deployment workspace-suite-api \
  --limits=memory=2Gi --requests=memory=512Mi
```

#### Permission Denied Errors
```bash
# Check service account permissions
kubectl describe sa workspace-suite-sa -n workspace-security

# Check role bindings
kubectl describe rolebinding workspace-suite-binding -n workspace-security
```

## Post-Deployment

### Verification Checklist
- [ ] All services running (3+ replicas each)
- [ ] Database migrations completed
- [ ] SSL certificates installed
- [ ] Health checks passing
- [ ] Logs aggregation working
- [ ] Backup jobs scheduled
- [ ] Monitoring alerts configured
- [ ] Documentation updated

### Next Steps
1. Configure initial users
2. Connect to Google Workspace
3. Run first audit
4. Set up monitoring dashboards
5. Train team on usage

## Support
For deployment support, contact: support@workspace-suite.dev
