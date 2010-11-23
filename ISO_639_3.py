#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ISO_639_3.py
#
# Module handling ISO_639_3.xml to produce C and Python data tables
#   Last modified: 2010-11-23 (also update versionString below)
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
Module handling ISO_639_3.xml to produce C and Python data tables.
"""

progName = "ISO 639_3 handler"
versionString = "0.90"

import logging, os.path
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree


class ISO_639_3_Convertor:
    """
    Class for handling and converting ISO 639-3 language codes.
    """
    filenameBase = "iso_639_3"
    treeTag = "iso_639_3_entries"
    mainElementTag = "iso_639_3_entry"
    compulsoryAttributes = ( "id", "name", "type", "scope" )
    optionalAttributes = ( "part1_code", "part2_code" )
    uniqueAttributes = ( "id", "name", "part1_code", "part2_code" )
    compulsoryElements = ()
    optionalElements = ()
    uniqueElements = compulsoryElements + optionalElements

    def __init__( self, XMLFilepath=None ):
        """
        Constructor: expects the filepath of the source XML file.
        Loads (and crudely validates the XML file) into an element tree.
        """
        if XMLFilepath is None:
            XMLFilepath = os.path.join( "DataFiles", ISO_639_3_Convertor.filenameBase + ".xml" )
        self.title = "ISO 639-3 language codes"
        self.tree = None
        self.load( XMLFilepath )
        self.validate()
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = ""
        if self.title: result += ('\n' if result else '') + self.title
        result += ('\n' if result else '') + "Num entries = " + str(len(self.tree))
        return result
    # end of __str__

    def load( self, XMLFilepath ):
        """
        Load the source XML file and remove the header from the tree.
        Also, extracts some useful Attributes from the header element.
        """
        self.tree = ElementTree().parse ( XMLFilepath )
        assert( len ( self.tree ) ) # Fail here if we didn't load anything at all

        if self.tree.tag  != ISO_639_3_Convertor.treeTag:
            logging.error( "Expected to load '%s' but got '%s'" % ( ISO_639_3_Convertor.treeTag, self.tree.tag ) )
    # end of load

    def validate( self ):
        """
        Check/validate the loaded data.
        """
        assert( len ( self.tree ) )

        uniqueDict = {}
        for attributeName in ISO_639_3_Convertor.uniqueAttributes: uniqueDict[attributeName] = []

        for j,element in enumerate(self.tree):
            if element.tag == ISO_639_3_Convertor.mainElementTag:
                # Check compulsory attributes on this main element
                for attributeName in ISO_639_3_Convertor.compulsoryAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is None:
                        logging.error( "Compulsory '%s' attribute is missing from %s element in record %i" % ( attributeName, element.tag, j ) )
                    if not attributeValue:
                        logging.warning( "Compulsory '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, j ) )

                # Check optional attributes on this main element
                for attributeName in ISO_639_3_Convertor.optionalAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if not attributeValue:
                            logging.warning( "Optional '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, j ) )

                # Check for unexpected additional attributes on this main element
                for attributeName in element.keys():
                    attributeValue = element.get( attributeName )
                    if attributeName not in ISO_639_3_Convertor.compulsoryAttributes and attributeName not in ISO_639_3_Convertor.optionalAttributes:
                        logging.warning( "Additional '%s' attribute ('%s') found on %s element in record %i" % ( attributeName, attributeValue, element.tag, j ) )

                # Check the attributes that must contain unique information (in that particular field -- doesn't check across different attributes)
                for attributeName in ISO_639_3_Convertor.uniqueAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if attributeValue in uniqueDict[attributeName]:
                            logging.error( "Found '%s' data repeated in '%s' field on %s element in record %i" % ( attributeValue, attributeName, element.tag, j ) )
                        uniqueDict[attributeName].append( attributeValue )
            else:
                logging.warning( "Unexpected element: %s in record %i" % ( element.tag, j ) )
    # end of validate

    def importDataToPython( self ):
        """
        Loads (and pivots) the data into suitable Python containers to use in a Python program.
        (Of course, you can just use the elementTree in self.tree if you prefer.)
        """
        assert( len ( self.tree ) )

        # We'll create a number of dictionaries with different Attributes as the key
        myIDDict, myNameDict = OrderedDict(), OrderedDict()
        for element in self.tree:
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
            if "id" in ISO_639_3_Convertor.compulsoryAttributes or ID:
                if "id" in ISO_639_3_Convertor.uniqueElements: assert( ID not in myIDDict ) # Shouldn't be any duplicates
                myIDDict[ID] = ( Name, Type, Scope, Part1Code, Part2Code, )
            if "name" in ISO_639_3_Convertor.compulsoryAttributes or Name:
                if "name" in ISO_639_3_Convertor.uniqueElements: assert( Name not in myNameDict ) # Shouldn't be any duplicates
                myNameDict[Name] = ( ID, Type, Scope, Part1Code, Part2Code, )
        return myIDDict, myNameDict # Just throw away any of the dictionaries that you don't need
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

        assert( len ( self.tree ) )
        if not filepath: filepath = os.path.join( "DerivedFiles", ISO_639_3_Convertor.filenameBase + "_Tables.py" )
        print( "Exporting to %s..." % ( filepath ) )

        IDDict, NameDict = self.importDataToPython()
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# %s\n#\n" % ( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by ISO_639_3_Convertor.py %s\n#\n" % ( datetime.now() ) )
            if self.title: myFile.write( "# %s\n" % ( self.title ) )
            #if self.version: myFile.write( "#  Version: %s\n" % ( self.version ) )
            #if self.date: myFile.write( "#  Date: %s\n#\n" % ( self.date ) )
            myFile.write( "#   %i %s loaded from the original XML file.\n#\n\n" % ( len(self.tree), ISO_639_3_Convertor.treeTag ) )
            exportPythonDict( myFile, IDDict, "ISO639_3_IDDict", "id", "Name, Type, Scope, Part1Code, Part2Code" )
            exportPythonDict( myFile, NameDict, "ISO639_3_NameDict", "name", "ID, Type, Scope, Part1Code, Part2Code" )
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
        # end of exportPythonDict

        from datetime import datetime

        assert( len ( self.tree ) )
        if not filepath: filepath = os.path.join( "DerivedFiles", ISO_639_3_Convertor.filenameBase + "_Tables.h" )
        print( "Exporting to %s..." % ( filepath ) )

        IDDict, NameDict = self.importDataToPython()
        ifdefName = ISO_639_3_Convertor.filenameBase.upper() + "_h"
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "// %s\n//\n" % ( filepath ) )
            myFile.write( "// This UTF-8 file was automatically generated by ISO_639_3.py %s\n//\n" % ( datetime.now() ) )
            if self.title: myFile.write( "// %s\n" % ( self.title ) )
            #if self.version: myFile.write( "//  Version: %s\n" % ( self.version ) )
            #if self.date: myFile.write( "//  Date: %s\n//\n" % ( self.date ) )
            myFile.write( "//   %i %s loaded from the original XML file.\n//\n\n" % ( len(self.tree), ISO_639_3_Convertor.treeTag ) )
            myFile.write( "#ifndef %s\n#define %s\n\n" % ( ifdefName, ifdefName ) )
            exportPythonDict( myFile, IDDict, "ISO639_3_IDDict", "{char* ID; char* Name; char* Type; char* Scope; char* Part1Code; char* Part2Code;}", "ID (sorted), Name, Type, Scope, Part1Code, Part2Code" )
            exportPythonDict( myFile, NameDict, "ISO639_3_NameDict", "{char* Name; char* ID; char* Type; char* Scope; char* Part1Code; char* Part2Code;}", "Name (sorted), ID, Type, Scope, Part1Code, Part2Code" )
            myFile.write( "#endif // %s\n" % ( ifdefName ) )
    # end of exportDataToC
# end of ISO_639_3_Convertor class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v%s" % ( versionString ) )
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML file to .py and .h tables suitable for directly including into other programs")
    CommandLineOptions, args = parser.parse_args()

    stuff = ISO_639_3_Convertor() # Load the XML
    if CommandLineOptions.export:
        stuff.exportDataToPython() # Produce the .py tables
        stuff.exportDataToC() # Produce the .h tables
    else: # Must be demo mode
        print( "%s V%s" % ( progName, versionString ) )
        print( stuff ) # Just print a summary
# end of main

if __name__ == '__main__':
    main()
# end of ISO_639_3.py
