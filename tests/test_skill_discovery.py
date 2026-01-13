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
import json
import unittest
from pathlib import Path


# Get the project root directory (parent of tests/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()


class TestSkillDiscovery(unittest.TestCase):
    """Test that the ServiceNow skill can be discovered by Claude Code."""

    def test_skill_md_exists(self):
        """SKILL.md file must exist for Claude Code to discover the skill."""
        skill_md = PROJECT_ROOT / "SKILL.md"
        self.assertTrue(
            skill_md.exists(),
            "SKILL.md file is required for skill discovery"
        )

    def test_skill_md_has_frontmatter(self):
        """SKILL.md must have valid YAML frontmatter with name and description."""
        skill_md = PROJECT_ROOT / "SKILL.md"
        content = skill_md.read_text()

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
        skill_md = PROJECT_ROOT / "SKILL.md"
        content = skill_md.read_text()
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
        skill_md = PROJECT_ROOT / "SKILL.md"
        content = skill_md.read_text()
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
        scripts_dir = PROJECT_ROOT / "scripts"
        self.assertTrue(
            scripts_dir.exists(),
            "scripts/ directory is required"
        )
        self.assertTrue(
            scripts_dir.is_dir(),
            "scripts/ must be a directory"
        )

    def test_skills_directory_exists(self):
        """skills/ directory must exist for skill documentation."""
        skills_dir = PROJECT_ROOT / "skills"
        self.assertTrue(
            skills_dir.exists(),
            "skills/ directory is required"
        )
        self.assertTrue(
            skills_dir.is_dir(),
            "skills/ must be a directory"
        )

    def test_servicenow_api_module_exists(self):
        """Base API module must exist."""
        api_module = PROJECT_ROOT / "scripts" / "servicenow_api.py"
        self.assertTrue(
            api_module.exists(),
            "scripts/servicenow_api.py is required"
        )

    def test_servicenow_api_module_syntax(self):
        """Base API module must have valid Python syntax."""
        api_module = PROJECT_ROOT / "scripts" / "servicenow_api.py"
        content = api_module.read_text()

        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"servicenow_api.py has syntax error: {e}")

    def test_incidents_module_exists(self):
        """Incidents module must exist."""
        incidents_module = PROJECT_ROOT / "scripts" / "incidents.py"
        self.assertTrue(
            incidents_module.exists(),
            "scripts/incidents.py is required"
        )

    def test_incidents_module_syntax(self):
        """Incidents module must have valid Python syntax."""
        incidents_module = PROJECT_ROOT / "scripts" / "incidents.py"
        content = incidents_module.read_text()

        try:
            ast.parse(content)
        except SyntaxError as e:
            self.fail(f"incidents.py has syntax error: {e}")

    def test_all_python_scripts_have_valid_syntax(self):
        """All Python scripts must have valid syntax."""
        scripts_dir = PROJECT_ROOT / "scripts"
        python_files = list(scripts_dir.glob("*.py"))

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
        skills_dir = PROJECT_ROOT / "skills"
        subdirs = [d for d in skills_dir.iterdir() if d.is_dir()]

        self.assertGreater(
            len(subdirs),
            0,
            "skills/ directory should contain at least one subdirectory"
        )

    def test_incidents_skill_directory_exists(self):
        """Incidents skill documentation directory must exist."""
        incidents_dir = PROJECT_ROOT / "skills" / "incidents"
        self.assertTrue(
            incidents_dir.exists(),
            "skills/incidents/ directory is required"
        )

    def test_incidents_skill_has_documentation(self):
        """Incidents skill must have at least one documentation file."""
        incidents_dir = PROJECT_ROOT / "skills" / "incidents"
        md_files = list(incidents_dir.glob("*.md"))

        self.assertGreater(
            len(md_files),
            0,
            "skills/incidents/ should contain at least one .md file"
        )

    def test_get_incident_documentation_exists(self):
        """get-incident.md documentation must exist."""
        get_incident_md = PROJECT_ROOT / "skills" / "incidents" / "get-incident.md"
        self.assertTrue(
            get_incident_md.exists(),
            "skills/incidents/get-incident.md is required"
        )

    def test_query_incidents_documentation_exists(self):
        """query-incidents.md documentation must exist."""
        query_incidents_md = PROJECT_ROOT / "skills" / "incidents" / "query-incidents.md"
        self.assertTrue(
            query_incidents_md.exists(),
            "skills/incidents/query-incidents.md is required"
        )

    def test_all_documentation_files_readable(self):
        """All documentation files must be readable."""
        skills_dir = PROJECT_ROOT / "skills"

        # Find all .md files recursively
        md_files = list(skills_dir.rglob("*.md"))

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
        skills_dir = PROJECT_ROOT / "skills"
        md_files = list(skills_dir.rglob("*.md"))

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
        required_files = [
            "SKILL.md",
            "scripts/servicenow_api.py",
            "scripts/incidents.py",
            "skills/incidents/get-incident.md",
            "skills/incidents/query-incidents.md",
        ]

        for file_path in required_files:
            full_path = PROJECT_ROOT / file_path
            self.assertTrue(
                full_path.exists(),
                f"Required file missing: {file_path}"
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
        readme = PROJECT_ROOT / "README.md"
        self.assertTrue(
            readme.exists(),
            "README.md is recommended for project documentation"
        )

    def test_gitignore_exists(self):
        """.gitignore should exist to prevent committing sensitive files."""
        gitignore = PROJECT_ROOT / ".gitignore"
        self.assertTrue(
            gitignore.exists(),
            ".gitignore is recommended"
        )

    def test_gitignore_excludes_env_files(self):
        """.gitignore should exclude environment files with credentials."""
        gitignore = PROJECT_ROOT / ".gitignore"
        content = gitignore.read_text()

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


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)
