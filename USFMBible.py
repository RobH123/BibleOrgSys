#!/usr/bin/python3
#
# USFMBible.py
#
# Module handling the USFM markers for Bible books
#   Last modified: 2010-11-09 (also update versionString below)
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


import os, logging
from collections import OrderedDict


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
                if '-' in verseText: # we have a range like 7-9
                    bits = verseText.split( '-', 1 )
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
    # end of __init_

    def __str__( self ):
        """
        This method returns the string representation of a Bible book code.
        
        @return: the name of a Bible object formatted as a string
        @rtype: string
        """
        result = ""
        if self.name: result += ('\n' if result else '') + self.name
        if self.sourceFolder: result += ('\n' if result else '') + "From: " + self.sourceFolder
        result += ('\n' if result else '') + "Num books = " + str(len(self.books))
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
# end of class USFMBible

def demo():
    """
    Demonstrate reading and processing some Bible databases.
    """
    uB = USFMBible( "Matigsalug" )
    uB.load( "/mnt/Data/Matigsalug/Scripture/MBTV" )
    print( uB )
    #print( uB.getVersification () )

if __name__ == '__main__':
    demo()
