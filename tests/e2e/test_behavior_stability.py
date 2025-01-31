from itertools import chain
from natrix.rules import rules


def test_run_all(all_contracts):
    # while there is no real testing here, this
    # is a good way to spot regressions in the rules
    for contract, number_of_issues in all_contracts:
        issues = list(chain.from_iterable(rule.run(contract) for rule in rules))
        assert len(issues) == number_of_issues
