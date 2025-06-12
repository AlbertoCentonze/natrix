import pytest
from natrix import parse_file
from natrix.rules.modifiers_ordering import ModifiersOrderingRule


@pytest.fixture()
def test_modifiers_ordering_contract():
    return parse_file("tests/contracts/test_modifiers_ordering.vy")


def test_modifiers_ordering(test_modifiers_ordering_contract):
    rule = ModifiersOrderingRule()

    issues = rule.run(test_modifiers_ordering_contract)

    # We expect 6 issues for the incorrect ordering examples
    assert len(issues) == 6

    # Check that we found all the incorrect orderings
    issue_messages = [issue.message for issue in issues]

    # Check specific issues
    incorrect_functions = [
        "incorrect_view_external",
        "incorrect_pure_internal",
        "incorrect_nonreentrant_external",
        "incorrect_nonreentrant_view_external",
        "incorrect_payable_nonreentrant_external",
        "incorrect_implicit_internal_nonreentrant_view",
    ]

    for func_name in incorrect_functions:
        assert any(
            func_name in msg for msg in issue_messages
        ), f"Expected issue for {func_name}"

    # Verify the issue details for one specific case
    view_external_issue = next(
        (issue for issue in issues if "incorrect_view_external" in issue.message), None
    )
    assert view_external_issue is not None
    assert view_external_issue.code == "NTX12"
    assert view_external_issue.severity == "style"
    assert "@view, @external" in view_external_issue.message

    # Verify implicit internal cases
    implicit_issue = next(
        (
            issue
            for issue in issues
            if "incorrect_implicit_internal_nonreentrant_view" in issue.message
        ),
        None,
    )
    assert implicit_issue is not None
    assert "@nonreentrant, @view" in implicit_issue.message
