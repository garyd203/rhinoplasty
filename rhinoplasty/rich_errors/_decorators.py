"""Decorators for applying rich exceptions."""

#TODO helper decorators for all exceptions
    # broken_test
    # exclude_test
    # irrelevant_test

#TODO update docstrings
#TODO read through all code and update it
#TODO rename decorators to be clearer, and have some systematic nameing approach


__all__ = [
    'broken',
    'broken_inherited_tests',
    'irrelevant',
]


from ._errors import BrokenTestException
from ._errors import IrrelevantTestException
from nose.tools import nottest
from rhinoplasty.wrapper import wrap_test_fixture
import inspect


@nottest
def broken_test(arg):
    """Decorator to mark that this test case or test suite is broken.
    
    This decorator may be used without arguments, or else it accepts a single
    string argument describing why the test fails. Examples:
    
    @see BrokenTestException for further information on usage.
    """
    #TODO see unittest.expectedFailure (note this is only for functions). Also, it's API is not currently supported by Nose.
    
    # Allow for two different decoration options
    arg_is_fixture = True
    description = "Test is known to fail"
    
    if isinstance(arg, basestring):
        description = arg
        arg_is_fixture = False
    
    # Get the wrapper function for the test fixture
    func = _get_skip_test_decorator(description, BrokenTestException)
    
    # Decorate the fixture
    if arg_is_fixture:
        return func(arg)
    return func


@nottest
def broken_inherited_tests(reason, *functions):
    """Decorator to mark that some test cases inherited from a superclass
    are broken.
    
    @param reason: Description of why the test is failing.
    @param functions: List of function names, provided as additional arguments
        to the decorator.
    @see BrokenTestException for further information on usage.
    """
    def decorate(TestClass):
        # Sanity checks
        if not inspect.isclass(TestClass):
            raise TypeError("@failing_virtual_tests must be applied to a class")
        
        if hasattr(TestClass, reason):
            raise ValueError("Failure reason appears to actually be a method: '%s'" % reason)
        
        # Mark these tests for this subclass only.
        # The only way to do this is to overwrite the method on the subclass,
        # and mark the overwritten method as a failure.
        for funcname in functions:
            # Check that we have a reference to a valid superclass method
            for SuperClass in inspect.getmro(TestClass):
                if hasattr(SuperClass, funcname):
                    original_function = getattr(SuperClass, funcname)
                    break
            else:
                raise ValueError("Test method '%s' is not defined by any superclass of %s" % (funcname, TestClass))
            
            # Create a replacement function
            @broken_test(reason)
            @wrap_test_fixture(original_function)
            def new_method(self):
                bound_function = original_function.__get__(self, TestClass)
                bound_function()
            
            setattr(TestClass, funcname, new_method)
        
        return TestClass
    
    return decorate


@nottest
def irrelevant_test(condition, description):
    """Decorator to mark that this test fixture is irrelevant under certain
    conditions.
    
    This allows the test to be skipped (or otherwise handled specially).
    """
    assert (isinstance(description, basestring)), "Description is not a string - check that the parameters are correct"
    
    if condition:
        # Skip the test fixture
        decorate = _get_skip_test_decorator(description, IrrelevantTestException)
    else:
        # Leave the decorated fixture unchanged.
        def decorate(fixture):
            return fixture
    
    return decorate


@nottest
def _get_skip_test_decorator(description, SkipExceptionClass):
    """Decorator helper to get a wrapper function for a test fixture, that will
    skip the fixture.
    
    @param description: Description for why the decorated object is skipped.
    @param SkipExceptionClass: The exception class to raise.
    """
    #TODO move to helper module?
    #TODO rename
    def decorate(fixture):
        if inspect.isclass(fixture):
            # Create a replacement class that raises an appropriate exception
            @wrap_test_fixture(fixture)
            class ClassWrapper(object):
                def test_suite_has_been_skipped(self):
                    raise SkipExceptionClass(description)
                test_suite_has_been_skipped.__doc__ = fixture.__doc__
            
            return ClassWrapper
                    
        elif callable(fixture):
            # Create a replacement function that raises an appropriate exception
            
            #noinspection PyUnusedLocal
            @wrap_test_fixture(fixture)
            def function_wrapper(*args):
                """Replaces the failing test and unconditionally skips the test."""
                raise SkipExceptionClass(description)
            return function_wrapper
        else:
            raise ValueError("Decorated object is neither a class nor a function")
    
    return decorate
