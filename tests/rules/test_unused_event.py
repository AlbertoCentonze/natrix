from natrix.rules.unused_event import UnusedEventRule


def test_unused_event(test_unused_event_contract):
    """Test detection of unused events."""
    rule = UnusedEventRule()
    ast = test_unused_event_contract
    issues = rule.run(ast)

    # Should detect 3 unused events: Approval, Mint, and Unpaused
    assert len(issues) == 3

    # Check that the correct events are flagged
    unused_events = {issue.message.split("'")[1] for issue in issues}
    assert unused_events == {"Approval", "Mint", "Unpaused"}

    # Verify Transfer and Paused are not flagged (they are used)
    for issue in issues:
        assert "Transfer" not in issue.message
        assert "Paused" not in issue.message


def test_all_events_used():
    """Test when all events are used - should have no issues."""
    source = """
# pragma version >=0.4.0

event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    amount: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    amount: uint256

@external
def transfer(to: address, amount: uint256):
    log Transfer(msg.sender, to, amount)

@external
def approve(spender: address, amount: uint256):
    log Approval(msg.sender, spender, amount)
"""
    from natrix.ast_tools import parse_source

    rule = UnusedEventRule()
    ast = parse_source(source)
    issues = rule.run(ast)

    assert len(issues) == 0


def test_event_without_parameters():
    """Test events without parameters (using pass)."""
    source = """
# pragma version >=0.4.0

event Started: pass
event Stopped: pass
event Paused: pass

@external
def start():
    log Started()

@external
def stop():
    log Stopped()

# Paused is never used
"""
    from natrix.ast_tools import parse_source

    rule = UnusedEventRule()
    ast = parse_source(source)
    issues = rule.run(ast)

    # Only Paused should be flagged as unused
    assert len(issues) == 1
    assert "Paused" in issues[0].message


def test_no_events():
    """Test contract with no events - should have no issues."""
    source = """
# pragma version >=0.4.0

counter: uint256

@external
def increment():
    self.counter += 1
"""
    from natrix.ast_tools import parse_source

    rule = UnusedEventRule()
    ast = parse_source(source)
    issues = rule.run(ast)

    assert len(issues) == 0
