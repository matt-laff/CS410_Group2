import sftp_client as sftp_client
import log_handler as log_handler
import getpass
import os
import sys, getopt


DEFAULT_HOST = "babbage.cs.pdx.edu"
DEFAULT_PORT = 22
DEFAULT_USER = "matt"

def main():
    
    PARENT_DIR = os.path.dirname(os.getcwd())
    TMP_PATH = os.path.join(PARENT_DIR, "tmp")
    os.makedirs(TMP_PATH)

    print(str(TMP_PATH))
   
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

    sftp_client = sftp_client.SFTP(port, hostname, username, password)
    sftp_client.connect()


    sftp_client.list_directory()

    return 
    
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