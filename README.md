# AttackMate Playbook CLI Client

This is a command-line client for interacting with the AttackMate API serverfor remotely executing playbooks.

## Installation

Clone the repository:
```bash
git clone [https://github.com/ait-testbed/attackmate-client](https://github.com/ait-testbed/attackmate-client)
cd attackmate-client
```

Install the client:

```bash
pip install .
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


# Example: Execute a Playbook

This command reads the YAML content from a local file and sends the full content directly to the AttackMate server's /playbooks/execute/yaml endpoint for execution.

```bash
attackmate-client  /path/to/local_playbook.yaml --username <user> --password <pass> --cacert /path/to/cert
```