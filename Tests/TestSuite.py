#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# TestSuite.py
#
# Suite for testing BibleOrgSys
#   Last modified: 2011-01-21 (also update versionString below)
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
versionString = "0.02"


import unittest

import BibleBooksCodesTest, BibleBookOrdersTest


# Create the test suite
suiteList = []
suite1 = unittest.TestLoader().loadTestsFromTestCase( BibleBooksCodesTest.BibleBooksCodesTests ); suiteList.append( suite1 )
suite2 = unittest.TestLoader().loadTestsFromTestCase( BibleBookOrdersTest.BibleBookOrderSystemsTests ); suiteList.append( suite2 )
suite3 = unittest.TestLoader().loadTestsFromTestCase( BibleBookOrdersTest.BibleBookOrderSystemTests ); suiteList.append( suite3 )
allTests = unittest.TestSuite( suiteList )


# Now run all the tests
unittest.TextTestRunner(verbosity=2).run( allTests )


# end of TestSuite.py
