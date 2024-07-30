
# % % % % % % % % % % % % % % % % % % % % % % % % % #
# Config                                           
# % % % % % % % % % % % % % % % % % % % % % % % % % #

import pytest
import os
import shutil
from .conftest import get_local_file_path, TMP

from .context import src
from src import sftp_client 


# % % % % % % % % % % % % % % % % % % % % % % % % % #
# Helper Methods                                           
# % % % % % % % % % % % % % % % % % % % % % % % % % #




@pytest.fixture(scope="function")
def client(sftpserver, content):

    sftpclient = sftp_client.SFTP(sftpserver.port, sftpserver.host, "stubUser", "stubPassword")
    return sftpclient


Authentication_Failed = ("Authentication failed: Bad authentication type; allowed types: ['publickey',"
                          "'gssapi-keyex', 'gssapi-with-mic', 'keyboard-interactive', 'hostbased']")

Port_Failed = "Unexpected error during SFTP connection: connect(): port must be 0-65535."

bad_host= bad_port = bad_username= bad_password = "dad"



#==============================================================#
#TEST: Initialize SSH transport layer for the connection.
#==============================================================#
def testTransportConnectionEstablishedSuccessfully(client):
    client.connect()
    transportSuccess = client._transport
    assert transportSuccess is not None

def testHostFailure(client):
    client._port = bad_port
    transportFailure = client.connect() 
    assert((transportFailure[0]== False))

def testPortFailure(client):
    client._port = bad_port#change
    transportFailure = client.connect() 
    #assert(transport_failure == (False,Port_Failed ))
    assert((transportFailure[0]== False))


#==============================================================#
# TEST: the SSH connection using the transport layer.
#==============================================================#

def testSSHConnectionEstablishedSuccessfully(client):
    client.connect()
    sshSuccess = client._transport
    assert(sshSuccess != None)

def testSSHAuthenticationFailureUsername(client):
    client._username =  None
    authFailure = client.connect() 
    assert((authFailure[0]== False))

def testSSHAuthenticationFailurePassword(client):
    client._password = None
    authFailure = client.connect()
    assert((authFailure[0]== False))


#==============================================================#
#TEST: Create an SFTP client instance for file operations.
#==============================================================#

def testSFTPClientConnectionEstablishedSuccessfully(client):
    sftpClientConnectionSuccess = client.connect() 
    assert(sftpClientConnectionSuccess == (True, "Connection Successful"))


def testSFTPClientValueCorrect(client):
    client.connect()
    sftpValue = client._SFTP
    assert(sftpValue != None)
