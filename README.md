# ServiceNow ITSM Skills

Claude Code skills for ServiceNow ITSM operations - query incidents, changes, problems, catalog, CMDB, and companies.

## Table of Contents

- [Overview](#overview)
- [Configuration](#configuration)
- [Authentication Methods](#authentication-methods)
- [Security Considerations](#security-considerations)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Available Operations](#available-operations)

## Overview

This skill provides comprehensive ServiceNow ITSM integration through Python. It enables incident management, change management, problem management, service catalog operations, CMDB queries, and company/organization management.

## Configuration

Create a `.claude/env` file with your ServiceNow credentials using one of the authentication methods below.

### Basic Authentication (Username/Password)

```
SERVICENOW_INSTANCE=https://your-instance.service-now.com
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password
```

### OAuth 2.0 Authentication

```
SERVICENOW_INSTANCE=https://your-instance.service-now.com
SERVICENOW_CLIENT_ID=your-client-id
SERVICENOW_CLIENT_SECRET=your-client-secret
```

### API Key Authentication

API key authentication is ideal for server-to-server integrations, automated workflows, and service accounts where interactive login is not possible or desired.

```
SERVICENOW_INSTANCE=https://your-instance.service-now.com
SERVICENOW_API_KEY=your-api-key
```

**When to use API Key authentication:**
- Automated CI/CD pipelines interacting with ServiceNow
- Background services and cron jobs
- Integration middleware and iPaaS platforms
- Scenarios where OAuth token refresh management adds unnecessary complexity

**Generating an API Key:**
1. Navigate to your ServiceNow instance's API key management interface (see version-specific paths below)
2. Create a new API key and associate it with an appropriate service account
3. Copy the generated key value (it will only be shown once)

**Version-Specific API Key Provisioning Paths:**

| ServiceNow Version | Navigation Path | Notes |
|-------------------|-----------------|-------|
| **Washington DC and later** | **System Security > API Keys** | Primary method. Dedicated API key management module with enhanced security features including automatic expiration policies. |
| **Vancouver, Utah** | **System Security > API Keys** | Available but may require activation via plugin (com.snc.platform.security.api_key). |
| **Tokyo, San Diego, Rome** | **System OAuth > Application Registry** | Create an OAuth API endpoint for external clients. API keys are managed as part of OAuth client credentials. |
| **Quebec and earlier** | **System OAuth > Application Registry** | OAuth-based API key management only. Dedicated API key module not available. |

**Key differences between versions:**
- **San Diego and later**: Support for API key expiration policies, allowing automatic key invalidation after a configured period
- **Tokyo and later**: Enhanced audit logging for API key usage, including source IP tracking
- **Washington DC and later**: Native key rotation reminders and integration with ServiceNow's Security Operations module

Consult your ServiceNow administrator for instance-specific API key provisioning procedures, as the process may vary based on your ServiceNow version, installed plugins, and security configuration.

The credentials require appropriate ServiceNow roles for the operations you intend to perform (e.g., `itil`, `itil_admin`, `catalog_admin`).

## Authentication Methods

### Recommended Authentication by Environment

| Environment | Recommended Method | Rationale |
|-------------|-------------------|-----------|
| **Development** | Username/Password | Simpler setup for local development and testing. Easier to rotate credentials during development cycles. |
| **Production** | OAuth 2.0 | More secure token-based authentication. Supports token refresh without exposing credentials. Better audit trail and access control. |
| **Service Integrations** | API Key | Ideal for server-to-server integrations and automated workflows. Simpler than OAuth for non-interactive scenarios. No token refresh management required. |

**Note:** For production environments, OAuth 2.0 is strongly recommended as it provides better security through short-lived tokens, avoids storing plain-text passwords, and integrates better with enterprise identity management systems.

### API Key Format Requirements

ServiceNow API keys are typically Base64-encoded strings. The format varies by ServiceNow version:

| ServiceNow Version | Key Format | Typical Length |
|-------------------|------------|----------------|
| **San Diego and later** | Base64-encoded UUID | 32-44 characters |
| **Rome and earlier** | Alphanumeric string | 20-40 characters |

**Valid characters:** `A-Z`, `a-z`, `0-9`, `+`, `/`, `=` (for Base64 padding)

**Note:** API key format and length may vary based on your instance configuration and any custom authentication plugins. Consult your ServiceNow administrator for instance-specific requirements.

## Security Considerations

### Authentication Method Comparison

When choosing an authentication method, consider the following security trade-offs:

| Aspect | Basic Auth | OAuth 2.0 | API Key |
|--------|------------|-----------|---------|
| **Security Level** | Low | High | Medium |
| **Credential Exposure** | Password transmitted with each request | Only tokens transmitted; credentials exchanged once | Key transmitted with each request |
| **Token/Key Lifetime** | N/A (password-based) | Short-lived tokens (minutes to hours) | Long-lived until rotated |
| **Revocation** | Requires password change | Tokens can be individually revoked | Key can be revoked without affecting user password |
| **Setup Complexity** | Simple | Complex (OAuth app registration required) | Simple |
| **Best For** | Development/testing only | Production applications | Server-to-server integrations |
| **MFA Support** | Limited | Full support | N/A (service accounts) |
| **Audit Trail** | Basic | Comprehensive | Good |

### API Key Security Best Practices

When using API key authentication, follow these security best practices:

| Practice | Recommendation | Details |
|----------|----------------|---------|
| **Key Rotation** | Rotate every 90 days | Limits exposure from compromised credentials |
| **Least Privilege** | Minimum required permissions | Avoid admin-level keys for routine operations |
| **Secure Storage** | Use environment variables or secret managers | Never commit API keys to version control. Use HashiCorp Vault, AWS Secrets Manager, or similar |
| **Access Logging** | Enable API access logging | Monitor key usage and detect anomalies in ServiceNow |
| **IP Restrictions** | Configure IP allowlists | Restrict API key usage to known source addresses where possible |
| **Separate Keys** | Distinct key per integration | Enables granular access control and easier revocation if needed |

### API Key Rotation Recommendations

Regular API key rotation is a critical security practice. The recommended rotation frequency depends on your environment's risk profile and compliance requirements:

| Environment | Rotation Frequency | Rationale |
|-------------|-------------------|-----------|
| **High-security / Regulated** | Every 30 days | Compliance requirements (PCI-DSS, HIPAA, SOX) often mandate frequent rotation. Minimizes exposure window for compromised keys. |
| **Standard Production** | Every 90 days | Industry best practice balancing security with operational overhead. Aligns with typical password rotation policies. |
| **Development / Testing** | Every 180 days | Lower risk environment with limited data access. Rotate immediately if key is exposed in logs or version control. |
| **Emergency Rotation** | Immediately | Required when: key exposure suspected, team member with access departs, security incident occurs, or anomalous API activity detected. |

**Automated Rotation Capabilities in ServiceNow:**

| ServiceNow Version | Automation Features |
|-------------------|---------------------|
| **Washington DC and later** | Native key expiration policies with configurable validity periods (30, 60, 90 days). Automatic notification workflows 7-14 days before expiration. Integration with ServiceNow Flow Designer for custom rotation workflows. |
| **Vancouver, Utah** | Key expiration can be configured via business rules. Manual rotation with ServiceNow Orchestration or Flow Designer automation possible. |
| **Tokyo and earlier** | No native expiration. Implement rotation via scheduled jobs or external automation (ServiceNow Orchestration, external scripts, or CI/CD pipelines). |

**Rotation Best Practices:**
1. **Overlap period**: When rotating keys, maintain both old and new keys active for 24-48 hours to allow dependent systems to update
2. **Automation**: Use CI/CD pipelines or secret management tools (HashiCorp Vault, AWS Secrets Manager) to automate key rotation
3. **Monitoring**: Set up alerts for keys approaching expiration and track rotation compliance
4. **Documentation**: Maintain a key inventory with creation dates, owners, and rotation schedules
5. **Testing**: Validate new keys in a non-production environment before rotating production credentials

### General Security Guidelines

1. **Never commit credentials to version control** - Use environment variables or secret managers
2. **Rotate credentials regularly** - Especially after team member departures
3. **Use least privilege principle** - Grant only the permissions necessary for the integration
4. **Monitor API usage** - Set up alerts for unusual activity patterns
5. **Secure your `.claude/env` file** - Ensure it's excluded from version control via `.gitignore`

## Error Handling

### ServiceNow API Error Responses

ServiceNow REST APIs return standard HTTP status codes along with error details in the response body. Understanding these patterns helps with debugging and implementing robust error handling.

### Common HTTP Status Codes

| Status Code | Meaning | Typical Cause |
|-------------|---------|---------------|
| `400` | Bad Request | Invalid query syntax, malformed JSON, or missing required fields |
| `401` | Unauthorized | Invalid credentials, expired token, or missing authentication |
| `403` | Forbidden | User lacks required role or ACL prevents access |
| `404` | Not Found | Record doesn't exist or table name is incorrect |
| `405` | Method Not Allowed | HTTP method not supported for the endpoint |
| `429` | Too Many Requests | Rate limit exceeded (see Rate Limiting section) |
| `500` | Internal Server Error | ServiceNow server-side error |
| `503` | Service Unavailable | Instance is down or undergoing maintenance |

### Error Response Format

ServiceNow returns errors in the following JSON structure:

```json
{
  "error": {
    "message": "Human-readable error description",
    "detail": "Additional technical details about the error"
  },
  "status": "failure"
}
```

### Retry Strategies for Transient Failures

Not all errors should trigger immediate retries. Use the following guidance:

| Error Type | Retry? | Strategy |
|------------|--------|----------|
| `401` Unauthorized | No | Re-authenticate, refresh OAuth token |
| `403` Forbidden | No | Check user permissions and ACLs |
| `404` Not Found | No | Verify record exists before retrying |
| `429` Rate Limited | Yes | Use exponential backoff with jitter |
| `500` Server Error | Yes | Retry with exponential backoff (max 3 attempts) |
| `503` Service Unavailable | Yes | Wait and retry, check instance status page |

### Recommended Retry Pattern

```python
# Integration with ServiceNow Skills: This pattern uses the exception classes
# defined in scripts/servicenow_api.py for proper error handling.

import time
import random
from scripts.servicenow_api import (
    ServiceNowError,
    RateLimitError,
    AuthenticationError,
    create_client
)

def retry_with_backoff(func, max_retries=3, base_delay=1):
    """
    Retry a function with exponential backoff and jitter.

    Retries on RateLimitError and general ServiceNowError (5xx errors).
    Does not retry on AuthenticationError (401/403) as these require
    credential fixes, not retries.
    """
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            # Always retry rate limit errors with backoff
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
        except ServiceNowError as e:
            # Only retry 5xx server errors
            if e.status_code and 500 <= e.status_code < 600:
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
            else:
                raise  # Don't retry 4xx client errors
```

## Rate Limiting

### ServiceNow API Rate Limits

ServiceNow implements rate limiting to ensure fair resource allocation and platform stability. Understanding these limits is crucial for building reliable integrations.

### Default Rate Limits

| Limit Type | Default Value | Scope |
|------------|---------------|-------|
| **Per-user rate limit** | 500 requests/minute | Per authenticated user |
| **Concurrent requests** | 10-25 simultaneous | Per user session |
| **Batch operations** | Varies by instance | Contact ServiceNow admin |

**Note:** Actual limits vary by instance configuration, licensing, and ServiceNow version. Contact your ServiceNow administrator for specific limits.

### Detecting Rate Limiting

When rate limited, ServiceNow returns:

- **HTTP Status Code:** `429 Too Many Requests`
- **Retry-After Header:** Seconds to wait before retrying (when available)

```json
{
  "error": {
    "message": "Rate limit exceeded",
    "detail": "Too many requests. Please wait before retrying."
  },
  "status": "failure"
}
```

### Best Practices for Avoiding Throttling

1. **Batch Operations When Possible**
   - Use bulk APIs for multiple record operations
   - Combine related queries to reduce API calls

2. **Implement Request Queuing**
   - Queue requests and process at a controlled rate
   - Avoid burst patterns during peak hours

3. **Cache Frequently Accessed Data**
   - Cache reference data (e.g., user lookups, category lists)
   - Set appropriate TTLs based on data volatility

4. **Use Pagination Efficiently**
   - Fetch only needed fields with `sysparm_fields`
   - Use reasonable `sysparm_limit` values (100-1000)
   - Avoid fetching all records when filters suffice

5. **Monitor Your Usage**
   - Track API call patterns in your application
   - Set up alerts for approaching rate limits

### Handling Rate Limit Responses

When receiving a `429` response:

1. **Read the Retry-After header** if present
2. **Implement exponential backoff** starting at 1 second
3. **Add jitter** to prevent thundering herd problems
4. **Log rate limit events** for capacity planning

```python
# Integration with ServiceNow Skills: This pattern demonstrates handling
# RateLimitError from scripts/servicenow_api.py with Retry-After header support.

import time
import random
from scripts.servicenow_api import RateLimitError, create_client

def handle_rate_limit_with_retry(client_func, max_retries=3):
    """
    Execute a ServiceNow client function with rate limit handling.

    Args:
        client_func: A callable that invokes the ServiceNow client.
        max_retries: Maximum number of retry attempts.

    Returns:
        The result from the client function.

    Raises:
        RateLimitError: If rate limit is still exceeded after max_retries.
    """
    for attempt in range(max_retries):
        try:
            return client_func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise

            # Check for Retry-After in the error details if available
            wait_time = min(60, 2 ** attempt)  # Default exponential backoff

            # Add jitter (10-20% randomization) to prevent thundering herd
            jitter = wait_time * random.uniform(0.1, 0.2)
            time.sleep(wait_time + jitter)

# Example usage with the ServiceNow client:
# client = create_client()
# result = handle_rate_limit_with_retry(
#     lambda: client.get('incident', query='state=1', limit=100)
# )
```

### Rate Limiting Across Multiple Users

For applications serving multiple users:

- Each authenticated user has their own rate limit quota
- Use service accounts judiciously for shared operations
- Consider distributing requests across multiple service accounts for high-volume scenarios
- Implement application-level rate limiting to stay well under ServiceNow limits

## Available Operations

For detailed usage and examples, see the individual skill documentation files:

### Incidents
- `skills/incidents/get-incident.md` - Retrieve incident details by number or sys_id
- `skills/incidents/query-incidents.md` - Search incidents using encoded queries

### Changes
- `skills/changes/get-change.md` - Retrieve change request details
- `skills/changes/query-changes.md` - Search change requests by criteria

### Problems
- `skills/problems/get-problem.md` - Retrieve problem details
- `skills/problems/query-problems.md` - Search problem records

### Service Catalog
- `skills/catalog/browse-catalog.md` - Browse available catalog items
- `skills/catalog/search-catalog.md` - Search catalog items
- `skills/catalog/request-status.md` - Check request item status

### CMDB
- `skills/cmdb/query-cis.md` - Query configuration items
- `skills/cmdb/get-ci.md` - Get CI details
- `skills/cmdb/ci-relationships.md` - Get CI relationships and dependencies

### Companies
- `skills/companies/get-company.md` - Get company details
- `skills/companies/query-companies.md` - Search companies by criteria
