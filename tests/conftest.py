import json

import pytest

from natrix import parse_file


def output_loader_old(contract_name):
    with open(f"tests/contracts/{contract_name}/ast.json") as output_raw:
        ast = json.load(output_raw)

    with open(f"tests/contracts/{contract_name}/metadata.json") as metadata_raw:
        metadata = json.load(metadata_raw)

    ast["metadata"] = metadata

    compiler_output = ast

    return compiler_output


def output_loader(contract_name):
    return parse_file(f"tests/contracts/{contract_name}.vy")


@pytest.fixture()
def fee_splitter_contract():
    return output_loader_old("fee_splitter")


@pytest.fixture()
def dummy_version_contract():
    return output_loader("version_dummy")


@pytest.fixture()
def uncached_contract():
    return output_loader("uncached")


@pytest.fixture()
def snekmate01_ownable_contract():
    return output_loader("ownable")


@pytest.fixture()
def twa_contract():
    return output_loader("TWA")


@pytest.fixture()
def unused_import_contract():
    return output_loader("unused_import")
