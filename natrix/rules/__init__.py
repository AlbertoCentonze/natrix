from dataclasses import dataclass
from typing import Callable
from natrix.rules.dynarray_overallocation import DynArrayOverallocation

@dataclass()
class Rule:
    name: str
    description: str
    apply: Callable
    # TODO add an id to ignore the rule

rules = [
    Rule(
        name="DynArrayOverallocation",
        description="Detect overallocation of DynArray",
        apply=DynArrayOverallocation()
    )
]

