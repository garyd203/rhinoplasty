"""Unit tests for the rhinoplasty.timed module."""

from nose.tools import assert_equal
from nose.tools import assert_greater_equal
from nose.tools import assert_raises
from nose.tools import TimeExpired
from rhinoplasty.timed import timeboxed
import random
import time
#FIXME from xtest import parametrise


class TestTimeBoxedDecorator(object):
    """Test decorator that times out a method if it takes too long."""
    
    #TODO tests:
        # accept no args, sequential args, keyword args
        # raise exception
    
    # Test Methods
    # ------------
    def test_timeout_triggered(self):
        """A function that runs too long should trigger a timeout error."""
        value = random.randint(0, 100000)
        
        with assert_raises(TimeExpired):
            self._run_long_method(value)
    
    def test_timeout_avoided(self):
        """A function that doesn't take too long should work normally."""
        value = random.randint(0, 100000)
        
        result = self._run_short_method(value)
        
        assert_equal(result, value, "Short run failed to return correct result")
    
    #FIXME turn test function into a generator
#    @parametrise.function([
#        0.01,
#        0.1,
#        1
#    ])
#    def test_timeout_length(self, time_period):
    def test_timeout_length(self):
        """The time out should not occur until the time period has elapsed."""
        # Setup
        time_period = 1
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
    
    
    # Helper Methods
    # --------------
    #TODO put these as local funcs
    @timeboxed(0.01)
    def _run_long_method(self, value):
        time.sleep(10)
        return value
    
    @timeboxed(1)
    def _run_short_method(self, value):
        return value


