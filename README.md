# AttackMate Playbook CLI Client

This is a command-line client for interacting with the AttackMate API server for remotely executing playbooks.
[Client Documentation[(https://ait-testbed.github.io/attackmate-client/latest/) on github pages.

**AttackMate** is a framework for automated security testing and attack simulation. For more information about the AttackMate framework, please visit the [main AttackMate repository](https://github.com/ait-testbed/attackmate) and the [ AttackMate api  server](https://github.com/ait-testbed/attackmate-api-server)

## Client Installation

Clone the repository:

```bash
git clone https://github.com/ait-testbed/attackmate-client
cd attackmate-client
```

With uv (recommended):

```bash
uv sync --dev
```

Using pip and virtualenv:

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage

The main executable command is `attackmate-client`. All commands require authentication credentials (`--username` and `--password`).

### Common Options

| Option        | Description                                                              |
|---------------|--------------------------------------------------------------------------|
| --server-url  | Base URL of the AttackMate API server (default: https://localhost:8445) |
| --username    | API username for authentication. (Required)                              |
| --password    | API password for authentication. (Required)                              |
| --cacert      | Path to the server's CA certificate file if using self-signed SSL.       |
| --debug       | Enable server debug logging for the playbook instance.                   |

### Example: Execute a Playbook

This command reads the YAML content from a local file and sends the full content directly to the AttackMate server's `/playbooks/execute/yaml` endpoint for execution.

```bash
uv run attackmate-client /path/to/local_playbook.yaml --server-url <server-url> --username <user> --password <pass> --cacert </path/to/cert>
```

**Example with real values:**

```bash
uv run attackmate-client playbooks/example.yaml \
  --server-url https://attackmate.example.com:8445 \
  --username admin \
  --password mypassword \
  --cacert certs/server-ca.crt \
  --debug
```

## Use in Scripts

The core functionality of the client is exposed through the `RemoteAttackMateClient` class, allowing you to integrate remote playbook execution into other Python scripts or automation workflows.

### API Reference

#### `RemoteAttackMateClient`

The main client class for interacting with the AttackMate API.

**Constructor:**

```python
RemoteAttackMateClient(
    server_url: str,
    username: str,
    password: SecretStr,
    cacert: Optional[str] = None,
    timeout: float = 60.0
)
```

**Parameters:**
- `server_url` (str): Base URL of the AttackMate server (e.g., "https://attackmate.example.com:8445")
- `username` (str): Username for authentication
- `password` (SecretStr): Password for authentication
- `cacert` (Optional[str]): Path to CA certificate file for SSL verification
- `timeout` (float): Request timeout in seconds (default: 60.0)

#### Available Methods

##### `execute_remote_playbook_yaml(playbook_yaml_content: str, debug: bool = False)`

Executes a playbook by sending its YAML content to the remote server.

**Parameters:**
- `playbook_yaml_content` (str): The complete YAML content of the playbook
- `debug` (bool): Enable debug logging on the server (default: False)

**Returns:**
- `Dict[str, Any]` on success containing:
  - `success` (bool): Whether execution succeeded
  - `message` (str): Status message
  - `final_state` (dict): Final state including variables
  - `instance_id` (str):  remote attackmate instance id
  - `attackmate_log` (str): attackmate log of remote instance
  - `output_log` (str): output log of remote instance
  - `json_log` (str): Json log of remote instance
- `None` on failure

##### `execute_remote_command(command_pydantic_model, debug: bool = False)`

Executes a single command using a Pydantic model.

**Parameters:**
- `command_pydantic_model`: Pydantic model instance representing the command
- `debug` (bool): Enable debug logging on the server (default: False)

**Returns:**
- `Dict[str, Any]` on success with execution results
- `None` on failure

### Code Examples

#### Example 1: Basic Playbook Execution

```python
from attackmate_client import RemoteAttackMateClient

# Initialize the client
client = RemoteAttackMateClient(
    server_url="https://attackmate.example.com:8445",
    username="admin",
    password="mypassword",
    cacert="/path/to/ca-cert.pem"
)

# Read playbook from file
with open("my_playbook.yaml", "r") as f:
    playbook_content = f.read()

# Execute the playbook
result = client.execute_remote_playbook_yaml(
    playbook_yaml_content=playbook_content,
    debug=True
)

# Check results
if result and result.get("success"):
    print("Playbook executed successfully!")
    print(f"Message: {result.get('message')}")

    # Access final state variables
    final_state = result.get("final_state", {})
    variables = final_state.get("variables", {})
    print(f"Final variables: {variables}")
else:
    print("Playbook execution failed!")
```

#### Example 2: Error Handling

```python
from attackmate_client import RemoteAttackMateClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

client = RemoteAttackMateClient(
    server_url="https://attackmate.example.com:8445",
    username="admin",
    password="mypassword",
    cacert="/path/to/self-signed-ca.crt"
)

try:
    with open("playbook.yaml", "r") as f:
        yaml_content = f.read()

    result = client.execute_remote_playbook_yaml(yaml_content)

    if not result:
        print("ERROR: No result returned from server")
        exit(1)

    if not result.get("success"):
        print(f"Playbook failed: {result.get('message')}")
        exit(1)

    print("Success!")

except FileNotFoundError:
    print("ERROR: Playbook file not found")
    exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    exit(1)
```

### Session Management

The client handles authentication tokens automatically:
- Tokens are cached per server URL in memory
- Automatic login when credentials are provided
- Token renewal is handled transparently
- Sessions are maintained across multiple API calls within the same process

## Documentation
Full documentation for the AttackMate framework and API server is available at:

#### Attackmate
- **GitHub Pages:** [https://ait-testbed.github.io/attackmate](https://ait-testbed.github.io/attackmate)
- **Main Repository:** [https://github.com/ait-testbed/attackmate](https://github.com/ait-testbed/attackmate)

#### Attackmate Api Server
- **Main Repository:** [https://github.com/ait-testbed/attackmate-api-server](https://github.com/ait-testbed/attackmate-api-server)


## License

This project is licensed under EUPL-1.2
