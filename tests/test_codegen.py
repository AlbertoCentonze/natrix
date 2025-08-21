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


def test_codegen_exports_with_module_comments():
    """Test the codegen exports command with module comments enabled."""
    # Use the scrvusd_oracle contract which imports from ownable
    test_contract = (
        Path(__file__).parent / "contracts" / "scrvusd_oracle" / "scrvusd_oracle.vy"
    )

    # Run the codegen exports command with --display-modules flag
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "natrix",
            "codegen",
            "exports",
            str(test_contract),
            "--display-modules",
        ],
        capture_output=True,
        text=True,
    )

    # Check that the command succeeded
    assert result.returncode == 0

    output = result.stdout.strip()

    # Should contain the exports section
    assert "exports: (" in output

    # Should contain functions from ownable module with comments
    assert "owner,  # ownable" in output
    assert "transfer_ownership,  # ownable" in output
    assert "renounce_ownership,  # ownable" in output

    # Should contain functions from main contract without comments
    assert "scrvusd_oracle.price_v0," in output
    assert "scrvusd_oracle.update_price," in output
