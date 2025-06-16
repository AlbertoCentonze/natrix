"""Tests for the codegen command."""

import subprocess
import sys
from pathlib import Path


def test_codegen_exports():
    """Test the codegen exports command."""
    # Use a test contract that has external functions
    test_contract = Path(__file__).parent / "contracts" / "version_dummy.vy"

    # Run the codegen exports command
    result = subprocess.run(
        [sys.executable, "-m", "natrix", "codegen", "exports", str(test_contract)],
        capture_output=True,
        text=True,
    )

    # Check that the command succeeded
    assert result.returncode == 0

    # Check the output
    expected = """# NOTE: Always double-check the generated exports
exports: (
    version_dummy.non_view_external,
    version_dummy.pure_external_marked_as_nothing,
    version_dummy.pure_external_marked_as_view,
    version_dummy.view_external_marked_as_nothing
)"""
    assert result.stdout.strip() == expected
