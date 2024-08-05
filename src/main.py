import sys
import getpass
import os
from src.menu import Menu
from src import SFTP, setup_logger

def main():

    sftp_client = SFTP()

    sftp_client._host = "ada.cs.pdx.edu"
    sftp_client._port = 22
    sftp_client._username = "matt"
    sftp_client._password = getpass.getpass("Enter password: ")
    sftp_client.connect()
    found = sftp_client.search_remote("test")
    

    remote_file_list = list(found)
    print(f"REMOTE FILE LIST: {remote_file_list}")

    local_file_list = list()
    sftp_client.set_download_location("/Users/matt/Desktop/test_download")
    
    result = sftp_client.download_all(remote_file_list, local_file_list)
    print(result)





    return

    test_menu = Menu()
    test_menu.set_title(" CS 410 Group 2 - SFTP ") 
    test_menu.add_option("login", login, sftp_client)
    test_menu.add_option("list", list_dir, sftp_client)
    test_menu.add_option("set default download location", set_download, sftp_client)
    test_menu.add_option("download file", download, sftp_client)
    test_menu.add_option("download multiple files", download_all, sftp_client)
    test_menu.add_option("upload file", upload, sftp_client)
    test_menu.add_option("Remove remote directory", remove_remote_dir, sftp_client)
    test_menu.add_option("Exit", exit)

    option_selection = None
    while(option_selection != "Exit"):
        print(test_menu)
        try:
            option_selection = test_menu.get_selection()
            result = test_menu.execute_option(option_selection)
            print(result[1])
            if (option_selection != "Exit"): 
                input("\nPress Enter to continue...")
        except Exception as e:
            print(f"There was an error with your selection: {e}")
        


# Input/Validation function requirements: return result of sftp_client function call
def login(sftp_client):

    
    hostname = None
    port = None
    username = None
    password = None

    hostname = input("Enter hostname: ") 
    port = input("enter port: ")
    username = input("enter username: ")
    password = getpass.getpass("Enter password: ")

    try:
        sftp_client._host = hostname
        sftp_client._port = int(port)
        sftp_client._username = username 
        sftp_client._password = password 
    except Exception as e:
        return (False, f"Invalid port number {port}")

    return sftp_client.connect()
    

def set_download(sftp_client):
    download_path = input("Enter download path: ")
    return sftp_client.set_download_location(download_path)


def list_dir(sftp_client):
    print(sftp_client)
    return sftp_client.list_directory()


def download(sftp_client):
    if (sftp_client.list_directory()):
        remote_path = input("Enter the file to download: ")
        local_path = input("Enter the local path: ")
        return sftp_client.download(remote_path, local_path)


def download_all(sftp_client):
    if (sftp_client.list_directory()):
        remote_file_str= input("Enter the files you want to download, separated by a space:\n")
        remote_file_list = remote_file_str.split(' ')

        local_file_str = input("Enter the file locations, separated by a space:\n")

        if (local_file_str != ""):
            local_file_list = local_file_str.split(' ')
        else:
            local_file_list = list()
        
        return sftp_client.download_all(remote_file_list, local_file_list)


def upload(sftp_client):
    if (sftp_client.list_directory_local()):
        local_path = input("Enter the file to upload: ")
        if (sftp_client.list_directory()):
            remote_path = input("Enter the remote path: ")
            return sftp_client.put(local_path, remote_path)

def remove_remote_dir(sftp_client):
    if (sftp_client.list_directory()):
        remote_dir_path = input("Enter the directory to delete: ")
        return sftp_client.rmdir(remote_dir_path)


def exit():
    return (True, "Exiting...")

if __name__ == "__main__":
    main()