from natrix.rules.common import BaseRule
from dpath import get


class ConstantNamingRule(BaseRule):
    def __init__(self, max_frame_size=20_000):
        super().__init__(
            severity="style",
            code="NTX002",
            message="Constant '{}' should be named in UPPER_SNAKE_CASE",
        )
        self.max_frame_size = max_frame_size

    def visit_VariableDecl(self, node):
        if not get(node, "is_constant"):
            return

        var_name = get(node, "target/id")

        if not var_name.isupper():
            self.add_issue(node, var_name)
