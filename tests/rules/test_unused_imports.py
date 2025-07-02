from pathlib import Path

from natrix.context import ProjectContext
from natrix.rules.unused_imports import UnusedImportsRule
from tests.conftest import run_rule_on_file


def test_unused_imports(test_project_context):
    """Test detection of unused imports."""
    rule = UnusedImportsRule()

    issues = run_rule_on_file(rule, "test_unused_imports.vy", test_project_context)

    # Should detect 3 unused imports: IERC20, IERC721, and UnusedERC165
    assert len(issues) == 3

    # Check that the correct imports are flagged
    unused_imports = {issue.message.split("'")[1] for issue in issues}
    assert unused_imports == {"IERC20", "IERC721", "UnusedERC165"}

    # Verify UsedERC20 and IERC4626 are not flagged (they are used)
    for issue in issues:
        assert "UsedERC20" not in issue.message
        assert "IERC4626" not in issue.message


def test_all_imports_used():
    """Test when all imports are used - should have no issues."""
    source = """
# pragma version >=0.4.0

from ethereum.ercs import IERC20
from ethereum.ercs import IERC721

token20: IERC20
token721: IERC721

@external
def set_token20(addr: address):
    self.token20 = IERC20(addr)

@external
def set_token721(addr: address):
    self.token721 = IERC721(addr)
"""

    rule = UnusedImportsRule()
    # Create a temporary file for the source
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".vy", delete=False) as f:
        f.write(source)
        temp_path = f.name

    try:
        context = ProjectContext([Path(temp_path)])
        issues = rule.run(context, Path(temp_path).resolve())
    finally:
        Path(temp_path).unlink()

    assert len(issues) == 0


def test_aliased_imports():
    """Test aliased imports detection."""
    source = """
# pragma version >=0.4.0

from ethereum.ercs import IERC20 as Token
from ethereum.ercs import IERC721 as NFT
from ethereum.ercs import IERC4626 as Vault

# Only Token is used
my_token: Token

@external
def set_token(addr: address):
    self.my_token = Token(addr)
"""

    rule = UnusedImportsRule()
    # Create a temporary file for the source
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".vy", delete=False) as f:
        f.write(source)
        temp_path = f.name

    try:
        context = ProjectContext([Path(temp_path)])
        issues = rule.run(context, Path(temp_path).resolve())
    finally:
        Path(temp_path).unlink()

    # NFT and Vault should be flagged as unused
    assert len(issues) == 2
    unused_imports = {issue.message.split("'")[1] for issue in issues}
    assert unused_imports == {"NFT", "Vault"}


def test_import_used_in_function_call():
    """Test import used directly in function calls."""
    source = """
# pragma version >=0.4.0

from ethereum.ercs import IERC20
from ethereum.ercs import IERC721

@external
@view
def get_balance(token: address, account: address) -> uint256:
    return staticcall IERC20(token).balanceOf(account)
"""

    rule = UnusedImportsRule()
    # Create a temporary file for the source
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".vy", delete=False) as f:
        f.write(source)
        temp_path = f.name

    try:
        context = ProjectContext([Path(temp_path)])
        issues = rule.run(context, Path(temp_path).resolve())
    finally:
        Path(temp_path).unlink()

    # Only IERC721 should be unused
    assert len(issues) == 1
    assert "IERC721" in issues[0].message


def test_no_imports():
    """Test contract with no imports - should have no issues."""
    source = """
# pragma version >=0.4.0

counter: uint256

@external
def increment():
    self.counter += 1
"""

    rule = UnusedImportsRule()
    # Create a temporary file for the source
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".vy", delete=False) as f:
        f.write(source)
        temp_path = f.name

    try:
        context = ProjectContext([Path(temp_path)])
        issues = rule.run(context, Path(temp_path).resolve())
    finally:
        Path(temp_path).unlink()

    assert len(issues) == 0


def test_import_used_in_type_annotation():
    """Test imports used in type annotations."""
    source = """
# pragma version >=0.4.0

from ethereum.ercs import IERC20
from ethereum.ercs import IERC721

@external
@view
def interact_with_token(token: IERC20) -> uint256:
    return staticcall token.totalSupply()
"""

    rule = UnusedImportsRule()
    # Create a temporary file for the source
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".vy", delete=False) as f:
        f.write(source)
        temp_path = f.name

    try:
        context = ProjectContext([Path(temp_path)])
        issues = rule.run(context, Path(temp_path).resolve())
    finally:
        Path(temp_path).unlink()

    # Only IERC721 should be unused
    assert len(issues) == 1
    assert "IERC721" in issues[0].message
