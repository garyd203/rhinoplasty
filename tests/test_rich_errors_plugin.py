"""Integration tests for the rhinoplasty.rich_errors.plugin module."""

#TODO these tests need to be run in a separate process

from cStringIO import StringIO
from nose.config import Config
from nose.core import TestProgram
from nose.plugins.manager import PluginManager
from nose.tools import assert_equals
from xml.dom.minidom import parse as dom_parse
import nose.plugins.xunit
import os
import rhinoplasty.rich_errors.plugin
import shutil
import tempfile

class TestXunitPluginPatch(object):
    """Test how the rich errors plugin interacts with the xunit plugin."""
    
    # Test Fixture
    # ------------
    @classmethod
    def setup_class(cls):
        cls.fake_tests = os.path.join(os.path.dirname(__file__),
                                      "rich_errors_plugin_data")
        cls.plugin_classes = [
            nose.plugins.xunit.Xunit,
            rhinoplasty.rich_errors.plugin.RichErrorReportingPlugin,
        ]
    
    
    # Test Cases
    # ----------
    def test_xunit_without_rich_errors(self):
        """Verify xunit output when rich errors plugin is disabled."""
        # Setup
        xunit_output_dir = tempfile.mkdtemp()
        xunit_output = os.path.join(xunit_output_dir, "nosetests.xml")
        
        # Exercise
        self._run_nose("--with-xunit", "--xunit-file=" + xunit_output)
        
        # Verify
        self._verify_xunit_output(xunit_output, 4, 2, 1, 0)
        
        # Teardown
        shutil.rmtree(xunit_output_dir)
    
    def test_xunit_with_rich_errors(self):
        """Verify xunit output when rich errors plugin is enabled."""
        # Setup
        xunit_output_dir = tempfile.mkdtemp()
        xunit_output = os.path.join(xunit_output_dir, "nosetests.xml")
        
        # Exercise
        self._run_nose("--with-rich-errors",
                       "--with-xunit", "--xunit-file=" + xunit_output
        )
        
        # Verify
        self._verify_xunit_output(xunit_output, 4, 1, 1, 1)
        
        # Teardown
        shutil.rmtree(xunit_output_dir)
    
    def test_rich_errors_without_xunit(self):
        """Verify rich errors plugin still works when xunit is disabled."""
        self._run_nose("--with-rich-errors")
    
    
    # Helper Methods
    # --------------
    def _run_nose(self, *args):
        """Run Nose with the supplied arguments.
        
        @param args: A list of command line arguments for Nose. This should
            not include the nose command, or a test suite.
        @return A file-like object wrapping the output from Nose. 
        """
        # Setup command line arguments
        argv = ["nosetests"]
        argv.extend(args)
        argv.append(self.fake_tests)
        
        # Setup Nose
        stream = StringIO()
        plugins = [PluginClass() for PluginClass in self.plugin_classes]
        config = Config(stream=stream,
                      plugins=PluginManager(plugins=plugins))
            
        self.nose = TestProgram(argv=argv, config=config, exit=False)
        
        # Return output
        stream.flush()
        stream.seek(0)
        return stream
    
    def _verify_xunit_output(self, filename, tests, errors, failures, skips):
        """Verify that the xunit file contains the expected number of tests."""
        dom = dom_parse(filename)
        
        assert_equals(tests, int(dom.documentElement.getAttribute("tests")),
                      "Incorrect total number of tests"
        )
        assert_equals(errors, int(dom.documentElement.getAttribute("errors")),
                      "Incorrect number of errors"
        )
        assert_equals(failures, int(dom.documentElement.getAttribute("failures")),
                      "Incorrect number of failed tests"
        )
        assert_equals(skips, int(dom.documentElement.getAttribute("skip")),
                      "Incorrect number of skipped tests"
        )
