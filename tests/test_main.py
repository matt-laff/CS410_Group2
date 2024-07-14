import pytest
import sys
import os
sys.path.append("..")
import src.sftp_client as sftp_client

@pytest.fixture
def credentials():
    full_path = os.path.join(os.path.dirname(__file__), "credentials.txt")
    with open(full_path, 'r') as file:
        host = file.readline().strip()
        port = file.readline().strip()
        user = file.readline().strip() 
        password = file.readline().strip()

    return host,port,user,password


@pytest.fixture
def client(credentials):
    host,port,user,password = credentials
    client = sftp_client.SFTP(port, host, user, password)
    return client 



def test_download_success(client):
    client.connect() # Not sure if its better to do this here or in the fixture
    
    if (os.path.isfile("test.txt")):
        os.remove("test.txt")
    file_exists = os.path.isfile("test.txt")
    assert(file_exists == False)

    success = client.download("test.txt", "")
    file_exists = os.path.isfile("test.txt")
    assert(file_exists == True)
    assert(success == True)
    
def test_download_failure(client):
    client.connect() # Not sure if its better to do this here or in the fixture
    
    if (os.path.isfile("test.txt")):
        os.remove("test.txt")
    file_exists = os.path.isfile("test.txt")
    assert(file_exists == False)

    success = client.download("", "")
    file_exists = os.path.isfile("test.txt")
    assert(file_exists == False)
    assert(success == False)


    