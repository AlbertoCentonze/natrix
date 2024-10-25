from natrix.rules import ConstantNamingRule


def test_fee_splitter_version_underscore(fee_splitter_contract):
    rule = ConstantNamingRule()

    issues = rule.run(fee_splitter_contract)
    assert len(issues) == 1
    assert issues[0].position == "47:0"
    assert issues[0].file == "contracts/FeeSplitter.vy"
