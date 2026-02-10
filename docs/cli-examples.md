# CLI Examples

This page provides practical examples of using the `attackmate-client` CLI in various scenarios.

## Basic Examples

### Simple Execution

Execute a playbook with minimal options:

```bash
uv run attackmate-client playbook.yaml \
  --username admin \
  --password adminpass
```

### Custom Server

Connect to a specific AttackMate server:

```bash
uv run attackmate-client playbook.yaml \
  --server-url https://attackmate.example.com:8445 \
  --username testuser \
  --password testpass
```

### Self-Signed Certificate

Execute with a self-signed SSL certificate:

```bash
uv run attackmate-client playbook.yaml \
  --username admin \
  --password adminpass \
  --cacert /etc/ssl/certs/attackmate-ca.crt
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
uv run attackmate-client playbook.yaml \
  --username admin \
  --password adminpass \
  --debug
```

## Tips and Tricks

### Credential File (Simple)

Create a credentials file `~/.attackmate/credentials`:

```bash
ATTACKMATE_SERVER="https://attackmate.example.com:8445"
ATTACKMATE_USER="your_username"
ATTACKMATE_PASS="your_password"
ATTACKMATE_CACERT="/etc/ssl/certs/attackmate-ca.crt"
```

Source it before running:

```bash
source ~/.attackmate/credentials

uv run attackmate-client playbook.yaml \
    --server-url "$ATTACKMATE_SERVER" \
    --username "$ATTACKMATE_USER" \
    --password "$ATTACKMATE_PASS" \
    --cacert "$ATTACKMATE_CACERT"
```

## Next Steps

- Learn about the [Python API](./client.md) for programmatic access
