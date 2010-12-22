#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleBooksCodes.py
#
# Module handling BibleBooksCodes.xml to produce C and Python data tables
#   Last modified: 2010-12-22 (also update versionString below)
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
versionString = "0.94"


import logging, os.path
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree

from singleton import singleton
import Globals


@singleton # Can only ever have one instance
class _BibleBooksCodesConvertor:
    """
    Class for reading, validating, and converting BibleBooksCodes.
    This is only intended as a transitory class (used at start-up).
    The BibleBooksCodes class has functions more generally useful.
    """

    def __init__( self ): # We can't give this parameters because of the singleton
        """
        Constructor: expects the filepath of the source XML file.
        Loads (and crudely validates the XML file) into an element tree.
        """
        self.filenameBase = "BibleBooksCodes"

        # These fields are used for parsing the XML
        self.treeTag = "BibleBooksCodes"
        self.headerTag = "header"
        self.mainElementTag = "BibleBookCodes"

        # These fields are used for automatically checking/validating the XML
        self.compulsoryAttributes = ()
        self.optionalAttributes = ()
        self.uniqueAttributes = self.compulsoryAttributes + self.optionalAttributes
        self.compulsoryElements = ( "nameEnglish", "referenceAbbreviation", "referenceNumber" )
        self.optionalElements = ( "expectedChapters", "SBLAbbreviation", "OSISAbbreviation", "SwordAbbreviation", "CCELNumber", "ParatextAbbreviation", "ParatextNumber", "NETBibleAbbreviation", "ByzantineAbbreviation", "possibleAlternativeBooks" )
        #self.uniqueElements = self.compulsoryElements + self.optionalElements
        self.uniqueElements = self.compulsoryElements # Relax the checking

        # These are fields that we will fill later
        self.XMLheader, self.XMLtree = None, None
        self._dataDicts = {} # Used for import
        self.titleString = self.versionString = self.dateString = ''
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "_BibleBooksCodesConvertor object"
        if self.titleString: result += ('\n' if result else '') + "  Title: %s" % ( self.titleString )
        if self.versionString: result += ('\n' if result else '') + "  Version: %s" % ( self.versionString )
        if self.dateString: result += ('\n' if result else '') + "  Date: %s" % ( self.dateString )
        if self.XMLtree is not None: result += ('\n' if result else '') + "  Num entries = %i" % ( len(self.XMLtree) )
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
        Also, extracts some useful elements from the header element.
        """
        assert( XMLFilepath )
        self.XMLFilepath = XMLFilepath
        assert( self.XMLtree is None or len(self.XMLtree)==0 ) # Make sure we're not doing this twice

        if Globals.verbosityLevel > 1: print( "Loading BibleBooksCodes XML file from '%s'..." % XMLFilepath )
        self.XMLtree = ElementTree().parse( XMLFilepath )
        assert( self.XMLtree ) # Fail here if we didn't load anything at all

        if self.XMLtree.tag == self.treeTag:
            header = self.XMLtree[0]
            if header.tag == self.headerTag:
                self.XMLheader = header
                self.XMLtree.remove( header )
                if len(header)>1:
                    logging.info( "Unexpected elements in header" )
                elif len(header)==0:
                    logging.info( "Missing work element in header" )
                else:
                    work = header[0]
                    if work.tag == "work":
                        self.versionString = work.find("version").text
                        self.dateString = work.find("date").text
                        self.titleString = work.find("title").text
                    else:
                        logging.warning( "Missing work element in header" )
            else:
                logging.warning( "Missing header element (looking for '%s' tag)" % ( self.headerTag ) )
            if header.tail is not None and header.tail.strip(): logging.error( "Unexpected '%s' tail data after header" % ( element.tail ) )
        else:
            logging.error( "Expected to load '%s' but got '%s'" % ( self.treeTag, self.XMLtree.tag ) )
    # end of _load

    def _validate( self ):
        """
        Check/validate the loaded data.
        """
        assert( self.XMLtree )

        uniqueDict = {}
        for elementName in self.uniqueElements: uniqueDict["Element_"+elementName] = []
        for attributeName in self.uniqueAttributes: uniqueDict["Attribute_"+attributeName] = []

        expectedID = 1
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
                        if attributeValue in uniqueDict["Attribute_"+attributeName]:
                            logging.error( "Found '%s' data repeated in '%s' field on %s element in record %i" % ( attributeValue, attributeName, element.tag, j ) )
                        uniqueDict["Attribute_"+attributeName].append( attributeValue )

                # Get the referenceAbbreviation to use as a record ID
                ID = element.find("referenceAbbreviation").text

                # Check compulsory elements
                for elementName in self.compulsoryElements:
                    if element.find( elementName ) is None:
                        logging.error( "Compulsory '%s' element is missing in record with ID '%s' (record %i)" % ( elementName, ID, j ) )
                    elif not element.find( elementName ).text:
                        logging.warning( "Compulsory '%s' element is blank in record with ID '%s' (record %i)" % ( elementName, ID, j ) )

                # Check optional elements
                for elementName in self.optionalElements:
                    if element.find( elementName ) is not None:
                        if not element.find( elementName ).text:
                            logging.warning( "Optional '%s' element is blank in record with ID '%s' (record %i)" % ( elementName, ID, j ) )

                # Check for unexpected additional elements
                for subelement in element:
                    if subelement.tag not in self.compulsoryElements and subelement.tag not in self.optionalElements:
                        logging.warning( "Additional '%s' element ('%s') found in record with ID '%s' (record %i)" % ( subelement.tag, subelement.text, ID, j ) )

                # Check the elements that must contain unique information (in that particular element -- doesn't check across different elements)
                for elementName in self.uniqueElements:
                    if element.find( elementName ) is not None:
                        text = element.find( elementName ).text
                        if text in uniqueDict["Element_"+elementName]:
                            logging.error( "Found '%s' data repeated in '%s' element in record with ID '%s' (record %i)" % ( text, elementName, ID, j ) )
                        uniqueDict["Element_"+elementName].append( text )
            else:
                logging.warning( "Unexpected element: %s in record %i" % ( element.tag, j ) )
            if element.tail is not None and element.tail.strip(): logging.error( "Unexpected '%s' tail data after %s element in record %i" % ( element.tail, element.tag, j ) )
        if self.XMLtree.tail is not None and self.XMLtree.tail.strip(): logging.error( "Unexpected '%s' tail data after %s element" % ( self.XMLtree.tail, self.XMLtree.tag ) )
    # end of _validate

    def importDataToPython( self ):
        """
        Loads (and pivots) the data (not including the header) into suitable Python containers to use in a Python program.
        (Of course, you can just use the elementTree in self.XMLtree if you prefer.)
        """
        assert( self.XMLtree )
        if self._dataDicts: # We've already done an import/restructuring -- no need to repeat it
            return self._dataDicts

        # We'll create a number of dictionaries with different elements as the key
        myIDDict,myRADict, mySBLDict,myOADict,mySwDict,myCCELDict,myPADict,myPNDict,myNETDict,myBzDict, myENDict = OrderedDict(),OrderedDict(), {},{},{},{},{},{},{},{}, {}
        for element in self.XMLtree:
            # Get the required information out of the tree for this element
            # Start with the compulsory elements
            nameEnglish = element.find("nameEnglish").text # This name is really just a comment element
            referenceAbbreviation = element.find("referenceAbbreviation").text
            if referenceAbbreviation.upper() != referenceAbbreviation:
                logging.error( "Reference abbreviation '%s' should be UPPER CASE" % ( referenceAbbreviation ) )
            ID = element.find("referenceNumber").text
            intID = int( ID )
            # The optional elements are set to None if they don't exist
            expectedChapters = None if element.find("expectedChapters") is None else element.find("expectedChapters").text
            SBLAbbreviation = None if element.find("SBLAbbreviation") is None else element.find("SBLAbbreviation").text
            OSISAbbreviation = None if element.find("OSISAbbreviation") is None else element.find("OSISAbbreviation").text
            SwordAbbreviation = None if element.find("SwordAbbreviation") is None else element.find("SwordAbbreviation").text
            CCELNumberString = None if element.find("CCELNumber") is None else element.find("CCELNumber").text
            #CCELNumber = int( CCELNumberString ) if CCELNumberString else -1
            ParatextAbbreviation = None if element.find("ParatextAbbreviation") is None else element.find("ParatextAbbreviation").text
            ParatextNumberString = None if element.find("ParatextNumber") is None else element.find("ParatextNumber").text
            #ParatextNumber = int( ParatextNumberString ) if ParatextNumberString else -1
            NETBibleAbbreviation = None if element.find("NETBibleAbbreviation") is None else element.find("NETBibleAbbreviation").text
            ByzantineAbbreviation = None if element.find("ByzantineAbbreviation") is None else element.find("ByzantineAbbreviation").text
            possibleAlternativeBooks = None if element.find("possibleAlternativeBooks") is None else element.find("possibleAlternativeBooks").text

            # Now put it into my dictionaries for easy access
            # This part should be customized or added to for however you need to process the data
            #   Add .upper() if you require the abbreviations to be uppercase (or .lower() for lower case)
            #   The referenceAbbreviation is UPPER CASE by definition
            if "referenceAbbreviation" in self.compulsoryElements or referenceAbbreviation:
                if "referenceAbbreviation" in self.uniqueElements: assert( referenceAbbreviation not in myRADict ) # Shouldn't be any duplicates
                #myRADict[referenceAbbreviation] = ( intID, SBLAbbreviation, OSISAbbreviation, SwordAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, NETBibleAbbreviation, ByzantineAbbreviation, expectedChapters, possibleAlternativeBooks, nameEnglish, )
                myRADict[referenceAbbreviation] = { "referenceNumber":intID, "SBLAbbreviation":SBLAbbreviation, "OSISAbbreviation":OSISAbbreviation,
                                                    "SwordAbbreviation":SwordAbbreviation, "CCELNumberString":CCELNumberString,
                                                    "ParatextAbbreviation":ParatextAbbreviation, "ParatextNumberString":ParatextNumberString,
                                                    "NETBibleAbbreviation":NETBibleAbbreviation, "ByzantineAbbreviation":ByzantineAbbreviation,
                                                    "numExpectedChapters":expectedChapters, "possibleAlternativeBooks":possibleAlternativeBooks, "nameEnglish":nameEnglish }
            if "referenceNumber" in self.compulsoryElements or ID:
                if "referenceNumber" in self.uniqueElements: assert( intID not in myIDDict ) # Shouldn't be any duplicates
                #myIDDict[intID] = ( referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, SwordAbbreviation, CCELNumberString, ParatextAbbreviation, ParatextNumberString, NETBibleAbbreviation, ByzantineAbbreviation, expectedChapters, possibleAlternativeBooks, nameEnglish, )
                myIDDict[intID] = { "referenceAbbreviation":referenceAbbreviation, "SBLAbbreviation":SBLAbbreviation, "OSISAbbreviation":OSISAbbreviation,
                                    "SwordAbbreviation":SwordAbbreviation, "CCELNumberString":CCELNumberString,
                                    "ParatextAbbreviation":ParatextAbbreviation, "ParatextNumberString":ParatextNumberString,
                                    "NETBibleAbbreviation":NETBibleAbbreviation, "ByzantineAbbreviation":ByzantineAbbreviation,
                                    "numExpectedChapters":expectedChapters, "possibleAlternativeBooks":possibleAlternativeBooks, "nameEnglish":nameEnglish }
            if "SBLAbbreviation" in self.compulsoryElements or SBLAbbreviation:
                if "SBLAbbreviation" in self.uniqueElements: ssert( SBLAbbreviation not in myOADict ) # Shouldn't be any duplicates 
                mySBLDict[SBLAbbreviation] = ( intID, referenceAbbreviation, )
            if "OSISAbbreviation" in self.compulsoryElements or OSISAbbreviation:
                if "OSISAbbreviation" in self.uniqueElements: assert( OSISAbbreviation not in myOADict ) # Shouldn't be any duplicates 
                myOADict[OSISAbbreviation] = ( intID, referenceAbbreviation )
            if "SwordAbbreviation" in self.compulsoryElements or SwordAbbreviation:
                if "SwordAbbreviation" in self.uniqueElements: assert( SwordAbbreviation not in mySwDict ) # Shouldn't be any duplicates
                mySwDict[SwordAbbreviation] = ( intID, referenceAbbreviation, )
            if "CCELNumberString" in self.compulsoryElements or CCELNumberString:
                if "CCELNumberString" in self.uniqueElements: assert( CCELNumberString not in myCCELDict ) # Shouldn't be any duplicates
                myCCELDict[CCELNumberString] = ( intID, referenceAbbreviation, )
            if "ParatextAbbreviation" in self.compulsoryElements or ParatextAbbreviation:
                if "ParatextAbbreviation" in self.uniqueElements: assert( ParatextAbbreviation not in myPADict ) # Shouldn't be any duplicates
                myPADict[ParatextAbbreviation] = ( intID, referenceAbbreviation, ParatextNumberString, )
            if "ParatextNumberString" in self.compulsoryElements or ParatextNumberString:
                if "ParatextNumberString" in self.uniqueElements: assert( ParatextNumberString not in myPNDict ) # Shouldn't be any duplicates
                myPNDict[ParatextNumberString] = ( intID, referenceAbbreviation, ParatextAbbreviation, )
            if "NETBibleAbbreviation" in self.compulsoryElements or NETBibleAbbreviation:
                if "NETBibleAbbreviation" in self.uniqueElements: assert( NETBibleAbbreviation not in myBzDict ) # Shouldn't be any duplicates
                myNETDict[NETBibleAbbreviation] = ( intID, referenceAbbreviation, )
            if "ByzantineAbbreviation" in self.compulsoryElements or ByzantineAbbreviation:
                if "ByzantineAbbreviation" in self.uniqueElements: assert( ByzantineAbbreviation not in myBzDict ) # Shouldn't be any duplicates
                myBzDict[ByzantineAbbreviation] = ( intID, referenceAbbreviation, )
            if "nameEnglish" in self.compulsoryElements or ParatextNumberString:
                if "nameEnglish" in self.uniqueElements: assert( nameEnglish not in myENDict ) # Shouldn't be any duplicates
                myENDict[nameEnglish] = ( intID, referenceAbbreviation )
        self._dataDicts = { "referenceNumber":myIDDict, "referenceAbbreviationDict":myRADict, "SBLDict":mySBLDict, "OSISAbbreviationDict":myOADict, "SwordAbbreviationDict":mySwDict,
                        "CCELDict":myCCELDict, "ParatextAbbreviationDict":myPADict, "ParatextNumberDict":myPNDict, "NETBibleAbbreviationDict":myNETDict,
                        "ByzantineAbbreviationDict":myBzDict, "EnglishNameDict":myENDict }
        return self._dataDicts # Just delete any of the dictionaries that you don't need
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

        assert( self.XMLtree )
        self.importDataToPython()
        assert( self._dataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables.py" )
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( filepath ) )
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# %s\n#\n" % ( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by BibleBooksCodes.py on %s\n#\n" % ( datetime.now() ) )
            if self.titleString: myFile.write( "# %s data\n" % ( self.titleString ) )
            if self.versionString: myFile.write( "#  Version: %s\n" % ( self.versionString ) )
            if self.dateString: myFile.write( "#  Date: %s\n#\n" % ( self.dateString ) )
            myFile.write( "#   %i %s loaded from the original XML file.\n#\n\n" % ( len(self.XMLtree), self.treeTag ) )
            mostEntries = "0=referenceNumber (integer 1..255), 1=referenceAbbreviation/BBB (3-uppercase characters)"
            dictInfo = { "referenceNumber":("referenceNumber (integer 1..255)","specified"), "referenceAbbreviationDict":("referenceAbbreviation","specified"),
                            "CCELDict":("CCELNumberString",mostEntries), "SBLDict":("SBLAbbreviation",mostEntries), "OSISAbbreviationDict":("OSISAbbreviation",mostEntries), "SwordAbbreviationDict":("SwordAbbreviation",mostEntries),
                            "ParatextAbbreviationDict":("ParatextAbbreviation",mostEntries), "ParatextNumberDict":("ParatextNumberString",mostEntries),
                            "NETBibleAbbreviationDict":("NETBibleAbbreviation",mostEntries), "ByzantineAbbreviationDict":("ByzantineAbbreviation",mostEntries), "EnglishNameDict":("nameEnglish",mostEntries) }
            for dictName,dictData in self._dataDicts.items():
                exportPythonDict( myFile, dictData, dictName, dictInfo[dictName][0], dictInfo[dictName][1] )
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
        assert( self._dataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables.json" )
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( filepath ) )
        with open( filepath, 'wt' ) as myFile:
            #myFile.write( "# %s\n#\n" % ( filepath ) ) # Not sure yet if these comment fields are allowed in JSON
            #myFile.write( "# This UTF-8 file was automatically generated by BibleBooksCodes.py on %s\n#\n" % ( datetime.now() ) )
            #if self.titleString: myFile.write( "# %s data\n" % ( self.titleString ) )
            #if self.versionString: myFile.write( "#  Version: %s\n" % ( self.versionString ) )
            #if self.dateString: myFile.write( "#  Date: %s\n#\n" % ( self.dateString ) )
            #myFile.write( "#   %i %s loaded from the original XML file.\n#\n\n" % ( len(self.XMLtree), self.treeTag ) )
            json.dump( self._dataDicts, myFile, indent=2 )
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
                    for field in entry:
                        if result: result += ", " # Separate the fields
                        if field is None: result += '""'
                        elif isinstance( field, str): result += '"' + str(field).replace('"','\\"') + '"'
                        elif isinstance( field, int): result += str(field)
                        else: logging.error( "Cannot convert unknown field type '%s' in entry '%s'" % ( field, entry ) )
                elif isinstance( entry, dict ):
                    for key in sorted(entry.keys()):
                        field = entry[key]
                        if result: result += ", " # Separate the fields
                        if field is None: result += '""'
                        elif isinstance( field, str): result += '"' + str(field).replace('"','\\"') + '"'
                        elif isinstance( field, int): result += str(field)
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

        from datetime import datetime

        assert( self.XMLtree )
        self.importDataToPython()
        assert( self._dataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self.filenameBase + "_Tables" )
        hFilepath = filepath + '.h'
        cFilepath = filepath + '.c'
        if Globals.verbosityLevel > 1: print( "Exporting to %s..." % ( cFilepath ) ) # Don't bother telling them about the .h file
        ifdefName = self.filenameBase.upper() + "_Tables_h"

        with open( hFilepath, 'wt' ) as myHFile, open( cFilepath, 'wt' ) as myCFile:
            myHFile.write( "// %s\n//\n" % ( hFilepath ) )
            myCFile.write( "// %s\n//\n" % ( cFilepath ) )
            lines = "// This UTF-8 file was automatically generated by BibleBooksCodes.py on %s\n//\n" % datetime.now()
            myHFile.write( lines ); myCFile.write( lines )
            if self.titleString:
                lines = "// %s data\n" % self.titleString
                myHFile.write( lines ); myCFile.write( lines )
            if self.versionString:
                lines = "//  Version: %s\n" % self.versionString
                myHFile.write( lines ); myCFile.write( lines )
            if self.dateString:
                lines = "//  Date: %s\n//\n" % self.dateString
                myHFile.write( lines ); myCFile.write( lines )
            myCFile.write( "//   %i %s loaded from the original XML file.\n//\n\n" % ( len(self.XMLtree), self.treeTag ) )
            myHFile.write( "\n#ifndef %s\n#define %s\n\n" % ( ifdefName, ifdefName ) )
            myCFile.write( '#include "%s"\n\n' % os.path.basename(hFilepath) )

            CHAR = "const unsigned char"
            BYTE = "const int"
            dictInfo = {
                "referenceNumber":("referenceNumber (integer 1..255)",
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

            for dictName,dictData in self._dataDicts.items():
                exportPythonDict( myHFile, myCFile, dictData, dictName, dictInfo[dictName][0], dictInfo[dictName][1] )

            myHFile.write( "#endif // %s\n\n" % ( ifdefName ) )
            myHFile.write( "// end of %s" % os.path.basename(hFilepath) )
            myCFile.write( "// end of %s" % os.path.basename(cFilepath) )
    # end of exportDataToC
# end of _BibleBooksCodesConvertor class


@singleton # Can only ever have one instance
class BibleBooksCodes:
    """
    Class for handling BibleBooksCodes.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.

    Note: BBB is used in this class to represent the three-character referenceAbbreviation.
    """

    def __init__( self ): # We can't give this parameters because of the singleton
        """
        Constructor: 
        """
        self.bbcc = _BibleBooksCodesConvertor()
        self._dataDicts = None # We'll import into this in loadData
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "BibleBooksCodes object"
        result += ('\n' if result else '') + "  Num entries = %i" % ( len(self._dataDicts["referenceAbbreviationDict"]) )
        return result
    # end of __str__

    def loadData( self, XMLFilepath=None ):
        """ Loads the XML data file and imports it to dictionary format (if not done already). """
        if not self._dataDicts: # Don't do this unnecessarily
            if XMLFilepath is not None: logging.warning( "Bible books codes are already loaded -- your given filepath of '%s' was ignored" % XMLFilepath )
            self.bbcc.loadAndValidate( XMLFilepath ) # Load the XML (if not done already)
            self._dataDicts = self.bbcc.importDataToPython() # Get the various dictionaries organised for quick lookup
            del self.bbcc # Now the convertor class (that handles the XML) is no longer needed
        return self
    # end of loadData

    # TODO: Add more useful routines in here

    def isValidReferenceAbbreviation( self, BBB ):
        """ Returns True or False. """
        return BBB in self._dataDicts["referenceAbbreviationDict"]

    def getAllReferenceAbbreviations( self ):
        """ Returns a list of all possible BBB codes. """
        return [BBB for BBB in self._dataDicts["referenceAbbreviationDict"]]
        #return self._dataDicts["referenceAbbreviationDict"].keys() # Why didn't this work?

    def getReferenceNumber( self, BBB ):
        """ Return the referenceNumber 1..255 for the given book code (referenceAbbreviation). """
        return self._dataDicts["referenceAbbreviationDict"][BBB]["referenceNumber"]

    def getOSISAbbreviation( self, BBB ):
        """ Return the OSIS abbrevation string for the given book code (referenceAbbreviation). """
        return self._dataDicts["referenceAbbreviationDict"][BBB]["OSISAbbreviation"]

    def getSwordAbbreviation( self, BBB ):
        """ Return the Sword abbrevation string for the given book code (referenceAbbreviation). """
        return self._dataDicts["referenceAbbreviationDict"][BBB]["SwordAbbreviation"]

    def getExpectedChaptersList( self, BBB ):
        """
        Gets a list with the number of expected chapters for the given book code (referenceAbbreviation).
        The number(s) of expected chapters is left in string form (not int).

        Why is it a list?
            Because some books have alternate possible numbers of chapters depending on the Biblical tradition.
        """
        if BBB not in self._dataDicts["referenceAbbreviationDict"] \
        or "numExpectedChapters" not in self._dataDicts["referenceAbbreviationDict"][BBB] \
        or self._dataDicts["referenceAbbreviationDict"][BBB]["numExpectedChapters"] is None:
            return []

        eC = self._dataDicts["referenceAbbreviationDict"][BBB]["numExpectedChapters"]
        if eC: return [v for v in eC.split(',')]
    # end of getExpectedChaptersList

    def getSingleChapterBooksList( self ):
        """ Gets a list of single chapter book codes. """
        result = []
        for BBB in self._dataDicts["referenceAbbreviationDict"]:
            if self._dataDicts["referenceAbbreviationDict"][BBB]["numExpectedChapters"] is not None \
            and self._dataDicts["referenceAbbreviationDict"][BBB]["numExpectedChapters"] == '1':
                result.append( BBB )
        return result

    def getOSISSingleChapterBooksList( self ):
        """ Gets a list of OSIS single chapter book abbreviations. """
        return [self.getOSISAbbreviation(BBB) for BBB in self.getSingleChapterBooksList()]

    def getAllParatextBooksCodeNumberTriples( self ):
        """
        Return a list of all available Paratext book codes.

        The list contains tuples of: paratextAbbreviation, paratextNumber, referenceAbbreviation
        """
        found, result = [], []
        for BBB, values in self._dataDicts["referenceAbbreviationDict"].items():
            pA = values["ParatextAbbreviation"]
            pN = values["ParatextNumberString"]
            if pA is not None and pN is not None:
                if pA not in found: # Don't want duplicates (where more than one book maps to a single paratextAbbreviation)
                    result.append( (pA, pN, BBB,) )
                    found.append( pA )
        return result
    # end of getAllParatextBooksCodeNumberTriples

    def getEnglishName_NR( self, BBB ): # NR = not recommended
        """
        Returns the first English name for a book.

        Remember: These names are only intended as comments or for some basic module processing.
            They are not intended to be used for a proper international human interface.
            The first one in the list is supposed to be the more common.
        """
        return self._dataDicts["referenceAbbreviationDict"][BBB]["nameEnglish"].split('/',1)[0].strip()
    # end of getEnglishName_NR

    def getEnglishNameList_NR( self, BBB ): # NR = not recommended
        """
        Returns a list of possible English names for a book.

        Remember: These names are only intended as comments or for some basic module processing.
            They are not intended to be used for a proper international human interface.
            The first one in the list is supposed to be the more common.
        """
        names = self._dataDicts["referenceAbbreviationDict"][BBB]["nameEnglish"]
        return [name.strip() for name in names.split('/')]
    # end of getEnglishNameList_NR

    def isOldTestament_NR( self, BBB ): # NR = not recommended
        """ Returns True if the given referenceAbbreviation indicates a European Protestant Old Testament book.
            NOTE: This is not truly international so it's not a recommended function. """
        return 1 <= self.getReferenceNumber(BBB) <= 39
    # end of isOldTestament_NR

    def isNewTestament_NR( self, BBB ): # NR = not recommended
        """ Returns True if the given referenceAbbreviation indicates a European Protestant New Testament book.
            NOTE: This is not truly international so it's not a recommended function. """
        return 40 <= self.getReferenceNumber(BBB) <= 66
    # end of isNewTestament_NR
# end of BibleBooksCodes class


def main():
    """
    Main program to handle command line parameters and then run what they want.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v%s" % ( versionString ) )
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML file to .py and .h/.c formats suitable for directly including into other programs, as well as .json.")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 0: print( "%s V%s" % ( progName, versionString ) )

    if Globals.commandLineOptions.export:
        bbcc = _BibleBooksCodesConvertor().loadAndValidate() # Load the XML
        bbcc.exportDataToPython() # Produce the .py tables
        bbcc.exportDataToJSON() # Produce a json output file
        bbcc.exportDataToC() # Produce the .h and .c tables

    else: # Must be demo mode
        # Demo the convertor object
        bbcc = _BibleBooksCodesConvertor().loadAndValidate() # Load the XML
        print( bbcc ) # Just print a summary

        # Demo the BibleBooksCodes object
        bbc = BibleBooksCodes().loadData() # Doesn't reload the XML unnecessarily :)
        print( bbc ) # Just print a summary
        print( "Esther has %s expected chapters" % (bbc.getExpectedChaptersList("EST")) )
        print( "Apocalypse of Ezra has %s expected chapters" % (bbc.getExpectedChaptersList("EZA")) )
        print( "Names for Genesis are:", bbc.getEnglishNameList_NR("GEN") )
        print( "Names for Sirach are:", bbc.getEnglishNameList_NR('SIR') )
        print( "All BBBs:", bbc.getAllReferenceAbbreviations() )
        print( "PT triples:", bbc.getAllParatextBooksCodeNumberTriples() )
        print( "Single chapter books (and OSIS):\n  %s\n  %s" % (bbc.getSingleChapterBooksList(), bbc.getOSISSingleChapterBooksList()) )
# end of main

if __name__ == '__main__':
    main()
# end of BibleBooksCodes.py
