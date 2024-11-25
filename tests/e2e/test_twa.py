from natrix.rules import rules


def test_twa(twa_contract):
    for rule in rules:
        for issue in rule.run(twa_contract):
            print(issue)
