from natrix.rules.implicit_pure import ImplicitPureRule
from tests.conftest import run_rule_on_file


def test_implicit_pure(test_project_context):
    rule = ImplicitPureRule()

    issues = run_rule_on_file(rule, "version_dummy.vy", test_project_context)
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


def test_implicit_pure_with_staticcalls(test_project_context):
    rule = ImplicitPureRule()

    issues = run_rule_on_file(rule, "test_implicit_pure.vy", test_project_context)
    assert len(issues) == 2
    assert issues[0].position == "9:0"
    assert issues[1].position == "14:0"
    assert (
        issues[0].message
        == "Function 'get_value_pure' does not access state but is not marked as 'pure'."
    )
    assert (
        issues[1].message
        == "Function 'get_values_pure' does not access state but is not marked as 'pure'."
    )
