import sys
import getpass
import os

from src import SFTP, setup_logger

DEFAULT_HOST = "babbage.cs.pdx.edu"
DEFAULT_PORT = 22
DEFAULT_USER = "matt"

def main():
    
    hostname = None
    port = None
    username = None
    password = None 

    if (len(sys.argv) > 1):
        hostname = DEFAULT_HOST
        port = DEFAULT_PORT
        username = DEFAULT_USER
        password = getpass.getpass("Enter password: ")
    else:
        hostname, port, username, password = get_credentials(hostname, port, username, password)

    sftp_client = SFTP(port, hostname, username, password)
    sftp_client.connect()

    sftp_client.list_directory()
    sftp_client.print_debug("Finished in main", None, True)


   # local_path = sftp_client.remote_to_local("/u/matt/test.txt") 
   # print(local_path)
    
    remote_file_str= input("Enter the files you want to download, separated by a space:\n")
    remote_file_list = remote_file_str.split(' ')

    local_file_str = input("Enter the file locations, separated by a space:\n")

    if (local_file_str != ""):
        local_file_list = local_file_str.split(' ')
    else:
        local_file_list = list()

    print(remote_file_list)
    print(local_file_list)


    sftp_client.download_all(remote_file_list, local_file_list)

    return 


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