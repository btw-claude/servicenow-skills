# Search Catalog

Search service catalog categories and items by text in ServiceNow.

## Script

```bash
python scripts/catalog.py
```

## Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"search"` |
| `search_term` | Yes | Text to search for in names/descriptions |
| `search_categories` | No | Include categories in search (default: true) |
| `search_items` | No | Include items in search (default: true) |
| `active_only` | No | Only return active records (default: true) |
| `fields` | No | Comma-separated list of fields to return |
| `limit` | No | Maximum number of records to return per type |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

## Examples

### Basic Search

Search for "laptop" in both categories and items:

```bash
echo '{
  "action": "search",
  "search_term": "laptop"
}' | python scripts/catalog.py
```

### Search Items Only

```bash
echo '{
  "action": "search",
  "search_term": "software",
  "search_categories": false,
  "search_items": true
}' | python scripts/catalog.py
```

### Search Categories Only

```bash
echo '{
  "action": "search",
  "search_term": "hardware",
  "search_categories": true,
  "search_items": false
}' | python scripts/catalog.py
```

### Search Including Inactive Records

```bash
echo '{
  "action": "search",
  "search_term": "network",
  "active_only": false
}' | python scripts/catalog.py
```

### Search with Field Selection

```bash
echo '{
  "action": "search",
  "search_term": "monitor",
  "fields": "sys_id,name,short_description,category,price",
  "limit": 10
}' | python scripts/catalog.py
```

### Search with Display Values

```bash
echo '{
  "action": "search",
  "search_term": "printer",
  "display_value": "true",
  "limit": 20
}' | python scripts/catalog.py
```

## Search Behavior

The search matches text in the following fields:

**Categories:**
- `title` - Category title
- `description` - Category description

**Items:**
- `name` - Item name
- `short_description` - Brief description
- `description` - Detailed description

The search uses a `LIKE` operator, which performs a case-insensitive substring match. For example, searching for "lap" will match "Laptop", "laptop", "LAPTOP", and "Overlap".

## Output

JSON object containing separate arrays for categories and items:

```json
{
  "categories": [
    {
      "sys_id": "a1b2c3d4e5f6g7h8i9j0",
      "title": "Hardware",
      "description": "Hardware requests including laptops and monitors",
      "active": "true"
    }
  ],
  "items": [
    {
      "sys_id": "b2c3d4e5f6g7h8i9j0k1",
      "name": "Laptop Request",
      "short_description": "Request a new laptop",
      "description": "Request a new laptop for work purposes",
      "active": "true",
      "price": "1200"
    },
    {
      "sys_id": "c3d4e5f6g7h8i9j0k1l2",
      "name": "Laptop Repair",
      "short_description": "Request laptop repair service",
      "description": "Submit your laptop for hardware repair",
      "active": "true",
      "price": "0"
    }
  ]
}
```

### Empty Results

If no matches are found, empty arrays are returned:

```json
{
  "categories": [],
  "items": []
}
```

### Filtered Results

When searching only categories or items, the other array will be empty:

```json
{
  "categories": [],
  "items": [
    {
      "sys_id": "b2c3d4e5f6g7h8i9j0k1",
      "name": "Laptop Request",
      "short_description": "Request a new laptop"
    }
  ]
}
```

## Errors

The script will output error details to stderr and exit with non-zero status if:

- Required `action` parameter is missing
- Required `search_term` parameter is missing or empty
- Invalid `action` value provided
- User lacks permission to search the catalog
- API authentication fails
