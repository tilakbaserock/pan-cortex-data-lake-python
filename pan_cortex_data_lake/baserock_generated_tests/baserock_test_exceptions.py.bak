import pytest
from pan_cortex_data_lake.exceptions import CortexError, HTTPError, PartialCredentialsError, RequiredKwargsError, UnexpectedKwargsError

class TestCortexError:
    def test_cortex_error_initialization(self):
        error_message = "Test error message"
        error = CortexError(error_message)
        assert isinstance(error, Exception)
        assert error.message == error_message
        assert str(error) == error_message

class TestHTTPError:
    def test_http_error_initialization(self):
        error_instance = "HTTP 404 Not Found"
        error = HTTPError(error_instance)
        assert isinstance(error, CortexError)
        assert str(error) == error_instance

class TestPartialCredentialsError:
    def test_partial_credentials_error_initialization(self):
        error_instance = "Missing API key"
        error = PartialCredentialsError(error_instance)
        assert isinstance(error, CortexError)
        assert str(error) == error_instance

class TestRequiredKwargsError:
    def test_required_kwargs_error_initialization(self):
        missing_kwarg = "api_key"
        error = RequiredKwargsError(missing_kwarg)
        assert isinstance(error, CortexError)
        assert str(error) == missing_kwarg

class TestUnexpectedKwargsError:
    def test_unexpected_kwargs_error_initialization(self):
        unexpected_kwargs = {"invalid_param": "value", "another_invalid": "another_value"}
        error = UnexpectedKwargsError(unexpected_kwargs)
        assert isinstance(error, CortexError)
        assert str(error) == "invalid_param, another_invalid"

    def test_unexpected_kwargs_error_single_kwarg(self):
        unexpected_kwargs = {"single_invalid": "value"}
        error = UnexpectedKwargsError(unexpected_kwargs)
        assert isinstance(error, CortexError)
        assert str(error) == "single_invalid"

def test_exception_hierarchy():
    assert issubclass(HTTPError, CortexError)
    assert issubclass(PartialCredentialsError, CortexError)
    assert issubclass(RequiredKwargsError, CortexError)
    assert issubclass(UnexpectedKwargsError, CortexError)

def test_raising_cortex_error():
    with pytest.raises(CortexError) as excinfo:
        raise CortexError("Test raising CortexError")
    assert str(excinfo.value) == "Test raising CortexError"

def test_raising_http_error():
    with pytest.raises(HTTPError) as excinfo:
        raise HTTPError("HTTP 500 Internal Server Error")
    assert str(excinfo.value) == "HTTP 500 Internal Server Error"

def test_raising_partial_credentials_error():
    with pytest.raises(PartialCredentialsError) as excinfo:
        raise PartialCredentialsError("Missing access token")
    assert str(excinfo.value) == "Missing access token"

def test_raising_required_kwargs_error():
    with pytest.raises(RequiredKwargsError) as excinfo:
        raise RequiredKwargsError("client_id")
    assert str(excinfo.value) == "client_id"

def test_raising_unexpected_kwargs_error():
    with pytest.raises(UnexpectedKwargsError) as excinfo:
        raise UnexpectedKwargsError({"unexpected": "value", "another": "param"})
    assert str(excinfo.value) == "unexpected, another"