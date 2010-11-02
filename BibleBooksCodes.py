#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleBooksCodesConvertor.py
#
# Module handling BibleBooksCodes.xml to produce C and Python data tables
#   Last modified: 2010-10-14 (also update versionString below)
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
Module handling BibleBooksCodes.xml to produce C and Python data tables.
"""

versionString = "0.90"

import logging, os.path
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree


class BibleBooksCodesConvertor:
    """
    Class for handling and converting BibleBooksCodes.
    """
    filenameBase = "BibleBooksCodes"
    treeTag = "BibleBooksCodes"
    headerTag = "header"
    mainElementTag = "BibleBookCodes"
    compulsoryAttributes = ()
    optionalAttributes = ()
    uniqueAttributes = compulsoryAttributes + optionalAttributes
    compulsoryElements = ( "id", "nameEnglish", "referenceAbbreviation" )
    optionalElements = ( "SBLAbbreviation", "OSISAbbreviation", "ParatextAbbreviation", "ParatextNumber", "NETBibleAbbreviation", "swordAbbreviation" )
    #uniqueElements = compulsoryElements + optionalElements
    uniqueElements = compulsoryElements # Relax the checking

    def __init__( self, XMLFilepath=None ):
        """
        Constructor: expects the filepath of the source XML file.
        Loads (and crudely validates the XML file) into an element tree.
        """
        if XMLFilepath is None:
            XMLFilepath = os.path.join( "DataFiles", BibleBooksCodesConvertor.filenameBase + ".xml" )
        self.title, self.version, self.date = None, None, None
        self.header, self.tree = None, None
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
        if self.version: result += ('\n' if result else '') + "Version: " + self.version
        if self.date: result += ('\n' if result else '') + "Date: " + self.date
        result += ('\n' if result else '') + "Num entries = " + str(len(self.tree))
        return result
    # end of __str__

    def load( self, XMLFilepath ):
        """
        Load the source XML file and remove the header from the tree.
        Also, extracts some useful elements from the header element.
        """
        self.tree = ElementTree().parse ( XMLFilepath )
        assert( len ( self.tree ) ) # Fail here if we didn't load anything at all

        if self.tree.tag  == BibleBooksCodesConvertor.treeTag:
            header = self.tree[0]
            if header.tag == BibleBooksCodesConvertor.headerTag:
                self.header = header
                self.tree.remove( header )
                if len(header)>1:
                    logging.info( "Unexpected elements in header" )
                elif len(header)==0:
                    logging.info( "Missing work element in header" )
                else:
                    work = header[0]
                    if work.tag == "work":
                        self.version = work.find("version").text
                        self.date = work.find("date").text
                        self.title = work.find("title").text
                    else:
                        logging.warning( "Missing work element in header" )
            else:
                logging.warning( "Missing header element (looking for '%s' tag)" % ( BibleBooksCodesConvertor.headerTag ) )
        else:
            logging.error( "Expected to load '%s' but got '%s'" % ( BibleBooksCodesConvertor.treeTag, self.tree.tag ) )
    # end of load

    def validate( self ):
        """
        Check/validate the loaded data.
        """
        assert( len ( self.tree ) )

        uniqueDict = {}
        for elementName in BibleBooksCodesConvertor.uniqueElements: uniqueDict[elementName] = []

        expectedID = 1
        for j,element in enumerate(self.tree):
            if element.tag == BibleBooksCodesConvertor.mainElementTag:
                # Check compulsory attributes on this main element
                for attributeName in BibleBooksCodesConvertor.compulsoryAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is None:
                        logging.error( "Compulsory '%s' attribute is missing from %s element in record %i" % ( attributeName, element.tag, j ) )
                    if not attributeValue:
                        logging.warning( "Compulsory '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, j ) )

                # Check optional attributes on this main element
                for attributeName in BibleBooksCodesConvertor.optionalAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if not attributeValue:
                            logging.warning( "Optional '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, j ) )

                # Check for unexpected additional attributes on this main element
                for attributeName in element.keys():
                    attributeValue = element.get( attributeName )
                    if attributeName not in BibleBooksCodesConvertor.compulsoryAttributes and attributeName not in BibleBooksCodesConvertor.optionalAttributes:
                        logging.warning( "Additional '%s' attribute ('%s') found on %s element in record %i" % ( attributeName, attributeValue, element.tag, j ) )

                # Check the attributes that must contain unique information (in that particular field -- doesn't check across different attributes)
                for attributeName in BibleBooksCodesConvertor.uniqueAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if attributeValue in uniqueDict[attributeName]:
                            logging.error( "Found '%s' data repeated in '%s' field on %s element in record %i" % ( attributeValue, attributeName, element.tag, j ) )
                        uniqueDict[attributeName].append( attributeValue )

                # Check the ascending ID elements
                ID = int( element.find("id").text )
                if ID != expectedID: logging.warning( "IDs out of sequence: expected %i but got '%i' (record %i)" % ( expectedID, ID, j ) )
                expectedID += 1

                # Check compulsory elements
                for elementName in BibleBooksCodesConvertor.compulsoryElements:
                    if element.find( elementName ) is None:
                        logging.error( "Compulsory '%s' element is missing in record with ID '%i' (record %i)" % ( elementName, ID, j ) )
                    if not element.find( elementName ).text:
                        logging.warning( "Compulsory '%s' element is blank in record with ID '%i' (record %i)" % ( elementName, ID, j ) )

                # Check optional elements
                for elementName in BibleBooksCodesConvertor.optionalElements:
                    if element.find( elementName ) is not None:
                        if not element.find( elementName ).text:
                            logging.warning( "Optional '%s' element is blank in record with ID '%i' (record %i)" % ( elementName, ID, j ) )

                # Check for unexpected additional elements
                for subelement in element:
                    if subelement.tag not in BibleBooksCodesConvertor.compulsoryElements and subelement.tag not in BibleBooksCodesConvertor.optionalElements:
                        logging.warning( "Additional '%s' element ('%s') found in record with ID '%i' (record %i)" % ( subelement.tag, subelement.text, ID, j ) )

                # Check the elements that must contain unique information (in that particular element -- doesn't check across different elements)
                for elementName in BibleBooksCodesConvertor.uniqueElements:
                    if element.find( elementName ) is not None:
                        text = element.find( elementName ).text
                        if text in uniqueDict[elementName]:
                            logging.error( "Found '%s' data repeated in '%s' element in record with ID '%i' (record %i)" % ( text, elementName, ID, j ) )
                        uniqueDict[elementName].append( text )
            else:
                logging.warning( "Unexpected element: %s in record %i" % ( element.tag, j ) )
    # end of validate

    def importDataToPython( self ):
        """
        Loads (and pivots) the data (not including the header) into suitable Python containers to use in a Python program.
        (Of course, you can just use the elementTree in self.tree if you prefer.)
        """
        assert( len ( self.tree ) )

        # We'll create a number of dictionaries with different elements as the key
        myIDDict, myRADict, mySBLDict, myOADict, myPADict, myPNDict, myENDict = OrderedDict(), OrderedDict(), {}, {}, {}, {}, {}
        for element in self.tree:
            # Get the required information out of the tree for this element
            # Start with the compulsory elements
            ID = element.find("id").text
            nameEnglish = element.find("nameEnglish").text # This name is really just a comment element
            referenceAbbreviation = element.find("referenceAbbreviation").text
            # The optional elements are set to None if they don't exist
            SBLAbbreviation = None if element.find("SBLAbbreviation") is None else  element.find("SBLAbbreviation").text
            OSISAbbreviation = None if element.find("OSISAbbreviation") is None else  element.find("OSISAbbreviation").text
            ParatextAbbreviation = None if element.find("ParatextAbbreviation") is None else  element.find("ParatextAbbreviation").text
            ParatextNumberString = None if element.find("ParatextNumber") is None else  element.find("ParatextNumber").text

            # Now put it into my dictionaries for easy access
            # This part should be customized or added to for however you need to process the data
            #   Add .upper() if you require the abbreviations to be uppercase (or .lower() for lower case)
            #   The referenceAbbreviation is UPPER CASE by definition
            if "id" in BibleBooksCodesConvertor.compulsoryElements or ID:
                intID = int( ID )
                if "id" in BibleBooksCodesConvertor.uniqueElements: assert( intID not in myIDDict ) # Shouldn't be any duplicates
                myIDDict[intID] = ( referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish, )
            if "referenceAbbreviation" in BibleBooksCodesConvertor.compulsoryElements or referenceAbbreviation:
                if "referenceAbbreviation" in BibleBooksCodesConvertor.uniqueElements: assert( referenceAbbreviation not in myRADict ) # Shouldn't be any duplicates
                myRADict[referenceAbbreviation] = ( intID, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish, )
            if "SBLAbbreviation" in BibleBooksCodesConvertor.compulsoryElements or SBLAbbreviation:
                if "SBLAbbreviation" in BibleBooksCodesConvertor.uniqueElements: ssert( SBLAbbreviation not in myOADict ) # Shouldn't be any duplicates 
                mySBLDict[SBLAbbreviation] = ( intID, referenceAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish, )
            if "OSISAbbreviation" in BibleBooksCodesConvertor.compulsoryElements or OSISAbbreviation:
                if "OSISAbbreviation" in BibleBooksCodesConvertor.uniqueElements: assert( OSISAbbreviation not in myOADict ) # Shouldn't be any duplicates 
                myOADict[OSISAbbreviation] = ( intID, referenceAbbreviation, SBLAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish, )
            if "ParatextAbbreviation" in BibleBooksCodesConvertor.compulsoryElements or ParatextAbbreviation:
                if "ParatextAbbreviation" in BibleBooksCodesConvertor.uniqueElements: assert( ParatextAbbreviation not in myPADict ) # Shouldn't be any duplicates
                myPADict[ParatextAbbreviation] = ( intID, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextNumberString, nameEnglish )
            if "ParatextNumber" in BibleBooksCodesConvertor.compulsoryElements or ParatextNumberString:
                if "ParatextNumber" in BibleBooksCodesConvertor.uniqueElements: assert( ParatextNumberString not in myPNDict ) # Shouldn't be any duplicates
                myPNDict[ParatextNumberString] = ( intID, ParatextAbbreviation, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, nameEnglish )
            if "nameEnglish" in BibleBooksCodesConvertor.compulsoryElements or ParatextNumberString:
                if "nameEnglish" in BibleBooksCodesConvertor.uniqueElements: assert( nameEnglish not in myENDict ) # Shouldn't be any duplicates
                myENDict[nameEnglish] = ( intID, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString )
        return myIDDict, myRADict, mySBLDict, myOADict, myPADict, myPNDict, myENDict # Just throw away any of the dictionaries that you don't need
    # end of importDataToPython

    def exportDataToPython( self, filepath=None ):
        """
        Writes the information tables to a .py file that can be cut and pasted into a Python program.
        """
        def exportPythonDict( theFile, theDict, dictName, keyComment, fieldsComment ):
            """Exports theDict to theFile."""
            theFile.write( "%s = {\n  # Key is %s\n  # Fields are: %s\n" % ( dictName, keyComment, fieldsComment ) )
            for entry in sorted(theDict.keys()):
                if isinstance( entry, str ):
                    theFile.write( "  '%s': %s,\n" % ( entry, theDict[entry] ) )
                elif isinstance( entry, int ):
                    theFile.write( "  %i: %s,\n" % ( entry, theDict[entry] ) )
                else:
                    logging.error( "Can't handle this type of data yet: %s" % ( entry ) )
            theFile.write( "}\n# end of %s\n\n" % ( dictName ) )
        # end of exportPythonDict

        from datetime import datetime

        assert( len ( self.tree ) )
        if not filepath: filepath = os.path.join( "DerivedFiles", BibleBooksCodesConvertor.filenameBase + ".py" )
        print( "Exporting to %s..." % ( filepath ) )

        IDDict, RADict, SBLDict, OADict, PADict, PNDict, ENDict = self.importDataToPython()
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# %s\n#\n" % ( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by BibleBooksCodesConvertor.py %s\n#\n" % ( datetime.now() ) )
            if self.title: myFile.write( "# %s\n" % ( self.title ) )
            if self.version: myFile.write( "#  Version: %s\n" % ( self.version ) )
            if self.date: myFile.write( "#  Date: %s\n#\n" % ( self.date ) )
            myFile.write( "#   %i %s loaded from the original XML file.\n#\n\n" % ( len(self.tree), BibleBooksCodesConvertor.treeTag ) )
            exportPythonDict( myFile, IDDict, "IDDict", "id", "referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            exportPythonDict( myFile, RADict, "RADict", "referenceAbbreviation", "id, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            exportPythonDict( myFile, SBLDict, "SBLDict", "SBLAbbreviation", "id, ReferenceAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            exportPythonDict( myFile, OADict, "OADict", "OSISAbbreviation", "id, ReferenceAbbreviation, SBLAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            exportPythonDict( myFile, PADict, "PADict", "ParatextAbbreviation", "id, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            exportPythonDict( myFile, PNDict, "PNDict", "ParatextNumberString", "id, ParatextAbbreviation, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, PNDict, "ENDict", "nameEnglish", "id, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString" )
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

        assert( len ( self.tree ) )
        if not filepath: filepath = os.path.join( "DerivedFiles", BibleBooksCodesConvertor.filenameBase + ".h" )
        print( "Exporting to %s..." % ( filepath ) )

        IDDict, RADict, SBLDict, OADict, PADict, PNDict, ENDict = self.importDataToPython()
        ifdefName = BibleBooksCodesConvertor.filenameBase.upper() + "_h"
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "// %s\n//\n" % ( filepath ) )
            myFile.write( "// This UTF-8 file was automatically generated by BibleBooksCodesConvertor.py %s\n//\n" % ( datetime.now() ) )
            if self.title: myFile.write( "// %s\n" % ( self.title ) )
            if self.version: myFile.write( "//  Version: %s\n" % ( self.version ) )
            if self.date: myFile.write( "//  Date: %s\n//\n" % ( self.date ) )
            myFile.write( "//   %i %s loaded from the original XML file.\n//\n\n" % ( len(self.tree), BibleBooksCodesConvertor.treeTag ) )
            myFile.write( "#ifndef %s\n#define %s\n\n" % ( ifdefName, ifdefName ) )
            exportPythonDict( myFile, IDDict, "IDDict", "{int id; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "id (sorted), referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            exportPythonDict( myFile, RADict, "RADict", "{char* refAbbrev; int id; char* SBLAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "referenceAbbreviation (sorted), SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, SBLDict, "SBLDict", "{char* SBLAbbrev; int id; char* refAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "SBLAbbreviation (sorted), ReferenceAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, OADict, "OADict", "{char* OSISAbbrev; int id; char* refAbbrev; char* SBLAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "OSISAbbreviation (sorted), ReferenceAbbreviation, SBLAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, PADict, "PADict", "{char* PTAbbrev; int id; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* PTNum; char* EngName;}", "ParatextAbbreviation (sorted), referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, PNDict, "PNDict", "{char* PTNum; int id; char* PTAbbrev; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* EngName;}", "ParatextNumberString (sorted), ParatextAbbreviation, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, id, nameEnglish (comment only)" )
            myFile.write( "#endif // %s\n" % ( ifdefName ) )
    # end of exportDataToC
# end of BibleBooksCodesConvertor class


def demo():
    """
    Demonstrate reading the XML file and outputting C and Python data tables.
    """
    print( "Bible Books Codes Convertor V%s" % ( versionString ) )
    bbcc = BibleBooksCodesConvertor()
    print( bbcc )
    bbcc.exportDataToPython()
    bbcc.exportDataToC()
# end of demo

if __name__ == '__main__':
    demo()
# end of BibleBooksCodesConvertor.py
