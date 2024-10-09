from dataclasses import dataclass
from typing import Callable, List


@dataclass()
class Rule:
    name: str
    description: str
    run: Callable
    # TODO add an id to ignore the rule

@dataclass()
class Issue:
    file: str
    position: str
    severity: str
    code: str
    message: str

class BaseRule:
    def __init__(self, severity: str, code: str, message: str):
        self.results = []
        self.severity = severity
        self.code = code
        self.message = message

    def run(self, ast) -> List[Issue]:
        self.visit(ast)
        self.path = ast.module_node.resolved_path
        # print(help(ast.module_node))

        issues = []

        for raw_issue in self.results:
            line, character, message_args = raw_issue

            issues.append(
                Issue(
                    file=self.path,
                    position="{}:{}".format(line, character),
                    severity=self.severity,
                    code=self.code,
                    message=self.message.format(*message_args),
                )
            )

        return issues

    def visit(self, node, **kwargs):
        for c in node.get_children():
            self.visit(c)

        for class_ in node.__class__.mro():
            ast_type = class_.__name__

            visitor_fn = getattr(self, f"visit_{ast_type}", None)

            if not visitor_fn:
                continue

            issue = visitor_fn(node)

            if issue is None:
                continue

            self.results.append(issue)

        return node
