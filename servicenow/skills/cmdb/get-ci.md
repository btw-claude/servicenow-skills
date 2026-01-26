# Get Configuration Item

Retrieve Configuration Item (CI) details from ServiceNow CMDB by sys_id, IP address, or serial number.

## Script

```bash
python scripts/cmdb.py
```

## Operations

### Get by sys_id

Retrieve a CI using its unique system identifier.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"get"` |
| `sys_id` | Yes | The sys_id of the CI |
| `fields` | No | Comma-separated list of fields to return |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Example

```bash
echo '{
  "action": "get",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0"
}' | python scripts/cmdb.py
```

Get specific fields only:

```bash
echo '{
  "action": "get",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0",
  "fields": "name,sys_class_name,ip_address,operational_status,location"
}' | python scripts/cmdb.py
```

### Get by IP Address

Retrieve CIs by their IP address.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"by_ip"` |
| `ip_address` | Yes | The IP address to search for |
| `ci_class` | No | Filter by CI class name |
| `fields` | No | Comma-separated list of fields to return |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Example

```bash
echo '{
  "action": "by_ip",
  "ip_address": "192.168.1.100"
}' | python scripts/cmdb.py
```

Filter by CI class:

```bash
echo '{
  "action": "by_ip",
  "ip_address": "192.168.1.100",
  "ci_class": "cmdb_ci_server"
}' | python scripts/cmdb.py
```

### Get by Serial Number

Retrieve CIs by their serial number.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"by_serial"` |
| `serial_number` | Yes | The serial number to search for |
| `ci_class` | No | Filter by CI class name |
| `fields` | No | Comma-separated list of fields to return |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Example

```bash
echo '{
  "action": "by_serial",
  "serial_number": "ABC123XYZ"
}' | python scripts/cmdb.py
```

With display values:

```bash
echo '{
  "action": "by_serial",
  "serial_number": "ABC123XYZ",
  "display_value": "true"
}' | python scripts/cmdb.py
```

## Parameters

### Fields Parameter

Specify which fields to include in the response. **When no `fields` parameter is specified, the following default fields (DEFAULT_FIELDS) are returned:**

- `sys_id` - Unique system identifier
- `name` - CI name
- `sys_class_name` - CI class (e.g., cmdb_ci_server, cmdb_ci_computer)
- `asset_tag` - Asset tag
- `serial_number` - Serial number
- `ip_address` - IP address
- `mac_address` - MAC address
- `dns_domain` - DNS domain
- `fqdn` - Fully qualified domain name
- `operational_status` - Operational status (1=Operational, 2=Non-Operational, 3=Repair in Progress, 4=DR Standby, 5=Ready, 6=Retired)
- `install_status` - Installation status
- `location` - Location
- `department` - Department
- `company` - Company
- `assigned_to` - Assigned user
- `managed_by` - Managed by user
- `owned_by` - Owner
- `supported_by` - Support group
- `manufacturer` - Manufacturer
- `model_id` - Model reference
- `model_number` - Model number
- `vendor` - Vendor
- `cost` - Cost
- `cost_center` - Cost center
- `purchase_date` - Purchase date
- `warranty_expiration` - Warranty expiration date
- `first_discovered` - First discovery timestamp
- `last_discovered` - Last discovery timestamp
- `discovery_source` - Discovery source
- `environment` - Environment (e.g., Production, Development, Test)
- `short_description` - Brief description
- `comments` - Additional comments
- `active` - Whether the CI is active
- `sys_created_on` - Record creation timestamp
- `sys_updated_on` - Record last update timestamp

### Display Value Parameter

Controls how reference fields are returned:

- `false` (default) - Returns sys_id values for reference fields
- `true` - Returns display values (human-readable names)
- `all` - Returns both sys_id and display value

## Output

### Get by sys_id

JSON object containing the CI record:

```json
{
  "sys_id": "a1b2c3d4e5f6g7h8i9j0",
  "name": "web-server-01",
  "sys_class_name": "cmdb_ci_server",
  "asset_tag": "ASSET001",
  "serial_number": "ABC123XYZ",
  "ip_address": "192.168.1.100",
  "operational_status": "1",
  "location": {
    "link": "https://instance.service-now.com/api/now/table/cmn_location/loc123",
    "value": "loc123"
  },
  "assigned_to": {
    "link": "https://instance.service-now.com/api/now/table/sys_user/user456",
    "value": "user456"
  },
  "manufacturer": {
    "link": "https://instance.service-now.com/api/now/table/core_company/mfg789",
    "value": "mfg789"
  },
  "environment": "Production",
  "active": "true",
  "sys_created_on": "<timestamp>"
}
```

### Get by IP Address / Serial Number

JSON array of CI records matching the criteria:

```json
[
  {
    "sys_id": "a1b2c3d4e5f6g7h8i9j0",
    "name": "web-server-01",
    "sys_class_name": "cmdb_ci_server",
    "ip_address": "192.168.1.100",
    "operational_status": "1",
    "active": "true"
  }
]
```

Returns an empty array `[]` if no CIs match the criteria.

## Errors

The script will output error details to stderr and exit with non-zero status if:

- Required `action` parameter is missing
- Required `sys_id` (for get), `ip_address` (for by_ip), or `serial_number` (for by_serial) is missing
- CI is not found (NotFoundError for get)
- User lacks permission to view the CI
- API authentication fails
