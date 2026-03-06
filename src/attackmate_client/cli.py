"""
Command-line interface for executing AttackMate playbooks against a remote API.

Usage:
    python cli.py <playbook_file> --username USER --password PASS [options]
"""

import argparse
import logging
import os
import sys
from typing import Any, Dict, Optional

import yaml
from pydantic import SecretStr

from attackmate_client import RemoteAttackMateClient

logger = logging.getLogger('playbook')


def print_result(result_data: Optional[Dict[str, Any]], action: str) -> None:
    """Prints a structured summary of the API result and exits on failure."""
    if not result_data:
        logger.error(f'{action} failed. See logs above for details.')
        sys.exit(1)

    print(f'\n--- {action} Result ---')
    print(f"Success: {result_data.get('success', 'N/A')}")
    print(f"Message: {result_data.get('message', 'No message.')}")
    print(f'\n--- {action} Logs ---')
    print(f" Attackmate Log:\n{result_data.get('attackmate_log', 'No log available.')}")
    print(f"Output Log:\n{result_data.get('output_log', 'No output log available.')}")
    print(f"Json Log:\n{result_data.get('json_log', 'No json log available.')}")

    final_state = result_data.get('final_state')
    if final_state and final_state.get('variables'):
        print('\n--- Final Variable Store State ---')
        print(yaml.safe_dump(final_state['variables'], indent=2, default_flow_style=False))

    if not result_data.get('success'):
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='AttackMate Playbook Client for Remote API Execution'
    )
    parser.add_argument(
        'playbook_file',
        help='Path to the local playbook YAML file to execute.',
    )
    parser.add_argument(
        '--server-url',
        default='https://localhost:8445',
        help='Base URL of the AttackMate API server (default: https://localhost:8445)',
    )
    parser.add_argument('--username', required=True, help='API username for authentication.')
    parser.add_argument('--password', required=True, help='API password for authentication.')
    parser.add_argument(
        '--cacert',
        help="Path to the server's self-signed certificate file for verification.",
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable server debug logging for this execution.',
    )
    return parser


def main() -> None:
    """Main entry point for the attackmate-client CLI."""
    parser = build_parser()
    args = parser.parse_args()

    if not os.path.exists(args.playbook_file):
        logger.error(f'Local playbook file not found: {args.playbook_file}')
        sys.exit(1)

    client = RemoteAttackMateClient(
        server_url=args.server_url,
        username=args.username,
        password=SecretStr(args.password),
        cacert=args.cacert,
    )

    try:
        with open(args.playbook_file, 'r') as f:
            yaml_content = f.read()
        result = client.execute_remote_playbook_yaml(yaml_content, args.debug)
        print_result(result, f'Playbook Execution (YAML: {args.playbook_file})')
    except IOError as e:
        logger.error(f'Failed to read file: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
