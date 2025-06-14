# Memory Expansion

| Property | Value |
|----------|-------|
| Rule Code | `NTX1` |
| Severity | Warning |
| Configuration | `max_frame_size` - Maximum allowed frame size in bytes (default: 20,000) |

!!! note "Metadata Requirement"
    This rule requires compiler metadata to analyze frame sizes. It cannot check files that use deferred module initialization (`uses:` statement). See [Metadata Limitations](../metadata-limitations.md) for details.

## Background

Vyper can only pass arguments by value. When a DynArray is passed as an argument in an external function, the amount of memory allocated will be the upper bound of the array size, and not its actual size, which can lead to unexpected memory expansion (and crazy gas costs) if arrays (even small) with large bounds are passed.

## Purpose

Detects when a function's memory frame size is too large (by default, over 20,000 bytes).

## Example

```vyper
# Non-compliant - large array passed by value can cause memory expansion issues
@external
def process_large_array(_data: DynArray[uint256, 100_000_000]) -> uint256:
    _sum: uint256 = 0
    for i: uint256 in range(1000):
        _sum += _data[i]
    return _sum
```

The `process_large_array` function can be flagged by this rule if the memory frame size exceeds the threshold. To avoid this issue, consider passing arrays with smaller bounds until vyper implements runtime allocation for arrays.

## Configuration

This rule can be customized by adjusting the maximum frame size threshold:

- `max_frame_size` (integer): Maximum allowed frame size in bytes (default: 20,000)

### pyproject.toml

```toml
[tool.natrix.rule_configs.MemoryExpansion]
max_frame_size = 25000
```

### Command Line Configuration
```bash
# Override threshold for a single run
natrix --rule-config MemoryExpansion.max_frame_size=25000
```

### Class Instantiation
```python
# Custom threshold of 10,000 bytes
MemoryExpansionRule(max_frame_size=10_000)
```
