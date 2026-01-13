---
name: servicenow-itsm
description: ServiceNow ITSM operations for managing incidents, changes, problems, service catalog, CMDB, and companies. Use when working with ServiceNow tickets, querying ITSM data, or automating IT service management workflows.
---

# ServiceNow ITSM Skill

This skill provides comprehensive ServiceNow ITSM integration through Python. It enables incident management, change management, problem management, service catalog operations, CMDB queries, and company/organization management.

## Configuration

Create a `.claude/env` file with your ServiceNow credentials:

```
SERVICENOW_INSTANCE=https://your-instance.service-now.com
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password
```

Alternatively, you can use OAuth authentication:

```
SERVICENOW_INSTANCE=https://your-instance.service-now.com
SERVICENOW_CLIENT_ID=your-client-id
SERVICENOW_CLIENT_SECRET=your-client-secret
```

Or, you can use API key authentication:

```
SERVICENOW_INSTANCE=https://your-instance.service-now.com
SERVICENOW_API_KEY=your-api-key
```

#### API Key Format Requirements

ServiceNow API keys are typically Base64-encoded strings. The format varies by ServiceNow version:

| ServiceNow Version | Key Format | Typical Length |
|-------------------|------------|----------------|
| **San Diego and later** | Base64-encoded UUID | 32-44 characters |
| **Rome and earlier** | Alphanumeric string | 20-40 characters |

**Valid characters:** `A-Z`, `a-z`, `0-9`, `+`, `/`, `=` (for Base64 padding)

**Note:** API key format and length may vary based on your instance configuration and any custom authentication plugins. Consult your ServiceNow administrator for instance-specific requirements.

The credentials require appropriate ServiceNow roles for the operations you intend to perform (e.g., `itil`, `itil_admin`, `catalog_admin`).

### Authentication Method Recommendations

| Environment | Recommended Method | Rationale |
|-------------|-------------------|-----------|
| **Development** | Username/Password | Simpler setup for local development and testing. Easier to rotate credentials during development cycles. |
| **Production** | OAuth 2.0 | More secure token-based authentication. Supports token refresh without exposing credentials. Better audit trail and access control. |
| **Service Integrations** | API Key | Ideal for server-to-server integrations and automated workflows. Simpler than OAuth for non-interactive scenarios. No token refresh management required. |

**Note:** For production environments, OAuth 2.0 is strongly recommended as it provides better security through short-lived tokens, avoids storing plain-text passwords, and integrates better with enterprise identity management systems.

### API Key Security Considerations

When using API key authentication, follow these security best practices:

| Practice | Recommendation | Details |
|----------|----------------|---------|
| **Key Rotation** | Rotate every 90 days | Limits exposure from compromised credentials |
| **Least Privilege** | Minimum required permissions | Avoid admin-level keys for routine operations |
| **Secure Storage** | Use environment variables or secret managers | Never commit API keys to version control. Use HashiCorp Vault, AWS Secrets Manager, or similar |
| **Access Logging** | Enable API access logging | Monitor key usage and detect anomalies in ServiceNow |
| **IP Restrictions** | Configure IP allowlists | Restrict API key usage to known source addresses where possible |
| **Separate Keys** | Distinct key per integration | Enables granular access control and easier revocation if needed |

## Available Operations

### Incidents

Read the specific skill file for detailed usage and examples.

- `skills/incidents/create-incident.md` - Create new incidents with priority, category, and assignment
- `skills/incidents/get-incident.md` - Retrieve incident details by number or sys_id
- `skills/incidents/update-incident.md` - Update incident fields, state, or assignment
- `skills/incidents/search-incidents.md` - Search incidents using encoded queries
- `skills/incidents/resolve-incident.md` - Resolve or close incidents with resolution notes

### Changes

- `skills/changes/create-change.md` - Create change requests (normal, standard, emergency)
- `skills/changes/get-change.md` - Retrieve change request details
- `skills/changes/update-change.md` - Update change request fields and state
- `skills/changes/search-changes.md` - Search change requests by criteria

### Problems

- `skills/problems/create-problem.md` - Create problem records
- `skills/problems/get-problem.md` - Retrieve problem details
- `skills/problems/update-problem.md` - Update problem fields and root cause
- `skills/problems/search-problems.md` - Search problem records

### Service Catalog

- `skills/catalog/list-catalog-items.md` - List available catalog items
- `skills/catalog/get-catalog-item.md` - Get catalog item details and variables
- `skills/catalog/submit-request.md` - Submit service catalog requests
- `skills/catalog/get-request-status.md` - Check request item status

### CMDB

- `skills/cmdb/query-cis.md` - Query configuration items
- `skills/cmdb/get-ci.md` - Get CI details and relationships
- `skills/cmdb/update-ci.md` - Update CI attributes
- `skills/cmdb/get-relationships.md` - Get CI relationships and dependencies

### Companies

- `skills/companies/list-companies.md` - List company records
- `skills/companies/get-company.md` - Get company details
- `skills/companies/search-companies.md` - Search companies by criteria

## Usage Pattern

1. Identify the operation category (incidents, changes, problems, catalog, cmdb, companies)
2. Read the corresponding skill file for detailed parameters and examples
3. Use the appropriate Python script with required parameters

For ServiceNow encoded query syntax and examples, see `skills/common/encoded-queries.md`.

## Error Handling Patterns

### ServiceNow API Error Responses

ServiceNow REST APIs return standard HTTP status codes along with error details in the response body. Understanding these patterns helps with debugging and implementing robust error handling.

#### Common HTTP Status Codes

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

#### Error Response Format

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

#### Retry Strategies for Transient Failures

Not all errors should trigger immediate retries. Use the following guidance:

| Error Type | Retry? | Strategy |
|------------|--------|----------|
| `401` Unauthorized | No | Re-authenticate, refresh OAuth token |
| `403` Forbidden | No | Check user permissions and ACLs |
| `404` Not Found | No | Verify record exists before retrying |
| `429` Rate Limited | Yes | Use exponential backoff with jitter |
| `500` Server Error | Yes | Retry with exponential backoff (max 3 attempts) |
| `503` Service Unavailable | Yes | Wait and retry, check instance status page |

**Recommended Retry Pattern:**

```python
# NOTE: This is an illustrative pattern - adapt exception handling to your implementation.
# RetryableError represents a custom exception you would define for your use case,
# e.g., class RetryableError(Exception): pass

import time
import random

def retry_with_backoff(func, max_retries=3, base_delay=1):
    """
    Retry a function with exponential backoff and jitter.
    """
    for attempt in range(max_retries):
        try:
            return func()
        except RetryableError as e:  # Replace with your specific retryable exception(s)
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

## Rate Limiting

### ServiceNow API Rate Limits

ServiceNow implements rate limiting to ensure fair resource allocation and platform stability. Understanding these limits is crucial for building reliable integrations.

#### Default Rate Limits

| Limit Type | Default Value | Scope |
|------------|---------------|-------|
| **Per-user rate limit** | 500 requests/minute | Per authenticated user |
| **Concurrent requests** | 10-25 simultaneous | Per user session |
| **Batch operations** | Varies by instance | Contact ServiceNow admin |

**Note:** Actual limits vary by instance configuration, licensing, and ServiceNow version. Contact your ServiceNow administrator for specific limits.

#### Detecting Rate Limiting

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
# NOTE: This is an illustrative pattern demonstrating rate limit handling logic.
# Integrate this into your retry loop, passing the current attempt number.

def handle_rate_limit(response, attempt_number=0):
    """
    Handle rate limit response with appropriate backoff.

    Args:
        response: The HTTP response object from the rate-limited request.
        attempt_number: Current retry attempt (0-indexed) for exponential backoff calculation.
    """
    retry_after = response.headers.get('Retry-After')
    if retry_after:
        wait_time = int(retry_after)
    else:
        # Default exponential backoff (capped at 60 seconds)
        wait_time = min(60, 2 ** attempt_number)

    # Add jitter (10-20% randomization) to prevent thundering herd
    jitter = wait_time * random.uniform(0.1, 0.2)
    time.sleep(wait_time + jitter)
```

### Rate Limiting Across Multiple Users

For applications serving multiple users:

- Each authenticated user has their own rate limit quota
- Use service accounts judiciously for shared operations
- Consider distributing requests across multiple service accounts for high-volume scenarios
- Implement application-level rate limiting to stay well under ServiceNow limits
