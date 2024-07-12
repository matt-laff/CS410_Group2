import SFTPClient
import LogHandler
import getpass
import os


DEFAULT_HOST = "babbage.cs.pdx.edu"
DEFAULT_PORT = 22
DEFAULT_USER = "matt"

def main():

    hostname = None
    port = None
    username = None
    password = None

    hostname, port, username, password = get_credentials(hostname, port, username, password)
    print(hostname)

    sftp_client = SFTPClient.SFTP(port, hostname, username, password)
    sftp_client.connect()


    sftp_client.list_directory()
    
    source_path = input("Enter file to download: ")

    print("Current Local Path: " + str(os.getcwd()))
    dest_path = input("Enter location to save file: ")

    sftp_client.download(source_path, dest_path)



def get_credentials(hostname, port, username, password):
    hostname = input("enter hostname: ")
    if (hostname == ''):
        hostname = DEFAULT_HOST
    port = input("enter port: ")
    if (port == ''):
        port = DEFAULT_PORT
    username = input("enter username: ")
    if (username == ''):
        username = DEFAULT_USER
    password = getpass.getpass("Enter password: ")
    return hostname, port, username, password




if __name__ == "__main__":
    main()