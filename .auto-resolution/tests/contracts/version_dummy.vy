version: uint256

@external
def view_external_marked_as_nothing() -> uint256:
    return self.version

@external
@view
def pure_external_marked_as_view() -> uint256:
    return 1234

@external
def pure_external_marked_as_nothing():
    pass

def pure_internal_marked_as_nothing():
    pass

@view
def pure_internal_marked_as_view() -> uint256:
    return 1234

def view_internal_marked_as_nothing() -> uint256:
    return self.version

@nonreentrant
@payable
@external
def non_view_external():
    self.version = 6789
