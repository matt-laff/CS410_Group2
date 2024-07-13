import pytest
import sys
import os
sys.path.append("..")
import SFTPClient

@pytest.fixture
def password():
    full_path = os.path.join(os.path.dirname(__file__), "credentials.txt")
    with open(full_path, 'r') as file:
        password = file.readline().strip()
    return password

@pytest.fixture
def client(password):
    client = SFTPClient.SFTP(22, "babbage.cs.pdx.edu", "matt", password)
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


    