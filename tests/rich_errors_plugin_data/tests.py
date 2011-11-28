"""Suite of fake tests for exercising the rich error plugins module.

Note that these tests are not intended to be run separately, and do not form
part of the test suite for the Rhinoplasty package.
"""

from rhinoplasty.rich_errors import IrrelevantTestException

def test_that_passes():
    pass

def test_that_fails():
    assert False

def test_that_has_an_error():
    raise ValueError("Stars are not aligned")

def test_that_has_rich_error():
    raise IrrelevantTestException("Just because")
