import json

import pytest


@pytest.fixture()
def fee_splitter_contract():
    with open("tests/contracts/fee_splitter/ast.json") as ast_raw:
        ast = json.load(ast_raw)

    with open("tests/contracts/fee_splitter/metadata.json") as metadata_raw:
        metadata = json.load(metadata_raw)

    ast["metadata"] = metadata

    return ast


@pytest.fixture()
def dummy_version_contract():
    with open("tests/contracts/version_dummy/ast.json") as ast_raw:
        ast = json.load(ast_raw)

    with open("tests/contracts/version_dummy/metadata.json") as metadata_raw:
        metadata = json.load(metadata_raw)

    ast["metadata"] = metadata

    return ast
