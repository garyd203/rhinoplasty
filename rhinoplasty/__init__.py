"""Experimental extensions to Nose."""

import re

## Version Information ##

# Version string
from _version import __version__

# Version tuple
version_info = tuple(map(int, re.match("(\d+)\.(\d+)\.(\d+)", __version__).groups()))