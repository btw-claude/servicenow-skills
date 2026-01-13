# Browse Catalog

Browse service catalog categories and items in ServiceNow.

## Script

```bash
python scripts/catalog.py
```

## Operations

### List Categories

Retrieve service catalog categories with optional filtering.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"categories"` |
| `parent` | No | Filter by parent category sys_id (use `"null"` for top-level) |
| `active` | No | Filter by active status (true/false) |
| `query` | No | Additional encoded query string |
| `fields` | No | Comma-separated list of fields to return |
| `limit` | No | Maximum number of records to return |
| `offset` | No | Starting record index for pagination |
| `order_by` | No | Field to sort by (prefix with `-` for descending) |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Examples

Get all active categories:

```bash
echo '{
  "action": "categories",
  "active": true
}' | python scripts/catalog.py
```

Get top-level categories only:

```bash
echo '{
  "action": "categories",
  "parent": "null",
  "active": true
}' | python scripts/catalog.py
```

Get subcategories of a specific category:

```bash
echo '{
  "action": "categories",
  "parent": "a1b2c3d4e5f6g7h8i9j0"
}' | python scripts/catalog.py
```

Get categories with pagination:

```bash
echo '{
  "action": "categories",
  "active": true,
  "limit": 10,
  "offset": 0,
  "order_by": "title"
}' | python scripts/catalog.py
```

### List Catalog Items

Retrieve service catalog items with optional filtering.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"items"` |
| `category` | No | Filter by category sys_id |
| `active` | No | Filter by active status (true/false) |
| `query` | No | Additional encoded query string |
| `fields` | No | Comma-separated list of fields to return |
| `limit` | No | Maximum number of records to return |
| `offset` | No | Starting record index for pagination |
| `order_by` | No | Field to sort by (prefix with `-` for descending) |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Examples

Get all active catalog items:

```bash
echo '{
  "action": "items",
  "active": true
}' | python scripts/catalog.py
```

Get items in a specific category:

```bash
echo '{
  "action": "items",
  "category": "a1b2c3d4e5f6g7h8i9j0",
  "active": true
}' | python scripts/catalog.py
```

Get items with specific fields:

```bash
echo '{
  "action": "items",
  "active": true,
  "fields": "sys_id,name,short_description,category,price",
  "limit": 20
}' | python scripts/catalog.py
```

Get items sorted by name:

```bash
echo '{
  "action": "items",
  "active": true,
  "order_by": "name",
  "limit": 50
}' | python scripts/catalog.py
```

## Category Fields

Common fields available for categories:

- `sys_id` - Unique system identifier
- `title` - Category title
- `description` - Category description
- `parent` - Parent category reference
- `active` - Whether the category is active
- `icon` - Category icon
- `order` - Display order
- `sc_catalog` - Associated service catalog
- `sys_created_on` - Creation timestamp
- `sys_updated_on` - Last update timestamp

## Item Fields

Common fields available for catalog items:

- `sys_id` - Unique system identifier
- `name` - Item name
- `short_description` - Brief description
- `description` - Detailed description
- `category` - Associated category
- `price` - Item price
- `active` - Whether the item is active
- `order` - Display order
- `availability` - Availability status
- `icon` - Item icon
- `picture` - Item picture
- `sys_created_on` - Creation timestamp
- `sys_updated_on` - Last update timestamp

## Output

### Categories Output

JSON array of category records:

```json
[
  {
    "sys_id": "a1b2c3d4e5f6g7h8i9j0",
    "title": "Hardware",
    "description": "Hardware requests and services",
    "active": "true",
    "parent": "",
    "order": "100"
  },
  {
    "sys_id": "b2c3d4e5f6g7h8i9j0k1",
    "title": "Software",
    "description": "Software installation and licensing",
    "active": "true",
    "parent": "",
    "order": "200"
  }
]
```

### Items Output

JSON array of item records:

```json
[
  {
    "sys_id": "c3d4e5f6g7h8i9j0k1l2",
    "name": "Laptop Request",
    "short_description": "Request a new laptop",
    "category": {
      "link": "https://instance.service-now.com/api/now/table/sc_category/a1b2c3d4",
      "value": "a1b2c3d4"
    },
    "price": "1200",
    "active": "true"
  },
  {
    "sys_id": "d4e5f6g7h8i9j0k1l2m3",
    "name": "Monitor Request",
    "short_description": "Request an additional monitor",
    "category": {
      "link": "https://instance.service-now.com/api/now/table/sc_category/a1b2c3d4",
      "value": "a1b2c3d4"
    },
    "price": "350",
    "active": "true"
  }
]
```

Returns an empty array `[]` if no records match the criteria.

## Errors

The script will output error details to stderr and exit with non-zero status if:

- Required `action` parameter is missing
- Invalid `action` value provided
- Invalid encoded query syntax
- User lacks permission to browse the catalog
- API authentication fails
