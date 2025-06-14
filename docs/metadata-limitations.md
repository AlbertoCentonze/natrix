# Metadata Limitations

## Overview

Some Natrix rules rely on metadata output from the Vyper compiler. However, files using deferred module initialization cannot generate metadata.

## Deferred Module Initialization

When a Vyper file uses the `uses:` statement for deferred initialization, the compiler cannot generate metadata. This is because module initialization constraints are validated after AST generation but before code generation (where metadata is produced).

For more details about the `uses:` statement, see the [Vyper documentation](https://docs.vyperlang.org/en/latest/using-modules.html#the-uses-statement).

## Affected Rules

- **Memory Expansion (NTX1)**: Cannot analyze function frame sizes without metadata

## Impact

For files using deferred initialization:
- AST-based rules work normally
- Metadata-dependent rules are silently skipped
