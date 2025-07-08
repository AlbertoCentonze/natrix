# pragma version >=0.4.0

# This constant is used by consumer.vy, so it should NOT be flagged.
USED_CONSTANT: constant(uint256) = 100

# This constant is used only within this file, so it should NOT be flagged.
LOCALLY_USED_CONSTANT: constant(uint256) = 200

# This constant is never used anywhere, so it SHOULD be flagged.
TRULY_UNUSED_CONSTANT: constant(uint256) = 300

# This constant is used but only through module1.module2.NESTED_USED_CONSTANT
NESTED_USED_CONSTANT: constant(uint256) = 400

# This constant is used but only through alias1.module2.NESTED_USED_CONSTANT
NESTED_ALIASED_USED_CONSTANT: constant(uint256) = 600

# This constant is used but only through alias1.alias2.NESTED_DOUBLE_ALIASED_USED_CONSTANT
NESTED_DOUBLE_ALIASED_USED_CONSTANT: constant(uint256) = 500

my_var: uint256

@deploy
def __init__():
    self.my_var = LOCALLY_USED_CONSTANT
