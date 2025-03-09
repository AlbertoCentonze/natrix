owner: public(immutable(address))
a: uint256
b: public(address)
c: address

@deploy
def __init__(_owner: address):
    owner = _owner

def not_caching_a_thing() -> uint256:
    hey_unused_var: uint256 = 1
    another_unused_var: address = empty(address)
    used_var: uint256 = 1234

    # a: sload
    if self.a == 1:
        print("hello")

    if used_var == 1234:
        print("world")

    # still unused
    another_unused_var = msg.sender
    hey_unused_var += 12

    # a: sstore (reset count)
    self.c = self.b
    self.a += 1
    # a: sload
    if self.a == 1:
        self.b = msg.sender
    # a: sload (two sloads in a row means it should have been cached after the sload)
    if self.a == 1:
        self.b = self

    self.b = msg.sender
    if self.c == empty(address):
        self.c = msg.sender
    return 1

def cross_function_not_cached():
    if self.c == empty(address):
        self.c = msg.sender
