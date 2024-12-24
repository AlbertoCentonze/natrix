from natrix.rules import rules


def test_unused_import(unused_import_contract):
    for rule in rules:
        for issue in rule.run(unused_import_contract):
            print(issue)
