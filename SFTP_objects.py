#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#         ~ Imports ~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

import paramiko
from paramiko.ssh_exception import SSHException, AuthenticationException

import logging


# TODO: DECORATORS / OPERATORS
# TODO: RE-WORK



######################################################
#
#SFTP (Secure File Transfer Protocol) class
#
######################################################


# Define a custom logging handler class that inherits from logging.Handler
class DebugErrorHandler(logging.Handler):
    # Initialize the handler with a filename
    def __init__(self, filename):
        # Call the parent class's __init__ method
        super().__init__()
        # Store the filename as an instance variable
        self.filename = filename

    # Define the emit method, which is called for each log record
    def emit(self, record):
        # Check if the log level is DEBUG or ERROR
        if record.levelno in [logging.DEBUG, logging.ERROR]:
            # Open the file in append mode
            with open(self.filename, 'w') as f:
                # Write the formatted log record to the file, followed by a newline
                f.write(self.format(record) + '\n')




# Define a function to set up a logger
def setup_logger(name, log_file):
    # Create a logger with the given name
    logger = logging.getLogger(name)
    # Set the logger's minimum level to DEBUG
    logger.setLevel(logging.DEBUG)

    # Create a formatter for log messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create an instance of our custom DebugErrorHandler
    debug_error_handler = DebugErrorHandler(log_file)
    # Set the formatter for this handler
    debug_error_handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(debug_error_handler)
    
    # Return the configured logger
    return logger




class SFTP:

    #Returns a string representation of the connection details: port, host, and username.
    def __str__(self):
        return f"Port: {self._port}, Host: {self._host}, Username: {self._username}"

    #init method used to call proper constructor
    def __init__(self, *args):

        #logger that only captures debug messages, errors, and raised values
        self._debug_logger = setup_logger('sftp_logger', 'SFTP_debug_error.log')

        #Calculate the number of arguments passed to the initializer. Will use as key for constructor calling.
        arg_len = len(args)


        # Action_map is a dictionary that maps the number of arguments (arg_len) to specific functions.
        # This allows us to dynamically choose which function to execute based on the number of arguments.
        action_map = {
            0: self._default_constructor,
            1: lambda: self._copy_constructor(*args),  # Wrap the call in a lambda to pass args
            4: lambda: self._param_constructor(*args)  # Wrap the call in a lambda to pass args
        }

        #Call the appropriate constructor based on match.
        if arg_len in action_map:
            action_map[arg_len]()  # Now correctly passes args to _copy_constructor and _param_constructor
        #Cannot find correct argument, abort instansiation.
        else:
            raise ValueError("Invalid argument length when initializing SFTP build")


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
        if type(to_copy) != SFTP(): 
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
        self._port = port
        self._host = host
        self._username = username
        self._password = password

         # Initialize connection objects
        self._transport = None
        self._SFTP = None



    #function for connection to remote server
    def connect():

        #This function call tells paramiko to redirect all its logging output to a file named paramiko.log.
        #By default, this will capture all log messages regardless of their severity level (e.g., DEBUG, INFO, WARNING, ERROR).
        paramiko.util.log_to_file("paramiko.log")



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



#port host username password
sftp_obj_default = SFTP(22, "linux.cecs.pdx.edu", "farley", "")
print(sftp_obj_default)

print(sftp_obj_default.connect())
sftp_obj_default.list_directory()


