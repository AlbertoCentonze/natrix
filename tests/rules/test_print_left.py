from natrix.rules.print_left import PrintLeftRule


def test_print_left(uncached_contract):
    rule = PrintLeftRule()

    issues = rule.run(uncached_contract)
    assert len(issues) == 2
    assert issues[0].position == "19:8"
    assert issues[1].position == "22:8"
    assert (
        issues[0].message
        == "Found a 'print' statement; consider removing it in production code."
    )
    assert (
        issues[1].message
        == "Found a 'print' statement; consider removing it in production code."
    )
