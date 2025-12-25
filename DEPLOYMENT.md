# Workspace Security Suite - Deployment Guide

## Quick Start (Development)

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git
- Google Cloud Project with Workspace APIs enabled

### Install & Run

```bash
# Clone repository
git clone https://github.com/romanchaa997/workspace-security-suite.git
cd workspace-security-suite

# Setup Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
cd scripts
pip install -r requirements.txt

# Setup Node.js frontend
cd ../src/workspace-sentinel
npm install
npm start
```

## Production Deployment

### Prerequisites
- Kubernetes cluster (1.20+)
- Docker & container registry
- PostgreSQL 12+ (or Cloud SQL)
- Redis 6+ (optional, for caching)
- Google Cloud Project

### Architecture

```
Internet → Cloud Load Balancer → 
  → Service (Frontend)
  → Service (API)
  → Service (Workers)
→ Cloud SQL (PostgreSQL)
→ Cloud Storage (backups)
→ Cloud Logging
```

### Step 1: Build Docker Images

```bash
# Build frontend image
docker build -t workspace-sentinel-frontend:1.0.0 src/workspace-sentinel/

# Build API image
docker build -t workspace-sentinel-api:1.0.0 .

# Push to container registry
docker tag workspace-sentinel-frontend:1.0.0 gcr.io/PROJECT_ID/workspace-sentinel-frontend:1.0.0
docker push gcr.io/PROJECT_ID/workspace-sentinel-frontend:1.0.0
```

### Step 2: Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace workspace-security

# Apply configuration
kubectl apply -f k8s/config.yaml

# Check deployment status
kubectl get pods -n workspace-security
kubectl get services -n workspace-security
```

### Step 3: Configure Google Workspace APIs

1. Go to Google Cloud Console
2. Enable Admin SDK API
3. Enable Reports API
4. Enable Drive API
5. Create service account
6. Download service account JSON
7. Share with super admin to enable domain-wide delegation

### Step 4: Configure Application

```bash
# Create ConfigMap with service account
kubectl create configmap workspace-config \
  --from-file=service-account.json \
  -n workspace-security

# Create Secrets for sensitive data
kubectl create secret generic workspace-secrets \
  --from-literal=db_password=<PASSWORD> \
  --from-literal=api_key=<API_KEY> \
  -n workspace-security
```

## Configuration

### Environment Variables

```bash
# Google Workspace
GOOGLE_WORKSPACE_DOMAIN=example.com
GOOGLE_SERVICE_ACCOUNT_EMAIL=workspace@project.iam.gserviceaccount.com

# Database
DATABASE_URL=postgresql://user:password@localhost/workspace_db

# Redis (optional)
REDIS_URL=redis://localhost:6379

# API
API_PORT=8000
API_HOST=0.0.0.0

# Frontend
REACT_APP_API_URL=https://api.example.com

# Logging
GOOGLE_CLOUD_PROJECT=project-id
LOG_LEVEL=INFO
```

## Monitoring & Logging

### Cloud Logging
```bash
# View logs
gcloud logging read "resource.type=k8s_container" \
  --limit 50 \
  --format json
```

### Cloud Monitoring
- Configure dashboards in GCP Console
- Set up alerts for critical metrics
- Monitor API latency, error rates, resource usage

## Scaling

### Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: workspace-sentinel-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: workspace-sentinel-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Security Hardening

### Network Policy
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: workspace-sentinel-network
spec:
  podSelector:
    matchLabels:
      app: workspace-sentinel
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: ingress-controller
```

### Pod Security Policy
- Run containers as non-root
- Use read-only root filesystem
- Disable privileged mode
- Drop unnecessary capabilities

### Secret Management
- Use Kubernetes Secrets for sensitive data
- Consider Google Secret Manager
- Rotate credentials regularly
- Audit secret access

## Backup & Disaster Recovery

### Database Backups
```bash
# Manual backup
pg_dump workspace_db > backup.sql

# Restore from backup
psql workspace_db < backup.sql
```

### Automated Backups
- Use Cloud SQL automated backups
- Retention: 7 days minimum
- Test recovery procedures monthly

## Troubleshooting

### Check Pod Status
```bash
kubectl describe pod <POD_NAME> -n workspace-security
kubectl logs <POD_NAME> -n workspace-security
```

### Database Connection Issues
```bash
kubectl exec -it <POD_NAME> -n workspace-security -- psql $DATABASE_URL
```

### API Health Check
```bash
curl -X GET http://localhost:8000/health
```

## Support & Community

- 📖 Documentation: See `/docs/`
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 🤝 Contributing: See CONTRIBUTING.md
