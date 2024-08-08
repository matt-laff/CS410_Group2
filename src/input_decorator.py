import builtins  # Import built-in objects module
import threading  # Import threading module for concurrent execution
import functools  # Import functools for higher-order functions
import os

#Custom exception for input timeout
class InputTimeoutError(Exception):
    pass

def reset_input_history():

    os.path.join(os.path.dirname(__file__), "input_history.log")
    if  os.path.isfile("input_history.log"):
        os.remove("input_history.log")


def input_with_timeout(timeout=10): #define the timeout paramaters

    def decorator(func):  # Define Decorator and pass the function whose behavior to agment ->input

        @functools.wraps(func)  # Preserve metadata/behavior of the original functions behavior ->input()

        # Define wrapper function
        def wrapper(*args, **kwargs):#[*args, **kwargs]: syntaxes that allow  functions to accept any # of positional  and keyword args


            #~~~~~~INPUT LOGIC~~~~~~#

            def input_thread(result):  # Define funciton to capture inputs() r-value

                result['value'] = func(*args, **kwargs)  # Call original input function and caputre return
                result['received'] = True  # Set flag that input was received to TRUE if input actually happend before timemout

            #~~~~~~~~~~~~~~~~~~~~~~~#
            
            #Start of the wrapper and true logical function execution start
            result = {'value': None, 'received': False}  # Initialize result dictionary in wrapper


            #~~~~~~THREAD LOGIC~~~~~~#

            #Create a separate thread for handling user input, allowing main thread to continue execution and implement a timeout mechanism
            thread = threading.Thread(target=input_thread, args=(result,))

             # Set thread as daemon..its now subserviant as Non-daemon threads..ie the thread we in
            thread.daemon = True  #If we dont make it a daemon, then it will prevent the program from exiting until the thread we
            #just created completes execution.  The main program will not exit until all non-daemon threads have finished. (other
            #exceptions will cause the program to hang then too). This is not what we want as the timeout thread should close if
            #we reach a certain time in the programs life

            thread.start()  # Start the input thread

            thread.join(timeout)  # Wait for thread to complete or timeout.. as we always join threads back together

            #~~~~~~~~~~~~~~~~~~~~~~~#


            if not result['received']:  # Check if input was received
                raise InputTimeoutError("Input timed out")  # Raise timeout exception if no input

            else:
                with open("input_history.log", 'a') as f:
                    # Write the formatted log record to the file, followed by a newline
                    f.write(result['value'] + '\n')

                return result['value']  # Return the input value

        return wrapper  # Return the wrapper function

    return decorator  # Return the decorator