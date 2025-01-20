import pytest
from unittest.mock import Mock, patch
import requests
from requests.exceptions import RequestException
from pan_cortex_data_lake.httpclient import HTTPClient
from pan_cortex_data_lake.exceptions import UnexpectedKwargsError, RequiredKwargsError, HTTPError, CortexError

@pytest.fixture
def http_client():
    return HTTPClient(url="https://test.api.com")

def test_httpclient_initialization():
    client = HTTPClient(url="https://test.api.com", port=8080)
    assert client.url == "https://test.api.com"
    assert client.port == 8080
    assert client.auto_refresh is True
    assert client.enforce_json is False

def test_httpclient_initialization_with_unexpected_kwargs():
    with pytest.raises(UnexpectedKwargsError):
        HTTPClient(url="https://test.api.com", unexpected_kwarg="value")

@patch('requests.Session')
def test_httpclient_default_headers(mock_session):
    HTTPClient()
    headers = mock_session.return_value.headers
    assert headers['Accept'] == 'application/json'
    assert 'User-Agent' in headers
    assert 'cortex-data-lake-python' in headers['User-Agent']

@patch('requests.Session')
def test_httpclient_custom_headers(mock_session):
    custom_headers = {'Custom-Header': 'Value'}
    HTTPClient(headers=custom_headers)
    headers = mock_session.return_value.headers
    assert headers['Custom-Header'] == 'Value'

def test_httpclient_repr():
    client = HTTPClient(url="https://test.api.com", headers={"Authorization": "Bearer token"})
    repr_str = repr(client)
    assert "HTTPClient" in repr_str
    assert "url='https://test.api.com'" in repr_str
    assert "Authorization" in repr_str
    assert "Bearer token" not in repr_str

@patch('requests.Session')
def test_apply_credentials(mock_session, http_client):
    mock_credentials = Mock()
    mock_credentials.get_credentials.return_value.access_token = "test_token"
    mock_credentials.jwt_is_expired.return_value = False

    headers = {}
    http_client._apply_credentials(auto_refresh=True, credentials=mock_credentials, headers=headers)

    assert headers['Authorization'] == 'Bearer test_token'

@patch('requests.Session')
def test_apply_credentials_refresh_token(mock_session, http_client):
    mock_credentials = Mock()
    mock_credentials.get_credentials.return_value.access_token = None
    mock_credentials.refresh.return_value = "new_token"

    headers = {}
    http_client._apply_credentials(auto_refresh=True, credentials=mock_credentials, headers=headers)

    assert headers['Authorization'] == 'Bearer new_token'
    mock_credentials.refresh.assert_called_once()

@patch('requests.Session')
def test_send_request(mock_session, http_client):
    mock_response = Mock()
    mock_response.json.return_value = {"key": "value"}
    mock_session.return_value.request.return_value = mock_response

    response = http_client._send_request(
        enforce_json=True,
        method="GET",
        raise_for_status=False,
        url="https://test.api.com/endpoint"
    )

    assert response == mock_response
    assert http_client.stats.transactions == 1

@patch('requests.Session')
def test_send_request_raise_for_status(mock_session, http_client):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Client Error")
    mock_session.return_value.request.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        http_client._send_request(
            enforce_json=False,
            method="GET",
            raise_for_status=True,
            url="https://test.api.com/endpoint"
        )

@patch('requests.Session')
def test_send_request_invalid_json(mock_session, http_client):
    mock_response = Mock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_session.return_value.request.return_value = mock_response

    with pytest.raises(CortexError, match="Invalid JSON"):
        http_client._send_request(
            enforce_json=True,
            method="GET",
            raise_for_status=False,
            url="https://test.api.com/endpoint"
        )

@patch.object(HTTPClient, '_send_request')
def test_request_method(mock_send_request, http_client):
    mock_send_request.return_value = Mock()

    response = http_client.request(
        method="GET",
        endpoint="/test",
        params={"key": "value"},
        headers={"Custom-Header": "Value"}
    )

    mock_send_request.assert_called_once_with(
        http_client.enforce_json,
        "GET",
        http_client.raise_for_status,
        "https://test.api.com:443/test",
        params={"key": "value"},
        headers={"Custom-Header": "Value", "Accept": "application/json", "User-Agent": mock_send_request.call_args[1]['headers']['User-Agent']},
        cookies=None,
        auth=None,
        proxies=None,
        verify=None,
        stream=None,
        cert=None
    )
    assert response == mock_send_request.return_value

def test_request_method_missing_method():
    client = HTTPClient()
    with pytest.raises(RequiredKwargsError, match="method"):
        client.request(endpoint="/test")

@patch.object(HTTPClient, '_send_request')
def test_request_method_with_credentials(mock_send_request, http_client):
    mock_credentials = Mock()
    mock_credentials.get_credentials.return_value.access_token = "test_token"
    http_client.credentials = mock_credentials

    http_client.request(method="GET", endpoint="/test")

    called_headers = mock_send_request.call_args[1]['headers']
    assert called_headers['Authorization'] == 'Bearer test_token'

@patch.object(HTTPClient, '_send_request')
def test_request_method_unexpected_kwargs(mock_send_request, http_client):
    with pytest.raises(UnexpectedKwargsError):
        http_client.request(method="GET", endpoint="/test", unexpected_kwarg="value")

@patch.object(HTTPClient, '_send_request')
def test_request_method_http_error(mock_send_request, http_client):
    mock_send_request.side_effect = requests.RequestException("Network error")

    with pytest.raises(HTTPError):
        http_client.request(method="GET", endpoint="/test")