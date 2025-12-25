# SIEM Integration Guide

Workspace Security Suite integrates with major SIEM platforms for centralized security monitoring and incident response.

## Supported SIEM Platforms

### 1. Splunk

#### Installation

```bash
# Install Splunk forwarder
sudo apt-get install splunkforwarder

# Configure inputs
sudo nano /opt/splunkforwarder/etc/apps/SplunkUniversalForwarder/local/inputs.conf
```

#### Configuration

```ini
[http://workspace_events]
disabled = 0
url = https://api.workspace-security.dev/v1/events
http_event_collector_token = <your-hec-token>
http_event_collector = false
source = workspace-security-suite
sourcetype = json
```

#### Usage

```spl
index=workspace sourcetype=json 
| stats count by severity, event_type
| timechart count by severity
```

---

### 2. ELK Stack (Elasticsearch, Logstash, Kibana)

#### Logstash Configuration

```conf
input {
  http {
    port => 5000
    codec => json
  }
}

filter {
  mutate {
    add_field => { "[@metadata][index_name]" => "workspace-security-%{+YYYY.MM.dd}" }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "%{[@metadata][index_name]}"
  }
}
```

#### Kibana Dashboard

- Create index pattern: `workspace-security-*`
- Visualize: Events by user, severity timeline, threat heatmap
- Alerts: High severity events, failed authentication attempts

---

### 3. Datadog

#### API Integration

```python
from datadog import initialize, api

options = {
    'api_key': '<your-api-key>',
    'app_key': '<your-app-key>'
}

initialize(**options)

# Send event
api.Event.create(
    title="Workspace Security Alert",
    text="Suspicious login attempt detected",
    priority="normal",
    tags=["workspace", "security"],
    alert_type="info"
)
```

#### Dashboard Setup

- Log aggregation from API
- Custom metrics: Event count, threat score
- Monitors: Alert on high severity events

---

### 4. Microsoft Sentinel

#### Azure Log Analytics Connector

```json
{
  "dataConnectorId": "workspace-security",
  "kind": "APIPolling",
  "properties": {
    "connectorUiConfig": {
      "title": "Workspace Security Suite",
      "publisher": "Workspace Security",
      "descriptionMarkdown": "Connect Workspace Security Suite to Microsoft Sentinel"
    },
    "pollingConfig": {
      "auth": {
        "authType": "APIKey"
      },
      "request": {
        "apiEndpoint": "https://api.workspace-security.dev/v1/events",
        "httpMethod": "GET",
        "rateLimitQPS": 10
      }
    }
  }
}
```

---

## API Endpoints for SIEM Integration

### Authentication

```bash
curl -X POST https://api.workspace-security.dev/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your-api-key", "secret": "your-secret"}'
```

### Events Export

```bash
curl -X GET "https://api.workspace-security.dev/v1/events?start_time=2025-01-01&end_time=2025-01-31" \
  -H "Authorization: Bearer <token>" \
  -H "Accept: application/json"
```

### Response Format

```json
{
  "events": [
    {
      "event_id": "evt_123456",
      "timestamp": "2025-01-15T10:30:00Z",
      "event_type": "auth_failed",
      "user_email": "user@example.com",
      "severity": "HIGH",
      "source_ip": "192.168.1.100",
      "description": "Failed login attempt after 3 retries"
    }
  ],
  "total": 1,
  "page": 1
}
```

---

## Real-time Webhook Integration

### Setup Webhook

```bash
curl -X POST https://api.workspace-security.dev/v1/webhooks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "SIEM Webhook",
    "url": "https://your-siem.com/webhook",
    "events": ["auth_failed", "privilege_escalation", "data_access"],
    "retry_policy": {
      "max_retries": 5,
      "backoff_multiplier": 2
    }
  }'
```

### Webhook Payload

```json
{
  "event_id": "evt_789012",
  "timestamp": "2025-01-15T11:45:00Z",
  "severity": "CRITICAL",
  "event_type": "privilege_escalation",
  "user": {
    "email": "admin@example.com",
    "department": "IT"
  },
  "details": {
    "previous_role": "User",
    "new_role": "Admin"
  }
}
```

---

## Alert Rules

### High Severity Events

Trigger alerts for:
- Privilege escalation
- Multiple failed logins (5+)
- Unusual data access patterns
- API key exposure
- Admin account changes

### Response Actions

- Auto-quarantine suspicious sessions
- Disable compromised accounts
- Create incident tickets
- Send notifications to SOC

---

## Troubleshooting

### Common Issues

1. **Connection timeout**
   - Check firewall rules
   - Verify API endpoint accessibility
   - Review SSL certificates

2. **Authentication failures**
   - Validate API key and token
   - Check token expiration
   - Verify IP whitelisting

3. **Missing events**
   - Check event filtering rules
   - Verify webhook configuration
   - Review log retention policies

---

## Performance & Compliance

- **Log Retention**: 90 days (configurable)
- **API Rate Limit**: 1000 req/min
- **Webhook Retry**: 5 attempts with exponential backoff
- **Compliance**: SOC2, ISO27001, HIPAA-ready

For support, contact: siem-support@workspace-security.dev
