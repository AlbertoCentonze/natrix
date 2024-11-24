# Natrix

Natrix is a vyper linter that checks for common mistakes in vyper contracts. It is designed to be your vyper copilot, helping you to write code that is more secure and efficient.

## Getting started

Currently natrix requires [`uv`](https://docs.astral.sh/uv/) to be installed to function correctly.

To check a contract:

```bash
natrix file_to_lint.vy
```

To check all vyper contract in the current directory:

```bash
natrix
```

## Pre-commit hook

Natrix can also be used as a [pre-commit hook](https://pre-commit.com/). This allows to have your contracts checked automatically before you can commit.

To add natrix just add the following lines to your `pre-commit-config.yaml` config file:
```yaml
repo:
TODO
```

and then install pre-commit in your repository by doing:
```bash
pre-commit install
```

## Disclaimer

Natrix is highly experimental software, I do not take any responsibility for changes to the codebase suggested by this linter that might lead to loss of funds or any other issue.
