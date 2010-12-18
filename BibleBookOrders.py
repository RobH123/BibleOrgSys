#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleBookOrders.py
#
# Module handling BibleBookOrderSystem_*.xml to produce C and Python data tables
#   Last modified: 2010-12-18 (also update versionString below)
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
versionString = "0.50"


import os, logging
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree

from singleton import singleton
import Globals
from BibleBooksCodes import BibleBooksCodes


@singleton # Can only ever have one instance
class _BibleBookOrdersConvertor:
    """
    A class to handle data for Bible book order systems.
    """

    def __init__( self ):
        """
        Constructor.
        """
        self.filenameBase = "BibleBookOrders"

        # These fields are used for parsing the XML
        self.treeTag = "BibleBookOrderSystem"
        self.headerTag = "header"
        self.mainElementTag = "book"

        # These fields are used for automatically checking/validating the XML
        self.compulsoryAttributes = ( "id", )
        self.optionalAttributes = ()
        self.uniqueAttributes = self.compulsoryAttributes + self.optionalAttributes
        self.compulsoryElements = ()
        self.optionalElements = ()
        self.uniqueElements = self.compulsoryElements + self.optionalElements


        # These are fields that we will fill later
        self.XMLSystems = {}
        self.DataDicts, self.DataLists = {}, {} # Used for import

        # Make sure we have the bible books codes data loaded and available
        self.BibleBooksCodes = BibleBooksCodes().loadData()
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book order system.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "_BibleBookOrdersConvertor object"
        result += ('\n' if result else '') + "  Num book order systems loaded = %i" % ( len(self.XMLSystems) )
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

    def loadSystems( self, XMLFolder=None ):
        """
        Load and pre-process the specified book order systems.
        """
        if not self.XMLSystems: # Only ever do this once
            if XMLFolder==None: XMLFolder = "DataFiles/BookOrders"
            self.XMLFolder = XMLFolder
            for filename in os.listdir( XMLFolder ):
                filepart, extension = os.path.splitext( filename )
                if extension.upper() == '.XML' and filepart.upper().startswith("BIBLEBOOKORDER_"):
                    bookOrderSystemCode = filepart[15:]
                    #print( "Loading %s book order system from %s..." % ( bookOrderSystemCode, filename ) )
                    self.XMLSystems[bookOrderSystemCode] = {}
                    self.XMLSystems[bookOrderSystemCode]["tree"] = ElementTree().parse( os.path.join( XMLFolder, filename ) )
                    assert( self.XMLSystems[bookOrderSystemCode]["tree"] ) # Fail here if we didn't load anything at all

                    # Check and remove the header element
                    if self.XMLSystems[bookOrderSystemCode]["tree"].tag  == self.treeTag:
                        header = self.XMLSystems[bookOrderSystemCode]["tree"][0]
                        if header.tag == self.headerTag:
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

                    self._validateSystem( self.XMLSystems[bookOrderSystemCode]["tree"], bookOrderSystemCode )
        return self
    # end of loadSystems

    def _validateSystem( self, bookOrderTree, systemName ):
        """
        """
        assert( bookOrderTree )

        uniqueDict = {}
        for elementName in self.uniqueElements: uniqueDict["Element_"+elementName] = []
        for attributeName in self.uniqueAttributes: uniqueDict["Attribute_"+attributeName] = []

        expectedID = 1
        for k,element in enumerate(bookOrderTree):
            if element.tag == self.mainElementTag:
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
                for attributeName in self.compulsoryAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is None:
                        logging.error( "Compulsory '%s' attribute is missing from %s element in record %i" % ( attributeName, element.tag, k ) )
                    if not attributeValue:
                        logging.warning( "Compulsory '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, k ) )

                # Check optional attributes on this main element
                for attributeName in self.optionalAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if not attributeValue:
                            logging.warning( "Optional '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, k ) )

                # Check for unexpected additional attributes on this main element
                for attributeName in element.keys():
                    attributeValue = element.get( attributeName )
                    if attributeName not in self.compulsoryAttributes and attributeName not in self.optionalAttributes:
                        logging.warning( "Additional '%s' attribute ('%s') found on %s element in record %i" % ( attributeName, attributeValue, element.tag, k ) )

                # Check the attributes that must contain unique information (in that particular field -- doesn't check across different attributes)
                for attributeName in self.uniqueAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if attributeValue in uniqueDict["Attribute_"+attributeName]:
                            logging.error( "Found '%s' data repeated in '%s' field on %s element in record %i" % ( attributeValue, attributeName, element.tag, k ) )
                        uniqueDict["Attribute_"+attributeName].append( attributeValue )

                # Check compulsory elements
                for elementName in self.compulsoryElements:
                    if element.find( elementName ) is None:
                        logging.error( "Compulsory '%s' element is missing in record with ID '%s' (record %i)" % ( elementName, ID, k ) )
                    if not element.find( elementName ).text:
                        logging.warning( "Compulsory '%s' element is blank in record with ID '%s' (record %i)" % ( elementName, ID, k ) )

                # Check optional elements
                for elementName in self.optionalElements:
                    if element.find( elementName ) is not None:
                        if not element.find( elementName ).text:
                            logging.warning( "Optional '%s' element is blank in record with ID '%s' (record %i)" % ( elementName, ID, k ) )

                # Check for unexpected additional elements
                for subelement in element:
                    if subelement.tag not in self.compulsoryElements and subelement.tag not in self.optionalElements:
                        logging.warning( "Additional '%s' element ('%s') found in record with ID '%s' (record %i)" % ( subelement.tag, subelement.text, ID, k ) )

                # Check the elements that must contain unique information (in that particular element -- doesn't check across different elements)
                for elementName in self.uniqueElements:
                    if element.find( elementName ) is not None:
                        text = element.find( elementName ).text
                        if text in uniqueDict["Element_"+elementName]:
                            logging.error( "Found '%s' data repeated in '%s' element in record with ID '%s' (record %i)" % ( text, elementName, ID, k ) )
                        uniqueDict["Element_"+elementName].append( text )
            else:
                logging.warning( "Unexpected element: %s in record %i" % ( element.tag, k ) )
    # end of _validateSystem

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
                if self.BibleBooksCodes.isValidReferenceAbbreviation( bookRA ):
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
        if self.DataDicts and self.DataLists: # We've already done an import/restructuring -- no need to repeat it
            return self.DataDicts, self.DataLists

        # We'll create a number of dictionaries
        for bookOrderSystemCode in self.XMLSystems.keys():
            #print( bookOrderSystemCode )
            # Make the data dictionary for this book order system
            bookDataDict, idDataDict, BBBList = OrderedDict(), OrderedDict(), []
            for bookElement in self.XMLSystems[bookOrderSystemCode]["tree"]:
                bookRA = bookElement.text
                ID = bookElement.get( "id" )
                intID = int( ID )
                if not self.BibleBooksCodes.isValidReferenceAbbreviation( bookRA ):
                    logging.error( "Unrecognized '%s' book abbreviation in '%s' book order system" % ( bookRA, bookOrderSystemCode ) )
                # Save it by book reference abbreviation
                if bookRA in bookDataDict:
                    logging.error( "Duplicate %s book reference abbreviations in '%s' book order system" % ( bookRA, bookOrderSystemCode ) )
                bookDataDict[bookRA] = intID
                if intID in idDataDict:
                    logging.error( "Duplicate %i ID (book index) numbers in '%s' book order system" % ( intID, bookOrderSystemCode ) )
                idDataDict[intID] = bookRA
                BBBList.append( bookRA )

            # Now put it into my dictionaries for easy access
            # This part should be customized or added to for however you need to process the data
            self.DataDicts[bookOrderSystemCode] = bookDataDict, idDataDict
            self.DataLists[bookOrderSystemCode] = BBBList # Don't explicitly include the book index numbers, but otherwise the same information in a different form
        return self.DataDicts, self.DataLists
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
        self.importDataToPython()
        assert( self.DataDicts and self.DataLists )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables.py" )
        print( "Exporting to %s..." % ( filepath ) )

        # Split into two dictionaries
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# %s\n#\n" % ( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by BibleBookOrders.py V%s %s\n#\n" % ( versionString, datetime.now() ) )
            #if self.title: myFile.write( "# %s\n" % ( self.title ) )
            #if self.version: myFile.write( "#  Version: %s\n" % ( self.version ) )
            #if self.date: myFile.write( "#  Date: %s\n#\n" % ( self.date ) )
            #myFile.write( "#   %i %s entries loaded from the original XML file.\n" % ( len(self.namesTree), self.treeTag ) )
            myFile.write( "#   %i %s loaded from the original XML files.\n#\n\n" % ( len(self.XMLSystems), self.treeTag ) )
            myFile.write( "from collections import OrderedDict\n\n\n" )
            myFile.write( "bookDataDict = {\n  # Key is versificationSystemName\n  # Fields are omittedVersesSystem\n\n" )
            for systemName in self.DataDicts:
                bookDataDict, idDataDict = self.DataDicts[systemName]
                exportPythonDict( myFile, bookDataDict, systemName, "referenceAbbreviation", "id" )
            myFile.write( "} # end of bookDataDict (%i systems)\n\n\n\n" % ( len(self.DataDicts) ) )
            myFile.write( "idDataDict = {\n  # Key is versificationSystemName\n  # Fields are omittedVersesSystem\n\n" )
            for systemName in self.DataDicts:
                bookDataDict, idDataDict = self.DataDicts[systemName]
                exportPythonDict( myFile, idDataDict, systemName, "id", "referenceAbbreviation" )
            myFile.write( "} # end of idDataDict (%i systems)\n" % ( len(self.DataDicts) ) )
            myFile.write( "# end of %s" % os.path.basename(filepath) )
    # end of exportDataToPython

    def exportDataToJSON( self, filepath=None ):
        """
        Writes the information tables to a .json file that can be easily loaded into a Java program.

        See http://en.wikipedia.org/wiki/JSON.
        """
        from datetime import datetime
        import json

        assert( self.XMLSystems )
        self.importDataToPython()
        assert( self.DataDicts and self.DataLists )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables.json" )
        print( "Exporting to %s..." % ( filepath ) )
        with open( filepath, 'wt' ) as myFile:
            #myFile.write( "# %s\n#\n" % ( filepath ) ) # Not sure yet if these comment fields are allowed in JSON
            #myFile.write( "# This UTF-8 file was automatically generated by BibleBooksCodes.py on %s\n#\n" % ( datetime.now() ) )
            #if self.titleString: myFile.write( "# %s data\n" % ( self.titleString ) )
            #if self.versionString: myFile.write( "#  Version: %s\n" % ( self.versionString ) )
            #if self.dateString: myFile.write( "#  Date: %s\n#\n" % ( self.dateString ) )
            #myFile.write( "#   %i %s loaded from the original XML file.\n#\n\n" % ( len(self.XMLtree), self.treeTag ) )
            json.dump( self.DataDicts, myFile, indent=2 )
            #myFile.write( "\n\n# end of %s" % os.path.basename(filepath) )
    # end of exportDataToJSON

    def exportDataToC( self, filepath=None ):
        """
        Writes the information tables to a .h file that can be included in c and c++ programs.
        """
        def writeStructure( hFile, structName, structure ):
            """ Writes a typedef to the .h file. """
            hFile.write( "typedef struct %sEntryStruct {\n" % structName )
            for declaration in structure.split(';'):
                adjDeclaration = declaration.strip()
                if adjDeclaration: hFile.write( "    %s;\n" % adjDeclaration )
            hFile.write( "} %sEntry;\n\n" % structName )
        # end of writeStructure

        def exportPythonDict( cFile, theDict, dictName, structName, sortedBy, structure ):
            """ Exports theDict to the .h and .c files. """
            def convertEntry( entry ):
                """ Convert special characters in an entry... """
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
            # end of convertEntry

            #for dictKey in theDict.keys(): # Have to iterate this :(
            #    fieldsCount = len( theDict[dictKey] ) + 1 # Add one since we include the key in the count
            #    break # We only check the first (random) entry we get
            fieldsCount = 2

            cFile.write( "const static %s\n %s[%i] = {\n  // Fields (%i) are %s\n  // Sorted by %s\n" % ( structName, dictName, len(theDict), fieldsCount, structure, sortedBy ) )
            for dictKey in sorted(theDict.keys()):
                if isinstance( dictKey, str ):
                    cFile.write( "  {\"%s\", %s},\n" % ( dictKey, convertEntry(theDict[dictKey]) ) )
                elif isinstance( dictKey, int ):
                    cFile.write( "  {%i, %s},\n" % ( dictKey, convertEntry(theDict[dictKey]) ) )
                else:
                    logging.error( "Can't handle this type of data yet: %s" % ( dictKey ) )
            cFile.write( "}; // %s (%i entries)\n\n" % ( dictName, len(theDict) ) )
        # end of exportPythonDict

        from datetime import datetime

        assert( self.XMLSystems )
        self.importDataToPython()
        assert( self.DataDicts and self.DataLists )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables" )
        hFilepath = filepath + '.h'
        cFilepath = filepath + '.c'
        print( "Exporting to %s..." % ( cFilepath ) ) # Don't bother telling them about the .h file
        ifdefName = self.filenameBase.upper() + "_Tables_h"

        with open( hFilepath, 'wt' ) as myHFile, open( cFilepath, 'wt' ) as myCFile:
            myHFile.write( "// %s\n//\n" % ( hFilepath ) )
            myCFile.write( "// %s\n//\n" % ( cFilepath ) )
            lines = "// This UTF-8 file was automatically generated by BibleBookOrders.py on %s\n//\n" % datetime.now()
            myHFile.write( lines ); myCFile.write( lines )
            myCFile.write( "//   %i %s loaded from the original XML file.\n//\n\n" % ( len(self.XMLSystems), self.treeTag ) )
            myHFile.write( "\n#ifndef %s\n#define %s\n\n" % ( ifdefName, ifdefName ) )
            myCFile.write( '#include "%s"\n\n' % os.path.basename(hFilepath) )

            CHAR = "const unsigned char"
            BYTE = "const int"
            N1 = "bookOrderByRef"
            N2 = "bookOrderByIndex"
            S1 = "%s referenceAbbreviation[3+1]; %s indexNumber;" % (CHAR,BYTE)
            S2 = "%s indexNumber; %s referenceAbbreviation[3+1];" % (BYTE,CHAR)
            writeStructure( myHFile, N1, S1 )
            writeStructure( myHFile, N2, S2 )
            writeStructure( myHFile, "table", "%s* systemName; %sEntry* byReference; %sEntry* byBook;" % (CHAR,N1,N2) ) # I'm not sure if I need one or two asterisks on those last two
                                                                                                        # They're supposed to be pointers to an array of structures
            myHFile.write( "#endif // %s\n\n" % ( ifdefName ) )
            myHFile.write( "// end of %s" % os.path.basename(hFilepath) )

            for systemName in self.DataDicts: # Now write out the actual data into the .c file
                bookDataDict, idDataDict = self.DataDicts[systemName]
                myCFile.write( "\n// %s\n" % ( systemName ) )
                exportPythonDict( myCFile, bookDataDict, systemName+"BookDataDict", N1+"Entry", "referenceAbbreviation", S1 )
                exportPythonDict( myCFile, idDataDict, systemName+"IndexNumberDataDict", N2+"Entry", "indexNumber", S2 )

            # Write out the final table of pointers to the above information
            myCFile.write( "\n// Pointers to above data\nconst static tableEntry bookOrderSystemTable[%i] = {\n" % len(self.DataDicts) )
            for systemName in self.DataDicts: # Now write out the actual pointer data into the .c file
                myCFile.write( '  { "%s", %s, %s },\n' % ( systemName, systemName+"BookDataDict", systemName+"IndexNumberDataDict" ) )
            myCFile.write( "}; // %i entries\n\n" % len(self.DataDicts) )
            myCFile.write( "// end of %s" % os.path.basename(cFilepath) )
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
# end of _BibleBookOrdersConvertor class


@singleton # Can only ever have one instance
class BibleBookOrders:
    """
    Class for handling Bible book order systems.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.

    Note: BBB is used in this class to represent the three-character referenceAbbreviation.
    """

    def __init__( self ): # We can't give this parameters because of the singleton
        """
        Constructor: 
        """
        self.bboc = _BibleBookOrdersConvertor()
        self.DataContainers = None # We'll import into this in loadData
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book order.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "BibleBooksOrders object"
        assert( len(self.DataContainers[0]) == len(self.DataContainers[1]) )
        result += ('\n' if result else '') + "  Num systems = %i" % ( len(self.DataContainers[0]) )
        return result
    # end of __str__

    def loadData( self, XMLFolder=None ):
        """ Loads the XML data file and imports it to dictionary format (if not done already). """
        if not self.DataContainers: # Don't do this unnecessarily
            if XMLFolder is not None: logging.warning( "Bible book order systems are already loaded -- your given XMLFolder of '%s' was ignored" % XMLFolder )
            self.bboc.loadSystems( XMLFolder ) # Load the XML (if not done already)
            self.DataContainers = self.bboc.importDataToPython() # Get the various dictionaries organised for quick lookup
            del self.bboc # Now the convertor class (that handles the XML) is no longer needed
        return self
    # end of loadData

    # TODO: Add some useful routines in here

# end of BibleBookOrders class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    global CommandLineOptions
    parser = OptionParser( version="v%s" % ( versionString ) )
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML files to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel>0: print( "%s V%s" % ( progName, versionString ) )

    if Globals.commandLineOptions.export:
        bbos = _BibleBookOrdersConvertor().loadSystems() # Load the XML
        bbos.checkDuplicates()
        bbos.exportDataToPython() # Produce the .py tables
        bbos.exportDataToJSON() # Produce a json output file
        bbos.exportDataToC() # Produce the .h and .c tables

    else: # Must be demo mode
        # Demo the convertor object
        bbos = _BibleBookOrdersConvertor().loadSystems() # Load the XML
        bbos.checkDuplicates()
        print( bbos ) # Just print a summary

        # Demo the BibleBookOrders object
        bbo = BibleBookOrders().loadData() # Doesn't reload the XML unnecessarily :)
        print( bbo ) # Just print a summary
# end of main

if __name__ == '__main__':
    main()
# end of BibleBookOrders.py
