#!/usr/bin/env python3
"""
ServiceNow Service Catalog Operations Module

Provides service catalog management operations for ServiceNow.
Actions: get_category, get_item, categories, items, search, status, query_requests
Tables: sc_category, sc_cat_item, sc_request, sc_req_item
"""

import sys
from typing import Any, Dict, List, Optional

from servicenow_api import (
    NotFoundError,
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

TABLE_CATEGORY = "sc_category"
TABLE_CAT_ITEM = "sc_cat_item"
TABLE_REQUEST = "sc_request"
TABLE_REQ_ITEM = "sc_req_item"

# Standard catalog category fields
DEFAULT_CATEGORY_FIELDS = [
    "sys_id",
    "title",
    "description",
    "parent",
    "active",
    "icon",
    "order",
    "sc_catalog",
    "sys_created_on",
    "sys_updated_on",
]

# Standard catalog item fields
DEFAULT_ITEM_FIELDS = [
    "sys_id",
    "name",
    "short_description",
    "description",
    "category",
    "price",
    "active",
    "order",
    "availability",
    "icon",
    "picture",
    "sys_created_on",
    "sys_updated_on",
]

# Standard request fields
DEFAULT_REQUEST_FIELDS = [
    "sys_id",
    "number",
    "short_description",
    "description",
    "request_state",
    "stage",
    "requested_for",
    "opened_by",
    "opened_at",
    "closed_at",
    "closed_by",
    "active",
    "approval",
    "price",
    "sys_created_on",
    "sys_updated_on",
]

# Standard request item fields
DEFAULT_REQ_ITEM_FIELDS = [
    "sys_id",
    "number",
    "short_description",
    "description",
    "request",
    "cat_item",
    "stage",
    "state",
    "quantity",
    "price",
    "opened_by",
    "opened_at",
    "closed_at",
    "closed_by",
    "active",
    "sys_created_on",
    "sys_updated_on",
]


# =============================================================================
# Catalog Operations
# =============================================================================

def get_category(
    client: ServiceNowClient,
    sys_id: str,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve a single catalog category by sys_id.

    Args:
        client: ServiceNow API client.
        sys_id: The sys_id of the category to retrieve.
        fields: Optional comma-separated list of fields to return.
            Defaults to DEFAULT_CATEGORY_FIELDS if not specified.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        Dictionary containing the category record.

    Raises:
        ValidationError: If sys_id is not provided.
        NotFoundError: If category is not found.
    """
    if not sys_id:
        raise ValidationError("sys_id is required for get_category action")

    # Use DEFAULT_CATEGORY_FIELDS when no specific fields are requested
    effective_fields = fields if fields is not None else ",".join(DEFAULT_CATEGORY_FIELDS)

    result = client.get(
        table=TABLE_CATEGORY,
        sys_id=sys_id,
        fields=effective_fields,
        display_value=display_value,
    )

    record = result.get("result", {})
    if not record:
        raise NotFoundError(f"Category with sys_id '{sys_id}' not found")
    return record


def get_item(
    client: ServiceNowClient,
    sys_id: str,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve a single catalog item by sys_id.

    Args:
        client: ServiceNow API client.
        sys_id: The sys_id of the catalog item to retrieve.
        fields: Optional comma-separated list of fields to return.
            Defaults to DEFAULT_ITEM_FIELDS if not specified.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        Dictionary containing the catalog item record.

    Raises:
        ValidationError: If sys_id is not provided.
        NotFoundError: If catalog item is not found.
    """
    if not sys_id:
        raise ValidationError("sys_id is required for get_item action")

    # Use DEFAULT_ITEM_FIELDS when no specific fields are requested
    effective_fields = fields if fields is not None else ",".join(DEFAULT_ITEM_FIELDS)

    result = client.get(
        table=TABLE_CAT_ITEM,
        sys_id=sys_id,
        fields=effective_fields,
        display_value=display_value,
    )

    record = result.get("result", {})
    if not record:
        raise NotFoundError(f"Catalog item with sys_id '{sys_id}' not found")
    return record


def get_categories(
    client: ServiceNowClient,
    parent: Optional[str] = None,
    active: Optional[bool] = None,
    query: Optional[str] = None,
    fields: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    display_value: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve service catalog categories.

    Args:
        client: ServiceNow API client.
        parent: Filter by parent category sys_id (use 'null' for top-level).
        active: Filter by active status (true/false).
        query: Additional encoded query string to append.
        fields: Optional comma-separated list of fields to return.
            Defaults to DEFAULT_CATEGORY_FIELDS if not specified.
        limit: Maximum number of records to return.
        offset: Starting record index for pagination.
        order_by: Field to sort by (prefix with - for descending).
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        List of catalog category records.
    """
    query_parts = []

    if parent is not None:
        if parent.lower() == 'null':
            query_parts.append("parentISEMPTY")
        else:
            query_parts.append(f"parent={parent}")

    if active is not None:
        active_value = "true" if active else "false"
        query_parts.append(f"active={active_value}")

    if query:
        query_parts.append(query)

    full_query = "^".join(query_parts) if query_parts else None

    # Use DEFAULT_CATEGORY_FIELDS when no specific fields are requested
    effective_fields = fields if fields is not None else ",".join(DEFAULT_CATEGORY_FIELDS)

    result = client.get(
        table=TABLE_CATEGORY,
        query=full_query,
        fields=effective_fields,
        limit=limit,
        offset=offset,
        order_by=order_by,
        display_value=display_value,
    )

    return result.get("result", [])


def get_items(
    client: ServiceNowClient,
    category: Optional[str] = None,
    active: Optional[bool] = None,
    query: Optional[str] = None,
    fields: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    display_value: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve service catalog items.

    Args:
        client: ServiceNow API client.
        category: Filter by category sys_id.
        active: Filter by active status (true/false).
        query: Additional encoded query string to append.
        fields: Optional comma-separated list of fields to return.
            Defaults to DEFAULT_ITEM_FIELDS if not specified.
        limit: Maximum number of records to return.
        offset: Starting record index for pagination.
        order_by: Field to sort by (prefix with - for descending).
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        List of catalog item records.
    """
    query_parts = []

    if category is not None:
        query_parts.append(f"category={category}")

    if active is not None:
        active_value = "true" if active else "false"
        query_parts.append(f"active={active_value}")

    if query:
        query_parts.append(query)

    full_query = "^".join(query_parts) if query_parts else None

    # Use DEFAULT_ITEM_FIELDS when no specific fields are requested
    effective_fields = fields if fields is not None else ",".join(DEFAULT_ITEM_FIELDS)

    result = client.get(
        table=TABLE_CAT_ITEM,
        query=full_query,
        fields=effective_fields,
        limit=limit,
        offset=offset,
        order_by=order_by,
        display_value=display_value,
    )

    return result.get("result", [])


def search_catalog(
    client: ServiceNowClient,
    search_term: str,
    search_categories: bool = True,
    search_items: bool = True,
    active_only: bool = True,
    fields: Optional[str] = None,
    limit: Optional[int] = None,
    display_value: Optional[str] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Search service catalog categories and/or items by text.

    Args:
        client: ServiceNow API client.
        search_term: Text to search for in names/descriptions.
        search_categories: Include categories in search results.
        search_items: Include items in search results.
        active_only: Only return active records.
        fields: Optional comma-separated list of fields to return.
            Defaults to DEFAULT_CATEGORY_FIELDS for categories,
            DEFAULT_ITEM_FIELDS for items if not specified.
        limit: Maximum number of records to return per type.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        Dictionary with 'categories' and 'items' lists.

    Raises:
        ValidationError: If search_term is not provided.
    """
    if not search_term:
        raise ValidationError("search_term is required for search action")

    results = {
        "categories": [],
        "items": [],
    }

    # Build search query for text matching
    active_filter = "active=true" if active_only else ""

    if search_categories:
        category_query_parts = [
            f"titleLIKE{search_term}^ORdescriptionLIKE{search_term}"
        ]
        if active_filter:
            category_query_parts.append(active_filter)

        category_query = "^".join(category_query_parts)

        # Use DEFAULT_CATEGORY_FIELDS when no specific fields are requested
        category_fields = fields if fields is not None else ",".join(DEFAULT_CATEGORY_FIELDS)

        category_result = client.get(
            table=TABLE_CATEGORY,
            query=category_query,
            fields=category_fields,
            limit=limit,
            display_value=display_value,
        )
        results["categories"] = category_result.get("result", [])

    if search_items:
        item_query_parts = [
            f"nameLIKE{search_term}^ORshort_descriptionLIKE{search_term}^ORdescriptionLIKE{search_term}"
        ]
        if active_filter:
            item_query_parts.append(active_filter)

        item_query = "^".join(item_query_parts)

        # Use DEFAULT_ITEM_FIELDS when no specific fields are requested
        item_fields = fields if fields is not None else ",".join(DEFAULT_ITEM_FIELDS)

        item_result = client.get(
            table=TABLE_CAT_ITEM,
            query=item_query,
            fields=item_fields,
            limit=limit,
            display_value=display_value,
        )
        results["items"] = item_result.get("result", [])

    return results


def get_request_status(
    client: ServiceNowClient,
    request_number: Optional[str] = None,
    request_sys_id: Optional[str] = None,
    include_items: bool = True,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get the status of a service catalog request.

    Args:
        client: ServiceNow API client.
        request_number: The request number (e.g., 'REQ0010001').
        request_sys_id: The request sys_id.
        include_items: Include associated request items in response.
        fields: Optional comma-separated list of fields to return.
            Defaults to DEFAULT_REQUEST_FIELDS for requests,
            DEFAULT_REQ_ITEM_FIELDS for items if not specified.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        Dictionary containing request details and optionally items.

    Raises:
        ValidationError: If neither request_number nor request_sys_id is provided.
    """
    if not request_number and not request_sys_id:
        raise ValidationError(
            "Either request_number or request_sys_id is required for status action"
        )

    # Use DEFAULT_REQUEST_FIELDS when no specific fields are requested
    request_fields = fields if fields is not None else ",".join(DEFAULT_REQUEST_FIELDS)

    # Get the request
    if request_sys_id:
        request_result = client.get(
            table=TABLE_REQUEST,
            sys_id=request_sys_id,
            fields=request_fields,
            display_value=display_value,
        )
        request_data = request_result.get("result", {})
    else:
        query = f"number={request_number}"
        request_result = client.get(
            table=TABLE_REQUEST,
            query=query,
            fields=request_fields,
            limit=1,
            display_value=display_value,
        )
        records = request_result.get("result", [])
        request_data = records[0] if records else {}

    if not request_data:
        return {}

    result = {"request": request_data}

    # Get associated request items if requested
    if include_items:
        request_id = request_data.get("sys_id") or request_sys_id
        if request_id:
            items_query = f"request={request_id}"
            # Use DEFAULT_REQ_ITEM_FIELDS when no specific fields are requested
            item_fields = fields if fields is not None else ",".join(DEFAULT_REQ_ITEM_FIELDS)
            items_result = client.get(
                table=TABLE_REQ_ITEM,
                query=items_query,
                fields=item_fields,
                display_value=display_value,
            )
            result["items"] = items_result.get("result", [])

    return result


def query_requests(
    client: ServiceNowClient,
    request_state: Optional[str] = None,
    stage: Optional[str] = None,
    requested_for: Optional[str] = None,
    opened_by: Optional[str] = None,
    active: Optional[bool] = None,
    query: Optional[str] = None,
    fields: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    display_value: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query service catalog requests with optional filtering parameters.

    Args:
        client: ServiceNow API client.
        request_state: Filter by request state (e.g., 'approved', 'closed_complete').
        stage: Filter by stage (e.g., 'request_approved', 'waiting_for_approval').
        requested_for: Filter by requested_for user sys_id.
        opened_by: Filter by opened_by user sys_id.
        active: Filter by active status (true/false).
        query: Additional encoded query string to append.
        fields: Optional comma-separated list of fields to return.
            Defaults to DEFAULT_REQUEST_FIELDS if not specified.
        limit: Maximum number of records to return.
        offset: Starting record index for pagination.
        order_by: Field to sort by (prefix with - for descending).
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        List of request records matching the query criteria.
    """
    query_parts = []

    if request_state is not None:
        query_parts.append(f"request_state={request_state}")

    if stage is not None:
        query_parts.append(f"stage={stage}")

    if requested_for is not None:
        query_parts.append(f"requested_for={requested_for}")

    if opened_by is not None:
        query_parts.append(f"opened_by={opened_by}")

    if active is not None:
        active_value = "true" if active else "false"
        query_parts.append(f"active={active_value}")

    if query:
        query_parts.append(query)

    full_query = "^".join(query_parts) if query_parts else None

    # Use DEFAULT_REQUEST_FIELDS when no specific fields are requested
    effective_fields = fields if fields is not None else ",".join(DEFAULT_REQUEST_FIELDS)

    result = client.get(
        table=TABLE_REQUEST,
        query=full_query,
        fields=effective_fields,
        limit=limit,
        offset=offset,
        order_by=order_by,
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
            "action is required. Valid actions: get_category, get_item, categories, items, search, status, query_requests"
        )

    # Create client
    client = create_client()

    # Common parameters
    fields = params.get("fields")
    display_value = params.get("display_value")

    if action == "get_category":
        return get_category(
            client=client,
            sys_id=params.get("sys_id"),
            fields=fields,
            display_value=display_value,
        )

    elif action == "get_item":
        return get_item(
            client=client,
            sys_id=params.get("sys_id"),
            fields=fields,
            display_value=display_value,
        )

    elif action == "categories":
        return get_categories(
            client=client,
            parent=params.get("parent"),
            active=params.get("active"),
            query=params.get("query"),
            fields=fields,
            limit=params.get("limit"),
            offset=params.get("offset"),
            order_by=params.get("order_by"),
            display_value=display_value,
        )

    elif action == "items":
        return get_items(
            client=client,
            category=params.get("category"),
            active=params.get("active"),
            query=params.get("query"),
            fields=fields,
            limit=params.get("limit"),
            offset=params.get("offset"),
            order_by=params.get("order_by"),
            display_value=display_value,
        )

    elif action == "search":
        return search_catalog(
            client=client,
            search_term=params.get("search_term", ""),
            search_categories=params.get("search_categories", True),
            search_items=params.get("search_items", True),
            active_only=params.get("active_only", True),
            fields=fields,
            limit=params.get("limit"),
            display_value=display_value,
        )

    elif action == "status":
        return get_request_status(
            client=client,
            request_number=params.get("request_number"),
            request_sys_id=params.get("request_sys_id"),
            include_items=params.get("include_items", True),
            fields=fields,
            display_value=display_value,
        )

    elif action == "query_requests":
        return query_requests(
            client=client,
            request_state=params.get("request_state"),
            stage=params.get("stage"),
            requested_for=params.get("requested_for"),
            opened_by=params.get("opened_by"),
            active=params.get("active"),
            query=params.get("query"),
            fields=fields,
            limit=params.get("limit"),
            offset=params.get("offset"),
            order_by=params.get("order_by"),
            display_value=display_value,
        )

    else:
        raise ValidationError(
            f"Invalid action: {action}. Valid actions: get_category, get_item, categories, items, search, status, query_requests"
        )


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> None:
    """Main entry point for the catalog script."""
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
