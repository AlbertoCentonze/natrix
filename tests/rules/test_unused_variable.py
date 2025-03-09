from natrix.rules.unused_variable import UnusedVariableRule


def test_unused_variable(uncached_contract):
    rule = UnusedVariableRule()
    issues = rule.run(uncached_contract)

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
    assert (
        another_unused_var_issue is not None
    ), "No issue found for 'another_unused_var'"

    # Check the positions - these should be the declaration positions, not the reassignment positions
    assert hey_unused_var_issue.position == "6:4"
    assert another_unused_var_issue.position == "7:4"

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
        if "Variable 'i' is declared but never used." == issue.message:
            i_issue = issue
        elif "Variable 'x' is declared but never used." == issue.message:
            x_issue = issue
        elif "Variable 'unused_var' is declared but never used." == issue.message:
            unused_var_issue = issue
        elif "Variable '_' is declared but never used." == issue.message:
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
