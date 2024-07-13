import paramiko
from paramiko.ssh_exception import SSHException, AuthenticationException
import LogHandler
from LogHandler import setup_logger
import os
import sys

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
            1: lambda: self._copy_constructor(*args),  # Wrap the call in a lambda to pass args
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

         # Initialize connection objects
        self._transport = None
        self._SFTP = None


    #Copy constructor
    def _copy_constructor(self,to_copy):

        #Copy constructor object to copy from must be of type SFTP.
        if type(to_copy) != SFTP: 
            raise ValueError("Type of to_copy is not SFTP in copy constructor")

        # Store & initialize connection parameters connection parameters
        self._port = to_copy._port 
        self._host = to_copy._host
        self._username = to_copy._username
        self._password = to_copy._password

         # Initialize connection objects
        self._transport = to_copy._transport
        self._SFTP = to_copy._SFTP



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


    def connect(self):

        try:
            self._debug_logger.debug(f"Connecting to {self._host}:{self._port}")
            self._transport = paramiko.Transport((self._host, self._port))
            
            self._debug_logger.debug(f"Authenticating with username: {self._username}")
            self._transport.connect(None, self._username, self._password)
            
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
            raise
        except SSHException as e:
            stage = "transport creation" if self._transport is None else "SFTP client creation"
            self._debug_logger.error(f"Failed during {stage}: {str(e)}")
            if self._transport:
                self._transport.close()
            raise
        except Exception as e:
            self._debug_logger.error(f"Unexpected error during SFTP connection: {str(e)}")
            if self._transport:
                self._transport.close()
            raise

        return "Connection Successful"



    #Lists the contents of the current directory on the remote server.
    def list_directory(self):
        if self._SFTP is None:
            print("Not connected to an SFTP server.")
            return
        
        try:
            # Assuming self._SFTP is an instance of paramiko.SFTPClient
            directory_contents = self._SFTP.listdir()
            for item in directory_contents:
                print(item)
        except IOError as e:
            print(f"Failed to list directory: {e}")


    # Download from source_path on the remote server to destination_path on the local machine
    def download(self, source_path, destination_path):
        self.print_debug(f"Operating System: {sys.platform}", None, True) # Debug info for operating system
        
        # Maps the result of sys.platform to different delimiters for the path - necessary since windows uses \\ and linux/mac use / 
        platform_map = {
            "win32": "\\",
            ("linux") or ("linux2"): "/",
            "darwin": "/"
        }
        delim = platform_map[sys.platform]

        try:
            source_tok = source_path.split('/') # Tokenize the source_path string to get the filename
            if (destination_path == ''):
                local = os.getcwd() + delim + source_tok[-1]  # Null entry from user - get current working directory, 
                                                                # add the appropriate slash to it (delim), 
                                                                # and get the name of the download file (source_tok[-1] is the last item in the source_path)
            else:
                local = destination_path + delim + source_tok[-1] # Otherwise user has to specify the filename when entering the path
            self._SFTP.get(source_path, local) # All pa
            self.print_debug(f"Successfully downloaded {source_tok[-1]} to {local}", None, True) 
        except Exception as e:
            self.print_error(f"Failed to download file {source_tok[-1]} to {local}", e, True)


    def print_debug(self, message, e, out):
        if (e == None):
            if (out == True):
                print(message)
            self._debug_logger.debug(f"{message}")
        else:
            if (out == True):
                print(message)
            self._debug_logger.debug(f"{message} : {e}")
        
    
    def print_error(self, message, e, out):
        if (e == None):
            if (out == True):
                print(message)
            self._debug_logger.error(f"{message}")
        else:
            if (out == True):
                print(message)
            self._debug_logger.error(f"{message} : {e}")
        