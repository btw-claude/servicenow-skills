# Query Configuration Items

Search and filter Configuration Items (CIs) in ServiceNow CMDB using various criteria.

## Script

```bash
python scripts/cmdb.py
```

## Operations

### Query CIs

Filter CIs by class, operational status, location, and other criteria.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"query"` |
| `ci_class` | No | Filter by CI class name (e.g., `cmdb_ci_server`) |
| `operational_status` | No | Filter by operational status |
| `location` | No | Filter by location (name or sys_id) |
| `query` | No | Additional encoded query string |
| `fields` | No | Comma-separated list of fields to return |
| `limit` | No | Maximum number of records to return |
| `offset` | No | Starting record index for pagination |
| `order_by` | No | Field to sort by (prefix with `-` for descending) |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

### Search CIs

Search CIs by name, asset tag, or serial number.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"search"` |
| `search_term` | Yes | Text to search for in name, asset_tag, or serial_number |
| `ci_class` | No | Filter by CI class name |
| `fields` | No | Comma-separated list of fields to return |
| `limit` | No | Maximum number of records to return |
| `offset` | No | Starting record index for pagination |
| `order_by` | No | Field to sort by (prefix with `-` for descending) |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

## CI Class Values

Common CI classes in ServiceNow CMDB:

| Class | Description |
|-------|-------------|
| `cmdb_ci` | Base Configuration Item |
| `cmdb_ci_server` | Server |
| `cmdb_ci_computer` | Computer |
| `cmdb_ci_win_server` | Windows Server |
| `cmdb_ci_linux_server` | Linux Server |
| `cmdb_ci_unix_server` | Unix Server |
| `cmdb_ci_vm_instance` | Virtual Machine Instance |
| `cmdb_ci_app_server` | Application Server |
| `cmdb_ci_database` | Database |
| `cmdb_ci_db_instance` | Database Instance |
| `cmdb_ci_storage_device` | Storage Device |
| `cmdb_ci_netgear` | Network Gear |
| `cmdb_ci_ip_router` | Router |
| `cmdb_ci_ip_switch` | Switch |
| `cmdb_ci_ip_firewall` | Firewall |
| `cmdb_ci_lb` | Load Balancer |
| `cmdb_ci_printer` | Printer |
| `cmdb_ci_spkg` | Software |
| `cmdb_ci_service` | Service |
| `cmdb_ci_service_auto` | Business Service |

## Operational Status Values

| Value | Description |
|-------|-------------|
| 1 | Operational |
| 2 | Non-Operational |
| 3 | Repair in Progress |
| 4 | DR Standby |
| 5 | Ready |
| 6 | Retired |

## Default Fields

**When no `fields` parameter is specified, the DEFAULT_FIELDS are returned.** See [CMDB.md](CMDB.md#ci-default-fields-default_fields) for the complete list of default fields.

To retrieve specific fields only, use the `fields` parameter with a comma-separated list of field names.

## Examples

### Query All Servers

```bash
echo '{
  "action": "query",
  "ci_class": "cmdb_ci_server"
}' | python scripts/cmdb.py
```

### Query Operational CIs

```bash
echo '{
  "action": "query",
  "operational_status": "1"
}' | python scripts/cmdb.py
```

### Query by Location

```bash
echo '{
  "action": "query",
  "location": "New York Data Center",
  "ci_class": "cmdb_ci_server"
}' | python scripts/cmdb.py
```

### Query with Multiple Filters

```bash
echo '{
  "action": "query",
  "ci_class": "cmdb_ci_server",
  "operational_status": "1",
  "limit": 50
}' | python scripts/cmdb.py
```

### Paginated Query

```bash
echo '{
  "action": "query",
  "ci_class": "cmdb_ci_server",
  "limit": 10,
  "offset": 0,
  "order_by": "-sys_created_on"
}' | python scripts/cmdb.py
```

### Search CIs by Name

```bash
echo '{
  "action": "search",
  "search_term": "web-server"
}' | python scripts/cmdb.py
```

### Search with Class Filter

```bash
echo '{
  "action": "search",
  "search_term": "prod",
  "ci_class": "cmdb_ci_server",
  "limit": 20
}' | python scripts/cmdb.py
```

### Query with Custom Encoded Query

Combine built-in filters with custom ServiceNow encoded query syntax:

```bash
echo '{
  "action": "query",
  "ci_class": "cmdb_ci_server",
  "query": "environmentLIKEproduction^active=true",
  "limit": 100
}' | python scripts/cmdb.py
```

### Get Specific Fields

```bash
echo '{
  "action": "query",
  "ci_class": "cmdb_ci_server",
  "fields": "name,ip_address,operational_status,location,environment",
  "limit": 20
}' | python scripts/cmdb.py
```

### Query with Display Values

```bash
echo '{
  "action": "query",
  "ci_class": "cmdb_ci_server",
  "display_value": "true",
  "limit": 10
}' | python scripts/cmdb.py
```

## Encoded Query Syntax

The `query` parameter accepts ServiceNow encoded query syntax. Common operators:

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `operational_status=1` |
| `!=` | Not equals | `operational_status!=6` |
| `LIKE` | Contains | `nameLIKEweb` |
| `STARTSWITH` | Starts with | `nameSTARTSWITHprod` |
| `ENDSWITH` | Ends with | `nameENDSWITH01` |
| `<` | Less than | `cost<1000` |
| `>` | Greater than | `cost>500` |
| `<=` | Less than or equal | `cost<=1000` |
| `>=` | Greater than or equal | `cost>=500` |
| `IN` | In list | `operational_statusIN1,5` |
| `NOTIN` | Not in list | `operational_statusNOTIN2,6` |
| `ISEMPTY` | Is empty | `ip_addressISEMPTY` |
| `ISNOTEMPTY` | Is not empty | `ip_addressISNOTEMPTY` |
| `^` | AND | `operational_status=1^active=true` |
| `^OR` | OR | `sys_class_name=cmdb_ci_server^ORsys_class_name=cmdb_ci_vm_instance` |

### Date Queries

| Operator | Description | Example |
|----------|-------------|---------|
| `ON` | On specific date | `last_discoveredON2024-01-15` |
| `BEFORE` | Before date | `warranty_expirationBEFORE2024-12-31` |
| `AFTER` | After date | `purchase_dateAFTER2024-01-01` |
| `BETWEEN` | Between dates | `sys_created_onBETWEEN2024-01-01@2024-06-30` |
| `RELATIVE` | Relative to now | `last_discoveredRELATIVEGE@dayofweek@ago@7` |

### Dot-Walking (Related Records)

Query fields on related records using dot notation:

```bash
echo '{
  "action": "query",
  "query": "location.name=New York^assigned_to.department=IT"
}' | python scripts/cmdb.py
```

## Output

JSON array of CI records matching the query:

```json
[
  {
    "sys_id": "a1b2c3d4e5f6g7h8i9j0",
    "name": "web-server-01",
    "sys_class_name": "cmdb_ci_server",
    "ip_address": "192.168.1.100",
    "operational_status": "1",
    "location": {
      "link": "https://instance.service-now.com/api/now/table/cmn_location/loc123",
      "value": "loc123"
    },
    "environment": "Production",
    "active": "true"
  },
  {
    "sys_id": "b2c3d4e5f6g7h8i9j0k1",
    "name": "web-server-02",
    "sys_class_name": "cmdb_ci_server",
    "ip_address": "192.168.1.101",
    "operational_status": "1",
    "location": {
      "link": "https://instance.service-now.com/api/now/table/cmn_location/loc123",
      "value": "loc123"
    },
    "environment": "Production",
    "active": "true"
  }
]
```

Returns an empty array `[]` if no CIs match the query criteria.

## Errors

The script will output error details to stderr and exit with non-zero status if:

- Required `action` parameter is missing
- Invalid `action` value provided
- Required `search_term` (for search action) is missing
- Invalid encoded query syntax
- User lacks permission to query CIs
- API authentication fails
