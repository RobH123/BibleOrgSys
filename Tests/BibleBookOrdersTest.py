#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleBookOrdersTest.py
#
# Module testing BibleBookOrders.py
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
Module testing BibleBookOrders.py.
"""

progName = "Bible Book Orders tests"
versionString = "0.57"


import sys, os.path
import unittest
from collections import OrderedDict


sourceFolder = "."
sys.path.append( sourceFolder )
import Globals, BibleBookOrders


class BibleBookOrderSystemsTests(unittest.TestCase):
    """ Unit tests for the BibleBookOrderSystems object. """

    def setUp( self ):
        # Create the BibleBookOrderSystems object
        self.bboss = BibleBookOrders.BibleBookOrderSystems().loadData( os.path.join( sourceFolder, "DataFiles/BookOrders/" ) ) # Doesn't reload the XML unnecessarily :)

    def test_010_len( self ):
        """ Test the __len__ function. """
        self.assert_( 10 < len(self.bboss) < 50 ) # The number of loaded systems
    # end of test_010_len

    def test_020_contains( self ):
        """ Test the __contains__ function. """
        for goodName in ('EuropeanProtestantBible','EuropeanProtestantOldTestament','EuropeanProtestantNewTestament',):
            self.assertTrue( goodName in self.bboss )
        for badName in ('XYZ','StandardBible',):
            self.assertFalse( badName in self.bboss )
    # end of test_020_contains

    def test_030_getAvailableBookOrderSystemNames( self ):
        """ Test the getAvailableBookOrderSystemNames function. """
        results = self.bboss.getAvailableBookOrderSystemNames()
        self.assert_( isinstance( results, list ) )
        self.assert_( 10 < len(results) < 50 ) # The number of loaded systems
        self.assertEqual( len(results), len(self.bboss) )
        self.assertFalse( None in results )
        self.assertFalse( '' in results )
        for name in ("EuropeanProtestantBible",): self.assert_( name in results )
    # end of test_030_getAvailableBookOrderSystemNames

    def test_040_getBookOrderSystem( self ):
        """ Test the getBookOrderSystem function. """
        results = self.bboss.getBookOrderSystem( "EuropeanProtestantBible" )
        self.assert_( isinstance( results, tuple ) )
        self.assertEqual( len(results), 3 ) # The dictionaries
        self.assert_( isinstance( results[0], OrderedDict ) )
        self.assert_( isinstance( results[1], OrderedDict ) )
        self.assert_( isinstance( results[2], list ) )
        self.assertFalse( None in results )
        self.assertFalse( '' in results )
        self.assertEqual( self.bboss.getBookOrderSystem('SomeName'), None )
    # end of test_040_getBookOrderSystem

    def test_050_numBooks( self ):
        """ Test the numBooks function. """
        self.assertEqual( self.bboss.numBooks("EuropeanProtestantBible"), 66 )
        self.assertEqual( self.bboss.numBooks("EuropeanProtestantOldTestament"), 39 )
        self.assertEqual( self.bboss.numBooks("EuropeanProtestantNewTestament"), 27 )
        self.assertRaises( KeyError, self.bboss.numBooks, 'XYZ' )
        self.assertRaises( KeyError, self.bboss.numBooks, 'SomeName' )
    # end of test_050_numBooks

    def test_060_containsBook( self ):
        """ Test the containsBook function. """
        self.assertTrue( self.bboss.containsBook("EuropeanProtestantBible",'GEN') )
        self.assertTrue( self.bboss.containsBook("EuropeanProtestantBible",'MAL') )
        self.assertTrue( self.bboss.containsBook("EuropeanProtestantBible",'MAT') )
        self.assertTrue( self.bboss.containsBook("EuropeanProtestantBible",'CO1') )
        self.assertTrue( self.bboss.containsBook("EuropeanProtestantBible",'REV') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantBible",'XYZ') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantBible",'Gen') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantBible",'LAO') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantBible",'MA1') )

        self.assertTrue( self.bboss.containsBook("EuropeanProtestantOldTestament",'GEN') )
        self.assertTrue( self.bboss.containsBook("EuropeanProtestantOldTestament",'MAL') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantOldTestament",'MAT') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantOldTestament",'CO1') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantOldTestament",'REV') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantOldTestament",'XYZ') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantOldTestament",'Gen') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantOldTestament",'LAO') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantOldTestament",'MA1') )

        self.assertFalse( self.bboss.containsBook("EuropeanProtestantNewTestament",'GEN') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantNewTestament",'MAL') )
        self.assertTrue( self.bboss.containsBook("EuropeanProtestantNewTestament",'MAT') )
        self.assertTrue( self.bboss.containsBook("EuropeanProtestantNewTestament",'CO1') )
        self.assertTrue( self.bboss.containsBook("EuropeanProtestantNewTestament",'REV') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantNewTestament",'XYZ') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantNewTestament",'Gen') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantNewTestament",'LAO') )
        self.assertFalse( self.bboss.containsBook("EuropeanProtestantNewTestament",'MA1') )

        self.assertRaises( KeyError, self.bboss.containsBook, "SomeName",'MAT' )
    # end of test_060_containsBook

    def test_070_getBookList( self ):
        """ Test the getBookList function. """
        for (name, count, books,) in ( ("EuropeanProtestantBible",66,('GEN','MAL','MAT','REV',)), ("EuropeanProtestantOldTestament",39,('GEN','MAL',)), ("EuropeanProtestantNewTestament",27,('MAT','REV',)), ):
            results = self.bboss.getBookList( name )
            self.assert_( isinstance( results, list ) )
            self.assertEqual( len(results), count ) # The number of books
            self.assertFalse( None in results )
            self.assertFalse( '' in results )
            for BBB in books: self.assert_( BBB in results )
    # end of test_070_getBookList

    def test_080_checkBookOrderSystem( self ):
        """ Test the getBookList function. """
        self.assertEqual( self.bboss.checkBookOrderSystem( "myTest", \
            ['MAT', 'MRK', 'LUK', 'JHN', 'ACT', 'ROM', 'CO1', 'CO2', 'GAL', 'EPH', 'PHP', 'COL', 'TH1', 'TH2', 'TI1', 'TI2', 'TIT', 'PHM', 'HEB', 'JAM', 'PE1', 'PE2', 'JN1', 'JN2', 'JN3', 'JDE', 'ReV'] ), None )
    # end of test_080_checkBookOrderSystem
# end of BibleBookOrderSystemsTests class


class BibleBookOrderSystemTests(unittest.TestCase):
    """ Unit tests for the BibleBookOrderSystem object. """

    def setUp( self ):
        # Create a BibleBookOrderSystem object
        self.systemName = "EuropeanProtestantBible"
        self.bbos = BibleBookOrders.BibleBookOrderSystem(self.systemName) # Doesn't reload the XML unnecessarily :)

    def test_010_numBooks( self ):
        """ Test the __len__ and numBooks functions. """
        self.assertEqual( len(self.bbos), 66 )
        self.assertEqual( self.bbos.numBooks(), 66 )
    # end of test_010_numBooks

    def test_020_contains( self ):
        """ Test the __contains__ function. """
        for BBB in ('GEN','MAL','MAT','CO1','REV'):
            self.assertTrue( BBB in self.bbos )
        for BBB in ('XYZ','Gen','LAO','MA1','Rev'):
            self.assertFalse( BBB in self.bbos )
    # end of test_020_contains

    def test_030_containsBook( self ):
        """ Test the containsBook function. """
        self.assertTrue( self.bbos.containsBook('GEN') )
        self.assertTrue( self.bbos.containsBook('MAL') )
        self.assertTrue( self.bbos.containsBook('MAT') )
        self.assertTrue( self.bbos.containsBook('CO1') )
        self.assertTrue( self.bbos.containsBook('REV') )
        self.assertFalse( self.bbos.containsBook('XYZ') )
        self.assertFalse( self.bbos.containsBook('Gen') )
        self.assertFalse( self.bbos.containsBook('LAO') )
        self.assertFalse( self.bbos.containsBook('MA1') )
    # end of test_030_containsBook

    def test_040_getBookOrderSystemName( self ):
        """ Test the getBookOrderSystemName function. """
        self.assertEqual( self.bbos.getBookOrderSystemName(), self.systemName )
    # end of test_040_getBookOrderSystemName

    def test_050_getBookPosition( self ):
        """ Test the getBookPosition function. """
        self.assertEqual( self.bbos.getBookPosition('GEN'), 1 )
        self.assertEqual( self.bbos.getBookPosition('MAL'), 39 )
        self.assertEqual( self.bbos.getBookPosition('MAT'), 40 )
        self.assertEqual( self.bbos.getBookPosition('CO1'), 46 )
        self.assertEqual( self.bbos.getBookPosition('REV'), 66 )
        self.assertRaises( KeyError, self.bbos.getBookPosition, 'XYZ' )
        self.assertRaises( KeyError, self.bbos.getBookPosition, 'Gen' )
    # end of test_050_getBookPosition

    def test_060_getBookAtPosition( self ):
        """ Test the getBookAtPosition function. """
        self.assertEqual( self.bbos.getBookAtPosition(1), 'GEN' )
        self.assertEqual( self.bbos.getBookAtPosition(39), 'MAL' )
        self.assertEqual( self.bbos.getBookAtPosition(40), 'MAT' )
        self.assertEqual( self.bbos.getBookAtPosition(46), 'CO1' )
        self.assertEqual( self.bbos.getBookAtPosition(66), 'REV' )
        self.assertRaises( KeyError, self.bbos.getBookAtPosition, 0 )
        self.assertRaises( KeyError, self.bbos.getBookAtPosition, 67 )
    # end of test_060_getBookAtPosition

    def test_070_getBookList( self ):
        """ Test the getSingleChapterBooksList function. """
        results = self.bbos.getBookList()
        self.assert_( isinstance( results, list ) )
        self.assert_( len(results) == 66 )
        self.assertFalse( None in results )
        self.assertFalse( '' in results )
        for BBB in ('OBA','PHM','JN2','JN3','JDE',): self.assert_( BBB in results )
    # end of test_070_getBookList

    def test_080_getNextBook( self ):
        """ Test the getNextBook function. """
        self.assertEqual( self.bbos.getNextBook('GEN'), 'EXO' )
        self.assertEqual( self.bbos.getNextBook('ZEC'), 'MAL' )
        self.assertEqual( self.bbos.getNextBook('MAL'), 'MAT' )
        self.assertEqual( self.bbos.getNextBook('CO1'), 'CO2' )
        self.assertEqual( self.bbos.getNextBook('JDE'), 'REV' )
        self.assertRaises( KeyError, self.bbos.getNextBook, 'XYZ' )
        self.assertRaises( KeyError, self.bbos.getNextBook, 'Gen' )
    # end of test_080_getNextBook

    def test_090_correctlyOrdered( self ):
        """ Test the correctlyOrdered function. """
        self.assertTrue( self.bbos.correctlyOrdered('GEN','EXO') )
        self.assertTrue( self.bbos.correctlyOrdered('GEN','LEV') )
        self.assertTrue( self.bbos.correctlyOrdered('GEN','REV') )
        self.assertTrue( self.bbos.correctlyOrdered('MAL','MAT') )
        self.assertTrue( self.bbos.correctlyOrdered('MAT','CO1') )
        self.assertTrue( self.bbos.correctlyOrdered('CO1','TI1') )
        self.assertTrue( self.bbos.correctlyOrdered('JDE','REV') )
        self.assertFalse( self.bbos.correctlyOrdered('EXO','GEN') )
        self.assertFalse( self.bbos.correctlyOrdered('CO2','CO1') )
        self.assertFalse( self.bbos.correctlyOrdered('REV','MAL') )
        self.assertRaises( KeyError, self.bbos.correctlyOrdered, 'MA1', 'MA2' )
        self.assertRaises( KeyError, self.bbos.correctlyOrdered, 'XYZ', 'MAT' )
        self.assertRaises( KeyError, self.bbos.correctlyOrdered, 'GEN', 'Rev' )
    # end of test_090_correctlyOrdered
# end of BibleBookOrderSystemTests class


if __name__ == '__main__':
    # Handle command line parameters (for compatibility)
    from optparse import OptionParser
    parser = OptionParser( version="v{}".format( versionString ) )
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML files to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 1: print( "{} V{}".format( progName, versionString ) )

    unittest.main() # Automatically runs all of the above tests
# end of BibleBookOrdersTest.py
