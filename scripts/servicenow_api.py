#!/usr/bin/env python3
"""
ServiceNow API Client Module

Base API client for ServiceNow REST API operations with environment loading,
authentication support (Basic and OAuth), and comprehensive error handling.
"""

import os
import re
import sys
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any, Union
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlparse, urlunparse


# =============================================================================
# Error Handling Classes
# =============================================================================

class ServiceNowError(Exception):
    """Base exception for ServiceNow API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None,
                 response_body: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization."""
        result = {"error": self.message}
        if self.status_code:
            result["status_code"] = self.status_code
        if self.response_body:
            try:
                result["details"] = json.loads(self.response_body)
            except json.JSONDecodeError:
                result["details"] = self.response_body
        return result


class AuthenticationError(ServiceNowError):
    """Raised when authentication fails."""
    pass


class ConfigurationError(ServiceNowError):
    """Raised when required configuration is missing or invalid."""
    pass


class NotFoundError(ServiceNowError):
    """Raised when a requested resource is not found."""
    pass


class RateLimitError(ServiceNowError):
    """Raised when API rate limit is exceeded."""
    pass


class ValidationError(ServiceNowError):
    """Raised when request validation fails."""
    pass


# =============================================================================
# Environment Loading
# =============================================================================

def _parse_quoted_value(value: str) -> str:
    """
    Parse a quoted value, handling escaped quotes and common escape sequences.

    Args:
        value: The value string (with or without quotes).

    Returns:
        The unquoted value with escape sequences resolved.

    Supported escape sequences:
        - \\" or \\' - escaped quotes
        - \\\\ - escaped backslash
        - \\n - newline
        - \\t - tab
    """
    value = value.strip()

    if not value:
        return value

    # Check for double-quoted strings
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        # Remove outer quotes and process escaped characters
        inner = value[1:-1]
        # Handle escape sequences (order matters: backslash first, then others)
        inner = inner.replace('\\\\', '\x00')  # Temporarily replace escaped backslash
        inner = inner.replace('\\"', '"')
        inner = inner.replace('\\n', '\n')
        inner = inner.replace('\\t', '\t')
        inner = inner.replace('\x00', '\\')  # Restore backslash
        return inner

    # Check for single-quoted strings
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        # Remove outer quotes and process escaped characters
        inner = value[1:-1]
        # Handle escape sequences (order matters: backslash first, then others)
        inner = inner.replace('\\\\', '\x00')  # Temporarily replace escaped backslash
        inner = inner.replace("\\'", "'")
        inner = inner.replace('\\n', '\n')
        inner = inner.replace('\\t', '\t')
        inner = inner.replace('\x00', '\\')  # Restore backslash
        return inner

    return value


def load_env_file(env_path: Optional[Path] = None) -> Dict[str, str]:
    """
    Load environment variables from a .claude/env file.

    Args:
        env_path: Optional path to the env file. If not provided, searches
                  in standard locations (~/.claude/env).

    Returns:
        Dictionary of environment variables loaded from the file.
    """
    env_vars = {}

    if env_path is None:
        # Search in standard locations
        search_paths = [
            Path.home() / ".claude" / "env",
            Path.cwd() / ".claude" / "env",
        ]
    else:
        search_paths = [env_path]

    for path in search_paths:
        if path.exists():
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue
                    # Parse KEY=VALUE format
                    if "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = _parse_quoted_value(value)
                        env_vars[key] = value
            break  # Use first found env file

    return env_vars


def get_config() -> Dict[str, Optional[str]]:
    """
    Get ServiceNow configuration from environment variables.

    Environment variables are first loaded from .claude/env file,
    then overridden by actual environment variables if set.

    Returns:
        Dictionary containing ServiceNow configuration.

    Raises:
        ConfigurationError: If required configuration is missing.
    """
    # Load from env file first
    file_vars = load_env_file()

    # Get timeout value with env vars taking precedence
    timeout_str = os.environ.get("SERVICENOW_TIMEOUT", file_vars.get("SERVICENOW_TIMEOUT"))
    timeout_value = None
    if timeout_str:
        try:
            timeout_value = int(timeout_str)
        except ValueError:
            pass  # Invalid timeout value, will use default

    # Get configuration with env vars taking precedence
    config = {
        "instance": os.environ.get("SERVICENOW_INSTANCE", file_vars.get("SERVICENOW_INSTANCE")),
        "username": os.environ.get("SERVICENOW_USERNAME", file_vars.get("SERVICENOW_USERNAME")),
        "password": os.environ.get("SERVICENOW_PASSWORD", file_vars.get("SERVICENOW_PASSWORD")),
        "client_id": os.environ.get("SERVICENOW_CLIENT_ID", file_vars.get("SERVICENOW_CLIENT_ID")),
        "client_secret": os.environ.get("SERVICENOW_CLIENT_SECRET", file_vars.get("SERVICENOW_CLIENT_SECRET")),
        "api_key": os.environ.get("SERVICENOW_API_KEY", file_vars.get("SERVICENOW_API_KEY")),
        "timeout": timeout_value,
    }

    # Validate required configuration
    if not config["instance"]:
        raise ConfigurationError(
            "SERVICENOW_INSTANCE is required. Set it in ~/.claude/env or as an environment variable."
        )

    # Ensure instance URL doesn't have trailing slash
    config["instance"] = config["instance"].rstrip("/")

    # Check for valid authentication method
    has_basic_auth = config["username"] and config["password"]
    has_oauth = config["client_id"] and config["client_secret"]
    has_api_key = config["api_key"]

    if not (has_basic_auth or has_oauth or has_api_key):
        raise ConfigurationError(
            "No valid authentication configured. Provide either:\n"
            "  - SERVICENOW_USERNAME and SERVICENOW_PASSWORD for Basic auth\n"
            "  - SERVICENOW_CLIENT_ID and SERVICENOW_CLIENT_SECRET for OAuth\n"
            "  - SERVICENOW_API_KEY for API key authentication"
        )

    return config


# =============================================================================
# ServiceNow API Client
# =============================================================================

class ServiceNowClient:
    """
    ServiceNow REST API client.

    Supports Basic authentication, OAuth 2.0, and API key authentication.
    Provides methods for common CRUD operations against ServiceNow tables.
    """

    # Default timeout in seconds for HTTP requests
    DEFAULT_TIMEOUT = 30

    def __init__(self, config: Optional[Dict[str, Any]] = None,
                 timeout: Optional[int] = None):
        """
        Initialize the ServiceNow client.

        Args:
            config: Optional configuration dictionary. If not provided,
                    configuration is loaded from environment.
            timeout: Optional timeout in seconds for HTTP requests.
                     Defaults to SERVICENOW_TIMEOUT env var, or DEFAULT_TIMEOUT (30 seconds).
        """
        self.config = config or get_config()
        self.instance = self.config["instance"]
        # Priority: explicit timeout param > config timeout (from env) > default
        if timeout is not None:
            self.timeout = timeout
        elif self.config.get("timeout") is not None:
            self.timeout = self.config["timeout"]
        else:
            self.timeout = self.DEFAULT_TIMEOUT
        self._access_token: Optional[str] = None
        self._token_type: str = "Bearer"

    def _get_auth_header(self) -> Dict[str, str]:
        """
        Get the appropriate authorization header based on configured auth method.

        Returns:
            Dictionary containing the Authorization header.

        Raises:
            AuthenticationError: If authentication fails.
        """
        # API Key authentication
        if self.config.get("api_key"):
            return {"Authorization": f"Bearer {self.config['api_key']}"}

        # OAuth authentication
        if self.config.get("client_id") and self.config.get("client_secret"):
            if not self._access_token:
                self._obtain_oauth_token()
            return {"Authorization": f"{self._token_type} {self._access_token}"}

        # Basic authentication
        if self.config.get("username") and self.config.get("password"):
            credentials = f"{self.config['username']}:{self.config['password']}"
            encoded = base64.b64encode(credentials.encode()).decode()
            return {"Authorization": f"Basic {encoded}"}

        raise AuthenticationError("No valid authentication method available")

    def _obtain_oauth_token(self) -> None:
        """
        Obtain OAuth 2.0 access token using client credentials flow.

        Raises:
            AuthenticationError: If token retrieval fails.
        """
        token_url = f"{self.instance}/oauth_token.do"

        data = urlencode({
            "grant_type": "client_credentials",
            "client_id": self.config["client_id"],
            "client_secret": self.config["client_secret"],
        }).encode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        try:
            request = Request(token_url, data=data, headers=headers, method="POST")
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode())
                self._access_token = result.get("access_token")
                self._token_type = result.get("token_type", "Bearer")

                if not self._access_token:
                    raise AuthenticationError("OAuth response did not contain access_token")

        except HTTPError as e:
            body = e.read().decode() if e.fp else None
            raise AuthenticationError(
                f"OAuth authentication failed: {e.reason}",
                status_code=e.code,
                response_body=body
            )
        except URLError as e:
            raise AuthenticationError(f"Failed to connect for OAuth: {e.reason}")

    def _build_url(self, table: str, sys_id: Optional[str] = None,
                   api_path: str = "/api/now/table") -> str:
        """
        Build the full URL for an API request.

        Args:
            table: ServiceNow table name.
            sys_id: Optional sys_id for single record operations.
            api_path: API path prefix (default: /api/now/table).

        Returns:
            Full URL string.
        """
        if sys_id:
            return f"{self.instance}{api_path}/{table}/{sys_id}"
        return f"{self.instance}{api_path}/{table}"

    def _make_request(self, method: str, url: str,
                      data: Optional[Dict[str, Any]] = None,
                      params: Optional[Dict[str, Any]] = None,
                      _retry: bool = False) -> Dict[str, Any]:
        """
        Make an HTTP request to the ServiceNow API.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE).
            url: Full URL for the request (should be base URL without query params).
            data: Optional request body data.
            params: Optional query parameters.
            _retry: Internal flag to prevent infinite retry loops on 401.

        Returns:
            Parsed JSON response.

        Raises:
            ServiceNowError: On API errors.
            AuthenticationError: On authentication failures.
            NotFoundError: When resource is not found.
            RateLimitError: When rate limit is exceeded.
        """
        # Build final URL with query parameters
        final_url = url
        if params:
            query_string = urlencode(params)
            final_url = f"{url}?{query_string}"

        # Prepare headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        headers.update(self._get_auth_header())

        # Prepare request body
        body = json.dumps(data).encode() if data else None

        try:
            request = Request(final_url, data=body, headers=headers, method=method)
            with urlopen(request, timeout=self.timeout) as response:
                response_body = response.read().decode()
                if response_body:
                    return json.loads(response_body)
                return {}

        except HTTPError as e:
            body = e.read().decode() if e.fp else None

            if e.code == 401:
                # Clear cached token and retry once for OAuth
                if self._access_token and not _retry:
                    self._access_token = None
                    # Retry with the base URL (without query params) - params will be re-added
                    return self._make_request(method, url, data, params, _retry=True)
                raise AuthenticationError(
                    "Authentication failed",
                    status_code=e.code,
                    response_body=body
                )
            elif e.code == 403:
                raise AuthenticationError(
                    "Access forbidden - insufficient permissions",
                    status_code=e.code,
                    response_body=body
                )
            elif e.code == 404:
                raise NotFoundError(
                    "Resource not found",
                    status_code=e.code,
                    response_body=body
                )
            elif e.code == 429:
                raise RateLimitError(
                    "Rate limit exceeded",
                    status_code=e.code,
                    response_body=body
                )
            elif e.code == 400:
                raise ValidationError(
                    "Invalid request",
                    status_code=e.code,
                    response_body=body
                )
            else:
                raise ServiceNowError(
                    f"API request failed: {e.reason}",
                    status_code=e.code,
                    response_body=body
                )

        except URLError as e:
            raise ServiceNowError(f"Failed to connect to ServiceNow: {e.reason}")

    def get(self, table: str, sys_id: Optional[str] = None,
            query: Optional[str] = None, fields: Optional[str] = None,
            limit: Optional[int] = None, offset: Optional[int] = None,
            order_by: Optional[str] = None,
            display_value: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve records from a ServiceNow table.

        Args:
            table: ServiceNow table name (e.g., 'incident', 'change_request').
            sys_id: Optional sys_id to retrieve a single record.
            query: Optional encoded query string for filtering.
            fields: Optional comma-separated list of fields to return.
            limit: Optional maximum number of records to return.
            offset: Optional starting record index for pagination.
            order_by: Optional field to sort results by (prefix with - for descending).
            display_value: Optional display value setting ('true', 'false', 'all').

        Returns:
            Dictionary containing the response with 'result' key.

        Example:
            # Get single incident
            client.get('incident', sys_id='abc123')

            # Search incidents with query
            client.get('incident', query='state=1^priority=1', limit=10)

            # Get specific fields only
            client.get('incident', fields='number,short_description,state')
        """
        url = self._build_url(table, sys_id)

        params = {}
        if query:
            params["sysparm_query"] = query
        if fields:
            params["sysparm_fields"] = fields
        if limit is not None:
            params["sysparm_limit"] = limit
        if offset is not None:
            params["sysparm_offset"] = offset
        if order_by:
            params["sysparm_order_by"] = order_by
        if display_value:
            params["sysparm_display_value"] = display_value

        return self._make_request("GET", url, params=params if params else None)

    def post(self, table: str, data: Dict[str, Any],
             display_value: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new record in a ServiceNow table.

        Args:
            table: ServiceNow table name.
            data: Dictionary of field values for the new record.
            display_value: Optional display value setting.

        Returns:
            Dictionary containing the created record.
        """
        url = self._build_url(table)

        params = {}
        if display_value:
            params["sysparm_display_value"] = display_value

        return self._make_request("POST", url, data=data,
                                  params=params if params else None)

    def put(self, table: str, sys_id: str, data: Dict[str, Any],
            display_value: Optional[str] = None) -> Dict[str, Any]:
        """
        Update a record in a ServiceNow table (full replacement).

        Args:
            table: ServiceNow table name.
            sys_id: The sys_id of the record to update.
            data: Dictionary of field values to set.
            display_value: Optional display value setting.

        Returns:
            Dictionary containing the updated record.
        """
        url = self._build_url(table, sys_id)

        params = {}
        if display_value:
            params["sysparm_display_value"] = display_value

        return self._make_request("PUT", url, data=data,
                                  params=params if params else None)

    def patch(self, table: str, sys_id: str, data: Dict[str, Any],
              display_value: Optional[str] = None) -> Dict[str, Any]:
        """
        Partially update a record in a ServiceNow table.

        Args:
            table: ServiceNow table name.
            sys_id: The sys_id of the record to update.
            data: Dictionary of field values to update.
            display_value: Optional display value setting.

        Returns:
            Dictionary containing the updated record.
        """
        url = self._build_url(table, sys_id)

        params = {}
        if display_value:
            params["sysparm_display_value"] = display_value

        return self._make_request("PATCH", url, data=data,
                                  params=params if params else None)

    def delete(self, table: str, sys_id: str) -> Dict[str, Any]:
        """
        Delete a record from a ServiceNow table.

        Args:
            table: ServiceNow table name.
            sys_id: The sys_id of the record to delete.

        Returns:
            Empty dictionary on success.
        """
        url = self._build_url(table, sys_id)
        return self._make_request("DELETE", url)


# =============================================================================
# Utility Functions
# =============================================================================

def create_client(config: Optional[Dict[str, Any]] = None,
                  timeout: Optional[int] = None) -> ServiceNowClient:
    """
    Factory function to create a ServiceNow client.

    Args:
        config: Optional configuration dictionary.
        timeout: Optional timeout in seconds for HTTP requests.

    Returns:
        Configured ServiceNowClient instance.
    """
    return ServiceNowClient(config, timeout=timeout)


def read_json_input() -> Dict[str, Any]:
    """
    Read and parse JSON input from stdin.

    Returns:
        Parsed JSON as dictionary.

    Raises:
        ValidationError: If input is not valid JSON.
    """
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            return {}
        return json.loads(input_data)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON input: {e}")


def output_json(data: Any) -> None:
    """
    Output data as formatted JSON to stdout.

    Args:
        data: Data to serialize as JSON.
    """
    print(json.dumps(data, indent=2))


def output_error(error: Union[ServiceNowError, Exception]) -> None:
    """
    Output error as JSON to stderr and exit with non-zero status.

    Args:
        error: Exception to output.
    """
    if isinstance(error, ServiceNowError):
        error_data = error.to_dict()
    else:
        error_data = {"error": str(error)}

    print(json.dumps(error_data, indent=2), file=sys.stderr)
    sys.exit(1)


# =============================================================================
# Main (for testing/standalone use)
# =============================================================================

if __name__ == "__main__":
    # Simple test: try to create client and validate configuration
    try:
        client = create_client()
        output_json({
            "status": "ok",
            "message": "ServiceNow client configured successfully",
            "instance": client.instance
        })
    except ServiceNowError as e:
        output_error(e)
    except Exception as e:
        output_error(e)
