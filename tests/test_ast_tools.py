import os
import re
import subprocess

from natrix.ast_tools import (
    SUPPORTED_VYPER_VERSION_PATTERN,
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
    test_file = "tests/contracts/version_dummy.vy"

    result = parse_file(test_file)

    assert isinstance(result, dict)
    assert "ast" in result
    assert "ast_type" in result["ast"]
    assert result["ast"]["ast_type"] == "Module"
    assert "metadata" in result
    assert isinstance(result["metadata"], dict)


def test_modules_compilation():
    test_file = "tests/contracts/scrvusd_oracle/scrvusd_oracle.vy"

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
