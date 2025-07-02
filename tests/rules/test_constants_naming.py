from natrix.rules.constants_naming import ConstantNamingRule
from tests.conftest import run_rule_on_file


def test_fee_splitter_version_underscore(test_project_context):
    rule = ConstantNamingRule()

    issues = run_rule_on_file(rule, "fee_splitter/FeeSplitter.vy", test_project_context)
    assert len(issues) == 1
    assert issues[0].position == "47:0"
    assert issues[0].file.name == "FeeSplitter.vy"
