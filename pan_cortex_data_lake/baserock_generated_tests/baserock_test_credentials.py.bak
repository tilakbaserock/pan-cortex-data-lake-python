import os
import pytest
from unittest.mock import patch, MagicMock
from collections import namedtuple
from pan_cortex_data_lake.credentials import Credentials, ReadOnlyCredentials, CortexError, PartialCredentialsError

@pytest.fixture
def mock_storage():
    return MagicMock()

@pytest.fixture
def credentials(mock_storage):
    with patch('pan_cortex_data_lake.credentials.Credentials._init_adapter', return_value=mock_storage):
        return Credentials(
            access_token='test_access_token',
            client_id='test_client_id',
            client_secret='test_client_secret',
            refresh_token='test_refresh_token'
        )

# ... (previous test functions remain unchanged)

@patch('pan_cortex_data_lake.credentials.HTTPClient')
def test_fetch_tokens(mock_httpclient, credentials):
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        'error': 'invalid_client',
        'error_description': 'Invalid client or client credentials.'
    }
    mock_response.text = '{"error_description":"Invalid client or client credentials.","error":"invalid_client"}'
    mock_httpclient.return_value.request.return_value = mock_response
    
    with pytest.raises(CortexError) as exc_info:
        credentials.fetch_tokens(code='test_code')
    
    assert str(exc_info.value) == '{"error_description":"Invalid client or client credentials.","error":"invalid_client"}'

@patch('pan_cortex_data_lake.credentials.HTTPClient')
def test_refresh_with_refresh_token(mock_httpclient, credentials):
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        'error': 'invalid_client',
        'error_description': 'Invalid client or client credentials.'
    }
    mock_response.text = '{"error_description":"Invalid client or client credentials.","error":"invalid_client"}'
    mock_httpclient.return_value.request.return_value = mock_response
    
    with pytest.raises(CortexError) as exc_info:
        credentials.refresh()
    
    assert str(exc_info.value) == '{"error_description":"Invalid client or client credentials.","error":"invalid_client"}'

@patch('pan_cortex_data_lake.credentials.HTTPClient')
def test_revoke_access_token(mock_httpclient, credentials):
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        'error': 'invalid_client',
        'error_description': 'Invalid client or client credentials.'
    }
    mock_response.text = '{"error_description":"Invalid client or client credentials.","error":"invalid_client"}'
    mock_httpclient.return_value.request.return_value = mock_response
    
    with pytest.raises(CortexError) as exc_info:
        credentials.revoke_access_token()
    
    assert str(exc_info.value) == '{"error_description":"Invalid client or client credentials.","error":"invalid_client"}'

@patch('pan_cortex_data_lake.credentials.HTTPClient')
def test_revoke_refresh_token(mock_httpclient, credentials):
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        'error': 'invalid_client',
        'error_description': 'Account temporarily locked because number of failed logins was exceeded or max number of invalid tokens was attempted to be revoked'
    }
    mock_response.text = '{"error_description":"Account temporarily locked because number of failed logins was exceeded or max number of invalid tokens was attempted to be revoked","error":"invalid_client"}'
    mock_httpclient.return_value.request.return_value = mock_response
    
    with pytest.raises(CortexError) as exc_info:
        credentials.revoke_refresh_token()
    
    assert str(exc_info.value) == '{"error_description":"Account temporarily locked because number of failed logins was exceeded or max number of invalid tokens was attempted to be revoked","error":"invalid_client"}'

# ... (remaining test functions remain unchanged)