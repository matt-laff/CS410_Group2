import sys
import getpass
import os
import builtins
from src.menu import Menu
from src import SFTP, setup_logger
from src.input_decorator import reset_input_history
from src.input_decorator import input_with_timeout
from src.input_decorator import InputTimeoutError

def main():

    #reset input_history log file
    reset_input_history()
    # Override the built-in input function
    simple_input = builtins.input
    builtins.input = input_with_timeout()(builtins.input)  # Apply timeout decorator to built-in input
    sftp_client = SFTP() 
    test_menu = Menu()
    test_menu.set_title(" CS 410 Group 2 - SFTP ") 
    test_menu.add_option("Login", login, sftp_client)
    test_menu.add_option("Quick Connect", quick_connect, sftp_client)
    test_menu.add_option("Disconnect", disconnect, sftp_client)
    test_menu.add_option("Save connection information", save_connection, sftp_client)
    test_menu.add_option("List files on remote server", list_remote, sftp_client)
    test_menu.add_option("List files on local server", list_local, sftp_client)
    test_menu.add_option("Set default download location", set_download, sftp_client)
    test_menu.add_option("Download file", download, sftp_client)
    test_menu.add_option("Download multiple files", download_all, sftp_client)
    test_menu.add_option("Upload file", upload, sftp_client)
    test_menu.add_option("Remove remote directory", remove_remote_dir, sftp_client)
    test_menu.add_option("Search remote server", search_remote, sftp_client)
    test_menu.add_option("File diff", diff, sftp_client)
    test_menu.add_option("Exit", exit)

    option_selection = None
    while(option_selection != "Exit"):
        print(test_menu)
        try:
            option_selection = test_menu.get_selection()
            result = test_menu.execute_option(option_selection)
            print(result[1])
            if (option_selection != "Exit"): 
                #simple_input("\nPress Enter to continue...")
                input("\nPress Enter to continue...")
        except InputTimeoutError as e:

            print("\nDue to inactivity, the program was shut down for security reasons")

            sys.exit()

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
    
def quick_connect(sftp_client):
    if (sftp_client.check_connection()[0] == True):
        return (False, "Already connected to a remote server, please disconnect and try again")
    if (sftp_client.display_saved_connections()[0]):
        connection_name = input("Enter the name of the connection: ")
        return sftp_client.quick_connect(connection_name)
    else: 
        return (False, "Client has no saved connections")

def save_connection(sftp_client):
    hostname = None
    port = None
    username = None
    password = None

    hostname = input("Enter hostname: ") 
    port = input("enter port: ")
    username = input("enter username: ")
    password = getpass.getpass("Enter password: ")

    connection_name = input("Please name this connection: ")

    result = sftp_client.save_credentials(connection_name, hostname, port, username, password)

    return result

def disconnect(sftp_client):
    connected = sftp_client.check_connection()
    if (connected[0]):
        return sftp_client.disconnect()
    else:
        return (False, "Not currently connected to a remote server")


def set_download(sftp_client):
    download_path = input("Enter download path: ")
    return sftp_client.set_download_location(download_path)


def list_remote(sftp_client):
    return sftp_client.list_directory()

def list_local(sftp_client):
    return sftp_client.list_directory_local()

def download(sftp_client):
    connected = sftp_client.check_connection()
    if (connected[0] == True):
        sftp_client.list_directory()
        remote_path = input("Enter the file to download: ")
        local_path = input("Enter the local path: ")
        return sftp_client.download(remote_path, local_path)
    return (False, "Not connected to server")


def download_all(sftp_client):
    connected = sftp_client.check_connection()
    if (connected[0]):
        sftp_client.list_directory()
        remote_file_str= input("Enter the files you want to download, separated by a space:\n")
        remote_file_list = remote_file_str.split(' ')

        local_file_str = input("Enter the file locations, separated by a space:\n")

        if (local_file_str != ""):
            local_file_list = local_file_str.split(' ')
        else:
            local_file_list = list()
        
        return sftp_client.download_all(remote_file_list, local_file_list)

    return (False, "Not connected to server")

def upload(sftp_client):
    connected = sftp_client.check_connection()
    if (connected[0]):
        sftp_client.list_directory_local()
        local_path = input("Enter the file to upload: ")
        if (sftp_client.list_directory()):
            remote_path = input("Enter the remote path: ")
            return sftp_client.put(local_path, remote_path)
    return (False, "Not connected to server")

def remove_remote_dir(sftp_client):
    connected = sftp_client.check_connection()
    if (connected[0]):
        sftp_client.list_directory()
        remote_dir_path = input("Enter the directory to delete: ")
        return sftp_client.rmdir(remote_dir_path)

    return (False, "Not connected to server")

def search_remote(sftp_client):
    connected = sftp_client.check_connection()
    if (connected[0]):
        sftp_client.list_directory()
        search_pattern = input("Enter a filename or pattern to search for: ")
        return sftp_client.search_remote(search_pattern)

    return (False, "Not connected to server")

def diff(sftp_client):
    connected = sftp_client.check_connection()
    if (connected[0]):
        sftp_client.list_directory()
        remote_path_one = input("Enter remote path one: ") 
        remote_path_two = input("Enter remote path two: ")
        print(sftp_client.diff(remote_path_one, remote_path_two))

    return (False, "Not connected to server")

def exit():
    return (True, "Exiting...")

if __name__ == "__main__":
    main()