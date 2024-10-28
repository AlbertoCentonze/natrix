a: uint256
b: public(address)

def not_caching_a_thing() -> uint256:
    hey_unused_var: uint256 = 1

    # a: sload
    if self.a == 1:
        print("hello")

    # a: sstore (reset count)
    self.a = 1
    # a: sload
    if self.a == 1:
        self.b = msg.sender
    # a: sload (two sloads in a row means it should have been cached after the sload)
    if self.a == 1:
        self.b = self

    self.b = msg.sender
    return 1
