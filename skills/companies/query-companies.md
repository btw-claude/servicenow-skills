# Query Companies

Search and filter companies in ServiceNow using various criteria.

## Script

```bash
python scripts/companies.py
```

## Operations

### Query Companies

Filter companies by various attributes.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"query"` |
| `name` | No | Filter by company name (exact match) |
| `city` | No | Filter by city |
| `state` | No | Filter by state/province |
| `country` | No | Filter by country |
| `customer` | No | Filter by customer flag (true/false) |
| `vendor` | No | Filter by vendor flag (true/false) |
| `manufacturer` | No | Filter by manufacturer flag (true/false) |
| `active` | No | Filter by active status (true/false) |
| `query` | No | Additional encoded query string |
| `fields` | No | Comma-separated list of fields to return |
| `limit` | No | Maximum number of records to return |
| `offset` | No | Starting record index for pagination |
| `order_by` | No | Field to sort by (prefix with `-` for descending) |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Examples

Query all active companies:

```bash
echo '{
  "action": "query",
  "active": true
}' | python scripts/companies.py
```

Query customers in a specific city:

```bash
echo '{
  "action": "query",
  "customer": true,
  "city": "San Francisco"
}' | python scripts/companies.py
```

Query vendors by country:

```bash
echo '{
  "action": "query",
  "vendor": true,
  "country": "USA",
  "limit": 50
}' | python scripts/companies.py
```

Paginated query:

```bash
echo '{
  "action": "query",
  "active": true,
  "limit": 10,
  "offset": 0,
  "order_by": "name"
}' | python scripts/companies.py
```

Query with custom encoded query:

```bash
echo '{
  "action": "query",
  "query": "websiteISNOTEMPTY^stock_symbolISNOTEMPTY",
  "limit": 20
}' | python scripts/companies.py
```

### Search Companies

Text search across name, city, and stock_symbol fields.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"search"` |
| `search_term` | Yes | Text to search for |
| `fields` | No | Comma-separated list of fields to return |
| `limit` | No | Maximum number of records to return |
| `offset` | No | Starting record index for pagination |
| `order_by` | No | Field to sort by (prefix with `-` for descending) |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Examples

Search for companies containing "tech":

```bash
echo '{
  "action": "search",
  "search_term": "tech"
}' | python scripts/companies.py
```

Search with limit and specific fields:

```bash
echo '{
  "action": "search",
  "search_term": "global",
  "fields": "name,city,country,website",
  "limit": 25
}' | python scripts/companies.py
```

### Get Latest Companies

Retrieve the most recently created companies.

#### Input

JSON object on stdin:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | Set to `"latest"` |
| `limit` | No | Maximum number of records to return (default: 10) |
| `fields` | No | Comma-separated list of fields to return |
| `display_value` | No | Display value setting (`true`, `false`, `all`) |

#### Examples

Get the 10 most recently created companies:

```bash
echo '{
  "action": "latest"
}' | python scripts/companies.py
```

Get the 5 most recent with specific fields:

```bash
echo '{
  "action": "latest",
  "limit": 5,
  "fields": "name,city,country,sys_created_on"
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

## Encoded Query Syntax

The `query` parameter accepts ServiceNow encoded query syntax. Common operators:

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `city=Boston` |
| `!=` | Not equals | `country!=USA` |
| `LIKE` | Contains | `nameLIKEtech` |
| `STARTSWITH` | Starts with | `nameSTARTSWITHAcme` |
| `ENDSWITH` | Ends with | `nameENDSWITHInc` |
| `IN` | In list | `countryINUSA,Canada,UK` |
| `NOTIN` | Not in list | `stateNOTINCA,NY,TX` |
| `ISEMPTY` | Is empty | `websiteISEMPTY` |
| `ISNOTEMPTY` | Is not empty | `phoneISNOTEMPTY` |
| `^` | AND | `customer=true^active=true` |
| `^OR` | OR | `customer=true^ORvendor=true` |

### Date Queries

| Operator | Description | Example |
|----------|-------------|---------|
| `ON` | On specific date | `sys_created_onON2024-01-15` |
| `BEFORE` | Before date | `sys_created_onBEFORE2024-01-15` |
| `AFTER` | After date | `sys_created_onAFTER2024-01-15` |
| `BETWEEN` | Between dates | `sys_created_onBETWEEN2024-01-01@2024-01-31` |
| `RELATIVE` | Relative to now | `sys_created_onRELATIVEGE@dayofweek@ago@2` |

### Dot-Walking (Related Records)

Query fields on related records using dot notation:

```bash
echo '{
  "action": "query",
  "query": "parent.name=Parent Corp^contact.email!=null"
}' | python scripts/companies.py
```

## Output

JSON array of company records matching the query:

```json
[
  {
    "sys_id": "a1b2c3d4e5f6g7h8i9j0",
    "name": "Acme Corporation",
    "city": "San Francisco",
    "state": "CA",
    "country": "USA",
    "phone": "+1-415-555-1234",
    "website": "https://www.acme.com",
    "customer": "true",
    "vendor": "false",
    "active": "true"
  },
  {
    "sys_id": "b2c3d4e5f6g7h8i9j0k1",
    "name": "Global Tech Solutions",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "phone": "+1-212-555-6789",
    "website": "https://www.globaltech.com",
    "customer": "true",
    "vendor": "true",
    "active": "true"
  }
]
```

Returns an empty array `[]` if no companies match the query criteria.

## Errors

The script will output error details to stderr and exit with non-zero status if:

- Required `action` parameter is missing
- Invalid `action` value provided
- Required `search_term` (for search) is missing
- Invalid encoded query syntax
- User lacks permission to query companies
- API authentication fails
