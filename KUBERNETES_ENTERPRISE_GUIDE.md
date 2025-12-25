# Kubernetes Enterprise Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying Workspace Security Suite on enterprise Kubernetes clusters with high availability, auto-scaling, and advanced security configurations.

## Prerequisites

- Kubernetes 1.24+ cluster
- kubectl configured with cluster access
- Helm 3.10+
- PostgreSQL 14+ (managed or self-hosted)
- Redis 7+ (managed or self-hosted)
- SSL/TLS certificates

## Quick Start

### 1. Create Namespace

```bash
kubectl create namespace workspace-security
kubectl label namespace workspace-security tier=production
```

### 2. Install Helm Chart

```bash
# Add Helm repository
helm repo add workspace-security https://helm.workspace-security.dev
helm repo update

# Install release
helm install workspace-security workspace-security/workspace-security \
  --namespace workspace-security \
  --values values-prod.yaml
```

### 3. Verify Deployment

```bash
kubectl get pods -n workspace-security
kubectl get svc -n workspace-security
kubectl logs -n workspace-security -f deployment/workspace-security-api
```

---

## Production Configuration

### values-prod.yaml

```yaml
replicaCount: 3

image:
  repository: workspace-security/suite
  tag: v1.0.0
  pullPolicy: IfNotPresent

resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
  hosts:
    - host: api.workspace-security.prod
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: workspace-security-tls
      hosts:
        - api.workspace-security.prod

persistence:
  enabled: true
  size: 100Gi
  storageClassName: fast-ssd

postgresql:
  external: true
  host: postgres.c.workspace-prod.internal
  port: 5432
  database: workspace_security
  
redis:
  external: true
  host: redis.c.workspace-prod.internal
  port: 6379

monitoring:
  prometheus:
    enabled: true
    interval: 30s
  alerts:
    enabled: true
    channels:
      - pagerduty
      - slack
```

---

## High Availability Setup

### 1. Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: workspace-security-pdb
  namespace: workspace-security
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: workspace-security
```

### 2. Affinity Rules

```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - workspace-security
        topologyKey: kubernetes.io/hostname
```

### 3. Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: workspace-security-netpol
spec:
  podSelector:
    matchLabels:
      app: workspace-security
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 6379
```

---

## Security Hardening

### 1. RBAC Configuration

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: workspace-security-role
  namespace: workspace-security
rules:
- apiGroups: [""]
  resources: ["secrets", "configmaps"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: workspace-security-rolebinding
  namespace: workspace-security
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: workspace-security-role
subjects:
- kind: ServiceAccount
  name: workspace-security
  namespace: workspace-security
```

### 2. Pod Security Policy

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: workspace-security-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'MustRunAs'
  fsGroup:
    rule: 'MustRunAs'
  readOnlyRootFilesystem: false
```

### 3. Secrets Management

```bash
# Using Sealed Secrets
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/

# Create sealed secret
echo -n 'mypassword' | kubectl create secret generic mysecret --dry-run=client --from-file=/dev/stdin -o yaml | kubeseal -f -
```

---

## Monitoring & Logging

### 1. Prometheus Operator Integration

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: workspace-security
  namespace: workspace-security
spec:
  selector:
    matchLabels:
      app: workspace-security
  endpoints:
  - port: metrics
    interval: 30s
```

### 2. ELK Stack Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: filebeat-config
  namespace: workspace-security
data:
  filebeat.yml: |
    filebeat.inputs:
    - type: container
      paths:
        - '/var/log/containers/*workspace-security*.log'
      processors:
        - add_kubernetes_metadata:
            in_cluster: true
    
    output.elasticsearch:
      hosts: ["elasticsearch:9200"]
      index: "workspace-security-%{+yyyy.MM.dd}"
```

---

## Scaling & Performance

### 1. Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: workspace-security-hpa
  namespace: workspace-security
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: workspace-security
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. Vertical Pod Autoscaler

```bash
# Install VPA
kubectl apply -f https://github.com/kubernetes/autoscaler/releases/vpa-v0.14.3.yaml

# Configure VPA
kubectl label node NODE_NAME kubernetes.io/hostname=NODE_NAME
```

---

## Disaster Recovery

### 1. Backup Strategy

```bash
# Velero backup setup
velero install --provider aws \
  --bucket workspace-security-backups \
  --secret-file ./credentials-velero \
  --use-volume-snapshots=true

# Create scheduled backup
velero schedule create daily-backup \
  --schedule="0 2 * * *" \
  --include-namespaces workspace-security
```

### 2. Restore Procedure

```bash
# List available backups
velero backup get

# Restore from backup
velero restore create --from-backup=daily-backup-20250115

# Monitor restore
velero restore describe daily-backup-20250115
```

---

## Troubleshooting

### Common Issues

**1. Pods not starting**
```bash
kubectl describe pod <pod-name> -n workspace-security
kubectl logs <pod-name> -n workspace-security
```

**2. Memory leaks**
```bash
kubectl top pods -n workspace-security
kubectl set resources deployment/workspace-security -n workspace-security --limits=memory=2Gi
```

**3. Network connectivity**
```bash
kubectl exec -it <pod-name> -n workspace-security -- nc -zv postgres 5432
kubectl exec -it <pod-name> -n workspace-security -- nc -zv redis 6379
```

---

## Cost Optimization

- Use spot instances for non-critical workloads
- Enable cluster autoscaling
- Implement resource quotas and limits
- Use multi-tier storage (SSD for hot, standard for cold)
- Schedule non-urgent jobs during off-peak hours

---

## Support

For Kubernetes deployment support: k8s-support@workspace-security.dev
