#!/usr/bin/python3
#
# USFMBible.py
#
# Module handling the USFM markers for Bible books
#   Last modified: 2011-01-27 by RJH (also update versionString below)
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
Module for defining and manipulating USFM Bible markers.
"""

progName = "USFM Bible handler"
versionString = "0.19"


import os, logging, datetime
from gettext import gettext as _
from collections import OrderedDict

from singleton import singleton
import Globals, ControlFiles
from BibleBooksCodes import BibleBooksCodes
from BibleOrganizationalSystems import BibleOrganizationalSystem
from BibleReferences import BibleReferenceList
from XMLWriter import XMLWriter


# Globals
USFMVersion = "2.3" # July 2010 at http://paratext.ubs-translations.org/about/usfm


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

        logging.info( "  " + _("Loading {}...").format( filename ) )
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
                logging.warning( _("Unexpected '{}' paragraph marker in Bible book {} (Text is '{}')").format( marker, self.bookReferenceCode, text ) )
    # end of load

    def getVersification( self ):
        """
        Get the versification of the book into a two lists of (c, v) tuples.
            The first list contains an entry for each chapter in the book showing the number of verses.
            The second list contains an entry for each missing verse in the book (not including verses that are missing at the END of a chapter).
        Note that all chapter and verse values are returned as strings not integers.
        """
        assert( self.lines )

        versification, omittedVerses, combinedVerses, reorderedVerses = [], [], [], []
        chapterText, chapterNumberString, lastChapterNumber = '0', 0, 0
        verseText, verseNumberString, lastVerseNumber = '0', 0, 0
        for marker,text in self.lines:
            #print( marker, text )
            if marker == 'c':
                if chapterNumberString > 0:
                    versification.append( (chapterText, str(lastVerseNumber),) )
                chapterText = text.strip()
                if ' ' in chapterText: # Seems that we can have footnotes here :)
                    logging.info( _("Unexpected space in USFM chapter number field '{}' after chapter {} of {}").format( chapterText, lastChapterNumber, self.bookReferenceCode ) )
                    chapterText = chapterText.split( None, 1)[0]
                #print( "{} chapter {}".format( self.bookReferenceCode, chapterText ) )
                chapterNumberString = int( chapterText)
                if chapterNumberString != lastChapterNumber+1:
                    logging.error( _("USFM chapter numbers out of sequence in Bible book {} ({} after {})").format( self.bookReferenceCode, chapterNumberString, lastChapterNumber ) )
                lastChapterNumber = chapterNumberString
                verseText, verseNumberString, lastVerseNumber = '0', 0, 0
            elif marker == 'cp':
                logging.warning( _("Encountered cp field {} after {}:{} of {}").format( text, chapterNumberString, lastVerseNumber, self.bookReferenceCode ) )
            elif marker == 'v':
                if not text:
                    logging.warning( _("Missing USFM verse number after {} in chapter {} of {}").format( lastVerseNumber, chapterNumberString, self.bookReferenceCode ) )
                    continue
                try:
                    verseText = text.split( None, 1 )[0]
                except:
                    print( "verseText is '{}'".format(verseText) )
                    halt
                doneWarning = False
                for char in 'abcdefghijklmnopqrstuvwxyz[]()\\':
                    if char in verseText:
                        if not doneWarning:
                            logging.info( _("Removing letter(s) from USFM verse number {} in Bible book {} {}").format( verseText, self.bookReferenceCode, chapterText ) )
                            doneWarning = True
                        verseText = verseText.replace( char, '' )
                if '-' in verseText or '–' in verseText: # we have a range like 7-9 with hyphen or en-dash
                    logging.info( _("Encountered combined verses field {} after {}:{} of {}").format( verseText, chapterNumberString, lastVerseNumber, self.bookReferenceCode ) )
                    bits = verseText.replace('–','-').split( '-', 1 ) # Make sure that it's a hyphen then split once
                    verseNumberString = bits[0]
                    endVerseNumber = bits[1]
                    if int(verseNumberString) >= int(endVerseNumber):
                        logging.error( _("USFM verse range out of sequence in Bible book {} {} ({}-{})").format( self.bookReferenceCode, chapterText, verseNumberString, endVerseNumber ) )
                    #else:
                    combinedVerses.append( (chapterText, verseText,) )
                elif ',' in verseText: # we have a range like 7,8
                    logging.info( _("Encountered comma combined verses field {} after {}:{} of {}").format( verseText, chapterNumberString, lastVerseNumber, self.bookReferenceCode ) )
                    bits = verseText.split( ',', 1 )
                    verseNumberString = bits[0]
                    endVerseNumber = bits[1]
                    if int(verseNumberString) >= int(endVerseNumber):
                        logging.error( _("USFM verse range out of sequence in Bible book {} {} ({}-{})").format( self.bookReferenceCode, chapterText, verseNumberString, endVerseNumber ) )
                    #else:
                    combinedVerses.append( (chapterText, verseText,) )
                else: # Should be just a single verse number
                    verseNumberString = verseText
                    endVerseNumber = verseNumberString
                if int(verseNumberString) != int(lastVerseNumber)+1:
                    if int(verseNumberString) <= int(lastVerseNumber):
                        logging.warning( _("USFM verse numbers out of sequence in Bible book {} {} ({} after {})").format( self.bookReferenceCode, chapterText, verseText, lastVerseNumber ) )
                    else: # Must be missing some verse numbers
                        logging.info( _("Missing USFM verse number(s) between {} and {} in Bible book {} {}").format( lastVerseNumber, verseNumberString, self.bookReferenceCode, chapterText ) )
                        for number in range( int(lastVerseNumber)+1, int(verseNumberString) ):
                            omittedVerses.append( (chapterText, str(number),) )
                lastVerseNumber = endVerseNumber
        versification.append( (chapterText, str(lastVerseNumber),) ) # Append the verse count for the final chapter
        if reorderedVerses: print( reorderedVerses ); halt
        return versification, omittedVerses, combinedVerses, reorderedVerses
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

        logging.info( _("Loading {} from {}...").format( self.name, folder ) )
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
        totalVersification, totalOmittedVerses, totalCombinedVerses, totalReorderedVerses = OrderedDict(), OrderedDict(), OrderedDict(), OrderedDict()
        for bookReferenceCode in self.books.keys():
            versification, omittedVerses, combinedVerses, reorderedVerses = self.books[bookReferenceCode].getVersification()
            totalVersification[bookReferenceCode] = versification
            if omittedVerses:
                totalOmittedVerses[bookReferenceCode] = omittedVerses
            if combinedVerses:
                totalCombinedVerses[bookReferenceCode] = combinedVerses
            if reorderedVerses:
                totalReorderedVerses[bookReferenceCode] = reorderedVerses
        return totalVersification, totalOmittedVerses, totalCombinedVerses, totalReorderedVerses
    # end of getVersification


    def toMediaWiki( self, controlFileFolder, controlFilename, wantErrorMessages=False ):
        """
        Using settings from the given control file,
            converts the USFM information to a UTF-8 Zefania XML file.

        This format is roughly documented at http://de.wikipedia.org/wiki/Zefania_XML
            but more fields can be discovered by looking at downloaded files.
        """
        # Get the data tables that we need for proper checking
        MediaWikiControls = {}
        ControlFiles.readControlFile( controlFileFolder, controlFilename, MediaWikiControls )
        #print( MediaWikiControls )
        unhandledMarkers = set()

        bookAbbrevDict, bookNameDict, bookAbbrevNameDict = {}, {}, {}
        #for BBB in BBC_BBBDict.keys(): # Pre-process the language booknames
        for BBB in self.BibleBooksCodes.getAllReferenceAbbreviations(): # Pre-process the language booknames
            if BBB in MediaWikiControls and MediaWikiControls[BBB]:
                bits = MediaWikiControls[BBB].split(',')
                if len(bits)!=2: logging.error( _("Unrecognized language book abbreviation and name for {}: '{}'").format( BBB, MediaWikiControls[BBB] ) )
                bookAbbrev = bits[0].strip().replace('"','') # Remove outside whitespace then the double quote marks
                bookName = bits[1].strip().replace('"','') # Remove outside whitespace then the double quote marks
                bookAbbrevDict[bookAbbrev], bookNameDict[bookName], bookAbbrevNameDict[BBB] = BBB, BBB, (bookAbbrev,bookName,)
                if ' ' in bookAbbrev: bookAbbrevDict[bookAbbrev.replace(' ','',1)] = BBB # Duplicate entries without the first space (presumably between a number and a name like 1 Kings)
                if ' ' in bookName: bookNameDict[bookName.replace(' ','',1)] = BBB # Duplicate entries without the first space

        toWikiMediaGlobals = { "vRef":'', "XRefNum":0, "FootnoteNum":0, "lastRef":'', "OneChapterOSISBookCodes":self.BibleBooksCodes.getOSISSingleChapterBooksList() } # These are our global variables

# TODO: Need to handle footnotes \f + \fr ref \fk key \ft text \f* 	becomes <ref><!--\fr ref \fk key \ft-->text</ref>
        def writeBook( writerObject, BBB, bkData ):
            """Writes a book to the MediaWiki writerObject."""

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
                    nonlocal BBB
                    toWikiMediaGlobals["XRefNum"] += 1
                    OSISxref = '<note type="crossReference" osisRef="{}" osisID="{}!crossreference.{}">'.format(toWikiMediaGlobals["vRef"],toWikiMediaGlobals["vRef"],toWikiMediaGlobals["XRefNum"])
                    for j,token in enumerate(USFMxref.split('\\')):
                        #print( "processXRef", j, "'"+token+"'", "from", '"'+USFMxref+'"' )
                        if j==0: # The first token (but the x has already been removed)
                            rest = token.strip()
                            if rest != '-': logging.warning( _("We got something else here other than hyphen (probably need to do something with it): {} '{}' from '{}'").format(cRef, token, text) )
                        elif token.startswith('xo '): # xref reference follows
                            adjToken = token[3:].strip()
                            if adjToken.endswith(' a'): adjToken = adjToken[:-2] # Remove any 'a' suffix (occurs when a cross-reference has multiple (a and b) parts
                            if adjToken.endswith(':'): adjToken = adjToken[:-1] # Remove any final colon (this is a language dependent hack)
                            adjToken = BOS.getBookAbbreviation(BBB) + ' ' + adjToken # Prepend the vernacular book abbreviation
                            osisRef = BRL.parseToOSIS( adjToken, wantErrorMessages )
                            if osisRef is not None:
                                OSISxref += '<reference type="source" osisRef="{}">{}</reference>'.format(osisRef,token[3:])
                                if wantErrorMessages and not BRL.containsReference( BBB, currentChapterNumberString, verseNumberString ):
                                    logging.error( _("Cross-reference at {} {}:{} seems to contain the wrong self-reference '{}'").format(BBB,currentChapterNumberString,verseNumberString, token) )
                        elif token.startswith('xt '): # xref text follows
                            xrefText = token[3:]
                            finalPunct = ''
                            while xrefText[-1] in (' ,;.'): finalPunct = xrefText[-1] + finalPunct; xrefText = xrefText[:-1]
                            #adjString = xrefText[:-6] if xrefText.endswith( ' (LXX)' ) else xrefText # Sorry, this is a crude hack to avoid unnecessary error messages
                            osisRef = BRL.parseToOSIS( xrefText, wantErrorMessages )
                            if osisRef is not None:
                                OSISxref += '<reference type="source" osisRef="{}">{}</reference>'.format(osisRef,xrefText+finalPunct)
                        elif token.startswith('x '): # another whole xref entry follows
                            rest = token[2:].strip()
                            if rest != '-': logging.warning( _("We got something else here other than hyphen (probably need to do something with it): {} '{}' from '{}'").format(cRef, token, text) )
                        elif token in ('xt*', 'x*'):
                            pass # We're being lazy here and not checking closing markers properly
                        else:
                            logging.warning( _("Unprocessed '{}' token in {} xref '{}'").format(token, toOSISGlobals["vRef"], USFMxref) )
                    OSISxref += '</note>'
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
                    toWikiMediaGlobals["FootnoteNum"] += 1
                    OSISfootnote = '<note osisRef="{}" osisID="{}!footnote.{}">'.format(toWikiMediaGlobals["vRef"],toWikiMediaGlobals["vRef"],toWikiMediaGlobals["FootnoteNum"])
                    for j,token in enumerate(USFMfootnote.split('\\')):
                        #print( "processFootnote", j, token, USFMfootnote )
                        if j==0: continue # ignore the + for now
                        elif token.startswith('fr '): # footnote reference follows
                            adjToken = token[3:].strip()
                            if adjToken.endswith(':'): adjToken = adjToken[:-1] # Remove any final colon (this is a language dependent hack)
                            adjToken = BOS.getBookAbbreviation(BBB) + ' ' + adjToken # Prepend the vernacular book abbreviation
                            osisRef = BRL.parseToOSIS( adjToken, wantErrorMessages )
                            if osisRef is not None:
                                OSISfootnote += '<reference osisRef="{}" type="source">{}</reference>'.format(osisRef,token[3:])
                                if wantErrorMessages and not BRL.containsReference( BBB, currentChapterNumberString, verseNumberString ):
                                    logging.error( _("Footnote at {} {}:{} seems to contain the wrong self-reference '{}'").format(BBB,currentChapterNumberString,verseNumberString, token) )
                        elif token.startswith('ft '): # footnote text follows
                            OSISfootnote += token[3:]
                        elif token.startswith('fq '): # footnote quote follows -- NOTE: We also assume here that the next marker closes the fq field
                            OSISfootnote += '<catchWord>{}</catchWord>'.format(token[3:]) # Note that the trailing space goes in the catchword here -- seems messy
                        elif token in ('ft*','fq*'):
                            pass # We're being lazy here and not checking closing markers properly
                        else:
                            logging.warning( _("Unprocessed '{}' token in {} footnote '{}'").format(token, toWikiMediaGlobals["vRef"], USFMfootnote) )
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
                        logging.warning( _("No space after xref entry in {}").format(toWikiMediaGlobals["vRef"]) )
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
#                        #logging.warning( 'No space after footnote entry in {}'.format(toWikiMediaGlobals["vRef"] )
#                    else: ix2b = ix2 + 4
                    footnote = verse[ix1+3:ix2]
                    osisFootnote = processFootnote( footnote )
                    #print( osisFootnote )
                    verse = verse[:ix1] + osisFootnote + verse[ix2+3:]
#                    verse = verse[:ix1] + osisFootnote + verse[ix2b:]
                return verse
            # end of processXRefsAndFootnotes

            bRef = self.BibleBooksCodes.getOSISAbbreviation( BBB ) # OSIS book name
            for marker,text in bkData.lines: # Process USFM lines
                if marker in ("id","h","mt1"):
                    writerObject.writeLineComment( '\\{} {}'.format( marker, text ) )
                    bookName = text # in case there's no toc2 entry later
                elif marker=="toc2":
                    bookName = text
                elif marker=="li":
                    # :<!-- \li -->text
                    writerObject.writeLineText( ":" )
                    writerObject.writeLineComment( '\\li' )
                    writerObject.writeLineText( text )
                elif marker=="c":
                    chapterNumberString = text
                    cRef = bRef + '.' + chapterNumberString
                    # Bible:BookName_#
                    writerObject.writeLineText( 'Bible:{}_{}'.format(bookName, chapterNumberString) )
                elif marker=="s1":
                    # === text ===
                    writerObject.writeLineText( '=== {} ==='.format(text) )
                elif marker=="r":
                    # <span class="srefs">text</span> 
                    writerObject.writeLineOpenClose( 'span', text, ('class','srefs') )
                elif marker=="p":
                    writerObject.writeNewLine(); writerObject.writeNewLine();
                elif marker=="v":
                    verseNumberString = text.split()[0] # Get the first token which is the first number
                    verseText = text[len(verseNumberString)+1:].lstrip() # Get the rest of the string which is the verse text
                    # TODO: We haven't stripped out character fields from within the verse -- not sure how MediaWiki handles them yet
                    if not verseText: # this is an empty (untranslated) verse
                        adjText = '- - -' # but we'll put in a filler
                    else: adjText = processXRefsAndFootnotes( verseText )
                    # <span id="chapter#_#"><sup>#</sup> text</span> 
                    writerObject.writeLineOpenClose( 'span', '<sup>{}</sup> {}'.format(verseNumberString,adjText), ('id',"chapter{}_{}".format(chapterNumberString, verseNumberString) ), noTextCheck=True )
                elif marker=="q1":
                    adjText = processXRefsAndFootnotes( verseText )
                    writerObject.writeLineText( ':{}'.format(adjText, noTextCheck=True) ) # No check so it doesn't choke on embedded xref and footnote fields
                elif marker=="q2":
                    adjText = processXRefsAndFootnotes( verseText )
                    writerObject.writeLineText( '::{}'.format(adjText, noTextCheck=True) )
                elif marker=='m': # Margin/Flush-left paragraph
                    adjText = processXRefsAndFootnotes( verseText )
                    writerObject.writeLineText( '::{}'.format(adjText, noTextCheck=True) )
                else:
                    unhandledMarkers.add( marker )
        # end of writeBook

        # Set-up our Bible reference system
        BOS = BibleOrganizationalSystem( MediaWikiControls["PublicationCode"] )
        BRL = BibleReferenceList( self.BibleBooksCodes, BOS )

        if Globals.verbosityLevel>1: print( _("Exporting to MediaWiki format...") )
        outputFolder = "OutputFiles"
        if not os.access( outputFolder, os.F_OK ): os.mkdir( outputFolder ) # Make the empty folder if there wasn't already one there
        xw = XMLWriter().setOutputFilePath( os.path.join( outputFolder, MediaWikiControls["MediaWikiOutputFilename"] ) )
        xw.setHumanReadable()
        xw.start()
        for BBB,bookData in self.books.items():
            writeBook( xw, BBB, bookData )
        xw.close()
        if unhandledMarkers and Globals.verbosityLevel>0: print( "  " + _("WARNING: Unhandled USFM markers were {}").format(unhandledMarkers) )
    # end of toMediaWiki



    def toZefania_XML( self, controlFileFolder, controlFilename, wantErrorMessages=False ):
        """
        Using settings from the given control file,
            converts the USFM information to a UTF-8 Zefania XML file.

        This format is roughly documented at http://de.wikipedia.org/wiki/Zefania_XML
            but more fields can be discovered by looking at downloaded files.
        """
        # Get the data tables that we need for proper checking
        ZefaniaControls = {}
        ControlFiles.readControlFile( controlFileFolder, controlFilename, ZefaniaControls )
        unhandledMarkers = set()

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
            for marker,text in bkData.lines: # Process USFM lines
                if marker=="c":
                    if haveOpenChapter:
                        writerObject.writeLineClose ( 'CHAPTER' )
                    writerObject.writeLineOpen ( 'CHAPTER', ('cnumber',text) )
                    haveOpenChapter = True
                elif marker=="v":
                    verseNumberString = text.split()[0] # Get the first token which is the first number
                    verseText = text[len(verseNumberString)+1:].lstrip() # Get the rest of the string which is the verse text
                    # TODO: We haven't stripped out character fields from within the verse -- not sure how Zefania handles them yet
                    if not verseText: # this is an empty (untranslated) verse
                        verseText = '- - -' # but we'll put in a filler
                    writerObject.writeLineOpenClose ( 'VERS', verseText, ('vnumber',verseNumberString) )
                else: unhandledMarkers.add( marker )
            if haveOpenChapter:
                writerObject.writeLineClose( 'CHAPTER' )
            writerObject.writeLineClose( 'BIBLEBOOK' )
        # end of writeBook

        # Set-up our Bible reference system
        BOS = BibleOrganizationalSystem( ZefaniaControls["PublicationCode"] )
        BRL = BibleReferenceList( self.BibleBooksCodes, BOS )

        if Globals.verbosityLevel>1: print( _("Exporting to Zefania format...") )
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
        if unhandledMarkers and Globals.verbosityLevel>0: print( "  " + _("WARNING: Unhandled USFM markers were {}").format(unhandledMarkers) )
    # end of toZefania_XML


    def toOSIS_XML( self, controlFileFolder, controlFilename, wantErrorMessages=False ):
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
        unhandledMarkers = set()

        # Set-up our Bible reference system
        BOS = BibleOrganizationalSystem( OSISControls["PublicationCode"] )
        BRL = BibleReferenceList( self.BibleBooksCodes, BOS )

        outputFolder = "OutputFiles"
        if not os.access( outputFolder, os.F_OK ): os.mkdir( outputFolder ) # Make the empty folder if there wasn't already one there

        # Let's write a Sword locale while we're at it
        SwLocFilepath = os.path.join( outputFolder, "SwLocale.conf" )
        print( _("Writing Sword locale file {}...").format(SwLocFilepath) )
        with open( SwLocFilepath, 'wt' ) as SwLocFile:
            SwLocFile.write( '[Meta]\nName={}\n'.format(OSISControls["xmlLanguage"]) )
            SwLocFile.write( 'Description={}\n'.format(OSISControls["LanguageName"]) )
            SwLocFile.write( 'Encoding=UTF-8\n\n[Text]\n' )
            for BBB in BOS.getBookList():
                SwLocFile.write( '{}={}\n'.format(self.BibleBooksCodes.getEnglishName_NR(BBB), BOS.getShortBookName(BBB) ) ) # Write the first English book name and the language book name
            SwLocFile.write( '\n[Book Abbrevs]\n' )
            for BBB in BOS.getBookList():
                SwLocFile.write( '{}={}\n'.format(self.BibleBooksCodes.getEnglishName_NR(BBB).upper(), self.BibleBooksCodes.getSwordAbbreviation(BBB) ) ) # Write the UPPER CASE language book name and the Sword abbreviation

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

        toOSISGlobals = { "vRef":'', "XRefNum":0, "FootnoteNum":0, "lastRef":'', "OneChapterOSISBookCodes":self.BibleBooksCodes.getOSISSingleChapterBooksList() } # These are our global variables


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
                    nonlocal BBB
                    toOSISGlobals["XRefNum"] += 1
                    OSISxref = '<note type="crossReference" osisRef="{}" osisID="{}!crossreference.{}">'.format(toOSISGlobals["vRef"],toOSISGlobals["vRef"],toOSISGlobals["XRefNum"])
                    for j,token in enumerate(USFMxref.split('\\')):
                        #print( "processXRef", j, "'"+token+"'", "from", '"'+USFMxref+'"' )
                        if j==0: # The first token (but the x has already been removed)
                            rest = token.strip()
                            if rest != '-': logging.warning( _("We got something else here other than hyphen (probably need to do something with it): {} '{}' from '{}'").format(cRef, token, text) )
                        elif token.startswith('xo '): # xref reference follows
                            adjToken = token[3:].strip()
                            if adjToken.endswith(' a'): adjToken = adjToken[:-2] # Remove any 'a' suffix (occurs when a cross-reference has multiple (a and b) parts
                            if adjToken.endswith(':'): adjToken = adjToken[:-1] # Remove any final colon (this is a language dependent hack)
                            adjToken = BOS.getBookAbbreviation(BBB) + ' ' + adjToken # Prepend the vernacular book abbreviation
                            osisRef = BRL.parseToOSIS( adjToken, wantErrorMessages )
                            if osisRef is not None:
                                OSISxref += '<reference type="source" osisRef="{}">{}</reference>'.format(osisRef,token[3:])
                                if wantErrorMessages and not BRL.containsReference( BBB, currentChapterNumberString, verseNumberString ):
                                    logging.error( _("Cross-reference at {} {}:{} seems to contain the wrong self-reference '{}'").format(BBB,currentChapterNumberString,verseNumberString, token) )
                        elif token.startswith('xt '): # xref text follows
                            xrefText = token[3:]
                            finalPunct = ''
                            while xrefText[-1] in (' ,;.'): finalPunct = xrefText[-1] + finalPunct; xrefText = xrefText[:-1]
                            #adjString = xrefText[:-6] if xrefText.endswith( ' (LXX)' ) else xrefText # Sorry, this is a crude hack to avoid unnecessary error messages
                            osisRef = BRL.parseToOSIS( xrefText, wantErrorMessages )
                            if osisRef is not None:
                                OSISxref += '<reference type="source" osisRef="{}">{}</reference>'.format(osisRef,xrefText+finalPunct)
                        elif token.startswith('x '): # another whole xref entry follows
                            rest = token[2:].strip()
                            if rest != '-': logging.warning( _("We got something else here other than hyphen (probably need to do something with it): {} '{}' from '{}'").format(cRef, token, text) )
                        elif token in ('xt*', 'x*'):
                            pass # We're being lazy here and not checking closing markers properly
                        else:
                            logging.warning( _("Unprocessed '{}' token in {} xref '{}'").format(token, toOSISGlobals["vRef"], USFMxref) )
                    OSISxref += '</note>'
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
                    OSISfootnote = '<note osisRef="{}" osisID="{}!footnote.{}">'.format(toOSISGlobals["vRef"],toOSISGlobals["vRef"],toOSISGlobals["FootnoteNum"])
                    for j,token in enumerate(USFMfootnote.split('\\')):
                        #print( "processFootnote", j, token, USFMfootnote )
                        if j==0: continue # ignore the + for now
                        elif token.startswith('fr '): # footnote reference follows
                            adjToken = token[3:].strip()
                            if adjToken.endswith(':'): adjToken = adjToken[:-1] # Remove any final colon (this is a language dependent hack)
                            adjToken = BOS.getBookAbbreviation(BBB) + ' ' + adjToken # Prepend the vernacular book abbreviation
                            osisRef = BRL.parseToOSIS( adjToken, wantErrorMessages ) # Note that this may return None
                            if osisRef is not None:
                                OSISfootnote += '<reference type="source" osisRef="{}">{}</reference>'.format(osisRef,token[3:])
                                if wantErrorMessages and not BRL.containsReference( BBB, currentChapterNumberString, verseNumberString ):
                                    logging.error( _("Footnote at {} {}:{} seems to contain the wrong self-reference '{}'").format(BBB,currentChapterNumberString,verseNumberString, token) )
                        elif token.startswith('ft '): # footnote text follows
                            OSISfootnote += token[3:]
                        elif token.startswith('fq '): # footnote quote follows -- NOTE: We also assume here that the next marker closes the fq field
                            OSISfootnote += '<catchWord>{}</catchWord>'.format(token[3:]) # Note that the trailing space goes in the catchword here -- seems messy
                        elif token in ('ft*','fq*'):
                            pass # We're being lazy here and not checking closing markers properly
                        else:
                            logging.warning( _("Unprocessed '{}' token in {} footnote '{}'").format(token, toOSISGlobals["vRef"], USFMfootnote) )
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
                        logging.warning( _("No space after xref entry in {}").format(toOSISGlobals["vRef"]) )
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
#                        #logging.warning( 'No space after footnote entry in {}'.format(toOSISGlobals["vRef"] )
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
                    logging.warning( _("Unexpected double angle brackets in {}: '{}' field is '{}'").format(toOSISGlobals["vRef"],marker,textToCheck) )
                    textToCheck = textToCheck.replace('<<','“' ).replace('>>','”' )
                if '\\bk ' in textToCheck and '\\bk*' in textToCheck:
                    textToCheck = textToCheck.replace('\\bk ','<reference type="x-bookName">').replace('\\bk*','</reference>')
                if '\\' in textToCheck:
                    logging.error( _("We still have some unprocessed backslashes in {}: '{}' field is '{}'").format(toOSISGlobals["vRef"],marker,textToCheck) )
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
                nonlocal verseNumberString
                verseNumberString = text.split()[0] # Get the first token which is the first number
                verseText = text[len(verseNumberString)+1:].lstrip() # Get the rest of the string which is the verse text
                if '-' in verseNumberString:
                    bits = verseNumberString.split('-')
                    if len(bits)!=2 or not bits[0].isdigit() or not bits[1].isdigit(): logging.critical( _("Doesn't handle verse number of form '{}' yet for {}").format(verseNumberString,cRef) )
                    toOSISGlobals["vRef"]  = cRef + '.' + bits[0]
                    vRef2 = cRef + '.' + bits[1]
                    sID    = toOSISGlobals["vRef"] + '-' + vRef2
                    osisID = toOSISGlobals["vRef"] + ' ' + vRef2
                elif ',' in verseNumberString:
                    raise Exception( "not written yet for comma in versenumber" )
                elif verseNumberString.isdigit():
                    sID = osisID = toOSISGlobals["vRef"] = cRef + '.' + verseNumberString
                else: logging.critical( _("Doesn't handle verse number of form '{}' yet for {}").format(verseNumberString,cRef) )
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
            for marker,text in bkData.lines: # Process USFM lines
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
                    currentChapterNumberString, verseNumberString = text, '0'
                    if not currentChapterNumberString.isdigit(): logging.critical( _("Can't handle non-digit '{}' chapter number yet").format(text) )
                    cRef = bRef + '.' + checkText(currentChapterNumberString)
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
                    if haveOpenParagraph or haveOpenSection or not haveOpenMajorSection: logging.error( _("Didn't expect major reference 'mr' marker after {}").format(toOSISGlobals["vRef"]) )
                    writerObject.writeLineOpenClose( 'title', checkText(text), ('type',"parallel") ) # Section reference
                elif marker=='r':
                    # Should only follow a s1 I think
                    if haveOpenParagraph or not haveOpenSection: logging.error( _("Didn't expect reference 'r' marker after {}").format(toOSISGlobals["vRef"]) )
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
                else: unhandledMarkers.add( marker )
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

        if Globals.verbosityLevel>1: print( _("Exporting to OSIS XML format...") )
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
        if unhandledMarkers and Globals.verbosityLevel>0: print( "  " + _("WARNING: Unhandled USFM markers were {}").format(unhandledMarkers) )
        print( "Need to find and look at an example where a new chapter isn't a new <p> to see how chapter eIDs should be handled there" )
    # end of toOSIS_XML


    def toSwordModule( self, controlFileFolder, controlFilename, wantErrorMessages=False ):
        """
        Using settings from the given control file,
            converts the USFM information to a UTF-8 OSIS-XML-based Sword module.
        """
        import struct
        assert( struct.calcsize("IH") == 6 ) # Six-byte format

        # Get the data tables that we need for proper checking
        SwordControls = {}
        ControlFiles.readControlFile( controlFileFolder, controlFilename, SwordControls )
        unhandledMarkers = set()

        # Set-up our Bible reference system
        BOS = BibleOrganizationalSystem( SwordControls["PublicationCode"] )
        BRL = BibleReferenceList( self.BibleBooksCodes, BOS )

        if 0:
            bookAbbrevDict, bookNameDict, bookAbbrevNameDict = {}, {}, {}
            for BBB in self.BibleBooksCodes.getAllReferenceAbbreviations(): # Pre-process the language booknames
                if BBB in SwordControls and SwordControls[BBB]:
                    bits = SwordControls[BBB].split(',')
                    if len(bits)!=2: logging.error( _("Unrecognized language book abbreviation and name for {}: '{}'").format( BBB, OSISControls[BBB] ) )
                    bookAbbrev = bits[0].strip().replace('"','') # Remove outside whitespace then the double quote marks
                    bookName = bits[1].strip().replace('"','') # Remove outside whitespace then the double quote marks
                    bookAbbrevDict[bookAbbrev], bookNameDict[bookName], bookAbbrevNameDict[BBB] = BBB, BBB, (bookAbbrev,bookName,)
                    if ' ' in bookAbbrev: bookAbbrevDict[bookAbbrev.replace(' ','',1)] = BBB # Duplicate entries without the first space (presumably between a number and a name like 1 Kings)
                    if ' ' in bookName: bookNameDict[bookName.replace(' ','',1)] = BBB # Duplicate entries without the first space

        # Let's write a Sword locale while we're at it
        outputFolder = "OutputFiles"
        if not os.access( outputFolder, os.F_OK ): os.mkdir( outputFolder ) # Make the empty folder if there wasn't already one there
        SwLocFilepath = os.path.join( outputFolder, "SwLocale.conf" )
        print( _("Writing Sword locale file {}...").format(SwLocFilepath) )
        with open( SwLocFilepath, 'wt' ) as SwLocFile:
            SwLocFile.write( '[Meta]\nName={}\n'.format(SwordControls["xmlLanguage"]) )
            SwLocFile.write( 'Description={}\n'.format(SwordControls["LanguageName"]) )
            SwLocFile.write( 'Encoding=UTF-8\n\n[Text]\n' )
            for BBB in BOS.getBookList():
                SwLocFile.write( '{}={}\n'.format(self.BibleBooksCodes.getEnglishName_NR(BBB), BOS.getShortBookName(BBB) ) ) # Write the first English book name and the language book name
            SwLocFile.write( '\n[Book Abbrevs]\n' )
            for BBB in BOS.getBookList():
                SwLocFile.write( '{}={}\n'.format(self.BibleBooksCodes.getEnglishName_NR(BBB).upper(), self.BibleBooksCodes.getSwordAbbreviation(BBB) ) ) # Write the UPPER CASE language book name and the Sword abbreviation

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

        toSwordGlobals = { 'currentID':0, "idStack":[], "vRef":'', "XRefNum":0, "FootnoteNum":0, "lastRef":'', 'offset':0, 'length':0, "OneChapterOSISBookCodes":self.BibleBooksCodes.getOSISSingleChapterBooksList() } # These are our global variables

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
                    nonlocal BBB
                    toSwordGlobals["XRefNum"] += 1
                    OSISxref = '<note type="crossReference" osisRef="{}" osisID="{}!crossreference.{}">'.format(toSwordGlobals["vRef"],toSwordGlobals["vRef"],toSwordGlobals["XRefNum"])
                    for j,token in enumerate(USFMxref.split('\\')):
                        #print( "processXRef", j, "'"+token+"'", "from", '"'+USFMxref+'"' )
                        if j==0: # The first token (but the x has already been removed)
                            rest = token.strip()
                            if rest != '-': logging.warning( _("We got something else here other than hyphen (probably need to do something with it): {} '{}' from '{}'").format(cRef, token, text) )
                        elif token.startswith('xo '): # xref reference follows
                            adjToken = token[3:].strip()
                            if adjToken.endswith(' a'): adjToken = adjToken[:-2] # Remove any 'a' suffix (occurs when a cross-reference has multiple (a and b) parts
                            if adjToken.endswith(':'): adjToken = adjToken[:-1] # Remove any final colon (this is a language dependent hack)
                            adjToken = BOS.getBookAbbreviation(BBB) + ' ' + adjToken # Prepend the vernacular book abbreviation
                            osisRef = BRL.parseToOSIS( adjToken, wantErrorMessages )
                            if osisRef is not None:
                                OSISxref += '<reference type="source" osisRef="{}">{}</reference>'.format(osisRef,token[3:])
                                if wantErrorMessages and not BRL.containsReference( BBB, currentChapterNumberString, verseNumberString ):
                                    logging.error( _("Cross-reference at {} {}:{} seems to contain the wrong self-reference '{}'").format(BBB,currentChapterNumberString,verseNumberString, token) )
                        elif token.startswith('xt '): # xref text follows
                            xrefText = token[3:]
                            finalPunct = ''
                            while xrefText[-1] in (' ,;.'): finalPunct = xrefText[-1] + finalPunct; xrefText = xrefText[:-1]
                            #adjString = xrefText[:-6] if xrefText.endswith( ' (LXX)' ) else xrefText # Sorry, this is a crude hack to avoid unnecessary error messages
                            osisRef = BRL.parseToOSIS( xrefText, wantErrorMessages )
                            if osisRef is not None:
                                OSISxref += '<reference type="source" osisRef="{}">{}</reference>'.format(osisRef,xrefText+finalPunct)
                        elif token.startswith('x '): # another whole xref entry follows
                            rest = token[2:].strip()
                            if rest != '-': logging.warning( _("We got something else here other than hyphen (probably need to do something with it): {} '{}' from '{}'").format(cRef, token, text) )
                        elif token in ('xt*', 'x*'):
                            pass # We're being lazy here and not checking closing markers properly
                        else:
                            logging.warning( _("Unprocessed '{}' token in {} xref '{}'").format(token, toOSISGlobals["vRef"], USFMxref) )
                    OSISxref += '</note>'
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
                    OSISfootnote = '<note osisRef="{}" osisID="{}!footnote.{}">'.format(toSwordGlobals["vRef"],toSwordGlobals["vRef"],toSwordGlobals["FootnoteNum"])
                    for j,token in enumerate(USFMfootnote.split('\\')):
                        #print( "processFootnote", j, token, USFMfootnote )
                        if j==0: continue # ignore the + for now
                        elif token.startswith('fr '): # footnote reference follows
                            adjToken = token[3:].strip()
                            if adjToken.endswith(':'): adjToken = adjToken[:-1] # Remove any final colon (this is a language dependent hack)
                            adjToken = BOS.getBookAbbreviation(BBB) + ' ' + adjToken # Prepend the vernacular book abbreviation
                            osisRef = BRL.parseToOSIS( adjToken, wantErrorMessages )
                            if osisRef is not None:
                                OSISfootnote += '<reference osisRef="{}" type="source">{}</reference>'.format(osisRef,token[3:])
                                if wantErrorMessages and not BRL.containsReference( BBB, currentChapterNumberString, verseNumberString ):
                                    logging.error( _("Footnote at {} {}:{} seems to contain the wrong self-reference '{}'").format(BBB,currentChapterNumberString,verseNumberString, token) )
                        elif token.startswith('ft '): # footnote text follows
                            OSISfootnote += token[3:]
                        elif token.startswith('fq '): # footnote quote follows -- NOTE: We also assume here that the next marker closes the fq field
                            OSISfootnote += '<catchWord>{}</catchWord>'.format(token[3:]) # Note that the trailing space goes in the catchword here -- seems messy
                        elif token in ('ft*','fq*'):
                            pass # We're being lazy here and not checking closing markers properly
                        else:
                            logging.warning( _("Unprocessed '{}' token in {} footnote '{}'").format(token, toSwordGlobals["vRef"], USFMfootnote) )
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
                        logging.warning( _("No space after xref entry in {}").format(toSwordGlobals["vRef"]) )
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
#                        #logging.warning( 'No space after footnote entry in {}'.format(toSwordGlobals["vRef"] )
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
                    logging.warning( _("Unexpected double angle brackets in {}: '{}' field is '{}'").format(toSwordGlobals["vRef"],marker,textToCheck) )
                    textToCheck = textToCheck.replace('<<','“' ).replace('>>','”' )
                if '\\bk ' in textToCheck and '\\bk*' in textToCheck:
                    textToCheck = textToCheck.replace('\\bk ','<reference type="x-bookName">').replace('\\bk*','</reference>')
                if '\\' in textToCheck:
                    logging.error( _("We still have some unprocessed backslashes in {}: '{}' field is '{}'").format(toSwordGlobals["vRef"],marker,textToCheck) )
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
                verseNumberString = text.split()[0] # Get the first token which is the first number
                verseText = text[len(verseNumberString)+1:].lstrip() # Get the rest of the string which is the verse text
                if '-' in verseNumberString:
                    bits = verseNumberString.split('-')
                    if len(bits)!=2 or not bits[0].isdigit() or not bits[1].isdigit(): logging.critical( _("Doesn't handle verse number of form '{}' yet for {}").format(verseNumberString,cRef) )
                    toSwordGlobals["vRef"]  = cRef + '.' + bits[0]
                    vRef2 = cRef + '.' + bits[1]
                    sID    = toSwordGlobals["vRef"] + '-' + vRef2
                    osisID = toSwordGlobals["vRef"] + ' ' + vRef2
                elif ',' in verseNumberString:
                    raise Exception( "not written yet for comma in versenumber" )
                elif verseNumberString.isdigit():
                    sID = osisID = toSwordGlobals["vRef"] = cRef + '.' + verseNumberString
                else: logging.critical( _("Doesn't handle verse number of form '{}' yet for {}").format(verseNumberString,cRef) )
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
                return "gen{}".format(toSwordGlobals['currentID'])
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
            for marker,text in bkData.lines: # Process USFM lines
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
                    currentChapterNumberString = text
                    if not currentChapterNumberString.isdigit(): logging.critical( _("Can't handle non-digit '{}' chapter number yet").format(text) )
                    cRef = bRef + '.' + checkText(currentChapterNumberString)
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
                    if haveOpenParagraph or haveOpenSection or not haveOpenMajorSection: logging.error( _("Didn't expect major reference 'mr' marker after {}").format(toSwordGlobals["vRef"]) )
                    writerObject.writeLineOpenClose( 'title', checkText(text), ('type',"parallel") ) # Section reference
                elif marker=='r':
                    # Should only follow a s1 I think
                    if haveOpenParagraph or not haveOpenSection: logging.error( _("Didn't expect reference 'r' marker after {}").format(toSwordGlobals["vRef"]) )
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
                else: unhandledMarkers.add( marker )
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
        if Globals.verbosityLevel>1: print( _("Exporting to Sword modified-OSIS XML format...") )
        xwOT = XMLWriter().setOutputFilePath( os.path.join( lgFolder, 'ot' ) )
        xwNT = XMLWriter().setOutputFilePath( os.path.join( lgFolder, 'nt' ) )
        xwOT.setHumanReadable( 'NLSpace', indentSize=5 ) # Can be set to 'All', 'Header', or 'None'
        xwNT.setHumanReadable( 'NLSpace', indentSize=5 ) # Can be set to 'All', 'Header', or 'None'
        xwOT.start( noAutoXML=True ); xwNT.start( noAutoXML=True )
        toSwordGlobals['length'] = xwOT.writeLineOpenSelfclose( 'milestone', [('type',"x-importer"), ('subtype',"x-USFMBible.py"), ('n',"${} $".format(versionString))] )
        toSwordGlobals['length'] = xwNT.writeLineOpenSelfclose( 'milestone', [('type',"x-importer"), ('subtype',"x-USFMBible.py"), ('n',"${} $".format(versionString))] )
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
                else: raise Exception( "Unexpected {} Bible book".format(BBB) )
                writeBook( xw, ix, BBB, bookData )
        xwOT.close(); xwNT.close()
        if unhandledMarkers and Globals.verbosityLevel>0: print( "  " + _("WARNING: Unhandled USFM markers were {}").format(unhandledMarkers) )
    #end of toSwordModule


    def toBible( self, outputFilepath=None, wantErrorMessages=False ):
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
                #else: print( "Doesn't handle {} marker yet".format(marker )
            #print( bk)
        if outputFilepath: B.write( outputFilepath )
        if unhandledMarkers and Globals.verbosityLevel>0: print( "  " + _("WARNING: Unhandled USFM markers were {}").format(unhandledMarkers) )
    # end of toBible
# end of class USFMBible


def main():
    """
    Demonstrate reading and processing some Bible databases.
    """
    # Handle command line parameters
    from optparse import OptionParser
    parser = OptionParser( version="v{}".format( versionString ) )
    parser.add_option("-e", "--export", action="store_true", dest="export", default=False, help="export the XML file to .py and .h tables suitable for directly including into other programs")
    Globals.addStandardOptionsAndProcess( parser )

    if Globals.verbosityLevel > 0: print( "{} V{}".format( progName, versionString ) )

    uB = USFMBible( "Matigsalug" )
    uB.load( "/mnt/Data/Matigsalug/Scripture/MBTV" )
    print( uB )
    #print( uB.getVersification () )

    if Globals.commandLineOptions.export:
        wantErrorMessages = True
        if Globals.verbosityLevel > 0: print( "NOTE: This is {} V{} -- i.e., still just alpha quality software!".format( progName, versionString ) )
        #uB.toZefania_XML( '', os.path.join( 'ControlFiles', "MBT_to_Zefania_controls.txt" ), wantErrorMessages )
        #uB.toMediaWiki( '', os.path.join( 'ControlFiles', "MBT_to_MediaWiki_controls.txt" ), wantErrorMessages )
        uB.toOSIS_XML( '', os.path.join( 'ControlFiles', "MBT_to_OSIS_controls.txt" ), wantErrorMessages )
        #uB.toSwordModule( '', os.path.join( 'ControlFiles', "MBT_to_OSIS_controls.txt" ), wantErrorMessages ) # We use the same OSIS controls (except for the output filename)
        #uB.toBible( os.path.join( 'ScrapedFiles', "TestBible.module" ), wantErrorMessages )

if __name__ == '__main__':
    main()
## End of USFMBible.py
