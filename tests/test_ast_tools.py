import subprocess
import re

from natrix.ast_tools import VYPER_VERSION, vyper_compile, parse_file


def test_vyper_compile_integration():
    result = subprocess.run(["vyper", "--version"], capture_output=True, text=True)
    assert result.returncode == 0, "Vyper compiler not available"

    version_match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
    assert version_match, "Could not determine Vyper version"
    version = version_match.group(1)
    assert (
        version == VYPER_VERSION
    ), f"Vyper version must be {VYPER_VERSION}, found {version}"

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


def test_paths_are_needed_for_snekmate():
    test_file = "tests/contracts/scrvusd_oracle.vy"

    # Try direct compilation without paths
    direct_command = ["vyper", "-f", "annotated_ast", test_file]
    direct_process = subprocess.Popen(
        direct_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    direct_stdout, direct_stderr = direct_process.communicate()

    # Check if it failed as expected
    assert (
        "ModuleNotFound: snekmate.auth.ownable" in direct_stderr
    ), "Direct compilation without paths should fail with ModuleNotFound"

    # Now try with our vyper_compile function which includes paths
    result = vyper_compile(test_file, "annotated_ast")
    assert isinstance(result, dict)
    assert "ast" in result
