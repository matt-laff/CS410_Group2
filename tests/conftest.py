import sys
import os
import pytest
from copy import deepcopy
from paramiko import Transport
from paramiko.channel import Channel
from paramiko.sftp_client import SFTPClient

from pytest_sftpserver.sftp.server import SFTPServer


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


DESTINATION_PATH="/tmp"
if (sys.platform == "win32"):
    DESTINATION_PATH="tmp\\"


CONTENT_OBJ = {
    "incoming": {
        "file1.txt": "file1",
        "file2.txt": "file2",
        "subdirectory": {
            "file3.txt": "file3"
        }
    },
    "outgoing": {
        "file4.txt": "file4",
        "file5.txt": "file5",
        "subdirectory": {
            "file6.txt": "file6"
        }
    },
    "archive": {
        "file7.txt": "file7",
        "subdirectory": {
            "file8.txt": "file8"
        }
    }
}


@pytest.fixture(scope="session")
def content(sftpserver):
    with sftpserver.serve_content(deepcopy(CONTENT_OBJ)):
        yield


def get_local_file_path(file_name):
    # Need to find a better name for this method that implies side effects.
    local_file_path = os.path.join(DESTINATION_PATH, file_name)
    if (os.path.isfile(local_file_path)):
        os.remove(local_file_path)
    file_exists = os.path.isfile(local_file_path)
    assert(file_exists == False)
    return local_file_path