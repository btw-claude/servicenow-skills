# Query Problems

Search and filter problems in ServiceNow using various criteria.

> **Navigation:** [Back to Skill Index](../../SKILL.md) | [Get Problem](./get-problem.md)

## Table of Contents

- [Script](#script)
- [Input](#input)
- [State Values](#state-values)
- [Priority Values](#priority-values)
- [Examples](#examples)
- [Encoded Query Syntax](#encoded-query-syntax)
  - [Date Queries](#date-queries)
  - [Dot-Walking (Related Records)](#dot-walking-related-records)
- [Output](#output)
- [Related Domains](#related-domains)
  - [Incident Management](#incident-management)
  - [Change Management](#change-management)
  - [Service Catalog](#service-catalog)
- [Errors](#errors)

## Script

```bash
python scripts/problems.py
```

## Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"query"` |
| `state` | No | Filter by problem state |
| `priority` | No | Filter by priority level |
| `assignment_group` | No | Filter by assignment group (name or sys_id) |
| `known_error` | No | Filter by known error status (true/false) |
| `active` | No | Filter by active status (true/false) |
| `query` | No | Additional encoded query string |
| `fields` | No | Comma-separated list of fields to return |
| `limit` | No | Maximum number of records to return |
| `offset` | No | Starting record index for pagination |
| `order_by` | No | Field to sort by (prefix with `-` for descending) |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

## State Values

| Value | Description |
|-------|-------------|
| 1 | Open |
| 2 | Known Error |
| 3 | Pending Change |
| 4 | Closed/Resolved |
| 5 | Closed/Cancelled |

## Priority Values

| Value | Description |
|-------|-------------|
| 1 | Critical |
| 2 | High |
| 3 | Moderate |
| 4 | Low |
| 5 | Planning |

## Examples

### Query Active Problems

```bash
echo '{
  "action": "query",
  "active": true
}' | python scripts/problems.py
```

### Query by State

Get all open problems:

```bash
echo '{
  "action": "query",
  "state": "1"
}' | python scripts/problems.py
```

### Query Known Errors

```bash
echo '{
  "action": "query",
  "known_error": true,
  "active": true
}' | python scripts/problems.py
```

### Query High Priority Problems

```bash
echo '{
  "action": "query",
  "priority": "2",
  "active": true
}' | python scripts/problems.py
```

### Query by Assignment Group

```bash
echo '{
  "action": "query",
  "assignment_group": "Problem Management",
  "active": true
}' | python scripts/problems.py
```

### Paginated Query

```bash
echo '{
  "action": "query",
  "active": true,
  "limit": 10,
  "offset": 0,
  "order_by": "-sys_created_on"
}' | python scripts/problems.py
```

### Query with Custom Encoded Query

Combine built-in filters with custom ServiceNow encoded query syntax:

```bash
echo '{
  "action": "query",
  "active": true,
  "query": "short_descriptionLIKEemail^major_problem=true",
  "limit": 50
}' | python scripts/problems.py
```

### Get Specific Fields

```bash
echo '{
  "action": "query",
  "state": "1",
  "fields": "number,short_description,priority,assignment_group,sys_created_on,known_error",
  "limit": 20
}' | python scripts/problems.py
```

### Query with Display Values

```bash
echo '{
  "action": "query",
  "active": true,
  "display_value": "true",
  "limit": 10
}' | python scripts/problems.py
```

## Encoded Query Syntax

The `query` parameter accepts ServiceNow encoded query syntax. Common operators:

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `state=1` |
| `!=` | Not equals | `state!=4` |
| `LIKE` | Contains | `short_descriptionLIKEemail` |
| `STARTSWITH` | Starts with | `numberSTARTSWITHPRB001` |
| `ENDSWITH` | Ends with | `numberENDSWITH001` |
| `<` | Less than | `priority<3` |
| `>` | Greater than | `priority>1` |
| `<=` | Less than or equal | `priority<=2` |
| `>=` | Greater than or equal | `priority>=2` |
| `IN` | In list | `stateIN1,2` |
| `NOTIN` | Not in list | `stateNOTIN4,5` |
| `ISEMPTY` | Is empty | `assigned_toISEMPTY` |
| `ISNOTEMPTY` | Is not empty | `assigned_toISNOTEMPTY` |
| `^` | AND | `state=1^priority=1` |
| `^OR` | OR | `state=1^ORstate=2` |

### Date Queries

| Operator | Description | Example |
|----------|-------------|---------|
| `ON` | On specific date | `opened_atON2024-01-15` |
| `BEFORE` | Before date | `opened_atBEFORE2024-01-15` |
| `AFTER` | After date | `opened_atAFTER2024-01-15` |
| `BETWEEN` | Between dates | `opened_atBETWEEN2024-01-01@2024-01-31` |
| `RELATIVE` | Relative to now | `opened_atRELATIVEGE@dayofweek@ago@2` |

### Dot-Walking (Related Records)

Query fields on related records using dot notation:

```bash
echo '{
  "action": "query",
  "query": "assignment_group.manager.name=John Smith^first_reported_by_task.caller_id.department=IT"
}' | python scripts/problems.py
```

## Output

JSON array of problem records matching the query:

```json
[
  {
    "sys_id": "a1b2c3d4e5f6g7h8i9j0",
    "number": "PRB0010001",
    "short_description": "Recurring email delivery failures",
    "state": "2",
    "priority": "2",
    "active": "true",
    "known_error": "true",
    "related_incidents": "5"
  },
  {
    "sys_id": "b2c3d4e5f6g7h8i9j0k1",
    "number": "PRB0010002",
    "short_description": "VPN connection drops during peak hours",
    "state": "1",
    "priority": "1",
    "active": "true",
    "known_error": "false",
    "related_incidents": "12"
  }
]
```

Returns an empty array `[]` if no problems match the query criteria.

## Related Domains

Problems often intersect with other ServiceNow domains. Consider these related skills for comprehensive problem management:

### Incident Management
Problems are often linked to incidents. Use these related skills to work with associated records:
- **[Get Incident](../incidents/get-incident.md)** - Retrieve details of incidents related to problems
- **[Query Incidents](../incidents/query-incidents.md)** - Search for incidents that may be associated with problems

> **Tip:** When investigating problems, use the incidents skill to find related incidents by querying for incidents that reference the problem record.

### Change Management
When problems require permanent fixes, they typically trigger change requests:
- **[Get Change Request](../changes/get-change.md)** - Retrieve details of change requests created to resolve problems
- **[Query Change Requests](../changes/query-changes.md)** - Search for changes related to problem resolution

> **Tip:** Query for problems with `state=3` (Pending Change) to find problems that are awaiting change implementation.

### Service Catalog
Problems may be resolved through standard service requests or may trigger catalog items for remediation:
- **[Browse Catalog](../catalog/browse-catalog.md)** - Browse available service catalog items that may help resolve issues
- **[Search Catalog](../catalog/search-catalog.md)** - Search for specific service offerings related to problem resolution
- **[Request Status](../catalog/request-status.md)** - Track the status of service requests created as part of problem resolution

## Errors

The script will output error details to stderr and exit with non-zero status if:

- Required `action` parameter is missing
- Invalid `action` value provided
- Invalid encoded query syntax
- User lacks permission to query problems
- API authentication fails
