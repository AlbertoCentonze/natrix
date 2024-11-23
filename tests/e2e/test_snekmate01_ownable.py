from natrix.rules import rules


def test_snekmate01_ownable(snekmate01_ownable_contract):
    issues = []
    for rule in rules:
        for issue in rule.run(snekmate01_ownable_contract):
            print(issue)
            issues.append(issue)

    # TODO
    # assert len(issues) == 0
