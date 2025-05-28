# API Reference

This section provides an overview of the Natrix API for developers creating custom rules or integrating Natrix into other tools.

## Core Architecture

Natrix is built around several key abstractions that provide an unstable API for rule development:

### AST Processing Pipeline
1. **Vyper Compilation**: Compile `.vy` files to annotated AST
2. **Node Wrapping**: Wrap raw AST in `Node` objects for easy traversal
3. **Rule Application**: Apply registered rules using the visitor pattern
4. **Issue Collection**: Gather and format rule violations

## Node API

The `Node` class is the primary abstraction for working with Vyper AST data. It is inspired by the [`VyperNode`](https://github.com/vyperlang/vyper/blob/6ecdb3c01088ebd0060ccdc65a5a4c231e6340cc/vyper/ast/nodes.py) class but adapted to work with json AST data.

### Basic Node Operations

```python
from natrix.ast_node import Node

# Create a node from AST data
node = Node(ast_dict)

# Access node properties safely
node_type = node.get("ast_type")
function_name = node.get("name", default="unknown")

# Navigate the AST tree
parent = node.parent
children = node.children
```

### Node Traversal Methods

This methods are inspired from the vyper

#### `get_descendants(node_type=None, filters=None, include_self=False, reverse=False)`
Find all descendant nodes matching criteria:

```python
# Find all function definitions
functions = root.get_descendants("FunctionDef")

# Find nodes with specific properties
assigns = root.get_descendants("Assign", filters={"target.id": "total"})

# Multiple node types
control_flow = root.get_descendants(("If", "For", "While"))
```

#### `get_children(node_type=None, filters=None, reverse=False)`
Find immediate children only:

```python
# Get all direct children of a specific type
statements = function_node.get_children("Expr")
```

#### `get_ancestor(node_type=None)`
Find parent nodes:

```python
# Find the containing function
containing_function = node.get_ancestor("FunctionDef")

# Find any ancestor matching types
container = node.get_ancestor(("FunctionDef", "For", "If"))
```

### Property Access with `get()`

Safely access nested properties using dot notation:

```python
# Simple property access
line_number = node.get("lineno")

# Nested property access
target_name = node.get("target.id")
decorator_name = node.get("decorator_list.0.id")

# With default values
node_name = node.get("name", default="anonymous")
```

## FunctionDefNode API

Specialized subclass for function definitions with additional properties:

```python
from natrix.ast_node import FunctionDefNode

# Cast or create FunctionDefNode
if node.ast_type == "FunctionDef":
    func_node = FunctionDefNode(node.node_dict, parent=node.parent)
```

### Properties

#### `modifiers: List[str]`
Get function decorators:

```python
# Returns list like ["external", "view", "nonreentrant"]
decorators = func_node.modifiers

# Check for specific modifiers
is_external = "external" in func_node.modifiers
is_view = "view" in func_node.modifiers
```

#### `is_constructor: bool`
Check if function is a constructor:

```python
if func_node.is_constructor:
    # Handle constructor logic
    pass
```

#### `is_from_interface: bool`
Check if function is from an interface definition:

```python
if func_node.is_from_interface:
    # Skip interface functions
    return
```

#### `memory_accesses: List[MemoryAccess]`
Get all memory read/write operations:

```python
for access in func_node.memory_accesses:
    print(f"{access.type}: {access.var}")  # "read: balance"
```

## Rule Development API

### Base Rule Class

All rules inherit from `BaseRule`:

```python
from natrix.rules.common import BaseRule, RuleRegistry
from natrix.ast_node import Node

@RuleRegistry.register
class MyRule(BaseRule):
    CODE = "NTX999"  # Unique rule identifier
    MESSAGE = "Following pattern is not allowed: {}"  # Format string for messages

    def __init__(self, custom_param="default"):
        super().__init__(
            severity="warning",  # "error", "warning", "info"
            code=self.CODE,
            message=self.MESSAGE,
        )
        self.custom_param = custom_param
```

### Visitor Methods

Implement visitor methods for specific AST node types:

```python
class MyRule(BaseRule):
    def visit_FunctionDef(self, node):
        """Called for every function definition"""
        if self._should_flag(node):
            self.add_issue(node, "Function violates rule")

    def visit_Assign(self, node):
        """Called for every assignment"""
        pass

    def visit_Name(self, node):
        """Called for every name reference"""
        pass
```

### Issue Reporting

#### `add_issue(node, *message_args)`
Report a rule violation:

```python
def visit_FunctionDef(self, node):
    function_name = node.get("name")
    if len(function_name) > 50:
        # Message formatting with arguments
        self.add_issue(node, function_name, len(function_name))
```

### Rule Registration

#### Manual Registration
```python
from natrix.rules.common import RuleRegistry

# Register a rule class
RuleRegistry.register(MyRule)
```

#### Decorator Registration
```python
@RuleRegistry.register  # Recommended approach
class MyRule(BaseRule):
    pass
```

## AST Tools API

Utilities for working with Vyper compilation:

```python
from natrix.ast_tools import parse_file, vyper_compile, VyperASTVisitor

# Parse a Vyper file to AST
ast_data = parse_file("contract.vy")
root_node = Node(ast_data)

# Compile with specific format
ast_only = vyper_compile("contract.vy", "annotated_ast")
metadata = vyper_compile("contract.vy", "metadata")
```

### VyperASTVisitor

Base visitor for traversing AST nodes:

```python
class MyVisitor(VyperASTVisitor):
    def visit_FunctionDef(self, node):
        print(f"Found function: {node.get('name')}")

    def visit_Assign(self, node):
        print(f"Assignment at line {node.get('lineno')}")

# Use the visitor
visitor = MyVisitor()
visitor.visit(root_node)
```

## Configuration API

### Rule Configuration

Rules can accept configuration parameters:

```python
class ConfigurableRule(BaseRule):
    def __init__(self, threshold=100, pattern="^_"):
        super().__init__()
        self.threshold = threshold
        self.pattern = re.compile(pattern)
```

Configuration is passed via:
- TOML files: `[tool.natrix.rule_configs.ConfigurableRule]`
- CLI arguments: `--rule-config ConfigurableRule.threshold=200`

## Creating Rules

### Step-by-Step Example

This examples shows how to apply a rule that at enforces function naming to be in `snake_case`.

```python
from natrix.rules.common import BaseRule, RuleRegistry
from natrix.ast_node import FunctionDefNode
import re

@RuleRegistry.register
class FunctionNamingRule(BaseRule):
    """
    Enforces function naming conventions.

    Functions should use snake_case naming.
    """

    CODE = "NTX100"
    MESSAGE = "Function '{}' should use snake_case naming"

    def __init__(self, pattern=r"^[a-z_][a-z0-9_]*$"):
        super().__init__(
            severity="warning",
            code=self.CODE,
            message=self.MESSAGE,
        )
        self.pattern = re.compile(pattern)

    def visit_FunctionDef(self, node: FunctionDefNode):
        # Skip interface functions
        if node.is_from_interface:
            return

        function_name = node.get("name")

        # Skip special functions
        if function_name.startswith("__"):
            return

        if not self.pattern.match(function_name):
            self.add_issue(node, function_name)
```

### Testing Rules

```python
import pytest
from natrix.ast_tools import parse_file
from natrix.ast_node import Node

def test_function_naming_rule():
    # Create test contract
    test_contract = """
@external
def badFunctionName():  # Should trigger rule
    pass

@external
def good_function_name():  # Should pass
    pass
"""

    # Parse and test
    with open("test.vy", "w") as f:
        f.write(test_contract)

    ast_data = parse_file("test.vy")
    rule = FunctionNamingRule()
    issues = rule.run(ast_data)

    assert len(issues) == 1
    assert "badFunctionName" in issues[0].message
```

## Best Practices

### Performance
- **Cache expensive operations** using `@cached_property`
- **Use specific visitor methods** instead of generic traversal
- **Filter early** with node type and filter parameters

### Robustness
- **Use `node.get()` with defaults** for safe property access
- **Check node types** before casting to specialized classes
- **Handle missing AST properties** gracefully

### Maintainability
- **Use descriptive rule codes and messages**
- **Document rule behavior** in docstrings
- **Provide configuration options** for flexibility
- **Include comprehensive tests**
