#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleBookOrders.py
#
# Module handling BibleBookOrderSystem_*.xml to produce C and Python data tables
#   Last modified: 2010-12-01 (also update versionString below)
#
# Copyright (C) 2010 Robert Hunt
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
Module handling BibleBookOrder_*.xml to produce C and Python data tables.
"""

progName = "Bible Book Order Systems handler"
versionString = "0.18"


import os, logging
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree
import BibleBooksCodes


class BibleBookOrdersConvertor:
    """
    A class to handle data for Bible book order systems.
    """
    filenameBase = "BibleBookOrders"
    treeTag = "BibleBookOrderSystem"
    headerTag = "header"
    mainElementTag = "book"
    compulsoryAttributes = ( "id", )
    optionalAttributes = ()
    uniqueAttributes = compulsoryAttributes + optionalAttributes
    compulsoryElements = ()
    optionalElements = ()
    uniqueElements = compulsoryElements + optionalElements

    def __init__( self, BibleBooksCodesDict=None ):
        """
        Constructor.
        """
        self.BibleBooksCodesDict = BibleBooksCodesDict
        #self.title, self.version, self.date = None, None, None
        self.XMLSystems, self.Dict, self.Lists = {}, {}, {}
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book order system.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = ""
        #if self.title: result += ('\n' if result else '') + self.title
        #if self.version: result += ('\n' if result else '') + "Version: %s" % ( self.version )
        #if self.date: result += ('\n' if result else '') + "Date: %s" % ( self.date )
        result += ('\n' if result else '') + "Num book order systems loaded = %i" % ( len(self.XMLSystems) )
        if 0: # Make it verbose
            for x in self.XMLSystems:
                result += ('\n' if result else '') + "  %s" % ( x )
                title = self.XMLSystems[x]["title"]
                if title: result += ('\n' if result else '') + "    %s" % ( title )
                version = self.XMLSystems[x]["version"]
                if version: result += ('\n' if result else '') + "    Version: %s" % ( version )
                date = self.XMLSystems[x]["date"]
                if date: result += ('\n' if result else '') + "    Last updated: %s" % ( date )
                result += ('\n' if result else '') + "    Num books = %i" % ( len(self.XMLSystems[x]["tree"]) )
        return result
    # end of __str__

    def loadSystems( self, folder=None ):
        """
        Load and pre-process the specified book order systems.
        """

        if folder==None: folder = "DataFiles/BookOrders"
        for filename in os.listdir( folder ):
            filepart, extension = os.path.splitext( filename )
            if extension.upper() == '.XML' and filepart.upper().startswith("BIBLEBOOKORDER_"):
                bookOrderSystemCode = filepart[15:]
                #print( "Loading %s book order system from %s..." % ( bookOrderSystemCode, filename ) )
                self.XMLSystems[bookOrderSystemCode] = {}
                self.XMLSystems[bookOrderSystemCode]["tree"] = ElementTree().parse ( os.path.join( folder, filename ) )
                assert( self.XMLSystems[bookOrderSystemCode]["tree"] ) # Fail here if we didn't load anything at all

                # Check and remove the header element
                if self.XMLSystems[bookOrderSystemCode]["tree"].tag  == BibleBookOrdersConvertor.treeTag:
                    header = self.XMLSystems[bookOrderSystemCode]["tree"][0]
                    if header.tag == BibleBookOrdersConvertor.headerTag:
                        self.XMLSystems[bookOrderSystemCode]["header"] = header
                        self.XMLSystems[bookOrderSystemCode]["tree"].remove( header )
                        if len(header)>1:
                            logging.info( "Unexpected elements in header" )
                        elif len(header)==0:
                            logging.info( "Missing work element in header" )
                        else:
                            work = header[0]
                            if work.tag == "work":
                                self.XMLSystems[bookOrderSystemCode]["version"] = work.find("version").text
                                self.XMLSystems[bookOrderSystemCode]["date"] = work.find("date").text
                                self.XMLSystems[bookOrderSystemCode]["title"] = work.find("title").text
                            else:
                                logging.warning( "Missing work element in header" )
                    else:
                        logging.warning( "Missing header element (looking for '%s' tag)" % ( headerTag ) )
                else:
                    logging.error( "Expected to load '%s' but got '%s'" % ( treeTag, self.XMLSystems[bookOrderSystemCode]["tree"].tag ) )
                bookCount = 0 # There must be an easier way to do this
                for subelement in self.XMLSystems[bookOrderSystemCode]["tree"]:
                    bookCount += 1
                logging.info( "    Loaded %i books" % ( bookCount ) )

                self.validateSystem( self.XMLSystems[bookOrderSystemCode]["tree"], bookOrderSystemCode )
    # end of loadSystems

    def validateSystem( self, bookOrderTree, systemName ):
        """
        """
        assert( bookOrderTree )

        uniqueDict = {}
        for elementName in BibleBookOrdersConvertor.uniqueElements: uniqueDict["Element_"+elementName] = []
        for attributeName in BibleBookOrdersConvertor.uniqueAttributes: uniqueDict["Attribute_"+attributeName] = []

        expectedID = 1
        for k,element in enumerate(bookOrderTree):
            if element.tag == BibleBookOrdersConvertor.mainElementTag:
                # Check ascending ID field
                ID = element.get("id")
                intID = int( ID )
                if intID != expectedID:
                    logging.error( "ID numbers out of sequence in record %i (got %i when expecting %i) for %s" % ( k, intID, expectedID, systemName ) )
                expectedID += 1

                # Check that this is unique
                if element.text:
                    if element.text in uniqueDict:
                        logging.error( "Found '%s' data repeated in '%s' element in record with ID '%s' (record %i) for %s" % ( element.text, element.tag, ID, k, systemName ) )
                    uniqueDict[element.text] = None

                # Check compulsory attributes on this main element
                for attributeName in BibleBookOrdersConvertor.compulsoryAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is None:
                        logging.error( "Compulsory '%s' attribute is missing from %s element in record %i" % ( attributeName, element.tag, k ) )
                    if not attributeValue:
                        logging.warning( "Compulsory '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, k ) )

                # Check optional attributes on this main element
                for attributeName in BibleBookOrdersConvertor.optionalAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if not attributeValue:
                            logging.warning( "Optional '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, k ) )

                # Check for unexpected additional attributes on this main element
                for attributeName in element.keys():
                    attributeValue = element.get( attributeName )
                    if attributeName not in BibleBookOrdersConvertor.compulsoryAttributes and attributeName not in BibleBookOrdersConvertor.optionalAttributes:
                        logging.warning( "Additional '%s' attribute ('%s') found on %s element in record %i" % ( attributeName, attributeValue, element.tag, k ) )

                # Check the attributes that must contain unique information (in that particular field -- doesn't check across different attributes)
                for attributeName in BibleBookOrdersConvertor.uniqueAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if attributeValue in uniqueDict["Attribute_"+attributeName]:
                            logging.error( "Found '%s' data repeated in '%s' field on %s element in record %i" % ( attributeValue, attributeName, element.tag, k ) )
                        uniqueDict["Attribute_"+attributeName].append( attributeValue )

                # Check compulsory elements
                for elementName in BibleBookOrdersConvertor.compulsoryElements:
                    if element.find( elementName ) is None:
                        logging.error( "Compulsory '%s' element is missing in record with ID '%s' (record %i)" % ( elementName, ID, k ) )
                    if not element.find( elementName ).text:
                        logging.warning( "Compulsory '%s' element is blank in record with ID '%s' (record %i)" % ( elementName, ID, k ) )

                # Check optional elements
                for elementName in BibleBookOrdersConvertor.optionalElements:
                    if element.find( elementName ) is not None:
                        if not element.find( elementName ).text:
                            logging.warning( "Optional '%s' element is blank in record with ID '%s' (record %i)" % ( elementName, ID, k ) )

                # Check for unexpected additional elements
                for subelement in element:
                    if subelement.tag not in BibleBookOrdersConvertor.compulsoryElements and subelement.tag not in BibleBookOrdersConvertor.optionalElements:
                        logging.warning( "Additional '%s' element ('%s') found in record with ID '%s' (record %i)" % ( subelement.tag, subelement.text, ID, k ) )

                # Check the elements that must contain unique information (in that particular element -- doesn't check across different elements)
                for elementName in BibleBookOrdersConvertor.uniqueElements:
                    if element.find( elementName ) is not None:
                        text = element.find( elementName ).text
                        if text in uniqueDict["Element_"+elementName]:
                            logging.error( "Found '%s' data repeated in '%s' element in record with ID '%s' (record %i)" % ( text, elementName, ID, k ) )
                        uniqueDict["Element_"+elementName].append( text )
            else:
                logging.warning( "Unexpected element: %s in record %i" % ( element.tag, k ) )
    # end of validateSystem

    def checkDuplicates( self ):
        """
        Checks for duplicate (redundant) book order systems.

        Returns True if a duplicate is found.
        """
        systemLists, foundDuplicate = {}, False
        for bookOrderSystemCode in self.XMLSystems.keys():
            # Get the referenceAbbreviations all into a list
            bookDataList = []
            for bookElement in self.XMLSystems[bookOrderSystemCode]["tree"]:
                bookRA = bookElement.text
                if bookRA in self.BibleBooksCodesDict:
                    bookDataList.append( bookRA )
            # Compare with existing lists
            for checkSystemCode,checkDataList in systemLists.items():
                if bookDataList == checkDataList:
                    logging.error( "%s and %s book order systems are identical (%i books)" % ( bookOrderSystemCode, checkSystemCode, len(bookDataList) ) )
                    foundDuplicate = True
            # Add this new list
            systemLists[bookOrderSystemCode] = bookDataList
        return foundDuplicate
    # end of checkDuplicates

    def importDataToPython( self ):
        """
        Loads (and pivots) the data (not including the header) into suitable Python containers to use in a Python program.
        """
        assert( self.XMLSystems )

        # We'll create a number of dictionaries
        self.Dict, self.Lists = {}, {}
        for bookOrderSystemCode in self.XMLSystems.keys():
            #print( bookOrderSystemCode )
            # Make the data dictionary for this book order system
            bookDataDict, idDataDict, BBBList = OrderedDict(), OrderedDict(), []
            for bookElement in self.XMLSystems[bookOrderSystemCode]["tree"]:
                bookRA = bookElement.text
                ID = bookElement.get( "id" )
                intID = int( ID )
                if self.BibleBooksCodesDict and bookRA not in self.BibleBooksCodesDict:
                    logging.error( "Unrecognized '%s' book abbreviation in '%s' book order system" % ( bookRA, bookOrderSystemCode ) )
                # Save it by book reference abbreviation
                if bookRA in bookDataDict:
                    logging.error( "Duplicate %s book reference abbreviations in '%s' book order system" % ( bookRA, bookOrderSystemCode ) )
                bookDataDict[bookRA] = intID
                if intID in idDataDict:
                    logging.error( "Duplicate %i ID numbers in '%s' book order system" % ( intID, bookOrderSystemCode ) )
                idDataDict[intID] = bookRA
                BBBList.append( bookRA )

            # Now put it into my dictionaries for easy access
            # This part should be customized or added to for however you need to process the data
            #   Add .upper() if you require the abbreviations to be uppercase (or .lower() for lower case)
            self.Dict[bookOrderSystemCode] = bookDataDict, idDataDict
            self.Lists[bookOrderSystemCode] = BBBList
        return self.Dict
    # end of importDataToPython

    def exportDataToPython( self, filepath=None ):
        """
        Writes the information tables to a .py file that can be cut and pasted into a Python program.
        """
        def exportPythonDict( theFile, theDict, dictName, keyComment, fieldsComment ):
            """Exports theDict to theFile."""
            theFile.write( '  "%s": {\n    # Key is %s\n    # Fields are: %s\n' % ( dictName, keyComment, fieldsComment ) )
            for dictKey in theDict.keys():
                theFile.write( '    %s: %s,\n' % ( repr(dictKey), repr(theDict[dictKey]) ) )
            theFile.write( "  }, # end of %s (%i entries)\n\n" % ( dictName, len(theDict) ) )
        # end of exportPythonDict

        from datetime import datetime

        assert( self.XMLSystems )
        if not filepath: filepath = os.path.join( "DerivedFiles", BibleBookOrdersConvertor.filenameBase + "_Tables.py" )
        print( "Exporting to %s..." % ( filepath ) )

        bookOrderSystemDict = self.importDataToPython()
        # Split into two dictionaries
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# %s\n#\n" % ( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by BibleBookOrders.py V%s %s\n#\n" % ( versionString, datetime.now() ) )
            #if self.title: myFile.write( "# %s\n" % ( self.title ) )
            #if self.version: myFile.write( "#  Version: %s\n" % ( self.version ) )
            #if self.date: myFile.write( "#  Date: %s\n#\n" % ( self.date ) )
            #myFile.write( "#   %i %s entries loaded from the original XML file.\n" % ( len(self.namesTree), BibleBookOrdersConvertor.treeTag ) )
            myFile.write( "#   %i %s loaded from the original XML files.\n#\n\n" % ( len(self.XMLSystems), BibleBookOrdersConvertor.treeTag ) )
            myFile.write( "from collections import OrderedDict\n\n\n" )
            myFile.write( "bookDataDict = {\n  # Key is versificationSystemName\n  # Fields are omittedVersesSystem\n\n" )
            for systemName in bookOrderSystemDict:
                bookDataDict, idDataDict = bookOrderSystemDict[systemName]
                exportPythonDict( myFile, bookDataDict, systemName, "referenceAbbreviation", "id" )
            myFile.write( "} # end of bookDataDict (%i systems)\n\n\n\n" % ( len(bookOrderSystemDict) ) )
            myFile.write( "idDataDict = {\n  # Key is versificationSystemName\n  # Fields are omittedVersesSystem\n\n" )
            for systemName in bookOrderSystemDict:
                bookDataDict, idDataDict = bookOrderSystemDict[systemName]
                exportPythonDict( myFile, idDataDict, systemName, "id", "referenceAbbreviation" )
            myFile.write( "} # end of idDataDict (%i systems)\n" % ( len(bookOrderSystemDict) ) )
    # end of exportDataToPython

    def exportDataToC( self, filepath=None ):
        """
        Writes the information tables to a .h file that can be included in c and c++ programs.
        """
        def exportPythonDict( theFile, theDict, dictName, structName, fieldsComment ):
            """Exports theDict to theFile."""
            def convertEntry( entry ):
                """Convert special characters in an entry..."""
                result = ""
                if isinstance( entry, int ): result += str(entry)
                elif isinstance( entry, str): result += '"' + str(entry).replace('"','\\"') + '"'
                else:
                    for field in entry:
                        if result: result += ", " # Separate the fields
                        if field is None: result += '""'
                        elif isinstance( field, str): result += '"' + str(field).replace('"','\\"') + '"'
                        elif isinstance( field, int): result += str(field)
                        else: logging.error( "Cannot convert unknown field type '%s' in entry '%s'" % ( field, entry ) )
                return result

            theFile.write( "static struct %s %s[] = {\n  // Fields are %s\n" % ( structName, dictName, fieldsComment ) )
            for entry in sorted(theDict.keys()):
                if isinstance( entry, str ):
                    theFile.write( "  {\"%s\", %s},\n" % ( entry, convertEntry(theDict[entry]) ) )
                elif isinstance( entry, int ):
                    theFile.write( "  {%i, %s},\n" % ( entry, convertEntry(theDict[entry]) ) )
                else:
                    logging.error( "Can't handle this type of data yet: %s" % ( entry ) )
            theFile.write( "}; // %s\n\n" % ( dictName) )
        # end of exportPythonDict

        from datetime import datetime

        assert( self.XMLSystems )
        if not filepath: filepath = os.path.join( "DerivedFiles", BibleBookOrdersConvertor.filenameBase + "_Tables.h" )
        print( "Exporting to %s..." % ( filepath ) )

        bookOrderSystemDict = self.importDataToPython()
        ifdefName = BibleBookOrdersConvertor.filenameBase.upper() + "_Tables_h"
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "// %s\n//\n" % ( filepath ) )
            myFile.write( "// This UTF-8 file was automatically generated by BibleBookOrdersConvertor.py V%s %s\n//\n" % ( versionString, datetime.now() ) )
            #if self.title: myFile.write( "// %s\n" % ( self.title ) )
            #if self.version: myFile.write( "//  Version: %s\n" % ( self.version ) )
            #if self.date: myFile.write( "//  Date: %s\n//\n" % ( self.date ) )
            myFile.write( "//   %i %s loaded from the original XML file.\n//\n\n" % ( len(self.XMLSystems), BibleBookOrdersConvertor.treeTag ) )
            myFile.write( "#ifndef %s\n#define %s\n\n" % ( ifdefName, ifdefName ) )
            for systemName in bookOrderSystemDict:
                bookDataDict, idDataDict = bookOrderSystemDict[systemName]
                myFile.write( "#\n# %s\n" % ( systemName ) )
                exportPythonDict( myFile, bookDataDict, "bookDataDict", "referenceAbbreviation", "reference Abbreviation, id" )
                exportPythonDict( myFile, idDataDict, "idDataDict", "id", "id, referenceAbbreviation" )
            myFile.write( "#endif // %s\n" % ( ifdefName ) )
    # end of exportDataToC

    def checkBookOrderSystem( self, systemName, bookOrderSchemeToCheck, exportFlag=False, debugFlag=False ):
        """
        Check the given book order scheme against all the loaded systems.
        Create a new book order file if it doesn't match any.
        """
        assert( systemName )
        assert( bookOrderSchemeToCheck )
        assert( self.Lists )
        #print( systemName, bookOrderSchemeToCheck )

        matchedBookOrderSystemCodes = []
        systemMatchCount, systemMismatchCount, allErrors, errorSummary = 0, 0, '', ''
        for bookOrderSystemCode in self.Lists: # Step through the various reference schemes
            theseErrors = ''
            if self.Lists[bookOrderSystemCode] == bookOrderSchemeToCheck:
                #print( "  Matches '%s' book order system" % ( bookOrderSystemCode ) )
                systemMatchCount += 1
                matchedBookOrderSystemCodes.append( bookOrderSystemCode )
            else:
                if len(self.Lists[bookOrderSystemCode]) == len(bookOrderSchemeToCheck):
                    for BBB1,BBB2 in zip(self.Lists[bookOrderSystemCode],bookOrderSchemeToCheck):
                        if BBB1 != BBB2: break
                    thisError = "    Doesn't match '%s' system (Both have %i books, but %s instead of %s)" % ( bookOrderSystemCode, len(bookOrderSchemeToCheck), BBB1, BBB2 )
                else:
                    thisError = "    Doesn't match '%s' system (%i books instead of %i)" % ( bookOrderSystemCode, len(bookOrderSchemeToCheck), len(self.Lists[bookOrderSystemCode]) )
                theseErrors += ("\n" if theseErrors else "") + thisError
                errorSummary += ("\n" if errorSummary else "") + thisError
                systemMismatchCount += 1

        if systemMatchCount:
            if systemMatchCount == 1: # What we hope for
                print( "  Matched %s book order (with these %i books)" % ( matchedBookOrderSystemCodes[0], len(bookOrderSchemeToCheck) ) )
                if debugFlag: print( errorSummary )
            else:
                print( "  Matched %i book order system(s): %s (with these %i books)" % ( systemMatchCount, matchedBookOrderSystemCodes, len(bookOrderSchemeToCheck) ) )
                if debugFlag: print( errorSummary )
        else:
            print( "  Mismatched %i book order systems (with these %i books)" % ( systemMismatchCount, len(bookOrderSchemeToCheck) ) )
            if debugFlag: print( allErrors )
            else: print( errorSummary)

        if exportFlag and not systemMatchCount: # Write a new file
            outputFilepath = os.path.join( "ScrapedFiles", "BibleBookOrder_"+systemName + ".xml" )
            print( "Writing %i books to %s..." % ( len(bookOrderSchemeToCheck), outputFilepath ) )
            with open( outputFilepath, 'wt' ) as myFile:
                for n,BBB in enumerate(bookOrderSchemeToCheck):
                    myFile.write( '  <book id="%i">%s</book>\n' % ( n+1,BBB ) )
                myFile.write( "</BibleBookOrderSystem>" )
    # end of checkBookOrderSystem
# end of BibleBookOrdersConvertor class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    global CommandLineOptions
    parser = OptionParser( version="v%s" % ( versionString ) )
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML files to .py and .h tables suitable for directly including into other programs")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False, help="display extra debugging information")
    CommandLineOptions, args = parser.parse_args()


    # Get the data tables that we need for proper checking
    bbc = BibleBooksCodes.BibleBooksCodesConvertor()
    junk, BBCRADict, junk, junk, junk, junk, junk, junk, BBCNameDict = bbc.importDataToPython()

    # Adjust the name dict to upper case
    UC_BBCNameDict = {}
    for key, entry in BBCNameDict.items():
        UC_BBCNameDict[key.upper()] = entry

    # Do a proper load/check
    bbos = BibleBookOrdersConvertor( BibleBooksCodesDict=BBCRADict )
    bbos.loadSystems()
    BookOrderNameDict = bbos.importDataToPython()
    bbos.checkDuplicates()

    if CommandLineOptions.export:
        bbos.exportDataToPython()
        bbos.exportDataToC()
    else: # not exporting -- must just be a demo run
        print( bbos )
# end of main

if __name__ == '__main__':
    main()
# end of BibleBookOrders.py
