import pytest
import os
import shutil
from unittest.mock import MagicMock, patch
from .conftest import get_local_file_path, TMP, CONTENT_OBJ
from .context import src
from src import sftp_client 

from paramiko import Transport
from paramiko.channel import Channel
from paramiko.sftp_client import SFTPClient
from pytest_sftpserver.sftp.server import SFTPServer

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

    print("\n*****************")
    data = client._SFTP.stat("incoming/file1.txt")
    print(data)
    dir_data = client._SFTP.stat("incoming")
    client._SFTP.chmod("incoming", 0)
    print(dir_data)
    dir_data = client._SFTP.stat("incoming")
    print(dir_data)
    print("*****************")
    success = client.download("incoming/file1.txt", local_file_path)
    file_exists = os.path.isfile(local_file_path)
    with open(local_file_path, 'r') as file:
            assert(file.read() == "file1")
    assert(file_exists == True)
    assert(success[0] == True)


def test_download_failure(client):
    local_file_path = get_local_file_path("test.txt")

    success = client.download("nonexistent.txt", local_file_path)
    file_exists = os.path.isfile(local_file_path)
    assert(file_exists == False)
    assert(success[0] == False)

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
    assert(success[0] == True)


# Test successful download of multiple files with no local path provided
def test_download_all_success_with_download_location(client):

    local_file_list = list()

    remote_file_list = list()
    remote_file_list.append("incoming/file1.txt")
    remote_file_list.append("incoming/file2.txt")
    remote_file_list.append("incoming/subdirectory/file3.txt")

    client.set_download_location(TMP)
    success = client.download_all(remote_file_list, local_file_list)

    file1_path = os.path.join(TMP, "file1.txt")
    file2_path = os.path.join(TMP, "file2.txt")
    file3_path = os.path.join(TMP, "file3.txt")
    
    file1_exists = os.path.isfile(file1_path)
    file2_exists = os.path.isfile(file2_path)
    file3_exists = os.path.isfile(file3_path)

    local_file_list.append(file1_path)
    local_file_list.append(file2_path)
    local_file_list.append(file3_path)

    for i in range(3):
       with open(local_file_list[i], 'r') as file:
                assert(file.read() == f"file{i+1}")
    
    assert(file1_exists == True)
    assert(file2_exists == True)
    assert(file3_exists == True)
    assert(success[0] == True)




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
    assert(success[0] == False)


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
    assert(success[0] == False)


def test_rmdir(mock_client):
    client = sftp_client.SFTP(mock_client)
    client.rmdir("/tmp")
    mock_client.rmdir.assert_called_once_with("/tmp")

def test_put(mock_client):
    client = sftp_client.SFTP(mock_client)
    client.put("/tmp/local.txt", "/tmp/remote.txt")
    mock_client.put.assert_called_once_with("/tmp/local.txt", "/tmp/remote.txt")



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                             Connect (Nolan)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
#                     Configuration
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#


@pytest.fixture(scope="function")
def client_connect_tests(sftpserver, content):
    sftpclient = sftp_client.SFTP(sftpserver.port, sftpserver.host, "stubUser", "stubPassword")
    return sftpclient


Authentication_Failed = ("Authentication failed: Bad authentication type; allowed types: ['publickey',"
                          "'gssapi-keyex', 'gssapi-with-mic', 'keyboard-interactive', 'hostbased']")

Port_Failed = "Unexpected error during SFTP connection: connect(): port must be 0-65535."

bad_host= bad_port = bad_username= bad_password = "dad"



#==============================================================#
#TEST: Initialize SSH transport layer for the connection.
#==============================================================#
def test_transport_connection_established_successfully(client_connect_tests):
    client_connect_tests.connect()
    transport_success = client_connect_tests._transport
    assert transport_success is not None

def test_host_failure(client_connect_tests):
    client_connect_tests._port = bad_port
    transport_failure = client_connect_tests.connect() 
    assert((transport_failure[0]== False))

def test_port_failure(client_connect_tests):
    client_connect_tests._port = bad_port
    transport_failure = client_connect_tests.connect() 
    assert((transport_failure[0]== False))

#==============================================================#
# TEST: the SSH connection using the transport layer.
#==============================================================#
def test_ssh_connection_established_successfully(client_connect_tests):
    client_connect_tests.connect()
    ssh_success = client_connect_tests._transport
    assert(ssh_success != None)

def test_ssh_authentication_failure_username(client_connect_tests):
    client_connect_tests._username =  None
    auth_failure = client_connect_tests.connect() 
    assert((auth_failure[0]== False))

"""
!This test wont work because password is not checked for being valid in mock sftp
def test_ssh_authentication_failure_password(client_connect_tests):
    client_connect_tests._password = None
    auth_failure = client_connect_tests.connect()
    assert((auth_failure[0]== False))
"""
#==============================================================#
#TEST: Create an SFTP client instance for file operations.
#==============================================================#
def test_sftp_client_connection_established_successfully(client_connect_tests):
    sftp_client_connection_success = client_connect_tests.connect() 
    assert(sftp_client_connection_success == (True, "Connection Successful"))

def test_sftp_client_value_correct(client_connect_tests):
    client_connect_tests.connect()
    sftp_value = client_connect_tests._SFTP
    assert(sftp_value != None)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                  List Directory remote Contents(Nolan)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def test_list_directory_current(client, content, capsys):
    success = client.list_directory()
    captured = capsys.readouterr()
    for root_dir in CONTENT_OBJ.keys():
        assert root_dir in captured.out
    assert success[0] == True


def test_list_directory_failure_not_connected_to_SFTP_server():
    disconnected_client = sftp_client.SFTP(22, 'localhost', 'user', 'password')
    captured = disconnected_client.list_directory()
    assert ((captured[0]== False) and (captured[1]=="Not connected to an SFTP server"))

    #Todo:test here general failure
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                  List Directory Local Contents(Nolan)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def test_list_directory_local_current(content, capsys):

    sample_client = sftp_client.SFTP(22, 'localhost', 'user', 'password')
    success = sample_client.list_directory_local()
    captured = capsys.readouterr()
    contents=  os.listdir(os.getcwd())
    for dir in contents:
        assert dir in captured.out
    assert success[0] == True 

    #Todo:test here general failure


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                  Change Permissions (Nolan)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


def test_change_permissions_success(client):

    remote_path = "incoming/file1.txt"
    new_mode = 0o644  # Desired permissions
    success = client.change_permissions(remote_path, new_mode)
    assert success[0]==True


def test_change_permissions_failure_not_connected_to_SFTP_server():
    disconnected_client = sftp_client.SFTP(22, 'localhost', 'user', 'password')
    remote_path = "incoming/file1.txt"
    new_mode = 0o644  # Desired permissions
    captured = disconnected_client.change_permissions(remote_path, new_mode)
    assert ((captured[0]== False) and (captured[1]=="Not connected to an SFTP server"))

def test_change_permissions_failure(client):
    remote_path = "non_existent_file.txt"
    new_mode = 0o644  # Desired permissions
    captured = client.change_permissions(remote_path, new_mode)
    assert ((captured[0]== False) and (captured[1]=="Failed to change permissions for non_existent_file.txt: [Errno 2] No such file"))

def test_copy_dir(client):
    local_path = os.path.join(TMP, "test_copy_dir")
    client.copy_dir("incoming", local_path)
    all_files = []
    for root, _, files in os.walk(local_path):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), local_path)
            all_files.append(relative_path)

    assert (set(all_files) == set(['file2.txt', 'file1.txt', 'subdirectory/file3.txt']))