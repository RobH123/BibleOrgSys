#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleBooksCodesTest.py
#
# Module testing BibleBooksCodes.py
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
Module testing BibleBooksCodes.py.
"""

progName = "Bible Books Codes tests"
versionString = "0.03"


import sys, os.path
import unittest

sourceFolder = ".."
sys.path.append( sourceFolder )
import BibleBooksCodes


class BibleBooksCodesTests(unittest.TestCase):

    def setUp( self ):
        # Create the BibleBooksCodes object
        self.bbc = BibleBooksCodes.BibleBooksCodes().loadData( os.path.join( sourceFolder, "DataFiles/BibleBooksCodes.xml" ) ) # Doesn't reload the XML unnecessarily :)

    def test_isValidReferenceAbbreviation( self ):
        """ Test the isValidReferenceAbbreviation function. """
        self.assertTrue( self.bbc.isValidReferenceAbbreviation('GEN') )
        self.assertTrue( self.bbc.isValidReferenceAbbreviation('CO1') )
        self.assertTrue( self.bbc.isValidReferenceAbbreviation('REV') )
        self.assertFalse( self.bbc.isValidReferenceAbbreviation('XYZ') )
        self.assertFalse( self.bbc.isValidReferenceAbbreviation('Gen') )
    # end of test_isValidReferenceAbbreviation

    def test_getAllReferenceAbbreviations( self ):
        """ Test the getAllReferenceAbbreviations function. """
        results = self.bbc.getAllReferenceAbbreviations()
        self.assert_( isinstance( results, list ) )
        self.assert_( len(results) > 66 )
        for result in results: self.assert_( len(result)==3 )
    # end of test_getAllReferenceAbbreviations

    def test_getReferenceNumber( self ):
        """ Test the getReferenceNumber function. """
        self.assertEqual( self.bbc.getReferenceNumber('GEN'), 1 )
        self.assertEqual( self.bbc.getReferenceNumber('CO1'), 46 )
        self.assertEqual( self.bbc.getReferenceNumber('REV'), 66 )
        self.assertRaises( KeyError, self.bbc.getReferenceNumber, 'XYZ' )
        self.assertRaises( KeyError, self.bbc.getReferenceNumber, 'Gen' )
    # end of test_getReferenceNumber

    def test_getOSISAbbreviation( self ):
        """ Test the getOSISAbbreviation function. """
        self.assertEqual( self.bbc.getOSISAbbreviation('GEN'), 'Gen' )
        self.assertEqual( self.bbc.getOSISAbbreviation('CO1'), '1Cor' )
        self.assertEqual( self.bbc.getOSISAbbreviation('REV'), 'Rev' )
        self.assertRaises( KeyError, self.bbc.getReferenceNumber, 'XYZ' )
        self.assertRaises( KeyError, self.bbc.getReferenceNumber, 'Gen' )
    # end of getOSISAbbreviation

    def test_getSwordAbbreviation( self ):
        """ Test the getSwordAbbreviation function. """
        self.assertEqual( self.bbc.getOSISAbbreviation('GEN'), 'Gen' )
        self.assertEqual( self.bbc.getOSISAbbreviation('CO1'), '1Cor' )
        self.assertEqual( self.bbc.getOSISAbbreviation('REV'), 'Rev' )
        self.assertRaises( KeyError, self.bbc.getReferenceNumber, 'XYZ' )
        self.assertRaises( KeyError, self.bbc.getReferenceNumber, 'Gen' )
    # end of getSwordAbbreviation

    def test_getExpectedChaptersList( self ):
        """ Test the getSingleChapterBooksList function. """
        self.assertEqual( self.bbc.getExpectedChaptersList('GEN'), ['50'] )
        self.assertEqual( self.bbc.getExpectedChaptersList('CO1'), ['16'] )
        self.assertEqual( self.bbc.getExpectedChaptersList('REV'), ['22'] )
        self.assertRaises( KeyError, self.bbc.getExpectedChaptersList, 'XYZ' )
        self.assertRaises( KeyError, self.bbc.getExpectedChaptersList, 'Gen' )
    # end of test_getExpectedChaptersList

    def test_getSingleChapterBooksList( self ):
        """ Test the getSingleChapterBooksList function. """
        results = self.bbc.getSingleChapterBooksList()
        self.assert_( isinstance( results, list ) )
        self.assert_( 10 < len(results) < 20 ) # Remember it includes many non-canonical books
        for BBB in ('OBA','PHM','JN2','JN3','JDE',): self.assert_( BBB in results )
    # end of test_getSingleChapterBooksList

    def test_getOSISSingleChapterBooksList( self ):
        """ Test the getOSISSingleChapterBooksList function. """
        results = self.bbc.getOSISSingleChapterBooksList()
        self.assert_( isinstance( results, list ) )
        self.assert_( 10 < len(results) < 20 ) # Remember it includes many non-canonical books
        for BBB in ('Obad','Phlm','2John','3John','Jude',): self.assert_( BBB in results )
    # end of test_getOSISSingleChapterBooksList

    def test_getAllParatextBooksCodeNumberTriples( self ):
        """ Test the getAllParatextBooksCodeNumberTriples function. """
        results = self.bbc.getAllParatextBooksCodeNumberTriples()
        self.assert_( isinstance( results, list ) )
        self.assert_( 66 <= len(results) < 120 ) # Remember it includes many non-canonical books
        for resultTuple in results:
            self.assert_( len(resultTuple)== 3 )
            self.assert_( len(resultTuple[0]) == 3 )
            self.assert_( len(resultTuple[1]) == 2 )
            self.assert_( len(resultTuple[2]) == 3 )
        for BBB in (('Gen','01','GEN'),): self.assert_( BBB in results )
    # end of test_getAllParatextBooksCodeNumberTriples
# end of BibleBooksCodesTests class


if __name__ == '__main__':
    unittest.main() # Automatically runs all of the above tests
# end of BibleBooksCodesTest.py
