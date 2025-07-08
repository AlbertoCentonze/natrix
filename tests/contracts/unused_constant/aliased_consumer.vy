# pragma version >=0.4.0

from . import provider as prov

# This uses USED_CONSTANT through an aliased import
aliased_value: uint256

@deploy
def __init__():
    self.aliased_value = prov.USED_CONSTANT
