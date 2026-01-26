# Get Problem

Retrieve problem details from ServiceNow by sys_id or problem number.

> **Navigation:** [Back to Skill Index](../../SKILL.md) | [Query Problems](./query-problems.md)

## Table of Contents

- [Script](#script)
- [Operations](#operations)
  - [Get by sys_id](#get-by-sys_id)
  - [Get by Number](#get-by-number)
- [Parameters](#parameters)
  - [Fields Parameter](#fields-parameter)
  - [Display Value Parameter](#display-value-parameter)
- [Output](#output)
- [Workaround Best Practices](#workaround-best-practices)
- [Related Domains](#related-domains)
  - [Incident Management](#incident-management)
  - [Change Management](#change-management)
  - [Service Catalog](#service-catalog)
- [Errors](#errors)

## Script

```bash
python scripts/problems.py
```

## Operations

### Get by sys_id

Retrieve a problem using its unique system identifier.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"get"` |
| `sys_id` | Yes | The sys_id of the problem |
| `fields` | No | Comma-separated list of fields to return |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Example

```bash
echo '{
  "action": "get",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0"
}' | python scripts/problems.py
```

Get specific fields only:

```bash
echo '{
  "action": "get",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0",
  "fields": "number,short_description,state,priority,known_error"
}' | python scripts/problems.py
```

### Get by Number

Retrieve a problem using its problem number (e.g., PRB0010001).

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"get_by_number"` |
| `number` | Yes | The problem number (e.g., "PRB0010001") |
| `fields` | No | Comma-separated list of fields to return |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Example

```bash
echo '{
  "action": "get_by_number",
  "number": "PRB0010001"
}' | python scripts/problems.py
```

Get with display values:

```bash
echo '{
  "action": "get_by_number",
  "number": "PRB0010001",
  "display_value": "true"
}' | python scripts/problems.py
```

## Parameters

### Fields Parameter

Specify which fields to include in the response. Common problem fields:

- `sys_id` - Unique system identifier
- `number` - Problem number (e.g., PRB0010001)
- `short_description` - Brief summary of the problem
- `description` - Detailed description
- `state` - Current state (1=Open, 2=Known Error, 3=Pending Change, 4=Closed/Resolved, 5=Closed/Cancelled)
- `problem_state` - Problem state value
- `priority` - Priority level (1=Critical, 2=High, 3=Moderate, 4=Low, 5=Planning)
- `assignment_group` - Assigned group
- `assigned_to` - Assigned user
- `opened_at` - When the problem was opened
- `opened_by` - Who opened the problem
- `resolved_at` - When the problem was resolved
- `resolved_by` - Who resolved the problem
- `closed_at` - When the problem was closed
- `closed_by` - Who closed the problem
- `close_notes` - Close notes
- `active` - Whether the problem is active
- `known_error` - Whether this is a known error
- `first_reported_by_task` - First task that reported this problem
- `cause_notes` - Root cause analysis notes
- `fix_notes` - Fix/resolution notes
- `workaround` - Workaround description (see [Workaround Best Practices](#workaround-best-practices) below)
- `major_problem` - Whether this is a major problem
- `resolution_code` - Resolution code
- `related_incidents` - Related incident count
- `sys_created_on` - Record creation timestamp
- `sys_updated_on` - Record last update timestamp

### Display Value Parameter

Controls how reference fields are returned:

- `false` (default) - Returns sys_id values for reference fields
- `true` - Returns display values (human-readable names)
- `all` - Returns both sys_id and display value

## Output

JSON object containing the problem record:

```json
{
  "sys_id": "a1b2c3d4e5f6g7h8i9j0",
  "number": "PRB0010001",
  "short_description": "Recurring email delivery failures",
  "description": "Multiple users reporting intermittent email delivery issues",
  "state": "2",
  "priority": "2",
  "assignment_group": {
    "link": "https://instance.service-now.com/api/now/table/sys_user_group/abc123",
    "value": "abc123"
  },
  "assigned_to": {
    "link": "https://instance.service-now.com/api/now/table/sys_user/def456",
    "value": "def456"
  },
  "opened_at": "<timestamp>",
  "active": "true",
  "known_error": "true",
  "workaround": "Users can resend failed emails after 5 minutes",
  "cause_notes": "Mail server queue overflow during peak hours",
  "related_incidents": "5"
}
```

## Workaround Best Practices

The `workaround` field is critical for Known Error management. Follow these best practices when documenting workarounds:

1. **Be Specific and Actionable**: Write clear, step-by-step instructions that users or support staff can follow immediately.

2. **Include Prerequisites**: Note any permissions, tools, or access required to execute the workaround.

3. **Document Limitations**: Clearly state what the workaround does and doesn't address, and any potential side effects.

4. **Keep It Updated**: Regularly review and update workarounds as new information becomes available or the underlying issue evolves.

5. **Link to Knowledge Articles**: If a detailed KB article exists, reference it in the workaround field for comprehensive guidance.

**Example of a well-documented workaround:**
```
Temporary fix for email delivery delays:
1. Clear the user's Outlook cache: File > Options > Advanced > Clear Cache
2. Restart Outlook
3. Wait 5 minutes for sync to complete
Note: This resolves 80% of reported cases. If issue persists, escalate to Email Team.
Limitation: Does not address root cause (mail server queue overflow during peak hours).
```

## Related Domains

Problems often intersect with other ServiceNow domains. Consider these related skills for comprehensive problem management:

### Incident Management
Problems are often linked to incidents. Use these related skills to work with associated records:
- **[Get Incident](../incidents/get-incident.md)** - Retrieve details of incidents related to this problem
- **[Query Incidents](../incidents/query-incidents.md)** - Search for incidents that may be associated with the problem

> **Tip:** Use the `related_incidents` field to see how many incidents are linked to a problem, then use the incidents skill to investigate them further.

### Change Management
When a problem requires a permanent fix, it typically triggers a change request:
- **[Get Change Request](../changes/get-change.md)** - Retrieve details of change requests created to resolve the problem
- **[Query Change Requests](../changes/query-changes.md)** - Search for changes related to problem resolution

> **Tip:** Check the `state` field for "Pending Change" (state=3) to identify problems awaiting a change implementation.

### Service Catalog
Problems may be resolved through standard service requests or may trigger catalog items for remediation:
- **[Browse Catalog](../catalog/browse-catalog.md)** - Browse available service catalog items that may help resolve issues
- **[Search Catalog](../catalog/search-catalog.md)** - Search for specific service offerings related to problem resolution
- **[Request Status](../catalog/request-status.md)** - Track the status of service requests created as part of problem resolution

## Errors

The script will output error details to stderr and exit with non-zero status if:

- Required `action` parameter is missing
- Required `sys_id` (for get) or `number` (for get_by_number) is missing
- Problem is not found (returns empty object for get_by_number, NotFoundError for get)
- User lacks permission to view the problem
- API authentication fails
