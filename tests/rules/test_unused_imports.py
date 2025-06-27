from natrix.rules.unused_imports import UnusedImportsRule


def test_unused_imports(test_unused_imports_contract):
    """Test detection of unused imports."""
    rule = UnusedImportsRule()
    ast = test_unused_imports_contract
    issues = rule.run(ast)

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
    from natrix.ast_tools import parse_source

    rule = UnusedImportsRule()
    ast = parse_source(source)
    issues = rule.run(ast)

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
    from natrix.ast_tools import parse_source

    rule = UnusedImportsRule()
    ast = parse_source(source)
    issues = rule.run(ast)

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
    from natrix.ast_tools import parse_source

    rule = UnusedImportsRule()
    ast = parse_source(source)
    issues = rule.run(ast)

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
    from natrix.ast_tools import parse_source

    rule = UnusedImportsRule()
    ast = parse_source(source)
    issues = rule.run(ast)

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
    from natrix.ast_tools import parse_source

    rule = UnusedImportsRule()
    ast = parse_source(source)
    issues = rule.run(ast)

    # Only IERC721 should be unused
    assert len(issues) == 1
    assert "IERC721" in issues[0].message
