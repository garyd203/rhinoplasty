"""Integration tests for the rhinoplasty.rich_errors.plugin module."""

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


# Xunit Interaction
# =================
class TestXunitPluginPatch(object):
    """Test how the rich errors plugin interacts with the xunit plugin."""
    
    # Test Fixture
    # ------------
    @classmethod
    def setup_class(cls):
        cls.fake_tests = os.path.join(os.path.dirname(__file__),
                                      "rich_errors_plugin_data")
    
    
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
    
    
    # Helper Methods
    # --------------
    def _run_nose(self, *args):
        """Run Nose with the supplied arguments.
        
        @param args: A list of command line arguments for Nose. This should
            not include the nose command, or a test suite.
        """
        # Setup extra command line arguments
        args = list(args)
        args.append(self.fake_tests)
        
        # Run Nose in a separate process to avoid mangling the memory of this
        # process.
        from multiprocessing import Process
        p = Process(target=_run_fake_tests, args=tuple(args))
        p.start()
        p.join()
    
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


def _run_fake_tests(*args):
    """Helper function to run Nose with the supplied arguments.
    
    This should be called in a standalone process.
    """
    # Fudge command line arguments
    argv = ["nosetests"]
    argv.extend(args)
    
    # Setup plugins
    plugin_classes = [
        nose.plugins.xunit.Xunit,
        rhinoplasty.rich_errors.plugin.RichErrorReportingPlugin,
    ]
    plugins = [PluginClass() for PluginClass in plugin_classes]
    
    # Use a custom output stream, otherwise Nose will write to stderr for the
    # parent process
    stream = StringIO()
    
    # Run Nose
    config = Config(stream=stream,
                    plugins=PluginManager(plugins=plugins))
    TestProgram(argv=argv, config=config, exit=False)
