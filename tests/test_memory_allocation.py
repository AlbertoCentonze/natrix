import json

import pytest

from natrix.rules import MemoryExpansionRule


@pytest.fixture()
def fee_splitter_contract():
    with open("tests/contracts/ast.json") as ast_raw:
        ast = json.load(ast_raw)

    with open("tests/contracts/metadata.json") as metadata_raw:
        metadata = json.load(metadata_raw)

    ast["metadata"] = metadata
    print(ast)
    return ast


def test_foo(fee_splitter_contract):
    rule = MemoryExpansionRule()

    issues = rule.run(fee_splitter_contract)
    assert len(issues) == 1
    assert issues[0].position == "158:0"
    assert issues[0].file == "contracts/FeeSplitter.vy"

