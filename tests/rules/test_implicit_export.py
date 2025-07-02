from natrix.rules.implicit_export import ImplicitExportRule
from tests.conftest import run_rule_on_file


def test_implicit_export(test_project_context):
    rule = ImplicitExportRule()

    issues = run_rule_on_file(
        rule, "scrvusd_oracle/scrvusd_oracle.vy", test_project_context
    )
    assert len(issues) == 1
    assert issues[0].position == "17:0"
    assert issues[0].message == (
        "Module 'ownable' is exposing all its functions using `__interface__`. "
        "Consider exporting them one by one to make the contract more explicit. "
        "You can run 'natrix codegen exports path/to/ownable.vy' to generate the explicit exports."
    )
