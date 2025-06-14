from natrix.rules.memory_expansion import MemoryExpansionRule


def test_fee_splitter_dispatch_fees(fee_splitter_contract):
    rule = MemoryExpansionRule()

    issues = rule.run(fee_splitter_contract)
    assert len(issues) == 2
    # Should detect both _set_receivers and set_receivers
    assert issues[0].position == "142:0"  # _set_receivers
    assert issues[1].position == "204:0"  # set_receivers
    assert all(
        issue.file == "tests/contracts/fee_splitter/FeeSplitter.vy" for issue in issues
    )
