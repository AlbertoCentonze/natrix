from natrix.rules import rules


def test_version_dummy(dummy_version_contract):
    for rule in rules:
        for issue in rule.run(dummy_version_contract):
            print(issue)
