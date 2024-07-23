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


############ Download Tests ############

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

def test_download_all_success_local_supplied(client):

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


#TODO: Need to set up a way for user to specify default download folder
def test_download_all_success_local_supplied(client):
    pass


def test_download_all_failure_local_supplied(client):

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

def test_download_all_failure_local_not_supplied(client):

    local_file_list = list() # Empty list == default download location


    local_file1 = get_local_file_path("test1.txt")
    local_file2 = get_local_file_path("test2.txt")
    local_file3 = get_local_file_path("test3.txt")

    remote_file_list = list()
    remote_file_list.append("nonexistant1.txt")
    remote_file_list.append("nonexistant2.txt")
    remote_file_list.append("nonexistant3.txt")

    success = client.download_all(remote_file_list, local_file_list)

    file1_exists = os.path.isfile(local_file1)
    file2_exists = os.path.isfile(local_file2)
    file3_exists = os.path.isfile(local_file3)

    
    assert(file1_exists == False)
    assert(file2_exists == False)
    assert(file3_exists == False)
    assert(success == False)
