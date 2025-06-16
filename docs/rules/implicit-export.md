# Implicit Export

| Property | Value |
|----------|-------|
| Rule Code | `NTX9` |
| Severity | Important |

## Background

Explicitly listing exported functions improves code clarity and reduces the risk of unintentionally exposing internal functions. It makes the contract's public interface clear and well-defined.

## Purpose

Detects when a module exposes all its functions using the `__interface__` expression without explicitly listing them.

## Example

Consider you have a module `erc20.vy`:

```vyper
# erc20


@external
def transfer():
    # ... does something ...
    pass

@external
def mint():
    # ... does something else ...
    pass
```

And you import it in another contract:

```vyper
# my_token.vy
import erc20

# Non-compliant - exposes all functions from MyHelperFunctions, including potentially _internal_logic
exports: (erc20.__interface__) # this also exposes the function to mint, which might not always be intended
```

```vyper
# my_token.vy
import erc20

# Compliant - explicitly lists the functions to be exposed
exports: (erc20.transfer, erc20.mint) # you can clearly tell that you are exposing a function to mint
```

## Automatic Fix

Natrix can automatically generate the explicit exports for you. Simply run:

```bash
natrix codegen exports path/to/erc20.vy
```

This will output the explicit exports declaration that you can copy into your contract.
