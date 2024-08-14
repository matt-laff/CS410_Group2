from typing import Dict
from pudb import set_trace
from datetime import datetime
import paramiko, humanize, json

class hostconnect:
    def __init__(self, session:Dict=None):
        self.host = session.get("host")
        self.port = session.get("port")
        self.username = session.get("username")
        self.password = session.get("password")

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def __enter__(self):
        self.client.connect(self.host, self.port, self.username, self.password)
        self.sftp = self.client.open_sftp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        #set_trace()
        if not exc_type and self.client:
            self.sftp.close()
            self.client.close()

    def listdir_attr(self, path:str=None):
        files: list[paramiko.SFTPAttributes] = self.sftp.listdir_attr(path)

        for file in files:
            file.st_size = humanize.intcomma(file.st_size)
            file.st_mtime = humanize.naturaltime(datetime.fromtimestamp(file.st_mtime))

        return files

    def rename(self, oldpath:str=None, newpath:str=None):
        self.sftp.rename(oldpath, newpath)
