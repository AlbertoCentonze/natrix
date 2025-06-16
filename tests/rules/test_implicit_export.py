from natrix.rules.implicit_export import ImplicitExportRule


def test_implicit_export(scrvusd_oracle_contract):
    rule = ImplicitExportRule()

    issues = rule.run(scrvusd_oracle_contract)
    assert len(issues) == 1
    assert issues[0].position == "17:0"
    assert issues[0].message == (
        "Module 'ownable' is exposing all its functions using `__interface__`. "
        "Consider exporting them one by one to make the contract more explicit. "
        "You can run 'natrix codegen exports path/to/ownable.vy' to generate the explicit exports."
    )
