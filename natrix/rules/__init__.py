from natrix.rules.implicit_internal import ImplicitInternalRule
from natrix.rules.implicit_pure import ImplicitPureRule
from natrix.rules.implicit_view import ImplicitViewRule
from natrix.rules.memory_expansion import MemoryExpansionRule
from natrix.rules.constants_naming import ConstantNamingRule
from natrix.rules.common import Rule
from natrix.rules.print_left import PrintLeftRule
from natrix.rules.storage_caching import CacheStorageVariableRule
from natrix.rules.unused_variable import UnusedVariableRule
from natrix.rules.implicit_export import ImplicitExportRule
from natrix.rules.unused_arg import UnusedArgRule
from natrix.rules.arg_naming_convention import ArgNamingConventionRule

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
    Rule(
        name="Implicit Internal Decorator Check",
        description="Detect when internal functions are missing the '@internal' decorator.",
        run=ImplicitInternalRule().run,
    ),
    Rule(
        name="Implicit View Decorator Check",
        description="Detect when view functions are missing the '@view' decorator.",
        run=ImplicitViewRule().run,
    ),
    Rule(
        name="Implicit Pure Decorator Check",
        description="Detect when pure functions are missing the '@pure' decorator.",
        run=ImplicitPureRule().run,
    ),
    Rule(
        name="Print Left Check",
        description="Detect when a 'print' statement is used in the code.",
        run=PrintLeftRule().run,
    ),
    Rule(
        name="Variable Caching Check",
        description="Detect when a variable is accessed multiple times in a function and suggest caching it.",
        run=CacheStorageVariableRule().run,
    ),
    Rule(
        name="Unused Variable Check",
        description="Detect when a variable is declared but not used.",
        run=UnusedVariableRule().run,
    ),
    Rule(
        name="Implicit Export Check",
        description="Detect when the entirety of a module is being exposed using the `__interface__` expression.",
        run=ImplicitExportRule().run,
    ),
    Rule(
        name="Unused Argument Check",
        description="Detect when the argument of a function is not being used in its body.",
        run=UnusedArgRule().run,
    ),
    Rule(
        name="Argument Naming Convention Check",
        description="Detect when function arguments don't follow the specified naming convention pattern.",
        run=ArgNamingConventionRule(pattern=r"^_").run,
    ),
]
