#!/usr/bin/env python3
"""
Test Domain Scripts Verification

Verifies all domain scripts (incidents, changes, problems, catalog, cmdb)
with all actions for correct JSON input/output and error handling.

SNOW-17: Verify All Domain Scripts
- Test each domain script with all supported actions
- Verify correct JSON input/output structure
- Test error handling for missing/invalid parameters
- Verify ValidationError is raised for invalid actions
"""

import os
import sys
import ast
import json
import unittest
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock

# Get the project root directory (parent of tests/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Add scripts directory to path for imports
sys.path.insert(0, str(SCRIPTS_DIR))


class TestIncidentsScript(unittest.TestCase):
    """Test incidents.py domain script with all actions."""

    @classmethod
    def setUpClass(cls):
        """Import the incidents module for testing."""
        from incidents import dispatch_action, ValidationError
        cls.dispatch_action = staticmethod(dispatch_action)
        cls.ValidationError = ValidationError

    def test_incidents_module_has_valid_syntax(self):
        """incidents.py must have valid Python syntax."""
        incidents_file = SCRIPTS_DIR / "incidents.py"
        content = incidents_file.read_text()
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"incidents.py has syntax error: {e}")

    def test_incidents_has_dispatch_action(self):
        """incidents.py must have dispatch_action function."""
        import incidents
        self.assertTrue(
            hasattr(incidents, 'dispatch_action'),
            "incidents.py must have dispatch_action function"
        )

    def test_incidents_missing_action_raises_error(self):
        """incidents.py must raise ValidationError when action is missing."""
        with self.assertRaises(self.ValidationError) as context:
            self.dispatch_action({})
        self.assertIn("action is required", str(context.exception))

    def test_incidents_invalid_action_raises_error(self):
        """incidents.py must raise ValidationError for invalid action."""
        with patch('incidents.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "invalid_action"})
            self.assertIn("Invalid action", str(context.exception))
            self.assertIn("get, get_by_number, query", str(context.exception))

    def test_incidents_get_action_requires_sys_id(self):
        """incidents.py get action must require sys_id parameter."""
        with patch('incidents.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "get"})
            self.assertIn("sys_id is required", str(context.exception))

    def test_incidents_get_by_number_action_requires_number(self):
        """incidents.py get_by_number action must require number parameter."""
        with patch('incidents.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "get_by_number"})
            self.assertIn("number is required", str(context.exception))

    def test_incidents_query_action_accepts_filters(self):
        """incidents.py query action should accept filter parameters."""
        with patch('incidents.create_client') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get.return_value = {"result": []}
            mock_client.return_value = mock_instance

            # Query should work without raising error
            result = self.dispatch_action({
                "action": "query",
                "state": "1",
                "urgency": "2",
                "impact": "3",
                "active": True,
                "limit": 10
            })

            self.assertIsInstance(result, list)

    def test_incidents_supports_documented_actions(self):
        """incidents.py must support all documented actions."""
        import incidents
        docstring = incidents.__doc__

        # Verify documented actions are mentioned
        self.assertIn("get", docstring)
        self.assertIn("get_by_number", docstring)
        self.assertIn("query", docstring)


class TestChangesScript(unittest.TestCase):
    """Test changes.py domain script with all actions."""

    @classmethod
    def setUpClass(cls):
        """Import the changes module for testing."""
        from changes import dispatch_action, ValidationError
        cls.dispatch_action = staticmethod(dispatch_action)
        cls.ValidationError = ValidationError

    def test_changes_module_has_valid_syntax(self):
        """changes.py must have valid Python syntax."""
        changes_file = SCRIPTS_DIR / "changes.py"
        content = changes_file.read_text()
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"changes.py has syntax error: {e}")

    def test_changes_has_dispatch_action(self):
        """changes.py must have dispatch_action function."""
        import changes
        self.assertTrue(
            hasattr(changes, 'dispatch_action'),
            "changes.py must have dispatch_action function"
        )

    def test_changes_missing_action_raises_error(self):
        """changes.py must raise ValidationError when action is missing."""
        with self.assertRaises(self.ValidationError) as context:
            self.dispatch_action({})
        self.assertIn("action is required", str(context.exception))

    def test_changes_invalid_action_raises_error(self):
        """changes.py must raise ValidationError for invalid action."""
        with patch('changes.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "invalid_action"})
            self.assertIn("Invalid action", str(context.exception))
            self.assertIn("get, get_by_number, query", str(context.exception))

    def test_changes_get_action_requires_sys_id(self):
        """changes.py get action must require sys_id parameter."""
        with patch('changes.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "get"})
            self.assertIn("sys_id is required", str(context.exception))

    def test_changes_get_by_number_action_requires_number(self):
        """changes.py get_by_number action must require number parameter."""
        with patch('changes.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "get_by_number"})
            self.assertIn("number is required", str(context.exception))

    def test_changes_query_action_accepts_filters(self):
        """changes.py query action should accept filter parameters."""
        with patch('changes.create_client') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get.return_value = {"result": []}
            mock_client.return_value = mock_instance

            result = self.dispatch_action({
                "action": "query",
                "state": "-5",
                "type": "normal",
                "risk": "2",
                "active": True,
                "limit": 10
            })

            self.assertIsInstance(result, list)

    def test_changes_supports_documented_actions(self):
        """changes.py must support all documented actions."""
        import changes
        docstring = changes.__doc__

        self.assertIn("get", docstring)
        self.assertIn("get_by_number", docstring)
        self.assertIn("query", docstring)


class TestProblemsScript(unittest.TestCase):
    """Test problems.py domain script with all actions."""

    @classmethod
    def setUpClass(cls):
        """Import the problems module for testing."""
        from problems import dispatch_action, ValidationError
        cls.dispatch_action = staticmethod(dispatch_action)
        cls.ValidationError = ValidationError

    def test_problems_module_has_valid_syntax(self):
        """problems.py must have valid Python syntax."""
        problems_file = SCRIPTS_DIR / "problems.py"
        content = problems_file.read_text()
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"problems.py has syntax error: {e}")

    def test_problems_has_dispatch_action(self):
        """problems.py must have dispatch_action function."""
        import problems
        self.assertTrue(
            hasattr(problems, 'dispatch_action'),
            "problems.py must have dispatch_action function"
        )

    def test_problems_missing_action_raises_error(self):
        """problems.py must raise ValidationError when action is missing."""
        with self.assertRaises(self.ValidationError) as context:
            self.dispatch_action({})
        self.assertIn("action is required", str(context.exception))

    def test_problems_invalid_action_raises_error(self):
        """problems.py must raise ValidationError for invalid action."""
        with patch('problems.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "invalid_action"})
            self.assertIn("Invalid action", str(context.exception))
            self.assertIn("get, get_by_number, query", str(context.exception))

    def test_problems_get_action_requires_sys_id(self):
        """problems.py get action must require sys_id parameter."""
        with patch('problems.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "get"})
            self.assertIn("sys_id is required", str(context.exception))

    def test_problems_get_by_number_action_requires_number(self):
        """problems.py get_by_number action must require number parameter."""
        with patch('problems.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "get_by_number"})
            self.assertIn("number is required", str(context.exception))

    def test_problems_query_action_accepts_filters(self):
        """problems.py query action should accept filter parameters."""
        with patch('problems.create_client') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get.return_value = {"result": []}
            mock_client.return_value = mock_instance

            result = self.dispatch_action({
                "action": "query",
                "state": "1",
                "priority": "2",
                "known_error": True,
                "active": True,
                "limit": 10
            })

            self.assertIsInstance(result, list)

    def test_problems_supports_documented_actions(self):
        """problems.py must support all documented actions."""
        import problems
        docstring = problems.__doc__

        self.assertIn("get", docstring)
        self.assertIn("get_by_number", docstring)
        self.assertIn("query", docstring)


class TestCatalogScript(unittest.TestCase):
    """Test catalog.py domain script with all actions."""

    @classmethod
    def setUpClass(cls):
        """Import the catalog module for testing."""
        from catalog import dispatch_action, ValidationError
        cls.dispatch_action = staticmethod(dispatch_action)
        cls.ValidationError = ValidationError

    def test_catalog_module_has_valid_syntax(self):
        """catalog.py must have valid Python syntax."""
        catalog_file = SCRIPTS_DIR / "catalog.py"
        content = catalog_file.read_text()
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"catalog.py has syntax error: {e}")

    def test_catalog_has_dispatch_action(self):
        """catalog.py must have dispatch_action function."""
        import catalog
        self.assertTrue(
            hasattr(catalog, 'dispatch_action'),
            "catalog.py must have dispatch_action function"
        )

    def test_catalog_missing_action_raises_error(self):
        """catalog.py must raise ValidationError when action is missing."""
        with self.assertRaises(self.ValidationError) as context:
            self.dispatch_action({})
        self.assertIn("action is required", str(context.exception))

    def test_catalog_invalid_action_raises_error(self):
        """catalog.py must raise ValidationError for invalid action."""
        with patch('catalog.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "invalid_action"})
            self.assertIn("Invalid action", str(context.exception))
            self.assertIn("categories", str(context.exception))
            self.assertIn("items", str(context.exception))
            self.assertIn("search", str(context.exception))
            self.assertIn("status", str(context.exception))
            self.assertIn("query_requests", str(context.exception))

    def test_catalog_categories_action(self):
        """catalog.py categories action should work."""
        with patch('catalog.create_client') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get.return_value = {"result": []}
            mock_client.return_value = mock_instance

            result = self.dispatch_action({
                "action": "categories",
                "active": True,
                "limit": 10
            })

            self.assertIsInstance(result, list)

    def test_catalog_items_action(self):
        """catalog.py items action should work."""
        with patch('catalog.create_client') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get.return_value = {"result": []}
            mock_client.return_value = mock_instance

            result = self.dispatch_action({
                "action": "items",
                "category": "test-category-id",
                "active": True
            })

            self.assertIsInstance(result, list)

    def test_catalog_search_action_requires_search_term(self):
        """catalog.py search action must require search_term parameter."""
        with patch('catalog.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "search", "search_term": ""})
            self.assertIn("search_term is required", str(context.exception))

    def test_catalog_status_action_requires_identifier(self):
        """catalog.py status action must require request_number or request_sys_id."""
        with patch('catalog.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "status"})
            self.assertIn("request_number or request_sys_id is required", str(context.exception))

    def test_catalog_query_requests_action(self):
        """catalog.py query_requests action should work."""
        with patch('catalog.create_client') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get.return_value = {"result": []}
            mock_client.return_value = mock_instance

            result = self.dispatch_action({
                "action": "query_requests",
                "request_state": "approved",
                "active": True,
                "limit": 10
            })

            self.assertIsInstance(result, list)

    def test_catalog_supports_documented_actions(self):
        """catalog.py must support all documented actions."""
        import catalog
        docstring = catalog.__doc__

        self.assertIn("categories", docstring)
        self.assertIn("items", docstring)
        self.assertIn("search", docstring)
        self.assertIn("status", docstring)
        self.assertIn("query_requests", docstring)


class TestCmdbScript(unittest.TestCase):
    """Test cmdb.py domain script with all actions."""

    @classmethod
    def setUpClass(cls):
        """Import the cmdb module for testing."""
        from cmdb import dispatch_action, ValidationError
        cls.dispatch_action = staticmethod(dispatch_action)
        cls.ValidationError = ValidationError

    def test_cmdb_module_has_valid_syntax(self):
        """cmdb.py must have valid Python syntax."""
        cmdb_file = SCRIPTS_DIR / "cmdb.py"
        content = cmdb_file.read_text()
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"cmdb.py has syntax error: {e}")

    def test_cmdb_has_dispatch_action(self):
        """cmdb.py must have dispatch_action function."""
        import cmdb
        self.assertTrue(
            hasattr(cmdb, 'dispatch_action'),
            "cmdb.py must have dispatch_action function"
        )

    def test_cmdb_missing_action_raises_error(self):
        """cmdb.py must raise ValidationError when action is missing."""
        with self.assertRaises(self.ValidationError) as context:
            self.dispatch_action({})
        self.assertIn("action is required", str(context.exception))

    def test_cmdb_invalid_action_raises_error(self):
        """cmdb.py must raise ValidationError for invalid action."""
        with patch('cmdb.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "invalid_action"})
            self.assertIn("Invalid action", str(context.exception))
            self.assertIn("get", str(context.exception))
            self.assertIn("query", str(context.exception))
            self.assertIn("search", str(context.exception))
            self.assertIn("relationships", str(context.exception))
            self.assertIn("by_ip", str(context.exception))
            self.assertIn("by_serial", str(context.exception))

    def test_cmdb_get_action_requires_sys_id(self):
        """cmdb.py get action must require sys_id parameter."""
        with patch('cmdb.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "get"})
            self.assertIn("sys_id is required", str(context.exception))

    def test_cmdb_query_action(self):
        """cmdb.py query action should work."""
        with patch('cmdb.create_client') as mock_client:
            mock_instance = MagicMock()
            mock_instance.get.return_value = {"result": []}
            mock_client.return_value = mock_instance

            result = self.dispatch_action({
                "action": "query",
                "ci_class": "cmdb_ci_server",
                "operational_status": "1",
                "limit": 10
            })

            self.assertIsInstance(result, list)

    def test_cmdb_search_action_requires_search_term(self):
        """cmdb.py search action must require search_term parameter."""
        with patch('cmdb.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "search"})
            self.assertIn("search_term is required", str(context.exception))

    def test_cmdb_relationships_action_requires_sys_id(self):
        """cmdb.py relationships action must require sys_id parameter."""
        with patch('cmdb.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "relationships"})
            self.assertIn("sys_id is required", str(context.exception))

    def test_cmdb_by_ip_action_requires_ip_address(self):
        """cmdb.py by_ip action must require ip_address parameter."""
        with patch('cmdb.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "by_ip"})
            self.assertIn("ip_address is required", str(context.exception))

    def test_cmdb_by_serial_action_requires_serial_number(self):
        """cmdb.py by_serial action must require serial_number parameter."""
        with patch('cmdb.create_client') as mock_client:
            mock_client.return_value = MagicMock()
            with self.assertRaises(self.ValidationError) as context:
                self.dispatch_action({"action": "by_serial"})
            self.assertIn("serial_number is required", str(context.exception))

    def test_cmdb_supports_documented_actions(self):
        """cmdb.py must support all documented actions."""
        import cmdb
        docstring = cmdb.__doc__

        self.assertIn("get", docstring)
        self.assertIn("query", docstring)
        self.assertIn("search", docstring)
        self.assertIn("relationships", docstring)
        self.assertIn("by_ip", docstring)
        self.assertIn("by_serial", docstring)


class TestServiceNowApiModule(unittest.TestCase):
    """Test servicenow_api.py base module."""

    def test_api_module_has_valid_syntax(self):
        """servicenow_api.py must have valid Python syntax."""
        api_file = SCRIPTS_DIR / "servicenow_api.py"
        content = api_file.read_text()
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"servicenow_api.py has syntax error: {e}")

    def test_api_module_exports_required_classes(self):
        """servicenow_api.py must export required classes and functions."""
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
        )

        # Verify classes are defined
        self.assertTrue(callable(ServiceNowClient))
        self.assertTrue(issubclass(ValidationError, ServiceNowError))
        self.assertTrue(issubclass(AuthenticationError, ServiceNowError))
        self.assertTrue(issubclass(NotFoundError, ServiceNowError))
        self.assertTrue(issubclass(ConfigurationError, ServiceNowError))
        self.assertTrue(issubclass(RateLimitError, ServiceNowError))

    def test_validation_error_has_to_dict(self):
        """ServiceNowError must have to_dict method for JSON serialization."""
        from servicenow_api import ServiceNowError

        error = ServiceNowError("Test error", status_code=400, response_body='{"detail": "test"}')
        error_dict = error.to_dict()

        self.assertIn("error", error_dict)
        self.assertEqual(error_dict["error"], "Test error")
        self.assertEqual(error_dict["status_code"], 400)

    def test_read_json_input_handles_empty_input(self):
        """read_json_input should handle empty input."""
        from servicenow_api import read_json_input

        with patch('sys.stdin', StringIO('')):
            result = read_json_input()
            self.assertEqual(result, {})

    def test_read_json_input_handles_valid_json(self):
        """read_json_input should parse valid JSON."""
        from servicenow_api import read_json_input

        test_input = '{"action": "test", "param": "value"}'
        with patch('sys.stdin', StringIO(test_input)):
            result = read_json_input()
            self.assertEqual(result["action"], "test")
            self.assertEqual(result["param"], "value")

    def test_read_json_input_raises_on_invalid_json(self):
        """read_json_input should raise ValidationError on invalid JSON."""
        from servicenow_api import read_json_input, ValidationError

        with patch('sys.stdin', StringIO('invalid json {')):
            with self.assertRaises(ValidationError) as context:
                read_json_input()
            self.assertIn("Invalid JSON input", str(context.exception))


class TestDomainScriptsIntegration(unittest.TestCase):
    """Integration tests for domain scripts structure."""

    def test_all_domain_scripts_exist(self):
        """All expected domain scripts must exist."""
        expected_scripts = [
            "incidents.py",
            "changes.py",
            "problems.py",
            "catalog.py",
            "cmdb.py",
            "servicenow_api.py",
        ]

        for script_name in expected_scripts:
            script_path = SCRIPTS_DIR / script_name
            self.assertTrue(
                script_path.exists(),
                f"Expected script {script_name} not found in scripts/"
            )

    def test_all_domain_scripts_have_main_function(self):
        """All domain scripts must have a main() function."""
        domain_scripts = [
            "incidents",
            "changes",
            "problems",
            "catalog",
            "cmdb",
        ]

        for script_name in domain_scripts:
            module = __import__(script_name)
            self.assertTrue(
                hasattr(module, 'main'),
                f"{script_name}.py must have main() function"
            )
            self.assertTrue(
                callable(module.main),
                f"{script_name}.main must be callable"
            )

    def test_all_domain_scripts_have_dispatch_action(self):
        """All domain scripts must have a dispatch_action() function."""
        domain_scripts = [
            "incidents",
            "changes",
            "problems",
            "catalog",
            "cmdb",
        ]

        for script_name in domain_scripts:
            module = __import__(script_name)
            self.assertTrue(
                hasattr(module, 'dispatch_action'),
                f"{script_name}.py must have dispatch_action() function"
            )
            self.assertTrue(
                callable(module.dispatch_action),
                f"{script_name}.dispatch_action must be callable"
            )

    def test_all_domain_scripts_import_from_servicenow_api(self):
        """All domain scripts must import from servicenow_api module."""
        domain_scripts = [
            "incidents.py",
            "changes.py",
            "problems.py",
            "catalog.py",
            "cmdb.py",
        ]

        for script_name in domain_scripts:
            script_path = SCRIPTS_DIR / script_name
            content = script_path.read_text()

            self.assertIn(
                "from servicenow_api import",
                content,
                f"{script_name} must import from servicenow_api module"
            )

    def test_all_domain_scripts_have_table_constant(self):
        """All domain scripts should define TABLE_NAME or similar constant."""
        domain_scripts = [
            "incidents.py",
            "changes.py",
            "problems.py",
            "cmdb.py",
        ]

        for script_name in domain_scripts:
            script_path = SCRIPTS_DIR / script_name
            content = script_path.read_text()

            self.assertIn(
                "TABLE_",
                content,
                f"{script_name} should define TABLE_NAME or similar constant"
            )


class TestErrorHandling(unittest.TestCase):
    """Test error handling across all domain scripts."""

    def test_validation_error_message_includes_valid_actions(self):
        """ValidationError for invalid action should list valid actions."""
        domain_modules = [
            ("incidents", ["get", "get_by_number", "query"]),
            ("changes", ["get", "get_by_number", "query"]),
            ("problems", ["get", "get_by_number", "query"]),
            ("catalog", ["categories", "items", "search", "status", "query_requests"]),
            ("cmdb", ["get", "query", "search", "relationships", "by_ip", "by_serial"]),
        ]

        from servicenow_api import ValidationError

        for module_name, expected_actions in domain_modules:
            module = __import__(module_name)

            with patch(f'{module_name}.create_client') as mock_client:
                mock_client.return_value = MagicMock()
                try:
                    module.dispatch_action({"action": "nonexistent"})
                    self.fail(f"{module_name} should raise ValidationError for invalid action")
                except ValidationError as e:
                    error_message = str(e)
                    for action in expected_actions:
                        self.assertIn(
                            action,
                            error_message,
                            f"{module_name} error message should mention '{action}' as valid action"
                        )


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)
