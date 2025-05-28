from natrix.rules.unused_arg import UnusedArgRule


def test_unused_argument(unused_import_contract):
    rule = UnusedArgRule()
    issues = rule.run(unused_import_contract)

    assert len(issues) == 1
    assert issues[0].position == "51:41"
    assert (
        issues[0].message
        == "Function 'set_some_addy_alt' argument 'unused_arg' is never used."
    )
