# Get Company

Retrieve company details from ServiceNow by sys_id or company name.

## Script

```bash
python scripts/companies.py
```

## Operations

### Get by sys_id

Retrieve a company using its unique system identifier.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"get"` |
| `sys_id` | Yes | The sys_id of the company |
| `fields` | No | Comma-separated list of fields to return |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Example

```bash
echo '{
  "action": "get",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0"
}' | python scripts/companies.py
```

Get specific fields only:

```bash
echo '{
  "action": "get",
  "sys_id": "a1b2c3d4e5f6g7h8i9j0",
  "fields": "name,city,state,country,phone,website"
}' | python scripts/companies.py
```

### Get by Name

Retrieve a company using its exact name.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"get_by_name"` |
| `name` | Yes | The exact company name (e.g., "Acme Corporation") |
| `fields` | No | Comma-separated list of fields to return |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Example

```bash
echo '{
  "action": "get_by_name",
  "name": "Acme Corporation"
}' | python scripts/companies.py
```

Get with display values:

```bash
echo '{
  "action": "get_by_name",
  "name": "Acme Corporation",
  "display_value": "true"
}' | python scripts/companies.py
```

## Parameters

### Fields Parameter

Specify which fields to include in the response. Common company fields:

- `sys_id` - Unique system identifier
- `name` - Company name
- `street` - Street address
- `city` - City
- `state` - State/province
- `zip` - ZIP/postal code
- `country` - Country
- `phone` - Phone number
- `fax` - Fax number
- `website` - Company website URL
- `stock_symbol` - Stock ticker symbol
- `notes` - Additional notes
- `contact` - Primary contact reference
- `primary` - Primary flag
- `parent` - Parent company reference
- `customer` - Customer flag (true/false)
- `vendor` - Vendor flag (true/false)
- `manufacturer` - Manufacturer flag (true/false)
- `active` - Whether the company record is active
- `sys_created_on` - Record creation timestamp
- `sys_updated_on` - Record last update timestamp

### Display Value Parameter

Controls how reference fields are returned:

- `false` (default) - Returns sys_id values for reference fields
- `true` - Returns display values (human-readable names)
- `all` - Returns both sys_id and display value

## Output

JSON object containing the company record:

```json
{
  "sys_id": "a1b2c3d4e5f6g7h8i9j0",
  "name": "Acme Corporation",
  "street": "123 Main Street",
  "city": "San Francisco",
  "state": "CA",
  "zip": "94102",
  "country": "USA",
  "phone": "+1-415-555-1234",
  "fax": "+1-415-555-1235",
  "website": "https://www.acme.com",
  "stock_symbol": "ACME",
  "customer": "true",
  "vendor": "false",
  "manufacturer": "false",
  "active": "true",
  "parent": {
    "link": "https://instance.service-now.com/api/now/table/core_company/parent123",
    "value": "parent123"
  },
  "sys_created_on": "2024-01-15 10:30:00"
}
```

Returns an empty object `{}` if:
- Company is not found (for get_by_name)

## Errors

The script will output error details to stderr and exit with non-zero status if:

- Required `action` parameter is missing
- Required `sys_id` (for get) or `name` (for get_by_name) is missing
- Company is not found (NotFoundError for get by sys_id)
- User lacks permission to view the company
- API authentication fails
