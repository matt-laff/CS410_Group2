import paramiko
from paramiko.ssh_exception import SSHException, AuthenticationException
import sys
import os
from .log_handler import setup_logger

DEFAULT_PORT = 22

class SFTP:

    #Returns a string representation of the connection details: port, host, and username.
    def __str__(self):
        return f"Port: {self._port}, Host: {self._host}, Username: {self._username}"

    #init method used to call proper constructor
    def __init__(self, *args):

        #logger that only captures debug messages, errors, and raised values
        self._debug_logger = setup_logger('sftp_logger', 'SFTP_debug_error.log')
        self._debug_logger.debug("New SFTP Instance Created")
        #Calculate the number of arguments passed to the initializer. Will use as key for constructor calling.
        arg_len = len(args)


        # Action_map is a dictionary that maps the number of arguments (arg_len) to specific functions.
        # This allows us to dynamically choose which function to execute based on the number of arguments.
        action_map = {
            0: self._default_constructor(),
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

        #Close open SFTP client
        if self._SFTP != None: 
            self._SFTP.close()

        #Close open transport
        if self._transport != None:
            self._transport.close()

        #Security: set connect objects to NUll
        self._transport = None
        self._SFTP = None

        # Download path
        self._download_location = None

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


        #TODO: BadAuthenticationType???? 
        #TODO: GENERIC EXCPEITON HANDLING
        #! HOW ARE WE NOT CATCHING AN ERROR WITH THE CATCH ALL ----- UNDERSTADN---- "EXEPTION CHAINING"


        except AuthenticationException as e:
            self._debug_logger.error(f"Authentication failed: {str(e)}")
            if self._transport:
                self._transport.close()
            
            self._transport = None
            self._SFTP = None

            return False, (f"Authentication failed: {str(e)}")

        except Exception as e:
            self._debug_logger.error(f"Unexpected error during SFTP connection: {str(e)}")
            if self._transport:
                self._transport.close()

            self._transport = None
            self._SFTP = None

            return False,(f"Unexpected error during SFTP connection: {str(e)}")

        return True,"Connection Successful"



    #Lists the contents of the current directory on the remote server.
    def list_directory(self):
        if self._SFTP is None:
            return (False, ("Not connected to an SFTP server"))
        
        try:
            # Assuming self._SFTP is an instance of paramiko.SFTPClient
            directory_contents = self._SFTP.listdir()
            for item in directory_contents:
                print(item)
        except IOError as e:
            return (False , (f"Failed to list directory: {e}"))
        
        return True

    # Changes the permissions of a file or directory on the remote server
    def change_permissions(self, remote_path, mode):
        try:
            # Ensure self._SFTP is initialized and connected
            if self._SFTP is None:
                return (False, ("Not connected to an SFTP server"))

            # Change the permissions
            # Use chmod method of SFTPClient instance to change the permissions of a file/directory on the remote server
            self._SFTP.chmod(remote_path, mode)

            print(f"Permissions changed for {remote_path}")
            return True

        except IOError as e:
            return ( False, (f"Failed to change permissions for {remote_path}: {e}"))
        


    def list_full(self):
        if self._SFTP is None:
            self.print_debug("Not connected to a server, list_full() failed", None, False) 
            return
        
        try:
            directory_contents = self._SFTP.listdir_attr()
            for item in directory_contents:
                print(item)
        except IOError as e:
            print(f"Failed to list directory: {e}")


    def download_all(self, remote_path_list, local_path_list):
        success = False
        if (len(local_path_list) == 0): # Empty local path, default to current directory
            self.print_debug("Empty local_path_list, building local_path", None, False)
            for path in remote_path_list:
                local_path = self.remote_to_local(path)
                self.print_debug(f"Local path: {local_path}", None, False)
                success = self.download(path, local_path)
        elif (len(local_path_list) == len(remote_path_list)):
            for remote_path, local_path in zip(remote_path_list, local_path_list):
                success = self.download(remote_path, local_path)
        return success


    # Download from source_path on the remote server to destination_path on the local machine
    def download(self, source_path, destination_path):
        try:
            self._SFTP.get(source_path, destination_path)
            self.print_debug(f"Successfully downloaded {source_path} to {destination_path}", None, True) 
            return True
        except Exception as e:
            if (os.path.isfile(destination_path)):
                os.remove(destination_path)
            self.print_error(f"Failed to download file {source_path} to {destination_path}", e, True)
            return False

    # Remove the directory at the remote path
    def rmdir(self, remote_path):
        try:
            self._SFTP.rmdir(remote_path)
            self.print_debug(f"Successsfully removed directory at {remote_path}")
        except Exception as e:
            self.print_error(f"Failed to remove directory at {remote_path}", e)
    
    # Copy a local file (local_path) to the SFTP server as remote_path
    def put(self, local_path, remote_path):
        try:
            self._SFTP.put(local_path, remote_path)
            self.print_debug(f"Successfully copied {local_path} to {remote_path}")
        except Exception as e:
            self.print_error(f"Failed to copy {local_path} to {remote_path}")

    def set_download_location(self, download_path):
        try:
            self._download_location = download_path
            assert(os.path.isdir(download_path))
            self._debug_logger.debug(f"Successfully set download location: {e}")
        except Exception as e:
            self._debug_logger.debug(f"Failed to set download location: {e}")


    # Helper function to convert remote formatting to local system formatting
    def remote_to_local(self, remote_path):
        self.print_debug(f"Operating System: {sys.platform}", None, True) # Debug info for operating system
        
        # Maps the result of sys.platform to different delimiters for the path - necessary since windows uses \\ and linux/mac use / 
        platform_map = {
            "win32": "\\",
            ("linux") or ("linux2"): "/",
            "darwin": "/"
        }
        delim = platform_map[sys.platform]

        try:
            source_tok = remote_path.split('/') # Tokenize the source_path string to get the filename

            if (self._download_location != None): 
                local_path = self._download_location + delim + source_tok[-1] 
            else:
                local_path = os.getcwd() + delim + source_tok[-1] 
            
            self._debug_logger.debug(f"Remote path from remote_to_local(): {remote_path}")
            self._debug_logger.debug(f"Local path from remote_to_local(): {local_path}")
            return local_path

        except Exception as e:
            self.print_error(f"Failed to download file {source_tok[-1]} to {local_path}", e, True)
            return None


    def print_debug(self, message, e = None, out = True):
        if (e == None):
            if (out == True):
                print(message)
            self._debug_logger.debug(f"{message}")
        else:
            if (out == True):
                print(message)
            self._debug_logger.debug(f"{message} : {e}")
        
    
    def print_error(self, message, e, out = True):
        if (e == None):
            if (out == True):
                print(message)
            self._debug_logger.error(f"{message}")
        else:
            if (out == True):
                print(message)
            self._debug_logger.error(f"{message} : {e}")
        
