import sys
import getpass
import os
from src.menu import Menu
from src import SFTP, setup_logger

def main():
    sftp_client = SFTP()
    test_menu = Menu()
    test_menu.add_option("login", login, sftp_client)
    test_menu.add_option("list", list_dir, sftp_client)
    test_menu.add_option("set default download location", set_download, sftp_client)
    test_menu.add_option("download file", download, sftp_client)
    test_menu.add_option("download multiple files", download_all, sftp_client)
    test_menu.add_option("upload file", upload, sftp_client)
    test_menu.add_option("Remove remote directory", remove_remote_dir, sftp_client)
    test_menu.add_option("Exit", None)

    option_selection = None
    while(option_selection != "Exit"):
        print(test_menu)
        option_selection = test_menu.get_selection()
        print(f"You Selected: {option_selection}")
        test_menu.execute_option(option_selection)
    
    


def login(sftp_client):
    DEFAULT_HOST = "babbage.cs.pdx.edu"
    DEFAULT_PORT = 22
    DEFAULT_USER = "matt"
    
    hostname = DEFAULT_HOST
    port = DEFAULT_PORT
    username = DEFAULT_USER
    password = getpass.getpass("Enter password: ")

    sftp_client._host = hostname
    sftp_client._port = port
    sftp_client._username = username 
    sftp_client._password = password 

    sftp_client.connect()

def set_download(sftp_client):
    download_path = input("Enter download path")
    sftp_client.set_download_location(download_path)


def list_dir(sftp_client):
    print(sftp_client)
    sftp_client.list_directory()


def download(sftp_client):
    if (sftp_client.list_directory()):
        remote_path = input("Enter the file to download: ")
        local_path = input("Enter the local path: ")
        sftp_client.download(remote_path, local_path)


def download_all(sftp_client):
    if (sftp_client.list_directory()):
        remote_file_str= input("Enter the files you want to download, separated by a space:\n")
        remote_file_list = remote_file_str.split(' ')

        local_file_str = input("Enter the file locations, separated by a space:\n")

        if (local_file_str != ""):
            local_file_list = local_file_str.split(' ')
        else:
            local_file_list = list()
        
        sftp_client.download_all(remote_file_list, local_file_list)


def upload(sftp_client):
    if (sftp_client.list_directory()):
        local_path = input("Enter the file to upload: ")
        remote_path = input("Enter the remote path: ")
        sftp_client.put(local_path, remote_path)

def remove_remote_dir(sftp_client):
    if (sftp_client.list_directory()):
        remote_dir_path = input("Enter the directory to delete: ")
        sftp_client.rmdir(remote_dir_path)



def use_example():




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