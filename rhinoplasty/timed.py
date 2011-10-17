"""Functions for timing tests."""

from nose.tools import TimeExpired
from threading import Event
from threading import Thread
from .wrapper import wrap_test_function
import sys


# Limit A Test's Duration
# -----------------------
def timeboxed(max_time):
    """Decorator to limit how long a test will run for.
    
    @param max_time: The maximum number of seconds the test is allowed to run
        for.
    @raise TimeExpired If the test runs too long. Nose will treat this as a
        test failure, rather than an error.
    @see nose.tools.timed for an alternative approach. The difference is that
        this decorator will not allow the test function to run any longer than
        the specified time limit, whereas Nose's version will wait until the
        test function finishes (however long that takes) before failing.
    """
    #FIXME check max explicitly, rather than waiting for func execution
    
    def decorate(func):
        @wrap_test_function(func)
        def new_func(*args, **kwargs):
            # Create a separate thread to run the function in.
            # 
            # Because we could decorate any arbitrary function, we do not have
            # any control over it's execution. Hence we need to run the
            # function in parallel, so that if it exceeds the allocated time
            # we can abandon it and return from the original thread of
            # execution. 
            # 
            # The multiprocessing module would provide some useful features
            # (such as the ability to terminate the target function if it runs
            # too long), but we can't use it because that would change the
            # execution environment for the target function.
            target = _TimeoutFunctionThread(lambda : func(*args, **kwargs))
            target.start()
            
            # Wait for the target function to finish executing, or else reach
            # it's time limit
            if not target.finished.wait(max_time):
                raise TimeExpired("%s could not be run within %s seconds" % (func.__name__, max_time))
            assert target.finished.is_set()
            
            # Return result for original function
            return target.get_result()
        
        return new_func
    
    return decorate


# Private Functions
# -----------------
class _TimeoutFunctionThread(Thread):
    """Run a function in a background thread and wait for it to complete..
    
    @param func: A parameter-less function to run.
    @see timeboxed
    """
    
    def __init__(self, func):
        Thread.__init__(self)
        
        # Event that is set when the function has finished executing
        self.finished = Event()
        
        # Target function to execute.
        #
        # The default Thread implementation will run a supplied function, but
        # it won't do anything with the result of the function. Hence we need
        # to completely replace this functionality.
        self.__target_func = func
        
        # Result from executing the target function. This is only valid when
        # the function has finished, and if an exception was not raised
        self.__result = None
        
        # Standard traceback data for an exception raised by the target
        # function (if any). This is only valid when the function has finished.
        self.__exc_info = None
        
        # Mark the thread as daemonic so that the Python process won't wait for
        # an overly long function to finish executing before exiting. This is
        # most relevant for running a single unit test.
        self.daemon = True
    
    def get_result(self):
        """Get the result from running the target function.
        
        @return The target function's return value.
        @raise Any unhandled exception caused by the target function. The
            original traceback will be preserved.
        """
        # Callers are supposed to wait for the function to complete before
        # getting the result.
        if not self.finished.is_set():
            raise StandardError("Target function has not finished executing yet")
        
        # Raise an exception or return the result, as relevant
        if self.__exc_info is None:
            return self.__result
        
        raise self.__exc_info[1], None, self.__exc_info[2]
    
    def run(self):
        self.finished.clear()
        
        try:
            self.__result = self.__target_func()
        except:
            self.__exc_info = sys.exc_info()
        
        self.finished.set()
