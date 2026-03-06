# RemoteAttackMateClient API Reference

The `RemoteAttackMateClient` class provides a Python API for interacting with the AttackMate server programmatically.

## Class Overview

```python
from attackmate_client import RemoteAttackMateClient
```

The `RemoteAttackMateClient` handles:

- Authentication and token management
- SSL/TLS certificate verification
- HTTP request lifecycle
- Session management across multiple API calls
- Error handling and logging

## Constructor

### `__init__()`

```python

RemoteAttackMateClient(
    server_url: str,
    username: str,
    password: str,
    cacert: Optional[str] = None,
    timeout: float = 60.0
)
```

Creates a new client instance for communicating with an AttackMate server.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `server_url` | `str` | Yes | - | Base URL of the AttackMate API server (e.g., `"https://attackmate.example.com:8445"`) |
| `username` | `str` | No | `None` | Username for authentication|
| `password` | `SecretStr` | No | `None` | Password for authentication |
| `cacert` | `Optional[str]` | No | `None` | Path to CA certificate file for SSL verification|
| `timeout` | `float` | No | `60.0` | Request timeout in seconds for long-running playbooks. |

#### Example

```python
client = RemoteAttackMateClient(
    server_url="https://attackmate.example.com:8445",
    username="admin",
    password="secure_password",
    cacert="/path/to/ca-cert.pem",
    timeout=120.0  # 2 minutes
)
```

## Methods

### `execute_remote_playbook_yaml()`

Executes a playbook by sending its YAML content to the remote server.

```python
def execute_remote_playbook_yaml(
    self,
    playbook_yaml_content: str,
    debug: bool = False
) -> Optional[Dict[str, Any]]
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `playbook_yaml_content` | `str` | Yes | - | Complete YAML content of the playbook to execute |
| `debug` | `bool` | No | `False` | Enable server-side debug logging for this execution |

#### Returns

- **On success**: `Dict[str, Any]` containing:
  ```python
  {
      "success": bool,           # Execution success status
      "message": str,            # Status or error message
      "final_state": {           # Final execution state
          "variables": dict,     # Variable store after execution
      },
  }
  ```

- **On failure**: `None`

#### Example

```python
with open("playbook.yaml", "r") as f:
    yaml_content = f.read()

result = client.execute_remote_playbook_yaml(
    playbook_yaml_content=yaml_content,
    debug=True
)

if result and result.get("success"):
    print("Playbook executed successfully!")
    variables = result.get("final_state", {}).get("variables", {})
    print(f"Final variables: {variables}")
else:
    print("Playbook execution failed")
```

#### Raises

Does not raise exceptions. Returns `None` on errors. Check logs for details.

---

### `execute_remote_command()`

Executes a single command using a Pydantic model.

```python
def execute_remote_command(
    self,
    command_pydantic_model,
    debug: bool = False
) -> Optional[Dict[str, Any]]
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `command_pydantic_model` | Pydantic Model | Yes | - | Pydantic model instance representing the command to execute |
| `debug` | `bool` | No | `False` | Enable server-side debug logging |

#### Returns

Similar structure to `execute_remote_playbook_yaml()`:

- **On success**: `Dict[str, Any]` with execution results
- **On failure**: `None`

#### Example

```python
from attacmkate import DebugCommand

command = DebugCommand(
    type="debug"
    cmd="hello world",
)

result = client.execute_remote_command(command, debug=False)

if result:
    print(f"Command result: {result.get('message')}")
```

#### Raises

Does not raise exceptions. Returns `None` on errors.

---

## Properties and Internal Methods

The following methods are internal and typically not called directly:

### `_get_session_token()` (Internal)

Retrieves or creates an authentication token. Called automatically by request methods.

### `_login()` (Internal)

Performs authentication and stores the token.

### `_make_authenticated_request()` (Internal)

HTTP request handler. Manages token renewal and error handling.

---

## Session Management

The client maintains session state globally per server URL:

```python
# Token storage is managed automatically
_active_sessions: Dict[Tuple[str, str], str] = {}
```

### How It Works

1. **First request**: Client authenticates and stores token
2. **Subsequent requests**: Client reuses stored token
3. **401 Unauthorized**: Client clears cached token, re-authenticates on next request

---

## Error Handling

The client handles errors gracefully without raising exceptions:

### Common Scenarios

| Scenario | Behavior | Return Value |
|----------|----------|--------------|
| Authentication failure | Logs error | `None` |
| Network error | Logs error | `None` |
| HTTP 4xx/5xx error | Logs status and detail | `None` |
| Token expired (401) | Clears token, logs warning | `None` (will re-auth on retry) |
| Invalid JSON response | Logs decode error | `None` |
| SSL verification failure | Logs error | `None` |


## Logging

The client uses Python's `logging` module. Configure logging to see detailed information:

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now client operations will be logged
client = RemoteAttackMateClient(...)
```

## Complete Example

```python
import logging
from attackmate_client import RemoteAttackMateClient

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize client
client = RemoteAttackMateClient(
    server_url="https://attackmate.example.com:8445",
    username="admin",
    password="secure_password",
    cacert="/etc/ssl/certs/attackmate-ca.crt",
    timeout=180.0
)

# Read playbook
with open("playbook.yaml", "r") as f:
    playbook_yaml = f.read()

# Execute playbook
result = client.execute_remote_playbook_yaml(
    playbook_yaml_content=playbook_yaml,
    debug=True
)

# Handle result
if not result:
    print("ERROR: Request failed")
    exit(1)

if result.get("success"):
    print(f"Success: {result.get('message')}")

    # Access final state
    final_state = result.get("final_state", {})
    variables = final_state.get("variables", {})

    print("\nFinal Variables:")
    for key, value in variables.items():
        print(f"  {key}: {value}")
else:
    print(f"Failed: {result.get('message')}")
    exit(1)
```
