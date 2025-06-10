from natrix.rules.memory_expansion import MemoryExpansionRule


def test_fee_splitter_dispatch_fees(fee_splitter_contract):
    rule = MemoryExpansionRule()

    issues = rule.run(fee_splitter_contract)
    assert len(issues) == 1
    assert issues[0].position == "158:0"
    assert issues[0].file == "tests/contracts/fee_splitter/FeeSplitter.vy"
