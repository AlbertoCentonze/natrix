from natrix.rules import UnusedVariableRule


def test_unused_variable(uncached_contract):
    rule = UnusedVariableRule()
    issues = rule.run(uncached_contract)

    # Expecting one issue for 'hey_unused_var'
    assert len(issues) == 1
    assert issues[0].position == "5:4"  # Adjusted to the correct position
    assert issues[0].message == "Variable 'hey_unused_var' is declared but never used."
