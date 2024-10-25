from dataclasses import dataclass
from typing import Callable, List

from natrix.ast_tools import VyperASTVisitor
from dpath import get


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
        self.compiler_output = compiler_output
        self.visit(compiler_output["ast"])
        return self.issues

    def add_issue(self, node: dict, *message_args):
        line = node["lineno"]
        character = node["col_offset"]

        issue = Issue(
            file=get(self.compiler_output, "contract_name"),
            position=f"{line}:{character}",
            severity=self.severity,
            code=self.code,
            message=self.message.format(*message_args),
        )
        self.issues.append(issue)
