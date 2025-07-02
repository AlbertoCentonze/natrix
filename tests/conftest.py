from pathlib import Path

import pytest

from natrix.context import ProjectContext


@pytest.fixture(scope="session")
def test_project_context():
    """Create a ProjectContext with all test contracts."""
    # Find all .vy and .vyi files in tests/contracts
    contracts_dir = Path("tests/contracts")
    vy_files = list(contracts_dir.rglob("*.vy")) + list(contracts_dir.rglob("*.vyi"))

    # Create context with all test contracts
    return ProjectContext(vy_files)


def run_rule_on_file(rule, filename, test_project_context):
    """Run a rule on a specific file using the test project context."""
    # Construct the full path
    file_path = Path("tests/contracts") / filename

    # Run the rule on the specific file
    return rule.run(test_project_context, file_path.resolve())
