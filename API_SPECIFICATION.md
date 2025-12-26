# Workspace Security Suite - API Specification

## Overview

REST API for Workspace Security Suite with OAuth 2.0 authentication.

Base URL: `https://api.workspace-security.com/v1`

## Authentication

### OAuth 2.0

```bash
POST /auth/token
Content-Type: application/json

{
  "grant_type": "client_credentials",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

Usage:
```bash
Authorization: Bearer {access_token}
```

## Core Endpoints

### 1. Incidents

#### List Incidents
```
GET /incidents
Query Parameters:
  - severity: CRITICAL,HIGH,MEDIUM,LOW
  - status: OPEN,IN_PROGRESS,CLOSED
  - limit: 1-100 (default: 20)
  - offset: pagination

Response:
{
  "data": [
    {
      "id": "INC-2024-001",
      "title": "Suspicious login attempts",
      "severity": "HIGH",
      "status": "OPEN",
      "created_at": "2024-01-15T10:30:00Z",
      "assigned_to": "john.doe@company.com"
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

#### Get Incident Details
```
GET /incidents/{incident_id}

Response:
{
  "id": "INC-2024-001",
  "title": "Suspicious login attempts",
  "description": "...",
  "severity": "HIGH",
  "status": "OPEN",
  "created_at": "2024-01-15T10:30:00Z",
  "resolved_at": null,
  "assigned_to": "john.doe@company.com",
  "events": [...],
  "timeline": [...]
}
```

#### Create Incident
```
POST /incidents
Content-Type: application/json

{
  "title": "Security alert",
  "description": "Details...",
  "severity": "HIGH",
  "source": "SIEM"
}

Response: 201 Created
```

#### Update Incident
```
PATCH /incidents/{incident_id}

{
  "status": "IN_PROGRESS",
  "assigned_to": "jane.smith@company.com",
  "notes": "Investigating..."
}
```

### 2. Events

#### Search Events
```
POST /events/search

{
  "query": "login AND failed AND 192.168.1.100",
  "filters": {
    "timestamp": {"gte": "2024-01-01T00:00:00Z"},
    "event_type": "authentication",
    "severity": "HIGH"
  },
  "limit": 100,
  "offset": 0
}

Response:
{
  "data": [...],
  "total": 1234,
  "query_time_ms": 45
}
```

### 3. Users

#### List Users
```
GET /users
Query Parameters:
  - role: ADMIN,ANALYST,USER
  - status: ACTIVE,INACTIVE,DISABLED
  - limit: 1-100

Response:
{
  "data": [
    {
      "id": "USR-001",
      "email": "john@company.com",
      "role": "ANALYST",
      "status": "ACTIVE",
      "created_at": "2023-01-01T00:00:00Z",
      "last_login": "2024-01-15T14:30:00Z"
    }
  ],
  "total": 156
}
```

#### Update User
```
PATCH /users/{user_id}

{
  "role": "ADMIN",
  "status": "ACTIVE"
}
```

### 4. Policies

#### List Policies
```
GET /policies

Response:
{
  "data": [
    {
      "id": "POL-001",
      "name": "Require MFA",
      "type": "ACCESS_CONTROL",
      "enabled": true,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2024-01-15T00:00:00Z"
    }
  ]
}
```

#### Create Policy
```
POST /policies

{
  "name": "Block VPN access",
  "type": "ACCESS_CONTROL",
  "rules": [
    {
      "condition": "location=VPN",
      "action": "DENY"
    }
  ],
  "enabled": true
}

Response: 201 Created
```

### 5. Reports

#### Generate Report
```
POST /reports

{
  "type": "COMPLIANCE",
  "framework": "SOC2",
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  }
}

Response:
{
  "id": "RPT-2024-001",
  "status": "GENERATING",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Get Report
```
GET /reports/{report_id}

Response:
{
  "id": "RPT-2024-001",
  "type": "COMPLIANCE",
  "status": "COMPLETED",
  "download_url": "https://...",
  "generated_at": "2024-01-15T10:45:00Z"
}
```

## Error Handling

Error Response Format:
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Required parameter missing",
    "details": {
      "parameter": "incident_id"
    }
  }
}
```

Common Status Codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Rate Limited (1000 req/min)
- 500: Server Error

## Rate Limiting

Headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642254000
```

## Webhook Support

Register webhook:
```
POST /webhooks

{
  "url": "https://your-app.com/webhook",
  "events": ["incident.created", "incident.updated"],
  "secret": "your_secret_key"
}
```

## SDKs

- Python: `pip install workspace-security-sdk`
- Go: `go get github.com/workspace-security/sdk-go`
- JavaScript: `npm install workspace-security-sdk`

## Changelog

### v1.0.0
- Initial release
- Core incident management
- User and policy management
- Reporting engine

---

Version: 1.0.0
Last Updated: 2024
