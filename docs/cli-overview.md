# CLI Overview

The `attackmate-client` command executes playbooks on a remote AttackMate server.

## Basic Usage

```bash
attackmate-client PLAYBOOK_FILE [OPTIONS]
```

## Required Options

| Option | Description |
|--------|-------------|
| `PLAYBOOK_FILE` | Path to your attackmate playbook YAML file |
| `--username` | API username for authentication |
| `--password` | API password for authentication |
| `--cacert` | Path to CA certificate for self-signed SSL |

## Optional Parameters

| Option | Default | Description |
|--------|---------|-------------|
| `--server-url` | `https://localhost:8445` | Base URL of the AttackMate API server |
| `--debug` | - | False |

## Examples

Execute an attackmate playbook on a remote server (self signed certificate):

```bash
attackmate-client playbook.yaml \
  --server-url https://attackmate.example.com:8445 \
  --username admin \
  --password mypass \
  --cacert /etc/ssl/certs/attackmate-ca.pem
```

### With uv

```bash
uv run attackmate-client playbook.yaml \
  --server-url https://attackmate.example.com:8445 \
  --username admin \
  --password mypass \
  --cacert /etc/ssl/certs/attackmate-ca.pem
```
### Debug Mode

Enable debug logging (on the server):

```bash
uv run attackmate-client playbook.yaml \
  --server-url https://attackmate.example.com:8445 \
  --username admin \
  --password adminpass \
  --cacert /etc/ssl/certs/attackmate-ca.crt \
  --debug
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
Message: Playbook execution finished.

--- Final Variable Store State ---
variable1: value1
variable2: value2
```

## Next Steps

- Learn about the [Python API](./client.md) for programmatic access
