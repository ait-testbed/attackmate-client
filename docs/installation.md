# Installation

## Prerequisites

- Python 3.8 or higher
- Git

## Install

### Using uv (Recommended)

```bash
git clone https://github.com/ait-testbed/attackmate-client
cd attackmate-client
uv sync --dev
```

### Using pip

```bash
git clone https://github.com/ait-testbed/attackmate-client
cd attackmate-client
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

## Verify

```bash
# With uv
uv run attackmate-client --help

# With pip (venv activated)
attackmate-client --help
```

## Next Steps

Proceed to the [Quick Start Guide](quickstart.md) to execute your first playbook.
