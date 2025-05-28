from natrix.rules.unused_arg import UnusedArgRule


def test_unused_arg(test_unused_arg_contract):
    """
    Test that the UnusedArgRule correctly identifies unused function arguments.

    This test verifies that:
    1. Unused arguments in regular functions are flagged
    2. Interface function definitions are not flagged
    """
    rule = UnusedArgRule()
    issues = rule.run(test_unused_arg_contract)

    # Check that only the unused argument is flagged
    assert len(issues) == 1
    assert issues[0].position == "3:49"  # Line for _unused_arg
    assert "_unused_arg" in issues[0].message
    assert "function_with_unused_arg" in issues[0].message

    # Verify that used arguments are not flagged
    for issue in issues:
        assert "_used_arg" not in issue.message
        assert "_arg1" not in issue.message
        assert "_arg2" not in issue.message


def test_interface_functions_not_flagged(twocrypto_contract):
    """
    Test that the UnusedArgRule does not flag interface function arguments.

    Uses the Twocrypto.vy contract which has interface function definitions.
    """
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
