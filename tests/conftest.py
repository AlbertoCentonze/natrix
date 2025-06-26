import pytest

from natrix import parse_file


def output_loader(contract_name):
    return parse_file(f"tests/contracts/{contract_name}.vy")


@pytest.fixture
def fee_splitter_contract():
    return output_loader("fee_splitter/FeeSplitter")


@pytest.fixture
def dummy_version_contract():
    return output_loader("version_dummy")


@pytest.fixture
def uncached_contract():
    return output_loader("uncached")


@pytest.fixture
def snekmate01_ownable_contract():
    return output_loader("ownable")


@pytest.fixture
def twa_contract():
    return output_loader("TWA")


@pytest.fixture
def unused_import_contract():
    return output_loader("unused_import")


@pytest.fixture
def scrvusd_oracle_contract():
    return output_loader("scrvusd_oracle/scrvusd_oracle")


@pytest.fixture
def twocrypto_contract():
    return output_loader("Twocrypto")


@pytest.fixture
def for_loop_underscore_contract():
    return output_loader("for_loop_underscore")


@pytest.fixture
def test_unused_arg_contract():
    return output_loader("test_unused_arg")
