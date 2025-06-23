# pragma version >=0.4.1

def function_with_unused_arg(_used_arg: uint256, _unused_arg: address) -> uint256:
    return _used_arg * 2

def function_with_all_used_args(_arg1: uint256, _arg2: address) -> uint256:
    if _arg2 == empty(address):
        return _arg1
    return _arg1 + 1

# Interface function - arguments should not be flagged
interface ITest:
    def some_interface_function(_interface_arg: uint256) -> bool: view
