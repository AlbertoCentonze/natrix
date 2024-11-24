from collections import defaultdict
from dataclasses import dataclass
from typing import List

from natrix.ast_node import Node
from natrix.rules.common import BaseRule


@dataclass
class MemoryAccess:
    node: Node
    type: str  # "read" or "write"
    var: str


def analyze_access_patterns(accesses) -> List[MemoryAccess]:
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
    access_counts = defaultdict(int)  # Tracks consecutive reads
    last_write = {}  # Tracks last write for each variable
    suggestions = []  # Collect suggestions for caching

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

    return suggestions


class CacheStorageVariableRule(BaseRule):
    def __init__(self):
        super().__init__(
            severity="optimization",
            code="NTX007",
            message="Storage variable '{}' is accessed multiple times; consider caching it to save gas.",
        )
        self.accesses = []

    def visit_FunctionDef(self, node: Node):
        # Reset accesses for each function
        self.accesses = []

        # Collect all attributes within the function
        attrs = node.get_descendants("Attribute")
        if not attrs:
            return

        # Process variable reads and writes
        for attr in attrs:
            for access_type in ("variable_reads", "variable_writes"):
                if access_type in attr.node_dict:
                    for item in attr.get(access_type):
                        self.accesses.append(
                            MemoryAccess(
                                node=attr,
                                type="read"
                                if access_type == "variable_reads"
                                else "write",
                                var=item.get("name"),
                            )
                        )

        # Analyze accesses for caching suggestions
        suggestions = analyze_access_patterns(self.accesses)

        # Emit warnings or suggestions
        for suggestion in suggestions:
            self.add_issue(
                suggestion.node,
                suggestion.var,
            )
