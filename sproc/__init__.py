#!/usr/bin/env python

"""
init stuff
"""

__version__ = "0.0.1"

import sproc.fetch
import sproc.jsonify
import sproc.imap
import sproc.smap
from sproc.newsproc import Sproc
from sproc.helpers import set_loglevel

set_loglevel("INFO")
