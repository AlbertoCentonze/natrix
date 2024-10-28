import json

import pytest


def output_loader(contract_name):
    with open(f"tests/contracts/{contract_name}/ast.json") as output_raw:
        ast = json.load(output_raw)

    with open(f"tests/contracts/{contract_name}/metadata.json") as metadata_raw:
        metadata = json.load(metadata_raw)

    ast["metadata"] = metadata

    return ast


@pytest.fixture()
def fee_splitter_contract():
    return output_loader("fee_splitter")


@pytest.fixture()
def dummy_version_contract():
    return output_loader("version_dummy")


@pytest.fixture()
def uncached_contract():
    return output_loader("uncached")
