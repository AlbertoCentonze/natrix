"""Tests for the ProjectContext dependency graph."""

from pathlib import Path

from natrix.context import ProjectContext


def test_no_duplicate_paths_in_dependency_graph():
    """Test that files are not tracked under both relative and absolute paths."""
    # Test with both relative and absolute paths to ensure normalization
    files = [
        Path("tests/contracts/fee_splitter/FeeSplitter.vy"),
        Path("tests/contracts/fee_splitter/ControllerMulticlaim.vy"),
    ]

    ctx = ProjectContext(files)

    # Check that ControllerMulticlaim appears only once
    controller_entries = [
        path for path in ctx.modules if path.name == "ControllerMulticlaim.vy"
    ]
    assert len(controller_entries) == 1, (
        f"Expected 1 ControllerMulticlaim entry, found {len(controller_entries)}: {controller_entries}"
    )

    # Check that all paths are absolute
    for path in ctx.modules:
        assert path.is_absolute(), f"Path {path} is not absolute"


def test_dependency_tracking_with_imports():
    """Test that dependencies and dependents are correctly tracked."""
    # FeeSplitter imports ControllerMulticlaim, so it should be tracked as a dependent
    files = [
        Path("tests/contracts/fee_splitter/FeeSplitter.vy"),
        Path("tests/contracts/fee_splitter/ControllerMulticlaim.vy"),
    ]

    ctx = ProjectContext(files)

    # Find the ControllerMulticlaim module
    controller_path = None
    for path in ctx.modules:
        if path.name == "ControllerMulticlaim.vy":
            controller_path = path
            break

    assert controller_path is not None, "ControllerMulticlaim.vy not found in modules"

    # Find the FeeSplitter module
    fee_splitter_path = None
    for path in ctx.modules:
        if path.name == "FeeSplitter.vy":
            fee_splitter_path = path
            break

    assert fee_splitter_path is not None, "FeeSplitter.vy not found in modules"

    # Check that FeeSplitter depends on ControllerMulticlaim
    fee_splitter_module = ctx.modules[fee_splitter_path]
    assert controller_path in fee_splitter_module.dependencies, (
        f"FeeSplitter should depend on ControllerMulticlaim, but dependencies are: {fee_splitter_module.dependencies}"
    )

    # Check that ControllerMulticlaim has FeeSplitter as a dependent
    controller_module = ctx.modules[controller_path]
    assert fee_splitter_path in controller_module.dependents, (
        f"ControllerMulticlaim should have FeeSplitter as dependent, but dependents are: {controller_module.dependents}"
    )


def test_single_file_processing():
    """Test that processing a single file doesn't create duplicate entries."""
    # Process just ControllerMulticlaim
    files = [Path("tests/contracts/fee_splitter/ControllerMulticlaim.vy")]
    ctx = ProjectContext(files)

    # Check no duplicates
    controller_entries = [
        path for path in ctx.modules if path.name == "ControllerMulticlaim.vy"
    ]
    assert len(controller_entries) == 1, (
        f"Expected 1 ControllerMulticlaim entry, found {len(controller_entries)}"
    )

    # The module should exist with its dependencies
    controller_path = controller_entries[0]
    controller_module = ctx.modules[controller_path]

    # Should have IController and IControllerFactory as dependencies
    dependency_names = [dep.name for dep in controller_module.dependencies]
    assert "IController.vyi" in dependency_names
    assert "IControllerFactory.vyi" in dependency_names


def test_path_normalization_consistency():
    """Test that the same file accessed via different paths results in one entry."""
    # Create context with one file
    files = [Path("tests/contracts/fee_splitter/ControllerMulticlaim.vy")]
    ctx1 = ProjectContext(files)

    # Create context with absolute path to same file
    abs_path = Path("tests/contracts/fee_splitter/ControllerMulticlaim.vy").resolve()
    ctx2 = ProjectContext([abs_path])

    # Both should have the same module keys
    assert set(ctx1.modules.keys()) == set(ctx2.modules.keys()), (
        "Different path formats should result in same module keys"
    )
