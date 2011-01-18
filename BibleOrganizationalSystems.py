#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# BibleOrganizationalSystems.py
#
# Module handling BibleOrganizationalSystems.xml to produce C and Python data tables
#   Last modified: 2011-01-18 (also update versionString below)
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
Module handling BibleOrganizationalSystems.xml to produce C and Python data tables.
"""

progName = "Bible Organization Systems handler"
versionString = "0.19"


import logging, os.path
from gettext import gettext as _
from collections import OrderedDict
from xml.etree.cElementTree import ElementTree

from singleton import singleton
import Globals
from ISO_639_3_Languages import ISO_639_3_Languages
from BibleBooksCodes import BibleBooksCodes
from BibleBookOrders import BibleBookOrderSystems, BibleBookOrderSystem
from BiblePunctuationSystems import BiblePunctuationSystems, BiblePunctuationSystem
from BibleVersificationSystems import BibleVersificationSystems, BibleVersificationSystem
from BibleBooksNames import BibleBooksNamesSystems, BibleBooksNamesSystem


allowedTypes = ( "edition", "revision", "translation", "original", ) # NOTE: The order is important here


@singleton # Can only ever have one instance
class _BibleOrganizationalSystemsConverter:
    """
    Class for handling and converting BibleOrganizationalSystems.
    """

    def __init__( self ):
        """
        Constructor: expects the filepath of the source XML file.
        Loads (and crudely validates the XML file) into an element tree.
        """
        self._filenameBase = "BibleOrganizationalSystems"

        # These fields are used for parsing the XML
        self._treeTag = "BibleOrganizationalSystems"
        self._headerTag = "header"
        self._mainElementTag = "BibleOrganizationalSystem"

        # These fields are used for automatically checking/validating the XML
        self._compulsoryAttributes = ( "type", )
        self._optionalAttributes = ()
        self._uniqueAttributes = ()
        self._compulsoryElements = ( "referenceAbbreviation", "languageCode", )
        self._optionalElements = ( "name", "publicationDate", "versificationSystem", "punctuationSystem", "bookOrderSystem", "booksNamesSystem", "derivedFrom", "usesText", )
        self._uniqueElements = ()
        self._allowedMultiple = ( "name", )

        # These are fields that we will fill later
        self.title, self.version, self.date = None, None, None
        self.header, self._XMLtree = None, None
        self.__dataDicts = None

        # Get the data tables that we need for proper checking
        self._ISOLanguages = ISO_639_3_Languages().loadData()
        self._BibleBooksCodes = BibleBooksCodes().loadData()
        self._BibleBookOrderSystems = BibleBookOrderSystems().loadData()
        self._BiblePunctuationSystems = BiblePunctuationSystems().loadData()
        self._BibleVersificationSystems = BibleVersificationSystems().loadData()
        self._BibleBooksNamesSystems = BibleBooksNamesSystems().loadData()
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = ""
        if self.title: result += ('\n' if result else '') + self.title
        if self.version: result += ('\n' if result else '') + "  Version: {}".format( self.version )
        if self.date: result += ('\n' if result else '') + "  Date: {}".format( self.date )
        result += ('\n' if result else '') + "  Num entries = {}".format( len(self._XMLtree) )
        return result
    # end of __str__

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
        Also, extracts some useful elements from the header element.
        """
        assert( XMLFilepath )
        self.XMLFilepath = XMLFilepath
        assert( self._XMLtree is None or len(self._XMLtree)==0 ) # Make sure we're not doing this twice

        if Globals.verbosityLevel > 2: print( _("Loading BibleOrganisationalSystems XML file from '{}'...").format( self.XMLFilepath ) )
        self._XMLtree = ElementTree().parse( self.XMLFilepath )
        assert( self._XMLtree ) # Fail here if we didn't load anything at all

        if self._XMLtree.tag  == self._treeTag:
            header = self._XMLtree[0]
            if header.tag == self._headerTag:
                self.header = header
                self._XMLtree.remove( header )
                if len(header)>1:
                    logging.info( _("Unexpected elements in header") )
                elif len(header)==0:
                    logging.info( _("Missing work element in header") )
                else:
                    work = header[0]
                    if work.tag == "work":
                        self.version = work.find("version").text
                        self.date = work.find("date").text
                        self.title = work.find("title").text
                    else:
                        logging.warning( _("Missing work element in header") )
            else:
                logging.warning( _("Missing header element (looking for '{}' tag)").format( self._headerTag ) )
        else:
            logging.error( _("Expected to load '{}' but got '{}'").format( self._treeTag, self._XMLtree.tag ) )
    # end of _load

    def _validate( self ):
        """
        Check/validate the loaded data.
        """
        assert( self._XMLtree )

        uniqueDict = {}
        for elementName in self._uniqueElements: uniqueDict["Element_"+elementName] = []
        for attributeName in self._uniqueAttributes: uniqueDict["Attribute_"+attributeName] = []

        expectedID = 1
        for j,element in enumerate(self._XMLtree):
            if element.tag == self._mainElementTag:
                # Check compulsory attributes on this main element
                for attributeName in self._compulsoryAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is None:
                        logging.error( _("Compulsory '{}' attribute is missing from {} element in record {}").format( attributeName, element.tag, j ) )
                    if not attributeValue:
                        logging.warning( _("Compulsory '{}' attribute is blank on {} element in record {}").format( attributeName, element.tag, j ) )

                # Check optional attributes on this main element
                for attributeName in self._optionalAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if not attributeValue:
                            logging.warning( _("Optional '{}' attribute is blank on {} element in record {}").format( attributeName, element.tag, j ) )

                # Check for unexpected additional attributes on this main element
                for attributeName in element.keys():
                    attributeValue = element.get( attributeName )
                    if attributeName not in self._compulsoryAttributes and attributeName not in self._optionalAttributes:
                        logging.warning( _("Additional '{}' attribute ('{}') found on {} element in record {}").format( attributeName, attributeValue, element.tag, j ) )

                # Check the attributes that must contain unique information (in that particular field -- doesn't check across different attributes)
                for attributeName in self._uniqueAttributes:
                    attributeValue = element.get( attributeName )
                    if attributeValue is not None:
                        if attributeValue in uniqueDict["Attribute_"+attributeName]:
                            logging.error( _("Found '{}' data repeated in '{}' field on {} element in record {}").format( attributeValue, attributeName, element.tag, j ) )
                        uniqueDict["Attribute_"+attributeName].append( attributeValue )

                ID = element.find("referenceAbbreviation").text

                # Check compulsory elements
                for elementName in self._compulsoryElements:
                    if element.find( elementName ) is None:
                        logging.error( _("Compulsory '{}' element is missing in record with ID '{}' (record {})").format( elementName, ID, j ) )
                    if not element.find( elementName ).text:
                        logging.warning( _("Compulsory '{}' element is blank in record with ID '{}' (record {})").format( elementName, ID, j ) )

                # Check optional elements
                for elementName in self._optionalElements:
                    if element.find( elementName ) is not None:
                        if not element.find( elementName ).text:
                            logging.warning( _("Optional '{}' element is blank in record with ID '{}' (record {})").format( elementName, ID, j ) )

                # Check for unexpected additional elements
                for subelement in element:
                    if subelement.tag not in self._compulsoryElements and subelement.tag not in self._optionalElements:
                        logging.warning( _("Additional '{}' element ('{}') found in record with ID '{}' (record {})").format( subelement.tag, subelement.text, ID, j ) )

                # Check the elements that must contain unique information (in that particular element -- doesn't check across different elements)
                for elementName in self._uniqueElements:
                    if element.find( elementName ) is not None:
                        text = element.find( elementName ).text
                        if text in uniqueDict["Element_"+elementName]:
                            logging.error( _("Found '{}' data repeated in '{}' element in record with ID '{}' (record {})").format( text, elementName, ID, j ) )
                        uniqueDict["Element_"+elementName].append( text )
            else:
                logging.warning( _("Unexpected element: {} in record {}").format( element.tag, j ) )
    # end of _validate

    def importDataToPython( self ):
        """
        Loads (and pivots) the data (not including the header) into suitable Python containers to use in a Python program.
        (Of course, you can just use the elementTree in self._XMLtree if you prefer.)
        """
        assert( self._XMLtree )
        if self.__dataDicts: # We've already done an import/restructuring -- no need to repeat it
            return self.__dataDicts

        # We'll create a number of dictionaries with different elements as the key
        dataDict, indexDict, combinedIndexDict = {}, {}, {}
        for element in self._XMLtree:
            bits = {}
            # Get the required information out of the tree for this element
            # Start with the compulsory elements and type attribute
            referenceAbbreviation = element.find("referenceAbbreviation").text
            bits["referenceAbbreviation"] = referenceAbbreviation
            myType = element.get( "type" )
            bits["type"] = myType
            if myType not in allowedTypes: logging.error( _("Unrecognized '{}' type for '{}' (expected one of {})").format(myType,referenceAbbreviation,allowedTypes) )
            languageCode = element.find("languageCode").text
            if self._ISOLanguages and not self._ISOLanguages.isValidLanguageCode( languageCode ): # Check that we have a valid language code
                logging.error( "Unrecognized '{}' ISO-639-3 language code in '{}' organisational system".format( languageCode, referenceAbbreviation ) )
            bits["languageCode"] = languageCode

            # Now work on the optional elements
            for name in ( "name", "publicationDate", "versificationSystem", "punctuationSystem", "bookOrderSystem", "booksNamesSystem", "derivedFrom", "usesText", ):
                for nameData in element.findall(name):
                    if name in self._allowedMultiple: # Put multiple entries into a list
                        if name not in bits: bits[name] = [nameData.text]
                        else: bits[name].append( nameData.text )
                    else: # Not allowed multiples
                        if name in bits: logging.error( _("Multiple {} elements found in {} {}").format(name, referenceAbbreviation, myType) )
                        bits[name] = nameData.text

            extension = '_' + myType
            extendedRA = referenceAbbreviation if referenceAbbreviation.endswith(extension) else (referenceAbbreviation + extension)
            dataDict[extendedRA] = bits
            if referenceAbbreviation in indexDict: indexDict[referenceAbbreviation].append( extendedRA )
            else: indexDict[referenceAbbreviation] = [extendedRA]
            if referenceAbbreviation in combinedIndexDict: combinedIndexDict[referenceAbbreviation].append( extendedRA )
            else: combinedIndexDict[referenceAbbreviation] = [extendedRA]
            if extendedRA != referenceAbbreviation:
                assert( extendedRA not in combinedIndexDict )
                combinedIndexDict[extendedRA] = [extendedRA]

        if Globals.strictCheckingFlag: # We'll do quite a bit more cross-checking now
            for extendedReferenceAbbreviation,data in dataDict.items():
                #print( extendedReferenceAbbreviation, data )
                systemType = data['type']
                if systemType=='edition':
                    if 'usesText' not in data: logging.error( _("{} edition doesn't specify 'usesText'").format( referenceAbbreviation ) )
                    if data['usesText'] not in indexDict: logging.error( _("{} edition specifies unknown '{}' text in 'usesText' field").format(referenceAbbreviation,data['usesText']) )
                    elif len(indexDict[data['usesText']]) > 1: # it could be ambiguous
                        found = 0
                        for thisType in ('revision','translation','original'): # but not 'edition'
                            usesTextExtended = data['usesText'] + '_' + thisType
                            if usesTextExtended in dataDict:
                                foundOne = usesTextExtended
                                found += 1
                        assert( found > 0 )
                        if found==1: # ah, it's not actually ambiguous
                            if Globals.verbosityLevel > 0: print( _("Adjusted text used for {} from the ambiguous '{}' to the extended name '{}'").format( extendedReferenceAbbreviation, data['usesText'], foundOne ) )
                            data['usesText'] = foundOne
                        else: logging.warning( _("{} edition specifies ambiguous '{}' texts in 'usesText' field").format(referenceAbbreviation,indexDict[data['usesText']]) )
                elif systemType=='revision':
                    if 'derivedFrom' not in data: logging.error( _("{} revision doesn't specify 'derivedFrom'").format( referenceAbbreviation ) )
                    if data['derivedFrom'] not in indexDict: logging.error( _("{} revision specifies unknown '{}' text in 'derivedFrom' field").format(referenceAbbreviation,data['derivedFrom']) )
                    elif len(indexDict[data['derivedFrom']]) > 1: logging.warning( _("{} edition specifies ambiguous '{}' texts in 'derivedFrom' field").format(referenceAbbreviation,indexDict[data['derivedFrom']]) )
                if 'versificationSystem' in data:
                    if not self._BibleVersificationSystems.isValidVersificationSystemName( data['versificationSystem'] ):
                        extra = "\n  Available systems are {}".format( self._BibleVersificationSystems.getAvailableVersificationSystemNames()) if Globals.verbosityLevel > 2 else ''
                        logging.error( _("Unknown '{}' versification system name in {}{}").format(data['versificationSystem'],extendedReferenceAbbreviation,extra) )
                if 'punctuationSystem' in data:
                    if not self._BiblePunctuationSystems.isValidPunctuationSystemName( data['punctuationSystem'] ):
                        extra = "\n  Available systems are {}".format( self._BiblePunctuationSystems.getAvailablePunctuationSystemNames()) if Globals.verbosityLevel > 2 else ''
                        logging.error( _("Unknown '{}' punctuation system name in {}{}").format(data['punctuationSystem'],extendedReferenceAbbreviation,extra) )

        self.__dataDicts = dataDict, indexDict, combinedIndexDict
        return self.__dataDicts
    # end of importDataToPython

    def exportDataToPython( self, filepath=None ):
        """
        Writes the information tables to a .py file that can be cut and pasted into a Python program.
        """
        def exportPythonDict( theFile, theDict, dictName, keyComment, fieldsComment ):
            """Exports theDict to theFile."""
            theFile.write( "{} = {{\n  # Key is {}\n  # Fields are: {}\n".format( dictName, keyComment, fieldsComment ) )
            for dictKey in sorted(theDict.keys()):
                theFile.write( '  {}: {},\n'.format( repr(dictKey), theDict[dictKey] ) )
            theFile.write( "}}\n# end of {}\n\n".format( dictName ) )
        # end of exportPythonDict

        from datetime import datetime

        assert( self._XMLtree )
        self.importDataToPython()
        assert( self.__dataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self._filenameBase + "_Tables.py" )
        if Globals.verbosityLevel > 1: print( _("Exporting to {}...").format( filepath ) )

        dataDict, indexDict, combinedIndexDict = self.importDataToPython()
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "# {}\n#\n".format( filepath ) )
            myFile.write( "# This UTF-8 file was automatically generated by BibleOrganizationalSystemsConverter.py V{} on {}\n#\n".format( versionString, datetime.now() ) )
            if self.title: myFile.write( "# {}\n".format( self.title ) )
            if self.version: myFile.write( "#  Version: {}\n".format( self.version ) )
            if self.date: myFile.write( "#  Date: {}\n#\n".format( self.date ) )
            myFile.write( "#   {} {} entries loaded from the original XML file.\n".format( len(self._XMLtree), self._treeTag ) )
            #myFile.write( "#   {} {} loaded from the original XML files.\n#\n\n".format( len(self.systems), self._treeTag ) )
            exportPythonDict( myFile, dataDict, "dataDict", "extendedReferenceAbbreviation", "referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            exportPythonDict( myFile, indexDict, "indexDict", "referenceAbbreviation", "id, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            exportPythonDict( myFile, combinedIndexDict, "combinedIndexDict", "referenceAbbreviation", "id, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
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
        assert( self.__dataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self._filenameBase + "_Tables.json" )
        if Globals.verbosityLevel > 1: print( _("Exporting to {}...").format( filepath ) )
        with open( filepath, 'wt' ) as myFile:
            #myFile.write( "# {}\n#\n".format( filepath ) ) # Not sure yet if these comment fields are allowed in JSON
            #myFile.write( "# This UTF-8 file was automatically generated by BibleBooksCodes.py V{} on {}\n#\n".format( versionString, datetime.now() ) )
            #if self.titleString: myFile.write( "# {} data\n".format( self.titleString ) )
            #if self.versionString: myFile.write( "#  Version: {}\n".format( self.versionString ) )
            #if self.dateString: myFile.write( "#  Date: {}\n#\n".format( self.dateString ) )
            #myFile.write( "#   {} {} loaded from the original XML file.\n#\n\n".format( len(self._XMLtree), self._treeTag ) )
            json.dump( self.__dataDicts, myFile, indent=2 )
            #myFile.write( "\n\n# end of {}".format( os.path.basename(filepath) ) )
    # end of exportDataToJSON

    def exportDataToC( self, filepath=None ):
        """
        Writes the information tables to a .h file that can be included in c and c++ programs.
        """
        raise Exception( "C export not written yet" )
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
                    else: logging.error( _("Cannot convert unknown field type '{}' in entry '{}'").format( field, entry ) )
                return result

            theFile.write( "static struct {} {}[] = {\n  // Fields are {}\n".format( structName, dictName, fieldsComment ) )
            for entry in sorted(theDict.keys()):
                if isinstance( entry, str ):
                    theFile.write( "  {\"{}\", {}},\n".format( entry, convertEntry(theDict[entry]) ) )
                elif isinstance( entry, int ):
                    theFile.write( "  {{}, {}},\n".format( entry, convertEntry(theDict[entry]) ) )
                else:
                    logging.error( _("Can't handle this type of data yet: {}").format( entry ) )
            theFile.write( "}; // {}\n\n".format( dictName) )
        # end of exportPythonDict

        from datetime import datetime

        assert( self._XMLtree )
        self.importDataToPython()
        assert( self.__dataDicts )

        if not filepath: filepath = os.path.join( "DerivedFiles", self._filenameBase + "_Tables.h" )
        if Globals.verbosityLevel > 1: print( _("Exporting to {}...").format( filepath ) )

        IDDict, RADict, SBLDict, OADict, PADict, PNDict = self.importDataToPython()
        ifdefName = self._filenameBase.upper() + "_Tables_h"
        with open( filepath, 'wt' ) as myFile:
            myFile.write( "// {}\n//\n".format( filepath ) )
            myFile.write( "// This UTF-8 file was automatically generated by BibleOrganizationalSystemsConverter.py V{} on {}\n//\n".format( versionString, datetime.now() ) )
            if self.title: myFile.write( "// {}\n".format( self.title ) )
            if self.version: myFile.write( "//  Version: {}\n".format( self.version ) )
            if self.date: myFile.write( "//  Date: {}\n//\n".format( self.date ) )
            myFile.write( "//   {} {} loaded from the original XML file.\n//\n\n".format( len(self._XMLtree), self._treeTag ) )
            myFile.write( "#ifndef {}\n#define {}\n\n".format( ifdefName, ifdefName ) )
            exportPythonDict( myFile, IDDict, "IDDict", "{int id; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "id (sorted), referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, nameEnglish (comment only)" )
            exportPythonDict( myFile, RADict, "RADict", "{char* refAbbrev; int id; char* SBLAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "referenceAbbreviation (sorted), SBLAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, SBLDict, "SBLDict", "{char* SBLAbbrev; int id; char* refAbbrev; char* OSISAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "SBLAbbreviation (sorted), ReferenceAbbreviation, OSISAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, OADict, "OADict", "{char* OSISAbbrev; int id; char* refAbbrev; char* SBLAbbrev; char* PTAbbrev; char* PTNum; char* EngName;}", "OSISAbbreviation (sorted), ReferenceAbbreviation, SBLAbbreviation, ParatextAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, PADict, "PADict", "{char* PTAbbrev; int id; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* PTNum; char* EngName;}", "ParatextAbbreviation (sorted), referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, ParatextNumberString, id, nameEnglish (comment only)" )
            exportPythonDict( myFile, PNDict, "PNDict", "{char* PTNum; int id; char* PTAbbrev; char* refAbbrev; char* SBLAbbrev; char* OSISAbbrev; char* EngName;}", "ParatextNumberString (sorted), ParatextAbbreviation, referenceAbbreviation, SBLAbbreviation, OSISAbbreviation, id, nameEnglish (comment only)" )
            myFile.write( "#endif // {}\n".format( ifdefName ) )
    # end of exportDataToC
# end of _BibleOrganizationalSystemsConverter class


@singleton # Can only ever have one instance
class BibleOrganizationalSystems:
    """
    Class for handling BibleOrganizationalSystems.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.
    """

    def __init__( self ): # We can't give this parameters because of the singleton
        """
        Constructor: 
        """
        self.__bosc = _BibleOrganizationalSystemsConverter()
        self.__dataDict = self.__indexDict = self.__combinedIndexDict = None # We'll import into this in loadData
    # end of __init__

    def loadData( self, XMLFilepath=None ):
        """ Loads the XML data file and imports it to dictionary format (if not done already). """
        if not self.__dataDict or not self.__indexDict: # Don't do this unnecessarily
            if XMLFilepath is not None: logging.warning( _("Bible books codes are already loaded -- your given filepath of '{}' was ignored").format( XMLFilepath ) )
            self.__bosc.loadAndValidate( XMLFilepath ) # Load the XML (if not done already)
            result = self.__bosc.importDataToPython() # Get the various dictionaries organised for quick lookup
            if result is not None:
                self.__dataDict, self.__indexDict, self.__combinedIndexDict = result
            del self.__bosc # Now the converter class (that handles the XML) is no longer needed
        return self
    # end of loadData

    def __str__( self ):
        """
        This method returns the string representation of a Bible organisational system.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "BibleOrganizationalSystems object"
        result += ('\n' if result else '') + "  Num entries = {}".format( len(self.__dataDict) )
        if Globals.verbosityLevel > 1: # Do a bit of extra analysis
            counters = {}
            for possibleType in allowedTypes: counters[possibleType] = 0
            for systemName, data in self.__dataDict.items():
                counters[data["type"]] += 1
            for possibleType in allowedTypes:
                if counters[possibleType]: result += "    {} {}(s)".format( counters[possibleType], possibleType )
        return result
    # end of __str__

    def getAvailableOrganizationalSystemNames( self, extended=False ):
        """ Returns a list of available system name strings. """
        if extended:
            result = []
            for x in self.__indexDict:
                result.append( "{} ({})".format(x, self.__dataDict[self.indexDict[x]]['type'] ) )
            return result
        # else:
        return [x for x in self.__indexDict]
    # end of getAvailableOrganizationalSystemNames

    def getOrganizationalSystem( self, systemName ):
        """ Returns the system dictionary.
            Accepts combined names (like KJV-1611_edition) or basic names (like KJV-1611). """
        assert( systemName )
        if systemName in self.__dataDict: # we found the combined name
            return self.__dataDict[systemName]
        # else
        if systemName in self.__indexDict:
            index = self.__indexDict[systemName]
            if len(index) == 1: # Must only be one (unique) entry
                return self.__dataDict[ index[0] ]
            # else it's an ambiguous name that has multiple matches
            for possibleType in allowedTypes: # Steps through in priority order
                x = systemName + '_' + possibleType
                if x in self.__dataDict: return self.__dataDict[x]  
        # else
        logging.error( _("No '{}' system in Bible Organisational Systems").format( systemName ) )
        if Globals.verbosityLevel>2: logging.error( _("Available systems are {}").format( self.getAvailableSystemNames( extended=True ) ) )
    # end of getOrganizationalSystem

    def getOrganizationalSystemValue( self, systemName, valueName ):
        """ Gets a value for the system. """
        assert( systemName )
        assert( valueName )
        thisSystem = self.getOrganizationalSystem( systemName )
        if thisSystem is not None:
            assert( thisSystem )
            if valueName in thisSystem: return thisSystem[valueName]
            # else maybe we can find the value in a derived text
            if 'usesText' in thisSystem:
                trySystemName = thisSystem['usesText']
                #print( "w1", "{} is trying usesText of {}".format(systemName,trySystemName) )
                #print( "\nKeys:", self.__dataDict.keys() )
                #print( "\nindexDict", self.__indexDict )
                #print( "\ncombinedIndexDict", self.__combinedIndexDict )
                #halt
                result = self.getOrganizationalSystemValue( trySystemName, valueName )
                if result is not None: return result
            # else we couldn't find it anywhere
            logging.error( _("{} Bible Organizational System has no {} specified").format(self.getOrganizationalSystemName(),valueName) )
    # end of getOrganizationalSystemValue
# end of BibleOrganizationalSystems class


class BibleOrganizationalSystem( BibleBookOrderSystem, BibleVersificationSystem, BiblePunctuationSystem, BibleBooksNamesSystem ):
    """
    Class for handling a BibleOrganizationalSystem.

    It is based on a number of system classes.

    This class doesn't deal at all with XML, only with Python dictionaries, etc.
    """

    def __init__( self, systemName ):
        """
        Constructor: 
        """
        self.__boss = BibleOrganizationalSystems().loadData() # Doesn't reload the XML unnecessarily :)
        result = self.__boss.getOrganizationalSystem( systemName )
        if result is None:
            self.__dataDict = self.__systemName = None
            return

        # else:
        self.__dataDict = result
        self.__systemName = systemName
        #print( self.__dataDict )

        # Now initialize the inherited classes
        value1 = self.getOrganizationalSystemValue( 'bookOrderSystem' )
        if value1: BibleBookOrderSystem.__init__( self, value1 )
        value2 = self.getOrganizationalSystemValue( 'versificationSystem' )
        if value2: BibleVersificationSystem.__init__( self, value2 )
        value3 = self.getOrganizationalSystemValue( 'punctuationSystem' )
        if value3: BiblePunctuationSystem.__init__( self, value3 )
        value4 = self.getOrganizationalSystemValue( 'booksNamesSystem' )
        if value4: BibleBooksNamesSystem.__init__( self, value4, BibleBookOrderSystem.getBookList(self) ) # Does one extra step To create the input abbreviations
    # end of __init__

    def __str__( self ):
        """
        This method returns the string representation of a Bible organisational system.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = "BibleOrganizationalSystem object"
        if self.__systemName is not None: result += ('\n' if result else '') + "  {} Bible organisational system".format( self.__systemName )
        if self.__dataDict is not None:
            result += ('\n' if result else '') + "  Type = {}".format( self.__dataDict["type"] )
            result += ('\n' if result else '') + "  Name(s) = {}".format( self.__dataDict["name"] )
            result += ('\n' if result else '') + "  Num entry lines = {}".format( len(self.__dataDict) )
            if Globals.verbosityLevel > 3: result += ('\n' if result else '') + "  Entries are: {}".format( self.__dataDict )
        return result
    # end of __str__

    def getOrganizationalSystemName( self ):
        """ Return the system name. """
        assert( self.__systemName )
        return self.__systemName
    # end of getOrganizationalSystemName

    def getOrganizationalSystemType( self ):
        """ Return the system type. """
        assert( self.__dataDict )
        return self.__dataDict["type"]
    # end of getOrganizationalSystemType

    def getMoreBasicTypes( self ):
        """ Returns a list of more basic (original) types. """
        ix = allowedTypes.index( self.__dataDict["type"] )
        return allowedTypes[ix+1:]
    # end of getMoreBasicTypes

    def getOrganizationalSystemValue( self, valueName ):
        """ Gets a value for the system. """
        assert( self.__dataDict )
        if valueName in self.__dataDict: return self.__dataDict[valueName]
        # else maybe we can find the value in a derived text
        #print( "q0", self.getOrganizationalSystemName() )
        for tryType in self.getMoreBasicTypes():
            if 'usesText' in self.__dataDict:
                trySystemName = self.__dataDict['usesText']
                #print( "q1", "{} is trying usesText of {}".format(self.__systemName,trySystemName) )
                result = self.__boss.getOrganizationalSystemValue( trySystemName, valueName )
                if result is not None: return result
            if 'derivedFrom' in self.__dataDict:
                trySystemName = self.__dataDict['derivedFrom']
                #print( "q2", "{} is trying derivedFrom of {}".format(self.__systemName,trySystemName) )
                result = self.__boss.getOrganizationalSystemValue( trySystemName, valueName )
                if result is not None: return result
        # else we couldn't find it anywhere
        logging.error( _("{} Bible Organizational System has no {} specified").format(self.getOrganizationalSystemName(),valueName) )
    # end of getOrganizationalSystemValue

    def isValidBCVRef( self, referenceTuple, referenceString, wantErrorMessages=False ):
        """ Returns True/False indicating if the given reference is valid in this system. """
        BBB, C, V, S = referenceTuple
        if BibleBookOrderSystem.containsBook( self, BBB ):
            return BibleVersificationSystem.isValidBCVRef( self, referenceTuple, referenceString, wantErrorMessages )
        elif wantErrorMessages: logging.error( _("{} {}:{} is invalid book for reference '{}' in {} versification system for {}").format(BBB,C,V,referenceString, self.getBookOrderSystemName(),self.getOrganizationalSystemName()) )
        return False
# end of BibleOrganizationalSystem class


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
        bosc = _BibleOrganizationalSystemsConverter().loadAndValidate()
        bosc.exportDataToPython() # Produce the .py tables
        bosc.exportDataToJSON() # Produce a json output file
        bosc.exportDataToC() # Produce the .h and .c tables

    else: # Must be demo mode
        # Demo the converter object
        bosc = _BibleOrganizationalSystemsConverter().loadAndValidate()
        print( bosc ) # Just print a summary

        # Demo the BibleOrganizationalSystems object
        boss = BibleOrganizationalSystems().loadData() # Doesn't reload the XML unnecessarily :)
        print( boss ) # Just print a summary
        print( _("Available system names are: {}").format( boss.getAvailableOrganizationalSystemNames() ) )

        # Demo a BibleBookOrder object -- this is the one most likely to be wanted by a user
        bos = BibleOrganizationalSystem( "KJV-1611_edition" )
        print( bos ) # Just print a summary
        print( "Book list is {}".format( bos.getBookList() ) )
        print( "This type is {}. More basic types are: {}".format(bos.getOrganizationalSystemType(),bos.getMoreBasicTypes()) )
        for test in ('GEN','Gen','MAT','Mat','Mt','JUD','Jud','JDE'):
            print( "Contains '{}': {}".format(test, bos.containsBook(test) ) )
        for test in ('GEN','Gen','MAT','Mat','Mt','JUD','Jud','Jde'):
            print( "'{}' gives {}".format(test,bos.getBBB(test) ) )
# end of main

if __name__ == '__main__':
    main()
# end of BibleOrganizationalSystems.py
