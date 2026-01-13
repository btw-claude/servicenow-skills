# Query Incidents

Search and filter incidents in ServiceNow using various criteria.

## Script

```bash
python scripts/incidents.py
```

## Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"query"` |
| `state` | No | Filter by incident state |
| `urgency` | No | Filter by urgency level |
| `impact` | No | Filter by impact level |
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
| 1 | New |
| 2 | In Progress |
| 3 | On Hold |
| 6 | Resolved |
| 7 | Closed |
| 8 | Canceled |

## Urgency/Impact Values

| Value | Description |
|-------|-------------|
| 1 | High |
| 2 | Medium |
| 3 | Low |

## Examples

### Query Active Incidents

```bash
echo '{
  "action": "query",
  "active": true
}' | python scripts/incidents.py
```

### Query by State

Get all incidents in progress:

```bash
echo '{
  "action": "query",
  "state": "2"
}' | python scripts/incidents.py
```

### Query High Priority Incidents

```bash
echo '{
  "action": "query",
  "urgency": "1",
  "impact": "1",
  "active": true
}' | python scripts/incidents.py
```

### Query by Assignment Group

```bash
echo '{
  "action": "query",
  "assignment_group": "Service Desk",
  "active": true
}' | python scripts/incidents.py
```

### Paginated Query

```bash
echo '{
  "action": "query",
  "active": true,
  "limit": 10,
  "offset": 0,
  "order_by": "-sys_created_on"
}' | python scripts/incidents.py
```

### Query with Custom Encoded Query

Combine built-in filters with custom ServiceNow encoded query syntax:

```bash
echo '{
  "action": "query",
  "active": true,
  "query": "short_descriptionLIKEemail^caller_id.department=IT",
  "limit": 50
}' | python scripts/incidents.py
```

### Get Specific Fields

```bash
echo '{
  "action": "query",
  "state": "1",
  "fields": "number,short_description,priority,assignment_group,sys_created_on",
  "limit": 20
}' | python scripts/incidents.py
```

### Query with Display Values

```bash
echo '{
  "action": "query",
  "active": true,
  "display_value": "true",
  "limit": 10
}' | python scripts/incidents.py
```

## Encoded Query Syntax

The `query` parameter accepts ServiceNow encoded query syntax. Common operators:

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `state=1` |
| `!=` | Not equals | `state!=7` |
| `LIKE` | Contains | `short_descriptionLIKEemail` |
| `STARTSWITH` | Starts with | `numberSTARTSWITHINC001` |
| `ENDSWITH` | Ends with | `numberENDSWITH001` |
| `<` | Less than | `priority<3` |
| `>` | Greater than | `priority>1` |
| `<=` | Less than or equal | `priority<=2` |
| `>=` | Greater than or equal | `priority>=2` |
| `IN` | In list | `stateIN1,2,3` |
| `NOTIN` | Not in list | `stateNOTIN6,7,8` |
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
  "query": "caller_id.department.name=IT^assignment_group.manager.name=John Smith"
}' | python scripts/incidents.py
```

## Output

JSON array of incident records matching the query:

```json
[
  {
    "sys_id": "a1b2c3d4e5f6g7h8i9j0",
    "number": "INC0010001",
    "short_description": "Email not working",
    "state": "2",
    "urgency": "2",
    "impact": "2",
    "priority": "3",
    "active": "true"
  },
  {
    "sys_id": "b2c3d4e5f6g7h8i9j0k1",
    "number": "INC0010002",
    "short_description": "VPN connection issues",
    "state": "1",
    "urgency": "1",
    "impact": "2",
    "priority": "2",
    "active": "true"
  }
]
```

Returns an empty array `[]` if no incidents match the query criteria.

## Errors

The script will output error details to stderr and exit with non-zero status if:

- Required `action` parameter is missing
- Invalid `action` value provided
- Invalid encoded query syntax
- User lacks permission to query incidents
- API authentication fails
