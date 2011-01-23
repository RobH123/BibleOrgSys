#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleBookOrders.py
#
# Module handling BibleBookOrderSystem_*.xml to produce C and Python data tables
#   Last modified: 2011-01-23 (also update versionString below)
#
# Copyright (C) 2010-2011 Robert Hunt
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
versionString = "0.57"


import os, logging
from gettext import gettext as _
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree

from singleton import singleton
import Globals
from BibleBooksCodes import BibleBooksCodes


@singleton # Can only ever have one instance
class _BibleBookOrdersConverter:
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
        self.__DataDicts, self.__DataLists = {}, {} # Used for import

        # Make sure we have the bible books codes data loaded and available
        self.BibleBooksCodes = BibleBooksCodes().loadData()
    # end of __init__

    def loadSystems( self, XMLFolder=None ):
        """
        Load and pre-process the specified book order systems.
        """
        if not self.XMLSystems: # Only ever do this once
            if XMLFolder==None: XMLFolder = "DataFiles/BookOrders"
            self.__XMLFolder = XMLFolder
            if Globals.verbosityLevel > 2: print( _("Loading book order systems from {}...").format( self.__XMLFolder ) )
            filenamePrefix = "BIBLEBOOKORDER_"
            for filename in os.listdir( XMLFolder ):
                filepart, extension = os.path.splitext( filename )
                if extension.upper() == '.XML' and filepart.upper().startswith(filenamePrefix):
                    bookOrderSystemCode = filepart[len(filenamePrefix):]
                    if Globals.verbosityLevel > 3: print( _("  Loading{} book order system from {}...").format( bookOrderSystemCode, filename ) )
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
                                logging.info( _("Unexpected elements in header") )
                            elif len(header)==0:
                                logging.info( _("Missing work element in header") )
                            else:
                                work = header[0]
                                if work.tag == "work":
                                    self.XMLSystems[bookOrderSystemCode]["version"] = work.find("version").text
                                    self.XMLSystems[bookOrderSystemCode]["date"] = work.find("date").text
                                    self.XMLSystems[bookOrderSystemCode]["title"] = work.find("title").text
                                else:
                                    logging.warning( _("Missing work element in header") )
                        else:
                            logging.warning( _("Missing header element (looking for '{}' tag)").format( headerTag ) )
                    else:
                        logging.error( _("Expected to load '{}' but got '{}'").format( treeTag, self.XMLSystems[bookOrderSystemCode]["tree"].tag ) )
                    bookCount = 0 # There must be an easier way to do this
                    for subelement in self.XMLSystems[bookOrderSystemCode]["tree"]:
                        bookCount += 1
                    logging.info( _("    Loaded {} books").format( bookCount ) )

                if Globals.strictCheckingFlag:
                    self.__validateSystem( self.XMLSystems[bookOrderSystemCode]["tree"], bookOrderSystemCode )
        else: # The data must have been already loaded
            if XMLFolder is not None and XMLFolder!=self.__XMLFolder: logging.error( _("Bible book order systems are already loaded -- your different folder of '{}' was ignored").format( XMLFolder ) )
        return self
    # end of loadSystems

    def __validateSystem( self, bookOrderTree, systemName ):
        """ Do a semi-automatic check of the XML file validity. """
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
                    logging.error( _("ID numbers out of sequence in record {} (got {} when expecting {}) for {}").format( k, intID, expectedID, systemName ) )
                expectedID += 1

                # Check that this is unique
                if element.text:
                    if element.text in uniqueDict:
                        logging.error( _("Found '{}' data repeated in '{}' element in record with ID '{}' (record {}) for {}").format( element.text, element.tag, ID, k, systemName ) )
                    uniqueDict[element.text] = None

                # Check compulsory attributes on this main element
                for attributeName in self.compulsoryAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is None:
                        logging.error( _("Compulsory '{}' attribute is missing from {} element in record {}").format( attributeName, element.tag, k ) )
                    if not attributeValue:
                        logging.warning( _("Compulsory '{}' attribute is blank on {} element in record {}").format( attributeName, element.tag, k ) )

                # Check optional attributes on this main element
                for attributeName in self.optionalAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if not attributeValue:
                            logging.warning( _("Optional '{}' attribute is blank on {} element in record {}").format( attributeName, element.tag, k ) )

                # Check for unexpected additional attributes on this main element
                for attributeName in element.keys():
                    attributeValue = element.get( attributeName )
                    if attributeName not in self.compulsoryAttributes and attributeName not in self.optionalAttributes:
                        logging.warning( _("Additional '{}' attribute ('{}') found on {} element in record {}").format( attributeName, attributeValue, element.tag, k ) )

                # Check the attributes that must contain unique information (in that particular field -- doesn't check across different attributes)
                for attributeName in self.uniqueAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if attributeValue in uniqueDict["Attribute_"+attributeName]:
                            logging.error( _("Found '{}' data repeated in '{}' field on {} element in record {}").format( attributeValue, attributeName, element.tag, k ) )
                        uniqueDict["Attribute_"+attributeName].append( attributeValue )

                # Check compulsory elements
                for elementName in self.compulsoryElements:
                    if element.find( elementName ) is None:
                        logging.error( _("Compulsory '{}' element is missing in record with ID '{}' (record {})").format( elementName, ID, k ) )
                    if not element.find( elementName ).text:
                        logging.warning( _("Compulsory '{}' element is blank in record with ID '{}' (record {})").format( elementName, ID, k ) )

                # Check optional elements
                for elementName in self.optionalElements:
                    if element.find( elementName ) is not None:
                        if not element.find( elementName ).text:
                            logging.warning( _("Optional '{}' element is blank in record with ID '{}' (record {})").format( elementName, ID, k ) )

                # Check for unexpected additional elements
                for subelement in element:
                    if subelement.tag not in self.compulsoryElements and subelement.tag not in self.optionalElements:
                        logging.warning( _("Additional '{}' element ('{}') found in record with ID '{}' (record {})").format( subelement.tag, subelement.text, ID, k ) )

                # Check the elements that must contain unique information (in that particular element -- doesn't check across different elements)
                for elementName in self.uniqueElements:
                    if element.find( elementName ) is not None:
                        text = element.find( elementName ).text
                        if text in uniqueDict["Element_"+elementName]:
                            logging.error( _("Found '{}' data repeated in '{}' element in record with ID '{}' (record {})").format( text, elementName, ID, k ) )
                        uniqueDict["Element_"+elementName].append( text )
            else:
                logging.warning( _("Unexpected element: {} in record {}").format( element.tag, k ) )
    # end of __validateSystem

    def __str__( self ):
        """
        This method returns the string representation of a Bible book order system.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "_BibleBookOrdersConverter object"
        result += ('\n' if result else '') + "  Num book order systems loaded ={}".format( len(self.XMLSystems) )
        if 0: # Make it verbose
            for x in self.XMLSystems:
                result += ('\n' if result else '') + " {}".format( x )
                title = self.XMLSystems[x]["title"]
                if title: result += ('\n' if result else '') + "   {}".format( title )
                version = self.XMLSystems[x]["version"]
                if version: result += ('\n' if result else '') + "    Version:{}".format( version )
                date = self.XMLSystems[x]["date"]
                if date: result += ('\n' if result else '') + "    Last updated:{}".format( date )
                result += ('\n' if result else '') + "    Num books ={}".format( len(self.XMLSystems[x]["tree"]) )
        return result
    # end of __str__

    def __len__( self ):
        """ Returns the number of systems loaded. """
        return len( self.XMLSystems )
    # end of __len__

    def importDataToPython( self ):
        """
        Loads (and pivots) the data (not including the header) into suitable Python containers to use in a Python program.
        """
        assert( self.XMLSystems )
        if self.__DataDicts and self.__DataLists: # We've already done an import/restructuring -- no need to repeat it
            return self.__DataDicts, self.__DataLists

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
                    logging.error( _("Unrecognized '{}' book abbreviation in '{}' book order system").format( bookRA, bookOrderSystemCode ) )
                # Save it by book reference abbreviation
                if bookRA in bookDataDict:
                    logging.error( _("Duplicate {} book reference abbreviations in '{}' book order system").format( bookRA, bookOrderSystemCode ) )
                bookDataDict[bookRA] = intID
                if intID in idDataDict:
                    logging.error( _("Duplicate {} ID (book index) numbers in '{}' book order system").format( intID, bookOrderSystemCode ) )
                idDataDict[intID] = bookRA
                BBBList.append( bookRA )

            if Globals.strictCheckingFlag: # check for duplicates
                for checkSystemCode in self.__DataLists:
                    if self.__DataLists[checkSystemCode] == BBBList:
                        logging.error( _("{} and {} book order systems are identical ({} books)").format( bookOrderSystemCode, checkSystemCode, len(BBBList) ) )

            # Now put it into my dictionaries for easy access
            self.__DataDicts[bookOrderSystemCode] = bookDataDict, idDataDict
            self.__DataLists[bookOrderSystemCode] = BBBList # Don't explicitly include the book index numbers, but otherwise the same information in a different form
        return self.__DataDicts, self.__DataLists
    # end of importDataToPython

    def exportDataToPython( self, filepath=None ):
        """
        Writes the information tables to a .py file that can be cut and pasted into a Python program.
        """
        def exportPythonDict( theFile, theDict, dictName, keyComment, fieldsComment ):
            """Exports theDict to theFile."""
            theFile.write( '  "{}": {{\n    # Key is{}\n    # Fields are:{}\n'.format( dictName, keyComment, fieldsComment ) )
            for dictKey in theDict.keys():
                theFile.write( '   {}:{},\n'.format( repr(dictKey), repr(theDict[dictKey]) ) )
            theFile.write( "  }}, # end of{} ({} entries)\n\n".format( dictName, len(theDict) ) )
        # end of exportPythonDict

        from datetime import datetime

        assert( self.XMLSystems )
        self.importDataToPython()
        assert( self.__DataDicts and self.__DataLists )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables.py" )
        if Globals.verbosityLevel > 1: print( _("Exporting to {}...").format( filepath ) )

        # Split into two dictionaries
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "#{}\n#\n".format( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by BibleBookOrders.py V{} on {}\n#\n".format( versionString, datetime.now() ) )
            #if self.title: myFile.write( "#{}\n".format( self.title ) )
            #if self.version: myFile.write( "#  Version:{}\n".format( self.version ) )
            #if self.date: myFile.write( "#  Date:{}\n#\n".format( self.date ) )
            #myFile.write( "#  {}{} entries loaded from the original XML file.\n".format( len(self.namesTree), self.treeTag ) )
            myFile.write( "#  {}{} loaded from the original XML files.\n#\n\n".format( len(self.XMLSystems), self.treeTag ) )
            myFile.write( "from collections import OrderedDict\n\n\n" )
            myFile.write( "bookDataDict = {\n  # Key is versificationSystemName\n  # Fields are omittedVersesSystem\n\n" )
            for systemName in self.__DataDicts:
                bookDataDict, idDataDict = self.__DataDicts[systemName]
                exportPythonDict( myFile, bookDataDict, systemName, "referenceAbbreviation", "id" )
            myFile.write( "}} # end of bookDataDict ({} systems)\n\n\n\n".format( len(self.__DataDicts) ) )
            myFile.write( "idDataDict = {\n  # Key is versificationSystemName\n  # Fields are omittedVersesSystem\n\n" )
            for systemName in self.__DataDicts:
                bookDataDict, idDataDict = self.__DataDicts[systemName]
                exportPythonDict( myFile, idDataDict, systemName, "id", "referenceAbbreviation" )
            myFile.write( "}} # end of idDataDict ({} systems)\n".format( len(self.__DataDicts) ) )
            myFile.write( "# end of{}".format( os.path.basename(filepath) ) )
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
        assert( self.__DataDicts and self.__DataLists )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables.json" )
        if Globals.verbosityLevel > 1: print( _("Exporting to {}...").format( filepath ) )
        with open( filepath, 'wt' ) as myFile:
            #myFile.write( "#{}\n#\n".format( filepath ) ) # Not sure yet if these comment fields are allowed in JSON
            #myFile.write( "# This UTF-8 file was automatically generated by BibleBooksCodes.py V{} on {}\n#\n".format( versionString, datetime.now() ) )
            #if self.titleString: myFile.write( "#{} data\n".format( self.titleString ) )
            #if self.versionString: myFile.write( "#  Version:{}\n".format( self.versionString ) )
            #if self.dateString: myFile.write( "#  Date:{}\n#\n".format( self.dateString ) )
            #myFile.write( "#  {}{} loaded from the original XML file.\n#\n\n".format( len(self.XMLtree), self.treeTag ) )
            json.dump( self.__DataDicts, myFile, indent=2 )
            #myFile.write( "\n\n# end of{}".format( os.path.basename(filepath) ) )
    # end of exportDataToJSON

    def exportDataToC( self, filepath=None ):
        """
        Writes the information tables to a .h file that can be included in c and c++ programs.
        """
        def writeStructure( hFile, structName, structure ):
            """ Writes a typedef to the .h file. """
            hFile.write( "typedef struct{}EntryStruct {{\n".format( structName ) )
            for declaration in structure.split(';'):
                adjDeclaration = declaration.strip()
                if adjDeclaration: hFile.write( "   {};\n".format( adjDeclaration ) )
            hFile.write( "}}{}Entry;\n\n".format( structName ) )
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
                        else: logging.error( _("Cannot convert unknown field type '{}' in entry '{}'").format( field, entry ) )
                return result
            # end of convertEntry

            #for dictKey in theDict.keys(): # Have to iterate this :(
            #    fieldsCount = len( theDict[dictKey] ) + 1 # Add one since we include the key in the count
            #    break # We only check the first (random) entry we get
            fieldsCount = 2

            cFile.write( "const static{}\n{}[{}] = {{\n  // Fields ({}) are{}\n  // Sorted by{}\n".format( structName, dictName, len(theDict), fieldsCount, structure, sortedBy ) )
            for dictKey in sorted(theDict.keys()):
                if isinstance( dictKey, str ):
                    cFile.write( "  {{\"{}\",{}}},\n".format( dictKey, convertEntry(theDict[dictKey]) ) )
                elif isinstance( dictKey, int ):
                    cFile.write( "  {{{},{}}},\n".format( dictKey, convertEntry(theDict[dictKey]) ) )
                else:
                    logging.error( _("Can't handle this type of data yet: {}").format( dictKey ) )
            cFile.write( "}}; //{} ({} entries)\n\n".format( dictName, len(theDict) ) )
        # end of exportPythonDict

        from datetime import datetime

        assert( self.XMLSystems )
        self.importDataToPython()
        assert( self.__DataDicts and self.__DataLists )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables" )
        hFilepath = filepath + '.h'
        cFilepath = filepath + '.c'
        if Globals.verbosityLevel > 1: print( _("Exporting to {}...").format( cFilepath ) ) # Don't bother telling them about the .h file
        ifdefName = self.filenameBase.upper() + "_Tables_h"

        with open( hFilepath, 'wt' ) as myHFile, open( cFilepath, 'wt' ) as myCFile:
            myHFile.write( "//{}\n//\n".format( hFilepath ) )
            myCFile.write( "//{}\n//\n".format( cFilepath ) )
            lines = "// This UTF-8 file was automatically generated by BibleBookOrders.py V{} on {}\n//\n".format( versionString, datetime.now() )
            myHFile.write( lines ); myCFile.write( lines )
            myCFile.write( "//  {}{} loaded from the original XML file.\n//\n\n".format( len(self.XMLSystems), self.treeTag ) )
            myHFile.write( "\n#ifndef{}\n#define{}\n\n".format( ifdefName, ifdefName ) )
            myCFile.write( '#include "{}"\n\n'.format( os.path.basename(hFilepath) ) )

            CHAR = "const unsigned char"
            BYTE = "const int"
            N1 = "bookOrderByRef"
            N2 = "bookOrderByIndex"
            S1 = "{} referenceAbbreviation[3+1];{} indexNumber;".format(CHAR,BYTE)
            S2 = "{} indexNumber;{} referenceAbbreviation[3+1];".format(BYTE,CHAR)
            writeStructure( myHFile, N1, S1 )
            writeStructure( myHFile, N2, S2 )
            writeStructure( myHFile, "table", "{}* systemName;{}Entry* byReference;{}Entry* byBook;".format(CHAR,N1,N2) ) # I'm not sure if I need one or two asterisks on those last two
                                                                                                        # They're supposed to be pointers to an array of structures
            myHFile.write( "#endif //{}\n\n".format( ifdefName ) )
            myHFile.write( "// end of{}".format( os.path.basename(hFilepath) ) )

            for systemName in self.__DataDicts: # Now write out the actual data into the .c file
                bookDataDict, idDataDict = self.__DataDicts[systemName]
                myCFile.write( "\n//{}\n".format( systemName ) )
                exportPythonDict( myCFile, bookDataDict, systemName+"BookDataDict", N1+"Entry", "referenceAbbreviation", S1 )
                exportPythonDict( myCFile, idDataDict, systemName+"IndexNumberDataDict", N2+"Entry", "indexNumber", S2 )

            # Write out the final table of pointers to the above information
            myCFile.write( "\n// Pointers to above data\nconst static tableEntry bookOrderSystemTable[{}] = {{\n".format( len(self.__DataDicts) ) )
            for systemName in self.__DataDicts: # Now write out the actual pointer data into the .c file
                myCFile.write( '  {{ "{}",{},{} }},\n'.format( systemName, systemName+"BookDataDict", systemName+"IndexNumberDataDict" ) )
            myCFile.write( "}}; //{} entries\n\n".format( len(self.__DataDicts) ) )
            myCFile.write( "// end of{}".format( os.path.basename(cFilepath) ) )
    # end of exportDataToC

    def checkBookOrderSystem( self, systemName, bookOrderSchemeToCheck ):
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
                #print( "  {} matches '{}' book order system".format( systemName, bookOrderSystemCode ) )
                systemMatchCount += 1
                matchedBookOrderSystemCodes.append( bookOrderSystemCode )
            else:
                if len(self.Lists[bookOrderSystemCode]) == len(bookOrderSchemeToCheck):
                    for BBB1,BBB2 in zip(self.Lists[bookOrderSystemCode],bookOrderSchemeToCheck):
                        if BBB1 != BBB2: break
                    thisError = "    Doesn't match '{}' system (Both have {} books, but{} instead of {})".format( bookOrderSystemCode, len(bookOrderSchemeToCheck), BBB1, BBB2 )
                else:
                    thisError = "    Doesn't match '{}' system ({} books instead of {})".format( bookOrderSystemCode, len(bookOrderSchemeToCheck), len(self.Lists[bookOrderSystemCode]) )
                theseErrors += ("\n" if theseErrors else "") + thisError
                errorSummary += ("\n" if errorSummary else "") + thisError
                systemMismatchCount += 1

        if systemMatchCount:
            if systemMatchCount == 1: # What we hope for
                print( _("  {} matched {} book order (with these {} books)").format( systemName, matchedBookOrderSystemCodes[0], len(bookOrderSchemeToCheck) ) )
                if Globals.commandLineOptions.debug: print( errorSummary )
            else:
                print( _("  {} matched {} book order system(s): {} (with these {} books)").format( systemName, systemMatchCount, matchedBookOrderSystemCodes, len(bookOrderSchemeToCheck) ) )
                if Globals.commandLineOptions.debug: print( errorSummary )
        else:
            print( _("  {} mismatched {} book order systems (with these {} books)").format( systemName, systemMismatchCount, len(bookOrderSchemeToCheck) ) )
            print( allErrors if Globals.commandLineOptions.debug else errorSummary )

        if Globals.commandLineOptions.export and not systemMatchCount: # Write a new file
            outputFilepath = os.path.join( "ScrapedFiles", "BibleBookOrder_"+systemName + ".xml" )
            print( _("Writing {} {} books to {}...").format( len(bookOrderSchemeToCheck), systemName, outputFilepath ) )
            with open( outputFilepath, 'wt' ) as myFile:
                for n,BBB in enumerate(bookOrderSchemeToCheck):
                    myFile.write( '  <book id="{}">{}</book>\n'.format( n+1,BBB ) )
                myFile.write( "</BibleBookOrderSystem>" )
    # end of checkBookOrderSystem
# end of _BibleBookOrdersConverter class


@singleton # Can only ever have one instance
class BibleBookOrderSystems:
    """
    Class for handling Bible book order systems.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.

    Note: BBB is used in this class to represent the three-character referenceAbbreviation.
    """

    def __init__( self ): # We can't give this parameters because of the singleton
        """
        Constructor: 
        """
        self.__bboc = _BibleBookOrdersConverter()
        self.__DataDicts = self.__DataLists = None # We'll import into these in loadData
    # end of __init__

    def loadData( self, XMLFolder=None ):
        """ Loads the XML data file and imports it to dictionary format (if not done already). """
        if not self.__DataDicts or not self.__DataLists: # Don't do this unnecessarily
            self.__bboc.loadSystems( XMLFolder ) # Load the XML (if not done already)
            self.__DataDicts, self.__DataLists = self.__bboc.importDataToPython() # Get the various dictionaries organised for quick lookup
            assert( len(self.__DataDicts) == len(self.__DataLists) )
            del self.__bboc # Now the converter class (that handles the XML) is no longer needed
        return self
    # end of loadData

    def __str__( self ):
        """
        This method returns the string representation of a Bible book order.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "BibleBooksOrders object"
        result += ('\n' if result else '') + "  Num systems ={}".format( len(self.__DataDicts) )
        return result
    # end of __str__

    def __len__( self ):
        """ Returns the number of systems loaded. """
        assert( len(self.__DataDicts) == len(self.__DataLists) )
        return len( self.__DataDicts )
    # end of __len__

    def __contains__( self, name ):
        """ Returns True/False if the name is in this system. """
        return name in self.__DataLists
    # end of __contains__

    def getAvailableBookOrderSystemNames( self ):
        """ Returns a list of available system name strings. """
        return [x for x in self.__DataLists]
    # end of getAvailableBookOrderSystemNames

    def getBookOrderSystem( self, systemName ):
        """ Returns two dictionaries and a list object."""
        if systemName in self.__DataDicts:
            return self.__DataDicts[systemName][0], self.__DataDicts[systemName][1], self.__DataLists[systemName]
        # else
        logging.error( _("No '{}' system in Bible Book Orders").format( systemName ) )
        if Globals.verbosityLevel > 2: logging.error( _("Available systems are {}").format( self.getAvailableSystemNames() ) )
    # end of getBookOrderSystem

    def numBooks( self, systemName ):
        """ Returns the number of books in this system. """
        return len( self.__DataLists[systemName] )
    # end of numBooks

    def containsBook( self, systemName, BBB ):
        """ Return True if the book is in this system. """
        return BBB in self.__DataLists[systemName]
    # end of containsBook

    def getBookList( self, systemName ):
        """ Returns the list of BBB book reference abbreviations in the correct order. """
        return self.__DataLists[systemName]
    # end of getBookList

    def checkBookOrderSystem( self, systemName, bookOrderSchemeToCheck ):
        """
        Check the given book order scheme against all the loaded systems.
        Create a new book order file if it doesn't match any.
        """
        assert( systemName )
        assert( bookOrderSchemeToCheck )
        assert( self.__DataLists )
        #print( systemName, bookOrderSchemeToCheck )

        matchedBookOrderSystemCodes = []
        systemMatchCount, systemMismatchCount, allErrors, errorSummary = 0, 0, '', ''
        for bookOrderSystemCode in self.__DataLists: # Step through the various reference schemes
            theseErrors = ''
            if self.__DataLists[bookOrderSystemCode] == bookOrderSchemeToCheck:
                #print( "  {} matches '{}' book order system".format( systemName, bookOrderSystemCode ) )
                systemMatchCount += 1
                matchedBookOrderSystemCodes.append( bookOrderSystemCode )
            else:
                if len(self.__DataLists[bookOrderSystemCode]) == len(bookOrderSchemeToCheck):
                    for BBB1,BBB2 in zip(self.__DataLists[bookOrderSystemCode],bookOrderSchemeToCheck):
                        if BBB1 != BBB2: break
                    thisError = "    Doesn't match '{}' system (Both have {} books, but {} instead of {})".format( bookOrderSystemCode, len(bookOrderSchemeToCheck), BBB1, BBB2 )
                else:
                    thisError = "    Doesn't match '{}' system ({} books instead of {})".format( bookOrderSystemCode, len(bookOrderSchemeToCheck), len(self.__DataLists[bookOrderSystemCode]) )
                theseErrors += ("\n" if theseErrors else "") + thisError
                errorSummary += ("\n" if errorSummary else "") + thisError
                systemMismatchCount += 1

        if systemMatchCount:
            if systemMatchCount == 1: # What we hope for
                print( _("  {} matched {} book order (with these {} books)").format( systemName, matchedBookOrderSystemCodes[0], len(bookOrderSchemeToCheck) ) )
                if Globals.commandLineOptions.debug: print( errorSummary )
            else:
                print( _("  {} matched {} book order system(s): {} (with these {} books)").format( systemName, systemMatchCount, matchedBookOrderSystemCodes, len(bookOrderSchemeToCheck) ) )
                if Globals.commandLineOptions.debug: print( errorSummary )
        else:
            print( _("  {} mismatched {} book order systems (with these {} books)").format( systemName, systemMismatchCount, len(bookOrderSchemeToCheck) ) )
            print( allErrors if Globals.commandLineOptions.debug else errorSummary )

        if Globals.commandLineOptions.export and not systemMatchCount: # Write a new file
            outputFilepath = os.path.join( "ScrapedFiles", "BibleBookOrder_"+systemName + ".xml" )
            print( _("Writing {} {} books to {}...").format( len(bookOrderSchemeToCheck), systemName, outputFilepath ) )
            with open( outputFilepath, 'wt' ) as myFile:
                for n,BBB in enumerate(bookOrderSchemeToCheck):
                    myFile.write( '  <book id="{}">{}</book>\n'.format( n+1,BBB ) )
                myFile.write( "</BibleBookOrderSystem>" )
    # end of checkBookOrderSystem
# end of BibleBookOrderSystems class


class BibleBookOrderSystem:
    """
    Class for handling an individual Bible book order system.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.

    Note: BBB is used in this class to represent the three-character referenceAbbreviation.
    """

    def __init__( self, systemName ):
        """
        Constructor: 
        """
        self.__systemName = systemName
        self.__bbos = BibleBookOrderSystems().loadData() # Doesn't reload the XML unnecessarily :)
        self.__BookOrderBookDict, self.__BookOrderNumberDict, self.__BookOrderList = self.__bbos.getBookOrderSystem( self.__systemName )
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book order.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "BibleBooksOrder object"
        result += ('\n' if result else '') + " {} book order system".format( self.__systemName )
        result += ('\n' if result else '') + "  Num books ={}".format( self.numBooks() )
        return result
    # end of __str__

    def __len__( self ):
        """ Returns the number of books in this system. """
        return len( self.__BookOrderList )
    # end of __len__

    def numBooks( self ):
        """ Returns the number of books in this system. """
        return len( self.__BookOrderList )
    # end of numBooks

    def __contains__( self, BBB ):
        """ Returns True/False if the book is in this system. """
        assert( len(BBB) == 3 )
        return BBB in self.__BookOrderList
    # end of __contains__

    def containsBook( self, BBB ):
        """ Return True/False if the book is in this system. """
        assert( len(BBB) == 3 )
        return BBB in self.__BookOrderList
    # end of containsBook

    def getBookOrderSystemName( self ):
        """ Return the book order system name. """
        return self.__systemName
    # end of getBookOrderSystemName

    def getBookPosition( self, BBB ):
        """ Returns the book position number (1..n). """
        assert( len(BBB) == 3 )
        return self.__BookOrderBookDict[BBB]
    # end of getBookPosition

    def getBookAtPosition( self, n ):
        """ Returns the BBB book reference abbreviation for the position number (1..n). """
        return self.__BookOrderNumberDict[n]
    # end of getBookAtPosition

    def getBookList( self ):
        """ Returns the list of BBB book reference abbreviations in the correct order. """
        return self.__BookOrderList
    # end of getBookList

    def getNextBook( self, BBB ):
        """ Returns the book (if any) after the given one. """
        assert( len(BBB)==3 )
        nextPosition = self.__BookOrderBookDict[BBB] + 1
        if nextPosition in self.__BookOrderNumberDict: return self.__BookOrderNumberDict[nextPosition]
    # end of getNextBook

    def correctlyOrdered( self, BBB1, BBB2 ):
        """ Returns True/False if the two books are in the correct order. """
        assert( BBB1 and len(BBB1)==3 )
        assert( BBB2 and len(BBB2)==3 )
        return self.__BookOrderBookDict[BBB1] < self.__BookOrderBookDict[BBB2]
    # end of correctlyOrdered
# end of BibleBookOrderSystem class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v{}".format( versionString ) )
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML files to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 1: print( "{} V{}".format( progName, versionString ) )

    if Globals.commandLineOptions.export:
        bbosc = _BibleBookOrdersConverter().loadSystems() # Load the XML
        bbosc.exportDataToPython() # Produce the .py tables
        bbosc.exportDataToJSON() # Produce a json output file
        bbosc.exportDataToC() # Produce the .h and .c tables

    else: # Must be demo mode
        # Demo the converter object
        bbosc = _BibleBookOrdersConverter().loadSystems() # Load the XML
        print( bbosc ) # Just print a summary

        # Demo the BibleBookOrders object
        bboss = BibleBookOrderSystems().loadData() # Doesn't reload the XML unnecessarily :)
        print( bboss ) # Just print a summary
        print( _("Number of loaded systems: {}").format( len(bboss) ) )
        print( _("Available system names are: {}").format( bboss.getAvailableBookOrderSystemNames() ) )
        systemName = "VulgateBible"
        print( "Number of books in {} is {}".format( systemName, bboss.numBooks(systemName) ) )
        systemName = "Septuagint"; BBB="ROM"
        print( "{} is in {}:{}".format( BBB, systemName, bboss.containsBook(systemName,BBB) ) )
        for systemName in ("ModernJewish", "EuropeanProtestantNewTestament", ):
            print( "Booklist for {} is {}".format( systemName, bboss.getBookList(systemName) ) )
        bboss.checkBookOrderSystem( "myTest", ['MAT', 'MRK', 'LUK', 'JHN', 'ACT', 'ROM', 'CO1', 'CO2', 'GAL', 'EPH', 'PHP', 'COL', 'TH1', 'TH2', 'TI1', 'TI2', 'TIT', 'PHM', 'HEB', 'JAM', 'PE1', 'PE2', 'JN1', 'JN2', 'JN3', 'JDE', 'ReV'] )

        # Demo a BibleBookOrder object -- this is the one most likely to be wanted by a user
        bbos = BibleBookOrderSystem( "EuropeanProtestantBible" )
        if bbos is not None:
            print( bbos ) # Just print a summary
            print( "Num books is {} or {}".format(len(bbos), bbos.numBooks()) )
            print( "The 3rd book is {}".format( bbos.getBookAtPosition(3) ) )
            print( "Contains Psalms: {}".format( bbos.containsBook("PSA") ) )
            print( "Luke is book #{}".format( bbos.getBookPosition("LUK") ) )
            print( "Book list is: {}".format( bbos.getBookList() ) )
            BBB = "TI1"
            while True:
                BBB2 = bbos.getNextBook( BBB )
                if BBB2 is None: break
                print( " Next book after {} is {}".format(BBB,BBB2) )
                BBB = BBB2
            
# end of main

if __name__ == '__main__':
    main()
# end of BibleBookOrders.py
