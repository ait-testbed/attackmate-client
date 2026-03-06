# AttackMate Playbook CLI Client

This is a command-line client for interacting with the AttackMate API server for remotely executing playbooks.
[Client Documentation](https://ait-testbed.github.io/attackmate-client/latest/) on github pages.

**AttackMate** is a framework for automated security testing and attack simulation.
For more information about the AttackMate framework, please visit the [AttackMate repository](https://github.com/ait-testbed/attackmate) and the [ AttackMate api server repository](https://github.com/ait-testbed/attackmate-api-server). Both can be installed with an ansible role:  [AttackMate ansible role] (https://github.com/ait-testbed/attackmate-ansible)

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

Alternatively using pip and virtualenv:

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Use from the Command Line

The main executable command is `attackmate-client`. All commands require authentication credentials (`--username` and `--password`).

### Options

| Option        | Description                                                              |
|---------------|--------------------------------------------------------------------------|
| --server-url  | Base URL of the AttackMate API server (default: https://localhost:8445) |
| --username    | API username for authentication. (required)                              |
| --password    | API password for authentication. (required)                              |
| --cacert      | Path to the server's CA certificate file if using self-signed SSL.       |
| --debug       | Enable server debug logging for the playbook instance.                   |

### Example: Execute a Playbook

This command reads the YAML content from a local file and sends the full content directly to the AttackMate server's `/playbooks/execute/yaml` endpoint for execution.

```bash
uv run attackmate-client </path/to/local_playbook.yaml> --server-url <server-url> --username <user> --password <pass> --cacert </path/to/cert>
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

`RemoteAttackMateClient` is the main client class for interacting with the AttackMate API.

**Constructor:**

```python
RemoteAttackMateClient(
    server_url: str,
    username: str,
    password: SecretStr,
    cacert: Optional[str] = None,
    timeout: Optional[float] = 60.0
)
```

**Parameters:**
- `server_url` (str): Base URL of the AttackMate server (e.g., "https://attackmate.example.com:8445")
- `username` (str): Username for authentication
- `password` (SecretStr): Password for authentication
- `cacert` (Optional[str]): Path to CA certificate file for SSL verification
- `timeout` (Optional[float]): Request timeout in seconds (default: 60.0)

**METHODS:**
####  `execute_remote_playbook_yaml(playbook_yaml_content: str, debug: bool = False)`

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

#### Code Example 1: Basic Playbook Execution

content of playbook.yml:
```yaml
commands:
  - type: shell
    cmd: whoami
```

```python
from attackmate_client import RemoteAttackMateClient
from pydantic import SecretStr
import yaml

# Initialize the client
client = RemoteAttackMateClient(
    server_url="https://attackmate.example.com:8445",
    username="admin",
    password=SecretStr("mypassword"),
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
    print(f"Success: {result.get('success', 'N/A')}")
    print(f"Message: {result.get('message', 'No message.')}")
    print(f" Attackmate Log:\n{result.get('attackmate_log', 'No log available.')}")
    print(f"Output Log:\n{result.get('output_log', 'No output log available.')}")
    print(f"Json Log:\n{result.get('json_log', 'No json log available.')}")

    final_state = result.get('final_state')
    if final_state and final_state.get('variables'):
        print('Final Variable Store State:')
        print(yaml.safe_dump(final_state['variables'], indent=2, default_flow_style=False))
else:
    print("Playbook execution failed!")
```

expected output:
```bash
Playbook executed successfully!
Success: True
Message: Playbook execution finished.
 Attackmate Log:
2026-03-06 11:43:10 INFO - Delay before commands: 0 seconds
2026-03-06 11:43:10 DEBUG - Template-Command: 'whoami'
2026-03-06 11:43:10 INFO - Executing Shell-Command: 'whoami'
2026-03-06 11:43:10 DEBUG - Running non interactive command
2026-03-06 11:43:10 DEBUG - Closing popen process
2026-03-06 11:43:10 DEBUG - loop_if does not match
2026-03-06 11:43:10 DEBUG - loop_if_not does not match
2026-03-06 11:43:10 WARNING - Cleaning up session stores
2026-03-06 11:43:10 WARNING - Cleaning up session stores
Output Log:
2026-03-06 11:43:10 INFO - Command: whoami
ubuntu

Json Log:
{"start-datetime": "2026-03-06T11:43:10.835655", "type": "shell", "cmd": "whoami", "parameters": {"only_if": null, "error_if": null, "error_if_not": null, "loop_if": null, "loop_if_not": null, "loop_count": "3", "exit_on_error": true, "save": null, "background": false, "kill_on_exit": true, "metadata": null, "interactive": false, "creates_session": null, "session": null, "command_timeout": "10", "read": true, "command_shell": "/bin/sh", "bin": false}}
Final Variable Store State:
RESULT_RETURNCODE: '0'
RESULT_STDOUT: 'ubuntu'
```

#### `execute_remote_command(command_pydantic_model, debug: bool = False)`

Executes a single  AttackMate command on the remote serve

**Parameters:**
- `command_pydantic_model`: A Pydantic model instance (e.g., `ShellCommand`) or a `RemoteCommand` representing the command. Must include a `type` field matching a valid remotely executable AttackMate command type.
- `debug` (bool): Enable debug logging on the server (default: `False`)

**Returns:**
- `Dict[str, Any]` on success containing:
  - `success` (bool): Whether execution succeeded
  - `result` (dict): Contains `stdout`, `returncode`, and optionally `error_message`
- `None` on failure

**The dependency problem:** `command_pydantic_model` expects a `RemotelyExecutableCommand` instance — a Pydantic model from the `attackmate` package. However, since `attackmate` is not a dependency of this client, you have two options:

**Option A — Pass a RemoteCommand from the attackmate client package (recommended for standalone use)**

The client accepts a RemoteCommand, use this approach when you do not have `attackmate` installed:
```python
from attackmate_client import RemoteAttackMateClient, RemoteCommand

client = RemoteAttackMateClient(...)

command = RemoteCommand(type="shell", cmd="id")
result = client.execute_remote_command(command, debug=True)
```

**Option B — Pass a Attackmate Command Pydantic model (for use within the AttackMate framework)**

If you are writing scripts that already have `attackmate` installed (e.g., plugins or internal tooling), you can import and instantiate the model directly:
```python
from attackmate_client import RemoteAttackMateClient
from attackmate.schemas.shell import ShellCommand

client = RemoteAttackMateClient(...)

command = ShellCommand(type="shell", cmd="whoami")
result = client.execute_remote_command(command, debug=False)
```

#### Code Example 2: Basic Remote Command Execution
```python
from pydantic import SecretStr
from attackmate_client import RemoteAttackMateClient, RemoteCommand

client = RemoteAttackMateClient(
    server_url="https://attackmate.example.com:8445",
    username="admin",
    password=SecretStr("mypassword"),
    cacert="/path/to/ca-cert.pem"
)

# Pass command as a plain dict — no attackmate dependency needed
command = RemoteCommand(type="shell", cmd="id")
result = client.execute_remote_command(command, debug=True)

if result:
    cmd_result = result.get("result", {})
    if cmd_result.get("success"):
        print("Command succeeded!")
        print(f"Output:\n{cmd_result.get('stdout', '')}")
        print(f"Return code: {cmd_result.get('returncode')}")
    else:
        print(f"Command failed: {cmd_result.get('error_message', 'Unknown error')}")
else:
    print("No response received from server.")
```

**Expected output:**
```
Command succeeded!
Output:
uid=1000(ubuntu) gid=1000(ubuntu) groups=1000(ubuntu)
Return code: 0
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
