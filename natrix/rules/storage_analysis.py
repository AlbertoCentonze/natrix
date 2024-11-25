from dataclasses import dataclass
from typing import List

from natrix.ast_node import Node

accesses_by_function = dict()


@dataclass()
class MemoryAccess:
    node: Node
    type: str  # "read" or "write"
    var: str


def get_memory_accesses(node: Node) -> List[MemoryAccess]:
    if node.ast_type != "FunctionDef":
        raise ValueError("Not a function")

    name = node.get("name")
    accesses = accesses_by_function.get(name, [])

    if accesses:
        print("cache hit")
        return accesses
    else:
        # This function relies on the assumption that storage accesses
        # are always reported in the Attribute node. As the AST is not
        # stable this might change across releases.
        attrs = node.get_descendants("Attribute")

        # If there are no attributes that means that there are no memory
        # accesses.
        if not attrs:
            return []

        # Process variable reads and writes
        for attr in attrs:
            for access_type in ("variable_reads", "variable_writes"):
                if access_type in attr.node_dict:
                    for item in attr.get(access_type):
                        accesses.append(
                            MemoryAccess(
                                node=attr,
                                type="read"
                                if access_type == "variable_reads"
                                else "write",
                                var=item.get("name"),
                            )
                        )

    return accesses
