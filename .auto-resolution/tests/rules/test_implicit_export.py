from natrix.rules.implicit_export import ImplicitExportRule


def test_implicit_export(scrvusd_oracle_contract):
    rule = ImplicitExportRule()

    issues = rule.run(scrvusd_oracle_contract)
    assert len(issues) == 1
    assert issues[0].position == "17:0"
    assert issues[
        0
    ].message, "Module 'ownable' is exposing all its functions. Consider exporting them one by one to makethe contract more explicit."
