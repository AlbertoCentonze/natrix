from natrix.rules.implicit_internal import ImplicitInternalRule
from tests.conftest import run_rule_on_file


def test_implicit_internal(test_project_context):
    rule = ImplicitInternalRule()

    issues = run_rule_on_file(rule, "version_dummy.vy", test_project_context)
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
