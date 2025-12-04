import argparse
import logging
import os
import sys
import json
from typing import Dict, Any, Optional, Tuple

import httpx
import yaml

logger = logging.getLogger('playbook')

# Global cache for active sessions (token storage)
_active_sessions: Dict[str, Dict[str, str]] = {}
DEFAULT_TIMEOUT = 60.0


class RemoteAttackMateClient:
    """
    Client to interact with a remote AttackMate REST API.
    Handles authentication and token management internally per server URL.
    """

    def __init__(
        self,
        server_url: str,
        cacert: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password

        self.timeout_config, self.verify_ssl = self._configure_http_settings(cacert, timeout)

        logger.debug(f'RemoteClient initialized for {self.server_url}')

    def _configure_http_settings(self, cacert: Optional[str], timeout: float) -> Tuple[httpx.Timeout, Any]:
        """Configures SSL verification and request timeout."""
        timeout_config = httpx.Timeout(10.0, connect=5.0, read=timeout)

        verify_ssl: Any = True  # Default to system CAs
        if cacert:
            if os.path.exists(cacert):
                verify_ssl = cacert
                logger.info(f'Client will verify {self.server_url} SSL using CA: {cacert}')
            else:
                logger.error(
                    f'CA certificate file not found: {cacert}. Falling back to default verification.')

        return timeout_config, verify_ssl

    def _get_session_token(self) -> Optional[str]:
        """Retrieves a valid token for the server_url from memory, logs in if necessary."""
        session_data = _active_sessions.get(self.server_url)
        # Check if token exists for the current user
        if session_data and session_data.get('user') == self.username:
            logger.debug(f"Using existing token for {self.server_url} by user {session_data['user']}")
            return session_data['token']
        # If not, try login with credentials
        elif self.username and self.password:
            return self._login(self.username, self.password)
        return None

    def _login(self, username: str, password: str) -> Optional[str]:
        """Internal login method, stores token."""
        login_url = f'{self.server_url}/login'
        logger.info(f"Attempting login to {login_url} for user '{username}'...")
        try:
            with httpx.Client(verify=self.verify_ssl, timeout=self.timeout_config) as client:
                # The API expects the credentials as form data
                response = client.post(login_url, data={'username': username, 'password': password})

            response.raise_for_status()
            data = response.json()
            token = data.get('access_token')

            if token:
                # Store the token globally
                _active_sessions[self.server_url] = {
                    'token': token,
                    'user': username
                }
                logger.info(f"Login successful for '{username}' at {self.server_url}. Token stored.")
                return token
            else:
                logger.error(
                    f"Login to {self.server_url} succeeded but no token received (missing 'access_token').")
                return None
        except httpx.HTTPStatusError as e:
            logger.error(
                (
                    f"Login failed for '{username}' at {self.server_url}: "
                    f'{e.response.status_code} - {e.response.text}'
                )
            )
            return None
        except Exception as e:
            logger.error(f'Login request to {self.server_url} failed: {e}', exc_info=True)
            return None

    def _prepare_request_kwargs(
        self,
        token: str,
        json_data: Optional[Dict[str, Any]] = None,
        content_data: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Prepares headers and payload arguments for httpx.request."""

        headers: Dict[str, str] = {'X-Auth-Token': token}

        if content_data is not None:
            headers['Content-Type'] = 'application/yaml'

        request_kwargs: Dict[str, Any] = {
            'headers': headers,
            'params': params,
        }

        if json_data is not None:
            request_kwargs['json'] = json_data
        elif content_data is not None:
            request_kwargs['content'] = content_data

        return request_kwargs

    def _make_request(
            self,
            method: str,
            endpoint: str,
            json_data: Optional[Dict[str, Any]] = None,
            content_data: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Makes an authenticated request, handles token renewal implicitly by server."""
        token = self._get_session_token()
        if not token:
            logger.error(f'Authentication failed or credentials not provided for {self.server_url}')
            return None

        url = f"{self.server_url}/{endpoint.lstrip('/')}"
        client_method = method.upper()
        try:
            request_kwargs = self._prepare_request_kwargs(
                token=token,
                json_data=json_data,
                content_data=content_data,
                params=params
            )

            logger.debug(f'Making {method.upper()} request to {url}')

            with httpx.Client(verify=self.verify_ssl, timeout=self.timeout_config) as client:
                response = client.request(
                    method=client_method,
                    url=url,
                    **request_kwargs
                )

            response.raise_for_status()
            response_data = response.json()

            # Update token if the server provided a renewed one
            new_token_from_response = response_data.get('current_token')
            if new_token_from_response and new_token_from_response != token:
                logger.info(f'Server returned a renewed token for {self.server_url}. Updating client cache.')
                _active_sessions[self.server_url]['token'] = new_token_from_response
            return response_data

        except httpx.HTTPStatusError as e:
            logger.error(f'API Error ({method} {url}): {e.response.status_code}')
            try:
                error_detail = e.response.json().get('detail', e.response.text)
                logger.error(f'Server Detail: {error_detail}')
            except json.JSONDecodeError:
                logger.error(f'Server Response Text: {e.response.text}')

            if e.response.status_code == 401:
                logger.warning(f'Token expired or invalid for {self.server_url}. Clearing session cache.')
                _active_sessions.pop(self.server_url, None)
            return None
        except httpx.RequestError as e:
            logger.error(f'Request Error ({method} {url}): {e}')
            return None
        except json.JSONDecodeError:
            logger.error(f'JSON Decode Error ({method} {url}). Invalid response received.')
            return None
        except Exception as e:
            logger.error(f'Unexpected error during API request ({method} {url}): {e}', exc_info=True)
            return None

    def execute_remote_playbook_yaml(
        self, playbook_yaml_content: str, debug: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Executes a playbook by sending its YAML content."""
        params = {'debug': 'true'} if debug else None
        return self._make_request(
            method='POST',
            endpoint='playbooks/execute/yaml',
            content_data=playbook_yaml_content,
            params=params)

    def execute_remote_command(
        self,
        command_pydantic_model,
        debug: bool = False
    ) -> Optional[Dict[str, Any]]:

        # Convert Pydantic model to dict for JSON body
        # handle None values for optional fields (exclude_none=True)
        command_body_dict = command_pydantic_model.model_dump(exclude_none=True)
        params = {'debug': 'true'} if debug else None
        return self._make_request(
            method='POST',
            endpoint='command/execute',
            json_data=command_body_dict,
            params=params
        )


def print_result(result_data: Optional[Dict[str, Any]], action: str):
    if not result_data:
        logger.error(f'{action} failed. See logs above for details.')
        sys.exit(1)

    print(f'\n--- {action} Result ---')
    print(f"Success: {result_data.get('success', 'N/A')}")
    print(f"Message: {result_data.get('message', 'No message.')}")

    final_state = result_data.get('final_state')
    if final_state and final_state.get('variables'):
        print('\n--- Final Variable Store State ---')
        print(yaml.safe_dump(final_state['variables'], indent=2, default_flow_style=False))

    if not result_data.get('success'):
        sys.exit(1)


def main():
    """Main entry point for the attackmate-client CLI."""
    parser = argparse.ArgumentParser(description='AttackMate Playbook Client for Remote API Execution')
    # Required Positional Argument: Playbook file path
    parser.add_argument(
        'playbook_file',
        help='Path to the local playbook YAML file to execute.'
    )

    parser.add_argument('--server-url', default='https://localhost:8445',
                        help='Base URL of the AttackMate API server (default: https://localhost:8445)')
    parser.add_argument('--username', required=True, help='API username for authentication.')
    parser.add_argument('--password', required=True, help='API password for authentication.')
    parser.add_argument(
        '--cacert',
        help='Path to the server\'s self-signed certificate file for verification.')
    parser.add_argument('--debug', action='store_true', help='Enable server debug logging for this instance.')

    args = parser.parse_args()

    if not os.path.exists(args.playbook_file):
        logger.error(f'Local playbook file not found: {args.playbook_file}')
        sys.exit(1)

    # Initialize the client
    client = RemoteAttackMateClient(
        server_url=args.server_url,
        cacert=args.cacert,
        username=args.username,
        password=args.password
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
