# CLI Overview

The `attackmate-client` command executes playbooks on a remote AttackMate server.

## Basic Usage

```bash
attackmate-client PLAYBOOK_FILE [OPTIONS]
```

## Required Options

| Option | Description |
|--------|-------------|
| `PLAYBOOK_FILE` | Path to your playbook YAML file |
| `--username` | API username for authentication |
| `--password` | API password for authentication |

## Optional Parameters

| Option | Default | Description |
|--------|---------|-------------|
| `--server-url` | `https://localhost:8445` | Base URL of the AttackMate API server |
| `--cacert` | - | Path to CA certificate for self-signed SSL |
| `--debug` | - | Enable server-side debug logging |

## Examples

### Basic Execution

```bash
attackmate-client playbook.yaml \
  --username admin \
  --password mypass
```

### Complete Example

```bash
attackmate-client playbook.yaml \
  --server-url https://attackmate.example.com:8445 \
  --username admin \
  --password mypass \
  --cacert /etc/ssl/certs/attackmate-ca.pem \
  --debug
```

### With uv

```bash
uv run attackmate-client playbook.yaml \
  --username admin \
  --password mypass
```

## Environment Variables

Use environment variables to avoid typing credentials:

```bash
export ATTACKMATE_USER="admin"
export ATTACKMATE_PASS="mypass"
export ATTACKMATE_SERVER="https://attackmate.example.com:8445"

attackmate-client playbook.yaml \
  --username "$ATTACKMATE_USER" \
  --password "$ATTACKMATE_PASS" \
  --server-url "$ATTACKMATE_SERVER"
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Failure (auth, network, or playbook error) |

## Output Format

```
--- Playbook Execution (YAML: playbook.yaml) Result ---
Success: True
Message: Playbook executed successfully

--- Final Variable Store State ---
variable1: value1
variable2: value2
```

## Next Steps

- See [CLI Examples](examples.md) for practical use cases
