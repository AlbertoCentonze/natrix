# Development Guide

This section provides information for developers contributing to Natrix.

### Python Version

Natrix requires Python 3.10 or higher. This is specified in `pyproject.toml`:
```toml
requires-python = ">=3.10"
```

### UV Package Manager

Natrix uses [UV](https://docs.astral.sh/uv/) for dependency management and development workflows.

### Vyper Compiler

Natrix requires a specific version of the Vyper compiler, each release of natrix is only compatible with a specific vyper compiler version.

## Creating a New Rule

See the [API Reference](../api/index.md#creating-rules) for detailed information on implementing new rules.

## Getting Help

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/albertocentonze/natrix/issues)
- **Discussions**: Ask questions on [Vyperholics](https://t.me/vyperlang)
