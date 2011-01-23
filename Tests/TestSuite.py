#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# TestSuite.py
#
# Suite for testing BibleOrgSys
#   Last modified: 2011-01-22 (also update versionString below)
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

progName = "Bible Organisational System test suite"
versionString = "0.03"


import sys, unittest


sourceFolder = "."
sys.path.append( sourceFolder )

import Globals
import BibleBooksCodesTest, BibleBookOrdersTest


# Handle command line parameters (for compatibility)
from optparse import OptionParser
parser = OptionParser( version="v{}".format( versionString ) )
parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML files to .py and .h tables suitable for directly including into other programs")
Globals.addStandardOptionsAndProcess( parser )

if Globals.verbosityLevel > 1: print( "{} V{}".format( progName, versionString ) )


# Create the test suite
suiteList = []
suite1 = unittest.TestLoader().loadTestsFromTestCase( BibleBooksCodesTest.BibleBooksCodesTests ); suiteList.append( suite1 )
suite2 = unittest.TestLoader().loadTestsFromTestCase( BibleBookOrdersTest.BibleBookOrderSystemsTests ); suiteList.append( suite2 )
suite3 = unittest.TestLoader().loadTestsFromTestCase( BibleBookOrdersTest.BibleBookOrderSystemTests ); suiteList.append( suite3 )
allTests = unittest.TestSuite( suiteList )


# Now run all the tests in the suite
unittest.TextTestRunner(verbosity=2).run( allTests )


# end of TestSuite.py
