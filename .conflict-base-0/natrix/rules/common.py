from dataclasses import dataclass
from typing import Callable, List, Dict, Type, Any
import inspect
import importlib
import os
import pkgutil
import importlib.util

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
    source_code: str = None
    start_position: tuple = None
    end_position: tuple = None

    def cli_format(self):
        # ANSI color codes
        RED = "\033[31m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        CYAN = "\033[36m"
        BOLD = "\033[1m"
        RESET = "\033[0m"

        # Color the severity based on its level
        severity_color = YELLOW
        if self.severity.lower() == "error":
            severity_color = RED
        elif self.severity.lower() == "important":
            severity_color = RED
        elif self.severity.lower() == "style":
            severity_color = BLUE

        # Format the main error message with colors
        result = (
            f"{BOLD}{self.file}:{self.position}{RESET} "
            f"{severity_color}{self.severity}{RESET} "
            f"{CYAN}{self.code}{RESET}: {self.message}"
        )

        # Add the source code snippet if available
        if self.source_code:
            # Replace the arrow markers with colored ones
            colored_source = self.source_code.replace("-> ", f"{RED}{BOLD}-> {RESET}")
            result += f"\n\n{colored_source}\n"

        return result


class RuleRegistry:
    _rules: Dict[str, Type["BaseRule"]] = {}
    _rule_instances: List[Rule] = None

    @classmethod
    def register(cls, rule_class: Type["BaseRule"]) -> Type["BaseRule"]:
        """Register a rule class"""
        rule_name = rule_class.__name__
        if rule_name.endswith("Rule"):
            rule_name = rule_name[:-4]  # Remove 'Rule' suffix
        cls._rules[rule_name] = rule_class
        return rule_class

    @classmethod
    def get_rule_classes(cls) -> Dict[str, Type["BaseRule"]]:
        """Get all registered rule classes"""
        return cls._rules.copy()

    @classmethod
    def get_rules(cls, rule_configs: Dict[str, Dict[str, Any]] = None) -> List[Rule]:
        """
        Get or create rule instances with the given configurations.
        Rules are discovered and instantiated only once per run.
        """
        # If rules have already been instantiated, return them
        if cls._rule_instances is not None:
            return cls._rule_instances

        # Ensure rules are discovered
        cls.discover_rules()

        # Initialize with empty config if none provided
        if rule_configs is None:
            rule_configs = {}

        # Create rule instances
        cls._rule_instances = []
        for rule_name, rule_class in cls._rules.items():
            # Get the parameters for this rule's __init__ method
            params = {}
            if rule_name in rule_configs:
                # Only pass parameters that the rule's __init__ accepts
                init_signature = inspect.signature(rule_class.__init__)
                valid_params = {
                    param: value
                    for param, value in rule_configs[rule_name].items()
                    if param in init_signature.parameters
                }
                params = valid_params

            # Instantiate the rule with parameters
            try:
                rule_instance = rule_class(**params)
                rule_doc = rule_class.__doc__ or ""
                rule_doc_lines = rule_doc.splitlines()

                # Create the Rule object
                cls._rule_instances.append(
                    Rule(
                        name=rule_doc_lines[0].strip() if rule_doc_lines else rule_name,
                        description="\n".join(
                            line.strip() for line in rule_doc_lines[1:] if line.strip()
                        ),
                        run=rule_instance.run,
                    )
                )
            except Exception as e:
                print(f"Error instantiating rule {rule_name}: {e}")

        return cls._rule_instances

    @classmethod
    def discover_rules(cls, rules_package: str = "natrix.rules"):
        """Discover all rule classes in the given package"""
        # Skip discovery if rules have already been discovered
        if cls._rules:
            return

        # Get the package directory in a way that works without __init__.py
        package_parts = rules_package.split(".")
        base_package = importlib.import_module(package_parts[0])
        base_path = os.path.dirname(base_package.__file__)
        package_path = os.path.join(base_path, *package_parts[1:])

        # Find all Python modules in the package
        for _, module_name, is_pkg in pkgutil.iter_modules([package_path]):
            if is_pkg or module_name == "__init__" or module_name == "common":
                continue

            # Import the module
            module_path = f"{rules_package}.{module_name}"
            try:
                module = importlib.import_module(module_path)

                # Find all classes in the module that are subclasses of BaseRule
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        inspect.isclass(attr)
                        and issubclass(attr, BaseRule)
                        and attr is not BaseRule
                    ):
                        # Register the rule class
                        cls.register(attr)
            except Exception as e:
                print(f"Error importing {module_path}: {e}")

    @classmethod
    def reset(cls):
        """Reset the registry (mainly for testing purposes)"""
        cls._rules = {}
        cls._rule_instances = None


class BaseRule(VyperASTVisitor):
    def __init__(
        self, severity: str = "warning", code: str = None, message: str = None
    ):
        self.results = []
        self.severity = severity
        self.code = code or getattr(
            self.__class__, "CODE", f"NTX{id(self.__class__) % 1000:03d}"
        )
        self.message = message or getattr(
            self.__class__, "MESSAGE", "Generic rule violation"
        )
        self.issues = []
        self.source_code = None
        self.file_path = None

    def run(self, compiler_output) -> List[Issue]:
        self.issues = []  # reset issues for each run
        self.compiler_output = Node(compiler_output)

        # Get the file path from the compiler output
        self.file_path = self.compiler_output.get("contract_name")

        # The source code is loaded only once when needed
        self.source_code = None

        self.visit(Node(compiler_output["ast"]))
        return self.issues

    def _load_source_code(self):
        """Load the source code from the file path if not already loaded."""
        if (
            self.source_code is None
            and self.file_path
            and os.path.exists(self.file_path)
        ):
            try:
                with open(self.file_path, "r") as f:
                    self.source_code = f.read()
            except Exception:
                self.source_code = None
        return self.source_code

    def add_issue(self, node: Node, *message_args):
        line = node.get("lineno")
        character = node.get("col_offset")
        end_line = node.get("end_lineno", line)
        end_character = node.get("end_col_offset", character)

        # Create the position string
        position = f"{line}:{character}"

        # Get the source code snippet if available
        source_snippet = None
        if self._load_source_code():
            try:
                # Split the source code into lines
                lines = self.source_code.splitlines()

                # Get the relevant lines
                context_lines = 1  # Number of lines to show before and after
                start_idx = max(0, line - 1 - context_lines)
                end_idx = min(len(lines), end_line + context_lines)

                # Create the snippet with line numbers
                snippet_lines = []
                for i in range(start_idx, end_idx):
                    line_num = i + 1
                    prefix = (
                        "-> " if line_num >= line and line_num <= end_line else "   "
                    )
                    snippet_lines.append(f"{prefix}{line_num}: {lines[i]}")

                # Add a caret pointing to the error position if it's a single line error
                if line == end_line:
                    caret_line = (
                        "   " + " " * (len(str(line)) + 2) + " " * character + "^"
                    )
                    if end_character > character:
                        caret_line += "~" * (end_character - character - 1)
                    snippet_lines.append(caret_line)

                source_snippet = "\n".join(snippet_lines)
            except Exception:
                # If anything goes wrong, just don't include the source
                pass

        issue = Issue(
            file=self.file_path,
            position=position,
            severity=self.severity,
            code=self.code,
            message=self.message.format(*message_args),
            source_code=source_snippet,
            start_position=(line, character),
            end_position=(end_line, end_character),
        )
        self.issues.append(issue)
