from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from natrix.rules.common import BaseRule

if TYPE_CHECKING:
    from natrix.ast_node import FunctionDefNode, MemoryAccess, Node


def analyze_access_patterns(accesses: list[MemoryAccess]) -> set[MemoryAccess]:
    # Sort accesses by the node's position in the code
    combined = sorted(
        accesses, key=lambda x: (x.node.get("lineno"), x.node.get("col_offset"))
    )
    filtered_combined = []

    # Identify positions of writes to filter out overlapping reads
    seen_write_positions = {
        (access.node, access.var) for access in accesses if access.type == "write"
    }

    # Filter reads that occur at the same position as a write
    for access in combined:
        if access.type == "read" and (access.node, access.var) in seen_write_positions:
            continue
        filtered_combined.append(access)

    # Analyze read/write patterns to suggest caching
    access_counts: dict[str, int] = defaultdict(int)  # Tracks consecutive reads
    last_write: dict[str, Node | None] = {}  # Tracks last write for each variable
    suggestions: list[MemoryAccess] = []  # Collect suggestions for caching

    for access in filtered_combined:
        if access.type == "read":
            # Increment read count if no intervening write
            if last_write.get(access.var, None) != access.node:
                access_counts[access.var] += 1
                if access_counts[access.var] > 1:
                    suggestions.append(
                        access
                    )  # Include full MemoryAccess object for reporting
        elif access.type == "write":
            # Reset read count on a write
            last_write[access.var] = access.node
            access_counts[access.var] = 0

    return set(suggestions)


# This rule is intentionally not registered in the RuleRegistry since it's too
# experimental.
class CacheStorageVariableRule(BaseRule):
    """
    Variable Caching Check

    Detect when a variable is accessed multiple times in a function and
    suggest caching it.
    """

    CODE = "NTX7"
    MESSAGE = (
        "Storage variable '{}' is accessed multiple times; "
        "consider caching it to save gas."
    )

    def __init__(self) -> None:
        super().__init__(
            severity="optimization",
            code=self.CODE,
            message=self.MESSAGE,
        )

    def visit_FunctionDef(self, node: FunctionDefNode) -> None:
        accesses = node.memory_accesses

        # Analyze accesses for caching suggestions
        issues = analyze_access_patterns(accesses)

        # Emit warnings or suggestions
        for issue in issues:
            self.add_issue(
                issue.node,
                issue.var,
            )
