#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ISO_639_3_Languages.py
#
# Module handling ISO_639_3.xml to produce C and Python data tables
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
Module handling ISO_639_3_Languages.xml to produce C and Python data tables.
"""

progName = "ISO 639_3_Languages handler"
versionString = "0.90"

import logging, os.path
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree

from singleton import singleton
import Globals


@singleton # Can only ever have one instance
class _ISO_639_3_Languages_Convertor:
    """
    Class for handling and converting ISO 639-3 language codes.
    """

    def __init__( self ):
        """
        Constructor: expects the filepath of the source XML file.
        Loads (and crudely validates the XML file) into an element tree.
        """
        self.filenameBase = "iso_639_3"

        # These fields are used for parsing the XML
        self.treeTag = "iso_639_3_entries"
        self.mainElementTag = "iso_639_3_entry"

        # These fields are used for automatically checking/validating the XML
        self.compulsoryAttributes = ( "id", "name", "type", "scope" )
        self.optionalAttributes = ( "part1_code", "part2_code" )
        self.uniqueAttributes = ( "id", "name", "part1_code", "part2_code" )
        self.compulsoryElements = ()
        self.optionalElements = ()
        self.uniqueElements = self.compulsoryElements + self.optionalElements

        self.title = "ISO 639-3 language codes"

        # These are fields that we will fill later
        self.XMLtree, self.DataDicts = None, None
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "_ISO_639_3_Languages_Convertor object"
        if self.title: result += ('\n' if result else '') + self.title
        result += ('\n' if result else '') + "  Num entries = " + str(len(self.XMLtree))
        return result
    # end of __str__

    def loadAndValidate( self, XMLFilepath=None ):
        """
        Loads (and crudely validates the XML file) into an element tree.
            Allows the filepath of the source XML file to be specified, otherwise uses the default.
        """
        if self.XMLtree is None: # We mustn't have already have loaded the data
            if XMLFilepath is None:
                XMLFilepath = os.path.join( "DataFiles", self.filenameBase + ".xml" )

            self._load( XMLFilepath )
            if Globals.strictCheckingFlag:
                self._validate()
        return self
    # end of loadAndValidate

    def _load( self, XMLFilepath ):
        """
        Load the source XML file and remove the header from the tree.
        Also, extracts some useful Attributes from the header element.
        """
        assert( XMLFilepath )
        self.XMLFilepath = XMLFilepath
        assert( self.XMLtree is None or len(self.XMLtree)==0 ) # Make sure we're not doing this twice

        if Globals.verbosityLevel > 1: print( "Loading ISO 639-3 languages XML file from '%s'..." % XMLFilepath )
        self.XMLtree = ElementTree().parse( XMLFilepath )
        assert( self.XMLtree ) # Fail here if we didn't load anything at all

        if self.XMLtree.tag  != self.treeTag:
            logging.error( "Expected to load '%s' but got '%s'" % ( self.treeTag, self.XMLtree.tag ) )
    # end of _load

    def _validate( self ):
        """
        Check/validate the loaded data.
        """
        assert( self.XMLtree )

        uniqueDict = {}
        for attributeName in self.uniqueAttributes: uniqueDict[attributeName] = []

        for j,element in enumerate(self.XMLtree):
            if element.tag == self.mainElementTag:
                # Check compulsory attributes on this main element
                for attributeName in self.compulsoryAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is None:
                        logging.error( "Compulsory '%s' attribute is missing from %s element in record %i" % ( attributeName, element.tag, j ) )
                    if not attributeValue:
                        logging.warning( "Compulsory '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, j ) )

                # Check optional attributes on this main element
                for attributeName in self.optionalAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if not attributeValue:
                            logging.warning( "Optional '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, j ) )

                # Check for unexpected additional attributes on this main element
                for attributeName in element.keys():
                    attributeValue = element.get( attributeName )
                    if attributeName not in self.compulsoryAttributes and attributeName not in self.optionalAttributes:
                        logging.warning( "Additional '%s' attribute ('%s') found on %s element in record %i" % ( attributeName, attributeValue, element.tag, j ) )

                # Check the attributes that must contain unique information (in that particular field -- doesn't check across different attributes)
                for attributeName in self.uniqueAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if attributeValue in uniqueDict[attributeName]:
                            logging.error( "Found '%s' data repeated in '%s' field on %s element in record %i" % ( attributeValue, attributeName, element.tag, j ) )
                        uniqueDict[attributeName].append( attributeValue )
            else:
                logging.warning( "Unexpected element: %s in record %i" % ( element.tag, j ) )
    # end of _validate

    def importDataToPython( self ):
        """
        Loads (and pivots) the data into suitable Python containers to use in a Python program.
        (Of course, you can just use the elementTree in self.XMLtree if you prefer.)
        """
        assert( self.XMLtree )
        if self.DataDicts: # We've already done an import/restructuring -- no need to repeat it
            return self.DataDicts

        # We'll create a number of dictionaries with different Attributes as the key
        myIDDict, myNameDict = OrderedDict(), OrderedDict()
        for element in self.XMLtree:
            # Get the required information out of the tree for this element
            # Start with the compulsory attributes
            ID = element.get("id")
            Name = element.get("name")
            Type = element.get("type")
            Scope = element.get("scope")
            # The optional attributes are set to None if they don't exist
            Part1Code = element.get("part1_code")
            Part2Code = element.get("part2_code")

            # Now put it into my dictionaries for easy access
            # This part should be customized or added to for however you need to process the data
            #   Add .upper() if you require the abbreviations to be uppercase (or .lower() for lower case)
            if "id" in self.compulsoryAttributes or ID:
                if "id" in self.uniqueElements: assert( ID not in myIDDict ) # Shouldn't be any duplicates
                myIDDict[ID] = ( Name, Type, Scope, Part1Code, Part2Code, )
            if "name" in self.compulsoryAttributes or Name:
                if "name" in self.uniqueElements: assert( Name not in myNameDict ) # Shouldn't be any duplicates
                myNameDict[Name] = ( ID, Type, Scope, Part1Code, Part2Code, )
            self.DataDicts = myIDDict, myNameDict
        return self.DataDicts # Just throw away any of the dictionaries that you don't need
    # end of importDataToPython

    def exportDataToPython( self, filepath=None ):
        """
        Writes the information tables to a .py file that can be cut and pasted into a Python program.
        """
        def exportPythonDict( theFile, theDict, dictName, keyComment, fieldsComment ):
            """Exports theDict to theFile."""
            theFile.write( "%s = {\n  # Key is %s\n  # Fields are: %s\n" % ( dictName, keyComment, fieldsComment ) )
            for dictKey in sorted(theDict.keys()):
                theFile.write( "  %s: %s,\n" % ( repr(dictKey), theDict[dictKey] ) )
            theFile.write( "}\n# end of %s\n\n" % ( dictName ) )
        # end of exportPythonDict

        from datetime import datetime

        assert( self.XMLtree )
        self.importDataToPython()
        assert( self.DataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Languages_Tables.py" )
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( filepath ) )

        IDDict, NameDict = self.DataDicts
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# %s\n#\n" % ( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by ISO_639_3_Languages_Convertor.py %s\n#\n" % ( datetime.now() ) )
            if self.title: myFile.write( "# %s\n" % ( self.title ) )
            #if self.version: myFile.write( "#  Version: %s\n" % ( self.version ) )
            #if self.date: myFile.write( "#  Date: %s\n#\n" % ( self.date ) )
            myFile.write( "#   %i %s loaded from the original XML file.\n#\n\n" % ( len(self.XMLtree), self.treeTag ) )
            exportPythonDict( myFile, IDDict, "ISO639_3_Languages_IDDict", "id", "Name, Type, Scope, Part1Code, Part2Code" )
            exportPythonDict( myFile, NameDict, "ISO639_3_Languages_NameDict", "name", "ID, Type, Scope, Part1Code, Part2Code" )
            myFile.write( "# end of %s" % os.path.basename(filepath) )
    # end of exportDataToPython

    def exportDataToJSON( self, filepath=None ):
        """
        Writes the information tables to a .json file that can be easily loaded into a Java program.

        See http://en.wikipedia.org/wiki/JSON.
        """
        from datetime import datetime
        import json

        assert( self.XMLtree )
        self.importDataToPython()
        assert( self.DataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "__Languages_Tables.json" )
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( filepath ) )
        with open( filepath, 'wt' ) as myFile:
            #myFile.write( "# %s\n#\n" % ( filepath ) ) # Not sure yet if these comment fields are allowed in JSON
            #myFile.write( "# This UTF-8 file was automatically generated by BibleBooksCodes.py on %s\n#\n" % ( datetime.now() ) )
            #if self.titleString: myFile.write( "# %s data\n" % ( self.titleString ) )
            #if self.versionString: myFile.write( "#  Version: %s\n" % ( self.versionString ) )
            #if self.dateString: myFile.write( "#  Date: %s\n#\n" % ( self.dateString ) )
            #myFile.write( "#   %i %s loaded from the original XML file.\n#\n\n" % ( len(self.XMLtree), self.XMLtreeTag ) )
            json.dump( self.DataDicts, myFile, indent=2 )
            #myFile.write( "\n\n# end of %s" % os.path.basename(filepath) )
    # end of exportDataToJSON

    def exportDataToC( self, filepath=None ):
        """
        Writes the information tables to a .h and .c files that can be included in c and c++ programs.

        NOTE: The (optional) filepath should not have the file extension specified -- this is added automatically.
        """
        def exportPythonDict( hFile, cFile, theDict, dictName, sortedBy, structure ):
            """ Exports theDict to the .h and .c files. """
            def convertEntry( entry ):
                """ Convert special characters in an entry... """
                result = ""
                if isinstance( entry, tuple ):
                    for j, field in enumerate(entry):
                        if result: result += ", " # Separate the fields
                        if field is None: result += '""'
                        elif isinstance( field, str):
                            if j>0 and len(field)==1: result += "'" + field + "'" # Catch the character fields
                            else: result += '"' + str(field).replace('"','\\"') + '"' # String fields
                        else: logging.error( "Cannot convert unknown field type '%s' in entry '%s'" % ( field, entry ) )
                else:
                    logging.error( "Can't handle this type of entry yet: %s" % repr(entry) )
                return result
            # end of convertEntry

            for dictKey in theDict.keys(): # Have to iterate this :(
                fieldsCount = len( theDict[dictKey] ) + 1 # Add one since we include the key in the count
                break # We only check the first (random) entry we get

            #hFile.write( "typedef struct %sEntryStruct { %s } %sEntry;\n\n" % ( dictName, structure, dictName ) )
            hFile.write( "typedef struct %sEntryStruct {\n" % dictName )
            for declaration in structure.split(';'):
                adjDeclaration = declaration.strip()
                if adjDeclaration: hFile.write( "    %s;\n" % adjDeclaration )
            hFile.write( "} %sEntry;\n\n" % dictName )

            cFile.write( "const static %sEntry\n %s[%i] = {\n  // Fields (%i) are %s\n  // Sorted by %s\n" % ( dictName, dictName, len(theDict), fieldsCount, structure, sortedBy ) )
            for dictKey in sorted(theDict.keys()):
                if isinstance( dictKey, str ):
                    cFile.write( "  {\"%s\", %s},\n" % ( dictKey, convertEntry(theDict[dictKey]) ) )
                elif isinstance( dictKey, int ):
                    cFile.write( "  {%i, %s},\n" % ( dictKey, convertEntry(theDict[dictKey]) ) )
                else:
                    logging.error( "Can't handle this type of key data yet: %s" % ( dictKey ) )
            cFile.write( "}; // %s (%i entries)\n\n" % ( dictName, len(theDict) ) )
        # end of exportPythonDict

        def XXXexportPythonDict( theFile, theDict, dictName, structName, fieldsComment ):
            """Exports theDict to theFile."""
            def convertEntry( entry ):
                """Convert special characters in an entry..."""
                result = ""
                for field in entry:
                    if result: result += ", " # Separate the fields
                    if field is None: result += '""'
                    elif isinstance( field, str): result += '"' + str(field).replace('"','\\"') + '"'
                    elif isinstance( field, int): result += str(field)
                    else: logging.error( "Cannot convert unknown field type '%s' in entry '%s'" % ( field, entry ) )
                return result

            theFile.write( "static struct %s %s[] = {\n  // Fields are %s\n" % ( structName, dictName, fieldsComment ) )
            for dictKey in sorted(theDict.keys()):
                if isinstance( dictKey, str ):
                    theFile.write( "  {\"%s\", %s},\n" % ( dictKey, convertEntry(theDict[dictKey]) ) )
                elif isinstance( dictKey, int ):
                    theFile.write( "  {%i, %s},\n" % ( dictKey, convertEntry(theDict[dictKey]) ) )
                else:
                    logging.error( "Can't handle this type of data yet: %s" % ( dictKey ) )
            theFile.write( "}; // %s\n\n" % ( dictName) )
        # end of XXXexportPythonDict

        from datetime import datetime

        assert( self.XMLtree )
        self.importDataToPython()
        assert( self.DataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Languages_Tables" )
        hFilepath = filepath + '.h'
        cFilepath = filepath + '.c'
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( cFilepath ) ) # Don't bother telling them about the .h file
        ifdefName = self.filenameBase.upper() + "_Tables_h"

        IDDict, NameDict = self.DataDicts
        with open( hFilepath, 'wt' ) as myHFile, open( cFilepath, 'wt' ) as myCFile:
            myHFile.write( "// %s\n//\n" % ( hFilepath ) )
            myCFile.write( "// %s\n//\n" % ( cFilepath ) )
            lines = "// This UTF-8 file was automatically generated by BibleBooksCodes.py on %s\n//\n" % datetime.now()
            myHFile.write( lines ); myCFile.write( lines )
            myCFile.write( "//   %i %s loaded from the original XML file.\n//\n\n" % ( len(self.XMLtree), self.treeTag ) )
            myHFile.write( "\n#ifndef %s\n#define %s\n\n" % ( ifdefName, ifdefName ) )
            myCFile.write( '#include "%s"\n\n' % os.path.basename(hFilepath) )

            CHAR = "const unsigned char"
            BYTE = "const int"
            dictInfo = {
                "IDDict":("referenceNumber (integer 1..255)",
                    "%s referenceNumber; %s* ByzantineAbbreviation; %s* CCELNumberString; %s* NETBibleAbbreviation; %s* OSISAbbreviation; %s ParatextAbbreviation[3+1]; %s ParatextNumberString[2+1]; %s* SBLAbbreviation; %s* SwordAbbreviation; %s* nameEnglish; %s* numExpectedChapters; %s* possibleAlternativeBooks; %s referenceAbbreviation[3+1];"
                    % (BYTE, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR ) ),
                "referenceAbbreviationDict":("referenceAbbreviation",
                    "%s referenceAbbreviation[3+1]; %s* ByzantineAbbreviation; %s* CCELNumberString; %s referenceNumber; %s* NETBibleAbbreviation; %s* OSISAbbreviation; %s ParatextAbbreviation[3+1]; %s ParatextNumberString[2+1]; %s* SBLAbbreviation; %s* SwordAbbreviation; %s* nameEnglish; %s* numExpectedChapters; %s* possibleAlternativeBooks;"
                    % (CHAR, CHAR, CHAR, BYTE, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR ) ),
                "CCELDict":("CCELNumberString", "%s* CCELNumberString; %s referenceNumber; %s referenceAbbreviation[3+1];" % (CHAR,BYTE,CHAR) ),
                "SBLDict":("SBLAbbreviation", "%s* SBLAbbreviation; %s referenceNumber; %s referenceAbbreviation[3+1];" % (CHAR,BYTE,CHAR) ),
                "OSISAbbreviationDict":("OSISAbbreviation", "%s* OSISAbbreviation; %s referenceNumber; %s referenceAbbreviation[3+1];" % (CHAR,BYTE,CHAR) ),
                "SwordAbbreviationDict":("SwordAbbreviation", "%s* SwordAbbreviation; %s referenceNumber; %s referenceAbbreviation[3+1];" % (CHAR,BYTE,CHAR) ),
                "ParatextAbbreviationDict":("ParatextAbbreviation", "%s ParatextAbbreviation[3+1]; %s referenceNumber; %s referenceAbbreviation[3+1]; %s ParatextNumberString[2+1];" % (CHAR,BYTE,CHAR,CHAR) ),
                "ParatextNumberDict":("ParatextNumberString", "%s ParatextNumberString[2+1]; %s referenceNumber; %s referenceAbbreviation[3+1]; %s ParatextAbbreviation[3+1];" % (CHAR,BYTE,CHAR,CHAR) ),
                "NETBibleAbbreviationDict":("NETBibleAbbreviation", "%s* NETBibleAbbreviation; %s referenceNumber; %s referenceAbbreviation[3+1];" % (CHAR,BYTE,CHAR) ),
                "ByzantineAbbreviationDict":("ByzantineAbbreviation", "%s* ByzantineAbbreviation; %s referenceNumber; %s referenceAbbreviation[3+1];" % (CHAR,BYTE,CHAR) ),
                "EnglishNameDict":("nameEnglish", "%s* nameEnglish; %s referenceNumber; %s referenceAbbreviation[3+1];" % (CHAR,BYTE,CHAR) ) }

            #for dictName,dictData in self.DataDicts.items():
            #    exportPythonDict( myHFile, myCFile, dictData, dictName, dictInfo[dictName][0], dictInfo[dictName][1] )
            exportPythonDict( myHFile, myCFile, IDDict, "IDDict", "3-character lower-case ID field", "%s* ID; %s* Name; %s Type; %s Scope; %s* Part1Code; %s* Part2Code;" % (CHAR,CHAR,CHAR,CHAR,CHAR,CHAR) )
            exportPythonDict( myHFile, myCFile, NameDict, "NameDict", "language name (alphabetical)", "%s* Name; %s* ID; %s Type; %s Scope; %s* Part1Code; %s* Part2Code;" % (CHAR,CHAR,CHAR,CHAR,CHAR,CHAR)  )

            myHFile.write( "#endif // %s\n\n" % ( ifdefName ) )
            myHFile.write( "// end of %s" % os.path.basename(hFilepath) )
            myCFile.write( "// end of %s" % os.path.basename(cFilepath) )



        return
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "// %s\n//\n" % ( filepath ) )
            myFile.write( "// This UTF-8 file was automatically generated by ISO_639_3_Languages.py %s\n//\n" % ( datetime.now() ) )
            if self.title: myFile.write( "// %s\n" % ( self.title ) )
            #if self.version: myFile.write( "//  Version: %s\n" % ( self.version ) )
            #if self.date: myFile.write( "//  Date: %s\n//\n" % ( self.date ) )
            myFile.write( "//   %i %s loaded from the original XML file.\n//\n\n" % ( len(self.XMLtree), self.treeTag ) )
            myFile.write( "#ifndef %s\n#define %s\n\n" % ( ifdefName, ifdefName ) )
            exportPythonDict( myFile, IDDict, "ISO639_3_Languages_IDDict", "{char* ID; char* Name; char* Type; char* Scope; char* Part1Code; char* Part2Code;}", "ID (sorted), Name, Type, Scope, Part1Code, Part2Code" )
            exportPythonDict( myFile, NameDict, "ISO639_3_Languages_NameDict", "{char* Name; char* ID; char* Type; char* Scope; char* Part1Code; char* Part2Code;}", "Name (sorted), ID, Type, Scope, Part1Code, Part2Code" )
            myFile.write( "#endif // %s\n" % ( ifdefName ) )
    # end of exportDataToC
# end of _ISO_639_3_Languages_Convertor class


@singleton # Can only ever have one instance
class ISO_639_3_Languages:
    """
    Class for handling ISO_639_3_Languages.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.

    Note: BBB is used in this class to represent the three-character referenceAbbreviation.
    """

    def __init__( self ): # We can't give this parameters because of the singleton
        """
        Constructor: 
        """
        self.lgC = _ISO_639_3_Languages_Convertor()
        self.DataDicts = None # We'll import into this in loadData
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "ISO_639_3_Languages object"
        assert( len(self.DataDicts[0]) == len(self.DataDicts[0]) )
        result += ('\n' if result else '') + "  Num entries = %i" % ( len(self.DataDicts[0]) )
        return result
    # end of __str__

    def loadData( self, XMLFilepath=None ):
        """ Loads the XML data file and imports it to dictionary format (if not done already). """
        if not self.DataDicts: # Don't do this unnecessarily
            if XMLFilepath is not None: logging.warning( "ISO 639-3 language codes are already loaded -- your given filepath of '%s' was ignored" % XMLFilepath )
            self.lgC.loadAndValidate( XMLFilepath ) # Load the XML (if not done already)
            self.DataDicts = self.lgC.importDataToPython() # Get the various dictionaries organised for quick lookup
            del self.lgC # Now the convertor class (that handles the XML) is no longer needed
        return self
    # end of loadData

    # TODO: Add more useful routines in here

    def isValidLanguageCode( self, ccc ):
        """ Returns True or False. """
        return ccc in self.DataDicts[0]

    def getLanguageName( self, ccc ):
        """ Return the language name for the given language code. """
        if ccc in self.DataDicts[0]: # Look in the ID dict
            return self.DataDicts[0][ccc][0] # The first field is the name
# end of ISO_639_3_Languages class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v%s" % ( versionString ) )
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML file to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 0: print( "%s V%s" % ( progName, versionString ) )

    if Globals.commandLineOptions.export:
        lgC = _ISO_639_3_Languages_Convertor().loadAndValidate() # Load the XML
        lgC.exportDataToPython() # Produce the .py tables
        lgC.exportDataToJSON() # Produce a json output file
        lgC.exportDataToC() # Produce the .h and .c tables

    else: # Must be demo mode
        # Demo the convertor object
        lgC = _ISO_639_3_Languages_Convertor().loadAndValidate() # Load the XML
        print( lgC ) # Just print a summary

        # Demo the languages object
        lg = ISO_639_3_Languages().loadData() # Doesn't reload the XML unnecessarily :)
        print( lg ) # Just print a summary
        print( "qwq valid?", lg.isValidLanguageCode("qwq") )
        print( "qwq name:", lg.getLanguageName("qwq") )
        print( "mbt valid?", lg.isValidLanguageCode("mbt") )
        print( "mbt name:", lg.getLanguageName("mbt") )
# end of main

if __name__ == '__main__':
    main()
# end of ISO_639_3_Languages.py
