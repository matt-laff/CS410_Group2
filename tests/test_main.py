import pytest
import os
import shutil
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

@pytest.fixture(scope="session")
def client(sftpserver, content):
    sftpclient = sftp_client.SFTP(sftpserver.port, sftpserver.host, "stubUser", "stubPassword")
    sftpclient.connect() # Not sure if its better to do this here or in the fixture
    yield sftpclient
    del sftpclient


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
