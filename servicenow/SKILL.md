---
name: servicenow-itsm
description: ServiceNow ITSM operations for managing incidents, changes, problems, service catalog, CMDB, and companies. Use when working with ServiceNow tickets, querying ITSM data, or automating IT service management workflows.
---

# ServiceNow ITSM Skill

This skill provides ServiceNow ITSM integration through Python scripts. For configuration, authentication setup, and security considerations, see `README.md`.

## Available Operations

### Incidents

Read the specific skill file for detailed usage and examples.

- `skills/incidents/get-incident.md` - Retrieve incident details by number or sys_id
- `skills/incidents/query-incidents.md` - Search incidents using encoded queries

### Changes

- `skills/changes/get-change.md` - Retrieve change request details
- `skills/changes/query-changes.md` - Search change requests by criteria

### Problems

- `skills/problems/get-problem.md` - Retrieve problem details
- `skills/problems/query-problems.md` - Search problem records

### Service Catalog

- `skills/catalog/browse-catalog.md` - Browse available catalog items
- `skills/catalog/search-catalog.md` - Search catalog items
- `skills/catalog/request-status.md` - Check request item status

### CMDB

- `skills/cmdb/query-cis.md` - Query configuration items
- `skills/cmdb/get-ci.md` - Get CI details
- `skills/cmdb/ci-relationships.md` - Get CI relationships and dependencies

### Companies

- `skills/companies/get-company.md` - Get company details
- `skills/companies/query-companies.md` - Search companies by criteria

## Usage Pattern

1. Identify the operation category (incidents, changes, problems, catalog, cmdb, companies)
2. Read the corresponding skill file for detailed parameters and examples
3. Use the appropriate Python script with required parameters

## Script Invocation

All scripts accept JSON input on stdin and output JSON to stdout. Base directory for scripts: `scripts/`

### Script Mapping

| Domain | Script | Operations |
|--------|--------|------------|
| Incidents | `scripts/incidents.py` | get, query |
| Changes | `scripts/changes.py` | get, query |
| Problems | `scripts/problems.py` | get, query |
| Catalog | `scripts/catalog.py` | browse, search, request-status |
| CMDB | `scripts/cmdb.py` | query-cis, get-ci, relationships |
| Companies | `scripts/companies.py` | get, query |

### Common Script Pattern

```bash
echo '{"action": "<action>", ...params}' | python scripts/<domain>.py
```

### Example Invocations

Get an incident:
```bash
echo '{"action": "get", "number": "INC0010001"}' | python scripts/incidents.py
```

Query changes:
```bash
echo '{"action": "query", "query": "state=1", "limit": 10}' | python scripts/changes.py
```

Search catalog:
```bash
echo '{"action": "search", "query": "laptop"}' | python scripts/catalog.py
```

For ServiceNow encoded query syntax and detailed configuration, see `README.md`.
