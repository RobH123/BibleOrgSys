#!/usr/bin/python3
#
# USFMBible.py
#
# Module handling the USFM markers for Bible books
#   Last modified: 2010-12-18 (also update versionString below)
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
Module for defining and manipulating USFM Bible markers.
"""

progName = "USFM Bible handler"
versionString = "0.02"


import os, logging, datetime
from collections import OrderedDict

from singleton import singleton
import Globals, ControlFiles
from BibleBooksCodes import BibleBooksCodes


# Globals
USFMVersion = "2.2"


# Line markers
ProjectMarkers = ( 'id', 'ide', 'sts', 'rem', 'h' )
IntroductionMarkers = ( 'toc1', 'toc2', 'toc3', 'imt1', 'is1', 'ip', 'ipi', 'im', 'imi', 'ipq', 'imq', 'ipr', 'iq1', 'iq2', 'ib', 'ili', 'iot', 'io1', 'io2', 'ior', 'iex', 'ie' )
HeaderMarkers = ( 'mt1', 'mt2', 'mt3', 'mte1', 'mte2' )
TextMarkers = ( 'ms1', 'ms2', 'mr', 's1', 's2', 'sr', 'r', 'd', 'sp', 'p', 'v', 'q1', 'q2', 'q3', 'm', 'b' )
AllParagraphMarkers = ProjectMarkers + IntroductionMarkers + HeaderMarkers + TextMarkers


# Character markers
IntroductionCharacterMarkers = ( 'iqt' )
HeaderCharacterMarkers = ( 'rq' )
AllCharacterMarkers = IntroductionCharacterMarkers + HeaderCharacterMarkers

AllLineMarkers = AllParagraphMarkers + ('c', 's', 'li', 'li1', 'li2', 'li3', 'pc', 'pi', 'tr', 'nb', 's3', 'cp', 'mt4', 'qc', 'pr', 'ps', 'mi', 'qr', 'f', 'cl', 'x', 'qs', 'ph', 'phi', 'restore') # Temp


MarkerDB = { # marker: ( status code, text code, name, type, occurs, details )
    # Status code = C:compulsory, O:optional
    # Text code = M:must, N:never, C:can contain text, D:digits only
# Identification
    'id': ( 'C', 'M', "File identification", "paragraph", "Introduction", "This is the initial USFM marker in any scripture text file" ),
    'ide': ( 'O', 'M', "An optional character encoding specification", "paragraph", "Introduction", "This marker should be used to specify the character encoding of the text within the file" ),
    'sts': ( 'O', 'M', "Project status tracking", "paragraph", "Introduction", "The contents of the status marker can be defined by the downstream system being used to track project status" ),
    'rem': ( 'O', 'M', "Used for adding brief comments by a translator, consultant, or support person", "paragraph", "Introduction", "" ),
    'h': ( 'C', 'M', "Running header text", "paragraph", "Introduction", "" ),
    'toc1': ( 'O', 'M', "Long table of contents text", "paragraph", "Introduction", "" ),
    'toc2': ( 'O', 'M', "Short table of contents text", "paragraph", "Introduction", "" ),
    'toc3': ( 'O', 'M', "Book abbreviation", "paragraph", "Introduction", "" ),
# Introductions
    'imt': ( 'O', 'M', "Introduction main title", "paragraph", "Introduction", "" ),
    'is': ( 'O', 'M', "Introduction section heading", "paragraph", "Introduction", "" ),
    'ip': ( 'O', 'M', "Introduction paragraph", "paragraph", "Introduction", "" ),
    'ipi': ( 'O', 'M', "Indented introduction paragraph", "paragraph", "Introduction", "" ),
    'im': ( 'O', 'M', "Introduction flush left (margin) paragraph", "paragraph", "Introduction", "" ),
    'imi': ( 'O', 'M', "Introduction flush left (margin) paragraph", "paragraph", "Introduction", "" ),
    'ipq': ( 'O', 'M', "Introduction quote from text paragraph", "paragraph", "Introduction", "" ),
    'imq': ( 'O', 'M', "Introduction flush left (margin) quote from text paragraph", "paragraph", "Introduction", "" ),
    'ipr': ( 'O', 'M', "Introduction right-aligned paragraph", "paragraph", "Introduction", "Typically used for a quote from text reference" ),
    'iq': ( 'O', 'M', "Introduction poetic line", "paragraph", "Introduction", "" ),
    'ib': ( 'O', 'N', "Introduction blank line", "paragraph", "Introduction", "May be used to explicitly indicate additional white space between paragraphs" ),
    'ili': ( 'O', 'M', "Introduction list item", "paragraph", "Introduction", "" ),
    'iot': ( 'O', 'M', "Introduction outline title", "paragraph", "Introduction", "" ),
    'io': ( 'O', 'M', "Introduction outline entry", "paragraph", "Introduction", "The outline entry typically ends with a range of references in parentheses" ),
    'iot': ( 'O', 'M', "Introduction outline title", "paragraph", "Introduction", "" ),
    'ior': ( 'O', 'M', "Introduction outline reference range", "paragraph", "Introduction", "An outline entry typically ends with a range of references in parentheses. This is an optional character style for marking (and potentially formatting) these references separately" ),
    'iex': ( 'O', 'M', "Introduction explanatory or bridge text", "paragraph", "Introduction", "e.g. explanation of missing book in a short Old Testament" ),
    'iqt': ( 'O', 'M', "Introduction quoted text", "character", "Introduction", "Scripture quotations, or other quoted text, appearing in the introduction" ),
    'imte': ( 'O', 'M', "Introduction major title ending", "paragraph", "Introduction", "Used to mark a major title indicating the end of the introduction" ),
    'ie': ( 'O', 'M', "Introduction end", "paragraph", "Introduction", "Optionally included to explicitly indicate the end of the introduction material" ),
# Titles, headings, and labels
    'b': ( 'O', 'N', "Blank line", "paragraph", "Text", "May be used to explicitly indicate additional white space between paragraphs" ),
# TODO: To be completed....
}

MarkerConversions = {
    'imt' : 'imt1',
    'is' : 'is1',
    'iq' : 'iq1',
    'ili' : 'ili1',
    'io' : 'io1',
    'imte' : 'imte1',
    'mt' : 'mt1',
    'mte' : 'mte1',
    'ms' : 'ms1',
    's' : 's1',
    'q' : 'q1',
}

MarkerBackConversions = {
    'imt1' : 'imt', 'imt2' : 'imt',
    'is1' : 'is', 'is2' : 'is',
    'iq1' : 'iq', 'iq2' : 'iq',
    'ili1' : 'ili', 'ili2' : 'ili',
    'io1' : 'io', 'io2' : 'io',
    'imte1' : 'imte', 'imte2' : 'imte',
    'mt1' : 'mt', 'mt2' : 'mt', 'mt3' : 'mt',
    'mte1' : 'mte', 'mte2' : 'mte',
    'ms1' : 'ms', 'ms2' : 'ms',
    's1' : 's', 's2' : 's',
    'q1' : 'q', 'q2' : 'q',
}


class USFMBibleBook:
    """
    Class to load and manipulate a single USFM file / book.
    """

    def __init__( self ):
        """
        Create the object.
        """
        self.lines = []
    # end of __init_

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = ""
        if self.bookReferenceCode: result += ('\n' if result else '') + self.bookReferenceCode
        if self.sourceFilepath: result += ('\n' if result else '') + "From: " + self.sourceFilepath
        result += ('\n' if result else '') + "Num lines = " + str(len(self.lines))
        return result
    # end of __str__

    def load( self, bookReferenceCode, folder, filename, encoding='utf-8' ):
        """
        Load the book from a file.
        """
        import SFMFile

        logging.info( "  Loading %s..." % ( filename ) )
        self.bookReferenceCode = bookReferenceCode
        self.sourceFolder = folder
        self.sourceFilename = filename
        self.sourceFilepath = os.path.join( folder, filename )
        originalBook = SFMFile.SFMLines()
        originalBook.read( self.sourceFilepath, encoding=encoding )

        # Do a little cleaning up before we save the data
        for marker,text in originalBook.lines:
            if marker in MarkerConversions:
                marker = MarkerConversions[marker]
            self.lines.append( (marker, text,) )
    # end of load

    def validateUSFM( self ):
        """
        Validate the loaded book.
        """
        assert( self.lines )

        for marker,text in self.lines:
            #print( marker, text )
            if marker not in AllLineMarkers:
                logging.warning( "Unexpected '%s' paragraph marker in Bible book %s (Text is '%s')" % ( marker, self.bookReferenceCode, text ) )
    # end of load

    def getVersification( self ):
        """
        Get the versification of the book into a two lists of (c, v) tuples.
            The first list contains an entry for each chapter in the book showing the number of verses.
            The second list contains an entry for each missing verse in the book (not including verses that are missing at the END of a chapter).
        Note that all chapter and verse values are returned as strings not integers.
        """
        assert( self.lines )

        versification, omittedVerses = [], []
        chapterText, chapterNumber, lastChapterNumber = '0', 0, 0
        verseText, verseNumber, lastVerseNumber = '0', 0, 0
        for marker,text in self.lines:
            #print( marker, text )
            if marker == 'c':
                if chapterNumber > 0:
                    versification.append( (chapterText, str(lastVerseNumber),) )
                chapterText = text.strip()
                if ' ' in chapterText:
                    logging.warning( "Unexpected space in USFM chapter number field '%s' after chapter %i of %s" % ( chapterText, lastChapterNumber, self.bookReferenceCode ) )
                    chapterText = chapterText.split( None, 1)[0]
                #print( "%s chapter %s" % ( self.bookReferenceCode, chapterText ) )
                chapterNumber = int( chapterText)
                if chapterNumber != lastChapterNumber+1:
                    logging.error( "USFM chapter numbers out of sequence in Bible book %s (%i after %i)" % ( self.bookReferenceCode, chapterNumber, lastChapterNumber ) )
                lastChapterNumber = chapterNumber
                verseText, verseNumber, lastVerseNumber = '0', 0, 0
            elif marker == 'v':
                if not text:
                    logging.warning( "Missing USFM verse number after %i in chapter %i of %s" % ( lastVerseNumber, chapterNumber, self.bookReferenceCode ) )
                    continue
                try:
                    verseText = text.split( None, 1 )[0]
                except:
                    print( "verseText is '%s'" % verseText )
                    halt
                doneWarning = False
                for char in 'abcdefghijklmnopqrstuvwxyz[]()\\':
                    if char in verseText:
                        if not doneWarning:
                            logging.info( "Removing letter(s) from USFM verse number %s in Bible book %s %s" % ( verseText, self.bookReferenceCode, chapterText ) )
                            doneWarning = True
                        verseText = verseText.replace( char, '' )
                if '-' or '–' in verseText: # we have a range like 7-9 with hyphen or en-dash
                    bits = verseText.replace('–','-').split( '-', 1 ) # Make sure that it's a hyphen then split once
                    verseNumber = bits[0]
                    endVerseNumber = bits[1]
                    if int(verseNumber) >= int(endVerseNumber):
                        logging.error( "USFM verse range out of sequence in Bible book %s %s (%s-%s)" % ( self.bookReferenceCode, chapterText, verseNumber, endVerseNumber ) )
                elif ',' in verseText: # we have a range like 7,8
                    bits = verseText.split( ',', 1 )
                    verseNumber = bits[0]
                    endVerseNumber = bits[1]
                    if int(verseNumber) >= int(endVerseNumber):
                        logging.error( "USFM verse range out of sequence in Bible book %s %s (%s-%s)" % ( self.bookReferenceCode, chapterText, verseNumber, endVerseNumber ) )
                else: # Should be just a single verse number
                    verseNumber = verseText
                    endVerseNumber = verseNumber
                if int(verseNumber) != int(lastVerseNumber)+1:
                    if int(verseNumber) <= int(lastVerseNumber):
                        logging.warning( "USFM verse numbers out of sequence in Bible book %s %s (%s after %s)" % ( self.bookReferenceCode, chapterText, verseText, lastVerseNumber ) )
                    else: # Must be missing some verse numbers
                        logging.info( "Missing USFM verse number(s) between %s and %s in Bible book %s %s" % ( lastVerseNumber, verseNumber, self.bookReferenceCode, chapterText ) )
                        for number in range( int(lastVerseNumber)+1, int(verseNumber) ):
                            omittedVerses.append( (chapterText, str(number),) )
                lastVerseNumber = endVerseNumber
        versification.append( (chapterText, str(lastVerseNumber),) ) # Append the verse count for the final chapter
        return versification, omittedVerses
    # end of getVersification
# end of class USFMBibleBook


class USFMBible:
    """
    Class to load and manipulate USFMBibles.

    """
    def __init__( self, name ):
        """
        Create the object.
        """
        self.name = name
        self.books = OrderedDict()

        self.BibleBooksCodes = BibleBooksCodes().loadData()
        self.OneChapterBBBBookCodes = self.BibleBooksCodes.getSingleChapterBooksList()
        self.OneChapterOSISBookCodes = self.BibleBooksCodes.getOSISSingleChapterBooksList()
    # end of __init_

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = ""
        if self.name: result += ('\n' if result else '') + self.name
        if self.sourceFolder: result += ('\n' if result else '') + "  From: " + self.sourceFolder
        result += ('\n' if result else '') + "  Num books = " + str(len(self.books))
        return result
    # end of __str__

    def load( self, folder, encoding='utf-8' ):
        """
        Load the books.
        """
        import USFMFilenames
        fileList = USFMFilenames.USFMFilenames( folder ).actualFiles()

        logging.info( "Loading %s from %s..." % ( self.name, folder ) )
        self.sourceFolder = folder
        for bookReferenceCode,filename in fileList:
            book = USFMBibleBook()
            book.load( bookReferenceCode, folder, filename, encoding )
            book.validateUSFM()
            #print( book )
            self.books[bookReferenceCode] = book
    # end of load

    def getVersification( self ):
        """
        Get the versification of the Bible into two ordered dictionaries with the referenceAbbreviation as key.
            Entries in both are lists of tuples, being (c, v).
            The first list contains an entry for each chapter in the book showing the number of verses.
            The second list contains an entry for each missing verse in the book (not including verses that are missing at the END of a chapter).
        """
        assert( self.books )
        totalVersification, totalOmittedVerses = OrderedDict(), OrderedDict()
        for bookReferenceCode in self.books.keys():
            versification, omittedVerses = self.books[bookReferenceCode].getVersification()
            totalVersification[bookReferenceCode] = versification
            if omittedVerses:
                totalOmittedVerses[bookReferenceCode] = omittedVerses
        return totalVersification, totalOmittedVerses
    # end of getVersification

    def toZefania_XML( self, controlFileFolder, controlFilename ):
        """
        Using settings from the given control file,
            converts the USFM information to a UTF-8 Zefania XML file.

        This format is roughly documented at http://de.wikipedia.org/wiki/Zefania_XML
            but more fields can be discovered by looking at downloaded files.
        """
        ZefaniaControls = {}
        # Get the data tables that we need for proper checking
        bbc = BibleBooksCodes.BibleBooksCodesConvertor()
        junk, BBC_BBBDict, junk, BBC_OADict, junk, junk, junk, junk, junk, junk, BBC_NameDict = bbc.importDataToPython()

        def NL( section ):
            """Returns a newline character if required (else an empty string)."""
            if ZefaniaControls["ZefaniaHumanReadable"] == "None": return ''
            if ZefaniaControls["ZefaniaHumanReadable"] == "All": return '\n'
            # Else, we'll assume that it's set to "Header"
            if section > 2: return '' # (not header)
            return '\n' # for header
        # end of NL

        def SP( section, level ):
            """Returns a newline character if required (else an empty string)."""
            spaceFactor = 5 # This many spaces indent for each level
            if ZefaniaControls["ZefaniaHumanReadable"] == "None": return ''
            if ZefaniaControls["ZefaniaHumanReadable"] == "All": return ' '*level*spaceFactor
            # Else, we'll assume that it's set to "Header"
            if section > 2: return '' # (not header)
            return ' '*level*spaceFactor # for header
        # end of SP

        def writeHeader( outputFile ):
            """Writes the Zefania header to the Zefania XML outputFile."""
            outputFile.write( SP(0,0) + '<?xml version="1.0" encoding="UTF-8"?>' + NL(0) )
# TODO: Some modules have <XMLBIBLE xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="zef2005.xsd" version="2.0.1.18" status="v" revision="1" type="x-bible" biblename="KJV+">
            outputFile.write( SP(0,0) + '<XMLBible xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" type="x-bible" biblename="%s">\n' % ZefaniaControls["ZefaniaBibleName"] )
            outputFile.write( SP(2,1) + '<INFORMATION>' + NL(2) )
            if "ZefaniaTitle" in ZefaniaControls and ZefaniaControls["ZefaniaTitle"]: outputFile.write( SP(2,2) + '<title>%s</title>' % ZefaniaControls["ZefaniaTitle"] + NL(2) )
            if "ZefaniaSubject" in ZefaniaControls and ZefaniaControls["ZefaniaSubject"]: outputFile.write( SP(2,2) + '<subject>%s</subject>' % ZefaniaControls["ZefaniaSubject"] + NL(2) )
            if "ZefaniaDescription" in ZefaniaControls and ZefaniaControls["ZefaniaDescription"]: outputFile.write( SP(2,2) + '<description>%s</description>' % ZefaniaControls["ZefaniaDescription"] + NL(2) )
            if "ZefaniaPublisher" in ZefaniaControls and ZefaniaControls["ZefaniaPublisher"]: outputFile.write( SP(2,2) + '<publisher>%s</publisher>' % ZefaniaControls["ZefaniaPublisher"] + NL(2) )
            if "ZefaniaContributors" in ZefaniaControls and ZefaniaControls["ZefaniaContributors"]: outputFile.write( SP(2,2) + '<contributors>%s</contributors>' % ZefaniaControls["ZefaniaContributors"] + NL(2) )
            if "ZefaniaIdentifier" in ZefaniaControls and ZefaniaControls["ZefaniaIdentifier"]: outputFile.write( SP(2,2) + '<identifier>%s</identifier>' % ZefaniaControls["ZefaniaIdentifier"] + NL(2) )
            if "ZefaniaSource" in ZefaniaControls and ZefaniaControls["ZefaniaSource"]: outputFile.write( SP(2,2) + '<identifier>%s</identifier>' % ZefaniaControls["ZefaniaSource"] + NL(2) )
            if "ZefaniaCoverage" in ZefaniaControls and ZefaniaControls["ZefaniaCoverage"]: outputFile.write( SP(2,2) + '<coverage>%s</coverage>' % ZefaniaControls["ZefaniaCoverage"] + NL(2) )
            outputFile.write( SP(2,2) + '<format>Zefania XML Bible Markup Language</format>' + NL(2) )
            outputFile.write( SP(2,2) + '<date>%s</date>' % datetime.datetime.now().date().isoformat() + NL(3) )
            outputFile.write( SP(2,2) + '<creator>USFMBible.py</creator>' + NL(2) )
            outputFile.write( SP(2,2) + '<type>bible text</type>' + NL(2) )
            if "ZefaniaLanguage" in ZefaniaControls and ZefaniaControls["ZefaniaLanguage"]: outputFile.write( SP(2,2) + '<language>%s</language>' % ZefaniaControls["ZefaniaLanguage"] + NL(2) )
            if "ZefaniaRights" in ZefaniaControls and ZefaniaControls["ZefaniaRights"]: outputFile.write( SP(2,2) + '<rights>%s</rights>' % ZefaniaControls["ZefaniaRights"] + NL(2) )
            outputFile.write( SP(2,1) + '</INFORMATION>\n' )
        # end of writeHeader

        def closeUp( outputFile ):
            """Writes closing stuff to the Zefania XML outputFile."""
            outputFile.write( SP(0,0) + '</XMLBIBLE>' + NL(0) )
        # end of closeUp

        def writeBook( outputFile, BBB, bkData, level ):
            """Writes a book to the Zefania XML outputFile."""
            outputFile.write( SP(3,level) + '<BIBLEBOOK bnumber="%s" bname="%s" bsname="%s">' % (BBC_BBBDict[BBB][0],BBC_BBBDict[BBB][1],BBC_BBBDict[BBB][2]) + NL(3) )
            haveOpenChapter = False
            for marker,text in bkData.lines:
                if marker=="c":
                    if haveOpenChapter:
                        outputFile.write ( SP(3,level+1) + '</CHAPTER>' + NL(3) )
                    outputFile.write ( SP(3,level+1) + '<CHAPTER cnumber="%s">' % text + NL(3) )
                    haveOpenChapter = True
                elif marker=="v":
                    verseNumber = text.split()[0] # Get the first token which is the first number
                    verseText = text[len(verseNumber)+1:].lstrip() # Get the rest of the string which is the verse text
                    # TODO: We haven't stripped out character fields from within the verse -- not sure how Zefania handles them yet
                    outputFile.write ( SP(3,level+2) + '<VERS vnumber="%s">%s</VERS>' % (verseNumber,verseText) + NL(3) )
            if haveOpenChapter:
                outputFile.write ( SP(3,level+1) + '</CHAPTER>' + NL(3) )
            outputFile.write( SP(3,level) + '</BIBLEBOOK>\n' )
        # end of writeBook

        ControlFiles.readControlFile( controlFileFolder, controlFilename, ZefaniaControls )
        #print( ZefaniaControls )
        #if ZefaniaControls["ZefaniaFiles"]=="byBible":
        if True:
            outputFilepath = ZefaniaControls["ZefaniaOutputFilename"]
            print( "Writing %s..." % outputFilepath )
            with open( outputFilepath, 'wt' ) as outputFile:
                writeHeader( outputFile )
                for BBB,bookData in self.books.items():
                    writeBook( outputFile, BBB, bookData, 1 )
                closeUp( outputFile )
    # end of toZefania_XML

    def toOSIS_XML( self, controlFileFolder, controlFilename ):
        """
        Using settings from the given control file,
            converts the USFM information to a UTF-8 OSIS XML file.

        You can validate the result using something like:
            xmllint --noout --schema http://www.bibletechnologies.net/osisCore.2.1.1.xsd YourOSISBibleFile.xml
        or if you download the schema from http://www.bibletechnologies.net/osisCore.2.1.1.xsd, then something like
            xmllint --noout --schema pathto/osisCore.2.1.1.xsd YourOSISBibleFile.xml

        TODO: We're not consistent about handling errors: sometimes we use assert, sometime raise (both of which abort the program), and sometimes log errors or warnings.
        """
        # Get the data tables that we need for proper checking
        bbc = BibleBooksCodes().loadData()
        OSISControls = {}
        ControlFiles.readControlFile( controlFileFolder, controlFilename, OSISControls )
        #print( OSISControls )

        bookAbbrevDict, bookNameDict, bookAbbrevNameDict = {}, {}, {}
        #for BBB in BBC_BBBDict.keys(): # Pre-process the language booknames
        for BBB in bbc.getAllReferenceAbbreviations(): # Pre-process the language booknames
            if BBB in OSISControls and OSISControls[BBB]:
                bits = OSISControls[BBB].split(',')
                if len(bits)!=2: logging.error( "Unrecognized language book abbreviation and name for %s: '%'" % ( BBB, OSISControls[BBB] ) )
                bookAbbrev = bits[0].strip().replace('"','') # Remove outside whitespace then the double quote marks
                bookName = bits[1].strip().replace('"','') # Remove outside whitespace then the double quote marks
                bookAbbrevDict[bookAbbrev], bookNameDict[bookName], bookAbbrevNameDict[BBB] = BBB, BBB, (bookAbbrev,bookName,)
                if ' ' in bookAbbrev: bookAbbrevDict[bookAbbrev.replace(' ','',1)] = BBB # Duplicate entries without the first space (presumably between a number and a name like 1 Kings)
                if ' ' in bookName: bookNameDict[bookName.replace(' ','',1)] = BBB # Duplicate entries without the first space
        # Let's write a Sword locale while we're at it
        SwLocFilepath = "SwLocale.conf"
        print( "Writing Sword locale file %s..." % SwLocFilepath )
        with open( SwLocFilepath, 'wt' ) as SwLocFile:
            SwLocFile.write( '[Meta]\nName=%s\n' % OSISControls["xmlLanguage"] )
            SwLocFile.write( 'Description=%s\n' % OSISControls["LanguageName"] )
            SwLocFile.write( 'Encoding=UTF-8\n\n[Text]\n' )
            #for BBB in BBC_BBBDict.keys():
            for BBB in bbc.getAllReferenceAbbreviations():
                if BBB in bookAbbrevNameDict:
                    SwLocFile.write( '%s=%s\n' % (bbc.getEnglishNameList(BBB)[0], bookAbbrevNameDict[BBB][1] ) ) # Write the first English book name and the language book name
            SwLocFile.write( '\n[Book Abbrevs]\n' )
            #for BBB in BBC_BBBDict.keys():
            for BBB in bbc.getAllReferenceAbbreviations():
                if BBB in bookAbbrevNameDict:
                    SwLocFile.write( '%s=%s\n' % (bbc.getEnglishNameList(BBB)[0].upper(), bbc.getSwordAbbreviation(BBB) ) ) # Write the UPPER CASE language book name and the Sword abbreviation

        def NL( section ):
            """Returns a newline character if required (else an empty string)."""
            if OSISControls["osisHumanReadable"] == "None": return ''
            if OSISControls["osisHumanReadable"] == "All": return '\n'
            # Else, we'll assume that it's set to "Header"
            if section > 2: return '' # (not header)
            return '\n' # for header
        # end of NL

        def SP( section, level ):
            """Returns a newline character if required (else an empty string)."""
            spaceFactor = 3 # This many spaces indent for each level
            if OSISControls["osisHumanReadable"] == "None": return ''
            if OSISControls["osisHumanReadable"] == "All": return ' '*level*spaceFactor
            # Else, we'll assume that it's set to "Header"
            if section > 2: return '' # (not header)
            return ' '*level*spaceFactor # for header
        # end of SP

        def writeHeader( outputFile ):
            """Writes the OSIS header to the OSIS XML outputFile."""
            outputFile.write( SP(0,0) + '<?xml version="1.0" encoding="UTF-8"?>' + NL(0) )
            outputFile.write( SP(0,0) + '<osis xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.bibletechnologies.net/2003/OSIS/namespace http://www.bibletechnologies.net/osisCore.2.1.1.xsd">' + NL(0) )
            outputFile.write( SP(1,0) + '<osisText osisRefWork="Bible" xml:lang="%s" osisIDWork="%s">\n' % (OSISControls["xmlLanguage"], OSISControls["osisIDWork"]) )
            outputFile.write( SP(2,1) + '<header>' + NL(2) )
            outputFile.write( SP(2,2) + '<work osisWork="%s">' % OSISControls["osisWork"] + NL(2) )
            outputFile.write( SP(2,3) + '<title>%s</title>' % OSISControls["Title"] + NL(2) )
            outputFile.write( SP(2,3) + '<creator role="encoder">USFMBible.py</creator>' + NL(2) )
            outputFile.write( SP(2,3) + '<type type="OSIS">Bible</type>' + NL(2) )
            outputFile.write( SP(2,3) + '<identifier type="OSIS">%s</identifier>' % OSISControls["Identifier"] + NL(2) )
            outputFile.write( SP(2,3) + '<scope>%s</scope>' % "dunno" + NL(2) )
            outputFile.write( SP(2,3) + '<refSystem>Bible</refSystem>' + NL(2) )
            outputFile.write( SP(2,2) + '</work>' + NL(2) )
            # Snowfall software write two work entries ???
            outputFile.write( SP(2,2) + '<work osisWork="%s">' % "bible" + NL(2) )
            outputFile.write( SP(2,3) + '<creator role="encoder">USFMBible.py</creator>' + NL(2) )
            outputFile.write( SP(2,3) + '<type type="OSIS">Bible</type>' + NL(2) )
            outputFile.write( SP(2,3) + '<refSystem>Bible</refSystem>' + NL(2) )
            outputFile.write( SP(2,2) + '</work>' + NL(2) )
            outputFile.write( SP(2,1) + '</header>\n' )
        # end of writeHeader

        def closeUp( outputFile ):
            """Writes closing stuff to the OSIS XML outputFile."""
            outputFile.write( SP(1,0) + '</osisText>' + NL(1) )
            outputFile.write( SP(0,0) + '</osis>' + NL(0) )
        # end of closeUp

        toOSISGlobals = { "vRef":'', "XRefNum":0, "FootnoteNum":0, "lastRef":'' }

        def convertReferenceToOSISRef( text, bRef, cRef ):
            """
            Takes a text reference (like '3:2' or '3:2: ' or '3: ' )
                and converts it to an OSIS reference string like "Esth.3.2" or "Phlm.1.3.

            Note that we might have trailing spaces in the text field.

            We simply discard any information about ranges, e.g., 1:17-18
            """
            #print( "convertReferenceToOSISRef got", "'"+text+"'", bRef, cRef )
            allowedVerseSpecifiers = ('a', 'b', 'c', 'd') # For specifying part of a verse, e.g., John 3:16 a

            adjText = text
            if '-' in text or '–' in text or '—' in text: # Also looks for en-dash and em-dash
                adjText = adjText.replace('–','-').replace('—','-') # Make sure it's a hyphen
                ix = adjText.index('-')
                adjText = adjText[:ix] # Discard the second bit of the range
                logging.info( "convertReferenceToOSISRef discarded range info from %s '%s'" % (cRef,text) )

            tokens = adjText.split()
            token1 = tokens[0]
            if len(tokens) == 1 \
            or (len(tokens)==2 and tokens[1] in allowedVerseSpecifiers): # It's telling about a portion of a verse (which OSIS doesn't handle I don't think) -- we'll completely ignore it
                if token1.isdigit(): # Assume it's a verse number
                    osisRef = cRef + '.' + token1
                elif token1 in allowedVerseSpecifiers: # Just have something like b, so we have to use the previous verse reference
                    assert( toOSISGlobals["lastRef"] )
                    osisRef = toOSISGlobals["lastRef"] # From the last call
                else: # it must have some punctuation in it
                    punctCount = 0
                    for char in ',.:': punctCount += token1.count( char )
                    if punctCount == 1:
                        if token1.endswith(':') and bRef in self.OneChapterOSISBookCodes:
                            V = token1[:-1] # Remove the final colon
                            if not V.isdigit(): logging.warning( "Unable to recognize 1-punct reference format %s '%s' from '%s'" % (cRef, token1, text) )
                            osisRef = bRef + '.1.' + V
                            toOSISGlobals["lastRef"] = osisRef
                        else: # Probably a CV reference like 8:2
                            CV = token1.replace(',','.').replace(':','.') # Make sure it's a dot
                            CVtokens = CV.split('.'); assert( len(CVtokens) == 2 )
                            for CVtoken in CVtokens: # Just double check that we're on the right track
                                if not CVtoken.isdigit(): logging.warning( "Unable to recognize 2nd 1-punct reference format %s '%s' from '%s'" % (cRef, token1, text) ); break
                            osisRef = bRef + '.' + CVtokens[0] + '.' + CVtokens[1]
                            toOSISGlobals["lastRef"] = osisRef
                    elif punctCount==2: # We have two punctuation characters in the reference
                        if token1.endswith(':'): # Let's try handling a final colon
                            CV = token1.replace(',','.',1).replace(':','.',1) # Make sure that the first punctuation character is a dot
                            CVtokens = CV.replace(':','',1).split('.'); assert( len(CVtokens) == 2 )
                            for CVtoken in CVtokens: # Just double check that we're on the right track
                                if not CVtoken.isdigit(): logging.warning( "Unable to recognize 2-punct reference format %s '%s' from '%s'" % (cRef, token1, text) ); break
                            osisRef = bRef + '.' + CVtokens[0] + '.' + CVtokens[1]
                            toOSISGlobals["lastRef"] = osisRef
                        else:
                            print( "convertReferenceToOSISRef got", "'"+text+"'", bRef, cRef ); raise Exception( "No code yet to handle references with multiple punctuation characters", text, token1 )
                    else: # We have >2 punctuation characters in the reference
                        print( "convertReferenceToOSISRef got", "'"+text+"'", bRef, cRef, toOSISGlobals["vRef"] )
                        logging.critical( "No code yet to handle references with more than two punctuation characters '%s' '%s'" % (text, token1) )
                        osisRef = 'XXX3p'
            else:
                print( "convertReferenceToOSISRef got", "'"+text+"'", bRef, cRef, toOSISGlobals["vRef"] )
                logging.critical( "No code yet to handle multiple tokens in a reference: %s" % tokens )
                osisRef = 'XXXmt'
            #print( "convertReferenceToOSISRef returns", osisRef )
            # TODO: We need to call a routine now to actually validate this reference
            return osisRef
        # end of convertReferenceToOSISRef

        def writeBook( outputFile, BBB, bkData, level ):
            """Writes a book to the OSIS XML outputFile.
            """

            def processXRefsAndFootnotes( verse ):
                """Convert cross-references and footnotes and return the adjusted verse text."""

                def processXRef( USFMxref ):
                    """
                    Return the OSIS code for the processed cross-reference (xref).

                    NOTE: The parameter here already has the /x and /x* removed.

                    \\x - \\xo 2:2: \\xt Lib 19:9-10; Diy 24:19.\\xt*\\x* (Backslashes are shown doubled here)
                        gives
                    <note type="crossReference" n="1">2:2: <reference>Lib 19:9-10; Diy 24:19.</reference></note> (Crosswire -- invalid OSIS -- which then needs to be converted)
                    <note type="crossReference" osisRef="Ruth.2.2" osisID="Ruth.2.2!crossreference.1" n="-"><reference type="source" osisRef="Ruth.2.2">2:2: </reference><reference osisRef="-">Lib 19:9-10</reference>; <reference osisRef="Ruth.Diy.24!:19">Diy 24:19</reference>.</note> (Snowfall)
                    \\x - \\xo 3:5: a \\xt Rum 11:1; \\xo b \\xt Him 23:6; 26:5.\\xt*\\x* is more complex still.
                    """
                    toOSISGlobals["XRefNum"] += 1
                    OSISxref = '<note type="crossReference" osisRef="%s" osisID="%s!crossreference.%s">' % (toOSISGlobals["vRef"],toOSISGlobals["vRef"],toOSISGlobals["XRefNum"])
                    for j,token in enumerate(USFMxref.split('\\')):
                        #print( "processXRef", j, "'"+token+"'", "from", '"'+USFMxref+'"' )
                        if j==0: # The first token (but the x has already been removed)
                            rest = token.strip()
                            if rest != '-': logging.warning( "We got something else here other than hyphen (probably need to do something with it): %s '%s' from '%s'" % (cRef, token, text) )
                        elif token.startswith('xo '): # xref reference follows
                            osisRef = convertReferenceToOSISRef( token[3:], bRef, cRef )
                            OSISxref += '<reference type="source" osisRef="%s">%s</reference>' % (osisRef,token[3:])
                        elif token.startswith('xt '): # xref text follows
###### This code needs to be re-written using the BibleReferences module .......................... XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
                            xrefText = token[3:]
                            endsWithPeriod = False;
                            if xrefText[-1]=='.': endsWithPeriod = True; xrefText = xrefText[:-1]
                            #print( "xrefText", "'"+xrefText+"'" )
                            # Here we ethnocentrically assume that multiple tokens will be separated by semicolons, e.g., 7:2; 8:5
                            subTokens = xrefText.split(';')
                            #print( "subTokens", subTokens )
                            osisBook = xRefChapter = ''
                            for k,referenceString in enumerate(subTokens):
                                for bit in referenceString.split():
                                    #print( "bit", bit )
                                    if bit in bookAbbrevDict: # Assume it's a bookname abbreviation
                                        BBB = bookAbbrevDict[bit]
                                        osisBook = bbc.getOSISAbbreviation( BBB )
                                        #print( BBB, "osisBook", osisBook )
                                    else: # Assume it's the actual reference
                                        if not osisBook: raise Exception( "Book code seems to be wrong or missing for xRef", bit, "from", USFMxref, "at", toOSISGlobals["vRef"] )
                                        punctCount = 0
                                        for char in ',.:-–': # included hyphen and en-dash in here (but not em-dash —)
                                            #print( '', char, bit.count(char), punctCount )
                                            punctCount += bit.count( char )
                                        #print( "punctCount is %i for '%s' in '%s'" % (punctCount,bit,referenceString) )
                                        if punctCount==0: # That's nice and easy
                                            if bit.isdigit() and BBB in self.OneChapterBBBBookCodes: # Then presumably a verse number
                                                xrefChapter = '1'
                                                osisRef = osisBook + '.' + xrefChapter + '.' + bit
                                                OSISxref += '<reference osisRef="%s">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
                                            else:
                                                logRoutine = logging.info if bit=='(LXX)' else logging.error # Sorry, this is a crude hack to avoid unnecessary error messages
                                                logRoutine( "Ignoring '%s' in xRef %s '%s' from '%s' (zero relevant punctuation)" % (bit,cRef, referenceString, text) )
                                        elif punctCount==1: # That's also nice and easy
                                            CV = bit.replace(',','.').replace(':','.') # Make sure it's a dot
                                            CVtokens = CV.split('.')
                                            CVtoken1 = CVtokens[0]
                                            if len(CVtokens)==1:
                                                if '-' in CVtoken1 or '–' in CVtoken1 and BBB not in self.OneChapterBBBBookCodes: # Could be something like spanning multiple chapters. e.g., Num 22-24
                                                    CBits = CVtoken1.replace('–','-').split('-')
                                                    assert( len(CBits) == 2 )
                                                    osisRef = osisBook + '.' + CBits[0] # Just ignore the second part of the range here
                                                elif BBB in self.OneChapterBBBBookCodes:
                                                    if not CVtoken1.isdigit(): logging.warning( "Unable to recognize cross-reference format %s '%s' from '%s'" % (cRef, referenceString, text) ); break
                                                    xrefChapter = '1'
                                                    osisRef = osisBook + '.' + xrefChapter + '.' + CVtoken1
                                                else: raise Exception( "Confused about cross-reference format %s %s '%s' from '%s'" % (cRef, CVtokens, referenceString, text) )
                                            elif len(CVtokens) == 2:
                                                for CVtoken in CVtokens: # Just double check that we're on the right track
                                                    if not CVtoken.isdigit(): logging.warning( "Unable to recognize cross-reference format %s '%s' from '%s'" % (cRef, referenceString, text) ); break
                                                xrefChapter = CVtoken1
                                                osisRef = osisBook + '.' + xrefChapter + '.' + CVtokens[1]
                                            else: raise Exception( "Seems like the wrong number of CV bits in cross-reference format %s %s '%s' from '%s'" % (cRef, CVtokens, referenceString, text) )
                                            OSISxref += '<reference osisRef="%s">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
                                        elif punctCount==2:
                                            if '-' in bit or '–' in bit: # Could have something like 7:1-4 with hyphen or en-dash
                                                CV = bit.replace(',','.').replace(':','.').replace('–','-') # Make sure CV separator (if any) is a dot and the range separator is a hyphen
                                                CVtokens = CV.split('.')
                                                CVtoken1 = CVtokens[0]
                                                assert( len(CVtokens) == 2 )
                                                # Just double check that we're on the right track
                                                if '-' in CVtoken1 or not CVtoken1.isdigit(): logging.warning( "Unable to recognize cross-reference format %s '%s' from '%s'" % (cRef, referenceString, text) ); break
                                                verseRangeBits = CVtokens[1].split('-')
                                                assert( len(verseRangeBits) == 2 )
                                                if len(verseRangeBits)!=2 or not verseRangeBits[0].isdigit() or not verseRangeBits[1].isdigit(): logging.critical( "Don't handle verse number of form '%s' yet for %s" % (CVtokens[1],cRef) )
                                                xRefChapter = CVtoken1
                                                xrefCref  = osisBook + '.' + xRefChapter
                                                osisRef = osisBook + '.' + xRefChapter + '.' + verseRangeBits[0]
                                                #print( "have", referenceString, osisBook, xRefChapter, xrefCref, osisRef, CVtokens, verseRangeBits )
                                                # Let's guess how to do this since we don't know for sure yet
                                                OSISxref += '<reference osisRef="%s">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
                                            elif ',' in bit: # Could have something like 7:1,4
                                                CV = bit.replace(':','.') # Make sure CV separator (if any) is a dot
                                                CVtokens = CV.split('.')
                                                CVtoken1 = CVtokens[0]
                                                assert( len(CVtokens) == 2 )
                                                # Just double check that we're on the right track
                                                if '-' in CVtoken1 or not CVtoken1.isdigit(): logging.warning( "Unable to recognize cross-reference format %s '%s' from '%s'" % (cRef, referenceString, text) ); break
                                                verseRangeBits = CVtokens[1].split(',')
                                                assert( len(verseRangeBits) == 2 )
                                                if len(verseRangeBits)!=2 or not verseRangeBits[0].isdigit() or not verseRangeBits[1].isdigit(): logging.critical( "Don't handle verse number of form '%s' yet for %s" % (CVtokens[1],cRef) )
                                                xRefChapter = CVtoken1
                                                xrefCref  = osisBook + '.' + xRefChapter
                                                osisRef = osisBook + '.' + xRefChapter + '.' + verseRangeBits[0]
                                                #print( "have", referenceString, osisBook, xRefChapter, xrefCref, osisRef, CVtokens, verseRangeBits )
                                                # Let's guess how to do this since we don't know for sure yet
                                                OSISxref += '<reference osisRef="%s">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
                                            else:
                                                raise Exception( "not written yet for 2 punctuation characters in verse number inside cross-reference" )
                                        elif punctCount==3:
                                            logging.critical( "Need to write code to handle this xref case: %s '%s' from '%s'" % (cRef, referenceString, text) ); continue
                                            if '-' in bit or '–' in bit: # Could have something like 7:1-8:4 with hyphen or en-dash
                                                CV = bit.replace(',','.').replace(':','.').replace('–','-') # Make sure CV separator (if any) is a dot and the range separator is a hyphen
                                                CVtokens = CV.split('.')
                                                CVtoken1 = CVtokens[0]
                                                assert( len(CVtokens) == 2 )
                                                # Just double check that we're on the right track
                                                if '-' in CVtoken1 or not CVtoken1.isdigit(): logging.warning( "Unable to recognize cross-reference format %s '%s' from '%s'" % (cRef, referenceString, text) ); break
                                                verseRangeBits = CVtokens[1].split('-')
                                                assert( len(verseRangeBits) == 2 )
                                                if len(verseRangeBits)!=2 or not verseRangeBits[0].isdigit() or not verseRangeBits[1].isdigit(): logging.critical( "Don't handle verse number of form '%s' yet for %s" % (verseNumber,cRef) )
                                                xRefChapter = CVtoken1
                                                xrefCref  = osisBook + '.' + xRefChapter
                                                osisRef = osisBook + '.' + xRefChapter + '.' + verseRangeBits[0]
                                                #print( "have", referenceString, osisBook, xRefChapter, xrefCref, osisRef, CVtokens, verseRangeBits )
                                                # Let's guess how to do this since we don't know for sure yet
                                                OSISxref += '<reference osisRef="%s">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
                                            elif ',' in bit: # Could have something like 7:1,4,9
                                                CV = bit.replace(':','.') # Make sure CV separator (if any) is a dot
                                                CVtokens = CV.split('.')
                                                CVtoken1 = CVtokens[0]
                                                assert( len(CVtokens) == 2 )
                                                # Just double check that we're on the right track
                                                if '-' in CVtoken1 or not CVtoken1.isdigit(): logging.warning( "Unable to recognize cross-reference format %s '%s' from '%s'" % (cRef, referenceString, text) ); break
                                                verseRangeBits = CVtokens[1].split(',')
                                                assert( len(verseRangeBits) == 2 )
                                                if len(verseRangeBits)!=2 or not verseRangeBits[0].isdigit() or not verseRangeBits[1].isdigit(): logging.critical( "Don't handle verse number of form '%s' yet for %s" % (verseNumber,cRef) )
                                                xRefChapter = CVtoken1
                                                xrefCref  = osisBook + '.' + xRefChapter
                                                osisRef = osisBook + '.' + xRefChapter + '.' + verseRangeBits[0]
                                                #print( "have", referenceString, osisBook, xRefChapter, xrefCref, osisRef, CVtokens, verseRangeBits )
                                                # Let's guess how to do this since we don't know for sure yet
                                                OSISxref += '<reference osisRef="%s">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
                                            else:
                                                raise Exception( "not written yet for 2 punctuation characters in verse number inside cross-reference" )
                                        else:
                                            print( "processXRef", punctCount )
                                            logging.error( "No code yet for xRef with more than 3 punctuation characters %s from %s at %s" % (bit, USFMxref, toOSISGlobals["vRef"]) )
                        elif token.startswith('x '): # another whole xref entry follows
                            rest = token[2:].strip()
                            if rest != '-': logging.warning( "We got something else here other than hyphen (probably need to do something with it): %s '%s' from '%s'" % (cRef, token, text) )
                        elif token in ('xt*', 'x*'):
                            pass # We're being lazy here and not checking closing markers properly
                        else:
                            logging.warning( "Unprocessed '%s' token in %s xref '%s'" % (token, toOSISGlobals["vRef"], USFMxref) )
                    OSISxref += '</note>'
                    #print( '', OSISxref )
                    return OSISxref

                def processFootnote( USFMfootnote ):
                    """
                    Return the OSIS code for the processed footnote.

                    NOTE: The parameter here already has the /f and /f* removed.

                    \\f + \\fr 1:20 \\ft Su ka kaluwasan te Nawumi ‘keupianan,’ piru ka kaluwasan te Mara ‘masakit se geyinawa.’\\f* (Backslashes are shown doubled here)
                        gives
                    <note n="1">1:20 Su ka kaluwasan te Nawumi ‘keupianan,’ piru ka kaluwasan te Mara ‘masakit se geyinawa.’</note> (Crosswire)
                    <note osisRef="Ruth.1.20" osisID="Ruth.1.20!footnote.1" n="+"><reference type="source" osisRef="Ruth.1.20">1:20 </reference>Su ka kaluwasan te Nawumi ‘keupianan,’ piru ka kaluwasan te Mara ‘masakit se geyinawa.’</note> (Snowfall)
                    """
                    toOSISGlobals["FootnoteNum"] += 1
                    OSISfootnote = '<note osisRef="%s" osisID="%s!footnote.%s">' % (toOSISGlobals["vRef"],toOSISGlobals["vRef"],toOSISGlobals["FootnoteNum"])
                    for j,token in enumerate(USFMfootnote.split('\\')):
                        #print( "processFootnote", j, token, USFMfootnote )
                        if j==0: continue # ignore the + for now
                        elif token.startswith('fr '): # footnote reference follows
                            osisRef = convertReferenceToOSISRef( token[3:], bRef, cRef )
                            OSISfootnote += '<reference type="source" osisRef="%s">%s</reference>' % (osisRef,token[3:])
                        elif token.startswith('ft '): # footnote text follows
                            OSISfootnote += token[3:]
                        elif token.startswith('fq '): # footnote quote follows -- NOTE: We also assume here that the next marker closes the fq field
                            OSISfootnote += '<catchWord>%s</catchWord>' % token[3:] # Note that the trailing space goes in the catchword here -- seems messy
                        elif token in ('ft*','fq*'):
                            pass # We're being lazy here and not checking closing markers properly
                        else:
                            logging.warning( "Unprocessed '%s' token in %s footnote '%s'" % (token, toOSISGlobals["vRef"], USFMfootnote) )
                    OSISfootnote += '</note>'
                    #print( '', OSISfootnote )
                    return OSISfootnote

                while '\\x ' in verse and '\\x*' in verse: # process cross-references (xrefs)
                    ix1 = verse.index('\\x ')
                    ix2 = verse.find('\\x* ') # Note the extra space here at the end
                    if ix2 == -1: # Didn't find it so must be no space after the asterisk
                        ix2 = verse.index('\\x*')
                        ix2b = ix2 + 3 # Where the xref ends
                        logging.warning( 'No space after xref entry in %s' % toOSISGlobals["vRef"] )
                    else: ix2b = ix2 + 4
                    xref = verse[ix1+3:ix2]
                    osisXRef = processXRef( xref )
                    #print( osisXRef )
                    verse = verse[:ix1] + osisXRef + verse[ix2b:]
                while '\\f ' in verse and '\\f*' in verse: # process footnotes
                    ix1 = verse.index('\\f ')
                    ix2 = verse.find('\\f*')
#                    ix2 = verse.find('\\f* ') # Note the extra space here at the end -- doesn't always work if there's two footnotes within one verse!!!
#                    if ix2 == -1: # Didn't find it so must be no space after the asterisk
#                        ix2 = verse.index('\\f*')
#                        ix2b = ix2 + 3 # Where the footnote ends
#                        #logging.warning( 'No space after footnote entry in %s' % toOSISGlobals["vRef"] )
#                    else: ix2b = ix2 + 4
                    footnote = verse[ix1+3:ix2]
                    osisFootnote = processFootnote( footnote )
                    #print( osisFootnote )
                    verse = verse[:ix1] + osisFootnote + verse[ix2+3:]
#                    verse = verse[:ix1] + osisFootnote + verse[ix2b:]
                return verse
            # end of processXRefsAndFootnotes

            def checkText( textToCheck ):
                """Handle some general backslash codes and warn about any others still unprocessed."""
                if '<<' in textToCheck or '>>' in textToCheck:
                    logging.warning( "Unexpected double angle brackets in %s: '%s' field is '%s'" % (toOSISGlobals["vRef"],marker,textToCheck) )
                    textToCheck = textToCheck.replace('<<','“' ).replace('>>','”' )
                if '\\bk ' in textToCheck and '\\bk*' in textToCheck:
                    textToCheck = textToCheck.replace('\\bk ','<reference type="x-bookName">').replace('\\bk*','</reference>')
                if '\\' in textToCheck:
                    logging.error( "We still have some unprocessed backslashes in %s: '%s' field is '%s'" % (toOSISGlobals["vRef"],marker,textToCheck) )
                    textToCheck = textToCheck.replace('\\','ENCODING ERROR HERE ' )
                return textToCheck
            # end of checkText

            def writeVerse( outputFile, BBB, cRef, level, text ):
                """
                Processes and writes a verse to the OSIS XML outputFile.
                    <verse sID="Gen.1.31" osisID="Gen.1.31"/>
                    Ne nakita te Manama ka langun ne innimu rin wey natelesan amana sikandin. Ne nasagkup e wey napawe, ne seeye ka igkeen-em ne aldew.
                    <verse eID="Gen.1.31"/>

                Has to handle joined verses, e.g.,
                    <verse sID="Esth.9.16" osisID="Esth.9.16 Esth.9.17"/>text<verse eID="Esth.9.16"/> (Crosswire)
                    <verse sID="Esth.9.16-Esth.9.17" osisID="Esth.9.16 Esth.9.17" n="16-17"/>text<verse eID="Esth.9.16-Esth.9.17"/> (Snowfall)
                """
                verseNumber = text.split()[0] # Get the first token which is the first number
                verseText = text[len(verseNumber)+1:].lstrip() # Get the rest of the string which is the verse text
                if '-' in verseNumber:
                    bits = verseNumber.split('-')
                    if len(bits)!=2 or not bits[0].isdigit() or not bits[1].isdigit(): logging.critical( "Don't handle verse number of form '%s' yet for %s" % (verseNumber,cRef) )
                    toOSISGlobals["vRef"]  = cRef + '.' + bits[0]
                    vRef2 = cRef + '.' + bits[1]
                    sID    = toOSISGlobals["vRef"] + '-' + vRef2
                    osisID = toOSISGlobals["vRef"] + ' ' + vRef2
                elif ',' in verseNumber:
                    raise Exception( "not written yet for comma in versenumber" )
                elif verseNumber.isdigit():
                    sID = osisID = toOSISGlobals["vRef"] = cRef + '.' + verseNumber
                else: logging.critical( "Don't handle verse number of form '%s' yet for %s" % (verseNumber,cRef) )
                adjText = processXRefsAndFootnotes( verseText )
                outputFile.write( SP(3,level) + '<verse sID="%s" osisID="%s"/>%s<verse eID="%s"/>' % (sID,osisID,checkText(adjText),sID) + NL(3) )
            # end of writeVerse

            bRef = bbc.getOSISAbbreviation( BBB ) # OSIS book name
            outputFile.write( SP(3,level) + '<div type="book" osisID="%s">' % bRef + NL(3) )
            currentLevel = level + 1
            haveOpenIntro = haveOpenOutline = haveOpenMajorSection = haveOpenSection = haveOpenSubsection = needChapterEID = haveOpenParagraph = haveOpenLG = haveOpenL = False
            lastMarker = unprocessedMarker = ''
            for marker,text in bkData.lines:
                if marker in ( 'id', 'h', 'mt2' ): continue # We just ignore these markers
                if marker=='mt1': outputFile.write( SP(3,currentLevel) + '<title>%s</title>' % checkText(text) + NL(3) )
                elif marker=='is1':
                    if haveOpenIntro: raise Exception( "Not handled yet is1" )
                    outputFile.write( SP(3,currentLevel) + '<div type="introduction">' + NL(3) )
                    currentLevel += 1
                    outputFile.write( SP(3,currentLevel) + '<title>%s</title>' % checkText(text) + NL(3) ) # Introduction heading
                    haveOpenIntro = True
                    cRef = bRef + '.0' # Not used by OSIS
                    toOSISGlobals["vRef"] = cRef + '.0' # Not used by OSIS
                elif marker=='ip':
                    if not haveOpenIntro: raise Exception( "Have an ip not in a introduction section" )
                    if haveOpenParagraph:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</p>' + NL(3) )
                    outputFile.write( SP(3,currentLevel) + '<p>%s' % checkText(text) + NL(3) ) # Sometimes there's text
                    currentLevel += 1
                    haveOpenParagraph = True
                elif marker=='iot':
                    if not haveOpenIntro: raise Exception( "Have an iot not in a introduction section" )
                    if haveOpenSection or haveOpenOutline: raise Exception( "Not handled yet iot" )
                    if haveOpenParagraph:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</p>' + NL(3) )
                        haveOpenParagraph = False
                    outputFile.write( SP(3,currentLevel) + '<div type="outline">' + NL(3) )
                    currentLevel += 1
                    outputFile.write( SP(3,currentLevel) + '<title>%s</title>' % checkText(text) + NL(3) )
                    outputFile.write( SP(3,currentLevel) + '<list>' + NL(3) )
                    currentLevel += 1
                    haveOpenOutline = True
                elif marker=='io1':
                    if not haveOpenIntro: raise Exception( "Have an io1 not in a introduction section" )
                    if not haveOpenOutline: raise Exception( "Have an io1 not in a outline section" )
                    outputFile.write( SP(3,currentLevel) + '<item>%s</item>' % checkText(text) + NL(3) )
                elif marker=='io2':
                    if not haveOpenIntro: raise Exception( "Have an io2 not in a introduction section" )
                    if not haveOpenOutline: raise Exception( "Have an io2 not in a outline section" )
                    outputFile.write( SP(3,currentLevel) + '<item>%s</item>' % checkText(text) + NL(3) ) # TODO: Shouldn't this be different from an io1???
                elif marker=='c':
                    if haveOpenOutline:
                        if text!='1': raise Exception( "This should be chapter 1 to close the outline" )
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</list>' + NL(3) )
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</div>' + NL(3) )
                        haveOpenOutline = False
                    if haveOpenIntro:
                        if text!='1': raise Exception( "This should be chapter 1 to close the introduction" )
                        if haveOpenParagraph:
                            currentLevel -= 1
                            outputFile.write( SP(3,currentLevel) + '</p>' + NL(3) )
                            haveOpenParagraph = False
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</div>\n' )
                        haveOpenIntro = False
                    if haveOpenLG:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</lg>' + NL(3) )
                        haveOpenLG = False
                    if needChapterEID:
                        outputFile.write( SP(3,currentLevel) + '<chapter eID="%s"/>' % (cRef) + NL(3) ) # This is an end milestone marker
                    currentChapterNumber = text
                    if not currentChapterNumber.isdigit(): logging.critical( "Can't handle non-digit '%s' chapter number yet" % text )
                    cRef = bRef + '.' + checkText(currentChapterNumber)
                    outputFile.write( SP(3,currentLevel) + '<chapter sID="%s" osisID="%s"/>' % (cRef,cRef) + NL(3) ) # This is a milestone marker
                    needChapterEID = True
                elif marker=='ms1':
                    if haveOpenParagraph:
                        if haveOpenLG:
                            currentLevel -= 1
                            outputFile.write( SP(3,currentLevel) + '</lg>' + NL(3) )
                            haveOpenLG = False
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</p>' + NL(3) )
                        haveOpenParagraph = False
                    if haveOpenSubsection:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</div>\n' )
                        haveOpenSubsection = False
                    if haveOpenSection:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</div>\n' )
                        haveOpenSection = False
                    if haveOpenMajorSection:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</div>\n' )
                    outputFile.write( SP(3,currentLevel) + '<div type="majorSection">' + NL(3) )
                    currentLevel += 1
                    outputFile.write( SP(3,currentLevel) + '<title>%s</title>' % checkText(text) + NL(3) ) # Section heading
                    haveOpenMajorSection = True
                elif marker=='s1':
                    if haveOpenParagraph:
                        if haveOpenLG:
                            currentLevel -= 1
                            outputFile.write( SP(3,currentLevel) + '</lg>' + NL(3) )
                            haveOpenLG = False
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</p>' + NL(3) )
                        haveOpenParagraph = False
                    if haveOpenSubsection:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</div>\n' )
                        haveOpenSubsection = False
                    if haveOpenSection:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</div>\n' )
                    outputFile.write( SP(3,currentLevel) + '<div type="section">' + NL(3) )
                    currentLevel += 1
                    outputFile.write( SP(3,currentLevel) + '<title>%s</title>' % checkText(text) + NL(3) ) # Section heading
                    haveOpenSection = True
                elif marker=='s2':
                    if haveOpenParagraph:
                        if haveOpenLG:
                            currentLevel -= 1
                            outputFile.write( SP(3,currentLevel) + '</lg>' + NL(3) )
                            haveOpenLG = False
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</p>' + NL(3) )
                        haveOpenParagraph = False
                    if haveOpenSubsection:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</div>\n' )
                    outputFile.write( SP(3,currentLevel) + '<div type="subSection">' + NL(3) )
                    currentLevel += 1
                    outputFile.write( SP(3,currentLevel) + '<title>%s</title>' % checkText(text) + NL(3) ) # Section heading
                    haveOpenSubsection = True
                elif marker=='mr':
                    # Should only follow a ms1 I think
                    if haveOpenParagraph or haveOpenSection or not haveOpenMajorSection: logging.error( "Didn't expect major reference 'mr' marker after %s" % toOSISGlobals["vRef"] )
                    outputFile.write( SP(3,currentLevel) + '<title type="parallel">%s</title>' % checkText(text) + NL(3) ) # Section reference
                elif marker=='r':
                    # Should only follow a s1 I think
                    if haveOpenParagraph or not haveOpenSection: logging.error( "Didn't expect reference 'r' marker after %s" % toOSISGlobals["vRef"] )
                    outputFile.write( SP(3,currentLevel) + '<title type="parallel">%s</title>' % checkText(text) + NL(3) ) # Section reference
                elif marker=='p':
                    if haveOpenLG:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</lg>' + NL(3) )
                        haveOpenLG = False
                    if haveOpenParagraph:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</p>' + NL(3) )
                    if not haveOpenSection:
                        outputFile.write( SP(3,currentLevel) + '<div type="section">' + NL(3) )
                        currentLevel += 1
                        haveOpenSection = True
                    adjustedText = processXRefsAndFootnotes( text )
                    outputFile.write( SP(3,currentLevel) + '<p>%s' % checkText(adjustedText) + NL(3) ) # Sometimes there's text
                    currentLevel += 1
                    haveOpenParagraph = True
                elif marker=='v':
                    if not haveOpenL and haveOpenLG:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</lg>' + NL(3) )
                        haveOpenLG = False
                    writeVerse( outputFile, BBB, cRef, currentLevel, text )
                    if haveOpenL:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</l>' + NL(3) )
                        haveOpenL = False
                elif marker=='q1' or marker=='q2' or marker=='q3':
                    qLevel = '1' if marker=='q1' else '2' if marker=='q2' else '3'
                    if not haveOpenLG:
                        outputFile.write( SP(3,currentLevel) + '<lg>' + NL(3) )
                        currentLevel += 1
                        haveOpenLG = True
                    if text:
                        adjustedText = processXRefsAndFootnotes( text )
                        outputFile.write( SP(3,currentLevel) + '<l level="%s">%s</l>' % (qLevel, checkText(adjustedText)) + NL(3) )
                    else: # No text -- this q1 applies to the next marker
                        outputFile.write( SP(3,currentLevel) + '<l level="%s">' % qLevel + NL(3) )
                        currentLevel += 1
                        haveOpenL = True
                elif marker=='m': # Margin/Flush-left paragraph
                    if haveOpenL:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</l>' + NL(3) )
                        haveOpenL = False
                    if haveOpenLG:
                        currentLevel -= 1
                        outputFile.write( SP(3,currentLevel) + '</lg>' + NL(3) )
                        haveOpenLG = False
                    if text:
                        outputFile.write( SP(3,currentLevel) + checkText(text) + NL(3) )
                elif marker=='b': # Blank line
                        # Doesn't seem that OSIS has a way to encode this presentation element
                        outputFile.write( '\n' ) # We'll do this for now
                else: logging.warning( "We didn't process %s '%s' USFM marker (%s)" % (cRef,marker,text) )
                lastMarker = marker
            if haveOpenIntro or haveOpenOutline or haveOpenLG or haveOpenL or unprocessedMarker: raise Exception( "These shouldn't be open here" )
            if needChapterEID:
                outputFile.write( SP(3,currentLevel) + '<chapter eID="%s"/>' % (cRef) + NL(3) ) # This is an end milestone marker
            if haveOpenParagraph:
                if haveOpenLG:
                    currentLevel -= 1
                    outputFile.write( SP(3,currentLevel) + '</lg>' + NL(3) )
                currentLevel -= 1
                outputFile.write( SP(3,currentLevel) + '</p>' + NL(3) )
            if haveOpenSection:
                currentLevel -= 1
                outputFile.write( SP(3,currentLevel) + '</div>' + NL(3) )
            if haveOpenMajorSection:
                currentLevel -= 1
                outputFile.write( SP(3,currentLevel) + '</div>' + NL(3) )
            currentLevel -= 1
            outputFile.write( SP(3,currentLevel) + '</div>\n' )
            #print( currentLevel, level )
            assert( currentLevel == level )
        # end of writeBook

        if OSISControls["osisFiles"]=="byBible":
            outputFilepath = OSISControls["osisOutputFilename"]
            print( "Writing %s..." % outputFilepath )
            with open( outputFilepath, 'wt' ) as outputFile:
                writeHeader( outputFile )
                for BBB,bookData in self.books.items():
                    writeBook( outputFile, BBB, bookData, 1 )
                closeUp( outputFile )
        #print( "Don't have chapter eIDs yet -- dunno where to put them (CrossWire put them after the next <p>, Snowfall put them before the </p> which seems much more logical)" )
        print( "Need to find and look at an example where a new chapter isn't a new <p> to see how chapter eIDs should be handled there" )
    # end of toOSIS_XML

    def toSwordModule( self, controlFileFolder, controlFilename ):
        """
        Using settings from the given control file,
            converts the USFM information to a UTF-8 OSIS-XML-based Sword module.
        """
        #You can validate the result using something like:
        #    xmllint --noout --schema http://www.bibletechnologies.net/osisCore.2.1.1.xsd YourOSISBibleFile.xml
        #or if you download the schema from http://www.bibletechnologies.net/osisCore.2.1.1.xsd, then something like
        #    xmllint --noout --schema pathto/osisCore.2.1.1.xsd YourOSISBibleFile.xml

        import BibleBooksCodes

        # Get the data tables that we need for proper checking
        bbc = BibleBooksCodes.BibleBooksCodesConvertor()
        junk, BBC_BBBDict, junk, BBC_OADict, junk, junk, junk, junk, junk, junk, BBC_NameDict = bbc.importDataToPython()
        SwordControls = {}
        ControlFiles.readControlFile( controlFileFolder, controlFilename, SwordControls )
        #print( SwordControls )

        bookAbbrevDict, bookNameDict, bookAbbrevNameDict = {}, {}, {}
        for BBB in BBC_BBBDict.keys(): # Pre-process the language booknames
            if BBB in SwordControls and SwordControls[BBB]:
                bits = SwordControls[BBB].split(',')
                if len(bits)!=2: logging.error( "Unrecognized language book abbreviation and name for %s: '%'" % ( BBB, OSISControls[BBB] ) )
                bookAbbrev = bits[0].strip().replace('"','') # Remove outside whitespace then the double quote marks
                bookName = bits[1].strip().replace('"','') # Remove outside whitespace then the double quote marks
                bookAbbrevDict[bookAbbrev], bookNameDict[bookName], bookAbbrevNameDict[BBB] = BBB, BBB, (bookAbbrev,bookName,)
                if ' ' in bookAbbrev: bookAbbrevDict[bookAbbrev.replace(' ','',1)] = BBB # Duplicate entries without the first space (presumably between a number and a name like 1 Kings)
                if ' ' in bookName: bookNameDict[bookName.replace(' ','',1)] = BBB # Duplicate entries without the first space
        # Let's write a Sword locale while we're at it
        SwLocFilepath = "SwLocale.conf"
        print( "Writing Sword locale file %s..." % SwLocFilepath )
        with open( SwLocFilepath, 'wt' ) as SwLocFile:
            SwLocFile.write( '[Meta]\nName=%s\n' % SwordControls["xmlLanguage"] )
            SwLocFile.write( 'Description=%s\n' % SwordControls["LanguageName"] )
            SwLocFile.write( 'Encoding=UTF-8\n\n[Text]\n' )
            for BBB in BBC_BBBDict.keys():
                if BBB in bookAbbrevNameDict:
                    SwLocFile.write( '%s=%s\n' % (BBC_BBBDict[BBB][11].split(' / ')[0], bookAbbrevNameDict[BBB][1] ) ) # Write the English book name and the language book name
            SwLocFile.write( '\n[Book Abbrevs]\n' )
            for BBB in BBC_BBBDict.keys():
                if BBB in bookAbbrevNameDict:
                    SwLocFile.write( '%s=%s\n' % (bookAbbrevNameDict[BBB][1].upper(), BBC_BBBDict[BBB][2] ) ) # Write the UPPER CASE language book name and the Sword abbreviation
        raise Exception( "Not written yet :-)" )
    #end of toSwordModule

    def toBible( self, outputFilepath=None ):
        """
        Converts the USFM information to a Bible object.
        """
        import Bible
        B = Bible.Bible()
        for bookReferenceCode,bookData in self.books.items():
            #print( bookReferenceCode, bookData )
            bk = B.addBook( bookReferenceCode )
            for marker,text in bookData.lines:
                #print( marker, text )
                if marker == 'p': bk.append( ('Pgr', text,) )
                elif marker=='c': bk.append( ('Chp', text,) )
                elif marker=='v':
                    verseNum = text.split()[0]
                    verseText = text[len(verseNum)+1:]
                    bk.append( ('Vrs', verseNum,) ); bk.append( ('Txt', verseText,) )
                elif marker=='q1': bk.append( ('Qu1', text,) )
                elif marker=='q2': bk.append( ('Qu2', text,) )
                elif marker=='q3': bk.append( ('Qu3', text,) )
                elif marker=='s1': bk.append( ('SH1', text,) )
                elif marker=='s2': bk.append( ('SH2', text,) )
                elif marker== 'r': bk.append( ('SXR', text,) )
                #else: print( "Doesn't handle %s marker yet" % marker )
            #print( bk)
        if outputFilepath: B.write( outputFilepath )
    # end of toBible
# end of class USFMBible


def main():
    """
    Demonstrate reading and processing some Bible databases.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v%s" % ( versionString ) )
    #parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML file to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 0: print( "%s V%s" % ( progName, versionString ) )

    uB = USFMBible( "Matigsalug" )
    uB.load( "/mnt/Data/Matigsalug/Scripture/MBTV" )
    #uB.load( "TestUSFM" )
    print( uB )
    #print( uB.getVersification () )
    #uB.toZefania_XML( '', "MBT_to_Zefania_controls.txt" )
    uB.toOSIS_XML( '', "MBT_to_OSIS_controls.txt" )
    #uB.toSwordModule( '', "MBT_to_Sword_controls.txt" )
    #uB.toBible( "ScrapedFiles/TestBible.module" )

if __name__ == '__main__':
    main()
## End of USFMBible.py
