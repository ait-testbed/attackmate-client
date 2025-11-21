# AttackMate Playbook CLI Client

This is a focused command-line client for interacting with the AttackMate API server, specifically designed for remotely executing playbooks and checking instance state.

## Installation

Clone the repository:
```bash
git clone [https://github.com/YourRepo/attackmate-client.git](https://github.com/YourRepo/attackmate-client.git)
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
| --server-url      | Base URL of the AttackMate API server (default: https://localhost:8445).       |
| --username   | API username for authentication. (Required)        |
| --password      | API password for authentication. (Required)       |
| --cacert | Path to the server's CA certificate file if using self-signed SSL.        |
| --debug     | (Playbook modes only) Enable server debug logging for the playbook instance.      |


# Example: Execute a Playbook by Sending Local YAML Content

This command reads the YAML content from a local file and sends the full content directly to the AttackMate server's /playbooks/execute/yaml endpoint for immediate execution.

```bash
attackmate-client playbook-yaml /path/to/my_local_scenario.yaml --username <user> --password <pass>
```