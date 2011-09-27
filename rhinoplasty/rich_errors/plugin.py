"""Nose plugin for displaying results from rich errors."""

#TODO add priority to the plugin, so that it hadnles errors before the standard Skip plugin (in case that is not disabled). i think you need to change the score

from nose.plugins.errorclass import ErrorClass, ErrorClassPlugin
from _errors import *

class RichErrorPlugin(ErrorClassPlugin):
    """Plugin that installs error classes for all the rich errors defined in
    this package.
    """
    
    broken = ErrorClass(BrokenTestException, label='BROKEN', isfailure=True)
    excluded = ErrorClass(ExcludeTestException, label='XCLUDE', isfailure=False) #TODO better label
    misconfigured = ErrorClass(InvalidTestConfigurationException, label='CONFIG_WRONG', isfailure=False) #TODO better label
    irrelevant = ErrorClass(IrrelevantTestException, label='IRRELEVANT', isfailure=False)
    
    