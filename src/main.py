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


def list_dir(sftp_client):
    print(sftp_client)
    sftp_client.list_directory()


def use_example():


    remote_file_str= input("Enter the files you want to download, separated by a space:\n")
    remote_file_list = remote_file_str.split(' ')

    local_file_str = input("Enter the file locations, separated by a space:\n")

    if (local_file_str != ""):
        local_file_list = local_file_str.split(' ')
    else:
        local_file_list = list()

    sftp_client.set_download_location("C:\\Users\\mattt\\Downloads")

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