# Rules

This section documents the available rules in Natrix.

| Rule Code | Name | Severity | Description |
|-----------|------|----------|-------------|
| [NTX1](memory-expansion.md) | Memory Expansion | Warning | Detects when a function's memory frame size is too large |
| [NTX2](constant-naming.md) | Constant Naming Convention | Style | Ensures that constants are named in `UPPER_SNAKE_CASE` |
| [NTX3](implicit-internal.md) | Implicit Internal | Style | Detects when internal functions are missing the `@internal` decorator |
| [NTX4](implicit-view.md) | Implicit View | Style | Detects when view functions are missing the `@view` decorator |
| [NTX5](implicit-pure.md) | Implicit Pure | Style | Detects when pure functions are missing the `@pure` decorator |
| [NTX6](print-left.md) | Print Left | Warning | Detects when `print` statements are left in the code |
| [NTX7](storage-caching.md) | Cache Storage Variable | Optimization | Detects when a storage variable is accessed multiple times and suggests caching |
| [NTX8](unused-variable.md) | Unused Variable | Warning | Detects variables that are declared but never used |
| [NTX9](implicit-export.md) | Implicit Export | Important | Detects when a module exposes all its functions using `__interface__` |
| [NTX10](unused-argument.md) | Unused Argument | Warning | Detects function arguments that are declared but never used |
| [NTX11](argument-naming.md) | Argument Naming Convention | Warning | Ensures function arguments follow a specified naming convention |

## Rule Categories

Rules are categorized by severity:

* **Style**: Suggestions to improve code readability and consistency.
* **Warning**: Potential issues that could lead to bugs or inefficiencies.
* **Optimization**: Suggestions to improve gas efficiency.
* **Important**: Issues that could have significant impact on security or correctness.
