# Documentation Contribution Guidelines

## Testing a rule against a file
- When a rule is being tested against a file in the @tests/contracts folder, the only way to use that file in the test is by using the fixture created in @tests/conftest.py, if you can't find a fixture just create one that uses `parse_file`.
