#!/usr/bin/env python3
"""
ServiceNow Incident Operations Module

Provides incident management operations for ServiceNow ITSM.
Actions: get, get_by_number, query
Table: incident
Query params: state, urgency, impact, assignment_group, active
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

TABLE_NAME = "incident"

# Standard incident fields commonly requested
DEFAULT_FIELDS = [
    "sys_id",
    "number",
    "short_description",
    "description",
    "state",
    "urgency",
    "impact",
    "priority",
    "assignment_group",
    "assigned_to",
    "caller_id",
    "category",
    "subcategory",
    "opened_at",
    "opened_by",
    "resolved_at",
    "resolved_by",
    "closed_at",
    "closed_by",
    "close_code",
    "close_notes",
    "active",
    "sys_created_on",
    "sys_updated_on",
]


# =============================================================================
# Incident Operations
# =============================================================================

def get_incident(
    client: ServiceNowClient,
    sys_id: str,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve a single incident by sys_id.

    Args:
        client: ServiceNow API client.
        sys_id: The sys_id of the incident to retrieve.
        fields: Optional comma-separated list of fields to return.
            When None, defaults to DEFAULT_FIELDS constant defined at module level.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        Dictionary containing the incident record.

    Raises:
        ValidationError: If sys_id is not provided.
        NotFoundError: If incident is not found.
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

    record = result.get("result", {})
    if not record:
        raise NotFoundError(f"Incident with sys_id '{sys_id}' not found")
    return record


def get_incident_by_number(
    client: ServiceNowClient,
    number: str,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve a single incident by incident number.

    Args:
        client: ServiceNow API client.
        number: The incident number (e.g., 'INC0010001').
        fields: Optional comma-separated list of fields to return.
            When None, defaults to DEFAULT_FIELDS constant defined at module level.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        Dictionary containing the incident record.

    Raises:
        ValidationError: If number is not provided.
        NotFoundError: If incident with the given number is not found.
    """
    if not number:
        raise ValidationError("number is required for get_by_number action")

    query = f"number={number}"
    effective_fields = fields if fields is not None else ",".join(DEFAULT_FIELDS)

    result = client.get(
        table=TABLE_NAME,
        query=query,
        fields=effective_fields,
        limit=1,
        display_value=display_value,
    )

    records = result.get("result", [])
    if not records:
        raise NotFoundError(f"Incident with number '{number}' not found")
    return records[0]


def query_incidents(
    client: ServiceNowClient,
    state: Optional[str] = None,
    urgency: Optional[str] = None,
    impact: Optional[str] = None,
    assignment_group: Optional[str] = None,
    active: Optional[bool] = None,
    query: Optional[str] = None,
    fields: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    display_value: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query incidents with optional filtering parameters.

    Args:
        client: ServiceNow API client.
        state: Filter by incident state (1=New, 2=In Progress, 3=On Hold,
               6=Resolved, 7=Closed, 8=Canceled).
        urgency: Filter by urgency (1=High, 2=Medium, 3=Low).
        impact: Filter by impact (1=High, 2=Medium, 3=Low).
        assignment_group: Filter by assignment group name or sys_id.
        active: Filter by active status (true/false).
        query: Additional encoded query string to append.
        fields: Optional comma-separated list of fields to return.
            When None, defaults to DEFAULT_FIELDS constant defined at module level.
        limit: Maximum number of records to return.
        offset: Starting record index for pagination.
        order_by: Field to sort by (prefix with - for descending).
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        List of incident records matching the query criteria.
    """
    query_parts = []

    if state is not None:
        query_parts.append(f"state={state}")

    if urgency is not None:
        query_parts.append(f"urgency={urgency}")

    if impact is not None:
        query_parts.append(f"impact={impact}")

    if assignment_group is not None:
        # Support both sys_id and name lookup
        query_parts.append(f"assignment_group={assignment_group}")

    if active is not None:
        active_value = "true" if active else "false"
        query_parts.append(f"active={active_value}")

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
            "action is required. Valid actions: get, get_by_number, query"
        )

    # Create client
    client = create_client()

    # Common parameters
    fields = params.get("fields")
    display_value = params.get("display_value")

    if action == "get":
        sys_id = params.get("sys_id")
        return get_incident(
            client=client,
            sys_id=sys_id,
            fields=fields,
            display_value=display_value,
        )

    elif action == "get_by_number":
        number = params.get("number")
        return get_incident_by_number(
            client=client,
            number=number,
            fields=fields,
            display_value=display_value,
        )

    elif action == "query":
        return query_incidents(
            client=client,
            state=params.get("state"),
            urgency=params.get("urgency"),
            impact=params.get("impact"),
            assignment_group=params.get("assignment_group"),
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
            f"Invalid action: {action}. Valid actions: get, get_by_number, query"
        )


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> None:
    """Main entry point for the incidents script."""
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
