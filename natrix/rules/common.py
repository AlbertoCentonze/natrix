from __future__ import annotations

import importlib
import importlib.util
import inspect
import pkgutil
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from collections.abc import Callable

from natrix.ast_node import Node
from natrix.ast_tools import VyperASTVisitor

if TYPE_CHECKING:
    from natrix.context import ProjectContext


@dataclass(frozen=True)
class Rule:
    name: str
    description: str
    run: Callable


@dataclass(frozen=True)
class Issue:
    file: Path
    position: str
    severity: str
    code: str
    message: str
    source_code: str | None = None
    start_position: tuple[int, int] | None = None
    end_position: tuple[int, int] | None = None

    def cli_format(self) -> str:
        # ANSI color codes
        red = "\033[31m"
        yellow = "\033[33m"
        blue = "\033[34m"
        cyan = "\033[36m"
        bold = "\033[1m"
        reset = "\033[0m"

        # Color the severity based on its level
        severity_color = yellow
        if self.severity.lower() == "error" or self.severity.lower() == "important":
            severity_color = red
        elif self.severity.lower() == "style":
            severity_color = blue

        # Format the main error message with colors
        result = (
            f"{bold}{self.file}:{self.position}{reset} "
            f"{severity_color}{self.severity}{reset} "
            f"{cyan}{self.code}{reset}: {self.message}"
        )

        # Add the source code snippet if available
        if self.source_code:
            # Replace the arrow markers with colored ones
            colored_source = self.source_code.replace("-> ", f"{red}{bold}-> {reset}")
            result += f"\n\n{colored_source}\n"

        return result


class RuleRegistry:
    _rules: ClassVar[dict[str, type[BaseRule]]] = {}
    _rule_instances: ClassVar[list[Rule] | None] = None

    @classmethod
    def register(cls, rule_class: type[BaseRule]) -> type[BaseRule]:
        """Register a rule class"""
        rule_name = rule_class.__name__
        if rule_name.endswith("Rule"):
            rule_name = rule_name[:-4]  # Remove 'Rule' suffix
        cls._rules[rule_name] = rule_class
        return rule_class

    @classmethod
    def get_rule_classes(cls) -> dict[str, type[BaseRule]]:
        """Get all registered rule classes"""
        return cls._rules.copy()

    @classmethod
    def get_rules(
        cls, rule_configs: dict[str, dict[str, Any]] | None = None
    ) -> list[Rule]:
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
    def discover_rules(cls, rules_package: str = "natrix.rules") -> None:
        """Discover all rule classes in the given package"""
        # Skip discovery if rules have already been discovered
        if cls._rules:
            return

        # Get the package directory in a way that works without __init__.py
        package_parts = rules_package.split(".")
        base_package = importlib.import_module(package_parts[0])
        if base_package.__file__ is None:
            return
        base_path = Path(base_package.__file__).parent
        package_path = base_path.joinpath(*package_parts[1:])

        # Find all Python modules in the package and import them
        # This will trigger any @RuleRegistry.register decorators
        for _, module_name, is_pkg in pkgutil.iter_modules([str(package_path)]):
            if is_pkg or module_name == "__init__" or module_name == "common":
                continue

            # Import the module to trigger decorator execution
            module_path = f"{rules_package}.{module_name}"
            try:
                importlib.import_module(module_path)
            except Exception as e:
                print(f"Error importing {module_path}: {e}")

    @classmethod
    def reset(cls) -> None:
        """Reset the registry (mainly for testing purposes)"""
        cls._rules = {}
        cls._rule_instances = None


class BaseRule(VyperASTVisitor):
    def __init__(self, severity: str, code: str, message: str):
        self.results: list[Any] = []
        self.severity = severity
        self.code = code
        self.message = message
        self.issues: list[Issue] = []
        self.source_code: str | None = None
        self.file_path: Path | None = None
        self.context: ProjectContext | None = None

    def run(self, project_context: ProjectContext, file_path: Path) -> list[Issue]:
        self.issues = []  # reset issues for each run
        self.context = project_context
        self.file_path = file_path

        # Get the module info from the context
        module_info = self.context.get_module(file_path)

        self.compiler_output = Node(module_info.compiler_output)

        # The source code is loaded only once when needed
        self.source_code = None

        # Call before_traversal hook if it exists
        if hasattr(self, "before_traversal"):
            self.before_traversal()

        self.visit(module_info.ast_node)

        # Call after_traversal hook if it exists
        if hasattr(self, "after_traversal"):
            self.after_traversal()

        return self.issues

    def _load_source_code(self) -> str | None:
        """Load the source code from the file path if not already loaded."""
        if self.source_code is None and self.file_path and self.file_path.exists():
            try:
                with self.file_path.open() as f:
                    self.source_code = f.read()
            except Exception:
                self.source_code = None
        return self.source_code

    def add_issue(self, node: Node, *message_args: Any) -> None:
        line = node.get("lineno")
        character = node.get("col_offset")
        end_line = node.get("end_lineno", line)
        end_character = node.get("end_col_offset", character)

        # Create the position string
        position = f"{line}:{character}"

        # Get the source code snippet if available
        source_snippet = None
        source_code = self._load_source_code()
        if source_code:
            try:
                # Split the source code into lines
                lines = source_code.splitlines()

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

                    # Add a caret pointing to the error position
                    # immediately after the error line
                    if line == end_line and line_num == line:
                        caret_line = (
                            "   " + " " * (len(str(line)) + 2) + " " * character + "^"
                        )
                        if end_character > character:
                            caret_line += "~" * (end_character - character - 1)
                        snippet_lines.append(caret_line)

                source_snippet = "\n".join(snippet_lines)
            except Exception:  # noqa: S110
                # If anything goes wrong, just don't include the source
                pass

        issue = Issue(
            file=self.file_path or Path("<unknown>"),
            position=position,
            severity=self.severity,
            code=self.code,
            message=self.message.format(*message_args),
            source_code=source_snippet,
            start_position=(line, character),
            end_position=(end_line, end_character),
        )
        self.issues.append(issue)


def _get_staticcall_function_mutability(staticcall_node: Node) -> str | None:
    """
    Extract the mutability (pure/view) of a function being called via staticcall.
    # TODO: does not work for imported interfaces
    Returns:
        "pure" if the interface function is pure
        "view" if the interface function is view
        None if mutability cannot be determined
    """
    try:
        # The staticcall_node.node_dict contains the StaticCall structure
        # Navigate: StaticCall -> value.func (Attribute) -> type.type_decl_node
        value_dict = staticcall_node.node_dict.get("value", {})
        func_dict = value_dict.get("func", {})

        if not func_dict or func_dict.get("ast_type") != "Attribute":
            return None

        # Get the type information which contains the declaration node reference
        type_info = func_dict.get("type", {})
        type_decl_node_info = type_info.get("type_decl_node", {})

        if not type_decl_node_info:
            return None

        # Find the interface function definition in the module
        module_node = staticcall_node.module_node
        if not module_node:
            return None

        # Search for the function definition with matching node_id
        target_node_id = type_decl_node_info.get("node_id")
        if target_node_id is None:
            return None

        # Search through all interface definitions
        for interface_def in module_node.get_descendants(node_type="InterfaceDef"):
            for func_def in interface_def.get_descendants(node_type="FunctionDef"):
                if func_def.node_dict.get("node_id") == target_node_id:
                    # Check the function body for mutability indicators
                    for stmt in func_def.node_dict.get("body", []):
                        if stmt.get("ast_type") == "Expr":
                            value = stmt.get("value", {})
                            if value.get("ast_type") == "Name":
                                name_id: str = value.get("id")
                                if name_id in ["pure", "view"]:
                                    return name_id

        return None
    except Exception:
        # If we can't determine mutability, err on the side of caution
        return None
