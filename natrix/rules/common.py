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

    def cli_format(self):
        return (
            f"{self.file}:{self.position} {self.severity} {self.code}: {self.message}"
        )


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
