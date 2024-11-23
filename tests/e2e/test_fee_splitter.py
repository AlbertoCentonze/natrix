from natrix.rules import rules


def test_fee_splitter(fee_splitter_contract):
    for rule in rules:
        for issue in rule.run(fee_splitter_contract):
            print(issue)
