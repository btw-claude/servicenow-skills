# CI Relationships

Retrieve and explore relationships between Configuration Items (CIs) in ServiceNow CMDB.

## Script

```bash
python scripts/cmdb.py
```

## Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"relationships"` |
| `sys_id` | Yes | The sys_id of the CI to get relationships for |
| `relationship_type` | No | Filter by relationship type sys_id |
| `direction` | No | Direction filter: `parent`, `child`, or `both` (default) |
| `fields` | No | Comma-separated list of fields to return |
| `limit` | No | Maximum number of records to return |
| `offset` | No | Starting record index for pagination |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

## Direction Parameter

Controls which relationships to return based on the CI's role:

| Value | Description |
|-------|-------------|
| `parent` | Returns relationships where the CI is the parent |
| `child` | Returns relationships where the CI is the child |
| `both` | Returns all relationships (default) |

## Common Relationship Types

ServiceNow CMDB supports various relationship types. Common examples:

| Relationship | Description |
|--------------|-------------|
| Depends on | CI depends on another CI |
| Used by | CI is used by another CI |
| Runs on | Application/service runs on infrastructure |
| Hosted on | CI is hosted on another CI |
| Contains | CI contains another CI |
| Connects to | CI connects to another CI |
| Cluster of | CI is part of a cluster |
| Members | CI has members |
| Provides | CI provides to another CI |
| Consumes | CI consumes from another CI |
| DR of | CI is disaster recovery for another CI |

## Examples

### Get All Relationships

Get all relationships for a CI (both parent and child):

```bash
echo '{
  "action": "relationships",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0"
}' | python scripts/cmdb.py
```

### Get Parent Relationships

Get relationships where the CI is the parent (downstream dependencies):

```bash
echo '{
  "action": "relationships",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0",
  "direction": "parent"
}' | python scripts/cmdb.py
```

### Get Child Relationships

Get relationships where the CI is the child (upstream dependencies):

```bash
echo '{
  "action": "relationships",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0",
  "direction": "child"
}' | python scripts/cmdb.py
```

### Filter by Relationship Type

Get only specific relationship types:

```bash
echo '{
  "action": "relationships",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0",
  "relationship_type": "rel_type_sys_id_here"
}' | python scripts/cmdb.py
```

### Paginated Query

```bash
echo '{
  "action": "relationships",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0",
  "limit": 10,
  "offset": 0
}' | python scripts/cmdb.py
```

### Get with Display Values

```bash
echo '{
  "action": "relationships",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0",
  "display_value": "true"
}' | python scripts/cmdb.py
```

### Get Specific Fields

```bash
echo '{
  "action": "relationships",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0",
  "fields": "sys_id,parent,child,type,connection_strength"
}' | python scripts/cmdb.py
```

## Relationship Fields

**When no `fields` parameter is specified, the following default fields (RELATIONSHIP_FIELDS) are returned:**

- `sys_id` - Unique system identifier for the relationship
- `parent` - Reference to the parent CI
- `child` - Reference to the child CI
- `type` - Reference to the relationship type (cmdb_rel_type)
- `connection_strength` - Strength of the relationship connection
- `port` - Port information (if applicable)
- `sys_created_on` - Record creation timestamp
- `sys_updated_on` - Record last update timestamp

## Output

JSON array of relationship records:

```json
[
  {
    "sys_id": "rel123456789",
    "parent": {
      "link": "https://instance.service-now.com/api/now/table/cmdb_ci/a1b2c3d4e5f6g7h8i9j0",
      "value": "a1b2c3d4e5f6g7h8i9j0"
    },
    "child": {
      "link": "https://instance.service-now.com/api/now/table/cmdb_ci/x9y8z7w6v5u4t3s2r1q0",
      "value": "x9y8z7w6v5u4t3s2r1q0"
    },
    "type": {
      "link": "https://instance.service-now.com/api/now/table/cmdb_rel_type/type456",
      "value": "type456"
    },
    "connection_strength": "Always",
    "sys_created_on": "<timestamp>"
  },
  {
    "sys_id": "rel987654321",
    "parent": {
      "link": "https://instance.service-now.com/api/now/table/cmdb_ci/p0o9i8u7y6t5r4e3w2q1",
      "value": "p0o9i8u7y6t5r4e3w2q1"
    },
    "child": {
      "link": "https://instance.service-now.com/api/now/table/cmdb_ci/a1b2c3d4e5f6g7h8i9j0",
      "value": "a1b2c3d4e5f6g7h8i9j0"
    },
    "type": {
      "link": "https://instance.service-now.com/api/now/table/cmdb_rel_type/type789",
      "value": "type789"
    },
    "connection_strength": "Always",
    "sys_created_on": "<timestamp>"
  }
]
```

With `display_value: "true"`:

```json
[
  {
    "sys_id": "rel123456789",
    "parent": "web-server-01",
    "child": "database-01",
    "type": "Depends on::Used by",
    "connection_strength": "Always",
    "sys_created_on": "<timestamp>"
  }
]
```

Returns an empty array `[]` if no relationships exist for the CI.

## Use Cases

### Impact Analysis

Find what depends on a CI (to assess impact of changes):

```bash
echo '{
  "action": "relationships",
  "sys_id": "database_server_sys_id",
  "direction": "parent"
}' | python scripts/cmdb.py
```

### Dependency Mapping

Find what a CI depends on (to understand prerequisites):

```bash
echo '{
  "action": "relationships",
  "sys_id": "application_sys_id",
  "direction": "child"
}' | python scripts/cmdb.py
```

### Service Topology

Build a complete view of service dependencies:

1. Get the service CI
2. Get all relationships recursively
3. Build a dependency tree/graph

## Errors

The script will output error details to stderr and exit with non-zero status if:

- Required `action` parameter is missing
- Required `sys_id` is missing
- Invalid `direction` value (must be `parent`, `child`, or `both`)
- CI is not found
- User lacks permission to view relationships
- API authentication fails
