# Test contract for unused argument rule
def example_function(used_arg: uint256, _unused_arg: uint256) -> uint256:
    return used_arg
