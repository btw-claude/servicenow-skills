# CMDB Skills

Configuration Management Database (CMDB) skills for managing Configuration Items (CIs) in ServiceNow.

## Overview

The CMDB is a central repository that stores information about all IT assets and their relationships. These skills enable you to retrieve, search, and explore Configuration Items and their dependencies.

## Available Skills

| Skill | Description |
|-------|-------------|
| [get-ci.md](get-ci.md) | Retrieve CI details by sys_id, IP address, or serial number |
| [query-cis.md](query-cis.md) | Search and filter CIs using various criteria and encoded queries |
| [ci-relationships.md](ci-relationships.md) | Explore relationships and dependencies between CIs |

## Common Use Cases

### Asset Lookup
Use `get-ci.md` to retrieve details about a specific CI when you have its identifier (sys_id, IP address, or serial number).

### Inventory Search
Use `query-cis.md` to find CIs based on class, status, location, or custom criteria. Supports pagination and sorting for large result sets.

### Impact Analysis
Use `ci-relationships.md` to understand what depends on a CI before making changes, or to map service dependencies.

## Script

All CMDB operations use the same script:

```bash
python scripts/cmdb.py
```

## Quick Reference

### sys_id Format

**Note:** In ServiceNow, `sys_id` values are 32-character hexadecimal strings that uniquely identify records. For example: `6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c`. The shortened examples in this documentation (e.g., `abc123`) are for readability only—actual sys_id values you'll encounter will always be 32 characters long.

### CI Classes
Common CI classes: `cmdb_ci_server`, `cmdb_ci_computer`, `cmdb_ci_database`, `cmdb_ci_network_gear`, `cmdb_ci_service`

### Operational Status
- 1: Operational
- 2: Non-Operational
- 3: Repair in Progress
- 4: DR Standby
- 5: Ready
- 6: Retired

### Relationship Directions
- `parent`: CIs that depend on the target CI
- `child`: CIs that the target CI depends on
- `both`: All relationships (default)

## Examples

### Get a CI by sys_id
```bash
echo '{"action": "get", "sys_id": "abc123"}' | python scripts/cmdb.py
```

**Expected output:**
```json
{
  "sys_id": "abc123",
  "name": "web-server-01",
  "sys_class_name": "cmdb_ci_server",
  "ip_address": "192.168.1.100",
  "operational_status": "1",
  "location": "Data Center A"
}
```

### Find all servers
```bash
echo '{"action": "query", "ci_class": "cmdb_ci_server"}' | python scripts/cmdb.py
```

**Expected output:**
```json
{
  "result": [
    {
      "sys_id": "abc123",
      "name": "web-server-01",
      "sys_class_name": "cmdb_ci_server",
      "operational_status": "1"
    },
    {
      "sys_id": "def456",
      "name": "db-server-01",
      "sys_class_name": "cmdb_ci_server",
      "operational_status": "1"
    }
  ],
  "count": 2
}
```

### Get CI relationships
```bash
echo '{"action": "relationships", "sys_id": "abc123"}' | python scripts/cmdb.py
```

**Expected output:**
```json
{
  "result": [
    {
      "sys_id": "rel001",
      "parent": { "value": "abc123", "display_value": "web-server-01" },
      "child": { "value": "xyz789", "display_value": "app-service-01" },
      "type": { "value": "type001", "display_value": "Depends on::Used by" }
    }
  ],
  "count": 1
}
```

## Default Fields

When no `fields` parameter is specified, CMDB operations return a standard set of fields.

### CI Default Fields (DEFAULT_FIELDS)

The following fields are returned by default for CI operations (`get`, `get_by_name`, `query`, `search`, `by_ip`, `by_serial`):

- `sys_id` - Unique system identifier
- `name` - CI name
- `sys_class_name` - CI class
- `asset_tag` - Asset tag
- `serial_number` - Serial number
- `ip_address` - IP address
- `mac_address` - MAC address
- `dns_domain` - DNS domain
- `fqdn` - Fully qualified domain name
- `operational_status` - Operational status
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
- `environment` - Environment
- `short_description` - Brief description
- `comments` - Additional comments
- `active` - Whether the CI is active
- `sys_created_on` - Record creation timestamp
- `sys_updated_on` - Record last update timestamp

### Relationship Default Fields (RELATIONSHIP_FIELDS)

The following fields are returned by default for the `relationships` action:

- `sys_id` - Unique system identifier for the relationship
- `parent` - Reference to the parent CI
- `child` - Reference to the child CI
- `type` - Reference to the relationship type
- `connection_strength` - Strength of the relationship connection
- `port` - Port information (if applicable)
- `sys_created_on` - Record creation timestamp
- `sys_updated_on` - Record last update timestamp

To customize the fields returned, use the `fields` parameter with a comma-separated list of field names.

## Example Output: Default Fields vs Custom Fields

This section provides concrete examples of what API responses look like when using default fields versus specifying custom fields. Understanding these output formats helps you know what to expect from the API.

### CI Query with Default Fields

When no `fields` parameter is specified, all DEFAULT_FIELDS are returned:

```bash
echo '{"action": "get", "sys_id": "abc123def456"}' | python scripts/cmdb.py
```

**Response with DEFAULT_FIELDS:**
```json
{
  "sys_id": "abc123def456",
  "name": "web-server-prod-01",
  "sys_class_name": "cmdb_ci_server",
  "asset_tag": "ASSET-2024-001",
  "serial_number": "SN-XYZ-789012",
  "ip_address": "192.168.1.100",
  "mac_address": "00:1A:2B:3C:4D:5E",
  "dns_domain": "example.corp",
  "fqdn": "web-server-prod-01.example.corp",
  "operational_status": "1",
  "install_status": "1",
  "location": {
    "link": "https://instance.service-now.com/api/now/table/cmn_location/loc123",
    "value": "loc123"
  },
  "department": {
    "link": "https://instance.service-now.com/api/now/table/cmn_department/dept456",
    "value": "dept456"
  },
  "company": {
    "link": "https://instance.service-now.com/api/now/table/core_company/comp789",
    "value": "comp789"
  },
  "assigned_to": {
    "link": "https://instance.service-now.com/api/now/table/sys_user/user001",
    "value": "user001"
  },
  "managed_by": {
    "link": "https://instance.service-now.com/api/now/table/sys_user/user002",
    "value": "user002"
  },
  "owned_by": {
    "link": "https://instance.service-now.com/api/now/table/sys_user/user003",
    "value": "user003"
  },
  "supported_by": {
    "link": "https://instance.service-now.com/api/now/table/sys_user_group/grp001",
    "value": "grp001"
  },
  "manufacturer": {
    "link": "https://instance.service-now.com/api/now/table/core_company/mfg001",
    "value": "mfg001"
  },
  "model_id": {
    "link": "https://instance.service-now.com/api/now/table/cmdb_model/mdl001",
    "value": "mdl001"
  },
  "model_number": "PowerEdge R740",
  "vendor": {
    "link": "https://instance.service-now.com/api/now/table/core_company/vnd001",
    "value": "vnd001"
  },
  "cost": "5000",
  "cost_center": {
    "link": "https://instance.service-now.com/api/now/table/cmn_cost_center/cc001",
    "value": "cc001"
  },
  "purchase_date": "2024-01-15",
  "warranty_expiration": "2027-01-15",
  "first_discovered": "2024-01-20 10:30:00",
  "last_discovered": "2024-06-15 14:22:00",
  "discovery_source": "ServiceNow Discovery",
  "environment": "Production",
  "short_description": "Primary web server for production workloads",
  "comments": "Migrated from legacy data center in Q1 2024",
  "active": "true",
  "sys_created_on": "2024-01-15 09:00:00",
  "sys_updated_on": "2024-06-15 14:22:00"
}
```

### CI Query with Custom Fields

When the `fields` parameter is specified, only the requested fields are returned:

```bash
echo '{
  "action": "get",
  "sys_id": "abc123def456",
  "fields": "name,ip_address,operational_status,environment"
}' | python scripts/cmdb.py
```

**Response with custom fields:**
```json
{
  "name": "web-server-prod-01",
  "ip_address": "192.168.1.100",
  "operational_status": "1",
  "environment": "Production"
}
```

### CI Query with Display Values

Using `display_value: "true"` returns human-readable values instead of sys_ids:

```bash
echo '{
  "action": "query",
  "ci_class": "cmdb_ci_server",
  "limit": 1,
  "display_value": "true"
}' | python scripts/cmdb.py
```

**Response with display values:**
```json
[
  {
    "sys_id": "abc123def456",
    "name": "web-server-prod-01",
    "sys_class_name": "Server",
    "asset_tag": "ASSET-2024-001",
    "serial_number": "SN-XYZ-789012",
    "ip_address": "192.168.1.100",
    "mac_address": "00:1A:2B:3C:4D:5E",
    "dns_domain": "example.corp",
    "fqdn": "web-server-prod-01.example.corp",
    "operational_status": "Operational",
    "install_status": "Installed",
    "location": "New York Data Center",
    "department": "IT Operations",
    "company": "Acme Corporation",
    "assigned_to": "John Smith",
    "managed_by": "Jane Doe",
    "owned_by": "Bob Wilson",
    "supported_by": "Server Support Team",
    "manufacturer": "Dell",
    "model_id": "PowerEdge R740",
    "model_number": "PowerEdge R740",
    "vendor": "Dell Technologies",
    "cost": "5000",
    "cost_center": "IT-INFRA-001",
    "purchase_date": "2024-01-15",
    "warranty_expiration": "2027-01-15",
    "first_discovered": "2024-01-20 10:30:00",
    "last_discovered": "2024-06-15 14:22:00",
    "discovery_source": "ServiceNow Discovery",
    "environment": "Production",
    "short_description": "Primary web server for production workloads",
    "comments": "Migrated from legacy data center in Q1 2024",
    "active": "true",
    "sys_created_on": "2024-01-15 09:00:00",
    "sys_updated_on": "2024-06-15 14:22:00"
  }
]
```

### Relationship Query with Default Fields

When no `fields` parameter is specified for relationships, RELATIONSHIP_FIELDS are returned:

```bash
echo '{"action": "relationships", "sys_id": "abc123def456"}' | python scripts/cmdb.py
```

**Response with RELATIONSHIP_FIELDS:**
```json
[
  {
    "sys_id": "rel001abc",
    "parent": {
      "link": "https://instance.service-now.com/api/now/table/cmdb_ci/abc123def456",
      "value": "abc123def456"
    },
    "child": {
      "link": "https://instance.service-now.com/api/now/table/cmdb_ci/db-server-001",
      "value": "db-server-001"
    },
    "type": {
      "link": "https://instance.service-now.com/api/now/table/cmdb_rel_type/type001",
      "value": "type001"
    },
    "connection_strength": "Always",
    "port": "3306",
    "sys_created_on": "2024-02-01 11:00:00",
    "sys_updated_on": "2024-02-01 11:00:00"
  },
  {
    "sys_id": "rel002def",
    "parent": {
      "link": "https://instance.service-now.com/api/now/table/cmdb_ci/load-balancer-001",
      "value": "load-balancer-001"
    },
    "child": {
      "link": "https://instance.service-now.com/api/now/table/cmdb_ci/abc123def456",
      "value": "abc123def456"
    },
    "type": {
      "link": "https://instance.service-now.com/api/now/table/cmdb_rel_type/type002",
      "value": "type002"
    },
    "connection_strength": "Always",
    "port": "443",
    "sys_created_on": "2024-02-01 11:30:00",
    "sys_updated_on": "2024-02-01 11:30:00"
  }
]
```

### CI Query with Display Value All

Using `display_value: "all"` returns both the raw sys_id values AND the display values in a nested structure. This is useful when you need to reference the sys_id (for subsequent API calls) while also showing the human-readable display name:

```bash
echo '{
  "action": "query",
  "ci_class": "cmdb_ci_server",
  "limit": 1,
  "display_value": "all"
}' | python scripts/cmdb.py
```

**Response with both sys_id and display values:**
```json
[
  {
    "sys_id": {
      "display_value": "abc123def456",
      "value": "abc123def456"
    },
    "name": {
      "display_value": "web-server-prod-01",
      "value": "web-server-prod-01"
    },
    "sys_class_name": {
      "display_value": "Server",
      "value": "cmdb_ci_server"
    },
    "operational_status": {
      "display_value": "Operational",
      "value": "1"
    },
    "location": {
      "display_value": "New York Data Center",
      "value": "loc123"
    },
    "assigned_to": {
      "display_value": "John Smith",
      "value": "user001"
    },
    "manufacturer": {
      "display_value": "Dell",
      "value": "mfg001"
    },
    "environment": {
      "display_value": "Production",
      "value": "Production"
    }
  }
]
```

**When to use each display_value option:**
- `false` (default): Best for programmatic processing when you only need sys_ids for subsequent API calls
- `true`: Best for display purposes when you want human-readable values
- `all`: Best when you need both - displaying to users while retaining sys_ids for follow-up operations

### Relationship Query with Custom Fields

When the `fields` parameter is specified for relationships:

```bash
echo '{
  "action": "relationships",
  "sys_id": "abc123def456",
  "fields": "parent,child,type",
  "display_value": "true"
}' | python scripts/cmdb.py
```

**Response with custom fields and display values:**
```json
[
  {
    "parent": "web-server-prod-01",
    "child": "mysql-db-prod-01",
    "type": "Depends on::Used by"
  },
  {
    "parent": "prod-load-balancer",
    "child": "web-server-prod-01",
    "type": "Routes to::Receives from"
  }
]
```

### Comparing Output Sizes

The following table shows approximate response sizes to help with planning:

| Query Type | Fields | Approximate JSON Size |
|------------|--------|----------------------|
| Single CI | Default (34 fields) | ~2-3 KB |
| Single CI | Custom (5 fields) | ~200-400 bytes |
| 10 CIs | Default | ~20-30 KB |
| 10 CIs | Custom (5 fields) | ~2-4 KB |
| Relationship | Default (8 fields) | ~500 bytes each |
| Relationship | Custom (3 fields) | ~150 bytes each |

**Note:** These sizes are approximate and actual sizes will vary based on field content length. Text-heavy fields like `comments` and `short_description` can vary significantly - a CI with extensive comments may be several KB larger than one with minimal notes.

**Tip:** For performance-sensitive operations or when working with large datasets, specify only the fields you need using the `fields` parameter.

## Error Responses

The CMDB API returns structured error responses when operations fail. Understanding these error formats helps with debugging and error handling in your integrations.

### CI Not Found

When requesting a CI that does not exist:

```bash
echo '{"action": "get", "sys_id": "nonexistent123456789012345678901"}' | python scripts/cmdb.py
```

**Error response:**
```json
{
  "error": {
    "message": "No record found",
    "detail": "Record not found for sys_id: nonexistent123456789012345678901"
  },
  "status": "failure"
}
```

### Invalid Parameters

When providing invalid or malformed parameters:

```bash
echo '{"action": "query", "ci_class": "invalid_class_name"}' | python scripts/cmdb.py
```

**Error response:**
```json
{
  "error": {
    "message": "Invalid table",
    "detail": "Table 'invalid_class_name' does not exist or is not accessible"
  },
  "status": "failure"
}
```

Another example with missing required parameters:

```bash
echo '{"action": "get"}' | python scripts/cmdb.py
```

**Error response:**
```json
{
  "error": {
    "message": "Missing required parameter",
    "detail": "The 'get' action requires one of: sys_id, ip_address, or serial_number"
  },
  "status": "failure"
}
```

### Permission Denied

When the authenticated user lacks permission to access the requested resource:

```bash
echo '{"action": "get", "sys_id": "restricted12345678901234567890123"}' | python scripts/cmdb.py
```

**Error response:**
```json
{
  "error": {
    "message": "Access denied",
    "detail": "User does not have permission to access this CI record. Required role: itil or cmdb_read"
  },
  "status": "failure"
}
```

### Authentication Failure

When API credentials are invalid or expired:

**Error response:**
```json
{
  "error": {
    "message": "Authentication failed",
    "detail": "Invalid credentials or session expired. Please verify your SERVICENOW_INSTANCE, SERVICENOW_USER, and SERVICENOW_PASSWORD environment variables."
  },
  "status": "failure"
}
```

## Related Documentation

For more information about the ServiceNow CMDB, refer to the official documentation:

- [CMDB Overview](https://docs.servicenow.com/bundle/latest/page/product/configuration-management/concept/c_ConfigurationManagementOverview.html) - Introduction to the Configuration Management Database
- [CMDB Table Hierarchy](https://docs.servicenow.com/bundle/latest/page/product/configuration-management/concept/cmdb-tables-background.html) - Understanding CI classes and table structure
- [CI Relationships](https://docs.servicenow.com/bundle/latest/page/product/configuration-management/concept/c_CMDBRelationshipTypes.html) - Learn about relationship types between CIs
- [CMDB API Reference](https://docs.servicenow.com/bundle/latest/page/integrate/inbound-other-web-services/concept/cmdb-api.html) - REST API documentation for CMDB operations
- [Best Practices for CMDB](https://docs.servicenow.com/bundle/latest/page/product/configuration-management/concept/c_BestPractices.html) - Recommendations for CMDB management
