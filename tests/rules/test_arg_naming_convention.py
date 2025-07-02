from natrix.rules.arg_naming_convention import ArgNamingConventionRule
from tests.conftest import run_rule_on_file


def test_arg_naming_convention(test_project_context):
    rule = ArgNamingConventionRule(pattern=r"^_")

    issues = run_rule_on_file(rule, "unused_import.vy", test_project_context)

    assert len(issues) == 4

    assert issues[0].position == "41:19"
    assert (
        issues[0].message
        == "Function '_set_some_addy' argument 'new_addy' does not match the naming convention pattern '^_'."
    )

    assert issues[1].position == "51:22"
    assert (
        issues[1].message
        == "Function 'set_some_addy_alt' argument 'new_addy' does not match the naming convention pattern '^_'."
    )

    assert issues[2].position == "51:41"
    assert (
        issues[2].message
        == "Function 'set_some_addy_alt' argument 'unused_arg' does not match the naming convention pattern '^_'."
    )

    assert issues[3].position == "58:27"
    assert (
        issues[3].message
        == "Function 'set_some_addy_no_check' argument 'new_addy' does not match the naming convention pattern '^_'."
    )
