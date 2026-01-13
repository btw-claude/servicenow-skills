---
name: servicenow-itsm
description: ServiceNow ITSM operations for managing incidents, changes, problems, service catalog, CMDB, and companies. Use when working with ServiceNow tickets, querying ITSM data, or automating IT service management workflows.
---

# ServiceNow ITSM Skill

This skill provides comprehensive ServiceNow ITSM integration through Python. It enables incident management, change management, problem management, service catalog operations, CMDB queries, and company/organization management.

## Configuration

Create a `.claude/env` file with your ServiceNow credentials:

```
SERVICENOW_INSTANCE=https://your-instance.service-now.com
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password
```

Alternatively, you can use OAuth or API key authentication:

```
SERVICENOW_INSTANCE=https://your-instance.service-now.com
SERVICENOW_CLIENT_ID=your-client-id
SERVICENOW_CLIENT_SECRET=your-client-secret
```

The credentials require appropriate ServiceNow roles for the operations you intend to perform (e.g., `itil`, `itil_admin`, `catalog_admin`).

## Available Operations

### Incidents

Read the specific skill file for detailed usage and examples.

- `skills/incidents/create-incident.md` - Create new incidents with priority, category, and assignment
- `skills/incidents/get-incident.md` - Retrieve incident details by number or sys_id
- `skills/incidents/update-incident.md` - Update incident fields, state, or assignment
- `skills/incidents/search-incidents.md` - Search incidents using encoded queries
- `skills/incidents/resolve-incident.md` - Resolve or close incidents with resolution notes

### Changes

- `skills/changes/create-change.md` - Create change requests (normal, standard, emergency)
- `skills/changes/get-change.md` - Retrieve change request details
- `skills/changes/update-change.md` - Update change request fields and state
- `skills/changes/search-changes.md` - Search change requests by criteria

### Problems

- `skills/problems/create-problem.md` - Create problem records
- `skills/problems/get-problem.md` - Retrieve problem details
- `skills/problems/update-problem.md` - Update problem fields and root cause
- `skills/problems/search-problems.md` - Search problem records

### Service Catalog

- `skills/catalog/list-catalog-items.md` - List available catalog items
- `skills/catalog/get-catalog-item.md` - Get catalog item details and variables
- `skills/catalog/submit-request.md` - Submit service catalog requests
- `skills/catalog/get-request-status.md` - Check request item status

### CMDB

- `skills/cmdb/query-cis.md` - Query configuration items
- `skills/cmdb/get-ci.md` - Get CI details and relationships
- `skills/cmdb/update-ci.md` - Update CI attributes
- `skills/cmdb/get-relationships.md` - Get CI relationships and dependencies

### Companies

- `skills/companies/list-companies.md` - List company records
- `skills/companies/get-company.md` - Get company details
- `skills/companies/search-companies.md` - Search companies by criteria

## Usage Pattern

1. Identify the operation category (incidents, changes, problems, catalog, cmdb, companies)
2. Read the corresponding skill file for detailed parameters and examples
3. Use the appropriate Python script with required parameters

For ServiceNow encoded query syntax and examples, see `skills/common/encoded-queries.md`.
