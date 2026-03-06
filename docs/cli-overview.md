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
--- Playbook Execution (YAML: playbook.yml) Result ---
Success: True
Message: Playbook execution finished.

--- Playbook Execution (YAML: playbook.yml) Logs ---
 Attackmate Log:
2026-03-06 10:55:03 INFO - Delay before commands: 0 seconds
2026-03-06 10:55:03 DEBUG - Template-Command: 'whoami'
2026-03-06 10:55:03 INFO - Executing Shell-Command: 'whoami'
2026-03-06 10:55:03 DEBUG - Running non interactive command
2026-03-06 10:55:03 DEBUG - Closing popen process
2026-03-06 10:55:03 DEBUG - loop_if does not match
2026-03-06 10:55:03 DEBUG - loop_if_not does not match
2026-03-06 10:55:03 WARNING - Cleaning up session stores
2026-03-06 10:55:03 WARNING - Cleaning up session stores
Output Log:
2026-03-06 10:55:03 INFO - Command: whoami
ubuntu

Json Log:
{"start-datetime": "2026-03-06T10:55:03.759623", "type": "shell", "cmd": "whoami", "parameters": {"only_if": null, "error_if": null, "error_if_not": null, "loop_if": null, "loop_if_not": null, "loop_count": "3", "exit_on_error": true, "save": null, "background": false, "kill_on_exit": true, "metadata": null, "interactive": false, "creates_session": null, "session": null, "command_timeout": "10", "read": true, "command_shell": "/bin/sh", "bin": false}}

--- Final Variable Store State ---
RESULT_RETURNCODE: '0'
RESULT_STDOUT: 'ubuntu'
```

## Next Steps

- Learn about the [Python API](./client.md) for programmatic access
