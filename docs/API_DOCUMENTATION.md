# Workspace Security Suite - API Documentation

## Base URL
```
https://api.workspace-security-suite.io/api/v1
```

## Authentication

All API requests require JWT token authentication.

### Getting a Token

**POST /auth/login**

```bash
curl -X POST https://api.workspace-security-suite.io/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "pass123"}'
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": "24h",
  "user": {"id": "user-123", "email": "user@example.com", "role": "admin"}
}
```

## Core Endpoints

### Workspaces

#### List Workspaces
**GET /workspaces** - Get all connected workspaces

#### Get Workspace Details
**GET /workspaces/:workspaceId** - Get specific workspace information

#### Create Workspace Connection
**POST /workspaces** - Connect new Google Workspace

### Audits

#### Run Audit
**POST /workspaces/:workspaceId/audits** - Trigger security audit

#### Get Audit Results
**GET /audits/:auditId** - Retrieve audit results and findings

### Reports

#### Generate Report
**POST /workspaces/:workspaceId/reports** - Generate compliance or audit report

#### Get Report Status
**GET /reports/:reportId** - Check report generation status

### Compliance

#### Get Compliance Status
**GET /workspaces/:workspaceId/compliance** - Check framework compliance

## Error Handling

Standard HTTP status codes are used:
- 200 OK - Successful request
- 400 Bad Request - Invalid parameters
- 401 Unauthorized - Missing/invalid token
- 403 Forbidden - Insufficient permissions
- 404 Not Found - Resource not found
- 429 Too Many Requests - Rate limit exceeded
- 500 Server Error

## Rate Limiting

1000 requests per hour per API key.

Headers:
- `X-RateLimit-Limit`: 1000
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp reset time

## Webhooks

Supported events:
- `audit.started`
- `audit.completed`
- `finding.discovered`
- `workspace.connected`
- `workspace.disconnected`

## SDK Support

SDKs available for:
- Python
- JavaScript/Node.js
- Go
- Java

## Support

For API support: api-support@workspace-suite.dev
