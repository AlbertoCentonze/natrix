from natrix.rules.memory_expansion import MemoryExpansionRule
from tests.conftest import run_rule_on_file


def test_fee_splitter_dispatch_fees(test_project_context):
    rule = MemoryExpansionRule()

    issues = run_rule_on_file(rule, "fee_splitter/FeeSplitter.vy", test_project_context)
    assert len(issues) == 2
    # Should detect both _set_receivers and set_receivers
    assert issues[0].position == "142:0"  # _set_receivers
    assert issues[1].position == "204:0"  # set_receivers
    assert all(issue.file.name == "FeeSplitter.vy" for issue in issues)
