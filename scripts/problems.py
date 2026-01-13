#!/usr/bin/env python3
"""
ServiceNow Problem Operations Module

Provides problem management operations for ServiceNow ITSM.
Actions: get, get_by_number, query
Table: problem
Query params: state, priority, assignment_group, known_error, active
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

TABLE_NAME = "problem"

# Standard problem fields commonly requested
DEFAULT_FIELDS = [
    "sys_id",
    "number",
    "short_description",
    "description",
    "state",
    "priority",
    "assignment_group",
    "assigned_to",
    "opened_at",
    "opened_by",
    "resolved_at",
    "resolved_by",
    "closed_at",
    "closed_by",
    "close_notes",
    "active",
    "known_error",
    "first_reported_by_task",
    "cause_notes",
    "fix_notes",
    "workaround",
    "major_problem",
    "problem_state",
    "resolution_code",
    "related_incidents",
    "sys_created_on",
    "sys_updated_on",
]


# =============================================================================
# Problem Operations
# =============================================================================

def get_problem(
    client: ServiceNowClient,
    sys_id: str,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve a single problem by sys_id.

    Args:
        client: ServiceNow API client.
        sys_id: The sys_id of the problem to retrieve.
        fields: Optional comma-separated list of fields to return.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        Dictionary containing the problem record.

    Raises:
        ValidationError: If sys_id is not provided.
        NotFoundError: If problem is not found.
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


def get_problem_by_number(
    client: ServiceNowClient,
    number: str,
    fields: Optional[str] = None,
    display_value: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve a single problem by problem number.

    Args:
        client: ServiceNow API client.
        number: The problem number (e.g., 'PRB0010001').
        fields: Optional comma-separated list of fields to return.
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        Dictionary containing the problem record, or empty dict if not found.

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


def query_problems(
    client: ServiceNowClient,
    state: Optional[str] = None,
    priority: Optional[str] = None,
    assignment_group: Optional[str] = None,
    known_error: Optional[bool] = None,
    active: Optional[bool] = None,
    query: Optional[str] = None,
    fields: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    display_value: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query problems with optional filtering parameters.

    Args:
        client: ServiceNow API client.
        state: Filter by problem state (1=Open, 2=Known Error, 3=Pending Change,
               4=Closed/Resolved, 5=Closed/Cancelled).
        priority: Filter by priority (1=Critical, 2=High, 3=Moderate, 4=Low, 5=Planning).
        assignment_group: Filter by assignment group name or sys_id.
        known_error: Filter by known error status (true/false).
        active: Filter by active status (true/false).
        query: Additional encoded query string to append.
        fields: Optional comma-separated list of fields to return.
        limit: Maximum number of records to return.
        offset: Starting record index for pagination.
        order_by: Field to sort by (prefix with - for descending).
        display_value: Optional display value setting ('true', 'false', 'all').

    Returns:
        List of problem records matching the query criteria.
    """
    # Build query string from parameters
    query_parts = []

    if state is not None:
        query_parts.append(f"state={state}")

    if priority is not None:
        query_parts.append(f"priority={priority}")

    if assignment_group is not None:
        # Support both sys_id and name lookup
        query_parts.append(f"assignment_group={assignment_group}")

    if known_error is not None:
        known_error_value = "true" if known_error else "false"
        query_parts.append(f"known_error={known_error_value}")

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
        return get_problem(
            client=client,
            sys_id=sys_id,
            fields=fields,
            display_value=display_value,
        )

    elif action == "get_by_number":
        number = params.get("number")
        return get_problem_by_number(
            client=client,
            number=number,
            fields=fields,
            display_value=display_value,
        )

    elif action == "query":
        return query_problems(
            client=client,
            state=params.get("state"),
            priority=params.get("priority"),
            assignment_group=params.get("assignment_group"),
            known_error=params.get("known_error"),
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
    """Main entry point for the problems script."""
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
