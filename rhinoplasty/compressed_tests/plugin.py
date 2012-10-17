"""A lazy developer hasn't written a proper module docstring."""

from nose.plugins.base import Plugin
import logging

logger = logging.getLogger("rhinoplasty.archives")


class CompressedTestLoaderPlugin(Plugin):
    """Nose plugin that loads tests from a compressed file
    (such as a zipfile).
    """
    
    # Standard Plugin attributes
    name = "load-zipfile"
    
    # Use default implementation of options() and configure to enable this plugin
    
    def help(self):
        return "Load tests from a zipfile or other compressed file."
    
    #TODO implement loading override
