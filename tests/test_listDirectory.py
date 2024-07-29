import pytest
import os
import shutil
from .conftest import get_local_file_path, TMP, CONTENT_OBJ

from .context import src
from src import sftp_client
from unittest.mock import Mock
from src.sftp_client import SFTP


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


def test_list_directory_root(client, content, capsys):
    client.list_directory()
    captured = capsys.readouterr()
    for root_dir in CONTENT_OBJ.keys():
        assert root_dir in captured.out


def test_list_directory_ued(capsys):
    disconnected_client = sftp_client.SFTP(22, 'localhost', 'user', 'password')
    disconnected_client.list_directory()
    captured = capsys.readouterr()
    assert "Not connected to an SFTP server." in captured.out


#TODO: MAYBE ADD A TEST FOR PERMISION ERRORS??????