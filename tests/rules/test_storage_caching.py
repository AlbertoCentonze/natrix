from natrix.rules.storage_caching import CacheStorageVariableRule


def test_storage_caching(uncached_contract):
    rule = CacheStorageVariableRule()

    issues = rule.run(uncached_contract)
    assert len(issues) == 1
    assert issues[0].position == "28:7"
    assert (
        issues[0].message
        == "Storage variable 'a' is accessed multiple times; consider caching it to save gas."
    )
