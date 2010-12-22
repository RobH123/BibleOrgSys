#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BiblePunctuationSystems.py
#
# Module handling BiblePunctuationSystem_*.xml to produce C and Python data tables
#   Last modified: 2010-12-19 (also update versionString below)
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
Module handling BiblePunctuation_*.xml to produce C and Python data tables.
"""

progName = "Bible Punctuation Systems handler"
versionString = "0.02"


import os, logging
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree

from singleton import singleton
import Globals


@singleton # Can only ever have one instance
class _BiblePunctuationSystemsConvertor:
    """
    A class to handle data for Bible punctuation systems.
    """

    def __init__( self ):
        """
        Constructor.
        """
        self.filenameBase = "BiblePunctuationSystems"

        # These fields are used for parsing the XML
        self.treeTag = "BiblePunctuationSystem"
        self.headerTag = "header"
        self.mainElementTags = ( "booknameCase", "booknameLength", "punctuationAfterBookAbbreviation", "bookChapterSeparator", "spaceAllowedAfterBCS",
                    "chapterBridgeCharacter", "chapterVerseSeparator", "verseSeparator", "verseBridgeCharacter", "chapterSeparator", "bookSeparator" )

        # These fields are used for automatically checking/validating the XML
        self.compulsoryAttributes = ()
        self.optionalAttributes = ()
        self.uniqueAttributes = self.compulsoryAttributes + self.optionalAttributes
        self.compulsoryElements = ()
        self.optionalElements = ()
        self.uniqueElements = self.compulsoryElements + self.optionalElements


        # These are fields that we will fill later
        self.XMLSystems = {}
        self.DataDict = {} # Used for import
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible punctuation system.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "_BiblePunctuationSystemsConvertor object"
        result += ('\n' if result else '') + "  Num punctuation systems loaded = %i" % ( len(self.XMLSystems) )
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
        Load and pre-process the specified punctuation systems.
        """
        if not self.XMLSystems: # Only ever do this once
            if XMLFolder==None: XMLFolder = "DataFiles/PunctuationSystems"
            self.XMLFolder = XMLFolder
            for filename in os.listdir( XMLFolder ):
                filepart, extension = os.path.splitext( filename )
                if extension.upper() == '.XML' and filepart.upper().startswith("BIBLEPUNCTUATIONSYSTEM_"):
                    punctuationSystemCode = filepart[15:]
                    #print( "Loading %s punctuation system from %s..." % ( punctuationSystemCode, filename ) )
                    self.XMLSystems[punctuationSystemCode] = {}
                    self.XMLSystems[punctuationSystemCode]["tree"] = ElementTree().parse( os.path.join( XMLFolder, filename ) )
                    assert( self.XMLSystems[punctuationSystemCode]["tree"] ) # Fail here if we didn't load anything at all

                    # Check and remove the header element
                    if self.XMLSystems[punctuationSystemCode]["tree"].tag  == self.treeTag:
                        header = self.XMLSystems[punctuationSystemCode]["tree"][0]
                        if header.tag == self.headerTag:
                            self.XMLSystems[punctuationSystemCode]["header"] = header
                            self.XMLSystems[punctuationSystemCode]["tree"].remove( header )
                            if len(header)>1:
                                logging.info( "Unexpected elements in header" )
                            elif len(header)==0:
                                logging.info( "Missing work element in header" )
                            else:
                                work = header[0]
                                if work.tag == "work":
                                    self.XMLSystems[punctuationSystemCode]["version"] = work.find("version").text
                                    self.XMLSystems[punctuationSystemCode]["date"] = work.find("date").text
                                    self.XMLSystems[punctuationSystemCode]["title"] = work.find("title").text
                                else:
                                    logging.warning( "Missing work element in header" )
                        else:
                            logging.warning( "Missing header element (looking for '%s' tag)" % ( headerTag ) )
                    else:
                        logging.error( "Expected to load '%s' but got '%s'" % ( treeTag, self.XMLSystems[punctuationSystemCode]["tree"].tag ) )
                    bookCount = 0 # There must be an easier way to do this
                    for subelement in self.XMLSystems[punctuationSystemCode]["tree"]:
                        bookCount += 1
                    logging.info( "    Loaded %i books" % ( bookCount ) )

                    if Globals.strictCheckingFlag:
                        self._validateSystem( self.XMLSystems[punctuationSystemCode]["tree"], punctuationSystemCode )
        return self
    # end of loadSystems

    def _validateSystem( self, punctuationTree, systemName ):
        """
        """
        assert( punctuationTree )

        uniqueDict = {}
        for elementName in self.uniqueElements: uniqueDict["Element_"+elementName] = []
        for attributeName in self.uniqueAttributes: uniqueDict["Attribute_"+attributeName] = []

        for k,element in enumerate(punctuationTree):
            if element.tag in self.mainElementTags:

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
        Checks for duplicate (redundant) punctuation systems.

        Returns True if a duplicate is found.
        """
        systemLists, foundDuplicate = {}, False
        for punctuationSystemCode in self.XMLSystems.keys():
            # Get the referenceAbbreviations all into a list
            bookDataList = []
            for bookElement in self.XMLSystems[punctuationSystemCode]["tree"]:
                bookRA = bookElement.text
            # Compare with existing lists
            for checkSystemCode,checkDataList in systemLists.items():
                if bookDataList == checkDataList:
                    logging.error( "%s and %s punctuation systems are identical" % ( punctuationSystemCode, checkSystemCode ) )
                    foundDuplicate = True
            # Add this new list
            systemLists[punctuationSystemCode] = bookDataList
        return foundDuplicate
    # end of checkDuplicates

    def importDataToPython( self ):
        """
        Loads (and pivots) the data (not including the header) into suitable Python containers to use in a Python program.
        """
        assert( self.XMLSystems )
        if self.DataDict: # We've already done an import/restructuring -- no need to repeat it
            return self.DataDict

        # We'll create a dictionary of dictionaries
        for punctuationSystemCode in self.XMLSystems.keys():
            # Make the data dictionary for this punctuation system
            punctuationDict = {}
            for element in self.XMLSystems[punctuationSystemCode]["tree"]:
                tag = element.tag
                text = element.text
                if tag in punctuationDict: logging.error( "Multiple %s entries in %s punctuation system" % ( tag, punctuationSystemCode ) )
                punctuationDict[tag] = text

            # Now put it into my dictionaries for easy access
            # This part should be customized or added to for however you need to process the data
            self.DataDict[punctuationSystemCode] = punctuationDict
        return self.DataDict
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
        assert( self.DataDict )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables.py" )
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( filepath ) )

        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# %s\n#\n" % ( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by BiblePunctuationSystems.py V%s %s\n#\n" % ( versionString, datetime.now() ) )
            #if self.title: myFile.write( "# %s\n" % ( self.title ) )
            #if self.version: myFile.write( "#  Version: %s\n" % ( self.version ) )
            #if self.date: myFile.write( "#  Date: %s\n#\n" % ( self.date ) )
            #myFile.write( "#   %i %s entries loaded from the original XML file.\n" % ( len(self.namesTree), self.treeTag ) )
            myFile.write( "#   %i %s loaded from the original XML files.\n#\n\n" % ( len(self.XMLSystems), self.treeTag ) )
            myFile.write( "from collections import OrderedDict\n\n\n" )
            myFile.write( "bookDataDict = {\n  # Key is versificationSystemName\n  # Fields are omittedVersesSystem\n\n" )
            for systemName, systemDict in self.DataDict.items():
                exportPythonDict( myFile, systemDict, systemName, "referenceAbbreviation", "id" )
            myFile.write( "} # end of bookDataDict (%i systems)\n\n\n\n" % ( len(self.DataDict) ) )
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
        assert( self.DataDict )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables.json" )
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( filepath ) )
        with open( filepath, 'wt' ) as myFile:
            #myFile.write( "# %s\n#\n" % ( filepath ) ) # Not sure yet if these comment fields are allowed in JSON
            #myFile.write( "# This UTF-8 file was automatically generated by BibleBooksCodes.py on %s\n#\n" % ( datetime.now() ) )
            #if self.titleString: myFile.write( "# %s data\n" % ( self.titleString ) )
            #if self.versionString: myFile.write( "#  Version: %s\n" % ( self.versionString ) )
            #if self.dateString: myFile.write( "#  Date: %s\n#\n" % ( self.dateString ) )
            #myFile.write( "#   %i %s loaded from the original XML file.\n#\n\n" % ( len(self.XMLtree), self.treeTag ) )
            json.dump( self.DataDict, myFile, indent=2 )
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
        assert( self.DataDict )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables" )
        hFilepath = filepath + '.h'
        cFilepath = filepath + '.c'
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( cFilepath ) ) # Don't bother telling them about the .h file
        ifdefName = self.filenameBase.upper() + "_Tables_h"

        with open( hFilepath, 'wt' ) as myHFile, open( cFilepath, 'wt' ) as myCFile:
            myHFile.write( "// %s\n//\n" % ( hFilepath ) )
            myCFile.write( "// %s\n//\n" % ( cFilepath ) )
            lines = "// This UTF-8 file was automatically generated by BiblePunctuationSystems.py on %s\n//\n" % datetime.now()
            myHFile.write( lines ); myCFile.write( lines )
            myCFile.write( "//   %i %s loaded from the original XML file.\n//\n\n" % ( len(self.XMLSystems), self.treeTag ) )
            myHFile.write( "\n#ifndef %s\n#define %s\n\n" % ( ifdefName, ifdefName ) )
            myCFile.write( '#include "%s"\n\n' % os.path.basename(hFilepath) )

            CHAR = "const unsigned char"
            BYTE = "const int"
            N1 = "punctuationByRef"
            N2 = "punctuationByIndex"
            S1 = "%s referenceAbbreviation[3+1]; %s indexNumber;" % (CHAR,BYTE)
            S2 = "%s indexNumber; %s referenceAbbreviation[3+1];" % (BYTE,CHAR)
            writeStructure( myHFile, N1, S1 )
            writeStructure( myHFile, N2, S2 )
            writeStructure( myHFile, "table", "%s* systemName; %sEntry* byReference; %sEntry* byBook;" % (CHAR,N1,N2) ) # I'm not sure if I need one or two asterisks on those last two
                                                                                                        # They're supposed to be pointers to an array of structures
            myHFile.write( "#endif // %s\n\n" % ( ifdefName ) )
            myHFile.write( "// end of %s" % os.path.basename(hFilepath) )

            for systemName, systemDict in self.DataDict.items(): # Now write out the actual data into the .c file
                myCFile.write( "\n// %s\n" % ( systemName ) )
                exportPythonDict( myCFile, systemDict, systemName+"BookDataDict", N1+"Entry", "referenceAbbreviation", S1 )

            # Write out the final table of pointers to the above information
            myCFile.write( "\n// Pointers to above data\nconst static tableEntry punctuationSystemTable[%i] = {\n" % len(self.DataDict) )
            for systemName in self.DataDict: # Now write out the actual pointer data into the .c file
                myCFile.write( '  { "%s", %s, %s },\n' % ( systemName, systemName+"BookDataDict", systemName+"IndexNumberDataDict" ) )
            myCFile.write( "}; // %i entries\n\n" % len(self.DataDict) )
            myCFile.write( "// end of %s" % os.path.basename(cFilepath) )
    # end of exportDataToC

    def checkPunctuationSystem( self, systemName, punctuationSchemeToCheck, exportFlag=False, debugFlag=False ):
        """
        Check the given punctuation scheme against all the loaded systems.
        Create a new punctuation file if it doesn't match any.
        """
        assert( systemName )
        assert( punctuationSchemeToCheck )
        assert( self.Lists )
        #print( systemName, punctuationSchemeToCheck )

        matchedPunctuationSystemCodes = []
        systemMatchCount, systemMismatchCount, allErrors, errorSummary = 0, 0, '', ''
        for punctuationSystemCode in self.Lists: # Step through the various reference schemes
            theseErrors = ''
            if self.Lists[punctuationSystemCode] == punctuationSchemeToCheck:
                #print( "  Matches '%s' punctuation system" % ( punctuationSystemCode ) )
                systemMatchCount += 1
                matchedPunctuationSystemCodes.append( punctuationSystemCode )
            else:
                if len(self.Lists[punctuationSystemCode]) == len(punctuationSchemeToCheck):
                    for BBB1,BBB2 in zip(self.Lists[punctuationSystemCode],punctuationSchemeToCheck):
                        if BBB1 != BBB2: break
                    thisError = "    Doesn't match '%s' system (Both have %i books, but %s instead of %s)" % ( punctuationSystemCode, len(punctuationSchemeToCheck), BBB1, BBB2 )
                else:
                    thisError = "    Doesn't match '%s' system (%i books instead of %i)" % ( punctuationSystemCode, len(punctuationSchemeToCheck), len(self.Lists[punctuationSystemCode]) )
                theseErrors += ("\n" if theseErrors else "") + thisError
                errorSummary += ("\n" if errorSummary else "") + thisError
                systemMismatchCount += 1

        if systemMatchCount:
            if systemMatchCount == 1: # What we hope for
                print( "  Matched %s punctuation (with these %i books)" % ( matchedPunctuationSystemCodes[0], len(punctuationSchemeToCheck) ) )
                if debugFlag: print( errorSummary )
            else:
                print( "  Matched %i punctuation system(s): %s (with these %i books)" % ( systemMatchCount, matchedPunctuationSystemCodes, len(punctuationSchemeToCheck) ) )
                if debugFlag: print( errorSummary )
        else:
            print( "  Mismatched %i punctuation systems (with these %i books)" % ( systemMismatchCount, len(punctuationSchemeToCheck) ) )
            if debugFlag: print( allErrors )
            else: print( errorSummary)

        if exportFlag and not systemMatchCount: # Write a new file
            outputFilepath = os.path.join( "ScrapedFiles", "BiblePunctuation_"+systemName + ".xml" )
            if Globals.verbosityLevel > 1: print( "Writing %i books to %s..." % ( len(punctuationSchemeToCheck), outputFilepath ) )
            with open( outputFilepath, 'wt' ) as myFile:
                for n,BBB in enumerate(punctuationSchemeToCheck):
                    myFile.write( '  <book id="%i">%s</book>\n' % ( n+1,BBB ) )
                myFile.write( "</BiblePunctuationSystem>" )
    # end of checkPunctuationSystem
# end of _BiblePunctuationSystemsConvertor class


@singleton # Can only ever have one instance
class BiblePunctuationSystems:
    """
    Class for handling Bible punctuation systems.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.
    """

    def __init__( self ): # We can't give this parameters because of the singleton
        """
        Constructor: 
        """
        self.bpsc = _BiblePunctuationSystemsConvertor()
        self.Dict = None # We'll import into this in loadData
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible punctuation.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "BiblePunctuationSystems object"
        result += ('\n' if result else '') + "  Num systems = %i" % ( len(self.Dict) )
        return result
    # end of __str__

    def loadData( self, XMLFolder=None ):
        """ Loads the XML data file and imports it to dictionary format (if not done already). """
        if not self.Dict: # Don't do this unnecessarily
            if XMLFolder is not None: logging.warning( "Bible punctuation systems are already loaded -- your given folder of '%s' was ignored" % XMLFolder )
            self.bpsc.loadSystems( XMLFolder ) # Load the XML (if not done already)
            self.Dict = self.bpsc.importDataToPython() # Get the various dictionaries organised for quick lookup
            del self.bpsc # Now the convertor class (that handles the XML) is no longer needed
        return self
    # end of loadData

    # TODO: Add some useful routines in here

# end of BiblePunctuationSystems class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v%s" % ( versionString ) )
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML files to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 0: print( "%s V%s" % ( progName, versionString ) )

    if Globals.commandLineOptions.export:
        bpsc = _BiblePunctuationSystemsConvertor().loadSystems() # Load the XML
        bpsc.checkDuplicates()
        bpsc.exportDataToPython() # Produce the .py tables
        bpsc.exportDataToJSON() # Produce a json output file
        bpsc.exportDataToC() # Produce the .h and .c tables

    else: # Must be demo mode
        # Demo the convertor object
        bpsc = _BiblePunctuationSystemsConvertor().loadSystems() # Load the XML
        bpsc.checkDuplicates()
        print( bpsc ) # Just print a summary

        # Demo the BiblePunctuationSystems object
        bps = BiblePunctuationSystems().loadData() # Doesn't reload the XML unnecessarily :)
        print( bps ) # Just print a summary
# end of main

if __name__ == '__main__':
    main()
# end of BiblePunctuationSystems.py
