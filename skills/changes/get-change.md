# Get Change Request

Retrieve change request details from ServiceNow by sys_id or change number.

> **Navigation:** [Back to Skill Index](../../SKILL.md) | [Query Change Requests](./query-changes.md)

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
python scripts/changes.py
```

## Operations

### Get by sys_id

Retrieve a change request using its unique system identifier.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"get"` |
| `sys_id` | Yes | The sys_id of the change request |
| `fields` | No | Comma-separated list of fields to return |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Example

```bash
echo '{
  "action": "get",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0"
}' | python scripts/changes.py
```

Get specific fields only:

```bash
echo '{
  "action": "get",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0",
  "fields": "number,short_description,state,type,risk"
}' | python scripts/changes.py
```

### Get by Number

Retrieve a change request using its change number (e.g., CHG0010001).

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"get_by_number"` |
| `number` | Yes | The change number (e.g., "CHG0010001") |
| `fields` | No | Comma-separated list of fields to return |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Example

```bash
echo '{
  "action": "get_by_number",
  "number": "CHG0010001"
}' | python scripts/changes.py
```

Get with display values:

```bash
echo '{
  "action": "get_by_number",
  "number": "CHG0010001",
  "display_value": "true"
}' | python scripts/changes.py
```

## Parameters

### Fields Parameter

Specify which fields to include in the response. Common change request fields:

- `sys_id` - Unique system identifier
- `number` - Change number (e.g., CHG0010001)
- `short_description` - Brief summary of the change
- `description` - Detailed description
- `state` - Current state (-5=New, -4=Assess, -3=Authorize, -2=Scheduled, -1=Implement, 0=Review, 3=Closed, 4=Canceled)
- `type` - Change type (standard, normal, emergency)
- `risk` - Risk level (1=High, 2=Moderate, 3=Low)
- `priority` - Priority level
- `assignment_group` - Assigned group
- `assigned_to` - Assigned user
- `requested_by` - User who requested the change
- `category` - Change category
- `start_date` - Actual start date
- `end_date` - Actual end date
- `planned_start_date` - Planned start date
- `planned_end_date` - Planned end date
- `work_start` - Work start date
- `work_end` - Work end date
- `opened_at` - When the change was opened
- `opened_by` - Who opened the change
- `closed_at` - When the change was closed
- `closed_by` - Who closed the change
- `close_code` - Close code
- `close_notes` - Close notes
- `active` - Whether the change is active
- `approval` - Approval status
- `phase` - Current phase
- `reason` - Reason for change
- `conflict_status` - Conflict status
- `cab_required` - Whether CAB approval is required

### Display Value Parameter

Controls how reference fields are returned:

- `false` (default) - Returns sys_id values for reference fields
- `true` - Returns display values (human-readable names)
- `all` - Returns both sys_id and display value

## Output

JSON object containing the change request record:

```json
{
  "sys_id": "a1b2c3d4e5f6g7h8i9j0",
  "number": "CHG0010001",
  "short_description": "Deploy new application version",
  "description": "Deploy version 2.0 of the customer portal application",
  "state": "-2",
  "type": "normal",
  "risk": "2",
  "priority": "3",
  "assignment_group": {
    "link": "https://instance.service-now.com/api/now/table/sys_user_group/abc123",
    "value": "abc123"
  },
  "assigned_to": {
    "link": "https://instance.service-now.com/api/now/table/sys_user/def456",
    "value": "def456"
  },
  "requested_by": {
    "link": "https://instance.service-now.com/api/now/table/sys_user/ghi789",
    "value": "ghi789"
  },
  "planned_start_date": "2026-01-20 02:00:00",
  "planned_end_date": "2026-01-20 04:00:00",
  "active": "true",
  "approval": "approved",
  "cab_required": "false"
}
```

## Related Domains

Change requests often intersect with other ServiceNow domains. Consider these related skills for comprehensive change management:

### Incident Management
Changes may cause incidents or be created in response to incidents:
- **[Get Incident](../incidents/get-incident.md)** - Retrieve details of incidents that may be related to this change
- **[Query Incidents](../incidents/query-incidents.md)** - Search for incidents caused by or related to changes

> **Tip:** After implementing a change, monitor for new incidents to identify any change-related issues.

### Problem Management
Changes are often created to resolve underlying problems:
- **[Get Problem](../problems/get-problem.md)** - Retrieve details of problems that triggered this change
- **[Query Problems](../problems/query-problems.md)** - Search for problems in "Pending Change" state waiting for this change

### Service Catalog
Changes may be requested through the service catalog:
- **[Browse Catalog](../catalog/browse-catalog.md)** - Browse available service catalog items related to change requests
- **[Search Catalog](../catalog/search-catalog.md)** - Search for standard change templates in the catalog
- **[Request Status](../catalog/request-status.md)** - Track the status of catalog-initiated change requests

## Errors

The script will output error details to stderr and exit with non-zero status if:

- Required `action` parameter is missing
- Required `sys_id` (for get) or `number` (for get_by_number) is missing
- Change request is not found (returns empty object for get_by_number, NotFoundError for get)
- User lacks permission to view the change request
- API authentication fails
