#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ISO_639_3_Languages.py
#
# Module handling ISO_639_3.xml to produce C and Python data tables
#   Last modified: 2011-01-17 (also update versionString below)
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
Module handling ISO_639_3_Languages.xml to produce C and Python data tables.
"""

progName = "ISO 639_3_Languages handler"
versionString = "0.92"

import logging, os.path
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree

from singleton import singleton
import Globals


@singleton # Can only ever have one instance
class _ISO_639_3_Languages_Converter:
    """
    Class for handling and converting ISO 639-3 language codes.
    """

    def __init__( self ):
        """
        Constructor: expects the filepath of the source XML file.
        Loads (and crudely validates the XML file) into an element tree.
        """
        self._filenameBase = "iso_639_3"

        # These fields are used for parsing the XML
        self._treeTag = "iso_639_3_entries"
        self._mainElementTag = "iso_639_3_entry"

        # These fields are used for automatically checking/validating the XML
        self._compulsoryAttributes = ( "id", "name", "type", "scope", )
        self._optionalAttributes = ( "part1_code", "part2_code", )
        self._uniqueAttributes = ( "id", "name", "part1_code", "part2_code", )
        self._compulsoryElements = ()
        self._optionalElements = ()
        self._uniqueElements = self._compulsoryElements + self._optionalElements

        self.title = "ISO 639-3 language codes"

        # These are fields that we will fill later
        self._XMLtree, self._DataDicts = None, None
    # end of __init__

    def loadAndValidate( self, XMLFilepath=None ):
        """
        Loads (and crudely validates the XML file) into an element tree.
            Allows the filepath of the source XML file to be specified, otherwise uses the default.
        """
        if self._XMLtree is None: # We mustn't have already have loaded the data
            if XMLFilepath is None:
                XMLFilepath = os.path.join( "DataFiles", self._filenameBase + ".xml" )

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
        assert( self._XMLtree is None or len(self._XMLtree)==0 ) # Make sure we're not doing this twice

        if Globals.verbosityLevel > 2: print( "Loading ISO 639-3 languages XML file from '{}'...".format( XMLFilepath ) )
        self._XMLtree = ElementTree().parse( XMLFilepath )
        assert( self._XMLtree ) # Fail here if we didn't load anything at all

        if self._XMLtree.tag  != self._treeTag:
            logging.error( "Expected to load '{}' but got '{}'".format( self._treeTag, self._XMLtree.tag ) )
    # end of _load

    def _validate( self ):
        """
        Check/validate the loaded data.
        """
        assert( self._XMLtree )

        uniqueDict = {}
        #for elementName in self._uniqueElements: uniqueDict["Element_"+elementName] = []
        for attributeName in self._uniqueAttributes: uniqueDict["Attribute_"+attributeName] = []

        for j,element in enumerate(self._XMLtree):
            if element.tag == self._mainElementTag:
                # Check compulsory attributes on this main element
                for attributeName in self._compulsoryAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is None:
                        logging.error( "Compulsory '{}' attribute is missing from {} element in record {}".format( attributeName, element.tag, j ) )
                    if not attributeValue:
                        logging.warning( "Compulsory '{}' attribute is blank on {} element in record {}".format( attributeName, element.tag, j ) )

                # Check optional attributes on this main element
                for attributeName in self._optionalAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if not attributeValue:
                            logging.warning( "Optional '{}' attribute is blank on {} element in record {}".format( attributeName, element.tag, j ) )

                # Check for unexpected additional attributes on this main element
                for attributeName in element.keys():
                    attributeValue = element.get( attributeName )
                    if attributeName not in self._compulsoryAttributes and attributeName not in self._optionalAttributes:
                        logging.warning( "Additional '{}' attribute ('{}') found on {} element in record {}".format( attributeName, attributeValue, element.tag, j ) )

                # Check the attributes that must contain unique information (in that particular field -- doesn't check across different attributes)
                for attributeName in self._uniqueAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if attributeValue in uniqueDict["Attribute_"+attributeName]:
                            logging.error( "Found '{}' data repeated in '{}' field on {} element in record {}".format( attributeValue, attributeName, element.tag, j ) )
                        uniqueDict["Attribute_"+attributeName].append( attributeValue )
            else:
                logging.warning( "Unexpected element: {} in record {}".format( element.tag, j ) )
    # end of _validate

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "_ISO_639_3_Languages_Converter object"
        if self.title: result += ('\n' if result else '') + self.title
        result += ('\n' if result else '') + "  Num entries = " + str(len(self._XMLtree))
        return result
    # end of __str__

    def importDataToPython( self ):
        """
        Loads (and pivots) the data into suitable Python containers to use in a Python program.
        (Of course, you can just use the elementTree in self._XMLtree if you prefer.)
        """
        assert( self._XMLtree )
        if self._DataDicts: # We've already done an import/restructuring -- no need to repeat it
            return self._DataDicts

        # We'll create a number of dictionaries with different Attributes as the key
        myIDDict, myNameDict = OrderedDict(), OrderedDict()
        for element in self._XMLtree:
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
            if "id" in self._compulsoryAttributes or ID:
                if "id" in self._uniqueElements: assert( ID not in myIDDict ) # Shouldn't be any duplicates
                myIDDict[ID] = ( Name, Type, Scope, Part1Code, Part2Code, )
            if "name" in self._compulsoryAttributes or Name:
                if "name" in self._uniqueElements: assert( Name not in myNameDict ) # Shouldn't be any duplicates
                myNameDict[Name] = ( ID, Type, Scope, Part1Code, Part2Code, )
            self._DataDicts = myIDDict, myNameDict
        return self._DataDicts # Just throw away any of the dictionaries that you don't need
    # end of importDataToPython

    def exportDataToPython( self, filepath=None ):
        """
        Writes the information tables to a .py file that can be cut and pasted into a Python program.
        """
        def exportPythonDict( theFile, theDict, dictName, keyComment, fieldsComment ):
            """Exports theDict to theFile."""
            theFile.write( "{} = {{\n  # Key is {}\n  # Fields are: {}\n".format( dictName, keyComment, fieldsComment ) )
            for dictKey in sorted(theDict.keys()):
                theFile.write( "  {}: {},\n".format( repr(dictKey), theDict[dictKey] ) )
            theFile.write( "}}\n# end of {}\n\n".format( dictName ) )
        # end of exportPythonDict

        from datetime import datetime

        assert( self._XMLtree )
        self.importDataToPython()
        assert( self._DataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self._filenameBase + "_Languages_Tables.py" )
        if Globals.verbosityLevel > 1: print( "Exporting to {}...".format( filepath ) )

        IDDict, NameDict = self._DataDicts
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# {}\n#\n".format( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by ISO_639_3_Languages_Converter.py V{} on {}\n#\n".format( versionString, datetime.now() ) )
            if self.title: myFile.write( "# {}\n".format( self.title ) )
            #if self.version: myFile.write( "#  Version: {}\n".format( self.version ) )
            #if self.date: myFile.write( "#  Date: {}\n#\n".format( self.date ) )
            myFile.write( "#   {} {} loaded from the original XML file.\n#\n\n".format( len(self._XMLtree), self._treeTag ) )
            exportPythonDict( myFile, IDDict, "ISO639_3_Languages_IDDict", "id", "Name, Type, Scope, Part1Code, Part2Code" )
            exportPythonDict( myFile, NameDict, "ISO639_3_Languages_NameDict", "name", "ID, Type, Scope, Part1Code, Part2Code" )
            myFile.write( "# end of {}".format( os.path.basename(filepath) ) )
    # end of exportDataToPython

    def exportDataToJSON( self, filepath=None ):
        """
        Writes the information tables to a .json file that can be easily loaded into a Java program.

        See http://en.wikipedia.org/wiki/JSON.
        """
        from datetime import datetime
        import json

        assert( self._XMLtree )
        self.importDataToPython()
        assert( self._DataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self._filenameBase + "__Languages_Tables.json" )
        if Globals.verbosityLevel > 1: print( "Exporting to {}...".format( filepath ) )
        with open( filepath, 'wt' ) as myFile:
            #myFile.write( "# {}\n#\n".format( filepath ) ) # Not sure yet if these comment fields are allowed in JSON
            #myFile.write( "# This UTF-8 file was automatically generated by BibleBooksCodes.py V{} on {}\n#\n".format( versionString, datetime.now() ) )
            #if self.titleString: myFile.write( "# {} data\n".format( self.titleString ) )
            #if self.versionString: myFile.write( "#  Version: {}\n".format( self.versionString ) )
            #if self.dateString: myFile.write( "#  Date: {}\n#\n".format( self.dateString ) )
            #myFile.write( "#   {} {} loaded from the original XML file.\n#\n\n".format( len(self._XMLtree), self._XMLtreeTag ) )
            json.dump( self._DataDicts, myFile, indent=2 )
            #myFile.write( "\n\n# end of {}".format( os.path.basename(filepath) ) )
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
                        else: logging.error( "Cannot convert unknown field type '{}' in entry '{}'".format( field, entry ) )
                else:
                    logging.error( "Can't handle this type of entry yet: {}".format( repr(entry) ) )
                return result
            # end of convertEntry

            for dictKey in theDict.keys(): # Have to iterate this :(
                fieldsCount = len( theDict[dictKey] ) + 1 # Add one since we include the key in the count
                break # We only check the first (random) entry we get

            #hFile.write( "typedef struct {}EntryStruct { {} } {}Entry;\n\n".format( dictName, structure, dictName ) )
            hFile.write( "typedef struct {}EntryStruct {{\n".format( dictName ) )
            for declaration in structure.split(';'):
                adjDeclaration = declaration.strip()
                if adjDeclaration: hFile.write( "    {};\n".format( adjDeclaration ) )
            hFile.write( "}} {}Entry;\n\n".format( dictName ) )

            cFile.write( "const static {}Entry\n {}[{}] = {{\n  // Fields ({}) are {}\n  // Sorted by {}\n".format( dictName, dictName, len(theDict), fieldsCount, structure, sortedBy ) )
            for dictKey in sorted(theDict.keys()):
                if isinstance( dictKey, str ):
                    cFile.write( "  {{\"{}\", {}}},\n".format( dictKey, convertEntry(theDict[dictKey]) ) )
                elif isinstance( dictKey, int ):
                    cFile.write( "  {{{}, {}}},\n".format( dictKey, convertEntry(theDict[dictKey]) ) )
                else:
                    logging.error( "Can't handle this type of key data yet: {}".format( dictKey ) )
            cFile.write( "}}; // {} ({} entries)\n\n".format( dictName, len(theDict) ) )
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
                    else: logging.error( "Cannot convert unknown field type '{}' in entry '{}'".format( field, entry ) )
                return result

            theFile.write( "static struct {} {}[] = {{\n  // Fields are {}\n".format( structName, dictName, fieldsComment ) )
            for dictKey in sorted(theDict.keys()):
                if isinstance( dictKey, str ):
                    theFile.write( "  {\"{}\", {}},\n".format( dictKey, convertEntry(theDict[dictKey]) ) )
                elif isinstance( dictKey, int ):
                    theFile.write( "  {{{}, {}}},\n".format( dictKey, convertEntry(theDict[dictKey]) ) )
                else:
                    logging.error( "Can't handle this type of data yet: {}".format( dictKey ) )
            theFile.write( "}}; // {}\n\n".format( dictName) )
        # end of XXXexportPythonDict

        from datetime import datetime

        assert( self._XMLtree )
        self.importDataToPython()
        assert( self._DataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self._filenameBase + "_Languages_Tables" )
        hFilepath = filepath + '.h'
        cFilepath = filepath + '.c'
        if Globals.verbosityLevel > 1: print( "Exporting to {}...".format( cFilepath ) ) # Don't bother telling them about the .h file
        ifdefName = self._filenameBase.upper() + "_Tables_h"

        IDDict, NameDict = self._DataDicts
        with open( hFilepath, 'wt' ) as myHFile, open( cFilepath, 'wt' ) as myCFile:
            myHFile.write( "// {}\n//\n".format( hFilepath ) )
            myCFile.write( "// {}\n//\n".format( cFilepath ) )
            lines = "// This UTF-8 file was automatically generated by BibleBooksCodes.py V{} on {}\n//\n".format( versionString, datetime.now() )
            myHFile.write( lines ); myCFile.write( lines )
            myCFile.write( "//   {} {} loaded from the original XML file.\n//\n\n".format( len(self._XMLtree), self._treeTag ) )
            myHFile.write( "\n#ifndef {}\n#define {}\n\n".format( ifdefName, ifdefName ) )
            myCFile.write( '#include "{}"\n\n'.format( os.path.basename(hFilepath) ) )

            CHAR = "const unsigned char"
            BYTE = "const int"
            dictInfo = {
                "IDDict":("referenceNumber (integer 1..255)",
                    "{} referenceNumber; {}* ByzantineAbbreviation; {}* CCELNumberString; {}* NETBibleAbbreviation; {}* OSISAbbreviation; {} ParatextAbbreviation[3+1]; {} ParatextNumberString[2+1]; {}* SBLAbbreviation; {}* SwordAbbreviation; {}* nameEnglish; {}* numExpectedChapters; {}* possibleAlternativeBooks; {} referenceAbbreviation[3+1];"
                   .format(BYTE, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR ) ),
                "referenceAbbreviationDict":("referenceAbbreviation",
                    "{} referenceAbbreviation[3+1]; {}* ByzantineAbbreviation; {}* CCELNumberString; {} referenceNumber; {}* NETBibleAbbreviation; {}* OSISAbbreviation; {} ParatextAbbreviation[3+1]; {} ParatextNumberString[2+1]; {}* SBLAbbreviation; {}* SwordAbbreviation; {}* nameEnglish; {}* numExpectedChapters; {}* possibleAlternativeBooks;"
                   .format(CHAR, CHAR, CHAR, BYTE, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR, CHAR ) ),
                "CCELDict":("CCELNumberString", "{}* CCELNumberString; {} referenceNumber; {} referenceAbbreviation[3+1];".format(CHAR,BYTE,CHAR) ),
                "SBLDict":("SBLAbbreviation", "{}* SBLAbbreviation; {} referenceNumber; {} referenceAbbreviation[3+1];".format(CHAR,BYTE,CHAR) ),
                "OSISAbbreviationDict":("OSISAbbreviation", "{}* OSISAbbreviation; {} referenceNumber; {} referenceAbbreviation[3+1];".format(CHAR,BYTE,CHAR) ),
                "SwordAbbreviationDict":("SwordAbbreviation", "{}* SwordAbbreviation; {} referenceNumber; {} referenceAbbreviation[3+1];".format(CHAR,BYTE,CHAR) ),
                "ParatextAbbreviationDict":("ParatextAbbreviation", "{} ParatextAbbreviation[3+1]; {} referenceNumber; {} referenceAbbreviation[3+1]; {} ParatextNumberString[2+1];".format(CHAR,BYTE,CHAR,CHAR) ),
                "ParatextNumberDict":("ParatextNumberString", "{} ParatextNumberString[2+1]; {} referenceNumber; {} referenceAbbreviation[3+1]; {} ParatextAbbreviation[3+1];".format(CHAR,BYTE,CHAR,CHAR) ),
                "NETBibleAbbreviationDict":("NETBibleAbbreviation", "{}* NETBibleAbbreviation; {} referenceNumber; {} referenceAbbreviation[3+1];".format(CHAR,BYTE,CHAR) ),
                "ByzantineAbbreviationDict":("ByzantineAbbreviation", "{}* ByzantineAbbreviation; {} referenceNumber; {} referenceAbbreviation[3+1];".format(CHAR,BYTE,CHAR) ),
                "EnglishNameDict":("nameEnglish", "{}* nameEnglish; {} referenceNumber; {} referenceAbbreviation[3+1];".format(CHAR,BYTE,CHAR) ) }

            #for dictName,dictData in self._DataDicts.items():
            #    exportPythonDict( myHFile, myCFile, dictData, dictName, dictInfo[dictName][0], dictInfo[dictName][1] )
            exportPythonDict( myHFile, myCFile, IDDict, "IDDict", "3-character lower-case ID field", "{}* ID; {}* Name; {} Type; {} Scope; {}* Part1Code; {}* Part2Code;".format(CHAR,CHAR,CHAR,CHAR,CHAR,CHAR) )
            exportPythonDict( myHFile, myCFile, NameDict, "NameDict", "language name (alphabetical)", "{}* Name; {}* ID; {} Type; {} Scope; {}* Part1Code; {}* Part2Code;".format(CHAR,CHAR,CHAR,CHAR,CHAR,CHAR)  )

            myHFile.write( "#endif // {}\n\n".format( ifdefName ) )
            myHFile.write( "// end of {}".format( os.path.basename(hFilepath) ) )
            myCFile.write( "// end of {}".format( os.path.basename(cFilepath) ) )



        return
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "// {}\n//\n".format( filepath ) )
            myFile.write( "// This UTF-8 file was automatically generated by ISO_639_3_Languages.py V{} on {}\n//\n".format( versionString, datetime.now() ) )
            if self.title: myFile.write( "// {}\n".format( self.title ) )
            #if self.version: myFile.write( "//  Version: {}\n".format( self.version ) )
            #if self.date: myFile.write( "//  Date: {}\n//\n".format( self.date ) )
            myFile.write( "//   {} {} loaded from the original XML file.\n//\n\n".format( len(self._XMLtree), self._treeTag ) )
            myFile.write( "#ifndef {}\n#define {}\n\n".format( ifdefName, ifdefName ) )
            exportPythonDict( myFile, IDDict, "ISO639_3_Languages_IDDict", "{char* ID; char* Name; char* Type; char* Scope; char* Part1Code; char* Part2Code;}", "ID (sorted), Name, Type, Scope, Part1Code, Part2Code" )
            exportPythonDict( myFile, NameDict, "ISO639_3_Languages_NameDict", "{char* Name; char* ID; char* Type; char* Scope; char* Part1Code; char* Part2Code;}", "Name (sorted), ID, Type, Scope, Part1Code, Part2Code" )
            myFile.write( "#endif // {}\n".format( ifdefName ) )
    # end of exportDataToC
# end of _ISO_639_3_Languages_Converter class


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
        self.lgC = _ISO_639_3_Languages_Converter()
        self._IDDict = self._NameDict = None # We'll import into this in loadData
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "ISO_639_3_Languages object"
        assert( len(self._IDDict) == len(self._NameDict) )
        result += ('\n' if result else '') + "  Num entries = {}".format( len(self._IDDict) )
        return result
    # end of __str__

    def loadData( self, XMLFilepath=None ):
        """ Loads the XML data file and imports it to dictionary format (if not done already). """
        if not self._IDDict and not self._NameDict: # Don't do this unnecessarily
            if XMLFilepath is not None: logging.warning( "ISO 639-3 language codes are already loaded -- your given filepath of '{}' was ignored".format( XMLFilepath ) )
            self.lgC.loadAndValidate( XMLFilepath ) # Load the XML (if not done already)
            self._IDDict, self._NameDict = self.lgC.importDataToPython() # Get the various dictionaries organised for quick lookup
            del self.lgC # Now the converter class (that handles the XML) is no longer needed
        return self
    # end of loadData

    # TODO: Add more useful routines in here

    def isValidLanguageCode( self, ccc ):
        """ Returns True or False. """
        return ccc in self._IDDict

    def getLanguageName( self, ccc ):
        """ Return the language name for the given language code. """
        if ccc in self._IDDict: # Look in the ID dict
            return self._IDDict[ccc][0] # The first field is the name
# end of ISO_639_3_Languages class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v{}".format( versionString ) )
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML file to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 1: print( "{} V{}".format( progName, versionString ) )

    if Globals.commandLineOptions.export:
        lgC = _ISO_639_3_Languages_Converter().loadAndValidate() # Load the XML
        lgC.exportDataToPython() # Produce the .py tables
        lgC.exportDataToJSON() # Produce a json output file
        lgC.exportDataToC() # Produce the .h and .c tables

    else: # Must be demo mode
        # Demo the converter object
        lgC = _ISO_639_3_Languages_Converter().loadAndValidate() # Load the XML
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
