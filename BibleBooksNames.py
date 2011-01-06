#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleBooksNames.py
#
# Module handling BibleBooksNamesSystem_*.xml to produce C and Python data tables
#   Last modified: 2011-01-06 (also update versionString below)
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
Module handling BibleBooksNamesSystem_*.xml to produce C and Python data tables.
"""

progName = "Bible Books Names Systems handler"
versionString = "0.24"


import os, logging
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree

from singleton import singleton
import Globals
from BibleBooksCodes import BibleBooksCodes
from ISO_639_3_Languages import ISO_639_3_Languages


@singleton # Can only ever have one instance
class _BibleBooksNamesSystemsConvertor:
    """
    A class to handle data for Bible booksNames systems.
    """

    def __init__( self ):
        """
        Constructor.
        """
        self.filenameBase = "BibleBooksNames"

        # These fields are used for parsing the XML
        self.treeTag = "BibleBooksNames"
        self.headerTag = "header"
        self.mainElementTags = ( "BibleDivisionNames", "BibleBooknameLeaders", "BibleBookNames" )

        # These fields are used for automatically checking/validating the XML
        self.compulsoryAttributes = { 0:(), 1:("standardLeader",), 2:("referenceAbbreviation",) }
        self.optionalAttributes = { 0:(), 1:(), 2:() }
        self.uniqueAttributes = {}
        for key in self.compulsoryAttributes.keys():
            self.uniqueAttributes[key] = self.compulsoryAttributes[key] + self.optionalAttributes[key]
        self.compulsoryElements = { 0:("defaultName","defaultAbbreviation","includesBook",), 1:("inputAbbreviation",), 2:("defaultName","defaultAbbreviation",) }
        self.optionalElements =  { 0:("inputAbbreviation",), 1:(), 2:("inputAbbreviation",) }
        self.uniqueElements = { 0:("defaultName","defaultAbbreviation","inputAbbreviation",), 1:("inputAbbreviation",), 2:("defaultName","defaultAbbreviation","inputAbbreviation",) }

        # These are fields that we will fill later
        self.XMLSystems, self.__BookNamesSystemsDict, self.__expandedInputSystems = {}, {}, {}

        # Get the data tables that we need for proper checking
        self.__BibleBooksCodes = BibleBooksCodes().loadData()
        self.__ISOLanguages = ISO_639_3_Languages().loadData() if Globals.strictCheckingFlag else None
    # end of __init__

    def loadSystems( self, folder=None ):
        """
        Load and pre-process the specified booksNames systems.
        """
        if not self.XMLSystems: # Only ever do this once
            if folder==None: folder = "DataFiles/BookNames"
            if Globals.verbosityLevel > 2: print( "Loading book names systems from %s..." % ( folder ) )
            for filename in os.listdir( folder ):
                filepart, extension = os.path.splitext( filename )
                if extension.upper() == '.XML' and filepart.upper().startswith(self.filenameBase.upper()+"_"):
                    booksNamesSystemCode = filepart[len(self.filenameBase)+1:]
                    if Globals.verbosityLevel > 3: print( "Loading %s books names system from %s..." % ( booksNamesSystemCode, filename ) )
                    self.XMLSystems[booksNamesSystemCode] = {}
                    self.XMLSystems[booksNamesSystemCode]["languageCode"] = booksNamesSystemCode.split('_',1)[0]
                    self.XMLSystems[booksNamesSystemCode]["tree"] = ElementTree().parse( os.path.join( folder, filename ) )
                    assert( self.XMLSystems[booksNamesSystemCode]["tree"] ) # Fail here if we didn't load anything at all

                    # Check and remove the header element
                    if self.XMLSystems[booksNamesSystemCode]["tree"].tag  == self.treeTag:
                        header = self.XMLSystems[booksNamesSystemCode]["tree"][0]
                        if header.tag == self.headerTag:
                            self.XMLSystems[booksNamesSystemCode]["header"] = header
                            self.XMLSystems[booksNamesSystemCode]["tree"].remove( header )
                            if len(header)>1:
                                logging.info( "Unexpected elements in header" )
                            elif len(header)==0:
                                logging.info( "Missing work element in header" )
                            else:
                                work = header[0]
                                if work.tag == "work":
                                    self.XMLSystems[booksNamesSystemCode]["version"] = work.find("version").text
                                    self.XMLSystems[booksNamesSystemCode]["date"] = work.find("date").text
                                    self.XMLSystems[booksNamesSystemCode]["title"] = work.find("title").text
                                else:
                                    logging.warning( "Missing work element in header" )
                        else:
                            logging.warning( "Missing header element (looking for '%s' tag)" % ( headerTag ) )
                    else:
                        logging.error( "Expected to load '%s' but got '%s'" % ( self.treeTag, self.XMLSystems[booksNamesSystemCode]["tree"].tag ) )
                    bookCount = 0 # There must be an easier way to do this
                    for subelement in self.XMLSystems[booksNamesSystemCode]["tree"]:
                        bookCount += 1
                    logging.info( "    Loaded %i books" % ( bookCount ) )

                    if Globals.strictCheckingFlag:
                        self.__validateSystem( booksNamesSystemCode )
        return self
    # end of loadSystems

    def __validateSystem( self, systemName ):
        """
        Checks for basic formatting/content errors in a Bible book name system.
        """
        assert( systemName )
        assert( self.XMLSystems[systemName]["tree"] )

        if len(self.XMLSystems[systemName]["languageCode"]) != 3:
            logging.error( "Couldn't find 3-letter language code in '%s' book names system" % ( systemName ) )
        if self.__ISOLanguages and not self.__ISOLanguages.isValidLanguageCode( self.XMLSystems[systemName]["languageCode"] ): # Check that we have a valid language code
            logging.error( "Unrecognized '%s' ISO-639-3 language code in '%s' book names system" % ( self.XMLSystems[systemName]["languageCode"], systemName ) )

        uniqueDict = {}
        for index in range( 0, len(self.mainElementTags) ):
            for elementName in self.uniqueElements[index]: uniqueDict["Element_"+str(index)+"_"+elementName] = []
            for attributeName in self.uniqueAttributes[index]: uniqueDict["Attribute_"+str(index)+"_"+attributeName] = []

        expectedID = 1
        for k,element in enumerate(self.XMLSystems[systemName]["tree"]):
            if element.tag in self.mainElementTags:
                index = self.mainElementTags.index( element.tag )

                # Check compulsory attributes on this main element
                for attributeName in self.compulsoryAttributes[index]:
                    attributeValue = element.get( attributeName )
                    if attributeValue is None:
                        logging.error( "Compulsory '%s' attribute is missing from %s element in record %i in %s" % ( attributeName, element.tag, k, systemName ) )
                    if not attributeValue:
                        logging.warning( "Compulsory '%s' attribute is blank on %s element in record %i in %s" % ( attributeName, element.tag, k, systemName ) )

                # Check optional attributes on this main element
                for attributeName in self.optionalAttributes[index]:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if not attributeValue:
                            logging.warning( "Optional '%s' attribute is blank on %s element in record %i in %s" % ( attributeName, element.tag, k, systemName ) )

                # Check for unexpected additional attributes on this main element
                for attributeName in element.keys():
                    attributeValue = element.get( attributeName )
                    if attributeName not in self.compulsoryAttributes[index] and attributeName not in self.optionalAttributes[index]:
                        logging.warning( "Additional '%s' attribute ('%s') found on %s element in record %i in %s" % ( attributeName, attributeValue, element.tag, k, systemName ) )

                # Check the attributes that must contain unique information (in that particular field -- doesn't check across different attributes)
                for attributeName in self.uniqueAttributes[index]:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if attributeValue in uniqueDict["Attribute_"+str(index)+"_"+attributeName]:
                            logging.error( "Found '%s' data repeated in '%s' field on %s element in record %i in %s" % ( attributeValue, attributeName, element.tag, k, systemName ) )
                        uniqueDict["Attribute_"+str(index)+"_"+attributeName].append( attributeValue )

                # Check compulsory elements
                for elementName in self.compulsoryElements[index]:
                    if element.find( elementName ) is None:
                        logging.error( "Compulsory '%s' element is missing (record %i) in %s" % ( elementName, k, systemName ) )
                    if not element.find( elementName ).text:
                        logging.warning( "Compulsory '%s' element is blank (record %i) in %s" % ( elementName, k, systemName ) )

                # Check optional elements
                for elementName in self.optionalElements[index]:
                    if element.find( elementName ) is not None:
                        if not element.find( elementName ).text:
                            logging.warning( "Optional '%s' element is blank (record %i) in %s" % ( elementName, k, systemName ) )

                # Check for unexpected additional elements
                for subelement in element:
                    if subelement.tag not in self.compulsoryElements[index] and subelement.tag not in self.optionalElements[index]:
                        logging.warning( "Additional '%s' element ('%s') found (record %i) in %s %s" % ( subelement.tag, subelement.text, k, systemName, element.tag ) )

                # Check the elements that must contain unique information (in that particular element -- doesn't check across different elements)
                for elementName in self.uniqueElements[index]:
                    if element.find( elementName ) is not None:
                        text = element.find( elementName ).text
                        if text in uniqueDict["Element_"+str(index)+"_"+elementName]:
                            myLogging = logging.info if element.tag == 'BibleDivisionNames' else logging.error
                            myLogging( "Found '%s' data repeated in '%s' element (record %i) in %s" % ( text, elementName, k, systemName ) )
                        uniqueDict["Element_"+str(index)+"_"+elementName].append( text )
            else:
                logging.warning( "Unexpected element: %s in record %i in %s" % ( element.tag, k, systemName ) )
    # end of __validateSystem

    def __str__( self ):
        """
        This method returns the string representation of a Bible booksNames system.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "_BibleBooksNamesSystemsConvertor object"
        result += ('\n' if result else '') + "  Num bookname systems loaded = %i" % ( len(self.XMLSystems) )
        if Globals.verbosityLevel > 2: # Make it verbose
            for x in self.XMLSystems:
                result += ('\n' if result else '') + "  %s" % ( x )
                if self.__ISOLanguages and self.XMLSystems[x]["languageCode"] and self.__ISOLanguages.isValidLanguageCode( self.XMLSystems[x]["languageCode"] ):
                    result += ('\n' if result else '') + "    Language code %s = %s" % ( self.XMLSystems[x]["languageCode"], self.__ISOLanguages.getLanguageName( self.XMLSystems[x]["languageCode"]) )
                title = self.XMLSystems[x]["title"]
                if title: result += ('\n' if result else '') + "    %s" % ( title )
                version = self.XMLSystems[x]["version"]
                if version: result += ('\n' if result else '') + "    Version: %s" % ( version )
                date = self.XMLSystems[x]["date"]
                if date: result += ('\n' if result else '') + "    Last updated: %s" % ( date )
                result += ('\n' if result else '') + "    Num entries = %i" % ( len(self.XMLSystems[x]["tree"]) )
                numDivisions, numLeaders, numBooks = 0, 0, 0
                for element in self.XMLSystems[x]["tree"]:
                    if element.tag == "BibleDivisionNames":
                        numDivisions += 1
                    elif element.tag == "BibleBooknameLeaders":
                        numLeaders += 1
                    elif element.tag == "BibleBookNames":
                        numBooks += 1
                if numDivisions: result += ('\n' if result else '') + "      Num divisions = %i" % ( numDivisions )
                if numLeaders: result += ('\n' if result else '') + "      Num bookname leaders = %i" % ( numLeaders )
                if numBooks: result += ('\n' if result else '') + "      Num books = %i" % ( numBooks )
        return result
    # end of __str__

    def expandInputs ( self, bookList ):
        """
        This is a helper function to expand the inputAbbreviation fields to include all unambiguous shorter abbreviations.

        It is best to do this for a specific publication since there will be less ambiguities if there are less actual books included.
        This routine is only really included here as a demo -- it's much better to call expandBibleNamesInputs
            when the actual list of books for your publication is already known.

        Saves divisions name and book name ordered dictionaries, all UPPER CASE, sorted with longest first.
        """
        assert( bookList )
        assert( self.XMLSystems )
        self.importDataToPython()
        assert( self.__BookNamesSystemsDict )
        if self.__expandedInputSystems: return # No need to do this again

        if Globals.verbosityLevel > 1: print( "Expanding input abbreviations..." )
        for systemName in self.__BookNamesSystemsDict:
            if Globals.verbosityLevel > 2: print( "  Expanding %s..." % ( systemName ) )
            divisionsNamesList, booknameLeadersDict, bookNamesDict = self.__BookNamesSystemsDict[systemName]
            self.__expandedInputSystems[systemName] = expandBibleNamesInputs( systemName, divisionsNamesList, booknameLeadersDict, bookNamesDict, bookList )
    # end of expandInputs

    def importDataToPython( self ):
        """
        Loads (and pivots) the data (not including the header) into suitable Python containers to use in a Python program.

        If necessary (but not actually recommended), expandInputs should be called before this to fill self.__expandedInputSystems.

        Returns two dictionaries which should each contain entries for each named system.
        """
        assert( self.XMLSystems )
        if self.__BookNamesSystemsDict: # We've already done an import/restructuring -- no need to repeat it
            return self.__BookNamesSystemsDict, self.__expandedInputSystems

        # We'll create a number of dictionaries
        if Globals.verbosityLevel > 3: print( "Importing data into Python dictionary..." )
        self.__BookNamesSystemsDict = {}
        for booksNamesSystemCode in self.XMLSystems.keys():
            #print( booksNamesSystemCode )
            # Make the data dictionary for this booksNames system
            myDivisionsNamesList, myBooknameLeadersDict, myBookNamesDict = [], {}, {}
            for element in self.XMLSystems[booksNamesSystemCode]["tree"]:
                if element.tag == "BibleDivisionNames":
                    defaultName = element.find("defaultName").text
                    defaultAbbreviation = element.find("defaultAbbreviation").text
                    inputFields = [ defaultName ]
                    if not defaultName.startswith( defaultAbbreviation ):
                        inputFields.append( defaultAbbreviation )
                    for subelement in element.findall("inputAbbreviation"):
                        if subelement.text in inputFields:
                            logging.warning( "Superfluous '%s' entry in inputAbbreviation field for %s division in '%s' booksNames system" % ( subelement.text, defaultName, booksNamesSystemCode ) )
                        else: inputFields.append( subelement.text )
                    includedBooks = []
                    for subelement in element.findall("includesBook"):
                        BBB = subelement.text
                        if not self.__BibleBooksCodes.isValidReferenceAbbreviation( BBB ):
                            logging.error( "Unrecognized '%s' book abbreviation in BibleDivisionNames in '%s' booksNames system" % ( BBB, booksNamesSystemCode ) )
                        if BBB in includedBooks:
                            logging.error( "Duplicate '%s' entry in includesBook field for '%s' division in '%s' booksNames system" % ( subelement.text, defaultName, booksNamesSystemCode ) )
                        else: includedBooks.append( BBB )
                    myDivisionsNamesList.append( {"includedBooks":includedBooks, "defaultName":defaultName, "defaultAbbreviation":defaultAbbreviation, "inputFields":inputFields } )
                elif element.tag == "BibleBooknameLeaders":
                    standardLeader = element.get("standardLeader")
                    inputFields = [] # Don't include the standard leader here
                    for subelement in element.findall("inputAbbreviation"):
                        adjField = subelement.text + ' '
                        if adjField in inputFields:
                            logging.error( "Duplicate '%s' entry in inputAbbreviation field for '%s' bookname leaders in '%s' booksNames system" % ( subelement.text, standardLeader, booksNamesSystemCode ) )
                        else: inputFields.append( adjField )
                    myBooknameLeadersDict[standardLeader+' '] = inputFields
                elif element.tag == "BibleBookNames":
                    referenceAbbreviation = element.get("referenceAbbreviation")
                    if not self.__BibleBooksCodes.isValidReferenceAbbreviation( referenceAbbreviation ):
                        logging.error( "Unrecognized '%s' book abbreviation in BibleBookNames in '%s' booksNames system" % ( referenceAbbreviation, booksNamesSystemCode ) )
                    defaultName = element.find("defaultName").text
                    defaultAbbreviation = element.find("defaultAbbreviation").text
                    inputFields = [ defaultName ] # Add the default name to the allowed input fields
                    if not defaultAbbreviation == defaultName: inputFields.append( defaultAbbreviation ) # Automatically add the default abbreviation if it's different
                    for subelement in element.findall("inputAbbreviation"):
                        if subelement.text in inputFields:
                            logging.info( "Superfluous '%s' entry in inputAbbreviation field for %s book in '%s' booksNames system" % ( subelement.text, defaultName, booksNamesSystemCode ) )
                        else: inputFields.append( subelement.text )
                    myBookNamesDict[referenceAbbreviation] = { "defaultName":defaultName, "defaultAbbreviation":defaultAbbreviation, "inputFields":inputFields }

            if Globals.strictCheckingFlag: # check for duplicates
                for checkSystemCode in self.__BookNamesSystemsDict:
                    checkDivisionsNamesList, checkBooknameLeadersDict, checkBookNamesDict = self.__BookNamesSystemsDict[checkSystemCode]
                    if checkDivisionsNamesList==myDivisionsNamesList and checkBookNamesDict==myBookNamesDict:
                        if checkBooknameLeadersDict == myBooknameLeadersDict:
                            logging.error( "%s and %s book name systems are exactly identical (%i divisions, %i book names, %i leaders)" % ( booksNamesSystemCode, checkSystemCode, len(myDivisionsNamesList), len(myBookNamesDict), len(myBooknameLeadersDict) ) )
                        else: # only the leaders are different
                            logging.error( "%s and %s book name systems are mostly identical (%i divisions, %i book names)" % ( booksNamesSystemCode, checkSystemCode, len(myDivisionsNamesList), len(myBookNamesDict) ) )

            # Now put it into my dictionary for easy access
            self.__BookNamesSystemsDict[booksNamesSystemCode] = myDivisionsNamesList, myBooknameLeadersDict, myBookNamesDict
        return self.__BookNamesSystemsDict, self.__expandedInputSystems
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

        def exportPythonOrderedDict( theFile, theDict, dictName, keyComment, fieldsComment ):
            """Exports theDict to theFile."""
            theFile.write( '  "%s": OrderedDict([\n    # Key is %s\n    # Fields are: %s\n' % ( dictName, keyComment, fieldsComment ) )
            for dictKey in theDict.keys():
                theFile.write( '    (%s, %s),\n' % ( repr(dictKey), repr(theDict[dictKey]) ) )
            theFile.write( "  ]), # end of %s (%i entries)\n\n" % ( dictName, len(theDict) ) )
        # end of exportPythonDict

        def exportPythonList( theFile, theList, listName, fieldsComment ):
            """Exports theList to theFile."""
            theFile.write( '  "%s": [\n    # Fields are: %s\n' % ( listName, fieldsComment ) )
            for j,entry in enumerate(theList):
                theFile.write( '    %s, # %i\n' % ( repr(entry), j ) )
            theFile.write( "  ], # end of %s (%i entries)\n\n" % ( listName, len(theList) ) )
        # end of exportPythonList

        from datetime import datetime

        assert( self.XMLSystems )
        self.importDataToPython()
        assert( self.__BookNamesSystemsDict )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables.py" )
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( filepath ) )
        # Split into three lists/dictionaries
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# %s\n#\n" % ( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by BibleBooksNames.py V%s %s\n#\n" % ( versionString, datetime.now() ) )
            #if self.title: myFile.write( "# %s\n" % ( self.title ) )
            #if self.version: myFile.write( "#  Version: %s\n" % ( self.version ) )
            #if self.date: myFile.write( "#  Date: %s\n#\n" % ( self.date ) )
            #myFile.write( "#   %i %s entries loaded from the original XML file.\n" % ( len(self.namesTree), self.treeTag ) )
            myFile.write( "#   %i %s loaded from the original XML files.\n#\n\n" % ( len(self.XMLSystems), self.treeTag ) )
            myFile.write( "from collections import OrderedDict\n\n" )
            myFile.write( "\ndivisionNamesList = {\n  # Key is languageCode\n  # Fields are divisionNames\n\n" )
            for systemName in self.__BookNamesSystemsDict:
                divisionsNamesList, booknameLeadersDict, bookNamesDict = self.__BookNamesSystemsDict[systemName]
                exportPythonList( myFile, divisionsNamesList, systemName, "startsWith( string), defaultName (string), defaultAbbreviation (string), inputFields (list of strings) all in a dictionary" )
            myFile.write( "} # end of divisionNamesList (%i systems)\n\n\n" % ( len(self.__BookNamesSystemsDict) ) )
            myFile.write( "\nbooknameLeadersDict = {\n  # Key is languageCode\n  # Fields are divisionNames\n\n" )
            for systemName in self.__BookNamesSystemsDict:
                divisionsNamesList, booknameLeadersDict, bookNamesDict = self.__BookNamesSystemsDict[systemName]
                exportPythonDict( myFile, booknameLeadersDict, systemName, "standardLeader (all fields include a trailing space)", "inputAlternatives (list of strings)" )
            myFile.write( "} # end of booknameLeadersDict (%i systems)\n\n\n" % ( len(self.__BookNamesSystemsDict) ) )
            myFile.write( "\nbookNamesDict = {\n  # Key is languageCode\n  # Fields are divisionNames\n\n" )
            for systemName in self.__BookNamesSystemsDict:
                divisionsNamesList, booknameLeadersDict, bookNamesDict = self.__BookNamesSystemsDict[systemName]
                exportPythonDict( myFile, bookNamesDict, systemName, "referenceAbbreviation", "defaultName (string), defaultAbbreviation (string), inputAbbreviations (list of strings) all in a dictionary" )
            myFile.write( "} # end of bookNamesDict (%i systems)\n\n\n" % ( len(self.__BookNamesSystemsDict) ) )
            if self.__expandedInputSystems:
                myFile.write( "\ndivisionsNamesInputDict = {\n  # Key is languageCode\n  # Fields are divisionNames\n\n" )
                for systemName in self.__BookNamesSystemsDict:
                    if systemName in self.__expandedInputSystems:
                        divisionsNamesInputDict, bookNamesInputDict = self.__expandedInputSystems[systemName]
                        exportPythonOrderedDict( myFile, divisionsNamesInputDict, "divisionsNamesInputDict", "UpperCaseInputString (sorted with longest first)", "index (into divisionNamesList above)" )
                myFile.write( "} # end of divisionsNamesInputDict (%i systems)\n\n\n" % ( len(self.__BookNamesSystemsDict) ) )
                myFile.write( "\nbookNamesInputDict = {\n  # Key is languageCode\n  # Fields are divisionNames\n\n" )
                for systemName in self.__BookNamesSystemsDict:
                    if systemName in self.__expandedInputSystems:
                        divisionsNamesInputDict, bookNamesInputDict = self.__expandedInputSystems[systemName]
                        exportPythonOrderedDict( myFile, bookNamesInputDict, "bookNamesInputDict", "UpperCaseInputString (sorted with longest first)", "referenceAbbreviation (string)" )
                myFile.write( "} # end of bookNamesInputDict (%i systems)\n" % ( len(self.__BookNamesSystemsDict) ) )
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
        assert( self.__BookNamesSystemsDict )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables.json" )
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( filepath ) )
        with open( filepath, 'wt' ) as myFile:
            #myFile.write( "# %s\n#\n" % ( filepath ) ) # Not sure yet if these comment fields are allowed in JSON
            #myFile.write( "# This UTF-8 file was automatically generated by BibleBooksCodes.py on %s\n#\n" % ( datetime.now() ) )
            #if self.titleString: myFile.write( "# %s data\n" % ( self.titleString ) )
            #if self.versionString: myFile.write( "#  Version: %s\n" % ( self.versionString ) )
            #if self.dateString: myFile.write( "#  Date: %s\n#\n" % ( self.dateString ) )
            #myFile.write( "#   %i %s loaded from the original XML file.\n#\n\n" % ( len(self.XMLtree), self.treeTag ) )
            json.dump( self.__BookNamesSystemsDict, myFile, indent=2 )
            #myFile.write( "\n\n# end of %s" % os.path.basename(filepath) )
    # end of exportDataToJSON

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

        assert( self.XMLSystems )
        self.importDataToPython()
        assert( self.__BookNamesSystemsDict )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables.h" )
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( filepath ) )
        raise Exception( "C export not written yet -- sorry." )

        ifdefName = self.filenameBase.upper() + "_Tables_h"
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "// %s\n//\n" % ( filepath ) )
            myFile.write( "// This UTF-8 file was automatically generated by BibleBooksNames.py V%s %s\n//\n" % ( versionString, datetime.now() ) )
            if self.title: myFile.write( "// %s\n" % ( self.title ) )
            if self.version: myFile.write( "//  Version: %s\n" % ( self.version ) )
            if self.date: myFile.write( "//  Date: %s\n//\n" % ( self.date ) )
            myFile.write( "//   %i %s loaded from the original XML file.\n//\n\n" % ( len(self.namesTree), self.treeTag ) )
            myFile.write( "#ifndef %s\n#define %s\n\n" % ( ifdefName, ifdefName ) )
            exportPythonDict( myFile, IDDict, "IDDict", "{int id; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "id (sorted), referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            exportPythonDict( myFile, RADict, "RADict", "{char* refAbbrev; int id; char* SBLAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "referenceAbbreviation (sorted), SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, SBLDict, "SBLDict", "{char* SBLAbbrev; int id; char* refAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "SBLAbbreviation (sorted), ReferenceAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, OADict, "OADict", "{char* OSISAbbrev; int id; char* refAbbrev; char* SBLAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "OSISAbbreviation (sorted), ReferenceAbbreviation, SBLAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, PADict, "PADict", "{char* PTAbbrev; int id; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* PTNum; char* EngName;}", "ParatextAbbreviation (sorted), referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, PNDict, "PNDict", "{char* PTNum; int id; char* PTAbbrev; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* EngName;}", "ParatextNumberString (sorted), ParatextAbbreviation, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, id, nameEnglish (comment only)" )
            myFile.write( "#endif // %s\n" % ( ifdefName ) )
    # end of exportDataToC
# end of _BibleBooksNamesSystemsConvertor class


def expandBibleNamesInputs ( systemName, divisionsNamesList, booknameLeadersDict, bookNamesDict, bookList ):
    """
    This is a helper function to expand the inputAbbreviation fields to include all unambiguous shorter abbreviations.

    It is best to do this for a specific publication since there will be less ambiguities if there are less actual books included.

    Returns divisions name and book name ordered dictionaries, all UPPER CASE, sorted with longest first.
    """

    def expandAbbrevs( UCString, value, originalDict, tempDict, theAmbigSet ):
        """
        Progressively remove characters off the end of the (UPPER CASE) UCString, plus also remove internal spaces.
            trying to find unambiguous shortcuts which the user could use.
        """
        # Drop off final letters and remove internal spaces
        tempString = UCString[:-1] # Drop off the last letter
        while( tempString ):
            if tempString[-1] != ' ':
                if tempString in originalDict:
                    if originalDict[tempString] == value:
                        if Globals.verbosityLevel > 3: logging.debug( "'%s' is superfluous: won't add to tempDict" % tempString )
                        ambigSet.add( tempString )
                    else: # it's a different value
                        if Globals.verbosityLevel > 3: logging.debug( "'%s' is ambiguous: won't add to tempDict" % tempString )
                        ambigSet.add( tempString )
                elif tempString in tempDict and tempDict[tempString]!=value:
                    if Globals.verbosityLevel > 3: logging.info( "'%s' is ambiguous: will remove from tempDict" % tempString )
                    ambigSet.add( tempString )
                else:
                    tempDict[tempString] = value
                tempTempString = tempString
                while ' ' in tempTempString:
                    tempTempString = tempTempString.replace( " ", "", 1 ) # Remove the first space
                    if tempTempString in originalDict:
                        if originalDict[tempTempString] == value:
                            if Globals.verbosityLevel > 3: logging.debug( "'%s' (spaces removed) is superfluous: won't add to tempDict" % tempTempString )
                            ambigSet.add( tempTempString )
                        else: # it's a different value
                            if Globals.verbosityLevel > 3: logging.debug( "'%s' (spaces removed) is ambiguous: won't add to tempDict" % tempTempString )
                            ambigSet.add( tempTempString )
                    elif tempTempString in tempDict and tempDict[tempTempString]!=value:
                        if Globals.verbosityLevel > 3: logging.info( "'%s' (spaces removed) is ambiguous: will remove from tempDict" % tempTempString )
                        ambigSet.add( tempTempString )
                    else:
                        tempDict[tempTempString] = value
            tempString = tempString[:-1] # Drop off another letter
    # end of expandAbbrevs

    assert( systemName )
    assert( divisionsNamesList ); assert( booknameLeadersDict ); assert( bookNamesDict )
    assert( bookList )

    if Globals.verbosityLevel > 2: print( "  Expanding %s input abbreviations (for %i books)..." % ( systemName, len(bookList) ) )

    # Firstly, make a new UPPER CASE leaders dictionary., e.g., Saint/Snt goes to SAINT/SNT
    UCBNLeadersDict = {}
    for leader in booknameLeadersDict:
        UCLeader = leader.upper()
        assert( UCLeader not in UCBNLeadersDict )
        UCBNLeadersDict[UCLeader] = [x.upper() for x in booknameLeadersDict[leader]]
    #print( "UCbnl", len(UCBNLeadersDict), UCBNLeadersDict )

    # Secondly make a set of the given allowed names
    divNameInputDict, bkNameInputDict, ambigSet = {}, {}, set()
    for k,entryDict in enumerate(divisionsNamesList):
        for field in entryDict["inputFields"]:
            UCField = field.upper()
            if UCField in divNameInputDict or UCField in bkNameInputDict:
                logging.warning( "Have duplicate entries of '%s' in divisionsNames for %s" % ( UCField, systemName ) )
                ambigSet.add( UCField )
            divNameInputDict[UCField] = k # Store the index into divisionsNamesList
    for refAbbrev in bookNamesDict.keys():
        if refAbbrev in bookList:
            for field in bookNamesDict[refAbbrev]["inputFields"]: # inputFields include the defaultName, defaultAbbreviation, and inputAbbreviations
                UCField = field.upper()
                if UCField in divNameInputDict or UCField in bkNameInputDict:
                    logging.warning( "Have duplicate entries of '%s' in divisions and book names for %s" % ( UCField, systemName ) )
                    ambigSet.add( UCField )
                bkNameInputDict[UCField] = refAbbrev # Store the index to the book
    #print( 'amb', len(ambigSet), ambigSet )

    # Now expand the divisions names
    #
    # We do this by replacing "2 " with alternatives like "II " and "Saint" with "Snt" and "St" (as entered in the XML file)
    #   At the same time, we progressively drop letters off the end until the (UPPER CASE) name becomes ambiguous
    #       We also remove internal spaces
    #
    # We add all unambiguous names to tempDict
    # We list ambiguous names in ambigSet so that they can be removed from tempDict after all entries have been processed
    #   (This is because we might not discover the ambiguity until later in processing the list)
    #
    # NOTE: In this code, division names and book names share a common ambiguous list
    #           If they are only ever entered into separate fields, the ambiguous list could be split into two
    #               i.e., they wouldn't be ambiguous in context
    #
    #print( "\ndivNameInputDict", len(divNameInputDict), divNameInputDict )
    tempDNDict = {}
    for UCField in divNameInputDict.keys():
        expandAbbrevs( UCField, divNameInputDict[UCField], divNameInputDict, tempDNDict, ambigSet  )
        for leader in UCBNLeadersDict: # Note that the leader here includes a trailing space
            if UCField.startswith( leader ):
                for replacementLeader in UCBNLeadersDict[leader]:
                    expandAbbrevs( UCField.replace(leader,replacementLeader), divNameInputDict[UCField], divNameInputDict, tempDNDict, ambigSet )
    #print ( '\ntempDN', len(tempDNDict), tempDNDict )
    #print( '\namb2', len(ambigSet), ambigSet )

    #print( "\nbkNameInputDict", len(bkNameInputDict), bkNameInputDict )
    tempBNDict = {}
    for UCField in bkNameInputDict.keys():
        expandAbbrevs( UCField, bkNameInputDict[UCField], bkNameInputDict, tempBNDict, ambigSet  )
        for leader in UCBNLeadersDict: # Note that the leader here includes a trailing space
            if UCField.startswith( leader ):
                for replacementLeader in UCBNLeadersDict[leader]:
                    expandAbbrevs( UCField.replace(leader,replacementLeader), bkNameInputDict[UCField], bkNameInputDict, tempBNDict, ambigSet )
    #print ( '\ntempBN', len(tempBNDict) )
    #print( '\namb3', len(ambigSet), ambigSet )

    # Add the unambiguous shortcuts and abbreviations to get all of our allowed options
    for field in tempDNDict:
        if field not in ambigSet:
            assert( field not in divNameInputDict )
            divNameInputDict[field] = tempDNDict[field]
    #print( "\ndivNameInputDict--final", len(divNameInputDict), divNameInputDict )
    for field in tempBNDict:
        if field not in ambigSet:
            assert( field not in bkNameInputDict )
            bkNameInputDict[field] = tempBNDict[field]
    #print( "\nbkNameInputDict--final", len(bkNameInputDict) )

    # Now sort both dictionaries to be longest string first
    sortedDNDict = OrderedDict( sorted(divNameInputDict.items(), key=lambda s: -len(s[0])) )
    sortedBNDict = OrderedDict( sorted( bkNameInputDict.items(), key=lambda s: -len(s[0])) )

    # Finally, return the expanded input fields
    return sortedDNDict, sortedBNDict
# end of expandBibleNamesInputs



@singleton # Can only ever have one instance
class BibleBooksNamesSystems:
    """
    Class for handling Bible books names systems.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.

    Note: BBB is used in this class to represent the three-character referenceAbbreviation.
    """

    def __init__( self ): # We can't give this parameters because of the singleton
        """
        Constructor: 
        """
        self.__bbnsc = _BibleBooksNamesSystemsConvertor()
        self.__DataDicts = self.__ExpandedDicts = None # We'll import into this in loadData
    # end of __init__

    def loadData( self, XMLFilepath=None ):
        """ Loads the XML data file and imports it to dictionary format (if not done already). """
        if not self.__DataDicts: # Don't do this unnecessarily
            self.__bbnsc.loadSystems( XMLFilepath ) # Load the XML (if not done already)
            #self.__bbnsc.expandInputs() # Expand the inputAbbreviations to find all shorter unambiguous possibilities
            self.__DataDicts, self.__ExpandedDicts = self.__bbnsc.importDataToPython() # Get the various dictionaries organised for quick lookup
            del self.__bbnsc # Now the convertor class (that handles the XML) is no longer needed
        return self
    # end of loadData

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "BibleBooksNamesSystems object"
        if self.__ExpandedDicts: assert( len(self.__DataDicts) == len(self.__ExpandedDicts) )
        result += ('\n' if result else '') + "  Num loaded bookname systems = %i" % ( len(self.__DataDicts) )
        return result
    # end of __str__

    def getAvailableBooksNamesSystemNames( self ):
        """ Returns a list of available system name strings. """
        return [x for x in self.__DataLists]
    # end of getAvailableBooksNamesSystemNames

    def getBooksNamesSystem( self, systemName, bookList=None ):
        """ Returns two dictionaries and a list object."""
        if systemName in self.__DataDicts:
            assert( len(self.__DataDicts[systemName]) == 3 )
            divisionsNamesList, booknameLeadersDict, bookNamesDict = self.__DataDicts[systemName] # unpack it so it's clearer what we're doing here
            if bookList is None:
                if self.__ExpandedDicts:
                    assert( len(self.__ExpandedDicts[systemName]) == 2 )
                    return divisionsNamesList, booknameLeadersDict, bookNamesDict, self.__ExpandedDicts[systemName][0], self.__ExpandedDicts[systemName][1]
                # else we haven't done any previous input abbreviation expansion
                return divisionsNamesList, booknameLeadersDict, bookNamesDict, {}, {}
            # else we were given a booklist so we need to expand the input abbreviations here now
            if self.__ExpandedDicts: logging.warning( "This %s book names system was already expanded, but never mind :)" % systemName )
            sortedDNDict, sortedBNDict = expandBibleNamesInputs( systemName, divisionsNamesList, booknameLeadersDict, bookNamesDict, bookList )
            #print( sortedBNDict )
            return divisionsNamesList, booknameLeadersDict, bookNamesDict, sortedDNDict, sortedBNDict
        # else we couldn't find the requested system name
        logging.error( "No '%s' system in Bible Books Names Systems" % systemName )
        if Globals.verbosityLevel > 2: logging.error( "Available systems are %s" % self.getAvailableSystemNames() )
    # end of getBooksNamesSystem

    # TODO: Add more useful routines in here

# end of BibleBooksNamesSystems class


class BibleBooksNamesSystem:
    """
    Class for handling a particular Bible book names system.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.
    """

    def __init__( self, systemName, bookList=None ):
        """
        Grabs a particular BibleBooksNames system from the singleton object which contains all of the known books names systems.
            The optional book list is used for determining non-ambiguous bookname abbreviations.
        """
        self.__systemName = systemName
        self.__languageCode = systemName.split('_',1)[0]
        self.__bnss = BibleBooksNamesSystems().loadData() # Doesn't reload the XML unnecessarily :)
        result = self.__bnss.getBooksNamesSystem( self.__systemName, bookList )
        if result is not None:
            self.__divisionsNamesList, self.__booknameLeadersDict, self.__bookNamesDict, self.__sortedDivisionNamesDict, self.__sortedBookNamesDict = result
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible books names system.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "BibleBooksNamesSystem object"
        result += ('\n' if result else '') + "  %s Bible books names system" % ( self.__systemName )
        result += ('\n' if result else '') + "  Language code = %s" % ( self.__languageCode )
        if Globals.verbosityLevel > 2: # Make it verbose
            result += ('\n' if result else '') + "    Num divisions = %i" % ( len(self.__divisionsNamesList) )
            result += ('\n' if result else '') + "    Num bookname leaders = %i" % ( len(self.__booknameLeadersDict) )
            result += ('\n' if result else '') + "    Num books = %i" % ( len(self.__bookNamesDict) )
            result += ('\n' if result else '') + "    Num expanded division name abbreviations = %i" % ( len(self.__sortedDivisionNamesDict) )
            result += ('\n' if result else '') + "    Num expanded book name abbreviations = %i" % ( len(self.__sortedBookNamesDict) )
        return result
    # end of __str__

    def getBooksNamesSystemName( self ):
        """ Return the book names system name. """
        return self.__systemName
    # end of getBooksNamesSystemName

    def getBBB( self, bookNameOrAbbreviation ):
        """ Get the referenceAbbreviation from the given book name or abbreviation.
                (Automatically converts to upper case before comparing strings.) """
        assert( bookNameOrAbbreviation )
        upperCaseBookNameOrAbbreviation = bookNameOrAbbreviation.upper()
        if upperCaseBookNameOrAbbreviation in self.__sortedBookNamesDict:
            return self.__sortedBookNamesDict[upperCaseBookNameOrAbbreviation]
        #print( "getBBB", bookNameOrAbbreviation, upperCaseBookNameOrAbbreviation )
        #myList = []
        #for key in self.__sortedBookNamesDict.keys():
        #    if key.startswith( upperCaseBookNameOrAbbreviation[0] ): myList.append( key )
        #print( "List is", myList )
    # end of getBBB

    def getShortBookName( self, BBB ):
        """ Get the short book name from the given referenceAbbreviation. """
        assert( len(BBB) == 3 )
        return self.__bookNamesDict[BBB]['defaultName']
    # end of getShortBookName

    def getit( self ): return self.__sortedBookNamesDict
# end of BibleBookNamesSystem class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v%s" % ( versionString ) )
    parser.add_option("-x", "--expandDemo", action="store_true", dest="expandDemo", default=False, help="expand the input abbreviations to include all unambiguous shorter forms")
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML files to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 1: print( "%s V%s" % ( progName, versionString ) )

    sampleBookList = ['JDG','MAT','MRK','LUK','JHN','ACT','ROM','CO1','CO2','PE1','PE2','JDE','REV']
    if Globals.commandLineOptions.export:
        bbnsc = _BibleBooksNamesSystemsConvertor().loadSystems() # Load the XML
        if Globals.commandLineOptions.expandDemo: # Expand the inputAbbreviations to find all shorter unambiguous possibilities
            bbnsc.expandInputs( sampleBookList )
        bbnsc.exportDataToPython() # Produce the .py tables
        bbnsc.exportDataToJSON() # Produce a json output file
        bbnsc.exportDataToC() # Produce the .h and .c tables

    else: # Must be demo mode
        # Demo the convertor object
        bbnsc = _BibleBooksNamesSystemsConvertor().loadSystems() # Load the XML
        print( bbnsc ) # Just print a summary
        if Globals.commandLineOptions.expandDemo: # Expand the inputAbbreviations to find all shorter unambiguous possibilities
            bbnsc.expandInputs( sampleBookList )
            print( bbnsc ) # Just print a summary

        # Demo the BibleBooksNamesSystems object
        bbnss = BibleBooksNamesSystems().loadData() # Doesn't reload the XML unnecessarily :)
        print( bbnss ) # Just print a summary

        # Demo the BibleBooksNamesSystem object
        bbns1 = BibleBooksNamesSystem("eng_traditional") # Doesn't reload the XML unnecessarily :)
        print( bbns1 ) # Just print a summary

        # Demo the BibleBooksNamesSystem object with a book list
        bbns2 = BibleBooksNamesSystem("eng_traditional",sampleBookList) # Doesn't reload the XML unnecessarily :)
        print( bbns2 ) # Just print a summary
        #names = []
        #for name in bbns2.getit():
        #    if name[0]=='J': names.append( name )
        #print( names )
# end of main

if __name__ == '__main__':
    main()
# end of BibleBooksNames.py
