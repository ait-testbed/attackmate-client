# AttackMate Playbook CLI Client

This is a command-line client for interacting with the AttackMate API server for remotely executing playbooks.

## Installation

Clone the repository:
```bash
git clone [https://github.com/ait-testbed/attackmate-client](https://github.com/ait-testbed/attackmate-client)
cd attackmate-client
```

With uv (recommended):

```bash
uv sync --dev
```

Using pip and virtualenv:
```
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage

The main executable command is attackmate-client. All commands require authentication credentials (--username and --password).

Common Options

| Option    | Description |
| ----------- | ----------- |
| --server-url      | Base URL of the AttackMate API server      |
| --username   | API username for authentication. (Required)        |
| --password      | API password for authentication. (Required)       |
| --cacert | Path to the server's CA certificate file if using self-signed SSL.        |
| --debug     | Enable server debug logging for the playbook instance.      |


## Example: Execute a Playbook

This command reads the YAML content from a local file and sends the full content directly to the AttackMate server's /playbooks/execute/yaml endpoint for execution.

```bash
uv run attackmate-client  /path/to/local_playbook.yaml --username <user> --password <pass> --cacert /path/to/cert
```

## Use in scripts
The core functionality of the client is exposed through the RemoteAttackMateClient class, allowing you to integrate remote playbook execution into other Python scripts.

The client is responsible for reading the local playbook file, authenticating with the remote server, and sending the content via HTTPS.

## Docs

The AttackMate API server is built using FastAPI, which automatically generates interactive documentation for all available endpoints.

You can access the full API documentation by navigating to the following paths on your running server:

| Documentation Type |	Endpoint
| Swagger UI (Interactive Docs) |	https://<server-url>:<port>/docs
| ReDoc (Alternative Static Docs) |	https://<server-url>:<port>/redoc

## License
This project is licensed under EUPL-1.2
