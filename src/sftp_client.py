import cryptography.fernet
import paramiko
from paramiko.ssh_exception import SSHException, AuthenticationException
import sys
import os
import stat
import difflib
import cryptography
import ast
from .log_handler import setup_logger

DEFAULT_PORT = 22
SAVED_CONNECTION_FILE = os.path.join("data", "saved.txt")
NUM_FIELDS = 5
CHAR_ENCODING = "utf-8"

class SFTP:

    #Returns a string representation of the connection details: port, host, and username.
    def __str__(self):
        return f"Port: {self._port}, Host: {self._host}, Username: {self._username}"

    #init method used to call proper constructor
    def __init__(self, *args):

        #logger that only captures debug messages, errors, and raised values
        self._debug_logger = setup_logger('sftp_logger', 'SFTP_debug_error.log')
        self._debug_logger.debug("New SFTP Instance Created")

        # Dictionary for saved connection information
        self._connections = {}
        self._connection_file = SAVED_CONNECTION_FILE
        self.load_saved_connections()

        #Calculate the number of arguments passed to the initializer. Will use as key for constructor calling.
        arg_len = len(args)

        # Action_map is a dictionary that maps the number of arguments (arg_len) to specific functions.
        # This allows us to dynamically choose which function to execute based on the number of arguments.
        self._default_constructor()
        action_map = {
            0: lambda: self._default_constructor(),
            1: lambda: self._sftp_client_DI_constructor(*args),  # Wrap the call in a lambda to pass args
            4: lambda: self._param_constructor(*args)  # Wrap the call in a lambda to pass args
        }

        #Call the appropriate constructor based on match.
        if arg_len in action_map:
            action_map[arg_len]()  # Now correctly passes args to _copy_constructor and _param_constructor
        #Cannot find correct argument, abort instansiation.
        else:
            raise ValueError("Invalid argument length when initializing SFTP build")


    #Defualt constructor
    def _default_constructor(self):

        # Store & initialize connection parameters connection parameters
        self._port = None
        self._host = None
        self._username = None
        self._password = None

        # Download path
        self._download_location = None

         # Initialize connection objects
        self._transport = None
        self._SFTP = None



    # Dependency injection of the SFTPClient for unit testing
    def _sftp_client_DI_constructor(self,sftp_client):

        # When passing in a mock, the type is <MagicMock name='SFTPClient()' id='4422325904'>
        # if type(sftp_client) != paramiko.SFTPClient: 
        #     raise ValueError("Type of sftp_client is not SFTPClient in single arg constructor")

        self._SFTP = sftp_client


    #Param constructor
    def _param_constructor(self, port, host, username, password):
        try:
            self._port = int(port)
        except Exception as e:
            self._debug_logger.error(f"Failed to cast port to int, exception {str(e)}")
            self._port = DEFAULT_PORT

        self._host = host
        self._username = username
        self._password = password

         # Initialize connection objects
        self._transport = None
        self._SFTP = None


    #destructor
    def __del__(self):

        #Security: set values to none to prevent collection
        self._port = None
        self._host = None
        self._username = None
        self._password = None

        self.disconnect()
        #Security: set connect objects to NUll
        self._transport = None
        self._SFTP = None

        # Download path
        self._download_location = None

    # Connect wrapper that sets credentials 
    def quick_connect(self, connection_name):
        if not connection_name in self._connections.keys():
            return (False, "No saved connection with that name")
        try:
            self._port = int(self._connections[connection_name]["port"])
        except Exception as e:
            self._debug_logger.error(f"Failed to cast port to int, exception {str(e)}")


        self._host = self._connections[connection_name]["host"]
        self._username = self._connections[connection_name]["username"]
        e_password = self._connections[connection_name]["password"]

        e_password = ast.literal_eval(e_password) 
        self._password = self.decrypt(e_password).decode("utf-8")


         # Initialize connection objects
        self._transport = None
        self._SFTP = None

        return self.connect()


    #destructor
    def __del__(self):
        #Security: set values to none to prevent collection
        self._port = None


    def connect(self):
        try:

            # Initialize SSH transport layer for the connection.
            self._debug_logger.debug(f"Connecting to {self._host}:{self._port}")
            self._transport = paramiko.Transport((self._host, self._port))
            
            
            # Establish the SSH connection using the transport layer.
            self._debug_logger.debug(f"Authenticating with username: {self._username}")
            self._transport.connect(None, self._username, self._password)
            
             # Create an SFTP client instance for file operations.
            self._debug_logger.debug("Creating SFTP client")
            self._SFTP = paramiko.SFTPClient.from_transport(self._transport)
            self._debug_logger.debug("SFTP connection established successfully")

        except AuthenticationException as e:
            self._debug_logger.error(f"Authentication failed: {str(e)}")

            self.disconnect()
            self._transport = None
            self._SFTP = None

            return False, (f"Authentication failed: {str(e)}")

        except Exception as e:
            self._debug_logger.error(f"Unexpected error during SFTP connection: {str(e)}")
            self.disconnect()
            self._transport = None
            self._SFTP = None

            return False,(f"Unexpected error during SFTP connection: {str(e)}")

        return (True,"Connection Successful")



    #Lists the contents of the current directory on the remote server.
    def list_directory(self):
        if self._SFTP is None:
            self._debug_logger.error("Not connected to a server, list_directory() Failed") 
            return (False, ("Not connected to an SFTP server"))
        
        try:

            # Assuming self._SFTP is an instance of paramiko.SFTPClient
            directory_contents = self._SFTP.listdir()
            for item in directory_contents:
                print(item)

        except Exception as e:
            self._debug_logger.error(f"Failed to list remote directory: {e}")
            return (False , (f"Failed to list remote directory: {e}"))
        
        self._debug_logger.debug(f"Successfully listed items in current remote directory")
        return (True, "") # Need empty string to fit convention


    #Lists the contents of the current directory on the remote server.
    def list_directory_local(self):
        try:
            # Get the current working directory
            cwd = os.getcwd()

            # List all entries in the current working directory
            entries = os.listdir(cwd)

            # Iterate over each entry and print its name
            for entry in entries:
                print(entry)

        except Exception as e:
            self._debug_logger.error(f"Failed to list local directory: {e}")
            return (False, (f"Failed to list local directory: {e}"))

        self._debug_logger.debug(f"Successfully listed items in local directory: {cwd} ")
        return (True, "")

    #Search files on local machine
    def search_local(self, pattern):
        try:
            found_files = []
            path = os.getcwd() 
            for root, dirs, files in os.walk(path): 
                for file in files:
                    if pattern in file:
                        found_files.append(os.path.join(root, file))
            if (len(found_files) == 0):
                return (False, "No files located")
            return (True, found_files)
        except Exception as e:
            self._debug_logger.error(f"Failed to search for file: {e}")
            return (False, (f"Failed to search for file: {e}"))

        
    # Changes the permissions of a file or directory on the remote server
    def change_permissions(self, remote_path, mode):
        o_mode = int(mode, 8)
        try:
            # Ensure self._SFTP is initialized and connected
            if self._SFTP is None:
                self._debug_logger.error("Not connected to a server, change_permissions() Failed") 
                return (False, ("Not connected to an SFTP server"))

            # Change the permissions
            # Use chmod method of SFTPClient instance to change the permissions of a file/directory on the remote server
            self._SFTP.chmod(remote_path, o_mode)

        except Exception as e:
            self._debug_logger.error(f"Failed to change permissions for {remote_path}: {e}")
            return ( False, (f"Failed to change permissions for {remote_path}: {e}"))
        
        self._debug_logger.debug(f"Successfully changed permissions to {mode} for {remote_path}")
        return (True, f"Successfully changed permissions to {mode} for {remote_path}")

    # Lists directory contents with file attributes (mode, atime, etc.)
    def list_full(self):
        if self._SFTP is None:
            return (False, "Not connected to a server, list with attributes failed." )
        
        try:
            directory_contents = self._SFTP.listdir_attr()
            for item in directory_contents:
                print(item)
            return (True, "")
        except Exception as e:
            self._debug_logger.error(f"Failed to list contents of directory: {e}")

    # Wrapper for search_remote_recursive
    def search_remote(self, pattern):
        curr_dir = self._SFTP.normalize(".") # Get absolute path of root directory
        found_files = []
        found_files = self.search_remote_recursive(pattern, curr_dir)
        self._SFTP.chdir(curr_dir) # Return to root directory explicitly after search
        if (len(found_files) == 0):
            return (False, "No files located")
        return (True, found_files)

    # Recursively search every directory starting from the login directory
    def search_remote_recursive(self, pattern, remote_dir):
        found_files = []
        self._SFTP.chdir(remote_dir)
        try:
            for item in self._SFTP.listdir_attr():
                if (item.filename[0] != "." ):
                    path = self.get_dir_path(item, remote_dir)
                    file_stat = self._SFTP.stat(path)
                    if (stat.S_ISDIR(file_stat.st_mode)):
                        try:
                            found_files += self.search_remote_recursive(pattern, path)
                        except Exception as e:
                            print(f"Exception:  {e}  , path: {path}")
                            continue
                    else:
                        if pattern in item.filename:
                            found_files.append(path)
        except Exception as e:
            print(f"Exception:  {e}")
        return found_files

    # Helper function for search remote to get the appropriate path to append to search path
    def get_dir_path(self, file_attr, remote_dir):
        path = remote_dir + '/' + file_attr.filename
        if stat.S_ISLNK(file_attr.st_mode): # Special case: dealing with a symbolic link, need to get the path of the linked location
            target_path = self._SFTP.readlink(path) 

            found_attr = self._SFTP.stat(target_path)
            if stat.S_ISDIR(found_attr.st_mode):
                return target_path
        return path

    # Download multiple files 
    def download_all(self, remote_path_list, local_path_list):
        success = (False, "")
        if (len(local_path_list) == 0): # Empty local path, default to current directory
            self._debug_logger.debug("Empty local path list, building local path")
            for path in remote_path_list:
                local_path = self.remote_to_local(path)
                self._debug_logger.debug(f"Local path: {local_path}") 
                success = self.download(path, local_path)
        elif (len(local_path_list) == len(remote_path_list)):
            for remote_path, local_path in zip(remote_path_list, local_path_list):
                success = self.download(remote_path, local_path)
        if (success[0]):
            return (True, "Successfully downloaded all files")
        else:
            return (False, "Failed to download all files")


    # Download from source_path on the remote server to destination_path on the local machine
    def download(self, source_path, destination_path):
        if ((self._download_location != None) and (destination_path == "" or destination_path == None)):
            filename = (source_path.split('/'))[-1]
            destination_path = os.path.join(self._download_location, filename)
            self._debug_logger.debug(f"Attempting to download {filename} to {destination_path}")
        try:
            self._SFTP.get(source_path, destination_path)
            result_msg = f"Sucessfully downloaded {source_path} to {destination_path}"
            self._debug_logger.debug(result_msg)
            return (True, result_msg)
        except Exception as e:
            if (os.path.isfile(destination_path)):
                os.remove(destination_path)
            result_msg = f"Failed to download file {source_path} to {destination_path}"
            self._debug_logger.error(result_msg) 
            return (False, result_msg)

    # Remove the directory at the remote path
    def rmdir(self, remote_path):
        try:
            self._SFTP.rmdir(remote_path)
            self._debug_logger.debug(f"Successfully removed directory at {remote_path}")
            return (True, f"Successfully removed directory at {remote_path}")
        except Exception as e:
            self._debug_logger.error(f"Failed to remove directory at {remote_path}")
            return (False, f"Failed to remove directory at {remote_path}")

    def remove_one_remote_file(self, remote_file_path):
        try:
            self._SFTP.remove(remote_file_path)
            self._debug_logger.debug(f"Successfully removed remote file {remote_file_path}")
            return (True, f"Successfully removed remote file {remote_file_path}")
        except Exception as e:
            self._debug_logger.error(f"Failed to remove remote file {remote_file_path}")
            return (False, f"Failed to remove remote file {remote_file_path}")
    
    # Copy a local file (local_path) to the SFTP server as remote_path
    def put(self, local_path, remote_path):
        try:
            self._SFTP.put(local_path, remote_path)
            self._debug_logger.debug(f"Successfully copied {local_path} to {remote_path}")
            return (True, f"Successfully copied {local_path} to {remote_path}")
        except Exception as e:
            self._debug_logger.error(f"Failed to copy {local_path} to {remote_path}")
            return (False, f"Failed to copy {local_path} to {remote_path}")

    # put multiple local files to remote server
    def put_all(self, local_path_list, remote_path_list):
        try:
            for local_path, remote_path in zip(local_path_list, remote_path_list):
                self.put(local_path, remote_path)
        except Exception as e:
            self.print_error("Failed to put multiple local files to remote server", e, False)
            return (False, "Failed to put multiple local files to remote server")
        return (True, "Successfully uploaded multiple files to remote server")

    # Set default download location for when no local path is provided
    def set_download_location(self, download_path):
        try:
            self._download_location = download_path
            assert(os.path.isdir(download_path))
            result_msg = f"Successfully set download location: {download_path}"
            self._debug_logger.debug(result_msg)
            return (True, result_msg)
        except Exception as e:
            result_msg = f"Failed to set download location"
            self._debug_logger.debug(f"{result_msg} : {e}")
            return (False, result_msg)

    #Create directory on remote server
    def mkdir(self, dir_name):
        if self._SFTP is None:
            return (False, "Not connected to an SFTP server") 
        try:
            self._SFTP.mkdir(dir_name, mode=511)
            self._debug_logger.debug(f"Successfully created directory {dir_name}")
            return (True, (f"Successfully created directory {dir_name}"))
        except Exception as e:
            self._debug_logger.error(f"Failed to make directory {dir_name}")
            return (False, (f"Failed to make directory {dir_name}:{e}"))


    # Helper function to convert remote formatting to local system formatting
    def remote_to_local(self, remote_path):
        try:
            source_tok = remote_path.split('/') # Tokenize the source_path string to get the filename

            if (self._download_location != None): 
                local_path = os.path.join(self._download_location, source_tok[-1])
            else:
                local_path = os.path.join(os.getcwd(), source_tok[-1])
            
            self._debug_logger.debug(f"Remote path from remote_to_local(): {remote_path}")
            self._debug_logger.debug(f"Local path from remote_to_local(): {local_path}")
            return local_path

        except Exception as e:
            self._debug_logger.error(f"Failed to download file {source_tok[-1]} to {local_path}")
            return None

    # Copy a remote dir (`remote_dir`) from the sftp server to the local host as `local_path`.
    def copy_dir(self, remote_dir, local_dir):
        if os.path.isfile(local_dir):
            self._debug_logger.debug(f"{local_dir} is file")
            return (False, f"Cannot copy directory to file")
        elif not os.path.exists(local_dir):
            self._debug_logger.debug(f"{local_dir} doesn't exist, creating directory")
            os.mkdir(local_dir)

        try:
            for entry in self._SFTP.listdir(remote_dir):
                remote_path = remote_dir + '/' + entry
                local_path = os.path.join(local_dir, entry)
                file_attr = self._SFTP.stat(remote_path)
                if stat.S_ISREG(file_attr.st_mode):
                    self.download(remote_path, local_path)
                elif stat.S_ISDIR(file_attr.st_mode):
                    os.mkdir(local_path)
                    self.copy_dir(remote_path, local_path)
        except FileNotFoundError as e:
            # This is only expected to happen on the initial `listdir`
            self._debug_logger.debug(str(e))
            return (False, f"Path {remote_dir} does not exist")

    # Returns the diff of two files on the remote sftp server
    def diff(self, remote_path_one, remote_path_two):
        with self._SFTP.file(remote_path_one, mode='r') as file_one:
            with self._SFTP.file(remote_path_two, mode='r') as file_two:
                diff = difflib.unified_diff(file_one.readlines(), file_two.readlines(), fromfile=remote_path_one, tofile=remote_path_two)
                return (True, f"{'\n'.join(diff)}")

    # Explicit disconnect method
    def disconnect(self):
        self._debug_logger.debug("Initiating disconnection process")

        client_error = None
        transport_error = None
        
        # Close SFTP client
        if self._SFTP:
            try:
                self._debug_logger.debug("Closing SFTP client")
                self._SFTP.close()
                self._debug_logger.debug("SFTP client closed successfully")
            except Exception as e:
                error_msg = f"Error closing SFTP client: {str(e)}"
                self._debug_logger.error(error_msg)
                client_error = error_msg
            finally:
                self._SFTP = None
        
        # Close SSH transport
        if self._transport != None and self._transport.is_active():
            try:
                self._debug_logger.debug("Closing SSH transport")
                self._transport.close()
                self._debug_logger.debug("SSH transport closed successfully")
            except Exception as e:
                error_msg = f"Error closing SSH transport: {str(e)}"
                self._debug_logger.error(error_msg)
                transport_error = error_msg
            finally:
                self._transport = None
        
        self._debug_logger.debug("Disconnection process completed")

        if client_error and transport_error:
            return (False, f"{client_error}; {transport_error}")
        elif client_error:
            return (False, client_error)
        elif transport_error:
            return (False, transport_error)
        else:
            return (True, "Successfully disconnected")


    # Check to see if client is currently connected to a remote server
    def check_connection(self):

        if self._SFTP is None or self._transport is None:
            self._debug_logger.error("Not connected to a server, check_connection() Failed") 
            return (False, "Not connected to an SFTP server")
    
        elif not self._transport.is_active():
            self._debug_logger.error("Transport not connected to a server, check_connection()) Failed") 
            return (False, "Not connected to an SFTP server")

        else:
            return (True, "")

    # Helper function to run on instantiation - open saved.txt and store each saved connection in the self._connections dictionary 
    def load_saved_connections(self):
        filepath = self._connection_file
        try:
            with open(filepath, "r") as file:
                lines = file.readlines()
            i = 0
            # Get lines and convert/decrypt each field except for password
            while i < len(lines):
                connection_name = lines[i].strip()
                host = lines[i+1].strip()
                host = ast.literal_eval(host) # Saved encoded - need to grab the literal, not the string version so we can decode it
                host = self.decrypt(host).decode(CHAR_ENCODING)
                
                port = lines[i+2].strip()
                port = ast.literal_eval(port)
                port = self.decrypt(port).decode(CHAR_ENCODING)
                
                user = lines[i+3].strip()
                user = ast.literal_eval(user)
                user = self.decrypt(user).decode(CHAR_ENCODING)
                
                password = lines[i+4].strip()
                #password = ast.literal_eval(password)
                #password = self.decrypt(password).decode(CHAR_ENCODING) #! leave password encrypted until it needs to be used

                # Add new connection information to saved connections
                self._connections[connection_name] = {
                    "host": host,
                    "port": port,
                    "username": user,
                    "password": password
                } 
                i += NUM_FIELDS # Skip past fields for the iterator

        except Exception as e:
            self._debug_logger.error(f"Failed to load saved connections: {e}")
            return (False, "Failed to load saved connections into dictionary")
        
    def rename(self, old_path, new_path):
        try:
            self._SFTP.rename(old_path, new_path)
            return (True, f"Renamed {old_path} to {new_path}")
        except Exception as e: 
            return (False, "failed to rename")


    # Simple display of saved connections
    def display_saved_connections(self):
        if (len(self._connections) == 0):
            return (False, "No saved connections")
        for name, subkey in self._connections.items():
            print(f'Connection: {name}\n {subkey["host"]}\n {subkey["port"]}')
        return (True, "")

    # Append connection information to saved.txt
    def save_credentials(self, connection_name, host, port, username, password):
        if (connection_name in self._connections.keys()): 
            return (False, "Connection name already exists")
        
        filepath = self._connection_file

        # Encrypt fields for writing to file
        e_host = self.encrypt(host)
        e_port = self.encrypt(str(port))
        e_user = self.encrypt(username)
        e_pass = self.encrypt(password)

        # Write encrypted fields
        try:
            with open(filepath, 'a') as file:
                file.write(f"{connection_name}\n")
                file.write(f"{e_host}\n")
                file.write(f"{e_port}\n")
                file.write(f"{e_user}\n")
                file.write(f"{e_pass}\n")

        except Exception as e:
            self._debug_logger.error(f"Error trying to save credentials {e}") 
            return (False, "Failed to save credentials to file")
    
        # Save connection information in saved connections dict all stored as byte strings
        self._connections[connection_name] = {
            "host": host,
            "port": port,
            "username": username,
            "password": str(e_pass)
        } 
        return (True, "Successfully saved credentials")


    #! Hacky and bad - with more time this would be more secure and avoid using a single key for every encrypted field
    # Just use one key for all encryption, save it in data/key.txt
    def get_key(self):
        key = cryptography.fernet.Fernet.generate_key()
        filepath = os.path.join("data", "key.txt")
        if not(os.path.isfile(filepath)):
            with open(filepath, "wb") as file:
                file.write(key)
        else:
            with open(filepath, "rb") as file:
                key = file.read()
        return key

    # Encrypt using the key in key.txt
    def encrypt(self, str):
        key = self.get_key()
        encryptor = cryptography.fernet.Fernet(key)
        b_str = str.encode('utf-8')
        encrypted = encryptor.encrypt(b_str)
        return encrypted

    # Decrypt using the key in key.txt
    def decrypt(self, e_str):
        key = self.get_key()
        decryptor = cryptography.fernet.Fernet(key)
        field = decryptor.decrypt(e_str)
        return field
