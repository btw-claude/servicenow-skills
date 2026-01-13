#!/usr/bin/env python3
"""
ServiceNow Change Request Operations Module

Provides change request management operations for ServiceNow ITSM.
Actions: get, get_by_number, query
Table: change_request
Query params: state, type, risk, assignment_group, active
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

TABLE_NAME = "change_request"

# Standard change request fields commonly requested
DEFAULT_FIELDS = [
    "sys_id",
    "number",
    "short_description",
    "description",
    "state",
    "type",
    "risk",
    "priority",
    "assignment_group",
    "assigned_to",
    "requested_by",
    "category",
    "start_date",
    "end_date",
    "planned_start_date",
    "planned_end_date",
    "work_start",
    "work_end",
    "opened_at",
    "opened_by",
    "closed_at",
    "closed_by",
    "close_code",
    "close_notes",
    "active",
    "approval",
    "phase",
    "reason",
    "conflict_status",
    "cab_required",
    "sys_created_on",
    "sys_updated_on",
]


# =============================================================================
# Change Request Operations
# =============================================================================

def get_change(
    client: ServiceNowClient,
    sys_id: str,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve a single change request by sys_id.

    Args:
        client: ServiceNow API client.
        sys_id: The sys_id of the change request to retrieve.
        fields: Optional comma-separated list of fields to return.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        Dictionary containing the change request record.

    Raises:
        ValidationError: If sys_id is not provided.
        NotFoundError: If change request is not found.
    """
    if not sys_id:
        raise ValidationError("sys_id is required for get action")

    result = client.get(
        table=TABLE_NAME,
        sys_id=sys_id,
        fields=fields,
        display_value=display_value,
    )

    return result.get("result", {})


def get_change_by_number(
    client: ServiceNowClient,
    number: str,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve a single change request by change number.

    Args:
        client: ServiceNow API client.
        number: The change request number (e.g., 'CHG0010001').
        fields: Optional comma-separated list of fields to return.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        Dictionary containing the change request record, or empty dict if not found.

    Raises:
        ValidationError: If number is not provided.
    """
    if not number:
        raise ValidationError("number is required for get_by_number action")

    query = f"number={number}"

    result = client.get(
        table=TABLE_NAME,
        query=query,
        fields=fields,
        limit=1,
        display_value=display_value,
    )

    records = result.get("result", [])
    return records[0] if records else {}


def query_changes(
    client: ServiceNowClient,
    state: Optional[str] = None,
    type: Optional[str] = None,
    risk: Optional[str] = None,
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
    Query change requests with optional filtering parameters.

    Args:
        client: ServiceNow API client.
        state: Filter by change state (-5=New, -4=Assess, -3=Authorize,
               -2=Scheduled, -1=Implement, 0=Review, 3=Closed, 4=Canceled).
        type: Filter by change type (standard, normal, emergency).
        risk: Filter by risk level (1=High, 2=Moderate, 3=Low).
        assignment_group: Filter by assignment group name or sys_id.
        active: Filter by active status (true/false).
        query: Additional encoded query string to append.
        fields: Optional comma-separated list of fields to return.
        limit: Maximum number of records to return.
        offset: Starting record index for pagination.
        order_by: Field to sort by (prefix with - for descending).
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        List of change request records matching the query criteria.
    """
    # Build query string from parameters
    query_parts = []

    if state is not None:
        query_parts.append(f"state={state}")

    if type is not None:
        query_parts.append(f"type={type}")

    if risk is not None:
        query_parts.append(f"risk={risk}")

    if assignment_group is not None:
        # Support both sys_id and name lookup
        query_parts.append(f"assignment_group={assignment_group}")

    if active is not None:
        active_value = "true" if active else "false"
        query_parts.append(f"active={active_value}")

    # Append any additional query string
    if query:
        query_parts.append(query)

    # Combine query parts with ^ (AND) operator
    full_query = "^".join(query_parts) if query_parts else None

    result = client.get(
        table=TABLE_NAME,
        query=full_query,
        fields=fields,
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
        return get_change(
            client=client,
            sys_id=sys_id,
            fields=fields,
            display_value=display_value,
        )

    elif action == "get_by_number":
        number = params.get("number")
        return get_change_by_number(
            client=client,
            number=number,
            fields=fields,
            display_value=display_value,
        )

    elif action == "query":
        return query_changes(
            client=client,
            state=params.get("state"),
            type=params.get("type"),
            risk=params.get("risk"),
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
    """Main entry point for the changes script."""
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
