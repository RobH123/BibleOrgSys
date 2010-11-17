#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleBooksCodes.py
#
# Module handling BibleBooksCodes.xml to produce C and Python data tables
#   Last modified: 2010-11-16 (also update versionString below)
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

progName = "Bible Books Codes handler"
versionString = "0.91"

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
    compulsoryElements = ( "nameEnglish", "referenceAbbreviation", "referenceNumber" )
    optionalElements = ( "SBLAbbreviation", "OSISAbbreviation", "CCELNumber", "ParatextAbbreviation", "ParatextNumber", "NETBibleAbbreviation", "SwordAbbreviation" )
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
        if self.version: result += ('\n' if result else '') + "Version: %s " % ( self.version )
        if self.date: result += ('\n' if result else '') + "Date: %s" % ( self.date )
        result += ('\n' if result else '') + "Num entries = %i" % ( len(self.tree) )
        return result
    # end of __str__

    def load( self, XMLFilepath ):
        """
        Load the source XML file and remove the header from the tree.
        Also, extracts some useful elements from the header element.
        """
        self.tree = ElementTree().parse ( XMLFilepath )
        assert( len ( self.tree ) ) # Fail here if we didn't load anything at all

        if self.tree.tag == BibleBooksCodesConvertor.treeTag:
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
        for elementName in BibleBooksCodesConvertor.uniqueElements: uniqueDict["Element_"+elementName] = []
        for attributeName in BibleBooksCodesConvertor.uniqueAttributes: uniqueDict["Attribute_"+attributeName] = []

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
                        if attributeValue in uniqueDict["Attribute_"+attributeName]:
                            logging.error( "Found '%s' data repeated in '%s' field on %s element in record %i" % ( attributeValue, attributeName, element.tag, j ) )
                        uniqueDict["Attribute_"+attributeName].append( attributeValue )

                # Get the referenceAbbreviation to use as a record ID
                ID = element.find("referenceAbbreviation").text

                # Check compulsory elements
                for elementName in BibleBooksCodesConvertor.compulsoryElements:
                    if element.find( elementName ) is None:
                        logging.error( "Compulsory '%s' element is missing in record with ID '%s' (record %i)" % ( elementName, ID, j ) )
                    elif not element.find( elementName ).text:
                        logging.warning( "Compulsory '%s' element is blank in record with ID '%s' (record %i)" % ( elementName, ID, j ) )

                # Check optional elements
                for elementName in BibleBooksCodesConvertor.optionalElements:
                    if element.find( elementName ) is not None:
                        if not element.find( elementName ).text:
                            logging.warning( "Optional '%s' element is blank in record with ID '%s' (record %i)" % ( elementName, ID, j ) )

                # Check for unexpected additional elements
                for subelement in element:
                    if subelement.tag not in BibleBooksCodesConvertor.compulsoryElements and subelement.tag not in BibleBooksCodesConvertor.optionalElements:
                        logging.warning( "Additional '%s' element ('%s') found in record with ID '%s' (record %i)" % ( subelement.tag, subelement.text, ID, j ) )

                # Check the elements that must contain unique information (in that particular element -- doesn't check across different elements)
                for elementName in BibleBooksCodesConvertor.uniqueElements:
                    if element.find( elementName ) is not None:
                        text = element.find( elementName ).text
                        if text in uniqueDict["Element_"+elementName]:
                            logging.error( "Found '%s' data repeated in '%s' element in record with ID '%s' (record %i)" % ( text, elementName, ID, j ) )
                        uniqueDict["Element_"+elementName].append( text )
            else:
                logging.warning( "Unexpected element: %s in record %i" % ( element.tag, j ) )
    # end of validate

    def getEnglishName( self, BBB ):
        """
        Gets the English bookname (useful as a comment) given the referenceAbbreviation BBB.
        """
        assert( len ( self.tree ) )

        for element in self.tree: # There must be a way to do this without a loop???
            if element.find("referenceAbbreviation").text == BBB:
                return element.find("nameEnglish").text
    # end of getEnglishName

    def getAllParatextBooksCodes( self ):
        """
        Return a list of all available Paratext book codes.
        """
        assert( len ( self.tree ) )

        result = []
        for element in self.tree:
            if element.find("ParatextAbbreviation") is not None:
                code = element.find("ParatextAbbreviation").text
                if code not in result: result.append( code )
        return result
    # end of getAllParatextBooksCodes

    def getAllParatextBooksCodeNumberTriples( self ):
        """
        Return a list of all available Paratext book codes.

        The list contains tuples of: paratextAbbreviation, paratextNumber, referenceAbbreviation
        """
        assert( len ( self.tree ) )

        found, result = [], []
        for element in self.tree:
            if element.find("ParatextAbbreviation") is not None:
                pA = element.find("ParatextAbbreviation").text
                pN = element.find("ParatextNumber").text if element.find("ParatextNumber") is not None else ''
                if pA not in found: # Don't want duplicates (where more than one book maps to a single paratextAbbreviation)
                    result.append( (pA, pN, element.find("referenceAbbreviation").text,) )
                    found.append( pA )
        return result
    # end of getAllParatextBooksCodeNumberTriples

    def importDataToPython( self ):
        """
        Loads (and pivots) the data (not including the header) into suitable Python containers to use in a Python program.
        (Of course, you can just use the elementTree in self.tree if you prefer.)
        """
        assert( len ( self.tree ) )

        # We'll create a number of dictionaries with different elements as the key
        myIDDict, myRADict, mySBLDict, myOADict, myCCELDict, myPADict, myPNDict, myENDict, mySwDict = OrderedDict(), OrderedDict(), {}, {}, {}, {}, {},{},{}
        for element in self.tree:
            # Get the required information out of the tree for this element
            # Start with the compulsory elements
            nameEnglish = element.find("nameEnglish").text # This name is really just a comment element
            referenceAbbreviation = element.find("referenceAbbreviation").text
            ID = element.find("referenceNumber").text
            intID = int( ID )
            # The optional elements are set to None if they don't exist
            SBLAbbreviation = None if element.find("SBLAbbreviation") is None else element.find("SBLAbbreviation").text
            OSISAbbreviation = None if element.find("OSISAbbreviation") is None else element.find("OSISAbbreviation").text
            CCELNumberString = None if element.find("CCELNumber") is None else element.find("CCELNumber").text
            #CCELNumber = int( CCELNumberString ) if CCELNumberString else -1
            ParatextAbbreviation = None if element.find("ParatextAbbreviation") is None else element.find("ParatextAbbreviation").text
            ParatextNumberString = None if element.find("ParatextNumber") is None else element.find("ParatextNumber").text
            #ParatextNumber = int( ParatextNumberString ) if ParatextNumberString else -1
            SwordAbbreviation = None if element.find("SwordAbbreviation") is None else element.find("SwordAbbreviation").text

            # Now put it into my dictionaries for easy access
            # This part should be customized or added to for however you need to process the data
            #   Add .upper() if you require the abbreviations to be uppercase (or .lower() for lower case)
            #   The referenceAbbreviation is UPPER CASE by definition
            if "referenceAbbreviation" in BibleBooksCodesConvertor.compulsoryElements or referenceAbbreviation:
                if "referenceAbbreviation" in BibleBooksCodesConvertor.uniqueElements: assert( referenceAbbreviation not in myRADict ) # Shouldn't be any duplicates
                myRADict[referenceAbbreviation] = ( intID, SBLAbbreviation, OSISAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish, )
            if "referenceNumber" in BibleBooksCodesConvertor.compulsoryElements or ID:
                if "referenceNumber" in BibleBooksCodesConvertor.uniqueElements: assert( intID not in myIDDict ) # Shouldn't be any duplicates
                myIDDict[intID] = ( referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish, )
            if "SBLAbbreviation" in BibleBooksCodesConvertor.compulsoryElements or SBLAbbreviation:
                if "SBLAbbreviation" in BibleBooksCodesConvertor.uniqueElements: ssert( SBLAbbreviation not in myOADict ) # Shouldn't be any duplicates 
                mySBLDict[SBLAbbreviation] = ( intID, referenceAbbreviation, OSISAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish, )
            if "OSISAbbreviation" in BibleBooksCodesConvertor.compulsoryElements or OSISAbbreviation:
                if "OSISAbbreviation" in BibleBooksCodesConvertor.uniqueElements: assert( OSISAbbreviation not in myOADict ) # Shouldn't be any duplicates 
                myOADict[OSISAbbreviation] = ( intID, referenceAbbreviation, SBLAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish, )
            if "CCELNumberString" in BibleBooksCodesConvertor.compulsoryElements or CCELNumberString:
                if "CCELNumberString" in BibleBooksCodesConvertor.uniqueElements: assert( CCELNumberString not in myCCELDict ) # Shouldn't be any duplicates
                myCCELDict[CCELNumberString] = ( intID, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish )
            if "ParatextAbbreviation" in BibleBooksCodesConvertor.compulsoryElements or ParatextAbbreviation:
                if "ParatextAbbreviation" in BibleBooksCodesConvertor.uniqueElements: assert( ParatextAbbreviation not in myPADict ) # Shouldn't be any duplicates
                myPADict[ParatextAbbreviation] = ( intID, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, CCELNumberString, ParatextNumberString, SwordAbbreviation, nameEnglish )
            if "ParatextNumberString" in BibleBooksCodesConvertor.compulsoryElements or ParatextNumberString:
                if "ParatextNumberString" in BibleBooksCodesConvertor.uniqueElements: assert( ParatextNumberString not in myPNDict ) # Shouldn't be any duplicates
                myPNDict[ParatextNumberString] = ( intID, ParatextAbbreviation, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, CCELNumberString, SwordAbbreviation, nameEnglish )
            if "SwordAbbreviation" in BibleBooksCodesConvertor.compulsoryElements or SwordAbbreviation:
                if "SwordAbbreviation" in BibleBooksCodesConvertor.uniqueElements: assert( SwordAbbreviation not in mySwDict ) # Shouldn't be any duplicates
                mySwDict[SwordAbbreviation] = ( intID, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, nameEnglish )
            if "nameEnglish" in BibleBooksCodesConvertor.compulsoryElements or ParatextNumberString:
                if "nameEnglish" in BibleBooksCodesConvertor.uniqueElements: assert( nameEnglish not in myENDict ) # Shouldn't be any duplicates
                myENDict[nameEnglish] = ( intID, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation )
        return myIDDict, myRADict, mySBLDict, myOADict, myCCELDict, myPADict, myPNDict, mySwDict, myENDict # Just throw away any of the dictionaries that you don't need
    # end of importDataToPython

    def exportDataToPython( self, filepath=None ):
        """
        Writes the information tables to a .py file that can be cut and pasted into a Python program.
        """
        def exportPythonDict( theFile, theDict, dictName, keyComment, fieldsComment ):
            """Exports theDict to theFile."""
            for dictKey in theDict.keys(): # Have to iterate this :(
                fieldsCount = len( theDict[dictKey] )
                break # We only check the first (random) entry we get
            theFile.write( "%s = {\n  # Key is %s\n  # Fields (%i) are: %s\n" % ( dictName, keyComment, fieldsCount, fieldsComment ) )
            for dictKey in sorted(theDict.keys()):
                theFile.write( '  %s: %s,\n' % ( repr(dictKey), theDict[dictKey] ) )
            theFile.write( "}\n# end of %s (%i entries)\n\n" % ( dictName, len(theDict) ) )
        # end of exportPythonDict

        from datetime import datetime

        assert( len ( self.tree ) )
        if not filepath: filepath = os.path.join( "DerivedFiles", BibleBooksCodesConvertor.filenameBase + "_Tables.py" )
        print( "Exporting to %s..." % ( filepath ) )

        IDDict, RADict, SBLDict, OADict, CCELDict, PADict, PNDict, SwDict, ENDict = self.importDataToPython()
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# %s\n#\n" % ( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by BibleBooksCodes.py on %s\n#\n" % ( datetime.now() ) )
            if self.title: myFile.write( "# %s\n" % ( self.title ) )
            if self.version: myFile.write( "#  Version: %s\n" % ( self.version ) )
            if self.date: myFile.write( "#  Date: %s\n#\n" % ( self.date ) )
            myFile.write( "#   %i %s loaded from the original XML file.\n#\n\n" % ( len(self.tree), BibleBooksCodesConvertor.treeTag ) )
            exportPythonDict( myFile, IDDict, "IDDict", "referenceNumber", "referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, RADict, "RADict", "referenceAbbreviation", "referenceNumber, SBLAbbreviation, OSISAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, SBLDict, "SBLDict", "SBLAbbreviation", "referenceNumber, ReferenceAbbreviation, OSISAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, OADict, "OADict", "OSISAbbreviation", "referenceNumber, ReferenceAbbreviation, SBLAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, CCELDict, "CCELDict", "CCELAbbreviation", "referenceNumber, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, PADict, "PADict", "ParatextAbbreviation", "referenceNumber, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, CCELNumberString, ParatextNumberString, SwordAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, PNDict, "PNDict", "ParatextNumberString", "referenceNumber, ParatextAbbreviation, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, CCELNumberString, SwordAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, SwDict, "SwDict", "SwordAbbreviation", "referenceNumber, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            exportPythonDict( myFile, ENDict, "ENDict", "nameEnglish", "referenceNumber, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation" )
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

            for dictKey in theDict.keys(): # Have to iterate this :(
                fieldsCount = len( theDict[dictKey] ) + 1 # Add one since we include the key in the count
                break # We only check the first (random) entry we get
            theFile.write( "static struct %s\n %s[] = {\n  // Fields (%i) are %s\n" % ( structName, dictName, fieldsCount, fieldsComment ) )
            for dictKey in sorted(theDict.keys()):
                if isinstance( dictKey, str ):
                    theFile.write( "  {\"%s\", %s},\n" % ( dictKey, convertEntry(theDict[dictKey]) ) )
                elif isinstance( dictKey, int ):
                    theFile.write( "  {%i, %s},\n" % ( dictKey, convertEntry(theDict[dictKey]) ) )
                else:
                    logging.error( "Can't handle this type of data yet: %s" % ( dictKey ) )
            theFile.write( "}; // %s (%i entries)\n\n" % ( dictName, len(theDict) ) )
        # end of exportPythonDict

        from datetime import datetime

        assert( len ( self.tree ) )
        if not filepath: filepath = os.path.join( "DerivedFiles", BibleBooksCodesConvertor.filenameBase + "_Tables.h" )
        print( "Exporting to %s..." % ( filepath ) )

        IDDict, RADict, SBLDict, OADict, CCELDict, PADict, PNDict, SwDict, ENDict = self.importDataToPython()
        ifdefName = BibleBooksCodesConvertor.filenameBase.upper() + "_Tables_h"
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "// %s\n//\n" % ( filepath ) )
            myFile.write( "// This UTF-8 file was automatically generated by BibleBooksCodes.py on %s\n//\n" % ( datetime.now() ) )
            if self.title: myFile.write( "// %s\n" % ( self.title ) )
            if self.version: myFile.write( "//  Version: %s\n" % ( self.version ) )
            if self.date: myFile.write( "//  Date: %s\n//\n" % ( self.date ) )
            myFile.write( "//   %i %s loaded from the original XML file.\n//\n\n" % ( len(self.tree), BibleBooksCodesConvertor.treeTag ) )
            myFile.write( "#ifndef %s\n#define %s\n\n" % ( ifdefName, ifdefName ) )
            exportPythonDict( myFile, IDDict, "IDDict", "{int referenceNumber; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; int CCELNum; char* PTAbbrev; int PTNum; char* SwAbbrev; char* EngName;}", "referenceNumber (sorted), referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, RADict, "RADict", "{char* refAbbrev; int referenceNumber; char* SBLAbbrev; char* OSISAbbrev; int CCELNum; char* PTAbbrev; int PTNum; char* SwAbbrev; char* EngName;}", "referenceAbbreviation (sorted), SBLAbbreviation, OSISAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, SBLDict, "SBLDict", "{char* SBLAbbrev; int referenceNumber; char* refAbbrev; char* OSISAbbrev; int CCELNum; char* PTAbbrev; int PTNum; char* SwAbbrev; char* EngName;}", "SBLAbbreviation (sorted), ReferenceAbbreviation, OSISAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, OADict, "OADict", "{char* OSISAbbrev; int referenceNumber; char* refAbbrev; char* SBLAbbrev; int CCELNum; char* PTAbbrev; int PTNum; char* SwAbbrev; char* EngName;}", "OSISAbbreviation (sorted), ReferenceAbbreviation, SBLAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, CCELDict, "CCELDict", "{int CCELNum; int referenceNumber; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* PTAbbrev; int PTNum; char* SwAbbrev; char* EngName;}", "CCELNumberString (sorted), referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, SwordAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, PADict, "PADict", "{char* PTAbbrev; int referenceNumber; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; int CCELNum; int PTNum; char* SwAbbrev; char* EngName;}", "ParatextAbbreviation (sorted), referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, CCELNumberString, ParatextNumberString, SwordAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, PNDict, "PNDict", "{int PTNum; int referenceNumber; char* PTAbbrev; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; int CCELNum; char* SwAbbrev; char* EngName;}", "ParatextNumberString (sorted), ParatextAbbreviation, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, CCELNumberString, SwordAbbreviation, nameEnglish (comment only)" )
            exportPythonDict( myFile, SwDict, "SwDict", "{char* SwAbbrev; int referenceNumber; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; int CCELNum; char* PTAbbrev; int PTNum; char* EngName;}", "SwordAbbreviation (sorted), referenceNumber, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            myFile.write( "#endif // %s\n" % ( ifdefName ) )
    # end of exportDataToC
# end of BibleBooksCodesConvertor class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v%s" % ( versionString ) )
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML file to .py and .h tables suitable for directly including into other programs")
    CommandLineOptions, args = parser.parse_args()

    bbcc = BibleBooksCodesConvertor() # Load the XML
    if CommandLineOptions.export:
        bbcc.exportDataToPython() # Produce the .py tables
        bbcc.exportDataToC() # Produce the .h tables
    else: # Must be demo mode
        print( "%s V%s" % ( progName, versionString ) )
        print( bbcc ) # Just print a summary
        #print( bbcc.getAllParatextBooksCodes() )
        print( bbcc.getAllParatextBooksCodeNumberTriples() )
        print( bbcc.getEnglishName( "JN3" ) )
# end of main

if __name__ == '__main__':
    main()
# end of BibleBooksCodes.py
