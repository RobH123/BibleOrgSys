#!/usr/bin/python3
#
# USFMBible.py
#
# Module handling the USFM markers for Bible books
#   Last modified: 2010-12-22 by RJH (also update versionString below)
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
versionString = "0.03"


import os, logging, datetime
from collections import OrderedDict

from singleton import singleton
import Globals, ControlFiles
from BibleBooksCodes import BibleBooksCodes
from XMLWriter import XMLWriter


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
        # Get the data tables that we need for proper checking
        ZefaniaControls = {}
        ControlFiles.readControlFile( controlFileFolder, controlFilename, ZefaniaControls )
        #print( ZefaniaControls )

        def writeHeader( writerObject ):
            """Writes the Zefania header to the Zefania XML writerObject."""
            writerObject.writeLineOpen( 'INFORMATION' )
            if "ZefaniaTitle" in ZefaniaControls and ZefaniaControls["ZefaniaTitle"]: writerObject.writeLineOpenClose( 'title' , ZefaniaControls["ZefaniaTitle"] )
            if "ZefaniaSubject" in ZefaniaControls and ZefaniaControls["ZefaniaSubject"]: writerObject.writeLineOpenClose( 'subject', ZefaniaControls["ZefaniaSubject"] )
            if "ZefaniaDescription" in ZefaniaControls and ZefaniaControls["ZefaniaDescription"]: writerObject.writeLineOpenClose( 'description', ZefaniaControls["ZefaniaDescription"] )
            if "ZefaniaPublisher" in ZefaniaControls and ZefaniaControls["ZefaniaPublisher"]: writerObject.writeLineOpenClose( 'publisher', ZefaniaControls["ZefaniaPublisher"] )
            if "ZefaniaContributors" in ZefaniaControls and ZefaniaControls["ZefaniaContributors"]: writerObject.writeLineOpenClose( 'contributors', ZefaniaControls["ZefaniaContributors"] )
            if "ZefaniaIdentifier" in ZefaniaControls and ZefaniaControls["ZefaniaIdentifier"]: writerObject.writeLineOpenClose( 'identifier', ZefaniaControls["ZefaniaIdentifier"] )
            if "ZefaniaSource" in ZefaniaControls and ZefaniaControls["ZefaniaSource"]: writerObject.writeLineOpenClose( 'identifier', ZefaniaControls["ZefaniaSource"] )
            if "ZefaniaCoverage" in ZefaniaControls and ZefaniaControls["ZefaniaCoverage"]: writerObject.writeLineOpenClose( 'coverage', ZefaniaControls["ZefaniaCoverage"] )
            writerObject.writeLineOpenClose( 'format', 'Zefania XML Bible Markup Language' )
            writerObject.writeLineOpenClose( 'date', datetime.datetime.now().date().isoformat() )
            writerObject.writeLineOpenClose( 'creator', 'USFMBible.py' )
            writerObject.writeLineOpenClose( 'type', 'bible text' )
            if "ZefaniaLanguage" in ZefaniaControls and ZefaniaControls["ZefaniaLanguage"]: writerObject.writeLineOpenClose( 'language', ZefaniaControls["ZefaniaLanguage"] )
            if "ZefaniaRights" in ZefaniaControls and ZefaniaControls["ZefaniaRights"]: writerObject.writeLineOpenClose( 'rights', ZefaniaControls["ZefaniaRights"] )
            writerObject.writeLineClose( 'INFORMATION' )
        # end of writeHeader

        def writeBook( writerObject, BBB, bkData ):
            """Writes a book to the Zefania XML writerObject."""
            writerObject.writeLineOpen( 'BIBLEBOOK', [('bnumber',self.BibleBooksCodes.getReferenceNumber(BBB)), ('bname',self.BibleBooksCodes.getEnglishName_NR(BBB)), ('bsname',self.BibleBooksCodes.getOSISAbbreviation(BBB))] )
            haveOpenChapter = False
            for marker,text in bkData.lines:
                if marker=="c":
                    if haveOpenChapter:
                        writerObject.writeLineClose ( 'CHAPTER' )
                    writerObject.writeLineOpen ( 'CHAPTER', ('cnumber',text) )
                    haveOpenChapter = True
                elif marker=="v":
                    verseNumber = text.split()[0] # Get the first token which is the first number
                    verseText = text[len(verseNumber)+1:].lstrip() # Get the rest of the string which is the verse text
                    # TODO: We haven't stripped out character fields from within the verse -- not sure how Zefania handles them yet
                    if not verseText: # this is an empty verse
                        verseText = '- - -' # but we'll put in a filler
                    writerObject.writeLineOpenClose ( 'VERS', verseText, ('vnumber',verseNumber) )
            if haveOpenChapter:
                writerObject.writeLineClose( 'CHAPTER' )
            writerObject.writeLineClose( 'BIBLEBOOK' )
        # end of writeBook

        if Globals.verbosityLevel>1: print( "Exporting to Zefania format..." )
        outputFolder = "OutputFiles"
        if not os.access( outputFolder, os.F_OK ): os.mkdir( outputFolder ) # Make the empty folder if there wasn't already one there
        xw = XMLWriter().setOutputFilePath( os.path.join( outputFolder, ZefaniaControls["ZefaniaOutputFilename"] ) )
        xw.setHumanReadable()
        xw.start()
# TODO: Some modules have <XMLBIBLE xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="zef2005.xsd" version="2.0.1.18" status="v" revision="1" type="x-bible" biblename="KJV+">
        xw.writeLineOpen( 'XMLBible', [('xmlns:xsi',"http://www.w3.org/2001/XMLSchema-instance"), ('type',"x-bible"), ('biblename',ZefaniaControls["ZefaniaBibleName"]) ] )
        if True: #if ZefaniaControls["ZefaniaFiles"]=="byBible":
            writeHeader( xw )
            for BBB,bookData in self.books.items():
                writeBook( xw, BBB, bookData )
        xw.writeLineClose( 'XMLBible' )
        xw.close()
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
        OSISControls = {}
        ControlFiles.readControlFile( controlFileFolder, controlFilename, OSISControls )
        #print( OSISControls )

        bookAbbrevDict, bookNameDict, bookAbbrevNameDict = {}, {}, {}
        #for BBB in BBC_BBBDict.keys(): # Pre-process the language booknames
        for BBB in self.BibleBooksCodes.getAllReferenceAbbreviations(): # Pre-process the language booknames
            if BBB in OSISControls and OSISControls[BBB]:
                bits = OSISControls[BBB].split(',')
                if len(bits)!=2: logging.error( "Unrecognized language book abbreviation and name for %s: '%'" % ( BBB, OSISControls[BBB] ) )
                bookAbbrev = bits[0].strip().replace('"','') # Remove outside whitespace then the double quote marks
                bookName = bits[1].strip().replace('"','') # Remove outside whitespace then the double quote marks
                bookAbbrevDict[bookAbbrev], bookNameDict[bookName], bookAbbrevNameDict[BBB] = BBB, BBB, (bookAbbrev,bookName,)
                if ' ' in bookAbbrev: bookAbbrevDict[bookAbbrev.replace(' ','',1)] = BBB # Duplicate entries without the first space (presumably between a number and a name like 1 Kings)
                if ' ' in bookName: bookNameDict[bookName.replace(' ','',1)] = BBB # Duplicate entries without the first space

        outputFolder = "OutputFiles"
        if not os.access( outputFolder, os.F_OK ): os.mkdir( outputFolder ) # Make the empty folder if there wasn't already one there

        # Let's write a Sword locale while we're at it
        SwLocFilepath = os.path.join( outputFolder, "SwLocale.conf" )
        print( "Writing Sword locale file %s..." % SwLocFilepath )
        with open( SwLocFilepath, 'wt' ) as SwLocFile:
            SwLocFile.write( '[Meta]\nName=%s\n' % OSISControls["xmlLanguage"] )
            SwLocFile.write( 'Description=%s\n' % OSISControls["LanguageName"] )
            SwLocFile.write( 'Encoding=UTF-8\n\n[Text]\n' )
            for BBB in self.BibleBooksCodes.getAllReferenceAbbreviations():
                if BBB in bookAbbrevNameDict:
                    SwLocFile.write( '%s=%s\n' % (self.BibleBooksCodes.getEnglishName_NR(BBB), bookAbbrevNameDict[BBB][1] ) ) # Write the first English book name and the language book name
            SwLocFile.write( '\n[Book Abbrevs]\n' )
            for BBB in self.BibleBooksCodes.getAllReferenceAbbreviations():
                if BBB in bookAbbrevNameDict:
                    SwLocFile.write( '%s=%s\n' % (self.BibleBooksCodes.getEnglishName_NR(BBB).upper(), self.BibleBooksCodes.getSwordAbbreviation(BBB) ) ) # Write the UPPER CASE language book name and the Sword abbreviation

        def writeHeader( writerObject ):
            """Writes the OSIS header to the OSIS XML writerObject."""
            writerObject.writeLineOpen( 'header' )
            writerObject.writeLineOpen( 'work', ('osisWork', OSISControls["osisWork"]) )
            writerObject.writeLineOpenClose( 'title', OSISControls["Title"] )
            writerObject.writeLineOpenClose( 'creator', "USFMBible.py", ('role',"encoder") )
            writerObject.writeLineOpenClose( 'type',  "Bible", ('type',"OSIS") )
            writerObject.writeLineOpenClose( 'identifier', OSISControls["Identifier"], ('type',"OSIS") )
            writerObject.writeLineOpenClose( 'scope', "dunno" )
            writerObject.writeLineOpenClose( 'refSystem', "Bible" )
            writerObject.writeLineClose( 'work' )
            # Snowfall software write two work entries ???
            writerObject.writeLineOpen( 'work', ('osisWork',"bible") )
            writerObject.writeLineOpenClose( 'creator', "USFMBible.py", ('role',"encoder") )
            writerObject.writeLineOpenClose( 'type',  "Bible", ('type',"OSIS") )
            writerObject.writeLineOpenClose( 'refSystem', "Bible" )
            writerObject.writeLineClose( 'work' )
            writerObject.writeLineClose( 'header' )
        # end of writeHeader

        toOSISGlobals = { "vRef":'', "XRefNum":0, "FootnoteNum":0, "lastRef":'' } # These are our global variables

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

        def writeBook( writerObject, BBB, bkData ):
            """Writes a book to the OSIS XML writerObject.
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
                                        osisBook = self.BibleBooksCodes.getOSISAbbreviation( BBB )
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
                                                OSISxref += '<reference type="source" osisRef="%s">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
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
                                            OSISxref += '<reference type="source" osisRef="%s">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
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
                                                OSISxref += '<reference type="source" osisRef="%s">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
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
                                                OSISxref += '<reference type="source" osisRef="%s">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
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
                                                OSISxref += '<reference type="source" osisRef="%s">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
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
                                                OSISxref += '<reference type="source" osisRef="%s">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
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
                # end of processXRef

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
                # end of processFootnote

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

            def writeVerse( writerObject, BBB, cRef, text ):
                """
                Processes and writes a verse to the OSIS XML writerObject.
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
                writerObject.writeLineOpenSelfclose( 'verse', [('sID',sID), ('osisID',osisID)] )
                writerObject.writeLineText( checkText(adjText), noTextCheck=True )
                writerObject.writeLineOpenSelfclose( 'verse', ('eID',sID) )
            # end of writeVerse

            def closeOpenMajorSection():
                """ Close a <div> if it's open. """
                nonlocal haveOpenMajorSection
                if haveOpenMajorSection:
                    writerObject.writeLineClose( 'div' )
                    haveOpenMajorSection = False
            # end of closeOpenMajorSection

            def closeOpenSection():
                """ Close a <div> if it's open. """
                nonlocal haveOpenSection
                if haveOpenSection:
                    writerObject.writeLineClose( 'div' )
                    haveOpenSection = False
            # end of closeOpenSection

            def closeOpenSubsection():
                """ Close a <div> if it's open. """
                nonlocal haveOpenSubsection
                if haveOpenSubsection:
                    writerObject.writeLineClose( 'div' )
                    haveOpenSubsection = False
            # end of closeOpenSubsection

            def closeOpenParagraph():
                """ Close a <p> if it's open. """
                nonlocal haveOpenParagraph
                if haveOpenParagraph:
                    writerObject.writeLineClose( 'p' )
                    haveOpenParagraph = False
            # end of closeOpenParagraph

            def closeOpenLG():
                """ Close a <lg> if it's open. """
                nonlocal haveOpenLG
                if haveOpenLG:
                    writerObject.writeLineClose( 'lg' )
                    haveOpenLG = False
            # end of closeOpenLG

            def closeOpenL():
                """ Close a <l> if it's open. """
                nonlocal haveOpenL
                if haveOpenL:
                    writerObject.writeLineClose( 'l' )
                    haveOpenL = False
            # end of closeOpenL

            bRef = self.BibleBooksCodes.getOSISAbbreviation( BBB ) # OSIS book name
            writerObject.writeLineOpen( 'div', [('type',"book"), ('osisID',bRef)] )
            haveOpenIntro = haveOpenOutline = haveOpenMajorSection = haveOpenSection = haveOpenSubsection = needChapterEID = haveOpenParagraph = haveOpenLG = haveOpenL = False
            lastMarker = unprocessedMarker = ''
            for marker,text in bkData.lines:
                if marker in ( 'id', 'h', 'mt2' ): continue # We just ignore these markers
                if marker=='mt1': writerObject.writeLineOpenClose( 'title', checkText(text) )
                elif marker=='is1':
                    if haveOpenIntro: raise Exception( "Not handled yet is1" )
                    writerObject.writeLineOpen( 'div', ('type',"introduction") )
                    writerObject.writeLineOpenClose( 'title', checkText(text) ) # Introduction heading
                    haveOpenIntro = True
                    cRef = bRef + '.0' # Not used by OSIS
                    toOSISGlobals["vRef"] = cRef + '.0' # Not used by OSIS
                elif marker=='ip':
                    if not haveOpenIntro: raise Exception( "Have an ip not in a introduction section" )
                    closeOpenParagraph()
                    writerObject.writeLineOpenText( 'p', checkText(text), noTextCheck=True ) # Sometimes there's text
                    haveOpenParagraph = True
                elif marker=='iot':
                    if not haveOpenIntro: raise Exception( "Have an iot not in a introduction section" )
                    if haveOpenSection or haveOpenOutline: raise Exception( "Not handled yet iot" )
                    closeOpenParagraph()
                    writerObject.writeLineOpen( 'div', ('type',"outline") )
                    writerObject.writeLineOpenClose( 'title', checkText(text) )
                    writerObject.writeLineOpen( 'list' )
                    haveOpenOutline = True
                elif marker=='io1':
                    if not haveOpenIntro: raise Exception( "Have an io1 not in a introduction section" )
                    if not haveOpenOutline: raise Exception( "Have an io1 not in a outline section" )
                    writerObject.writeLineOpenClose( 'item', checkText(text) )
                elif marker=='io2':
                    if not haveOpenIntro: raise Exception( "Have an io2 not in a introduction section" )
                    if not haveOpenOutline: raise Exception( "Have an io2 not in a outline section" )
                    writerObject.writeLineOpenClose( 'item', checkText(text) ) # TODO: Shouldn't this be different from an io1???
                elif marker=='c':
                    if haveOpenOutline:
                        if text!='1': raise Exception( "This should be chapter 1 to close the outline" )
                        writerObject.writeLineClose( 'list' )
                        writerObject.writeLineClose( 'div' )
                        haveOpenOutline = False
                    if haveOpenIntro:
                        if text!='1': raise Exception( "This should normally be chapter 1 to close the introduction" )
                        closeOpenParagraph()
                        writerObject.writeLineClose( 'div' )
                        haveOpenIntro = False
                    closeOpenLG()
                    if needChapterEID:
                        writerObject.writeLineOpenSelfclose( 'chapter', ('eID',cRef) ) # This is an end milestone marker
                    currentChapterNumber = text
                    if not currentChapterNumber.isdigit(): logging.critical( "Can't handle non-digit '%s' chapter number yet" % text )
                    cRef = bRef + '.' + checkText(currentChapterNumber)
                    writerObject.writeLineOpenSelfclose( 'chapter', [('sID',cRef), ('osisID',cRef)] ) # This is a milestone marker
                    needChapterEID = True
                elif marker=='ms1':
                    if haveOpenParagraph:
                        closeOpenLG()
                        closeOpenParagraph()
                    closeOpenSubsection()
                    closeOpenSection()
                    closeOpenMajorSection()
                    writerObject.writeLineOpen( 'div', ('type',"majorSection") )
                    writerObject.writeLineOpenClose( 'title', checkText(text) ) # Section heading
                    haveOpenMajorSection = True
                elif marker=='s1':
                    if haveOpenParagraph:
                        closeOpenLG()
                        closeOpenParagraph()
                    closeOpenSubsection()
                    closeOpenSection()
                    writerObject.writeLineOpen( 'div', ('type', "section") )
                    writerObject.writeLineOpenClose( 'title', checkText(text) ) # Section heading
                    haveOpenSection = True
                elif marker=='s2':
                    if haveOpenParagraph:
                        closeOpenLG()
                        closeOpenParagraph()
                    closeOpenSubsection()
                    writerObject.writeLineOpen( 'div', ('type', "subSection") )
                    writerObject.writeLineOpenClose( 'title',checkText(text) ) # Section heading
                    haveOpenSubsection = True
                elif marker=='mr':
                    # Should only follow a ms1 I think
                    if haveOpenParagraph or haveOpenSection or not haveOpenMajorSection: logging.error( "Didn't expect major reference 'mr' marker after %s" % toOSISGlobals["vRef"] )
                    writerObject.writeLineOpenClose( 'title', checkText(text), ('type',"parallel") ) # Section reference
                elif marker=='r':
                    # Should only follow a s1 I think
                    if haveOpenParagraph or not haveOpenSection: logging.error( "Didn't expect reference 'r' marker after %s" % toOSISGlobals["vRef"] )
                    writerObject.writeLineOpenClose( 'title', checkText(text), ('type',"parallel") ) # Section reference
                elif marker=='p':
                    closeOpenLG()
                    closeOpenParagraph()
                    if not haveOpenSection:
                        writerObject.writeLineOpen( 'div', ('type', "section") )
                        haveOpenSection = True
                    adjustedText = processXRefsAndFootnotes( text )
                    writerObject.writeLineOpenText( 'p', checkText(adjustedText), noTextCheck=True ) # Sometimes there's text
                    haveOpenParagraph = True
                elif marker=='v':
                    if not haveOpenL: closeOpenLG()
                    writeVerse( writerObject, BBB, cRef, text )
                    closeOpenL()
                elif marker=='q1' or marker=='q2' or marker=='q3':
                    qLevel = '1' if marker=='q1' else '2' if marker=='q2' else '3'
                    if not haveOpenLG:
                        writerObject.writeLineOpen( 'lg' )
                        haveOpenLG = True
                    if text:
                        adjustedText = processXRefsAndFootnotes( text )
                        writerObject.writeLineOpenClose( 'l', checkText(adjustedText), ('level',qLevel), noTextCheck=True )
                    else: # No text -- this q1 applies to the next marker
                        writerObject.writeLineOpen( 'l', ('level',qLevel) )
                        haveOpenL = True
                elif marker=='m': # Margin/Flush-left paragraph
                    closeOpenL()
                    closeOpenLG()
                    if text: writerObject.writeLineText( checkText(text) )
                elif marker=='b': # Blank line
                        # Doesn't seem that OSIS has a way to encode this presentation element
                        writerObject.writeNewLine() # We'll do this for now
                else: logging.warning( "We didn't process %s '%s' USFM marker (%s)" % (cRef,marker,text) )
                lastMarker = marker
            if haveOpenIntro or haveOpenOutline or haveOpenLG or haveOpenL or unprocessedMarker: raise Exception( "These shouldn't be open here" )
            if needChapterEID:
                writerObject.writeLineOpenSelfclose( 'chapter', ('eID',cRef) ) # This is an end milestone marker
            if haveOpenParagraph:
                closeOpenLG()
                closeOpenParagraph()
            closeOpenSection()
            closeOpenMajorSection()
            writerObject.writeLineClose( 'div' ) # Close book division
            writerObject.writeNewLine()
        # end of writeBook

        if Globals.verbosityLevel>1: print( "Exporting to OSIS XML format..." )
        xw = XMLWriter().setOutputFilePath( os.path.join( outputFolder, OSISControls["osisOutputFilename"] ) )
        xw.setHumanReadable( 'All' ) # Can be set to 'All', 'Header', or 'None' -- one output file went from None/Header=4.7MB to All=5.7MB
        xw.start()
        xw.writeLineOpen( 'osis', [('xmlns',"http://www.bibletechnologies.net/2003/OSIS/namespace"), ('xmlns:xsi',"http://www.w3.org/2001/XMLSchema-instance"), ('xsi:schemaLocation',"http://www.bibletechnologies.net/2003/OSIS/namespace http://www.bibletechnologies.net/osisCore.2.1.1.xsd")] )
        xw.writeLineOpen( 'osisText', [('osisRefWork',"Bible"), ('xml:lang',OSISControls["xmlLanguage"]), ('osisIDWork',OSISControls["osisIDWork"])] )
        if OSISControls["osisFiles"]=="byBible":
            xw.setSectionName( 'Header' )
            writeHeader( xw )
            xw.setSectionName( 'Main' )
            for BBB,bookData in self.books.items(): # Process each Bible book
                writeBook( xw, BBB, bookData )
        xw.writeLineClose( 'osisText' )
        xw.writeLineClose( 'osis' )
        xw.close()
        print( "Need to find and look at an example where a new chapter isn't a new <p> to see how chapter eIDs should be handled there" )
    # end of toOSIS_XML


    def toSwordModule( self, controlFileFolder, controlFilename ):
        """
        Using settings from the given control file,
            converts the USFM information to a UTF-8 OSIS-XML-based Sword module.
        """
        import struct
        assert( struct.calcsize("IH") == 6 ) # Six-byte format

        # Get the data tables that we need for proper checking
        SwordControls = {}
        ControlFiles.readControlFile( controlFileFolder, controlFilename, SwordControls )
        #print( SwordControls )

        bookAbbrevDict, bookNameDict, bookAbbrevNameDict = {}, {}, {}
        for BBB in self.BibleBooksCodes.getAllReferenceAbbreviations(): # Pre-process the language booknames
            if BBB in SwordControls and SwordControls[BBB]:
                bits = SwordControls[BBB].split(',')
                if len(bits)!=2: logging.error( "Unrecognized language book abbreviation and name for %s: '%'" % ( BBB, OSISControls[BBB] ) )
                bookAbbrev = bits[0].strip().replace('"','') # Remove outside whitespace then the double quote marks
                bookName = bits[1].strip().replace('"','') # Remove outside whitespace then the double quote marks
                bookAbbrevDict[bookAbbrev], bookNameDict[bookName], bookAbbrevNameDict[BBB] = BBB, BBB, (bookAbbrev,bookName,)
                if ' ' in bookAbbrev: bookAbbrevDict[bookAbbrev.replace(' ','',1)] = BBB # Duplicate entries without the first space (presumably between a number and a name like 1 Kings)
                if ' ' in bookName: bookNameDict[bookName.replace(' ','',1)] = BBB # Duplicate entries without the first space

        # Let's write a Sword locale while we're at it
        outputFolder = "OutputFiles"
        if not os.access( outputFolder, os.F_OK ): os.mkdir( outputFolder ) # Make the empty folder if there wasn't already one there
        SwLocFilepath = os.path.join( outputFolder, "SwLocale.conf" )
        print( "Writing Sword locale file %s..." % SwLocFilepath )
        with open( SwLocFilepath, 'wt' ) as SwLocFile:
            SwLocFile.write( '[Meta]\nName=%s\n' % SwordControls["xmlLanguage"] )
            SwLocFile.write( 'Description=%s\n' % SwordControls["LanguageName"] )
            SwLocFile.write( 'Encoding=UTF-8\n\n[Text]\n' )
            for BBB in self.BibleBooksCodes.getAllReferenceAbbreviations():
                if BBB in bookAbbrevNameDict:
                    SwLocFile.write( '%s=%s\n' % (self.BibleBooksCodes.getEnglishName_NR(BBB), bookAbbrevNameDict[BBB][1] ) ) # Write the first English book name and the language book name
            SwLocFile.write( '\n[Book Abbrevs]\n' )
            for BBB in self.BibleBooksCodes.getAllReferenceAbbreviations():
                if BBB in bookAbbrevNameDict:
                    SwLocFile.write( '%s=%s\n' % (self.BibleBooksCodes.getEnglishName_NR(BBB).upper(), self.BibleBooksCodes.getSwordAbbreviation(BBB) ) ) # Write the UPPER CASE language book name and the Sword abbreviation

        # Make our other folders if necessary
        modsdFolder = os.path.join( outputFolder, "mods.d" )
        if not os.access( modsdFolder, os.F_OK ): os.mkdir( modsdFolder ) # Make the empty folder if there wasn't already one there
        modulesFolder = os.path.join( outputFolder, "modules" )
        if not os.access( modulesFolder, os.F_OK ): os.mkdir( modulesFolder ) # Make the empty folder if there wasn't already one there
        textsFolder = os.path.join( modulesFolder, "texts" )
        if not os.access( textsFolder, os.F_OK ): os.mkdir( textsFolder ) # Make the empty folder if there wasn't already one there
        rawTextFolder = os.path.join( textsFolder, "rawtext" )
        if not os.access( rawTextFolder, os.F_OK ): os.mkdir( rawTextFolder ) # Make the empty folder if there wasn't already one there
        lgFolder = os.path.join( rawTextFolder, SwordControls["osisWork"].lower() )
        if not os.access( lgFolder, os.F_OK ): os.mkdir( lgFolder ) # Make the empty folder if there wasn't already one there

        toSwordGlobals = { 'currentID':0, "idStack":[], "vRef":'', "XRefNum":0, "FootnoteNum":0, "lastRef":'', 'offset':0, 'length':0 } # These are our global variables

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
                    assert( toSwordGlobals["lastRef"] )
                    osisRef = toSwordGlobals["lastRef"] # From the last call
                else: # it must have some punctuation in it
                    punctCount = 0
                    for char in ',.:': punctCount += token1.count( char )
                    if punctCount == 1:
                        if token1.endswith(':') and bRef in self.OneChapterOSISBookCodes:
                            V = token1[:-1] # Remove the final colon
                            if not V.isdigit(): logging.warning( "Unable to recognize 1-punct reference format %s '%s' from '%s'" % (cRef, token1, text) )
                            osisRef = bRef + '.1.' + V
                            toSwordGlobals["lastRef"] = osisRef
                        else: # Probably a CV reference like 8:2
                            CV = token1.replace(',','.').replace(':','.') # Make sure it's a dot
                            CVtokens = CV.split('.'); assert( len(CVtokens) == 2 )
                            for CVtoken in CVtokens: # Just double check that we're on the right track
                                if not CVtoken.isdigit(): logging.warning( "Unable to recognize 2nd 1-punct reference format %s '%s' from '%s'" % (cRef, token1, text) ); break
                            osisRef = bRef + '.' + CVtokens[0] + '.' + CVtokens[1]
                            toSwordGlobals["lastRef"] = osisRef
                    elif punctCount==2: # We have two punctuation characters in the reference
                        if token1.endswith(':'): # Let's try handling a final colon
                            CV = token1.replace(',','.',1).replace(':','.',1) # Make sure that the first punctuation character is a dot
                            CVtokens = CV.replace(':','',1).split('.'); assert( len(CVtokens) == 2 )
                            for CVtoken in CVtokens: # Just double check that we're on the right track
                                if not CVtoken.isdigit(): logging.warning( "Unable to recognize 2-punct reference format %s '%s' from '%s'" % (cRef, token1, text) ); break
                            osisRef = bRef + '.' + CVtokens[0] + '.' + CVtokens[1]
                            toSwordGlobals["lastRef"] = osisRef
                        else:
                            print( "convertReferenceToOSISRef got", "'"+text+"'", bRef, cRef ); raise Exception( "No code yet to handle references with multiple punctuation characters", text, token1 )
                    else: # We have >2 punctuation characters in the reference
                        print( "convertReferenceToOSISRef got", "'"+text+"'", bRef, cRef, toSwordGlobals["vRef"] )
                        logging.critical( "No code yet to handle references with more than two punctuation characters '%s' '%s'" % (text, token1) )
                        osisRef = 'XXX3p'
            else:
                print( "convertReferenceToOSISRef got", "'"+text+"'", bRef, cRef, toSwordGlobals["vRef"] )
                logging.critical( "No code yet to handle multiple tokens in a reference: %s" % tokens )
                osisRef = 'XXXmt'
            #print( "convertReferenceToOSISRef returns", osisRef )
            # TODO: We need to call a routine now to actually validate this reference
            return osisRef
        # end of convertReferenceToOSISRef

        def writeIndexEntry( writerObject, indexFile ):
            """ Writes a newLine to the main file and an entry to the index file. """
            writerObject.writeNewLine()
            writerObject._write( "IDX " ) # temp ..... XXXXXXX
            indexFile.write( struct.pack( "IH", toSwordGlobals['offset'], toSwordGlobals['length'] ) )
            toSwordGlobals['offset'] = writerObject.getFilePosition() # Get the new offset
            toSwordGlobals['length'] = 0 # Reset
        # end of writeIndexEntry

        def writeBook( writerObject, ix, BBB, bkData ):
            """ Writes a Bible book to the output files. """

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
                    toSwordGlobals["XRefNum"] += 1
                    OSISxref = '<note osisID="%s!crossreference.%s" osisRef="%s" type="crossReference">' % (toSwordGlobals["XRefNum"],toSwordGlobals["vRef"], toSwordGlobals["vRef"])
                    for j,token in enumerate(USFMxref.split('\\')):
                        #print( "processXRef", j, "'"+token+"'", "from", '"'+USFMxref+'"' )
                        if j==0: # The first token (but the x has already been removed)
                            rest = token.strip()
                            if rest != '-': logging.warning( "We got something else here other than hyphen (probably need to do something with it): %s '%s' from '%s'" % (cRef, token, text) )
                        elif token.startswith('xo '): # xref reference follows
                            osisRef = convertReferenceToOSISRef( token[3:], bRef, cRef )
                            OSISxref += '<reference osisRef="%s" type="source">%s</reference>' % (osisRef,token[3:])
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
                                        osisBook = self.BibleBooksCodes.getOSISAbbreviation( BBB )
                                        #print( BBB, "osisBook", osisBook )
                                    else: # Assume it's the actual reference
                                        if not osisBook: raise Exception( "Book code seems to be wrong or missing for xRef", bit, "from", USFMxref, "at", toSwordGlobals["vRef"] )
                                        punctCount = 0
                                        for char in ',.:-–': # included hyphen and en-dash in here (but not em-dash —)
                                            #print( '', char, bit.count(char), punctCount )
                                            punctCount += bit.count( char )
                                        #print( "punctCount is %i for '%s' in '%s'" % (punctCount,bit,referenceString) )
                                        if punctCount==0: # That's nice and easy
                                            if bit.isdigit() and BBB in self.OneChapterBBBBookCodes: # Then presumably a verse number
                                                xrefChapter = '1'
                                                osisRef = osisBook + '.' + xrefChapter + '.' + bit
                                                OSISxref += '<reference osisRef="%s" type="source">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
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
                                            OSISxref += '<reference osisRef="%s" type="source">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
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
                                                OSISxref += '<reference osisRef="%s" type="source">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
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
                                                OSISxref += '<reference osisRef="%s" type="source">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
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
                                                OSISxref += '<reference osisRef="%s" type="source">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
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
                                                OSISxref += '<reference osisRef="%s" type="source">%s</reference>' % (osisRef,referenceString+('.' if k==len(subTokens)-1 and endsWithPeriod else ''))
                                            else:
                                                raise Exception( "not written yet for 2 punctuation characters in verse number inside cross-reference" )
                                        else:
                                            print( "processXRef", punctCount )
                                            logging.error( "No code yet for xRef with more than 3 punctuation characters %s from %s at %s" % (bit, USFMxref, toSwordGlobals["vRef"]) )
                        elif token.startswith('x '): # another whole xref entry follows
                            rest = token[2:].strip()
                            if rest != '-': logging.warning( "We got something else here other than hyphen (probably need to do something with it): %s '%s' from '%s'" % (cRef, token, text) )
                        elif token in ('xt*', 'x*'):
                            pass # We're being lazy here and not checking closing markers properly
                        else:
                            logging.warning( "Unprocessed '%s' token in %s xref '%s'" % (token, toSwordGlobals["vRef"], USFMxref) )
                    OSISxref += '</note>'
                    #print( '', OSISxref )
                    return OSISxref
                # end of processXRef

                def processFootnote( USFMfootnote ):
                    """
                    Return the OSIS code for the processed footnote.

                    NOTE: The parameter here already has the /f and /f* removed.

                    \\f + \\fr 1:20 \\ft Su ka kaluwasan te Nawumi ‘keupianan,’ piru ka kaluwasan te Mara ‘masakit se geyinawa.’\\f* (Backslashes are shown doubled here)
                        gives
                    <note n="1">1:20 Su ka kaluwasan te Nawumi ‘keupianan,’ piru ka kaluwasan te Mara ‘masakit se geyinawa.’</note> (Crosswire)
                    <note osisRef="Ruth.1.20" osisID="Ruth.1.20!footnote.1" n="+"><reference type="source" osisRef="Ruth.1.20">1:20 </reference>Su ka kaluwasan te Nawumi ‘keupianan,’ piru ka kaluwasan te Mara ‘masakit se geyinawa.’</note> (Snowfall)
                    """
                    toSwordGlobals["FootnoteNum"] += 1
                    OSISfootnote = '<note osisRef="%s" osisID="%s!footnote.%s">' % (toSwordGlobals["vRef"],toSwordGlobals["vRef"],toSwordGlobals["FootnoteNum"])
                    for j,token in enumerate(USFMfootnote.split('\\')):
                        #print( "processFootnote", j, token, USFMfootnote )
                        if j==0: continue # ignore the + for now
                        elif token.startswith('fr '): # footnote reference follows
                            osisRef = convertReferenceToOSISRef( token[3:], bRef, cRef )
                            OSISfootnote += '<reference osisRef="%s" type="source">%s</reference>' % (osisRef,token[3:])
                        elif token.startswith('ft '): # footnote text follows
                            OSISfootnote += token[3:]
                        elif token.startswith('fq '): # footnote quote follows -- NOTE: We also assume here that the next marker closes the fq field
                            OSISfootnote += '<catchWord>%s</catchWord>' % token[3:] # Note that the trailing space goes in the catchword here -- seems messy
                        elif token in ('ft*','fq*'):
                            pass # We're being lazy here and not checking closing markers properly
                        else:
                            logging.warning( "Unprocessed '%s' token in %s footnote '%s'" % (token, toSwordGlobals["vRef"], USFMfootnote) )
                    OSISfootnote += '</note>'
                    #print( '', OSISfootnote )
                    return OSISfootnote
                # end of processFootnote

                while '\\x ' in verse and '\\x*' in verse: # process cross-references (xrefs)
                    ix1 = verse.index('\\x ')
                    ix2 = verse.find('\\x* ') # Note the extra space here at the end
                    if ix2 == -1: # Didn't find it so must be no space after the asterisk
                        ix2 = verse.index('\\x*')
                        ix2b = ix2 + 3 # Where the xref ends
                        logging.warning( 'No space after xref entry in %s' % toSwordGlobals["vRef"] )
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
#                        #logging.warning( 'No space after footnote entry in %s' % toSwordGlobals["vRef"] )
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
                    logging.warning( "Unexpected double angle brackets in %s: '%s' field is '%s'" % (toSwordGlobals["vRef"],marker,textToCheck) )
                    textToCheck = textToCheck.replace('<<','“' ).replace('>>','”' )
                if '\\bk ' in textToCheck and '\\bk*' in textToCheck:
                    textToCheck = textToCheck.replace('\\bk ','<reference type="x-bookName">').replace('\\bk*','</reference>')
                if '\\' in textToCheck:
                    logging.error( "We still have some unprocessed backslashes in %s: '%s' field is '%s'" % (toSwordGlobals["vRef"],marker,textToCheck) )
                    textToCheck = textToCheck.replace('\\','ENCODING ERROR HERE ' )
                return textToCheck
            # end of checkText

            def writeVerse( writerObject, indexFile, BBB, cRef, text ):
                """
                Processes and writes a verse to the OSIS XML writerObject.
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
                    toSwordGlobals["vRef"]  = cRef + '.' + bits[0]
                    vRef2 = cRef + '.' + bits[1]
                    sID    = toSwordGlobals["vRef"] + '-' + vRef2
                    osisID = toSwordGlobals["vRef"] + ' ' + vRef2
                elif ',' in verseNumber:
                    raise Exception( "not written yet for comma in versenumber" )
                elif verseNumber.isdigit():
                    sID = osisID = toSwordGlobals["vRef"] = cRef + '.' + verseNumber
                else: logging.critical( "Don't handle verse number of form '%s' yet for %s" % (verseNumber,cRef) )
                adjText = processXRefsAndFootnotes( verseText )
                writerObject.writeLineText( checkText(adjText), noTextCheck=True )
                writeIndexEntry( writerObject, indexFile )
            # end of writeVerse

            def closeOpenMajorSection():
                """ Close a <div> if it's open. """
                nonlocal haveOpenMajorSection
                if haveOpenMajorSection:
                    writerObject.writeLineClose( 'div' )
                    haveOpenMajorSection = False
            # end of closeOpenMajorSection

            def closeOpenSection():
                """ Close a <div> if it's open. """
                nonlocal haveOpenSection
                if haveOpenSection:
                    writerObject.writeLineClose( 'div' )
                    haveOpenSection = False
            # end of closeOpenSection

            def closeOpenSubsection():
                """ Close a <div> if it's open. """
                nonlocal haveOpenSubsection
                if haveOpenSubsection:
                    writerObject.writeLineClose( 'div' )
                    haveOpenSubsection = False
            # end of closeOpenSubsection

            def closeOpenParagraph():
                """ Close a <p> if it's open. """
                nonlocal haveOpenParagraph
                if haveOpenParagraph:
                    writerObject.writeLineOpenSelfclose( 'div', [('eID',toSwordGlobals['idStack'].pop()), ('type',"paragraph")] )
                    haveOpenParagraph = False
            # end of closeOpenParagraph

            def closeOpenLG():
                """ Close a <lg> if it's open. """
                nonlocal haveOpenLG
                if haveOpenLG:
                    writerObject.writeLineClose( 'lg' )
                    haveOpenLG = False
            # end of closeOpenLG

            def closeOpenL():
                """ Close a <l> if it's open. """
                nonlocal haveOpenL
                if haveOpenL:
                    writerObject.writeLineClose( 'l' )
                    haveOpenL = False
            # end of closeOpenL

            def getNextID():
                """ Returns the next sID sequence code. """
                toSwordGlobals['currentID'] += 1
                return "gen%i" % toSwordGlobals['currentID']
            # end of getNextID

            def getSID():
                """ Returns a tuple containing ('sID', getNextID() ). """
                ID = getNextID()
                toSwordGlobals['idStack'].append( ID )
                return ('sID', ID )
            # end of getSID

            bRef = self.BibleBooksCodes.getOSISAbbreviation( BBB ) # OSIS book name
            writerObject.writeLineOpenSelfclose( 'div', [('osisID',bRef), getSID(), ('type',"book")] )
            haveOpenIntro = haveOpenOutline = haveOpenMajorSection = haveOpenSection = haveOpenSubsection = needChapterEID = haveOpenParagraph = haveOpenLG = haveOpenL = False
            lastMarker = unprocessedMarker = ''
            for marker,text in bkData.lines:
                if marker in ( 'id', 'h', 'mt2' ): continue # We just ignore these markers
                if marker=='mt1': writerObject.writeLineOpenClose( 'title', checkText(text) )
                elif marker=='is1':
                    if haveOpenIntro: raise Exception( "Not handled yet is1" )
                    writerObject.writeLineOpenSelfclose( 'div', [getSID(), ('type',"introduction")] )
                    writerObject.writeLineOpenClose( 'title', checkText(text) ) # Introduction heading
                    haveOpenIntro = True
                    cRef = bRef + '.0' # Not used by OSIS
                    toSwordGlobals["vRef"] = cRef + '.0' # Not used by OSIS
                elif marker=='ip':
                    if not haveOpenIntro: raise Exception( "Have an ip not in a introduction section" )
                    closeOpenParagraph()
                    writerObject.writeLineOpenSelfclose( 'div', [getSID(), ('type',"paragraph")] )
                    writerObject.writeLineText( checkText(text), noTextCheck=True ) # Sometimes there's text
                    haveOpenParagraph = True
                elif marker=='iot':
                    if not haveOpenIntro: raise Exception( "Have an iot not in a introduction section" )
                    if haveOpenSection or haveOpenOutline: raise Exception( "Not handled yet iot" )
                    closeOpenParagraph()
                    writerObject.writeLineOpenSelfclose( 'div', [getSID(), ('type',"outline")] )
                    writerObject.writeLineOpenClose( 'title', checkText(text) )
                    writerObject.writeLineOpen( 'list' )
                    haveOpenOutline = True
                elif marker=='io1':
                    if not haveOpenIntro: raise Exception( "Have an io1 not in a introduction section" )
                    if not haveOpenOutline: raise Exception( "Have an io1 not in a outline section" )
                    writerObject.writeLineOpenClose( 'item', checkText(text) )
                elif marker=='io2':
                    if not haveOpenIntro: raise Exception( "Have an io2 not in a introduction section" )
                    if not haveOpenOutline: raise Exception( "Have an io2 not in a outline section" )
                    writerObject.writeLineOpenClose( 'item', checkText(text) ) # TODO: Shouldn't this be different from an io1???
                elif marker=='c':
                    if haveOpenOutline:
                        if text!='1': raise Exception( "This should be chapter 1 to close the outline" )
                        writerObject.writeLineClose( 'list' )
                        writerObject.writeLineOpenSelfclose( 'div', [('eID',toSwordGlobals['idStack'].pop()), ('type',"outline")] )
                        haveOpenOutline = False
                    if haveOpenIntro:
                        if text!='1': raise Exception( "This should normally be chapter 1 to close the introduction" )
                        closeOpenParagraph()
                        writerObject.writeLineOpenSelfclose( 'div', [('eID',toSwordGlobals['idStack'].pop()), ('type',"introduction")] )
                        haveOpenIntro = False
                    closeOpenLG()
                    if needChapterEID:
                        writerObject.writeLineOpenSelfclose( 'chapter', ('eID',cRef) ) # This is an end milestone marker
                    writeIndexEntry( writerObject, ix )
                    currentChapterNumber = text
                    if not currentChapterNumber.isdigit(): logging.critical( "Can't handle non-digit '%s' chapter number yet" % text )
                    cRef = bRef + '.' + checkText(currentChapterNumber)
                    writerObject.writeLineOpenSelfclose( 'chapter', [('osisID',cRef), ('sID',cRef)] ) # This is a milestone marker
                    needChapterEID = True
                    writeIndexEntry( writerObject, ix )
                elif marker=='ms1':
                    if haveOpenParagraph:
                        closeOpenLG()
                        closeOpenParagraph()
                    closeOpenSubsection()
                    closeOpenSection()
                    closeOpenMajorSection()
                    writerObject.writeLineOpen( 'div', ('type',"majorSection") )
                    writerObject.writeLineOpenClose( 'title', checkText(text) ) # Section heading
                    haveOpenMajorSection = True
                elif marker=='s1':
                    if haveOpenParagraph:
                        closeOpenLG()
                        closeOpenParagraph()
                    closeOpenSubsection()
                    closeOpenSection()
                    writerObject.writeLineOpenSelfclose( 'div', [getSID(), ('type',"section")] )
                    writerObject.writeLineOpenClose( 'title', checkText(text) ) # Section heading
                    haveOpenSection = True
                elif marker=='s2':
                    if haveOpenParagraph:
                        closeOpenLG()
                        closeOpenParagraph()
                    closeOpenSubsection()
                    writerObject.writeLineOpen( 'div', ('type', "subSection") )
                    writerObject.writeLineOpenClose( 'title',checkText(text) ) # Section heading
                    haveOpenSubsection = True
                elif marker=='mr':
                    # Should only follow a ms1 I think
                    if haveOpenParagraph or haveOpenSection or not haveOpenMajorSection: logging.error( "Didn't expect major reference 'mr' marker after %s" % toSwordGlobals["vRef"] )
                    writerObject.writeLineOpenClose( 'title', checkText(text), ('type',"parallel") ) # Section reference
                elif marker=='r':
                    # Should only follow a s1 I think
                    if haveOpenParagraph or not haveOpenSection: logging.error( "Didn't expect reference 'r' marker after %s" % toSwordGlobals["vRef"] )
                    writerObject.writeLineOpenClose( 'title', checkText(text), ('type',"parallel") ) # Section reference
                elif marker=='p':
                    closeOpenLG()
                    closeOpenParagraph()
                    if not haveOpenSection:
                        writerObject.writeLineOpenSelfclose( 'div', [getSID(), ('type',"section")] )
                        haveOpenSection = True
                    adjustedText = processXRefsAndFootnotes( text )
                    writerObject.writeLineOpenSelfclose( 'div', [getSID(), ('type',"paragraph")] )
                    writerObject.writeLineText( checkText(adjustedText), noTextCheck=True ) # Sometimes there's text
                    haveOpenParagraph = True
                elif marker=='v':
                    if not haveOpenL: closeOpenLG()
                    writeVerse( writerObject, ix, BBB, cRef, text )
                    closeOpenL()
                elif marker=='q1' or marker=='q2' or marker=='q3':
                    qLevel = '1' if marker=='q1' else '2' if marker=='q2' else '3'
                    if not haveOpenLG:
                        writerObject.writeLineOpen( 'lg' )
                        haveOpenLG = True
                    if text:
                        adjustedText = processXRefsAndFootnotes( text )
                        writerObject.writeLineOpenClose( 'l', checkText(adjustedText), ('level',qLevel), noTextCheck=True )
                    else: # No text -- this q1 applies to the next marker
                        writerObject.writeLineOpen( 'l', ('level',qLevel) )
                        haveOpenL = True
                elif marker=='m': # Margin/Flush-left paragraph
                    closeOpenL()
                    closeOpenLG()
                    if text: writerObject.writeLineText( checkText(text) )
                elif marker=='b': # Blank line
                        # Doesn't seem that OSIS has a way to encode this presentation element
                        writerObject.writeNewLine() # We'll do this for now
                else: logging.warning( "We didn't process %s '%s' USFM marker (%s)" % (cRef,marker,text) )
                lastMarker = marker
            if haveOpenIntro or haveOpenOutline or haveOpenLG or haveOpenL or unprocessedMarker: raise Exception( "These shouldn't be open here" )
            if needChapterEID:
                writerObject.writeLineOpenSelfclose( 'chapter', ('eID',cRef) ) # This is an end milestone marker
            if haveOpenParagraph:
                closeOpenLG()
                closeOpenParagraph()
            closeOpenSection()
            closeOpenMajorSection()
            writerObject.writeLineClose( 'div' ) # Close book division
            writerObject.writeNewLine()
        # end of writeBook

        # An uncompressed Sword module consists of a .conf file
        #   plus ot and nt XML files with binary indexes ot.vss and nt.vss (containing 6-byte chunks = 4-byte offset, 2-byte length)
        if Globals.verbosityLevel>1: print( "Exporting to Sword modified-OSIS XML format..." )
        xwOT = XMLWriter().setOutputFilePath( os.path.join( lgFolder, 'ot' ) )
        xwNT = XMLWriter().setOutputFilePath( os.path.join( lgFolder, 'nt' ) )
        xwOT.setHumanReadable( 'NLSpace', indentSize=5 ) # Can be set to 'All', 'Header', or 'None'
        xwNT.setHumanReadable( 'NLSpace', indentSize=5 ) # Can be set to 'All', 'Header', or 'None'
        xwOT.start( noAutoXML=True ); xwNT.start( noAutoXML=True )
        toSwordGlobals['length'] = xwOT.writeLineOpenSelfclose( 'milestone', [('type',"x-importer"), ('subtype',"x-USFMBible.py"), ('n',"$%s $" % versionString)] )
        toSwordGlobals['length'] = xwNT.writeLineOpenSelfclose( 'milestone', [('type',"x-importer"), ('subtype',"x-USFMBible.py"), ('n',"$%s $" % versionString)] )
        xwOT.setSectionName( 'Main' ); xwNT.setSectionName( 'Main' )
        with open( os.path.join( lgFolder, 'ot.vss' ), 'wb' ) as ixOT, open( os.path.join( lgFolder, 'nt.vss' ), 'wb' ) as ixNT:
            ixOT.write( struct.pack( "IH", 0, 0 ) ) # Write the first dummy entry
            ixNT.write( struct.pack( "IH", 0, 0 ) ) # Write the first dummy entry
            writeIndexEntry( xwOT, ixOT ) # Write the second entry pointing to the opening milestone
            writeIndexEntry( xwNT, ixNT ) # Write the second entry pointing to the opening milestone
            for BBB,bookData in self.books.items(): # Process each Bible book
                if self.BibleBooksCodes.isOldTestament_NR( BBB ):
                    xw = xwOT; ix = ixOT
                elif self.BibleBooksCodes.isNewTestament_NR( BBB ):
                    xw = xwNT; ix = ixNT
                else: raise Exception( "Unexpected %s Bible book" % BBB )
                writeBook( xw, ix, BBB, bookData )
        xwOT.close(); xwNT.close()
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
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML file to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 0: print( "%s V%s" % ( progName, versionString ) )

    uB = USFMBible( "Matigsalug" )
    uB.load( "/mnt/Data/Matigsalug/Scripture/MBTV" )
    print( uB )
    #print( uB.getVersification () )

    if Globals.commandLineOptions.export:
        if Globals.verbosityLevel > 0: print( "NOTE: This is %s V%s -- i.e., still just alpha quality software!" % ( progName, versionString ) )
        #uB.toZefania_XML( '', os.path.join( 'ControlFiles', "MBT_to_Zefania_controls.txt" ) )
        #uB.toOSIS_XML( '', os.path.join( 'ControlFiles', "MBT_to_OSIS_controls.txt" ) )
        uB.toSwordModule( '', os.path.join( 'ControlFiles', "MBT_to_OSIS_controls.txt" ) ) # We use the same OSIS controls
        #uB.toBible( os.path.join( 'ScrapedFiles', "TestBible.module" ) )

if __name__ == '__main__':
    main()
## End of USFMBible.py
