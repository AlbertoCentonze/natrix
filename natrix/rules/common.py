from dataclasses import dataclass
from typing import Callable, List

from natrix.ast_tools import VyperASTVisitor


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


class BaseRule(VyperASTVisitor):
    def __init__(self, severity: str, code: str, message: str):
        self.results = []
        self.severity = severity
        self.code = code
        self.message = message
        self.issues = []

    def run(self, compiler_output) -> List[Issue]:
        self.compiler_output = compiler_output
        self.visit(compiler_output["ast"])
        return self.issues

    def add_issue(self, node: dict, *message_args):
        line = node['lineno'],
        character = node['col_offset'],
        # Create an Issue object and append it to issues
        issue = Issue(
            file=self.compiler_output.get('contract_name', 'unknown'),
            position=f"{line}:{character}",
            severity=self.severity,
            code=self.code,
            message=self.message.format(*message_args)
        )
        self.issues.append(issue)