#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleBooksNames.py
#
# Module handling BibleBooksNamesSystem_*.xml to produce C and Python data tables
#   Last modified: 2010-11-15 (also update versionString below)
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
Module handling BibleBooksNamesSystem_*.xml to produce C and Python data tables.
"""

progName = "Bible Books Names Systems handler"
versionString = "0.15"


import os, logging
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree
import BibleBooksCodes, iso_639_3


class BibleBooksNamesSystemsConvertor:
    """
    A class to handle data for Bible booksNames systems.
    """
    filenameBase = "BibleBooksNames"
    treeTag = "BibleBooksNames"
    headerTag = "header"
    mainElementTags = ( "BibleDivisionNames", "BibleBooknameLeaders", "BibleBookNames" )
    compulsoryAttributes = { 0:(), 1:("standardLeader",), 2:("referenceAbbreviation",) }
    optionalAttributes = { 0:(), 1:(), 2:() }
    uniqueAttributes = {}
    for key in compulsoryAttributes.keys():
        uniqueAttributes[key] = compulsoryAttributes[key] + optionalAttributes[key]
    compulsoryElements = { 0:("defaultName","defaultAbbreviation","includesBook",), 1:("inputAbbreviation",), 2:("defaultName","defaultAbbreviation",) }
    optionalElements =  { 0:("inputAbbreviation",), 1:(), 2:("inputAbbreviation",) }
    uniqueElements = {}
    for key in compulsoryElements.keys():
        uniqueElements[key] = compulsoryElements[key] + optionalElements[key]

    def __init__( self, ISO639Dict=None, BibleBooksCodesDict=None ):
        """
        Constructor.
        """
        self.ISO639Dict, self.BibleBooksCodesDict = ISO639Dict, BibleBooksCodesDict
        self.systems, self.importedSystems, self.expandedInputSystems = {}, {}, {}
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible booksNames system.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = ""
        result += ('\n' if result else '') + "Num systems loaded = %i" % ( len(self.systems) )
        for x in self.systems:
            result += ('\n' if result else '') + "  %s" % ( x )
            if self.ISO639Dict and self.systems[x]["languageCode"] and self.systems[x]["languageCode"] in self.ISO639Dict:
                result += ('\n' if result else '') + "    Language code %s = %s" % ( self.systems[x]["languageCode"], self.ISO639Dict[self.systems[x]["languageCode"]][0] )
            title = self.systems[x]["title"]
            if title: result += ('\n' if result else '') + "    %s" % ( title )
            version = self.systems[x]["version"]
            if version: result += ('\n' if result else '') + "    Version: %s" % ( version )
            date = self.systems[x]["date"]
            if date: result += ('\n' if result else '') + "    Last updated: %s" % ( date )
            result += ('\n' if result else '') + "    Num entries = %i" % ( len(self.systems[x]["tree"]) )
            numDivisions, numLeaders, numBooks = 0, 0, 0
            for element in self.systems[x]["tree"]:
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

    def loadSystems( self, folder=None ):
        """
        Load and pre-process the specified booksNames systems.
        """

        if folder==None: folder = "DataFiles/BookNames"
        for filename in os.listdir( folder ):
            filepart, extension = os.path.splitext( filename )
            if extension.upper() == '.XML' and filepart.upper().startswith(BibleBooksNamesSystemsConvertor.filenameBase.upper()+"_"):
                booksNamesSystemCode = filepart[len(BibleBooksNamesSystemsConvertor.filenameBase)+1:]
                #print( "Loading %s booksNames system from %s..." % ( booksNamesSystemCode, filename ) )
                self.systems[booksNamesSystemCode] = {}
                self.systems[booksNamesSystemCode]["languageCode"] = booksNamesSystemCode.split('_')[0]
                self.systems[booksNamesSystemCode]["tree"] = ElementTree().parse ( os.path.join( folder, filename ) )
                assert( self.systems[booksNamesSystemCode]["tree"] ) # Fail here if we didn't load anything at all

                # Check and remove the header element
                if self.systems[booksNamesSystemCode]["tree"].tag  == BibleBooksNamesSystemsConvertor.treeTag:
                    header = self.systems[booksNamesSystemCode]["tree"][0]
                    if header.tag == BibleBooksNamesSystemsConvertor.headerTag:
                        self.systems[booksNamesSystemCode]["header"] = header
                        self.systems[booksNamesSystemCode]["tree"].remove( header )
                        if len(header)>1:
                            logging.info( "Unexpected elements in header" )
                        elif len(header)==0:
                            logging.info( "Missing work element in header" )
                        else:
                            work = header[0]
                            if work.tag == "work":
                                self.systems[booksNamesSystemCode]["version"] = work.find("version").text
                                self.systems[booksNamesSystemCode]["date"] = work.find("date").text
                                self.systems[booksNamesSystemCode]["title"] = work.find("title").text
                            else:
                                logging.warning( "Missing work element in header" )
                    else:
                        logging.warning( "Missing header element (looking for '%s' tag)" % ( headerTag ) )
                else:
                    logging.error( "Expected to load '%s' but got '%s'" % ( BibleBooksNamesSystemsConvertor.treeTag, self.systems[booksNamesSystemCode]["tree"].tag ) )
                bookCount = 0 # There must be an easier way to do this
                for subelement in self.systems[booksNamesSystemCode]["tree"]:
                    bookCount += 1
                logging.info( "    Loaded %i books" % ( bookCount ) )

                self.validateSystem( booksNamesSystemCode )
    # end of loadSystems

    def validateSystem( self, systemName ):
        """
        Checks for basic formatting/content errors in a Bible book name system.
        """
        assert( systemName )
        assert( self.systems[systemName]["tree"] )

        if len(self.systems[systemName]["languageCode"]) != 3:
            logging.error( "Couldn't find 3-letter language code in '%s' book names system" % ( systemName ) )
        if self.ISO639Dict: # Check that we have a valid language code
            if self.systems[systemName]["languageCode"] not in self.ISO639Dict:
                logging.error( "Unrecognized '%s' ISO-639-3 language code in '%s' book names system" % ( self.systems[systemName]["languageCode"], systemName ) )

        uniqueDict = {}
        for index in range( 0, len(BibleBooksNamesSystemsConvertor.mainElementTags) ):
            for elementName in BibleBooksNamesSystemsConvertor.uniqueElements[index]: uniqueDict["Element_"+str(index)+"_"+elementName] = []
            for attributeName in BibleBooksNamesSystemsConvertor.uniqueAttributes[index]: uniqueDict["Attribute_"+str(index)+"_"+attributeName] = []

        expectedID = 1
        for k,element in enumerate(self.systems[systemName]["tree"]):
            if element.tag in BibleBooksNamesSystemsConvertor.mainElementTags:
                index = BibleBooksNamesSystemsConvertor.mainElementTags.index( element.tag )

                # Check compulsory attributes on this main element
                for attributeName in BibleBooksNamesSystemsConvertor.compulsoryAttributes[index]:
                    attributeValue = element.get( attributeName )
                    if attributeValue is None:
                        logging.error( "Compulsory '%s' attribute is missing from %s element in record %i in %s" % ( attributeName, element.tag, k, systemName ) )
                    if not attributeValue:
                        logging.warning( "Compulsory '%s' attribute is blank on %s element in record %i in %s" % ( attributeName, element.tag, k, systemName ) )

                # Check optional attributes on this main element
                for attributeName in BibleBooksNamesSystemsConvertor.optionalAttributes[index]:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if not attributeValue:
                            logging.warning( "Optional '%s' attribute is blank on %s element in record %i in %s" % ( attributeName, element.tag, k, systemName ) )

                # Check for unexpected additional attributes on this main element
                for attributeName in element.keys():
                    attributeValue = element.get( attributeName )
                    if attributeName not in BibleBooksNamesSystemsConvertor.compulsoryAttributes[index] and attributeName not in BibleBooksNamesSystemsConvertor.optionalAttributes[index]:
                        logging.warning( "Additional '%s' attribute ('%s') found on %s element in record %i in %s" % ( attributeName, attributeValue, element.tag, k, systemName ) )

                # Check the attributes that must contain unique information (in that particular field -- doesn't check across different attributes)
                for attributeName in BibleBooksNamesSystemsConvertor.uniqueAttributes[index]:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if attributeValue in uniqueDict["Attribute_"+str(index)+"_"+attributeName]:
                            logging.error( "Found '%s' data repeated in '%s' field on %s element in record %i in %s" % ( attributeValue, attributeName, element.tag, k, systemName ) )
                        uniqueDict["Attribute_"+str(index)+"_"+attributeName].append( attributeValue )

                # Check compulsory elements
                for elementName in BibleBooksNamesSystemsConvertor.compulsoryElements[index]:
                    if element.find( elementName ) is None:
                        logging.error( "Compulsory '%s' element is missing (record %i) in %s" % ( elementName, k, systemName ) )
                    if not element.find( elementName ).text:
                        logging.warning( "Compulsory '%s' element is blank (record %i) in %s" % ( elementName, k, systemName ) )

                # Check optional elements
                for elementName in BibleBooksNamesSystemsConvertor.optionalElements[index]:
                    if element.find( elementName ) is not None:
                        if not element.find( elementName ).text:
                            logging.warning( "Optional '%s' element is blank (record %i) in %s" % ( elementName, k, systemName ) )

                # Check for unexpected additional elements
                for subelement in element:
                    if subelement.tag not in BibleBooksNamesSystemsConvertor.compulsoryElements[index] and subelement.tag not in BibleBooksNamesSystemsConvertor.optionalElements[index]:
                        logging.warning( "Additional '%s' element ('%s') found (record %i) in %s %s" % ( subelement.tag, subelement.text, k, systemName, element.tag ) )

                # Check the elements that must contain unique information (in that particular element -- doesn't check across different elements)
                for elementName in BibleBooksNamesSystemsConvertor.uniqueElements[index]:
                    if element.find( elementName ) is not None:
                        text = element.find( elementName ).text
                        if text in uniqueDict["Element_"+str(index)+"_"+elementName]:
                            logging.error( "Found '%s' data repeated in '%s' element (record %i) in %s" % ( text, elementName, k, systemName ) )
                        uniqueDict["Element_"+str(index)+"_"+elementName].append( text )
            else:
                logging.warning( "Unexpected element: %s in record %i in %s" % ( element.tag, k, systemName ) )
    # end of validateSystem

    def importDataToPython( self ):
        """
        Loads (and pivots) the data (not including the header) into suitable Python containers to use in a Python program.
        """
        # We'll create a number of dictionaries
        myBookNamesSystemsDict = {}
        for booksNamesSystemCode in self.systems.keys():
            #print( booksNamesSystemCode )
            # Make the data dictionary for this booksNames system
            myDivisionsNamesList, myBooknameLeadersDict, myBookNamesDict = [], {}, {}
            for element in self.systems[booksNamesSystemCode]["tree"]:
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
                    if self.BibleBooksCodesDict and referenceAbbreviation not in self.BibleBooksCodesDict:
                        logging.error( "Unrecognized '%s' book abbreviation BibleBookNames in '%s' booksNames system" % ( referenceAbbreviation, booksNamesSystemCode ) )
                    defaultName = element.find("defaultName").text
                    defaultAbbreviation = element.find("defaultAbbreviation").text
                    inputFields = [ defaultName ] # Add the default name to the allowed input fields
                    if not defaultName.startswith( defaultAbbreviation ):
                        inputFields.append( defaultAbbreviation )
                    for subelement in element.findall("inputAbbreviation"):
                        if subelement.text in inputFields:
                            logging.info( "Superfluous '%s' entry in inputAbbreviation field for %s book in '%s' booksNames system" % ( subelement.text, defaultName, booksNamesSystemCode ) )
                        else: inputFields.append( subelement.text )
                    myBookNamesDict[referenceAbbreviation] = { "defaultName":defaultName, "defaultAbbreviation":defaultAbbreviation, "inputFields":inputFields }
            # Now put it into my dictionary for easy access
            myBookNamesSystemsDict[booksNamesSystemCode] = myDivisionsNamesList, myBooknameLeadersDict, myBookNamesDict
        self.importedSystems = myBookNamesSystemsDict
    # end of importDataToPython

    def expandInputs ( self ):
        """
        Expand the inputAbbreviation fields to include all unambiguous shorter abbreviations.

        Would it be better to do this for a specific publication since there will be less ambiguities if there are less actual books included???
        """
        def expandAbbrevs( UCString, value, originalDict, tempDict, theAmbigSet ):
            """
            Progressively remove characters off the end of the (UPPER CASE) UCString, plus also remove internal spaces.
                trying to find unambiguous shortcuts which the user could use.
            """
            # Now drop off final letters and remove internal spaces
            tempString = UCString[:-1] # Drop off the last letter
            while( tempString ):
                if tempString[-1] != ' ':
                    if tempString in originalDict:
                        if originalDict[tempString] == value:
                            #print( "'%s' is superfluous: won't add to tempDict" % tempString )
                            ambigSet.add( tempString )
                        else: # it's a different value
                            #print( "'%s' is ambiguous: won't add to tempDict" % tempString )
                            ambigSet.add( tempString )
                    elif tempString in tempDict and tempDict[tempString]!=value:
                        #print( "'%s' is ambiguous: will remove from tempDict" % tempString )
                        ambigSet.add( tempString )
                    else:
                        tempDict[tempString] = value
                    tempTempString = tempString
                    while ' ' in tempTempString:
                        tempTempString = tempTempString.replace( " ", "", 1 ) # Remove the first space
                        if tempTempString in originalDict:
                            if originalDict[tempTempString] == value:
                                #print( "'%s' is superfluous: won't add to tempDict" % tempTempString )
                                ambigSet.add( tempTempString )
                            else: # it's a different value
                                #print( "'%s' is ambiguous: won't add to tempDict" % tempTempString )
                                ambigSet.add( tempTempString )
                        elif tempTempString in tempDict and tempDict[tempTempString]!=value:
                            #print( "'%s' (spaces removed) is ambiguous: will remove from tempDict" % tempTempString )
                            ambigSet.add( tempTempString )
                        else:
                            tempDict[tempTempString] = value
                tempString = tempString[:-1] # Drop off another letter
        # end of expandAbbrevs

        assert( self.importedSystems )
        for systemName in self.importedSystems:
            print( "Expanding %s..." % ( systemName ) )
            divisionsNamesList, booknameLeadersDict, bookNamesDict = self.importedSystems[systemName]

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
                        logging.error( "Have duplicate entries of '%s' in divisionsNames for %s" % ( UCField, systemName ) )
                        ambigSet.add( UCField )
                    divNameInputDict[UCField] = k # Store the index into divisionsNamesList
            for refAbbrev in bookNamesDict.keys():
                for field in bookNamesDict[refAbbrev]["inputFields"]:
                    UCField = field.upper()
                    if UCField in divNameInputDict or UCField in bkNameInputDict:
                        logging.error( "Have duplicate entries of '%s' in divisions and book names for %s" % ( UCField, systemName ) )
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

            # Finally, save the expanded input fields
            self.expandedInputSystems[systemName] = sortedDNDict, sortedBNDict
    # end of expandInputs

    def exportDataToPython( self, filepath=None ):
        """
        Writes the information tables to a .py file that can be cut and pasted into a Python program.
        """
        def exportPythonDict( theFile, theDict, dictName, keyComment, fieldsComment ):
            """Exports theDict to theFile."""
            theFile.write( "%s = {\n  # Key is %s\n  # Fields are: %s\n" % ( dictName, keyComment, fieldsComment ) )
            for dictKey in theDict.keys():
                theFile.write( '  %s: %s,\n' % ( repr(dictKey), repr(theDict[dictKey]) ) )
            theFile.write( "} # (%i entries)\n# end of %s\n\n" % ( len(theDict), dictName ) )
        # end of exportPythonDict

        def exportPythonOrderedDict( theFile, theDict, dictName, keyComment, fieldsComment ):
            """Exports theDict to theFile."""
            theFile.write( "%s = OrderedDict([\n  # Key is %s\n  # Fields are: %s\n" % ( dictName, keyComment, fieldsComment ) )
            for dictKey in theDict.keys():
                theFile.write( '  (%s, %s),\n' % ( repr(dictKey), repr(theDict[dictKey]) ) )
            theFile.write( "]) # (%i entries)\n# end of %s\n\n" % ( len(theDict), dictName ) )
        # end of exportPythonDict

        def exportPythonList( theFile, theList, listName, fieldsComment ):
            """Exports theList to theFile."""
            theFile.write( "%s = [\n  # Fields are: %s\n" % ( listName, fieldsComment ) )
            for j,entry in enumerate(theList):
                theFile.write( '  %s, # %i\n' % ( repr(entry), j ) )
            theFile.write( "] # (%i entries)\n# end of %s\n\n" % ( len(theList), listName ) )
        # end of exportPythonList

        from datetime import datetime

        assert( self.importedSystems )
        if not filepath: filepath = os.path.join( "DerivedFiles", BibleBooksNamesSystemsConvertor.filenameBase + "_Tables.py" )
        print( "Exporting to %s..." % ( filepath ) )

        # Split into three lists/dictionaries
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# %s\n#\n" % ( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by BibleBooksNames.py V%s %s\n#\n" % ( versionString, datetime.now() ) )
            #if self.title: myFile.write( "# %s\n" % ( self.title ) )
            #if self.version: myFile.write( "#  Version: %s\n" % ( self.version ) )
            #if self.date: myFile.write( "#  Date: %s\n#\n" % ( self.date ) )
            #myFile.write( "#   %i %s entries loaded from the original XML file.\n" % ( len(self.namesTree), BibleBooksNamesSystemsConvertor.treeTag ) )
            myFile.write( "#   %i %s loaded from the original XML files.\n#\n\n" % ( len(self.systems), BibleBooksNamesSystemsConvertor.treeTag ) )
            myFile.write( "from collections import OrderedDict\n" )
            for systemName in self.importedSystems:
                divisionsNamesList, booknameLeadersDict, bookNamesDict = self.importedSystems[systemName]
                myFile.write( "\n\n#\n# %s\n#\n\n" % ( systemName ) )
                exportPythonList( myFile, divisionsNamesList, "divisionNamesList", "startsWith( string), defaultName (string), defaultAbbreviation (string), inputFields (list of strings) all in a dictionary" )
                exportPythonDict( myFile, booknameLeadersDict, "booknameLeadersDict", "standardLeader (all fields include a trailing space)", "inputAlternatives (list of strings)" )
                exportPythonDict( myFile, bookNamesDict, "bookNamesDict", "referenceAbbreviation", "defaultName (string), defaultAbbreviation (string), inputAbbreviations (list of strings) all in a dictionary" )
                if systemName in self.expandedInputSystems:
                    divisionsNamesInputDict, bookNamesInputDict = self.expandedInputSystems[systemName]
                    #myFile.write( "#\n# %s\n" % ( systemName ) )
                    exportPythonOrderedDict( myFile, divisionsNamesInputDict, "divisionsNamesInputDict", "UpperCaseInputString", "index (into divisionNamesList above)" )
                    exportPythonOrderedDict( myFile, bookNamesInputDict, "bookNamesInputDict", "UpperCaseInputString", "referenceAbbreviation (string)" )
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

        assert( self.importedSystems )
        if not filepath: filepath = os.path.join( "DerivedFiles", BibleBooksNamesSystemsConvertor.filenameBase + "_Tables.h" )
        print( "Exporting to %s..." % ( filepath ) )

        ifdefName = BibleBooksNamesSystemsConvertor.filenameBase.upper() + "_Tables_h"
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "// %s\n//\n" % ( filepath ) )
            myFile.write( "// This UTF-8 file was automatically generated by BibleBooksNamesSystemsConvertor.py V%s %s\n//\n" % ( versionString, datetime.now() ) )
            if self.title: myFile.write( "// %s\n" % ( self.title ) )
            if self.version: myFile.write( "//  Version: %s\n" % ( self.version ) )
            if self.date: myFile.write( "//  Date: %s\n//\n" % ( self.date ) )
            myFile.write( "//   %i %s loaded from the original XML file.\n//\n\n" % ( len(self.namesTree), BibleBooksNamesSystemsConvertor.treeTag ) )
            myFile.write( "#ifndef %s\n#define %s\n\n" % ( ifdefName, ifdefName ) )
            exportPythonDict( myFile, IDDict, "IDDict", "{int id; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "id (sorted), referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            exportPythonDict( myFile, RADict, "RADict", "{char* refAbbrev; int id; char* SBLAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "referenceAbbreviation (sorted), SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, SBLDict, "SBLDict", "{char* SBLAbbrev; int id; char* refAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "SBLAbbreviation (sorted), ReferenceAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, OADict, "OADict", "{char* OSISAbbrev; int id; char* refAbbrev; char* SBLAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "OSISAbbreviation (sorted), ReferenceAbbreviation, SBLAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, PADict, "PADict", "{char* PTAbbrev; int id; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* PTNum; char* EngName;}", "ParatextAbbreviation (sorted), referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, PNDict, "PNDict", "{char* PTNum; int id; char* PTAbbrev; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* EngName;}", "ParatextNumberString (sorted), ParatextAbbreviation, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, id, nameEnglish (comment only)" )
            myFile.write( "#endif // %s\n" % ( ifdefName ) )
    # end of exportDataToC


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
    iso = iso_639_3.iso_639_3_Convertor()
    ISOIDDict, junk = iso.importDataToPython()

    # Adjust the name dict to upper case
    UC_BBCNameDict = {}
    for key, entry in BBCNameDict.items():
        UC_BBCNameDict[key.upper()] = entry

    # Do a proper load/check
    bbns = BibleBooksNamesSystemsConvertor( ISO639Dict=ISOIDDict, BibleBooksCodesDict=BBCRADict )
    bbns.loadSystems()
    bbns.importDataToPython()
    # Expand the inputAbbreviations to find all shorter unambiguous possibilities
    bbns.expandInputs()

    if CommandLineOptions.export:
        bbns.exportDataToPython()
        bbns.exportDataToC()
    else: # not scraping or exporting -- must just be a demo run
        print( bbns )
        bbns.expandInputs()
        print( bbns )
# end of main

if __name__ == '__main__':
    main()
# end of BibleBooksNames.py
