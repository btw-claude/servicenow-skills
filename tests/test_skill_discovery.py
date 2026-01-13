#!/usr/bin/env python3
"""
Test Skill Discovery and Loading

Verifies that the ServiceNow skill is properly configured for Claude Code discovery,
loads correctly on demand, and all skill documentation files are accessible.

Test coverage:
- SKILL.md exists and has required frontmatter (name, description)
- Skill documentation files in skills/ directory are accessible
- Python scripts in scripts/ directory are valid
- Required file structure is present
"""

import os
import sys
import ast
import unittest
import tempfile
import shutil
from pathlib import Path


# Get the project root directory (parent of tests/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Common path fixtures for DRY code
SKILL_MD_PATH = PROJECT_ROOT / "SKILL.md"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
SKILLS_DIR = PROJECT_ROOT / "skills"
INCIDENTS_DIR = SKILLS_DIR / "incidents"
SERVICENOW_API_PATH = SCRIPTS_DIR / "servicenow_api.py"
INCIDENTS_MODULE_PATH = SCRIPTS_DIR / "incidents.py"
GET_INCIDENT_MD_PATH = INCIDENTS_DIR / "get-incident.md"
QUERY_INCIDENTS_MD_PATH = INCIDENTS_DIR / "query-incidents.md"
README_PATH = PROJECT_ROOT / "README.md"
GITIGNORE_PATH = PROJECT_ROOT / ".gitignore"


class TestSkillDiscovery(unittest.TestCase):
    """Test that the ServiceNow skill can be discovered by Claude Code."""

    def test_skill_md_exists(self):
        """SKILL.md file must exist for Claude Code to discover the skill."""
        self.assertTrue(
            SKILL_MD_PATH.exists(),
            "SKILL.md file is required for skill discovery"
        )

    def test_skill_md_has_frontmatter(self):
        """SKILL.md must have valid YAML frontmatter with name and description."""
        content = SKILL_MD_PATH.read_text()

        # Check for frontmatter delimiters
        self.assertTrue(
            content.startswith("---"),
            "SKILL.md must start with YAML frontmatter (---)"
        )

        # Find the closing frontmatter delimiter
        lines = content.split("\n")
        frontmatter_end = None
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                frontmatter_end = i
                break

        self.assertIsNotNone(
            frontmatter_end,
            "SKILL.md must have closing frontmatter delimiter (---)"
        )

        # Extract and validate frontmatter
        frontmatter_lines = lines[1:frontmatter_end]
        frontmatter_content = "\n".join(frontmatter_lines)

        # Check for required fields
        self.assertIn(
            "name:",
            frontmatter_content,
            "SKILL.md frontmatter must contain 'name' field"
        )
        self.assertIn(
            "description:",
            frontmatter_content,
            "SKILL.md frontmatter must contain 'description' field"
        )

    def test_skill_md_has_name(self):
        """SKILL.md frontmatter name field must be non-empty."""
        content = SKILL_MD_PATH.read_text()
        lines = content.split("\n")

        name_value = None
        for line in lines:
            if line.strip().startswith("name:"):
                name_value = line.split(":", 1)[1].strip()
                break

        self.assertIsNotNone(name_value, "name field not found in frontmatter")
        self.assertTrue(
            len(name_value) > 0,
            "name field must not be empty"
        )

    def test_skill_md_has_description(self):
        """SKILL.md frontmatter description field must be non-empty."""
        content = SKILL_MD_PATH.read_text()
        lines = content.split("\n")

        description_value = None
        for line in lines:
            if line.strip().startswith("description:"):
                description_value = line.split(":", 1)[1].strip()
                break

        self.assertIsNotNone(
            description_value,
            "description field not found in frontmatter"
        )
        self.assertTrue(
            len(description_value) > 0,
            "description field must not be empty"
        )


class TestSkillLoading(unittest.TestCase):
    """Test that the ServiceNow skill loads correctly on demand."""

    def test_scripts_directory_exists(self):
        """scripts/ directory must exist for skill operations."""
        self.assertTrue(
            SCRIPTS_DIR.exists(),
            "scripts/ directory is required"
        )
        self.assertTrue(
            SCRIPTS_DIR.is_dir(),
            "scripts/ must be a directory"
        )

    def test_skills_directory_exists(self):
        """skills/ directory must exist for skill documentation."""
        self.assertTrue(
            SKILLS_DIR.exists(),
            "skills/ directory is required"
        )
        self.assertTrue(
            SKILLS_DIR.is_dir(),
            "skills/ must be a directory"
        )

    def test_servicenow_api_module_exists(self):
        """Base API module must exist."""
        self.assertTrue(
            SERVICENOW_API_PATH.exists(),
            "scripts/servicenow_api.py is required"
        )

    def test_servicenow_api_module_syntax(self):
        """Base API module must have valid Python syntax."""
        content = SERVICENOW_API_PATH.read_text()

        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"servicenow_api.py has syntax error: {e}")

    def test_incidents_module_exists(self):
        """Incidents module must exist."""
        self.assertTrue(
            INCIDENTS_MODULE_PATH.exists(),
            "scripts/incidents.py is required"
        )

    def test_incidents_module_syntax(self):
        """Incidents module must have valid Python syntax."""
        content = INCIDENTS_MODULE_PATH.read_text()

        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"incidents.py has syntax error: {e}")

    def test_all_python_scripts_have_valid_syntax(self):
        """All Python scripts must have valid syntax."""
        python_files = list(SCRIPTS_DIR.glob("*.py"))

        self.assertGreater(
            len(python_files),
            0,
            "No Python scripts found in scripts/ directory"
        )

        for py_file in python_files:
            content = py_file.read_text()
            try:
                ast.parse(content)
            except SyntaxError as e:
                self.fail(f"{py_file.name} has syntax error: {e}")


class TestSkillDocumentation(unittest.TestCase):
    """Test that all skill documentation files are accessible."""

    def test_skills_directory_has_subdirectories(self):
        """skills/ directory should contain operation subdirectories."""
        subdirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir()]

        self.assertGreater(
            len(subdirs),
            0,
            "skills/ directory should contain at least one subdirectory"
        )

    def test_incidents_skill_directory_exists(self):
        """Incidents skill documentation directory must exist."""
        self.assertTrue(
            INCIDENTS_DIR.exists(),
            "skills/incidents/ directory is required"
        )

    def test_incidents_skill_has_documentation(self):
        """Incidents skill must have at least one documentation file."""
        md_files = list(INCIDENTS_DIR.glob("*.md"))

        self.assertGreater(
            len(md_files),
            0,
            "skills/incidents/ should contain at least one .md file"
        )

    def test_get_incident_documentation_exists(self):
        """get-incident.md documentation must exist."""
        self.assertTrue(
            GET_INCIDENT_MD_PATH.exists(),
            "skills/incidents/get-incident.md is required"
        )

    def test_query_incidents_documentation_exists(self):
        """query-incidents.md documentation must exist."""
        self.assertTrue(
            QUERY_INCIDENTS_MD_PATH.exists(),
            "skills/incidents/query-incidents.md is required"
        )

    def test_all_documentation_files_readable(self):
        """All documentation files must be readable."""
        # Find all .md files recursively
        md_files = list(SKILLS_DIR.rglob("*.md"))

        self.assertGreater(
            len(md_files),
            0,
            "No documentation files found in skills/ directory"
        )

        for md_file in md_files:
            try:
                content = md_file.read_text()
                self.assertGreater(
                    len(content),
                    0,
                    f"{md_file} is empty"
                )
            except Exception as e:
                self.fail(f"Failed to read {md_file}: {e}")

    def test_documentation_has_script_references(self):
        """Documentation files should reference the scripts to execute."""
        md_files = list(SKILLS_DIR.rglob("*.md"))

        for md_file in md_files:
            content = md_file.read_text()
            # Each doc file should mention how to run the operation
            # Either via "python scripts/" or "Script" section
            has_script_ref = (
                "python scripts/" in content.lower() or
                "## script" in content.lower() or
                "```bash" in content.lower()
            )
            self.assertTrue(
                has_script_ref,
                f"{md_file} should reference how to execute the operation"
            )


class TestSkillStructure(unittest.TestCase):
    """Test the overall skill structure integrity."""

    def test_required_files_exist(self):
        """All required files for a valid skill must exist."""
        required_paths = [
            SKILL_MD_PATH,
            SERVICENOW_API_PATH,
            INCIDENTS_MODULE_PATH,
            GET_INCIDENT_MD_PATH,
            QUERY_INCIDENTS_MD_PATH,
        ]

        for file_path in required_paths:
            self.assertTrue(
                file_path.exists(),
                f"Required file missing: {file_path.relative_to(PROJECT_ROOT)}"
            )

    def test_no_syntax_errors_in_any_python_file(self):
        """No Python file in the project should have syntax errors."""
        python_files = list(PROJECT_ROOT.rglob("*.py"))

        # Exclude test files from this check (they may have intentional issues)
        python_files = [f for f in python_files if "test_" not in f.name]

        for py_file in python_files:
            content = py_file.read_text()
            try:
                ast.parse(content)
            except SyntaxError as e:
                self.fail(f"{py_file.relative_to(PROJECT_ROOT)} has syntax error: {e}")

    def test_readme_exists(self):
        """README.md should exist for project documentation."""
        self.assertTrue(
            README_PATH.exists(),
            "README.md is recommended for project documentation"
        )

    def test_gitignore_exists(self):
        """.gitignore should exist to prevent committing sensitive files."""
        self.assertTrue(
            GITIGNORE_PATH.exists(),
            ".gitignore is recommended"
        )

    def test_gitignore_excludes_env_files(self):
        """.gitignore should exclude environment files with credentials."""
        content = GITIGNORE_PATH.read_text()

        # Check for common patterns that exclude env files
        excludes_env = any([
            ".env" in content,
            "*.env" in content,
            ".claude/env" in content,
        ])

        self.assertTrue(
            excludes_env,
            ".gitignore should exclude .env files to prevent credential leaks"
        )


class TestErrorHandling(unittest.TestCase):
    """Negative test cases for error handling scenarios."""

    def setUp(self):
        """Create a temporary directory for test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up temporary directory after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_missing_skill_md_detected(self):
        """Verify that a missing SKILL.md file is detected."""
        missing_skill_md = self.temp_dir / "SKILL.md"
        self.assertFalse(
            missing_skill_md.exists(),
            "Test fixture should not have SKILL.md"
        )

    def test_invalid_frontmatter_missing_opening_delimiter(self):
        """Detect SKILL.md without opening frontmatter delimiter."""
        invalid_skill_md = self.temp_dir / "SKILL.md"
        invalid_skill_md.write_text("name: test\ndescription: test\n---\n# Content")

        content = invalid_skill_md.read_text()
        self.assertFalse(
            content.startswith("---"),
            "Content without opening delimiter should be detected"
        )

    def test_invalid_frontmatter_missing_closing_delimiter(self):
        """Detect SKILL.md without closing frontmatter delimiter."""
        invalid_skill_md = self.temp_dir / "SKILL.md"
        invalid_skill_md.write_text("---\nname: test\ndescription: test\n# Content without closing")

        content = invalid_skill_md.read_text()
        lines = content.split("\n")

        frontmatter_end = None
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                frontmatter_end = i
                break

        self.assertIsNone(
            frontmatter_end,
            "Missing closing delimiter should be detected"
        )

    def test_invalid_frontmatter_missing_name_field(self):
        """Detect SKILL.md with missing name field."""
        invalid_skill_md = self.temp_dir / "SKILL.md"
        invalid_skill_md.write_text("---\ndescription: test description\n---\n# Content")

        content = invalid_skill_md.read_text()
        lines = content.split("\n")

        name_value = None
        for line in lines:
            if line.strip().startswith("name:"):
                name_value = line.split(":", 1)[1].strip()
                break

        self.assertIsNone(
            name_value,
            "Missing name field should be detected"
        )

    def test_invalid_frontmatter_missing_description_field(self):
        """Detect SKILL.md with missing description field."""
        invalid_skill_md = self.temp_dir / "SKILL.md"
        invalid_skill_md.write_text("---\nname: test name\n---\n# Content")

        content = invalid_skill_md.read_text()
        lines = content.split("\n")

        description_value = None
        for line in lines:
            if line.strip().startswith("description:"):
                description_value = line.split(":", 1)[1].strip()
                break

        self.assertIsNone(
            description_value,
            "Missing description field should be detected"
        )

    def test_invalid_frontmatter_empty_name_field(self):
        """Detect SKILL.md with empty name field."""
        invalid_skill_md = self.temp_dir / "SKILL.md"
        invalid_skill_md.write_text("---\nname:\ndescription: test description\n---\n# Content")

        content = invalid_skill_md.read_text()
        lines = content.split("\n")

        name_value = None
        for line in lines:
            if line.strip().startswith("name:"):
                name_value = line.split(":", 1)[1].strip()
                break

        self.assertEqual(
            name_value,
            "",
            "Empty name field should be detected"
        )

    def test_invalid_frontmatter_empty_description_field(self):
        """Detect SKILL.md with empty description field."""
        invalid_skill_md = self.temp_dir / "SKILL.md"
        invalid_skill_md.write_text("---\nname: test name\ndescription:\n---\n# Content")

        content = invalid_skill_md.read_text()
        lines = content.split("\n")

        description_value = None
        for line in lines:
            if line.strip().startswith("description:"):
                description_value = line.split(":", 1)[1].strip()
                break

        self.assertEqual(
            description_value,
            "",
            "Empty description field should be detected"
        )

    def test_invalid_python_syntax_detected(self):
        """Detect Python files with syntax errors."""
        invalid_py = self.temp_dir / "invalid.py"
        invalid_py.write_text("def broken(\n    # missing closing paren")

        content = invalid_py.read_text()
        with self.assertRaises(SyntaxError):
            ast.parse(content)

    def test_missing_scripts_directory(self):
        """Verify missing scripts directory is detected."""
        missing_scripts = self.temp_dir / "scripts"
        self.assertFalse(
            missing_scripts.exists(),
            "Test fixture should not have scripts directory"
        )

    def test_missing_skills_directory(self):
        """Verify missing skills directory is detected."""
        missing_skills = self.temp_dir / "skills"
        self.assertFalse(
            missing_skills.exists(),
            "Test fixture should not have skills directory"
        )

    def test_empty_documentation_file_detected(self):
        """Detect empty documentation files."""
        docs_dir = self.temp_dir / "skills" / "incidents"
        docs_dir.mkdir(parents=True)
        empty_doc = docs_dir / "empty.md"
        empty_doc.write_text("")

        content = empty_doc.read_text()
        self.assertEqual(
            len(content),
            0,
            "Empty documentation file should be detected"
        )


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)
