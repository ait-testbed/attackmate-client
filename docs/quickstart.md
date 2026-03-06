# Quick Start

## Prerequisites

1. [Installed AttackMate Client](installation.md)
2. Access to an AttackMate API server
3. Valid credentials (username and password)
4. A playbook YAML file

## Execute Your First Playbook

### Basic Example with self-Signed Certificate

```bash
uv run attackmate-client playbook.yaml \
  --server-url https://localhost:8445 \
  --username admin \
  --password adminpass \
  --cacert /path/to/server-ca.crt
```

minimal content for playbook.yml:
```yaml
commands:
  - type: shell
    cmd: whoami
```
## Successful Output

```
--- Playbook Execution (YAML: playbook.yaml) Result ---
Success: True
Message: Playbook execution finished

--- Final Variable Store State ---
RESULT_RETURNCODE: '0'
RESULT_STDOUT:  'ubuntu'
```

## Common Issues

| Issue | Solution |
|-------|----------|
| `Authentication failed` | Verify username and password |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Use `--cacert` with CA certificate path |
| `Connection refused` | Check server URL and ensure server is running |
| `Playbook file not found` | Verify file path is correct |

## Next Steps

- [CLI Usage Guide](./cli-overview.md) -  CLI options
- [Python API](./client.md) - Use in scripts
