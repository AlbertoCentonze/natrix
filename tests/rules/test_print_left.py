from natrix.rules.print_left import PrintLeftRule
from tests.conftest import run_rule_on_file


def test_print_left(test_project_context):
    rule = PrintLeftRule()

    issues = run_rule_on_file(rule, "uncached.vy", test_project_context)
    assert len(issues) == 2
    assert issues[0].position == "19:8"
    assert issues[1].position == "22:8"
    assert (
        issues[0].message
        == "Found a 'print' statement; consider removing it in production code."
    )
    assert (
        issues[1].message
        == "Found a 'print' statement; consider removing it in production code."
    )
