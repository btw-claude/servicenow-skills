#!/usr/bin/env python3
"""
ServiceNow CMDB Operations Module

Provides Configuration Management Database (CMDB) operations for ServiceNow.
Actions: get, get_by_name, query, search, relationships, by_ip, by_serial
Tables: cmdb_ci, cmdb_rel_ci
Query params: ci_class, operational_status, location
"""

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

TABLE_NAME = "cmdb_ci"
RELATIONSHIP_TABLE = "cmdb_rel_ci"

# Standard CMDB CI fields commonly requested
DEFAULT_FIELDS = [
    "sys_id",
    "name",
    "sys_class_name",
    "asset_tag",
    "serial_number",
    "ip_address",
    "mac_address",
    "dns_domain",
    "fqdn",
    "operational_status",
    "install_status",
    "location",
    "department",
    "company",
    "assigned_to",
    "managed_by",
    "owned_by",
    "supported_by",
    "manufacturer",
    "model_id",
    "model_number",
    "vendor",
    "cost",
    "cost_center",
    "purchase_date",
    "warranty_expiration",
    "first_discovered",
    "last_discovered",
    "discovery_source",
    "environment",
    "short_description",
    "comments",
    "active",
    "sys_created_on",
    "sys_updated_on",
]

# Standard CMDB relationship fields
RELATIONSHIP_FIELDS = [
    "sys_id",
    "parent",
    "child",
    "type",
    "connection_strength",
    "port",
    "sys_created_on",
    "sys_updated_on",
]


# =============================================================================
# CMDB Operations
# =============================================================================

def get_ci(
    client: ServiceNowClient,
    sys_id: str,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve a single Configuration Item by sys_id.

    Args:
        client: ServiceNow API client.
        sys_id: The sys_id of the CI to retrieve.
        fields: Optional comma-separated list of fields to return.
            When None, defaults to DEFAULT_FIELDS constant defined at module level.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        Dictionary containing the CI record.

    Raises:
        ValidationError: If sys_id is not provided.
        NotFoundError: If CI is not found.
    """
    if not sys_id:
        raise ValidationError("sys_id is required for get action")

    effective_fields = fields if fields is not None else ",".join(DEFAULT_FIELDS)

    result = client.get(
        table=TABLE_NAME,
        sys_id=sys_id,
        fields=effective_fields,
        display_value=display_value,
    )

    return result.get("result", {})


def get_ci_by_name(
    client: ServiceNowClient,
    name: str,
    ci_class: Optional[str] = None,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve a single Configuration Item by name.

    Args:
        client: ServiceNow API client.
        name: The name of the CI to retrieve.
        ci_class: Optional filter by CI class name.
        fields: Optional comma-separated list of fields to return.
            When None, defaults to DEFAULT_FIELDS constant defined at module level.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        Dictionary containing the CI record.

    Raises:
        ValidationError: If name is not provided.
        NotFoundError: If CI with the given name is not found.
    """
    if not name:
        raise ValidationError("name is required for get_by_name action")

    query_parts = [f"name={name}"]
    if ci_class is not None:
        query_parts.append(f"sys_class_name={ci_class}")

    full_query = "^".join(query_parts)
    effective_fields = fields if fields is not None else ",".join(DEFAULT_FIELDS)

    result = client.get(
        table=TABLE_NAME,
        query=full_query,
        fields=effective_fields,
        limit=1,
        display_value=display_value,
    )

    records = result.get("result", [])
    if not records:
        raise NotFoundError(f"CI with name '{name}' not found")
    return records[0]


def query_cis(
    client: ServiceNowClient,
    ci_class: Optional[str] = None,
    operational_status: Optional[str] = None,
    location: Optional[str] = None,
    query: Optional[str] = None,
    fields: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    display_value: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query Configuration Items with optional filtering parameters.

    Args:
        client: ServiceNow API client.
        ci_class: Filter by CI class name (e.g., 'cmdb_ci_server', 'cmdb_ci_computer').
        operational_status: Filter by operational status (1=Operational, 2=Non-Operational,
                          3=Repair in Progress, 4=DR Standby, 5=Ready, 6=Retired).
        location: Filter by location name or sys_id.
        query: Additional encoded query string to append.
        fields: Optional comma-separated list of fields to return.
            When None, defaults to DEFAULT_FIELDS constant defined at module level.
        limit: Maximum number of records to return.
        offset: Starting record index for pagination.
        order_by: Field to sort by (prefix with - for descending).
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        List of CI records matching the query criteria.
    """
    query_parts = []

    if ci_class is not None:
        query_parts.append(f"sys_class_name={ci_class}")
    if operational_status is not None:
        query_parts.append(f"operational_status={operational_status}")
    if location is not None:
        query_parts.append(f"location={location}")
    if query:
        query_parts.append(query)

    full_query = "^".join(query_parts) if query_parts else None
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


def search_cis(
    client: ServiceNowClient,
    search_term: str,
    ci_class: Optional[str] = None,
    fields: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    display_value: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Search Configuration Items by name, asset_tag, or serial_number.

    Args:
        client: ServiceNow API client.
        search_term: Text to search for in name, asset_tag, or serial_number fields.
        ci_class: Optional filter by CI class name.
        fields: Optional comma-separated list of fields to return.
            When None, defaults to DEFAULT_FIELDS constant defined at module level.
        limit: Maximum number of records to return.
        offset: Starting record index for pagination.
        order_by: Field to sort by (prefix with - for descending).
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        List of CI records matching the search criteria.

    Raises:
        ValidationError: If search_term is not provided.
    """
    if not search_term:
        raise ValidationError("search_term is required for search action")

    search_conditions = [
        f"nameLIKE{search_term}",
        f"asset_tagLIKE{search_term}",
        f"serial_numberLIKE{search_term}",
    ]
    search_query = "^OR".join(search_conditions)

    if ci_class is not None:
        search_query = f"sys_class_name={ci_class}^({search_query})"

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


def get_ci_relationships(
    client: ServiceNowClient,
    sys_id: str,
    relationship_type: Optional[str] = None,
    direction: Optional[str] = None,
    fields: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    display_value: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve relationships for a Configuration Item.

    Args:
        client: ServiceNow API client.
        sys_id: The sys_id of the CI to get relationships for.
        relationship_type: Optional filter by relationship type sys_id.
        direction: Optional direction filter ('parent', 'child', 'both').
                  'parent' returns relationships where CI is the parent.
                  'child' returns relationships where CI is the child.
                  'both' or None returns all relationships.
        fields: Optional comma-separated list of fields to return.
            When None, defaults to RELATIONSHIP_FIELDS constant defined at module level.
        limit: Maximum number of records to return.
        offset: Starting record index for pagination.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        List of relationship records for the CI.

    Raises:
        ValidationError: If sys_id is not provided.
    """
    if not sys_id:
        raise ValidationError("sys_id is required for relationships action")

    query_parts = []
    if direction == "parent":
        query_parts.append(f"parent={sys_id}")
    elif direction == "child":
        query_parts.append(f"child={sys_id}")
    else:
        query_parts.append(f"parent={sys_id}^ORchild={sys_id}")

    if relationship_type is not None:
        query_parts.append(f"type={relationship_type}")

    full_query = "^".join(query_parts) if query_parts else None
    effective_fields = fields if fields is not None else ",".join(RELATIONSHIP_FIELDS)

    result = client.get(
        table=RELATIONSHIP_TABLE,
        query=full_query,
        fields=effective_fields,
        limit=limit,
        offset=offset,
        display_value=display_value,
    )

    return result.get("result", [])


def get_ci_by_ip(
    client: ServiceNowClient,
    ip_address: str,
    ci_class: Optional[str] = None,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve Configuration Items by IP address.

    Args:
        client: ServiceNow API client.
        ip_address: The IP address to search for.
        ci_class: Optional filter by CI class name.
        fields: Optional comma-separated list of fields to return.
            When None, defaults to DEFAULT_FIELDS constant defined at module level.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        List of CI records matching the IP address.

    Raises:
        ValidationError: If ip_address is not provided.
    """
    if not ip_address:
        raise ValidationError("ip_address is required for by_ip action")

    query_parts = [f"ip_address={ip_address}"]
    if ci_class is not None:
        query_parts.append(f"sys_class_name={ci_class}")

    full_query = "^".join(query_parts)
    effective_fields = fields if fields is not None else ",".join(DEFAULT_FIELDS)

    result = client.get(
        table=TABLE_NAME,
        query=full_query,
        fields=effective_fields,
        display_value=display_value,
    )

    return result.get("result", [])


def get_ci_by_serial(
    client: ServiceNowClient,
    serial_number: str,
    ci_class: Optional[str] = None,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve Configuration Items by serial number.

    Args:
        client: ServiceNow API client.
        serial_number: The serial number to search for.
        ci_class: Optional filter by CI class name.
        fields: Optional comma-separated list of fields to return.
            When None, defaults to DEFAULT_FIELDS constant defined at module level.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        List of CI records matching the serial number.

    Raises:
        ValidationError: If serial_number is not provided.
    """
    if not serial_number:
        raise ValidationError("serial_number is required for by_serial action")

    query_parts = [f"serial_number={serial_number}"]
    if ci_class is not None:
        query_parts.append(f"sys_class_name={ci_class}")

    full_query = "^".join(query_parts)
    effective_fields = fields if fields is not None else ",".join(DEFAULT_FIELDS)

    result = client.get(
        table=TABLE_NAME,
        query=full_query,
        fields=effective_fields,
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
            "action is required. Valid actions: get, get_by_name, query, search, relationships, by_ip, by_serial"
        )

    # Create client
    client = create_client()

    # Common parameters
    fields = params.get("fields")
    display_value = params.get("display_value")

    if action == "get":
        sys_id = params.get("sys_id")
        return get_ci(
            client=client,
            sys_id=sys_id,
            fields=fields,
            display_value=display_value,
        )

    elif action == "get_by_name":
        return get_ci_by_name(
            client=client,
            name=params.get("name"),
            ci_class=params.get("ci_class"),
            fields=fields,
            display_value=display_value,
        )

    elif action == "query":
        return query_cis(
            client=client,
            ci_class=params.get("ci_class"),
            operational_status=params.get("operational_status"),
            location=params.get("location"),
            query=params.get("query"),
            fields=fields,
            limit=params.get("limit"),
            offset=params.get("offset"),
            order_by=params.get("order_by"),
            display_value=display_value,
        )

    elif action == "search":
        return search_cis(
            client=client,
            search_term=params.get("search_term"),
            ci_class=params.get("ci_class"),
            fields=fields,
            limit=params.get("limit"),
            offset=params.get("offset"),
            order_by=params.get("order_by"),
            display_value=display_value,
        )

    elif action == "relationships":
        return get_ci_relationships(
            client=client,
            sys_id=params.get("sys_id"),
            relationship_type=params.get("relationship_type"),
            direction=params.get("direction"),
            fields=fields,
            limit=params.get("limit"),
            offset=params.get("offset"),
            display_value=display_value,
        )

    elif action == "by_ip":
        return get_ci_by_ip(
            client=client,
            ip_address=params.get("ip_address"),
            ci_class=params.get("ci_class"),
            fields=fields,
            display_value=display_value,
        )

    elif action == "by_serial":
        return get_ci_by_serial(
            client=client,
            serial_number=params.get("serial_number"),
            ci_class=params.get("ci_class"),
            fields=fields,
            display_value=display_value,
        )

    else:
        raise ValidationError(
            f"Invalid action: {action}. Valid actions: get, get_by_name, query, search, relationships, by_ip, by_serial"
        )


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> None:
    """Main entry point for the CMDB script."""
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
