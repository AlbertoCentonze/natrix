# pragma version >=0.4.0

from . import provider

# This line uses the constant from the provider module.
some_value: uint256

@deploy
def __init__():
    self.some_value = provider.USED_CONSTANT
