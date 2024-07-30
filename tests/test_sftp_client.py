import pytest
import os
import shutil
from unittest.mock import MagicMock, patch
from .conftest import get_local_file_path, TMP
from .context import src
from src import sftp_client 


@pytest.fixture(scope="session", autouse=True)
def setup():
    os.makedirs(TMP)

@pytest.fixture(scope="session", autouse=True)
def teardown():
    yield
    shutil.rmtree(TMP)

# In memory client for unit/integration tests
@pytest.fixture(scope="session")
def client(sftpserver, content):
    sftpclient = sftp_client.SFTP(sftpserver.port, sftpserver.host, "stubUser", "stubPassword")
    sftpclient.connect() # Not sure if its better to do this here or in the fixture
    yield sftpclient
    del sftpclient

# Mock client for purely unit testing
@pytest.fixture(scope="session")
def mock_client():
    with patch('paramiko.SFTPClient') as mock:
        mock_instance = mock.return_value
        yield mock_instance

def test_download_success(client):
    local_file_path = get_local_file_path("test.txt")

    success = client.download("incoming/file1.txt", local_file_path)
    file_exists = os.path.isfile(local_file_path)
    with open(local_file_path, 'r') as file:
            assert(file.read() == "file1")
    assert(file_exists == True)
    assert(success == True)


def test_download_failure(client):
    local_file_path = get_local_file_path("test.txt")

    success = client.download("nonexistent.txt", local_file_path)
    file_exists = os.path.isfile(local_file_path)
    with open(local_file_path, 'r') as file:
            assert(file.read() == "")
    assert(file_exists == True)
    assert(success == False)

def test_rmdir(mock_client):
    client = sftp_client.SFTP(mock_client)
    client.rmdir("/tmp")
    mock_client.rmdir.assert_called_once_with("/tmp")

def test_put(mock_client):
    client = sftp_client.SFTP(mock_client)
    client.put("/tmp/local.txt", "/tmp/remote.txt")
    mock_client.put.assert_called_once_with("/tmp/local.txt", "/tmp/remote.txt")
