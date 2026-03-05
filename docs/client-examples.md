# API Code Examples

This page provides comprehensive code examples for integrating the `RemoteAttackMateClient` into your Python applications.

## Basic Usage

### Simple Playbook Execution With Self-Signed Certificate

```python
from attackmate_client import RemoteAttackMateClient

# Initialize the client
client = RemoteAttackMateClient(
    server_url="https://localhost:8445",
    username="admin",
    password="adminpass",
    cacert="/path/to/self-signed-ca.crt"
)

# Read and execute playbook
with open("playbook.yaml", "r") as f:
    playbook_content = f.read()

result = client.execute_remote_playbook_yaml(playbook_content)

# Check results
if result and result.get("success"):
    print("✓ Playbook executed successfully!")
else:
    print("✗ Playbook execution failed")
```

## Error Handling Patterns

### Basic Error Handling

```python
from attackmate_client import RemoteAttackMateClient
import sys

client = RemoteAttackMateClient(
    server_url="https://attackmate.example.com:8445",
    username="admin",
    password="password"
)

try:
    with open("playbook.yaml", "r") as f:
        yaml_content = f.read()
except FileNotFoundError:
    print("ERROR: Playbook file not found")
    sys.exit(1)
except IOError as e:
    print(f"ERROR: Cannot read playbook: {e}")
    sys.exit(1)

result = client.execute_remote_playbook_yaml(yaml_content)

if not result:
    print("ERROR: No result returned from server (auth/network failure)")
    sys.exit(1)

if not result.get("success"):
    print(f"ERROR: Playbook failed: {result.get('message')}")
    sys.exit(1)

print("SUCCESS: Playbook completed")
```
