from __future__ import annotations

from typing import TYPE_CHECKING

from natrix.rules.common import BaseRule, RuleRegistry

if TYPE_CHECKING:
    from natrix.ast_node import Node


@RuleRegistry.register
class UnusedEventRule(BaseRule):
    """
    Unused Event Check

    Detects events that are defined but never emitted in the contract.
    This helps identify dead code or missing functionality where events
    were defined but the corresponding log statements were never added.

    Example:
        event Transfer:  # This event will be reported if never used
            sender: indexed(address)
            receiver: indexed(address)
            amount: uint256
    """

    CODE = "NTX13"
    MESSAGE = "Event '{}' is defined but never emitted."

    def __init__(self) -> None:
        super().__init__(
            severity="warning",
            code=self.CODE,
            message=self.MESSAGE,
        )
        self.defined_events: dict[str, Node] = {}
        self.used_events: set[str] = set()

    def before_traversal(self) -> None:
        """Reset state before each analysis."""
        self.defined_events = {}
        self.used_events = set()

    def visit_EventDef(self, node: Node) -> None:
        """Track event definitions during traversal."""
        event_name = node.get("name")
        if event_name:
            self.defined_events[event_name] = node

    def visit_Log(self, node: Node) -> None:
        """Track event emissions via Log nodes."""
        # Get the event name from the Log node
        event_name = node.get("value.func.id")
        if event_name and event_name in self.defined_events:
            self.used_events.add(event_name)

    def after_traversal(self) -> None:
        """After traversal, report unused events."""
        for event_name, event_node in self.defined_events.items():
            if event_name not in self.used_events:
                self.add_issue(event_node, event_name)
