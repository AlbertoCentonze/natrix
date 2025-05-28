# pragma version 0.4.1

@external
def test_for_loop_underscore():
    # For loop with unused variable - should be reported
    for i: uint256 in range(5):
        pass

    # For loop with underscore variable - should NOT be reported
    for _: uint256 in range(5):
        pass

    # For loop with used variable - should NOT be reported
    for j: uint256 in range(5):
        x: uint256 = j

    # Regular unused variable - should be reported
    unused_var: uint256 = 42
