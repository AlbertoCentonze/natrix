import textwrap

import pytest

from natrix.rules.dynarray_overallocation import DynArrayOverallocation
from natrix.utils import parse_source_to_ast


def test_int():
    source = textwrap.dedent(
        """
    y: DynArray[uint256, 1234]
    """
    )

    ast = parse_source_to_ast(source)

    rule = DynArrayOverallocation()

    rule(ast)
    assert len(rule.result) == 1
    value, node = rule.result[0]
    assert value == 1234
    assert node.lineno == 2


def test_name():
    source = textwrap.dedent(
        """
    MAX_LENGTH: constant(uint256) = 1234
    y: DynArray[uint256, MAX_LENGTH]
    """
    )
    ast = parse_source_to_ast(source)

    rule = DynArrayOverallocation()

    rule(ast)
    assert len(rule.result) == 1
    value, node = rule.result[0]
    assert value == 1234
    assert node.lineno == 3


def test_multiple():
    source = textwrap.dedent(
        """
    MAX_LENGTH: constant(uint256) = 1234
    y: DynArray[uint256, MAX_LENGTH]
    z: DynArray[uint256, 4321]
    """
    )
    ast = parse_source_to_ast(source)

    rule = DynArrayOverallocation()

    rule(ast)
    assert len(rule.result) == 2
    assert rule.result[0][0] == 1234
    assert rule.result[0][1].lineno == 3
    assert rule.result[1][0] == 4321
    assert rule.result[1][1].lineno == 4


def test_lower_threshold():
    pytest.xfail("Not implemented yet")


def test_no_dynarray():
    pytest.xfail("Not implemented yet")


def test_custom_threshold():
    pytest.xfail("Not implemented yet")
