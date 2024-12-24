from natrix.rules import UnusedVariableRule


def test_unused_variable(uncached_contract):
    rule = UnusedVariableRule()
    issues = rule.run(uncached_contract)

    assert len(issues) == 2
    assert issues[0].position == "19:4"
    assert issues[1].position == "18:4"
    assert issues[0].message == "Variable 'hey_unused_var' is declared but never used."
    assert (
        issues[1].message == "Variable 'another_unused_var' is declared but never used."
    )
