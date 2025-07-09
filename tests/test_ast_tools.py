import os
import re
import subprocess
from pathlib import Path

from natrix.ast_tools import (
    SUPPORTED_VYPER_VERSION_PATTERN,
    _parse_comments,
    parse_file,
    parse_source,
    vyper_compile,
)


def test_vyper_compile_integration():
    result = subprocess.run(["vyper", "--version"], capture_output=True, text=True)
    assert result.returncode == 0, "Vyper compiler not available"

    version_match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
    assert version_match, "Could not determine Vyper version"
    version = version_match.group(1)
    assert SUPPORTED_VYPER_VERSION_PATTERN.match(version), (
        f"Vyper version must be >= 0.4.0, found {version}"
    )

    test_file = "tests/contracts/version_dummy.vy"

    result = vyper_compile(test_file, "annotated_ast")

    assert isinstance(result, dict)
    assert "ast" in result
    assert "ast_type" in result["ast"]
    assert result["ast"]["ast_type"] == "Module"

    result_metadata = vyper_compile(test_file, "metadata")
    assert isinstance(result_metadata, dict)
    assert "function_info" in result_metadata


def test_parse_file_integration():
    test_file = Path("tests/contracts/version_dummy.vy")

    result = parse_file(test_file)

    assert isinstance(result, dict)
    assert "ast" in result
    assert "ast_type" in result["ast"]
    assert result["ast"]["ast_type"] == "Module"
    assert "metadata" in result
    assert isinstance(result["metadata"], dict)


def test_modules_compilation():
    test_file = Path("tests/contracts/scrvusd_oracle/scrvusd_oracle.vy")

    result = vyper_compile(test_file, "annotated_ast")
    assert isinstance(result, dict)
    assert "ast" in result


def test_parse_source():
    # Simple Vyper contract source code
    source_code = """
# A simple counter contract
counter: uint256

@external
def increment():
    self.counter += 1

@external
@view
def get_counter() -> uint256:
    return self.counter
"""

    result = parse_source(source_code)

    # Check the result structure
    assert isinstance(result, dict)
    assert "ast" in result
    assert "ast_type" in result["ast"]
    assert result["ast"]["ast_type"] == "Module"
    assert "metadata" in result
    assert isinstance(result["metadata"], dict)
    assert "function_info" in result["metadata"]

    # Check that we have our two functions
    functions = result["metadata"]["function_info"]
    function_names = [name.split()[0] for name in functions]
    assert "increment" in function_names
    assert "get_counter" in function_names


def test_vyper_version_ci_matrix():
    # Check if we're running in CI
    if not os.environ.get("CI"):
        # Not in CI, skip the check
        return

    # In CI, VYPER_VERSION MUST be set
    expected_version = os.environ.get("VYPER_VERSION")
    assert expected_version, (
        "VYPER_VERSION environment variable MUST be set in CI. "
        'The CI workflow should export it with: echo "VYPER_VERSION=${{ matrix.vyper-version }}" >> $GITHUB_ENV'
    )

    # Get the actual installed Vyper version
    result = subprocess.run(["vyper", "--version"], capture_output=True, text=True)
    assert result.returncode == 0, "Vyper compiler not available"

    version_match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
    assert version_match, "Could not determine Vyper version"
    actual_version = version_match.group(1)

    # Assert that the installed version matches exactly the CI matrix version
    assert actual_version == expected_version, (
        f"Vyper version mismatch in CI: expected {expected_version} from matrix, but got {actual_version}"
    )


def test_comment_parser_all_contracts():
    # Test that the comment parser can parse all contracts without errors
    contracts_dir = Path("tests/contracts")

    # Get all .vy files
    vy_files = list(contracts_dir.rglob("*.vy"))
    assert len(vy_files) > 0

    for vy_file in vy_files:
        # Parse comments should not raise any exceptions
        comments = _parse_comments(vy_file)

        # Comments should be a list (can be empty)
        assert isinstance(comments, list)

        # Each comment should have the required fields
        for comment in comments:
            assert comment["ast_type"] == "Comment"
            assert isinstance(comment["lineno"], int)
            assert isinstance(comment["col_offset"], int)
            assert isinstance(comment["end_lineno"], int)
            assert isinstance(comment["end_col_offset"], int)
            assert isinstance(comment["content"], str)
