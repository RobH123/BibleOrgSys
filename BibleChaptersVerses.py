#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleChaptersVerses.py
#
# Module handling BibleVersificationSystem_*.xml to produce C and Python data tables
#   Last modified: 2010-11-30 (also update versionString below)
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
versionString = "0.17"


import os, logging
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree
import BibleBooksCodes


class BibleVersificationSystemsConvertor:
    """
    A class to handle data for Bible versification systems.
    """
    filenameBase = "BibleVersificationSystems"
    treeTag = "BibleVersificationSystem"
    headerTag = "header"
    mainElementTag = "BibleBookVersification"
    compulsoryAttributes = ()
    optionalAttributes = ( "omittedVerses", )
    uniqueAttributes = compulsoryAttributes + optionalAttributes
    compulsoryElements = ( "nameEnglish", "referenceAbbreviation", "numChapters", "numVerses" )
    optionalElements = ()
    uniqueElements = ( "nameEnglish", "referenceAbbreviation" ) + optionalElements

    def __init__( self, BibleBooksCodesDict=None ):
        """
        Constructor.
        """
        self.BibleBooksCodesDict = BibleBooksCodesDict
        #self.title, self.version, self.date = None, None, None
        self.systems = {}
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible versification system.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = ""
        #if self.title: result += ('\n' if result else '') + self.title
        #if self.version: result += ('\n' if result else '') + "Version: %s" % ( self.version )
        #if self.date: result += ('\n' if result else '') + "Date: %s" % ( self.date )
        result += ('\n' if result else '') + "Num versification systems loaded = %i" % ( len(self.systems) )
        if 0: # Make it verbose
            for x in self.systems:
                result += ('\n' if result else '') + "  %s" % ( x )
                title = self.systems[x]["title"]
                if title: result += ('\n' if result else '') + "    %s" % ( title )
                version = self.systems[x]["version"]
                if version: result += ('\n' if result else '') + "    Version: %s" % ( version )
                date = self.systems[x]["date"]
                if date: result += ('\n' if result else '') + "    Last updated: %s" % ( date )
                result += ('\n' if result else '') + "    Num books = %i" % ( len(self.systems[x]["tree"]) )
                totalChapters, totalVerses, totalOmittedVerses = 0, 0, 0
                for bookElement in self.systems[x]["tree"]:
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

    def loadSystems( self, folder=None ):
        """
        Load and pre-process the specified versification systems.
        """

        if folder==None: folder = "DataFiles/VersificationSystems"
        for filename in os.listdir( folder ):
            filepart, extension = os.path.splitext( filename )
            if extension.upper() == '.XML' and filepart.upper().startswith("BIBLEVERSIFICATIONSYSTEM_"):
                versificationSystemCode = filepart[25:]
                #print( "Loading %s versification system from %s..." % ( versificationSystemCode, filename ) )
                self.systems[versificationSystemCode] = {}
                self.systems[versificationSystemCode]["tree"] = ElementTree().parse ( os.path.join( folder, filename ) )
                assert( self.systems[versificationSystemCode]["tree"] ) # Fail here if we didn't load anything at all

                # Check and remove the header element
                if self.systems[versificationSystemCode]["tree"].tag  == BibleVersificationSystemsConvertor.treeTag:
                    header = self.systems[versificationSystemCode]["tree"][0]
                    if header.tag == BibleVersificationSystemsConvertor.headerTag:
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
                    logging.error( "Expected to load '%s' but got '%s'" % ( BibleVersificationSystemsConvertor.treeTag, self.systems[versificationSystemCode]["tree"].tag ) )
                bookCount = 0 # There must be an easier way to do this
                for subelement in self.systems[versificationSystemCode]["tree"]:
                    bookCount += 1
                logging.info( "    Loaded %i books" % ( bookCount ) )

                self.validateSystem( self.systems[versificationSystemCode]["tree"] )
    # end of loadSystems

    def validateSystem( self, versificationTree ):
        """
        """
        assert( versificationTree )

        uniqueDict = {}
        for elementName in BibleVersificationSystemsConvertor.uniqueElements: uniqueDict["Element_"+elementName] = []
        for attributeName in BibleVersificationSystemsConvertor.uniqueAttributes: uniqueDict["Attribute_"+attributeName] = []

        expectedID = 1
        for k,element in enumerate(versificationTree):
            if element.tag == BibleVersificationSystemsConvertor.mainElementTag:
                # Check compulsory attributes on this main element
                for attributeName in BibleVersificationSystemsConvertor.compulsoryAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is None:
                        logging.error( "Compulsory '%s' attribute is missing from %s element in record %i" % ( attributeName, element.tag, k ) )
                    if not attributeValue:
                        logging.warning( "Compulsory '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, k ) )

                # Check optional attributes on this main element
                for attributeName in BibleVersificationSystemsConvertor.optionalAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if not attributeValue:
                            logging.warning( "Optional '%s' attribute is blank on %s element in record %i" % ( attributeName, element.tag, k ) )

                # Check for unexpected additional attributes on this main element
                for attributeName in element.keys():
                    attributeValue = element.get( attributeName )
                    if attributeName not in BibleVersificationSystemsConvertor.compulsoryAttributes and attributeName not in BibleVersificationSystemsConvertor.optionalAttributes:
                        logging.warning( "Additional '%s' attribute ('%s') found on %s element in record %i" % ( attributeName, attributeValue, element.tag, k ) )

                # Check the attributes that must contain unique information (in that particular field -- doesn't check across different attributes)
                for attributeName in BibleVersificationSystemsConvertor.uniqueAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if attributeValue in uniqueDict["Attribute_"+attributeName]:
                            logging.error( "Found '%s' data repeated in '%s' field on %s element in record %i" % ( attributeValue, attributeName, element.tag, k ) )
                        uniqueDict["Attribute_"+attributeName].append( attributeValue )

                # Check compulsory elements
                ID = element.find("referenceAbbreviation").text
                for elementName in BibleVersificationSystemsConvertor.compulsoryElements:
                    if element.find( elementName ) is None:
                        logging.error( "Compulsory '%s' element is missing in record with ID '%s' (record %i)" % ( elementName, ID, k ) )
                    if not element.find( elementName ).text:
                        logging.warning( "Compulsory '%s' element is blank in record with ID '%s' (record %i)" % ( elementName, ID, k ) )

                # Check optional elements
                for elementName in BibleVersificationSystemsConvertor.optionalElements:
                    if element.find( elementName ) is not None:
                        if not element.find( elementName ).text:
                            logging.warning( "Optional '%s' element is blank in record with ID '%s' (record %i)" % ( elementName, ID, k ) )

                # Check for unexpected additional elements
                for subelement in element:
                    if subelement.tag not in BibleVersificationSystemsConvertor.compulsoryElements and subelement.tag not in BibleVersificationSystemsConvertor.optionalElements:
                        logging.warning( "Additional '%s' element ('%s') found in record with ID '%s' (record %i)" % ( subelement.tag, subelement.text, ID, k ) )

                # Check the elements that must contain unique information (in that particular element -- doesn't check across different elements)
                for elementName in BibleVersificationSystemsConvertor.uniqueElements:
                    if element.find( elementName ) is not None:
                        text = element.find( elementName ).text
                        if text in uniqueDict["Element_"+elementName]:
                            logging.error( "Found '%s' data repeated in '%s' element in record with ID '%s' (record %i)" % ( text, elementName, ID, k ) )
                        uniqueDict["Element_"+elementName].append( text )
            else:
                logging.warning( "Unexpected element: %s in record %i" % ( element.tag, k ) )
    # end of validateSystem

    def importDataToPython( self ):
        """
        Loads (and pivots) the data (not including the header) into suitable Python containers to use in a Python program.
        """
        # We'll create a number of dictionaries
        myVersificationDict = {}
        for versificationSystemCode in self.systems.keys():
            #print( versificationSystemCode )
            # Make the data dictionary for this versification system
            chapterDataDict, omittedVersesDict = OrderedDict(), OrderedDict()
            for bookElement in self.systems[versificationSystemCode]["tree"]:
                sReferenceAbbreviation = bookElement.find("referenceAbbreviation").text
                #print( sReferenceAbbreviation )
                if self.BibleBooksCodesDict and sReferenceAbbreviation not in self.BibleBooksCodesDict:
                    logging.error( "Unrecognized '%s' book abbreviation in '%s' versification system" % ( sReferenceAbbreviation, versificationSystemCode ) )
                numChapters = bookElement.find("numChapters").text
                chapterData, omittedVersesData = OrderedDict(), []
                chapterData[''] = numChapters
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
                #assert( sReferenceAbbreviation not in bookData )
                #bookData[sReferenceAbbreviation] = (chapterData, omittedVersesData,)
                if sReferenceAbbreviation in chapterDataDict:
                    logging.error( "Duplicate %s in %s" % ( sReferenceAbbreviation, versificationSystemCode ) )
                chapterDataDict[sReferenceAbbreviation] = chapterData
                if sReferenceAbbreviation in omittedVersesDict:
                    logging.error( "Duplicate omitted data for %s in %s" % ( sReferenceAbbreviation, versificationSystemCode ) )
                omittedVersesDict[sReferenceAbbreviation] = omittedVersesData

            # Now put it into my dictionaries for easy access
            # This part should be customized or added to for however you need to process the data
            #   Add .upper() if you require the abbreviations to be uppercase (or .lower() for lower case)
            myVersificationDict[versificationSystemCode] = chapterDataDict, omittedVersesDict
        return myVersificationDict
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

        assert( self.systems )
        if not filepath: filepath = os.path.join( "DerivedFiles", BibleVersificationSystemsConvertor.filenameBase + "_Tables.py" )
        print( "Exporting to %s..." % ( filepath ) )

        versificationSystemDict = self.importDataToPython()
        # Split into two dictionaries
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# %s\n#\n" % ( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by BibleChaptersVerses.py V%s %s\n#\n" % ( versionString, datetime.now() ) )
            #if self.title: myFile.write( "# %s\n" % ( self.title ) )
            #if self.version: myFile.write( "#  Version: %s\n" % ( self.version ) )
            #if self.date: myFile.write( "#  Date: %s\n#\n" % ( self.date ) )
            myFile.write( "#   %i %s loaded from the original XML files.\n#\n\n" % ( len(self.systems), BibleVersificationSystemsConvertor.treeTag ) )
            myFile.write( "from collections import OrderedDict\n\n" )
            myFile.write( "chapterVerseDict = {\n  # Key is versificationSystemName\n  # Fields are versificationSystem\n" )
            for systemName in versificationSystemDict:
                exportPythonDict( myFile, versificationSystemDict[systemName][0], systemName, "BBB referenceAbbreviation", "tuples containing (emptyString, numChapters) then (chapterNumber, numVerses)" )
            myFile.write( "} # end of chapterVerseDict (%i systems)\n\n" % ( len(versificationSystemDict) ) )
            myFile.write( "omittedVersesDict = {\n  # Key is versificationSystemName\n  # Fields are omittedVersesSystem\n" )
            for systemName in versificationSystemDict:
                exportPythonDict( myFile, versificationSystemDict[systemName][1], systemName, "BBB referenceAbbreviation", "tuples containing (chapterNumber, omittedVerseNumber)" )
            myFile.write( "} # end of omittedVersesDict (%i systems)\n\n" % ( len(versificationSystemDict) ) )
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
                elif isinstance( entry, int ):
                    theFile.write( "  {%i, %s},\n" % ( dictKey, convertEntry(theDict[dictKey]) ) )
                else:
                    logging.error( "Can't handle this type of key data yet: %s" % ( dictKey ) )
            theFile.write( "}; // %s (%i entries)\n\n" % ( dictName, len(theDict) ) )
        # end of exportPythonDict

        from datetime import datetime

        assert( self.systems )
        if not filepath: filepath = os.path.join( "DerivedFiles", BibleVersificationSystemsConvertor.filenameBase + "_Tables.h" )
        print( "Exporting to %s..." % ( filepath ) )

        versificationSystemDict = self.importDataToPython()
        ifdefName = BibleVersificationSystemsConvertor.filenameBase.upper() + "_Tables_h"
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "// %s\n//\n" % ( filepath ) )
            myFile.write( "// This UTF-8 file was automatically generated by BibleVersificationSystemsConvertor.py V%s %s\n//\n" % ( versionString, datetime.now() ) )
            #if self.title: myFile.write( "// %s\n" % ( self.title ) )
            #if self.version: myFile.write( "//  Version: %s\n" % ( self.version ) )
            #if self.date: myFile.write( "//  Date: %s\n//\n" % ( self.date ) )
            myFile.write( "#   %i %s loaded from the original XML files.\n#\n\n" % ( len(self.systems), BibleVersificationSystemsConvertor.treeTag ) )
            myFile.write( "#ifndef %s\n#define %s\n\n" % ( ifdefName, ifdefName ) )
            myFile.write( "static struct {struct char*, void*, void*} versificationSystemNames[%i] = {\n  // Fields are systemName, systemVersification, systemOmittedVerses\n" % ( len(versificationSystemDict) ) )
            for systemName in versificationSystemDict:
                myFile.write( '  { "%s", %s_versificationSystem, %s_omittedVerses },\n' % ( systemName, systemName, systemName ) )
            myFile.write( "}; // versificationSystemNames (%i entries)\n\n" % ( len(versificationSystemDict) ) )
            for systemName in versificationSystemDict:
                myFile.write( "#\n# %s\n" % ( systemName ) )
                exportPythonDict( myFile, versificationSystemDict[systemName][0], systemName+"_versificationSystem", "{struct char* stuff[]}", "tables containing referenceAbbreviation, emptyString, numChapters) then pairs of chapterNumber,numVerses" )
                exportPythonDict( myFile, versificationSystemDict[systemName][1], systemName+"_omittedVerses", "{struct char* stuff[]}", "tables containing referenceAbbreviation then pairs of chapterNumber,omittedVerseNumber" )
                exportPythonDict( myFile, versificationSystemDict[systemName][1], "omittedVersesDict", "{struct char* stuff[]}", "tables containing referenceAbbreviation then pairs of chapterNumber,omittedVerseNumber" )
            myFile.write( "#endif // %s\n" % ( ifdefName ) )
    # end of exportDataToC

    def checkVersificationSystem( self, VSDict, thisSystemName, versificationSchemeToCheck, omittedVersesToCheck=None ):
        """
        Check the given versification scheme against all the loaded systems.
        Create a new versification file if it doesn't match any.
        """
        assert( VSDict )
        assert( versificationSchemeToCheck )
        if omittedVersesToCheck is None: omittedVersesToCheck = {}

        matchedVersificationSystemCodes = []
        systemMatchCount, systemMismatchCount, allErrors, errorSummary = 0, 0, '', ''
        for versificationSystemCode in VSDict: # Step through the various reference schemes
            #print( system )
            bookMismatchCount, chapterMismatchCount, verseMismatchCount, omittedVerseMismatchCount, theseErrors = 0, 0, 0, 0, ''
            CVData, OVData = VSDict[versificationSystemCode]

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
            if chapterMismatchCount==0 and 0<verseMismatchCount<8 and omittedVerseMismatchCount<10: print( theseErrors )
            allErrors += ("\n" if allErrors else "") + theseErrors
        if systemMatchCount:
            if systemMatchCount == 1: # What we hope for
                print( "  Matched %s (with these %i books)" % ( matchedVersificationSystemCodes[0], len(versificationSchemeToCheck) ) )
                if CommandLineOptions.debug: print( errorSummary )
            else:
                print( "  Matched %i system(s): %s (with these %i books)" % ( systemMatchCount, matchedVersificationSystemCodes, len(versificationSchemeToCheck) ) )
                if CommandLineOptions.debug: print( errorSummary )
        else:
            print( "  Mismatched %i systems (with these %i books)" % ( systemMismatchCount, len(versificationSchemeToCheck) ) )
            if CommandLineOptions.debug: print( allErrors )
            else: print( errorSummary)
        if not systemMatchCount: # Write a new file
            outputFilepath = os.path.join( "ScrapedFiles", "BibleVersificationSystem_"+thisSystemName + ".xml" )
            print( "Writing %i books to %s..." % ( len(versificationSchemeToCheck), outputFilepath ) )
            if omittedVersesToCheck:
                totalOmittedVerses = 0
                for BBB in omittedVersesToCheck.keys():
                    totalOmittedVerses += len( omittedVersesToCheck[BBB] )
                print( "  Have %i omitted verses for %i books" % ( totalOmittedVerses, len(omittedVersesToCheck) ) )
            with open( outputFilepath, 'wt' ) as myFile:
                for BBB in versificationSchemeToCheck:
                    myFile.write( "  <BibleBookVersification>\n" )
                    myFile.write( "    <nameEnglish>%s</nameEnglish>\n" % ( self.BibleBooksCodesDict[BBB][7] ) ) # the book name from the BibleBooksCodes.xml file
                    myFile.write( "    <referenceAbbreviation>%s</referenceAbbreviation>\n" % ( BBB ) )
                    myFile.write( "    <numChapters>%i</numChapters>\n" % ( len(versificationSchemeToCheck[BBB]) ) )
                    for c,numV in versificationSchemeToCheck[BBB]:
                        omittedVerseString = ''
                        if BBB in omittedVersesToCheck:
                            for oc,ov in omittedVersesToCheck[BBB]:
                                if oc == c: # It's this chapter
                                    omittedVerseString += (',' if omittedVerseString else '') + str(ov)
                        if omittedVerseString:
                            print( '   ', BBB, c+':'+omittedVerseString )
                            myFile.write( '    <numVerses chapter="%s" omittedVerses="%s">%s</numVerses>\n' % ( c, omittedVerseString, numV ) )
                        else:
                            myFile.write( '    <numVerses chapter="%s">%s</numVerses>\n' % ( c, numV ) )
                    myFile.write( "  </BibleBookVersification>\n" )
                myFile.write( "\n</BibleVersificationSystem>" )
    # end of checkVersificationSystem
# end of BibleVersificationSystemsConvertor class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    global CommandLineOptions
    parser = OptionParser( version="v%s" % ( versionString ) )
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML files to .py and .h tables suitable for directly including into other programs")
    parser.add_option("-d", "--debug", action="store_true", dest="debug", default=False, help="display extra debugging information")
    CommandLineOptions, args = parser.parse_args()


    # Get the data tables that we need for proper checking
    bbc = BibleBooksCodes.BibleBooksCodesConvertor()
    junk, BBCRADict, junk, junk, junk, junk, junk, junk, BBCNameDict = bbc.importDataToPython()

    # Adjust the name dict to upper case
    UC_BBCNameDict = {}
    for key, entry in BBCNameDict.items():
        UC_BBCNameDict[key.upper()] = entry

    # Do a proper load/check
    bcvs = BibleVersificationSystemsConvertor( BibleBooksCodesDict=BBCRADict )
    bcvs.loadSystems()
    VersificationNameDict = bcvs.importDataToPython()

    if CommandLineOptions.export:
        bcvs.exportDataToPython()
        bcvs.exportDataToC()
    else: # not exporting -- must just be a demo run
        print( bcvs )
# end of main

if __name__ == '__main__':
    main()
# end of BibleChaptersVerses.py
