from natrix.rules import rules


def test_uncached(uncached_contract):
    for rule in rules:
        for issue in rule.run(uncached_contract):
            print(issue)
