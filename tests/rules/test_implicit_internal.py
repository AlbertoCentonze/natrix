from natrix.rules.implicit_internal import ImplicitInternalRule


def test_implicit_internal(dummy_version_contract):
    rule = ImplicitInternalRule()

    issues = rule.run(dummy_version_contract)
    assert len(issues) == 3
    assert issues[0].position == "18:0"
    assert issues[1].position == "22:0"
    assert issues[2].position == "25:0"
    assert (
        issues[0].message
        == "Internal function 'pure_internal_marked_as_nothing' is missing the '@internal' decorator."
    )
    assert (
        issues[1].message
        == "Internal function 'pure_internal_marked_as_view' is missing the '@internal' decorator."
    )
    assert (
        issues[2].message
        == "Internal function 'view_internal_marked_as_nothing' is missing the '@internal' decorator."
    )
