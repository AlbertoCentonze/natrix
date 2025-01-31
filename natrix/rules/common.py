from dataclasses import dataclass
from typing import Callable, List

from natrix.ast_node import Node
from natrix.ast_tools import VyperASTVisitor


@dataclass(frozen=True)
class Rule:
    name: str
    description: str
    run: Callable


@dataclass(frozen=True)
class Issue:
    file: str
    position: str
    severity: str
    code: str
    message: str

    def cli_format(self):
        return (
            f"{self.file}:{self.position} {self.severity} {self.code}: {self.message}"
        )


class BaseRule(VyperASTVisitor):
    def __init__(self, severity: str, code: str, message: str):
        self.results = []
        self.severity = severity
        self.code = code
        self.message = message
        self.issues = []

    def run(self, compiler_output) -> List[Issue]:
        self.issues = []  # reset issues for each run
        self.compiler_output = Node(compiler_output)
        self.visit(Node(compiler_output["ast"]))
        return self.issues

    def add_issue(self, node: Node, *message_args):
        line = node.get("lineno")
        character = node.get("col_offset")

        issue = Issue(
            file=self.compiler_output.get("contract_name"),
            position=f"{line}:{character}",
            severity=self.severity,
            code=self.code,
            message=self.message.format(*message_args),
        )
        self.issues.append(issue)
