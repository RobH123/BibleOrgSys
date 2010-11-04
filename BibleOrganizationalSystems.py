#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleOrganizationalSystems.py
#
# Module handling BibleOrganizationalSystems.xml to produce C and Python data tables
#   Last modified: 2010-11-04 (also update versionString below)
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
Module handling BibleOrganizationalSystems.xml to produce C and Python data tables.
"""

progName = "Bible Organization Systems handler"
versionString = "0.10"


import logging, os.path
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree
import BibleBooksCodes, iso_639_3


class BibleOrganizationalSystemsConvertor:
    """
    Class for handling and converting BibleOrganizationalSystems.
    """
    filenameBase = "BibleOrganizationalSystems"
    treeTag = "BibleOrganizationalSystems"
    headerTag = "header"
    mainElementTag = "BibleOrganizationalSystem"
    compulsoryAttributes = ()
    optionalAttributes = ()
    uniqueAttributes = compulsoryAttributes + optionalAttributes
    compulsoryElements = ( "nameEnglish", "name", "versificationSystemCode" )
    optionalElements = ()
    uniqueElements = ( "nameEnglish", "name" ) + optionalElements

    def __init__( self, XMLFilepath=None, ISO639Dict=None, BibleBooksCodesDict=None ):
        """
        Constructor: expects the filepath of the source XML file.
        Loads (and crudely validates the XML file) into an element tree.
        """
        if XMLFilepath is None:
            XMLFilepath = os.path.join( "DataFiles", BibleOrganizationalSystemsConvertor.filenameBase + ".xml" )
        self.ISO639Dict, self.BibleBooksCodesDict = ISO639Dict, BibleBooksCodesDict
        self.title, self.version, self.date = None, None, None
        self.header, self.namesTree = None, None
        self.systems, self.loadedPrefixes = {}, []
        self.load( XMLFilepath )
        self.validate()
        self.loadSystems()
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = ""
        if self.title: result += ('\n' if result else '') + self.title
        if self.version: result += ('\n' if result else '') + "Version: %s" % ( self.version )
        if self.date: result += ('\n' if result else '') + "Date: %s" % ( self.date )
        result += ('\n' if result else '') + "Num entries = %i" % ( len(self.namesTree) )

        result += ('\n' if result else '') + "Num systems loaded = %i" % ( len(self.systems) )
        for x in self.systems:
            result += ('\n' if result else '') + "  %s" % ( x )
            title = self.systems[x]["title"]
            if title: result += ('\n' if result else '') + "    %s" % ( title )
            version = self.systems[x]["version"]
            if version: result += ('\n' if result else '') + "    Version: %s" % ( version )
            date = self.systems[x]["date"]
            if date: result += ('\n' if result else '') + "    Date: %s" % ( date )
            result += ('\n' if result else '') + "    Num entries = %i" % ( len(self.systems[x]["tree"]) )
        return result
    # end of __str__

    def load( self, XMLFilepath ):
        """
        Load the source XML file and remove the header from the tree.
        Also, extracts some useful elements from the header element.
        """
        self.namesTree = ElementTree().parse ( XMLFilepath )
        assert( self.namesTree ) # Fail here if we didn't load anything at all

        if self.namesTree.tag  == BibleOrganizationalSystemsConvertor.treeTag:
            header = self.namesTree[0]
            if header.tag == BibleOrganizationalSystemsConvertor.headerTag:
                self.header = header
                self.namesTree.remove( header )
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
                logging.warning( "Missing header element (looking for '%s' tag)" % ( BibleOrganizationalSystemsConvertor.headerTag ) )
        else:
            logging.error( "Expected to load '%s' but got '%s'" % ( BibleOrganizationalSystemsConvertor.treeTag, self.namesTree.tag ) )
    # end of load

    def validate( self ):
        """
        Check/validate the loaded data.
        """
        assert( self.namesTree )

        uniqueDict = {}
        for elementName in BibleOrganizationalSystemsConvertor.uniqueElements: uniqueDict[elementName] = []

        expectedID = 1
        for j,element in enumerate(self.namesTree):
            if element.tag == BibleOrganizationalSystemsConvertor.mainElementTag:
                # Check compulsory attributes on this main element
                for attributeName in BibleOrganizationalSystemsConvertor.compulsoryAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is None:
                        logging.error( "Compulsory '%s' attribute is missing from %s element in record %i" % ( attributeName, element.tag, j ) )
                    if not attributeValue:
                        logging.warning( "Compulsory '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, j ) )

                # Check optional attributes on this main element
                for attributeName in BibleOrganizationalSystemsConvertor.optionalAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if not attributeValue:
                            logging.warning( "Optional '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, j ) )

                # Check for unexpected additional attributes on this main element
                for attributeName in element.keys():
                    attributeValue = element.get( attributeName )
                    if attributeName not in BibleOrganizationalSystemsConvertor.compulsoryAttributes and attributeName not in BibleOrganizationalSystemsConvertor.optionalAttributes:
                        logging.warning( "Additional '%s' attribute ('%s') found on %s element in record %i" % ( attributeName, attributeValue, element.tag, j ) )

                # Check the attributes that must contain unique information (in that particular field -- doesn't check across different attributes)
                for attributeName in BibleOrganizationalSystemsConvertor.uniqueAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if attributeValue in uniqueDict[attributeName]:
                            logging.error( "Found '%s' data repeated in '%s' field on %s element in record %i" % ( attributeValue, attributeName, element.tag, j ) )
                        uniqueDict[attributeName].append( attributeValue )

                ID = element.find("nameEnglish").text
                # Check the ascending ID elements
                #ID = int( element.find("id").text )
                #if ID != expectedID: logging.warning( "IDs out of sequence: expected %i but got '%i' (record %i)" % ( expectedID, ID, j ) )
                #expectedID += 1

                # Check compulsory elements
                for elementName in BibleOrganizationalSystemsConvertor.compulsoryElements:
                    if element.find( elementName ) is None:
                        logging.error( "Compulsory '%s' element is missing in record with ID '%s' (record %i)" % ( elementName, ID, j ) )
                    if not element.find( elementName ).text:
                        logging.warning( "Compulsory '%s' element is blank in record with ID '%s' (record %i)" % ( elementName, ID, j ) )

                # Check optional elements
                for elementName in BibleOrganizationalSystemsConvertor.optionalElements:
                    if element.find( elementName ) is not None:
                        if not element.find( elementName ).text:
                            logging.warning( "Optional '%s' element is blank in record with ID '%s' (record %i)" % ( elementName, ID, j ) )

                # Check for unexpected additional elements
                for subelement in element:
                    if subelement.tag not in BibleOrganizationalSystemsConvertor.compulsoryElements and subelement.tag not in BibleOrganizationalSystemsConvertor.optionalElements:
                        logging.warning( "Additional '%s' element ('%s') found in record with ID '%s' (record %i)" % ( subelement.tag, subelement.text, ID, j ) )

                # Check the elements that must contain unique information (in that particular element -- doesn't check across different elements)
                for elementName in BibleOrganizationalSystemsConvertor.uniqueElements:
                    if element.find( elementName ) is not None:
                        text = element.find( elementName ).text
                        if text in uniqueDict[elementName]:
                            logging.error( "Found '%s' data repeated in '%s' element in record with ID '%s' (record %i)" % ( text, elementName, ID, j ) )
                        uniqueDict[elementName].append( text )
            else:
                logging.warning( "Unexpected element: %s in record %i" % ( element.tag, j ) )
    # end of validate

    def loadSystems( self, folder=None ):
        """
        Load and pre-process the specified versification systems.
        """
        filenameBase = "BibleVersificationSystem"
        treeTag = "BibleVersificationSystem"
        headerTag = "header"
        mainElementTag = "BibleBookVersification"
        compulsoryAttributes = ()
        optionalAttributes = ()
        uniqueAttributes = compulsoryAttributes + optionalAttributes
        compulsoryElements = ( "nameEnglish", "referenceAbbreviation", "numChapters", "numVerses" )
        optionalElements = ()
        uniqueElements = ( "nameEnglish", "referenceAbbreviation" ) + optionalElements

        def validateSystem( versificationTree ):
            """
            """
            assert( versificationTree )

            uniqueDict = {}
            for elementName in uniqueElements: uniqueDict[elementName] = []

            expectedID = 1
            for k,element in enumerate(versificationTree):
                if element.tag == mainElementTag:
                    # Check compulsory attributes on this main element
                    for attributeName in compulsoryAttributes:
                        attributeValue = element.get( attributeName )
                        if attributeValue is None:
                            logging.error( "Compulsory '%s' attribute is missing from %s element in record %i" % ( attributeName, element.tag, k ) )
                        if not attributeValue:
                            logging.warning( "Compulsory '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, k ) )

                    # Check optional attributes on this main element
                    for attributeName in optionalAttributes:
                        attributeValue = element.get( attributeName )
                        if attributeValue is not None:
                            if not attributeValue:
                                logging.warning( "Optional '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, k ) )

                    # Check for unexpected additional attributes on this main element
                    for attributeName in element.keys():
                        attributeValue = element.get( attributeName )
                        if attributeName not in compulsoryAttributes and attributeName not in optionalAttributes:
                            logging.warning( "Additional '%s' attribute ('%s') found on %s element in record %i" % ( attributeName, attributeValue, element.tag, k ) )

                    # Check the attributes that must contain unique information (in that particular field -- doesn't check across different attributes)
                    for attributeName in uniqueAttributes:
                        attributeValue = element.get( attributeName )
                        if attributeValue is not None:
                            if attributeValue in uniqueDict[attributeName]:
                                logging.error( "Found '%s' data repeated in '%s' field on %s element in record %i" % ( attributeValue, attributeName, element.tag, k ) )
                            uniqueDict[attributeName].append( attributeValue )

                    ID = element.find("referenceAbbreviation").text
                    # Check the ascending ID elements
                    #ID = int( element.find("id").text )
                    #if ID != expectedID: logging.warning( "IDs out of sequence: expected %i but got '%i' (record %i)" % ( expectedID, ID, k ) )
                    #expectedID += 1

                    # Check compulsory elements
                    for elementName in compulsoryElements:
                        if element.find( elementName ) is None:
                            logging.error( "Compulsory '%s' element is missing in record with ID '%s' (record %i)" % ( elementName, ID, k ) )
                        if not element.find( elementName ).text:
                            logging.warning( "Compulsory '%s' element is blank in record with ID '%s' (record %i)" % ( elementName, ID, k ) )

                    # Check optional elements
                    for elementName in optionalElements:
                        if element.find( elementName ) is not None:
                            if not element.find( elementName ).text:
                                logging.warning( "Optional '%s' element is blank in record with ID '%s' (record %i)" % ( elementName, ID, k ) )

                    # Check for unexpected additional elements
                    for subelement in element:
                        if subelement.tag not in compulsoryElements and subelement.tag not in optionalElements:
                            logging.warning( "Additional '%s' element ('%s') found in record with ID '%s' (record %i)" % ( subelement.tag, subelement.text, ID, k ) )

                    # Check the elements that must contain unique information (in that particular element -- doesn't check across different elements)
                    for elementName in uniqueElements:
                        if element.find( elementName ) is not None:
                            text = element.find( elementName ).text
                            if text in uniqueDict[elementName]:
                                logging.error( "Found '%s' data repeated in '%s' element in record with ID '%s' (record %i)" % ( text, elementName, ID, k ) )
                            uniqueDict[elementName].append( text )
                else:
                    logging.warning( "Unexpected element: %s in record %i" % ( element.tag, k ) )
        # end of validateSystem

        if folder==None: folder = "DataFiles"
        for j,element in enumerate(self.namesTree):
            #ID = element.find("id").text
            nameEnglish = element.find("nameEnglish").text # This name is really just a comment element
            versificationSystemCode = element.find("versificationSystemCode").text # This name is really just a comment element

            if versificationSystemCode not in self.loadedPrefixes:
                filepath = os.path.join( folder, "BibleVersificationSystem_" + versificationSystemCode + ".xml" )
                print( "  Loading %s..." % ( filepath ) )
                self.systems[versificationSystemCode] = {}
                self.systems[versificationSystemCode]["tree"] = ElementTree().parse ( filepath )
                assert( self.systems[versificationSystemCode]["tree"] ) # Fail here if we didn't load anything at all

                # Check and remove the header element
                if self.systems[versificationSystemCode]["tree"].tag  == treeTag:
                    header = self.systems[versificationSystemCode]["tree"][0]
                    if header.tag == headerTag:
                        self.systems[versificationSystemCode]["header"] = header
                        self.systems[versificationSystemCode]["tree"].remove( header )
                        if len(header)>1:
                            logging.info( "Unexpected elements in header" )
                        elif len(header)==0:
                            logging.info( "Missing work element in header" )
                        else:
                            work = header[0]
                            if work.tag == "work":
                                self.systems[versificationSystemCode]["version"] = work.find("version").text
                                self.systems[versificationSystemCode]["date"] = work.find("date").text
                                self.systems[versificationSystemCode]["title"] = work.find("title").text
                            else:
                                logging.warning( "Missing work element in header" )
                    else:
                        logging.warning( "Missing header element (looking for '%s' tag)" % ( headerTag ) )
                else:
                    logging.error( "Expected to load '%s' but got '%s'" % ( treeTag, self.systems[versificationSystemCode]["tree"].tag ) )
                bookCount = 0 # There must be an easier way to do this
                for subelement in self.systems[versificationSystemCode]["tree"]:
                    bookCount += 1
                print( "    Loaded %i books" % ( bookCount ) )

                validateSystem( self.systems[versificationSystemCode]["tree"] )

                self.loadedPrefixes.append( versificationSystemCode )
    # end of loadSystems

    def importDataToPython( self ):
        """
        Loads (and pivots) the data (not including the header) into suitable Python containers to use in a Python program.
        (Of course, you can just use the elementTree in self.namesTree if you prefer.)
        """
        assert( self.namesTree )

        # We'll create a number of dictionaries with different elements as the key
        myNameDict, myCombinedDict = {}, {}
        for element in self.namesTree:
            # Get the required information out of the tree for this element
            # Start with the compulsory elements
            #ID = element.find("id").text
            nameEnglish = element.find("nameEnglish").text # This name is really just a comment element
            versificationSystemCode = element.find("versificationSystemCode").text
            names = {}
            for name in element.findall("name"):
                languageCode = name.get("language")
                names[languageCode] = name.text
                if self.ISO639Dict and languageCode not in self.ISO639Dict:
                    logging.error( "Unrecognized '%s' ISO-639-3 language code in '%s' versification system" % ( languageCode, versificationSystemCode ) )
            assert( names )

            # Make the data dictionary for this versification system
            bookData = OrderedDict()
            for subelement in self.systems[versificationSystemCode]["tree"]:
                #sID = int( subelement.find("id").text )
                sNameEnglish = subelement.find("nameEnglish").text # This name is really just a comment element
                sReferenceAbbreviation = subelement.find("referenceAbbreviation").text
                if self.BibleBooksCodesDict and sReferenceAbbreviation not in self.BibleBooksCodesDict:
                    logging.error( "Unrecognized '%s' book abbreviation in '%s' versification system" % ( sReferenceAbbreviation, versificationSystemCode ) )
                numChapters = int( subelement.find("numChapters").text )
                chapterData = OrderedDict()
                chapterData[0] = numChapters
                for chapterElement in subelement.findall("numVerses"):
                    chapter = int( chapterElement.get("chapter") )
                    numVerses = int( chapterElement.text )
                    assert( chapter not in chapterData )
                    chapterData[chapter] = numVerses
                # Save the data twice -- one of the other sets can be deleted if not required
                # Save it by integer book ID
                #assert( sID not in bookData )
                #bookData[sID] = chapterData
                # Save it by book reference abbreviation
                assert( sReferenceAbbreviation not in bookData )
                bookData[sReferenceAbbreviation] = chapterData 

            # Now put it into my dictionaries for easy access
            # This part should be customized or added to for however you need to process the data
            #   Add .upper() if you require the abbreviations to be uppercase (or .lower() for lower case)
            #if "id" in BibleOrganizationalSystemsConvertor.compulsoryElements or ID:
            #    intID = int( ID )
            #    assert( intID not in myIDDict ) # Shouldn't be any duplicates
            #    myIDDict[intID] = ( nameEnglish, versificationSystemCode, bookData, )
            #    assert( intID not in myCombinedDict ) # Shouldn't be any duplicates
            #    myCombinedDict[intID] = ( nameEnglish, versificationSystemCode, bookData, )
            if "nameEnglish" in BibleOrganizationalSystemsConvertor.compulsoryElements or nameEnglish:
                assert( nameEnglish not in myNameDict ) # Shouldn't be any duplicates
                myNameDict[nameEnglish] = ( versificationSystemCode, bookData, )
                assert( nameEnglish not in myCombinedDict ) # Shouldn't be any duplicates
                myCombinedDict[nameEnglish] = ( versificationSystemCode, bookData, )
        return myNameDict, myCombinedDict # Just throw away any of the dictionaries that you don't need
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

        assert( self.namesTree )
        if not filepath: filepath = os.path.join( "DerivedFiles", BibleOrganizationalSystemsConvertor.filenameBase + ".py" )
        print( "Exporting to %s..." % ( filepath ) )

        IDDict, NameDict, combinedIDNameDict = self.importDataToPython()
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# %s\n#\n" % ( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by BibleOrganizationalSystemsConvertor.py V%s %s\n#\n" % ( versionString, datetime.now() ) )
            if self.title: myFile.write( "# %s\n" % ( self.title ) )
            if self.version: myFile.write( "#  Version: %s\n" % ( self.version ) )
            if self.date: myFile.write( "#  Date: %s\n#\n" % ( self.date ) )
            myFile.write( "#   %i %s entries loaded from the original XML file.\n" % ( len(self.namesTree), BibleOrganizationalSystemsConvertor.treeTag ) )
            myFile.write( "#   %i %s loaded from the original XML files.\n#\n\n" % ( len(self.systems), BibleOrganizationalSystemsConvertor.treeTag ) )
            exportPythonDict( myFile, IDDict, "IDDict", "id", "referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            exportPythonDict( myFile, NameDict, "NameDict", "referenceAbbreviation", "id, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
    # end of exportDataToPython

    def exportDataToC( self, filepath=None ):
        """
        Writes the information tables to a .h file that can be included in c and c++ programs.
        """
        print( "not written yet" ); halt
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

        assert( self.namesTree )
        if not filepath: filepath = os.path.join( "DerivedFiles", BibleOrganizationalSystemsConvertor.filenameBase + ".h" )
        print( "Exporting to %s..." % ( filepath ) )

        IDDict, RADict, SBLDict, OADict, PADict, PNDict = self.importDataToPython()
        ifdefName = BibleOrganizationalSystemsConvertor.filenameBase.upper() + "_h"
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "// %s\n//\n" % ( filepath ) )
            myFile.write( "// This UTF-8 file was automatically generated by BibleOrganizationalSystemsConvertor.py V%s %s\n//\n" % ( versionString, datetime.now() ) )
            if self.title: myFile.write( "// %s\n" % ( self.title ) )
            if self.version: myFile.write( "//  Version: %s\n" % ( self.version ) )
            if self.date: myFile.write( "//  Date: %s\n//\n" % ( self.date ) )
            myFile.write( "//   %i %s loaded from the original XML file.\n//\n\n" % ( len(self.namesTree), BibleOrganizationalSystemsConvertor.treeTag ) )
            myFile.write( "#ifndef %s\n#define %s\n\n" % ( ifdefName, ifdefName ) )
            exportPythonDict( myFile, IDDict, "IDDict", "{int id; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "id (sorted), referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            exportPythonDict( myFile, RADict, "RADict", "{char* refAbbrev; int id; char* SBLAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "referenceAbbreviation (sorted), SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, SBLDict, "SBLDict", "{char* SBLAbbrev; int id; char* refAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "SBLAbbreviation (sorted), ReferenceAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, OADict, "OADict", "{char* OSISAbbrev; int id; char* refAbbrev; char* SBLAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "OSISAbbreviation (sorted), ReferenceAbbreviation, SBLAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, PADict, "PADict", "{char* PTAbbrev; int id; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* PTNum; char* EngName;}", "ParatextAbbreviation (sorted), referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, PNDict, "PNDict", "{char* PTNum; int id; char* PTAbbrev; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* EngName;}", "ParatextNumberString (sorted), ParatextAbbreviation, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, id, nameEnglish (comment only)" )
            myFile.write( "#endif // %s\n" % ( ifdefName ) )
    # end of exportDataToC

    def checkBibleditFile( self, nameDict, VSDict, folder, filename ):
        """
        Check a Bibledit versification file against all loaded versification systems
        """
        filepath = os.path.join( folder, filename+".xml" )
        print( "\nChecking %s..." % ( filepath ) )
        beTree = ElementTree().parse ( filepath )
        assert( beTree ) # Fail here if we didn't load anything at all

        # Load all of the Bibledit data
        BEData, BENames, BEChapters = OrderedDict(), {}, {}
        for element in beTree:
            if element.tag == "triad":
                bookName = element.find("book").text.upper()
                chapter = int( element.find("chapter").text )
                numVerses = int( element.find("verse").text )
                #print( bookName, chapter, numVerses )
                if bookName not in nameDict: # Try a more careful search
                    for name in nameDict:
                        if name.startswith(bookName):
                            if CommandLineOptions.debug: print( "Use '%s' instead of '%s'" % ( name, bookName ) )
                            nameDict[bookName] = nameDict[name] # Put it in there for next time
                            break
                if bookName not in nameDict: # Try a more careful search
                    for name in nameDict:
                        if name.endswith(bookName):
                            if CommandLineOptions.debug: print( "Use '%s' instead of '%s'" % ( name, bookName ) )
                            nameDict[bookName] = nameDict[name] # Put it in there for next time
                            break
                if bookName not in nameDict:
                    logging.error( "Unknown book name: %s" % ( bookName ) )
                    return False
                BBB = nameDict[bookName][1]
                if BBB not in BEData: BEData[BBB] = []
                BEData[BBB].append( (chapter, numVerses,) )
                if BBB not in BENames: BENames[BBB] = bookName
                BEChapters[BBB] = chapter

        # Check against the various loaded systems
        checkedVersificationSystemCodes, matchedVersificationSystemCodes = [], []
        systemMatchCount, systemMismatchCount, errors = 0, 0, ''
        for system in VSDict:
            errors = ""
            #print( system )
            bookMismatchCount, chapterMismatchCount, verseMismatchCount = 0, 0, 0
            versificationSystemCode, bookData = VSDict[system]
            if versificationSystemCode not in checkedVersificationSystemCodes:
                for BBB in BEData:
                    #print( BBB )
                    if BBB in bookData:
                        CVData = bookData[BBB]
                        for beChapter,beVerse in BEData[BBB]:
                            if beChapter in CVData:
                                if CVData[beChapter] != beVerse:
                                    errors += ("\n" if errors else "") + "    Doesn't match '%s' system at %s %s verse %s" % ( versificationSystemCode, BBB, beChapter,beVerse )
                                    verseMismatchCount += 1
                            else: # We don't have that chapter number
                                errors += ("\n" if errors else "") + "    Doesn't match '%s' system at %s chapter %s (%s verses)" % ( versificationSystemCode, BBB, beChapter,beVerse )
                                chapterMismatchCount += 1
                    else:
                        errors += ("\n" if errors else "") + "    Can't find '%s' bookcode in %s" % ( BBB, versificationSystemCode )
                        bookMismatchCount += 1
                if bookMismatchCount or chapterMismatchCount or verseMismatchCount:
                    errors += ("\n" if errors else "") + "    Doesn't match '%s' system (%i book mismatches, %i chapter mismatches, %i verse mismatches)" % ( versificationSystemCode, bookMismatchCount, chapterMismatchCount, verseMismatchCount )
                    systemMismatchCount += 1
                else:
                    #print( "  Matches '%s' system" % ( versificationSystemCode ) )
                    systemMatchCount += 1
                    matchedVersificationSystemCodes.append( versificationSystemCode )
                checkedVersificationSystemCodes.append( versificationSystemCode )
        if systemMatchCount:
            if systemMatchCount == 1: # What we hope for
                print( "  Matched %s (with these %i books)" % ( matchedVersificationSystemCodes[0], len(BEData) ) )
            else:
                print( "  Matched %i system(s): %s (with these %i books)" % ( systemMatchCount, matchedVersificationSystemCodes, len(BEData) ) )
        else:
            print( "  Mismatched %i systems (with these %i books)" % ( systemMismatchCount, len(BEData) ) )
            if CommandLineOptions.debug: print( errors )
        if not systemMatchCount: # Write a new file
            outputFilepath = os.path.join( "DerivedFiles", "BibleVersificationSystem_Bibledit_"+filename + ".xml" )
            print( "  Writing %s..." % ( outputFilepath ) )
            with open( outputFilepath, 'wt' ) as myFile:
                for i,BBB in enumerate(BEData):
                    myFile.write( "  <BibleBookVersification>\n" )
                    #myFile.write( "    <id>%i</id>\n" % ( i+1 ) )
                    myFile.write( "    <nameEnglish>%s</nameEnglish>\n" % ( BENames[BBB] ) )
                    myFile.write( "    <referenceAbbreviation>%s</referenceAbbreviation>\n" % ( BBB ) )
                    myFile.write( "    <numChapters>%i</numChapters>\n" % ( BEChapters[BBB] ) )
                    for c,v in BEData[BBB]:
                        myFile.write( '    <numVerses chapter="%i">%i</numVerses>\n' % ( c, v ) )
                    myFile.write( "  </BibleBookVersification>\n" )
                myFile.write( "\n</BibleVersificationSystem>" )
    # end of checkBibleditFile

    def checkSwordFile( self, nameDict, VSDict, folder, filename ):
        """
        Check a Sword versification file against all loaded versification systems
        """
        filepath = os.path.join( folder, filename+".h" )
        print( "\nChecking %s..." % ( filepath ) )
        status, lineCount, lastLine = 0, 0, ""
        chapterIndex, currentChapter, remainingChapters = {}, 0, 0
        SwData, SwNames, SwChapters = OrderedDict(), {}, {}
        with open( filepath, 'rt' ) as myFile:
            for line in myFile:
                lineCount += 1
                if lineCount==1 and line and line[0]==chr(65279): #U+FEFF
                    print( "      Detected UTF-16 Byte Order Marker" )
                    line = line[1:] # Remove the UTF-8 Byte Order Marker
                if line[-1]=='\n': line = line[:-1] # Removing trailing newline character
                if not line: continue # Just discard blank lines
                #print( status, line )
                lastLine = line
                if status == 0: # Getting started
                    if line.endswith("},"):
                        status = 1
                    elif line.startswith("  // "): # Must be no summary table
                        status = 2
                if status == 3: # Getting verse counts
                    if line.startswith("  // "):
                        status = 2
                    elif line == "};":
                        status = 4
                    else:
                        bits = line.split(",")
                        #print( bits )
                        for bit in bits:
                            bit = bit.strip()
                            if bit:
                                currentChapter += 1
                                if BBB in chapterIndex and currentChapter > chapterIndex[BBB]:
                                    logging.error( "Too many chapters (%i/%i) in %s" % ( currentChapter, chapterIndex[BBB], BBB ) )
                                    print( bits )
                                numVerses = int( bit )
                                SwData[BBB].append( (currentChapter, numVerses,) )
                                SwChapters[BBB] = currentChapter
                                remainingChapters -= 1
                                assert( remainingChapters >= 0 )
                if status == 2: # Get bookname for verse counts on following line(s)
                    if line.endswith("},"):
                        status = 1
                    if line.startswith("  // "):
                        if "---" in line: continue # Ignore comment line
                        bookName = line.replace("  // ", "").strip().replace("IV ","4 ").replace("III ","3 ").replace("II ","2 ").replace("I ","1 ").replace("Esther (Greek)","Greek Esther")
                        UCBookName = bookName.upper()
                        if UCBookName not in nameDict: # Try a more careful search
                            for name in nameDict:
                                if name.startswith(UCBookName):
                                    if CommandLineOptions.debug: print( "Use '%s' instead of '%s'" % ( name, bookName ) )
                                    nameDict[UCBookName] = nameDict[name] # Put it in there for next time
                                    break
                        if UCBookName not in nameDict: # Try a more careful search
                            for name in nameDict:
                                if name.endswith(UCBookName):
                                    if CommandLineOptions.debug: print( "Use '%s' instead of '%s'" % ( name, bookName ) )
                                    nameDict[UCBookName] = nameDict[name] # Put it in there for next time
                                    break
                        if UCBookName not in nameDict:
                            logging.error( "Unknown book name: %s" % ( bookName ) )
                            return False
                        BBB = nameDict[UCBookName][1]
                        if UCBookName in chapterIndex:
                            chapterIndex[BBB] = chapterIndex[UCBookName] # Duplicate for convenience
                            remainingChapters = chapterIndex[UCBookName]
                        else: # it seems to be a fault with some Sword canon files
                            logging.debug( "Bookname %s is missing from Sword header data" % ( bookName ) )
                            remainingChapters = 999
                        currentChapter = 0
                        SwData[BBB] = []
                        if BBB not in SwNames: SwNames[BBB] = bookName
                        status = 3
                if status == 1: # Getting chapter counts
                    if line.endswith("},"):
                        line = line.replace("  {","").replace("},","")
                        bits = line.split(",")
                        assert( len(bits) == 4 )
                        bookName = bits[0].strip().replace("IV ","4 ").replace("III ","3 ").replace("II ","2 ").replace("I ","1 ").replace("Esther (Greek)","Greek Esther")[1:-1] # Adjust, then remove beginning and ending double quotes
                        numChapters = bits[3].strip()
                        chapterIndex[bookName.upper()] = int( numChapters )
                    else:
                        #print( chapterIndex )
                        status = 2

        # Check against the various loaded systems
        checkedVersificationSystemCodes, matchedVersificationSystemCodes = [], []
        systemMatchCount, systemMismatchCount, errors, errorSummary = 0, 0, '', ''
        for system in VSDict:
            #print( system )
            bookMismatchCount, chapterMismatchCount, verseMismatchCount = 0, 0, 0
            versificationSystemCode, bookData = VSDict[system]
            if versificationSystemCode not in checkedVersificationSystemCodes:
                for BBB in SwData:
                    #print( BBB )
                    if BBB in bookData:
                        CVData = bookData[BBB]
                        for beChapter,beVerse in SwData[BBB]:
                            if beChapter in CVData:
                                if CVData[beChapter] != beVerse:
                                    errors += ("\n" if errors else "") + "    Doesn't match '%s' system at %s %s verse %s" % ( versificationSystemCode, BBB, beChapter,beVerse )
                                    verseMismatchCount += 1
                            else: # We don't have that chapter number
                                errors += ("\n" if errors else "") + "    Doesn't match '%s' system at %s chapter %s (%s verses)" % ( versificationSystemCode, BBB, beChapter,beVerse )
                                chapterMismatchCount += 1
                    else:
                        errors += ("\n" if errors else "") + "    Can't find '%s' bookcode in %s" % ( BBB, versificationSystemCode )
                        bookMismatchCount += 1
                if bookMismatchCount or chapterMismatchCount or verseMismatchCount:
                    thisError = "    Doesn't match '%s' system (%i book mismatches, %i chapter mismatches, %i verse mismatches)" % ( versificationSystemCode, bookMismatchCount, chapterMismatchCount, verseMismatchCount )
                    errors += ("\n" if errors else "") + thisError
                    errorSummary += ("\n" if errorSummary else "") + thisError
                    systemMismatchCount += 1
                else:
                    #print( "  Matches '%s' system" % ( versificationSystemCode ) )
                    systemMatchCount += 1
                    matchedVersificationSystemCodes.append( versificationSystemCode )
                checkedVersificationSystemCodes.append( versificationSystemCode )
        if systemMatchCount:
            if systemMatchCount == 1: # What we hope for
                print( "  Matched %s (with these %i books)" % ( matchedVersificationSystemCodes[0], len(SwData) ) )
            else:
                print( "  Matched %i system(s): %s (with these %i books)" % ( systemMatchCount, matchedVersificationSystemCodes, len(SwData) ) )
        else:
            print( "  Mismatched %i systems (with these %i books)" % ( systemMismatchCount, len(SwData) ) )
            if CommandLineOptions.debug: print( errors )
            else: print( errorSummary)
        if not systemMatchCount: # Write a new file
            outputFilepath = os.path.join( "DerivedFiles", "BibleVersificationSystem_Sword_"+filename + ".xml" )
            print( "  Writing %s..." % ( outputFilepath ) )
            with open( outputFilepath, 'wt' ) as myFile:
                for i,BBB in enumerate(SwData):
                    myFile.write( "  <BibleBookVersification>\n" )
                    #myFile.write( "    <id>%i</id>\n" % ( i+1 ) )
                    myFile.write( "    <nameEnglish>%s</nameEnglish>\n" % ( SwNames[BBB] ) )
                    myFile.write( "    <referenceAbbreviation>%s</referenceAbbreviation>\n" % ( BBB ) )
                    myFile.write( "    <numChapters>%i</numChapters>\n" % ( SwChapters[BBB] ) )
                    for c,v in SwData[BBB]:
                        myFile.write( '    <numVerses chapter="%i">%i</numVerses>\n' % ( c, v ) )
                    myFile.write( "  </BibleBookVersification>\n" )
                myFile.write( "\n</BibleVersificationSystem>" )
    # end of checkSwordFile

    def checkUSFMBible( self, nameDict, VSDict, name, folder ):
        """
        Check a USFM Bible versification file against all loaded versification systems
NOT WRITTEN YET
        """
        filepath = os.path.join( folder, filename+".xml" )
        print( "\nChecking %s..." % ( filepath ) )
        beTree = ElementTree().parse ( filepath )
        assert( beTree ) # Fail here if we didn't load anything at all

        # Load all of the Bibledit data
        BEData, BENames, BEChapters = OrderedDict(), {}, {}
        for element in beTree:
            if element.tag == "triad":
                book = element.find("book").text
                chapter = int( element.find("chapter").text )
                verse = int( element.find("verse").text )
                #print( book, chapter, verse )
                if book not in nameDict:
                    logging.error( "Unknown book name" )
                    return False
                BBB = nameDict[book][1]
                if BBB not in BEData: BEData[BBB] = []
                BEData[BBB].append( (chapter, verse,) )
                if BBB not in BENames: BENames[BBB] = book
                BEChapters[BBB] = chapter

        # Check against the various loaded systems
        checkedVersificationSystemCodes, matchedVersificationSystemCodes = [], []
        systemMatchCount, systemMismatchCount, errors = 0, 0, ''
        for system in VSDict:
            #print( system )
            bookMismatchCount, chapterMismatchCount, verseMismatchCount = 0, 0, 0
            intID, versificationSystemCode, bookData = VSDict[system]
            if versificationSystemCode not in checkedVersificationSystemCodes:
                for BBB in BEData:
                    #print( BBB )
                    if BBB in bookData:
                        CVData = bookData[BBB]
                        for beChapter,beVerse in BEData[BBB]:
                            if beChapter in CVData:
                                if CVData[beChapter] != beVerse:
                                    logging.warning( "Doesn't match '%s' system at %s %s verse %s" % ( versificationSystemCode, BBB, beChapter,beVerse ) )
                                    verseMismatchCount += 1
                            else: # We don't have that chapter number
                                logging.warning( "Doesn't match '%s' system at %s chapter %s (%s verses)" % ( versificationSystemCode, BBB, beChapter,beVerse ) )
                                chapterMismatchCount += 1
                    else:
                        #logging.warning( "Can't find '%s' bookcode in %s" % ( BBB, versificationSystemCode ) )
                        bookMismatchCount += 1
                if bookMismatchCount or chapterMismatchCount or verseMismatchCount:
                    #print( "    Doesn't match '%s' system (%i book mismatches, %i chapter mismatches, %i verse mismatches)" % ( versificationSystemCode, bookMismatchCount, chapterMismatchCount, verseMismatchCount ) )
                    systemMismatchCount += 1
                else:
                    #print( "  Matches '%s' system" % ( versificationSystemCode ) )
                    systemMatchCount += 1
                    matchedVersificationSystemCodes.append( versificationSystemCode )
                checkedVersificationSystemCodes.append( versificationSystemCode )
        if systemMatchCount:
            print( "  Matched %i system(s): %s" % ( systemMatchCount, matchedVersificationSystemCodes ) )
        else:
            print( "  Mismatched %i systems" % ( systemMismatchCount ) )
            if CommandLineOptions.debug: print( errors )
        if not systemMatchCount: # Write a new file
            outputFilepath = os.path.join( "DerivedFiles", "BibleVersificationSystem_Bibledit_"+filename + ".xml" )
            print( "Writing %s..." % ( outputFilepath ) )
            with open( outputFilepath, 'wt' ) as myFile:
                for i,BBB in enumerate(BEData):
                    myFile.write( "  <BibleBookVersification>\n" )
                    #myFile.write( "    <id>%i</id>\n" % ( i+1 ) )
                    myFile.write( "    <nameEnglish>%s</nameEnglish>\n" % ( BENames[BBB] ) )
                    myFile.write( "    <referenceAbbreviation>%s</referenceAbbreviation>\n" % ( BBB ) )
                    myFile.write( "    <numChapters>%i</numChapters>\n" % ( BEChapters[BBB] ) )
                    for c,v in BEData[BBB]:
                        myFile.write( '    <numVerses chapter="%i">%i</numVerses>\n' % ( c, v ) )
                    myFile.write( "  </BibleBookVersification>\n" )
                myFile.write( "\n</BibleVersificationSystem>" )
    # end of checkUSFMBible
# end of BibleOrganizationalSystemsConvertor class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    global CommandLineOptions
    parser = OptionParser( version="v%s" % ( versionString ) )
    #parser.add_option("-c", "--convert", action="store_true", dest="convert", default=False, help="convert the XML file to .py and .h tables suitable for directly including into other programs")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False, help="display extra debugging information")
    CommandLineOptions, args = parser.parse_args()


    # Do an initial load/check
    #bvs1 = BibleOrganizationalSystemsConvertor()
    #print( bvs1 )

    # Get the data tables that we need for proper checking
    bbc = BibleBooksCodes.BibleBooksCodesConvertor()
    junk, BBCRADict, junk, junk, junk, junk, junk, junk, BBCNameDict = bbc.importDataToPython()
    iso = iso_639_3.iso_639_3_Convertor()
    ISOIDDict, junk = iso.importDataToPython()

    # Do a proper load/check
    bvs = BibleOrganizationalSystemsConvertor( ISO639Dict=ISOIDDict, BibleBooksCodesDict=BBCRADict )
    #print( bvs )
    VersificationNameDict, VersificationCombinedDict = bvs.importDataToPython()

    # Adjust the name dict
    UC_BBCNameDict = {}
    for key, entry in BBCNameDict.items():
        UC_BBCNameDict[key.upper()] = entry

    # Check/Scrape the Bibledit versification systems
    BibleditFolder = "/mnt/Data/WebDevelopment/bibledit/gtk/templates/"
    if True:
        bvs.checkBibleditFile( UC_BBCNameDict, VersificationNameDict, BibleditFolder, "versification_original")
        bvs.checkBibleditFile( UC_BBCNameDict, VersificationNameDict, BibleditFolder, "versification_english")
        bvs.checkBibleditFile( UC_BBCNameDict, VersificationNameDict, BibleditFolder, "versification_septuagint")
        bvs.checkBibleditFile( UC_BBCNameDict, VersificationNameDict, BibleditFolder, "versification_vulgate")
        bvs.checkBibleditFile( UC_BBCNameDict, VersificationNameDict, BibleditFolder, "versification_spanish")
        bvs.checkBibleditFile( UC_BBCNameDict, VersificationNameDict, BibleditFolder, "versification_dutch_traditional")
        bvs.checkBibleditFile( UC_BBCNameDict, VersificationNameDict, BibleditFolder, "versification_russian_canonical")
        bvs.checkBibleditFile( UC_BBCNameDict, VersificationNameDict, BibleditFolder, "versification_russian_orthodox")
        bvs.checkBibleditFile( UC_BBCNameDict, VersificationNameDict, BibleditFolder, "versification_russian_protestant")
        bvs.checkBibleditFile( UC_BBCNameDict, VersificationNameDict, BibleditFolder, "versification_staten_bible")

    # Check/Scrape the Sword versification systems
    SwordFolder = "/mnt/Data/WebDevelopment/sword/include/"
    if True:
        bvs.checkSwordFile( UC_BBCNameDict, VersificationNameDict, SwordFolder, "canon")
        bvs.checkSwordFile( UC_BBCNameDict, VersificationNameDict, SwordFolder, "canon_mt")
        bvs.checkSwordFile( UC_BBCNameDict, VersificationNameDict, SwordFolder, "canon_leningrad")
        bvs.checkSwordFile( UC_BBCNameDict, VersificationNameDict, SwordFolder, "canon_synodal")
        bvs.checkSwordFile( UC_BBCNameDict, VersificationNameDict, SwordFolder, "canon_vulg")
        bvs.checkSwordFile( UC_BBCNameDict, VersificationNameDict, SwordFolder, "canon_luther")
        bvs.checkSwordFile( UC_BBCNameDict, VersificationNameDict, SwordFolder, "canon_kjva") # Seems to be missing NT summary data
        bvs.checkSwordFile( UC_BBCNameDict, VersificationNameDict, SwordFolder, "canon_nrsv") # Seems to be missing all summary data
        bvs.checkSwordFile( UC_BBCNameDict, VersificationNameDict, SwordFolder, "canon_nrsva") # Seems to be missing NT summary data
        bvs.checkSwordFile( UC_BBCNameDict, VersificationNameDict, SwordFolder, "canon_synodalp") # Seems to be missing all summary data
        bvs.checkSwordFile( UC_BBCNameDict, VersificationNameDict, SwordFolder, "canon_catholic") # Seems to be missing NT summary data
        bvs.checkSwordFile( UC_BBCNameDict, VersificationNameDict, SwordFolder, "canon_catholic2") # Seems to be missing NT summary data
        bvs.checkSwordFile( UC_BBCNameDict, VersificationNameDict, SwordFolder, "canon_german") # Seems to be missing NT summary data

    # Check/Scrape USFM versification systems
    if False:
        bvs.checkUSFMBible( UC_BBCNameDict, VersificationNameDict, "Matigsalug", "/mnt/Data/Matigsalug/Scripture/MBTV" )

    # Check/Scrape Sword versification systems

    # Check/Scrape eSword versification systems

    #bvs.exportDataToPython()
    #bvs.exportDataToC()
# end of main

if __name__ == '__main__':
    main()
# end of BibleOrganizationalSystems.py
