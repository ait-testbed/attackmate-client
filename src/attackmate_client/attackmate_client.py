import json
import logging
import os
import threading
from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel
import httpx
from pydantic import SecretStr

logger = logging.getLogger('playbook')

# Global cache for active sessions (token storage), keyed by (server_url, username)
_active_sessions: Dict[Tuple[str, str], str] = {}
_sessions_lock = threading.Lock()
DEFAULT_TIMEOUT = 60.0


class RemoteAttackMateClient:
    """
    Client to interact with a remote AttackMate REST API.
    Handles authentication and token management internally per server URL.
    """

    def __init__(
        self,
        server_url: str,
        username: str,
        password: SecretStr,
        cacert: Optional[str] = None,
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
        with _sessions_lock:
            token = _active_sessions.get((self.server_url, self.username))
            if token:
                logger.debug(f'Using existing token for {self.server_url} by user {self.username}')
                return token

        # If not, try login with credentials (outside lock — network I/O should not block other threads)
        return self._login(self.username, self.password)

    def _login(self, username: str, password: SecretStr) -> Optional[str]:
        """Internal login method, stores token."""
        login_url = f'{self.server_url}/login'
        logger.info(f"Attempting login to {login_url} for user '{username}'...")
        try:
            with httpx.Client(verify=self.verify_ssl, timeout=self.timeout_config) as client:
                response = client.post(
                    login_url,
                    data={
                        'username': username,
                        'password': password.get_secret_value(),
                    },
                )

            response.raise_for_status()
            data = response.json()
            token = data.get('access_token')

            if token:
                # Store the token globally, guarded by the lock
                with _sessions_lock:
                    # Re-check under lock: another thread may have logged in while we were waiting
                    session_key = (self.server_url, username)
                    existing_token = _active_sessions.get(session_key)
                    if existing_token:
                        logger.debug(
                            f"Token for '{username}' at {self.server_url} stored by another thread. "
                            'Using existing token.'
                        )
                        return existing_token
                    _active_sessions[session_key] = token
                logger.info(f"Login successful for '{username}' at {self.server_url}. Token stored.")
                return token
            else:
                logger.error(
                    f"Login to {self.server_url} succeeded but no token received (missing 'access_token').")
                return None
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Login failed for '{username}' at {self.server_url}: "
                f'{e.response.status_code} - {e.response.text}'
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

    def _make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        content_data: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Makes an authenticated request, handles token renewal on 401."""
        token = self._get_session_token()
        if not token:
            logger.error(f'Authentication failed or credentials not provided for {self.server_url}')
            return None

        url = f"{self.server_url}/{endpoint.lstrip('/')}"
        client_method = method.upper()

        def _dispatch_request(explicit_token: str) -> httpx.Response:
            kwargs = self._prepare_request_kwargs(
                token=explicit_token,
                json_data=json_data,
                content_data=content_data,
                params=params,
            )
            logger.debug(f'Making {client_method} request to {url}')
            with httpx.Client(verify=self.verify_ssl, timeout=self.timeout_config) as client:
                response = client.request(method=client_method, url=url, **kwargs)
            response.raise_for_status()
            return response

        try:
            return _dispatch_request(explicit_token=token).json()

        except httpx.HTTPStatusError as e:
            logger.error(f'API Error ({method} {url}): {e.response.status_code}')
            try:
                error_detail = e.response.json().get('detail', e.response.text)
                logger.error(f'Server Detail: {error_detail}')
            except json.JSONDecodeError:
                logger.error(f'Server Response Text: {e.response.text}')

            if e.response.status_code == 401:
                logger.warning(f'Token expired or invalid for {self.server_url}. Clearing session cache.')
                with _sessions_lock:
                    _active_sessions.pop((self.server_url, self.username), None)

                new_token = self._login(self.username, self.password)
                if new_token:
                    try:
                        return _dispatch_request(explicit_token=new_token).json()
                    except Exception as retry_e:
                        logger.error(
                            f'Retry after re-login failed ({method} {url}): {retry_e}',
                            exc_info=True,
                        )
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
        return self._make_authenticated_request(
            method='POST',
            endpoint='playbooks/execute/yaml',
            content_data=playbook_yaml_content,
            params=params,
        )

    def execute_remote_command(
        self,
        command_pydantic_model,
        debug: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Executes a single command by sending a Pydantic model as JSON."""
        command_body_dict = command_pydantic_model.model_dump(exclude_none=True)
        params = {'debug': 'true'} if debug else None
        return self._make_authenticated_request(
            method='POST',
            endpoint='command/execute',
            json_data=command_body_dict,
            params=params,
        )


class RemoteCommand(BaseModel):
    model_config = {'extra': 'allow'}
    type: str
