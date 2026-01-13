#!/usr/bin/env python3
"""
Pytest Fixtures for ServiceNow API Tests

SNOW-36: Migration to pytest fixtures for cleaner setup/teardown.
These fixtures provide reusable test configurations and mock objects.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

# Get the project root directory (parent of tests/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Add scripts directory to path for imports
sys.path.insert(0, str(SCRIPTS_DIR))

from servicenow_api import ServiceNowClient


# =============================================================================
# Configuration Fixtures
# =============================================================================

@pytest.fixture
def basic_auth_config():
    """Configuration with Basic authentication."""
    return {
        "instance": "https://test.service-now.com",
        "username": "admin",
        "password": "secret",
        "client_id": None,
        "client_secret": None,
        "api_key": None,
    }


@pytest.fixture
def oauth_config():
    """Configuration with OAuth authentication."""
    return {
        "instance": "https://test.service-now.com",
        "username": None,
        "password": None,
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "api_key": None,
    }


@pytest.fixture
def api_key_config():
    """Configuration with API key authentication."""
    return {
        "instance": "https://test.service-now.com",
        "username": None,
        "password": None,
        "client_id": None,
        "client_secret": None,
        "api_key": "test-api-key-12345",
    }


# =============================================================================
# Client Fixtures
# =============================================================================

@pytest.fixture
def basic_auth_client(basic_auth_config):
    """ServiceNow client with Basic authentication."""
    return ServiceNowClient(basic_auth_config)


@pytest.fixture
def oauth_client(oauth_config):
    """ServiceNow client with OAuth authentication."""
    return ServiceNowClient(oauth_config)


@pytest.fixture
def api_key_client(api_key_config):
    """ServiceNow client with API key authentication."""
    return ServiceNowClient(api_key_config)


@pytest.fixture
def client_with_custom_timeout(basic_auth_config):
    """ServiceNow client with custom timeout."""
    return ServiceNowClient(basic_auth_config, timeout=120)


# =============================================================================
# Mock Response Fixtures
# =============================================================================

@pytest.fixture
def mock_success_response():
    """Mock successful API response."""
    response = MagicMock()
    response.read.return_value = b'{"result": [{"number": "INC0001", "sys_id": "abc123"}]}'
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    return response


@pytest.fixture
def mock_empty_response():
    """Mock empty API response."""
    response = MagicMock()
    response.read.return_value = b'{"result": []}'
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    return response


@pytest.fixture
def mock_single_record_response():
    """Mock single record API response."""
    response = MagicMock()
    response.read.return_value = b'{"result": {"sys_id": "abc123", "number": "INC0001"}}'
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    return response


@pytest.fixture
def mock_oauth_token_response():
    """Mock OAuth token response."""
    response = MagicMock()
    response.read.return_value = b'{"access_token": "test-token-123", "token_type": "Bearer"}'
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    return response


@pytest.fixture
def mock_delete_response():
    """Mock successful DELETE response (empty body)."""
    response = MagicMock()
    response.read.return_value = b''
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    return response


# =============================================================================
# Environment File Content Fixtures
# =============================================================================

@pytest.fixture
def valid_env_content():
    """Valid env file content with all auth types."""
    return """
# ServiceNow Configuration
SERVICENOW_INSTANCE=https://test.service-now.com
SERVICENOW_USERNAME=admin
SERVICENOW_PASSWORD=secret

# Optional OAuth
SERVICENOW_CLIENT_ID=test-client
SERVICENOW_CLIENT_SECRET=test-secret

# Optional API Key
SERVICENOW_API_KEY="quoted-key"
"""


@pytest.fixture
def malformed_env_content():
    """Env file content with various malformed lines."""
    return """
# Valid lines
SERVICENOW_INSTANCE=https://test.service-now.com
SERVICENOW_USERNAME=admin

# Malformed lines below
MALFORMED_LINE_NO_EQUALS
another bad line

# More valid lines
SERVICENOW_PASSWORD=secret
"""


@pytest.fixture
def empty_env_content():
    """Empty env file content."""
    return """
# Only comments

# No actual values

"""
