from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from natrix.ast_node import Node
from natrix.ast_tools import parse_file


@dataclass
class ModuleInfo:
    """Information about a compiled Vyper module."""

    path: Path
    ast_node: Node
    dependencies: set[Path] = field(default_factory=set)  # Paths this module imports
    dependents: set[Path] = field(default_factory=set)  # Paths that import this module
    compiler_output: dict[str, Any] = field(
        default_factory=dict
    )  # Full compiler output


class ProjectContext:
    """Manages the entire project's dependency graph and module compilation."""

    def __init__(self, initial_files: list[Path], extra_paths: tuple[Path, ...] = ()):
        # Normalize initial files to absolute Path objects
        self.initial_files = [f.resolve() for f in initial_files]
        self.extra_paths = extra_paths
        self.modules: dict[Path, ModuleInfo] = {}
        self.project_root = self._determine_project_root()
        self._build_graph()

    def _determine_project_root(self) -> Path:
        """Determine the project root directory from initial files."""
        if not self.initial_files:
            return Path.cwd()

        # Initial files are already Path objects
        if len(self.initial_files) == 1:
            return self.initial_files[0].parent

        # Find common ancestor
        common_parent = self.initial_files[0].parent
        for p in self.initial_files[1:]:
            while not p.is_relative_to(common_parent):
                common_parent = common_parent.parent

        return common_parent

    def _build_graph(self) -> None:
        """Build the dependency graph for all modules."""
        # Queue of files to process
        to_process: set[Path] = set(self.initial_files)
        processed: set[Path] = set()

        while to_process:
            file_path = to_process.pop()

            # Skip if already processed
            if file_path in processed:
                continue

            processed.add(file_path)

            # Compile the file
            compiler_output = parse_file(file_path, extra_paths=self.extra_paths)

            # Create ModuleInfo
            module_info = ModuleInfo(
                path=file_path,
                ast_node=Node.from_dict(compiler_output["ast"]),
                compiler_output=compiler_output,
            )

            # Store the module
            self.modules[file_path] = module_info

            # Process imports
            for import_info in compiler_output.get("imports", []):
                dep_path = Path(import_info["resolved_path"]).resolve()

                # Add to dependencies
                module_info.dependencies.add(dep_path)

                # Add this file as a dependent of the imported module
                if dep_path in self.modules:
                    self.modules[dep_path].dependents.add(file_path)
                else:
                    # Add to processing queue
                    to_process.add(dep_path)

        # Second pass: Update dependents for all modules
        for module_path, module_info in self.modules.items():
            for dep_path in module_info.dependencies:
                if dep_path in self.modules:
                    self.modules[dep_path].dependents.add(module_path)

    def get_module(self, path: Path) -> ModuleInfo:
        """Retrieve a module by its path."""
        return self.modules[path]

    def get_dependents_of(self, path: Path) -> set[Path]:
        """Get all modules that import the given module."""
        module = self.get_module(path)
        if module:
            return module.dependents.copy()
        return set()

    def get_dependencies_of(self, path: Path) -> set[Path]:
        """Get all modules that the given module imports."""
        module = self.get_module(path)
        if module:
            return module.dependencies.copy()
        return set()

    def get_all_modules(self) -> list[ModuleInfo]:
        """Get all modules."""
        return list(self.modules.values())
