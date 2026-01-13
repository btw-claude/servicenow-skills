# Request Status

Check the status of service catalog requests and query requests in ServiceNow.

> **Navigation:** [Back to Skill Index](../../SKILL.md) | [Browse Catalog](./browse-catalog.md) | [Search Catalog](./search-catalog.md)

## Table of Contents

- [Script](#script)
- [Operations](#operations)
  - [Get Request Status](#get-request-status)
  - [Query Requests](#query-requests)
- [Request Fields](#request-fields)
- [Request Item Fields](#request-item-fields)
- [Output](#output)
- [Related Documentation](#related-documentation)
- [Related Domains](#related-domains)
- [Errors](#errors)

## Script

```bash
python scripts/catalog.py
```

## Operations

### Get Request Status

Retrieve the status of a specific service catalog request with its associated request items.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"status"` |
| `request_number` | No* | The request number (e.g., "REQ0010001") |
| `request_sys_id` | No* | The request sys_id |
| `include_items` | No | Include associated request items (default: true) |
| `fields` | No | Comma-separated list of fields to return |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

*Either `request_number` or `request_sys_id` is required.

#### Examples

Get request status by number:

```bash
echo '{
  "action": "status",
  "request_number": "REQ0010001"
}' | python scripts/catalog.py
```

Get request status by sys_id:

```bash
echo '{
  "action": "status",
  "request_sys_id": "a1b2c3d4e5f6g7h8i9j0"
}' | python scripts/catalog.py
```

Get request without items:

```bash
echo '{
  "action": "status",
  "request_number": "REQ0010001",
  "include_items": false
}' | python scripts/catalog.py
```

Get request with display values:

```bash
echo '{
  "action": "status",
  "request_number": "REQ0010001",
  "display_value": "true"
}' | python scripts/catalog.py
```

Get specific fields:

```bash
echo '{
  "action": "status",
  "request_number": "REQ0010001",
  "fields": "number,request_state,stage,opened_at,closed_at"
}' | python scripts/catalog.py
```

### Query Requests

Search and filter service catalog requests with various criteria.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"query_requests"` |
| `request_state` | No | Filter by request state |
| `stage` | No | Filter by stage |
| `requested_for` | No | Filter by requested_for user sys_id |
| `opened_by` | No | Filter by opened_by user sys_id |
| `active` | No | Filter by active status (true/false) |
| `query` | No | Additional encoded query string |
| `fields` | No | Comma-separated list of fields to return |
| `limit` | No | Maximum number of records to return |
| `offset` | No | Starting record index for pagination |
| `order_by` | No | Field to sort by (prefix with `-` for descending) |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Request State Values

| Value | Description |
|-------|-------------|
| `approved` | Request is approved |
| `closed_complete` | Request completed successfully |
| `closed_incomplete` | Request closed without completion |
| `closed_cancelled` | Request was cancelled |
| `closed_rejected` | Request was rejected |

#### Stage Values

| Value | Description |
|-------|-------------|
| `waiting_for_approval` | Awaiting approval |
| `request_approved` | Request has been approved |
| `fulfillment` | Being fulfilled |
| `delivery` | Being delivered |
| `complete` | Complete |

#### Examples

Query active requests:

```bash
echo '{
  "action": "query_requests",
  "active": true
}' | python scripts/catalog.py
```

Query requests by state:

```bash
echo '{
  "action": "query_requests",
  "request_state": "approved",
  "active": true
}' | python scripts/catalog.py
```

Query requests by stage:

```bash
echo '{
  "action": "query_requests",
  "stage": "waiting_for_approval"
}' | python scripts/catalog.py
```

Query requests for a specific user:

```bash
echo '{
  "action": "query_requests",
  "requested_for": "a1b2c3d4e5f6g7h8i9j0",
  "active": true
}' | python scripts/catalog.py
```

Query requests opened by a specific user:

```bash
echo '{
  "action": "query_requests",
  "opened_by": "b2c3d4e5f6g7h8i9j0k1"
}' | python scripts/catalog.py
```

Query with pagination and sorting:

```bash
echo '{
  "action": "query_requests",
  "active": true,
  "limit": 20,
  "offset": 0,
  "order_by": "-opened_at"
}' | python scripts/catalog.py
```

Query with custom encoded query:

```bash
echo '{
  "action": "query_requests",
  "active": true,
  "query": "short_descriptionLIKElaptop^priceGREATERTHAN500"
}' | python scripts/catalog.py
```

## Request Fields

Common fields available for requests:

- `sys_id` - Unique system identifier
- `number` - Request number (e.g., REQ0010001)
- `short_description` - Brief summary
- `description` - Detailed description
- `request_state` - Current request state
- `stage` - Current workflow stage
- `requested_for` - User the request is for
- `opened_by` - User who opened the request
- `opened_at` - When the request was opened
- `closed_at` - When the request was closed
- `closed_by` - User who closed the request
- `active` - Whether the request is active
- `approval` - Approval status
- `price` - Total price
- `sys_created_on` - Creation timestamp
- `sys_updated_on` - Last update timestamp

## Request Item Fields

Common fields available for request items:

- `sys_id` - Unique system identifier
- `number` - Request item number (e.g., RITM0010001)
- `short_description` - Brief summary
- `description` - Detailed description
- `request` - Parent request reference
- `cat_item` - Catalog item reference
- `stage` - Current workflow stage
- `state` - Current state
- `quantity` - Quantity requested
- `price` - Item price
- `opened_by` - User who opened the item
- `opened_at` - When the item was opened
- `closed_at` - When the item was closed
- `closed_by` - User who closed the item
- `active` - Whether the item is active

## Output

### Status Output

JSON object containing the request and optionally its items:

```json
{
  "request": {
    "sys_id": "a1b2c3d4e5f6g7h8i9j0",
    "number": "REQ0010001",
    "short_description": "Laptop and Monitor Request",
    "request_state": "approved",
    "stage": "fulfillment",
    "requested_for": {
      "link": "https://instance.service-now.com/api/now/table/sys_user/def456",
      "value": "def456"
    },
    "opened_at": "<timestamp>",
    "active": "true",
    "price": "1550"
  },
  "items": [
    {
      "sys_id": "b2c3d4e5f6g7h8i9j0k1",
      "number": "RITM0010001",
      "short_description": "Laptop Request",
      "stage": "fulfillment",
      "state": "2",
      "quantity": "1",
      "price": "1200"
    },
    {
      "sys_id": "c3d4e5f6g7h8i9j0k1l2",
      "number": "RITM0010002",
      "short_description": "Monitor Request",
      "stage": "fulfillment",
      "state": "2",
      "quantity": "1",
      "price": "350"
    }
  ]
}
```

Returns an empty object `{}` if the request is not found.

### Query Requests Output

JSON array of request records:

```json
[
  {
    "sys_id": "a1b2c3d4e5f6g7h8i9j0",
    "number": "REQ0010001",
    "short_description": "Laptop Request",
    "request_state": "approved",
    "stage": "fulfillment",
    "active": "true"
  },
  {
    "sys_id": "d4e5f6g7h8i9j0k1l2m3",
    "number": "REQ0010002",
    "short_description": "Software License",
    "request_state": "approved",
    "stage": "delivery",
    "active": "true"
  }
]
```

Returns an empty array `[]` if no requests match the query criteria.

## Related Documentation

- [Browse Catalog](browse-catalog.md) - For browsing catalog categories and items
- [Search Catalog](search-catalog.md) - For text-based searching of categories and items

## Related Domains

Service catalog requests often relate to other ServiceNow domains. Consider these related skills for comprehensive request tracking:

### Incident Management
Track requests related to incident resolution:
- **[Get Incident](../incidents/get-incident.md)** - Retrieve incident details associated with catalog requests
- **[Query Incidents](../incidents/query-incidents.md)** - Find incidents that triggered catalog requests

### Problem Management
Track requests created as part of problem resolution:
- **[Get Problem](../problems/get-problem.md)** - Retrieve problem details associated with catalog requests
- **[Query Problems](../problems/query-problems.md)** - Find problems with pending catalog requests

### Change Management
Track requests that trigger or are associated with changes:
- **[Get Change Request](../changes/get-change.md)** - Retrieve change request details initiated through catalog requests
- **[Query Change Requests](../changes/query-changes.md)** - Find changes associated with catalog requests

> **Tip:** When a catalog request triggers a change, monitor both the request status and the associated change status for complete visibility.

## Errors

The script will output error details to stderr and exit with non-zero status if:

- Required `action` parameter is missing
- Neither `request_number` nor `request_sys_id` provided (for status action)
- Invalid `action` value provided
- Invalid encoded query syntax
- User lacks permission to view requests
- API authentication fails
