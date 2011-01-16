#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# TestSuite.py
#
# Suite for testing BibleOrgSys
#   Last modified: 2011-01-15 (also update versionString below)
#
# Copyright (C) 2011 Robert Hunt
# Author: Robert Hunt <robert316@users.sourceforge.net>
# License: See gpl-3.0.txt
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Suite testing BibleOrgSys.
"""

progName = "Bible Org Sys test suite"
versionString = "0.01"


import unittest

import BibleBooksCodesTest


# Create the test suite
suite = unittest.TestLoader().loadTestsFromTestCase(BibleBooksCodesTest.BibleBooksCodesTests)

# Now run all the tests
unittest.TextTestRunner(verbosity=2).run(suite)

# end of TestSuite.py
