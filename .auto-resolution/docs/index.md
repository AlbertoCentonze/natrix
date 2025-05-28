# Welcome to Natrix

Natrix is a static analysis tool for Vyper contracts that helps you identify potential issues, style violations, and optimization opportunities in your smart contracts.

## Why Natrix?

Smart contracts on blockchain platforms manage valuable assets and are immutable once deployed. Static analysis helps detect potential issues before deployment, saving gas costs and preventing security vulnerabilities.

Natrix focuses specifically on Vyper, providing tailored analysis for this smart contract language.

## Features

Natrix performs various checks on your Vyper code, including:

- Style checks (naming conventions, explicit decorators)
- Gas optimization suggestions (storage caching, memory expansion)
- Code quality warnings (unused variables and arguments)
- Security best practices

For a complete list of rules, see the [Rules](./rules/index.md) section.

## Getting Started

Ready to start using Natrix? Check out our [Quick Start](./quick-start.md) guide for installation and basic usage instructions.

For advanced configuration options, see the [Configuration](./configuration.md) guide.

## Acknowledgements

Natrix would not be possible without the support of:

* [**Builder ENS Grants**](https://builder.ensgrants.xyz/) - For providing a grant to support the development of Natrix.
* [**Charles Cooper**](https://x.com/big_tech_sux) - Vyper core developer, for his invaluable help with the AST implementation and technical guidance.
* [**Curve Finance**](https://curve.finance) - For providing complex smart contract challenges that inspired the creation of this linter.

Thank you to all contributors and supporters who have helped make this project a reality!
