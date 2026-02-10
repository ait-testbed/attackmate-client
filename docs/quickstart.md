# Quick Start

Get started with AttackMate Client in minutes.

## Prerequisites

1. [Installed AttackMate Client](installation.md)
2. Access to an AttackMate API server
3. Valid credentials (username and password)
4. A playbook YAML file

## Execute Your First Playbook

### Basic Example

```bash
uv run attackmate-client playbook.yaml \
  --server-url https://attackmate.example.com:8445 \
  --username admin \
  --password mypassword
```

### With Self-Signed Certificate

```bash
uv run attackmate-client playbook.yaml \
  --server-url https://localhost:8445 \
  --username admin \
  --password adminpass \
  --cacert /path/to/server-ca.crt
```

### With Debug Mode

```bash
uv run attackmate-client playbook.yaml \
  --server-url https://localhost:8445 \
  --username admin \
  --password adminpass \
  --debug
```

## Successful Output

```
--- Playbook Execution (YAML: playbook.yaml) Result ---
Success: True
Message: Playbook executed successfully

--- Final Variable Store State ---
target_ip: 192.168.1.100
```

## Common Issues

| Issue | Solution |
|-------|----------|
| `Authentication failed` | Verify username and password |
| `SSL: CERTIFICATE_VERIFY_FAILED` | Use `--cacert` with CA certificate path |
| `Connection refused` | Check server URL and ensure server is running |
| `Playbook file not found` | Verify file path is correct |

## Next Steps

- [CLI Usage Guide](./cli-overview.md) - Learn all CLI options
- [CLI Examples](./cli-examples.md) - See practical examples
- [Python API](./client.md) - Use in your scripts
