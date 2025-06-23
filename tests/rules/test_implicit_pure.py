from natrix.rules.implicit_pure import ImplicitPureRule


def test_implicit_pure(dummy_version_contract):
    rule = ImplicitPureRule()

    issues = rule.run(dummy_version_contract)
    assert len(issues) == 4
    assert issues[0].position == "11:0"
    assert issues[1].position == "15:0"
    assert issues[2].position == "18:0"
    assert issues[3].position == "22:0"
    assert (
        issues[0].message
        == "Function 'pure_external_marked_as_view' does not access state but is not marked as 'pure'."
    )
    assert (
        issues[1].message
        == "Function 'pure_external_marked_as_nothing' does not access state but is not marked as 'pure'."
    )
    assert (
        issues[2].message
        == "Function 'pure_internal_marked_as_nothing' does not access state but is not marked as 'pure'."
    )
    assert (
        issues[3].message
        == "Function 'pure_internal_marked_as_view' does not access state but is not marked as 'pure'."
    )
