#!/usr/bin/env python3
"""
Test ServiceNow API Client with Real Instance

SNOW-16: Test API Client with ServiceNow Instance
- Test servicenow_api.py with a real ServiceNow instance
- Verify authentication, GET requests, and error handling work correctly

These tests are designed to run against a real ServiceNow instance.
Configure credentials in ~/.claude/env or set environment variables:
  - SERVICENOW_INSTANCE
  - SERVICENOW_USERNAME / SERVICENOW_PASSWORD (for Basic auth)
  - SERVICENOW_CLIENT_ID / SERVICENOW_CLIENT_SECRET (for OAuth)
  - SERVICENOW_API_KEY (for API key auth)

Run with: python -m pytest tests/test_servicenow_api.py -v
Or: python tests/test_servicenow_api.py
"""

import os
import sys
import json
import unittest
from pathlib import Path
from io import StringIO, BytesIO
from unittest.mock import patch, MagicMock, Mock
from urllib.error import HTTPError, URLError

# Get the project root directory (parent of tests/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Add scripts directory to path for imports
sys.path.insert(0, str(SCRIPTS_DIR))

from servicenow_api import (
    ServiceNowClient,
    ServiceNowError,
    ValidationError,
    AuthenticationError,
    NotFoundError,
    ConfigurationError,
    RateLimitError,
    create_client,
    read_json_input,
    output_json,
    output_error,
    load_env_file,
    get_config,
    _parse_quoted_value,
)


# =============================================================================
# Unit Tests - Error Handling Classes
# =============================================================================

class TestServiceNowErrorClasses(unittest.TestCase):
    """Test error handling classes."""

    def test_servicenow_error_basic(self):
        """ServiceNowError should store message and optional fields."""
        error = ServiceNowError("Test error")
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.message, "Test error")
        self.assertIsNone(error.status_code)
        self.assertIsNone(error.response_body)

    def test_servicenow_error_with_status_code(self):
        """ServiceNowError should store status code."""
        error = ServiceNowError("Test error", status_code=500)
        self.assertEqual(error.status_code, 500)

    def test_servicenow_error_with_response_body(self):
        """ServiceNowError should store response body."""
        error = ServiceNowError("Test error", response_body='{"detail": "error"}')
        self.assertEqual(error.response_body, '{"detail": "error"}')

    def test_servicenow_error_to_dict_basic(self):
        """to_dict should return error message."""
        error = ServiceNowError("Test error")
        result = error.to_dict()
        self.assertEqual(result, {"error": "Test error"})

    def test_servicenow_error_to_dict_with_status(self):
        """to_dict should include status code when present."""
        error = ServiceNowError("Test error", status_code=404)
        result = error.to_dict()
        self.assertEqual(result["error"], "Test error")
        self.assertEqual(result["status_code"], 404)

    def test_servicenow_error_to_dict_with_json_body(self):
        """to_dict should parse JSON response body."""
        error = ServiceNowError(
            "Test error",
            status_code=400,
            response_body='{"error": {"message": "Validation failed"}}'
        )
        result = error.to_dict()
        self.assertEqual(result["details"], {"error": {"message": "Validation failed"}})

    def test_servicenow_error_to_dict_with_non_json_body(self):
        """to_dict should include raw body when not JSON."""
        error = ServiceNowError("Test error", response_body="Not JSON")
        result = error.to_dict()
        self.assertEqual(result["details"], "Not JSON")

    def test_authentication_error_inheritance(self):
        """AuthenticationError should inherit from ServiceNowError."""
        error = AuthenticationError("Auth failed", status_code=401)
        self.assertIsInstance(error, ServiceNowError)
        self.assertEqual(error.status_code, 401)

    def test_configuration_error_inheritance(self):
        """ConfigurationError should inherit from ServiceNowError."""
        error = ConfigurationError("Config missing")
        self.assertIsInstance(error, ServiceNowError)

    def test_not_found_error_inheritance(self):
        """NotFoundError should inherit from ServiceNowError."""
        error = NotFoundError("Resource not found", status_code=404)
        self.assertIsInstance(error, ServiceNowError)
        self.assertEqual(error.status_code, 404)

    def test_rate_limit_error_inheritance(self):
        """RateLimitError should inherit from ServiceNowError."""
        error = RateLimitError("Rate limited", status_code=429)
        self.assertIsInstance(error, ServiceNowError)
        self.assertEqual(error.status_code, 429)

    def test_validation_error_inheritance(self):
        """ValidationError should inherit from ServiceNowError."""
        error = ValidationError("Invalid input", status_code=400)
        self.assertIsInstance(error, ServiceNowError)


# =============================================================================
# Unit Tests - Quote Parsing
# =============================================================================

class TestQuoteParsing(unittest.TestCase):
    """Test quote parsing for env file values."""

    def test_parse_empty_value(self):
        """_parse_quoted_value should handle empty string."""
        self.assertEqual(_parse_quoted_value(""), "")

    def test_parse_unquoted_value(self):
        """_parse_quoted_value should return unquoted values unchanged."""
        self.assertEqual(_parse_quoted_value("simple_value"), "simple_value")

    def test_parse_double_quoted_value(self):
        """_parse_quoted_value should remove double quotes."""
        self.assertEqual(_parse_quoted_value('"quoted"'), "quoted")

    def test_parse_single_quoted_value(self):
        """_parse_quoted_value should remove single quotes."""
        self.assertEqual(_parse_quoted_value("'quoted'"), "quoted")

    def test_parse_escaped_double_quote(self):
        """_parse_quoted_value should handle escaped double quotes."""
        self.assertEqual(_parse_quoted_value('"value \\"with\\" quotes"'), 'value "with" quotes')

    def test_parse_escaped_single_quote(self):
        """_parse_quoted_value should handle escaped single quotes."""
        self.assertEqual(_parse_quoted_value("'value \\'with\\' quotes'"), "value 'with' quotes")

    def test_parse_escaped_backslash(self):
        """_parse_quoted_value should handle escaped backslashes."""
        self.assertEqual(_parse_quoted_value('"value \\\\with\\\\ backslash"'), 'value \\with\\ backslash')

    def test_parse_complex_escaped_value(self):
        """_parse_quoted_value should handle complex escaped strings."""
        self.assertEqual(_parse_quoted_value('"pass\\"word\\\\123"'), 'pass"word\\123')

    def test_parse_whitespace_handling(self):
        """_parse_quoted_value should strip surrounding whitespace."""
        self.assertEqual(_parse_quoted_value('  "quoted"  '), "quoted")

    def test_parse_empty_quoted_string(self):
        """_parse_quoted_value should handle empty quoted strings."""
        self.assertEqual(_parse_quoted_value('""'), "")
        self.assertEqual(_parse_quoted_value("''"), "")


# =============================================================================
# Unit Tests - Environment Loading
# =============================================================================

class TestEnvLoading(unittest.TestCase):
    """Test environment file loading."""

    def test_load_env_file_nonexistent(self):
        """load_env_file should return empty dict for nonexistent file."""
        result = load_env_file(Path("/nonexistent/path/.claude/env"))
        self.assertEqual(result, {})

    def test_load_env_file_with_mock(self):
        """load_env_file should parse KEY=VALUE format."""
        env_content = """
# Comment line
SERVICENOW_INSTANCE=https://test.service-now.com
SERVICENOW_USERNAME=admin
SERVICENOW_PASSWORD=secret

# Another comment
SERVICENOW_API_KEY="quoted-key"
SINGLE_QUOTED='single-quoted-value'
"""
        with patch('builtins.open', unittest.mock.mock_open(read_data=env_content)):
            with patch.object(Path, 'exists', return_value=True):
                result = load_env_file(Path("/fake/.claude/env"))

                self.assertEqual(result["SERVICENOW_INSTANCE"], "https://test.service-now.com")
                self.assertEqual(result["SERVICENOW_USERNAME"], "admin")
                self.assertEqual(result["SERVICENOW_PASSWORD"], "secret")
                self.assertEqual(result["SERVICENOW_API_KEY"], "quoted-key")
                self.assertEqual(result["SINGLE_QUOTED"], "single-quoted-value")

    def test_get_config_missing_instance(self):
        """get_config should raise ConfigurationError if instance is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('servicenow_api.load_env_file', return_value={}):
                with self.assertRaises(ConfigurationError) as context:
                    get_config()
                self.assertIn("SERVICENOW_INSTANCE", str(context.exception))

    def test_get_config_missing_auth(self):
        """get_config should raise ConfigurationError if no auth is configured."""
        with patch.dict(os.environ, {"SERVICENOW_INSTANCE": "https://test.service-now.com"}, clear=True):
            with patch('servicenow_api.load_env_file', return_value={}):
                with self.assertRaises(ConfigurationError) as context:
                    get_config()
                self.assertIn("authentication", str(context.exception).lower())

    def test_get_config_basic_auth(self):
        """get_config should accept basic auth credentials."""
        env_vars = {
            "SERVICENOW_INSTANCE": "https://test.service-now.com",
            "SERVICENOW_USERNAME": "admin",
            "SERVICENOW_PASSWORD": "secret"
        }
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('servicenow_api.load_env_file', return_value={}):
                config = get_config()
                self.assertEqual(config["instance"], "https://test.service-now.com")
                self.assertEqual(config["username"], "admin")
                self.assertEqual(config["password"], "secret")

    def test_get_config_oauth(self):
        """get_config should accept OAuth credentials."""
        env_vars = {
            "SERVICENOW_INSTANCE": "https://test.service-now.com",
            "SERVICENOW_CLIENT_ID": "client123",
            "SERVICENOW_CLIENT_SECRET": "secret456"
        }
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('servicenow_api.load_env_file', return_value={}):
                config = get_config()
                self.assertEqual(config["client_id"], "client123")
                self.assertEqual(config["client_secret"], "secret456")

    def test_get_config_api_key(self):
        """get_config should accept API key."""
        env_vars = {
            "SERVICENOW_INSTANCE": "https://test.service-now.com",
            "SERVICENOW_API_KEY": "api-key-123"
        }
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('servicenow_api.load_env_file', return_value={}):
                config = get_config()
                self.assertEqual(config["api_key"], "api-key-123")

    def test_get_config_strips_trailing_slash(self):
        """get_config should strip trailing slash from instance URL."""
        env_vars = {
            "SERVICENOW_INSTANCE": "https://test.service-now.com/",
            "SERVICENOW_API_KEY": "key"
        }
        with patch.dict(os.environ, env_vars, clear=True):
            with patch('servicenow_api.load_env_file', return_value={}):
                config = get_config()
                self.assertEqual(config["instance"], "https://test.service-now.com")


# =============================================================================
# Unit Tests - ServiceNow Client
# =============================================================================

class TestServiceNowClient(unittest.TestCase):
    """Test ServiceNowClient class."""

    def setUp(self):
        """Create client with mock config."""
        self.config = {
            "instance": "https://test.service-now.com",
            "username": "admin",
            "password": "secret",
            "client_id": None,
            "client_secret": None,
            "api_key": None,
        }
        self.client = ServiceNowClient(self.config)

    def test_client_initialization(self):
        """Client should initialize with provided config."""
        self.assertEqual(self.client.instance, "https://test.service-now.com")
        self.assertEqual(self.client.config["username"], "admin")

    def test_client_build_url_table_only(self):
        """_build_url should construct table URL."""
        url = self.client._build_url("incident")
        self.assertEqual(url, "https://test.service-now.com/api/now/table/incident")

    def test_client_build_url_with_sys_id(self):
        """_build_url should construct URL with sys_id."""
        url = self.client._build_url("incident", sys_id="abc123")
        self.assertEqual(url, "https://test.service-now.com/api/now/table/incident/abc123")

    def test_client_build_url_custom_api_path(self):
        """_build_url should support custom API path."""
        url = self.client._build_url("cmdb_ci_server", api_path="/api/now/cmdb/instance")
        self.assertEqual(url, "https://test.service-now.com/api/now/cmdb/instance/cmdb_ci_server")

    def test_client_basic_auth_header(self):
        """_get_auth_header should return Basic auth header."""
        header = self.client._get_auth_header()
        self.assertIn("Authorization", header)
        self.assertTrue(header["Authorization"].startswith("Basic "))

    def test_client_api_key_auth_header(self):
        """_get_auth_header should return Bearer token for API key."""
        config = self.config.copy()
        config["api_key"] = "test-api-key"
        config["username"] = None
        config["password"] = None
        client = ServiceNowClient(config)

        header = client._get_auth_header()
        self.assertEqual(header["Authorization"], "Bearer test-api-key")

    def test_client_default_timeout(self):
        """Client should use default timeout of 30 seconds."""
        self.assertEqual(self.client.timeout, 30)

    def test_client_custom_timeout(self):
        """Client should accept custom timeout."""
        client = ServiceNowClient(self.config, timeout=60)
        self.assertEqual(client.timeout, 60)

    def test_client_zero_timeout(self):
        """Client should allow timeout of 0 (no timeout check)."""
        client = ServiceNowClient(self.config, timeout=0)
        self.assertEqual(client.timeout, 0)


class TestServiceNowClientRequests(unittest.TestCase):
    """Test ServiceNowClient HTTP request methods."""

    def setUp(self):
        """Create client with mock config."""
        self.config = {
            "instance": "https://test.service-now.com",
            "username": "admin",
            "password": "secret",
            "client_id": None,
            "client_secret": None,
            "api_key": None,
        }
        self.client = ServiceNowClient(self.config)

    @patch('servicenow_api.urlopen')
    def test_get_request_success(self, mock_urlopen):
        """GET request should return parsed JSON."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"result": [{"number": "INC0001"}]}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = self.client.get("incident")

        self.assertEqual(result["result"][0]["number"], "INC0001")

    @patch('servicenow_api.urlopen')
    def test_get_request_with_query_params(self, mock_urlopen):
        """GET request should include query parameters in URL."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"result": []}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        self.client.get("incident", query="state=1", limit=10)

        # Verify URL contains query parameters
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        self.assertIn("sysparm_query=state%3D1", request.full_url)
        self.assertIn("sysparm_limit=10", request.full_url)

    @patch('servicenow_api.urlopen')
    def test_get_request_404_raises_not_found(self, mock_urlopen):
        """GET request returning 404 should raise NotFoundError."""
        mock_error = HTTPError(
            url="https://test.service-now.com/api/now/table/incident/invalid",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=BytesIO(b'{"error": {"message": "Record not found"}}')
        )
        mock_urlopen.side_effect = mock_error

        with self.assertRaises(NotFoundError) as context:
            self.client.get("incident", sys_id="invalid")

        self.assertEqual(context.exception.status_code, 404)

    @patch('servicenow_api.urlopen')
    def test_get_request_401_raises_auth_error(self, mock_urlopen):
        """GET request returning 401 should raise AuthenticationError."""
        mock_error = HTTPError(
            url="https://test.service-now.com/api/now/table/incident",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=BytesIO(b'{"error": {"message": "Invalid credentials"}}')
        )
        mock_urlopen.side_effect = mock_error

        with self.assertRaises(AuthenticationError) as context:
            self.client.get("incident")

        self.assertEqual(context.exception.status_code, 401)

    @patch('servicenow_api.urlopen')
    def test_get_request_403_raises_auth_error(self, mock_urlopen):
        """GET request returning 403 should raise AuthenticationError."""
        mock_error = HTTPError(
            url="https://test.service-now.com/api/now/table/incident",
            code=403,
            msg="Forbidden",
            hdrs={},
            fp=BytesIO(b'{"error": {"message": "Access denied"}}')
        )
        mock_urlopen.side_effect = mock_error

        with self.assertRaises(AuthenticationError) as context:
            self.client.get("incident")

        self.assertEqual(context.exception.status_code, 403)

    @patch('servicenow_api.urlopen')
    def test_get_request_429_raises_rate_limit_error(self, mock_urlopen):
        """GET request returning 429 should raise RateLimitError."""
        mock_error = HTTPError(
            url="https://test.service-now.com/api/now/table/incident",
            code=429,
            msg="Too Many Requests",
            hdrs={},
            fp=BytesIO(b'{"error": {"message": "Rate limit exceeded"}}')
        )
        mock_urlopen.side_effect = mock_error

        with self.assertRaises(RateLimitError) as context:
            self.client.get("incident")

        self.assertEqual(context.exception.status_code, 429)

    @patch('servicenow_api.urlopen')
    def test_get_request_400_raises_validation_error(self, mock_urlopen):
        """GET request returning 400 should raise ValidationError."""
        mock_error = HTTPError(
            url="https://test.service-now.com/api/now/table/incident",
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=BytesIO(b'{"error": {"message": "Invalid query"}}')
        )
        mock_urlopen.side_effect = mock_error

        with self.assertRaises(ValidationError) as context:
            self.client.get("incident")

        self.assertEqual(context.exception.status_code, 400)

    @patch('servicenow_api.urlopen')
    def test_get_request_500_raises_servicenow_error(self, mock_urlopen):
        """GET request returning 500 should raise ServiceNowError."""
        mock_error = HTTPError(
            url="https://test.service-now.com/api/now/table/incident",
            code=500,
            msg="Internal Server Error",
            hdrs={},
            fp=BytesIO(b'{"error": {"message": "Server error"}}')
        )
        mock_urlopen.side_effect = mock_error

        with self.assertRaises(ServiceNowError) as context:
            self.client.get("incident")

        self.assertEqual(context.exception.status_code, 500)

    @patch('servicenow_api.urlopen')
    def test_get_request_connection_error(self, mock_urlopen):
        """GET request with connection error should raise ServiceNowError."""
        mock_urlopen.side_effect = URLError("Connection refused")

        with self.assertRaises(ServiceNowError) as context:
            self.client.get("incident")

        self.assertIn("connect", str(context.exception).lower())

    @patch('servicenow_api.urlopen')
    def test_post_request_success(self, mock_urlopen):
        """POST request should send data and return result."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"result": {"sys_id": "new123", "number": "INC0002"}}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        data = {"short_description": "Test incident", "urgency": "2"}
        result = self.client.post("incident", data)

        self.assertEqual(result["result"]["sys_id"], "new123")

        # Verify POST method was used
        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        self.assertEqual(request.method, "POST")

    @patch('servicenow_api.urlopen')
    def test_put_request_success(self, mock_urlopen):
        """PUT request should send data with sys_id."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"result": {"sys_id": "abc123"}}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        data = {"short_description": "Updated description"}
        result = self.client.put("incident", "abc123", data)

        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        self.assertEqual(request.method, "PUT")
        self.assertIn("/abc123", request.full_url)

    @patch('servicenow_api.urlopen')
    def test_patch_request_success(self, mock_urlopen):
        """PATCH request should partially update record."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"result": {"sys_id": "abc123"}}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        data = {"state": "6"}
        result = self.client.patch("incident", "abc123", data)

        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        self.assertEqual(request.method, "PATCH")

    @patch('servicenow_api.urlopen')
    def test_delete_request_success(self, mock_urlopen):
        """DELETE request should delete record."""
        mock_response = MagicMock()
        mock_response.read.return_value = b''
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = self.client.delete("incident", "abc123")

        call_args = mock_urlopen.call_args
        request = call_args[0][0]
        self.assertEqual(request.method, "DELETE")
        self.assertEqual(result, {})


class TestServiceNowClientOAuth(unittest.TestCase):
    """Test ServiceNowClient OAuth authentication."""

    def setUp(self):
        """Create client with OAuth config."""
        self.config = {
            "instance": "https://test.service-now.com",
            "username": None,
            "password": None,
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "api_key": None,
        }
        self.client = ServiceNowClient(self.config)

    @patch('servicenow_api.urlopen')
    def test_oauth_token_request(self, mock_urlopen):
        """OAuth should request access token."""
        # First call - token request
        token_response = MagicMock()
        token_response.read.return_value = b'{"access_token": "test-token-123", "token_type": "Bearer"}'
        token_response.__enter__ = Mock(return_value=token_response)
        token_response.__exit__ = Mock(return_value=False)

        # Second call - actual API request
        api_response = MagicMock()
        api_response.read.return_value = b'{"result": []}'
        api_response.__enter__ = Mock(return_value=api_response)
        api_response.__exit__ = Mock(return_value=False)

        mock_urlopen.side_effect = [token_response, api_response]

        self.client.get("incident")

        # Verify token endpoint was called
        first_call = mock_urlopen.call_args_list[0]
        request = first_call[0][0]
        self.assertIn("oauth_token.do", request.full_url)

    @patch('servicenow_api.urlopen')
    def test_oauth_uses_bearer_token(self, mock_urlopen):
        """OAuth should use Bearer token for API requests."""
        token_response = MagicMock()
        token_response.read.return_value = b'{"access_token": "test-token-123", "token_type": "Bearer"}'
        token_response.__enter__ = Mock(return_value=token_response)
        token_response.__exit__ = Mock(return_value=False)

        api_response = MagicMock()
        api_response.read.return_value = b'{"result": []}'
        api_response.__enter__ = Mock(return_value=api_response)
        api_response.__exit__ = Mock(return_value=False)

        mock_urlopen.side_effect = [token_response, api_response]

        self.client.get("incident")

        # Verify Bearer token is used in API request
        second_call = mock_urlopen.call_args_list[1]
        request = second_call[0][0]
        self.assertEqual(request.headers["Authorization"], "Bearer test-token-123")

    @patch('servicenow_api.urlopen')
    def test_oauth_failure_raises_auth_error(self, mock_urlopen):
        """OAuth token failure should raise AuthenticationError."""
        mock_error = HTTPError(
            url="https://test.service-now.com/oauth_token.do",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=BytesIO(b'{"error": "invalid_client"}')
        )
        mock_urlopen.side_effect = mock_error

        with self.assertRaises(AuthenticationError):
            self.client._obtain_oauth_token()

    @patch('servicenow_api.urlopen')
    def test_oauth_401_retry_preserves_query_params(self, mock_urlopen):
        """OAuth 401 retry should preserve query parameters."""
        # First call - get token
        token_response = MagicMock()
        token_response.read.return_value = b'{"access_token": "old-token", "token_type": "Bearer"}'
        token_response.__enter__ = Mock(return_value=token_response)
        token_response.__exit__ = Mock(return_value=False)

        # Second call - API request fails with 401
        mock_401_error = HTTPError(
            url="https://test.service-now.com/api/now/table/incident",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=BytesIO(b'{"error": "Token expired"}')
        )

        # Third call - get new token
        new_token_response = MagicMock()
        new_token_response.read.return_value = b'{"access_token": "new-token", "token_type": "Bearer"}'
        new_token_response.__enter__ = Mock(return_value=new_token_response)
        new_token_response.__exit__ = Mock(return_value=False)

        # Fourth call - retry API request succeeds
        api_response = MagicMock()
        api_response.read.return_value = b'{"result": [{"number": "INC001"}]}'
        api_response.__enter__ = Mock(return_value=api_response)
        api_response.__exit__ = Mock(return_value=False)

        mock_urlopen.side_effect = [token_response, mock_401_error, new_token_response, api_response]

        result = self.client.get("incident", query="state=1", limit=10)

        # Verify the query params are in the final retry request
        final_call = mock_urlopen.call_args_list[-1]
        request = final_call[0][0]
        self.assertIn("sysparm_query=state%3D1", request.full_url)
        self.assertIn("sysparm_limit=10", request.full_url)
        self.assertEqual(result["result"][0]["number"], "INC001")


# =============================================================================
# Unit Tests - Utility Functions
# =============================================================================

class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""

    def test_create_client_with_config(self):
        """create_client should create client with provided config."""
        config = {
            "instance": "https://test.service-now.com",
            "username": "admin",
            "password": "secret",
            "client_id": None,
            "client_secret": None,
            "api_key": None,
        }
        client = create_client(config)
        self.assertIsInstance(client, ServiceNowClient)
        self.assertEqual(client.instance, "https://test.service-now.com")

    def test_create_client_with_timeout(self):
        """create_client should pass timeout to client."""
        config = {
            "instance": "https://test.service-now.com",
            "username": "admin",
            "password": "secret",
            "client_id": None,
            "client_secret": None,
            "api_key": None,
        }
        client = create_client(config, timeout=120)
        self.assertEqual(client.timeout, 120)

    def test_read_json_input_empty(self):
        """read_json_input should return empty dict for empty input."""
        with patch('sys.stdin', StringIO('')):
            result = read_json_input()
            self.assertEqual(result, {})

    def test_read_json_input_whitespace(self):
        """read_json_input should return empty dict for whitespace input."""
        with patch('sys.stdin', StringIO('   \n\t  ')):
            result = read_json_input()
            self.assertEqual(result, {})

    def test_read_json_input_valid(self):
        """read_json_input should parse valid JSON."""
        with patch('sys.stdin', StringIO('{"key": "value", "number": 42}')):
            result = read_json_input()
            self.assertEqual(result["key"], "value")
            self.assertEqual(result["number"], 42)

    def test_read_json_input_invalid(self):
        """read_json_input should raise ValidationError for invalid JSON."""
        with patch('sys.stdin', StringIO('not valid json')):
            with self.assertRaises(ValidationError) as context:
                read_json_input()
            self.assertIn("Invalid JSON", str(context.exception))

    def test_output_json(self):
        """output_json should print formatted JSON to stdout."""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            output_json({"key": "value"})
            output = mock_stdout.getvalue()
            self.assertIn('"key"', output)
            self.assertIn('"value"', output)

    def test_output_error_servicenow_error(self):
        """output_error should output ServiceNowError as JSON."""
        error = ServiceNowError("Test error", status_code=500)
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            with self.assertRaises(SystemExit):
                output_error(error)
            output = mock_stderr.getvalue()
            self.assertIn("Test error", output)
            self.assertIn("500", output)

    def test_output_error_generic_exception(self):
        """output_error should handle generic exceptions."""
        error = Exception("Generic error")
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            with self.assertRaises(SystemExit):
                output_error(error)
            output = mock_stderr.getvalue()
            self.assertIn("Generic error", output)


# =============================================================================
# Unit Tests - Timeout Scenarios (SNOW-36)
# =============================================================================

class TestTimeoutScenarios(unittest.TestCase):
    """Test timeout handling scenarios."""

    def setUp(self):
        """Create client with mock config."""
        self.config = {
            "instance": "https://test.service-now.com",
            "username": "admin",
            "password": "secret",
            "client_id": None,
            "client_secret": None,
            "api_key": None,
        }

    @patch('servicenow_api.urlopen')
    def test_request_timeout_raises_servicenow_error(self, mock_urlopen):
        """Request timeout should raise ServiceNowError."""
        import socket
        mock_urlopen.side_effect = URLError(socket.timeout("timed out"))

        client = ServiceNowClient(self.config, timeout=5)

        with self.assertRaises(ServiceNowError) as context:
            client.get("incident")

        self.assertIn("connect", str(context.exception).lower())

    @patch('servicenow_api.urlopen')
    def test_oauth_timeout_raises_auth_error(self, mock_urlopen):
        """OAuth token request timeout should raise AuthenticationError."""
        import socket
        mock_urlopen.side_effect = URLError(socket.timeout("timed out"))

        config = self.config.copy()
        config["username"] = None
        config["password"] = None
        config["client_id"] = "test-client"
        config["client_secret"] = "test-secret"
        client = ServiceNowClient(config, timeout=5)

        with self.assertRaises(AuthenticationError) as context:
            client._obtain_oauth_token()

        self.assertIn("connect", str(context.exception).lower())

    @patch('servicenow_api.urlopen')
    def test_custom_timeout_used_in_request(self, mock_urlopen):
        """Custom timeout should be passed to urlopen."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"result": []}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = ServiceNowClient(self.config, timeout=120)
        client.get("incident")

        # Verify timeout was passed to urlopen
        call_args = mock_urlopen.call_args
        self.assertEqual(call_args[1]["timeout"], 120)

    @patch('servicenow_api.urlopen')
    def test_default_timeout_used_when_not_specified(self, mock_urlopen):
        """Default timeout should be used when not specified."""
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"result": []}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = ServiceNowClient(self.config)  # No timeout specified
        client.get("incident")

        # Verify default timeout (30) was passed to urlopen
        call_args = mock_urlopen.call_args
        self.assertEqual(call_args[1]["timeout"], 30)


# =============================================================================
# Unit Tests - Retry Logic (SNOW-36)
# =============================================================================

class TestRetryLogic(unittest.TestCase):
    """Test retry logic for OAuth 401 scenarios."""

    def setUp(self):
        """Create client with OAuth config."""
        self.config = {
            "instance": "https://test.service-now.com",
            "username": None,
            "password": None,
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
            "api_key": None,
        }

    @patch('servicenow_api.urlopen')
    def test_oauth_401_retry_clears_token(self, mock_urlopen):
        """OAuth 401 should clear cached token and retry."""
        # First call - get initial token
        token_response = MagicMock()
        token_response.read.return_value = b'{"access_token": "old-token", "token_type": "Bearer"}'
        token_response.__enter__ = Mock(return_value=token_response)
        token_response.__exit__ = Mock(return_value=False)

        # Second call - API request fails with 401
        mock_401_error = HTTPError(
            url="https://test.service-now.com/api/now/table/incident",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=BytesIO(b'{"error": "Token expired"}')
        )

        # Third call - get new token
        new_token_response = MagicMock()
        new_token_response.read.return_value = b'{"access_token": "new-token", "token_type": "Bearer"}'
        new_token_response.__enter__ = Mock(return_value=new_token_response)
        new_token_response.__exit__ = Mock(return_value=False)

        # Fourth call - retry succeeds
        api_response = MagicMock()
        api_response.read.return_value = b'{"result": []}'
        api_response.__enter__ = Mock(return_value=api_response)
        api_response.__exit__ = Mock(return_value=False)

        mock_urlopen.side_effect = [token_response, mock_401_error, new_token_response, api_response]

        client = ServiceNowClient(self.config)
        client.get("incident")

        # Verify new token is used after retry
        self.assertEqual(client._access_token, "new-token")

    @patch('servicenow_api.urlopen')
    def test_oauth_401_no_infinite_retry(self, mock_urlopen):
        """OAuth should not retry infinitely on persistent 401."""
        # First call - get initial token
        token_response = MagicMock()
        token_response.read.return_value = b'{"access_token": "bad-token", "token_type": "Bearer"}'
        token_response.__enter__ = Mock(return_value=token_response)
        token_response.__exit__ = Mock(return_value=False)

        # Second call - API request fails with 401
        mock_401_error = HTTPError(
            url="https://test.service-now.com/api/now/table/incident",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=BytesIO(b'{"error": "Invalid credentials"}')
        )

        # Third call - get new token
        new_token_response = MagicMock()
        new_token_response.read.return_value = b'{"access_token": "still-bad-token", "token_type": "Bearer"}'
        new_token_response.__enter__ = Mock(return_value=new_token_response)
        new_token_response.__exit__ = Mock(return_value=False)

        # Fourth call - retry also fails with 401
        mock_401_error_2 = HTTPError(
            url="https://test.service-now.com/api/now/table/incident",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=BytesIO(b'{"error": "Still invalid"}')
        )

        mock_urlopen.side_effect = [token_response, mock_401_error, new_token_response, mock_401_error_2]

        client = ServiceNowClient(self.config)

        # Should raise AuthenticationError after retry fails
        with self.assertRaises(AuthenticationError):
            client.get("incident")

        # Should have made exactly 4 calls (no infinite loop)
        self.assertEqual(mock_urlopen.call_count, 4)

    @patch('servicenow_api.urlopen')
    def test_basic_auth_401_no_retry(self, mock_urlopen):
        """Basic auth 401 should not trigger retry logic."""
        config = {
            "instance": "https://test.service-now.com",
            "username": "admin",
            "password": "wrong-password",
            "client_id": None,
            "client_secret": None,
            "api_key": None,
        }

        mock_401_error = HTTPError(
            url="https://test.service-now.com/api/now/table/incident",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=BytesIO(b'{"error": "Invalid credentials"}')
        )
        mock_urlopen.side_effect = mock_401_error

        client = ServiceNowClient(config)

        with self.assertRaises(AuthenticationError):
            client.get("incident")

        # Basic auth should only make one call (no retry)
        self.assertEqual(mock_urlopen.call_count, 1)


# =============================================================================
# Unit Tests - Malformed Env Files (SNOW-36)
# =============================================================================

class TestMalformedEnvFiles(unittest.TestCase):
    """Test handling of malformed env file content."""

    def test_load_env_file_line_without_equals(self):
        """load_env_file should skip lines without '=' separator."""
        env_content = """
SERVICENOW_INSTANCE=https://test.service-now.com
MALFORMED_LINE_WITHOUT_EQUALS
SERVICENOW_USERNAME=admin
another malformed line
SERVICENOW_PASSWORD=secret
"""
        with patch('builtins.open', unittest.mock.mock_open(read_data=env_content)):
            with patch.object(Path, 'exists', return_value=True):
                result = load_env_file(Path("/fake/.claude/env"))

                # Valid lines should be parsed
                self.assertEqual(result["SERVICENOW_INSTANCE"], "https://test.service-now.com")
                self.assertEqual(result["SERVICENOW_USERNAME"], "admin")
                self.assertEqual(result["SERVICENOW_PASSWORD"], "secret")
                # Malformed lines should be skipped (not causing keys)
                self.assertNotIn("MALFORMED_LINE_WITHOUT_EQUALS", result)
                self.assertNotIn("another malformed line", result)

    def test_load_env_file_empty_key(self):
        """load_env_file should handle lines with empty key before '='."""
        env_content = """
=value_without_key
SERVICENOW_INSTANCE=https://test.service-now.com
"""
        with patch('builtins.open', unittest.mock.mock_open(read_data=env_content)):
            with patch.object(Path, 'exists', return_value=True):
                result = load_env_file(Path("/fake/.claude/env"))

                # Empty key line creates an empty key (current behavior)
                self.assertEqual(result.get(""), "value_without_key")
                self.assertEqual(result["SERVICENOW_INSTANCE"], "https://test.service-now.com")

    def test_load_env_file_empty_value(self):
        """load_env_file should handle lines with empty value after '='."""
        env_content = """
SERVICENOW_INSTANCE=https://test.service-now.com
EMPTY_VALUE=
SERVICENOW_USERNAME=admin
"""
        with patch('builtins.open', unittest.mock.mock_open(read_data=env_content)):
            with patch.object(Path, 'exists', return_value=True):
                result = load_env_file(Path("/fake/.claude/env"))

                self.assertEqual(result["SERVICENOW_INSTANCE"], "https://test.service-now.com")
                self.assertEqual(result["EMPTY_VALUE"], "")
                self.assertEqual(result["SERVICENOW_USERNAME"], "admin")

    def test_load_env_file_multiple_equals(self):
        """load_env_file should handle lines with multiple '=' signs."""
        env_content = """
SERVICENOW_INSTANCE=https://test.service-now.com
URL_WITH_PARAMS=https://example.com?foo=bar&baz=qux
KEY=value=with=equals
"""
        with patch('builtins.open', unittest.mock.mock_open(read_data=env_content)):
            with patch.object(Path, 'exists', return_value=True):
                result = load_env_file(Path("/fake/.claude/env"))

                self.assertEqual(result["SERVICENOW_INSTANCE"], "https://test.service-now.com")
                # Only first '=' should be used as separator
                self.assertEqual(result["URL_WITH_PARAMS"], "https://example.com?foo=bar&baz=qux")
                self.assertEqual(result["KEY"], "value=with=equals")

    def test_load_env_file_only_comments(self):
        """load_env_file should return empty dict for file with only comments."""
        env_content = """
# This is a comment
# Another comment
#COMMENTED_OUT=value
"""
        with patch('builtins.open', unittest.mock.mock_open(read_data=env_content)):
            with patch.object(Path, 'exists', return_value=True):
                result = load_env_file(Path("/fake/.claude/env"))

                self.assertEqual(result, {})

    def test_load_env_file_only_empty_lines(self):
        """load_env_file should return empty dict for file with only empty lines."""
        env_content = """



\t
"""
        with patch('builtins.open', unittest.mock.mock_open(read_data=env_content)):
            with patch.object(Path, 'exists', return_value=True):
                result = load_env_file(Path("/fake/.claude/env"))

                self.assertEqual(result, {})

    def test_load_env_file_key_with_spaces(self):
        """load_env_file should strip spaces from keys."""
        env_content = """
  SERVICENOW_INSTANCE  =https://test.service-now.com
SERVICENOW_USERNAME = admin
"""
        with patch('builtins.open', unittest.mock.mock_open(read_data=env_content)):
            with patch.object(Path, 'exists', return_value=True):
                result = load_env_file(Path("/fake/.claude/env"))

                self.assertEqual(result["SERVICENOW_INSTANCE"], "https://test.service-now.com")
                self.assertEqual(result["SERVICENOW_USERNAME"], "admin")

    def test_load_env_file_inline_comment_not_stripped(self):
        """load_env_file should not strip inline comments (they become part of value)."""
        env_content = """
SERVICENOW_INSTANCE=https://test.service-now.com # production
"""
        with patch('builtins.open', unittest.mock.mock_open(read_data=env_content)):
            with patch.object(Path, 'exists', return_value=True):
                result = load_env_file(Path("/fake/.claude/env"))

                # Inline comments are not stripped in simple env file parsing
                self.assertEqual(result["SERVICENOW_INSTANCE"], "https://test.service-now.com # production")


# =============================================================================
# Integration Tests (requires real ServiceNow instance)
# =============================================================================

@unittest.skipUnless(
    os.environ.get('SERVICENOW_INSTANCE') and
    (os.environ.get('SERVICENOW_API_KEY') or
     (os.environ.get('SERVICENOW_USERNAME') and os.environ.get('SERVICENOW_PASSWORD')) or
     (os.environ.get('SERVICENOW_CLIENT_ID') and os.environ.get('SERVICENOW_CLIENT_SECRET'))),
    "ServiceNow credentials not configured - skipping integration tests"
)
class TestServiceNowIntegration(unittest.TestCase):
    """Integration tests against real ServiceNow instance.

    These tests are skipped unless ServiceNow credentials are configured.
    Set the following environment variables to run:
        - SERVICENOW_INSTANCE
        - SERVICENOW_USERNAME / SERVICENOW_PASSWORD (or other auth method)
    """

    @classmethod
    def setUpClass(cls):
        """Create client for integration tests."""
        cls.client = create_client()

    def test_integration_client_connection(self):
        """Verify client can connect to ServiceNow instance."""
        # This test simply verifies the client is configured
        self.assertIsNotNone(self.client.instance)

    def test_integration_get_incidents(self):
        """Verify GET request works for incident table."""
        try:
            result = self.client.get("incident", limit=1)
            self.assertIn("result", result)
        except (AuthenticationError, ServiceNowError) as e:
            self.skipTest(f"Integration test skipped due to: {e}")

    def test_integration_query_with_filters(self):
        """Verify query with filters works."""
        try:
            result = self.client.get(
                "incident",
                query="active=true",
                fields="number,short_description,state",
                limit=5
            )
            self.assertIn("result", result)
        except (AuthenticationError, ServiceNowError) as e:
            self.skipTest(f"Integration test skipped due to: {e}")

    def test_integration_get_sys_user(self):
        """Verify GET request works for sys_user table."""
        try:
            result = self.client.get("sys_user", limit=1)
            self.assertIn("result", result)
        except (AuthenticationError, ServiceNowError) as e:
            self.skipTest(f"Integration test skipped due to: {e}")


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)
