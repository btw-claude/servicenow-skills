#!/usr/bin/env python3
"""
ServiceNow Company Operations Module

Provides company record operations for ServiceNow.
Actions: get, get_by_name, query, search, latest
Table: core_company
Query params: name, city, state, country, active
"""

import sys
from typing import Any, Dict, List, Optional

from servicenow_api import (
    ServiceNowClient,
    ServiceNowError,
    ValidationError,
    create_client,
    output_error,
    output_json,
    read_json_input,
)


# =============================================================================
# Constants
# =============================================================================

TABLE_NAME = "core_company"

# Standard company fields commonly requested
DEFAULT_FIELDS = [
    "sys_id",
    "name",
    "street",
    "city",
    "state",
    "zip",
    "country",
    "phone",
    "fax",
    "website",
    "stock_symbol",
    "notes",
    "contact",
    "primary",
    "parent",
    "customer",
    "vendor",
    "manufacturer",
    "active",
    "sys_created_on",
    "sys_updated_on",
]


# =============================================================================
# Company Operations
# =============================================================================

def get_company(
    client: ServiceNowClient,
    sys_id: str,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve a single company by sys_id.

    Args:
        client: ServiceNow API client.
        sys_id: The sys_id of the company to retrieve.
        fields: Optional comma-separated list of fields to return.
            Defaults to DEFAULT_FIELDS if not specified.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        Dictionary containing the company record.

    Raises:
        ValidationError: If sys_id is not provided.
        NotFoundError: If company is not found.
    """
    if not sys_id:
        raise ValidationError("sys_id is required for get action")

    # Use DEFAULT_FIELDS when no specific fields are requested
    effective_fields = fields if fields is not None else ",".join(DEFAULT_FIELDS)

    result = client.get(
        table=TABLE_NAME,
        sys_id=sys_id,
        fields=effective_fields,
        display_value=display_value,
    )

    return result.get("result", {})


def get_company_by_name(
    client: ServiceNowClient,
    name: str,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve a single company by name.

    Args:
        client: ServiceNow API client.
        name: The name of the company (e.g., 'Acme Corporation').
        fields: Optional comma-separated list of fields to return.
            Defaults to DEFAULT_FIELDS if not specified.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        Dictionary containing the company record, or empty dict if not found.

    Raises:
        ValidationError: If name is not provided.
    """
    if not name:
        raise ValidationError("name is required for get_by_name action")

    query = f"name={name}"

    # Use DEFAULT_FIELDS when no specific fields are requested
    effective_fields = fields if fields is not None else ",".join(DEFAULT_FIELDS)

    result = client.get(
        table=TABLE_NAME,
        query=query,
        fields=effective_fields,
        limit=1,
        display_value=display_value,
    )

    records = result.get("result", [])
    return records[0] if records else {}


def query_companies(
    client: ServiceNowClient,
    name: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
    customer: Optional[bool] = None,
    vendor: Optional[bool] = None,
    manufacturer: Optional[bool] = None,
    active: Optional[bool] = None,
    query: Optional[str] = None,
    fields: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    display_value: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query companies with optional filtering parameters.

    Args:
        client: ServiceNow API client.
        name: Filter by company name (exact match).
        city: Filter by city.
        state: Filter by state/province.
        country: Filter by country.
        customer: Filter by customer flag (true/false).
        vendor: Filter by vendor flag (true/false).
        manufacturer: Filter by manufacturer flag (true/false).
        active: Filter by active status (true/false).
        query: Additional encoded query string to append.
        fields: Optional comma-separated list of fields to return.
            Defaults to DEFAULT_FIELDS if not specified.
        limit: Maximum number of records to return.
        offset: Starting record index for pagination.
        order_by: Field to sort by (prefix with - for descending).
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        List of company records matching the query criteria.
    """
    # Build query string from parameters
    query_parts = []

    if name is not None:
        query_parts.append(f"name={name}")

    if city is not None:
        query_parts.append(f"city={city}")

    if state is not None:
        query_parts.append(f"state={state}")

    if country is not None:
        query_parts.append(f"country={country}")

    if customer is not None:
        customer_value = "true" if customer else "false"
        query_parts.append(f"customer={customer_value}")

    if vendor is not None:
        vendor_value = "true" if vendor else "false"
        query_parts.append(f"vendor={vendor_value}")

    if manufacturer is not None:
        manufacturer_value = "true" if manufacturer else "false"
        query_parts.append(f"manufacturer={manufacturer_value}")

    if active is not None:
        active_value = "true" if active else "false"
        query_parts.append(f"active={active_value}")

    # Append any additional query string
    if query:
        query_parts.append(query)

    # Combine query parts with ^ (AND) operator
    full_query = "^".join(query_parts) if query_parts else None

    # Use DEFAULT_FIELDS when no specific fields are requested
    effective_fields = fields if fields is not None else ",".join(DEFAULT_FIELDS)

    result = client.get(
        table=TABLE_NAME,
        query=full_query,
        fields=effective_fields,
        limit=limit,
        offset=offset,
        order_by=order_by,
        display_value=display_value,
    )

    return result.get("result", [])


def search_companies(
    client: ServiceNowClient,
    search_term: str,
    fields: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    display_value: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search companies by name, city, or stock_symbol.

    Args:
        client: ServiceNow API client.
        search_term: Text to search for in name, city, or stock_symbol fields.
        fields: Optional comma-separated list of fields to return.
            Defaults to DEFAULT_FIELDS if not specified.
        limit: Maximum number of records to return.
        offset: Starting record index for pagination.
        order_by: Field to sort by (prefix with - for descending).
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        List of company records matching the search criteria.

    Raises:
        ValidationError: If search_term is not provided.
    """
    if not search_term:
        raise ValidationError("search_term is required for search action")

    # Build search query using CONTAINS operator (LIKE)
    search_conditions = [
        f"nameLIKE{search_term}",
        f"cityLIKE{search_term}",
        f"stock_symbolLIKE{search_term}",
    ]

    # Use OR conditions for search
    search_query = "^OR".join(search_conditions)

    # Use DEFAULT_FIELDS when no specific fields are requested
    effective_fields = fields if fields is not None else ",".join(DEFAULT_FIELDS)

    result = client.get(
        table=TABLE_NAME,
        query=search_query,
        fields=effective_fields,
        limit=limit,
        offset=offset,
        order_by=order_by,
        display_value=display_value,
    )

    return result.get("result", [])


def get_latest_companies(
    client: ServiceNowClient,
    limit: Optional[int] = None,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve the most recently created companies.

    Args:
        client: ServiceNow API client.
        limit: Maximum number of records to return (default: 10).
        fields: Optional comma-separated list of fields to return.
            Defaults to DEFAULT_FIELDS if not specified.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        List of company records sorted by creation date (newest first).
    """
    # Default limit to 10 if not specified
    if limit is None:
        limit = 10

    # Use DEFAULT_FIELDS when no specific fields are requested
    effective_fields = fields if fields is not None else ",".join(DEFAULT_FIELDS)

    result = client.get(
        table=TABLE_NAME,
        fields=effective_fields,
        limit=limit,
        order_by="-sys_created_on",
        display_value=display_value,
    )

    return result.get("result", [])


# =============================================================================
# Action Dispatcher
# =============================================================================

def dispatch_action(params: Dict[str, Any]) -> Any:
    """
    Dispatch to the appropriate action handler based on input parameters.

    Args:
        params: Dictionary containing action and parameters.

    Returns:
        Result from the action handler.

    Raises:
        ValidationError: If action is missing or invalid.
    """
    action = params.get("action")

    if not action:
        raise ValidationError(
            "action is required. Valid actions: get, get_by_name, query, search, latest"
        )

    # Create client
    client = create_client()

    # Common parameters
    fields = params.get("fields")
    display_value = params.get("display_value")

    if action == "get":
        sys_id = params.get("sys_id")
        return get_company(
            client=client,
            sys_id=sys_id,
            fields=fields,
            display_value=display_value,
        )

    elif action == "get_by_name":
        name = params.get("name")
        return get_company_by_name(
            client=client,
            name=name,
            fields=fields,
            display_value=display_value,
        )

    elif action == "query":
        return query_companies(
            client=client,
            name=params.get("name"),
            city=params.get("city"),
            state=params.get("state"),
            country=params.get("country"),
            customer=params.get("customer"),
            vendor=params.get("vendor"),
            manufacturer=params.get("manufacturer"),
            active=params.get("active"),
            query=params.get("query"),
            fields=fields,
            limit=params.get("limit"),
            offset=params.get("offset"),
            order_by=params.get("order_by"),
            display_value=display_value,
        )

    elif action == "search":
        return search_companies(
            client=client,
            search_term=params.get("search_term"),
            fields=fields,
            limit=params.get("limit"),
            offset=params.get("offset"),
            order_by=params.get("order_by"),
            display_value=display_value,
        )

    elif action == "latest":
        return get_latest_companies(
            client=client,
            limit=params.get("limit"),
            fields=fields,
            display_value=display_value,
        )

    else:
        raise ValidationError(
            f"Invalid action: {action}. Valid actions: get, get_by_name, query, search, latest"
        )


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> None:
    """Main entry point for the companies script."""
    try:
        params = read_json_input()
        result = dispatch_action(params)
        output_json(result)

    except ServiceNowError as e:
        output_error(e)
    except Exception as e:
        output_error(e)


if __name__ == "__main__":
    main()
