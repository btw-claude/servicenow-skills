# Query Change Requests

Search and filter change requests in ServiceNow using various criteria.

## Script

```bash
python scripts/changes.py
```

## Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"query"` |
| `state` | No | Filter by change state |
| `type` | No | Filter by change type |
| `risk` | No | Filter by risk level |
| `assignment_group` | No | Filter by assignment group (name or sys_id) |
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
| -5 | New |
| -4 | Assess |
| -3 | Authorize |
| -2 | Scheduled |
| -1 | Implement |
| 0 | Review |
| 3 | Closed |
| 4 | Canceled |

## Type Values

| Value | Description |
|-------|-------------|
| standard | Standard change (pre-approved, low risk) |
| normal | Normal change (requires CAB approval) |
| emergency | Emergency change (expedited approval) |

## Risk Values

| Value | Description |
|-------|-------------|
| 1 | High |
| 2 | Moderate |
| 3 | Low |

## Examples

### Query Active Changes

```bash
echo '{
  "action": "query",
  "active": true
}' | python scripts/changes.py
```

### Query by State

Get all scheduled changes:

```bash
echo '{
  "action": "query",
  "state": "-2"
}' | python scripts/changes.py
```

### Query Emergency Changes

```bash
echo '{
  "action": "query",
  "type": "emergency",
  "active": true
}' | python scripts/changes.py
```

### Query High Risk Changes

```bash
echo '{
  "action": "query",
  "risk": "1",
  "active": true
}' | python scripts/changes.py
```

### Query by Assignment Group

```bash
echo '{
  "action": "query",
  "assignment_group": "Change Management",
  "active": true
}' | python scripts/changes.py
```

### Paginated Query

```bash
echo '{
  "action": "query",
  "active": true,
  "limit": 10,
  "offset": 0,
  "order_by": "-sys_created_on"
}' | python scripts/changes.py
```

### Query with Custom Encoded Query

Combine built-in filters with custom ServiceNow encoded query syntax:

```bash
echo '{
  "action": "query",
  "active": true,
  "query": "short_descriptionLIKEdeploy^cab_required=true",
  "limit": 50
}' | python scripts/changes.py
```

### Get Specific Fields

```bash
echo '{
  "action": "query",
  "state": "-2",
  "fields": "number,short_description,type,risk,planned_start_date,assignment_group",
  "limit": 20
}' | python scripts/changes.py
```

### Query with Display Values

```bash
echo '{
  "action": "query",
  "active": true,
  "display_value": "true",
  "limit": 10
}' | python scripts/changes.py
```

### Query Normal Changes in Review

```bash
echo '{
  "action": "query",
  "type": "normal",
  "state": "0",
  "active": true
}' | python scripts/changes.py
```

## Encoded Query Syntax

The `query` parameter accepts ServiceNow encoded query syntax. Common operators:

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `state=-2` |
| `!=` | Not equals | `state!=3` |
| `LIKE` | Contains | `short_descriptionLIKEdeploy` |
| `STARTSWITH` | Starts with | `numberSTARTSWITHCHG001` |
| `ENDSWITH` | Ends with | `numberENDSWITH001` |
| `<` | Less than | `risk<2` |
| `>` | Greater than | `risk>1` |
| `<=` | Less than or equal | `risk<=2` |
| `>=` | Greater than or equal | `risk>=2` |
| `IN` | In list | `stateIN-2,-1,0` |
| `NOTIN` | Not in list | `stateNOTIN3,4` |
| `ISEMPTY` | Is empty | `assigned_toISEMPTY` |
| `ISNOTEMPTY` | Is not empty | `assigned_toISNOTEMPTY` |
| `^` | AND | `state=-2^type=normal` |
| `^OR` | OR | `type=emergency^ORrisk=1` |

### Date Queries

| Operator | Description | Example |
|----------|-------------|---------|
| `ON` | On specific date | `planned_start_dateON2026-01-20` |
| `BEFORE` | Before date | `planned_start_dateBEFORE2026-01-20` |
| `AFTER` | After date | `planned_start_dateAFTER2026-01-20` |
| `BETWEEN` | Between dates | `planned_start_dateBETWEEN2026-01-01@2026-01-31` |
| `RELATIVE` | Relative to now | `planned_start_dateRELATIVEGE@dayofweek@ago@2` |

### Dot-Walking (Related Records)

Query fields on related records using dot notation:

```bash
echo '{
  "action": "query",
  "query": "requested_by.department.name=IT^assignment_group.manager.name=John Smith"
}' | python scripts/changes.py
```

## Output

JSON array of change request records matching the query:

```json
[
  {
    "sys_id": "a1b2c3d4e5f6g7h8i9j0",
    "number": "CHG0010001",
    "short_description": "Deploy new application version",
    "state": "-2",
    "type": "normal",
    "risk": "2",
    "priority": "3",
    "active": "true",
    "planned_start_date": "2026-01-20 02:00:00",
    "planned_end_date": "2026-01-20 04:00:00"
  },
  {
    "sys_id": "b2c3d4e5f6g7h8i9j0k1",
    "number": "CHG0010002",
    "short_description": "Emergency security patch",
    "state": "-1",
    "type": "emergency",
    "risk": "1",
    "priority": "1",
    "active": "true",
    "planned_start_date": "2026-01-15 18:00:00",
    "planned_end_date": "2026-01-15 19:00:00"
  }
]
```

Returns an empty array `[]` if no change requests match the query criteria.

## Errors

The script will output error details to stderr and exit with non-zero status if:

- Required `action` parameter is missing
- Invalid `action` value provided
- Invalid encoded query syntax
- User lacks permission to query change requests
- API authentication fails
