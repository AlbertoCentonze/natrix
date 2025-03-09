from natrix.rules.unused_variable import UnusedVariableRule


def test_unused_variable(uncached_contract):
    """
    Test that the UnusedVariableRule correctly identifies unused variables.

    This test also verifies that immutable variables (like 'owner') are not
    flagged as unused, even when they are only assigned in the constructor
    and not used elsewhere in the code.
    """
    rule = UnusedVariableRule()
    issues = rule.run(uncached_contract)

    # We should only have the two local unused variables, not the immutable 'owner'
    assert len(issues) == 2

    # Sort issues by line number for consistent testing
    sorted_issues = sorted(issues, key=lambda x: int(x.position.split(":")[0]))

    # Check exact line numbers and messages to prevent regressions
    assert sorted_issues[0].position == "23:4"  # Line for another_unused_var
    assert sorted_issues[1].position == "24:4"  # Line for hey_unused_var
    assert "another_unused_var" in sorted_issues[0].message
    assert "hey_unused_var" in sorted_issues[1].message

    # Verify that 'owner' is not in the issues
    for issue in issues:
        assert "owner" not in issue.message
