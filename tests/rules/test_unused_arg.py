from natrix.rules.unused_arg import UnusedArgRule
from natrix.ast_tools import parse_file


def test_unused_arg():
    """
    Test that the UnusedArgRule correctly identifies unused function arguments.
    
    This test verifies that:
    1. Unused arguments in regular functions are flagged
    2. Interface function definitions are not flagged
    """
    # Parse the test file with unused arguments
    ast = parse_file("tests/test_unused_arg.vy")
    
    rule = UnusedArgRule()
    issues = rule.run(ast)
    
    # Check that only the unused argument is flagged
    assert len(issues) == 1
    assert issues[0].position == "2:49"  # Line for _unused_arg
    assert "_unused_arg" in issues[0].message
    assert "function_with_unused_arg" in issues[0].message
    
    # Verify that used arguments are not flagged
    for issue in issues:
        assert "_used_arg" not in issue.message
        assert "_arg1" not in issue.message
        assert "_arg2" not in issue.message


def test_interface_functions_not_flagged():
    """
    Test that the UnusedArgRule does not flag interface function arguments.
    
    Uses the Twocrypto.vy contract which has interface function definitions.
    """
    # Load the Twocrypto contract directly
    twocrypto_contract = parse_file("tests/contracts/Twocrypto.vy")
    
    rule = UnusedArgRule()
    issues = rule.run(twocrypto_contract)
    
    # Check that no interface function arguments are flagged
    for issue in issues:
        # Make sure none of the interface function arguments are flagged
        assert "wad_exp" not in issue.message
        assert "newton_D" not in issue.message
        assert "get_y" not in issue.message
        assert "get_p" not in issue.message
        assert "calc_token_amount" not in issue.message
        assert "get_dy" not in issue.message
        assert "get_dx" not in issue.message
