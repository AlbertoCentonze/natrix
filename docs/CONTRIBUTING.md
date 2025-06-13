# Documentation Contribution Guidelines

## Adding New Rule Documentation

1. Create a new file in `docs/rules/<rule-name>.md`
2. Use this template:

```markdown
# Rule Name

| Property | Value |
|----------|-------|
| Rule Code | `NTXN` |
| Severity | Warning/Style/Optimization/Important |
| Configuration | `param_name` - Description (default: value) |

## Background
Brief explanation of why this rule exists.

## Purpose
What the rule detects or enforces.

## Example
```vyper
# Non-compliant code
...

# Compliant code
...
```

## Configuration
### pyproject.toml
```toml
[tool.natrix.rule_configs.RuleName]
param = "value"
```

### Command Line
```bash
natrix --rule-config RuleName.param=value
```
```

3. **Important**:
   - Only include the Configuration section if the rule has configurable parameters
   - Do not add arbitrary sections - stick to the template
   - Keep the structure consistent with existing rule documentation

4. Update `docs/rules/index.md` with the new rule entry

5. Add the rule to `mkdocs.yml` navigation:
   ```yaml
   nav:
     - Rules:
       - Rule Name (NTXN): rules/rule-name.md
   ```

6. Update `docs/configuration.md` if the rule has configurable parameters

7. Verify the documentation builds correctly:
   ```bash
   mkdocs build
   ```
