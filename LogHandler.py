import logging
import os

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

        path = os.path.join(os.path.dirname(__file__), filename)
        # Store the filename as an instance variable
        if  os.path.isfile(filename):
            os.remove(filename)

        self.filename = filename

    # Define the emit method, which is called for each log record
    def emit(self, record):
        # Check if the log level is DEBUG or ERROR
        if record.levelno in [logging.DEBUG, logging.ERROR]:
            # Open the file in append mode
            with open(self.filename, 'a') as f:
                # Write the formatted log record to the file, followed by a newline
                f.write(self.format(record) + '\n')




# Define a function to set up a logger
def setup_logger(name, log_file):
    # Create a logger with the given name
    logger = logging.getLogger(name)
    # Set the logger's minimum level to DEBUG
    logger.setLevel(logging.DEBUG)

    # Create a formatter for log messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%H:%M:%S")

    # Create an instance of our custom DebugErrorHandler
    debug_error_handler = DebugErrorHandler(log_file)
    # Set the formatter for this handler
    debug_error_handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(debug_error_handler)
    
    # Return the configured logger
    return logger