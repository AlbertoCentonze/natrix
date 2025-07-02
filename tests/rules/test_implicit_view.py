from natrix.rules.implicit_view import ImplicitViewRule
from tests.conftest import run_rule_on_file


def test_implicit_view(test_project_context):
    rule = ImplicitViewRule()

    issues = run_rule_on_file(rule, "version_dummy.vy", test_project_context)
    assert len(issues) == 2
    assert issues[0].position == "6:0"
    assert issues[1].position == "25:0"
    assert (
        issues[0].message
        == "Function 'view_external_marked_as_nothing' reads contract state but is not marked as 'view'."
    )
    assert (
        issues[1].message
        == "Function 'view_internal_marked_as_nothing' reads contract state but is not marked as 'view'."
    )
