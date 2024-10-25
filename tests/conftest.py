import json

import pytest


@pytest.fixture()
def fee_splitter_contract():
    with open("tests/contracts/ast.json") as ast_raw:
        ast = json.load(ast_raw)

    with open("tests/contracts/metadata.json") as metadata_raw:
        metadata = json.load(metadata_raw)

    ast["metadata"] = metadata
    return ast
