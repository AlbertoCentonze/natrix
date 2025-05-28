import pytest


@pytest.fixture()
def all_contracts(
    fee_splitter_contract,
    scrvusd_oracle_contract,
    snekmate01_ownable_contract,
    twa_contract,
    twocrypto_contract,
    uncached_contract,
    unused_import_contract,
    dummy_version_contract,
):
    # each item maps contract filename to the number of expected issues
    return [
        [fee_splitter_contract, 21],
        [scrvusd_oracle_contract, 47],
        [snekmate01_ownable_contract, 3],
        [twa_contract, 7],
        [twocrypto_contract, 207],
        [uncached_contract, 7],
        [unused_import_contract, 11],
        [dummy_version_contract, 9],
    ]
