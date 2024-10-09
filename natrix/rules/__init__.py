from natrix.rules.dynarray_overallocation import DynArrayOverallocation
from natrix.rules.common import Rule

rules = [
    Rule(
        name="DynArrayOverallocation",
        description="Detect overallocation of DynArray",
        run=DynArrayOverallocation().run,
    )
]
