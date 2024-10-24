from natrix.rules.memory_expansion import MemoryExpansionRule
from natrix.rules.common import Rule

rules = [
    Rule(
        name="DynArrayOverallocation",
        description="Detect overallocation of DynArray",
        run=MemoryExpansionRule().run,
    )
]
