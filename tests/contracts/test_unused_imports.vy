# pragma version >=0.4.0

# Unused imports - should trigger warnings
from ethereum.ercs import IERC20
from ethereum.ercs import IERC721
from ethereum.ercs import IERC165 as UnusedERC165

# Used imports - should not trigger warnings
from ethereum.ercs import IERC20Detailed as UsedERC20
from ethereum.ercs import IERC4626

# Storage variables
token: UsedERC20
vault: IERC4626

@external
def set_token(new_token: address):
    """Uses the UsedERC20 import"""
    self.token = UsedERC20(new_token)

@external
def set_vault(new_vault: address):
    """Uses the IERC4626 import"""
    self.vault = IERC4626(new_vault)

@external
@view
def get_token_name() -> String[32]:
    """Uses the token which uses UsedERC20"""
    return staticcall self.token.name()

@external
@view
def get_vault_assets() -> address:
    """Uses the vault which uses IERC4626"""
    return staticcall self.vault.asset()
