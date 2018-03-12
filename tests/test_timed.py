"""Unit tests for the rhinoplasty.timed module."""

from nose.tools import assert_equal
from nose.tools import assert_greater_equal
from nose.tools import assert_raises
from nose.tools import TimeExpired
from rhinoplasty.timed import timeboxed
import random
import time


class TestTimeBoxedDecorator(object):
    """Test decorator that times out a method if it takes too long."""
    
    # Test Methods
    # ------------
    def test_function_with_no_parameters(self):
        """Should be able to decorate a function that accepts no parameters."""
        # Setup
        value = random.randint(0, 100000)
        
        @timeboxed(1)
        def func():
            return value
        
        # Exercise
        assert_equal(value, func())
    
    def test_function_with_multiple_parameters(self):
        """Should be able to decorate a function that accepts sequential and
        keyword  parameters.
        """
        # Setup
        value_a = random.randint(0, 100000)
        value_b = random.randint(0, 100000)
        expected_result = "%s_%s" % (value_a, value_b)
        
        @timeboxed(1)
        def func(a, b):
            return "%s_%s" % (a, b)
        
        # Exercise
        assert_equal(expected_result, func(value_a, b=value_b))
    
    def test_timeout_triggered(self):
        """A function that runs too long should trigger a timeout error."""
        # Setup
        value = random.randint(0, 100000)
        
        @timeboxed(0.01)
        def run_long_method(param):
            time.sleep(10)
            return param
        
        # Exercise
        with assert_raises(TimeExpired):
            run_long_method(value)
    
    def test_timeout_avoided(self):
        """A function that doesn't take too long should work normally."""
        # Setup
        value = random.randint(0, 100000)
        
        @timeboxed(1)
        def func(param):
            return param
        
        # Exercise
        result = func(value)
        
        # Verify
        assert_equal(result, value, "Short run failed to return correct result")
    
    def test_exception_raised(self):
        """An exception raised by the target function should be passed through to the caller."""
        # Setup
        class FrobnicationError(Exception):
            pass
        
        @timeboxed(1)
        def func():
            raise FrobnicationError()
        
        # Exercise
        with assert_raises(FrobnicationError):
            func()
    
    #FIXME turn test function into a generator
#    @parametrise.function([
#        0.02,
#        0.2,
#        2,
#    ])
#    def test_timeout_length(self, time_period):
    def test_timeout_length(self):
        """The time out should not occur until the time period has elapsed."""
        # Setup
        time_period = 0.2
        
        @timeboxed(time_period)
        def func():
            time.sleep(time_period*5)
        
        # Exercise
        start = time.time()
        with assert_raises(TimeExpired):
            func()
        end = time.time()
        
        # Verify
        test_duration = end - start
        assert_greater_equal(test_duration, time_period)


