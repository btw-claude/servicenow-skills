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

### CI Classes
Common CI classes: `cmdb_ci_server`, `cmdb_ci_computer`, `cmdb_ci_database`, `cmdb_ci_netgear`, `cmdb_ci_service`

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

### Find all servers
```bash
echo '{"action": "query", "ci_class": "cmdb_ci_server"}' | python scripts/cmdb.py
```

### Get CI relationships
```bash
echo '{"action": "relationships", "sys_id": "abc123"}' | python scripts/cmdb.py
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
