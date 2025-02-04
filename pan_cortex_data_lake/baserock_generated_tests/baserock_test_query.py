import pytest
from unittest.mock import Mock, patch
import time
from pan_cortex_data_lake.exceptions import CortexError
from pan_cortex_data_lake.query import QueryService
from pan_cortex_data_lake import __version__

@pytest.fixture
def query_service():
    return QueryService(url="https://api.example.com", credentials=Mock())

def test_query_service_repr(query_service):
    repr_str = repr(query_service)
    assert "QueryService" in repr_str
    assert "url='https://api.example.com'" in repr_str
    assert "credentials=" in repr_str

@patch('pan_cortex_data_lake.query.HTTPClient')
def test_cancel_job(mock_http_client, query_service):
    mock_response = Mock()
    mock_http_client.return_value.request.return_value = mock_response
    
    result = query_service.cancel_job("job123")
    
    assert result == mock_response
    mock_http_client.return_value.request.assert_called_once_with(
        method="DELETE",
        url=query_service.url,
        endpoint="/query/v2/jobs/job123"
    )
    assert query_service.stats.cancel_job == 1

@patch('pan_cortex_data_lake.query.HTTPClient')
def test_create_query(mock_http_client, query_service):
    mock_response = Mock()
    mock_http_client.return_value.request.return_value = mock_response
    
    result = query_service.create_query(job_id="job123", query_params={"param1": "value1"})
    
    assert result == mock_response
    mock_http_client.return_value.request.assert_called_once_with(
        method="POST",
        url=query_service.url,
        json={
            "jobId": "job123",
            "params": {"param1": "value1"},
            "clientType": "cortex-data-lake-python",
            "clientVersion": __version__
        },
        endpoint="/query/v2/jobs"
    )
    assert query_service.stats.create_query == 1

@patch('pan_cortex_data_lake.query.HTTPClient')
def test_get_job(mock_http_client, query_service):
    mock_response = Mock()
    mock_http_client.return_value.request.return_value = mock_response
    
    result = query_service.get_job("job123")
    
    assert result == mock_response
    mock_http_client.return_value.request.assert_called_once_with(
        method="GET",
        url=query_service.url,
        endpoint="/query/v2/jobs/job123"
    )
    assert query_service.stats.get_job == 1

@patch('pan_cortex_data_lake.query.HTTPClient')
def test_get_job_results(mock_http_client, query_service):
    mock_response = Mock()
    mock_response.json.return_value = {"rowsInPage": 10}
    mock_http_client.return_value.request.return_value = mock_response
    
    result = query_service.get_job_results("job123", max_wait=5, page_size=100)
    
    assert result == mock_response
    mock_http_client.return_value.request.assert_called_once_with(
        method="GET",
        url=query_service.url,
        params={"maxWait": 5, "pageSize": 100},
        endpoint="/query/v2/jobResults/job123"
    )
    assert query_service.stats.get_job_results == 1
    assert query_service.stats.records == 10

@patch('pan_cortex_data_lake.query.QueryService.get_job_results')
def test_iter_job_results_done(mock_get_job_results, query_service):
    mock_response = Mock()
    mock_response.json.return_value = {
        "state": "DONE",
        "page": {"pageCursor": "cursor1"}
    }
    mock_get_job_results.return_value = mock_response
    
    results = list(query_service.iter_job_results("job123"))
    
    assert len(results) == 1
    assert results[0] == mock_response
    mock_get_job_results.assert_called_once_with(
        job_id="job123",
        params={},
        enforce_json=True
    )

@patch('pan_cortex_data_lake.query.QueryService.get_job_results')
@patch('time.sleep')
def test_iter_job_results_running_then_done(mock_sleep, mock_get_job_results, query_service):
    running_response = Mock()
    running_response.json.return_value = {"state": "RUNNING"}
    done_response = Mock()
    done_response.json.return_value = {"state": "DONE", "page": {}}
    mock_get_job_results.side_effect = [running_response, done_response]
    
    results = list(query_service.iter_job_results("job123"))
    
    assert len(results) == 1
    assert results[0] == done_response
    assert mock_get_job_results.call_count == 2
    mock_sleep.assert_called_once_with(1)

@patch('pan_cortex_data_lake.query.QueryService.get_job_results')
def test_iter_job_results_failed(mock_get_job_results, query_service):
    failed_response = Mock()
    failed_response.json.return_value = {"state": "FAILED"}
    mock_get_job_results.return_value = failed_response
    
    results = list(query_service.iter_job_results("job123"))
    
    assert len(results) == 1
    assert results[0] == failed_response

@patch('pan_cortex_data_lake.query.QueryService.get_job_results')
def test_iter_job_results_bad_state(mock_get_job_results, query_service):
    bad_response = Mock()
    bad_response.json.return_value = {"state": "INVALID"}
    mock_get_job_results.return_value = bad_response
    
    with pytest.raises(CortexError, match="Bad state: INVALID"):
        list(query_service.iter_job_results("job123"))

@patch('pan_cortex_data_lake.query.HTTPClient')
def test_list_jobs(mock_http_client, query_service):
    mock_response = Mock()
    mock_http_client.return_value.request.return_value = mock_response
    
    result = query_service.list_jobs(max_jobs=10, state="RUNNING", job_type="SQL")
    
    assert result == mock_response
    mock_http_client.return_value.request.assert_called_once_with(
        method="GET",
        url=query_service.url,
        params={"maxJobs": 10, "state": "RUNNING", "type": "SQL"},
        endpoint="/query/v2/jobs"
    )
    assert query_service.stats.list_jobs == 1