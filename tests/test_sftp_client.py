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
def teardown(client):
    yield
    shutil.rmtree(TMP)
    del client

# In memory client for unit/integration tests
@pytest.fixture(scope="session")
def client(sftpserver, content):
    sftpclient = sftp_client.SFTP(sftpserver.port, sftpserver.host, "stubUser", "stubPassword")
    sftpclient.connect()
    #yield sftpclient   #! This stalls out my terminal on test failures
    #del sftpclient
    return sftpclient

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
    assert(file_exists == False)
    assert(success == False)

############ Download Multiple Tests ############

# Download location helper test
def test_set_download_location(client):
     assert(client._download_location == None)
     client.set_download_location("some/path")
     assert(client._download_location == "some/path")

# Test successful download of multiple files with local path provided
def test_download_all_success_no_download_location(client):

    local_file_list = list()
    local_file_list.append(get_local_file_path("test1.txt"))
    local_file_list.append(get_local_file_path("test2.txt"))
    local_file_list.append(get_local_file_path("test3.txt"))

    remote_file_list = list()
    remote_file_list.append("incoming/file1.txt")
    remote_file_list.append("incoming/file2.txt")
    remote_file_list.append("incoming/subdirectory/file3.txt")

    success = client.download_all(remote_file_list, local_file_list)

    file1_exists = os.path.isfile(local_file_list[0])
    file2_exists = os.path.isfile(local_file_list[1])
    file3_exists = os.path.isfile(local_file_list[2])

    for i in range(3):
        with open(local_file_list[i], 'r') as file:
                assert(file.read() == f"file{i+1}")
    
    assert(file1_exists == True)
    assert(file2_exists == True)
    assert(file3_exists == True)
    assert(success == True)


# Test successful download of multiple files with no local path provided
def test_download_all_success_with_download_location(client):

    local_file_list = list()

    remote_file_list = list()
    remote_file_list.append("incoming/file1.txt")
    remote_file_list.append("incoming/file2.txt")
    remote_file_list.append("incoming/subdirectory/file3.txt")

    client.set_download_location("tmp\\")
    success = client.download_all(remote_file_list, local_file_list)

    file1_exists = os.path.isfile("tmp\\file1.txt")
    file2_exists = os.path.isfile("tmp\\file2.txt")
    file3_exists = os.path.isfile("tmp\\file3.txt")

    local_file_list.append("tmp\\file1.txt")
    local_file_list.append("tmp\\file2.txt")
    local_file_list.append("tmp\\file3.txt")

    for i in range(3):
       with open(local_file_list[i], 'r') as file:
                assert(file.read() == f"file{i+1}")
    
    assert(file1_exists == True)
    assert(file2_exists == True)
    assert(file3_exists == True)
    assert(success == True)



# Test nonexistant download files results in failure
def test_download_all_failure_nonexistant(client):

    local_file_list = list()
    local_file_list.append(get_local_file_path("test1.txt"))
    local_file_list.append(get_local_file_path("test2.txt"))
    local_file_list.append(get_local_file_path("test3.txt"))

    remote_file_list = list()
    remote_file_list.append("nonexistant1.txt")
    remote_file_list.append("nonexistant2.txt")
    remote_file_list.append("nonexistant3.txt")

    success = client.download_all(remote_file_list, local_file_list)

    file1_exists = os.path.isfile(local_file_list[0])
    file2_exists = os.path.isfile(local_file_list[1])
    file3_exists = os.path.isfile(local_file_list[2])

    
    assert(file1_exists == False)
    assert(file2_exists == False)
    assert(file3_exists == False)
    assert(success == False)


# Test to make sure download_all fails on mismatched list lengths
def test_download_all_failure_bad_length(client):

    local_file_list = list()
    local_file_list.append(get_local_file_path("test1.txt"))
    local_file_list.append(get_local_file_path("test2.txt"))

    remote_file_list = list()
    remote_file_list.append("incoming/file1.txt")

    success = client.download_all(remote_file_list, local_file_list)

    file1_exists = os.path.isfile(local_file_list[0])
    file2_exists = os.path.isfile(local_file_list[1])
    
    assert(file1_exists == False)
    assert(file2_exists == False)
    assert(success == False)


def test_rmdir(mock_client):
    client = sftp_client.SFTP(mock_client)
    client.rmdir("/tmp")
    mock_client.rmdir.assert_called_once_with("/tmp")

def test_put(mock_client):
    client = sftp_client.SFTP(mock_client)
    client.put("/tmp/local.txt", "/tmp/remote.txt")
    mock_client.put.assert_called_once_with("/tmp/local.txt", "/tmp/remote.txt")


