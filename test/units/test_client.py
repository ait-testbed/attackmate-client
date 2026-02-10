import pytest
import json
import logging
import httpx
from unittest import mock
from typing import Dict, Any, Optional
from attackmate_client.attackmate_client import (
    RemoteAttackMateClient,
    _active_sessions,
    DEFAULT_TIMEOUT,
)


@pytest.fixture(autouse=True)
def clear_sessions() -> Dict[str, Dict[str, Optional[str]]]:
    """Fixture to ensure the global session cache is empty before each test."""
    _active_sessions.clear()
    return _active_sessions

# Define a simple mock class that resembles a Pydantic model instance


class MockCommandModel:
    """Mock for the Pydantic model expected by execute_remote_command."""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def model_dump(self, exclude_none: bool = False) -> Dict[str, Any]:
        if exclude_none:
            return {k: v for k, v in self._data.items() if v is not None}
        return self._data

# Helper function to simulate httpx responses


def mock_response(status_code: int = 200,
                  json_data: Optional[Dict[str,
                                           Any]] = None,
                  text: str = '') -> httpx.Response:
    """Creates a mock httpx.Response object."""
    response = mock.MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.text = text
    response.raise_for_status.side_effect = None
    if 400 <= status_code < 600:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            f'{status_code} Error', request=mock.MagicMock(), response=response
        )
    if json_data is not None:
        response.json.return_value = json_data
    else:
        # Ensure json() call fails for non-JSON content or success with empty body
        response.json.side_effect = json.JSONDecodeError(
            'No JSON content',
            doc=text or 'None',
            pos=0) if status_code != 204 and not json_data else None
        if status_code == 200 and not text and not json_data:
            response.json.return_value = {}

    return response


class TestRemoteAttackMateClient:

    SERVER_URL = 'http://api.test'
    USERNAME = 'testuser'
    PASSWORD = 'testpassword'

    def test_init_default(self) -> None:
        """Test default client initialization."""
        client = RemoteAttackMateClient(self.SERVER_URL, username=self.USERNAME, password=self.PASSWORD)
        assert client.server_url == self.SERVER_URL
        assert client.username == self.USERNAME
        assert client.password == self.PASSWORD
        assert client.verify_ssl is True
        assert client.timeout_config.read == DEFAULT_TIMEOUT

    def test_prepare_request_kwargs_json(self) -> None:
        """Test request preparation for JSON payload."""
        token = '2345'
        json_data = {'key': 'value'}
        params = {'q': 'search'}
        kwargs = RemoteAttackMateClient(self.SERVER_URL)._prepare_request_kwargs(
            token, json_data=json_data, params=params
        )
        assert kwargs['headers'] == {'X-Auth-Token': token}
        assert kwargs['json'] == json_data
        assert kwargs['params'] == params
        assert 'content' not in kwargs

    def test_prepare_request_kwargs_yaml(self) -> None:
        """Test request preparation for YAML/content payload."""
        token = '12345'
        content_data = 'playbook: []'
        kwargs = RemoteAttackMateClient(self.SERVER_URL)._prepare_request_kwargs(
            token, content_data=content_data
        )
        assert kwargs['headers'] == {'X-Auth-Token': token, 'Content-Type': 'application/yaml'}
        assert kwargs['content'] == content_data
        assert 'json' not in kwargs


class TestClientLogin:

    SERVER_URL = 'http://api.test'
    USERNAME = 'testuser'
    PASSWORD = 'testpassword'
    TOKEN = 'test_token_123'

    @mock.patch('httpx.Client')
    def test_login_success(self, MockClient, clear_sessions):
        """Test successful login, token caching, and return."""
        mock_response_instance = mock_response(
            json_data={'access_token': self.TOKEN, 'user': self.USERNAME}
        )
        MockClient.return_value.__enter__.return_value.post.return_value = mock_response_instance

        client = RemoteAttackMateClient(self.SERVER_URL, username=self.USERNAME, password=self.PASSWORD)
        token = client._login(self.USERNAME, self.PASSWORD)

        assert token == self.TOKEN
        assert clear_sessions[self.SERVER_URL]['token'] == self.TOKEN
        assert clear_sessions[self.SERVER_URL]['user'] == self.USERNAME

    @mock.patch('httpx.Client')
    def test_login_401_failure(self, MockClient, caplog, clear_sessions) -> None:
        """Test login failure due to 401 Unauthorized status."""
        mock_response_instance = mock_response(status_code=401, text='Invalid credentials')
        MockClient.return_value.__enter__.return_value.post.return_value = mock_response_instance

        client = RemoteAttackMateClient(self.SERVER_URL, username=self.USERNAME, password=self.PASSWORD)
        with caplog.at_level(logging.ERROR):
            token = client._login(self.USERNAME, self.PASSWORD)

        assert token is None
        assert not clear_sessions
        assert "Login failed for 'testuser'" in caplog.text


class TestClientMakeRequest:

    SERVER_URL = 'http://api.test'
    USERNAME = 'testuser'
    PASSWORD = 'testpassword'
    TOKEN = 'initial_token'
    NEW_TOKEN = 'renewed_token'

    @pytest.fixture
    def setup_client(self, clear_sessions) -> RemoteAttackMateClient:
        """Setup client with a pre-cached token to skip login."""
        clear_sessions[self.SERVER_URL] = {'token': self.TOKEN, 'user': self.USERNAME}
        return RemoteAttackMateClient(self.SERVER_URL, username=self.USERNAME, password=self.PASSWORD)

    @mock.patch('httpx.Client')
    def test_make_request_success(self, MockClient, setup_client) -> None:
        """Test successful GET request."""
        endpoint = 'status'
        expected_result = {'status': 'ok'}
        mock_response_instance = mock_response(json_data=expected_result)
        MockClient.return_value.__enter__.return_value.request.return_value = mock_response_instance

        result = setup_client._make_request(method='GET', endpoint=endpoint)

        assert result == expected_result
        MockClient.return_value.__enter__.return_value.request.assert_called_once()

    @mock.patch('httpx.Client')
    def test_make_request_500_server_error(self, MockClient, setup_client, caplog) -> None:
        """Test handling of a generic server error (500)."""
        endpoint = 'action'
        mock_response_instance = mock_response(status_code=500, text='Internal Server Error')
        MockClient.return_value.__enter__.return_value.request.return_value = mock_response_instance

        with caplog.at_level(logging.ERROR):
            result = setup_client._make_request(method='POST', endpoint=endpoint)

        assert result is None
        assert 'API Error (POST http://api.test/action): 500' in caplog.text
        assert 'Server Response Text: Internal Server Error' in caplog.text


class TestClientExecutionMethods:

    SERVER_URL = 'http://api.test'
    USERNAME = 'testuser'
    PASSWORD = 'testpassword'
    TOKEN = 'exec_token'

    @pytest.fixture
    def setup_client(self, clear_sessions):
        clear_sessions[self.SERVER_URL] = {'token': self.TOKEN, 'user': self.USERNAME}
        return RemoteAttackMateClient(self.SERVER_URL, username=self.USERNAME, password=self.PASSWORD)

    @mock.patch.object(RemoteAttackMateClient, '_make_request')
    def test_execute_remote_playbook_yaml(self, mock_make_request, setup_client):
        """Test playbook execution with correct request parameters (YAML)."""
        yaml_content = 'commands: mock commands'
        setup_client.execute_remote_playbook_yaml(yaml_content, debug=False)

        mock_make_request.assert_called_once_with(
            method='POST',
            endpoint='playbooks/execute/yaml',
            content_data=yaml_content,
            params=None
        )

    @mock.patch.object(RemoteAttackMateClient, '_make_request')
    def test_execute_remote_command(self, mock_make_request, setup_client):
        """Test command execution with Pydantic model conversion."""
        # Mock Pydantic model behavior
        mock_model = MockCommandModel(
            {'type': 'shell', 'cmd': 'whoami'}
        )

        setup_client.execute_remote_command(mock_model, debug=False)

        # model_dump(exclude_none=True) should be called
        expected_body = {'type': 'shell', 'cmd': 'whoami'}

        mock_make_request.assert_called_once_with(
            method='POST',
            endpoint='command/execute',
            json_data=expected_body,
            params=None
        )
