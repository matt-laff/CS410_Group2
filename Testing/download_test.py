import pytest
import sys
import os
import SFTPClient

@pytest.fixture
def client():
    try:
        with open("credentials.txt", 'r') as file:
            password = file.read().strip() 
    except Exception as e:
        print(f"Error - credentials file doesn't exist: {e}")
    client = SFTPClient.SFTP(22, "babbage.cs.pdx.edu", "matt", password)
    return client 



def test_download():
    file_exists = os.path.isfile("test.txt")
    assert(file_exists == False)
