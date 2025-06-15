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

    # Find issues for specific variables
    hey_unused_var_issue = None
    another_unused_var_issue = None

    for issue in issues:
        if "hey_unused_var" in issue.message:
            hey_unused_var_issue = issue
        elif "another_unused_var" in issue.message:
            another_unused_var_issue = issue

    # Check that the issues are for the expected variables
    assert hey_unused_var_issue is not None, "No issue found for 'hey_unused_var'"
    assert another_unused_var_issue is not None, (
        "No issue found for 'another_unused_var'"
    )

    # Check the positions - these should be the declaration positions, not the reassignment positions
    assert hey_unused_var_issue.position == "11:4"
    assert another_unused_var_issue.position == "12:4"

    # Check the messages
    assert (
        hey_unused_var_issue.message
        == "Variable 'hey_unused_var' is declared but never used."
    )
    assert (
        another_unused_var_issue.message
        == "Variable 'another_unused_var' is declared but never used."
    )


def test_for_loop_underscore(for_loop_underscore_contract):
    """Test that the unused variable rule ignores underscore variables in for loops."""
    rule = UnusedVariableRule()
    issues = rule.run(for_loop_underscore_contract)

    # We should have 3 issues: the unused 'i' in the for loop, the unused 'x' variable, and the unused_var
    assert len(issues) == 3

    # Find issues for specific variables
    i_issue = None
    x_issue = None
    unused_var_issue = None
    underscore_issue = None

    for issue in issues:
        if issue.message == "Variable 'i' is declared but never used.":
            i_issue = issue
        elif issue.message == "Variable 'x' is declared but never used.":
            x_issue = issue
        elif issue.message == "Variable 'unused_var' is declared but never used.":
            unused_var_issue = issue
        elif issue.message == "Variable '_' is declared but never used.":
            underscore_issue = issue

    # Check that the issues are for the expected variables
    assert i_issue is not None, "No issue found for 'i'"
    assert x_issue is not None, "No issue found for 'x'"
    assert unused_var_issue is not None, "No issue found for 'unused_var'"
    assert underscore_issue is None, "Issue found for '_' but it should be ignored"

    # Check the positions - using the actual positions reported by the rule
    assert i_issue.position == "6:8"  # Correct position for 'i' in the for loop
    assert x_issue.position == "15:8"
    assert unused_var_issue.position == "18:4"

    # Check the messages
    assert i_issue.message == "Variable 'i' is declared but never used."
    assert x_issue.message == "Variable 'x' is declared but never used."
    assert (
        unused_var_issue.message == "Variable 'unused_var' is declared but never used."
    )

    # Sort issues by line number for consistent testing
    sorted_issues = sorted(issues, key=lambda x: int(x.position.split(":")[0]))

    # Check exact line numbers and messages to prevent regressions
    assert sorted_issues[0].position == "6:8"  # Line for i in for loop
    assert sorted_issues[1].position == "15:8"  # Line for x variable
    assert sorted_issues[2].position == "18:4"  # Line for unused_var
    assert "i" in sorted_issues[0].message
    assert "x" in sorted_issues[1].message
    assert "unused_var" in sorted_issues[2].message

    # Verify that 'owner' is not in the issues
    for issue in issues:
        assert "owner" not in issue.message
