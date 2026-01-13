# Get Incident

Retrieve incident details from ServiceNow by sys_id or incident number.

> **Navigation:** [Back to Skill Index](../../SKILL.md) | [Query Incidents](./query-incidents.md)

## Table of Contents

- [Script](#script)
- [Operations](#operations)
  - [Get by sys_id](#get-by-sys_id)
  - [Get by Number](#get-by-number)
- [Parameters](#parameters)
  - [Fields Parameter](#fields-parameter)
  - [Display Value Parameter](#display-value-parameter)
- [Output](#output)
- [Related Domains](#related-domains)
- [Errors](#errors)

## Script

```bash
python scripts/incidents.py
```

> **Note:** Run all scripts from the skill root directory (where the `scripts/` folder is located).

## Operations

### Get by sys_id

Retrieve an incident using its unique system identifier.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"get"` |
| `sys_id` | Yes | The sys_id of the incident |
| `fields` | No | Comma-separated list of fields to return |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Example

```bash
echo '{
  "action": "get",
  "sys_id": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"
}' | python scripts/incidents.py
```

Get specific fields only:

```bash
echo '{
  "action": "get",
  "sys_id": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
  "fields": "number,short_description,state,priority"
}' | python scripts/incidents.py
```

### Get by Number

Retrieve an incident using its incident number (e.g., INC0010001).

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"get_by_number"` |
| `number` | Yes | The incident number (e.g., "INC0010001") |
| `fields` | No | Comma-separated list of fields to return |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Example

```bash
echo '{
  "action": "get_by_number",
  "number": "INC0010001"
}' | python scripts/incidents.py
```

Get with display values:

```bash
echo '{
  "action": "get_by_number",
  "number": "INC0010001",
  "display_value": "true"
}' | python scripts/incidents.py
```

## Parameters

### Fields Parameter

Specify which fields to include in the response. Common incident fields:

- `sys_id` - Unique system identifier
- `number` - Incident number (e.g., INC0010001)
- `short_description` - Brief summary of the incident
- `description` - Detailed description
- `state` - Current state (1=New, 2=In Progress, 3=On Hold, 6=Resolved, 7=Closed, 8=Canceled)
- `urgency` - Urgency level (1=High, 2=Medium, 3=Low)
- `impact` - Impact level (1=High, 2=Medium, 3=Low)
- `priority` - Calculated priority
- `assignment_group` - Assigned group
- `assigned_to` - Assigned user
- `caller_id` - Caller/requester
- `category` - Incident category
- `subcategory` - Incident subcategory
- `opened_at` - When the incident was opened
- `opened_by` - Who opened the incident
- `resolved_at` - When the incident was resolved
- `resolved_by` - Who resolved the incident
- `closed_at` - When the incident was closed
- `closed_by` - Who closed the incident
- `close_code` - Resolution code
- `close_notes` - Resolution notes
- `active` - Whether the incident is active

### Display Value Parameter

Controls how reference fields are returned:

- `false` (default) - Returns sys_id values for reference fields
- `true` - Returns display values (human-readable names)
- `all` - Returns both sys_id and display value

## Output

JSON object containing the incident record:

```json
{
  "sys_id": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
  "number": "INC0010001",
  "short_description": "Email not working",
  "description": "User cannot send or receive emails",
  "state": "2",
  "urgency": "2",
  "impact": "2",
  "priority": "3",
  "assignment_group": {
    "link": "https://instance.service-now.com/api/now/table/sys_user_group/abc123",
    "value": "abc123"
  },
  "assigned_to": {
    "link": "https://instance.service-now.com/api/now/table/sys_user/def456",
    "value": "def456"
  },
  "caller_id": {
    "link": "https://instance.service-now.com/api/now/table/sys_user/ghi789",
    "value": "ghi789"
  },
  "opened_at": "<timestamp>",
  "active": "true"
}
```

## Related Domains

Incidents often intersect with other ServiceNow domains. Consider these related skills for comprehensive incident management:

### Problem Management
Incidents are often linked to problems for root cause analysis:
- **[Get Problem](../problems/get-problem.md)** - Retrieve details of problems that may be the root cause
- **[Query Problems](../problems/query-problems.md)** - Search for known problems related to this incident

> **Tip:** Check if a known error exists for recurring incidents to apply documented workarounds quickly.

### Change Management
Incidents may be caused by changes or may require changes to resolve:
- **[Get Change Request](../changes/get-change.md)** - Retrieve details of change requests that may have caused the incident
- **[Query Change Requests](../changes/query-changes.md)** - Search for recent changes that might be related to the incident

> **Tip:** When troubleshooting incidents, check recent changes in the affected area using the changes skill to identify potential root causes.

### Service Catalog
Incidents may result in service requests or be related to catalog items:
- **[Browse Catalog](../catalog/browse-catalog.md)** - Browse available service catalog items for remediation options
- **[Search Catalog](../catalog/search-catalog.md)** - Search for specific service offerings that may help resolve the incident
- **[Request Status](../catalog/request-status.md)** - Track the status of service requests related to incident resolution

## Errors

The script will output error details to stderr and exit with non-zero status if:

- Required `action` parameter is missing
- Required `sys_id` (for get) or `number` (for get_by_number) is missing
- Incident is not found (returns empty object for get_by_number, NotFoundError for get)
- User lacks permission to view the incident
- API authentication fails
