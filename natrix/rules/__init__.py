from natrix.rules.memory_expansion import MemoryExpansionRule
from natrix.rules.constants_naming import ConstantNamingRule
from natrix.rules.common import Rule

rules = [
    Rule(
        name="Memory Expansion Check",
        description="Detect when memory expansion is too big compared to the specified threshold. "
        "This can be useful to spot when dynarrays with a large number of elements "
        "are being passed by value.",
        run=MemoryExpansionRule().run,
    ),
    Rule(
        name="Constant Naming Check",
        description="Detect when a constant is not named in UPPER_SNAKE_CASE.",
        run=ConstantNamingRule().run,
    ),
]
