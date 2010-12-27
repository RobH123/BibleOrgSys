#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleVersificationSystems.py
#
# Module handling BibleVersificationSystem_*.xml to produce C and Python data tables
#   Last modified: 2010-12-27 (also update versionString below)
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
Module handling BibleVersificationSystem_*.xml to produce C and Python data tables.
"""

progName = "Bible Chapter/Verse Systems handler"
versionString = "0.33"


import os, logging
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree

from singleton import singleton
import Globals
from BibleBooksCodes import BibleBooksCodes


@singleton # Can only ever have one instance
class _BibleVersificationSystemsConvertor:
    """
    A class to handle data for Bible versification systems.
    """

    def __init__( self ):
        """
        Constructor.
        """
        self.filenameBase = "BibleVersificationSystems"

        # These fields are used for parsing the XML
        self.treeTag = "BibleVersificationSystem"
        self.headerTag = "header"
        self.mainElementTag = "BibleBookVersification"

        # These fields are used for automatically checking/validating the XML
        self.compulsoryAttributes = ()
        self.optionalAttributes = ( "omittedVerses", )
        self.uniqueAttributes = self.compulsoryAttributes + self.optionalAttributes
        self.compulsoryElements = ( "nameEnglish", "referenceAbbreviation", "numChapters", "numVerses" )
        self.optionalElements = ()
        self.uniqueElements = ( "nameEnglish", "referenceAbbreviation" ) + self.optionalElements

        # These are fields that we will fill later
        self.XMLSystems, self._DataDict = {}, {}

        # Make sure we have the bible books codes data loaded and available
        self.BibleBooksCodes = BibleBooksCodes().loadData()
    # end of __init__

    def loadSystems( self, folder=None ):
        """
        Load and pre-process the specified versification systems.
        """
        if not self.XMLSystems: # Only ever do this once
            if folder==None: folder = "DataFiles/VersificationSystems"
            if Globals.verbosityLevel > 2: print( "Loading versification systems from %s..." % ( folder ) )
            filenamePrefix = "BIBLEVERSIFICATIONSYSTEM_"
            for filename in os.listdir( folder ):
                filepart, extension = os.path.splitext( filename )
                if extension.upper() == '.XML' and filepart.upper().startswith(filenamePrefix):
                    versificationSystemCode = filepart[len(filenamePrefix):]
                    if Globals.verbosityLevel > 3: print( "Loading %s versification system from %s..." % ( versificationSystemCode, filename ) )
                    self.XMLSystems[versificationSystemCode] = {}
                    self.XMLSystems[versificationSystemCode]["tree"] = ElementTree().parse( os.path.join( folder, filename ) )
                    assert( self.XMLSystems[versificationSystemCode]["tree"] ) # Fail here if we didn't load anything at all

                    # Check and remove the header element
                    if self.XMLSystems[versificationSystemCode]["tree"].tag  == self.treeTag:
                        header = self.XMLSystems[versificationSystemCode]["tree"][0]
                        if header.tag == self.headerTag:
                            self.XMLSystems[versificationSystemCode]["header"] = header
                            self.XMLSystems[versificationSystemCode]["tree"].remove( header )
                            if len(header)>1:
                                logging.info( "Unexpected elements in header" )
                            elif len(header)==0:
                                logging.info( "Missing work element in header" )
                            else:
                                work = header[0]
                                if work.tag == "work":
                                    self.XMLSystems[versificationSystemCode]["version"] = work.find("version").text
                                    self.XMLSystems[versificationSystemCode]["date"] = work.find("date").text
                                    self.XMLSystems[versificationSystemCode]["title"] = work.find("title").text
                                else:
                                    logging.warning( "Missing work element in header" )
                        else:
                            logging.warning( "Missing header element (looking for '%s' tag)" % ( headerTag ) )
                    else:
                        logging.error( "Expected to load '%s' but got '%s'" % ( self.treeTag, self.XMLSystems[versificationSystemCode]["tree"].tag ) )
                    bookCount = 0 # There must be an easier way to do this
                    for subelement in self.XMLSystems[versificationSystemCode]["tree"]:
                        bookCount += 1
                    logging.info( "    Loaded %i books" % ( bookCount ) )

                    if Globals.strictCheckingFlag:
                        self._validateSystem( self.XMLSystems[versificationSystemCode]["tree"] )
        return self
    # end of loadSystems

    def _validateSystem( self, versificationTree ):
        """
        """
        assert( versificationTree )

        uniqueDict = {}
        for elementName in self.uniqueElements: uniqueDict["Element_"+elementName] = []
        for attributeName in self.uniqueAttributes: uniqueDict["Attribute_"+attributeName] = []

        expectedID = 1
        for k,element in enumerate(versificationTree):
            if element.tag == self.mainElementTag:
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
                ID = element.find("referenceAbbreviation").text
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

    def __str__( self ):
        """
        This method returns the string representation of a Bible versification system.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "_BibleVersificationSystemsConvertor object"
        #if self.title: result += ('\n' if result else '') + self.title
        #if self.version: result += ('\n' if result else '') + "Version: %s" % ( self.version )
        #if self.date: result += ('\n' if result else '') + "Date: %s" % ( self.date )
        result += ('\n' if result else '') + "  Num versification systems loaded = %i" % ( len(self.XMLSystems) )
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
                totalChapters, totalVerses, totalOmittedVerses = 0, 0, 0
                for bookElement in self.XMLSystems[x]["tree"]:
                    totalChapters += int( bookElement.find("numChapters").text )
                    for chapterElement in bookElement.findall("numVerses"):
                        totalVerses += int( chapterElement.text )
                        omittedVerses = chapterElement.get( "omittedVerses" )
                        if omittedVerses is not None:
                            totalOmittedVerses += len(omittedVerses.split(','))
                if totalChapters: result += ('\n' if result else '') + "      Total chapters = %i" % ( totalChapters )
                if totalVerses: result += ('\n' if result else '') + "      Total verses = %i" % ( totalVerses )
                if totalOmittedVerses: result += ('\n' if result else '') + "      Total omitted verses = %i" % ( totalOmittedVerses )
        return result
    # end of __str__

    def importDataToPython( self ):
        """
        Loads (and pivots) the data (not including the header) into suitable Python containers to use in a Python program.
        """
        assert( self.XMLSystems )
        if self._DataDict: # We've already done an import/restructuring -- no need to repeat it
            return self._DataDict

        # We'll create a number of dictionaries
        self._DataDict = {}
        for versificationSystemCode in self.XMLSystems.keys():
            #print( versificationSystemCode )
            # Make the data dictionary for this versification system
            chapterDataDict, omittedVersesDict = OrderedDict(), OrderedDict()
            for bookElement in self.XMLSystems[versificationSystemCode]["tree"]:
                BBB = bookElement.find("referenceAbbreviation").text
                #print( BBB )
                if not self.BibleBooksCodes.isValidReferenceAbbreviation( BBB ):
                    logging.error( "Unrecognized '%s' book abbreviation in '%s' versification system" % ( BBB, versificationSystemCode ) )
                numChapters = bookElement.find("numChapters").text # This is a string

                # Check the chapter data against the expected chapters in the BibleBooksCodes data
                if numChapters not in self.BibleBooksCodes.getExpectedChaptersList(BBB):
                    logging.info( "Expected number of chapters for %s is %s but we got '%s' for %s" % (BBB, self.BibleBooksCodes.getExpectedChaptersList(BBB), numChapters, versificationSystemCode ) )

                chapterData, omittedVersesData = OrderedDict(), []
                chapterData['numChapters'] = numChapters
                for chapterElement in bookElement.findall("numVerses"):
                    chapter = chapterElement.get("chapter")
                    numVerses = chapterElement.text
                    assert( chapter not in chapterData )
                    chapterData[chapter] = numVerses
                    omittedVerses = chapterElement.get( "omittedVerses" )
                    if omittedVerses is not None:
                        bits = omittedVerses.split(',')
                        for bit in bits:
                            omittedVersesData.append( (chapter, bit,) )
                # Save it by book reference abbreviation
                #assert( BBB not in bookData )
                #bookData[BBB] = (chapterData, omittedVersesData,)
                if BBB in chapterDataDict:
                    logging.error( "Duplicate %s in %s" % ( BBB, versificationSystemCode ) )
                chapterDataDict[BBB] = chapterData
                if BBB in omittedVersesDict:
                    logging.error( "Duplicate omitted data for %s in %s" % ( BBB, versificationSystemCode ) )
                omittedVersesDict[BBB] = omittedVersesData

            if Globals.strictCheckingFlag: # check for duplicates
                for checkSystemCode in self._DataDict:
                    checkChapterDataDict, checkOmittedVersesDict = self._DataDict[checkSystemCode]
                    if checkChapterDataDict==chapterDataDict:
                        if checkOmittedVersesDict==omittedVersesDict:
                            logging.error( "%s and %s versification systems are exactly identical" % ( versificationSystemCode, checkSystemCode ) )
                        else: # only the omitted verse lists differ
                            logging.warning( "%s and %s versification systems are mostly identical (omitted verse lists differ)" % ( versificationSystemCode, checkSystemCode ) )
                    else: # check if one is the subset of the other
                        BBBcombinedSet = set( checkChapterDataDict.keys() ) or set( chapterDataDict.keys() )
                        different, numCommon = False, 0
                        for BBB in BBBcombinedSet:
                            if BBB in checkChapterDataDict and BBB in chapterDataDict: # This book is in both
                                numCommon += 1
                                if checkChapterDataDict[BBB] != chapterDataDict[BBB]: different = True
                        if not different:
                            different2, numCommon2 = False, 0
                            for BBB in BBBcombinedSet:
                                if BBB in checkOmittedVersesDict and BBB in omittedVersesDict: # This book is in both
                                    numCommon2 += 1
                                    if checkOmittedVersesDict[BBB] != omittedVersesDict[BBB]: different2 = True
                            if not different2:
                                logging.warning( "The %i common books in %s (%i) and %s (%i) versification systems are exactly identical" % ( numCommon, versificationSystemCode, len(chapterDataDict), checkSystemCode, len(checkChapterDataDict) ) )
                            else: # only the omitted verse lists differ
                                logging.warning( "The %i common books in %s (%i) and %s (%i) versification systems are mostly identical (omitted verse lists differ)" % ( numCommon, versificationSystemCode, len(chapterDataDict), checkSystemCode, len(checkChapterDataDict) ) )


            # Now put it into my dictionaries for easy access
            self._DataDict[versificationSystemCode] = chapterDataDict, omittedVersesDict
        return self._DataDict
    # end of importDataToPython

    def exportDataToPython( self, filepath=None ):
        """
        Writes the information tables to a .py file that can be cut and pasted into a Python program.
        """
        def exportPythonDict( theFile, theDict, systemName, keyComment, fieldsComment ):
            """Exports theDict to theFile."""
            theFile.write( '  "%s": {\n    # Key is %s\n    # Fields are: %s\n' % ( systemName, keyComment, fieldsComment ) )
            for dictKey in theDict.keys():
                theFile.write( '    %s: %s,\n' % ( repr(dictKey), theDict[dictKey] ) )
            theFile.write( "  }, # end of %s (%i entries)\n\n" % ( systemName, len(theDict) ) )
        # end of exportPythonDict

        from datetime import datetime

        assert( self.XMLSystems )
        self.importDataToPython()
        assert( self._DataDict )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables.py" )
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( filepath ) )
        versificationSystemDict = self.importDataToPython()
        # Split into two dictionaries
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# %s\n#\n" % ( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by BibleVersificationSystems.py V%s %s\n#\n" % ( versionString, datetime.now() ) )
            #if self.title: myFile.write( "# %s\n" % ( self.title ) )
            #if self.version: myFile.write( "#  Version: %s\n" % ( self.version ) )
            #if self.date: myFile.write( "#  Date: %s\n#\n" % ( self.date ) )
            myFile.write( "#   %i %s loaded from the original XML files.\n#\n\n" % ( len(self.XMLSystems), self.treeTag ) )
            myFile.write( "from collections import OrderedDict\n\n" )
            myFile.write( "chapterVerseDict = {\n  # Key is versificationSystemName\n  # Fields are versificationSystem\n" )
            for systemName in versificationSystemDict:
                exportPythonDict( myFile, versificationSystemDict[systemName][0], systemName, "BBB referenceAbbreviation", "tuples containing (\"numChapters\", numChapters) then (chapterNumber, numVerses)" )
            myFile.write( "} # end of chapterVerseDict (%i systems)\n\n" % ( len(versificationSystemDict) ) )
            myFile.write( "omittedVersesDict = {\n  # Key is versificationSystemName\n  # Fields are omittedVersesSystem\n" )
            for systemName in versificationSystemDict:
                exportPythonDict( myFile, versificationSystemDict[systemName][1], systemName, "BBB referenceAbbreviation", "tuples containing (chapterNumber, omittedVerseNumber)" )
            myFile.write( "} # end of omittedVersesDict (%i systems)\n\n" % ( len(versificationSystemDict) ) )
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
        assert( self._DataDict )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables.json" )
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( filepath ) )
        with open( filepath, 'wt' ) as myFile:
            #myFile.write( "# %s\n#\n" % ( filepath ) ) # Not sure yet if these comment fields are allowed in JSON
            #myFile.write( "# This UTF-8 file was automatically generated by BibleVersificationSystems.py on %s\n#\n" % ( datetime.now() ) )
            #if self.titleString: myFile.write( "# %s data\n" % ( self.titleString ) )
            #if self.versionString: myFile.write( "#  Version: %s\n" % ( self.versionString ) )
            #if self.dateString: myFile.write( "#  Date: %s\n#\n" % ( self.dateString ) )
            #myFile.write( "#   %i %s loaded from the original XML file.\n#\n\n" % ( len(self.XMLtree), self.treeTag ) )
            json.dump( self._DataDict, myFile, indent=2 )
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
                        elif isinstance( field, tuple):
                            tupleResult = ""
                            for value in field:
                                if tupleResult: tupleResult += "," # Separate the fields (without a space)
                                tupleResult += convertEntry( value ) # recursive call
                            result += "{ %s }" % tupleResult
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

        def XXXexportPythonDict( theFile, theDict, dictName, structName, fieldsComment ):
            """Exports theDict to theFile."""
            def convertEntry( entry ):
                """Convert special characters in an entry..."""
                result = ""
                for field in entry if isinstance( entry, list) else entry.items():
                    #print( field )
                    if result: result += ", " # Separate the fields
                    if field is None: result += '""'
                    elif isinstance( field, str): result += '"' + str(field).replace('"','\\"') + '"'
                    elif isinstance( field, int): result += str(field)
                    elif isinstance( field, tuple):
                        tupleResult = ""
                        for tupleField in field:
                            #print( field, tupleField )
                            if tupleResult: tupleResult += "," # Separate the fields (without a space)
                            if tupleField is None: tupleResult += '""'
                            elif isinstance( tupleField, str): tupleResult += '"' + str(tupleField).replace('"','\\"') + '"'
                            elif isinstance( tupleField, int): tupleResult += str(tupleField)
                            else: logging.error( "Cannot convert unknown tuplefield type '%s' in entry '%s' for %s" % ( tupleField, entry, field ) )
                        result += tupleResult
                    else: logging.error( "Cannot convert unknown field type '%s' in entry '%s'" % ( field, entry ) )
                return result

            theFile.write( "static struct %s %s[%i] = {\n  // Fields are %s\n" % ( structName, dictName, len(theDict), fieldsComment ) )
            for dictKey in sorted(theDict.keys()):
                if isinstance( dictKey, str ):
                    #print( dictKey, theDict[dictKey] )
                    theFile.write( "  {\"%s\", %s},\n" % ( dictKey, convertEntry(theDict[dictKey]) ) )
                elif isinstance( dictKey, int ):
                    theFile.write( "  {%i, %s},\n" % ( dictKey, convertEntry(theDict[dictKey]) ) )
                else:
                    logging.error( "Can't handle this type of key data yet: %s" % ( dictKey ) )
            theFile.write( "}; // %s (%i entries)\n\n" % ( dictName, len(theDict) ) )
        # end of XXXexportPythonDict

        from datetime import datetime

        assert( self.XMLSystems )
        self.importDataToPython()
        assert( self._DataDict )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables" )
        hFilepath = filepath + '.h'
        cFilepath = filepath + '.c'
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( cFilepath ) ) # Don't bother telling them about the .h file
        ifdefName = self.filenameBase.upper() + "_Tables_h"

        with open( hFilepath, 'wt' ) as myHFile, open( cFilepath, 'wt' ) as myCFile:
            myHFile.write( "// %s\n//\n" % ( hFilepath ) )
            myCFile.write( "// %s\n//\n" % ( cFilepath ) )
            lines = "// This UTF-8 file was automatically generated by BibleVersificationSystems.py on %s\n//\n" % datetime.now()
            myHFile.write( lines ); myCFile.write( lines )
            myCFile.write( "//   %i %s loaded from the original XML file.\n//\n\n" % ( len(self.XMLSystems), self.treeTag ) )
            myHFile.write( "\n#ifndef %s\n#define %s\n\n" % ( ifdefName, ifdefName ) )
            myCFile.write( '#include "%s"\n\n' % os.path.basename(hFilepath) )

            # This needs to be thought out better :(
            # Need to put all CV data for all books into an array
            #  and then have another level that points into it
            #    BBB, numChapters, startIndex
            raise Exception( "Sorry, this c export isn't working yet :(" )

            CHAR = "const unsigned char"
            BYTE = "const int"
            N1 = "CVCount"
            N2 = "CVCounts"
            N3 = "CVOmitted"
            N4 = "CVOmits"
            S1 = "%s* chapterNumberString; %s* numVersesString;" % (CHAR,CHAR)
            S2 = "%s referenceAbbreviation[3+1]; %sEntry numVersesString[];" % (CHAR,N1)
            S3 = "%s* chapterNumberString; %s* verseNumberString;" % (CHAR,CHAR)
            S4 = "%s referenceAbbreviation[3+1]; %sEntry numVersesString[];" % (CHAR,N3)
            writeStructure( myHFile, N1, S1 )
            writeStructure( myHFile, N2, S2 )
            writeStructure( myHFile, N3, S4 )
            writeStructure( myHFile, N4, S4 )
            writeStructure( myHFile, "table", "%s* systemName; %sEntry* systemCVCounts; %sEntry* systemOmittedVerses;" % (CHAR,N2,N4) ) # I'm not sure if I need one or two asterisks on those last two
                                                                                                        # They're supposed to be pointers to an array of structures
            myHFile.write( "#endif // %s\n\n" % ( ifdefName ) )
            myHFile.write( "// end of %s" % os.path.basename(hFilepath) )

            #myHFile.write( "static struct {struct char*, void*, void*} versificationSystemNames[%i] = {\n  // Fields are systemName, systemVersification, systemOmittedVerses\n" % ( len(versificationSystemDict) ) )

            for systemName,systemInfo in self._DataDict.items(): # Now write out the actual data into the .c file
                myCFile.write( "\n// %s\n" % ( systemName ) )
                exportPythonDict( myCFile, systemInfo[0], systemName+"CVDict", N1+"Entry", "referenceAbbreviation", S1 )
                exportPythonDict( myCFile, systemInfo[1], systemName+"OmittedVersesDict", N2+"Entry", "indexNumber", S2 )

                break # Just do one for now
#            for systemName in self._DataDict: # Now write out the actual data into the .c file
#                print( systemName )
#                myCFile.write( '  { "%s", %s_versificationSystem, %s_omittedVerses },\n' % ( systemName, systemName, systemName ) )
#            myCFile.write( "}; // versificationSystemNames (%i entries)\n\n" % ( len(self._DataDict) ) )
#            for systemName in self._DataDict:
#                print( systemName )
#                myCFile.write( "#\n# %s\n" % ( systemName ) )
#                exportPythonDict( myCFile, self._DataDict[systemName][0], systemName+"_versificationSystem", "{struct char* stuff[]}", "tables containing referenceAbbreviation, (\"numChapters\", numChapters) then pairs of chapterNumber,numVerses" )
#                exportPythonDict( myCFile, self._DataDict[systemName][1], systemName+"_omittedVerses", "{struct char* stuff[]}", "tables containing referenceAbbreviation then pairs of chapterNumber,omittedVerseNumber" )
#                exportPythonDict( myCFile, self._DataDict[systemName][1], "omittedVersesDict", "{struct char* stuff[]}", "tables containing referenceAbbreviation then pairs of chapterNumber,omittedVerseNumber" )

            # Write out the final table of pointers to the above information
            myCFile.write( "\n// Pointers to above data\nconst static tableEntry bookOrderSystemTable[%i] = {\n" % len(self._DataDict) )
            for systemName in self._DataDict: # Now write out the actual pointer data into the .c file
                myCFile.write( '  { "%s", %s, %s },\n' % ( systemName, systemName+"CVDict", systemName+"OmittedVersesDict" ) )
            myCFile.write( "}; // %i entries\n\n" % len(self._DataDict) )
            myCFile.write( "// end of %s" % os.path.basename(cFilepath) )
    # end of exportDataToC

    def checkVersificationSystem( self, thisSystemName, versificationSchemeToCheck, omittedVersesToCheck=None, exportFlag=False, debugFlag=False ):
        """
        Check the given versification scheme against all the loaded systems.
        Create a new versification file if it doesn't match any.
        """
        assert( self._DataDict )
        assert( versificationSchemeToCheck )
        if omittedVersesToCheck is None: omittedVersesToCheck = {}

        matchedVersificationSystemCodes = []
        systemMatchCount, systemMismatchCount, allErrors, errorSummary = 0, 0, '', ''
        for versificationSystemCode in self._DataDict: # Step through the various reference schemes
            #print( system )
            bookMismatchCount, chapterMismatchCount, verseMismatchCount, omittedVerseMismatchCount, theseErrors = 0, 0, 0, 0, ''
            CVData, OVData = self._DataDict[versificationSystemCode]

            # Check verses per chapter
            for BBB in versificationSchemeToCheck.keys():
                #print( BBB )
                if BBB in CVData:
                    for chapterToCheck,numVersesToCheck in versificationSchemeToCheck[BBB]:
                        if not isinstance(chapterToCheck,str): logging.critical( "Chapter programming error" ); halt
                        if not isinstance(numVersesToCheck,str): logging.critical( "Verse programming error" ); halt
                        if chapterToCheck in CVData[BBB]: # That chapter number is in our scheme
                            if CVData[BBB][chapterToCheck] != numVersesToCheck:
                                theseErrors += ("\n" if theseErrors else "") + "    Doesn't match '%s' system at %s %s verse %s" % ( versificationSystemCode, BBB, chapterToCheck, numVersesToCheck )
                                verseMismatchCount += 1
                        else: # Our scheme doesn't have that chapter number
                            theseErrors += ("\n" if theseErrors else "") + "    Doesn't match '%s' system at %s chapter %s (%s verses)" % ( versificationSystemCode, BBB, chapterToCheck, numVersesToCheck )
                            chapterMismatchCount += 1
                else:
                    theseErrors += ("\n" if theseErrors else "") + "    Can't find %s bookcode in %s" % ( BBB, versificationSystemCode )
                    bookMismatchCount += 1

            # Check omitted verses
            for BBB in omittedVersesToCheck.keys():
                if BBB in OVData:
                    if OVData[BBB] == omittedVersesToCheck[BBB]: continue # Perfect match for this book
                    for cv in omittedVersesToCheck[BBB]:
                        if cv not in OVData[BBB]:
                            theseErrors += ("\n" if theseErrors else "") + "    %s:%s not omitted in %s reference versification for %s" % ( cv[0], cv[1], versificationSystemCode, BBB )
                            omittedVerseMismatchCount += 1
                    for cv in OVData[BBB]:
                        if cv not in omittedVersesToCheck[BBB]:
                            theseErrors += ("\n" if theseErrors else "") + "    %s:%s is omitted in %s reference versification for %s" % ( cv[0], cv[1], versificationSystemCode, BBB )
                            omittedVerseMismatchCount += 1
                else: # We don't match
                    theseErrors += ("\n" if theseErrors else "") + "    No omitted verses for %s in %s" % ( BBB, versificationSystemCode )
                    omittedVerseMismatchCount += len( omittedVersesToCheck[BBB] )

            if bookMismatchCount or chapterMismatchCount or verseMismatchCount or omittedVerseMismatchCount:
                if omittedVersesToCheck:
                    thisError = "    Doesn't match '%s' system (%i book mismatches, %i chapter mismatches, %i verse mismatches, %i omitted-verse mismatches)" % ( versificationSystemCode, bookMismatchCount, chapterMismatchCount, verseMismatchCount,omittedVerseMismatchCount )
                else:
                    thisError = "    Doesn't match '%s' system (%i book mismatches, %i chapter mismatches, %i verse mismatches)" % ( versificationSystemCode, bookMismatchCount, chapterMismatchCount, verseMismatchCount )
                theseErrors += ("\n" if theseErrors else "") + thisError
                errorSummary += ("\n" if errorSummary else "") + thisError
                systemMismatchCount += 1
            else:
                #print( "  Matches '%s' system" % ( versificationSystemCode ) )
                systemMatchCount += 1
                matchedVersificationSystemCodes.append( versificationSystemCode )
            if debugFlag and chapterMismatchCount==0 and 0<verseMismatchCount<8 and omittedVerseMismatchCount<10: print( theseErrors )
            allErrors += ("\n" if allErrors else "") + theseErrors

        if systemMatchCount:
            if systemMatchCount == 1: # What we hope for
                print( "  Matched %s versification (with these %i books)" % ( matchedVersificationSystemCodes[0], len(versificationSchemeToCheck) ) )
                if debugFlag: print( errorSummary )
            else:
                print( "  Matched %i versification system(s): %s (with these %i books)" % ( systemMatchCount, matchedVersificationSystemCodes, len(versificationSchemeToCheck) ) )
                if debugFlag: print( errorSummary )
        else:
            print( "  Mismatched %i versification systems (with these %i books)" % ( systemMismatchCount, len(versificationSchemeToCheck) ) )
            if debugFlag: print( allErrors )
            else: print( errorSummary)

        if exportFlag and not systemMatchCount: # Write a new file
            outputFilepath = os.path.join( "ScrapedFiles", "BibleVersificationSystem_"+thisSystemName + ".xml" )
            if Globals.verbosityLevel > 1: print( "Writing %i books to %s..." % ( len(versificationSchemeToCheck), outputFilepath ) )
            if omittedVersesToCheck:
                totalOmittedVerses = 0
                for BBB in omittedVersesToCheck.keys():
                    totalOmittedVerses += len( omittedVersesToCheck[BBB] )
                if Globals.verbosityLevel > 2: print( "  Have %i omitted verses for %i books" % ( totalOmittedVerses, len(omittedVersesToCheck) ) )
            with open( outputFilepath, 'wt' ) as myFile:
                for BBB in versificationSchemeToCheck:
                    myFile.write( "  <BibleBookVersification>\n" )
                    myFile.write( "    <nameEnglish>%s</nameEnglish>\n" % ( self.BibleBooksCodesDict[BBB][9] ) ) # the book name from the BibleBooksCodes.xml file
                    myFile.write( "    <referenceAbbreviation>%s</referenceAbbreviation>\n" % ( BBB ) )
                    myFile.write( "    <numChapters>%i</numChapters>\n" % ( len(versificationSchemeToCheck[BBB]) ) )
                    for c,numV in versificationSchemeToCheck[BBB]:
                        omittedVerseString = ''
                        if BBB in omittedVersesToCheck:
                            for oc,ov in omittedVersesToCheck[BBB]:
                                if oc == c: # It's this chapter
                                    omittedVerseString += (',' if omittedVerseString else '') + str(ov)
                        if omittedVerseString:
                            if Globals.verbosityLevel > 3 or Globals.debugFlag: print( '   ', BBB, c+':'+omittedVerseString )
                            myFile.write( '    <numVerses chapter="%s" omittedVerses="%s">%s</numVerses>\n' % ( c, omittedVerseString, numV ) )
                        else:
                            myFile.write( '    <numVerses chapter="%s">%s</numVerses>\n' % ( c, numV ) )
                    myFile.write( "  </BibleBookVersification>\n" )
                myFile.write( "\n</BibleVersificationSystem>" )
    # end of checkVersificationSystem
# end of _BibleVersificationSystemsConvertor class


@singleton # Can only ever have one instance
class BibleVersificationSystems:
    """
    Class for handling BibleVersificationSystems.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.

    Note: BBB is used in this class to represent the three-character referenceAbbreviation.
    """

    def __init__( self ): # We can't give this parameters because of the singleton
        """
        Constructor: 
        """
        self._bvsc = _BibleVersificationSystemsConvertor()
        self._DataDict = None # We'll import into this in loadData
    # end of __init__

    def loadData( self, folder=None ):
        """ Loads the XML data file and imports it to dictionary format (if not done already). """
        if not self._DataDict: # Don't do this unnecessarily
            if folder is not None: logging.warning( "Bible versification systems are already loaded -- your given folder of '%s' was ignored" % folder )
            self._bvsc.loadSystems( folder ) # Load the XML (if not done already)
            self._DataDict = self._bvsc.importDataToPython() # Get the various dictionaries organised for quick lookup
            del self._bvsc # Now the convertor class (that handles the XML) is no longer needed
        return self
    # end of loadData

    def __str__( self ):
        """
        This method returns the string representation of a Bible book order.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "BibleVersificationSystems object"
        for key in self._DataDict:
            assert( len(self._DataDict[key][0]) == len(self._DataDict[key][1]) )
        result += ('\n' if result else '') + "  Num systems = %i" % ( len(self._DataDict[key][0]) )
        return result
    # end of __str__

    def getAvailableSystemNames( self ):
        """ Returns a list of available system name strings. """
        return [x for x in self._DataDict]
    # end of getAvailableSystemNames

    def isValidSystemName( self, systemName ):
        """ Returns True or False. """
        return systemName in self._DataDict
    # end of isValidSystemName

    def getSystem( self, systemName ):
        """ Returns the dictionary for the requested system. """
        if systemName in self._DataDict:
            return self._DataDict[systemName]
        # else
        logging.error( "No '%s' system in Bible Book Orders" % systemName )
        if Globals.verbosityLevel > 2: logging.error( "Available systems are %s" % self.getAvailableSystemNames() )
    # end of getSystem
# end of BibleVersificationSystems class


class BibleVersificationSystem:
    """
    Class for handling a particular Bible versification system.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.
    """

    def __init__( self, systemName ):
        """
        Constructor: 
        """
        self._systemName = systemName
        self._bvss = BibleVersificationSystems().loadData() # Doesn't reload the XML unnecessarily :)
        self._ChapterDataDict, self._OmittedVersesDict = self._bvss.getSystem( self._systemName )
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible versification system.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "BibleVersificationSystem object"
        result += ('\n' if result else '') + "  %s Bible versification system" % ( self._systemName )
        #result += ('\n' if result else '') + "  Num values = %i" % ( len(self._Dict) )
        return result
    # end of __str__

    def getVersificationSystemName( self ):
        """ Return the book order system name. """
        return self._systemName
    # end of getSystemName

    def numAvailableBooks( self ):
        """ Returns the number of available books in the versification system.
            NOTE: This value is not useful for finding the number of books in a particular Bible. """
        return len( self._ChapterDataDict )
    # end of numAvailableBooks

    def getNumChapters( self, BBB ):
        """ Returns the number of chapters (int) in the given book. """
        return int( self._ChapterDataDict[BBB]['numChapters'] )
    # end of getNumChapters

    def getNumVerses( self, BBB, C ):
        """ Returns the number of verses (int) in the given book and chapter. """
        return int( self._ChapterDataDict[BBB][C] )
    # end of getNumVerses

    def getNumVersesList( self, BBB ):
        """ Returns a list containing an integer for each chapter indicating the number of verses. """
        myList = []
        for x in self._ChapterDataDict[BBB].keys():
            if x!='numChapters': myList.append( int( self._ChapterDataDict[BBB][x] ) )
        return myList
    # end of getNumVersesList

    def getOmittedVerseList( self, BBB, fullRefs=False ):
        """ Returns a list of (C,V) tuples noting omitted verses in the given book.

        If fullRefs are requested, the list consists of (BBB,C,V) tuples instead. """
        if fullRefs:
            return [(BBB,C,V) for (C,V) in self._OmittedVersesDict[BBB]]
        # else
        return self._OmittedVersesDict[BBB]
    # end of getOmittedVerseList

    def isOmittedVerse( self, BBB, C, V ):
        """ Returns True/False indicating if the given reference in omitted in this system. """
        return (C,V) in self._OmittedVersesDict[BBB]
    # end of isOmittedVerse
# end of BibleVersificationSystem class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v%s" % ( versionString ) )
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML files to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 1: print( "%s V%s" % ( progName, versionString ) )

    if Globals.commandLineOptions.export:
        bvsc = _BibleVersificationSystemsConvertor().loadSystems() # Load the XML
        bvsc.exportDataToPython() # Produce the .py tables
        bvsc.exportDataToJSON() # Produce a json output file
        bvsc.exportDataToC() # Produce the .h and .c tables

    else: # Must be demo mode
        # Demo the convertor object
        bvsc = _BibleVersificationSystemsConvertor().loadSystems() # Load the XML
        print( bvsc ) # Just print a summary

        # Demo the BibleVersificationSystems object
        bvss = BibleVersificationSystems().loadData() # Doesn't reload the XML unnecessarily :)
        print( bvss ) # Just print a summary
        print( "Available system names are: %s" % bvss.getAvailableSystemNames() )

        # Demo a BibleVersificationSystem object -- this is the one most likely to be wanted by a user
        bvs = BibleVersificationSystem( "NLT96" )
        if bvs is not None:
            print( bvs ) # Just print a summary
            print( "Num available books for %s is %i" % (bvs.getVersificationSystemName(),bvs.numAvailableBooks()) )
            BBB = 'PRO'
            print( "%s has %i chapters in %s" % (BBB,bvs.getNumChapters(BBB),bvs.getVersificationSystemName()) )
            BBB = 'MAT'; C='1'
            print( "%s %s has %i verses" % (BBB,C,bvs.getNumVerses(BBB,C)) )
            BBB = 'DAN'
            print( "Verse list for the %i chapters in %s is: %s" % (bvs.getNumChapters(BBB),BBB,bvs.getNumVersesList(BBB)) )
            BBB = 'MRK'; C='7'; V='16'
            print( "%s %s %s is omitted: %s" % (BBB,C,V,bvs.isOmittedVerse(BBB,C,V)) )
            print( "Omitted verses in %s are: %s" % (BBB,bvs.getOmittedVerseList(BBB)) )
# end of main

if __name__ == '__main__':
    main()
# end of BibleVersificationSystems.py
