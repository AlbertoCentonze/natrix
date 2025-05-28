from itertools import chain
from natrix.rules.common import RuleRegistry


def test_run_all(all_contracts):
    # while there is no real testing here, this
    # is a good way to spot regressions in the rules

    # Ensure all rules are discovered
    RuleRegistry.discover_rules()

    # Get all rules
    rules = RuleRegistry.get_rules()

    for contract, number_of_issues in all_contracts:
        issues = list(chain.from_iterable(rule.run(contract) for rule in rules))
        assert len(issues) == number_of_issues
